import streamlit as st
import plotly.express as px
import pandas as pd

from utils.database import executar_query


# ==================================================
# CABEÇALHO
# ==================================================

st.title("🟨 Análise Disciplinar")

st.write(
    "Explore o comportamento disciplinar dos clubes da Premier League "
    "por meio de faltas, cartões amarelos e cartões vermelhos."
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
        key="disciplina_temporada"
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
        key="disciplina_clube"
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
# BASE DISCIPLINAR
# ==================================================

query_disciplina = f"""
WITH jogos_disciplina AS (

    SELECT
        season_id,

        home_team_id AS team_id,

        home_fouls AS faltas,

        home_yellow_cards AS amarelos,

        home_red_cards AS vermelhos

    FROM matches

    WHERE 1 = 1
    {filtro_temporada}


    UNION ALL


    SELECT
        season_id,

        away_team_id AS team_id,

        away_fouls AS faltas,

        away_yellow_cards AS amarelos,

        away_red_cards AS vermelhos

    FROM matches

    WHERE 1 = 1
    {filtro_temporada}
)

SELECT
    COUNT(*) AS jogos,

    SUM(faltas) AS faltas,

    SUM(amarelos) AS amarelos,

    SUM(vermelhos) AS vermelhos,

    SUM(amarelos + vermelhos) AS total_cartoes,

    ROUND(
        AVG(faltas)::numeric,
        2
    ) AS faltas_por_jogo,

    ROUND(
        AVG(amarelos)::numeric,
        2
    ) AS amarelos_por_jogo,

    ROUND(
        AVG(vermelhos)::numeric,
        3
    ) AS vermelhos_por_jogo,

    ROUND(
        AVG(amarelos + vermelhos)::numeric,
        2
    ) AS cartoes_por_jogo

FROM jogos_disciplina

{filtro_clube};
"""


dados_disciplina = executar_query(
    query_disciplina
)


# ==================================================
# KPIs DISCIPLINARES
# ==================================================

faltas_por_jogo = float(
    dados_disciplina.loc[
        0,
        "faltas_por_jogo"
    ]
)


amarelos_por_jogo = float(
    dados_disciplina.loc[
        0,
        "amarelos_por_jogo"
    ]
)


total_vermelhos = int(
    dados_disciplina.loc[
        0,
        "vermelhos"
    ]
)


cartoes_por_jogo = float(
    dados_disciplina.loc[
        0,
        "cartoes_por_jogo"
    ]
)


# --------------------------------------------------
# Cards
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="Faltas por jogo",
        value=f"{faltas_por_jogo:.2f}"
    )


with col2:

    st.metric(
        label="Cartões amarelos por jogo",
        value=f"{amarelos_por_jogo:.2f}"
    )


with col3:

    st.metric(
        label="Cartões vermelhos",
        value=total_vermelhos
    )


with col4:

    st.metric(
        label="Cartões por jogo",
        value=f"{cartoes_por_jogo:.2f}"
    )


# ==================================================
# RANKING DISCIPLINAR
# ==================================================

st.divider()


if temporada_selecionada == "Todas":

    st.subheader(
        "Ranking disciplinar dos clubes no período"
    )

else:

    st.subheader(
        f"Ranking disciplinar da temporada "
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
# Consulta do ranking disciplinar
# --------------------------------------------------

query_ranking_disciplina = f"""
WITH jogos_disciplina AS (

    SELECT
        home_team_id AS team_id,

        home_fouls AS faltas,

        home_yellow_cards AS amarelos,

        home_red_cards AS vermelhos

    FROM matches

    {filtro_ranking}


    UNION ALL


    SELECT
        away_team_id AS team_id,

        away_fouls AS faltas,

        away_yellow_cards AS amarelos,

        away_red_cards AS vermelhos

    FROM matches

    {filtro_ranking}
)

SELECT
    t.name AS clube,

    COUNT(*) AS jogos,

    SUM(j.faltas) AS faltas,

    SUM(j.amarelos) AS amarelos,

    SUM(j.vermelhos) AS vermelhos,

    ROUND(
        AVG(j.faltas)::numeric,
        2
    ) AS faltas_por_jogo,

    ROUND(
        AVG(j.amarelos)::numeric,
        2
    ) AS amarelos_por_jogo,

    ROUND(
        AVG(j.amarelos + j.vermelhos)::numeric,
        2
    ) AS cartoes_por_jogo,

    ROUND(
        (
            SUM(j.vermelhos)::numeric
            / COUNT(*)
        ) * 100,
        2
    ) AS vermelhos_por_100_jogos

FROM jogos_disciplina j

JOIN teams t
    ON t.id = j.team_id

GROUP BY
    t.id,
    t.name;
"""


ranking_disciplina = executar_query(
    query_ranking_disciplina
)


# --------------------------------------------------
# Garantir valores numéricos
# --------------------------------------------------

colunas_ranking_numericas = [
    "faltas_por_jogo",
    "amarelos_por_jogo",
    "cartoes_por_jogo",
    "vermelhos_por_100_jogos"
]


for coluna in colunas_ranking_numericas:

    ranking_disciplina[coluna] = (
        ranking_disciplina[coluna]
        .astype(float)
    )


# --------------------------------------------------
# Escolha da métrica
# --------------------------------------------------

metrica_disciplina = st.selectbox(
    "Selecione a métrica disciplinar:",
    [
        "Faltas por jogo",
        "Cartões amarelos por jogo",
        "Cartões por jogo",
        "Cartões vermelhos a cada 100 jogos"
    ],
    key="disciplina_metrica_ranking"
)


mapa_metricas_disciplina = {

    "Faltas por jogo":
        "faltas_por_jogo",

    "Cartões amarelos por jogo":
        "amarelos_por_jogo",

    "Cartões por jogo":
        "cartoes_por_jogo",

    "Cartões vermelhos a cada 100 jogos":
        "vermelhos_por_100_jogos"
}


coluna_disciplina = mapa_metricas_disciplina[
    metrica_disciplina
]


st.caption(
    "Valores maiores indicam maior incidência disciplinar."
)


# --------------------------------------------------
# Ordenar ranking
# --------------------------------------------------

ranking_ordenado = (
    ranking_disciplina
    .sort_values(
        by=coluna_disciplina,
        ascending=False
    )
    .copy()
)


top10_disciplina = (
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
    not in top10_disciplina["clube"].values
):

    clube_fora_top10 = ranking_ordenado[
        ranking_ordenado["clube"]
        == clube_selecionado
    ]


    if not clube_fora_top10.empty:

        top10_disciplina = (
            top10_disciplina
            .iloc[:9]
            .copy()
        )


        top10_disciplina = pd.concat(
            [
                top10_disciplina,
                clube_fora_top10
            ],
            ignore_index=True
        )


# --------------------------------------------------
# Ordenar para gráfico horizontal
# --------------------------------------------------

top10_disciplina = (
    top10_disciplina
    .sort_values(
        by=coluna_disciplina,
        ascending=True
    )
    .copy()
)


# --------------------------------------------------
# Texto das barras
# --------------------------------------------------

top10_disciplina["texto"] = (
    top10_disciplina[coluna_disciplina]
    .map(
        lambda x: f"{x:.2f}"
    )
)


# --------------------------------------------------
# Destacar clube selecionado
# --------------------------------------------------

top10_disciplina["destaque"] = (
    top10_disciplina["clube"]
    .apply(
        lambda clube:
        "Clube selecionado"
        if clube == clube_selecionado
        else "Demais clubes"
    )
)


# --------------------------------------------------
# Preservar a posição real do ranking
# --------------------------------------------------

ordem_clubes_disciplina = (
    top10_disciplina["clube"]
    .tolist()
)


# --------------------------------------------------
# Gráfico
# --------------------------------------------------

fig_ranking_disciplina = px.bar(
    top10_disciplina,

    x=coluna_disciplina,

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

        coluna_disciplina:
            metrica_disciplina,

        "destaque":
            ""
    }
)


fig_ranking_disciplina.update_traces(
    textposition="outside"
)


fig_ranking_disciplina.update_layout(
    xaxis_title=metrica_disciplina,

    yaxis_title="",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    ),

    yaxis=dict(
        categoryorder="array",
        categoryarray=ordem_clubes_disciplina
    )
)


st.plotly_chart(
    fig_ranking_disciplina,
    width="stretch"
)


# ==================================================
# FALTAS X CARTÕES AMARELOS
# ==================================================

st.divider()

st.subheader(
    "Faltas por jogo × Cartões amarelos por jogo"
)

st.write(
    "Compare a frequência de faltas cometidas pelos clubes "
    "com a média de cartões amarelos recebidos por partida."
)


# --------------------------------------------------
# Preparar dados
# --------------------------------------------------

scatter_disciplina = ranking_disciplina.copy()


scatter_disciplina["destaque"] = (
    scatter_disciplina["clube"]
    .apply(
        lambda clube:
        "Clube selecionado"
        if clube == clube_selecionado
        else "Demais clubes"
    )
)


# --------------------------------------------------
# Médias de referência
# --------------------------------------------------

media_faltas = (
    scatter_disciplina[
        "faltas_por_jogo"
    ].mean()
)


media_amarelos = (
    scatter_disciplina[
        "amarelos_por_jogo"
    ].mean()
)


# --------------------------------------------------
# Gráfico
# --------------------------------------------------

fig_scatter_disciplina = px.scatter(
    scatter_disciplina,

    x="faltas_por_jogo",

    y="amarelos_por_jogo",

    color="destaque",

    hover_name="clube",

    hover_data={
        "jogos": True,
        "faltas": True,
        "amarelos": True,
        "vermelhos": True,
        "faltas_por_jogo": ":.2f",
        "amarelos_por_jogo": ":.2f",
        "cartoes_por_jogo": ":.2f",
        "vermelhos_por_100_jogos": ":.2f",
        "destaque": False
    },

    color_discrete_map={
        "Clube selecionado":
            "#FFD700",

        "Demais clubes":
            "#7EC8F5"
    },

    labels={
        "faltas_por_jogo":
            "Faltas por jogo",

        "amarelos_por_jogo":
            "Cartões amarelos por jogo",

        "cartoes_por_jogo":
            "Cartões por jogo",

        "vermelhos_por_100_jogos":
            "Vermelhos a cada 100 jogos",

        "destaque":
            ""
    }
)


fig_scatter_disciplina.update_traces(
    marker=dict(
        size=12
    )
)


# --------------------------------------------------
# Linhas de referência
# --------------------------------------------------

fig_scatter_disciplina.add_vline(
    x=media_faltas,
    line_dash="dash",
    annotation_text="Média de faltas",
    annotation_position="top"
)


fig_scatter_disciplina.add_hline(
    y=media_amarelos,
    line_dash="dash",
    annotation_text="Média de amarelos",
    annotation_position="right"
)


fig_scatter_disciplina.update_layout(
    xaxis_title="Faltas por jogo",

    yaxis_title="Cartões amarelos por jogo",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    )
)


# --------------------------------------------------
# Destacar clube selecionado
# --------------------------------------------------

if clube_selecionado != "Todos":

    clube_destaque = scatter_disciplina[
        scatter_disciplina["clube"]
        == clube_selecionado
    ]


    if not clube_destaque.empty:

        fig_scatter_disciplina.add_annotation(
            x=clube_destaque[
                "faltas_por_jogo"
            ].iloc[0],

            y=clube_destaque[
                "amarelos_por_jogo"
            ].iloc[0],

            text=clube_selecionado,

            showarrow=True,

            arrowhead=2,

            ax=35,

            ay=-35
        )


st.plotly_chart(
    fig_scatter_disciplina,
    width="stretch"
)


# ==================================================
# CARTÕES VERMELHOS A CADA 100 JOGOS
# ==================================================

st.divider()

st.subheader(
    "Cartões vermelhos a cada 100 jogos"
)

st.write(
    "Compare a incidência proporcional de cartões vermelhos "
    "entre os clubes."
)


# --------------------------------------------------
# Preparar ranking
# --------------------------------------------------

ranking_vermelhos = (
    ranking_disciplina
    .sort_values(
        by="vermelhos_por_100_jogos",
        ascending=False
    )
    .copy()
)


top10_vermelhos = (
    ranking_vermelhos
    .head(10)
    .copy()
)


# --------------------------------------------------
# Garantir que o clube selecionado apareça
# --------------------------------------------------

if (
    clube_selecionado != "Todos"
    and clube_selecionado
    not in top10_vermelhos["clube"].values
):

    clube_fora_top10 = ranking_vermelhos[
        ranking_vermelhos["clube"]
        == clube_selecionado
    ]


    if not clube_fora_top10.empty:

        top10_vermelhos = (
            top10_vermelhos
            .iloc[:9]
            .copy()
        )


        top10_vermelhos = pd.concat(
            [
                top10_vermelhos,
                clube_fora_top10
            ],
            ignore_index=True
        )


# --------------------------------------------------
# Ordenar para gráfico horizontal
# --------------------------------------------------

top10_vermelhos = (
    top10_vermelhos
    .sort_values(
        by="vermelhos_por_100_jogos",
        ascending=True
    )
    .copy()
)


# --------------------------------------------------
# Texto das barras
# --------------------------------------------------

top10_vermelhos["texto"] = (
    top10_vermelhos[
        "vermelhos_por_100_jogos"
    ]
    .map(
        lambda x: f"{x:.2f}"
    )
)


# --------------------------------------------------
# Destaque do clube selecionado
# --------------------------------------------------

top10_vermelhos["destaque"] = (
    top10_vermelhos["clube"]
    .apply(
        lambda clube:
        "Clube selecionado"
        if clube == clube_selecionado
        else "Demais clubes"
    )
)


# --------------------------------------------------
# Preservar a ordem real
# --------------------------------------------------

ordem_clubes_vermelhos = (
    top10_vermelhos["clube"]
    .tolist()
)


# --------------------------------------------------
# Gráfico
# --------------------------------------------------

fig_vermelhos = px.bar(
    top10_vermelhos,

    x="vermelhos_por_100_jogos",

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

    hover_data={
        "jogos": True,
        "vermelhos": True,
        "vermelhos_por_100_jogos": ":.2f",
        "destaque": False
    },

    labels={
        "clube":
            "Clube",

        "vermelhos_por_100_jogos":
            "Vermelhos a cada 100 jogos",

        "vermelhos":
            "Cartões vermelhos",

        "jogos":
            "Jogos",

        "destaque":
            ""
    }
)


fig_vermelhos.update_traces(
    textposition="outside"
)


fig_vermelhos.update_layout(
    xaxis_title="Cartões vermelhos a cada 100 jogos",

    yaxis_title="",

    legend_title_text="",

    showlegend=(
        clube_selecionado != "Todos"
    ),

    yaxis=dict(
        categoryorder="array",
        categoryarray=ordem_clubes_vermelhos
    )
)


st.plotly_chart(
    fig_vermelhos,
    width="stretch"
)


# ==================================================
# EVOLUÇÃO DISCIPLINAR DO CLUBE
# ==================================================

if club_id is not None:

    st.divider()

    st.subheader(
        f"Evolução disciplinar do {clube_selecionado}"
    )

    st.write(
        "Acompanhe a evolução dos principais indicadores "
        "disciplinares do clube ao longo das temporadas."
    )


    # --------------------------------------------------
    # Consulta histórica
    # --------------------------------------------------

    query_evolucao_disciplina = f"""
    WITH jogos_clube AS (

        SELECT
            season_id,

            home_fouls AS faltas,

            home_yellow_cards AS amarelos,

            home_red_cards AS vermelhos

        FROM matches

        WHERE home_team_id = {club_id}


        UNION ALL


        SELECT
            season_id,

            away_fouls AS faltas,

            away_yellow_cards AS amarelos,

            away_red_cards AS vermelhos

        FROM matches

        WHERE away_team_id = {club_id}
    )

    SELECT
        s.season,

        COUNT(*) AS jogos,

        ROUND(
            AVG(j.faltas)::numeric,
            2
        ) AS faltas_por_jogo,

        ROUND(
            AVG(j.amarelos)::numeric,
            2
        ) AS amarelos_por_jogo,

        ROUND(
            AVG(j.amarelos + j.vermelhos)::numeric,
            2
        ) AS cartoes_por_jogo,

        SUM(j.vermelhos)
            AS vermelhos,

        ROUND(
            (
                SUM(j.vermelhos)::numeric
                / COUNT(*)
            ) * 100,
            2
        ) AS vermelhos_por_100_jogos

    FROM jogos_clube j

    JOIN seasons s
        ON s.id = j.season_id

    GROUP BY
        s.id,
        s.season

    ORDER BY
        s.season;
    """


    evolucao_disciplina = executar_query(
        query_evolucao_disciplina
    )


    # --------------------------------------------------
    # Garantir valores numéricos
    # --------------------------------------------------

    colunas_evolucao_numericas = [
        "faltas_por_jogo",
        "amarelos_por_jogo",
        "cartoes_por_jogo",
        "vermelhos_por_100_jogos"
    ]


    for coluna in colunas_evolucao_numericas:

        evolucao_disciplina[coluna] = (
            evolucao_disciplina[coluna]
            .astype(float)
        )


    # ==================================================
    # GRÁFICO 1
    # FALTAS POR JOGO
    # ==================================================

    st.markdown(
        "#### Faltas por jogo"
    )


    fig_faltas_evolucao = px.line(
        evolucao_disciplina,

        x="season",

        y="faltas_por_jogo",

        markers=True,

        text="faltas_por_jogo",

        labels={
            "season":
                "Temporada",

            "faltas_por_jogo":
                "Faltas por jogo"
        }
    )


    fig_faltas_evolucao.update_traces(
        textposition="top center"
    )


    fig_faltas_evolucao.update_layout(
        xaxis_title="Temporada",

        yaxis_title="Faltas por jogo",

        hovermode="x unified"
    )


    # --------------------------------------------------
    # Destacar temporada selecionada
    # --------------------------------------------------

    if temporada_selecionada != "Todas":

        destaque_disciplina = (
            evolucao_disciplina[
                evolucao_disciplina["season"]
                == temporada_selecionada
            ]
        )


        if not destaque_disciplina.empty:

            fig_faltas_evolucao.add_scatter(
                x=destaque_disciplina[
                    "season"
                ],

                y=destaque_disciplina[
                    "faltas_por_jogo"
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
        fig_faltas_evolucao,
        width="stretch"
    )


    # ==================================================
    # GRÁFICO 2
    # CARTÕES POR JOGO
    # ==================================================

    st.markdown(
        "#### Cartões por jogo"
    )


    evolucao_cartoes = (
        evolucao_disciplina[
            [
                "season",
                "amarelos_por_jogo",
                "cartoes_por_jogo"
            ]
        ]
        .melt(
            id_vars="season",

            var_name="indicador",

            value_name="valor"
        )
    )


    nomes_indicadores_cartoes = {
        "amarelos_por_jogo":
            "Cartões amarelos por jogo",

        "cartoes_por_jogo":
            "Total de cartões por jogo"
    }


    evolucao_cartoes[
        "indicador"
    ] = (
        evolucao_cartoes[
            "indicador"
        ]
        .map(
            nomes_indicadores_cartoes
        )
    )


    fig_cartoes_evolucao = px.line(
        evolucao_cartoes,

        x="season",

        y="valor",

        color="indicador",

        markers=True,

        labels={
            "season":
                "Temporada",

            "valor":
                "Cartões por jogo",

            "indicador":
                ""
        }
    )


    fig_cartoes_evolucao.update_layout(
        xaxis_title="Temporada",

        yaxis_title="Cartões por jogo",

        hovermode="x unified",

        legend_title_text=""
    )


    # --------------------------------------------------
    # Destacar temporada no gráfico de cartões
    # --------------------------------------------------

    if temporada_selecionada != "Todas":

        destaque_cartoes = (
            evolucao_cartoes[
                evolucao_cartoes["season"]
                == temporada_selecionada
            ]
        )


        if not destaque_cartoes.empty:

            fig_cartoes_evolucao.add_scatter(
                x=destaque_cartoes[
                    "season"
                ],

                y=destaque_cartoes[
                    "valor"
                ],

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
        fig_cartoes_evolucao,
        width="stretch"
    )


    # ==================================================
    # GRÁFICO 3
    # CARTÕES VERMELHOS A CADA 100 JOGOS
    # ==================================================

    st.markdown(
        "#### Cartões vermelhos a cada 100 jogos"
    )


    evolucao_disciplina[
        "destaque_temporada"
    ] = (
        evolucao_disciplina[
            "season"
        ]
        .apply(
            lambda temporada:
            "Temporada selecionada"
            if temporada == temporada_selecionada
            else "Demais temporadas"
        )
    )


    ordem_temporadas = (
        evolucao_disciplina[
            "season"
        ]
        .tolist()
    )


    fig_vermelhos_evolucao = px.bar(
        evolucao_disciplina,

        x="season",

        y="vermelhos_por_100_jogos",

        text="vermelhos_por_100_jogos",

        color="destaque_temporada",

        color_discrete_map={
            "Temporada selecionada":
                "#FFD700",

            "Demais temporadas":
                "#7EC8F5"
        },

        hover_data={
            "jogos": True,
            "vermelhos": True,
            "vermelhos_por_100_jogos": ":.2f",
            "destaque_temporada": False
        },

        labels={
            "season":
                "Temporada",

            "vermelhos_por_100_jogos":
                "Vermelhos a cada 100 jogos",

            "vermelhos":
                "Cartões vermelhos",

            "jogos":
                "Jogos",

            "destaque_temporada":
                ""
        }
    )


    fig_vermelhos_evolucao.update_traces(
        texttemplate="%{text:.2f}",

        textposition="outside"
    )


    fig_vermelhos_evolucao.update_layout(
        xaxis_title="Temporada",

        yaxis_title="Cartões vermelhos a cada 100 jogos",

        legend_title_text="",

        showlegend=(
            temporada_selecionada != "Todas"
        ),

        xaxis=dict(
            categoryorder="array",
            categoryarray=ordem_temporadas
        )
    )


    st.plotly_chart(
        fig_vermelhos_evolucao,
        width="stretch"
    )