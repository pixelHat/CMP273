from dataclasses import dataclass
import pyarrow.parquet as pq
import streamlit as st
import plotly.graph_objects as go
from functools import cache, cached_property

import networkx as nx


@dataclass
class Application:
    file_name: str
    highlighted: list[str]
    cpe: bool

    def __init__(
        self,
        file_name: str,
        should_display_outliers: bool = False,
        show_idless_cpu: bool = False,
        show_abe: bool = False,
    ):
        self.file_name = file_name
        self.application = pq.read_table("application.parquet").to_pandas()
        self.total_time = max(self.application["End"])
        self.cpe = True
        self.should_display_outliers = should_display_outliers
        self.highlighted = []
        self.show_idless_cpu = show_idless_cpu
        self.show_abe = show_abe

    def tasks_by_resource(self, resourceId: list[str]):
        return self.application[self.application["ResourceId"].isin(resourceId)]

    def idelles_resource_time(self, resource_tasks):
        return round(
            (
                1
                - sum(
                    [
                        task["End"] - task["Start"]
                        for _, task in resource_tasks.iterrows()
                    ]
                )
                / self.total_time
            )
            * 100,
            2,
        )

    @property
    def resourcesId(self):
        return self.application["ResourceId"].unique()

    @property
    def chart(self):
        COLORS = [
            "#8dd3c7",
            "#ffffb3",
            "#bebada",
            "#fb8072",
            "#80b1d3",
            "#fdb462",
            "#b3de69",
            "#fccde5",
            "#d9d9d9",
            "#bc80bd",
        ]
        df = self.tasks_by_resource(self.resourcesId)
        df["Task"] = df["ResourceId"]
        task_names = df["Task"].unique()
        task_positions = {task: index for index, task in enumerate(task_names)}
        types_of_tasks = df["Value"].unique()
        # TODO: generate better colors
        task_colors = {
            task: COLORS[index] for (index, task) in enumerate(types_of_tasks)
        }

        # Create the figure
        fig = go.Figure()

        legend_entries = set()

        bars = []
        for task in types_of_tasks:
            task_data = df[df["Value"] == task]
            for _, row in task_data.iterrows():
                show_legend = task not in legend_entries

                if self.should_display_outliers:
                    opacity = 1 if row["Outlier"] else 0.3
                else:
                    opacity = (
                        1
                        if len(self.highlighted) == 0
                        else (1 if row["JobId"] in self.highlighted else 0.3)
                    )

                bar = go.Bar(
                    y=[task_positions[row["Task"]]],
                    x=[row["End"] - row["Start"]],
                    orientation="h",
                    name=task,
                    legendgroup=task,
                    showlegend=show_legend,
                    opacity=opacity,
                    base=row["Start"],
                    marker_color=task_colors[row["Value"]],
                    hovertext=row["Duration"],
                    customdata=[{"id": row["JobId"]}],
                    selected=dict(marker=dict(opacity=1)),
                    unselected=dict(marker=dict(opacity=1)),
                    uid=row["JobId"],
                )
                bars.append(bar)

                if show_legend:
                    legend_entries.add(task)  # Add the task to the legend tracking set
        fig.add_traces(bars)

        fig.update_layout(
            title="Task Timeline",
            xaxis_title="Time (milliseconds)",
            yaxis_title="Core",
            barmode="relative",
            yaxis=dict(
                tickvals=list(range(len(df["ResourceId"].unique()))),
                ticktext=df["ResourceId"].unique(),
            ),
        )
        fig.update_yaxes(autorange="reversed")

        fig.update_xaxes(
            tickmode="linear",  # Set tick mode to linear
            tick0=0,  # Starting point
            dtick=10000,  # Interval between ticks
            tickformat=",",  # Format to show full numbers without abbreviations
        )

        # ABE
        if self.show_abe:
            fig.add_vrect(
                x0=self.abe,
                x1=self.abe,
                label=dict(
                    text=f"ABE {self.abe}",
                    font=dict(size=16, color="white"),
                    textangle=-90,
                ),
                line=dict(color="rgba(128, 128, 128, 0.8)", width=20),
            )

        # Idle CPU
        if self.show_idless_cpu:
            for index, resourceId in enumerate(self.resourcesId):
                fig.add_annotation(
                    text=f"{self.idelles_resource_time(self.tasks_by_resource([resourceId]))}%",
                    x=1,  # x position
                    y=index,  # y position
                    font=dict(color="black"),
                    bgcolor="white",
                    bordercolor="black",
                    borderwidth=1,
                    borderpad=2,
                    align="center",
                    showarrow=False,
                    xanchor="left",
                )

        return fig

    @cached_property
    def abe(self):
        return int(
            self.application["Duration"].mean()
            * self.application["Duration"].size
            / len(self.resourcesId),
        )

    def highlight(self, bars: list[str]):
        self.highlighted = list(bars)

    def highlight_task_depedency(self, id: str):
        if self.should_display_outliers:
            return
        dag = pq.read_table("dag.parquet", columns=["JobId", "Dependent"]).to_pandas()
        kids = dag[dag["Dependent"] == id]
        self.highlighted = list([str(j) for j in kids["JobId"]]) + [id]

    def toggle_cpe(self):
        # self.cpe = not self.cpe
        dag = pq.read_table("dag.parquet", columns=["JobId", "Dependent"]).to_pandas()
        st.write(dag)
        graph = nx.DiGraph()
        # graph.add_edges_from()


@dataclass
class StarPU:
    file_name: str

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.starpu = pq.read_table(
            "starpu.parquet",
            columns=["ResourceId", "Value", "Start", "End", "Duration"],
        ).to_pandas()
        # self.total_time = max(self.application["End"])

    def tasks_by_resource(self, resourceId: list[str]):
        return self.starpu[self.starpu["ResourceId"].isin(resourceId)]

    @property
    def resourcesId(self):
        return self.starpu["ResourceId"].unique()

    def chart(self):
        COLORS = [
            "#8dd3c7",
            "#ffffb3",
            "#bebada",
            "#fb8072",
            "#80b1d3",
            "#fdb462",
            "#b3de69",
            "#fccde5",
            "#d9d9d9",
            "#bc80bd",
        ]

        df = self.tasks_by_resource(self.resourcesId)
        df["Task"] = df["ResourceId"]
        task_names = df["Task"].unique()
        task_positions = {task: index for index, task in enumerate(task_names)}
        types_of_tasks = df["Value"].unique()
        # TODO: generate better colors
        task_colors = {
            task: COLORS[index] for (index, task) in enumerate(types_of_tasks)
        }

        # Create the figure
        fig = go.Figure()

        legend_entries = set()

        for task in types_of_tasks:
            task_data = df[df["Value"] == task][df["Duration"] > 1]
            for _, row in task_data.iterrows():
                show_legend = task not in legend_entries
                fig.add_trace(
                    go.Bar(
                        y=[task_positions[row["Task"]]],
                        x=[row["End"] - row["Start"]],
                        orientation="h",
                        name=task,
                        legendgroup=task,
                        showlegend=show_legend,
                        base=row["Start"],
                        marker_color=task_colors[row["Value"]],
                    ),
                )

                if show_legend:
                    legend_entries.add(task)  # Add the task to the legend tracking set

        fig.update_layout(
            title="Task Timeline",
            xaxis_title="Time (milliseconds)",
            yaxis_title="Core",
            barmode="relative",
            yaxis=dict(
                tickvals=list(range(len(df["ResourceId"].unique()))),
                ticktext=df["ResourceId"].unique(),
            ),
        )
        fig.update_yaxes(autorange="reversed")

        fig.update_xaxes(
            tickmode="linear",  # Set tick mode to linear
            tick0=0,  # Starting point
            dtick=10000,  # Interval between ticks
            tickformat=",",  # Format to show full numbers without abbreviations
        )

        return fig
