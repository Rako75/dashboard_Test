import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration de la page
st.set_page_config(
    page_title="RakoStats Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Moderne et Professionnel
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Variables CSS */
    :root {
        --primary: #1e40af;
        --primary-dark: #1e3a8a;
        --secondary: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --dark: #0f172a;
        --gray: #64748b;
        --light: #f8fafc;
    }
    
    /* Reset Streamlit */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Header Principal */
    .main-header {
        background: linear-gradient(135deg, var(--primary-dark), var(--primary), var(--secondary));
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.8);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255,255,255,0.05);
        padding: 0.5rem;
        border-radius: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: rgba(255,255,255,0.6);
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: var(--primary);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.3);
        border-color: rgba(255,255,255,0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: rgba(255,255,255,0.6);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    /* Player Card */
    .player-card {
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.2), rgba(6, 182, 212, 0.1));
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
    }
    
    .player-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(30, 64, 175, 0.4);
        border-color: var(--secondary);
    }
    
    .player-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: white;
        margin: 0.5rem 0;
    }
    
    .player-team {
        font-size: 0.875rem;
        color: var(--secondary);
        font-weight: 600;
    }
    
    /* Filters */
    .filter-section {
        background: rgba(255,255,255,0.05);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-primary {
        background: var(--primary);
        color: white;
    }
    
    .badge-success {
        background: var(--success);
        color: white;
    }
    
    .badge-warning {
        background: var(--warning);
        color: white;
    }
    
    /* Percentile Bar */
    .percentile-bar {
        height: 0.5rem;
        background: rgba(255,255,255,0.1);
        border-radius: 0.25rem;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .percentile-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--success), var(--secondary));
        border-radius: 0.25rem;
        transition: width 0.3s ease;
    }
    
    /* Section Title */
    .section-title {
        color: white;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(255,255,255,0.1);
    }
    
    /* Buttons */
    .stButton button {
        background: var(--primary);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: var(--primary-dark);
        box-shadow: 0 8px 16px rgba(30, 64, 175, 0.4);
        transform: translateY(-2px);
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# Initialisation de la session state
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'grid'

# Données de démonstration
@st.cache_data
def load_demo_data():
    df = pd.read_csv('df_BIG2025.csv', encoding='utf-8', delimiter=';')
    # Nettoyer les colonnes numériques
    numeric_cols = ['Buts', 'Passes décisives', 'Buts attendus (xG)', 'Passes décisives attendues (xAG)', 
                    'Minutes jouées', 'Âge', 'Valeur marchande']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

players_df = load_demo_data()

# Header Principal
st.markdown("""
<div class="main-header">
    <h1>⚽ RakoStats Pro</h1>
    <p>Advanced Football Scouting & Analytics Platform · Season 2024/25</p>
</div>
""", unsafe_allow_html=True)

# Navigation principale
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "👥 Players Database", "⭐ Shortlist", "📈 Advanced Analytics"])

# ============================================================================
# TAB 1: DASHBOARD
# ============================================================================
with tab1:
    # KPIs Globaux
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Players</div>
            <div class="metric-value">{len(players_df)}</div>
            <div class="badge badge-primary">Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Compétitions</div>
            <div class="metric-value">{players_df['Compétition'].nunique()}</div>
            <div class="badge badge-success">Top 5</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Age</div>
            <div class="metric-value">{players_df['Âge'].mean():.1f}</div>
            <div class="badge badge-warning">Years</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_value = players_df['Valeur marchande'].sum() / 1000000  # Conversion en millions
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Value</div>
            <div class="metric-value">€{total_value:.0f}M</div>
            <div class="badge badge-success">Market</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Shortlist</div>
            <div class="metric-value">{len(st.session_state.shortlist)}</div>
            <div class="badge badge-primary">Saved</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">🔥 Top Performers</div>', unsafe_allow_html=True)
    
    # Top performers par catégorie
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### ⚽ Top Scorers")
        top_scorers = players_df.nlargest(5, 'Buts')[['Joueur', 'Équipe', 'Buts']]
        for idx, row in top_scorers.iterrows():
            st.markdown(f"""
            <div class="player-card">
                <div class="player-name">{row['Joueur']}</div>
                <div class="player-team">{row['Équipe']}</div>
                <div class="metric-value" style="font-size: 1.5rem;">{int(row['Buts'])} goals</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Top Assisters")
        top_assists = players_df.nlargest(5, 'Passes décisives')[['Joueur', 'Équipe', 'Passes décisives']]
        for idx, row in top_assists.iterrows():
            st.markdown(f"""
            <div class="player-card">
                <div class="player-name">{row['Joueur']}</div>
                <div class="player-team">{row['Équipe']}</div>
                <div class="metric-value" style="font-size: 1.5rem;">{int(row['Passes décisives'])} assists</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 💎 Highest Value")
        top_valued = players_df.nlargest(5, 'Valeur marchande')[['Joueur', 'Équipe', 'Valeur marchande']]
        for idx, row in top_valued.iterrows():
            st.markdown(f"""
            <div class="player-card">
                <div class="player-name">{row['Joueur']}</div>
                <div class="player-team">{row['Équipe']}</div>
                <div class="metric-value" style="font-size: 1.5rem;">€{row['Valeur marchande']/1000000:.1f}M</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Graphiques
    st.markdown('<div class="section-title">📊 Visual Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Goals vs xG scatter
        fig_scatter = px.scatter(
            players_df[players_df['Minutes jouées'] > 900], 
            x='Buts attendus (xG)', 
            y='Buts',
            size='Valeur marchande',
            color='Position',
            hover_data=['Joueur', 'Équipe'],
            title='Goals vs Expected Goals (xG)',
            labels={'Buts attendus (xG)': 'Expected Goals', 'Buts': 'Actual Goals'}
        )
        fig_scatter.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Distribution par position
        fig_bar = px.bar(
            players_df.groupby('Position').size().reset_index(name='count'),
            x='Position',
            y='count',
            title='Players by Position',
            color='Position'
        )
        fig_bar.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ============================================================================
# TAB 2: PLAYERS DATABASE
# ============================================================================
with tab2:
    st.markdown('<div class="section-title">🔍 Player Search & Filters</div>', unsafe_allow_html=True)
    
    # Filtres
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_name = st.text_input("🔎 Search by name", placeholder="Enter player name...")
    
    with col2:
        filter_competition = st.selectbox("🏆 Compétition", ['All'] + sorted(players_df['Compétition'].unique().tolist()))
    
    with col3:
        filter_position = st.selectbox("📍 Position", ['All'] + sorted(players_df['Position'].unique().tolist()))
    
    with col4:
        age_range = st.slider("📅 Age Range", 16, 40, (18, 35))
    
    # Appliquer les filtres
    filtered_df = players_df.copy()
    
    if search_name:
        filtered_df = filtered_df[filtered_df['Joueur'].str.contains(search_name, case=False, na=False)]
    
    if filter_competition != 'All':
        filtered_df = filtered_df[filtered_df['Compétition'] == filter_competition]
    
    if filter_position != 'All':
        filtered_df = filtered_df[filtered_df['Position'] == filter_position]
    
    filtered_df = filtered_df[(filtered_df['Âge'] >= age_range[0]) & (filtered_df['Âge'] <= age_range[1])]
    
    st.markdown(f'<div class="section-title">👥 Players ({len(filtered_df)} results)</div>', unsafe_allow_html=True)
    
    # Affichage en grille
    cols_per_row = 3
    for i in range(0, min(len(filtered_df), 30), cols_per_row):  # Limiter à 30 joueurs pour la performance
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(filtered_df):
                player = filtered_df.iloc[i + j]
                with col:
                    # Bouton shortlist
                    is_in_shortlist = player['Joueur'] in st.session_state.shortlist
                    star_icon = "⭐" if is_in_shortlist else "☆"
                    
                    # Calculer un rating basé sur les performances
                    rating = min(100, int((player['Buts'] * 5 + player['Passes décisives'] * 3 + player['Minutes jouées'] / 100) / 2))
                    
                    st.markdown(f"""
                    <div class="player-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <div class="player-name">{player['Joueur']}</div>
                                <div class="player-team">{player['Équipe']}</div>
                            </div>
                            <div style="font-size: 1.5rem; cursor: pointer;">{star_icon}</div>
                        </div>
                        <div style="margin: 1rem 0;">
                            <span class="badge badge-primary">{player['Position']}</span>
                            <span class="badge badge-success">{int(player['Âge'])} yrs</span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 1rem;">
                            <div>
                                <div class="metric-label">Goals</div>
                                <div class="metric-value" style="font-size: 1.5rem;">{int(player['Buts'])}</div>
                            </div>
                            <div>
                                <div class="metric-label">Assists</div>
                                <div class="metric-value" style="font-size: 1.5rem;">{int(player['Passes décisives'])}</div>
                            </div>
                        </div>
                        <div style="margin-top: 1rem;">
                            <div class="metric-label">Market Value</div>
                            <div class="metric-value" style="font-size: 1.25rem; color: #10b981;">€{player['Valeur marchande']/1000000:.1f}M</div>
                        </div>
                        <div style="margin-top: 1rem;">
                            <div class="metric-label">Rating</div>
                            <div class="percentile-bar">
                                <div class="percentile-fill" style="width: {rating}%;"></div>
                            </div>
                            <div style="color: white; font-weight: 600; margin-top: 0.25rem;">{rating}/100</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Boutons d'action
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(star_icon, key=f"star_{i}_{j}", use_container_width=True):
                            if player['Joueur'] in st.session_state.shortlist:
                                st.session_state.shortlist.remove(player['Joueur'])
                            else:
                                st.session_state.shortlist.append(player['Joueur'])
                            st.rerun()
                    
                    with col_b:
                        if st.button("📊 View", key=f"view_{i}_{j}", use_container_width=True):
                            st.session_state.selected_player = player['Joueur']
                            st.rerun()

# ============================================================================
# TAB 3: SHORTLIST
# ============================================================================
with tab3:
    st.markdown('<div class="section-title">⭐ My Shortlist</div>', unsafe_allow_html=True)
    
    if len(st.session_state.shortlist) == 0:
        st.info("📋 Your shortlist is empty. Add players from the Players Database!")
    else:
        shortlist_df = players_df[players_df['Joueur'].isin(st.session_state.shortlist)]
        
        # Actions
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.shortlist = []
                st.rerun()
        
        with col2:
            if st.button("📥 Export CSV", use_container_width=True):
                csv = shortlist_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="shortlist.csv",
                    mime="text/csv"
                )
        
        # Afficher les joueurs
        for idx, player in shortlist_df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"### {player['Joueur']}")
                st.markdown(f"**{player['Équipe']}** · {player['Compétition']}")
            
            with col2:
                st.metric("Goals", int(player['Buts']))
            
            with col3:
                st.metric("Assists", int(player['Passes décisives']))
            
            with col4:
                st.metric("Minutes", int(player['Minutes jouées']))
            
            with col5:
                st.metric("Value", f"€{player['Valeur marchande']/1000000:.1f}M")
            
            with col6:
                if st.button("❌", key=f"remove_{player['Joueur']}_{idx}"):
                    st.session_state.shortlist.remove(player['Joueur'])
                    st.rerun()
            
            st.divider()

# ============================================================================
# TAB 4: ADVANCED ANALYTICS
# ============================================================================
with tab4:
    st.markdown('<div class="section-title">📈 Advanced Analytics</div>', unsafe_allow_html=True)
    
    # Sélection de joueurs à comparer
    col1, col2 = st.columns(2)
    
    player_list = players_df['Joueur'].tolist()
    
    with col1:
        player1 = st.selectbox("Select Player 1", player_list)
    
    with col2:
        player2 = st.selectbox("Select Player 2", player_list, index=min(1, len(player_list)-1))
    
    if player1 and player2:
        p1_data = players_df[players_df['Joueur'] == player1].iloc[0]
        p2_data = players_df[players_df['Joueur'] == player2].iloc[0]
        
        # Radar chart comparaison
        categories = ['Goals', 'Assists', 'xG', 'xAG', 'Minutes/90']
        
        fig_radar = go.Figure()
        
        # Normaliser les valeurs pour le radar
        p1_values = [
            min(100, p1_data['Buts'] * 10),
            min(100, p1_data['Passes décisives'] * 10),
            min(100, p1_data['Buts attendus (xG)'] * 10),
            min(100, p1_data['Passes décisives attendues (xAG)'] * 10),
            min(100, (p1_data['Minutes jouées'] / 90) * 2)
        ]
        
        p2_values = [
            min(100, p2_data['Buts'] * 10),
            min(100, p2_data['Passes décisives'] * 10),
            min(100, p2_data['Buts attendus (xG)'] * 10),
            min(100, p2_data['Passes décisives attendues (xAG)'] * 10),
            min(100, (p2_data['Minutes jouées'] / 90) * 2)
        ]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=p1_values,
            theta=categories,
            fill='toself',
            name=player1,
            fillcolor='rgba(30, 64, 175, 0.3)',
            line=dict(color='#1e40af', width=3)
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=p2_values,
            theta=categories,
            fill='toself',
            name=player2,
            fillcolor='rgba(6, 182, 212, 0.3)',
            line=dict(color='#06b6d4', width=3)
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=True,
            title=f"Performance Comparison: {player1} vs {player2}",
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14)
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Tableau comparatif
        st.markdown('<div class="section-title">📊 Detailed Comparison</div>', unsafe_allow_html=True)
        
        comparison_df = pd.DataFrame({
            'Metric': ['Goals', 'Assists', 'xG', 'xAG', 'Minutes', 'Matches', 'Yellow Cards', 'Red Cards'],
            player1: [
                int(p1_data['Buts']), 
                int(p1_data['Passes décisives']), 
                f"{p1_data['Buts attendus (xG)']:.2f}", 
                f"{p1_data['Passes décisives attendues (xAG)']:.2f}",
                int(p1_data['Minutes jouées']),
                int(p1_data['Matchs joués']),
                int(p1_data['Cartons jaunes']),
                int(p1_data['Cartons rouges'])
            ],
            player2: [
                int(p2_data['Buts']), 
                int(p2_data['Passes décisives']), 
                f"{p2_data['Buts attendus (xG)']:.2f}", 
                f"{p2_data['Passes décisives attendues (xAG)']:.2f}",
                int(p2_data['Minutes jouées']),
                int(p2_data['Matchs joués']),
                int(p2_data['Cartons jaunes']),
                int(p2_data['Cartons rouges'])
            ]
        })
        
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.5); font-size: 0.875rem;">
    <p>RakoStats Pro © 2025 · Advanced Football Analytics · Powered by Streamlit</p>
    <p>Data: Season 2024/25</p>
</div>
""", unsafe_allow_html=True)
