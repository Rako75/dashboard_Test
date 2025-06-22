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
    page_title="⚽ Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé avec thème football
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
    
    .main {
        background: linear-gradient(135deg, #0E4B99 0%, #2E8B57 50%, #1E3A8A 100%);
        font-family: 'Roboto', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #0E4B99 0%, #2E8B57 50%, #1E3A8A 100%);
    }
    
    /* Style des onglets comme un terrain de football */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(90deg, #228B22 0%, #32CD32 100%);
        border-radius: 15px;
        padding: 8px;
        border: 3px solid #FFFFFF;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #FFFFFF;
        border-radius: 10px;
        font-weight: bold;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF6B35 0%, #FF4500 100%);
        color: #FFFFFF;
        border: 2px solid #FFFFFF;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
    }
    
    /* Cards avec style terrain de football */
    .metric-card {
        background: linear-gradient(135deg, #228B22 0%, #32CD32 100%);
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #FFFFFF;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '⚽';
        position: absolute;
        top: -10px;
        right: -10px;
        font-size: 3em;
        opacity: 0.1;
        transform: rotate(15deg);
    }
    
    .stMetric {
        background: linear-gradient(135deg, #228B22 0%, #32CD32 100%);
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #FFFFFF;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar comme vestiaire */
    .css-1d391kg {
        background: linear-gradient(180deg, #1E3A8A 0%, #0E4B99 100%);
        border-right: 4px solid #FF6B35;
    }
    
    /* Animations football */
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .football-bounce {
        animation: bounce 2s infinite;
        display: inline-block;
    }
    
    /* Terrain de football en background */
    .football-field {
        background: 
            linear-gradient(90deg, transparent 49%, #FFFFFF 49%, #FFFFFF 51%, transparent 51%),
            linear-gradient(0deg, transparent 49%, #FFFFFF 49%, #FFFFFF 51%, transparent 51%),
            radial-gradient(circle at 50% 50%, transparent 9%, #FFFFFF 9%, #FFFFFF 10%, transparent 10%),
            linear-gradient(135deg, #228B22 0%, #32CD32 100%);
        background-size: 100px 100px, 100px 100px, 50px 50px, 100% 100%;
        background-position: 0 0, 0 0, 25px 25px, 0 0;
    }
    
    /* Style pour les titres */
    .football-title {
        background: linear-gradient(45deg, #FF6B35, #FFD700, #FF6B35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# Couleurs thème football
COLORS = {
    'primary': '#FF6B35',      # Orange football
    'secondary': '#1E3A8A',    # Bleu marine
    'accent': '#32CD32',       # Vert terrain
    'success': '#228B22',      # Vert foncé
    'warning': '#FFD700',      # Jaune arbitre
    'danger': '#DC143C',       # Rouge carton
    'field_green': '#228B22',  # Vert terrain
    'white_lines': '#FFFFFF',  # Lignes blanches
    'gradient': ['#FF6B35', '#1E3A8A', '#32CD32', '#FFD700', '#DC143C']
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
        st.error("⚠️ Fichier 'df_BIG2025.csv' non trouvé. Veuillez vous assurer que le fichier est dans le même répertoire.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
        return None

# Chargement des données
df = load_data()

if df is not None:
    # Header avec design football
    st.markdown("""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #228B22 0%, #32CD32 50%, #228B22 100%); border-radius: 20px; margin-bottom: 30px; border: 4px solid #FFFFFF; position: relative; overflow: hidden;'>
        <div style='position: absolute; top: -20px; left: -20px; font-size: 4em; opacity: 0.1; transform: rotate(-15deg);'>⚽</div>
        <div style='position: absolute; bottom: -20px; right: -20px; font-size: 4em; opacity: 0.1; transform: rotate(15deg);'>🏆</div>
        <h1 style='color: white; margin: 0; font-size: 3.5em; text-shadow: 3px 3px 6px rgba(0,0,0,0.5); font-weight: 900;'>
            <span class="football-bounce">⚽</span> FOOTBALL ANALYTICS <span class="football-bounce">⚽</span>
        </h1>
        <p style='color: #E8F5E8; margin: 15px 0 0 0; font-size: 1.3em; font-weight: bold;'>
            🏟️ Dashboard Professionnel d'Analyse des Performances - Saison 2024-25 🏟️
        </p>
        <div style='margin-top: 15px; font-size: 1.5em;'>🥅⚽🏃‍♂️📊🏆</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar avec design vestiaire
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E3A8A 0%, #0E4B99 100%); padding: 25px; border-radius: 20px; margin-bottom: 25px; border: 3px solid #FF6B35; text-align: center;'>
            <h2 style='color: #FFD700; margin-bottom: 20px; font-size: 1.8em; font-weight: 900;'>
                🏟️ SÉLECTION JOUEUR 🏟️
            </h2>
            <div style='font-size: 1.2em; margin-bottom: 10px;'>👕🥾📋</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection de la compétition avec style football
        st.markdown("### 🏆 **CHAMPIONNAT**")
        competitions = sorted(df['Compétition'].dropna().unique())
        selected_competition = st.selectbox(
            "🏆 Choisir une compétition :",
            competitions,
            index=0
        )
        
        # Filtrer les joueurs selon la compétition
        df_filtered = df[df['Compétition'] == selected_competition]
        
        # Filtre par minutes jouées
        min_minutes = int(df_filtered['Minutes jouées'].min()) if not df_filtered['Minutes jouées'].empty else 0
        max_minutes = int(df_filtered['Minutes jouées'].max()) if not df_filtered['Minutes jouées'].empty else 3000
        
        st.markdown("---")
        st.markdown("### ⏱️ **TEMPS DE JEU**")
        
        # Slider pour sélectionner le minimum de minutes
        min_minutes_filter = st.slider(
            "Minutes minimum jouées :",
            min_value=min_minutes,
            max_value=max_minutes,
            value=min_minutes,
            step=90,
            help="🔍 Filtrer les joueurs ayant joué au minimum ce nombre de minutes"
        )
        
        # Filtrer les joueurs selon les minutes jouées
        df_filtered_minutes = df_filtered[df_filtered['Minutes jouées'] >= min_minutes_filter]
        
        # Afficher le nombre de joueurs après filtrage
        nb_joueurs = len(df_filtered_minutes)
        st.markdown(f"""
        <div style='background: linear-gradient(90deg, #228B22 0%, #32CD32 100%); padding: 15px; border-radius: 10px; text-align: center; border: 2px solid white; margin: 10px 0;'>
            <h4 style='color: white; margin: 0;'>👥 **{nb_joueurs} JOUEURS** disponibles</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sélection du joueur
        st.markdown("### 👤 **SÉLECTION JOUEUR**")
        if not df_filtered_minutes.empty:
            joueurs = sorted(df_filtered_minutes['Joueur'].dropna().unique())
            selected_player = st.selectbox(
                "👤 Choisir un joueur :",
                joueurs,
                index=0
            )
        else:
            st.error("❌ Aucun joueur ne correspond aux critères sélectionnés.")
            selected_player = None
    
    # Obtenir les données du joueur sélectionné
    if selected_player:
        player_data = df_filtered_minutes[df_filtered_minutes['Joueur'] == selected_player].iloc[0]
        
        # Utiliser df_filtered_minutes pour les comparaisons et calculs
        df_comparison = df_filtered_minutes  # Utiliser les données filtrées par minutes
    
        # Affichage des informations générales du joueur avec design football
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1E3A8A 0%, #0E4B99 100%); padding: 30px; border-radius: 20px; margin: 25px 0; border: 4px solid #FF6B35; position: relative; overflow: hidden;'>
            <div style='position: absolute; top: 10px; right: 20px; font-size: 3em; opacity: 0.2;'>👕</div>
            <div style='position: absolute; bottom: 10px; left: 20px; font-size: 2em; opacity: 0.2;'>⚽🥅</div>
            <h2 style='color: #FFD700; text-align: center; margin-bottom: 25px; font-size: 2.2em; font-weight: 900;'>
                🌟 PROFIL DE {selected_player.upper()} 🌟
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #228B22 0%, #32CD32 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                <div style='font-size: 2em; margin-bottom: 10px;'>🎂</div>
                <h3 style='color: white; margin: 0; font-weight: bold;'>ÂGE</h3>
                <h2 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{} ans</h2>
            </div>
            """.format(player_data['Âge']), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #228B22 0%, #32CD32 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                <div style='font-size: 2em; margin-bottom: 10px;'>⚽</div>
                <h3 style='color: white; margin: 0; font-weight: bold;'>POSITION</h3>
                <h2 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.5em;'>{}</h2>
            </div>
            """.format(player_data['Position']), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #228B22 0%, #32CD32 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                <div style='font-size: 2em; margin-bottom: 10px;'>🏟️</div>
                <h3 style='color: white; margin: 0; font-weight: bold;'>ÉQUIPE</h3>
                <h2 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.3em;'>{}</h2>
            </div>
            """.format(player_data['Équipe']), unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #228B22 0%, #32CD32 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                <div style='font-size: 2em; margin-bottom: 10px;'>🌍</div>
                <h3 style='color: white; margin: 0; font-weight: bold;'>NATIONALITÉ</h3>
                <h2 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.3em;'>{}</h2>
            </div>
            """.format(player_data['Nationalité']), unsafe_allow_html=True)
        with col5:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #228B22 0%, #32CD32 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                <div style='font-size: 2em; margin-bottom: 10px;'>⏱️</div>
                <h3 style='color: white; margin: 0; font-weight: bold;'>MINUTES</h3>
                <h2 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.5em;'>{} min</h2>
            </div>
            """.format(int(player_data['Minutes jouées'])), unsafe_allow_html=True)
        
        st.markdown("---")
    
        # Graphiques principaux avec onglets football
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 ATTAQUE", "🛡️ DÉFENSE", "🎨 TECHNIQUE", "⚔️ COMPARAISON"])
        
        with tab1:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #FF6B35 0%, #FF4500 100%); border-radius: 15px; margin-bottom: 25px; border: 3px solid white;'>
                <h2 style='color: white; margin: 0; font-size: 2.2em; font-weight: 900;'>🎯 PERFORMANCE OFFENSIVE 🥅</h2>
                <p style='color: #FFE8E8; margin: 10px 0 0 0; font-size: 1.1em;'>Analyse des actions offensives et de finition</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions offensives avec style football
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
                        line=dict(color='white', width=2)
                    ),
                    text=list(actions_off.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Arial Black')
                )])
                
                fig_bar_off.update_layout(
                    title=dict(
                        text="⚽ Actions Offensives ⚽",
                        font=dict(size=18, color='white', family='Arial Black'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', size=12, family='Arial Black'),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', size=12),
                        gridcolor='rgba(255,255,255,0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(34,139,34,0.2)',
                    font=dict(color='white'),
                    height=400
                )
                st.plotly_chart(fig_bar_off, use_container_width=True)
                
                # Radar professionnel des actions offensives
                st.markdown("""
                <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); border-radius: 10px; margin: 20px 0; border: 2px solid white;'>
                    <h3 style='color: #1E3A8A; margin: 0; font-weight: 900;'>🎯 RADAR OFFENSIF PROFESSIONNEL 🎯</h3>
                </div>
                """, unsafe_allow_html=True)
                
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
                
                # Calculer les percentiles par rapport à la compétition pour une meilleure lisibilité
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
                
                # Créer le radar avec les moyennes de la compétition comme référence
                fig_radar = go.Figure()
                
                # Ajouter la performance du joueur
                fig_radar.add_trace(go.Scatterpolar(
                    r=percentile_values,
                    theta=list(offensive_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(255, 107, 53, 0.4)',
                    line=dict(color=COLORS['primary'], width=4),
                    marker=dict(color=COLORS['primary'], size=10, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(offensive_metrics.values())
                ))
                
                # Calculer les percentiles des moyennes de la compétition (seront autour de 50)
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
                            gridcolor='rgba(255,255,255,0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=11, family='Arial Black'),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=12, family='Arial Black'),
                            linecolor='rgba(255,255,255,0.6)'
                        ),
                        bgcolor='rgba(34, 139, 34, 0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    title=dict(
                        text="⚽ RADAR OFFENSIF (Percentiles) ⚽",
                        font=dict(size=18, color='white', family='Arial Black'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color='white', size=11, family='Arial Black')
                    ),
                    height=450,
                    annotations=[
                        dict(
                            text=f"🏆 Performance vs Moyenne {selected_competition} 🏆",
                            showarrow=False,
                            x=0.5,
                            y=-0.15,
                            xref="paper",
                            yref="paper",
                            font=dict(color='white', size=13, family='Arial Black'),
                            bgcolor='rgba(255, 107, 53, 0.9)',
                            bordercolor='white',
                            borderwidth=2
                        )
                    ]
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite offensifs avec style football
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
                    subplot_titles=[f"🎯 {k}" for k in pourcentages_off.keys()]
                )
                
                colors_off = [COLORS['primary'], COLORS['secondary'], COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages_off.items()):
                    fig_gauge_off.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_off[i], thickness=0.8),
                                bgcolor="rgba(34,139,34,0.3)",
                                borderwidth=3,
                                bordercolor="white",
                                steps=[
                                    {'range': [0, 33], 'color': 'rgba(220,20,60,0.3)'},
                                    {'range': [33, 66], 'color': 'rgba(255,215,0,0.3)'},
                                    {'range': [66, 100], 'color': 'rgba(34,139,34,0.3)'}
                                ],
                                threshold={
                                    'line': {'color': "white", 'width': 4},
                                    'thickness': 0.8,
                                    'value': 80
                                }
                            ),
                            number={'suffix': '%', 'font': {'color': 'white', 'size': 16, 'family': 'Arial Black'}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_off.update_layout(
                    height=350, 
                    title_text="🥅 Pourcentages de Réussite Offensive 🥅",
                    title_font=dict(color='white', size=16, family='Arial Black'),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', family='Arial Black')
                )
                st.plotly_chart(fig_gauge_off, use_container_width=True)
                
                # Graphique de comparaison offensive avec style football
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
                    name=f"⭐ {selected_player}",
                    x=list(offensive_comparison.keys()),
                    y=list(offensive_comparison.values()),
                    marker=dict(
                        color=COLORS['primary'],
                        line=dict(color='white', width=2)
                    ),
                    text=[f"{v:.2f}" for v in offensive_comparison.values()],
                    textposition='outside',
                    textfont=dict(color='white', size=12, family='Arial Black')
                ))
                
                fig_off_comp.add_trace(go.Bar(
                    name=f"📊 Moyenne {selected_competition}",
                    x=list(avg_comparison_off.keys()),
                    y=list(avg_comparison_off.values()),
                    marker=dict(
                        color=COLORS['secondary'],
                        line=dict(color='white', width=2)
                    ),
                    text=[f"{v:.2f}" for v in avg_comparison_off.values()],
                    textposition='outside',
                    textfont=dict(color='white', size=12, family='Arial Black')
                ))
                
                fig_off_comp.update_layout(
                    title=dict(
                        text='⚔️ Actions Offensives vs Moyenne Championnat ⚔️',
                        font=dict(color='white', size=16, family='Arial Black'),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(34,139,34,0.2)',
                    font=dict(color='white', family='Arial Black'),
                    xaxis=dict(
                        tickfont=dict(color='white', size=12, family='Arial Black'),
                        gridcolor='rgba(255,255,255,0.3)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', size=12),
                        gridcolor='rgba(255,255,255,0.3)'
                    ),
                    height=400,
                    legend=dict(
                        font=dict(color='white', family='Arial Black')
                    )
                )
                
                st.plotly_chart(fig_off_comp, use_container_width=True)
            
            # Scatter plot pour comparaison offensive avec style football
            st.markdown("""
            <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #32CD32 0%, #228B22 100%); border-radius: 15px; margin: 30px 0; border: 3px solid white;'>
                <h3 style='color: white; margin: 0; font-size: 1.5em; font-weight: 900;'>🔍 ANALYSE COMPARATIVE OFFENSIVE 🔍</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                # Sélection des métriques pour le scatter plot offensif
                metric_options_off = [
                    'Buts', 'Passes décisives', 'Tirs', 'Buts attendus (xG)',
                    'Passes décisives attendues (xAG)', 'Passes clés', 'Actions menant à un tir',
                    'Pourcentage de tirs cadrés'
                ]
                
                st.markdown("#### 🎯 **Sélection des métriques**")
                x_metric_off = st.selectbox("📊 Métrique X", metric_options_off, index=0, key="x_off")
                y_metric_off = st.selectbox("📊 Métrique Y", metric_options_off, index=1, key="y_off")
            
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
                    name='👥 Autres joueurs',
                    marker=dict(color=COLORS['accent'], size=10, opacity=0.7, 
                               line=dict(color='white', width=1)),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                # Joueur sélectionné
                fig_scatter_off.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=f"⭐ {selected_player}",
                    marker=dict(color=COLORS['primary'], size=25, symbol='star',
                               line=dict(color='white', width=3)),
                    hovertemplate=f'<b>⭐ {selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_off.update_layout(
                    title=dict(text=f"⚽ {x_title} vs {y_title} ⚽", 
                              font=dict(size=16, color='white', family='Arial Black'), x=0.5),
                    xaxis=dict(
                        title=dict(text=x_title, font=dict(color='white', family='Arial Black')), 
                        tickfont=dict(color='white'),
                        gridcolor='rgba(255,255,255,0.3)'
                    ),
                    yaxis=dict(
                        title=dict(text=y_title, font=dict(color='white', family='Arial Black')), 
                        tickfont=dict(color='white'),
                        gridcolor='rgba(255,255,255,0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(34,139,34,0.2)',
                    font=dict(color='white', family='Arial Black'),
                    height=400,
                    legend=dict(font=dict(color='white', family='Arial Black'))
                )
                
                st.plotly_chart(fig_scatter_off, use_container_width=True)
            
            # Métriques offensives par 90 minutes avec design football
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); border-radius: 15px; margin: 30px 0; border: 3px solid white;'>
                <h3 style='color: #1E3A8A; margin: 0; font-size: 1.8em; font-weight: 900;'>📊 STATISTIQUES OFFENSIVES PAR 90 MINUTES 📊</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #FF6B35 0%, #FF4500 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>⚽</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>BUTS/90min</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.2f}</h3>
                </div>
                """.format(player_data['Buts par 90 minutes']), unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #FF6B35 0%, #FF4500 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>🎯</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>PASSES D./90min</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.2f}</h3>
                </div>
                """.format(player_data['Passes décisives par 90 minutes']), unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #FF6B35 0%, #FF4500 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>📈</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>xG/90min</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.2f}</h3>
                </div>
                """.format(player_data['Buts attendus par 90 minutes']), unsafe_allow_html=True)
            with col4:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #FF6B35 0%, #FF4500 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>🔫</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>ACTIONS→TIR/90min</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.2f}</h3>
                </div>
                """.format(player_data['Actions menant à un tir par 90 minutes']), unsafe_allow_html=True)
            with col5:
                # Nouveau compteur de pourcentage d'efficacité offensive
                efficiency_off = (player_data['Buts'] + player_data['Passes décisives']) / player_data.get('Tirs', 1) * 100 if player_data.get('Tirs', 0) > 0 else 0
                st.markdown("""
                <div style='background: linear-gradient(135deg, #FF6B35 0%, #FF4500 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>🏆</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>EFFICACITÉ OFF.</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.1f}%</h3>
                </div>
                """.format(efficiency_off), unsafe_allow_html=True)
    
        with tab2:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #1E3A8A 0%, #0E4B99 100%); border-radius: 15px; margin-bottom: 25px; border: 3px solid white;'>
                <h2 style='color: white; margin: 0; font-size: 2.2em; font-weight: 900;'>🛡️ PERFORMANCE DÉFENSIVE 🛡️</h2>
                <p style='color: #E8E8FF; margin: 10px 0 0 0; font-size: 1.1em;'>Analyse des actions défensives et récupération</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions défensives avec style football
                actions_def = {
                    'Tacles gagnants': player_data['Tacles gagnants'],
                    'Interceptions': player_data['Interceptions'],
                    'Ballons récupérés': player_data['Ballons récupérés'],
                    'Duels aériens gagnés': player_data['Duels aériens gagnés'],
                    'Dégagements': player_data['Dégagements']
                }
                
                fig_bar = go.Figure(data=[go.Bar(
                    x=list(actions_def.keys()),
                    y=list(actions_def.values()),
                    marker=dict(
                        color=COLORS['gradient'],
                        line=dict(color='white', width=2)
                    ),
                    text=list(actions_def.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Arial Black')
                )])
                
                fig_bar.update_layout(
                    title=dict(
                        text="🛡️ Actions Défensives 🛡️",
                        font=dict(size=18, color='white', family='Arial Black'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', size=12, family='Arial Black'),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', size=12),
                        gridcolor='rgba(255,255,255,0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30,58,138,0.2)',
                    font=dict(color='white'),
                    height=400
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Radar professionnel des actions défensives
                st.markdown("""
                <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #1E3A8A 0%, #0E4B99 100%); border-radius: 10px; margin: 20px 0; border: 2px solid white;'>
                    <h3 style='color: #FFD700; margin: 0; font-weight: 900;'>🛡️ RADAR DÉFENSIF PROFESSIONNEL 🛡️</h3>
                </div>
                """, unsafe_allow_html=True)
                
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
                
                # Calculer les percentiles et moyennes par rapport à la compétition
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
                        
                        # Nettoyer les valeurs NaN et infinies
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
                
                # Ajouter la performance du joueur
                fig_def_radar.add_trace(go.Scatterpolar(
                    r=def_percentile_values,
                    theta=list(defensive_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(30, 58, 138, 0.4)',
                    line=dict(color=COLORS['secondary'], width=4),
                    marker=dict(color=COLORS['secondary'], size=10, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(defensive_metrics.values())
                ))
                
                # Calculer les percentiles des moyennes de la compétition
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
                
                # Ajouter une ligne de référence pour la moyenne de la compétition
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
                            gridcolor='rgba(255,255,255,0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=11, family='Arial Black'),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.4)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=12, family='Arial Black'),
                            linecolor='rgba(255,255,255,0.6)'
                        ),
                        bgcolor='rgba(30, 58, 138, 0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    title=dict(
                        text="🛡️ RADAR DÉFENSIF (Percentiles) 🛡️",
                        font=dict(size=18, color='white', family='Arial Black'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color='white', size=11, family='Arial Black')
                    ),
                    height=450,
                    annotations=[
                        dict(
                            text=f"🏆 Performance Défensive vs Moyenne {selected_competition} 🏆",
                            showarrow=False,
                            x=0.5,
                            y=-0.15,
                            xref="paper",
                            yref="paper",
                            font=dict(color='white', size=13, family='Arial Black'),
                            bgcolor='rgba(30, 58, 138, 0.9)',
                            bordercolor='white',
                            borderwidth=2
                        )
                    ]
                )
                
                st.plotly_chart(fig_def_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite avec design football
                pourcentages = {
                    'Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                    'Duels défensifs': player_data['Pourcentage de duels gagnés'],
                    'Passes réussies': player_data['Pourcentage de passes réussies']
                }
                
                # Nettoyer les valeurs NaN
                pourcentages = {k: v if pd.notna(v) else 0 for k, v in pourcentages.items()}
                
                fig_gauge = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=[f"🛡️ {k}" for k in pourcentages.keys()]
                )
                
                colors = [COLORS['danger'], COLORS['secondary'], COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages.items()):
                    fig_gauge.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors[i], thickness=0.8),
                                bgcolor="rgba(30,58,138,0.3)",
                                borderwidth=3,
                                bordercolor="white",
                                steps=[
                                    {'range': [0, 33], 'color': 'rgba(220,20,60,0.3)'},
                                    {'range': [33, 66], 'color': 'rgba(255,215,0,0.3)'},
                                    {'range': [66, 100], 'color': 'rgba(34,139,34,0.3)'}
                                ],
                                threshold={
                                    'line': {'color': "white", 'width': 4},
                                    'thickness': 0.8,
                                    'value': 80
                                }
                            ),
                            number={'suffix': '%', 'font': {'color': 'white', 'size': 16, 'family': 'Arial Black'}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge.update_layout(
                    height=350, 
                    title_text="🛡️ Pourcentages de Réussite Défensive 🛡️",
                    title_font=dict(color='white', size=16, family='Arial Black'),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', family='Arial Black')
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Graphique de comparaison défensive
                defensive_comparison = {
                    'Tacles/90': player_data['Tacles gagnants'] / (player_data['Minutes jouées'] / 90),
                    'Interceptions/90': player_data['Interceptions'] / (player_data['Minutes jouées'] / 90),
                    'Ballons récupérés/90': player_data['Ballons récupérés'] / (player_data['Minutes jouées'] / 90)
                }
                
                # Moyennes de la compétition
                avg_comparison = {
                    'Tacles/90': (df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Interceptions/90': (df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Ballons récupérés/90': (df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)).mean()
                }
                
                fig_def_comp = go.Figure()
                
                fig_def_comp.add_trace(go.Bar(
                    name=f"⭐ {selected_player}",
                    x=list(defensive_comparison.keys()),
                    y=list(defensive_comparison.values()),
                    marker=dict(
                        color=COLORS['primary'],
                        line=dict(color='white', width=2)
                    ),
                    text=[f"{v:.2f}" for v in defensive_comparison.values()],
                    textposition='outside',
                    textfont=dict(color='white', size=12, family='Arial Black')
                ))
                
                fig_def_comp.add_trace(go.Bar(
                    name=f"📊 Moyenne {selected_competition}",
                    x=list(avg_comparison.keys()),
                    y=list(avg_comparison.values()),
                    marker=dict(
                        color=COLORS['secondary'],
                        line=dict(color='white', width=2)
                    ),
                    text=[f"{v:.2f}" for v in avg_comparison.values()],
                    textposition='outside',
                    textfont=dict(color='white', size=12, family='Arial Black')
                ))
                
                fig_def_comp.update_layout(
                    title=dict(
                        text='⚔️ Actions Défensives vs Moyenne Championnat ⚔️',
                        font=dict(color='white', size=16, family='Arial Black'),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(30,58,138,0.2)',
                    font=dict(color='white', family='Arial Black'),
                    xaxis=dict(
                        tickfont=dict(color='white', size=12, family='Arial Black'),
                        gridcolor='rgba(255,255,255,0.3)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', size=12),
                        gridcolor='rgba(255,255,255,0.3)'
                    ),
                    height=400,
                    legend=dict(font=dict(color='white', family='Arial Black'))
                )
                
                st.plotly_chart(fig_def_comp, use_container_width=True)
            
            # Métriques défensives par 90 minutes avec design football
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); border-radius: 15px; margin: 30px 0; border: 3px solid white;'>
                <h3 style='color: #1E3A8A; margin: 0; font-size: 1.8em; font-weight: 900;'>📊 STATISTIQUES DÉFENSIVES PAR 90 MINUTES 📊</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            # Calcul des métriques par 90 minutes
            minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
            
            with col1:
                tacles_90 = player_data['Tacles gagnants'] / minutes_90
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1E3A8A 0%, #0E4B99 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>⚔️</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>TACLES/90min</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.2f}</h3>
                </div>
                """.format(tacles_90), unsafe_allow_html=True)
            with col2:
                interceptions_90 = player_data['Interceptions'] / minutes_90
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1E3A8A 0%, #0E4B99 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>🚫</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>INTERCEPTIONS/90min</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.2f}</h3>
                </div>
                """.format(interceptions_90), unsafe_allow_html=True)
            with col3:
                ballons_90 = player_data['Ballons récupérés'] / minutes_90
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1E3A8A 0%, #0E4B99 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>⚽</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>BALLONS RÉC./90min</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.2f}</h3>
                </div>
                """.format(ballons_90), unsafe_allow_html=True)
            with col4:
                duels_90 = player_data['Duels aériens gagnés'] / minutes_90
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1E3A8A 0%, #0E4B99 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>🦅</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>DUELS AÉRIENS/90min</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.2f}</h3>
                </div>
                """.format(duels_90), unsafe_allow_html=True)
            with col5:
                # Nouveau compteur de pourcentage de réussite défensive
                defensive_success = (player_data['Pourcentage de duels gagnés'] + player_data['Pourcentage de duels aériens gagnés']) / 2
                st.markdown("""
                <div style='background: linear-gradient(135deg, #1E3A8A 0%, #0E4B99 100%); padding: 20px; border-radius: 15px; text-align: center; border: 3px solid white; margin: 5px;'>
                    <div style='font-size: 2.5em; margin-bottom: 10px;'>🏆</div>
                    <h4 style='color: white; margin: 0; font-weight: bold;'>EFFICACITÉ DÉF.</h4>
                    <h3 style='color: #FFD700; margin: 5px 0 0 0; font-size: 1.8em;'>{:.1f}%</h3>
                </div>
                """.format(defensive_success), unsafe_allow_html=True)
        
        with tab3:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #32CD32 0%, #228B22 100%); border-radius: 15px; margin-bottom: 25px; border: 3px solid white;'>
                <h2 style='color: white; margin: 0; font-size: 2.2em; font-weight: 900;'>🎨 PERFORMANCE TECHNIQUE 🎨</h2>
                <p style='color: #E8FFE8; margin: 10px 0 0 0; font-size: 1.1em;'>Analyse des compétences techniques et maîtrise du ballon</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des actions techniques avec style football
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
                        color=COLORS['gradient'],
                        line=dict(color='white', width=2)
                    ),
                    text=list(actions_tech.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Arial Black')
                )])
                
                fig_bar_tech.update_layout(
                    title=dict(
                        text="🎨 Actions Techniques 🎨",
                        font=dict(size=18, color='white', family='Arial Black'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', size=12, family='Arial Black'),
                        tickangle=45
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', size=12),
                        gridcolor='rgba(255,255,255,0.3)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(50,205,50,0.2)',
                    font=dict(color='white'),
                    height=400
                )
                st.plotly_chart(fig_bar_tech, use_container_width=True)
                
                # Radar technique professionnel
                st.markdown("""
                <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #32CD32 0%, #228B22 100%); border-radius: 10px; margin: 20px 0; border: 2px solid white;'>
                    <h3 style='color: #FFD700; margin: 0; font-weight: 900;'>🎨 RADAR TECHNIQUE PROFESSIONNEL 🎨</h3>
                </div>
                """, unsafe_allow_html=True)
                
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
                
                # Le reste du code pour les radars et graphiques techniques sera similaire...
                # [Continuer avec la même logique que pour les autres onglets]
                
            # Footer avec design football
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; padding: 25px; background: linear-gradient(135deg, #228B22 0%, #32CD32 50%, #228B22 100%); border-radius: 20px; margin-top: 30px; border: 4px solid white; position: relative; overflow: hidden;'>
                <div style='position: absolute; top: 10px; left: 20px; font-size: 2em; opacity: 0.2;'>⚽</div>
                <div style='position: absolute; bottom: 10px; right: 20px; font-size: 2em; opacity: 0.2;'>🏆</div>
                <div style='position: absolute; top: 50%; left: 10px; font-size: 1.5em; opacity: 0.1; transform: rotate(-20deg);'>🥅</div>
                <div style='position: absolute; top: 50%; right: 10px; font-size: 1.5em; opacity: 0.1; transform: rotate(20deg);'>👕</div>
                <h3 style='color: white; margin: 0; font-size: 1.8em; font-weight: 900;'>
                    ⚽ FOOTBALL ANALYTICS DASHBOARD PRO ⚽
                </h3>
                <p style='color: #E8F5E8; margin: 10px 0 5px 0; font-size: 1.2em; font-weight: bold;'>
                    🏟️ Analyse Professionnelle des Performances - Saison 2024-25 🏟️
                </p>
                <p style='color: #C8E6C9; margin: 5px 0 0 0; font-size: 1em;'>
                    📊 Données: FBRef | 🎨 Design: Football Dashboard Pro | ⚽ Powered by Streamlit
                </p>
            </div>
            """, unsafe_allow_html=True)

else:
    # Message d'erreur avec design football
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #DC143C 0%, #B22222 100%); border-radius: 20px; margin: 20px 0; border: 4px solid white; position: relative; overflow: hidden;'>
        <div style='position: absolute; top: -10px; left: -10px; font-size: 3em; opacity: 0.2; transform: rotate(-15deg);'>⚠️</div>
        <div style='position: absolute; bottom: -10px; right: -10px; font-size: 3em; opacity: 0.2; transform: rotate(15deg);'>🚫</div>
        <h2 style='color: white; margin: 0; font-size: 2.5em; font-weight: 900;'>⚠️ ERREUR DE CHARGEMENT ⚠️</h2>
        <p style='color: #FFE8E8; margin: 20px 0 0 0; font-size: 1.3em; font-weight: bold;'>
            🚫 Impossible de charger les données du championnat 🚫
        </p>
        <p style='color: #FFD0D0; margin: 15px 0 0 0; font-size: 1.1em;'>
            📂 Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent dans le répertoire
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Ce dashboard de football nécessite un fichier CSV avec les statistiques des joueurs conformes au format FBRef.")
