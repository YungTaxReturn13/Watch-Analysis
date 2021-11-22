import dash
from dash.dependencies import Input, Output
from dash import dash_table
from dash import dcc
from dash import html
import pandas as pd

# Import data into pandas
df = pd.read_csv("data.csv")
df["Condition"] = df["Condition Category"]
df = df.drop(["Condition Category", "Missed Prices", "Index", "SKU"], axis=1)

df = df[
    [
        "Brand",
        "Model",
        "Reference",
        "Year",
        "Condition",
        "Papers",
        "Box",
        "Movement",
        "Dimensions",
        "Gender",
        "Case",
        "Bracelet",
        "Crystal",
        "Dial Color",
        "Price",
        "Features",
        "Link",
    ]
]

app = dash.Dash(__name__)

money = dash_table.FormatTemplate.money(0)
# App Layout
app.layout = html.Div(
    [
        # Title
        html.H1("Watch Data", style={"text-align": "center"}),
        # Dropdowns
        html.Div(
            className="row",
            children=[
                # First dropdown
                html.Div(
                    children=[
                        html.Label(["Brand"], style={"text-align": "center"},),
                        dcc.Dropdown(
                            id="brand_dropdown",
                            options=[
                                {"label": i, "value": i}
                                for i in df["Brand"].sort_values().unique()
                            ],
                            value=None,
                            clearable=True,
                            searchable=True,
                        ),
                    ],
                    style=dict(width="50%"),
                ),
                # Second dropdown
                html.Div(
                    children=[
                        html.Label(["Model"], style={"text-align": "center"},),
                        dcc.Dropdown(
                            id="model_dropdown",
                            value=None,  # [![enter image description here][1]][1]
                            clearable=True,
                            searchable=True,
                        ),
                    ],
                    style=dict(width="50%"),
                ),
                html.Div(
                    children=[
                        html.Label(["Price"], style={"text-align": "center"},),
                        dcc.RangeSlider(
                            id="range_slider",
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                    ],
                    style=dict(width="50%"),
                ),
            ],
            style=dict(display="flex"),
        ),
        html.Br(),
        html.Div(
            [
                dash_table.DataTable(
                    id="table",
                    filter_action="native",
                    sort_action="native",
                    style_cell={"textAlign": "left", "minWidth": 110, "width": 110},
                    style_table={"minWidth": "100%"},
                    style_cell_conditional=[
                        {"if": {"column_id": "Features"}, "textAlign": "right",},
                        {"if": {"column_id": "Link"}, "textAlign": "right"},
                    ],
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "rgb(220, 220, 220)",
                        }
                    ],
                    style_header={
                        "backgroundColor": "rgb(210, 210, 210)",
                        "color": "black",
                        "fontWeight": "bold",
                    },
                )
            ]
        ),
    ]
)

# Connecting Dash Components
@app.callback(
    [Output(component_id="model_dropdown", component_property="options")],
    [Input(component_id="brand_dropdown", component_property="value")],
)
def update_model(brand_selected):

    dff = df[df["Brand"] == brand_selected]
    return [[{"label": i, "value": i} for i in dff["Model"].sort_values().unique()]]


@app.callback(
    [
        Output(component_id="range_slider", component_property="min"),
        Output(component_id="range_slider", component_property="max"),
        Output(component_id="range_slider", component_property="value"),
    ],
    [
        Input(component_id="brand_dropdown", component_property="value"),
        Input(component_id="model_dropdown", component_property="value"),
    ],
)
def update_slider(brand_selected, model_selected):

    dff = df[(df["Brand"] == brand_selected) & (df["Model"] == model_selected)]
    return (
        dff["Price"].min(),
        dff["Price"].max(),
        [dff["Price"].min(), dff["Price"].max()],
    )


@app.callback(
    [
        Output(component_id="table", component_property="columns"),
        Output(component_id="table", component_property="data"),
    ],
    [
        Input(component_id="brand_dropdown", component_property="value"),
        Input(component_id="model_dropdown", component_property="value"),
        Input(component_id="range_slider", component_property="value"),
    ],
)
def update_table(brand_selected, model_selected, range):
    if brand_selected is None and model_selected is None:
        dff = df
    elif model_selected is None:
        dff = df[df["Brand"] == brand_selected]
    else:
        dff = df[
            (df["Brand"] == brand_selected)
            & (df["Model"] == model_selected)
            & (df["Price"] >= range[0])
            & (df["Price"] <= range[1])
        ]
    return (
        [
            {"name": i, "id": i, "hideable": True, "type": "numeric", "format": money}
            if i == "Price"
            else {"name": i, "id": i, "hideable": True}
            for i in dff.columns
        ],
        dff.to_dict("records"),
    )


if __name__ == "__main__":
    app.run_server(debug=True)
