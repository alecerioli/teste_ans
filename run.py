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
# Dados da ANS (Taxa de cobertura)
""")

#PLOT E TABELA
estados = st.multiselect(
        "Escolha o estado", list(grouped_dfs[0].index), ["RN"]
    )

if not estados:
    st.error("Selecione pelo menos um estado.")
else:
    data = grouped_dfs[0].loc[estados]
    data1 = data
    data = data.T.reset_index()
    data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "ano", "value": "taxa"}
        )

    hover = alt.selection_point(
        fields=["ano"],
        nearest=True,
        on="mouseover",
        empty=False,
    )

    chart = (
        alt.Chart(data, title="Taxa de cobertura de 2010 a 2023")
        .mark_line()
        .encode(
            x=alt.X("ano:T", title="Ano"),
            y=alt.Y("taxa:Q", stack=None, title="Taxa de cobertura (%)"),
            color=alt.Color("SG_UF:N", title="Estado"),
        )
    )

    points = chart.transform_filter(hover).mark_circle(size=65)

    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="ano:T",
            y="taxa:Q",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("year(ano)" , title="Ano"),
                alt.Tooltip("taxa", title="Taxa de cobertura (%)"),
                alt.Tooltip("SG_UF:N", title="Estado"),
            ],
        )
        .add_params(hover)
    )

    st.altair_chart((chart + points + tooltips).interactive(), use_container_width=True)
    data1 = data1.rename_axis('Estado')
    st.write(data1.sort_index())