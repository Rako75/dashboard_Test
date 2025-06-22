import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration de la page avec thème football
st.set_page_config(
    page_title="⚽ Football Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design football professionnel
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto:wght@300;400;500;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #0B4D3A 0%, #1E5631 30%, #0F3D0F 100%);
        font-family: 'Roboto', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0B4D3A 0%, #1E5631 30%, #0F3D0F 100%);
    }
    
    /* Header principal avec effet terrain de football */
    .football-header {
        background: linear-gradient(45deg, #228B22 0%, #32CD32 25%, #228B22 50%, #32CD32 75%, #228B22 100%);
        background-size: 20px 20px;
        padding: 30px;
        border-radius: 20px;
        border: 3px solid #FFD700;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        position: relative;
        overflow: hidden;
        margin-bottom: 30px;
    }
    
    .football-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: repeating-linear-gradient(
            90deg,
            rgba(255,255,255,0.1) 0px,
            rgba(255,255,255,0.1) 1px,
            transparent 1px,
            transparent 20px
        );
    }
    
    .football-title {
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        font-size: 3.5em;
        color: #FFFFFF;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.8);
        text-align: center;
        margin: 0;
        position: relative;
        z-index: 2;
    }
    
    .football-subtitle {
        font-family: 'Roboto', sans-serif;
        font-weight: 300;
        font-size: 1.3em;
        color: #FFD700;
        text-align: center;
        margin: 15px 0 0 0;
        position: relative;
        z-index: 2;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    
    /* Sidebar avec design terrain */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0B4D3A 0%, #1E5631 100%);
        border-right: 3px solid #FFD700;
    }
    
    /* Onglets avec design football */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #1E5631 0%, #2F7D32 100%);
        border-radius: 15px;
        border: 2px solid #FFD700;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #FFFFFF;
        border-radius: 10px;
        font-weight: 600;
        font-family: 'Roboto', sans-serif;
        margin: 0 2px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 215, 0, 0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #1E5631;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
    }
    
    /* Cards avec effet terrain */
    .metric-card {
        background: linear-gradient(135deg, #1E5631 0%, #2F7D32 100%);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #FFD700;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '⚽';
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 24px;
        opacity: 0.3;
    }
    
    /* Métriques avec style football */
    .stMetric {
        background: linear-gradient(135deg, #2F7D32 0%, #388E3C 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #FFD700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        position: relative;
    }
    
    .stMetric label {
        color: #FFD700 !important;
        font-weight: 600;
        font-family: 'Roboto', sans-serif;
    }
    
    .stMetric [data-testid="metric-value"] {
        color: #FFFFFF !important;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
    }
    
    /* Selectbox avec style football */
    .stSelectbox > div > div > div {
        background: linear-gradient(135deg, #1E5631 0%, #2F7D32 100%);
        border: 2px solid #FFD700;
        border-radius: 10px;
    }
    
    .stSelectbox > div > div > div > div {
        color: #FFFFFF;
        font-weight: 500;
    }
    
    /* Slider avec couleurs football */
    .stSlider > div > div > div > div {
        background: #FFD700;
    }
    
    .stSlider > div > div > div > div > div {
        background: #1E5631;
    }
    
    /* Radio buttons football style */
    .stRadio > div {
        background: linear-gradient(135deg, #1E5631 0%, #2F7D32 100%);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #FFD700;
    }
    
    /* Titres des sections */
    .section-title {
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        color: #FFD700;
        font-size: 1.8em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin: 20px 0;
        text-align: center;
        position: relative;
    }
    
    .section-title::before {
        content: '⚽';
        margin-right: 10px;
    }
    
    .section-title::after {
        content: '⚽';
        margin-left: 10px;
    }
    
    /* Footer football */
    .football-footer {
        background: linear-gradient(135deg, #1E5631 0%, #2F7D32 100%);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #FFD700;
        text-align: center;
        margin-top: 30px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }
    
    /* Animations */
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }
    
    .bounce-animation {
        animation: bounce 2s infinite;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0B4D3A 0%, #1E5631 100%);
    }
    
    /* Sidebar title */
    .sidebar-title {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        border: 2px solid #1E5631;
        color: #1E5631;
        font-weight: 700;
        font-family: 'Orbitron', monospace;
    }
</style>
""", unsafe_allow_html=True)

# Couleurs thème football professionnel
COLORS = {
    'primary': '#FFD700',      # Or (comme les trophées)
    'secondary': '#1E5631',    # Vert foncé terrain
    'accent': '#32CD32',       # Vert clair terrain
    'success': '#00C851',      # Vert succès
    'warning': '#FF8C00',      # Orange
    'danger': '#DC143C',       # Rouge carton
    'dark': '#0B4D3A',         # Vert très foncé
    'light': '#F8F9FA',        # Blanc
    'gradient': ['#FFD700', '#32CD32', '#1E5631', '#00C851', '#FF8C00']
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

COLOR_1 = COLORS['primary']
COLOR_2 = COLORS['secondary']
SLICE_COLORS = [COLORS['accent']] * len(RAW_STATS)

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
    # Header avec design football professionnel
    st.markdown("""
    <div class='football-header'>
        <h1 class='football-title bounce-animation'>⚽ FOOTBALL ANALYTICS PRO ⚽</h1>
        <p class='football-subtitle'>🏆 Analyse Avancée des Performances | Saison 2024-25 🏆</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar avec design football
    with st.sidebar:
        st.markdown("""
        <div class='sidebar-title'>
            🎯 CENTRE DE CONTRÔLE ⚽
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection de la compétition/ligue
        st.markdown("### 🏆 Sélection de la Compétition")
        competitions = sorted(df['Compétition'].dropna().unique())
        selected_competition = st.selectbox(
            "Choisir une compétition :",
            competitions,
            index=0,
            help="Sélectionnez la ligue ou compétition à analyser"
        )
        
        # Filtrer les joueurs selon la compétition
        df_filtered = df[df['Compétition'] == selected_competition]
        
        # Filtre par minutes jouées
        min_minutes = int(df_filtered['Minutes jouées'].min()) if not df_filtered['Minutes jouées'].empty else 0
        max_minutes = int(df_filtered['Minutes jouées'].max()) if not df_filtered['Minutes jouées'].empty else 3000
        
        st.markdown("---")
        st.markdown("### ⏱️ Filtre Temps de Jeu")
        
        # Slider pour sélectionner le minimum de minutes
        min_minutes_filter = st.slider(
            "Minutes minimum jouées :",
            min_value=min_minutes,
            max_value=max_minutes,
            value=min_minutes,
            step=90,
            help="Filtrer les joueurs ayant joué au minimum ce nombre de minutes"
        )
        
        # Filtrer les joueurs selon les minutes jouées
        df_filtered_minutes = df_filtered[df_filtered['Minutes jouées'] >= min_minutes_filter]
        
        # Afficher le nombre de joueurs après filtrage
        nb_joueurs = len(df_filtered_minutes)
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                    padding: 15px; border-radius: 10px; text-align: center; 
                    border: 2px solid #1E5631; margin: 15px 0;'>
            <strong style='color: #1E5631; font-family: Orbitron;'>
                🏃‍♂️ {nb_joueurs} JOUEURS ACTIFS ⚽
            </strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sélection du joueur (maintenant filtré par minutes)
        st.markdown("### 👤 Sélection du Joueur")
        if not df_filtered_minutes.empty:
            joueurs = sorted(df_filtered_minutes['Joueur'].dropna().unique())
            selected_player = st.selectbox(
                "Choisir un joueur :",
                joueurs,
                index=0,
                help="Sélectionnez le joueur à analyser"
            )
        else:
            st.error("⚠️ Aucun joueur ne correspond aux critères sélectionnés.")
            selected_player = None
        
        # Informations sidebar
        st.markdown("---")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E5631 0%, #2F7D32 100%); 
                    padding: 15px; border-radius: 10px; border: 1px solid #FFD700;'>
            <h4 style='color: #FFD700; text-align: center; margin: 0;'>📊 Données</h4>
            <p style='color: white; font-size: 0.9em; margin: 10px 0 0 0; text-align: center;'>
                Source: FBRef<br>
                Saison 2024-25<br>
                Mise à jour continue
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Obtenir les données du joueur sélectionné
    if selected_player:
        player_data = df_filtered_minutes[df_filtered_minutes['Joueur'] == selected_player].iloc[0]
        
        # Utiliser df_filtered_minutes pour les comparaisons et calculs
        df_comparison = df_filtered_minutes  # Utiliser les données filtrées par minutes
    
        # Affichage des informations générales du joueur avec design football
        st.markdown(f"""
        <div class='section-title'>
            📊 PROFIL JOUEUR : {selected_player}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("⏱️ Âge", f"{player_data['Âge']} ans")
        with col2:
            st.metric("🎯 Position", player_data['Position'])
        with col3:
            st.metric("🏟️ Équipe", player_data['Équipe'])
        with col4:
            st.metric("🌍 Nationalité", player_data['Nationalité'])
        with col5:
            st.metric("⚽ Minutes", f"{int(player_data['Minutes jouées'])} min")
        
        st.markdown("---")
    
        # Graphiques principaux avec thème football
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 ATTAQUE", 
            "🛡️ DÉFENSE", 
            "🎨 TECHNIQUE", 
            "🔄 COMPARAISON"
        ])
        
        with tab1:
            st.markdown("<div class='section-title'>🎯 PERFORMANCE OFFENSIVE</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions offensives avec couleurs football
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
                        color=COLORS['gradient'],
                        line=dict(color='#FFD700', width=2)
                    ),
                    text=list(actions_off.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Orbitron')
                )])
                
                fig_bar_off.update_layout(
                    title=dict(
                        text="⚽ Actions Offensives",
                        font=dict(size=18, color='#FFD700', family='Orbitron'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', family='Roboto'),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', family='Roboto'),
                        gridcolor='rgba(255,215,0,0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30,86,49,0.1)',
                    font=dict(color='white'),
                    height=400
                )
                st.plotly_chart(fig_bar_off, use_container_width=True)
                
                # Radar professionnel des actions offensives avec couleurs football
                st.markdown("<h3 style='color: #FFD700; margin-top: 30px; text-align: center; font-family: Orbitron;'>🎯 Radar Offensif Professionnel</h3>", unsafe_allow_html=True)
                
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
                        percentile_values.append(min(percentile, 100))  # Cap à 100
                        avg_values.append(avg_comp)
                    else:
                        percentile_values.append(50)  # Valeur par défaut si problème
                        avg_values.append(0)
                
                # Créer le radar avec les couleurs football
                fig_radar = go.Figure()
                
                # Ajouter la performance du joueur
                fig_radar.add_trace(go.Scatterpolar(
                    r=percentile_values,
                    theta=list(offensive_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(255, 215, 0, 0.3)',
                    line=dict(color=COLORS['primary'], width=3),
                    marker=dict(color=COLORS['primary'], size=8, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(offensive_metrics.values())
                ))
                
                # Calculer les percentiles des moyennes de la compétition
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
                
                # Ajouter une ligne de référence pour la moyenne de la compétition
                fig_radar.add_trace(go.Scatterpolar(
                    r=avg_percentiles,
                    theta=list(offensive_metrics.keys()),
                    mode='lines',
                    line=dict(color='rgba(50,205,50,0.8)', width=2, dash='dash'),
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
                            gridcolor='rgba(255,215,0,0.4)',
                            tickcolor='#FFD700',
                            tickfont=dict(color='white', size=10, family='Roboto'),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,215,0,0.4)',
                            tickcolor='#FFD700',
                            tickfont=dict(color='white', size=11, family='Orbitron'),
                            linecolor='rgba(255,215,0,0.6)'
