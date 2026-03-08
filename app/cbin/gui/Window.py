from cbin.gui.Client import Client
from cbin.gui.Plotter import Plotter
from cbin.gui.Utils import chart_div, generate_contents_for_left_panel, generate_modal_close_callback, \
    generate_modal_open_callback, generate_order_button_callback, generate_rate_callback, get_row, modal, update_trades
from dash.dependencies import Input, Output, State
import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
import os

# Detailed example at https://dash-gallery.plotly.host/dash-web-trader/ and
# https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-web-trader

client = Client(os.getenv("API_URL", "http://localhost:443"))
plotter = Plotter(client)
currencies = client.get_product_list()
if not currencies:
    currencies = ["EURGBP"]

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
app.layout = html.Div(
    className="row",
    children=[
        # Interval component for live clock
        dcc.Interval(id="interval", interval=1 * 60000, n_intervals=0),
        # Interval component for rate updates
        dcc.Interval(id="i_rate", interval=1 * 2000, n_intervals=0),
        # Interval component for position updates
        dcc.Interval(id="i_positions", interval=1 * 5000, n_intervals=0),
        # Interval component for trade updates
        dcc.Interval(id="i_trades", interval=1 * 15000, n_intervals=0),
        # Interval component for order book updates
        dcc.Interval(id="i_orderbook", interval=1 * 1000, n_intervals=0),
        # Left Panel Div
        html.Div(
            className="two columns div-left-panel",
            children=[
                # Div for Left Panel App Info
                html.Div(
                    className="div-info",
                    children=[
                        html.H6(className="title-header", children="FOREX TRADER"),
                    ],
                ),
                # Rate Currency Div
                html.Div(
                    className="div-currency-toggles",
                    children=[
                        html.P(
                            id="live_clock",
                            className="two-col",
                            children=datetime.datetime.now().strftime("%H:%M"),
                        ),
                        html.P(className="two-col", children="Rate"),
                        html.Div(
                            id="pairs",
                            className="div-rate",
                            children=[
                                get_row([pair, plotter.get_y()[pair][-1]])
                                for pair in currencies
                            ],
                        ),
                    ],
                ),
                # Div for trade updates
                html.Div(
                    className="div-trades",
                    children=[html.Div(id="trades", children=update_trades(client))],
                ),
            ],
        ),
        # Right Panel Div
        html.Div(
            className="ten columns div-right-panel",
            children=[
                # Chart Div
                html.Div(
                    id="chart",
                    className="row",
                    children=[chart_div(pair) for pair in currencies],
                ),
                html.Div(
                    id="orderbook_panel",
                    className="row",
                    children=[html.Div(id=pair + "orderbook", className="orderbook-panel") for pair in currencies],
                ),
                # Panel for positions
                html.Div(
                    id="bottom_panel",
                    className="row div-bottom-panel",
                    children=[html.Div(id="positions_table", className="row table-positions")],
                ),
            ],
        ),
        html.Div([modal(pair) for pair in currencies]),
        # Hidden div to serve as a sink for callback without output
        html.Div(children=[html.Div(id="hidden-div", style={"display": "none"})]),
    ],
)

for pair in currencies:
    # Callback for Buy/Sell and Chart Buttons for Left Panel
    app.callback(
        [Output(pair + "contents", "className"), Output(pair + "summary", "className")],
        [Input(pair + "summary", "n_clicks")],
    )(generate_contents_for_left_panel())
    # Show Buy/Sell modal
    app.callback(Output(pair + "modal", "style"), [Input(pair + "Buy", "n_clicks")])(
        generate_modal_open_callback()
    )
    # Hide Buy/Sell modal
    app.callback(
        Output(pair + "Buy", "n_clicks"),
        [
            Input(pair + "closeModal", "n_clicks"),
            Input(pair + "button_order", "n_clicks"),
        ],
    )(generate_modal_close_callback())
    # Place a trade
    app.callback(
        Output("hidden-div", "children"),
        [Input(pair + "button_order", "n_clicks")],
        [
            State(pair + "volume", "value"),
            State(pair + "trade_type", "value"),
            State(pair + "traderId", "value"),
        ],
    )(generate_order_button_callback(pair, client))
    app.callback([Output(pair + 'chart', 'figure'),
                  Output(pair + "row", "children")],
                 [Input('i_rate', 'n_intervals'),
                  Input(pair + "dropdown_period", "value")],
                 [State(pair + "rate", "children")])(generate_rate_callback(plotter, pair))
    app.callback(
        Output(pair + "orderbook", "children"),
        [Input("i_orderbook", "n_intervals")],
    )(lambda n, pair=pair: update_orderbook_panel(client, pair))

# Callback to update live clock
@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(n):
    return datetime.datetime.now().strftime("%H:%M")


# Callback to update trades
@app.callback(Output("trades", "children"), [Input("i_trades", "n_intervals")])
def update_news_div(n):
    return update_trades(client)


# Callback to update Positions Table
@app.callback(Output("positions_table", "children"), [Input("i_positions", "n_intervals")])
def update_positions_table(n):
    capitals = client.get_capitals()
    if not capitals:
        return html.Div("No trader data available yet.")
    normalized_capitals = sorted(client.get_normalized_capital().items(), key=lambda kv: kv[1], reverse=True)
    headers = ["Rank", "Trader"]
    for currency in capitals[next(iter(capitals))]:
        headers.append(currency)
    headers.append('Meets Criteria')
    headers.append('PnL')

    rows = []
    rank = 1
    for trader, total_position in normalized_capitals:
        tr_childs = [html.Td(rank), html.Td(trader)]
        for currency in headers[2:-2]:
            tr_childs.append(html.Td(round(float(capitals[trader][currency]), 2)))
        normalized_cap = float(total_position)
        pnl = round(normalized_cap - 1000000, 2)
        tr_childs.append(html.Td(str((normalized_cap - float(capitals[trader]['GBP'])) >= 0.3 * normalized_cap)))
        tr_childs.append(html.Td(pnl))
        # Color row based on profitability of positions
        if pnl >= 0:
            rows.append(html.Tr(className="profit", children=tr_childs))
        else:
            rows.append(html.Tr(className="no-profit", children=tr_childs))
        rank += 1
    return html.Table(children=[html.Tr([html.Th(title) for title in headers])] + rows)


def update_orderbook_panel(client, pair):
    data = client.get_order_book(pair, levels=10)
    if not data or "bids" not in data or "asks" not in data:
        return html.Div(className="orderbook-empty", children="Order book unavailable")

    bids = data.get("bids", [])
    asks = data.get("asks", [])
    best_bid = data.get("best_bid")
    best_ask = data.get("best_ask")
    spread = (best_ask - best_bid) if (best_bid is not None and best_ask is not None) else None

    max_levels = min(max(len(bids), len(asks)), 10)
    rows = []
    for i in range(max_levels):
        bid = bids[i] if i < len(bids) else ["", "", ""]
        ask = asks[i] if i < len(asks) else ["", "", ""]
        rows.append(
            html.Tr(
                children=[
                    html.Td("" if bid[1] == "" else round(float(bid[1]), 5), className="bid-price"),
                    html.Td("" if bid[2] == "" else int(bid[2])),
                    html.Td("" if ask[2] == "" else int(ask[2])),
                    html.Td("" if ask[1] == "" else round(float(ask[1]), 5), className="ask-price"),
                ]
            )
        )

    summary = "Best Bid: {} | Best Ask: {} | Spread: {}".format(
        "-" if best_bid is None else round(float(best_bid), 5),
        "-" if best_ask is None else round(float(best_ask), 5),
        "-" if spread is None else round(float(spread), 5),
    )

    return html.Div(
        children=[
            html.P("{} Order Book".format(pair), className="orderbook-title"),
            html.P(summary, className="orderbook-summary"),
            html.Table(
                className="table-orderbook",
                children=[
                    html.Tr(
                        children=[
                            html.Th("Bid Px"),
                            html.Th("Bid Qty"),
                            html.Th("Ask Qty"),
                            html.Th("Ask Px"),
                        ]
                    )
                ] + rows,
            ),
        ]
    )
