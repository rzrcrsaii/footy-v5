-- Footy-Brain v5 Database Schema - Fact Tables (PART 1/2)
-- This file creates all fact (transactional) tables for the football data platform
-- Execute order: 10 (after dimension tables)

-- =============================================================================
-- FIXTURES FACT TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS fixture (
    id INTEGER PRIMARY KEY,
    referee VARCHAR(200),
    timezone VARCHAR(50),
    date TIMESTAMPTZ NOT NULL,
    timestamp BIGINT,
    
    -- Venue information
    venue_id INTEGER REFERENCES venue(id),
    
    -- Status information
    status_short VARCHAR(10) NOT NULL,
    status_long VARCHAR(50),
    status_elapsed INTEGER,
    status_extra INTEGER,
    
    -- League and season
    league_id INTEGER NOT NULL REFERENCES league(id),
    season_year INTEGER NOT NULL,
    round VARCHAR(100),
    
    -- Teams
    home_team_id INTEGER NOT NULL REFERENCES team(id),
    away_team_id INTEGER NOT NULL REFERENCES team(id),
    
    -- Scores
    home_goals INTEGER DEFAULT 0,
    away_goals INTEGER DEFAULT 0,
    home_goals_ht INTEGER DEFAULT 0,
    away_goals_ht INTEGER DEFAULT 0,
    home_goals_et INTEGER DEFAULT 0,
    away_goals_et INTEGER DEFAULT 0,
    home_goals_pen INTEGER DEFAULT 0,
    away_goals_pen INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_fixture_goals_positive CHECK (
        home_goals >= 0 AND away_goals >= 0 AND
        home_goals_ht >= 0 AND away_goals_ht >= 0
    )
);

-- Indexes for fixture table
CREATE INDEX IF NOT EXISTS idx_fixture_date ON fixture(date);
CREATE INDEX IF NOT EXISTS idx_fixture_league_season ON fixture(league_id, season_year);
CREATE INDEX IF NOT EXISTS idx_fixture_home_team ON fixture(home_team_id);
CREATE INDEX IF NOT EXISTS idx_fixture_away_team ON fixture(away_team_id);
CREATE INDEX IF NOT EXISTS idx_fixture_status ON fixture(status_short);
CREATE INDEX IF NOT EXISTS idx_fixture_venue ON fixture(venue_id);
CREATE INDEX IF NOT EXISTS idx_fixture_round ON fixture(round);

-- =============================================================================
-- LIVE ODDS TICK (TimescaleDB Hypertable)
-- =============================================================================
CREATE TABLE IF NOT EXISTS live_odds_tick (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fixture_id INTEGER NOT NULL REFERENCES fixture(id),
    bookmaker_id INTEGER NOT NULL REFERENCES bookmaker(id),
    bet_market_id INTEGER NOT NULL REFERENCES bet_def_market(id),
    bet_value VARCHAR(50) NOT NULL,
    
    -- Odds data
    odd_value DECIMAL(10,2) NOT NULL,
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    match_minute INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_live_odds_positive CHECK (odd_value > 0)
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('live_odds_tick', 'timestamp', if_not_exists => TRUE);

-- Indexes for live_odds_tick
CREATE INDEX IF NOT EXISTS idx_live_odds_tick_fixture ON live_odds_tick(fixture_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_live_odds_tick_bookmaker ON live_odds_tick(bookmaker_id);
CREATE INDEX IF NOT EXISTS idx_live_odds_tick_market ON live_odds_tick(bet_market_id);
CREATE INDEX IF NOT EXISTS idx_live_odds_tick_timestamp ON live_odds_tick(timestamp DESC);

-- =============================================================================
-- LIVE EVENT TICK (TimescaleDB Hypertable)
-- =============================================================================
CREATE TABLE IF NOT EXISTS live_event_tick (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fixture_id INTEGER NOT NULL REFERENCES fixture(id),
    
    -- Event details
    event_type VARCHAR(50) NOT NULL,
    event_detail VARCHAR(100),
    event_comments TEXT,
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    match_minute INTEGER,
    match_minute_extra INTEGER,
    
    -- Team and player
    team_id INTEGER REFERENCES team(id),
    player_id INTEGER REFERENCES player(id),
    assist_player_id INTEGER REFERENCES player(id),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('live_event_tick', 'timestamp', if_not_exists => TRUE);

-- Indexes for live_event_tick
CREATE INDEX IF NOT EXISTS idx_live_event_tick_fixture ON live_event_tick(fixture_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_live_event_tick_type ON live_event_tick(event_type);
CREATE INDEX IF NOT EXISTS idx_live_event_tick_team ON live_event_tick(team_id);
CREATE INDEX IF NOT EXISTS idx_live_event_tick_player ON live_event_tick(player_id);
CREATE INDEX IF NOT EXISTS idx_live_event_tick_timestamp ON live_event_tick(timestamp DESC);

-- =============================================================================
-- LIVE STATS TICK (TimescaleDB Hypertable)
-- =============================================================================
CREATE TABLE IF NOT EXISTS live_stats_tick (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fixture_id INTEGER NOT NULL REFERENCES fixture(id),
    team_id INTEGER NOT NULL REFERENCES team(id),
    
    -- Match statistics
    shots_on_goal INTEGER DEFAULT 0,
    shots_off_goal INTEGER DEFAULT 0,
    total_shots INTEGER DEFAULT 0,
    blocked_shots INTEGER DEFAULT 0,
    shots_inside_box INTEGER DEFAULT 0,
    shots_outside_box INTEGER DEFAULT 0,
    fouls INTEGER DEFAULT 0,
    corner_kicks INTEGER DEFAULT 0,
    offsides INTEGER DEFAULT 0,
    ball_possession INTEGER DEFAULT 0, -- percentage
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    goalkeeper_saves INTEGER DEFAULT 0,
    total_passes INTEGER DEFAULT 0,
    passes_accurate INTEGER DEFAULT 0,
    passes_percentage INTEGER DEFAULT 0,
    
    -- Timing
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    match_minute INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_live_stats_positive CHECK (
        shots_on_goal >= 0 AND shots_off_goal >= 0 AND
        total_shots >= 0 AND ball_possession >= 0 AND ball_possession <= 100
    )
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('live_stats_tick', 'timestamp', if_not_exists => TRUE);

-- Indexes for live_stats_tick
CREATE INDEX IF NOT EXISTS idx_live_stats_tick_fixture ON live_stats_tick(fixture_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_live_stats_tick_team ON live_stats_tick(team_id);
CREATE INDEX IF NOT EXISTS idx_live_stats_tick_timestamp ON live_stats_tick(timestamp DESC);

-- =============================================================================
-- PREMATCH ODDS SNAPSHOTS
-- =============================================================================
CREATE TABLE IF NOT EXISTS prematch_odds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fixture_id INTEGER NOT NULL REFERENCES fixture(id),
    bookmaker_id INTEGER NOT NULL REFERENCES bookmaker(id),
    bet_market_id INTEGER NOT NULL REFERENCES bet_def_market(id),
    bet_value VARCHAR(50) NOT NULL,
    
    -- Odds data
    odd_value DECIMAL(10,2) NOT NULL,
    
    -- Timing
    snapshot_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    hours_before_match INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT chk_prematch_odds_positive CHECK (odd_value > 0),
    CONSTRAINT chk_prematch_hours_positive CHECK (hours_before_match >= 0)
);

-- Indexes for prematch_odds
CREATE INDEX IF NOT EXISTS idx_prematch_odds_fixture ON prematch_odds(fixture_id);
CREATE INDEX IF NOT EXISTS idx_prematch_odds_bookmaker ON prematch_odds(bookmaker_id);
CREATE INDEX IF NOT EXISTS idx_prematch_odds_market ON prematch_odds(bet_market_id);
CREATE INDEX IF NOT EXISTS idx_prematch_odds_snapshot ON prematch_odds(snapshot_time DESC);
CREATE INDEX IF NOT EXISTS idx_prematch_odds_hours_before ON prematch_odds(hours_before_match);

-- =============================================================================
-- PREMATCH BETS MAPPING
-- =============================================================================
CREATE TABLE IF NOT EXISTS prematch_bets (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixture(id),
    bookmaker_id INTEGER NOT NULL REFERENCES bookmaker(id),
    bet_market_id INTEGER NOT NULL REFERENCES bet_def_market(id),
    
    -- Bet mapping data
    api_bet_id INTEGER,
    api_bet_name VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(fixture_id, bookmaker_id, bet_market_id)
);

-- =============================================================================
-- FIXTURE EVENTS (Final events after match)
-- =============================================================================
CREATE TABLE IF NOT EXISTS fixture_event (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixture(id),
    
    -- Event details
    event_type VARCHAR(50) NOT NULL,
    event_detail VARCHAR(100),
    event_comments TEXT,
    
    -- Timing
    match_minute INTEGER NOT NULL,
    match_minute_extra INTEGER,
    
    -- Team and player
    team_id INTEGER NOT NULL REFERENCES team(id),
    player_id INTEGER REFERENCES player(id),
    assist_player_id INTEGER REFERENCES player(id),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fixture_event
CREATE INDEX IF NOT EXISTS idx_fixture_event_fixture ON fixture_event(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_event_type ON fixture_event(event_type);
CREATE INDEX IF NOT EXISTS idx_fixture_event_team ON fixture_event(team_id);
CREATE INDEX IF NOT EXISTS idx_fixture_event_player ON fixture_event(player_id);
CREATE INDEX IF NOT EXISTS idx_fixture_event_minute ON fixture_event(match_minute);

-- =============================================================================
-- FIXTURE STATISTICS (Final stats after match)
-- =============================================================================
CREATE TABLE IF NOT EXISTS fixture_statistic (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixture(id),
    team_id INTEGER NOT NULL REFERENCES team(id),
    
    -- Match statistics (same as live_stats_tick but final values)
    shots_on_goal INTEGER DEFAULT 0,
    shots_off_goal INTEGER DEFAULT 0,
    total_shots INTEGER DEFAULT 0,
    blocked_shots INTEGER DEFAULT 0,
    shots_inside_box INTEGER DEFAULT 0,
    shots_outside_box INTEGER DEFAULT 0,
    fouls INTEGER DEFAULT 0,
    corner_kicks INTEGER DEFAULT 0,
    offsides INTEGER DEFAULT 0,
    ball_possession INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    goalkeeper_saves INTEGER DEFAULT 0,
    total_passes INTEGER DEFAULT 0,
    passes_accurate INTEGER DEFAULT 0,
    passes_percentage INTEGER DEFAULT 0,
    expected_goals DECIMAL(4,2) DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(fixture_id, team_id)
);

-- Indexes for fixture_statistic
CREATE INDEX IF NOT EXISTS idx_fixture_statistic_fixture ON fixture_statistic(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_statistic_team ON fixture_statistic(team_id);

-- =============================================================================
-- FIXTURE LINEUPS
-- =============================================================================
CREATE TABLE IF NOT EXISTS fixture_lineup (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixture(id),
    team_id INTEGER NOT NULL REFERENCES team(id),

    -- Formation
    formation VARCHAR(20),

    -- Coach
    coach_id INTEGER,
    coach_name VARCHAR(200),
    coach_photo VARCHAR(255),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint
    UNIQUE(fixture_id, team_id)
);

CREATE TABLE IF NOT EXISTS fixture_lineup_player (
    id SERIAL PRIMARY KEY,
    lineup_id INTEGER NOT NULL REFERENCES fixture_lineup(id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES player(id),

    -- Player details
    player_name VARCHAR(200) NOT NULL,
    player_number INTEGER,
    player_position VARCHAR(50),
    player_grid VARCHAR(10), -- Grid position like "1:1"

    -- Status
    is_starter BOOLEAN DEFAULT TRUE,
    is_substitute BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for lineup tables
CREATE INDEX IF NOT EXISTS idx_fixture_lineup_fixture ON fixture_lineup(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_lineup_team ON fixture_lineup(team_id);
CREATE INDEX IF NOT EXISTS idx_fixture_lineup_player_lineup ON fixture_lineup_player(lineup_id);
CREATE INDEX IF NOT EXISTS idx_fixture_lineup_player_player ON fixture_lineup_player(player_id);

-- =============================================================================
-- PLAYER STATISTICS (Per match)
-- =============================================================================
CREATE TABLE IF NOT EXISTS player_match_statistic (
    id SERIAL PRIMARY KEY,
    fixture_id INTEGER NOT NULL REFERENCES fixture(id),
    team_id INTEGER NOT NULL REFERENCES team(id),
    player_id INTEGER NOT NULL REFERENCES player(id),

    -- Playing time
    minutes_played INTEGER DEFAULT 0,

    -- Offensive stats
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    shots_total INTEGER DEFAULT 0,
    shots_on_target INTEGER DEFAULT 0,

    -- Passing stats
    passes_total INTEGER DEFAULT 0,
    passes_accurate INTEGER DEFAULT 0,
    passes_percentage INTEGER DEFAULT 0,
    key_passes INTEGER DEFAULT 0,

    -- Defensive stats
    tackles INTEGER DEFAULT 0,
    blocks INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    duels_total INTEGER DEFAULT 0,
    duels_won INTEGER DEFAULT 0,

    -- Disciplinary
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    fouls_drawn INTEGER DEFAULT 0,
    fouls_committed INTEGER DEFAULT 0,

    -- Other stats
    offsides INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0, -- For goalkeepers
    penalty_won INTEGER DEFAULT 0,
    penalty_committed INTEGER DEFAULT 0,
    penalty_scored INTEGER DEFAULT 0,
    penalty_missed INTEGER DEFAULT 0,
    penalty_saved INTEGER DEFAULT 0,

    -- Rating
    rating DECIMAL(3,1),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint
    UNIQUE(fixture_id, player_id)
);

-- Indexes for player_match_statistic
CREATE INDEX IF NOT EXISTS idx_player_match_stat_fixture ON player_match_statistic(fixture_id);
CREATE INDEX IF NOT EXISTS idx_player_match_stat_team ON player_match_statistic(team_id);
CREATE INDEX IF NOT EXISTS idx_player_match_stat_player ON player_match_statistic(player_id);
CREATE INDEX IF NOT EXISTS idx_player_match_stat_rating ON player_match_statistic(rating DESC);

-- =============================================================================
-- HEAD TO HEAD STATISTICS
-- =============================================================================
CREATE TABLE IF NOT EXISTS h2h_statistic (
    id SERIAL PRIMARY KEY,
    team1_id INTEGER NOT NULL REFERENCES team(id),
    team2_id INTEGER NOT NULL REFERENCES team(id),

    -- Overall stats
    total_matches INTEGER DEFAULT 0,
    team1_wins INTEGER DEFAULT 0,
    team2_wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,

    -- Goals
    team1_goals_for INTEGER DEFAULT 0,
    team1_goals_against INTEGER DEFAULT 0,
    team2_goals_for INTEGER DEFAULT 0,
    team2_goals_against INTEGER DEFAULT 0,

    -- Last update
    last_match_date DATE,
    last_updated TIMESTAMPTZ DEFAULT NOW(),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint (ensure team1_id < team2_id for consistency)
    UNIQUE(team1_id, team2_id),
    CONSTRAINT chk_h2h_team_order CHECK (team1_id < team2_id)
);

-- Indexes for h2h_statistic
CREATE INDEX IF NOT EXISTS idx_h2h_statistic_team1 ON h2h_statistic(team1_id);
CREATE INDEX IF NOT EXISTS idx_h2h_statistic_team2 ON h2h_statistic(team2_id);
CREATE INDEX IF NOT EXISTS idx_h2h_statistic_last_match ON h2h_statistic(last_match_date DESC);

-- =============================================================================
-- STANDINGS (League tables)
-- =============================================================================
CREATE TABLE IF NOT EXISTS standing (
    id SERIAL PRIMARY KEY,
    league_id INTEGER NOT NULL REFERENCES league(id),
    season_year INTEGER NOT NULL,
    team_id INTEGER NOT NULL REFERENCES team(id),

    -- Position
    rank INTEGER NOT NULL,
    points INTEGER DEFAULT 0,

    -- Matches
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,

    -- Goals
    goals_for INTEGER DEFAULT 0,
    goals_against INTEGER DEFAULT 0,
    goal_difference INTEGER DEFAULT 0,

    -- Form (last 5 matches)
    form VARCHAR(5), -- e.g., "WWDLL"

    -- Status
    status VARCHAR(50), -- e.g., "same", "up", "down"
    description TEXT,

    -- Home/Away breakdown
    home_matches_played INTEGER DEFAULT 0,
    home_wins INTEGER DEFAULT 0,
    home_draws INTEGER DEFAULT 0,
    home_losses INTEGER DEFAULT 0,
    home_goals_for INTEGER DEFAULT 0,
    home_goals_against INTEGER DEFAULT 0,

    away_matches_played INTEGER DEFAULT 0,
    away_wins INTEGER DEFAULT 0,
    away_draws INTEGER DEFAULT 0,
    away_losses INTEGER DEFAULT 0,
    away_goals_for INTEGER DEFAULT 0,
    away_goals_against INTEGER DEFAULT 0,

    -- Metadata
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint
    UNIQUE(league_id, season_year, team_id)
);

-- Indexes for standing
CREATE INDEX IF NOT EXISTS idx_standing_league_season ON standing(league_id, season_year);
CREATE INDEX IF NOT EXISTS idx_standing_team ON standing(team_id);
CREATE INDEX IF NOT EXISTS idx_standing_rank ON standing(rank);
CREATE INDEX IF NOT EXISTS idx_standing_points ON standing(points DESC);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- =============================================================================
CREATE TRIGGER update_fixture_updated_at BEFORE UPDATE ON fixture
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_standing_updated_at BEFORE UPDATE ON standing
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
