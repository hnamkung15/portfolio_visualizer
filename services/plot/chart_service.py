import plotly.graph_objs as go

from models.tickers import Ticker
from services.portfolio_service import Portfolio

offset = 0.17
inner_domain = {"x": [offset, 1 - offset], "y": [offset, 1 - offset]}
inner_hole = 0.5
outer_domain = {"x": [0, 1], "y": [0, 1]}
outer_hole = 0.7
common_pie_properties = {
    "direction": "clockwise",
    "sort": False,
    "textinfo": "percent+label",
    "textposition": "inside",
    "textfont": dict(size=15, color="black"),
    "showlegend": False,
}


def total_portfolio_pie_chart(
    db, usd_portfolio: Portfolio, krw_portfolio: Portfolio, fx_rate
):
    symbols = list(usd_portfolio.holdings.keys()) + list(krw_portfolio.holdings.keys())
    ticker_map = {
        t.symbol: t.name
        for t in db.query(Ticker).filter(Ticker.symbol.in_(symbols)).all()
    }
    category_map = {
        t.symbol: t.category
        for t in db.query(Ticker).filter(Ticker.symbol.in_(symbols)).all()
    }

    for k, v in usd_portfolio.holdings.items():
        if v["quantity"] != 0:
            print(
                k,
                "/",
                ticker_map[k],
                "/",
                category_map[k],
                float(v["quantity"]) * float(v["avg_cost"]),
            )
    print(usd_portfolio.cash)
    for k, v in krw_portfolio.holdings.items():
        if v["quantity"] != 0:
            print(
                k,
                "/",
                ticker_map[k],
                "/",
                category_map[k],
                float(v["quantity"]) * float(v["avg_cost"]),
            )
    print(krw_portfolio.cash)
    data = [
        go.Pie(
            values=[20, 40],
            labels=["Reds", "Blues"],
            domain=inner_domain,
            hole=inner_hole,
            marker={"colors": ["#CB4335", "#2E86C1"]},
            **common_pie_properties
        ),
        go.Pie(
            values=[5, 15, 30, 10],
            labels=["Medium Red", "Light Red", "Medium Blue", "Light Blue"],
            domain=outer_domain,
            hole=outer_hole,
            marker={"colors": ["#EC7063", "#F1948A", "#5DADE2", "#85C1E9"]},
            **common_pie_properties
        ),
    ]

    # Create figure and show it
    fig = go.Figure(data=data)
    fig.update_layout(
        title="ABC",
        height=600,
        width=600,
        shapes=[
            # Add a rectangle border around the entire figure
            {
                "type": "rect",
                "xref": "paper",  # 'paper'는 전체 차트를 기준으로
                "yref": "paper",
                "x0": 0,
                "y0": 0,
                "x1": 1,
                "y1": 1,
                "line": {"color": "black", "width": 2},  # 테두리 색상  # 테두리 두께
            }
        ],
    )  # 원하는 너비  # 원하는 높이
    return fig
    # fig.show()


# fig = pie_chart("", "")
# fig.show()
