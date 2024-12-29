# TODO

- [x] Show tasks depedency
- [x] Add charts for the submmited and ready
- [x] Add button to show outlier
- [x] Adds idleless worker
- [x] Allows user to select the dataset
- [x] Allows user to select more than one dataset and display all of them side by side.

### Extra

- [x] Allows user to add annotations
- [x] Extract gantt chart to a class
- [ ] Add slider to aggregate equal tasks that have distance less than a value
- [ ] Add the critical path estimation

# Power Point

I can talk about the 1-d indexing and its effect in the depedency between the tasks. We could use a hash table to avoid it. I can use the plotly annotation here.

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

# Further work

## Optmizations

### MinMaxLTTB: Leveraging MinMax-Preselection to Scale LTTB

https://arxiv.org/abs/2305.00332
https://github.com/predict-idlab/MinMaxLTTB

Visualization plays an important role in analyzing and exploring time series data. To facilitate efficient visualization of large datasets, downsampling has emerged as a well-established approach. This work concentrates on LTTB (Largest-Triangle-Three-Buckets), a widely adopted downsampling algorithm for time series data point selection. Specifically, we propose MinMaxLTTB, a two-step algorithm that marks a significant enhancement in the scalability of LTTB. MinMaxLTTB entails the following two steps: (i) the MinMax algorithm preselects a certain ratio of minimum and maximum data points, followed by (ii) applying the LTTB algorithm on only these preselected data points, effectively reducing LTTB's time complexity. The low computational cost of the MinMax algorithm, along with its parallelization capabilities, facilitates efficient preselection of data points. Additionally, the competitive performance of MinMax in terms of visual representativeness also makes it an effective reduction method. Experiments show that MinMaxLTTB outperforms LTTB by more than an order of magnitude in terms of computation time. Furthermore, preselecting a small multiple of the desired output size already provides similar visual representativeness compared to LTTB. In summary, MinMaxLTTB leverages the computational efficiency of MinMax to scale LTTB, without compromising on LTTB's favored visualization properties. The accompanying code and experiments of this paper can be found at this https URL.

The perfect case would be to modify the algorithm to work with the critical path.

## Lazy Loading

The tool should start by rendering the panels that users can see.

## Replicate zoom in/out

Some panels like Application and StarPU are showing the same thing. Thus, it would be good to sync the zoom between them.
