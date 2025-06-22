import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration de la page avec thème football premium
st.set_page_config(
    page_title="⚽ Football Analytics Pro",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un look football premium
st.markdown("""
<style>
    /* Import Google Fonts pour un look plus pro */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    .main {
        background: linear-gradient(135deg, #0a1426 0%, #1a2642 50%, #0f1419 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a1426 0%, #1a2642 30%, #0f3460 60%, #0a1426 100%);
    }
    
    /* Header style football */
    .football-header {
        background: linear-gradient(135deg, #00c851 0%, #007e33 50%, #004d20 100%);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        border: 3px solid #fff;
        box-shadow: 0 15px 35px rgba(0, 200, 81, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .football-header::before {
        content: '⚽';
        position: absolute;
        top: -20px;
        right: -20px;
        font-size: 120px;
        opacity: 0.1;
        transform: rotate(15deg);
    }
    
    .football-header h1 {
        color: white;
        margin: 0;
        font-size: 3.5em;
        font-weight: 900;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        font-family: 'Inter', sans-serif;
    }
    
    .football-header p {
        color: #e8f5e8;
        margin: 15px 0 0 0;
        font-size: 1.3em;
        font-weight: 500;
    }
    
    /* Sidebar football style */
    .sidebar-header {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        border: 2px solid #00c851;
        box-shadow: 0 8px 25px rgba(0, 200, 81, 0.2);
    }
    
    .sidebar-header h2 {
        color: #00c851;
        text-align: center;
        margin: 0;
        font-size: 1.8em;
        font-weight: 700;
    }
    
    /* Tabs style football */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #1a2642 0%, #2d3748 100%);
        border-radius: 15px;
        padding: 5px;
        border: 2px solid #00c851;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #ffffff;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1em;
        padding: 15px 25px;
        margin: 0 5px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(0, 200, 81, 0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00c851 0%, #007e33 100%);
        color: #ffffff !important;
        box-shadow: 0 5px 15px rgba(0, 200, 81, 0.4);
        transform: translateY(-2px);
    }
    
    /* Métriques style football */
    .stMetric {
        background: linear-gradient(135deg, #1a2642 0%, #2d3748 100%);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #00c851;
        box-shadow: 0 8px 25px rgba(0, 200, 81, 0.15);
        transition: transform 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 200, 81, 0.25);
    }
    
    .stMetric label {
        color: #00c851 !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.8em !important;
    }
    
    /* Player profile card */
    .player-profile {
        background: linear-gradient(135deg, #1a2642 0%, #2d3748 100%);
        padding: 30px;
        border-radius: 20px;
        margin: 25px 0;
        border: 3px solid #00c851;
        box-shadow: 0 15px 35px rgba(0, 200, 81, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .player-profile::before {
        content: '🏆';
        position: absolute;
        top: -15px;
        right: -15px;
        font-size: 100px;
        opacity: 0.1;
    }
    
    .player-profile h2 {
        color: #00c851;
        text-align: center;
        margin-bottom: 25px;
        font-size: 2.2em;
        font-weight: 800;
    }
    
    /* Section headers style football */
    .section-header {
        background: linear-gradient(135deg, #00c851 0%, #007e33 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        margin: 25px 0 15px 0;
        font-weight: 700;
        font-size: 1.4em;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 200, 81, 0.3);
        border: 2px solid #fff;
    }
    
    /* Selectbox football style */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #1a2642 0%, #2d3748 100%);
        border: 2px solid #00c851;
        border-radius: 10px;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #00ff66;
        box-shadow: 0 0 20px rgba(0, 200, 81, 0.3);
    }
    
    /* Radio buttons football style */
    .stRadio > div {
        background: linear-gradient(135deg, #1a2642 0%, #2d3748 100%);
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #00c851;
    }
    
    /* Slider football style */
    .stSlider > div > div > div {
        background: linear-gradient(135deg, #1a2642 0%, #2d3748 100%);
        border-radius: 10px;
        padding: 15px;
        border: 2px solid #00c851;
    }
    
    /* Info boxes style football */
    .info-card {
        background: linear-gradient(135deg, #004d20 0%, #007e33 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        border: 2px solid #00c851;
        box-shadow: 0 8px 20px rgba(0, 200, 81, 0.2);
    }
    
    /* Footer style football */
    .football-footer {
        background: linear-gradient(135deg, #1a2642 0%, #2d3748 100%);
        padding: 25px;
        border-radius: 15px;
        margin-top: 30px;
        border: 2px solid #00c851;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 200, 81, 0.15);
    }
    
    /* Animation pour les éléments interactifs */
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(0, 200, 81, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 200, 81, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 200, 81, 0); }
    }
    
    .pulse-animation {
        animation: pulse-green 2s infinite;
    }
    
    /* Couleurs des graphiques adaptées au football */
    .plotly-graph-div {
        border-radius: 15px;
        border: 2px solid rgba(0, 200, 81, 0.3);
        box-shadow: 0 8px 20px rgba(0, 200, 81, 0.1);
    }
    
    /* Style pour les warnings et erreurs */
    .stAlert {
        border-radius: 12px;
        border: 2px solid;
    }
    
    .stSuccess {
        border-color: #00c851;
        background: linear-gradient(135deg, rgba(0, 200, 81, 0.1) 0%, rgba(0, 126, 51, 0.1) 100%);
    }
    
    .stWarning {
        border-color: #ffa500;
        background: linear-gradient(135deg, rgba(255, 165, 0, 0.1) 0%, rgba(255, 140, 0, 0.1) 100%);
    }
    
    .stError {
        border-color: #ff4444;
        background: linear-gradient(135deg, rgba(255, 68, 68, 0.1) 0%, rgba(220, 20, 60, 0.1) 100%);
    }
</style>
""", unsafe_allow_html=True)

# Couleurs thème football professionnel
FOOTBALL_COLORS = {
    'primary': '#00c851',      # Vert gazon
    'secondary': '#007e33',    # Vert foncé
    'accent': '#00ff66',       # Vert électrique
    'success': '#28a745',      # Vert succès
    'warning': '#ffc107',      # Jaune carton
    'danger': '#dc3545',       # Rouge carton
    'dark': '#1a2642',         # Bleu nuit
    'light': '#f8f9fa',        # Blanc
    'gradient': ['#00c851', '#007e33', '#004d20', '#28a745', '#ffc107']
}

# ---------------------- PARAMÈTRES DU RADAR ----------------------

RAW_STATS = {
    "Buts\nsans pénalty": "Buts (sans penalty)",
    "Passes déc.": "Passes décisives",
    "Buts +\nPasses déc.": "Buts + Passes D",
    "Cartons\njaunes": "Cartons jaunes",
    "Cartons\nrouges": "Cartons rouges",
    "Passes\ntentées": "Passes tentées",
    "Passes\nclés": "Passes clés",
    "Passes\nprogressives": "Passes progressives",
    "Passes\ndernier 1/3": "Passes dans le dernier tiers",
    "Passes\ndans la surface": "Passes dans la surface",
    "Touches": "Touches de balle",
    "Dribbles\ntentés": "Dribbles tentés",
    "Dribbles\nréussis": "Dribbles réussis",
    "Ballons perdus\nsous pression": "Ballons perdus sous la pression d'un adversaire",
    "Ballons perdus\nen conduite": "Ballons perdus en conduite",
    "Tacles\ngagnants": "Tacles gagnants",
    "Tirs\nbloqués": "Tirs bloqués",
    "Duels\ngagnés": "Duels défensifs gagnés",
    "Interceptions": "Interceptions",
    "Dégagements": "Dégagements"
}

COLOR_1 = FOOTBALL_COLORS['primary']
COLOR_2 = FOOTBALL_COLORS['secondary']
SLICE_COLORS = [FOOTBALL_COLORS['accent']] * len(RAW_STATS)

def calculate_percentiles(player_name, df):
    """Calcule les percentiles pour le pizza chart"""
    player = df[df["Joueur"] == player_name].iloc[0]
    percentiles = []

    for label, col in RAW_STATS.items():
        try:
            if col not in df.columns or pd.isna(player[col]):
                percentile = 0
            elif "par 90 minutes" in col or "%" in col:
                val = player[col]
                dist = df[col]
                if pd.isna(val) or dist.dropna().empty:
                    percentile = 0
                else:
                    percentile = round((dist < val).mean() * 100)
            else:
                if player.get("Matchs en 90 min", 0) == 0:
                    matches = player.get("Matchs joués", 1)
                    if matches == 0:
                        percentile = 0
                    else:
                        val = player[col] / matches
                        dist = df[col] / df.get("Matchs joués", 1)
                        if pd.isna(val) or dist.dropna().empty:
                            percentile = 0
                        else:
                            percentile = round((dist < val).mean() * 100)
                else:
                    val = player[col] / player["Matchs en 90 min"]
                    dist = df[col] / df["Matchs en 90 min"]
                    if pd.isna(val) or dist.dropna().empty:
                        percentile = 0
                    else:
                        percentile = round((dist < val).mean() * 100)
        except Exception as e:
            percentile = 0
        percentiles.append(percentile)

    return percentiles

@st.cache_data
def load_data():
    """Charge les données depuis le fichier CSV"""
    try:
        df = pd.read_csv('df_BIG2025.csv', encoding='utf-8')
        return df
    except FileNotFoundError:
        st.error("Fichier 'df_BIG2025.csv' non trouvé. Veuillez vous assurer que le fichier est dans le même répertoire.")
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

# Chargement des données
df = load_data()

if df is not None:
    # Header avec design football premium
    st.markdown("""
    <div class='football-header'>
        <h1>🏆 Football Analytics Pro Dashboard</h1>
        <p>🚀 Analyse avancée des performances footballistiques - Saison 2024-25</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar avec design football
    with st.sidebar:
        st.markdown("""
        <div class='sidebar-header'>
            <h2>🎯 Centre de Contrôle</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection de la compétition/ligue
        competitions = sorted(df['Compétition'].dropna().unique())
        selected_competition = st.selectbox(
            "🏆 Compétition / Championnat :",
            competitions,
            index=0,
            help="Sélectionnez le championnat à analyser"
        )
        
        # Filtrer les joueurs selon la compétition
        df_filtered = df[df['Compétition'] == selected_competition]
        
        # Filtre par minutes jouées
        min_minutes = int(df_filtered['Minutes jouées'].min()) if not df_filtered['Minutes jouées'].empty else 0
        max_minutes = int(df_filtered['Minutes jouées'].max()) if not df_filtered['Minutes jouées'].empty else 3000
        
        st.markdown("---")
        st.markdown("**⏱️ Filtre Performance :**")
        
        # Slider pour sélectionner le minimum de minutes
        min_minutes_filter = st.slider(
            "Minutes minimum de jeu :",
            min_value=min_minutes,
            max_value=max_minutes,
            value=min_minutes,
            step=90,
            help="Filtrer les joueurs par temps de jeu minimum"
        )
        
        # Filtrer les joueurs selon les minutes jouées
        df_filtered_minutes = df_filtered[df_filtered['Minutes jouées'] >= min_minutes_filter]
        
        # Afficher le nombre de joueurs après filtrage avec style
        nb_joueurs = len(df_filtered_minutes)
        st.markdown(f"""
        <div class='info-card'>
            <strong>📊 {nb_joueurs} joueurs</strong><br>
            correspondent aux critères
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sélection du joueur (maintenant filtré par minutes)
        if not df_filtered_minutes.empty:
            joueurs = sorted(df_filtered_minutes['Joueur'].dropna().unique())
            selected_player = st.selectbox(
                "⭐ Sélection du joueur :",
                joueurs,
                index=0,
                help="Choisissez le joueur à analyser"
            )
        else:
            st.error("❌ Aucun joueur ne correspond aux critères sélectionnés.")
            selected_player = None
        
        # Informations additionnelles dans la sidebar
        if selected_player:
            st.markdown("---")
            st.markdown("**🎖️ Infos Rapides :**")
            player_quick_info = df_filtered_minutes[df_filtered_minutes['Joueur'] == selected_player].iloc[0]
            st.info(f"🏃‍♂️ **{player_quick_info['Position']}** dans l'équipe **{player_quick_info['Équipe']}**")
    
    # Obtenir les données du joueur sélectionné
    if selected_player:
        player_data = df_filtered_minutes[df_filtered_minutes['Joueur'] == selected_player].iloc[0]
        
        # Utiliser df_filtered_minutes pour les comparaisons et calculs
        df_comparison = df_filtered_minutes  # Utiliser les données filtrées par minutes
    
        # Affichage des informations générales du joueur avec design football
        st.markdown(f"""
        <div class='player-profile'>
            <h2>⚽ Fiche Joueur : {selected_player}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🎂 Âge", f"{player_data['Âge']} ans")
        with col2:
            st.metric("⚽ Position", player_data['Position'])
        with col3:
            st.metric("🏟️ Équipe", player_data['Équipe'])
        with col4:
            st.metric("🌍 Nationalité", player_data['Nationalité'])
        with col5:
            st.metric("⏱️ Minutes", f"{int(player_data['Minutes jouées'])} min")
        
        st.markdown("---")
    
        # Onglets principaux avec design football
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Performance Offensive", 
            "🛡️ Performance Défensive", 
            "🎨 Performance Technique", 
            "🔄 Comparer Joueurs"
        ])
        
        with tab1:
            st.markdown("<div class='section-header'>🎯 Analyse Offensive Complète</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions offensives
                actions_off = {
                    'Buts': player_data['Buts'],
                    'Passes décisives': player_data['Passes décisives'],
                    'Passes clés': player_data['Passes clés'],
                    'Actions → Tir': player_data.get('Actions menant à un tir', 0),
                    'Tirs': player_data.get('Tirs', 0)
                }
                
                fig_bar_off = go.Figure(data=[go.Bar(
                    x=list(actions_off.keys()),
                    y=list(actions_off.values()),
                    marker=dict(
                        color=FOOTBALL_COLORS['gradient'],
                        line=dict(color='white', width=2)
                    ),
                    text=list(actions_off.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Inter')
                )])
                
                fig_bar_off.update_layout(
                    title=dict(
                        text="⚽ Actions Offensives Totales",
                        font=dict(size=18, color='white', family='Inter'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', size=12),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', size=12),
                        gridcolor='rgba(0, 200, 81, 0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 38, 66, 0.5)',
                    font=dict(color='white'),
                    height=450
                )
                st.plotly_chart(fig_bar_off, use_container_width=True)
                
                # Radar professionnel des actions offensives
                st.markdown("<div class='section-header'>🎯 Radar Offensif Elite</div>", unsafe_allow_html=True)
                
                offensive_metrics = {
                    'Buts/90': player_data['Buts par 90 minutes'],
                    'Passes D./90': player_data['Passes décisives par 90 minutes'],
                    'xG/90': player_data['Buts attendus par 90 minutes'],
                    'xA/90': player_data['Passes décisives attendues par 90 minutes'],
                    'Tirs/90': player_data['Tirs par 90 minutes'],
                    'Passes clés/90': player_data['Passes clés'] / (player_data['Minutes jouées'] / 90),
                    'Dribbles réussis/90': player_data['Dribbles réussis'] / (player_data['Minutes jouées'] / 90),
                    'Actions → Tir/90': player_data['Actions menant à un tir par 90 minutes'],
                    'Passes dernier tiers/90': player_data.get('Passes dans le dernier tiers', 0) / (player_data['Minutes jouées'] / 90),
                    'Passes prog./90': player_data.get('Passes progressives', 0) / (player_data['Minutes jouées'] / 90)
                }
                
                # Calculer les percentiles par rapport à la compétition
                percentile_values = []
                avg_values = []
                for metric, value in offensive_metrics.items():
                    if metric.endswith('/90'):
                        # Métriques déjà par 90 minutes
                        if metric == 'Buts/90':
                            distribution = df_comparison['Buts par 90 minutes']
                        elif metric == 'Passes D./90':
                            distribution = df_comparison['Passes décisives par 90 minutes']
                        elif metric == 'xG/90':
                            distribution = df_comparison['Buts attendus par 90 minutes']
                        elif metric == 'xA/90':
                            distribution = df_comparison['Passes décisives attendues par 90 minutes']
                        elif metric == 'Tirs/90':
                            distribution = df_comparison['Tirs par 90 minutes']
                        elif metric == 'Actions → Tir/90':
                            distribution = df_comparison['Actions menant à un tir par 90 minutes']
                        elif metric == 'Passes dernier tiers/90':
                            distribution = df_comparison['Passes dans le dernier tiers'] / (df_comparison['Minutes jouées'] / 90)
                        else:
                            # Calculer pour les autres métriques
                            base_column = metric.replace('/90', '').replace('Passes D.', 'Passes décisives').replace('Passes prog.', 'Passes progressives')
                            distribution = df_comparison[base_column] / (df_comparison['Minutes jouées'] / 90)
                        
                        # Calculer le percentile et la moyenne
                        percentile = (distribution < value).mean() * 100
                        avg_comp = distribution.mean()
                        percentile_values.append(min(percentile, 100))
                        avg_values.append(avg_comp)
                    else:
                        percentile_values.append(50)
                        avg_values.append(0)
                
                # Créer le radar avec thème football
                fig_radar = go.Figure()
                
                # Performance du joueur
                fig_radar.add_trace(go.Scatterpolar(
                    r=percentile_values,
                    theta=list(offensive_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(0, 200, 81, 0.4)',
                    line=dict(color=FOOTBALL_COLORS['primary'], width=4),
                    marker=dict(color=FOOTBALL_COLORS['primary'], size=10, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(offensive_metrics.values())
                ))
                
                # Calculer les percentiles des moyennes
                avg_percentiles = []
                for i, avg_val in enumerate(avg_values):
                    if avg_val > 0:
                        metric_name = list(offensive_metrics.keys())[i]
                        if metric_name == 'Buts/90':
                            distribution = df_comparison['Buts par 90 minutes']
                        elif metric_name == 'Passes D./90':
                            distribution = df_comparison['Passes décisives par 90 minutes']
                        elif metric_name == 'xG/90':
                            distribution = df_comparison['Buts attendus par 90 minutes']
                        elif metric_name == 'xA/90':
                            distribution = df_comparison['Passes décisives attendues par 90 minutes']
                        elif metric_name == 'Tirs/90':
                            distribution = df_comparison['Tirs par 90 minutes']
                        elif metric_name == 'Actions → Tir/90':
                            distribution = df_comparison['Actions menant à un tir par 90 minutes']
                        elif metric_name == 'Passes dernier tiers/90':
                            distribution = df_comparison['Passes dans le dernier tiers'] / (df_comparison['Minutes jouées'] / 90)
                        else:
                            base_column = metric_name.replace('/90', '').replace('Passes D.', 'Passes décisives').replace('Passes prog.', 'Passes progressives')
                            distribution = df_comparison[base_column] / (df_comparison['Minutes jouées'] / 90)
                        
                        avg_percentile = (distribution < avg_val).mean() * 100
                        avg_percentiles.append(avg_percentile)
                    else:
                        avg_percentiles.append(50)
                
                # Moyenne de la compétition
                fig_radar.add_trace(go.Scatterpolar(
                    r=avg_percentiles,
                    theta=list(offensive_metrics.keys()),
                    mode='lines',
                    line=dict(color='rgba(255,255,255,0.8)', width=3, dash='dash'),
                    name=f'Moyenne {selected_competition}',
                    showlegend=True,
                    hovertemplate='<b>%{theta}</b><br>Moyenne ligue: %{customdata:.2f}<extra></extra>',
                    customdata=avg_values
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='rgba(0, 200, 81, 0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=11),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(0, 200, 81, 0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=12, family='Inter'),
                            linecolor='rgba(0, 200, 81, 0.6)'
                        ),
                        bgcolor='rgba(26, 38, 66, 0.8)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    title=dict(
                        text="🚀 Radar Offensif Elite (Percentiles)",
                        font=dict(size=18, color='white', family='Inter'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color='white', size=11)
                    ),
                    height=500
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite offensifs
                pourcentages_off = {
                    'Conversion (Buts/Tirs)': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                    'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                    'Efficacité passes clés': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
                }
                
                # Nettoyer les valeurs NaN
                pourcentages_off = {k: v if pd.notna(v) else 0 for k, v in pourcentages_off.items()}
                
                fig_gauge_off = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_off.keys())
                )
                
                colors_off = [FOOTBALL_COLORS['primary'], FOOTBALL_COLORS['secondary'], FOOTBALL_COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages_off.items()):
                    fig_gauge_off.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_off[i]),
                                bgcolor="rgba(26, 38, 66, 0.6)",
                                borderwidth=3,
                                bordercolor=FOOTBALL_COLORS['primary'],
                                steps=[
                                    {'range': [0, 33], 'color': 'rgba(220, 53, 69, 0.3)'},
                                    {'range': [33, 66], 'color': 'rgba(255, 193, 7, 0.3)'},
                                    {'range': [66, 100], 'color': 'rgba(0, 200, 81, 0.3)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': 'white', 'size': 16}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_off.update_layout(
                    height=350, 
                    title_text="🎯 Efficacité Offensive (%)",
                    title_font_color='white',
                    title_font_size=16,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_gauge_off, use_container_width=True)
                
                # Graphique de comparaison offensive
                offensive_comparison = {
                    'Buts/90': player_data['Buts par 90 minutes'],
                    'Passes D./90': player_data['Passes décisives par 90 minutes'],
                    'xG/90': player_data['Buts attendus par 90 minutes']
                }
                
                # Moyennes de la compétition
                avg_comparison_off = {
                    'Buts/90': df_comparison['Buts par 90 minutes'].mean(),
                    'Passes D./90': df_comparison['Passes décisives par 90 minutes'].mean(),
                    'xG/90': df_comparison['Buts attendus par 90 minutes'].mean()
                }
                
                fig_off_comp = go.Figure()
                
                fig_off_comp.add_trace(go.Bar(
                    name=selected_player,
                    x=list(offensive_comparison.keys()),
                    y=list(offensive_comparison.values()),
                    marker_color=FOOTBALL_COLORS['primary'],
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_off_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison_off.keys()),
                    y=list(avg_comparison_off.values()),
                    marker_color=FOOTBALL_COLORS['secondary'],
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_off_comp.update_layout(
                    title=dict(
                        text='⚽ Performance vs Moyenne Championnat',
                        font=dict(color='white', size=16),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 38, 66, 0.5)',
                    font=dict(color='white'),
                    xaxis=dict(tickfont=dict(color='white', size=12)),
                    yaxis=dict(tickfont=dict(color='white', size=12), gridcolor='rgba(0, 200, 81, 0.3)'),
                    height=450
                )
                
                st.plotly_chart(fig_off_comp, use_container_width=True)
            
            # Scatter plot pour comparaison offensive
            st.markdown("<div class='section-header'>🔍 Analyse Comparative Elite</div>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                # Sélection des métriques pour le scatter plot offensif
                metric_options_off = [
                    'Buts', 'Passes décisives', 'Tirs', 'Buts attendus (xG)',
                    'Passes décisives attendues (xAG)', 'Passes clés', 'Actions menant à un tir',
                    'Pourcentage de tirs cadrés'
                ]
                
                x_metric_off = st.selectbox("📊 Métrique X", metric_options_off, index=0, key="x_off")
                y_metric_off = st.selectbox("📈 Métrique Y", metric_options_off, index=1, key="y_off")
            
            with col_scatter2:
                # Créer le scatter plot offensif
                fig_scatter_off = go.Figure()
                
                # Convertir en par 90 minutes si nécessaire
                if x_metric_off not in ['Pourcentage de tirs cadrés']:
                    x_data = df_comparison[x_metric_off] / (df_comparison['Minutes jouées'] / 90)
                    x_player = player_data[x_metric_off] / (player_data['Minutes jouées'] / 90)
                    x_title = f"{x_metric_off} par 90min"
                else:
                    x_data = df_comparison[x_metric_off]
                    x_player = player_data[x_metric_off]
                    x_title = x_metric_off
                    
                if y_metric_off not in ['Pourcentage de tirs cadrés']:
                    y_data = df_comparison[y_metric_off] / (df_comparison['Minutes jouées'] / 90)
                    y_player = player_data[y_metric_off] / (player_data['Minutes jouées'] / 90)
                    y_title = f"{y_metric_off} par 90min"
                else:
                    y_data = df_comparison[y_metric_off]
                    y_player = player_data[y_metric_off]
                    y_title = y_metric_off
                
                # Tous les joueurs
                fig_scatter_off.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color=FOOTBALL_COLORS['accent'], size=10, opacity=0.6, line=dict(color='white', width=1)),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                # Joueur sélectionné
                fig_scatter_off.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color=FOOTBALL_COLORS['primary'], size=25, symbol='star', line=dict(color='white', width=3)),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_off.update_layout(
                    title=dict(text=f"🎯 {x_title} vs {y_title}", font=dict(size=16, color='white'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color='white')), tickfont=dict(color='white')),
                    yaxis=dict(title=dict(text=y_title, font=dict(color='white')), tickfont=dict(color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 38, 66, 0.5)',
                    font=dict(color='white'),
                    height=450
                )
                
                st.plotly_chart(fig_scatter_off, use_container_width=True)
            
            # Métriques offensives par 90 minutes avec design football
            st.markdown("<div class='section-header'>📊 Statistiques Offensives Elite</div>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("⚽ Buts/90min", f"{player_data['Buts par 90 minutes']:.2f}")
            with col2:
                st.metric("🎯 Passes D./90min", f"{player_data['Passes décisives par 90 minutes']:.2f}")
            with col3:
                st.metric("📈 xG/90min", f"{player_data['Buts attendus par 90 minutes']:.2f}")
            with col4:
                st.metric("🚀 Actions → Tir/90min", f"{player_data['Actions menant à un tir par 90 minutes']:.2f}")
            with col5:
                # Efficacité offensive globale
                efficiency_off = (player_data['Buts'] + player_data['Passes décisives']) / player_data.get('Tirs', 1) * 100 if player_data.get('Tirs', 0) > 0 else 0
                st.metric("🏆 Efficacité Offensive", f"{efficiency_off:.1f}%")
    
        with tab2:
            st.markdown("<div class='section-header'>🛡️ Analyse Défensive Complète</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions défensives
                actions_def = {
                    'Tacles gagnants': player_data['Tacles gagnants'],
                    'Interceptions': player_data['Interceptions'],
                    'Ballons récupérés': player_data['Ballons récupérés'],
                    'Duels aériens gagnés': player_data['Duels aériens gagnés'],
                    'Dégagements': player_data['Dégagements']
                }
                
                fig_bar_def = go.Figure(data=[go.Bar(
                    x=list(actions_def.keys()),
                    y=list(actions_def.values()),
                    marker=dict(
                        color=['#dc3545', '#007e33', '#00c851', '#ffc107', '#6c757d'],
                        line=dict(color='white', width=2)
                    ),
                    text=list(actions_def.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Inter')
                )])
                
                fig_bar_def.update_layout(
                    title=dict(
                        text="🛡️ Actions Défensives Totales",
                        font=dict(size=18, color='white', family='Inter'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', size=12),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', size=12),
                        gridcolor='rgba(220, 53, 69, 0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 38, 66, 0.5)',
                    font=dict(color='white'),
                    height=450
                )
                st.plotly_chart(fig_bar_def, use_container_width=True)
                
                # Radar défensif professionnel
                st.markdown("<div class='section-header'>🛡️ Radar Défensif Elite</div>", unsafe_allow_html=True)
                
                defensive_metrics = {
                    'Tacles/90': player_data['Tacles gagnants'] / (player_data['Minutes jouées'] / 90),
                    'Interceptions/90': player_data['Interceptions'] / (player_data['Minutes jouées'] / 90),
                    'Ballons récupérés/90': player_data['Ballons récupérés'] / (player_data['Minutes jouées'] / 90),
                    'Duels défensifs/90': player_data.get('Duels défensifs gagnés', 0) / (player_data['Minutes jouées'] / 90),
                    'Duels aériens/90': player_data['Duels aériens gagnés'] / (player_data['Minutes jouées'] / 90),
                    'Dégagements/90': player_data['Dégagements'] / (player_data['Minutes jouées'] / 90),
                    'Tirs bloqués/90': player_data.get('Tirs bloqués', 0) / (player_data['Minutes jouées'] / 90),
                    '% Duels gagnés': player_data.get('Pourcentage de duels gagnés', 0),
                    '% Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                    'Total Blocs/90': player_data.get('Total de blocs (tirs et passes)', 0) / (player_data['Minutes jouées'] / 90)
                }
                
                # Calculer les percentiles défensifs
                def_percentile_values = []
                def_avg_values = []
                for metric, value in defensive_metrics.items():
                    try:
                        if metric == 'Tacles/90':
                            distribution = df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Interceptions/90':
                            distribution = df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Ballons récupérés/90':
                            distribution = df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Duels défensifs/90':
                            distribution = df_comparison.get('Duels défensifs gagnés', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Duels aériens/90':
                            distribution = df_comparison['Duels aériens gagnés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Dégagements/90':
                            distribution = df_comparison['Dégagements'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Tirs bloqués/90':
                            distribution = df_comparison.get('Tirs bloqués', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == '% Duels gagnés':
                            distribution = df_comparison.get('Pourcentage de duels gagnés', pd.Series([0]*len(df_comparison)))
                        elif metric == '% Duels aériens':
                            distribution = df_comparison['Pourcentage de duels aériens gagnés']
                        elif metric == 'Total Blocs/90':
                            distribution = df_comparison.get('Total de blocs (tirs et passes)', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        
                        # Nettoyer les valeurs
                        distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                        value = value if not np.isnan(value) and not np.isinf(value) else 0
                        
                        if len(distribution) > 0:
                            percentile = (distribution < value).mean() * 100
                            avg_comp = distribution.mean()
                        else:
                            percentile = 50
                            avg_comp = 0
                        
                        def_percentile_values.append(min(percentile, 100))
                        def_avg_values.append(avg_comp)
                    except:
                        def_percentile_values.append(50)
                        def_avg_values.append(0)
                
                # Créer le radar défensif
                fig_def_radar = go.Figure()
                
                # Performance du joueur
                fig_def_radar.add_trace(go.Scatterpolar(
                    r=def_percentile_values,
                    theta=list(defensive_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(220, 53, 69, 0.4)',
                    line=dict(color='#dc3545', width=4),
                    marker=dict(color='#dc3545', size=10, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(defensive_metrics.values())
                ))
                
                # Calculer les percentiles des moyennes
                def_avg_percentiles = []
                for i, avg_val in enumerate(def_avg_values):
                    try:
                        if avg_val > 0:
                            metric_name = list(defensive_metrics.keys())[i]
                            if metric_name == 'Tacles/90':
                                distribution = df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Interceptions/90':
                                distribution = df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Ballons récupérés/90':
                                distribution = df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Duels défensifs/90':
                                distribution = df_comparison.get('Duels défensifs gagnés', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Duels aériens/90':
                                distribution = df_comparison['Duels aériens gagnés'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Dégagements/90':
                                distribution = df_comparison['Dégagements'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Tirs bloqués/90':
                                distribution = df_comparison.get('Tirs bloqués', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == '% Duels gagnés':
                                distribution = df_comparison.get('Pourcentage de duels gagnés', pd.Series([0]*len(df_comparison)))
                            elif metric_name == '% Duels aériens':
                                distribution = df_comparison['Pourcentage de duels aériens gagnés']
                            elif metric_name == 'Total Blocs/90':
                                distribution = df_comparison.get('Total de blocs (tirs et passes)', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            
                            distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                            if len(distribution) > 0:
                                avg_percentile = (distribution < avg_val).mean() * 100
                                def_avg_percentiles.append(avg_percentile)
                            else:
                                def_avg_percentiles.append(50)
                        else:
                            def_avg_percentiles.append(50)
                    except:
                        def_avg_percentiles.append(50)
                
                # Moyenne de la compétition
                fig_def_radar.add_trace(go.Scatterpolar(
                    r=def_avg_percentiles,
                    theta=list(defensive_metrics.keys()),
                    mode='lines',
                    line=dict(color='rgba(255,255,255,0.8)', width=3, dash='dash'),
                    name=f'Moyenne {selected_competition}',
                    showlegend=True,
                    hovertemplate='<b>%{theta}</b><br>Moyenne ligue: %{customdata:.2f}<extra></extra>',
                    customdata=def_avg_values
                ))
                
                fig_def_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='rgba(220, 53, 69, 0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=11),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(220, 53, 69, 0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=12, family='Inter'),
                            linecolor='rgba(220, 53, 69, 0.6)'
                        ),
                        bgcolor='rgba(26, 38, 66, 0.8)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    title=dict(
                        text="🛡️ Radar Défensif Elite (Percentiles)",
                        font=dict(size=18, color='white', family='Inter'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color='white', size=11)
                    ),
                    height=500
                )
                
                st.plotly_chart(fig_def_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite défensifs
                pourcentages_def = {
                    'Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                    'Duels défensifs': player_data['Pourcentage de duels gagnés'],
                    'Passes réussies': player_data['Pourcentage de passes réussies']
                }
                
                # Nettoyer les valeurs NaN
                pourcentages_def = {k: v if pd.notna(v) else 0 for k, v in pourcentages_def.items()}
                
                fig_gauge_def = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_def.keys())
                )
                
                colors_def = ['#dc3545', '#007e33', '#00c851']
                for i, (metric, value) in enumerate(pourcentages_def.items()):
                    fig_gauge_def.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_def[i]),
                                bgcolor="rgba(26, 38, 66, 0.6)",
                                borderwidth=3,
                                bordercolor='#dc3545',
                                steps=[
                                    {'range': [0, 33], 'color': 'rgba(220, 53, 69, 0.3)'},
                                    {'range': [33, 66], 'color': 'rgba(255, 193, 7, 0.3)'},
                                    {'range': [66, 100], 'color': 'rgba(0, 200, 81, 0.3)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': 'white', 'size': 16}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_def.update_layout(
                    height=350, 
                    title_text="🛡️ Efficacité Défensive (%)",
                    title_font_color='white',
                    title_font_size=16,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_gauge_def, use_container_width=True)
                
                # Graphique de comparaison défensive
                defensive_comparison = {
                    'Tacles/90': player_data['Tacles gagnants'] / (player_data['Minutes jouées'] / 90),
                    'Interceptions/90': player_data['Interceptions'] / (player_data['Minutes jouées'] / 90),
                    'Ballons récupérés/90': player_data['Ballons récupérés'] / (player_data['Minutes jouées'] / 90)
                }
                
                # Moyennes de la compétition
                avg_comparison_def = {
                    'Tacles/90': (df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Interceptions/90': (df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Ballons récupérés/90': (df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)).mean()
                }
                
                fig_def_comp = go.Figure()
                
                fig_def_comp.add_trace(go.Bar(
                    name=selected_player,
                    x=list(defensive_comparison.keys()),
                    y=list(defensive_comparison.values()),
                    marker_color='#dc3545',
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_def_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison_def.keys()),
                    y=list(avg_comparison_def.values()),
                    marker_color='#007e33',
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_def_comp.update_layout(
                    title=dict(
                        text='🛡️ Performance vs Moyenne Championnat',
                        font=dict(color='white', size=16),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 38, 66, 0.5)',
                    font=dict(color='white'),
                    xaxis=dict(tickfont=dict(color='white', size=12)),
                    yaxis=dict(tickfont=dict(color='white', size=12), gridcolor='rgba(220, 53, 69, 0.3)'),
                    height=450
                )
                
                st.plotly_chart(fig_def_comp, use_container_width=True)
            
            # Scatter plot pour comparaison défensive
            st.markdown("<div class='section-header'>🔍 Analyse Comparative Défensive</div>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                # Sélection des métriques pour le scatter plot défensif
                metric_options_def = [
                    'Tacles gagnants', 'Interceptions', 'Ballons récupérés', 
                    'Duels aériens gagnés', 'Dégagements', 'Pourcentage de duels gagnés',
                    'Pourcentage de duels aériens gagnés'
                ]
                
                x_metric_def = st.selectbox("📊 Métrique X", metric_options_def, index=0, key="x_def")
                y_metric_def = st.selectbox("📈 Métrique Y", metric_options_def, index=1, key="y_def")
            
            with col_scatter2:
                # Créer le scatter plot défensif
                fig_scatter_def = go.Figure()
                
                # Convertir en par 90 minutes si nécessaire
                if x_metric_def not in ['Pourcentage de duels gagnés', 'Pourcentage de duels aériens gagnés']:
                    x_data = df_comparison[x_metric_def] / (df_comparison['Minutes jouées'] / 90)
                    x_player = player_data[x_metric_def] / (player_data['Minutes jouées'] / 90)
                    x_title = f"{x_metric_def} par 90min"
                else:
                    x_data = df_comparison[x_metric_def]
                    x_player = player_data[x_metric_def]
                    x_title = x_metric_def
                    
                if y_metric_def not in ['Pourcentage de duels gagnés', 'Pourcentage de duels aériens gagnés']:
                    y_data = df_comparison[y_metric_def] / (df_comparison['Minutes jouées'] / 90)
                    y_player = player_data[y_metric_def] / (player_data['Minutes jouées'] / 90)
                    y_title = f"{y_metric_def} par 90min"
                else:
                    y_data = df_comparison[y_metric_def]
                    y_player = player_data[y_metric_def]
                    y_title = y_metric_def
                
                # Tous les joueurs
                fig_scatter_def.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color='#ffc107', size=10, opacity=0.6, line=dict(color='white', width=1)),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                # Joueur sélectionné
                fig_scatter_def.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color='#dc3545', size=25, symbol='star', line=dict(color='white', width=3)),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_def.update_layout(
                    title=dict(text=f"🛡️ {x_title} vs {y_title}", font=dict(size=16, color='white'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color='white')), tickfont=dict(color='white')),
                    yaxis=dict(title=dict(text=y_title, font=dict(color='white')), tickfont=dict(color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 38, 66, 0.5)',
                    font=dict(color='white'),
                    height=450
                )
                
                st.plotly_chart(fig_scatter_def, use_container_width=True)
            
            # Métriques défensives par 90 minutes
            st.markdown("<div class='section-header'>📊 Statistiques Défensives Elite</div>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Calcul des métriques par 90 minutes
            minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
            
            with col1:
                tacles_90 = player_data['Tacles gagnants'] / minutes_90
                st.metric("⚔️ Tacles/90min", f"{tacles_90:.2f}")
            with col2:
                interceptions_90 = player_data['Interceptions'] / minutes_90
                st.metric("🎯 Interceptions/90min", f"{interceptions_90:.2f}")
            with col3:
                ballons_90 = player_data['Ballons récupérés'] / minutes_90
                st.metric("🔄 Ballons récupérés/90min", f"{ballons_90:.2f}")
            with col4:
                duels_90 = player_data['Duels aériens gagnés'] / minutes_90
                st.metric("🚁 Duels aériens/90min", f"{duels_90:.2f}")
            with col5:
                # Efficacité défensive globale
                defensive_success = (player_data['Pourcentage de duels gagnés'] + player_data['Pourcentage de duels aériens gagnés']) / 2
                st.metric("🏆 Efficacité Défensive", f"{defensive_success:.1f}%")
        
        with tab3:
            st.markdown("<div class='section-header'>🎨 Analyse Technique Complète</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions techniques
                actions_tech = {
                    'Passes tentées': player_data['Passes tentées'],
                    'Passes progressives': player_data.get('Passes progressives', 0),
                    'Dribbles tentés': player_data['Dribbles tentés'],
                    'Touches de balle': player_data['Touches de balle'],
                    'Passes clés': player_data['Passes clés']
                }
                
                fig_bar_tech = go.Figure(data=[go.Bar(
                    x=list(actions_tech.keys()),
                    y=list(actions_tech.values()),
                    marker=dict(
                        color=['#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#17a2b8'],
                        line=dict(color='white', width=2)
                    ),
                    text=list(actions_tech.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Inter')
                )])
                
                fig_bar_tech.update_layout(
                    title=dict(
                        text="🎨 Actions Techniques Totales",
                        font=dict(size=18, color='white', family='Inter'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', size=12),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', size=12),
                        gridcolor='rgba(111, 66, 193, 0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 38, 66, 0.5)',
                    font=dict(color='white'),
                    height=450
                )
                st.plotly_chart(fig_bar_tech, use_container_width=True)
                
                # Radar technique professionnel
                st.markdown("<div class='section-header'>🎨 Radar Technique Elite</div>", unsafe_allow_html=True)
                
                technical_metrics = {
                    'Passes tentées/90': player_data['Passes tentées'] / (player_data['Minutes jouées'] / 90),
                    'Passes prog./90': player_data.get('Passes progressives', 0) / (player_data['Minutes jouées'] / 90),
                    'Dribbles/90': player_data['Dribbles tentés'] / (player_data['Minutes jouées'] / 90),
                    'Touches/90': player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90),
                    'Passes clés/90': player_data['Passes clés'] / (player_data['Minutes jouées'] / 90),
                    '% Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                    '% Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                    'Distance prog./90': player_data.get('Distance progressive des passes', 0) / (player_data['Minutes jouées'] / 90),
                    'Centres/90': player_data.get('Centres réussis', 0) / (player_data['Minutes jouées'] / 90),
                    'Courses prog./90': player_data.get('Courses progressives', 0) / (player_data['Minutes jouées'] / 90)
                }
                
                # Calculer les percentiles techniques
                tech_percentile_values = []
                tech_avg_values = []
                for metric, value in technical_metrics.items():
                    try:
                        if metric == 'Passes tentées/90':
                            distribution = df_comparison['Passes tentées'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Passes prog./90':
                            distribution = df_comparison.get('Passes progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Dribbles/90':
                            distribution = df_comparison['Dribbles tentés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Touches/90':
                            distribution = df_comparison['Touches de balle'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Passes clés/90':
                            distribution = df_comparison['Passes clés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == '% Passes réussies':
                            distribution = df_comparison.get('Pourcentage de passes réussies', pd.Series([0]*len(df_comparison)))
                        elif metric == '% Dribbles réussis':
                            distribution = df_comparison.get('Pourcentage de dribbles réussis', pd.Series([0]*len(df_comparison)))
                        elif metric == 'Distance prog./90':
                            distribution = df_comparison.get('Distance progressive des passes', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Centres/90':
                            distribution = df_comparison.get('Centres réussis', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Courses prog./90':
                            distribution = df_comparison.get('Courses progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        
                        # Nettoyer les valeurs
                        distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                        value = value if not np.isnan(value) and not np.isinf(value) else 0
                        
                        if len(distribution) > 0:
                            percentile = (distribution < value).mean() * 100
                            avg_comp = distribution.mean()
                        else:
                            percentile = 50
                            avg_comp = 0
                        
                        tech_percentile_values.append(min(percentile, 100))
                        tech_avg_values.append(avg_comp)
                    except:
                        tech_percentile_values.append(50)
                        tech_avg_values.append(0)
                
                # Créer le radar technique
                fig_tech_radar = go.Figure()
                
                # Performance du joueur
                fig_tech_radar.add_trace(go.Scatterpolar(
                    r=tech_percentile_values,
                    theta=list(technical_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(111, 66, 193, 0.4)',
                    line=dict(color='#6f42c1', width=4),
                    marker=dict(color='#6f42c1', size=10, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(technical_metrics.values())
                ))
                
                # Calculer les percentiles des moyennes
                tech_avg_percentiles = []
                for i, avg_val in enumerate(tech_avg_values):
                    try:
                        if avg_val > 0:
                            metric_name = list(technical_metrics.keys())[i]
                            if metric_name == 'Passes tentées/90':
                                distribution = df_comparison['Passes tentées'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Passes prog./90':
                                distribution = df_comparison.get('Passes progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Dribbles/90':
                                distribution = df_comparison['Dribbles tentés'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Touches/90':
                                distribution = df_comparison['Touches de balle'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Passes clés/90':
                                distribution = df_comparison['Passes clés'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == '% Passes réussies':
                                distribution = df_comparison.get('Pourcentage de passes réussies', pd.Series([0]*len(df_comparison)))
                            elif metric_name == '% Dribbles réussis':
                                distribution = df_comparison.get('Pourcentage de dribbles réussis', pd.Series([0]*len(df_comparison)))
                            elif metric_name == 'Distance prog./90':
                                distribution = df_comparison.get('Distance progressive des passes', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Centres/90':
                                distribution = df_comparison.get('Centres réussis', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Courses prog./90':
                                distribution = df_comparison.get('Courses progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            
                            distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                            if len(distribution) > 0:
                                avg_percentile = (distribution < avg_val).mean() * 100
                                tech_avg_percentiles.append(avg_percentile)
                            else:
                                tech_avg_percentiles.append(50)
                        else:
                            tech_avg_percentiles.append(50)
                    except:
                        tech_avg_percentiles.append(50)
                
                # Moyenne de la compétition
                fig_tech_radar.add_trace(go.Scatterpolar(
                    r=tech_avg_percentiles,
                    theta=list(technical_metrics.keys()),
                    mode='lines',
                    line=dict(color='rgba(255,255,255,0.8)', width=3, dash='dash'),
                    name=f'Moyenne {selected_competition}',
                    showlegend=True,
                    hovertemplate='<b>%{theta}</b><br>Moyenne ligue: %{customdata:.2f}<extra></extra>',
                    customdata=tech_avg_values
                ))
                
                fig_tech_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='rgba(111, 66, 193, 0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=11),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(111, 66, 193, 0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=12, family='Inter'),
                            linecolor='rgba(111, 66, 193, 0.6)'
                        ),
                        bgcolor='rgba(26, 38, 66, 0.8)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    title=dict(
                        text="🎨 Radar Technique Elite (Percentiles)",
                        font=dict(size=18, color='white', family='Inter'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color='white', size=11)
                    ),
                    height=500
                )
                
                st.plotly_chart(fig_tech_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite techniques
                pourcentages_tech = {
                    'Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                    'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                    'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
                }
                
                # Nettoyer les valeurs NaN
                pourcentages_tech = {k: v if pd.notna(v) else 0 for k, v in pourcentages_tech.items()}
                
                fig_gauge_tech = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_tech.keys())
                )
                
                colors_tech = ['#28a745', '#ffc107', '#6f42c1']
                for i, (metric, value) in enumerate(pourcentages_tech.items()):
                    fig_gauge_tech.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_tech[i]),
                                bgcolor="rgba(26, 38, 66, 0.6)",
                                borderwidth=3,
                                bordercolor='#6f42c1',
                                steps=[
                                    {'range': [0, 33], 'color': 'rgba(220, 53, 69, 0.3)'},
                                    {'range': [33, 66], 'color': 'rgba(255, 193, 7, 0.3)'},
                                    {'range': [66, 100], 'color': 'rgba(40, 167, 69, 0.3)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': 'white', 'size': 16}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_tech.update_layout(
                    height=350, 
                    title_text="🎨 Précision Technique (%)",
                    title_font_color='white',
                    title_font_size=16,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_gauge_tech, use_container_width=True)
                
                # Graphique de comparaison technique
                technical_comparison = {
                    'Passes/90': player_data['Passes tentées'] / (player_data['Minutes jouées'] / 90),
                    'Dribbles/90': player_data['Dribbles tentés'] / (player_data['Minutes jouées'] / 90),
                    'Touches/90': player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90)
                }
                
                # Moyennes de la compétition
                avg_comparison_tech = {
                    'Passes/90': (df_comparison['Passes tentées'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Dribbles/90': (df_comparison['Dribbles tentés'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Touches/90': (df_comparison['Touches de balle'] / (df_comparison['Minutes jouées'] / 90)).mean()
                }
                
                fig_tech_comp = go.Figure()
                
                fig_tech_comp.add_trace(go.Bar(
                    name=selected_player,
                    x=list(technical_comparison.keys()),
                    y=list(technical_comparison.values()),
                    marker_color='#6f42c1',
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_tech_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison_tech.keys()),
                    y=list(avg_comparison_tech.values()),
                    marker_color='#e83e8c',
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_tech_comp.update_layout(
                    title=dict(
                        text='🎨 Performance vs Moyenne Championnat',
                        font=dict(color='white', size=16),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 38, 66, 0.5)',
                    font=dict(color='white'),
                    xaxis=dict(tickfont=dict(color='white', size=12)),
                    yaxis=dict(tickfont=dict(color='white', size=12), gridcolor='rgba(111, 66, 193, 0.3)'),
                    height=450
                )
                
                st.plotly_chart(fig_tech_comp, use_container_width=True)
            
            # Scatter plot pour comparaison technique
            st.markdown("<div class='section-header'>🔍 Analyse Comparative Technique</div>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                # Sélection des métriques pour le scatter plot technique
                metric_options_tech = [
                    'Passes tentées', 'Pourcentage de passes réussies', 'Passes progressives',
                    'Passes clés', 'Dribbles tentés', 'Pourcentage de dribbles réussis',
                    'Touches de balle', 'Distance progressive des passes'
                ]
                
                x_metric_tech = st.selectbox("📊 Métrique X", metric_options_tech, index=0, key="x_tech")
                y_metric_tech = st.selectbox("📈 Métrique Y", metric_options_tech, index=1, key="y_tech")
            
            with col_scatter2:
                # Créer le scatter plot technique
                fig_scatter_tech = go.Figure()
                
                # Convertir en par 90 minutes si nécessaire pour les métriques non-pourcentage
                if 'Pourcentage' not in x_metric_tech:
                    x_data = df_comparison[x_metric_tech] / (df_comparison['Minutes jouées'] / 90)
                    x_player = player_data[x_metric_tech] / (player_data['Minutes jouées'] / 90)
                    x_title = f"{x_metric_tech} par 90min"
                else:
                    x_data = df_comparison[x_metric_tech]
                    x_player = player_data[x_metric_tech]
                    x_title = x_metric_tech
                    
                if 'Pourcentage' not in y_metric_tech:
                    y_data = df_comparison[y_metric_tech] / (df_comparison['Minutes jouées'] / 90)
                    y_player = player_data[y_metric_tech] / (player_data['Minutes jouées'] / 90)
                    y_title = f"{y_metric_tech} par 90min"
                else:
                    y_data = df_comparison[y_metric_tech]
                    y_player = player_data[y_metric_tech]
                    y_title = y_metric_tech
                
                # Tous les joueurs
                fig_scatter_tech.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color='#17a2b8', size=10, opacity=0.6, line=dict(color='white', width=1)),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                # Joueur sélectionné
                fig_scatter_tech.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color='#6f42c1', size=25, symbol='star', line=dict(color='white', width=3)),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_tech.update_layout(
                    title=dict(text=f"🎨 {x_title} vs {y_title}", font=dict(size=16, color='white'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color='white')), tickfont=dict(color='white')),
                    yaxis=dict(title=dict(text=y_title, font=dict(color='white')), tickfont=dict(color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26, 38, 66, 0.5)',
                    font=dict(color='white'),
                    height=450
                )
                
                st.plotly_chart(fig_scatter_tech, use_container_width=True)
            
            # Métriques techniques détaillées
            st.markdown("<div class='section-header'>📊 Statistiques Techniques Elite</div>", unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("📏 Distance passes", f"{player_data.get('Distance totale des passes', 0):.0f}m")
                st.metric("🚀 Distance progressive", f"{player_data.get('Distance progressive des passes', 0):.0f}m")
            
            with col2:
                st.metric("⚽ Passes tentées", f"{player_data.get('Passes tentées', 0):.0f}")
                st.metric("✅ % Réussite passes", f"{player_data.get('Pourcentage de passes réussies', 0):.1f}%")
            
            with col3:
                touches_90 = player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90)
                st.metric("🎯 Touches/90min", f"{touches_90:.1f}")
                st.metric("🔑 Passes clés", f"{player_data.get('Passes clés', 0):.0f}")
            
            with col4:
                distance_portee = player_data.get('Distance totale parcourue avec le ballon (en mètres)', 0)
                st.metric("🏃‍♂️ Distance portée", f"{distance_portee:.0f}m")
                st.metric("📡 Centres dans surface", f"{player_data.get('Centres dans la surface', 0):.0f}")
            
            with col5:
                # Précision technique globale
                passes_critiques = (player_data.get('Pourcentage de passes longues réussies', 0) + 
                                   player_data.get('Pourcentage de passes courtes réussies', 0)) / 2
                st.metric("🏆 Précision Zones Critiques", f"{passes_critiques:.1f}%")
        
        with tab4:
            st.markdown("<div class='section-header'>🔄 Comparaison Pizza Chart Elite</div>", unsafe_allow_html=True)
            
            # Choix du mode avec design football
            mode = st.radio(
                "🎮 Mode de visualisation :",
                ["Radar individuel", "Radar comparatif"], 
                horizontal=True,
                help="Choisissez entre l'analyse individuelle ou la comparaison entre deux joueurs"
            )
            
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            if mode == "Radar individuel":
                st.markdown(f"<div class='section-header'>🎯 Radar Elite : {selected_player}</div>", unsafe_allow_html=True)
                
                try:
                    values1 = calculate_percentiles(selected_player, df_comparison)
                    
                    baker = PyPizza(
                        params=list(RAW_STATS.keys()),
                        background_color="#0a1426",
                        straight_line_color="#FFFFFF",
                        straight_line_lw=2,
                        last_circle_color="#00c851",
                        last_circle_lw=3,
                        other_circle_lw=1,
                        other_circle_color="#FFFFFF",
                        inner_circle_size=12
                    )
                    
                    fig, ax = baker.make_pizza(
                        values1,
                        figsize=(14, 16),
                        param_location=110,
                        color_blank_space="same",
                        slice_colors=[FOOTBALL_COLORS['primary']] * len(values1),
                        value_colors=["#ffffff"] * len(values1),
                        value_bck_colors=[FOOTBALL_COLORS['primary']] * len(values1),
                        kwargs_slices=dict(edgecolor="#FFFFFF", zorder=2, linewidth=2),
                        kwargs_params=dict(color="#ffffff", fontsize=14, fontproperties=font_bold.prop),
                        kwargs_values=dict(color="#ffffff", fontsize=12, fontproperties=font_normal.prop,
                                           bbox=dict(edgecolor="#FFFFFF", facecolor=FOOTBALL_COLORS['primary'], 
                                                   boxstyle="round,pad=0.3", lw=2))
                    )
                    
                    # Headers avec style football
                    fig.text(0.515, 0.97, f"🏆 {selected_player}", size=32, ha="center", 
                            fontproperties=font_bold.prop, color="#00c851", weight='bold')
                    fig.text(0.515, 0.945, f"⚽ Football Analytics Pro | Percentile Elite | Saison 2024-25", 
                            size=16, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                    fig.text(0.515, 0.925, f"🏟️ {player_data['Équipe']} | {selected_competition}", 
                            size=14, ha="center", fontproperties=font_normal.prop, color="#e8f5e8")
                    
                    # Footer avec style
                    fig.text(0.99, 0.02, "🚀 Football Analytics Pro Dashboard | Source: FBRef | Design: Elite Performance",
                             size=10, ha="right", fontproperties=font_italic.prop, color="#a0aec0")
                    
                    # Ajout d'éléments décoratifs
                    fig.text(0.02, 0.98, "⚽", size=40, ha="left", va="top", color="#00c851", alpha=0.3)
                    fig.text(0.98, 0.98, "🏆", size=40, ha="right", va="top", color="#ffc107", alpha=0.3)
                    
                    st.pyplot(fig)
                    
                    # Légende explicative avec style football
                    st.markdown("""
                    <div class='info-card'>
                        <h4>📊 Interprétation du Radar Elite :</h4>
                        <p><strong>🟢 Zone Verte (70-100) :</strong> Performance exceptionnelle - Top joueurs</p>
                        <p><strong>🟡 Zone Jaune (40-70) :</strong> Performance solide - Niveau professionnel</p>
                        <p><strong>🔴 Zone Rouge (0-40) :</strong> Points d'amélioration - Potentiel de progression</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de la création du radar individuel : {str(e)}")
            
            elif mode == "Radar comparatif":
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🏟️ Configuration Joueur 1**")
                    ligue1 = st.selectbox("🏆 Championnat Joueur 1", competitions, 
                                         index=competitions.index(selected_competition), key="ligue1_comp")
                    df_j1 = df[df['Compétition'] == ligue1]
                    joueur1 = st.selectbox("⭐ Joueur 1", df_j1['Joueur'].sort_values(), 
                                          index=list(df_j1['Joueur'].sort_values()).index(selected_player), key="joueur1_comp")
                
                with col2:
                    st.markdown("**🏟️ Configuration Joueur 2**")
                    ligue2 = st.selectbox("🏆 Championnat Joueur 2", competitions, key="ligue2_comp")
                    df_j2 = df[df['Compétition'] == ligue2]
                    joueur2 = st.selectbox("⭐ Joueur 2", df_j2['Joueur'].sort_values(), key="joueur2_comp")
                
                if joueur1 and joueur2:
                    st.markdown(f"<div class='section-header'>⚔️ Duel Elite : {joueur1} vs {joueur2}</div>", unsafe_allow_html=True)
                    
                    # Infos comparatives des joueurs
                    player1_info = df_j1[df_j1['Joueur'] == joueur1].iloc[0]
                    player2_info = df_j2[df_j2['Joueur'] == joueur2].iloc[0]
                    
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown(f"""
                        <div class='info-card'>
                            <h4>🔵 {joueur1}</h4>
                            <p>🏟️ <strong>{player1_info['Équipe']}</strong></p>
                            <p>⚽ <strong>{player1_info['Position']}</strong> | 🎂 <strong>{player1_info['Âge']} ans</strong></p>
                            <p>⏱️ <strong>{int(player1_info['Minutes jouées'])} min</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_info2:
                        st.markdown(f"""
                        <div class='info-card'>
                            <h4>🔴 {joueur2}</h4>
                            <p>🏟️ <strong>{player2_info['Équipe']}</strong></p>
                            <p>⚽ <strong>{player2_info['Position']}</strong> | 🎂 <strong>{player2_info['Âge']} ans</strong></p>
                            <p>⏱️ <strong>{int(player2_info['Minutes jouées'])} min</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    try:
                        values1 = calculate_percentiles(joueur1, df_j1)
                        values2 = calculate_percentiles(joueur2, df_j2)
                        
                        baker = PyPizza(
                            params=list(RAW_STATS.keys()),
                            background_color="#0a1426",
                            straight_line_color="#FFFFFF",
                            straight_line_lw=2,
                            last_circle_color="#FFFFFF",
                            last_circle_lw=2,
                            other_circle_ls="-.",
                            other_circle_lw=1,
                            other_circle_color="#a0aec0"
                        )
                        
                        fig, ax = baker.make_pizza(
                            values1,
                            compare_values=values2,
                            figsize=(14, 14),
                            kwargs_slices=dict(facecolor=FOOTBALL_COLORS['primary'], edgecolor="#FFFFFF", 
                                             linewidth=2, zorder=2, alpha=0.8),
                            kwargs_compare=dict(facecolor='#dc3545', edgecolor="#FFFFFF", 
                                              linewidth=2, zorder=2, alpha=0.8),
                            kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop),
                            kwargs_values=dict(
                                color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                                bbox=dict(edgecolor="#FFFFFF", facecolor=FOOTBALL_COLORS['primary'], 
                                        boxstyle="round,pad=0.2", lw=1)
                            ),
                            kwargs_compare_values=dict(
                                color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                                bbox=dict(edgecolor="#FFFFFF", facecolor='#dc3545', 
                                        boxstyle="round,pad=0.2", lw=1)
                            )
                        )
                        
                        # Headers avec style football comparatif
                        fig.text(0.515, 0.975, "⚔️ Duel Elite | Percentiles Comparatifs | Saison 2024-25",
                                 size=18, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                        
                        # Légende améliorée
                        legend_p1 = mpatches.Patch(color=FOOTBALL_COLORS['primary'], label=f"🔵 {joueur1}")
                        legend_p2 = mpatches.Patch(color='#dc3545', label=f"🔴 {joueur2}")
                        legend = ax.legend(handles=[legend_p1, legend_p2], loc="upper right", 
                                         bbox_to_anchor=(1.35, 1.0), fontsize=12, 
                                         facecolor='#1a2642', edgecolor='#00c851', 
                                         labelcolor='white')
                        legend.get_frame().set_alpha(0.9)
                        
                        # Footer avec infos
                        fig.text(0.99, 0.02, "🚀 Football Analytics Pro | Comparaison Elite\nSource: FBRef | Design: Performance Analytics",
                                 size=9, ha="right", fontproperties=font_italic.prop, color="#a0aec0")
                        
                        # Éléments décoratifs
                        fig.text(0.02, 0.98, "⚽", size=35, ha="left", va="top", color=FOOTBALL_COLORS['primary'], alpha=0.4)
                        fig.text(0.98, 0.98, "⚽", size=35, ha="right", va="top", color='#dc3545', alpha=0.4)
                        
                        st.pyplot(fig)
                        
                        # Analyse comparative détaillée
                        st.markdown("<div class='section-header'>📊 Analyse Comparative Détaillée</div>", unsafe_allow_html=True)
                        
                        # Calcul des scores moyens
                        score1 = np.mean(values1)
                        score2 = np.mean(values2)
                        
                        col_analysis1, col_analysis2, col_analysis3 = st.columns(3)
                        
                        with col_analysis1:
                            st.metric("🔵 Score Global Joueur 1", f"{score1:.1f}/100")
                            winner1 = sum(1 for v1, v2 in zip(values1, values2) if v1 > v2)
                            st.metric("🏆 Catégories Dominées", f"{winner1}/{len(values1)}")
                        
                        with col_analysis2:
                            st.metric("🔴 Score Global Joueur 2", f"{score2:.1f}/100")
                            winner2 = sum(1 for v1, v2 in zip(values1, values2) if v2 > v1)
                            st.metric("🏆 Catégories Dominées", f"{winner2}/{len(values2)}")
                        
                        with col_analysis3:
                            if score1 > score2:
                                st.success(f"🏆 {joueur1} domine avec +{score1-score2:.1f} points")
                            elif score2 > score1:
                                st.success(f"🏆 {joueur2} domine avec +{score2-score1:.1f} points")
                            else:
                                st.info("⚖️ Performance équilibrée")
                            
                            draws = len(values1) - winner1 - winner2
                            st.metric("🤝 Égalités", f"{draws}")
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la création du radar comparatif : {str(e)}")

    else:
        st.warning("⚠️ Veuillez ajuster les filtres pour sélectionner un joueur.")

    # Footer avec design football premium
    st.markdown("---")
    st.markdown("""
    <div class='football-footer'>
        <h3 style='color: #00c851; margin-bottom: 15px;'>🚀 Football Analytics Pro Dashboard</h3>
        <p style='color: #e8f5e8; margin: 0; font-size: 1.2em; font-weight: 500;'>
            ⚽ Analyse avancée des performances footballistiques de niveau professionnel
        </p>
        <p style='color: #a0aec0; margin: 8px 0 0 0; font-size: 1em;'>
            📊 Source des données: FBRef | 🎨 Design: Elite Performance Analytics | 🏆 Saison 2024-25
        </p>
        <div style='margin-top: 15px; display: flex; justify-content: center; gap: 20px;'>
            <span style='color: #00c851;'>🏟️ Terrain</span>
            <span style='color: #ffc107;'>🏆 Excellence</span>
            <span style='color: #dc3545;'>⚽ Passion</span>
            <span style='color: #17a2b8;'>📈 Données</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Message d'erreur avec design football
    st.markdown("""
    <div class='football-header' style='background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);'>
        <h2 style='color: white; margin: 0;'>⚠️ Erreur de Chargement des Données</h2>
        <p style='color: #ffe8e8; margin: 15px 0 0 0; font-size: 1.2em;'>
            Impossible de charger les données footballistiques. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Ce dashboard Football Analytics Pro nécessite un fichier CSV avec les colonnes spécifiées dans les données fournies.")
    
    # Informations d'aide avec style football
    st.markdown("""
    <div class='info-card'>
        <h4>🛠️ Configuration requise :</h4>
        <p>• 📁 Fichier 'df_BIG2025.csv' dans le répertoire</p>
        <p>• 📊 Colonnes de données footballistiques standards</p>
        <p>• ⚽ Statistiques par joueur et par compétition</p>
    </div>
    """, unsafe_allow_html=True)
