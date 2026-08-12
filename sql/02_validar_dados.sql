-- ============================================================
-- PREMIER LEAGUE ANALYTICS
-- Validação dos dados carregados
-- ============================================================


-- ============================================================
-- 1. QUANTIDADE DE REGISTROS
-- ============================================================

SELECT COUNT(*) AS total_temporadas
FROM seasons;

SELECT COUNT(*) AS total_clubes
FROM teams;

SELECT COUNT(*) AS total_partidas
FROM matches;


-- ============================================================
-- 2. LISTAR TEMPORADAS
-- ============================================================

SELECT *
FROM seasons
ORDER BY season;


-- ============================================================
-- 3. LISTAR CLUBES
-- ============================================================

SELECT *
FROM teams
ORDER BY name;


-- ============================================================
-- 4. PARTIDAS POR TEMPORADA
-- ============================================================

SELECT
    s.season,
    COUNT(*) AS partidas
FROM matches m
JOIN seasons s
    ON s.id = m.season_id
GROUP BY s.season
ORDER BY s.season;


-- ============================================================
-- 5. VISUALIZAR 20 PARTIDAS
-- ============================================================

SELECT
    s.season,
    m.match_date,
    home.name AS home_team,
    away.name AS away_team,
    m.home_goals,
    m.away_goals,
    m.full_time_result
FROM matches m

JOIN seasons s
    ON s.id = m.season_id

JOIN teams home
    ON home.id = m.home_team_id

JOIN teams away
    ON away.id = m.away_team_id

ORDER BY
    m.match_date,
    m.id

LIMIT 20;


-- ============================================================
-- 6. DISTRIBUIÇÃO DOS RESULTADOS
-- ============================================================

SELECT
    full_time_result,
    COUNT(*) AS quantidade
FROM matches
GROUP BY full_time_result
ORDER BY full_time_result;


-- ============================================================
-- 7. VERIFICAR DUPLICIDADES
-- ============================================================

SELECT
    season_id,
    match_date,
    home_team_id,
    away_team_id,
    COUNT(*)
FROM matches
GROUP BY
    season_id,
    match_date,
    home_team_id,
    away_team_id
HAVING COUNT(*) > 1;