import streamlit as st
import pandas as pd
from pysus.utilities.readdbc import read_dbc
import plotly.express as px

dfs = read_dbc('teste.dbc', encoding='iso-8859-1')
dfs["BENEF_TOTA"] = pd.to_numeric(dfs["BENEF_TOTA"])
dfs["POPULACAO"] = pd.to_numeric(dfs["POPULACAO"])
grouped_df = dfs.groupby(by=["SG_UF"], as_index=False).agg(
    {"BENEF_TOTA": "sum", "POPULACAO": "sum"}
)
grouped_df = grouped_df.drop([8,28]).reset_index()
grouped_df["PORCENT"] = grouped_df["BENEF_TOTA"]/grouped_df["POPULACAO"]*100
fig = px.bar(
    data_frame=grouped_df,
    x="SG_UF",
    y="PORCENT",
    labels={
            "SG_UF": "Estado",
            "PORCENT": "Porcentagem",
            },
)
st.write("""
# Taxa de cobertura Setembro 2023
""")
st.plotly_chart(fig)