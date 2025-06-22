-- Footy-Brain v5 Database Schema - Dimension Tables
-- This file creates all dimension (reference) tables for the football data platform
-- Execute order: 00 (first)

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Enable UUID extension for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- COUNTRIES DIMENSION
-- =============================================================================
CREATE TABLE IF NOT EXISTS country (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(3),
    flag VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_country_code ON country(code);
CREATE INDEX IF NOT EXISTS idx_country_name ON country(name);

-- =============================================================================
-- LEAGUES DIMENSION
-- =============================================================================
CREATE TABLE IF NOT EXISTS league (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50), -- League, Cup, etc.
    logo VARCHAR(255),
    country_id INTEGER REFERENCES country(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_league_country ON league(country_id);
CREATE INDEX IF NOT EXISTS idx_league_name ON league(name);
CREATE INDEX IF NOT EXISTS idx_league_type ON league(type);

-- =============================================================================
-- SEASONS DIMENSION
-- =============================================================================
CREATE TABLE IF NOT EXISTS season (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    current BOOLEAN DEFAULT FALSE,
    coverage JSONB, -- API coverage information
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(year)
);

CREATE INDEX IF NOT EXISTS idx_season_year ON season(year);
CREATE INDEX IF NOT EXISTS idx_season_current ON season(current);

-- =============================================================================
-- LEAGUE SEASONS (Many-to-Many)
-- =============================================================================
CREATE TABLE IF NOT EXISTS league_season (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL REFERENCES league(id),
    season_id INTEGER NOT NULL REFERENCES season(id),
    start_date DATE,
    end_date DATE,
    current BOOLEAN DEFAULT FALSE,
    coverage JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(league_id, season_id)
);

CREATE INDEX IF NOT EXISTS idx_league_season_league ON league_season(league_id);
CREATE INDEX IF NOT EXISTS idx_league_season_season ON league_season(season_id);
CREATE INDEX IF NOT EXISTS idx_league_season_current ON league_season(current);

-- =============================================================================
-- TEAMS DIMENSION
-- =============================================================================
CREATE TABLE IF NOT EXISTS team (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    code VARCHAR(10),
    country_id INTEGER REFERENCES country(id),
    founded INTEGER,
    national BOOLEAN DEFAULT FALSE,
    logo VARCHAR(255),
    venue_id INTEGER, -- Will reference venue table
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_team_name ON team(name);
CREATE INDEX IF NOT EXISTS idx_team_country ON team(country_id);
CREATE INDEX IF NOT EXISTS idx_team_national ON team(national);

-- =============================================================================
-- VENUES DIMENSION
-- =============================================================================
CREATE TABLE IF NOT EXISTS venue (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    country_id INTEGER REFERENCES country(id),
    capacity INTEGER,
    surface VARCHAR(50),
    image VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_venue_name ON venue(name);
CREATE INDEX IF NOT EXISTS idx_venue_city ON venue(city);
CREATE INDEX IF NOT EXISTS idx_venue_country ON venue(country_id);

-- Add foreign key constraint to team table
ALTER TABLE team ADD CONSTRAINT fk_team_venue 
    FOREIGN KEY (venue_id) REFERENCES venue(id);

-- =============================================================================
-- PLAYERS DIMENSION
-- =============================================================================
CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    age INTEGER,
    birth_date DATE,
    birth_place VARCHAR(200),
    birth_country VARCHAR(100),
    nationality VARCHAR(100),
    height VARCHAR(10),
    weight VARCHAR(10),
    injured BOOLEAN DEFAULT FALSE,
    photo VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_player_name ON player(name);
CREATE INDEX IF NOT EXISTS idx_player_nationality ON player(nationality);
CREATE INDEX IF NOT EXISTS idx_player_age ON player(age);

-- =============================================================================
-- BOOKMAKERS DIMENSION
-- =============================================================================
CREATE TABLE IF NOT EXISTS bookmaker (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bookmaker_name ON bookmaker(name);

-- =============================================================================
-- BET DEFINITIONS
-- =============================================================================
CREATE TABLE IF NOT EXISTS bet_def_market (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bet_def_value (
    id SERIAL PRIMARY KEY,
    market_id INTEGER NOT NULL REFERENCES bet_def_market(id),
    value VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(market_id, value)
);

CREATE INDEX IF NOT EXISTS idx_bet_def_value_market ON bet_def_value(market_id);

-- =============================================================================
-- FIXTURE STATUS DEFINITIONS
-- =============================================================================
CREATE TABLE IF NOT EXISTS fixture_status (
    id SERIAL PRIMARY KEY,
    short VARCHAR(10) NOT NULL UNIQUE,
    long VARCHAR(50) NOT NULL,
    description TEXT,
    is_finished BOOLEAN DEFAULT FALSE,
    is_live BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert common fixture statuses
INSERT INTO fixture_status (short, long, description, is_finished, is_live) VALUES
('TBD', 'Time To Be Defined', 'Match time not yet defined', FALSE, FALSE),
('NS', 'Not Started', 'Match not started', FALSE, FALSE),
('1H', 'First Half', 'First half in progress', FALSE, TRUE),
('HT', 'Halftime', 'Halftime break', FALSE, TRUE),
('2H', 'Second Half', 'Second half in progress', FALSE, TRUE),
('ET', 'Extra Time', 'Extra time in progress', FALSE, TRUE),
('BT', 'Break Time', 'Break before extra time', FALSE, TRUE),
('P', 'Penalty In Progress', 'Penalty shootout in progress', FALSE, TRUE),
('SUSP', 'Match Suspended', 'Match suspended', FALSE, FALSE),
('INT', 'Match Interrupted', 'Match interrupted', FALSE, FALSE),
('FT', 'Match Finished', 'Match finished after 90 minutes', TRUE, FALSE),
('AET', 'Match Finished After Extra Time', 'Match finished after extra time', TRUE, FALSE),
('PEN', 'Match Finished After Penalty', 'Match finished after penalty shootout', TRUE, FALSE),
('PST', 'Match Postponed', 'Match postponed', FALSE, FALSE),
('CANC', 'Match Cancelled', 'Match cancelled', FALSE, FALSE),
('ABD', 'Match Abandoned', 'Match abandoned', FALSE, FALSE),
('AWD', 'Technical Loss', 'Match awarded (walkover)', TRUE, FALSE),
('WO', 'WalkOver', 'Walkover', TRUE, FALSE)
ON CONFLICT (short) DO NOTHING;

-- =============================================================================
-- EVENT TYPES DEFINITIONS
-- =============================================================================
CREATE TABLE IF NOT EXISTS event_type (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert common event types
INSERT INTO event_type (type, description) VALUES
('Goal', 'Goal scored'),
('Card', 'Yellow or red card'),
('subst', 'Player substitution'),
('Var', 'VAR decision'),
('Penalty', 'Penalty awarded'),
('Own Goal', 'Own goal'),
('Missed Penalty', 'Penalty missed'),
('Yellow Card', 'Yellow card shown'),
('Red Card', 'Red card shown'),
('Second Yellow card', 'Second yellow card (red)'),
('Offside', 'Offside'),
('Foul', 'Foul committed')
ON CONFLICT (type) DO NOTHING;

-- =============================================================================
-- POSITIONS DIMENSION
-- =============================================================================
CREATE TABLE IF NOT EXISTS position (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    abbreviation VARCHAR(10),
    category VARCHAR(20), -- Goalkeeper, Defender, Midfielder, Attacker
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert common positions
INSERT INTO position (name, abbreviation, category) VALUES
('Goalkeeper', 'GK', 'Goalkeeper'),
('Defender', 'DF', 'Defender'),
('Centre-Back', 'CB', 'Defender'),
('Left-Back', 'LB', 'Defender'),
('Right-Back', 'RB', 'Defender'),
('Wing-Back', 'WB', 'Defender'),
('Defensive Midfield', 'DM', 'Midfielder'),
('Central Midfield', 'CM', 'Midfielder'),
('Attacking Midfield', 'AM', 'Midfielder'),
('Left Midfield', 'LM', 'Midfielder'),
('Right Midfield', 'RM', 'Midfielder'),
('Left Winger', 'LW', 'Attacker'),
('Right Winger', 'RW', 'Attacker'),
('Centre-Forward', 'CF', 'Attacker'),
('Striker', 'ST', 'Attacker'),
('Second Striker', 'SS', 'Attacker')
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- TIMEZONE DEFINITIONS
-- =============================================================================
CREATE TABLE IF NOT EXISTS timezone_def (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    offset_hours INTEGER NOT NULL,
    offset_minutes INTEGER DEFAULT 0,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- AUDIT LOG TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_record ON audit_log(record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON audit_log(operation);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(changed_at);

-- =============================================================================
-- SYSTEM CONFIGURATION TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default system configurations
INSERT INTO system_config (key, value, description) VALUES
('schema_version', '5.0.0', 'Database schema version'),
('last_migration', NOW()::TEXT, 'Last migration timestamp'),
('data_retention_days', '90', 'Default data retention period'),
('api_rate_limit', '6', 'API requests per second limit'),
('websocket_enabled', 'true', 'WebSocket real-time updates enabled')
ON CONFLICT (key) DO UPDATE SET 
    value = EXCLUDED.value,
    updated_at = NOW();

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to all dimension tables
CREATE TRIGGER update_country_updated_at BEFORE UPDATE ON country
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_league_updated_at BEFORE UPDATE ON league
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_season_updated_at BEFORE UPDATE ON season
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_team_updated_at BEFORE UPDATE ON team
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_venue_updated_at BEFORE UPDATE ON venue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_player_updated_at BEFORE UPDATE ON player
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookmaker_updated_at BEFORE UPDATE ON bookmaker
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
