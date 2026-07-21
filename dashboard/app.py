from __future__ import annotations

import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")


st.set_page_config(page_title="Brazil Indicators", layout="wide")
st.title("Brazil Indicators Dashboard")


@st.cache_data(ttl=300)
def load_records() -> pd.DataFrame:
    response = requests.get(f"{API_URL}/indicators", params={"limit": 500}, timeout=10)
    response.raise_for_status()
    return pd.DataFrame(response.json())


try:
    data = load_records()
except requests.RequestException as exc:
    st.error(f"API indisponivel: {exc}")
    st.stop()

if data.empty:
    st.info("Nenhum dado encontrado. Execute a coleta pela API ou pelo scheduler.")
    st.stop()

indicator_options = sorted(data["indicator_code"].unique())
selected_indicator = st.selectbox("Indicador", indicator_options)
filtered_data = data[data["indicator_code"] == selected_indicator].sort_values("year")

latest_row = filtered_data.iloc[-1]
first_row = filtered_data.iloc[0]

metric_columns = st.columns(3)
metric_columns[0].metric("Ultimo ano", int(latest_row["year"]))
metric_columns[1].metric("Valor mais recente", f"{latest_row['value']:,.2f}")
metric_columns[2].metric("Observacoes", len(filtered_data))

st.subheader(str(latest_row["indicator_name"]))
st.line_chart(filtered_data.set_index("year")["value"])

st.dataframe(
    filtered_data[
        [
            "country_name",
            "indicator_code",
            "indicator_name",
            "year",
            "value",
            "source",
            "collected_at",
        ]
    ],
    use_container_width=True,
)

st.caption(f"Serie iniciada em {int(first_row['year'])}. Fonte: World Bank API.")
