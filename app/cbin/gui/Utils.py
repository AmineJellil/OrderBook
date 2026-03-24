from datetime import datetime
from plotly.subplots import make_subplots
import dash_core_components as dcc
import dash_html_components as html

n_interval = 0


# Creates HTML Rate (Buy/Sell buttons)
def get_row(data):
    return html.Div(
        children=[
            # Summary
            html.Div(
                id=data[0] + "summary",
                className="row summary",
                n_clicks=0,
                children=[
                    html.Div(
                        id=data[0] + "row",
                        className="row",
                        children=[
                            html.P(
                                data[0],  # currency pair name
                                id=data[0],
                                className="two-col",
                            ),
                            html.P(
                                round(data[1], 5),  # Rate value
                                id=data[0] + "rate",
                                className="two-col",
                            ),
                        ],
                    )
                ],
            ),
            # Contents
            html.Div(
                id=data[0] + "contents",
                className="row details",
                children=[
                    # Button for buy/sell modal
                    html.Div(
                        className="button-buy-sell",
                        children=[
                            html.Button(
                                id=data[0] + "Buy",
                                children="Buy/Sell",
                                n_clicks=0,
                            )
                        ],
                    ),
                ],
            ),
        ]
    )


# Get HTML chart div
def chart_div(pair):
    return html.Div(
        id=pair + "graph_div",
        className="chart-style ten columns",
        children=[
            # Chart Top Bar
            html.Div(
                className="row chart-top-bar",
                children=[
                    html.Span(
                        id=pair + "label",
                        className="inline-block chart-title",
                        children=f"{pair}",
                        n_clicks=0,
                    ),
                    # Dropdown float right
                    html.Div(
                        className="graph-top-right inline-block",
                        children=[
                            html.Div(
                                className="inline-block",
                                children=[
                                    dcc.Dropdown(
                                        className="dropdown-period",
                                        id=pair + "dropdown_period",
                                        options=[
                                            {"label": "5 min", "value": "5"},
                                            {"label": "10 min", "value": "10"},
                                            {"label": "15 min", "value": "15"},
                                            {"label": "30 min", "value": "30"},
                                            {"label": "60 min", "value": "60"},
                                        ],
                                        value="5",
                                        clearable=False,
                                    )
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Graph div
            html.Div(
                dcc.Graph(
                    id=pair + "chart",
                    className="chart-graph",
                    config={"displayModeBar": False, "scrollZoom": True},
                )
            ),
        ],
    )


# Returns modal Buy/Sell
def modal(pair):
    return html.Div(
        id=pair + "modal",
        className="modal",
        style={"display": "none"},
        children=[
            html.Div(
                className="modal-content",
                children=[
                    html.Span(
                        id=pair + "closeModal", className="modal-close", children="×"
                    ),
                    html.P(id="modal" + pair, children=pair),
                    # row div with two div
                    html.Div(
                        className="row",
                        children=[
                            # order values div
                            html.Div(
                                className="six columns modal-user-control",
                                children=[
                                    html.Div(
                                        children=[
                                            html.P("Volume"),
                                            dcc.Input(
                                                id=pair + "volume",
                                                className="modal-input",
                                                type="number",
                                                value=10000,
                                                min=0,
                                                step=10000,
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.P("Side"),
                                            dcc.RadioItems(
                                                id=pair + "trade_type",
                                                options=[
                                                    {"label": "Buy", "value": "buy"},
                                                    {"label": "Sell", "value": "sell"},
                                                ],
                                                value="buy",
                                                labelStyle={"display": "inline-block"},
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.P("Order Mode"),
                                            dcc.RadioItems(
                                                id=pair + "order_mode",
                                                options=[
                                                    {"label": "Market", "value": "market"},
                                                    {"label": "Limit", "value": "limit"},
                                                ],
                                                value="market",
                                                labelStyle={"display": "inline-block"},
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.P("Limit Price"),
                                            dcc.Input(
                                                id=pair + "limit_price",
                                                className="modal-input",
                                                type="number",
                                                min=0,
                                                step=0.00001,
                                                placeholder="e.g. 0.87850",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        children=[
                                            html.P("TraderId"),
                                            dcc.Input(
                                                id=pair + "traderId",
                                                className="modal-input",
                                                type="text",
                                            ),
                                        ]
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="modal-order-btn",
                        children=html.Button(
                            "Order", id=pair + "button_order", n_clicks=0
                        ),
                    ),
                ],
            )
        ],
    )


# Generate Buy/Sell Button for Left Panel
def generate_contents_for_left_panel():
    def show_contents(n_clicks):
        if n_clicks is None:
            return "display-none", "row summary"
        elif n_clicks % 2 == 0:
            return "display-none", "row summary"
        return "row details", "row summary-open"

    return show_contents


# Open Modal
def generate_modal_open_callback():
    def open_modal(n):
        if n > 0:
            return {"display": "block"}
        else:
            return {"display": "none"}

    return open_modal


# Function to close modal
def generate_modal_close_callback():
    def close_modal(n, n2):
        return 0

    return close_modal


# Function to trade a position
def generate_order_button_callback(pair, client):
    def order_callback(n, volume, side, trader_id, order_mode, limit_price):
        if not n:
            return ""
        if trader_id is None or str(trader_id).strip() == "":
            return ""
        if volume is None:
            return ""

        if order_mode == "limit":
            if limit_price is None or float(limit_price) <= 0:
                return ""
            client.trade(pair, str(trader_id).strip(), str(volume), side, float(limit_price))
            return ""

        client.trade(pair, str(trader_id).strip(), str(volume), side)
        return ""
    return order_callback


def redraw_chart(plotter, pair, time_horizon):
    x = plotter.get_x()
    y = plotter.get_y()

    # Create the graph with subplots
    fig = make_subplots(rows=1, cols=1, vertical_spacing=0.2)
    fig["layout"][
        "uirevision"
    ] = "The User is always right"  # Ensures zoom on graph is the same on update
    fig["layout"]["margin"] = {"t": 50, "l": 50, "b": 50, "r": 25}
    fig["layout"]["autosize"] = True
    fig["layout"]["height"] = 400
    fig["layout"]["xaxis"]["rangeslider"]["visible"] = False
    fig["layout"]["xaxis"]["tickformat"] = "%H:%M:%S"
    fig["layout"]["yaxis"]["showgrid"] = True
    fig["layout"]["yaxis"]["gridcolor"] = "#3E3F40"
    fig["layout"]["yaxis"]["gridwidth"] = 1
    fig["layout"].update(paper_bgcolor="#21252C", plot_bgcolor="#21252C")

    nb_datapoints = int(time_horizon) * 30
    fig.append_trace({
        'x': x[pair][-nb_datapoints:],
        'y': y[pair][-nb_datapoints:],
        'name': pair,
        'mode': 'lines',
        'type': 'scatter'}, 1, 1)

    return fig


def generate_rate_callback(plotter, pair):
    def update_rate_live(n, time_horizon, previous_rate):

        global n_interval
        if not n == n_interval:
            plotter.update_plot()
            n_interval = n
        fig = redraw_chart(plotter, pair, time_horizon)

        new_rate = plotter.get_y()[pair][-1]
        row = [
            html.P(pair, id=pair, className="two-col"),
            html.P(
                round(new_rate, 5),
                id=pair + "rate",
                className="two-col",
                style={"color": get_color(new_rate, previous_rate)},
            ),
        ]

        return fig, row
    return update_rate_live


# Color of rates
def get_color(a, b):
    if a == b:
        return "white"
    elif a > b:
        return "#45df7e"
    else:
        return "#da5657"


# API Call to update trades
def update_trades(client):
    data = client.get_trade_history()
    max_rows = 10
    return html.Div(
        children=[
            html.P(className="p-trades", children="Last Trades"),
            html.P(
                className="p-trades float-right",
                children="Last update: " + datetime.now().strftime("%H:%M:%S"),
            ),
            html.Table(
                className="table-trades",
                children=[
                    html.Tr(
                        children=[
                            html.Td(
                                children=[
                                    html.A(
                                        className="td-trade",
                                        children="{} - {} {} {} {} @ {}".format(
                                            datetime.utcfromtimestamp(int(data[i]["time"])).strftime("%H:%M:%S"),
                                            data[i]["user_name"],
                                            data[i]["side"],
                                            data[i]["quantity"],
                                            data[i]["pair"],
                                            round(float(data[i]["rate"]), 5)),
                                        target="_blank",
                                    )
                                ]
                            )
                        ]
                    )
                    for i in range(len(data) - 1, len(data) - min(len(data), max_rows) - 1, -1)
                ],
            ),
        ]
    )
