-- Footy-Brain v5 Database Seeds - Bootstrap Static Data
-- This file populates initial static data for countries, leagues, bet definitions, etc.

-- =============================================================================
-- COUNTRIES SEED DATA
-- =============================================================================
INSERT INTO country (id, name, code, flag) VALUES
(39, 'England', 'GB', 'https://media.api-sports.io/flags/gb.svg'),
(6, 'Spain', 'ES', 'https://media.api-sports.io/flags/es.svg'),
(25, 'Germany', 'DE', 'https://media.api-sports.io/flags/de.svg'),
(27, 'Italy', 'IT', 'https://media.api-sports.io/flags/it.svg'),
(2, 'France', 'FR', 'https://media.api-sports.io/flags/fr.svg'),
(32, 'Netherlands', 'NL', 'https://media.api-sports.io/flags/nl.svg'),
(17, 'Portugal', 'PT', 'https://media.api-sports.io/flags/pt.svg'),
(19, 'Turkey', 'TR', 'https://media.api-sports.io/flags/tr.svg'),
(21, 'Brazil', 'BR', 'https://media.api-sports.io/flags/br.svg'),
(26, 'Argentina', 'AR', 'https://media.api-sports.io/flags/ar.svg'),
(11, 'Belgium', 'BE', 'https://media.api-sports.io/flags/be.svg'),
(15, 'Austria', 'AT', 'https://media.api-sports.io/flags/at.svg'),
(18, 'Switzerland', 'CH', 'https://media.api-sports.io/flags/ch.svg'),
(22, 'Poland', 'PL', 'https://media.api-sports.io/flags/pl.svg'),
(24, 'Czech-Republic', 'CZ', 'https://media.api-sports.io/flags/cz.svg')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    code = EXCLUDED.code,
    flag = EXCLUDED.flag,
    updated_at = NOW();

-- =============================================================================
-- LEAGUES SEED DATA
-- =============================================================================
INSERT INTO league (id, name, type, logo, country_id) VALUES
-- England
(39, 'Premier League', 'League', 'https://media.api-sports.io/football/leagues/39.png', 39),
(40, 'Championship', 'League', 'https://media.api-sports.io/football/leagues/40.png', 39),
(41, 'League One', 'League', 'https://media.api-sports.io/football/leagues/41.png', 39),
(42, 'League Two', 'League', 'https://media.api-sports.io/football/leagues/42.png', 39),
(45, 'FA Cup', 'Cup', 'https://media.api-sports.io/football/leagues/45.png', 39),
(48, 'League Cup', 'Cup', 'https://media.api-sports.io/football/leagues/48.png', 39),

-- Spain
(140, 'La Liga', 'League', 'https://media.api-sports.io/football/leagues/140.png', 6),
(141, 'Segunda División', 'League', 'https://media.api-sports.io/football/leagues/141.png', 6),
(143, 'Copa del Rey', 'Cup', 'https://media.api-sports.io/football/leagues/143.png', 6),

-- Germany
(78, 'Bundesliga', 'League', 'https://media.api-sports.io/football/leagues/78.png', 25),
(79, '2. Bundesliga', 'League', 'https://media.api-sports.io/football/leagues/79.png', 25),
(81, 'DFB Pokal', 'Cup', 'https://media.api-sports.io/football/leagues/81.png', 25),

-- Italy
(135, 'Serie A', 'League', 'https://media.api-sports.io/football/leagues/135.png', 27),
(136, 'Serie B', 'League', 'https://media.api-sports.io/football/leagues/136.png', 27),
(137, 'Coppa Italia', 'Cup', 'https://media.api-sports.io/football/leagues/137.png', 27),

-- France
(61, 'Ligue 1', 'League', 'https://media.api-sports.io/football/leagues/61.png', 2),
(62, 'Ligue 2', 'League', 'https://media.api-sports.io/football/leagues/62.png', 2),
(66, 'Coupe de France', 'Cup', 'https://media.api-sports.io/football/leagues/66.png', 2),

-- Netherlands
(88, 'Eredivisie', 'League', 'https://media.api-sports.io/football/leagues/88.png', 32),
(89, 'Eerste Divisie', 'League', 'https://media.api-sports.io/football/leagues/89.png', 32),

-- Portugal
(94, 'Primeira Liga', 'League', 'https://media.api-sports.io/football/leagues/94.png', 17),
(95, 'Segunda Liga', 'League', 'https://media.api-sports.io/football/leagues/95.png', 17),

-- Turkey
(203, 'Süper Lig', 'League', 'https://media.api-sports.io/football/leagues/203.png', 19),

-- International
(2, 'UEFA Champions League', 'Cup', 'https://media.api-sports.io/football/leagues/2.png', NULL),
(3, 'UEFA Europa League', 'Cup', 'https://media.api-sports.io/football/leagues/3.png', NULL),
(848, 'UEFA Europa Conference League', 'Cup', 'https://media.api-sports.io/football/leagues/848.png', NULL),
(1, 'World Cup', 'Cup', 'https://media.api-sports.io/football/leagues/1.png', NULL),
(4, 'UEFA European Championship', 'Cup', 'https://media.api-sports.io/football/leagues/4.png', NULL)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    type = EXCLUDED.type,
    logo = EXCLUDED.logo,
    country_id = EXCLUDED.country_id,
    updated_at = NOW();

-- =============================================================================
-- SEASONS SEED DATA
-- =============================================================================
INSERT INTO season (year, start_date, end_date, current) VALUES
(2024, '2024-08-01', '2025-05-31', TRUE),
(2023, '2023-08-01', '2024-05-31', FALSE),
(2022, '2022-08-01', '2023-05-31', FALSE),
(2025, '2025-08-01', '2026-05-31', FALSE),
(2026, '2026-08-01', '2027-05-31', FALSE)
ON CONFLICT (year) DO UPDATE SET
    start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date,
    current = EXCLUDED.current,
    updated_at = NOW();

-- =============================================================================
-- BOOKMAKERS SEED DATA
-- =============================================================================
INSERT INTO bookmaker (id, name) VALUES
(6, 'Bwin'),
(8, 'Bet365'),
(11, 'Unibet'),
(16, '10Bet'),
(18, '18Bet'),
(23, 'Betfair'),
(25, 'Betway'),
(28, 'Ladbrokes'),
(29, 'William Hill'),
(31, 'Pinnacle'),
(35, 'Marathonbet'),
(44, 'Betclic'),
(45, 'Betsson'),
(49, 'SBO'),
(50, 'Sportingbet')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    updated_at = NOW();

-- =============================================================================
-- BET MARKET DEFINITIONS
-- =============================================================================
INSERT INTO bet_def_market (id, name, description) VALUES
(1, 'Match Winner', '1X2 - Home/Draw/Away'),
(2, 'Over/Under 2.5', 'Total goals over or under 2.5'),
(3, 'Both Teams To Score', 'Both teams score - Yes/No'),
(4, 'Double Chance', '1X, 12, X2'),
(5, 'Asian Handicap', 'Asian handicap betting'),
(8, 'Over/Under 1.5', 'Total goals over or under 1.5'),
(9, 'Over/Under 3.5', 'Total goals over or under 3.5'),
(12, 'Correct Score', 'Exact final score'),
(15, 'First Half Winner', '1X2 for first half only'),
(16, 'Second Half Winner', '1X2 for second half only'),
(18, 'Handicap', 'European handicap'),
(19, 'Goals O/U First Half', 'First half goals over/under'),
(20, 'HT/FT', 'Half time / Full time result'),
(21, 'Team To Score First', 'Which team scores first'),
(22, 'Team To Score Last', 'Which team scores last'),
(25, 'To Qualify', 'Team to qualify (knockout matches)'),
(26, 'Exact Goals Number', 'Exact number of goals in match')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description;

-- =============================================================================
-- BET VALUES FOR COMMON MARKETS
-- =============================================================================

-- Match Winner (1X2)
INSERT INTO bet_def_value (market_id, value, description) VALUES
(1, '1', 'Home team wins'),
(1, 'X', 'Draw'),
(1, '2', 'Away team wins')
ON CONFLICT (market_id, value) DO NOTHING;

-- Over/Under 2.5
INSERT INTO bet_def_value (market_id, value, description) VALUES
(2, 'Over 2.5', 'More than 2.5 goals'),
(2, 'Under 2.5', 'Less than 2.5 goals')
ON CONFLICT (market_id, value) DO NOTHING;

-- Both Teams To Score
INSERT INTO bet_def_value (market_id, value, description) VALUES
(3, 'Yes', 'Both teams score'),
(3, 'No', 'At least one team does not score')
ON CONFLICT (market_id, value) DO NOTHING;

-- Double Chance
INSERT INTO bet_def_value (market_id, value, description) VALUES
(4, '1X', 'Home team wins or draw'),
(4, '12', 'Home team wins or away team wins'),
(4, 'X2', 'Draw or away team wins')
ON CONFLICT (market_id, value) DO NOTHING;

-- Over/Under 1.5
INSERT INTO bet_def_value (market_id, value, description) VALUES
(8, 'Over 1.5', 'More than 1.5 goals'),
(8, 'Under 1.5', 'Less than 1.5 goals')
ON CONFLICT (market_id, value) DO NOTHING;

-- Over/Under 3.5
INSERT INTO bet_def_value (market_id, value, description) VALUES
(9, 'Over 3.5', 'More than 3.5 goals'),
(9, 'Under 3.5', 'Less than 3.5 goals')
ON CONFLICT (market_id, value) DO NOTHING;

-- First Half Winner
INSERT INTO bet_def_value (market_id, value, description) VALUES
(15, '1', 'Home team leads at half time'),
(15, 'X', 'Draw at half time'),
(15, '2', 'Away team leads at half time')
ON CONFLICT (market_id, value) DO NOTHING;

-- Second Half Winner
INSERT INTO bet_def_value (market_id, value, description) VALUES
(16, '1', 'Home team wins second half'),
(16, 'X', 'Second half ends in draw'),
(16, '2', 'Away team wins second half')
ON CONFLICT (market_id, value) DO NOTHING;

-- =============================================================================
-- TIMEZONE DEFINITIONS
-- =============================================================================
INSERT INTO timezone_def (name, offset_hours, offset_minutes, description) VALUES
('UTC', 0, 0, 'Coordinated Universal Time'),
('GMT', 0, 0, 'Greenwich Mean Time'),
('CET', 1, 0, 'Central European Time'),
('EET', 2, 0, 'Eastern European Time'),
('BST', 1, 0, 'British Summer Time'),
('CEST', 2, 0, 'Central European Summer Time'),
('EEST', 3, 0, 'Eastern European Summer Time'),
('EST', -5, 0, 'Eastern Standard Time'),
('PST', -8, 0, 'Pacific Standard Time'),
('JST', 9, 0, 'Japan Standard Time'),
('AEST', 10, 0, 'Australian Eastern Standard Time'),
('TRT', 3, 0, 'Turkey Time')
ON CONFLICT (name) DO UPDATE SET
    offset_hours = EXCLUDED.offset_hours,
    offset_minutes = EXCLUDED.offset_minutes,
    description = EXCLUDED.description;

-- =============================================================================
-- SAMPLE VENUES (Major stadiums)
-- =============================================================================
INSERT INTO venue (id, name, address, city, country_id, capacity, surface, image) VALUES
(556, 'Old Trafford', 'Sir Matt Busby Way', 'Manchester', 39, 76000, 'grass', 'https://media.api-sports.io/football/venues/556.png'),
(550, 'Stamford Bridge', 'Fulham Road', 'London', 39, 40834, 'grass', 'https://media.api-sports.io/football/venues/550.png'),
(554, 'Anfield', 'Anfield Road', 'Liverpool', 39, 54074, 'grass', 'https://media.api-sports.io/football/venues/554.png'),
(555, 'Emirates Stadium', 'Queensland Road', 'London', 39, 60704, 'grass', 'https://media.api-sports.io/football/venues/555.png'),
(562, 'Etihad Stadium', 'Etihad Campus', 'Manchester', 39, 55097, 'grass', 'https://media.api-sports.io/football/venues/562.png'),
(558, 'Tottenham Hotspur Stadium', '782 High Road', 'London', 39, 62850, 'grass', 'https://media.api-sports.io/football/venues/558.png'),
(738, 'Santiago Bernabéu', 'Avenida de Concha Espina 1', 'Madrid', 6, 81044, 'grass', 'https://media.api-sports.io/football/venues/738.png'),
(739, 'Camp Nou', 'C. d\'Aristides Maillol 12', 'Barcelona', 6, 99354, 'grass', 'https://media.api-sports.io/football/venues/739.png'),
(743, 'Allianz Arena', 'Werner-Heisenberg-Allee 25', 'Munich', 25, 75000, 'grass', 'https://media.api-sports.io/football/venues/743.png'),
(907, 'San Siro', 'Piazzale Angelo Moratti', 'Milan', 27, 80018, 'grass', 'https://media.api-sports.io/football/venues/907.png')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    address = EXCLUDED.address,
    city = EXCLUDED.city,
    country_id = EXCLUDED.country_id,
    capacity = EXCLUDED.capacity,
    surface = EXCLUDED.surface,
    image = EXCLUDED.image,
    updated_at = NOW();

-- =============================================================================
-- SYSTEM CONFIGURATION UPDATES
-- =============================================================================
UPDATE system_config SET 
    value = NOW()::TEXT,
    updated_at = NOW()
WHERE key = 'last_bootstrap_seed';

-- Insert bootstrap completion marker
INSERT INTO system_config (key, value, description) VALUES
('bootstrap_completed', 'true', 'Indicates that bootstrap seeding is completed'),
('bootstrap_version', '5.0.0', 'Version of bootstrap data'),
('bootstrap_date', NOW()::TEXT, 'Date when bootstrap was completed')
ON CONFLICT (key) DO UPDATE SET 
    value = EXCLUDED.value,
    updated_at = NOW();

-- =============================================================================
-- VERIFICATION QUERIES (for logging)
-- =============================================================================

-- Log seeding statistics
DO $$
DECLARE
    country_count INTEGER;
    league_count INTEGER;
    bookmaker_count INTEGER;
    market_count INTEGER;
    venue_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO country_count FROM country;
    SELECT COUNT(*) INTO league_count FROM league;
    SELECT COUNT(*) INTO bookmaker_count FROM bookmaker;
    SELECT COUNT(*) INTO market_count FROM bet_def_market;
    SELECT COUNT(*) INTO venue_count FROM venue;
    
    INSERT INTO audit_log (table_name, record_id, operation, new_values, changed_by)
    VALUES ('bootstrap_seed', 'completion', 'INSERT', 
            jsonb_build_object(
                'countries_seeded', country_count,
                'leagues_seeded', league_count,
                'bookmakers_seeded', bookmaker_count,
                'bet_markets_seeded', market_count,
                'venues_seeded', venue_count,
                'completion_time', NOW()
            ),
            'bootstrap_process');
END $$;
