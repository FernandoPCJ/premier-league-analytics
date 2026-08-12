import streamlit as st
import plotly.express as px
import pandas as pd

from utils.database import executar_query


# ==================================================
# CABEÇALHO
# ==================================================

st.title("⚽ Análise Ofensiva")

st.write(
    "Explore o desempenho ofensivo dos clubes da Premier League "
    "por meio de gols, finalizações e finalizações no alvo."
)


# ==================================================
# FILTRO DE TEMPORADA
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


col_filtro1, col_filtro2 = st.columns(2)


with col_filtro1:

    temporada_selecionada = st.selectbox(
        "Temporada:",
        opcoes_temporadas,
        key="ataque_temporada"
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


# ==================================================
# FILTRO DE CLUBE
# ==================================================

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


with col_filtro2:

    clube_selecionado = st.selectbox(
        "Clube:",
        opcoes_clubes,
        key="ataque_clube"
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
# BASE OFENSIVA
# ==================================================

filtro_temporada = ""

if season_id is not None:

    filtro_temporada = (
        f"WHERE season_id = {season_id}"
    )


query_ofensiva = f"""
WITH jogos_ofensivos AS (

    SELECT
        season_id,
        home_team_id AS team_id,
        home_goals AS gols,
        home_shots AS finalizacoes,
        home_shots_on_target AS finalizacoes_alvo

    FROM matches
    {filtro_temporada}


    UNION ALL


    SELECT
        season_id,
        away_team_id AS team_id,
        away_goals AS gols,
        away_shots AS finalizacoes,
        away_shots_on_target AS finalizacoes_alvo

    FROM matches
    {filtro_temporada}
)

SELECT
    COUNT(*) AS jogos,

    SUM(gols) AS gols,

    ROUND(
        AVG(gols)::numeric,
        2
    ) AS gols_por_jogo,

    ROUND(
        AVG(finalizacoes)::numeric,
        2
    ) AS finalizacoes_por_jogo,

    ROUND(
        AVG(finalizacoes_alvo)::numeric,
        2
    ) AS finalizacoes_alvo_por_jogo

FROM jogos_ofensivos
"""


# --------------------------------------------------
# Aplicar filtro de clube
# --------------------------------------------------

if club_id is not None:

    query_ofensiva = query_ofensiva.replace(
        "FROM jogos_ofensivos\n",
        (
            "FROM jogos_ofensivos\n"
            f"WHERE team_id = {club_id}\n"
        )
    )


dados_ofensivos = executar_query(
    query_ofensiva
)


# ==================================================
# KPIs OFENSIVOS
# ==================================================

total_gols = int(
    dados_ofensivos.loc[0, "gols"]
)

gols_por_jogo = float(
    dados_ofensivos.loc[
        0,
        "gols_por_jogo"
    ]
)

finalizacoes_por_jogo = float(
    dados_ofensivos.loc[
        0,
        "finalizacoes_por_jogo"
    ]
)

finalizacoes_alvo_por_jogo = float(
    dados_ofensivos.loc[
        0,
        "finalizacoes_alvo_por_jogo"
    ]
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="Gols",
        value=f"{total_gols:,}".replace(",", ".")
    )


with col2:

    st.metric(
        label="Gols por jogo",
        value=f"{gols_por_jogo:.2f}"
    )


with col3:

    st.metric(
        label="Finalizações por jogo",
        value=f"{finalizacoes_por_jogo:.2f}"
    )


with col4:

    st.metric(
        label="Finalizações no alvo por jogo",
        value=f"{finalizacoes_alvo_por_jogo:.2f}"
    )

# ==================================================
# RANKING OFENSIVO
# ==================================================

st.divider()


if temporada_selecionada == "Todas":

    st.subheader(
        "Ranking ofensivo dos clubes no período"
    )

else:

    st.subheader(
        f"Ranking ofensivo da temporada "
        f"{temporada_selecionada}"
    )


# --------------------------------------------------
# Filtro de temporada
# --------------------------------------------------

if season_id is None:

    filtro_ranking = ""

else:

    filtro_ranking = (
        f"WHERE season_id = {season_id}"
    )


# --------------------------------------------------
# Consulta do ranking ofensivo
# --------------------------------------------------

query_ranking_ofensivo = f"""
WITH jogos_ofensivos AS (

    SELECT
        home_team_id AS team_id,
        home_goals AS gols,
        home_shots AS finalizacoes,
        home_shots_on_target AS finalizacoes_alvo

    FROM matches

    {filtro_ranking}


    UNION ALL


    SELECT
        away_team_id AS team_id,
        away_goals AS gols,
        away_shots AS finalizacoes,
        away_shots_on_target AS finalizacoes_alvo

    FROM matches

    {filtro_ranking}
)

SELECT
    t.name AS clube,

    COUNT(*) AS jogos,

    SUM(j.gols) AS gols,

    ROUND(
        AVG(j.gols)::numeric,
        2
    ) AS gols_por_jogo,

    ROUND(
        AVG(j.finalizacoes)::numeric,
        2
    ) AS finalizacoes_por_jogo,

    ROUND(
        AVG(j.finalizacoes_alvo)::numeric,
        2
    ) AS finalizacoes_alvo_por_jogo,

    ROUND(
        (
            SUM(j.gols)::numeric
            / NULLIF(SUM(j.finalizacoes), 0)
        ) * 100,
        2
    ) AS conversao

FROM jogos_ofensivos j

JOIN teams t
    ON t.id = j.team_id

GROUP BY
    t.id,
    t.name;
"""


ranking_ofensivo = executar_query(
    query_ranking_ofensivo
)


# --------------------------------------------------
# Escolha da métrica
# --------------------------------------------------

metrica_ofensiva = st.selectbox(
    "Selecione a métrica ofensiva:",
    [
        "Gols por jogo",
        "Finalizações por jogo",
        "Finalizações no alvo por jogo",
        "Conversão de finalizações"
    ],
    key="ataque_metrica_ranking"
)


mapa_metricas_ofensivas = {
    "Gols por jogo":
        "gols_por_jogo",

    "Finalizações por jogo":
        "finalizacoes_por_jogo",

    "Finalizações no alvo por jogo":
        "finalizacoes_alvo_por_jogo",

    "Conversão de finalizações":
        "conversao"
}


coluna_ofensiva = mapa_metricas_ofensivas[
    metrica_ofensiva
]


# --------------------------------------------------
# Ordenar ranking
# --------------------------------------------------

ranking_ordenado = (
    ranking_ofensivo
    .sort_values(
        by=coluna_ofensiva,
        ascending=False
    )
    .copy()
)


top10_ofensivo = (
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
    not in top10_ofensivo["clube"].values
):

    clube_fora_top10 = ranking_ordenado[
        ranking_ordenado["clube"]
        == clube_selecionado
    ]


    if not clube_fora_top10.empty:

        top10_ofensivo = (
            top10_ofensivo
            .iloc[:9]
            .copy()
        )


        top10_ofensivo = pd.concat(
            [
                top10_ofensivo,
                clube_fora_top10
            ],
            ignore_index=True
        )


# --------------------------------------------------
# Ordenação para gráfico horizontal
# --------------------------------------------------

top10_ofensivo = (
    top10_ofensivo
    .sort_values(
        by=coluna_ofensiva,
        ascending=True
    )
    .copy()
)


# --------------------------------------------------
# Texto das barras
# --------------------------------------------------

if metrica_ofensiva == "Conversão de finalizações":

    top10_ofensivo["texto"] = (
        top10_ofensivo[coluna_ofensiva]
        .map(
            lambda x: f"{x:.2f}%"
        )
    )

else:

    top10_ofensivo["texto"] = (
        top10_ofensivo[coluna_ofensiva]
        .map(
            lambda x: f"{x:.2f}"
        )
    )


# --------------------------------------------------
# Destaque do clube selecionado
# --------------------------------------------------

top10_ofensivo["destaque"] = (
    top10_ofensivo["clube"]
    .apply(
        lambda clube:
        "Clube selecionado"
        if clube == clube_selecionado
        else "Demais clubes"
    )
)


# --------------------------------------------------
# Gráfico
# --------------------------------------------------

fig_ranking_ofensivo = px.bar(
    top10_ofensivo,

    x=coluna_ofensiva,

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

        coluna_ofensiva:
            metrica_ofensiva,

        "destaque":
            ""
    }
)


fig_ranking_ofensivo.update_traces(
    textposition="outside"
)


fig_ranking_ofensivo.update_layout(
    xaxis_title=metrica_ofensiva,

    yaxis_title="",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    )
)


st.plotly_chart(
    fig_ranking_ofensivo,
    width="stretch"
)

# ==================================================
# FINALIZAÇÕES X GOLS POR JOGO
# ==================================================

st.divider()

st.subheader(
    "Finalizações por jogo × Gols por jogo"
)

st.write(
    "Compare o volume de finalizações dos clubes com a média "
    "de gols marcados por partida."
)


# --------------------------------------------------
# Preparar dados
# --------------------------------------------------

scatter_ofensivo = ranking_ofensivo.copy()


scatter_ofensivo["destaque"] = (
    scatter_ofensivo["clube"]
    .apply(
        lambda clube:
        "Clube selecionado"
        if clube == clube_selecionado
        else "Demais clubes"
    )
)


# --------------------------------------------------
# Médias para referência
# --------------------------------------------------

media_finalizacoes = (
    scatter_ofensivo[
        "finalizacoes_por_jogo"
    ].mean()
)

media_gols = (
    scatter_ofensivo[
        "gols_por_jogo"
    ].mean()
)


# --------------------------------------------------
# Gráfico
# --------------------------------------------------

fig_scatter_ofensivo = px.scatter(
    scatter_ofensivo,

    x="finalizacoes_por_jogo",

    y="gols_por_jogo",

    color="destaque",

    hover_name="clube",

    hover_data={
        "jogos": True,
        "gols": True,
        "finalizacoes_por_jogo": ":.2f",
        "finalizacoes_alvo_por_jogo": ":.2f",
        "gols_por_jogo": ":.2f",
        "conversao": ":.2f",
        "destaque": False
    },

    color_discrete_map={
        "Clube selecionado": "#FFD700",
        "Demais clubes": "#7EC8F5"
    },

    labels={
        "finalizacoes_por_jogo":
            "Finalizações por jogo",

        "gols_por_jogo":
            "Gols por jogo",

        "finalizacoes_alvo_por_jogo":
            "Finalizações no alvo por jogo",

        "conversao":
            "Conversão (%)",

        "destaque":
            ""
    }
)


fig_scatter_ofensivo.update_traces(
    marker=dict(
        size=12
    )
)


# --------------------------------------------------
# Linhas de referência
# --------------------------------------------------

fig_scatter_ofensivo.add_vline(
    x=media_finalizacoes,
    line_dash="dash",
    annotation_text="Média de finalizações",
    annotation_position="top"
)


fig_scatter_ofensivo.add_hline(
    y=media_gols,
    line_dash="dash",
    annotation_text="Média de gols",
    annotation_position="right"
)


fig_scatter_ofensivo.update_layout(
    xaxis_title="Finalizações por jogo",

    yaxis_title="Gols por jogo",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    )
)


# --------------------------------------------------
# Nome do clube selecionado
# --------------------------------------------------

if clube_selecionado != "Todos":

    clube_destaque = scatter_ofensivo[
        scatter_ofensivo["clube"]
        == clube_selecionado
    ]


    if not clube_destaque.empty:

        fig_scatter_ofensivo.add_annotation(
            x=clube_destaque[
                "finalizacoes_por_jogo"
            ].iloc[0],

            y=clube_destaque[
                "gols_por_jogo"
            ].iloc[0],

            text=clube_selecionado,

            showarrow=True,

            arrowhead=2,

            ax=35,

            ay=-35
        )


st.plotly_chart(
    fig_scatter_ofensivo,
    width="stretch"
)
# ==================================================
# FINALIZAÇÕES NO ALVO X GOLS POR JOGO
# ==================================================

st.divider()

st.subheader(
    "Finalizações no alvo por jogo × Gols por jogo"
)

st.write(
    "Compare a frequência de finalizações no alvo dos clubes "
    "com a média de gols marcados por partida."
)


# --------------------------------------------------
# Preparar dados
# --------------------------------------------------

scatter_alvo = ranking_ofensivo.copy()


scatter_alvo["destaque"] = (
    scatter_alvo["clube"]
    .apply(
        lambda clube:
        "Clube selecionado"
        if clube == clube_selecionado
        else "Demais clubes"
    )
)


# --------------------------------------------------
# Médias para referência
# --------------------------------------------------

media_finalizacoes_alvo = (
    scatter_alvo[
        "finalizacoes_alvo_por_jogo"
    ].mean()
)

media_gols_alvo = (
    scatter_alvo[
        "gols_por_jogo"
    ].mean()
)


# --------------------------------------------------
# Gráfico
# --------------------------------------------------

fig_scatter_alvo = px.scatter(
    scatter_alvo,

    x="finalizacoes_alvo_por_jogo",

    y="gols_por_jogo",

    color="destaque",

    hover_name="clube",

    hover_data={
        "jogos": True,
        "gols": True,
        "finalizacoes_por_jogo": ":.2f",
        "finalizacoes_alvo_por_jogo": ":.2f",
        "gols_por_jogo": ":.2f",
        "conversao": ":.2f",
        "destaque": False
    },

    color_discrete_map={
        "Clube selecionado": "#FFD700",
        "Demais clubes": "#7EC8F5"
    },

    labels={
        "finalizacoes_alvo_por_jogo":
            "Finalizações no alvo por jogo",

        "finalizacoes_por_jogo":
            "Finalizações por jogo",

        "gols_por_jogo":
            "Gols por jogo",

        "conversao":
            "Conversão (%)",

        "destaque":
            ""
    }
)


fig_scatter_alvo.update_traces(
    marker=dict(
        size=12
    )
)


# --------------------------------------------------
# Linhas de referência
# --------------------------------------------------

fig_scatter_alvo.add_vline(
    x=media_finalizacoes_alvo,
    line_dash="dash",
    annotation_text="Média de finalizações no alvo",
    annotation_position="top"
)


fig_scatter_alvo.add_hline(
    y=media_gols_alvo,
    line_dash="dash",
    annotation_text="Média de gols",
    annotation_position="right"
)


fig_scatter_alvo.update_layout(
    xaxis_title="Finalizações no alvo por jogo",

    yaxis_title="Gols por jogo",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    )
)


# --------------------------------------------------
# Nome do clube selecionado
# --------------------------------------------------

if clube_selecionado != "Todos":

    clube_destaque_alvo = scatter_alvo[
        scatter_alvo["clube"]
        == clube_selecionado
    ]


    if not clube_destaque_alvo.empty:

        fig_scatter_alvo.add_annotation(
            x=clube_destaque_alvo[
                "finalizacoes_alvo_por_jogo"
            ].iloc[0],

            y=clube_destaque_alvo[
                "gols_por_jogo"
            ].iloc[0],

            text=clube_selecionado,

            showarrow=True,

            arrowhead=2,

            ax=35,

            ay=-35
        )


st.plotly_chart(
    fig_scatter_alvo,
    width="stretch"
)

# ==================================================
# EVOLUÇÃO OFENSIVA DO CLUBE
# ==================================================

if club_id is not None:

    st.divider()

    st.subheader(
        f"Evolução ofensiva do {clube_selecionado}"
    )

    st.write(
        "Acompanhe a evolução dos principais indicadores "
        "ofensivos do clube ao longo das temporadas."
    )


    # --------------------------------------------------
    # Consulta histórica do clube
    # --------------------------------------------------

    query_evolucao_ofensiva = f"""
    WITH jogos_clube AS (

        SELECT
            season_id,
            home_goals AS gols,
            home_shots AS finalizacoes,
            home_shots_on_target AS finalizacoes_alvo

        FROM matches

        WHERE home_team_id = {club_id}


        UNION ALL


        SELECT
            season_id,
            away_goals AS gols,
            away_shots AS finalizacoes,
            away_shots_on_target AS finalizacoes_alvo

        FROM matches

        WHERE away_team_id = {club_id}
    )

    SELECT
        s.season,

        COUNT(*) AS jogos,

        ROUND(
            AVG(j.gols)::numeric,
            2
        ) AS gols_por_jogo,

        ROUND(
            AVG(j.finalizacoes)::numeric,
            2
        ) AS finalizacoes_por_jogo,

        ROUND(
            AVG(j.finalizacoes_alvo)::numeric,
            2
        ) AS finalizacoes_alvo_por_jogo

    FROM jogos_clube j

    JOIN seasons s
        ON s.id = j.season_id

    GROUP BY
        s.id,
        s.season

    ORDER BY
        s.season;
    """


    evolucao_ofensiva = executar_query(
        query_evolucao_ofensiva
    )


    # ==================================================
    # GRÁFICO 1: GOLS POR JOGO
    # ==================================================

    fig_gols_clube = px.line(
        evolucao_ofensiva,

        x="season",

        y="gols_por_jogo",

        markers=True,

        text="gols_por_jogo",

        labels={
            "season":
                "Temporada",

            "gols_por_jogo":
                "Gols por jogo"
        }
    )


    fig_gols_clube.update_traces(
        textposition="top center"
    )


    fig_gols_clube.update_layout(
        xaxis_title="Temporada",

        yaxis_title="Gols por jogo",

        hovermode="x unified"
    )


    # --------------------------------------------------
    # Destacar temporada selecionada
    # --------------------------------------------------

    if temporada_selecionada != "Todas":

        destaque_gols = evolucao_ofensiva[
            evolucao_ofensiva["season"]
            == temporada_selecionada
        ]


        if not destaque_gols.empty:

            fig_gols_clube.add_scatter(
                x=destaque_gols["season"],

                y=destaque_gols[
                    "gols_por_jogo"
                ],

                mode="markers",

                marker=dict(
                    size=16,
                    symbol="circle-open",
                    line=dict(width=3)
                ),

                showlegend=False,

                hoverinfo="skip"
            )


    st.plotly_chart(
        fig_gols_clube,
        width="stretch"
    )


    # ==================================================
    # GRÁFICO 2: FINALIZAÇÕES
    # ==================================================

    evolucao_finalizacoes = (
        evolucao_ofensiva[
            [
                "season",
                "finalizacoes_por_jogo",
                "finalizacoes_alvo_por_jogo"
            ]
        ]
        .melt(
            id_vars="season",

            var_name="indicador",

            value_name="valor"
        )
    )


    nomes_indicadores = {
        "finalizacoes_por_jogo":
            "Finalizações por jogo",

        "finalizacoes_alvo_por_jogo":
            "Finalizações no alvo por jogo"
    }


    evolucao_finalizacoes["indicador"] = (
        evolucao_finalizacoes["indicador"]
        .map(nomes_indicadores)
    )


    fig_finalizacoes_clube = px.line(
        evolucao_finalizacoes,

        x="season",

        y="valor",

        color="indicador",

        markers=True,

        labels={
            "season":
                "Temporada",

            "valor":
                "Média por jogo",

            "indicador":
                ""
        }
    )


    fig_finalizacoes_clube.update_layout(
        xaxis_title="Temporada",

        yaxis_title="Média por jogo",

        hovermode="x unified",

        legend_title_text=""
    )


    st.plotly_chart(
        fig_finalizacoes_clube,
        width="stretch"
    )