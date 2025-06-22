-- Footy-Brain v5 Database Schema - Continuous Aggregates
-- This file creates TimescaleDB continuous aggregates for efficient querying
-- Execute order: 20 (after fact tables)

-- =============================================================================
-- LIVE ODDS TICK OHLC (Open, High, Low, Close) - 1 MINUTE
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS live_odds_tick_ohlc_1m
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 minute', timestamp) AS bucket,
    fixture_id,
    bookmaker_id,
    bet_market_id,
    bet_value,
    
    -- OHLC data
    FIRST(odd_value, timestamp) AS open_odd,
    MAX(odd_value) AS high_odd,
    MIN(odd_value) AS low_odd,
    LAST(odd_value, timestamp) AS close_odd,
    
    -- Statistics
    COUNT(*) AS tick_count,
    AVG(odd_value) AS avg_odd,
    STDDEV(odd_value) AS stddev_odd,
    
    -- Timing
    MIN(timestamp) AS first_timestamp,
    MAX(timestamp) AS last_timestamp
FROM live_odds_tick
GROUP BY bucket, fixture_id, bookmaker_id, bet_market_id, bet_value;

-- Add refresh policy for 1-minute OHLC
SELECT add_continuous_aggregate_policy('live_odds_tick_ohlc_1m',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute');

-- =============================================================================
-- LIVE ODDS TICK OHLC (Open, High, Low, Close) - 5 MINUTES
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS live_odds_tick_ohlc_5m
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('5 minutes', timestamp) AS bucket,
    fixture_id,
    bookmaker_id,
    bet_market_id,
    bet_value,
    
    -- OHLC data
    FIRST(odd_value, timestamp) AS open_odd,
    MAX(odd_value) AS high_odd,
    MIN(odd_value) AS low_odd,
    LAST(odd_value, timestamp) AS close_odd,
    
    -- Statistics
    COUNT(*) AS tick_count,
    AVG(odd_value) AS avg_odd,
    STDDEV(odd_value) AS stddev_odd,
    
    -- Movement analysis
    (LAST(odd_value, timestamp) - FIRST(odd_value, timestamp)) AS odd_change,
    ((LAST(odd_value, timestamp) - FIRST(odd_value, timestamp)) / FIRST(odd_value, timestamp) * 100) AS odd_change_percent,
    
    -- Timing
    MIN(timestamp) AS first_timestamp,
    MAX(timestamp) AS last_timestamp
FROM live_odds_tick
GROUP BY bucket, fixture_id, bookmaker_id, bet_market_id, bet_value;

-- Add refresh policy for 5-minute OHLC
SELECT add_continuous_aggregate_policy('live_odds_tick_ohlc_5m',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes');

-- =============================================================================
-- LIVE EVENTS SUMMARY - 1 MINUTE
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS live_event_summary_1m
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 minute', timestamp) AS bucket,
    fixture_id,
    team_id,
    event_type,
    
    -- Event counts
    COUNT(*) AS event_count,
    
    -- Player involvement
    COUNT(DISTINCT player_id) AS unique_players,
    
    -- Match timing
    MIN(match_minute) AS first_minute,
    MAX(match_minute) AS last_minute,
    AVG(match_minute) AS avg_minute,
    
    -- Timing
    MIN(timestamp) AS first_timestamp,
    MAX(timestamp) AS last_timestamp
FROM live_event_tick
GROUP BY bucket, fixture_id, team_id, event_type;

-- Add refresh policy for event summary
SELECT add_continuous_aggregate_policy('live_event_summary_1m',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute');

-- =============================================================================
-- LIVE STATS PROGRESSION - 5 MINUTES
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS live_stats_progression_5m
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('5 minutes', timestamp) AS bucket,
    fixture_id,
    team_id,
    
    -- Latest stats (using LAST function)
    LAST(shots_on_goal, timestamp) AS shots_on_goal,
    LAST(shots_off_goal, timestamp) AS shots_off_goal,
    LAST(total_shots, timestamp) AS total_shots,
    LAST(ball_possession, timestamp) AS ball_possession,
    LAST(corner_kicks, timestamp) AS corner_kicks,
    LAST(fouls, timestamp) AS fouls,
    LAST(yellow_cards, timestamp) AS yellow_cards,
    LAST(red_cards, timestamp) AS red_cards,
    LAST(total_passes, timestamp) AS total_passes,
    LAST(passes_accurate, timestamp) AS passes_accurate,
    LAST(passes_percentage, timestamp) AS passes_percentage,
    
    -- Changes during the period
    (LAST(total_shots, timestamp) - FIRST(total_shots, timestamp)) AS shots_change,
    (LAST(ball_possession, timestamp) - FIRST(ball_possession, timestamp)) AS possession_change,
    (LAST(corner_kicks, timestamp) - FIRST(corner_kicks, timestamp)) AS corners_change,
    (LAST(fouls, timestamp) - FIRST(fouls, timestamp)) AS fouls_change,
    
    -- Statistics
    COUNT(*) AS tick_count,
    MIN(match_minute) AS first_minute,
    MAX(match_minute) AS last_minute,
    
    -- Timing
    MIN(timestamp) AS first_timestamp,
    MAX(timestamp) AS last_timestamp
FROM live_stats_tick
GROUP BY bucket, fixture_id, team_id;

-- Add refresh policy for stats progression
SELECT add_continuous_aggregate_policy('live_stats_progression_5m',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes');

-- =============================================================================
-- MATCH LIVE FRAME (1 MINUTE COMPREHENSIVE SUMMARY)
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS match_live_frame
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 minute', lo.timestamp) AS bucket,
    lo.fixture_id,
    
    -- Match context
    f.home_team_id,
    f.away_team_id,
    f.status_short,
    f.status_elapsed,
    f.home_goals,
    f.away_goals,
    
    -- Odds summary (1X2 market only for simplicity)
    AVG(CASE WHEN lo.bet_value = '1' THEN lo.odd_value END) AS avg_home_win_odd,
    AVG(CASE WHEN lo.bet_value = 'X' THEN lo.odd_value END) AS avg_draw_odd,
    AVG(CASE WHEN lo.bet_value = '2' THEN lo.odd_value END) AS avg_away_win_odd,
    
    -- Odds movement
    (LAST(CASE WHEN lo.bet_value = '1' THEN lo.odd_value END, lo.timestamp) - 
     FIRST(CASE WHEN lo.bet_value = '1' THEN lo.odd_value END, lo.timestamp)) AS home_odd_change,
    (LAST(CASE WHEN lo.bet_value = '2' THEN lo.odd_value END, lo.timestamp) - 
     FIRST(CASE WHEN lo.bet_value = '2' THEN lo.odd_value END, lo.timestamp)) AS away_odd_change,
    
    -- Event counts
    COUNT(DISTINCT le.id) AS total_events,
    COUNT(DISTINCT CASE WHEN le.event_type = 'Goal' THEN le.id END) AS goals,
    COUNT(DISTINCT CASE WHEN le.event_type = 'Card' THEN le.id END) AS cards,
    COUNT(DISTINCT CASE WHEN le.event_type = 'subst' THEN le.id END) AS substitutions,
    
    -- Activity level
    COUNT(DISTINCT lo.id) AS odds_ticks,
    COUNT(DISTINCT le.id) AS event_ticks,
    
    -- Timing
    MIN(lo.timestamp) AS first_timestamp,
    MAX(lo.timestamp) AS last_timestamp
FROM live_odds_tick lo
LEFT JOIN fixture f ON lo.fixture_id = f.id
LEFT JOIN live_event_tick le ON lo.fixture_id = le.fixture_id 
    AND time_bucket('1 minute', le.timestamp) = time_bucket('1 minute', lo.timestamp)
WHERE lo.bet_market_id = 1  -- Assuming market_id 1 is Match Winner (1X2)
GROUP BY bucket, lo.fixture_id, f.home_team_id, f.away_team_id, f.status_short, 
         f.status_elapsed, f.home_goals, f.away_goals;

-- Add refresh policy for match live frame
SELECT add_continuous_aggregate_policy('match_live_frame',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute');

-- =============================================================================
-- DAILY FIXTURE SUMMARY
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_fixture_summary
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', date) AS bucket,
    league_id,
    
    -- Match counts
    COUNT(*) AS total_matches,
    COUNT(CASE WHEN status_short = 'FT' THEN 1 END) AS finished_matches,
    COUNT(CASE WHEN status_short IN ('1H', '2H', 'HT', 'ET') THEN 1 END) AS live_matches,
    COUNT(CASE WHEN status_short = 'NS' THEN 1 END) AS upcoming_matches,
    
    -- Goals statistics
    AVG(home_goals + away_goals) AS avg_total_goals,
    MAX(home_goals + away_goals) AS max_total_goals,
    MIN(home_goals + away_goals) AS min_total_goals,
    
    -- Results distribution
    COUNT(CASE WHEN home_goals > away_goals THEN 1 END) AS home_wins,
    COUNT(CASE WHEN home_goals = away_goals THEN 1 END) AS draws,
    COUNT(CASE WHEN home_goals < away_goals THEN 1 END) AS away_wins,
    
    -- Home advantage
    AVG(home_goals::DECIMAL / NULLIF(away_goals, 0)) AS home_goal_ratio,
    (COUNT(CASE WHEN home_goals > away_goals THEN 1 END)::DECIMAL / 
     NULLIF(COUNT(CASE WHEN status_short = 'FT' THEN 1 END), 0) * 100) AS home_win_percentage
FROM fixture
GROUP BY bucket, league_id;

-- Add refresh policy for daily fixture summary
SELECT add_continuous_aggregate_policy('daily_fixture_summary',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 hour');

-- =============================================================================
-- BOOKMAKER ODDS COMPARISON
-- =============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS bookmaker_odds_comparison_5m
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('5 minutes', timestamp) AS bucket,
    fixture_id,
    bet_market_id,
    bet_value,
    
    -- Bookmaker statistics
    COUNT(DISTINCT bookmaker_id) AS bookmaker_count,
    AVG(odd_value) AS avg_odd,
    MIN(odd_value) AS min_odd,
    MAX(odd_value) AS max_odd,
    STDDEV(odd_value) AS stddev_odd,
    
    -- Best odds tracking
    FIRST(bookmaker_id, odd_value) AS best_odd_bookmaker_id,
    MAX(odd_value) AS best_odd_value,
    
    -- Market efficiency
    (MAX(odd_value) - MIN(odd_value)) AS odd_spread,
    ((MAX(odd_value) - MIN(odd_value)) / AVG(odd_value) * 100) AS odd_spread_percent,
    
    -- Timing
    MIN(timestamp) AS first_timestamp,
    MAX(timestamp) AS last_timestamp
FROM live_odds_tick
GROUP BY bucket, fixture_id, bet_market_id, bet_value
HAVING COUNT(DISTINCT bookmaker_id) >= 2;  -- Only include when multiple bookmakers

-- Add refresh policy for bookmaker comparison
SELECT add_continuous_aggregate_policy('bookmaker_odds_comparison_5m',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes');

-- =============================================================================
-- INDEXES FOR CONTINUOUS AGGREGATES
-- =============================================================================

-- Indexes for live_odds_tick_ohlc_1m
CREATE INDEX IF NOT EXISTS idx_live_odds_ohlc_1m_bucket ON live_odds_tick_ohlc_1m(bucket DESC);
CREATE INDEX IF NOT EXISTS idx_live_odds_ohlc_1m_fixture ON live_odds_tick_ohlc_1m(fixture_id, bucket DESC);

-- Indexes for live_odds_tick_ohlc_5m
CREATE INDEX IF NOT EXISTS idx_live_odds_ohlc_5m_bucket ON live_odds_tick_ohlc_5m(bucket DESC);
CREATE INDEX IF NOT EXISTS idx_live_odds_ohlc_5m_fixture ON live_odds_tick_ohlc_5m(fixture_id, bucket DESC);

-- Indexes for live_event_summary_1m
CREATE INDEX IF NOT EXISTS idx_live_event_summary_1m_bucket ON live_event_summary_1m(bucket DESC);
CREATE INDEX IF NOT EXISTS idx_live_event_summary_1m_fixture ON live_event_summary_1m(fixture_id, bucket DESC);

-- Indexes for live_stats_progression_5m
CREATE INDEX IF NOT EXISTS idx_live_stats_prog_5m_bucket ON live_stats_progression_5m(bucket DESC);
CREATE INDEX IF NOT EXISTS idx_live_stats_prog_5m_fixture ON live_stats_progression_5m(fixture_id, bucket DESC);

-- Indexes for match_live_frame
CREATE INDEX IF NOT EXISTS idx_match_live_frame_bucket ON match_live_frame(bucket DESC);
CREATE INDEX IF NOT EXISTS idx_match_live_frame_fixture ON match_live_frame(fixture_id, bucket DESC);

-- Indexes for daily_fixture_summary
CREATE INDEX IF NOT EXISTS idx_daily_fixture_summary_bucket ON daily_fixture_summary(bucket DESC);
CREATE INDEX IF NOT EXISTS idx_daily_fixture_summary_league ON daily_fixture_summary(league_id, bucket DESC);

-- Indexes for bookmaker_odds_comparison_5m
CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_comp_5m_bucket ON bookmaker_odds_comparison_5m(bucket DESC);
CREATE INDEX IF NOT EXISTS idx_bookmaker_odds_comp_5m_fixture ON bookmaker_odds_comparison_5m(fixture_id, bucket DESC);
