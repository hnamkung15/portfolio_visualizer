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
# 색상 팔레트
# ===============================
COLORS = {
    "blue": "#1f77b4",
    "orange": "#ff7f0e",
    "green": "#2ca02c",
    "red": "#d62728",
    "purple": "#9467bd",
    "brown": "#8c564b",
    "gray": "#7f7f7f",
    "pastel_blue": "#4e79a7",
    "pastel_orange": "#f28e2b",
    "pastel_green": "#59a14f",
    "pastel_red": "#e15759",
    "pastel_purple": "#af7aa1",
    "pastel_yellow": "#edc948",
    "pastel_gray": "#bab0ab",
    "deep_blue": "#0052cc",
    "bright_orange": "#ff6f00",
    "lime_green": "#00c853",
    "crimson": "#c62828",
    "violet": "#8e24aa",
    "cyan": "#00acc1",
    "gold": "#fdd835",
}


# ===============================
# 개별 그래프
# ===============================
def return_graph(account_currency_type, data: PortfolioTimeSeries):
    d = preprocess_data(account_currency_type, data)

    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title, yaxis_tickformat = "금액 ($)", "~s"
    else:
        yaxis_title, yaxis_tickformat = "금액 (만원)", "d"

    profit = [v - i for v, i in zip(d["valuation"], d["invest"])]
    total_profit = [
        v - i + float(ti)
        for v, i, ti in zip(d["valuation"], d["invest"], d["total_income"])
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=(profit),
            mode="lines",
            name="평가 수익",
            stackgroup="A",
            line=dict(color=COLORS["pastel_green"], width=3),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=(d["total_income"]),
            mode="lines",
            name="확정 소득",
            stackgroup="A",
            line=dict(color=COLORS["pastel_orange"], width=3),
        )
    )

    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        **default_layout(
            "총 수익 = 평가 수익 + 확정 소득 (청산 이익 + 이자 + 배당금)",
            "날짜",
            yaxis_title,
            yaxis_tickformat,
        )
    )
    fig.add_hline(
        y=0,
        line=dict(color="black", width=2, dash="dash"),
        annotation_text="0%",
        annotation_position="bottom right",
    )
    fig.update_yaxes(range=[min(profit) * 1.2, max(total_profit) * 1.4])
    return fig


def return_pct_graph(account_currency_type, data: PortfolioTimeSeries):
    d = preprocess_data(account_currency_type, data)

    yaxis_title, yaxis_tickformat = "수익률 (%)", ""

    profit_pct = [
        ((v - i + float(ti)) / i * 100) if i != 0 else 0
        for v, i, ti in zip(d["valuation"], d["invest"], d["total_income"])
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=profit_pct,
            mode="lines",
            name="수익률 (%)",
            line=dict(color=COLORS["pastel_yellow"], width=3),
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        **default_layout(
            "수익률 (%) = 총 수익 / 투자금", "날짜", yaxis_title, yaxis_tickformat
        )
    )
    fig.add_hline(
        y=0,
        line=dict(color="black", width=2, dash="dash"),
        annotation_text="0%",
        annotation_position="bottom right",
    )
    fig.update_yaxes(range=[min(profit_pct) * 1.2, max(profit_pct) * 1.4])
    return fig


def total_valuation_and_invest_graph(account_currency_type, data: PortfolioTimeSeries):
    d = preprocess_data(account_currency_type, data)

    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title, yaxis_tickformat = "금액 ($)", "~s"
    else:
        yaxis_title, yaxis_tickformat = "금액 (만원)", "d"

    fig = go.Figure()
    # total_vaulation = [
    #     v + float(ti) for v, ti in zip(d["valuation"], d["total_income"])
    # ]

    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["invest"],
            mode="lines",
            name="투자 금액",
            stackgroup="A",
            line=dict(color=COLORS["gray"], width=2, dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["valuation"],
            mode="lines",
            name="평가금액",
            line=dict(color=COLORS["pastel_green"], width=3),
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        **default_layout(
            "투자 금액과 평가금액",
            "날짜",
            yaxis_title,
            yaxis_tickformat,
        )
    )
    fig.update_yaxes(range=[0, max(d["valuation"]) * 1.1])
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
            line=dict(color=COLORS["pastel_green"], width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["interest_income"],
            mode="lines",
            name="이자 소득",
            line=dict(color=COLORS["cyan"], width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["dividend_income"],
            mode="lines",
            name="배당 소득",
            line=dict(color=COLORS["purple"], width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["total_income"],
            mode="lines",
            name="총 확정 소득",
            stackgroup="A",
            line=dict(color=COLORS["pastel_orange"], width=3, dash="dot"),
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
        **default_layout(
            "총 자산 = 평가 금액 + 현금", "날짜", yaxis_title, yaxis_tickformat
        )
    )
    total_assets = [float(c) + float(v) for c, v in zip(d["cash"], d["valuation"])]
    fig.update_yaxes(range=[0, max(total_assets) * 1.1])
    return fig


def cash_and_interest_graph(account_currency_type, data: PortfolioTimeSeries):
    d = preprocess_data(account_currency_type, data)

    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title, yaxis_tickformat = "금액 ($)", "~s"
    else:
        yaxis_title, yaxis_tickformat = "금액 (만원)", "d"

    cash_minus_interest = [
        float(c) - float(ti) for c, ti in zip(d["cash"], d["total_income"])
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=cash_minus_interest,
            mode="lines",
            name="현금",
            stackgroup="A",
            line=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["timestamps"],
            y=d["total_income"],
            mode="lines",
            name="이자 수익",
            stackgroup="A",
            line=dict(color=COLORS["cyan"], width=3),
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        **default_layout("현금 이자수익", "날짜", yaxis_title, yaxis_tickformat)
    )
    fig.update_yaxes(range=[0, max(d["cash"]) * 1.1])
    return fig
