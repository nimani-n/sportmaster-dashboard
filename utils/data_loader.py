import pandas as pd
import streamlit as st


REQUIRED_COLUMNS = {"site_version", "time", "title", "target"}


@st.cache_data
def load_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, sep=";")

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"В файле не хватает колонок: {', '.join(sorted(missing))}"
        )

    return df