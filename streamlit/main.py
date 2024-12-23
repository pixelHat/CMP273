import streamlit as st
import plotly as pl
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
from criticalpath import Node

# https://github.com/okld/streamlit-elements?tab=readme-ov-file

import networkx as nx

from gantt import Application, StarPU

variables = pq.read_table("variable.parquet").to_pandas()
# st.write(variables)
ready_data = variables[variables["Type"] == "Ready"]
submitted_data = variables[variables["Type"] == "Submitted"]
submitted_chart = px.line(submitted_data, x="Start", y="Value", title="Submitted")
ready_chart = px.line(ready_data, x="Start", y="Value", title="Ready")

# st.plotly_chart(submitted_chart)


df_skipped = (
    pd.concat([ready_data.iloc[::6], ready_data.iloc[-1:]])
    .drop_duplicates()
    .reset_index(drop=True)
)

fig = px.scatter(
    df_skipped,
    x="Start",
    y="Value",
    color="Value",
    title="Abc",
)
fig.update_traces(mode="lines", line_shape="hv")
# st.plotly_chart(fig)


application = pq.read_table("application.parquet").to_pandas()

# st.write(application)

st.markdown("# Testes")

total_time = max(application["End"])
cpu0_spent = sum(
    [
        resource["Duration"]
        for (_, resource) in application.iterrows()
        if resource["ResourceId"] == "CPU0"
    ]
) / len(
    [_ for (_, resource) in application.iterrows() if resource["ResourceId"] == "CPU0"]
)


should_display_outliers = st.toggle("Outliers")
should_display_cpu_idless = st.toggle("CPU Idless")
gantt = Application(
    "application.parquet",
    should_display_outliers=should_display_outliers,
    show_idless_cpu=should_display_cpu_idless,
)


@st.fragment
def handle_application_chart_events():
    click_data = st.session_state.get("st", None)
    if (
        click_data
        and len(click_data["selection"]["points"]) > 0
        and not should_display_outliers
    ):
        id = click_data["selection"]["points"][0]["customdata"]["id"]
        gantt.highlight_task_depedency(id)
    else:
        gantt.highlight([])


handle_application_chart_events()


def application_on_select():
    if should_display_outliers:
        del st.session_state["st"]


st.plotly_chart(
    gantt.chart,
    use_container_width=True,
    on_select=application_on_select,
    key="st",
)


@st.fragment
def tmp():
    starpu_gantt = StarPU("starpu.parquet")
    # st.plotly_chart(starpu_gantt.chart(), use_container_width=True)


tmp()


def cpe_test():

    # id = "1"
    dag = pq.read_table("dag.parquet").to_pandas()
    st.write(dag)

    # Add new categories first
    dag["Dependent"] = dag["Dependent"].astype("category")
    dag["Dependent"] = dag["Dependent"].cat.add_categories(["root"])
    dag["Cost"] = dag["Cost"] * -1

    # 45220
    dag.loc[dag["JobId"] == "11", "Dependent"] = "1"
    dag.loc[dag["JobId"] == "1", "Dependent"] = "root"
    tuple_list = list(zip(dag["JobId"], dag["Dependent"], dag["Cost"]))
    graph = nx.DiGraph()
    graph.add_weighted_edges_from(tuple_list)
    critical_path = nx.dag_longest_path(graph)
    df = dag[dag["JobId"].isin(critical_path)]
    st.write(df["Cost"].sum())


# 45

# tasks = tuple(zip(dag["JobId"], dag["Cost"]))
# dag_without_the_root = dag[dag["JobId"] != "1"]
# depend = tuple(zip(dag_without_the_root["JobId"], dag_without_the_root["Dependent"]))
#
# proj = Node("Project")
# for t in tasks:
#     proj.add(Node(t[0], duration=t[1]))
#
# # add dependency
# for d in depend:
#     proj.link(d[0], d[1])
#
# # upadate
# st.write("calls update")
# proj.update_all()
#
# # crit_path = [str(n) for n in proj.get_critical_path()]
# total_time = proj.duration
# st.write("total finished")
#
# # st.write("critical path", crit_path)
# st.write("total time", total_time)
