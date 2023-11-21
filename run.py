import streamlit as st
import pandas as pd
from pysus.utilities.readdbc import read_dbc
import plotly.express as px
import altair as alt

#TRATAMENTO
dfs = []

for i in range(13):
    dfs.append(read_dbc('tb_tx_20' + str(i+10) + '-12.dbc', encoding='iso-8859-1'))
dfs.append(read_dbc('tb_tx_2023-09.dbc', encoding='iso-8859-1'))

for i in range(14):
    dfs[i]["BENEF_TOTA"] = pd.to_numeric(dfs[i]["BENEF_TOTA"])
    dfs[i]["POPULACAO"] = pd.to_numeric(dfs[i]["POPULACAO"])

grouped_dfs = []

for i in range(14):
    grouped_dfs.append(dfs[i].groupby(by=["SG_UF"], as_index=False).agg(
    {"BENEF_TOTA": "sum", "POPULACAO": "sum"}
    ))
    grouped_dfs[i] = grouped_dfs[i].drop([8,28]).reset_index()
    grouped_dfs[i]["PORCENT"] = grouped_dfs[i]["BENEF_TOTA"]/grouped_dfs[i]["POPULACAO"]*100
    grouped_dfs[i] = grouped_dfs[i].drop(columns = ["index", "BENEF_TOTA", "POPULACAO"])
    grouped_dfs[i] = grouped_dfs[i].set_index("SG_UF")

grouped_dfs[0]["2010"] = grouped_dfs[0]["PORCENT"] 
grouped_dfs[0] = grouped_dfs[0].drop(columns = ["PORCENT"])

for i in range(13):
    grouped_dfs[0]["20" + str(i+11)] = grouped_dfs[i+1]["PORCENT"]

#TITULO
st.write("""
# Taxa de cobertura de 2010 a 2023
""")

#PLOT
estados = st.multiselect(
        "Escolha o estado", list(grouped_dfs[0].index), ["RN"]
    )
if not estados:
    st.error("Selecione pelo menos um estado.")
else:
    data = grouped_dfs[0].loc[estados]
    st.write("Taxa de cobertura (%)", data.sort_index())

    data = data.T.reset_index()
    data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "ano", "value": "Taxa de cobertura (%)"}
        )
    chart = (
        alt.Chart(data)
        .mark_area(opacity=0.3)
        .encode(
            x="ano:T",
            y=alt.Y("Taxa de cobertura (%):Q", stack=None),
            color="SG_UF:N",
        )
    )
    st.altair_chart(chart, use_container_width=True)