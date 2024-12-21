import streamlit as st
import plotly as pl
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

from gantt import Application, StarPU

# tmp = pq.read_table("variable.parquet").to_pandas()
# dag = pq.read_table("dag.parquet").to_pandas()
# st.write(dag)

st.markdown("# Todos")
st.markdown(
    """
- [x] Show tasks depedency
- [ ] Add the critical path estimation
- [ ] Add charts for the submmited and ready
- [ ] Allows user to select the dataset
- [ ] Allows user to select more than one dataset and display all of them side by side.
- [ ] Add button to show outlier
- [ ] Adds idleless worker

### Extra

- [ ] Extract gantt chart to a class
- [ ] Add slider to aggregate equal tasks that have distance less than a value
"""
)

application = pq.read_table("application.parquet").to_pandas()

st.write(application)

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


gantt = Application("application.parquet")


@st.fragment
def handle_application_chart_events():
    if st.button("CPB"):
        gantt.toggle_cpe()
    click_data = st.session_state.get("st", None)
    if click_data and len(click_data["selection"]["points"]) > 0:
        id = click_data["selection"]["points"][0]["customdata"]["id"]
        st.write(f"You clicked on: {click_data}")
        gantt.highlight_task_depedency(id)
    else:
        gantt.highlight([])


handle_application_chart_events()

st.plotly_chart(
    gantt.chart,
    use_container_width=True,
    on_select="rerun",
    key="st",
)

starpu_gantt = StarPU("starpu.parquet")
st.plotly_chart(starpu_gantt.chart(), use_container_width=True)

import networkx as nx

# id = "1"
dag = pq.read_table("dag.parquet", columns=["JobId", "Dependent", "Cost"]).to_pandas()

# Add new categories first
dag["Dependent"] = dag["Dependent"].astype("category")
dag["Dependent"] = dag["Dependent"].cat.add_categories(["root"])

# 45220
dag.loc[dag["JobId"] == "11", "Dependent"] = "1"
dag.loc[dag["JobId"] == "1", "Dependent"] = "root"
tuple_list = list(zip(dag["JobId"], dag["Dependent"], dag["Cost"]))
graph = nx.DiGraph()
graph.add_weighted_edges_from(tuple_list)
critical_path = nx.dag_longest_path(graph)
df = application[application["JobId"].isin(critical_path)]
st.write(df["Duration"].sum())
# 45

st.write(dag)
st.write(graph.nodes["1"])
# crit_path = [str(n) for n in graph.nodes.get_critical_path()]
