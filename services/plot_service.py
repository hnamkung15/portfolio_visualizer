import plotly.graph_objects as go
from models.account import AccountCurrencyType


def graphs(
    account_currency_type,
    timestamps,
    cash,
    invest,
    valuation,
    returns,
    capital_gain,
    interest_income,
    dividend_income,
    total_income,
):
    if account_currency_type == AccountCurrencyType.USD:
        yaxis_title = "금액 ($)"
        yaxis_tickformat = "~s"  # 100k, 1M 이런 축약
    elif account_currency_type == AccountCurrencyType.KRW:
        yaxis_title = "금액 (만원)"
        yaxis_tickformat = "d"  # 숫자 축약 없이 그대로

        def to_manwon(arr):
            return [x / 10000 for x in arr]

        cash = to_manwon(cash)
        invest = to_manwon(invest)
        valuation = to_manwon(valuation)
        capital_gain = to_manwon(capital_gain)
        interest_income = to_manwon(interest_income)
        dividend_income = to_manwon(dividend_income)
        total_income = to_manwon(total_income)
    fig_1 = go.Figure()
    fig_1.add_trace(
        go.Scatter(
            x=timestamps,
            y=invest,
            mode="lines",
            name="투자 금액",
            stackgroup="A",
            line=dict(color="gray", width=2, dash="dot"),  # 회색 점선
        )
    )

    fig_1.add_trace(
        go.Scatter(
            x=timestamps,
            y=valuation,
            mode="lines",
            name="평가 금액",
            line=dict(color="green", width=3),  # 강조된 초록색
        )
    )
    fig_1.update_xaxes(tickformat="%Y-%m-%d")
    fig_1.update_layout(
        title="총 평가 금액",
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
    fig_1.update_yaxes(range=[0, max(valuation) * 1.1])
    fig_1.update_yaxes(tickformat=yaxis_tickformat)

    fig_2 = go.Figure()
    fig_2.add_trace(
        go.Scatter(
            x=timestamps,
            y=returns,
            mode="lines",
            name="수익률 (%)",
            line=dict(color="orange", width=2),
        )
    )

    fig_2.update_xaxes(tickformat="%Y-%m-%d")
    fig_2.update_layout(
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
    fig_2.add_hline(
        y=0,
        line=dict(color="black", width=1, dash="dash"),  # 검은색 점선
        annotation_text="0%",
        annotation_position="bottom right",
    )
    fig_2.update_yaxes(range=[min(returns) * 1.2, max(returns) * 1.2])

    fig_3 = go.Figure()
    fig_3.add_trace(
        go.Scatter(
            x=timestamps,
            y=capital_gain,
            mode="lines",
            name="청산이익",
            # stackgroup="A",
            line=dict(color="red"),
        )
    )
    fig_3.add_trace(
        go.Scatter(
            x=timestamps,
            y=interest_income,
            mode="lines",
            name="이자 소득",
            # stackgroup="A",
            line=dict(color="blue"),
        )
    )
    fig_3.add_trace(
        go.Scatter(
            x=timestamps,
            y=dividend_income,
            mode="lines",
            name="배당 소득",
            # stackgroup="A",
            line=dict(color="green"),
        )
    )
    fig_3.add_trace(
        go.Scatter(
            x=timestamps,
            y=total_income,
            mode="lines",
            name="총 확정 소득",
            stackgroup="A",
            line=dict(color="black", width=1, dash="dot"),
        )
    )
    fig_3.update_xaxes(tickformat="%Y-%m-%d")
    fig_3.update_layout(
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
    fig_3.update_yaxes(tickformat=yaxis_tickformat)

    fig_4 = go.Figure()
    fig_4.add_trace(
        go.Scatter(
            x=timestamps,
            y=cash,
            mode="lines",
            name="현금",
            stackgroup="A",
            line=dict(color="blue"),
        )
    )

    fig_4.add_trace(
        go.Scatter(
            x=timestamps,
            y=valuation,
            mode="lines",
            name="평가 금액",
            stackgroup="A",
            line=dict(color="green"),
        )
    )

    fig_4.update_xaxes(tickformat="%Y-%m-%d")
    fig_4.update_layout(
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

    fig_4.update_yaxes(range=[0, max(total_assets) * 1.1])
    fig_4.update_yaxes(tickformat=yaxis_tickformat)

    return (fig_1, fig_2, fig_3, fig_4)
