import plotly.graph_objects as go
from models.account import AccountCurrencyType
from services.portfolio_service import PortfolioTimeSeries


def total_valuation_and_invest_graph(account_currency_type, data: PortfolioTimeSeries):
    timestamps = data.timestamps
    cash = data.cash
    invest = data.invest
    valuation = data.valuation
    capital_gain = data.capital_gain
    interest_income = data.interest_income
    dividend_income = data.dividend_income
    total_income = data.total_income
    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title = "금액 ($)"
        yaxis_tickformat = "~s"  # 100k, 1M 이런 축약
    elif account_currency_type == AccountCurrencyType.KRW:
        yaxis_title = "금액 (만원)"
        yaxis_tickformat = "d"  # 숫자 축약 없이 그대로

        def to_manwon(arr):
            return [x / 10000 for x in arr]

        cash = to_manwon(data.cash)
        invest = to_manwon(data.invest)
        valuation = to_manwon(data.valuation)
        capital_gain = to_manwon(data.capital_gain)
        interest_income = to_manwon(data.interest_income)
        dividend_income = to_manwon(data.dividend_income)
        total_income = to_manwon(data.total_income)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=invest,
            mode="lines",
            name="투자 금액",
            stackgroup="A",
            line=dict(color="gray", width=2, dash="dot"),  # 회색 점선
        )
    )

    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=valuation,
            mode="lines",
            name="평가 금액",
            line=dict(color="green", width=3),  # 강조된 초록색
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        title="총 평가 금액",
        title_font=dict(size=24, family="Arial, sans-serif", color="rgb(33, 33, 33)"),
        xaxis_title="날짜",
        yaxis_title=yaxis_title,
        font=dict(family="Arial, sans-serif", size=14, color="rgb(102, 102, 102)"),
        template="plotly",
        showlegend=True,
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=True,
            showticklabels=True,
            tickangle=45,
            gridcolor="rgb(224, 224, 224)",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgb(224, 224, 224)",
            zeroline=True,
        ),
        margin=dict(l=50, r=50, t=80, b=50),
    )
    fig.update_yaxes(range=[0, max(valuation) * 1.1])
    fig.update_yaxes(tickformat=yaxis_tickformat)
    return fig


def return_pct_graph(account_currency_type, data: PortfolioTimeSeries):
    timestamps = data.timestamps
    cash = data.cash
    invest = data.invest
    valuation = data.valuation
    capital_gain = data.capital_gain
    interest_income = data.interest_income
    dividend_income = data.dividend_income
    total_income = data.total_income
    returns_pct = data.returns_pct
    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title = "금액 ($)"
        yaxis_tickformat = "~s"  # 100k, 1M 이런 축약
    elif account_currency_type == AccountCurrencyType.KRW:
        yaxis_title = "금액 (만원)"
        yaxis_tickformat = "d"  # 숫자 축약 없이 그대로

        def to_manwon(arr):
            return [x / 10000 for x in arr]

        cash = to_manwon(data.cash)
        invest = to_manwon(data.invest)
        valuation = to_manwon(data.valuation)
        capital_gain = to_manwon(data.capital_gain)
        interest_income = to_manwon(data.interest_income)
        dividend_income = to_manwon(data.dividend_income)
        total_income = to_manwon(data.total_income)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=returns_pct,
            mode="lines",
            name="수익률 (%)",
            line=dict(color="orange", width=2),
        )
    )

    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        title="수익률 변화 (%)",
        title_font=dict(size=24, family="Arial, sans-serif", color="rgb(33, 33, 33)"),
        xaxis_title="날짜",
        yaxis_title="수익률 (%)",
        font=dict(family="Arial, sans-serif", size=14, color="rgb(102, 102, 102)"),
        template="plotly",
        showlegend=True,
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=True,
            showticklabels=True,
            tickangle=45,
            gridcolor="rgb(224, 224, 224)",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgb(224, 224, 224)",
            zeroline=True,
        ),
        margin=dict(l=50, r=50, t=80, b=50),
    )
    fig.add_hline(
        y=0,
        line=dict(color="black", width=1, dash="dash"),  # 검은색 점선
        annotation_text="0%",
        annotation_position="bottom right",
    )
    fig.update_yaxes(range=[min(data.returns_pct) * 1.2, max(data.returns_pct) * 1.2])
    return fig


def realized_gain_graph(account_currency_type, data: PortfolioTimeSeries):
    timestamps = data.timestamps
    cash = data.cash
    invest = data.invest
    valuation = data.valuation
    capital_gain = data.capital_gain
    interest_income = data.interest_income
    dividend_income = data.dividend_income
    total_income = data.total_income

    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title = "금액 ($)"
        yaxis_tickformat = "~s"  # 100k, 1M 이런 축약
    elif account_currency_type == AccountCurrencyType.KRW:
        yaxis_title = "금액 (만원)"
        yaxis_tickformat = "d"  # 숫자 축약 없이 그대로

        def to_manwon(arr):
            return [x / 10000 for x in arr]

        cash = to_manwon(data.cash)
        invest = to_manwon(data.invest)
        valuation = to_manwon(data.valuation)
        capital_gain = to_manwon(data.capital_gain)
        interest_income = to_manwon(data.interest_income)
        dividend_income = to_manwon(data.dividend_income)
        total_income = to_manwon(data.total_income)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=capital_gain,
            mode="lines",
            name="청산이익",
            # stackgroup="A",
            line=dict(color="red"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=interest_income,
            mode="lines",
            name="이자 소득",
            # stackgroup="A",
            line=dict(color="blue"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=dividend_income,
            mode="lines",
            name="배당 소득",
            # stackgroup="A",
            line=dict(color="green"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=total_income,
            mode="lines",
            name="총 확정 소득",
            stackgroup="A",
            line=dict(color="black", width=1, dash="dot"),
        )
    )
    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        title="총 확정 소득 변화",
        title_font=dict(size=24, family="Arial, sans-serif", color="rgb(33, 33, 33)"),
        xaxis_title="날짜",
        yaxis_title=yaxis_title,
        font=dict(family="Arial, sans-serif", size=14, color="rgb(102, 102, 102)"),
        template="plotly",  # 밝고 깔끔한 스타일
        showlegend=True,
        plot_bgcolor="white",  # 배경 색상 흰색
        xaxis=dict(
            showgrid=True,
            showticklabels=True,
            tickangle=45,
            gridcolor="rgb(224, 224, 224)",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgb(224, 224, 224)",
            zeroline=True,
        ),
        margin=dict(l=50, r=50, t=80, b=50),
    )
    fig.update_yaxes(tickformat=yaxis_tickformat)
    return fig


def total_capital_and_cash_graph(account_currency_type, data: PortfolioTimeSeries):
    timestamps = data.timestamps
    cash = data.cash
    invest = data.invest
    valuation = data.valuation
    capital_gain = data.capital_gain
    interest_income = data.interest_income
    dividend_income = data.dividend_income
    total_income = data.total_income

    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title = "금액 ($)"
        yaxis_tickformat = "~s"  # 100k, 1M 이런 축약
    elif account_currency_type == AccountCurrencyType.KRW:
        yaxis_title = "금액 (만원)"
        yaxis_tickformat = "d"  # 숫자 축약 없이 그대로

        def to_manwon(arr):
            return [x / 10000 for x in arr]

        cash = to_manwon(data.cash)
        invest = to_manwon(data.invest)
        valuation = to_manwon(data.valuation)
        capital_gain = to_manwon(data.capital_gain)
        interest_income = to_manwon(data.interest_income)
        dividend_income = to_manwon(data.dividend_income)
        total_income = to_manwon(data.total_income)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=cash,
            mode="lines",
            name="현금",
            stackgroup="A",
            line=dict(color="blue"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=valuation,
            mode="lines",
            name="평가 금액",
            stackgroup="A",
            line=dict(color="green"),
        )
    )

    fig.update_xaxes(tickformat="%Y-%m-%d")
    fig.update_layout(
        title="총 자산",
        title_font=dict(size=24, family="Arial, sans-serif", color="rgb(33, 33, 33)"),
        xaxis_title="날짜",
        yaxis_title=yaxis_title,
        font=dict(family="Arial, sans-serif", size=14, color="rgb(102, 102, 102)"),
        template="plotly",  # 밝고 깔끔한 스타일
        showlegend=True,
        plot_bgcolor="white",  # 배경 색상 흰색
        xaxis=dict(
            showgrid=True,
            showticklabels=True,
            tickangle=45,
            gridcolor="rgb(224, 224, 224)",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgb(224, 224, 224)",
            zeroline=True,
        ),
        margin=dict(l=50, r=50, t=80, b=50),
    )
    total_assets = [float(c) + float(v) for c, v in zip(cash, valuation)]

    fig.update_yaxes(range=[0, max(total_assets) * 1.1])
    fig.update_yaxes(tickformat=yaxis_tickformat)
    return fig
