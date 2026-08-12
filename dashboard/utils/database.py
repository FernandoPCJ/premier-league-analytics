import streamlit as st
import pandas as pd

from sqlalchemy import create_engine


@st.cache_resource
def get_engine():

    config = st.secrets["postgres"]

    url = (
        f"postgresql+psycopg://"
        f"{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}"
        f"/{config['database']}"
    )

    engine = create_engine(url)

    return engine


@st.cache_data
def executar_query(query):

    engine = get_engine()

    return pd.read_sql_query(
        query,
        engine
    )