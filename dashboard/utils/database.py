import streamlit as st
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.engine import URL


@st.cache_resource
def get_engine():

    config = st.secrets["postgres"]

    url = URL.create(
        drivername="postgresql+psycopg",
        username=config["user"],
        password=config["password"],
        host=config["host"],
        port=int(config["port"]),
        database=config["database"],
        query={
            "sslmode": "require",
            "channel_binding": "require"
        }
    )

    engine = create_engine(
        url,
        pool_pre_ping=True
    )

    return engine


@st.cache_data
def executar_query(query):

    engine = get_engine()

    return pd.read_sql_query(
        query,
        engine
    )