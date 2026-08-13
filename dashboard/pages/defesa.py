import streamlit as st
import plotly.express as px
import pandas as pd

from utils.database import executar_query


# ==================================================
# CABEÇALHO
# ==================================================

st.title("🛡️ Análise Defensiva")

st.write(
    "Explore o desempenho defensivo dos clubes da Premier League "
    "por meio de gols sofridos, finalizações concedidas "
    "e finalizações no alvo concedidas."
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

temporadas_df = executar_query(
    query_temporadas
)

opcoes_temporadas = (
    ["Todas"]
    + temporadas_df["season"].tolist()
)


col_filtro1, col_filtro2 = st.columns(2)


with col_filtro1:

    temporada_selecionada = st.selectbox(
        "Temporada:",
        opcoes_temporadas,
        key="defesa_temporada"
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
        key="defesa_clube"
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
# FILTROS SQL
# ==================================================

if season_id is None:

    filtro_temporada = ""

else:

    filtro_temporada = (
        f"AND season_id = {season_id}"
    )


if club_id is None:

    filtro_clube = ""

else:

    filtro_clube = (
        f"WHERE team_id = {club_id}"
    )


# ==================================================
# BASE DEFENSIVA
# ==================================================

query_defensiva = f"""
WITH jogos_defensivos AS (

    SELECT
        season_id,

        home_team_id AS team_id,

        away_goals AS gols_sofridos,

        away_shots AS finalizacoes_concedidas,

        away_shots_on_target
            AS finalizacoes_alvo_concedidas

    FROM matches

    WHERE 1 = 1
    {filtro_temporada}


    UNION ALL


    SELECT
        season_id,

        away_team_id AS team_id,

        home_goals AS gols_sofridos,

        home_shots AS finalizacoes_concedidas,

        home_shots_on_target
            AS finalizacoes_alvo_concedidas

    FROM matches

    WHERE 1 = 1
    {filtro_temporada}
)

SELECT
    COUNT(*) AS jogos,

    SUM(gols_sofridos)
        AS gols_sofridos,

    ROUND(
        AVG(gols_sofridos)::numeric,
        2
    ) AS gols_sofridos_por_jogo,

    ROUND(
        AVG(finalizacoes_concedidas)::numeric,
        2
    ) AS finalizacoes_concedidas_por_jogo,

    ROUND(
        AVG(finalizacoes_alvo_concedidas)::numeric,
        2
    ) AS finalizacoes_alvo_concedidas_por_jogo

FROM jogos_defensivos

{filtro_clube};
"""


dados_defensivos = executar_query(
    query_defensiva
)


# ==================================================
# KPIs DEFENSIVOS
# ==================================================

total_gols_sofridos = int(
    dados_defensivos.loc[
        0,
        "gols_sofridos"
    ]
)


gols_sofridos_por_jogo = float(
    dados_defensivos.loc[
        0,
        "gols_sofridos_por_jogo"
    ]
)


finalizacoes_concedidas_por_jogo = float(
    dados_defensivos.loc[
        0,
        "finalizacoes_concedidas_por_jogo"
    ]
)


finalizacoes_alvo_concedidas_por_jogo = float(
    dados_defensivos.loc[
        0,
        "finalizacoes_alvo_concedidas_por_jogo"
    ]
)


# --------------------------------------------------
# Cards
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="Gols sofridos",
        value=f"{total_gols_sofridos:,}".replace(",", ".")
    )


with col2:

    st.metric(
        label="Gols sofridos por jogo",
        value=f"{gols_sofridos_por_jogo:.2f}"
    )


with col3:

    st.metric(
        label="Finalizações concedidas por jogo",
        value=f"{finalizacoes_concedidas_por_jogo:.2f}"
    )


with col4:

    st.metric(
        label="Finalizações no alvo concedidas por jogo",
        value=f"{finalizacoes_alvo_concedidas_por_jogo:.2f}"
    )


# ==================================================
# RANKING DEFENSIVO
# ==================================================

st.divider()


if temporada_selecionada == "Todas":

    st.subheader(
        "Ranking defensivo dos clubes no período"
    )

else:

    st.subheader(
        f"Ranking defensivo da temporada "
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
# Consulta do ranking defensivo
# --------------------------------------------------

query_ranking_defensivo = f"""
WITH jogos_defensivos AS (

    SELECT
        home_team_id AS team_id,

        away_goals AS gols_sofridos,

        away_shots AS finalizacoes_concedidas,

        away_shots_on_target
            AS finalizacoes_alvo_concedidas,

        CASE
            WHEN away_goals = 0 THEN 1
            ELSE 0
        END AS clean_sheet

    FROM matches

    {filtro_ranking}


    UNION ALL


    SELECT
        away_team_id AS team_id,

        home_goals AS gols_sofridos,

        home_shots AS finalizacoes_concedidas,

        home_shots_on_target
            AS finalizacoes_alvo_concedidas,

        CASE
            WHEN home_goals = 0 THEN 1
            ELSE 0
        END AS clean_sheet

    FROM matches

    {filtro_ranking}
)

SELECT
    t.name AS clube,

    COUNT(*) AS jogos,

    SUM(j.gols_sofridos)
        AS gols_sofridos,

    ROUND(
        AVG(j.gols_sofridos)::numeric,
        2
    ) AS gols_sofridos_por_jogo,

    ROUND(
        AVG(j.finalizacoes_concedidas)::numeric,
        2
    ) AS finalizacoes_concedidas_por_jogo,

    ROUND(
        AVG(j.finalizacoes_alvo_concedidas)::numeric,
        2
    ) AS finalizacoes_alvo_concedidas_por_jogo,

    ROUND(
        (
            SUM(j.clean_sheet)::numeric
            / COUNT(*)
        ) * 100,
        2
    ) AS clean_sheets

FROM jogos_defensivos j

JOIN teams t
    ON t.id = j.team_id

GROUP BY
    t.id,
    t.name;
"""


ranking_defensivo = executar_query(
    query_ranking_defensivo
)


# --------------------------------------------------
# Garantir valores numéricos
# --------------------------------------------------

colunas_ranking_numericas = [
    "gols_sofridos_por_jogo",
    "finalizacoes_concedidas_por_jogo",
    "finalizacoes_alvo_concedidas_por_jogo",
    "clean_sheets"
]


for coluna in colunas_ranking_numericas:

    ranking_defensivo[coluna] = (
        ranking_defensivo[coluna]
        .astype(float)
    )


# --------------------------------------------------
# Escolha da métrica
# --------------------------------------------------

metrica_defensiva = st.selectbox(
    "Selecione a métrica defensiva:",
    [
        "Gols sofridos por jogo",
        "Finalizações concedidas por jogo",
        "Finalizações no alvo concedidas por jogo",
        "Clean sheets (%)"
    ],
    key="defesa_metrica_ranking"
)


mapa_metricas_defensivas = {
    "Gols sofridos por jogo":
        "gols_sofridos_por_jogo",

    "Finalizações concedidas por jogo":
        "finalizacoes_concedidas_por_jogo",

    "Finalizações no alvo concedidas por jogo":
        "finalizacoes_alvo_concedidas_por_jogo",

    "Clean sheets (%)":
        "clean_sheets"
}


coluna_defensiva = mapa_metricas_defensivas[
    metrica_defensiva
]


# --------------------------------------------------
# Definir se maior ou menor é melhor
# --------------------------------------------------

if metrica_defensiva == "Clean sheets (%)":

    menor_e_melhor = False

    st.caption(
        "Quanto maior o percentual de clean sheets, "
        "melhor o desempenho defensivo."
    )

else:

    menor_e_melhor = True

    st.caption(
        "Quanto menor o valor, "
        "melhor o desempenho defensivo."
    )


# --------------------------------------------------
# Ordenar ranking pelos melhores
# --------------------------------------------------

ranking_ordenado = (
    ranking_defensivo
    .sort_values(
        by=coluna_defensiva,
        ascending=menor_e_melhor
    )
    .copy()
)


top10_defensivo = (
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
    not in top10_defensivo["clube"].values
):

    clube_fora_top10 = ranking_ordenado[
        ranking_ordenado["clube"]
        == clube_selecionado
    ]


    if not clube_fora_top10.empty:

        top10_defensivo = (
            top10_defensivo
            .iloc[:9]
            .copy()
        )


        top10_defensivo = pd.concat(
            [
                top10_defensivo,
                clube_fora_top10
            ],
            ignore_index=True
        )


# --------------------------------------------------
# Ordenar para gráfico horizontal
# --------------------------------------------------

if menor_e_melhor:

    # Melhor = menor.
    # Para barra horizontal, o melhor ficará no topo.
    top10_defensivo = (
        top10_defensivo
        .sort_values(
            by=coluna_defensiva,
            ascending=False
        )
        .copy()
    )

else:

    # Melhor = maior.
    # Para barra horizontal, o melhor ficará no topo.
    top10_defensivo = (
        top10_defensivo
        .sort_values(
            by=coluna_defensiva,
            ascending=True
        )
        .copy()
    )


# --------------------------------------------------
# Texto das barras
# --------------------------------------------------

if metrica_defensiva == "Clean sheets (%)":

    top10_defensivo["texto"] = (
        top10_defensivo[coluna_defensiva]
        .map(
            lambda x: f"{x:.2f}%"
        )
    )

else:

    top10_defensivo["texto"] = (
        top10_defensivo[coluna_defensiva]
        .map(
            lambda x: f"{x:.2f}"
        )
    )


# --------------------------------------------------
# Destaque do clube selecionado
# --------------------------------------------------

top10_defensivo["destaque"] = (
    top10_defensivo["clube"]
    .apply(
        lambda clube:
        "Clube selecionado"
        if clube == clube_selecionado
        else "Demais clubes"
    )
)


# --------------------------------------------------
# Preservar a ordem real do ranking
# --------------------------------------------------

ordem_clubes = (
    top10_defensivo["clube"]
    .tolist()
)


# --------------------------------------------------
# Gráfico
# --------------------------------------------------

fig_ranking_defensivo = px.bar(
    top10_defensivo,

    x=coluna_defensiva,

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

        coluna_defensiva:
            metrica_defensiva,

        "destaque":
            ""
    }
)


fig_ranking_defensivo.update_traces(
    textposition="outside"
)


fig_ranking_defensivo.update_layout(
    xaxis_title=metrica_defensiva,

    yaxis_title="",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    ),

    yaxis=dict(
        categoryorder="array",
        categoryarray=ordem_clubes
    )
)


st.plotly_chart(
    fig_ranking_defensivo,
    width="stretch"
)


# ==================================================
# FINALIZAÇÕES CONCEDIDAS X GOLS SOFRIDOS
# ==================================================

st.divider()

st.subheader(
    "Finalizações concedidas por jogo × Gols sofridos por jogo"
)

st.write(
    "Compare o volume de finalizações permitidas aos adversários "
    "com a média de gols sofridos pelos clubes."
)


# --------------------------------------------------
# Preparar dados
# --------------------------------------------------

scatter_defensivo = ranking_defensivo.copy()


scatter_defensivo["destaque"] = (
    scatter_defensivo["clube"]
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

media_finalizacoes_concedidas = (
    scatter_defensivo[
        "finalizacoes_concedidas_por_jogo"
    ].mean()
)


media_gols_sofridos = (
    scatter_defensivo[
        "gols_sofridos_por_jogo"
    ].mean()
)


# --------------------------------------------------
# Gráfico
# --------------------------------------------------

fig_scatter_defensivo = px.scatter(
    scatter_defensivo,

    x="finalizacoes_concedidas_por_jogo",

    y="gols_sofridos_por_jogo",

    color="destaque",

    hover_name="clube",

    hover_data={
        "jogos": True,
        "gols_sofridos": True,
        "finalizacoes_concedidas_por_jogo": ":.2f",
        "finalizacoes_alvo_concedidas_por_jogo": ":.2f",
        "gols_sofridos_por_jogo": ":.2f",
        "clean_sheets": ":.2f",
        "destaque": False
    },

    color_discrete_map={
        "Clube selecionado":
            "#FFD700",

        "Demais clubes":
            "#7EC8F5"
    },

    labels={
        "finalizacoes_concedidas_por_jogo":
            "Finalizações concedidas por jogo",

        "gols_sofridos_por_jogo":
            "Gols sofridos por jogo",

        "finalizacoes_alvo_concedidas_por_jogo":
            "Finalizações no alvo concedidas por jogo",

        "clean_sheets":
            "Clean sheets (%)",

        "destaque":
            ""
    }
)


fig_scatter_defensivo.update_traces(
    marker=dict(
        size=12
    )
)


# --------------------------------------------------
# Linhas de referência
# --------------------------------------------------

fig_scatter_defensivo.add_vline(
    x=media_finalizacoes_concedidas,
    line_dash="dash",
    annotation_text="Média de finalizações concedidas",
    annotation_position="top"
)


fig_scatter_defensivo.add_hline(
    y=media_gols_sofridos,
    line_dash="dash",
    annotation_text="Média de gols sofridos",
    annotation_position="right"
)


fig_scatter_defensivo.update_layout(
    xaxis_title="Finalizações concedidas por jogo",

    yaxis_title="Gols sofridos por jogo",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    )
)


# --------------------------------------------------
# Destacar clube selecionado
# --------------------------------------------------

if clube_selecionado != "Todos":

    clube_destaque = scatter_defensivo[
        scatter_defensivo["clube"]
        == clube_selecionado
    ]


    if not clube_destaque.empty:

        fig_scatter_defensivo.add_annotation(
            x=clube_destaque[
                "finalizacoes_concedidas_por_jogo"
            ].iloc[0],

            y=clube_destaque[
                "gols_sofridos_por_jogo"
            ].iloc[0],

            text=clube_selecionado,

            showarrow=True,

            arrowhead=2,

            ax=35,

            ay=-35
        )


st.plotly_chart(
    fig_scatter_defensivo,
    width="stretch"
)


# ==================================================
# FINALIZAÇÕES NO ALVO CONCEDIDAS X GOLS SOFRIDOS
# ==================================================

st.divider()

st.subheader(
    "Finalizações no alvo concedidas por jogo × Gols sofridos por jogo"
)

st.write(
    "Compare a quantidade de finalizações no alvo permitidas "
    "aos adversários com a média de gols sofridos pelos clubes."
)


# --------------------------------------------------
# Preparar dados
# --------------------------------------------------

scatter_alvo_defensivo = (
    ranking_defensivo.copy()
)


scatter_alvo_defensivo["destaque"] = (
    scatter_alvo_defensivo["clube"]
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

media_alvo_concedidas = (
    scatter_alvo_defensivo[
        "finalizacoes_alvo_concedidas_por_jogo"
    ].mean()
)


media_gols_sofridos_alvo = (
    scatter_alvo_defensivo[
        "gols_sofridos_por_jogo"
    ].mean()
)


# --------------------------------------------------
# Gráfico
# --------------------------------------------------

fig_scatter_alvo_defensivo = px.scatter(
    scatter_alvo_defensivo,

    x="finalizacoes_alvo_concedidas_por_jogo",

    y="gols_sofridos_por_jogo",

    color="destaque",

    hover_name="clube",

    hover_data={
        "jogos": True,
        "gols_sofridos": True,
        "finalizacoes_concedidas_por_jogo": ":.2f",
        "finalizacoes_alvo_concedidas_por_jogo": ":.2f",
        "gols_sofridos_por_jogo": ":.2f",
        "clean_sheets": ":.2f",
        "destaque": False
    },

    color_discrete_map={
        "Clube selecionado":
            "#FFD700",

        "Demais clubes":
            "#7EC8F5"
    },

    labels={
        "finalizacoes_alvo_concedidas_por_jogo":
            "Finalizações no alvo concedidas por jogo",

        "gols_sofridos_por_jogo":
            "Gols sofridos por jogo",

        "finalizacoes_concedidas_por_jogo":
            "Finalizações concedidas por jogo",

        "clean_sheets":
            "Clean sheets (%)",

        "destaque":
            ""
    }
)


fig_scatter_alvo_defensivo.update_traces(
    marker=dict(
        size=12
    )
)


# --------------------------------------------------
# Linhas de referência
# --------------------------------------------------

fig_scatter_alvo_defensivo.add_vline(
    x=media_alvo_concedidas,
    line_dash="dash",
    annotation_text="Média de finalizações no alvo",
    annotation_position="top"
)


fig_scatter_alvo_defensivo.add_hline(
    y=media_gols_sofridos_alvo,
    line_dash="dash",
    annotation_text="Média de gols sofridos",
    annotation_position="right"
)


fig_scatter_alvo_defensivo.update_layout(
    xaxis_title="Finalizações no alvo concedidas por jogo",

    yaxis_title="Gols sofridos por jogo",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    )
)


# --------------------------------------------------
# Destacar clube selecionado
# --------------------------------------------------

if clube_selecionado != "Todos":

    clube_destaque_alvo = (
        scatter_alvo_defensivo[
            scatter_alvo_defensivo["clube"]
            == clube_selecionado
        ]
    )


    if not clube_destaque_alvo.empty:

        fig_scatter_alvo_defensivo.add_annotation(
            x=clube_destaque_alvo[
                "finalizacoes_alvo_concedidas_por_jogo"
            ].iloc[0],

            y=clube_destaque_alvo[
                "gols_sofridos_por_jogo"
            ].iloc[0],

            text=clube_selecionado,

            showarrow=True,

            arrowhead=2,

            ax=35,

            ay=-35
        )


st.plotly_chart(
    fig_scatter_alvo_defensivo,
    width="stretch"
)


# ==================================================
# EVOLUÇÃO DEFENSIVA DO CLUBE
# ==================================================

if club_id is not None:

    st.divider()

    st.subheader(
        f"Evolução defensiva do {clube_selecionado}"
    )

    st.write(
        "Acompanhe a evolução dos principais indicadores "
        "defensivos do clube ao longo das temporadas."
    )


    # --------------------------------------------------
    # Consulta histórica
    # --------------------------------------------------

    query_evolucao_defensiva = f"""
    WITH jogos_clube AS (

        SELECT
            season_id,

            away_goals AS gols_sofridos,

            away_shots AS finalizacoes_concedidas,

            away_shots_on_target
                AS finalizacoes_alvo_concedidas,

            CASE
                WHEN away_goals = 0 THEN 1
                ELSE 0
            END AS clean_sheet

        FROM matches

        WHERE home_team_id = {club_id}


        UNION ALL


        SELECT
            season_id,

            home_goals AS gols_sofridos,

            home_shots AS finalizacoes_concedidas,

            home_shots_on_target
                AS finalizacoes_alvo_concedidas,

            CASE
                WHEN home_goals = 0 THEN 1
                ELSE 0
            END AS clean_sheet

        FROM matches

        WHERE away_team_id = {club_id}
    )

    SELECT
        s.season,

        COUNT(*) AS jogos,

        ROUND(
            AVG(j.gols_sofridos)::numeric,
            2
        ) AS gols_sofridos_por_jogo,

        ROUND(
            AVG(j.finalizacoes_concedidas)::numeric,
            2
        ) AS finalizacoes_concedidas_por_jogo,

        ROUND(
            AVG(j.finalizacoes_alvo_concedidas)::numeric,
            2
        ) AS finalizacoes_alvo_concedidas_por_jogo,

        ROUND(
            (
                SUM(j.clean_sheet)::numeric
                / COUNT(*)
            ) * 100,
            2
        ) AS clean_sheets

    FROM jogos_clube j

    JOIN seasons s
        ON s.id = j.season_id

    GROUP BY
        s.id,
        s.season

    ORDER BY
        s.season;
    """


    evolucao_defensiva = executar_query(
        query_evolucao_defensiva
    )


    # --------------------------------------------------
    # Garantir valores numéricos
    # --------------------------------------------------

    colunas_numericas = [
        "gols_sofridos_por_jogo",
        "finalizacoes_concedidas_por_jogo",
        "finalizacoes_alvo_concedidas_por_jogo",
        "clean_sheets"
    ]


    for coluna in colunas_numericas:

        evolucao_defensiva[coluna] = (
            evolucao_defensiva[coluna]
            .astype(float)
        )


    # ==================================================
    # GRÁFICO 1
    # GOLS SOFRIDOS POR JOGO
    # ==================================================

    st.markdown(
        "#### Gols sofridos por jogo"
    )


    fig_gols_sofridos = px.line(
        evolucao_defensiva,

        x="season",

        y="gols_sofridos_por_jogo",

        markers=True,

        text="gols_sofridos_por_jogo",

        labels={
            "season":
                "Temporada",

            "gols_sofridos_por_jogo":
                "Gols sofridos por jogo"
        }
    )


    fig_gols_sofridos.update_traces(
        textposition="top center"
    )


    fig_gols_sofridos.update_layout(
        xaxis_title="Temporada",

        yaxis_title="Gols sofridos por jogo",

        hovermode="x unified"
    )


    # --------------------------------------------------
    # Destacar temporada selecionada
    # --------------------------------------------------

    if temporada_selecionada != "Todas":

        destaque_defesa = (
            evolucao_defensiva[
                evolucao_defensiva["season"]
                == temporada_selecionada
            ]
        )


        if not destaque_defesa.empty:

            fig_gols_sofridos.add_scatter(
                x=destaque_defesa[
                    "season"
                ],

                y=destaque_defesa[
                    "gols_sofridos_por_jogo"
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
        fig_gols_sofridos,
        width="stretch"
    )


    # ==================================================
    # GRÁFICO 2
    # FINALIZAÇÕES CONCEDIDAS
    # ==================================================

    st.markdown(
        "#### Finalizações concedidas"
    )


    evolucao_finalizacoes_defesa = (
        evolucao_defensiva[
            [
                "season",
                "finalizacoes_concedidas_por_jogo",
                "finalizacoes_alvo_concedidas_por_jogo"
            ]
        ]
        .melt(
            id_vars="season",

            var_name="indicador",

            value_name="valor"
        )
    )


    nomes_indicadores_defesa = {
        "finalizacoes_concedidas_por_jogo":
            "Finalizações concedidas por jogo",

        "finalizacoes_alvo_concedidas_por_jogo":
            "Finalizações no alvo concedidas por jogo"
    }


    evolucao_finalizacoes_defesa[
        "indicador"
    ] = (
        evolucao_finalizacoes_defesa[
            "indicador"
        ]
        .map(
            nomes_indicadores_defesa
        )
    )


    fig_finalizacoes_defesa = px.line(
        evolucao_finalizacoes_defesa,

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


    fig_finalizacoes_defesa.update_layout(
        xaxis_title="Temporada",

        yaxis_title="Média por jogo",

        hovermode="x unified",

        legend_title_text=""
    )


    st.plotly_chart(
        fig_finalizacoes_defesa,
        width="stretch"
    )


    # ==================================================
    # GRÁFICO 3
    # CLEAN SHEETS
    # ==================================================

    st.markdown(
        "#### Clean sheets por temporada"
    )


    fig_clean_sheets = px.bar(
        evolucao_defensiva,

        x="season",

        y="clean_sheets",

        text="clean_sheets",

        labels={
            "season":
                "Temporada",

            "clean_sheets":
                "Clean sheets (%)"
        }
    )


    fig_clean_sheets.update_traces(
        texttemplate="%{text:.2f}%",

        textposition="outside"
    )


    fig_clean_sheets.update_layout(
        xaxis_title="Temporada",

        yaxis_title="Clean sheets (%)",

        showlegend=False
    )


    st.plotly_chart(
        fig_clean_sheets,
        width="stretch"
    )