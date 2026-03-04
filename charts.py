# charts.py — All Plotly visualizations

import numpy as np
import plotly.graph_objects as go

GOLD = '#D4AF37'
DARK = '#AA8418'
BG   = 'rgba(0,0,0,0)'
FONT = '#e0e0e0'


def _layout(title: str, height: int = 320) -> dict:
    return dict(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font_color=FONT,
        title=dict(text=title, font=dict(color=GOLD, size=14)),
        height=height,
        margin=dict(t=45, b=15, l=10, r=10),
    )


def prob_bar(res: dict, home: str = "Home", away: str = "Away") -> go.Figure:
    """Horizontal probability bar chart for 1X2 outcomes."""
    fig = go.Figure(go.Bar(
        x=[f"🏠 {home}", "Draw", f"✈️ {away}"],
        y=[res['home'], res['draw'], res['away']],
        marker_color=[GOLD, '#555555', DARK],
        text=[f"{v:.1%}" for v in [res['home'], res['draw'], res['away']]],
        textposition='outside',
        textfont=dict(color=FONT),
    ))
    fig.update_layout(
        **_layout("Outcome Probabilities"),
        yaxis=dict(tickformat='.0%', gridcolor='#1a1a1a', range=[0, 1.1]),
        showlegend=False,
    )
    return fig


def score_heatmap(matrix: np.ndarray) -> go.Figure:
    """6×6 correct score probability heatmap."""
    m6 = matrix[:6, :6]
    fig = go.Figure(go.Heatmap(
        z=m6,
        x=[str(i) for i in range(6)],
        y=[str(i) for i in range(6)],
        colorscale=[[0, '#0a0a0a'], [0.5, '#5a3e00'], [1, GOLD]],
        text=[[f"{m6[i, j]:.1%}" for j in range(6)] for i in range(6)],
        texttemplate="%{text}",
        showscale=False,
    ))
    fig.update_layout(
        **_layout("Correct Score Heatmap  (Home ↕  Away →)", height=340),
        xaxis_title="Away Goals",
        yaxis_title="Home Goals",
    )
    return fig


def team_radar(home_name: str, away_name: str, home_str: float, away_str: float) -> go.Figure:
    """
    Radar chart comparing two teams on five derived attributes.
    Values are visual proxies scaled from the strength rating.
    """
    categories = ['Attack', 'Defense', 'Strength', 'Form', 'Value']

    def make_vals(s):
        return [s, 2.0 - s, s * 0.95, s * 1.05, s * 0.90]

    h_vals = make_vals(home_str)
    a_vals = make_vals(away_str)
    mx     = max(max(h_vals), max(a_vals), 0.01)
    h_vals = [v / mx * 10 for v in h_vals]
    a_vals = [v / mx * 10 for v in a_vals]
    cats   = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=h_vals + [h_vals[0]], theta=cats, fill='toself',
        name=home_name, line_color=GOLD,
        fillcolor='rgba(212,175,55,0.15)',
    ))
    fig.add_trace(go.Scatterpolar(
        r=a_vals + [a_vals[0]], theta=cats, fill='toself',
        name=away_name, line_color=DARK,
        fillcolor='rgba(170,132,24,0.10)',
    ))
    fig.update_layout(
        **_layout("Team Comparison", height=340),
        polar=dict(
            bgcolor=BG,
            radialaxis=dict(visible=True, range=[0, 10], color='#555'),
            angularaxis=dict(color=GOLD),
        ),
        legend=dict(font=dict(color=FONT)),
        showlegend=True,
    )
    return fig


def pnl_chart(bet_history: list):
    """Running profit/loss line chart from settled bets. Returns None if no settled bets."""
    settled = [
        (b['Stake ($)'], b['Potential'], b['Result'])
        for b in bet_history
        if b['Result'] in ('Won', 'Lost')
    ]
    if not settled:
        return None

    running, total = [], 0.0
    for stake, potential, result in settled:
        total += (potential - stake) if result == 'Won' else -stake
        running.append(round(total, 2))

    line_color = GOLD if running[-1] >= 0 else '#c0392b'
    fig = go.Figure(go.Scatter(
        x=list(range(1, len(running) + 1)),
        y=running,
        mode='lines+markers',
        line=dict(color=line_color, width=2),
        marker=dict(color=line_color, size=6),
        fill='tozeroy',
        fillcolor='rgba(212,175,55,0.08)',
    ))
    fig.update_layout(
        **_layout("Running Profit / Loss", height=300),
        xaxis_title="Bet #",
        yaxis=dict(
            title="P&L ($)",
            gridcolor='#1a1a1a',
            zeroline=True,
            zerolinecolor='#444',
        ),
    )
    return fig
