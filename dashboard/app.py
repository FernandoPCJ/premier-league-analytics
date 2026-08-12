import streamlit as st

st.set_page_config(
    page_title="Premier League Analytics",
    page_icon="⚽",
    layout="wide"
)

pagina_visao_geral = st.Page(
    "pages/visao_geral.py",
    title="Visão Geral",
    icon="🏠",
    default=True
)

pagina_ataque = st.Page(
    "pages/ataque.py",
    title="Ataque",
    icon="⚽"
)

pagina_defesa = st.Page(
    "pages/defesa.py",
    title="Defesa",
    icon="🛡️"
)

pagina_disciplina = st.Page(
    "pages/disciplina.py",
    title="Disciplina",
    icon="🟨"
)

pagina_estatistica = st.Page(
    "pages/estatistica.py",
    title="Estatística",
    icon="📊"
)

navegacao = st.navigation(
    [
        pagina_visao_geral,
        pagina_ataque,
        pagina_defesa,
        pagina_disciplina,
        pagina_estatistica
    ]
)

navegacao.run()