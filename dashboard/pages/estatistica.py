import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from scipy import stats

from utils.database import executar_query


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================

def formatar_p_valor(valor, casas=4):
    if pd.isna(valor):
        return "N/A"

    if valor < 0.001:
        return "< 0,001"

    return f"{valor:.{casas}f}".replace(".", ",")


def calcular_correlacao_segura(serie_1, serie_2, metodo="pearson"):
    dados = pd.concat(
        [serie_1, serie_2],
        axis=1
    ).dropna()

    if (
        len(dados) < 3
        or dados.iloc[:, 0].nunique() < 2
        or dados.iloc[:, 1].nunique() < 2
    ):
        return np.nan, np.nan

    if metodo == "pearson":
        return stats.pearsonr(
            dados.iloc[:, 0],
            dados.iloc[:, 1]
        )

    return stats.spearmanr(
        dados.iloc[:, 0],
        dados.iloc[:, 1]
    )


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
    # Contexto do clube
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
# DADOS DA VANTAGEM DE MANDO
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


vantagem_mando = executar_query(
    query_mando
)


# --------------------------------------------------
# Garantir tipos numéricos
# --------------------------------------------------

colunas_mando_numericas = [
    "diferenca_media",
    "media_gols_casa",
    "media_gols_fora"
]


for coluna in colunas_mando_numericas:

    vantagem_mando[coluna] = (
        vantagem_mando[coluna]
        .astype(float)
    )


# ==================================================
# GRÁFICO DA VANTAGEM DE MANDO
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


# --------------------------------------------------
# Destacar temporada selecionada
# --------------------------------------------------

if temporada_selecionada != "Todas":

    destaque_mando = (
        vantagem_mando[
            vantagem_mando["season"]
            == temporada_selecionada
        ]
    )


    if not destaque_mando.empty:

        fig_mando.add_scatter(
            x=destaque_mando[
                "season"
            ],

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
    # Diferenças casa - fora
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
    # Cohen's dz
    # --------------------------------------------------

    if (
        pd.isna(desvio_diferenca)
        or desvio_diferenca == 0
    ):

        cohen_dz = np.nan

    else:

        cohen_dz = (
            media_diferenca
            / desvio_diferenca
        )


    # --------------------------------------------------
    # Intervalo de confiança de 95%
    # --------------------------------------------------

    if len(diferencas) >= 2:

        erro_padrao = stats.sem(
            diferencas
        )


        ic_95 = stats.t.interval(
            confidence=0.95,

            df=len(diferencas) - 1,

            loc=media_diferenca,

            scale=erro_padrao
        )

    else:

        ic_95 = (
            np.nan,
            np.nan
        )


    # --------------------------------------------------
    # Wilcoxon
    # --------------------------------------------------

    if np.allclose(
        diferencas.to_numpy(),
        0
    ):

        p_wilcoxon_valor = 1.0

    else:

        teste_wilcoxon = stats.wilcoxon(
            diferencas,
            alternative="two-sided"
        )

        p_wilcoxon_valor = (
            teste_wilcoxon.pvalue
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

        if (
            pd.isna(ic_95[0])
            or pd.isna(ic_95[1])
        ):

            ic_texto = "N/A"

        else:

            ic_texto = (
                f"{ic_95[0]:.3f} a "
                f"{ic_95[1]:.3f}"
            )


        st.metric(
            label="IC 95%",
            value=ic_texto
        )


    with col3:

        if pd.isna(cohen_dz):

            cohen_texto = "N/A"

        else:

            cohen_texto = (
                f"{cohen_dz:.3f}"
            )


        st.metric(
            label="Cohen's dz",
            value=cohen_texto
        )


    with col4:

        st.metric(
            label="p-valor do teste t",
            value=formatar_p_valor(
                teste_t.pvalue,
                casas=3
            )
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


    if pd.isna(cohen_dz):

        interpretacao_efeito = (
            "não disponível"
        )

    elif abs(cohen_dz) < 0.20:

        interpretacao_efeito = "muito pequeno"

    elif abs(cohen_dz) < 0.50:

        interpretacao_efeito = "pequeno"

    elif abs(cohen_dz) < 0.80:

        interpretacao_efeito = "moderado"

    else:

        interpretacao_efeito = "grande"


    if pd.isna(cohen_dz):

        texto_efeito = (
            "O tamanho de efeito não pôde ser calculado."
        )

    else:

        texto_efeito = (
            f"O tamanho de efeito observado é "
            f"{interpretacao_efeito} "
            f"(Cohen's dz = {cohen_dz:.3f})."
        )


    st.info(
        f"{resultado_t}. "
        f"{texto_efeito}"
    )


    st.caption(
        "Teste não paramétrico de Wilcoxon: "
        f"p-valor {formatar_p_valor(p_wilcoxon_valor, casas=3)}."
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


        if (
            pd.isna(desvio_temporada)
            or desvio_temporada == 0
        ):

            cohen_temporada = np.nan

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
        testes_temporadas[
            "p_valor"
        ]
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
    # TABELA
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
            lambda x:
            f"{x:.3f}"
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
            formatar_p_valor(
                x,
                casas=4
            )
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
            formatar_p_valor(
                x,
                casas=4
            )
        )
    )


    tabela_holm[
        "Cohen's dz"
    ] = (
        tabela_holm[
            "Cohen's dz"
        ]
        .map(
            lambda x:
            "N/A"
            if pd.isna(x)
            else f"{x:.3f}"
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
# Base por equipe/partida
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


if club_id is not None:

    query_correlacao += (
        f"\nWHERE team_id = {club_id}"
    )


query_correlacao += ";"


dados_correlacao = executar_query(
    query_correlacao
)


variaveis_correlacao = [
    "goals",
    "shots",
    "shots_on_target",
    "fouls",
    "yellow_cards",
    "red_cards"
]


for coluna in variaveis_correlacao:

    dados_correlacao[coluna] = (
        dados_correlacao[coluna]
        .astype(float)
    )


# --------------------------------------------------
# Aviso para variáveis constantes
# --------------------------------------------------

variaveis_constantes = [
    coluna
    for coluna in variaveis_correlacao
    if dados_correlacao[coluna].nunique() < 2
]


if variaveis_constantes:

    st.caption(
        "Algumas correlações podem aparecer como indisponíveis "
        "porque uma das variáveis não apresentou variação no "
        "recorte selecionado."
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
# RELAÇÕES SELECIONADAS
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
                (
                    "N/A"
                    if pd.isna(r)
                    else f"{r:.3f}"
                )
        }
    )


st.dataframe(
    pd.DataFrame(
        resumo_correlacoes
    ),
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


resultados_comparacao = []


for nome, variavel_1, variavel_2 in pares_comparacao:

    pearson_r, pearson_p = calcular_correlacao_segura(
        dados_correlacao[variavel_1],
        dados_correlacao[variavel_2],
        metodo="pearson"
    )


    spearman_rho, spearman_p = calcular_correlacao_segura(
        dados_correlacao[variavel_1],
        dados_correlacao[variavel_2],
        metodo="spearman"
    )


    if (
        pd.isna(pearson_r)
        or pd.isna(spearman_rho)
    ):

        diferenca_absoluta = np.nan

    else:

        diferenca_absoluta = abs(
            pearson_r
            - spearman_rho
        )


    resultados_comparacao.append(
        {
            "Relação": nome,
            "Pearson": pearson_r,
            "Spearman": spearman_rho,
            "Diferença absoluta": diferenca_absoluta,
            "p Pearson": pearson_p,
            "p Spearman": spearman_p
        }
    )


comparacao_correlacoes = pd.DataFrame(
    resultados_comparacao
)


# ==================================================
# TABELA PEARSON X SPEARMAN
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


for coluna in [
    "Pearson",
    "Spearman",
    "Diferença absoluta"
]:

    tabela_comparacao[coluna] = (
        tabela_comparacao[coluna]
        .map(
            lambda x:
            "N/A"
            if pd.isna(x)
            else f"{x:.3f}"
        )
    )


st.dataframe(
    tabela_comparacao,
    width="stretch",
    hide_index=True
)


# ==================================================
# GRÁFICO PEARSON X SPEARMAN
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
    .dropna(
        subset=[
            "Correlação"
        ]
    )
)


if comparacao_long.empty:

    st.info(
        "Não há variação suficiente no recorte selecionado "
        "para comparar Pearson e Spearman."
    )

else:

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


# ==================================================
# DESEMPENHO MÉDIO X CONSISTÊNCIA DOS CLUBES
# ==================================================

st.divider()

st.subheader(
    "Desempenho médio × Consistência dos clubes"
)

st.write(
    "Compare o desempenho médio dos clubes com a variação "
    "dos resultados entre temporadas. Para esta análise, "
    "são considerados clubes com pelo menos 5 temporadas."
)

st.caption(
    "Esta análise utiliza o histórico completo das temporadas, "
    "independentemente do filtro de temporada selecionado no topo."
)


# ==================================================
# PONTOS POR CLUBE E TEMPORADA
# ==================================================

query_consistencia = """
WITH jogos_clubes AS (

    SELECT
        season_id,
        home_team_id AS team_id,
        home_goals AS gols_pro,
        away_goals AS gols_contra,

        CASE
            WHEN home_goals > away_goals THEN 3
            WHEN home_goals = away_goals THEN 1
            ELSE 0
        END AS pontos

    FROM matches


    UNION ALL


    SELECT
        season_id,
        away_team_id AS team_id,
        away_goals AS gols_pro,
        home_goals AS gols_contra,

        CASE
            WHEN away_goals > home_goals THEN 3
            WHEN away_goals = home_goals THEN 1
            ELSE 0
        END AS pontos

    FROM matches
),

clube_temporada AS (

    SELECT
        season_id,
        team_id,

        COUNT(*) AS jogos,

        SUM(pontos) AS pontos,

        SUM(gols_pro) AS gols_pro,

        SUM(gols_contra) AS gols_contra,

        SUM(gols_pro - gols_contra) AS saldo_gols,

        SUM(pontos)::numeric
        / COUNT(*) AS pontos_por_jogo

    FROM jogos_clubes

    GROUP BY
        season_id,
        team_id
)

SELECT
    s.season,
    t.name AS clube,
    ct.jogos,
    ct.pontos,
    ct.gols_pro,
    ct.gols_contra,
    ct.saldo_gols,
    ct.pontos_por_jogo

FROM clube_temporada ct

JOIN seasons s
    ON s.id = ct.season_id

JOIN teams t
    ON t.id = ct.team_id

ORDER BY
    t.name,
    s.season;
"""


dados_consistencia = executar_query(
    query_consistencia
)


dados_consistencia[
    "pontos_por_jogo"
] = (
    dados_consistencia[
        "pontos_por_jogo"
    ]
    .astype(float)
)


dados_consistencia[
    "saldo_gols"
] = (
    dados_consistencia[
        "saldo_gols"
    ]
    .astype(float)
)


# ==================================================
# RESUMO POR CLUBE
# ==================================================

resumo_consistencia = (
    dados_consistencia
    .groupby(
        "clube",
        as_index=False
    )
    .agg(
        temporadas=(
            "season",
            "nunique"
        ),

        media_pontos_jogo=(
            "pontos_por_jogo",
            "mean"
        ),

        desvio_pontos_jogo=(
            "pontos_por_jogo",
            "std"
        ),

        media_saldo_gols=(
            "saldo_gols",
            "mean"
        )
    )
)


resumo_consistencia = (
    resumo_consistencia[
        resumo_consistencia[
            "temporadas"
        ] >= 5
    ]
    .copy()
)


resumo_consistencia[
    "media_pontos_jogo"
] = (
    resumo_consistencia[
        "media_pontos_jogo"
    ]
    .round(3)
)


resumo_consistencia[
    "desvio_pontos_jogo"
] = (
    resumo_consistencia[
        "desvio_pontos_jogo"
    ]
    .round(3)
)


resumo_consistencia[
    "media_saldo_gols"
] = (
    resumo_consistencia[
        "media_saldo_gols"
    ]
    .round(3)
)


# ==================================================
# MÉDIAS DE REFERÊNCIA
# ==================================================

media_geral_pontos = (
    resumo_consistencia[
        "media_pontos_jogo"
    ]
    .mean()
)


media_geral_desvio = (
    resumo_consistencia[
        "desvio_pontos_jogo"
    ]
    .mean()
)


# ==================================================
# CLASSIFICAÇÃO DOS CLUBES
# ==================================================

def classificar_clube(linha):

    alto_desempenho = (
        linha["media_pontos_jogo"]
        >= media_geral_pontos
    )

    consistente = (
        linha["desvio_pontos_jogo"]
        <= media_geral_desvio
    )


    if alto_desempenho and consistente:

        return (
            "Alto desempenho + consistente"
        )


    if alto_desempenho and not consistente:

        return (
            "Alto desempenho + volátil"
        )


    if not alto_desempenho and consistente:

        return (
            "Abaixo da média + consistente"
        )


    return (
        "Abaixo da média + volátil"
    )


resumo_consistencia[
    "perfil"
] = (
    resumo_consistencia.apply(
        classificar_clube,
        axis=1
    )
)


# ==================================================
# DESTAQUE DO CLUBE
# ==================================================

resumo_consistencia[
    "destaque"
] = (
    resumo_consistencia[
        "clube"
    ]
    .apply(
        lambda clube:
        "Clube selecionado"
        if clube == clube_selecionado
        else "Demais clubes"
    )
)


clube_consistencia = (
    resumo_consistencia[
        resumo_consistencia[
            "clube"
        ] == clube_selecionado
    ]
)


clube_incluido_consistencia = (
    clube_selecionado != "Todos"
    and not clube_consistencia.empty
)


# ==================================================
# INDICADORES DE REFERÊNCIA
# ==================================================

col1, col2 = st.columns(2)


with col1:

    st.metric(
        label="Média geral de pontos por jogo",
        value=f"{media_geral_pontos:.3f}"
    )


with col2:

    st.metric(
        label="Média do desvio entre temporadas",
        value=f"{media_geral_desvio:.3f}"
    )


# ==================================================
# SCATTER DE CONSISTÊNCIA
# ==================================================

fig_consistencia = px.scatter(
    resumo_consistencia,

    x="media_pontos_jogo",

    y="desvio_pontos_jogo",

    hover_name="clube",

    color="destaque",

    color_discrete_map={
        "Clube selecionado":
            "#FFD700",

        "Demais clubes":
            "#7EC8F5"
    },

    hover_data={
        "temporadas": True,
        "media_pontos_jogo": ":.3f",
        "desvio_pontos_jogo": ":.3f",
        "media_saldo_gols": ":.3f",
        "perfil": True,
        "destaque": False
    },

    labels={
        "media_pontos_jogo":
            "Média de pontos por jogo",

        "desvio_pontos_jogo":
            "Desvio padrão entre temporadas",

        "temporadas":
            "Temporadas",

        "media_saldo_gols":
            "Saldo médio de gols",

        "perfil":
            "Perfil",

        "destaque":
            ""
    }
)


fig_consistencia.update_traces(
    marker=dict(
        size=13
    )
)


fig_consistencia.add_vline(
    x=media_geral_pontos,

    line_dash="dash",

    annotation_text="Média de desempenho",

    annotation_position="top"
)


fig_consistencia.add_hline(
    y=media_geral_desvio,

    line_dash="dash",

    annotation_text="Média de variação",

    annotation_position="right"
)


fig_consistencia.update_layout(
    xaxis_title="Média de pontos por jogo",

    yaxis_title="Desvio padrão entre temporadas",

    legend_title_text="",

    showlegend=clube_incluido_consistencia
)


# --------------------------------------------------
# Nome do clube selecionado
# --------------------------------------------------

if clube_incluido_consistencia:

    fig_consistencia.add_annotation(
        x=clube_consistencia[
            "media_pontos_jogo"
        ].iloc[0],

        y=clube_consistencia[
            "desvio_pontos_jogo"
        ].iloc[0],

        text=clube_selecionado,

        showarrow=True,

        arrowhead=2,

        ax=40,

        ay=-35
    )


elif clube_selecionado != "Todos":

    st.info(
        f"O {clube_selecionado} não possui pelo menos "
        "5 temporadas no período analisado e, por isso, "
        "não entra na análise de consistência."
    )


st.plotly_chart(
    fig_consistencia,
    width="stretch"
)


# ==================================================
# TABELA RESUMIDA
# ==================================================

st.markdown(
    "#### Classificação dos clubes"
)


tabela_consistencia = (
    resumo_consistencia[
        [
            "clube",
            "temporadas",
            "media_pontos_jogo",
            "desvio_pontos_jogo",
            "perfil"
        ]
    ]
    .sort_values(
        by="media_pontos_jogo",
        ascending=False
    )
    .copy()
)


tabela_consistencia.columns = [
    "Clube",
    "Temporadas",
    "Média de pontos por jogo",
    "Desvio entre temporadas",
    "Perfil"
]


st.dataframe(
    tabela_consistencia,
    width="stretch",
    hide_index=True
)