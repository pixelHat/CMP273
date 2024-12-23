# TODO

- [x] Show tasks depedency
- [x] Add charts for the submmited and ready
- [x] Add button to show outlier
- [x] Adds idleless worker
- [ ] Allows user to select the dataset
- [ ] Allows user to select more than one dataset and display all of them side by side.

### Extra

- [ ] Allows user to add annotations
- [ ] Extract gantt chart to a class
- [ ] Add slider to aggregate equal tasks that have distance less than a value
- [ ] Add the critical path estimation

# StreamLit



## fragment

```py
@st.fragment
def handle_application_chart_events():
    click_data = st.session_state.get("st", None)
    st.write(should_display_outliers)
    if (
        click_data
        and len(click_data["selection"]["points"]) > 0
        and not should_display_outliers
    ):
        st.write("entrou", should_display_outliers)
        id = click_data["selection"]["points"][0]["customdata"]["id"]
        gantt.highlight_task_depedency(id)
    else:
        gantt.highlight([])


handle_application_chart_events()
```

## Stateless

By default StreamLit will reload the page. So, we have a stateless application. Thus don't need to mutate variables.

```py
# Stateless
should_display_outliers = st.toggle("Outliers")
gantt = Application(
    "application.parquet", should_display_outliers=should_display_outliers
)
```

```py
# Stateful
should_display_outliers = st.toggle("Outliers")
gantt = Application("application.parquet")
if should_display_outliers:
    gantt.show_outliers()
else:
    gantt.hide_outliers()
```

# Plotly

https://plotly.com/python/reference

## graph_objects

The Plotly graph_objects module allows us to create custom charts simliar to ggplot2. However, we can use OOP.

We are goint to create graph objects and add them to a trace. A trace acts like a div.

```py
bars = []
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
fig.add_traces(bars)
```

Sometimes we need to configure a trace that was created via `plotly.express`.

```py
# we don't have the line_shape option.
fig = px.scatter(
    df_skipped,
    x="Start",
    y="Value",
    color="Value",
    title="Abc",
)
fig.update_traces(mode="lines", line_shape="hv")
```

## User annotation

https://plotly.com/python/shapes/#style-of-userdrawn-shapes

Plotly allows users to create their own annotations.

```py
fig.show(
    config={
        'modeBarButtonsToAdd': [
            'drawline',
            'drawopenpath',
            'drawclosedpath',
            'drawcircle',
            'drawrect',
            'eraseshape'
        ]})
```
