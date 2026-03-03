import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd
from itertools import combinations
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta

# API Configuration
API_KEY = st.secrets["FOOTBALL_API_KEY"] if "FOOTBALL_API_KEY" in st.secrets else "7ab0a5f50ad043559bb77700e966fe78"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {
    'X-Auth-Token': API_KEY,
    'Accept-Encoding': ''
}

# Page config
st.set_page_config(
    page_title="Blackmosphere Odds",
    page_icon="⚫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    }
    .stMarkdown, .stText, h1, h2, h3, h4, p {
        color: #e0e0e0 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    h1 {
        text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: 2px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
        color: #00d4ff;
    }
    [data-testid="stMetricLabel"] {
        color: #a0a0a0;
    }
    .stSuccess {
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid #00ff88;
        border-radius: 10px;
    }
    .stInfo {
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# League mapping
LEAGUE_CODES = {
    'Premier League': 'PL',
    'Bundesliga': 'BL1',
    'Serie A': 'SA',
    'La Liga': 'PD',
    'Ligue 1': 'FL1',
    'Eredivisie': 'DED'
}

# Fallback parameters
fallback_league_params = {
    'PL': {'home_win_rate': 0.45, 'draw_rate': 0.25, 'away_win_rate': 0.30, 'home_adv_goals': 0.32, 'xg_per_match': 2.79, 'btts_rate': 0.57},
    'BL1': {'home_win_rate': 0.47, 'draw_rate': 0.24, 'away_win_rate': 0.29, 'home_adv_goals': 0.35, 'xg_per_match': 3.18, 'btts_rate': 0.60},
    'SA': {'home_win_rate': 0.43, 'draw_rate': 0.27, 'away_win_rate': 0.30, 'home_adv_goals': 0.35, 'xg_per_match': 2.35, 'btts_rate': 0.49},
    'PD': {'home_win_rate': 0.43, 'draw_rate': 0.27, 'away_win_rate': 0.30, 'home_adv_goals': 0.36, 'xg_per_match': 2.5, 'btts_rate': 0.48},
    'FL1': {'home_win_rate': 0.42, 'draw_rate': 0.28, 'away_win_rate': 0.30, 'home_adv_goals': 0.33, 'xg_per_match': 2.9, 'btts_rate': 0.55},
    'DED': {'home_win_rate': 0.45, 'draw_rate': 0.25, 'away_win_rate': 0.30, 'home_adv_goals': 0.40, 'xg_per_match': 3.3, 'btts_rate': 0.61}
}

@st.cache_data(ttl=300)
def fetch_live_matches():
    """Fetch upcoming matches from the API."""
    try:
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        url = f"{BASE_URL}/matches"
        params = {
            'dateFrom': date_from,
            'dateTo': date_to,
            'status': 'SCHEDULED'
        }
        
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        matches = []
        for match in data.get('matches', []):
            comp_code = match.get('competition', {}).get('code')
            if comp_code in LEAGUE_CODES.values():
                matches.append({
                    'id': match['id'],
                    'home_team': match['homeTeam']['name'],
                    'away_team': match['awayTeam']['name'],
                    'competition': match['competition']['name'],
                    'competition_code': comp_code,
                    'date': match['utcDate'],
                    'odds': match.get('odds', {})
                })
        return matches
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return []

def predict_match_outcome(league, home_strength=1.0, away_strength=1.0, live_odds=None):
    """Predict match outcome using Poisson distribution."""
    league_api_code = LEAGUE_CODES.get(league)
    if not league_api_code:
        raise ValueError(f"Unsupported league: {league}")
    
    params = fallback_league_params[league_api_code]
    avg_goals = params['xg_per_match'] / 2
    
    # Home advantage calculation
    home_adv = params['home_adv_goals']
    home_adv_factor = 1 + (0.2 * np.tanh(home_adv / 0.5)) + (0.05 * (home_strength - away_strength))
    home_adv_factor = max(0.5, min(2.0, home_adv_factor))
    
    # Lambda calculations
    lambda_home = avg_goals * home_strength * home_adv_factor / away_strength
    lambda_away = avg_goals * away_strength / (home_strength * home_adv_factor)
    
    lambda_home = max(0.1, lambda_home)
    lambda_away = max(0.1, lambda_away)
    
    # Poisson probabilities
    max_goals = 15
    h_goals = np.arange(max_goals + 1)
    a_goals = np.arange(max_goals + 1)
    p_h = poisson.pmf(h_goals, lambda_home)
    p_a = poisson.pmf(a_goals, lambda_away)
    
    prob_matrix = np.outer(p_h, p_a)
    
    p_home_win = np.sum(prob_matrix[np.triu_indices_from(prob_matrix, k=1)])
    p_draw = np.sum(np.diag(prob_matrix))
    p_away_win = np.sum(prob_matrix[np.tril_indices_from(prob_matrix, k=-1)])
    p_btts = np.sum(prob_matrix[1:, 1:])
    
    # Normalize
    total = p_home_win + p_draw + p_away_win
    if total > 0:
        p_home_win /= total
        p_draw /= total
        p_away_win /= total
    
    # Blend BTTS
    blend_factor = 0.5
    p_btts = blend_factor * p_btts + (1 - blend_factor) * params['btts_rate']
    p_btts = max(0, min(1, p_btts))
    
    live_home_odds = live_odds.get('homeWin') if live_odds else None
    live_draw_odds = live_odds.get('draw') if live_odds else None
    live_away_odds = live_odds.get('awayWin') if live_odds else None
    
    return {
        'home_win_prob': p_home_win,
        'draw_prob': p_draw,
        'away_win_prob': p_away_win,
        'expected_home_goals': lambda_home,
        'expected_away_goals': lambda_away,
        'btts_prob': p_btts,
        'home_odds': 1 / p_home_win if p_home_win > 0.001 else float('inf'),
        'draw_odds': 1 / p_draw if p_draw > 0.001 else float('inf'),
        'away_odds': 1 / p_away_win if p_away_win > 0.001 else float('inf'),
        'btts_odds': 1 / p_btts if p_btts > 0.001 else float('inf'),
        'live_home_odds': live_home_odds,
        'live_draw_odds': live_draw_odds,
        'live_away_odds': live_away_odds
    }

def create_prob_chart(pred):
    """Create bar chart of probabilities."""
    outcomes = ['Home Win', 'Draw', 'Away Win']
    probs = [pred['home_win_prob'], pred['draw_prob'], pred['away_win_prob']]
    colors = ['#00d4ff', '#ffd700', '#ff6b6b']
    
    fig = go.Figure(data=[
        go.Bar(
            x=outcomes,
            y=[p*100 for p in probs],
            marker_color=colors,
            text=[f'{p*100:.1f}%' for p in probs],
            textposition='auto',
            textfont={'color': 'white', 'size': 14}
        )
    ])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e0e0e0'},
        height=300,
        yaxis_title='Probability (%)',
        xaxis_title='Outcome',
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=40)
    )
    
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)', range=[0, 100])
    
    return fig

# Initialize session state
if 'parlay_matches' not in st.session_state:
    st.session_state.parlay_matches = []

# Header
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="font-size: 3.5rem; margin-bottom: 10px;">⚫ BLACKMOSPHERE ODDS</h1>
    <p style="font-size: 1.2rem; color: #888; letter-spacing: 3px;">ADVANCED PREDICTIVE ANALYTICS</p>
    <div style="margin-top: 10px;">
        <span style="display: inline-block; width: 10px; height: 10px; background: #00ff88; border-radius: 50%; animation: pulse 2s infinite; margin-right: 8px;"></span>
        <span style="color: #00ff88; font-size: 0.9rem;">LIVE DATA CONNECTED</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Create tabs
tab1, tab2, tab3 = st.tabs(["🔮 Match Predictor", "⚽ Live Matches", "🎯 Parlay Builder"])

with tab1:
    st.markdown("### Configure Match Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 Home Team")
        home_league = st.selectbox("Select League", list(LEAGUE_CODES.keys()), key='home_league')
        home_strength = st.slider("Team Strength Multiplier", 0.5, 2.0, 1.0, 0.1, key='home_strength')
        st.caption("1.0 = Average, >1.0 = Stronger, <1.0 = Weaker")
    
    with col2:
        st.markdown("#### ✈️ Away Team")
        away_league = st.selectbox("Select League (Away)", list(LEAGUE_CODES.keys()), key='away_league')
        away_strength = st.slider("Team Strength Multiplier", 0.5, 2.0, 1.0, 0.1, key='away_strength')
    
    selected_league = home_league
    
    if st.button("🚀 Calculate Prediction", use_container_width=True):
        try:
            pred = predict_match_outcome(selected_league, home_strength, away_strength)
            
            st.markdown("---")
            st.markdown("### 📊 Prediction Results")
            
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            
            with mcol1:
                st.metric("Expected Goals (H)", f"{pred['expected_home_goals']:.2f}")
            with mcol2:
                st.metric("Expected Goals (A)", f"{pred['expected_away_goals']:.2f}")
            with mcol3:
                st.metric("BTTS Probability", f"{pred['btts_prob']*100:.1f}%")
            with mcol4:
                st.metric("BTTS Odds", f"{pred['btts_odds']:.2f}")
            
            st.markdown("---")
            st.markdown("#### Win Probability Distribution")
            
            prob_col1, prob_col2 = st.columns([2, 1])
            
            with prob_col1:
                fig = create_prob_chart(pred)
                st.plotly_chart(fig, use_container_width=True)
            
            with prob_col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,212,255,0.05)); 
                            border: 1px solid #00d4ff; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                    <div style="color: #00d4ff; font-size: 0.9rem;">Home Win</div>
                    <div style="color: white; font-size: 1.8rem; font-weight: bold;">{pred['home_win_prob']*100:.1f}%</div>
                    <div style="color: #888; font-size: 0.9rem;">Odds: {pred['home_odds']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,215,0,0.05)); 
                            border: 1px solid #ffd700; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                    <div style="color: #ffd700; font-size: 0.9rem;">Draw</div>
                    <div style="color: white; font-size: 1.8rem; font-weight: bold;">{pred['draw_prob']*100:.1f}%</div>
                    <div style="color: #888; font-size: 0.9rem;">Odds: {pred['draw_odds']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(255,107,107,0.2), rgba(255,107,107,0.05)); 
                            border: 1px solid #ff6b6b; border-radius: 10px; padding: 15px;">
                    <div style="color: #ff6b6b; font-size: 0.9rem;">Away Win</div>
                    <div style="color: white; font-size: 1.8rem; font-weight: bold;">{pred['away_win_prob']*100:.1f}%</div>
                    <div style="color: #888; font-size: 0.9rem;">Odds: {pred['away_odds']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("➕ Add to Parlay Builder", use_container_width=True):
                match_data = {
                    'league': selected_league,
                    'home_team': 'Custom Home',
                    'away_team': 'Custom Away',
                    'home_strength': home_strength,
                    'away_strength': away_strength,
                    'pred': pred
                }
                st.session_state.parlay_matches.append(match_data)
                st.success(f"Added to parlay builder!")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab2:
    st.markdown("### ⚽ Live Upcoming Matches")
    
    with st.spinner("Fetching live matches..."):
        live_matches = fetch_live_matches()
    
    if not live_matches:
        st.warning("No live matches available. API may be loading or limit reached.")
    else:
        st.success(f"Found {len(live_matches)} upcoming matches")
        
        for match in live_matches[:5]:
            with st.container():
                match_time = datetime.fromisoformat(match['date'].replace('Z', '+00:00'))
                local_time = match_time.strftime('%d %b %H:%M')
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); 
                                border-radius: 12px; padding: 15px; margin: 10px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="text-align: center; flex: 1;">
                                <div style="font-size: 1.1rem; font-weight: bold; color: #00d4ff;">{match['home_team']}</div>
                            </div>
                            <div style="padding: 0 15px; color: #ffd700; font-weight: bold;">VS</div>
                            <div style="text-align: center; flex: 1;">
                                <div style="font-size: 1.1rem; font-weight: bold; color: #ff6b6b;">{match['away_team']}</div>
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 8px; color: #888; font-size: 0.85rem;">
                            🏆 {match['competition']} | 🕒 {local_time}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"Analyze", key=f"analyze_{match['id']}"):
                        pred = predict_match_outcome(match['competition'], live_odds=match.get('odds', {}))
                        st.session_state.current_match = {'match': match, 'pred': pred}
                        st.rerun()
                    
                    if st.button(f"Add +", key=f"add_{match['id']}"):
                        pred = predict_match_outcome(match['competition'], live_odds=match.get('odds', {}))
                        match_data = {
                            'league': match['competition'],
                            'home_team': match['home_team'],
                            'away_team': match['away_team'],
                            'pred': pred
                        }
                        st.session_state.parlay_matches.append(match_data)
                        st.success("Added!")

with tab3:
    st.markdown("### 🎯 Parlay Builder")
    
    if not st.session_state.parlay_matches:
        st.info("No matches added. Go to Match Predictor or Live Matches to add.")
    else:
        st.markdown(f"**{len(st.session_state.parlay_matches)} matches selected**")
        
        for i, match in enumerate(st.session_state.parlay_matches):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                home = match.get('home_team', 'Home')
                away = match.get('away_team', 'Away')
                st.markdown(f"**{match['league']}**<br>{home} vs {away}", unsafe_allow_html=True)
            with col2:
                best = max([
                    ('Home', match['pred']['home_win_prob'], match['pred']['home_odds']),
                    ('Draw', match['pred']['draw_prob'], match['pred']['draw_odds']),
                    ('Away', match['pred']['away_win_prob'], match['pred']['away_odds'])
                ], key=lambda x: x[1])
                st.markdown(f"Best: **{best[0]}** ({best[1]*100:.1f}%)")
            with col3:
                if st.button("🗑️", key=f"remove_{i}"):
                    st.session_state.parlay_matches.pop(i)
                    st.rerun()
        
        if len(st.session_state.parlay_matches) >= 2:
            st.markdown("---")
            if st.button("🔍 Calculate Parlay", use_container_width=True):
                total_odds = 1.0
                total_prob = 1.0
                for match in st.session_state.parlay_matches:
                    best_prob = max(match['pred']['home_win_prob'], match['pred']['draw_prob'], match['pred']['away_win_prob'])
                    best_odds = max(match['pred']['home_odds'], match['pred']['draw_odds'], match['pred']['away_odds'])
                    total_odds *= best_odds
                    total_prob *= best_prob
                
                st.markdown(f"""
                <div style="background: rgba(123, 44, 191, 0.2); border: 1px solid rgba(123, 44, 191, 0.5); 
                            border-radius: 15px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #00d4ff; margin-top: 0;">Parlay Summary</h3>
                    <div style="display: flex; justify-content: space-around; text-align: center;">
                        <div>
                            <div style="color: #888; font-size: 0.9rem;">Total Odds</div>
                            <div style="color: #ffd700; font-size: 2rem; font-weight: bold;">{total_odds:.2f}</div>
                        </div>
                        <div>
                            <div style="color: #888; font-size: 0.9rem;">Win Probability</div>
                            <div style="color: #00ff88; font-size: 2rem; font-weight: bold;">{total_prob*100:.2f}%</div>
                        </div>
                        <div>
                            <div style="color: #888; font-size: 0.9rem;">Expected Value</div>
                            <div style="color: #ff6b6b; font-size: 2rem; font-weight: bold;">{total_prob * total_odds:.3f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #555; padding: 20px;">
    <p style="font-size: 0.8rem;">⚫ BLACKMOSPHERE ODDS v2.0 | Powered by Football-Data.org</p>
</div>
""", unsafe_allow_html=True)
