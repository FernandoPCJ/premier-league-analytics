-- ============================================================
-- PREMIER LEAGUE ANALYTICS
-- Criação da estrutura inicial do banco de dados
-- ============================================================


-- ============================================================
-- 1. TEMPORADAS
-- ============================================================

CREATE TABLE seasons (
    id SERIAL PRIMARY KEY,
    season VARCHAR(7) NOT NULL UNIQUE
);


-- ============================================================
-- 2. TIMES
-- ============================================================

CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);


-- ============================================================
-- 3. PARTIDAS
-- ============================================================

CREATE TABLE matches (
    id BIGSERIAL PRIMARY KEY,

    season_id INTEGER NOT NULL,

    division VARCHAR(10) NOT NULL,
    match_date DATE NOT NULL,

    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,

    home_goals SMALLINT NOT NULL,
    away_goals SMALLINT NOT NULL,
    full_time_result CHAR(1) NOT NULL,

    home_half_time_goals SMALLINT NOT NULL,
    away_half_time_goals SMALLINT NOT NULL,
    half_time_result CHAR(1) NOT NULL,

    referee VARCHAR(120) NOT NULL,

    home_shots SMALLINT NOT NULL,
    away_shots SMALLINT NOT NULL,

    home_shots_on_target SMALLINT NOT NULL,
    away_shots_on_target SMALLINT NOT NULL,

    home_fouls SMALLINT NOT NULL,
    away_fouls SMALLINT NOT NULL,

    home_corners SMALLINT NOT NULL,
    away_corners SMALLINT NOT NULL,

    home_yellow_cards SMALLINT NOT NULL,
    away_yellow_cards SMALLINT NOT NULL,

    home_red_cards SMALLINT NOT NULL,
    away_red_cards SMALLINT NOT NULL,

    CONSTRAINT fk_matches_season
        FOREIGN KEY (season_id)
        REFERENCES seasons(id),

    CONSTRAINT fk_matches_home_team
        FOREIGN KEY (home_team_id)
        REFERENCES teams(id),

    CONSTRAINT fk_matches_away_team
        FOREIGN KEY (away_team_id)
        REFERENCES teams(id),

    CONSTRAINT chk_different_teams
        CHECK (home_team_id <> away_team_id),

    CONSTRAINT chk_full_time_result
        CHECK (full_time_result IN ('H', 'D', 'A')),

    CONSTRAINT chk_half_time_result
        CHECK (half_time_result IN ('H', 'D', 'A')),

    CONSTRAINT uq_match
        UNIQUE (
            season_id,
            match_date,
            home_team_id,
            away_team_id
        )
);