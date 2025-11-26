import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats # Indispensable pour les calculs de percentiles

# ============================================================================
# 1. CONFIGURATION DE LA PAGE & STYLES
# ============================================================================
st.set_page_config(
    page_title="RakoStats Pro | Scouting Platform",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Optimisé et Moderne
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #3b82f6;
        --secondary: #8b5cf6;
        --bg-dark: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.7);
    }
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 60%);
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.1));
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    
    .stat-card {
        background: var(--card-bg);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.25rem;
        transition: transform 0.2s;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255,255,255,0.1);
    }
    
    /* Player Cards Grid */
    .player-card-grid {
        background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem;
        height: 100%;
    }
    
    /* Badges */
    .custom-badge {
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Tabs Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(0,0,0,0.2);
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary) !important;
        color: white !important;
    }
    
    /* Remove default streamlit junk */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 2. GESTION DES DONNÉES (ROBUSTESSE)
# ============================================================================

# Initialisation Session State
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

@st.cache_data
def generate_dummy_data():
    """Génère des données de test si aucun CSV n'est trouvé."""
    names = [f"Player {i}" for i in range(1, 201)]
    teams = ['Real Madrid', 'Man City', 'Arsenal', 'Bayern', 'PSG', 'Inter', 'Liverpool']
    positions = ['Attaquant', 'Milieu', 'Défenseur', 'Gardien']
    
    data = {
        'Joueur': names,
        'Équipe': np.random.choice(teams, 200),
        'Compétition': np.random.choice(['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1'], 200),
        'Position': np.random.choice(positions, 200),
        'Âge': np.random.randint(17, 38, 200),
        'Matchs joués': np.random.randint(5, 38, 200),
        'Minutes jouées': np.random.randint(400, 3400, 200),
        'Buts': np.random.poisson(3, 200),
        'Passes décisives': np.random.poisson(2, 200),
        'Valeur marchande': np.random.randint(1000000, 150000000, 200)
    }
    df = pd.DataFrame(data)
    # Ajout de corrélation pour le réalisme (plus de buts pour les attaquants)
    df.loc[df['Position'] == 'Attaquant', 'Buts'] += np.random.randint(5, 15, len(df[df['Position'] == 'Attaquant']))
    df['Buts attendus (xG)'] = df['Buts'] * np.random.uniform(0.8, 1.2, 200)
    df['Passes décisives attendues (xAG)'] = df['Passes décisives'] * np.random.uniform(0.8, 1.2, 200)
    return df

@st.cache_data
def load_and_prep_data(uploaded_file=None):
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, delimiter=';' if uploaded_file.name.endswith('.csv') else ',')
        except:
            df = pd.read_csv(uploaded_file, encoding='latin-1')
    else:
        try:
            df = pd.read_csv('df_BIG2025.csv', delimiter=';', encoding='utf-8')
        except FileNotFoundError:
            df = generate_dummy_data()
            
    # Nettoyage et conversion
    numeric_cols = ['Buts', 'Passes décisives', 'Buts attendus (xG)', 'Passes décisives attendues (xAG)', 
                    'Minutes jouées', 'Âge', 'Valeur marchande']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

# Chargement initial
with st.sidebar:
    st.markdown("### ⚙️ Data Settings")
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    st.info("Format attendu: Délimiteur ';', colonnes: Joueur, Équipe, Position, Buts, etc.")

df_raw = load_and_prep_data(uploaded_file)
if uploaded_file is None and 'Player 1' in df_raw['Joueur'].values:
    st.toast("⚠️ Mode Démo activé (Fichier CSV introuvable)", icon="ℹ️")

# ============================================================================
# 3. INTERFACE PRINCIPALE
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 2.2rem;">⚽ RakoStats Pro</h1>
    <p style="margin:0; opacity: 0.7;">Advanced Football Scouting & Performance Analytics</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "👥 Player Database", "⭐ Shortlist", "📈 Pro Analytics"])

# ----------------------------------------------------------------------------
# TAB 1: DASHBOARD
# ----------------------------------------------------------------------------
with tab1:
    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f'<div class="stat-card"><h3>{len(df_raw)}</h3><p>Total Players</p></div>', unsafe_allow_html=True)
    with kpi2:
        val_m = df_raw['Valeur marchande'].sum() / 1e9
        st.markdown(f'<div class="stat-card"><h3>€{val_m:.2f}B</h3><p>Total Market Value</p></div>', unsafe_allow_html=True)
    with kpi3:
        avg_age = df_raw['Âge'].mean()
        st.markdown(f'<div class="stat-card"><h3>{avg_age:.1f}</h3><p>Avg Age</p></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="stat-card"><h3>{len(st.session_state.shortlist)}</h3><p>Shortlisted</p></div>', unsafe_allow_html=True)

    st.markdown("### 🔥 Top Performers")
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        # Scatter Plot Interactif
        st.subheader("Efficiency: Goals vs xG")
        fig_scatter = px.scatter(
            df_raw[df_raw['Buts'] > 5],
            x='Buts attendus (xG)', y='Buts',
            size='Valeur marchande', color='Position',
            hover_name='Joueur', hover_data=['Équipe'],
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_scatter.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.05)',
            height=400
        )
        fig_scatter.add_shape(type="line", x0=0, y0=0, x1=30, y1=30, line=dict(color="gray", dash="dash"))
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_top2:
        st.subheader("Most Valuable Players")
        top_val = df_raw.nlargest(5, 'Valeur marchande')[['Joueur', 'Équipe', 'Valeur marchande', 'Position']]
        for _, row in top_val.iterrows():
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px; background:rgba(255,255,255,0.05); margin-bottom:8px; border-radius:8px;">
                <div>
                    <div style="font-weight:bold;">{row['Joueur']}</div>
                    <div style="font-size:0.8em; color:#94a3b8;">{row['Équipe']} • {row['Position']}</div>
                </div>
                <div style="color:#10b981; font-weight:bold;">€{row['Valeur marchande']/1e6:.1f}M</div>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# TAB 2: DATABASE (OPTIMISÉE AVEC PAGINATION)
# ----------------------------------------------------------------------------
with tab2:
    # Filtres
    with st.expander("🔎 Advanced Filters", expanded=True):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        search = c1.text_input("Search Player", placeholder="Mbappé, Haaland...")
        pos_filter = c2.selectbox("Position", ["All"] + sorted(df_raw['Position'].unique().tolist()))
        comp_filter = c3.selectbox("League", ["All"] + sorted(df_raw['Compétition'].unique().tolist()))
        age_range = c4.slider("Age", int(df_raw['Âge'].min()), int(df_raw['Âge'].max()), (16, 40))

    # Application des filtres
    df_filtered = df_raw.copy()
    if search:
        df_filtered = df_filtered[df_filtered['Joueur'].str.contains(search, case=False, na=False)]
    if pos_filter != "All":
        df_filtered = df_filtered[df_filtered['Position'] == pos_filter]
    if comp_filter != "All":
        df_filtered = df_filtered[df_filtered['Compétition'] == comp_filter]
    df_filtered = df_filtered[(df_filtered['Âge'] >= age_range[0]) & (df_filtered['Âge'] <= age_range[1])]

    # Pagination Logic
    ITEMS_PER_PAGE = 12
    if 'total_pages' not in st.session_state: st.session_state.total_pages = 1
    
    st.session_state.total_pages = max(1, len(df_filtered) // ITEMS_PER_PAGE + (1 if len(df_filtered) % ITEMS_PER_PAGE > 0 else 0))
    
    # Contrôles de pagination
    col_res, col_pag = st.columns([2, 2])
    with col_res:
        st.caption(f"Showing {len(df_filtered)} players found")
    with col_pag:
        c_prev, c_page, c_next = st.columns([1, 2, 1])
        if c_prev.button("⬅️", key="prev"):
            st.session_state.page_number = max(0, st.session_state.page_number - 1)
        c_page.markdown(f"<div style='text-align:center; padding-top:5px;'>Page {st.session_state.page_number + 1} / {st.session_state.total_pages}</div>", unsafe_allow_html=True)
        if c_next.button("➡️", key="next"):
            st.session_state.page_number = min(st.session_state.total_pages - 1, st.session_state.page_number + 1)

    # Slice Dataframe
    start_idx = st.session_state.page_number * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_data = df_filtered.iloc[start_idx:end_idx]

    # Grid Display
    rows = st.columns(3)
    for idx, (i, player) in enumerate(page_data.iterrows()):
        with rows[idx % 3]:
            in_shortlist = player['Joueur'] in st.session_state.shortlist
            btn_label = "❌ Remove" if in_shortlist else "⭐ Add to List"
            btn_type = "secondary" if in_shortlist else "primary"
            
            st.markdown(f"""
            <div class="player-card-grid">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <div style="font-weight:bold; font-size:1.1rem;">{player['Joueur']}</div>
                    <div style="background:#3b82f6; padding:2px 8px; border-radius:4px; font-size:0.7rem;">{player['Position']}</div>
                </div>
                <div style="color:#94a3b8; font-size:0.9rem; margin-bottom:10px;">{player['Équipe']}</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:15px; font-size:0.9rem;">
                    <div>⚽ <b>{int(player['Buts'])}</b> Goals</div>
                    <div>🎯 <b>{int(player['Passes décisives'])}</b> Ast</div>
                    <div>⏱ <b>{int(player['Minutes jouées'])}</b> Min</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(btn_label, key=f"btn_{player['Joueur']}", type=btn_type, use_container_width=True):
                if in_shortlist:
                    st.session_state.shortlist.remove(player['Joueur'])
                    st.toast(f"{player['Joueur']} removed!", icon="🗑️")
                else:
                    st.session_state.shortlist.append(player['Joueur'])
                    st.toast(f"{player['Joueur']} added!", icon="✅")
                st.rerun()

# ----------------------------------------------------------------------------
# TAB 3: SHORTLIST
# ----------------------------------------------------------------------------
with tab3:
    if not st.session_state.shortlist:
        st.info("Your shortlist is empty. Go to the Database to scout players!")
    else:
        sl_df = df_raw[df_raw['Joueur'].isin(st.session_state.shortlist)]
        
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f"### ⭐ My Targets ({len(sl_df)})")
        with c2:
            csv = sl_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export CSV", csv, "scouting_list.csv", "text/csv", use_container_width=True)

        st.dataframe(
            sl_df[['Joueur', 'Équipe', 'Position', 'Age', 'Buts', 'Passes décisives', 'Valeur marchande']],
            use_container_width=True,
            hide_index=True
        )

# ----------------------------------------------------------------------------
# TAB 4: PRO ANALYTICS (PERCENTILES & RADARS)
# ----------------------------------------------------------------------------
with tab4:
    st.markdown("### 📈 Deep Dive Comparison (Per 90 Norm)")
    
    # Data Prep pour Analytics (Filtrer joueurs < 500 min pour éviter les biais)
    df_an = df_raw[df_raw['Minutes jouées'] > 450].copy()
    
    # Création stats Per 90
    metrics = ['Buts', 'Passes décisives', 'Buts attendus (xG)', 'Passes décisives attendues (xAG)']
    radar_cols = []
    for m in metrics:
        new_col = f"{m}/90"
        df_an[new_col] = (df_an[m] / df_an['Minutes jouées']) * 90
        radar_cols.append(new_col)
    
    radar_cols.append('Valeur marchande') # On garde la valeur brute

    # Selecteurs
    c1, c2 = st.columns(2)
    with c1:
        p1 = st.selectbox("Player 1 (Blue)", sorted(df_an['Joueur'].unique()), index=0)
    with c2:
        # Essayer de trouver un joueur de la même position par défaut
        p1_pos = df_an[df_an['Joueur'] == p1]['Position'].iloc[0]
        peers = df_an[df_an['Position'] == p1_pos]['Joueur'].tolist()
        def_idx = 1 if len(peers) > 1 else 0
        p2 = st.selectbox("Player 2 (Purple)", sorted(df_an['Joueur'].unique()), index=0)

    if p1 and p2:
        def get_percentile(player, metric, position):
            # Comparer uniquement avec les joueurs du MEME POSTE
            cohort = df_an[df_an['Position'] == position]
            score = df_an[df_an['Joueur'] == player][metric].values[0]
            return stats.percentileofscore(cohort[metric], score), score

        # Calcul des données Radar
        vals_p1, vals_p2 = [], []
        pct_p1, pct_p2 = [], []
        
        pos1 = df_an[df_an['Joueur'] == p1]['Position'].values[0]
        pos2 = df_an[df_an['Joueur'] == p2]['Position'].values[0]

        for m in radar_cols:
            p_score1, raw1 = get_percentile(p1, m, pos1)
            p_score2, raw2 = get_percentile(p2, m, pos2)
            pct_p1.append(p_score1)
            pct_p2.append(p_score2)
            vals_p1.append(raw1)
            vals_p2.append(raw2)

        # Plot Radar
        col_graph, col_stats = st.columns([1.5, 1])
        
        with col_graph:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=pct_p1, theta=['Goals/90', 'Assists/90', 'xG/90', 'xAG/90', 'Value'], 
                                          fill='toself', name=p1, fillcolor='rgba(59, 130, 246, 0.4)', line_color='#3b82f6'))
            fig.add_trace(go.Scatterpolar(r=pct_p2, theta=['Goals/90', 'Assists/90', 'xG/90', 'xAG/90', 'Value'], 
                                          fill='toself', name=p2, fillcolor='rgba(139, 92, 246, 0.4)', line_color='#8b5cf6'))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False), bgcolor='rgba(0,0,0,0)'),
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", y=-0.1),
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Scale: 0-100 Percentile Rank among {pos1}s (P1) and {pos2}s (P2).")

        with col_stats:
            # Similarity Calculation
            dist = np.linalg.norm(np.array(pct_p1) - np.array(pct_p2))
            sim_score = max(0, 100 - dist)
            
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; text-align:center; margin-bottom:20px;">
                <div style="color:#94a3b8; font-size:0.8rem;">Similarity Score</div>
                <div style="font-size:2rem; font-weight:800; color:{'#10b981' if sim_score > 70 else '#f59e0b'}">
                    {sim_score:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Data Table
            comp_df = pd.DataFrame({
                'Metric': ['Goals/90', 'Assists/90', 'xG/90', 'xAG/90', 'Value'],
                p1: [f"{v:.2f}" if m != 'Valeur marchande' else f"{v/1e6:.1f}M" for v, m in zip(vals_p1, radar_cols)],
                p2: [f"{v:.2f}" if m != 'Valeur marchande' else f"{v/1e6:.1f}M" for v, m in zip(vals_p2, radar_cols)]
            })
            st.dataframe(comp_df, hide_index=True, use_container_width=True)
