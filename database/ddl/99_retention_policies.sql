-- Footy-Brain v5 Database Schema - Retention Policies & Compression
-- This file creates TimescaleDB retention policies and compression settings
-- Execute order: 99 (last)

-- =============================================================================
-- COMPRESSION POLICIES
-- =============================================================================

-- Enable compression for live_odds_tick after 7 days
ALTER TABLE live_odds_tick SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'fixture_id, bookmaker_id, bet_market_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);

SELECT add_compression_policy('live_odds_tick', INTERVAL '7 days');

-- Enable compression for live_event_tick after 7 days
ALTER TABLE live_event_tick SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'fixture_id, team_id, event_type',
    timescaledb.compress_orderby = 'timestamp DESC'
);

SELECT add_compression_policy('live_event_tick', INTERVAL '7 days');

-- Enable compression for live_stats_tick after 7 days
ALTER TABLE live_stats_tick SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'fixture_id, team_id',
    timescaledb.compress_orderby = 'timestamp DESC'
);

SELECT add_compression_policy('live_stats_tick', INTERVAL '7 days');

-- =============================================================================
-- RETENTION POLICIES FOR RAW DATA
-- =============================================================================

-- Retention policy for live_odds_tick: 30 days
SELECT add_retention_policy('live_odds_tick', INTERVAL '30 days');

-- Retention policy for live_event_tick: 90 days
SELECT add_retention_policy('live_event_tick', INTERVAL '90 days');

-- Retention policy for live_stats_tick: 60 days
SELECT add_retention_policy('live_stats_tick', INTERVAL '60 days');

-- =============================================================================
-- RETENTION POLICIES FOR CONTINUOUS AGGREGATES
-- =============================================================================

-- Keep 1-minute OHLC data for 7 days
SELECT add_retention_policy('live_odds_tick_ohlc_1m', INTERVAL '7 days');

-- Keep 5-minute OHLC data for 30 days
SELECT add_retention_policy('live_odds_tick_ohlc_5m', INTERVAL '30 days');

-- Keep 1-minute event summaries for 30 days
SELECT add_retention_policy('live_event_summary_1m', INTERVAL '30 days');

-- Keep 5-minute stats progression for 30 days
SELECT add_retention_policy('live_stats_progression_5m', INTERVAL '30 days');

-- Keep match live frames for 90 days (important for analysis)
SELECT add_retention_policy('match_live_frame', INTERVAL '90 days');

-- Keep daily fixture summaries for 2 years
SELECT add_retention_policy('daily_fixture_summary', INTERVAL '2 years');

-- Keep bookmaker odds comparison for 30 days
SELECT add_retention_policy('bookmaker_odds_comparison_5m', INTERVAL '30 days');

-- =============================================================================
-- CUSTOM RETENTION FUNCTIONS
-- =============================================================================

-- Function to clean up old prematch odds based on configuration
CREATE OR REPLACE FUNCTION cleanup_old_prematch_odds()
RETURNS INTEGER AS $$
DECLARE
    retention_days INTEGER;
    deleted_count INTEGER;
BEGIN
    -- Get retention period from system config
    SELECT value::INTEGER INTO retention_days 
    FROM system_config 
    WHERE key = 'prematch_odds_retention_days';
    
    -- Default to 365 days if not configured
    IF retention_days IS NULL THEN
        retention_days := 365;
    END IF;
    
    -- Delete old prematch odds
    DELETE FROM prematch_odds 
    WHERE snapshot_time < NOW() - INTERVAL '1 day' * retention_days;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup
    INSERT INTO audit_log (table_name, record_id, operation, new_values, changed_by)
    VALUES ('prematch_odds', 'cleanup', 'DELETE', 
            jsonb_build_object('deleted_count', deleted_count, 'retention_days', retention_days),
            'system_cleanup');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old fixture events
CREATE OR REPLACE FUNCTION cleanup_old_fixture_events()
RETURNS INTEGER AS $$
DECLARE
    retention_days INTEGER;
    deleted_count INTEGER;
BEGIN
    -- Get retention period from system config
    SELECT value::INTEGER INTO retention_days 
    FROM system_config 
    WHERE key = 'fixture_events_retention_days';
    
    -- Default to 730 days (2 years) if not configured
    IF retention_days IS NULL THEN
        retention_days := 730;
    END IF;
    
    -- Delete old fixture events for matches older than retention period
    DELETE FROM fixture_event 
    WHERE fixture_id IN (
        SELECT id FROM fixture 
        WHERE date < NOW() - INTERVAL '1 day' * retention_days
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup
    INSERT INTO audit_log (table_name, record_id, operation, new_values, changed_by)
    VALUES ('fixture_event', 'cleanup', 'DELETE', 
            jsonb_build_object('deleted_count', deleted_count, 'retention_days', retention_days),
            'system_cleanup');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old player match statistics
CREATE OR REPLACE FUNCTION cleanup_old_player_statistics()
RETURNS INTEGER AS $$
DECLARE
    retention_days INTEGER;
    deleted_count INTEGER;
BEGIN
    -- Get retention period from system config
    SELECT value::INTEGER INTO retention_days 
    FROM system_config 
    WHERE key = 'player_stats_retention_days';
    
    -- Default to 365 days if not configured
    IF retention_days IS NULL THEN
        retention_days := 365;
    END IF;
    
    -- Delete old player statistics for matches older than retention period
    DELETE FROM player_match_statistic 
    WHERE fixture_id IN (
        SELECT id FROM fixture 
        WHERE date < NOW() - INTERVAL '1 day' * retention_days
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup
    INSERT INTO audit_log (table_name, record_id, operation, new_values, changed_by)
    VALUES ('player_match_statistic', 'cleanup', 'DELETE', 
            jsonb_build_object('deleted_count', deleted_count, 'retention_days', retention_days),
            'system_cleanup');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old audit logs
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    retention_days INTEGER;
    deleted_count INTEGER;
BEGIN
    -- Get retention period from system config (default 90 days for audit logs)
    SELECT value::INTEGER INTO retention_days 
    FROM system_config 
    WHERE key = 'audit_log_retention_days';
    
    -- Default to 90 days if not configured
    IF retention_days IS NULL THEN
        retention_days := 90;
    END IF;
    
    -- Delete old audit logs
    DELETE FROM audit_log 
    WHERE changed_at < NOW() - INTERVAL '1 day' * retention_days;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- MAINTENANCE PROCEDURES
-- =============================================================================

-- Comprehensive cleanup procedure
CREATE OR REPLACE FUNCTION run_maintenance_cleanup()
RETURNS TABLE(
    cleanup_type TEXT,
    deleted_count INTEGER,
    execution_time INTERVAL
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    prematch_deleted INTEGER;
    events_deleted INTEGER;
    player_stats_deleted INTEGER;
    audit_deleted INTEGER;
BEGIN
    -- Cleanup prematch odds
    start_time := NOW();
    SELECT cleanup_old_prematch_odds() INTO prematch_deleted;
    end_time := NOW();
    
    RETURN QUERY SELECT 'prematch_odds'::TEXT, prematch_deleted, end_time - start_time;
    
    -- Cleanup fixture events
    start_time := NOW();
    SELECT cleanup_old_fixture_events() INTO events_deleted;
    end_time := NOW();
    
    RETURN QUERY SELECT 'fixture_events'::TEXT, events_deleted, end_time - start_time;
    
    -- Cleanup player statistics
    start_time := NOW();
    SELECT cleanup_old_player_statistics() INTO player_stats_deleted;
    end_time := NOW();
    
    RETURN QUERY SELECT 'player_statistics'::TEXT, player_stats_deleted, end_time - start_time;
    
    -- Cleanup audit logs
    start_time := NOW();
    SELECT cleanup_old_audit_logs() INTO audit_deleted;
    end_time := NOW();
    
    RETURN QUERY SELECT 'audit_logs'::TEXT, audit_deleted, end_time - start_time;
    
    -- Update system config with last cleanup time
    INSERT INTO system_config (key, value, description)
    VALUES ('last_maintenance_cleanup', NOW()::TEXT, 'Last maintenance cleanup execution time')
    ON CONFLICT (key) DO UPDATE SET 
        value = EXCLUDED.value,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- VACUUM AND ANALYZE PROCEDURES
-- =============================================================================

-- Function to run VACUUM and ANALYZE on key tables
CREATE OR REPLACE FUNCTION run_maintenance_vacuum()
RETURNS TABLE(
    table_name TEXT,
    operation TEXT,
    execution_time INTERVAL
) AS $$
DECLARE
    start_time TIMESTAMPTZ;
    end_time TIMESTAMPTZ;
    table_rec RECORD;
BEGIN
    -- List of tables to vacuum and analyze
    FOR table_rec IN 
        SELECT t.table_name 
        FROM information_schema.tables t
        WHERE t.table_schema = 'public' 
        AND t.table_type = 'BASE TABLE'
        AND t.table_name IN (
            'fixture', 'prematch_odds', 'fixture_event', 
            'fixture_statistic', 'player_match_statistic',
            'standing', 'h2h_statistic'
        )
    LOOP
        -- VACUUM
        start_time := NOW();
        EXECUTE 'VACUUM ' || table_rec.table_name;
        end_time := NOW();
        
        RETURN QUERY SELECT table_rec.table_name, 'VACUUM'::TEXT, end_time - start_time;
        
        -- ANALYZE
        start_time := NOW();
        EXECUTE 'ANALYZE ' || table_rec.table_name;
        end_time := NOW();
        
        RETURN QUERY SELECT table_rec.table_name, 'ANALYZE'::TEXT, end_time - start_time;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- MONITORING VIEWS
-- =============================================================================

-- View to monitor hypertable sizes
CREATE OR REPLACE VIEW hypertable_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables 
WHERE tablename IN ('live_odds_tick', 'live_event_tick', 'live_stats_tick')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- View to monitor compression ratios
CREATE OR REPLACE VIEW compression_stats AS
SELECT 
    chunk_schema,
    chunk_name,
    pg_size_pretty(before_compression_total_bytes) AS before_compression,
    pg_size_pretty(after_compression_total_bytes) AS after_compression,
    ROUND(
        (before_compression_total_bytes::NUMERIC - after_compression_total_bytes::NUMERIC) 
        / before_compression_total_bytes::NUMERIC * 100, 2
    ) AS compression_ratio_percent
FROM timescaledb_information.chunk_compression_stats
ORDER BY before_compression_total_bytes DESC;

-- View to monitor retention policy status
CREATE OR REPLACE VIEW retention_policy_status AS
SELECT 
    application_name,
    schedule_interval,
    max_runtime,
    max_retries,
    retry_period,
    next_start,
    last_finish,
    last_successful_finish,
    last_run_status
FROM timescaledb_information.jobs
WHERE proc_name = 'policy_retention'
ORDER BY next_start;

-- =============================================================================
-- INITIAL SYSTEM CONFIGURATION FOR RETENTION
-- =============================================================================

-- Insert retention configuration values
INSERT INTO system_config (key, value, description) VALUES
('prematch_odds_retention_days', '365', 'Retention period for prematch odds in days'),
('fixture_events_retention_days', '730', 'Retention period for fixture events in days'),
('player_stats_retention_days', '365', 'Retention period for player statistics in days'),
('audit_log_retention_days', '90', 'Retention period for audit logs in days'),
('compression_after_days', '7', 'Days after which to compress hypertable data'),
('maintenance_schedule', '0 3 * * *', 'Cron schedule for maintenance tasks')
ON CONFLICT (key) DO NOTHING;
