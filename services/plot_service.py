import plotly.graph_objects as go
from models.account import AccountCurrencyType
from services.portfolio_service import PortfolioTimeSeries


# ===============================
# 공통 유틸
# ===============================
def preprocess_data(account_currency_type, data: PortfolioTimeSeries):
    def to_manwon(arr):
        return [x / 10000 for x in arr]

    convert = (
        to_manwon if account_currency_type == AccountCurrencyType.KRW else lambda x: x
    )

    return {
        "timestamps": data.timestamps,
        "cash": convert(data.cash),
        "invest": convert(data.invest),
        "valuation": convert(data.valuation),
        "capital_gain": convert(data.capital_gain),
        "interest_income": convert(data.interest_income),
        "dividend_income": convert(data.dividend_income),
        "total_income": convert(data.total_income),
        "returns_pct": getattr(data, "returns_pct", None),
    }


def default_layout(title, xaxis_title, yaxis_title, yaxis_tickformat):
    return dict(
        title=title,
        title_font=dict(size=24, family="Arial, sans-serif", color="rgb(33,33,33)"),
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        font=dict(family="Arial, sans-serif", size=14, color="rgb(102,102,102)"),
        template="plotly",
        showlegend=True,
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=True,
            showticklabels=True,
            tickangle=45,
            gridcolor="rgb(224,224,224)",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgb(224,224,224)",
            zeroline=True,
            tickformat=yaxis_tickformat,
        ),
        margin=dict(l=50, r=50, t=80, b=50),
    )


# ===============================
# 개별 그래프
# ===============================
def total_valuation_and_invest_graph(account_currency_type, data: PortfolioTimeSeries):
    d = preprocess_data(account_currency_type, data)

    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title, yaxis_tickformat = "금액 ($)", "~s"
    else:
        yaxis_title, yaxis_tickformat = "금액 (만원)", "d"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["invest"],
            mode="lines",
            name="투자 금액",
            stackgroup="A",
            line=dict(color="gray", width=2, dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["valuation"],
            mode="lines",
            name="평가 금액",
            line=dict(color="green", width=3),
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        **default_layout("총 평가 금액", "날짜", yaxis_title, yaxis_tickformat)
    )
    fig.update_yaxes(range=[0, max(d["valuation"]) * 1.1])
    return fig


def return_pct_graph(account_currency_type, data: PortfolioTimeSeries):
    d = preprocess_data(account_currency_type, data)

    yaxis_title, yaxis_tickformat = "수익률 (%)", ""

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["returns_pct"],
            mode="lines",
            name="수익률 (%)",
            line=dict(color="orange", width=2),
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        **default_layout("수익률 변화 (%)", "날짜", yaxis_title, yaxis_tickformat)
    )
    fig.add_hline(
        y=0,
        line=dict(color="black", width=1, dash="dash"),
        annotation_text="0%",
        annotation_position="bottom right",
    )
    fig.update_yaxes(range=[min(d["returns_pct"]) * 1.2, max(d["returns_pct"]) * 1.2])
    return fig


def realized_gain_graph(account_currency_type, data: PortfolioTimeSeries):
    d = preprocess_data(account_currency_type, data)

    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title, yaxis_tickformat = "금액 ($)", "~s"
    else:
        yaxis_title, yaxis_tickformat = "금액 (만원)", "d"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["capital_gain"],
            mode="lines",
            name="청산이익",
            line=dict(color="red"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["interest_income"],
            mode="lines",
            name="이자 소득",
            line=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["dividend_income"],
            mode="lines",
            name="배당 소득",
            line=dict(color="green"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["total_income"],
            mode="lines",
            name="총 확정 소득",
            stackgroup="A",
            line=dict(color="black", width=1, dash="dot"),
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        **default_layout("총 확정 소득 변화", "날짜", yaxis_title, yaxis_tickformat)
    )
    return fig


def total_capital_and_cash_graph(account_currency_type, data: PortfolioTimeSeries):
    d = preprocess_data(account_currency_type, data)

    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title, yaxis_tickformat = "금액 ($)", "~s"
    else:
        yaxis_title, yaxis_tickformat = "금액 (만원)", "d"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["cash"],
            mode="lines",
            name="현금",
            stackgroup="A",
            line=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["valuation"],
            mode="lines",
            name="평가 금액",
            stackgroup="A",
            line=dict(color="green"),
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        **default_layout("총 자산", "날짜", yaxis_title, yaxis_tickformat)
    )
    total_assets = [float(c) + float(v) for c, v in zip(d["cash"], d["valuation"])]
    fig.update_yaxes(range=[0, max(total_assets) * 1.1])
    return fig
