import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="⚽ Football Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== STYLES CSS MODERNES ====================
def load_css():
    st.markdown("""
    <style>
    /* Variables CSS */
    :root {
        --primary-color: #FF6B35;
        --secondary-color: #004E89;
        --accent-color: #1A759F;
        --success-color: #00C896;
        --warning-color: #F7B801;
        --danger-color: #D62828;
        --dark-bg: #0E1117;
        --card-bg: #1E2640;
        --text-primary: #FFFFFF;
        --text-secondary: #E2E8F0;
        --border-radius: 12px;
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* Background global */
    .main {
        background: linear-gradient(135deg, var(--dark-bg) 0%, var(--card-bg) 100%);
        padding: 0;
    }

    /* Header principal */
    .header-container {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: var(--shadow);
    }

    .header-title {
        color: var(--text-primary);
        font-size: 3rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .header-subtitle {
        color: var(--text-secondary);
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }

    /* Sidebar améliorée */
    .sidebar-container {
        background: linear-gradient(135deg, var(--card-bg) 0%, #2D3748 100%);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        margin-bottom: 1rem;
        border: 2px solid var(--primary-color);
    }

    .sidebar-title {
        color: var(--primary-color);
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* Carte joueur redesignée */
    .player-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, #2D3748 100%);
        border: 3px solid var(--primary-color);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        position: relative;
        overflow: hidden;
    }

    .player-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
    }

    .player-name {
        color: var(--primary-color);
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        margin: 0 0 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    /* Métriques modernes */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }

    .metric-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, #2D3748 100%);
        border: 1px solid var(--accent-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--primary-color);
    }

    .metric-value {
        color: var(--primary-color);
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }

    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Tabs modernes */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--card-bg);
        border-radius: var(--border-radius);
        padding: 0.5rem;
        border: 2px solid var(--accent-color);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-secondary);
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        margin: 0 0.25rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
        color: var(--text-primary);
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
    }

    /* Section headers */
    .section-header {
        color: var(--primary-color);
        font-size: 2rem;
        font-weight: 800;
        margin: 2rem 0 1rem 0;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }

    .subsection-header {
        color: var(--success-color);
        font-size: 1.5rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid var(--success-color);
        padding-left: 1rem;
    }

    /* Image containers */
    .image-container {
        background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%);
        border: 2px solid var(--primary-color);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 200px;
        box-shadow: var(--shadow);
    }

    .image-caption {
        color: var(--primary-color);
        font-weight: bold;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        text-align: center;
    }

    /* Footer */
    .footer {
        background: linear-gradient(135deg, var(--card-bg) 0%, #2D3748 100%);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin-top: 3rem;
        text-align: center;
        border-top: 3px solid var(--primary-color);
    }

    /* Responsive */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        
        .player-name {
            font-size: 1.8rem;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr;
        }
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-in {
        animation: fadeIn 0.6s ease-out;
    }

    /* Masquer les éléments Streamlit non désirés */
    .stAlert > div {
        display: none;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==================== CONFIGURATION COULEURS ====================
COLORS = {
    'primary': '#FF6B35',
    'secondary': '#004E89', 
    'accent': '#1A759F',
    'success': '#00C896',
    'warning': '#F7B801',
    'danger': '#D62828',
    'dark': '#1E2640',
    'light': '#F8F9FA',
    'gradient': ['#FF6B35', '#004E89', '#1A759F', '#00C896', '#F7B801']
}

# ==================== FONCTIONS UTILITAIRES ====================
@st.cache_data
def load_data():
    """Charge les données depuis le fichier CSV"""
    try:
        df = pd.read_csv('df_BIG2025.csv', encoding='utf-8')
        return df
    except FileNotFoundError:
        st.error("❌ Fichier 'df_BIG2025.csv' non trouvé")
        return None
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement : {str(e)}")
        return None

def get_player_photo(player_name):
    """Retourne le chemin de la photo du joueur"""
    extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG']
    
    for ext in extensions:
        photo_path = f"images_joueurs/**{player_name}{ext}"
        if os.path.exists(photo_path):
            return photo_path
    
    import glob
    for ext in extensions:
        pattern = f"images_joueurs/**{player_name}*{ext}"
        files = glob.glob(pattern)
        if files:
            return files[0]
    
    return None

def get_club_logo(competition, team_name):
    """Retourne le chemin du logo du club"""
    league_folders = {
        'Bundliga': 'Bundliga_Logos',
        'La Liga': 'La_Liga_Logos',
        'Ligue 1': 'Ligue1_Logos',
        'Premier League': 'Premier_League_Logos',
        'Serie A': 'Serie_A_Logos'
    }
    
    folder = league_folders.get(competition)
    if not folder:
        return None
    
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    
    for ext in extensions:
        logo_path = f"{folder}/**{team_name}{ext}"
        if os.path.exists(logo_path):
            return logo_path
    
    return None

def create_modern_metric_card(label, value, icon="📊"):
    """Crée une carte métrique moderne"""
    return f"""
    <div class="metric-card animate-in">
        <div class="metric-value">{icon} {value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """

def display_player_header(player_data, selected_competition):
    """Affiche l'en-tête du joueur avec design moderne"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Photo du joueur
        player_photo_path = get_player_photo(player_data['Joueur'])
        if player_photo_path:
            try:
                player_image = Image.open(player_photo_path)
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(player_image, use_column_width=True)
                st.markdown(f'<div class="image-caption">📸 {player_data["Joueur"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            except:
                st.info("📷 Photo non disponible")
        else:
            st.info("📷 Photo non trouvée")
    
    with col2:
        # Nom et infos centrales
        st.markdown(f"""
        <div class="player-card animate-in">
            <h1 class="player-name">{player_data['Joueur']}</h1>
            <div style="text-align: center; color: #E2E8F0; font-size: 1.2rem;">
                {player_data['Position']} • {player_data['Équipe']} • {selected_competition}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Logo du club
        club_logo_path = get_club_logo(selected_competition, player_data['Équipe'])
        if club_logo_path:
            try:
                club_image = Image.open(club_logo_path)
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(club_image, use_column_width=True)
                st.markdown(f'<div class="image-caption">🏟️ {player_data["Équipe"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            except:
                st.info("🏟️ Logo non disponible")
        else:
            st.info("🏟️ Logo non trouvé")

def create_modern_radar(metrics, values, title, color_primary, color_secondary=None):
    """Crée un radar chart moderne"""
    fig = go.Figure()
    
    # Trace principale
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        fillcolor=f'rgba({color_primary[1:3]}, {color_primary[3:5]}, {color_primary[5:7]}, 0.3)',
        line=dict(color=color_primary, width=3),
        marker=dict(color=color_primary, size=8),
        name=title
    ))
    
    # Configuration du radar
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.3)',
                tickcolor='white',
                tickfont=dict(color='white', size=10)
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.3)',
                tickcolor='white',
                tickfont=dict(color='white', size=11, family='Arial Black')
            ),
            bgcolor='rgba(30, 38, 64, 0.8)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title=dict(
            text=title,
            font=dict(size=16, color='white', family='Arial Black'),
            x=0.5
        ),
        height=500
    )
    
    return fig

# ==================== APPLICATION PRINCIPALE ====================
def main():
    # Charger les styles
    load_css()
    
    # Header principal
    st.markdown("""
    <div class="header-container animate-in">
        <h1 class="header-title">⚽ Football Analytics Pro</h1>
        <p class="header-subtitle">Analyse avancée des performances • Saison 2024-25</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chargement des données
    df = load_data()
    
    if df is None:
        st.error("❌ Impossible de charger les données")
        return
    
    # ==================== SIDEBAR ====================
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-container">
            <h2 class="sidebar-title">🎯 Configuration</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection compétition
        st.markdown("### 🏆 Compétition")
        competitions = sorted(df['Compétition'].dropna().unique())
        selected_competition = st.selectbox(
            "Choisir une compétition",
            competitions,
            label_visibility="collapsed"
        )
        
        # Filtrage par compétition
        df_filtered = df[df['Compétition'] == selected_competition]
        
        st.markdown("---")
        
        # Filtre minutes
        st.markdown("### ⏱️ Minutes jouées")
        min_minutes = int(df_filtered['Minutes jouées'].min()) if not df_filtered['Minutes jouées'].empty else 0
        max_minutes = int(df_filtered['Minutes jouées'].max()) if not df_filtered['Minutes jouées'].empty else 3000
        
        min_minutes_filter = st.slider(
            "Minutes minimum",
            min_value=min_minutes,
            max_value=max_minutes,
            value=min_minutes,
            step=90,
            label_visibility="collapsed"
        )
        
        df_filtered_minutes = df_filtered[df_filtered['Minutes jouées'] >= min_minutes_filter]
        
        # Statistiques de filtrage
        nb_joueurs = len(df_filtered_minutes)
        st.info(f"📊 **{nb_joueurs} joueurs** disponibles")
        
        st.markdown("---")
        
        # Sélection joueur
        st.markdown("### 👤 Joueur")
        if not df_filtered_minutes.empty:
            joueurs = sorted(df_filtered_minutes['Joueur'].dropna().unique())
            selected_player = st.selectbox(
                "Choisir un joueur",
                joueurs,
                label_visibility="collapsed"
            )
        else:
            st.error("Aucun joueur disponible")
            return
    
    # ==================== CONTENU PRINCIPAL ====================
    if selected_player:
        player_data = df_filtered_minutes[df_filtered_minutes['Joueur'] == selected_player].iloc[0]
        
        # Header du joueur
        display_player_header(player_data, selected_competition)
        
        # Métriques principales
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        
        metrics_html = [
            create_modern_metric_card("Âge", f"{player_data['Âge']} ans", "🎂"),
            create_modern_metric_card("Position", player_data['Position'], "⚽"),
            create_modern_metric_card("Nationalité", player_data['Nationalité'], "🌍"),
            create_modern_metric_card("Minutes", f"{int(player_data['Minutes jouées'])}", "⏱️"),
            create_modern_metric_card("Matchs", f"{int(player_data.get('Matchs joués', 0))}", "📅")
        ]
        
        for metric in metrics_html:
            st.markdown(metric, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ==================== ONGLETS PRINCIPAUX ====================
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Analyse Offensive", 
            "🛡️ Analyse Défensive", 
            "🎨 Analyse Technique", 
            "📊 Radar Complet",
            "🔄 Comparaison"
        ])
        
        with tab1:
            st.markdown('<h2 class="section-header">🎯 Analyse Offensive Complète</h2>', unsafe_allow_html=True)
            
            # Heatmap des performances
            fig_heatmap = create_performance_heatmap(player_data, df_filtered_minutes)
            if fig_heatmap:
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<h3 class="subsection-header">📈 Actions Offensives</h3>', unsafe_allow_html=True)
                
                # Actions offensives avec plus de détails
                actions_off = {
                    'Buts': player_data['Buts'],
                    'Passes décisives': player_data['Passes décisives'],
                    'Passes clés': player_data['Passes clés'],
                    'Tirs': player_data.get('Tirs', 0),
                    'Actions → Tir': player_data.get('Actions menant à un tir', 0)
                }
                
                fig_bar = go.Figure()
                
                fig_bar.add_trace(go.Bar(
                    x=list(actions_off.keys()),
                    y=list(actions_off.values()),
                    marker=dict(
                        color=COLORS['gradient'],
                        line=dict(color='white', width=1)
                    ),
                    text=list(actions_off.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=12, family='Arial Black')
                ))
                
                fig_bar.update_layout(
                    title=dict(
                        text="Distribution des Actions Offensives",
                        font=dict(size=14, color='white', family='Arial Black'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white'),
                        tickangle=45,
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30, 38, 64, 0.8)',
                    font=dict(color='white'),
                    height=400
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Graphique d'efficacité offensive
                st.markdown('<h3 class="subsection-header">⚡ Efficacité Offensive</h3>', unsafe_allow_html=True)
                
                efficiency_metrics = {
                    'Conversion (Buts/Tirs)': (player_data['Buts'] / max(player_data.get('Tirs', 1), 1)) * 100,
                    'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                    'Efficacité passes clés': (player_data['Passes décisives'] / max(player_data['Passes clés'], 1)) * 100 if player_data['Passes clés'] > 0 else 0
                }
                
                fig_gauge = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(efficiency_metrics.keys())
                )
                
                colors_gauge = [COLORS['primary'], COLORS['warning'], COLORS['success']]
                
                for i, (metric, value) in enumerate(efficiency_metrics.items()):
                    fig_gauge.add_trace(
                        go.Indicator(
                            mode="gauge+number+delta",
                            value=value,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': metric.split('(')[0]},
                            delta={'reference': 50},
                            gauge={
                                'axis': {'range': [None, 100]},
                                'bar': {'color': colors_gauge[i]},
                                'steps': [
                                    {'range': [0, 25], 'color': "lightgray"},
                                    {'range': [25, 50], 'color': "gray"},
                                    {'range': [50, 75], 'color': "lightblue"},
                                    {'range': [75, 100], 'color': "lightgreen"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge.update_layout(
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=10)
                )
                
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                st.markdown('<h3 class="subsection-header">📊 Radar Offensif Avancé</h3>', unsafe_allow_html=True)
                
                # Radar offensif plus détaillé
                offensive_metrics = {
                    'Buts/90': player_data['Buts par 90 minutes'] * 20,
                    'Passes D./90': player_data['Passes décisives par 90 minutes'] * 30,
                    'xG/90': player_data['Buts attendus par 90 minutes'] * 25,
                    'xA/90': player_data['Passes décisives attendues par 90 minutes'] * 30,
                    'Tirs/90': min(player_data['Tirs par 90 minutes'] * 8, 100),
                    'Actions → Tir/90': min(player_data.get('Actions menant à un tir par 90 minutes', 0) * 5, 100)
                }
                
                # Normaliser les valeurs entre 0 et 100
                offensive_values = [min(v, 100) for v in offensive_metrics.values()]
                
                fig_radar_off = create_modern_radar(
                    list(offensive_metrics.keys()), 
                    offensive_values, 
                    "Radar Offensif Complet", 
                    COLORS['primary']
                )
                
                st.plotly_chart(fig_radar_off, use_container_width=True)
                
                # Scatter plot comparatif
                st.markdown('<h3 class="subsection-header">🎯 Analyse Comparative</h3>', unsafe_allow_html=True)
                
                col_scatter1, col_scatter2 = st.columns(2)
                
                with col_scatter1:
                    x_metric_off = st.selectbox(
                        "Axe X", 
                        ['Buts', 'Tirs', 'Buts attendus (xG)', 'Passes clés'], 
                        key="x_off"
                    )
                
                with col_scatter2:
                    y_metric_off = st.selectbox(
                        "Axe Y", 
                        ['Passes décisives', 'Passes décisives attendues (xAG)', 'Actions menant à un tir'], 
                        key="y_off"
                    )
                
                if x_metric_off and y_metric_off:
                    fig_scatter_off = create_advanced_scatter_plot(
                        df_filtered_minutes, x_metric_off, y_metric_off, selected_player
                    )
                    st.plotly_chart(fig_scatter_off, use_container_width=True)
            
            # Métriques détaillées améliorées
            st.markdown('<h3 class="subsection-header">📈 Statistiques Offensives Détaillées</h3>', unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "Buts/90min", 
                    f"{player_data['Buts par 90 minutes']:.2f}",
                    delta=f"vs moy: {df_filtered_minutes['Buts par 90 minutes'].mean():.2f}"
                )
            
            with col2:
                st.metric(
                    "Passes D./90min", 
                    f"{player_data['Passes décisives par 90 minutes']:.2f}",
                    delta=f"vs moy: {df_filtered_minutes['Passes décisives par 90 minutes'].mean():.2f}"
                )
            
            with col3:
                st.metric(
                    "xG/90min", 
                    f"{player_data['Buts attendus par 90 minutes']:.2f}",
                    delta=f"vs moy: {df_filtered_minutes['Buts attendus par 90 minutes'].mean():.2f}"
                )
            
            with col4:
                st.metric(
                    "Actions → Tir/90min", 
                    f"{player_data.get('Actions menant à un tir par 90 minutes', 0):.2f}",
                    delta=f"vs moy: {df_filtered_minutes.get('Actions menant à un tir par 90 minutes', pd.Series([0])).mean():.2f}"
                )
            
            with col5:
                efficiency_off = ((player_data['Buts'] + player_data['Passes décisives']) / max(player_data.get('Tirs', 1), 1)) * 100
                avg_efficiency = ((df_filtered_minutes['Buts'] + df_filtered_minutes['Passes décisives']) / df_filtered_minutes.get('Tirs', 1).replace(0, 1)).mean() * 100
                st.metric(
                    "Efficacité Offensive", 
                    f"{efficiency_off:.1f}%",
                    delta=f"vs moy: {avg_efficiency:.1f}%"
                )
        
        with tab2:
            st.markdown('<h2 class="section-header">🛡️ Analyse Défensive Complète</h2>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<h3 class="subsection-header">🛡️ Actions Défensives</h3>', unsafe_allow_html=True)
                
                # Actions défensives détaillées
                actions_def = {
                    'Tacles gagnants': player_data['Tacles gagnants'],
                    'Interceptions': player_data['Interceptions'],
                    'Ballons récupérés': player_data['Ballons récupérés'],
                    'Duels aériens gagnés': player_data['Duels aériens gagnés'],
                    'Dégagements': player_data['Dégagements']
                }
                
                fig_bar_def = go.Figure()
                
                fig_bar_def.add_trace(go.Bar(
                    x=list(actions_def.keys()),
                    y=list(actions_def.values()),
                    marker=dict(
                        color=COLORS['accent'],
                        line=dict(color='white', width=1)
                    ),
                    text=list(actions_def.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=12)
                ))
                
                fig_bar_def.update_layout(
                    title=dict(
                        text="Distribution des Actions Défensives",
                        font=dict(size=14, color='white'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white'),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30, 38, 64, 0.8)',
                    font=dict(color='white'),
                    height=400
                )
                
                st.plotly_chart(fig_bar_def, use_container_width=True)
                
                # Radar défensif
                st.markdown('<h3 class="subsection-header">📊 Radar Défensif</h3>', unsafe_allow_html=True)
                
                minutes_90 = player_data['Minutes jouées'] / 90
                defensive_metrics = {
                    'Tacles/90': min((player_data['Tacles gagnants'] / minutes_90) * 25, 100),
                    'Interceptions/90': min((player_data['Interceptions'] / minutes_90) * 20, 100),
                    'Ballons récup./90': min((player_data['Ballons récupérés'] / minutes_90) * 15, 100),
                    'Duels aériens/90': min((player_data['Duels aériens gagnés'] / minutes_90) * 30, 100),
                    '% Duels gagnés': player_data.get('Pourcentage de duels gagnés', 0),
                    '% Duels aériens': player_data['Pourcentage de duels aériens gagnés']
                }
                
                defensive_values = list(defensive_metrics.values())
                
                fig_radar_def = create_modern_radar(
                    list(defensive_metrics.keys()), 
                    defensive_values, 
                    "Radar Défensif", 
                    COLORS['accent']
                )
                
                st.plotly_chart(fig_radar_def, use_container_width=True)
            
            with col2:
                st.markdown('<h3 class="subsection-header">📊 Efficacité Défensive</h3>', unsafe_allow_html=True)
                
                # Pourcentages de réussite avec graphique moderne
                pourcentages_def = {
                    'Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                    'Duels défensifs': player_data.get('Pourcentage de duels gagnés', 0),
                    'Passes réussies': player_data['Pourcentage de passes réussies']
                }
                
                fig_donut = go.Figure(data=[go.Pie(
                    labels=list(pourcentages_def.keys()),
                    values=list(pourcentages_def.values()),
                    hole=0.5,
                    marker=dict(
                        colors=[COLORS['danger'], COLORS['warning'], COLORS['success']],
                        line=dict(color='white', width=2)
                    ),
                    textfont=dict(size=12, color='white'),
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'
                )])
                
                fig_donut.update_layout(
                    title=dict(
                        text="Pourcentages de Réussite Défensive",
                        font=dict(size=14, color='white'),
                        x=0.5
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=400,
                    annotations=[dict(text='Efficacité<br>Défensive', x=0.5, y=0.5, font_size=16, showarrow=False, font_color='white')]
                )
                
                st.plotly_chart(fig_donut, use_container_width=True)
                
                # Comparaison défensive
                st.markdown('<h3 class="subsection-header">⚔️ Comparaison Défensive</h3>', unsafe_allow_html=True)
                
                defensive_comparison = {
                    f'{selected_player}': [
                        player_data['Tacles gagnants'] / minutes_90,
                        player_data['Interceptions'] / minutes_90,
                        player_data['Ballons récupérés'] / minutes_90
                    ],
                    'Moyenne équipe': [
                        (df_filtered_minutes['Tacles gagnants'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean(),
                        (df_filtered_minutes['Interceptions'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean(),
                        (df_filtered_minutes['Ballons récupérés'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean()
                    ]
                }
                
                fig_comp_def = go.Figure()
                
                metrics_names = ['Tacles/90', 'Interceptions/90', 'Ballons récup./90']
                
                fig_comp_def.add_trace(go.Scatterpolar(
                    r=defensive_comparison[selected_player],
                    theta=metrics_names,
                    fill='toself',
                    name=selected_player,
                    line_color=COLORS['primary']
                ))
                
                fig_comp_def.add_trace(go.Scatterpolar(
                    r=defensive_comparison['Moyenne équipe'],
                    theta=metrics_names,
                    fill='toself',
                    name='Moyenne',
                    line_color=COLORS['secondary']
                ))
                
                fig_comp_def.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, max(max(defensive_comparison[selected_player]), max(defensive_comparison['Moyenne équipe'])) * 1.1]
                        )
                    ),
                    showlegend=True,
                    title="Comparaison Défensive",
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=400
                )
                
                st.plotly_chart(fig_comp_def, use_container_width=True)
            
            # Métriques défensives détaillées
            st.markdown('<h3 class="subsection-header">🛡️ Statistiques Défensives Détaillées</h3>', unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                tacles_90 = player_data['Tacles gagnants'] / minutes_90
                avg_tacles = (df_filtered_minutes['Tacles gagnants'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean()
                st.metric(
                    "Tacles/90min", 
                    f"{tacles_90:.2f}",
                    delta=f"vs moy: {avg_tacles:.2f}"
                )
            
            with col2:
                interceptions_90 = player_data['Interceptions'] / minutes_90
                avg_interceptions = (df_filtered_minutes['Interceptions'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean()
                st.metric(
                    "Interceptions/90min", 
                    f"{interceptions_90:.2f}",
                    delta=f"vs moy: {avg_interceptions:.2f}"
                )
            
            with col3:
                ballons_90 = player_data['Ballons récupérés'] / minutes_90
                avg_ballons = (df_filtered_minutes['Ballons récupérés'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean()
                st.metric(
                    "Ballons récup./90min", 
                    f"{ballons_90:.2f}",
                    delta=f"vs moy: {avg_ballons:.2f}"
                )
            
            with col4:
                duels_90 = player_data['Duels aériens gagnés'] / minutes_90
                avg_duels = (df_filtered_minutes['Duels aériens gagnés'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean()
                st.metric(
                    "Duels aériens/90min", 
                    f"{duels_90:.2f}",
                    delta=f"vs moy: {avg_duels:.2f}"
                )
            
            with col5:
                defensive_success = (player_data['Pourcentage de duels gagnés'] + player_data['Pourcentage de duels aériens gagnés']) / 2
                avg_def_success = (df_filtered_minutes.get('Pourcentage de duels gagnés', 0) + df_filtered_minutes['Pourcentage de duels aériens gagnés']).mean() / 2
                st.metric(
                    "Efficacité Défensive", 
                    f"{defensive_success:.1f}%",
                    delta=f"vs moy: {avg_def_success:.1f}%"
                )
        
        with tab3:
            st.markdown('<h2 class="section-header">🎨 Analyse Technique Complète</h2>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<h3 class="subsection-header">🎨 Actions Techniques</h3>', unsafe_allow_html=True)
                
                # Actions techniques détaillées
                actions_tech = {
                    'Passes tentées': player_data['Passes tentées'],
                    'Passes progressives': player_data.get('Passes progressives', 0),
                    'Dribbles tentés': player_data['Dribbles tentés'],
                    'Touches de balle': player_data['Touches de balle'],
                    'Passes clés': player_data['Passes clés']
                }
                
                # Graphique en aires empilées
                fig_area = go.Figure()
                
                categories = list(actions_tech.keys())
                values = list(actions_tech.values())
                
                fig_area.add_trace(go.Scatter(
                    x=categories,
                    y=values,
                    fill='tonexty',
                    mode='lines+markers',
                    line=dict(color=COLORS['success'], width=3),
                    marker=dict(color=COLORS['success'], size=10),
                    name='Actions Techniques'
                ))
                
                fig_area.update_layout(
                    title=dict(
                        text="Profil Technique du Joueur",
                        font=dict(size=14, color='white'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white'),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30, 38, 64, 0.8)',
                    font=dict(color='white'),
                    height=400
                )
                
                st.plotly_chart(fig_area, use_container_width=True)
                
                # Métriques de progression
                st.markdown('<h3 class="subsection-header">🚀 Progression du Ballon</h3>', unsafe_allow_html=True)
                
                progression_metrics = {
                    'Distance prog./90': player_data.get('Distance progressive des passes', 0) / minutes_90,
                    'Passes prog./90': player_data.get('Passes progressives', 0) / minutes_90,
                    'Courses prog./90': player_data.get('Courses progressives', 0) / minutes_90
                }
                
                fig_prog = go.Figure()
                
                fig_prog.add_trace(go.Bar(
                    x=list(progression_metrics.keys()),
                    y=list(progression_metrics.values()),
                    marker=dict(
                        color=[COLORS['primary'], COLORS['warning'], COLORS['success']],
                        line=dict(color='white', width=1)
                    ),
                    text=[f"{v:.1f}" for v in progression_metrics.values()],
                    textposition='outside'
                ))
                
                fig_prog.update_layout(
                    title="Capacité de Progression",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30, 38, 64, 0.8)',
                    font=dict(color='white'),
                    height=300
                )
                
                st.plotly_chart(fig_prog, use_container_width=True)
            
            with col2:
                st.markdown('<h3 class="subsection-header">📊 Efficacité Technique</h3>', unsafe_allow_html=True)
                
                # Radar technique avancé
                technical_metrics = {
                    'Passes/90': min((player_data['Passes tentées'] / minutes_90) / 10, 100),
                    'Touches/90': min((player_data['Touches de balle'] / minutes_90) / 8, 100),
                    'Dribbles/90': min((player_data['Dribbles tentés'] / minutes_90) * 15, 100),
                    '% Passes': player_data.get('Pourcentage de passes réussies', 0),
                    '% Dribbles': player_data.get('Pourcentage de dribbles réussis', 0),
                    'Passes clés/90': min((player_data['Passes clés'] / minutes_90) * 20, 100)
                }
                
                technical_values = list(technical_metrics.values())
                
                fig_radar_tech = create_modern_radar(
                    list(technical_metrics.keys()), 
                    technical_values, 
                    "Radar Technique", 
                    COLORS['success']
                )
                
                st.plotly_chart(fig_radar_tech, use_container_width=True)
                
                # Analyse de précision
                st.markdown('<h3 class="subsection-header">🎯 Analyse de Précision</h3>', unsafe_allow_html=True)
                
                precision_data = {
                    'Passes courtes': player_data.get('Pourcentage de passes courtes réussies', 0),
                    'Passes moyennes': player_data.get('Pourcentage de passes moyennes réussies', 0),
                    'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
                }
                
                # Graphique en barres horizontales
                fig_precision = go.Figure()
                
                fig_precision.add_trace(go.Bar(
                    y=list(precision_data.keys()),
                    x=list(precision_data.values()),
                    orientation='h',
                    marker=dict(
                        color=[COLORS['success'], COLORS['warning'], COLORS['danger']],
                        line=dict(color='white', width=1)
                    ),
                    text=[f"{v:.1f}%" for v in precision_data.values()],
                    textposition='inside'
                ))
                
                fig_precision.update_layout(
                    title="Précision par Type de Passes",
                    xaxis=dict(title="Pourcentage de Réussite", range=[0, 100]),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30, 38, 64, 0.8)',
                    font=dict(color='white'),
                    height=300
                )
                
                st.plotly_chart(fig_precision, use_container_width=True)
            
            # Métriques techniques détaillées
            st.markdown('<h3 class="subsection-header">🎨 Statistiques Techniques Détaillées</h3>', unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                passes_90 = player_data['Passes tentées'] / minutes_90
                avg_passes = (df_filtered_minutes['Passes tentées'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean()
                st.metric(
                    "Passes/90min", 
                    f"{passes_90:.1f}",
                    delta=f"vs moy: {avg_passes:.1f}"
                )
            
            with col2:
                touches_90 = player_data['Touches de balle'] / minutes_90
                avg_touches = (df_filtered_minutes['Touches de balle'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean()
                st.metric(
                    "Touches/90min", 
                    f"{touches_90:.1f}",
                    delta=f"vs moy: {avg_touches:.1f}"
                )
            
            with col3:
                dribbles_90 = player_data['Dribbles tentés'] / minutes_90
                avg_dribbles = (df_filtered_minutes['Dribbles tentés'] / (df_filtered_minutes['Minutes jouées'] / 90)).mean()
                st.metric(
                    "Dribbles/90min", 
                    f"{dribbles_90:.1f}",
                    delta=f"vs moy: {avg_dribbles:.1f}"
                )
            
            with col4:
                passes_precision = player_data.get('Pourcentage de passes réussies', 0)
                avg_precision = df_filtered_minutes.get('Pourcentage de passes réussies', pd.Series([0])).mean()
                st.metric(
                    "% Passes réussies", 
                    f"{passes_precision:.1f}%",
                    delta=f"vs moy: {avg_precision:.1f}%"
                )
            
            with col5:
                technical_efficiency = (
                    player_data.get('Pourcentage de passes réussies', 0) + 
                    player_data.get('Pourcentage de dribbles réussis', 0)
                ) / 2
                avg_tech_efficiency = (
                    df_filtered_minutes.get('Pourcentage de passes réussies', pd.Series([0])).mean() + 
                    df_filtered_minutes.get('Pourcentage de dribbles réussis', pd.Series([0])).mean()
                ) / 2
                st.metric(
                    "Efficacité Technique", 
                    f"{technical_efficiency:.1f}%",
                    delta=f"vs moy: {avg_tech_efficiency:.1f}%"
                )
        
        with tab4:
            st.markdown('<h2 class="section-header">📊 Radar Pizza Chart Complet</h2>', unsafe_allow_html=True)
            
            # Choix du mode
            mode = st.radio(
                "Mode de visualisation", 
                ["Radar individuel", "Radar comparatif"], 
                horizontal=True,
                help="Choisissez entre un radar individuel ou une comparaison entre deux joueurs"
            )
            
            if mode == "Radar individuel":
                st.markdown(f'<h3 class="subsection-header">🎯 Radar complet : {selected_player}</h3>', unsafe_allow_html=True)
                
                fig_pizza = create_pizza_chart(selected_player, df_filtered_minutes, "Radar Pizza Chart Individuel")
                if fig_pizza:
                    st.pyplot(fig_pizza)
                    
                    # Interprétation des résultats
                    percentiles = calculate_percentiles(selected_player, df_filtered_minutes)
                    avg_percentile = np.mean(percentiles)
                    
                    if avg_percentile >= 80:
                        interpretation = "🌟 **Excellent** - Performance exceptionnelle dans la majorité des domaines"
                        color = "success"
                    elif avg_percentile >= 60:
                        interpretation = "🔥 **Très bon** - Performance solide avec des points forts marqués"
                        color = "warning"
                    elif avg_percentile >= 40:
                        interpretation = "📈 **Moyen** - Performance dans la moyenne avec du potentiel d'amélioration"
                        color = "info"
                    else:
                        interpretation = "💪 **En développement** - Marge de progression importante"
                        color = "error"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, var(--card-bg) 0%, #2D3748 100%); 
                                padding: 1.5rem; border-radius: 12px; margin: 1rem 0; 
                                border-left: 4px solid var(--{color}-color);">
                        <h4 style="color: var(--primary-color); margin: 0 0 0.5rem 0;">📊 Analyse du Profil</h4>
                        <p style="color: white; margin: 0; font-size: 1.1rem;">{interpretation}</p>
                        <p style="color: #A0AEC0; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                            Percentile moyen: {avg_percentile:.1f}% • Top {100-avg_percentile:.0f}% des joueurs
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ Impossible de générer le radar chart")
            
            elif mode == "Radar comparatif":
                st.markdown('<h3 class="subsection-header">⚔️ Comparaison de deux joueurs</h3>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**👤 Joueur 1**")
                    ligue1 = st.selectbox(
                        "🏆 Compétition Joueur 1", 
                        competitions, 
                        index=competitions.index(selected_competition), 
                        key="ligue1_comp"
                    )
                    df_j1 = df[df['Compétition'] == ligue1]
                    joueur1 = st.selectbox(
                        "Choisir joueur 1", 
                        sorted(df_j1['Joueur'].dropna().unique()), 
                        index=list(sorted(df_j1['Joueur'].dropna().unique())).index(selected_player) if selected_player in df_j1['Joueur'].values else 0,
                        key="joueur1_comp"
                    )
                
                with col2:
                    st.markdown("**👤 Joueur 2**")
                    ligue2 = st.selectbox(
                        "🏆 Compétition Joueur 2", 
                        competitions, 
                        key="ligue2_comp"
                    )
                    df_j2 = df[df['Compétition'] == ligue2]
                    joueur2 = st.selectbox(
                        "Choisir joueur 2", 
                        sorted(df_j2['Joueur'].dropna().unique()), 
                        key="joueur2_comp"
                    )
                
                if joueur1 and joueur2 and joueur1 != joueur2:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%); 
                                padding: 1rem; border-radius: 12px; margin: 1rem 0; text-align: center;">
                        <h4 style="color: white; margin: 0;">⚔️ {joueur1} vs {joueur2}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    fig_comp_pizza = create_comparison_pizza(joueur1, joueur2, df_j1, df_j2)
                    if fig_comp_pizza:
                        st.pyplot(fig_comp_pizza)
                        
                        # Analyse comparative
                        percentiles1 = calculate_percentiles(joueur1, df_j1)
                        percentiles2 = calculate_percentiles(joueur2, df_j2)
                        
                        avg_perc1 = np.mean(percentiles1)
                        avg_perc2 = np.mean(percentiles2)
                        
                        col_comp1, col_comp2, col_comp3 = st.columns(3)
                        
                        with col_comp1:
                            st.metric(
                                f"📊 {joueur1}",
                                f"{avg_perc1:.1f}%",
                                delta=f"{avg_perc1 - avg_perc2:+.1f}%" if avg_perc1 != avg_perc2 else "0%"
                            )
                        
                        with col_comp2:
                            winner = joueur1 if avg_perc1 > avg_perc2 else joueur2 if avg_perc2 > avg_perc1 else "Égalité"
                            st.markdown(f"""
                            <div style="text-align: center; padding: 1rem;">
                                <h4 style="color: var(--primary-color);">🏆 Avantage</h4>
                                <p style="color: white; font-size: 1.2rem; margin: 0;">{winner}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_comp3:
                            st.metric(
                                f"📊 {joueur2}",
                                f"{avg_perc2:.1f}%",
                                delta=f"{avg_perc2 - avg_perc1:+.1f}%" if avg_perc2 != avg_perc1 else "0%"
                            )
                    else:
                        st.error("❌ Impossible de générer la comparaison")
        
        with tab5:
            st.markdown('<h2 class="section-header">🔄 Comparaison Avancée</h2>', unsafe_allow_html=True)
            
            # Sélection de plusieurs joueurs pour comparaison
            st.markdown('<h3 class="subsection-header">👥 Sélection des joueurs</h3>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🎯 Joueurs à comparer**")
                selected_players_comp = st.multiselect(
                    "Choisir jusqu'à 5 joueurs",
                    joueurs,
                    default=[selected_player],
                    max_selections=5,
                    help="Sélectionnez entre 2 et 5 joueurs pour la comparaison"
                )
            
            with col2:
                st.markdown("**📊 Métriques à analyser**")
                metric_categories = {
                    "Offensive": ['Buts', 'Passes décisives', 'Tirs', 'Buts attendus (xG)'],
                    "Défensive": ['Tacles gagnants', 'Interceptions', 'Ballons récupérés', 'Duels aériens gagnés'],
                    "Technique": ['Passes tentées', 'Pourcentage de passes réussies', 'Dribbles tentés', 'Touches de balle']
                }
                
                selected_category = st.selectbox(
                    "Catégorie de métriques",
                    list(metric_categories.keys())
                )
                
                selected_metrics_comp = st.multiselect(
                    f"Métriques {selected_category.lower()}",
                    metric_categories[selected_category],
                    default=metric_categories[selected_category][:3]
                )
            
            if len(selected_players_comp) >= 2 and selected_metrics_comp:
                # Graphique de comparaison multiple
                st.markdown('<h3 class="subsection-header">📈 Comparaison Multi-Joueurs</h3>', unsafe_allow_html=True)
                
                fig_multi_comp = go.Figure()
                
                colors_multi = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['success'], COLORS['warning']]
                
                for i, player in enumerate(selected_players_comp):
                    player_stats = df_filtered_minutes[df_filtered_minutes['Joueur'] == player].iloc[0]
                    
                    # Convertir en par 90 minutes
                    minutes_90_comp = player_stats['Minutes jouées'] / 90
                    
                    values_comp = []
                    for metric in selected_metrics_comp:
                        if 'Pourcentage' in metric or '%' in metric:
                            values_comp.append(player_stats.get(metric, 0))
                        else:
                            values_comp.append(player_stats.get(metric, 0) / minutes_90_comp)
                    
                    fig_multi_comp.add_trace(go.Scatterpolar(
                        r=values_comp,
                        theta=selected_metrics_comp,
                        fill='toself',
                        name=player,
                        line_color=colors_multi[i % len(colors_multi)],
                        fillcolor=f'rgba({colors_multi[i % len(colors_multi)][1:3]}, {colors_multi[i % len(colors_multi)][3:5]}, {colors_multi[i % len(colors_multi)][5:7]}, 0.2)'
                    ))
                
                fig_multi_comp.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor='white',
                            tickfont=dict(color='white')
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=11)
                        ),
                        bgcolor='rgba(30, 38, 64, 0.8)'
                    ),
                    showlegend=True,
                    title=dict(
                        text=f"Comparaison {selected_category}",
                        font=dict(size=16, color='white'),
                        x=0.5
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=500,
                    legend=dict(
                        bgcolor='rgba(30, 38, 64, 0.8)',
                        bordercolor='white',
                        borderwidth=1
                    )
                )
                
                st.plotly_chart(fig_multi_comp, use_container_width=True)
                
                # Tableau de comparaison détaillé
                st.markdown('<h3 class="subsection-header">📋 Tableau Comparatif Détaillé</h3>', unsafe_allow_html=True)
                
                comparison_data = []
                for player in selected_players_comp:
                    player_stats = df_filtered_minutes[df_filtered_minutes['Joueur'] == player].iloc[0]
                    minutes_90_comp = player_stats['Minutes jouées'] / 90
                    
                    row = {'Joueur': player}
                    for metric in selected_metrics_comp:
                        if 'Pourcentage' in metric or '%' in metric:
                            row[f"{metric}"] = f"{player_stats.get(metric, 0):.1f}%"
                        else:
                            row[f"{metric}/90"] = f"{player_stats.get(metric, 0) / minutes_90_comp:.2f}"
                    
                    # Ajouter quelques métriques générales
                    row['Âge'] = player_stats['Âge']
                    row['Position'] = player_stats['Position']
                    row['Minutes'] = int(player_stats['Minutes jouées'])
                    
                    comparison_data.append(row)
                
                comparison_df = pd.DataFrame(comparison_data)
                
                # Affichage du tableau avec style
                st.dataframe(
                    comparison_df,
                    use_container_width=True,
                    height=300
                )
                
                # Analyse des forces et faiblesses
                st.markdown('<h3 class="subsection-header">💪 Analyse des Forces et Faiblesses</h3>', unsafe_allow_html=True)
                
                if len(selected_players_comp) == 2:
                    player1_name, player2_name = selected_players_comp[0], selected_players_comp[1]
                    player1_stats = df_filtered_minutes[df_filtered_minutes['Joueur'] == player1_name].iloc[0]
                    player2_stats = df_filtered_minutes[df_filtered_minutes['Joueur'] == player2_name].iloc[0]
                    
                    col_analysis1, col_analysis2 = st.columns(2)
                    
                    with col_analysis1:
                        st.markdown(f"**🔥 Forces de {player1_name}**")
                        strengths1 = []
                        for metric in selected_metrics_comp:
                            val1 = player1_stats.get(metric, 0)
                            val2 = player2_stats.get(metric, 0)
                            if val1 > val2:
                                strengths1.append(f"• {metric}: {val1:.2f} vs {val2:.2f}")
                        
                        if strengths1:
                            for strength in strengths1[:3]:  # Top 3
                                st.success(strength)
                        else:
                            st.info("Aucun avantage significatif détecté")
                    
                    with col_analysis2:
                        st.markdown(f"**🔥 Forces de {player2_name}**")
                        strengths2 = []
                        for metric in selected_metrics_comp:
                            val1 = player1_stats.get(metric, 0)
                            val2 = player2_stats.get(metric, 0)
                            if val2 > val1:
                                strengths2.append(f"• {metric}: {val2:.2f} vs {val1:.2f}")
                        
                        if strengths2:
                            for strength in strengths2[:3]:  # Top 3
                                st.success(strength)
                        else:
                            st.info("Aucun avantage significatif détecté")
                
                # Scatter plot multi-dimensionnel
                if len(selected_metrics_comp) >= 2:
                    st.markdown('<h3 class="subsection-header">🎯 Analyse Multi-dimensionnelle</h3>', unsafe_allow_html=True)
                    
                    col_scatter_x, col_scatter_y = st.columns(2)
                    
                    with col_scatter_x:
                        x_metric_multi = st.selectbox(
                            "Métrique axe X", 
                            selected_metrics_comp, 
                            key="x_multi"
                        )
                    
                    with col_scatter_y:
                        y_metric_multi = st.selectbox(
                            "Métrique axe Y", 
                            [m for m in selected_metrics_comp if m != x_metric_multi], 
                            key="y_multi"
                        )
                    
                    if x_metric_multi and y_metric_multi:
                        fig_scatter_multi = go.Figure()
                        
                        # Tous les autres joueurs (en arrière-plan)
                        other_players_multi = df_filtered_minutes[~df_filtered_minutes['Joueur'].isin(selected_players_comp)]
                        
                        if 'Pourcentage' not in x_metric_multi:
                            x_others_multi = other_players_multi[x_metric_multi] / (other_players_multi['Minutes jouées'] / 90)
                        else:
                            x_others_multi = other_players_multi[x_metric_multi]
                            
                        if 'Pourcentage' not in y_metric_multi:
                            y_others_multi = other_players_multi[y_metric_multi] / (other_players_multi['Minutes jouées'] / 90)
                        else:
                            y_others_multi = other_players_multi[y_metric_multi]
                        
                        fig_scatter_multi.add_trace(go.Scatter(
                            x=x_others_multi,
                            y=y_others_multi,
                            mode='markers',
                            name='Autres joueurs',
                            marker=dict(color='rgba(128,128,128,0.3)', size=6),
                            showlegend=True
                        ))
                        
                        # Joueurs sélectionnés
                        for i, player in enumerate(selected_players_comp):
                            player_stats_multi = df_filtered_minutes[df_filtered_minutes['Joueur'] == player].iloc[0]
                            minutes_90_multi = player_stats_multi['Minutes jouées'] / 90
                            
                            if 'Pourcentage' not in x_metric_multi:
                                x_val = player_stats_multi[x_metric_multi] / minutes_90_multi
                            else:
                                x_val = player_stats_multi[x_metric_multi]
                                
                            if 'Pourcentage' not in y_metric_multi:
                                y_val = player_stats_multi[y_metric_multi] / minutes_90_multi
                            else:
                                y_val = player_stats_multi[y_metric_multi]
                            
                            fig_scatter_multi.add_trace(go.Scatter(
                                x=[x_val],
                                y=[y_val],
                                mode='markers+text',
                                name=player,
                                marker=dict(
                                    color=colors_multi[i % len(colors_multi)], 
                                    size=15,
                                    symbol='star'
                                ),
                                text=[player],
                                textposition='top center',
                                textfont=dict(color='white', size=10)
                            ))
                        
                        fig_scatter_multi.update_layout(
                            title=f"{x_metric_multi} vs {y_metric_multi}",
                            xaxis=dict(title=x_metric_multi, tickfont=dict(color='white')),
                            yaxis=dict(title=y_metric_multi, tickfont=dict(color='white')),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(30, 38, 64, 0.8)',
                            font=dict(color='white'),
                            height=500
                        )
                        
                        st.plotly_chart(fig_scatter_multi, use_container_width=True)
            
            else:
                st.info("👆 Sélectionnez au moins 2 joueurs et des métriques pour commencer la comparaison")

    # Footer
    st.markdown("""
    <div class="footer animate-in">
        <h3 style="color: #FF6B35; margin-bottom: 1rem;">⚽ Football Analytics Pro</h3>
        <p style="color: #E2E8F0; margin: 0;">
            Dashboard professionnel d'analyse des performances footballistiques
        </p>
        <p style="color: #A0AEC0; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            Données: FBRef | Design: Football Analytics Pro | Saison 2024-25
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer animate-in">
        <h3 style="color: #FF6B35; margin-bottom: 1rem;">⚽ Football Analytics Pro</h3>
        <p style="color: #E2E8F0; margin: 0;">
            Dashboard professionnel d'analyse des performances footballistiques
        </p>
        <p style="color: #A0AEC0; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
            Données: FBRef | Design: Football Analytics Pro | Saison 2024-25
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================== FONCTIONS RADAR AVANCÉES ====================

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

def create_pizza_chart(player_name, df, title="Radar Pizza Chart"):
    """Crée un pizza chart avec mplsoccer"""
    try:
        values = calculate_percentiles(player_name, df)
        
        font_normal = FontManager()
        font_bold = FontManager()
        font_italic = FontManager()
        
        baker = PyPizza(
            params=list(RAW_STATS.keys()),
            background_color="#0E1117",
            straight_line_color="#FFFFFF",
            straight_line_lw=1,
            last_circle_color="#FFFFFF",
            last_circle_lw=1,
            other_circle_lw=0,
            inner_circle_size=11
        )
        
        fig, ax = baker.make_pizza(
            values,
            figsize=(12, 14),
            param_location=110,
            color_blank_space="same",
            slice_colors=[COLORS['primary']] * len(values),
            value_colors=["#ffffff"] * len(values),
            value_bck_colors=[COLORS['primary']] * len(values),
            kwargs_slices=dict(edgecolor="#FFFFFF", zorder=2, linewidth=1),
            kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop),
            kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop,
                               bbox=dict(edgecolor="#FFFFFF", facecolor=COLORS['primary'], boxstyle="round,pad=0.2", lw=1))
        )
        
        fig.text(0.515, 0.95, player_name, size=26, ha="center", fontproperties=font_bold.prop, color="#ffffff")
        fig.text(0.515, 0.925, f"{title} | Percentile | Saison 2024-25", size=14,
                 ha="center", fontproperties=font_bold.prop, color="#ffffff")
        fig.text(0.99, 0.01, "Football Analytics Pro | Données: FBRef",
                 size=8, ha="right", fontproperties=font_italic.prop, color="#dddddd")
        
        return fig
        
    except Exception as e:
        st.error(f"Erreur lors de la création du pizza chart : {str(e)}")
        return None

def create_comparison_pizza(player1_name, player2_name, df1, df2):
    """Crée un pizza chart comparatif"""
    try:
        values1 = calculate_percentiles(player1_name, df1)
        values2 = calculate_percentiles(player2_name, df2)
        
        font_normal = FontManager()
        font_bold = FontManager()
        font_italic = FontManager()
        
        params_offset = [False] * len(RAW_STATS)
        if len(params_offset) > 9:
            params_offset[9] = True
        if len(params_offset) > 10:
            params_offset[10] = True
        
        baker = PyPizza(
            params=list(RAW_STATS.keys()),
            background_color="#0E1117",
            straight_line_color="#FFFFFF",
            straight_line_lw=1,
            last_circle_color="#FFFFFF",
            last_circle_lw=1,
            other_circle_ls="-.",
            other_circle_lw=1
        )
        
        fig, ax = baker.make_pizza(
            values1,
            compare_values=values2,
            figsize=(12, 12),
            kwargs_slices=dict(facecolor=COLORS['primary'], edgecolor="#FFFFFF", linewidth=1, zorder=2),
            kwargs_compare=dict(facecolor=COLORS['secondary'], edgecolor="#FFFFFF", linewidth=1, zorder=2),
            kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop),
            kwargs_values=dict(
                color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                bbox=dict(edgecolor="#FFFFFF", facecolor=COLORS['primary'], boxstyle="round,pad=0.2", lw=1)
            ),
            kwargs_compare_values=dict(
                color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                bbox=dict(edgecolor="#FFFFFF", facecolor=COLORS['secondary'], boxstyle="round,pad=0.2", lw=1)
            )
        )
        
        fig.text(0.515, 0.955, "Radar comparatif | Percentile | Saison 2024-25",
                 size=14, ha="center", fontproperties=font_bold.prop, color="#ffffff")
        
        legend_p1 = mpatches.Patch(color=COLORS['primary'], label=player1_name)
        legend_p2 = mpatches.Patch(color=COLORS['secondary'], label=player2_name)
        ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0))
        
        fig.text(0.99, 0.01, "Football Analytics Pro | Source: FBRef",
                 size=8, ha="right", fontproperties=font_italic.prop, color="#dddddd")
        
        return fig
        
    except Exception as e:
        st.error(f"Erreur lors de la création du radar comparatif : {str(e)}")
        return None

def create_advanced_scatter_plot(df, x_metric, y_metric, selected_player):
    """Crée un scatter plot avancé avec annotations"""
    fig = go.Figure()
    
    # Convertir en par 90 minutes si nécessaire
    if 'Pourcentage' not in x_metric and '%' not in x_metric:
        x_data = df[x_metric] / (df['Minutes jouées'] / 90)
        x_title = f"{x_metric} par 90min"
    else:
        x_data = df[x_metric]
        x_title = x_metric
        
    if 'Pourcentage' not in y_metric and '%' not in y_metric:
        y_data = df[y_metric] / (df['Minutes jouées'] / 90)
        y_title = f"{y_metric} par 90min"
    else:
        y_data = df[y_metric]
        y_title = y_metric
    
    # Données du joueur sélectionné
    player_data = df[df['Joueur'] == selected_player].iloc[0]
    if 'Pourcentage' not in x_metric and '%' not in x_metric:
        x_player = player_data[x_metric] / (player_data['Minutes jouées'] / 90)
    else:
        x_player = player_data[x_metric]
        
    if 'Pourcentage' not in y_metric and '%' not in y_metric:
        y_player = player_data[y_metric] / (player_data['Minutes jouées'] / 90)
    else:
        y_player = player_data[y_metric]
    
    # Tous les autres joueurs
    other_players = df[df['Joueur'] != selected_player]
    if 'Pourcentage' not in x_metric and '%' not in x_metric:
        x_others = other_players[x_metric] / (other_players['Minutes jouées'] / 90)
    else:
        x_others = other_players[x_metric]
        
    if 'Pourcentage' not in y_metric and '%' not in y_metric:
        y_others = other_players[y_metric] / (other_players['Minutes jouées'] / 90)
    else:
        y_others = other_players[y_metric]
    
    # Scatter plot pour les autres joueurs
    fig.add_trace(go.Scatter(
        x=x_others,
        y=y_others,
        mode='markers',
        name='Autres joueurs',
        marker=dict(
            color=COLORS['accent'], 
            size=8, 
            opacity=0.6,
            line=dict(width=1, color='white')
        ),
        text=other_players['Joueur'],
        hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
    ))
    
    # Joueur sélectionné
    fig.add_trace(go.Scatter(
        x=[x_player],
        y=[y_player],
        mode='markers',
        name=selected_player,
        marker=dict(
            color=COLORS['primary'], 
            size=20, 
            symbol='star',
            line=dict(width=2, color='white')
        ),
        hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
    ))
    
    # Lignes de moyenne
    x_mean = x_data.mean()
    y_mean = y_data.mean()
    
    fig.add_hline(y=y_mean, line_dash="dash", line_color="rgba(255,255,255,0.5)", 
                  annotation_text=f"Moyenne {y_title}: {y_mean:.2f}")
    fig.add_vline(x=x_mean, line_dash="dash", line_color="rgba(255,255,255,0.5)", 
                  annotation_text=f"Moyenne {x_title}: {x_mean:.2f}")
    
    fig.update_layout(
        title=dict(
            text=f"Analyse: {x_title} vs {y_title}", 
            font=dict(size=16, color='white'), 
            x=0.5
        ),
        xaxis=dict(
            title=dict(text=x_title, font=dict(color='white')), 
            tickfont=dict(color='white'),
            gridcolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(color='white')), 
            tickfont=dict(color='white'),
            gridcolor='rgba(255,255,255,0.2)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30, 38, 64, 0.8)',
        font=dict(color='white'),
        height=500,
        showlegend=True,
        legend=dict(
            bgcolor='rgba(30, 38, 64, 0.8)',
            bordercolor='white',
            borderwidth=1
        )
    )
    
    return fig

def create_performance_heatmap(player_data, df_comparison):
    """Crée une heatmap des performances"""
    metrics = [
        'Buts par 90 minutes',
        'Passes décisives par 90 minutes',
        'Buts attendus par 90 minutes',
        'Tirs par 90 minutes',
        'Pourcentage de passes réussies',
        'Pourcentage de duels gagnés'
    ]
    
    # Calculer les percentiles
    percentiles = []
    metric_names = []
    
    for metric in metrics:
        if metric in df_comparison.columns and metric in player_data.index:
            value = player_data[metric]
            distribution = df_comparison[metric].dropna()
            
            if not distribution.empty and not pd.isna(value):
                percentile = (distribution < value).mean() * 100
                percentiles.append(percentile)
                metric_names.append(metric.replace(' par 90 minutes', '/90').replace('Pourcentage de ', '% '))
    
    if not percentiles:
        return None
    
    # Créer la heatmap
    fig = go.Figure(data=go.Heatmap(
        z=[percentiles],
        x=metric_names,
        y=['Performance'],
        colorscale=[
            [0, '#D62828'],      # Rouge pour faible
            [0.25, '#F7B801'],   # Jaune pour moyen-faible
            [0.5, '#1A759F'],    # Bleu pour moyen
            [0.75, '#00C896'],   # Vert pour bon
            [1, '#FF6B35']       # Orange pour excellent
        ],
        text=[[f"{p:.0f}" for p in percentiles]],
        texttemplate="%{text}",
        textfont={"size": 12, "color": "white"},
        hovertemplate='<b>%{x}</b><br>Percentile: %{z:.0f}<extra></extra>',
        showscale=True,
        colorbar=dict(
            title="Percentile",
            titlefont=dict(color='white'),
            tickfont=dict(color='white')
        )
    ))
    
    fig.update_layout(
        title=dict(
            text="Heatmap des Performances (Percentiles)",
            font=dict(size=16, color='white'),
            x=0.5
        ),
        xaxis=dict(
            tickfont=dict(color='white'),
            tickangle=45
        ),
        yaxis=dict(
            tickfont=dict(color='white'),
            showticklabels=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=200
    )
    
    return fig

# ==================== EXÉCUTION PRINCIPALE ====================
if __name__ == "__main__":
    main()
