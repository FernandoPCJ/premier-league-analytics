import streamlit as st
import plotly.express as px
import pandas as pd

from utils.database import executar_query


# ==================================================
# CABEÇALHO
# ==================================================

st.title("⚽ Premier League Analytics")

st.subheader(
    "Análise interativa da Premier League"
)

st.write(
    "Explore dados ofensivos, defensivos, disciplinares "
    "e estatísticos das temporadas de 2016/17 a 2025/26."
)


# ==================================================
# FILTROS
# ==================================================

query_temporadas = """
SELECT
    id,
    season
FROM seasons
ORDER BY season;
"""

temporadas_df = executar_query(query_temporadas)

opcoes_temporadas = (
    ["Todas"]
    + temporadas_df["season"].tolist()
)


# --------------------------------------------------
# Filtros lado a lado
# --------------------------------------------------

col_filtro1, col_filtro2 = st.columns(2)


with col_filtro1:

    temporada_selecionada = st.selectbox(
        "Temporada:",
        opcoes_temporadas
    )


if temporada_selecionada == "Todas":

    season_id = None

else:

    season_id = int(
        temporadas_df.loc[
            temporadas_df["season"]
            == temporada_selecionada,
            "id"
        ].iloc[0]
    )


# --------------------------------------------------
# Buscar clubes disponíveis
# --------------------------------------------------

if season_id is None:

    query_lista_clubes = """
    SELECT
        id,
        name
    FROM teams
    ORDER BY name;
    """

else:

    query_lista_clubes = f"""
    SELECT DISTINCT
        t.id,
        t.name

    FROM teams t

    JOIN (
        SELECT
            home_team_id AS team_id
        FROM matches
        WHERE season_id = {season_id}

        UNION

        SELECT
            away_team_id AS team_id
        FROM matches
        WHERE season_id = {season_id}
    ) participantes

        ON participantes.team_id = t.id

    ORDER BY
        t.name;
    """


clubes_df = executar_query(
    query_lista_clubes
)


opcoes_clubes = (
    ["Todos"]
    + clubes_df["name"].tolist()
)


# --------------------------------------------------
# Filtro de clube
# --------------------------------------------------

with col_filtro2:

    clube_selecionado = st.selectbox(
        "Clube:",
        opcoes_clubes
    )


if clube_selecionado == "Todos":

    club_id = None

else:

    club_id = int(
        clubes_df.loc[
            clubes_df["name"]
            == clube_selecionado,
            "id"
        ].iloc[0]
    )


# ==================================================
# KPIs GERAIS
# ==================================================

if season_id is None:

    query_kpis = """
    SELECT
        COUNT(*) AS partidas,
        COUNT(DISTINCT season_id) AS temporadas,
        SUM(home_goals + away_goals) AS total_gols
    FROM matches;
    """

else:

    query_kpis = f"""
    SELECT
        COUNT(*) AS partidas,
        COUNT(DISTINCT season_id) AS temporadas,
        SUM(home_goals + away_goals) AS total_gols
    FROM matches
    WHERE season_id = {season_id};
    """


# --------------------------------------------------
# Total de clubes
# --------------------------------------------------

if season_id is None:

    query_clubes = """
    SELECT
        COUNT(DISTINCT team_id) AS clubes
    FROM (
        SELECT
            home_team_id AS team_id
        FROM matches

        UNION

        SELECT
            away_team_id AS team_id
        FROM matches
    ) AS clubes_participantes;
    """

else:

    query_clubes = f"""
    SELECT
        COUNT(DISTINCT team_id) AS clubes
    FROM (
        SELECT
            home_team_id AS team_id
        FROM matches
        WHERE season_id = {season_id}

        UNION

        SELECT
            away_team_id AS team_id
        FROM matches
        WHERE season_id = {season_id}
    ) AS clubes_participantes;
    """


# --------------------------------------------------
# Executar consultas dos KPIs
# --------------------------------------------------

kpis = executar_query(
    query_kpis
)

clubes = executar_query(
    query_clubes
)


# --------------------------------------------------
# Valores dos KPIs
# --------------------------------------------------

total_partidas = int(
    kpis.loc[0, "partidas"]
)

total_temporadas = int(
    kpis.loc[0, "temporadas"]
)

total_gols = int(
    kpis.loc[0, "total_gols"]
)

total_clubes = int(
    clubes.loc[0, "clubes"]
)


# --------------------------------------------------
# Cards gerais
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="Temporadas",
        value=total_temporadas
    )


with col2:

    st.metric(
        label="Partidas",
        value=f"{total_partidas:,}".replace(",", ".")
    )


with col3:

    st.metric(
        label="Clubes",
        value=total_clubes
    )


with col4:

    st.metric(
        label="Gols",
        value=f"{total_gols:,}".replace(",", ".")
    )


# ==================================================
# RESUMO DO CLUBE SELECIONADO
# ==================================================

if club_id is not None:

    st.divider()


    # --------------------------------------------------
    # Filtro de temporada para o resumo do clube
    # --------------------------------------------------

    if season_id is None:

        filtro_temporada_clube = ""

    else:

        filtro_temporada_clube = (
            f"AND season_id = {season_id}"
        )


    # --------------------------------------------------
    # Consulta do resumo do clube
    # --------------------------------------------------

    query_clube = f"""
    WITH jogos_clube AS (

        SELECT
            home_goals AS gols_pro,
            away_goals AS gols_contra,

            CASE
                WHEN home_goals > away_goals THEN 3
                WHEN home_goals = away_goals THEN 1
                ELSE 0
            END AS pontos

        FROM matches

        WHERE home_team_id = {club_id}
        {filtro_temporada_clube}


        UNION ALL


        SELECT
            away_goals AS gols_pro,
            home_goals AS gols_contra,

            CASE
                WHEN away_goals > home_goals THEN 3
                WHEN away_goals = home_goals THEN 1
                ELSE 0
            END AS pontos

        FROM matches

        WHERE away_team_id = {club_id}
        {filtro_temporada_clube}
    )

    SELECT
        COUNT(*) AS jogos,

        SUM(pontos) AS pontos,

        SUM(gols_pro) AS gols,

        SUM(gols_contra) AS gols_sofridos,

        SUM(
            CASE
                WHEN pontos = 3 THEN 1
                ELSE 0
            END
        ) AS vitorias,

        ROUND(
            (
                SUM(pontos)::numeric
                / (COUNT(*) * 3)
            ) * 100,
            2
        ) AS aproveitamento

    FROM jogos_clube;
    """


    dados_clube = executar_query(
        query_clube
    )


    # --------------------------------------------------
    # Valores do clube
    # --------------------------------------------------

    jogos_clube = int(
        dados_clube.loc[0, "jogos"]
    )

    pontos_clube = int(
        dados_clube.loc[0, "pontos"]
    )

    gols_clube = int(
        dados_clube.loc[0, "gols"]
    )

    aproveitamento_clube = float(
        dados_clube.loc[
            0,
            "aproveitamento"
        ]
    )


    # --------------------------------------------------
    # Título do clube
    # --------------------------------------------------

    st.markdown(
        f"### {clube_selecionado}"
    )


    if temporada_selecionada == "Todas":

        st.caption(
            "Desempenho no período analisado"
        )

    else:

        st.caption(
            f"Desempenho na temporada "
            f"{temporada_selecionada}"
        )


    # --------------------------------------------------
    # Cards do clube
    # --------------------------------------------------

    clube_col1, clube_col2, clube_col3, clube_col4 = (
        st.columns(4)
    )


    with clube_col1:

        st.metric(
            label="Jogos",
            value=jogos_clube
        )


    with clube_col2:

        st.metric(
            label="Pontos",
            value=pontos_clube
        )


    with clube_col3:

        st.metric(
            label="Gols",
            value=gols_clube
        )


    with clube_col4:

        st.metric(
            label="Aproveitamento",
            value=f"{aproveitamento_clube:.2f}%"
        )


    # ==================================================
    # EVOLUÇÃO DO DESEMPENHO DO CLUBE
    # ==================================================

    st.markdown(
        f"#### Evolução do desempenho do {clube_selecionado}"
    )


    query_evolucao_clube = f"""
    WITH jogos_clube AS (

        SELECT
            season_id,

            CASE
                WHEN home_goals > away_goals THEN 3
                WHEN home_goals = away_goals THEN 1
                ELSE 0
            END AS pontos

        FROM matches

        WHERE home_team_id = {club_id}


        UNION ALL


        SELECT
            season_id,

            CASE
                WHEN away_goals > home_goals THEN 3
                WHEN away_goals = home_goals THEN 1
                ELSE 0
            END AS pontos

        FROM matches

        WHERE away_team_id = {club_id}
    )

    SELECT
        s.season,

        COUNT(*) AS jogos,

        SUM(j.pontos) AS pontos,

        ROUND(
            SUM(j.pontos)::numeric
            / COUNT(*),
            2
        ) AS pontos_por_jogo

    FROM jogos_clube j

    JOIN seasons s
        ON s.id = j.season_id

    GROUP BY
        s.id,
        s.season

    ORDER BY
        s.season;
    """


    evolucao_clube = executar_query(
        query_evolucao_clube
    )


    # --------------------------------------------------
    # Gráfico de evolução do clube
    # --------------------------------------------------

    fig_evolucao_clube = px.line(
        evolucao_clube,

        x="season",

        y="pontos_por_jogo",

        markers=True,

        text="pontos_por_jogo",

        labels={
            "season":
                "Temporada",

            "pontos_por_jogo":
                "Pontos por jogo"
        }
    )


    fig_evolucao_clube.update_traces(
        textposition="top center"
    )


    fig_evolucao_clube.update_layout(
        xaxis_title="Temporada",

        yaxis_title="Pontos por jogo",

        hovermode="x unified"
    )


    # --------------------------------------------------
    # Destacar temporada escolhida
    # --------------------------------------------------

    if temporada_selecionada != "Todas":

        destaque_clube = evolucao_clube[
            evolucao_clube["season"]
            == temporada_selecionada
        ]


        if not destaque_clube.empty:

            fig_evolucao_clube.add_scatter(
                x=destaque_clube["season"],

                y=destaque_clube[
                    "pontos_por_jogo"
                ],

                mode="markers",

                marker=dict(
                    size=16,

                    symbol="circle-open",

                    line=dict(
                        width=3
                    )
                ),

                showlegend=False,

                hoverinfo="skip"
            )


    st.plotly_chart(
        fig_evolucao_clube,
        width="stretch"
    )


# ==================================================
# EVOLUÇÃO DA MÉDIA DE GOLS DA PREMIER LEAGUE
# ==================================================

st.divider()

st.subheader(
    "Evolução da média de gols por partida"
)


query_gols_temporada = """
SELECT
    s.season,

    COUNT(*) AS partidas,

    SUM(
        m.home_goals
        + m.away_goals
    ) AS total_gols,

    ROUND(
        AVG(
            m.home_goals
            + m.away_goals
        )::numeric,
        2
    ) AS media_gols

FROM matches m

JOIN seasons s
    ON s.id = m.season_id

GROUP BY
    s.id,
    s.season

ORDER BY
    s.season;
"""


gols_temporada = executar_query(
    query_gols_temporada
)


fig_gols = px.line(
    gols_temporada,

    x="season",

    y="media_gols",

    markers=True,

    text="media_gols",

    labels={
        "season":
            "Temporada",

        "media_gols":
            "Média de gols por partida"
    }
)


fig_gols.update_traces(
    textposition="top center"
)


fig_gols.update_layout(
    xaxis_title="Temporada",

    yaxis_title="Média de gols por partida",

    hovermode="x unified"
)


# --------------------------------------------------
# Destaque da temporada selecionada
# --------------------------------------------------

if temporada_selecionada != "Todas":

    dados_destaque = gols_temporada[
        gols_temporada["season"]
        == temporada_selecionada
    ]


    fig_gols.add_scatter(
        x=dados_destaque["season"],

        y=dados_destaque["media_gols"],

        mode="markers",

        marker=dict(
            size=16,

            symbol="circle-open",

            line=dict(
                width=3
            )
        ),

        name=(
            f"Selecionada: "
            f"{temporada_selecionada}"
        ),

        showlegend=False,

        hoverinfo="skip"
    )


st.plotly_chart(
    fig_gols,
    width="stretch"
)


# ==================================================
# EVOLUÇÃO DOS RESULTADOS DAS PARTIDAS
# ==================================================

st.divider()

st.subheader(
    "Evolução dos resultados das partidas"
)


query_resultados = """
SELECT
    s.season,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN m.home_goals > m.away_goals
                    THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS vitorias_casa,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN m.home_goals = m.away_goals
                    THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS empates,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN m.home_goals < m.away_goals
                    THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS vitorias_fora

FROM matches m

JOIN seasons s
    ON s.id = m.season_id

GROUP BY
    s.id,
    s.season

ORDER BY
    s.season;
"""


resultados_temporada = executar_query(
    query_resultados
)


resultados_long = resultados_temporada.melt(
    id_vars="season",

    value_vars=[
        "vitorias_casa",
        "empates",
        "vitorias_fora"
    ],

    var_name="resultado",

    value_name="percentual"
)


nomes_resultados = {
    "vitorias_casa":
        "Vitórias em casa",

    "empates":
        "Empates",

    "vitorias_fora":
        "Vitórias fora"
}


resultados_long["resultado"] = (
    resultados_long["resultado"]
    .map(nomes_resultados)
)


fig_resultados = px.line(
    resultados_long,

    x="season",

    y="percentual",

    color="resultado",

    markers=True,

    labels={
        "season":
            "Temporada",

        "percentual":
            "Percentual de partidas (%)",

        "resultado":
            "Resultado"
    }
)


fig_resultados.update_layout(
    xaxis_title="Temporada",

    yaxis_title="Percentual de partidas (%)",

    hovermode="x unified",

    legend_title_text=""
)


# --------------------------------------------------
# Destaque da temporada selecionada
# --------------------------------------------------

if temporada_selecionada != "Todas":

    destaque_resultados = resultados_long[
        resultados_long["season"]
        == temporada_selecionada
    ]


    fig_resultados.add_scatter(
        x=destaque_resultados["season"],

        y=destaque_resultados["percentual"],

        mode="markers",

        marker=dict(
            size=14,

            symbol="circle-open",

            line=dict(
                width=3
            )
        ),

        showlegend=False,

        hoverinfo="skip"
    )


st.plotly_chart(
    fig_resultados,
    width="stretch"
)


# ==================================================
# RANKING HISTÓRICO DOS CLUBES
# ==================================================

st.divider()


if temporada_selecionada == "Todas":

    st.subheader(
        "Top clubes do período"
    )

else:

    st.subheader(
        f"Top clubes da temporada "
        f"{temporada_selecionada}"
    )


# --------------------------------------------------
# Filtro SQL do ranking
# --------------------------------------------------

if season_id is None:

    filtro_ranking = ""

else:

    filtro_ranking = (
        f"WHERE season_id = {season_id}"
    )


query_ranking = f"""
WITH jogos_clubes AS (

    SELECT
        home_team_id AS team_id,

        home_goals AS gols_pro,

        CASE
            WHEN home_goals > away_goals THEN 3
            WHEN home_goals = away_goals THEN 1
            ELSE 0
        END AS pontos

    FROM matches

    {filtro_ranking}


    UNION ALL


    SELECT
        away_team_id AS team_id,

        away_goals AS gols_pro,

        CASE
            WHEN away_goals > home_goals THEN 3
            WHEN away_goals = home_goals THEN 1
            ELSE 0
        END AS pontos

    FROM matches

    {filtro_ranking}
)

SELECT
    t.name AS clube,

    COUNT(*) AS jogos,

    SUM(j.gols_pro) AS gols,

    SUM(j.pontos) AS pontos,

    ROUND(
        (
            SUM(j.pontos)::numeric
            / (COUNT(*) * 3)
        ) * 100,
        2
    ) AS aproveitamento

FROM jogos_clubes j

JOIN teams t
    ON t.id = j.team_id

GROUP BY
    t.id,
    t.name;
"""


ranking_clubes = executar_query(
    query_ranking
)


# --------------------------------------------------
# Métrica do ranking
# --------------------------------------------------

metrica_ranking = st.selectbox(
    "Selecione a métrica do ranking:",

    [
        "Pontos",
        "Gols",
        "Aproveitamento"
    ]
)


mapa_metricas = {
    "Pontos":
        "pontos",

    "Gols":
        "gols",

    "Aproveitamento":
        "aproveitamento"
}


coluna_ranking = mapa_metricas[
    metrica_ranking
]


# --------------------------------------------------
# Ordenar ranking
# --------------------------------------------------

ranking_ordenado = (
    ranking_clubes
    .sort_values(
        by=coluna_ranking,
        ascending=False
    )
    .copy()
)


# --------------------------------------------------
# Top 10
# --------------------------------------------------

top10_clubes = (
    ranking_ordenado
    .head(10)
    .copy()
)


# --------------------------------------------------
# Garantir que o clube selecionado apareça
# --------------------------------------------------

if (
    clube_selecionado != "Todos"
    and clube_selecionado
    not in top10_clubes["clube"].values
):

    clube_fora_top10 = ranking_ordenado[
        ranking_ordenado["clube"]
        == clube_selecionado
    ]


    if not clube_fora_top10.empty:

        top10_clubes = (
            top10_clubes
            .iloc[:9]
            .copy()
        )


        top10_clubes = pd.concat(
            [
                top10_clubes,
                clube_fora_top10
            ],
            ignore_index=True
        )


# --------------------------------------------------
# Ordenar para gráfico horizontal
# --------------------------------------------------

top10_clubes = (
    top10_clubes
    .sort_values(
        by=coluna_ranking,
        ascending=True
    )
    .copy()
)


# --------------------------------------------------
# Texto das barras
# --------------------------------------------------

if metrica_ranking == "Aproveitamento":

    top10_clubes["texto"] = (
        top10_clubes[coluna_ranking]
        .map(
            lambda x:
            f"{x:.2f}%"
        )
    )

else:

    top10_clubes["texto"] = (
        top10_clubes[coluna_ranking]
        .map(
            lambda x:
            f"{int(x)}"
        )
    )


# --------------------------------------------------
# Identificar clube selecionado
# --------------------------------------------------

top10_clubes["destaque"] = (
    top10_clubes["clube"]
    .apply(
        lambda clube:
        "Clube selecionado"
        if clube == clube_selecionado
        else "Demais clubes"
    )
)


# --------------------------------------------------
# Gráfico do ranking
# --------------------------------------------------

fig_ranking = px.bar(
    top10_clubes,

    x=coluna_ranking,

    y="clube",

    orientation="h",

    text="texto",

    color="destaque",

    color_discrete_map={
        "Clube selecionado":
            "#FFD700",

        "Demais clubes":
            "#7EC8F5"
    },

    labels={
        "clube":
            "Clube",

        coluna_ranking:
            metrica_ranking,

        "destaque":
            ""
    }
)


fig_ranking.update_traces(
    textposition="outside"
)


fig_ranking.update_layout(
    xaxis_title=metrica_ranking,

    yaxis_title="",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    )
)


st.plotly_chart(
    fig_ranking,
    width="stretch"
)