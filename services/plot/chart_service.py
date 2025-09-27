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

    # 카테고리별 총합을 저장할 딕셔너리
    category_totals = {}
    individual_stock_totals = []  # 개별 종목들의 금액을 저장할 리스트

    # 각 포트폴리오에서 금액을 계산
    for portfolio, currency in [(usd_portfolio, "USD"), (krw_portfolio, "KRW")]:
        for k, v in portfolio.holdings.items():
            if v["quantity"] != 0:
                total_value = float(v["quantity"]) * float(v["avg_cost"])
                total_value_in_usd = (
                    total_value if currency == "USD" else total_value / fx_rate
                )
                if currency == "USD":
                    individual_stock_totals.append(
                        (k, total_value_in_usd)
                    )  # 개별 종목 금액 추가
                # 카테고리별 합산
                category = category_map[k]
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += total_value_in_usd  # 카테고리 총합 추가

    # 현금도 카테고리에 포함
    usd_cash_in_usd = usd_portfolio.cash
    krw_cash_in_usd = krw_portfolio.cash / fx_rate
    category_totals["Stable Assets"] = usd_cash_in_usd + krw_cash_in_usd

    category_labels = []
    category_values = []
    for key in [
        "Individual Stocks",
        "S&P 500",
        "Nasdaq",
        "Big Tech",
        "Dividend Stocks",
        "Stable Assets",
    ]:
        category_labels.append(key)
        category_values.append(category_totals[key])

    # category_values = list(category_totals.values())
    # category_labels = list()
    # print(category_labels)

    # # 바깥쪽 Pie (개별 종목 금액)
    # individual_stock_values = [v for _, v in individual_stock_totals]
    # individual_stock_labels = [ticker_map[k] for k, _ in individual_stock_totals]

    # Pie 차트 데이터
    data = [
        go.Pie(
            values=category_values,
            labels=category_labels,
            domain=inner_domain,
            hole=inner_hole,
            marker={"colors": ["#CB4335", "#2E86C1", "#F1948A", "#5DADE2"]},
            **common_pie_properties,
        ),
        # go.Pie(
        #     values=individual_stock_values,
        #     labels=individual_stock_labels,
        #     domain=outer_domain,
        #     hole=outer_hole,
        #     marker={"colors": ["#EC7063", "#F1948A", "#5DADE2", "#85C1E9"]},
        #     **common_pie_properties,
        # ),
    ]

    # 차트 레이아웃 설정
    fig = go.Figure(data=data)
    fig.update_layout(
        title="Portfolio Breakdown",
        height=600,
        width=600,
        shapes=[
            {
                "type": "rect",
                "xref": "paper",
                "yref": "paper",
                "x0": 0,
                "y0": 0,
                "x1": 1,
                "y1": 1,
                "line": {"color": "black", "width": 2},
            }
        ],
        margin=dict(t=0, b=0, l=0, r=0),
    )

    return fig


# fig = pie_chart("", "")
# fig.show()
