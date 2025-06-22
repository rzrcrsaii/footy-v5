"""
Footy-Brain v5 Database Initialization
DDL orchestration, continuous aggregates, retention policies, and seed data.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List, Optional

import asyncpg

logger = logging.getLogger(__name__)

# Project root path
project_root = Path(__file__).parent.parent.parent.parent


async def execute_sql_file(conn: asyncpg.Connection, file_path: Path) -> None:
    """Execute SQL commands from a file."""
    logger.info(f"Executing SQL file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                try:
                    await conn.execute(statement)
                except Exception as e:
                    logger.error(f"Error executing statement in {file_path}: {e}")
                    logger.error(f"Statement: {statement[:200]}...")
                    raise
        
        logger.info(f"Successfully executed {file_path}")
        
    except FileNotFoundError:
        logger.error(f"SQL file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error executing SQL file {file_path}: {e}")
        raise


async def get_ddl_files() -> List[Path]:
    """Get DDL files in numeric order."""
    ddl_dir = project_root / 'database' / 'ddl'
    
    if not ddl_dir.exists():
        logger.warning(f"DDL directory not found: {ddl_dir}")
        return []
    
    # Get all .sql files and sort them numerically
    ddl_files = list(ddl_dir.glob('*.sql'))
    ddl_files.sort(key=lambda x: x.name)
    
    logger.info(f"Found {len(ddl_files)} DDL files")
    return ddl_files


async def get_seed_files() -> List[Path]:
    """Get seed files."""
    seeds_dir = project_root / 'database' / 'seeds'
    
    if not seeds_dir.exists():
        logger.warning(f"Seeds directory not found: {seeds_dir}")
        return []
    
    seed_files = list(seeds_dir.glob('*.sql'))
    seed_files.sort(key=lambda x: x.name)
    
    logger.info(f"Found {len(seed_files)} seed files")
    return seed_files


async def check_database_exists(database_url: str) -> bool:
    """Check if database exists and is accessible."""
    try:
        conn = await asyncpg.connect(database_url)
        await conn.execute('SELECT 1')
        await conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def check_schema_version(conn: asyncpg.Connection) -> Optional[str]:
    """Check current schema version."""
    try:
        result = await conn.fetchval("""
            SELECT value FROM system_config WHERE key = 'schema_version'
        """)
        return result
    except Exception:
        # Table might not exist yet
        return None


async def is_database_empty(conn: asyncpg.Connection) -> bool:
    """Check if database is empty (no tables)."""
    try:
        result = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        return result == 0
    except Exception:
        return True


async def should_run_seeds(conn: asyncpg.Connection) -> bool:
    """Check if seed data should be run."""
    try:
        # Check if country table is empty
        result = await conn.fetchval("SELECT COUNT(*) FROM country")
        return result == 0
    except Exception:
        # Table might not exist, so we should run seeds
        return True


async def create_database_if_not_exists(database_url: str) -> None:
    """Create database if it doesn't exist."""
    # Parse database URL to get connection details
    import urllib.parse
    
    parsed = urllib.parse.urlparse(database_url)
    db_name = parsed.path[1:]  # Remove leading slash
    
    # Connect to postgres database to create our database
    postgres_url = database_url.replace(f'/{db_name}', '/postgres')
    
    try:
        conn = await asyncpg.connect(postgres_url)
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        
        if not exists:
            logger.info(f"Creating database: {db_name}")
            await conn.execute(f'CREATE DATABASE "{db_name}"')
        
        await conn.close()
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise


async def run_ddl_scripts(conn: asyncpg.Connection) -> None:
    """Run all DDL scripts in numeric order."""
    logger.info("Running DDL scripts...")
    
    ddl_files = await get_ddl_files()
    
    if not ddl_files:
        logger.warning("No DDL files found")
        return
    
    for ddl_file in ddl_files:
        await execute_sql_file(conn, ddl_file)
    
    logger.info("DDL scripts completed successfully")


async def run_seed_scripts(conn: asyncpg.Connection) -> None:
    """Run seed scripts to populate initial data."""
    logger.info("Running seed scripts...")
    
    seed_files = await get_seed_files()
    
    if not seed_files:
        logger.warning("No seed files found")
        return
    
    for seed_file in seed_files:
        await execute_sql_file(conn, seed_file)
    
    logger.info("Seed scripts completed successfully")


async def setup_timescaledb_extensions(conn: asyncpg.Connection) -> None:
    """Setup TimescaleDB extensions and configurations."""
    logger.info("Setting up TimescaleDB extensions...")
    
    try:
        # Enable TimescaleDB extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
        
        # Enable UUID extension
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        
        # Check TimescaleDB version
        version = await conn.fetchval("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';")
        logger.info(f"TimescaleDB version: {version}")
        
    except Exception as e:
        logger.error(f"Error setting up TimescaleDB extensions: {e}")
        raise


async def verify_database_setup(conn: asyncpg.Connection) -> dict:
    """Verify database setup and return status."""
    logger.info("Verifying database setup...")
    
    verification = {
        "tables_created": 0,
        "hypertables_created": 0,
        "continuous_aggregates_created": 0,
        "seed_data_loaded": False,
        "timescaledb_enabled": False
    }
    
    try:
        # Count tables
        verification["tables_created"] = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        
        # Count hypertables
        verification["hypertables_created"] = await conn.fetchval("""
            SELECT COUNT(*) FROM timescaledb_information.hypertables
        """)
        
        # Count continuous aggregates
        verification["continuous_aggregates_created"] = await conn.fetchval("""
            SELECT COUNT(*) FROM timescaledb_information.continuous_aggregates
        """)
        
        # Check if seed data is loaded
        country_count = await conn.fetchval("SELECT COUNT(*) FROM country")
        verification["seed_data_loaded"] = country_count > 0
        
        # Check TimescaleDB
        timescale_version = await conn.fetchval("""
            SELECT extversion FROM pg_extension WHERE extname = 'timescaledb'
        """)
        verification["timescaledb_enabled"] = timescale_version is not None
        
        logger.info(f"Database verification: {verification}")
        
    except Exception as e:
        logger.error(f"Error during database verification: {e}")
        raise
    
    return verification


async def initialize_database(database_url: str, force_recreate: bool = False) -> dict:
    """
    Initialize database with DDL scripts, continuous aggregates, and seed data.
    
    Args:
        database_url: Database connection URL
        force_recreate: Whether to force recreation of schema
        
    Returns:
        Dictionary with initialization status
    """
    logger.info("Starting database initialization...")
    
    try:
        # Create database if it doesn't exist
        await create_database_if_not_exists(database_url)
        
        # Connect to the database
        conn = await asyncpg.connect(database_url)
        
        try:
            # Setup TimescaleDB extensions first
            await setup_timescaledb_extensions(conn)
            
            # Check if database is empty or if we should force recreate
            is_empty = await is_database_empty(conn)
            current_version = await check_schema_version(conn)
            
            logger.info(f"Database empty: {is_empty}, Current version: {current_version}")
            
            if is_empty or force_recreate:
                logger.info("Running full database initialization...")
                
                # Run DDL scripts
                await run_ddl_scripts(conn)
                
                # Check if we should run seeds
                if await should_run_seeds(conn):
                    await run_seed_scripts(conn)
            else:
                logger.info("Database already initialized, skipping DDL and seeds")
            
            # Verify setup
            verification = await verify_database_setup(conn)
            
            logger.info("Database initialization completed successfully")
            
            return {
                "status": "success",
                "message": "Database initialized successfully",
                "verification": verification
            }
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return {
            "status": "error",
            "message": f"Database initialization failed: {str(e)}",
            "verification": {}
        }


async def reset_database(database_url: str) -> dict:
    """
    Reset database by dropping all tables and recreating schema.
    WARNING: This will delete all data!
    
    Args:
        database_url: Database connection URL
        
    Returns:
        Dictionary with reset status
    """
    logger.warning("RESETTING DATABASE - ALL DATA WILL BE LOST!")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        try:
            # Drop all tables in public schema
            await conn.execute("""
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
                GRANT ALL ON SCHEMA public TO postgres;
                GRANT ALL ON SCHEMA public TO public;
            """)
            
            logger.info("Database reset completed")
            
            # Reinitialize
            return await initialize_database(database_url, force_recreate=True)
            
        finally:
            await conn.close()
            
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return {
            "status": "error",
            "message": f"Database reset failed: {str(e)}"
        }


# CLI interface for database operations
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization utility")
    parser.add_argument("--reset", action="store_true", help="Reset database (WARNING: deletes all data)")
    parser.add_argument("--force", action="store_true", help="Force recreation of schema")
    parser.add_argument("--url", help="Database URL (default from environment)")
    
    args = parser.parse_args()
    
    database_url = args.url or os.getenv('DATABASE_URL', 
        'postgresql://footy:footy_secure_2024@localhost:5432/footy')
    
    async def main():
        if args.reset:
            result = await reset_database(database_url)
        else:
            result = await initialize_database(database_url, force_recreate=args.force)
        
        print(f"Result: {result}")
    
    asyncio.run(main())
