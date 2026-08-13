import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from scipy import stats

from utils.database import executar_query

# ==================================================
# CABEÇALHO
# ==================================================

st.title("📊 Análise Estatística")

st.write(
    "Explore indicadores estatísticos da Premier League, "
    "comparando produção de gols, desempenho como mandante "
    "e desempenho como visitante."
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
        key="estatistica_temporada"
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
        key="estatistica_clube"
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
# FILTRO SQL DE TEMPORADA
# ==================================================

if season_id is None:

    filtro_temporada = ""

else:

    filtro_temporada = (
        f"WHERE season_id = {season_id}"
    )


# ==================================================
# ESTATÍSTICAS GERAIS DA LIGA
# ==================================================

if club_id is None:

    query_estatisticas = f"""
    SELECT
        COUNT(*) AS partidas,

        ROUND(
            AVG(home_goals + away_goals)::numeric,
            2
        ) AS media_gols,

        ROUND(
            AVG(home_goals)::numeric,
            2
        ) AS media_gols_casa,

        ROUND(
            AVG(away_goals)::numeric,
            2
        ) AS media_gols_fora,

        ROUND(
            AVG(home_goals - away_goals)::numeric,
            3
        ) AS diferenca_media

    FROM matches

    {filtro_temporada};
    """


    estatisticas = executar_query(
        query_estatisticas
    )


    partidas = int(
        estatisticas.loc[
            0,
            "partidas"
        ]
    )

    media_gols = float(
        estatisticas.loc[
            0,
            "media_gols"
        ]
    )

    media_gols_casa = float(
        estatisticas.loc[
            0,
            "media_gols_casa"
        ]
    )

    media_gols_fora = float(
        estatisticas.loc[
            0,
            "media_gols_fora"
        ]
    )

    diferenca_media = float(
        estatisticas.loc[
            0,
            "diferenca_media"
        ]
    )


    # --------------------------------------------------
    # Cards gerais
    # --------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        st.metric(
            label="Partidas",
            value=f"{partidas:,}".replace(",", ".")
        )


    with col2:

        st.metric(
            label="Gols por partida",
            value=f"{media_gols:.2f}"
        )


    with col3:

        st.metric(
            label="Gols do mandante por jogo",
            value=f"{media_gols_casa:.2f}"
        )


    with col4:

        st.metric(
            label="Gols do visitante por jogo",
            value=f"{media_gols_fora:.2f}"
        )


    with col5:

        st.metric(
            label="Diferença média casa - fora",
            value=f"{diferenca_media:.3f}"
        )


# ==================================================
# ESTATÍSTICAS DO CLUBE SELECIONADO
# ==================================================

else:

    if season_id is None:

        filtro_temporada_clube = ""

    else:

        filtro_temporada_clube = (
            f"AND season_id = {season_id}"
        )


    query_estatisticas_clube = f"""
    WITH jogos_clube AS (

        SELECT
            season_id,

            'home' AS local,

            home_goals AS gols_pro,

            away_goals AS gols_contra

        FROM matches

        WHERE home_team_id = {club_id}
        {filtro_temporada_clube}


        UNION ALL


        SELECT
            season_id,

            'away' AS local,

            away_goals AS gols_pro,

            home_goals AS gols_contra

        FROM matches

        WHERE away_team_id = {club_id}
        {filtro_temporada_clube}
    )

    SELECT
        COUNT(*) AS jogos,

        ROUND(
            AVG(gols_pro)::numeric,
            2
        ) AS gols_por_jogo,

        ROUND(
            AVG(
                CASE
                    WHEN local = 'home'
                    THEN gols_pro
                END
            )::numeric,
            2
        ) AS gols_casa,

        ROUND(
            AVG(
                CASE
                    WHEN local = 'away'
                    THEN gols_pro
                END
            )::numeric,
            2
        ) AS gols_fora,

        ROUND(
            (
                AVG(
                    CASE
                        WHEN local = 'home'
                        THEN gols_pro
                    END
                )
                -
                AVG(
                    CASE
                        WHEN local = 'away'
                        THEN gols_pro
                    END
                )
            )::numeric,
            3
        ) AS diferenca_casa_fora

    FROM jogos_clube;
    """


    estatisticas_clube = executar_query(
        query_estatisticas_clube
    )


    jogos = int(
        estatisticas_clube.loc[
            0,
            "jogos"
        ]
    )

    gols_por_jogo = float(
        estatisticas_clube.loc[
            0,
            "gols_por_jogo"
        ]
    )

    gols_casa = float(
        estatisticas_clube.loc[
            0,
            "gols_casa"
        ]
    )

    gols_fora = float(
        estatisticas_clube.loc[
            0,
            "gols_fora"
        ]
    )

    diferenca_casa_fora = float(
        estatisticas_clube.loc[
            0,
            "diferenca_casa_fora"
        ]
    )


    # --------------------------------------------------
    # Título do clube
    # --------------------------------------------------

    if temporada_selecionada == "Todas":

        st.caption(
            f"Indicadores do {clube_selecionado} "
            "no período analisado."
        )

    else:

        st.caption(
            f"Indicadores do {clube_selecionado} "
            f"na temporada {temporada_selecionada}."
        )


    # --------------------------------------------------
    # Cards do clube
    # --------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:

        st.metric(
            label="Jogos",
            value=jogos
        )


    with col2:

        st.metric(
            label="Gols por jogo",
            value=f"{gols_por_jogo:.2f}"
        )


    with col3:

        st.metric(
            label="Gols em casa por jogo",
            value=f"{gols_casa:.2f}"
        )


    with col4:

        st.metric(
            label="Gols fora por jogo",
            value=f"{gols_fora:.2f}"
        )


    with col5:

        st.metric(
            label="Diferença casa - fora",
            value=f"{diferenca_casa_fora:.3f}"
        )


# ==================================================
# EVOLUÇÃO DA VANTAGEM DE MANDO
# ==================================================

st.divider()


# --------------------------------------------------
# Definir título e descrição
# --------------------------------------------------

if club_id is None:

    st.subheader(
        "Evolução da vantagem de mando"
    )

    st.write(
        "Acompanhe a diferença média entre os gols marcados "
        "pelos mandantes e visitantes em cada temporada."
    )

else:

    st.subheader(
        f"Evolução da vantagem de mando do {clube_selecionado}"
    )

    st.write(
        f"Acompanhe a diferença entre a média de gols marcados "
        f"em casa e fora pelo {clube_selecionado} "
        "ao longo das temporadas."
    )


# ==================================================
# DADOS DA LIGA
# ==================================================

if club_id is None:

    query_mando = """
    SELECT
        s.season,

        COUNT(*) AS partidas,

        ROUND(
            AVG(m.home_goals)::numeric,
            3
        ) AS media_gols_casa,

        ROUND(
            AVG(m.away_goals)::numeric,
            3
        ) AS media_gols_fora,

        ROUND(
            AVG(
                m.home_goals - m.away_goals
            )::numeric,
            3
        ) AS diferenca_media

    FROM matches m

    JOIN seasons s
        ON s.id = m.season_id

    GROUP BY
        s.id,
        s.season

    ORDER BY
        s.season;
    """


# ==================================================
# DADOS DO CLUBE
# ==================================================

else:

    query_mando = f"""
    WITH jogos_clube AS (

        SELECT
            season_id,

            'home' AS local,

            home_goals AS gols_pro

        FROM matches

        WHERE home_team_id = {club_id}


        UNION ALL


        SELECT
            season_id,

            'away' AS local,

            away_goals AS gols_pro

        FROM matches

        WHERE away_team_id = {club_id}
    )

    SELECT
        s.season,

        COUNT(*) AS partidas,

        ROUND(
            AVG(
                CASE
                    WHEN j.local = 'home'
                    THEN j.gols_pro
                END
            )::numeric,
            3
        ) AS media_gols_casa,

        ROUND(
            AVG(
                CASE
                    WHEN j.local = 'away'
                    THEN j.gols_pro
                END
            )::numeric,
            3
        ) AS media_gols_fora,

        ROUND(
            (
                AVG(
                    CASE
                        WHEN j.local = 'home'
                        THEN j.gols_pro
                    END
                )
                -
                AVG(
                    CASE
                        WHEN j.local = 'away'
                        THEN j.gols_pro
                    END
                )
            )::numeric,
            3
        ) AS diferenca_media

    FROM jogos_clube j

    JOIN seasons s
        ON s.id = j.season_id

    GROUP BY
        s.id,
        s.season

    ORDER BY
        s.season;
    """


# ==================================================
# EXECUTAR CONSULTA
# ==================================================

vantagem_mando = executar_query(
    query_mando
)


# --------------------------------------------------
# Garantir tipos numéricos
# --------------------------------------------------

vantagem_mando["diferenca_media"] = (
    vantagem_mando["diferenca_media"]
    .astype(float)
)

vantagem_mando["media_gols_casa"] = (
    vantagem_mando["media_gols_casa"]
    .astype(float)
)

vantagem_mando["media_gols_fora"] = (
    vantagem_mando["media_gols_fora"]
    .astype(float)
)


# ==================================================
# GRÁFICO
# ==================================================

fig_mando = px.line(
    vantagem_mando,

    x="season",

    y="diferenca_media",

    markers=True,

    text="diferenca_media",

    hover_data={
        "media_gols_casa": ":.3f",
        "media_gols_fora": ":.3f",
        "partidas": True,
        "diferenca_media": ":.3f"
    },

    labels={
        "season":
            "Temporada",

        "diferenca_media":
            "Diferença média de gols (casa - fora)",

        "media_gols_casa":
            "Gols em casa por jogo",

        "media_gols_fora":
            "Gols fora por jogo",

        "partidas":
            "Jogos"
    }
)


fig_mando.update_traces(
    textposition="top center"
)


# --------------------------------------------------
# Linha de referência
# --------------------------------------------------

fig_mando.add_hline(
    y=0,

    line_dash="dash",

    annotation_text="Sem vantagem de mando",

    annotation_position="bottom right"
)


fig_mando.update_layout(
    xaxis_title="Temporada",

    yaxis_title="Diferença média de gols (casa - fora)",

    hovermode="x unified"
)


# ==================================================
# DESTACAR TEMPORADA SELECIONADA
# ==================================================

if temporada_selecionada != "Todas":

    destaque_mando = vantagem_mando[
        vantagem_mando["season"]
        == temporada_selecionada
    ]


    if not destaque_mando.empty:

        fig_mando.add_scatter(
            x=destaque_mando["season"],

            y=destaque_mando[
                "diferenca_media"
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


# ==================================================
# EXIBIR GRÁFICO
# ==================================================

st.plotly_chart(
    fig_mando,
    width="stretch"
)

# ==================================================
# TESTE ESTATÍSTICO DA VANTAGEM DE MANDO
# ==================================================

if club_id is None:

    st.divider()

    st.subheader(
        "Significância estatística da vantagem de mando"
    )

    st.write(
        "Avalie se a diferença entre os gols marcados por "
        "mandantes e visitantes é estatisticamente significativa."
    )


    # --------------------------------------------------
    # Dados por partida
    # --------------------------------------------------

    if season_id is None:

        filtro_teste = ""

    else:

        filtro_teste = (
            f"WHERE m.season_id = {season_id}"
        )


    query_teste_mando = f"""
    SELECT
        s.season,
        m.home_goals,
        m.away_goals

    FROM matches m

    JOIN seasons s
        ON s.id = m.season_id

    {filtro_teste}

    ORDER BY
        m.match_date;
    """


    dados_teste = executar_query(
        query_teste_mando
    )


    dados_teste["home_goals"] = (
        dados_teste["home_goals"]
        .astype(float)
    )

    dados_teste["away_goals"] = (
        dados_teste["away_goals"]
        .astype(float)
    )


    # --------------------------------------------------
    # Diferença casa - fora
    # --------------------------------------------------

    diferencas = (
        dados_teste["home_goals"]
        - dados_teste["away_goals"]
    )


    media_diferenca = (
        diferencas.mean()
    )

    desvio_diferenca = (
        diferencas.std(ddof=1)
    )


    # --------------------------------------------------
    # Teste t pareado
    # --------------------------------------------------

    teste_t = stats.ttest_rel(
        dados_teste["home_goals"],
        dados_teste["away_goals"]
    )


    # --------------------------------------------------
    # Tamanho de efeito de Cohen
    # --------------------------------------------------

    cohen_dz = (
        media_diferenca
        / desvio_diferenca
    )


    # --------------------------------------------------
    # Intervalo de confiança de 95%
    # --------------------------------------------------

    erro_padrao = stats.sem(
        diferencas
    )


    ic_95 = stats.t.interval(
        confidence=0.95,

        df=len(diferencas) - 1,

        loc=media_diferenca,

        scale=erro_padrao
    )


    # --------------------------------------------------
    # Wilcoxon
    # --------------------------------------------------

    teste_wilcoxon = stats.wilcoxon(
        dados_teste["home_goals"],
        dados_teste["away_goals"],
        alternative="two-sided"
    )


    # ==================================================
    # CARDS
    # ==================================================

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            label="Diferença média",
            value=f"{media_diferenca:.3f}"
        )


    with col2:

        st.metric(
            label="IC 95%",
            value=(
                f"{ic_95[0]:.3f} a "
                f"{ic_95[1]:.3f}"
            )
        )


    with col3:

        st.metric(
            label="Cohen's dz",
            value=f"{cohen_dz:.3f}"
        )


    with col4:

        if teste_t.pvalue < 0.001:

            p_texto = "< 0,001"

        else:

            p_texto = (
                f"{teste_t.pvalue:.3f}"
            )


        st.metric(
            label="p-valor do teste t",
            value=p_texto
        )


    # --------------------------------------------------
    # Interpretação
    # --------------------------------------------------

    if teste_t.pvalue < 0.05:

        resultado_t = (
            "Diferença estatisticamente significativa"
        )

    else:

        resultado_t = (
            "Diferença não estatisticamente significativa"
        )


    if abs(cohen_dz) < 0.20:

        interpretacao_efeito = "muito pequeno"

    elif abs(cohen_dz) < 0.50:

        interpretacao_efeito = "pequeno"

    elif abs(cohen_dz) < 0.80:

        interpretacao_efeito = "moderado"

    else:

        interpretacao_efeito = "grande"


    st.info(
        f"{resultado_t}. "
        f"O tamanho de efeito observado é "
        f"{interpretacao_efeito} "
        f"(Cohen's dz = {cohen_dz:.3f})."
    )


    # --------------------------------------------------
    # Resultado complementar de Wilcoxon
    # --------------------------------------------------

    if teste_wilcoxon.pvalue < 0.001:

        p_wilcoxon = "< 0,001"

    else:

        p_wilcoxon = (
            f"{teste_wilcoxon.pvalue:.3f}"
        )


    st.caption(
        "Teste não paramétrico de Wilcoxon: "
        f"p-valor {p_wilcoxon}."
    )

# ==================================================
# SIGNIFICÂNCIA POR TEMPORADA + CORREÇÃO DE HOLM
# ==================================================

if club_id is None:

    st.divider()

    st.subheader(
        "Vantagem de mando por temporada"
    )

    st.write(
        "Compare a vantagem de mando entre as temporadas "
        "considerando a correção de Holm para múltiplos testes."
    )


    # --------------------------------------------------
    # Buscar dados de todas as temporadas
    # --------------------------------------------------

    query_testes_temporadas = """
    SELECT
        s.season,
        m.home_goals,
        m.away_goals

    FROM matches m

    JOIN seasons s
        ON s.id = m.season_id

    ORDER BY
        s.season,
        m.match_date;
    """


    dados_temporadas = executar_query(
        query_testes_temporadas
    )


    dados_temporadas["home_goals"] = (
        dados_temporadas["home_goals"]
        .astype(float)
    )

    dados_temporadas["away_goals"] = (
        dados_temporadas["away_goals"]
        .astype(float)
    )


    # --------------------------------------------------
    # Teste t para cada temporada
    # --------------------------------------------------

    resultados_temporadas = []


    for temporada, grupo in dados_temporadas.groupby(
        "season",
        sort=True
    ):

        diferencas_temporada = (
            grupo["home_goals"]
            - grupo["away_goals"]
        )


        media_temporada = (
            diferencas_temporada.mean()
        )


        desvio_temporada = (
            diferencas_temporada.std(ddof=1)
        )


        teste_temporada = stats.ttest_rel(
            grupo["home_goals"],
            grupo["away_goals"]
        )


        # ----------------------------------------------
        # Cohen's dz
        # ----------------------------------------------

        if desvio_temporada == 0:

            cohen_temporada = 0.0

        else:

            cohen_temporada = (
                media_temporada
                / desvio_temporada
            )


        resultados_temporadas.append(
            {
                "season":
                    temporada,

                "diferenca":
                    media_temporada,

                "p_valor":
                    teste_temporada.pvalue,

                "cohen_dz":
                    cohen_temporada
            }
        )


    testes_temporadas = pd.DataFrame(
        resultados_temporadas
    )


    # ==================================================
    # CORREÇÃO DE HOLM
    # ==================================================

    p_valores = (
        testes_temporadas["p_valor"]
        .to_numpy()
    )


    quantidade_testes = len(
        p_valores
    )


    ordem = np.argsort(
        p_valores
    )


    p_holm = np.zeros(
        quantidade_testes
    )


    maior_ajustado = 0.0


    for posicao, indice_original in enumerate(
        ordem
    ):

        fator = (
            quantidade_testes
            - posicao
        )


        valor_ajustado = (
            p_valores[indice_original]
            * fator
        )


        # Holm precisa preservar monotonicidade
        valor_ajustado = max(
            valor_ajustado,
            maior_ajustado
        )


        valor_ajustado = min(
            valor_ajustado,
            1.0
        )


        p_holm[
            indice_original
        ] = valor_ajustado


        maior_ajustado = (
            valor_ajustado
        )


    testes_temporadas[
        "p_holm"
    ] = p_holm


    testes_temporadas[
        "significativo_holm"
    ] = (
        testes_temporadas[
            "p_holm"
        ] < 0.05
    )


    # ==================================================
    # TABELA PARA EXIBIÇÃO
    # ==================================================

    tabela_holm = (
        testes_temporadas[
            [
                "season",
                "diferenca",
                "p_valor",
                "p_holm",
                "cohen_dz",
                "significativo_holm"
            ]
        ]
        .copy()
    )


    tabela_holm.columns = [
        "Temporada",
        "Diferença média",
        "p-valor",
        "p ajustado (Holm)",
        "Cohen's dz",
        "Significativa"
    ]


    tabela_holm[
        "Diferença média"
    ] = (
        tabela_holm[
            "Diferença média"
        ]
        .map(
            lambda x: f"{x:.3f}"
        )
    )


    tabela_holm[
        "p-valor"
    ] = (
        tabela_holm[
            "p-valor"
        ]
        .map(
            lambda x:
            "< 0,001"
            if x < 0.001
            else f"{x:.4f}"
        )
    )


    tabela_holm[
        "p ajustado (Holm)"
    ] = (
        tabela_holm[
            "p ajustado (Holm)"
        ]
        .map(
            lambda x:
            "< 0,001"
            if x < 0.001
            else f"{x:.4f}"
        )
    )


    tabela_holm[
        "Cohen's dz"
    ] = (
        tabela_holm[
            "Cohen's dz"
        ]
        .map(
            lambda x: f"{x:.3f}"
        )
    )


    tabela_holm[
        "Significativa"
    ] = (
        tabela_holm[
            "Significativa"
        ]
        .map(
            {
                True: "Sim",
                False: "Não"
            }
        )
    )


    st.dataframe(
        tabela_holm,
        width="stretch",
        hide_index=True
    )


    # ==================================================
    # RESUMO
    # ==================================================

    quantidade_significativas = int(
        testes_temporadas[
            "significativo_holm"
        ].sum()
    )


    st.info(
        f"{quantidade_significativas} das "
        f"{quantidade_testes} temporadas apresentaram "
        "vantagem de mando estatisticamente significativa "
        "após a correção de Holm."
    )

# ==================================================
# CORRELAÇÃO ENTRE INDICADORES DAS PARTIDAS
# ==================================================

st.divider()

st.subheader(
    "Correlação entre indicadores das partidas"
)

st.write(
    "Analise a relação linear entre gols, finalizações, "
    "finalizações no alvo, faltas e cartões."
)


# --------------------------------------------------
# Filtro de temporada
# --------------------------------------------------

if season_id is None:

    filtro_correlacao_temporada = ""

else:

    filtro_correlacao_temporada = (
        f"WHERE season_id = {season_id}"
    )


# --------------------------------------------------
# Montar base por equipe/partida
# --------------------------------------------------

query_correlacao = f"""
WITH dados_equipes AS (

    SELECT
        season_id,
        home_team_id AS team_id,

        home_goals AS goals,
        home_shots AS shots,
        home_shots_on_target AS shots_on_target,
        home_fouls AS fouls,
        home_yellow_cards AS yellow_cards,
        home_red_cards AS red_cards

    FROM matches

    {filtro_correlacao_temporada}


    UNION ALL


    SELECT
        season_id,
        away_team_id AS team_id,

        away_goals AS goals,
        away_shots AS shots,
        away_shots_on_target AS shots_on_target,
        away_fouls AS fouls,
        away_yellow_cards AS yellow_cards,
        away_red_cards AS red_cards

    FROM matches

    {filtro_correlacao_temporada}
)

SELECT
    season_id,
    team_id,
    goals,
    shots,
    shots_on_target,
    fouls,
    yellow_cards,
    red_cards

FROM dados_equipes
"""


# --------------------------------------------------
# Aplicar clube selecionado
# --------------------------------------------------

if club_id is not None:

    query_correlacao += (
        f"\nWHERE team_id = {club_id}"
    )


query_correlacao += ";"


dados_correlacao = executar_query(
    query_correlacao
)


# --------------------------------------------------
# Variáveis analisadas
# --------------------------------------------------

variaveis_correlacao = [
    "goals",
    "shots",
    "shots_on_target",
    "fouls",
    "yellow_cards",
    "red_cards"
]


# --------------------------------------------------
# Garantir valores numéricos
# --------------------------------------------------

for coluna in variaveis_correlacao:

    dados_correlacao[coluna] = (
        dados_correlacao[coluna]
        .astype(float)
    )


# --------------------------------------------------
# Matriz de Pearson
# --------------------------------------------------

matriz_pearson = (
    dados_correlacao[
        variaveis_correlacao
    ]
    .corr(
        method="pearson"
    )
)


# --------------------------------------------------
# Nomes em português
# --------------------------------------------------

nomes_variaveis = {
    "goals":
        "Gols",

    "shots":
        "Finalizações",

    "shots_on_target":
        "Finalizações no alvo",

    "fouls":
        "Faltas",

    "yellow_cards":
        "Amarelos",

    "red_cards":
        "Vermelhos"
}


matriz_exibicao = (
    matriz_pearson
    .rename(
        index=nomes_variaveis,
        columns=nomes_variaveis
    )
)


# ==================================================
# HEATMAP
# ==================================================

fig_correlacao = go.Figure(
    data=go.Heatmap(
        z=matriz_exibicao.values,

        x=matriz_exibicao.columns,

        y=matriz_exibicao.index,

        zmin=-1,

        zmax=1,

        colorscale="Viridis",

        text=np.round(
            matriz_exibicao.values,
            2
        ),

        texttemplate="%{text:.2f}",

        hovertemplate=(
            "%{y} × %{x}"
            "<br>Correlação de Pearson: %{z:.3f}"
            "<extra></extra>"
        )
    )
)


fig_correlacao.update_layout(
    xaxis_title="",

    yaxis_title="",

    height=600
)


st.plotly_chart(
    fig_correlacao,
    width="stretch"
)

# ==================================================
# PRINCIPAIS CORRELAÇÕES
# ==================================================

st.markdown(
    "#### Relações selecionadas"
)


pares_correlacao = [
    (
        "Finalizações × Gols",
        "shots",
        "goals"
    ),

    (
        "Finalizações no alvo × Gols",
        "shots_on_target",
        "goals"
    ),

    (
        "Finalizações × Finalizações no alvo",
        "shots",
        "shots_on_target"
    ),

    (
        "Faltas × Cartões amarelos",
        "fouls",
        "yellow_cards"
    ),

    (
        "Faltas × Cartões vermelhos",
        "fouls",
        "red_cards"
    )
]


resumo_correlacoes = []


for nome, variavel_1, variavel_2 in pares_correlacao:

    r = matriz_pearson.loc[
        variavel_1,
        variavel_2
    ]


    resumo_correlacoes.append(
        {
            "Relação":
                nome,

            "Pearson r":
                round(r, 3)
        }
    )


tabela_correlacoes = pd.DataFrame(
    resumo_correlacoes
)


st.dataframe(
    tabela_correlacoes,
    width="stretch",
    hide_index=True
)

# ==================================================
# COMPARAÇÃO PEARSON X SPEARMAN
# ==================================================

st.divider()

st.subheader(
    "Comparação entre Pearson e Spearman"
)

st.write(
    "Compare a correlação linear de Pearson com a correlação "
    "por postos de Spearman nas principais relações analisadas."
)


# --------------------------------------------------
# Relações analisadas
# --------------------------------------------------

pares_comparacao = [
    (
        "Finalizações × Gols",
        "shots",
        "goals"
    ),

    (
        "Finalizações no alvo × Gols",
        "shots_on_target",
        "goals"
    ),

    (
        "Finalizações × Finalizações no alvo",
        "shots",
        "shots_on_target"
    ),

    (
        "Faltas × Amarelos",
        "fouls",
        "yellow_cards"
    ),

    (
        "Faltas × Vermelhos",
        "fouls",
        "red_cards"
    )
]


# --------------------------------------------------
# Calcular Pearson e Spearman
# --------------------------------------------------

resultados_comparacao = []


for nome, variavel_1, variavel_2 in pares_comparacao:

    # Pearson
    pearson_r, pearson_p = stats.pearsonr(
        dados_correlacao[variavel_1],
        dados_correlacao[variavel_2]
    )


    # Spearman
    spearman_rho, spearman_p = stats.spearmanr(
        dados_correlacao[variavel_1],
        dados_correlacao[variavel_2]
    )


    resultados_comparacao.append(
        {
            "Relação": nome,

            "Pearson":
                pearson_r,

            "Spearman":
                spearman_rho,

            "Diferença absoluta":
                abs(
                    pearson_r
                    - spearman_rho
                ),

            "p Pearson":
                pearson_p,

            "p Spearman":
                spearman_p
        }
    )


comparacao_correlacoes = pd.DataFrame(
    resultados_comparacao
)


# ==================================================
# TABELA
# ==================================================

tabela_comparacao = (
    comparacao_correlacoes[
        [
            "Relação",
            "Pearson",
            "Spearman",
            "Diferença absoluta"
        ]
    ]
    .copy()
)


tabela_comparacao[
    "Pearson"
] = (
    tabela_comparacao[
        "Pearson"
    ]
    .map(
        lambda x: f"{x:.3f}"
    )
)


tabela_comparacao[
    "Spearman"
] = (
    tabela_comparacao[
        "Spearman"
    ]
    .map(
        lambda x: f"{x:.3f}"
    )
)


tabela_comparacao[
    "Diferença absoluta"
] = (
    tabela_comparacao[
        "Diferença absoluta"
    ]
    .map(
        lambda x: f"{x:.3f}"
    )
)


st.dataframe(
    tabela_comparacao,
    width="stretch",
    hide_index=True
)


# ==================================================
# PREPARAR DADOS PARA O GRÁFICO
# ==================================================

comparacao_long = (
    comparacao_correlacoes[
        [
            "Relação",
            "Pearson",
            "Spearman"
        ]
    ]
    .melt(
        id_vars="Relação",

        var_name="Método",

        value_name="Correlação"
    )
)


# ==================================================
# GRÁFICO
# ==================================================

fig_comparacao = px.bar(
    comparacao_long,

    x="Relação",

    y="Correlação",

    color="Método",

    barmode="group",

    text="Correlação",

    labels={
        "Relação":
            "",

        "Correlação":
            "Coeficiente de correlação",

        "Método":
            ""
    }
)


fig_comparacao.update_traces(
    texttemplate="%{text:.3f}",
    textposition="outside"
)


fig_comparacao.update_layout(
    yaxis_title="Coeficiente de correlação",

    xaxis_title="",

    legend_title_text=""
)


st.plotly_chart(
    fig_comparacao,
    width="stretch"
)