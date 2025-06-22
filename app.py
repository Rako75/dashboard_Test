import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration de la page avec thème moderne
st.set_page_config(
    page_title="Dashboard Joueur Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.streamlit.io',
        'Report a bug': None,
        'About': "Dashboard Football Professionnel v2.0"
    }
)

# Utilisation du nouveau système de thème Streamlit
st.markdown("""
<style>
    /* Variables CSS modernes */
    :root {
        --primary-color: #FF6B35;
        --secondary-color: #004E89;
        --accent-color: #1A759F;
        --success-color: #00C896;
        --warning-color: #F7B801;
        --danger-color: #D62828;
        --dark-color: #1E2640;
        --light-color: #F8F9FA;
    }
    
    /* Interface moderne avec glassmorphism */
    .main > div {
        background: linear-gradient(135deg, rgba(14, 17, 23, 0.95) 0%, rgba(30, 38, 64, 0.95) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Containers avec effet de profondeur */
    .stContainer {
        background: rgba(30, 38, 64, 0.6);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Tabs modernes */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, rgba(30, 38, 64, 0.8) 0%, rgba(45, 55, 72, 0.8) 100%);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #FFFFFF;
        border-radius: 12px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 107, 53, 0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF6B35 0%, #F77F00 100%);
        color: #FFFFFF;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
    }
    
    /* Métriques avec animations */
    .stMetric {
        background: linear-gradient(135deg, rgba(45, 55, 72, 0.8) 0%, rgba(74, 85, 104, 0.8) 100%);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
        border-color: rgba(255, 107, 53, 0.5);
    }
    
    /* Sidebar moderne */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(30, 38, 64, 0.95) 0%, rgba(45, 55, 72, 0.95) 100%);
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Animations pour les éléments interactifs */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .metric-card {
        animation: fadeInUp 0.6s ease-out;
        background: linear-gradient(135deg, rgba(30, 38, 64, 0.8) 0%, rgba(45, 55, 72, 0.8) 100%);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 60px rgba(255, 107, 53, 0.2);
    }
    
    /* Headers avec effet néon */
    .neon-text {
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.8),
                     0 0 20px rgba(255, 107, 53, 0.6),
                     0 0 30px rgba(255, 107, 53, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Couleurs modernes avec support du thème sombre
COLORS = {
    'primary': '#FF6B35',
    'secondary': '#004E89', 
    'accent': '#1A759F',
    'success': '#00C896',
    'warning': '#F7B801',
    'danger': '#D62828',
    'dark': '#1E2640',
    'light': '#F8F9FA',
    'gradient': ['#FF6B35', '#004E89', '#1A759F', '#00C896', '#F7B801'],
    'glassmorphism': 'rgba(255, 255, 255, 0.1)'
}

# Configuration des graphiques avec thème moderne
def setup_modern_plotly_theme():
    """Configure un thème moderne pour Plotly"""
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': 'white', 'family': 'Inter, sans-serif'},
        'colorway': COLORS['gradient'],
        'template': 'plotly_dark'
    }

# ---------------------- PARAMÈTRES DU RADAR (inchangés) ----------------------
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

@st.cache_data(ttl=3600, show_spinner="Chargement des données...")
def load_data():
    """Charge les données depuis le fichier CSV avec cache optimisé"""
    try:
        df = pd.read_csv('df_BIG2025.csv', encoding='utf-8')
        # Optimisation mémoire
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='integer')
        return df
    except FileNotFoundError:
        st.error("📁 Fichier 'df_BIG2025.csv' non trouvé. Veuillez vous assurer que le fichier est dans le même répertoire.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
        return None

def create_modern_metric_card(title, value, delta=None, delta_color="normal"):
    """Crée une carte métrique moderne avec animations"""
    delta_html = ""
    if delta is not None:
        color = "#00C896" if delta_color == "normal" else "#D62828" if delta_color == "inverse" else "#F7B801"
        delta_html = f'<p style="color: {color}; font-size: 0.9em; margin: 5px 0 0 0;">{"+" if delta > 0 else ""}{delta}</p>'
    
    return f"""
    <div class="metric-card">
        <h3 style="color: #FF6B35; margin: 0; font-size: 1.1em;">{title}</h3>
        <p style="color: white; font-size: 2em; font-weight: bold; margin: 10px 0;">{value}</p>
        {delta_html}
    </div>
    """

def create_enhanced_radar_chart(metrics, values, avg_values, title, color_primary, color_secondary):
    """Crée un radar chart moderne avec animations et interactivité"""
    fig = go.Figure()
    
    # Performance du joueur avec effet de glow
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=list(metrics.keys()),
        fill='toself',
        fillcolor=f'rgba({int(color_primary[1:3], 16)}, {int(color_primary[3:5], 16)}, {int(color_primary[5:7], 16)}, 0.3)',
        line=dict(color=color_primary, width=4),
        marker=dict(color=color_primary, size=10, symbol='circle', 
                   line=dict(color='white', width=2)),
        name='Performance',
        hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
        customdata=list(metrics.values())
    ))
    
    # Moyenne de la compétition
    fig.add_trace(go.Scatterpolar(
        r=avg_values,
        theta=list(metrics.keys()),
        mode='lines',
        line=dict(color='rgba(255,255,255,0.7)', width=3, dash='dash'),
        name='Moyenne Compétition',
        hovertemplate='<b>%{theta}</b><br>Moyenne: %{customdata:.2f}<extra></extra>',
        customdata=list(metrics.values())
    ))
    
    # Mise en page moderne avec glassmorphism
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.2)',
                tickcolor='white',
                tickfont=dict(color='white', size=11, family='Inter'),
                showticklabels=True,
                tickmode='linear',
                tick0=0,
                dtick=25,
                gridwidth=1
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.2)',
                tickcolor='white',
                tickfont=dict(color='white', size=12, family='Inter', weight='bold'),
                linecolor='rgba(255,255,255,0.3)',
                gridwidth=1
            ),
            bgcolor='rgba(30, 38, 64, 0.4)'
        ),
        **setup_modern_plotly_theme(),
        title=dict(
            text=title,
            font=dict(size=18, color='white', family='Inter', weight='bold'),
            x=0.5,
            y=0.95
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color='white', size=11, family='Inter'),
            bgcolor='rgba(30, 38, 64, 0.6)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        height=500,
        showlegend=True
    )
    
    return fig

# Chargement des données avec spinner moderne
with st.spinner('🔄 Chargement des données...'):
    df = load_data()

if df is not None:
    # Header moderne avec effet néon
    st.markdown("""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(255, 107, 53, 0.2) 0%, rgba(0, 78, 137, 0.2) 100%); 
                backdrop-filter: blur(15px); border-radius: 25px; margin-bottom: 30px; border: 1px solid rgba(255, 255, 255, 0.1);'>
        <h1 class='neon-text' style='color: white; margin: 0; font-size: 3.5em; font-family: Inter, sans-serif; font-weight: 800;'>
            ⚽ Dashboard Football Analytics
        </h1>
        <p style='color: #E2E8F0; margin: 15px 0 0 0; font-size: 1.3em; font-family: Inter, sans-serif;'>
            🚀 Analyse Avancée des Performances - Saison 2024-25
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar modernisée avec st.container
    with st.sidebar:
        with st.container():
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(30, 38, 64, 0.8) 0%, rgba(45, 55, 72, 0.8) 100%); 
                        backdrop-filter: blur(15px); padding: 25px; border-radius: 20px; margin-bottom: 25px;
                        border: 1px solid rgba(255, 255, 255, 0.1);'>
                <h2 style='color: #FF6B35; text-align: center; margin-bottom: 20px; font-family: Inter, sans-serif;'>
                    🎯 Configuration
                </h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Utilisation des nouveaux widgets Streamlit
            competitions = sorted(df['Compétition'].dropna().unique())
            selected_competition = st.selectbox(
                "🏆 Choisir une compétition :",
                competitions,
                index=0,
                help="Sélectionnez la compétition pour filtrer les joueurs"
            )
            
            # Filtrer les joueurs selon la compétition
            df_filtered = df[df['Compétition'] == selected_competition]
            
            # Nouveau widget range slider pour les minutes
            min_minutes = int(df_filtered['Minutes jouées'].min()) if not df_filtered['Minutes jouées'].empty else 0
            max_minutes = int(df_filtered['Minutes jouées'].max()) if not df_filtered['Minutes jouées'].empty else 3000
            
            st.markdown("---")
            
            # Utilisation du nouveau widget number_input avec step
            min_minutes_filter = st.number_input(
                "⏱️ Minutes minimum jouées :",
                min_value=min_minutes,
                max_value=max_minutes,
                value=min_minutes,
                step=90,
                help="Filtrer les joueurs ayant joué au minimum ce nombre de minutes"
            )
            
            # Filtrer selon les minutes avec progress bar
            df_filtered_minutes = df_filtered[df_filtered['Minutes jouées'] >= min_minutes_filter]
            
            # Indicateur moderne du nombre de joueurs
            nb_joueurs = len(df_filtered_minutes)
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(0, 200, 150, 0.2) 0%, rgba(26, 117, 159, 0.2) 100%);
                        backdrop-filter: blur(10px); padding: 15px; border-radius: 15px; text-align: center;
                        border: 1px solid rgba(255, 255, 255, 0.1);'>
                <h3 style='color: #00C896; margin: 0; font-family: Inter, sans-serif;'>
                    📊 {nb_joueurs} joueurs disponibles
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Sélection du joueur avec recherche améliorée
            if not df_filtered_minutes.empty:
                joueurs = sorted(df_filtered_minutes['Joueur'].dropna().unique())
                selected_player = st.selectbox(
                    "👤 Choisir un joueur :",
                    joueurs,
                    index=0,
                    help="Sélectionnez le joueur à analyser"
                )
            else:
                st.error("⚠️ Aucun joueur ne correspond aux critères sélectionnés.")
                selected_player = None
    
    # Interface principale modernisée
    if selected_player:
        player_data = df_filtered_minutes[df_filtered_minutes['Joueur'] == selected_player].iloc[0]
        df_comparison = df_filtered_minutes
    
        # Profil du joueur avec design glassmorphism
        with st.container():
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(30, 38, 64, 0.6) 0%, rgba(45, 55, 72, 0.6) 100%); 
                        backdrop-filter: blur(15px); padding: 30px; border-radius: 25px; margin: 25px 0; 
                        border: 2px solid rgba(255, 107, 53, 0.3); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);'>
                <h2 style='color: #FF6B35; text-align: center; margin-bottom: 25px; font-family: Inter, sans-serif; font-weight: 700;'>
                    📊 Profil de {selected_player}
                </h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Métriques avec nouveau layout responsive
            col1, col2, col3, col4, col5 = st.columns(5)
            
            metrics_data = [
                ("Âge", f"{player_data['Âge']} ans"),
                ("Position", player_data['Position']),
                ("Équipe", player_data['Équipe']),
                ("Nationalité", player_data['Nationalité']),
                ("Minutes", f"{int(player_data['Minutes jouées'])} min")
            ]
            
            for col, (title, value) in zip([col1, col2, col3, col4, col5], metrics_data):
                with col:
                    st.markdown(create_modern_metric_card(title, value), unsafe_allow_html=True)
        
        st.markdown("---")
    
        # Tabs modernisés avec nouveaux noms et icônes
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Performance Offensive", 
            "🛡️ Performance Défensive", 
            "🎨 Maîtrise Technique", 
            "🔄 Comparaison Radar",
            "📈 Analytics Avancées"
        ])
        
        with tab1:
            st.markdown("<h2 style='color: #FF6B35; font-family: Inter, sans-serif;'>🎯 Performance Offensive</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                # Graphique moderne avec nouvelles animations
                actions_off = {
                    'Buts': player_data['Buts'],
                    'Passes décisives': player_data['Passes décisives'],
                    'Passes clés': player_data['Passes clés'],
                    'Actions → Tir': player_data.get('Actions menant à un tir', 0),
                    'Tirs': player_data.get('Tirs', 0)
                }
                
                fig_bar_off = go.Figure()
                
                # Ajout d'un effet de gradient sur les barres
                fig_bar_off.add_trace(go.Bar(
                    x=list(actions_off.keys()),
                    y=list(actions_off.values()),
                    marker=dict(
                        color=COLORS['gradient'],
                        line=dict(color='rgba(255,255,255,0.8)', width=2),
                        opacity=0.9
                    ),
                    text=list(actions_off.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Inter', weight='bold'),
                    hovertemplate='<b>%{x}</b><br>Valeur: %{y}<extra></extra>'
                ))
                
                fig_bar_off.update_layout(
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text="🎯 Actions Offensives",
                        font=dict(size=18, color='white', family='Inter', weight='bold'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', family='Inter'),
                        tickangle=45,
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', family='Inter'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    height=450,
                    margin=dict(t=80, b=60, l=60, r=60)
                )
                
                st.plotly_chart(fig_bar_off, use_container_width=True, key="off_bar")
                
                # Radar offensif avec nouvelles métriques
                st.markdown("<h3 style='color: #00C896; margin-top: 30px; font-family: Inter, sans-serif;'>🎯 Radar Offensif Avancé</h3>", unsafe_allow_html=True)
                
                offensive_metrics = {
                    'Buts/90': player_data['Buts par 90 minutes'],
                    'Passes D./90': player_data['Passes décisives par 90 minutes'],
                    'xG/90': player_data['Buts attendus par 90 minutes'],
                    'xA/90': player_data['Passes décisives attendues par 90 minutes'],
                    'Tirs/90': player_data['Tirs par 90 minutes'],
                    'Passes clés/90': player_data['Passes clés'] / (player_data['Minutes jouées'] / 90),
                    'Dribbles/90': player_data['Dribbles réussis'] / (player_data['Minutes jouées'] / 90),
                    'Actions→Tir/90': player_data['Actions menant à un tir par 90 minutes']
                }
                
                # Calcul des percentiles amélioré
                percentiles = []
                avg_values = []
                
                for metric, value in offensive_metrics.items():
                    try:
                        if metric == 'Buts/90':
                            dist = df_comparison['Buts par 90 minutes']
                        elif metric == 'Passes D./90':
                            dist = df_comparison['Passes décisives par 90 minutes']
                        elif metric == 'xG/90':
                            dist = df_comparison['Buts attendus par 90 minutes']
                        elif metric == 'xA/90':
                            dist = df_comparison['Passes décisives attendues par 90 minutes']
                        elif metric == 'Tirs/90':
                            dist = df_comparison['Tirs par 90 minutes']
                        elif metric == 'Actions→Tir/90':
                            dist = df_comparison['Actions menant à un tir par 90 minutes']
                        else:
                            base_col = metric.replace('/90', '').replace('Passes D.', 'Passes décisives')
                            dist = df_comparison[base_col] / (df_comparison['Minutes jouées'] / 90)
                        
                        percentile = (dist < value).mean() * 100
                        avg_val = dist.mean()
                        
                        percentiles.append(min(percentile, 100))
                        avg_values.append(avg_val)
                    except:
                        percentiles.append(50)
                        avg_values.append(0)
                
                # Calcul des percentiles des moyennes
                avg_percentiles = []
                for i, avg_val in enumerate(avg_values):
                    if avg_val > 0:
                        metric_name = list(offensive_metrics.keys())[i]
                        if metric_name == 'Buts/90':
                            dist = df_comparison['Buts par 90 minutes']
                        elif metric_name == 'Passes D./90':
                            dist = df_comparison['Passes décisives par 90 minutes']
                        elif metric_name == 'xG/90':
                            dist = df_comparison['Buts attendus par 90 minutes']
                        elif metric_name == 'xA/90':
                            dist = df_comparison['Passes décisives attendues par 90 minutes']
                        elif metric_name == 'Tirs/90':
                            dist = df_comparison['Tirs par 90 minutes']
                        elif metric_name == 'Actions→Tir/90':
                            dist = df_comparison['Actions menant à un tir par 90 minutes']
                        else:
                            base_col = metric_name.replace('/90', '').replace('Passes D.', 'Passes décisives')
                            dist = df_comparison[base_col] / (df_comparison['Minutes jouées'] / 90)
                        
                        avg_percentile = (dist < avg_val).mean() * 100
                        avg_percentiles.append(avg_percentile)
                    else:
                        avg_percentiles.append(50)
                
                # Créer le radar moderne
                fig_radar_off = create_enhanced_radar_chart(
                    offensive_metrics, percentiles, avg_percentiles,
                    "🎯 Performance Offensive (Percentiles)",
                    COLORS['primary'], COLORS['secondary']
                )
                
                st.plotly_chart(fig_radar_off, use_container_width=True, key="off_radar")
            
            with col2:
                # Jauges modernes avec animations
                pourcentages_off = {
                    'Conversion Buts': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                    'Précision Tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                    'Efficacité Passes': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
                }
                
                # Nettoyer les valeurs NaN
                pourcentages_off = {k: v if pd.notna(v) else 0 for k, v in pourcentages_off.items()}
                
                # Créer des jauges modernes avec Plotly
                fig_gauge_off = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_off.keys()),
                    horizontal_spacing=0.1
                )
                
                colors_off = [COLORS['primary'], COLORS['secondary'], COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages_off.items()):
                    fig_gauge_off.add_trace(
                        go.Indicator(
                            mode="gauge+number+delta",
                            value=value,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': metric, 'font': {'color': 'white', 'size': 14}},
                            gauge=dict(
                                axis=dict(range=[0, 100], tickcolor='white', tickfont={'color': 'white'}),
                                bar=dict(color=colors_off[i], thickness=0.8),
                                bgcolor="rgba(30,38,64,0.6)",
                                borderwidth=3,
                                bordercolor="rgba(255,255,255,0.3)",
                                steps=[
                                    {'range': [0, 33], 'color': 'rgba(214,40,40,0.3)'},
                                    {'range': [33, 66], 'color': 'rgba(247,184,1,0.3)'},
                                    {'range': [66, 100], 'color': 'rgba(0,200,150,0.3)'}
                                ],
                                threshold={
                                    'line': {'color': "white", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            ),
                            number={'suffix': '%', 'font': {'color': 'white', 'size': 20}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_off.update_layout(
                    height=350,
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text="📊 Efficacité Offensive",
                        font=dict(size=18, color='white', family='Inter'),
                        x=0.5
                    ),
                    margin=dict(t=80, b=50, l=50, r=50)
                )
                
                st.plotly_chart(fig_gauge_off, use_container_width=True, key="off_gauge")
                
                # Graphique de comparaison moderne avec animation
                st.markdown("<h3 style='color: #1A759F; margin-top: 20px; font-family: Inter, sans-serif;'>📈 Comparaison vs Moyenne</h3>", unsafe_allow_html=True)
                
                offensive_comparison = {
                    'Buts/90': player_data['Buts par 90 minutes'],
                    'Passes D./90': player_data['Passes décisives par 90 minutes'],
                    'xG/90': player_data['Buts attendus par 90 minutes']
                }
                
                avg_comparison_off = {
                    'Buts/90': df_comparison['Buts par 90 minutes'].mean(),
                    'Passes D./90': df_comparison['Passes décisives par 90 minutes'].mean(),
                    'xG/90': df_comparison['Buts attendus par 90 minutes'].mean()
                }
                
                fig_off_comp = go.Figure()
                
                # Barres du joueur avec effet de glow
                fig_off_comp.add_trace(go.Bar(
                    name=selected_player,
                    x=list(offensive_comparison.keys()),
                    y=list(offensive_comparison.values()),
                    marker=dict(
                        color=COLORS['primary'],
                        line=dict(color='white', width=2),
                        opacity=0.9
                    ),
                    text=[f"{v:.2f}" for v in offensive_comparison.values()],
                    textposition='outside',
                    textfont=dict(color='white', size=12, family='Inter'),
                    hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.2f}<extra></extra>'
                ))
                
                # Barres de la moyenne
                fig_off_comp.add_trace(go.Bar(
                    name=f'Moyenne {selected_competition}',
                    x=list(avg_comparison_off.keys()),
                    y=list(avg_comparison_off.values()),
                    marker=dict(
                        color=COLORS['secondary'],
                        line=dict(color='white', width=2),
                        opacity=0.7
                    ),
                    text=[f"{v:.2f}" for v in avg_comparison_off.values()],
                    textposition='outside',
                    textfont=dict(color='white', size=12, family='Inter'),
                    hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:.2f}<extra></extra>'
                ))
                
                fig_off_comp.update_layout(
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text='🆚 Performance vs Moyenne Compétition',
                        font=dict(color='white', size=16, family='Inter'),
                        x=0.5
                    ),
                    barmode='group',
                    bargap=0.2,
                    bargroupgap=0.1,
                    xaxis=dict(
                        tickfont=dict(color='white', family='Inter'),
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', family='Inter'),
                        gridcolor='rgba(255,255,255,0.2)',
                        title=dict(text='Valeur par 90min', font=dict(color='white'))
                    ),
                    height=400,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        font=dict(color='white', family='Inter')
                    )
                )
                
                st.plotly_chart(fig_off_comp, use_container_width=True, key="off_comp")
            
            # Section d'analyse avancée avec nouveau design
            st.markdown("---")
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px; font-family: Inter, sans-serif;'>🔍 Analyse Offensive Approfondie</h3>", unsafe_allow_html=True)
            
            col_analysis1, col_analysis2 = st.columns([2, 1])
            
            with col_analysis1:
                # Scatter plot interactif moderne
                metric_options_off = [
                    'Buts', 'Passes décisives', 'Tirs', 'Buts attendus (xG)',
                    'Passes décisives attendues (xAG)', 'Passes clés', 'Actions menant à un tir',
                    'Pourcentage de tirs cadrés'
                ]
                
                col_select1, col_select2 = st.columns(2)
                with col_select1:
                    x_metric_off = st.selectbox("📊 Métrique X", metric_options_off, index=0, key="x_off")
                with col_select2:
                    y_metric_off = st.selectbox("📈 Métrique Y", metric_options_off, index=1, key="y_off")
                
                # Créer le scatter plot moderne
                fig_scatter_off = go.Figure()
                
                # Conversion en par 90 minutes si nécessaire
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
                
                # Points des autres joueurs avec effet de transparence
                fig_scatter_off.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(
                        color=COLORS['accent'], 
                        size=8, 
                        opacity=0.6,
                        line=dict(color='white', width=0.5)
                    ),
                    text=df_comparison['Joueur'],
                    customdata=df_comparison[['Équipe', 'Position']],
                    hovertemplate='<b>%{text}</b><br>Équipe: %{customdata[0]}<br>Position: %{customdata[1]}<br>' + 
                                 x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                # Point du joueur sélectionné avec animation
                fig_scatter_off.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(
                        color=COLORS['primary'], 
                        size=25, 
                        symbol='star',
                        line=dict(color='white', width=3)
                    ),
                    hovertemplate=f'<b>{selected_player}</b><br>Équipe: {player_data["Équipe"]}<br>Position: {player_data["Position"]}<br>' + 
                                 x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                # Lignes de référence pour les moyennes
                fig_scatter_off.add_hline(
                    y=y_data.mean(), 
                    line_dash="dash", 
                    line_color="rgba(255,255,255,0.5)",
                    annotation_text=f"Moyenne {y_title}: {y_data.mean():.2f}",
                    annotation_position="top left"
                )
                fig_scatter_off.add_vline(
                    x=x_data.mean(), 
                    line_dash="dash", 
                    line_color="rgba(255,255,255,0.5)",
                    annotation_text=f"Moyenne {x_title}: {x_data.mean():.2f}",
                    annotation_position="top right"
                )
                
                fig_scatter_off.update_layout(
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text=f"🔍 {x_title} vs {y_title}",
                        font=dict(size=16, color='white', family='Inter'),
                        x=0.5
                    ),
                    xaxis=dict(
                        title=dict(text=x_title, font=dict(color='white', family='Inter')),
                        tickfont=dict(color='white', family='Inter'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    yaxis=dict(
                        title=dict(text=y_title, font=dict(color='white', family='Inter')),
                        tickfont=dict(color='white', family='Inter'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    height=450,
                    showlegend=True,
                    legend=dict(
                        font=dict(color='white', family='Inter'),
                        bgcolor='rgba(30,38,64,0.6)',
                        bordercolor='rgba(255,255,255,0.2)',
                        borderwidth=1
                    )
                )
                
                st.plotly_chart(fig_scatter_off, use_container_width=True, key="off_scatter")
            
            with col_analysis2:
                # Métriques avancées avec nouveaux indicateurs
                st.markdown("##### 📊 Métriques Avancées")
                
                # Calcul d'indices personnalisés
                offensive_index = (
                    player_data['Buts par 90 minutes'] * 3 +
                    player_data['Passes décisives par 90 minutes'] * 2 +
                    player_data['Actions menant à un tir par 90 minutes'] * 1
                ) / 6
                
                finishing_quality = (
                    player_data['Buts'] / player_data['Buts attendus (xG)'] * 100
                    if player_data['Buts attendus (xG)'] > 0 else 100
                )
                
                creativity_index = (
                    player_data['Passes clés'] / (player_data['Minutes jouées'] / 90) +
                    player_data['Passes décisives attendues par 90 minutes']
                ) / 2
                
                metrics_advanced = [
                    ("🎯 Indice Offensif", f"{offensive_index:.2f}"),
                    ("🏹 Qualité de Finition", f"{finishing_quality:.1f}%"),
                    ("🎨 Indice Créativité", f"{creativity_index:.2f}"),
                    ("⚡ Actions/90min", f"{player_data['Actions menant à un tir par 90 minutes']:.2f}"),
                    ("🎪 Dribbles/90min", f"{player_data['Dribbles réussis'] / (player_data['Minutes jouées'] / 90):.2f}")
                ]
                
                for title, value in metrics_advanced:
                    st.markdown(create_modern_metric_card(title, value), unsafe_allow_html=True)
        
        with tab2:
            st.markdown("<h2 style='color: #FF6B35; font-family: Inter, sans-serif;'>🛡️ Performance Défensive</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                # Graphique des actions défensives modernisé
                actions_def = {
                    'Tacles': player_data['Tacles gagnants'],
                    'Interceptions': player_data['Interceptions'],
                    'Ballons récupérés': player_data['Ballons récupérés'],
                    'Duels aériens': player_data['Duels aériens gagnés'],
                    'Dégagements': player_data['Dégagements']
                }
                
                fig_bar_def = go.Figure()
                
                fig_bar_def.add_trace(go.Bar(
                    x=list(actions_def.keys()),
                    y=list(actions_def.values()),
                    marker=dict(
                        color=['#1A759F', '#004E89', '#00C896', '#F7B801', '#D62828'],
                        line=dict(color='rgba(255,255,255,0.8)', width=2),
                        opacity=0.9
                    ),
                    text=list(actions_def.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Inter', weight='bold'),
                    hovertemplate='<b>%{x}</b><br>Total: %{y}<br>Par 90min: %{customdata:.2f}<extra></extra>',
                    customdata=[v / (player_data['Minutes jouées'] / 90) for v in actions_def.values()]
                ))
                
                fig_bar_def.update_layout(
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text="🛡️ Actions Défensives",
                        font=dict(size=18, color='white', family='Inter', weight='bold'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', family='Inter'),
                        tickangle=45,
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', family='Inter'),
                        gridcolor='rgba(255,255,255,0.2)',
                        title=dict(text='Nombre d\'actions', font=dict(color='white'))
                    ),
                    height=450,
                    margin=dict(t=80, b=80, l=60, r=60)
                )
                
                st.plotly_chart(fig_bar_def, use_container_width=True, key="def_bar")
                
                # Radar défensif avancé
                st.markdown("<h3 style='color: #00C896; margin-top: 30px; font-family: Inter, sans-serif;'>🛡️ Radar Défensif Avancé</h3>", unsafe_allow_html=True)
                
                defensive_metrics = {
                    'Tacles/90': player_data['Tacles gagnants'] / (player_data['Minutes jouées'] / 90),
                    'Interceptions/90': player_data['Interceptions'] / (player_data['Minutes jouées'] / 90),
                    'Ballons récup./90': player_data['Ballons récupérés'] / (player_data['Minutes jouées'] / 90),
                    'Duels défensifs/90': player_data.get('Duels défensifs gagnés', 0) / (player_data['Minutes jouées'] / 90),
                    'Duels aériens/90': player_data['Duels aériens gagnés'] / (player_data['Minutes jouées'] / 90),
                    'Dégagements/90': player_data['Dégagements'] / (player_data['Minutes jouées'] / 90),
                    '% Duels réussis': player_data.get('Pourcentage de duels gagnés', 0),
                    '% Duels aériens': player_data['Pourcentage de duels aériens gagnés']
                }
                
                # Calcul des percentiles défensifs
                def_percentiles = []
                def_avg_values = []
                
                for metric, value in defensive_metrics.items():
                    try:
                        if metric == 'Tacles/90':
                            dist = df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Interceptions/90':
                            dist = df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Ballons récup./90':
                            dist = df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Duels défensifs/90':
                            dist = df_comparison.get('Duels défensifs gagnés', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Duels aériens/90':
                            dist = df_comparison['Duels aériens gagnés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Dégagements/90':
                            dist = df_comparison['Dégagements'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == '% Duels réussis':
                            dist = df_comparison.get('Pourcentage de duels gagnés', pd.Series([0]*len(df_comparison)))
                        elif metric == '% Duels aériens':
                            dist = df_comparison['Pourcentage de duels aériens gagnés']
                        
                        dist = dist.replace([np.inf, -np.inf], np.nan).dropna()
                        value = value if not np.isnan(value) and not np.isinf(value) else 0
                        
                        if len(dist) > 0:
                            percentile = (dist < value).mean() * 100
                            avg_val = dist.mean()
                        else:
                            percentile = 50
                            avg_val = 0
                        
                        def_percentiles.append(min(percentile, 100))
                        def_avg_values.append(avg_val)
                    except:
                        def_percentiles.append(50)
                        def_avg_values.append(0)
                
                # Calcul des percentiles des moyennes
                def_avg_percentiles = []
                for i, avg_val in enumerate(def_avg_values):
                    try:
                        if avg_val > 0:
                            metric_name = list(defensive_metrics.keys())[i]
                            if metric_name == 'Tacles/90':
                                dist = df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Interceptions/90':
                                dist = df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)
                            # ... autres métriques
                            
                            dist = dist.replace([np.inf, -np.inf], np.nan).dropna()
                            if len(dist) > 0:
                                avg_percentile = (dist < avg_val).mean() * 100
                                def_avg_percentiles.append(avg_percentile)
                            else:
                                def_avg_percentiles.append(50)
                        else:
                            def_avg_percentiles.append(50)
                    except:
                        def_avg_percentiles.append(50)
                
                # Créer le radar défensif
                fig_radar_def = create_enhanced_radar_chart(
                    defensive_metrics, def_percentiles, def_avg_percentiles,
                    "🛡️ Performance Défensive (Percentiles)",
                    COLORS['accent'], COLORS['secondary']
                )
                
                st.plotly_chart(fig_radar_def, use_container_width=True, key="def_radar")
            
            with col2:
                # Jauges défensives modernes
                pourcentages_def = {
                    'Duels Aériens': player_data['Pourcentage de duels aériens gagnés'],
                    'Duels Défensifs': player_data.get('Pourcentage de duels gagnés', 0),
                    'Passes Réussies': player_data['Pourcentage de passes réussies']
                }
                
                pourcentages_def = {k: v if pd.notna(v) else 0 for k, v in pourcentages_def.items()}
                
                fig_gauge_def = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_def.keys()),
                    horizontal_spacing=0.1
                )
                
                colors_def = [COLORS['danger'], COLORS['secondary'], COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages_def.items()):
                    fig_gauge_def.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100], tickcolor='white', tickfont={'color': 'white'}),
                                bar=dict(color=colors_def[i], thickness=0.8),
                                bgcolor="rgba(30,38,64,0.6)",
                                borderwidth=3,
                                bordercolor="rgba(255,255,255,0.3)",
                                steps=[
                                    {'range': [0, 50], 'color': 'rgba(214,40,40,0.3)'},
                                    {'range': [50, 75], 'color': 'rgba(247,184,1,0.3)'},
                                    {'range': [75, 100], 'color': 'rgba(0,200,150,0.3)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': 'white', 'size': 20}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_def.update_layout(
                    height=350,
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text="📊 Efficacité Défensive",
                        font=dict(size=18, color='white', family='Inter'),
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig_gauge_def, use_container_width=True, key="def_gauge")
                
                # Métriques défensives détaillées
                st.markdown("##### 🛡️ Métriques Défensives/90min")
                
                minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
                
                defensive_stats = [
                    ("🥅 Tacles", f"{player_data['Tacles gagnants'] / minutes_90:.2f}"),
                    ("🚫 Interceptions", f"{player_data['Interceptions'] / minutes_90:.2f}"),
                    ("⚽ Ballons récupérés", f"{player_data['Ballons récupérés'] / minutes_90:.2f}"),
                    ("🦘 Duels aériens", f"{player_data['Duels aériens gagnés'] / minutes_90:.2f}"),
                    ("🛡️ Indice Défensif", f"{(player_data['Tacles gagnants'] + player_data['Interceptions'] + player_data['Ballons récupérés']) / minutes_90:.2f}")
                ]
                
                for title, value in defensive_stats:
                    st.markdown(create_modern_metric_card(title, value), unsafe_allow_html=True)
        
        with tab3:
            st.markdown("<h2 style='color: #FF6B35; font-family: Inter, sans-serif;'>🎨 Maîtrise Technique</h2>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                # Graphique technique moderne
                actions_tech = {
                    'Passes tentées': player_data['Passes tentées'],
                    'Passes progressives': player_data.get('Passes progressives', 0),
                    'Dribbles tentés': player_data['Dribbles tentés'],
                    'Touches': player_data['Touches de balle'],
                    'Passes clés': player_data['Passes clés']
                }
                
                fig_bar_tech = go.Figure()
                
                fig_bar_tech.add_trace(go.Bar(
                    x=list(actions_tech.keys()),
                    y=list(actions_tech.values()),
                    marker=dict(
                        color=COLORS['gradient'],
                        line=dict(color='rgba(255,255,255,0.8)', width=2),
                        opacity=0.9
                    ),
                    text=list(actions_tech.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Inter', weight='bold'),
                    hovertemplate='<b>%{x}</b><br>Total: %{y}<br>Par 90min: %{customdata:.2f}<extra></extra>',
                    customdata=[v / (player_data['Minutes jouées'] / 90) for v in actions_tech.values()]
                ))
                
                fig_bar_tech.update_layout(
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text="🎨 Actions Techniques",
                        font=dict(size=18, color='white', family='Inter', weight='bold'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color='white', family='Inter'),
                        tickangle=45,
                        gridcolor='rgba(255,255,255,0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color='white', family='Inter'),
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    height=450
                )
                
                st.plotly_chart(fig_bar_tech, use_container_width=True, key="tech_bar")
                
                # Radar technique avancé
                st.markdown("<h3 style='color: #00C896; margin-top: 30px; font-family: Inter, sans-serif;'>🎨 Radar Technique Avancé</h3>", unsafe_allow_html=True)
                
                technical_metrics = {
                    'Passes/90': player_data['Passes tentées'] / (player_data['Minutes jouées'] / 90),
                    'Passes prog./90': player_data.get('Passes progressives', 0) / (player_data['Minutes jouées'] / 90),
                    'Dribbles/90': player_data['Dribbles tentés'] / (player_data['Minutes jouées'] / 90),
                    'Touches/90': player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90),
                    'Passes clés/90': player_data['Passes clés'] / (player_data['Minutes jouées'] / 90),
                    '% Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                    '% Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                    'Distance prog./90': player_data.get('Distance progressive des passes', 0) / (player_data['Minutes jouées'] / 90)
                }
                
                # Calcul des percentiles techniques
                tech_percentiles = []
                tech_avg_values = []
                
                for metric, value in technical_metrics.items():
                    try:
                        if metric == 'Passes/90':
                            dist = df_comparison['Passes tentées'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Passes prog./90':
                            dist = df_comparison.get('Passes progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Dribbles/90':
                            dist = df_comparison['Dribbles tentés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Touches/90':
                            dist = df_comparison['Touches de balle'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == 'Passes clés/90':
                            dist = df_comparison['Passes clés'] / (df_comparison['Minutes jouées'] / 90)
                        elif metric == '% Passes réussies':
                            dist = df_comparison.get('Pourcentage de passes réussies', pd.Series([0]*len(df_comparison)))
                        elif metric == '% Dribbles réussis':
                            dist = df_comparison.get('Pourcentage de dribbles réussis', pd.Series([0]*len(df_comparison)))
                        elif metric == 'Distance prog./90':
                            dist = df_comparison.get('Distance progressive des passes', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                        
                        dist = dist.replace([np.inf, -np.inf], np.nan).dropna()
                        value = value if not np.isnan(value) and not np.isinf(value) else 0
                        
                        if len(dist) > 0:
                            percentile = (dist < value).mean() * 100
                            avg_val = dist.mean()
                        else:
                            percentile = 50
                            avg_val = 0
                        
                        tech_percentiles.append(min(percentile, 100))
                        tech_avg_values.append(avg_val)
                    except:
                        tech_percentiles.append(50)
                        tech_avg_values.append(0)
                
                # Calcul des percentiles des moyennes techniques
                tech_avg_percentiles = []
                for i, avg_val in enumerate(tech_avg_values):
                    try:
                        if avg_val > 0:
                            metric_name = list(technical_metrics.keys())[i]
                            if metric_name == 'Passes/90':
                                dist = df_comparison['Passes tentées'] / (df_comparison['Minutes jouées'] / 90)
                            elif metric_name == 'Passes prog./90':
                                dist = df_comparison.get('Passes progressives', pd.Series([0]*len(df_comparison))) / (df_comparison['Minutes jouées'] / 90)
                            # Autres métriques...
                            
                            dist = dist.replace([np.inf, -np.inf], np.nan).dropna()
                            if len(dist) > 0:
                                avg_percentile = (dist < avg_val).mean() * 100
                                tech_avg_percentiles.append(avg_percentile)
                            else:
                                tech_avg_percentiles.append(50)
                        else:
                            tech_avg_percentiles.append(50)
                    except:
                        tech_avg_percentiles.append(50)
                
                # Créer le radar technique
                fig_radar_tech = create_enhanced_radar_chart(
                    technical_metrics, tech_percentiles, tech_avg_percentiles,
                    "🎨 Performance Technique (Percentiles)",
                    COLORS['success'], COLORS['secondary']
                )
                
                st.plotly_chart(fig_radar_tech, use_container_width=True, key="tech_radar")
            
            with col2:
                # Jauges techniques avec design moderne
                pourcentages_tech = {
                    'Passes Réussies': player_data.get('Pourcentage de passes réussies', 0),
                    'Dribbles Réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                    'Passes Longues': player_data.get('Pourcentage de passes longues réussies', 0)
                }
                
                pourcentages_tech = {k: v if pd.notna(v) else 0 for k, v in pourcentages_tech.items()}
                
                fig_gauge_tech = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_tech.keys()),
                    horizontal_spacing=0.1
                )
                
                colors_tech = [COLORS['success'], COLORS['warning'], COLORS['primary']]
                for i, (metric, value) in enumerate(pourcentages_tech.items()):
                    fig_gauge_tech.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100], tickcolor='white', tickfont={'color': 'white'}),
                                bar=dict(color=colors_tech[i], thickness=0.8),
                                bgcolor="rgba(30,38,64,0.6)",
                                borderwidth=3,
                                bordercolor="rgba(255,255,255,0.3)",
                                steps=[
                                    {'range': [0, 60], 'color': 'rgba(214,40,40,0.3)'},
                                    {'range': [60, 80], 'color': 'rgba(247,184,1,0.3)'},
                                    {'range': [80, 100], 'color': 'rgba(0,200,150,0.3)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': 'white', 'size': 20}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_tech.update_layout(
                    height=350,
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text="📊 Précision Technique",
                        font=dict(size=18, color='white', family='Inter'),
                        x=0.5
                    )
                )
                
                st.plotly_chart(fig_gauge_tech, use_container_width=True, key="tech_gauge")
                
                # Heatmap de progression du ballon
                st.markdown("##### 🎯 Progression du Ballon")
                
                progression_data = {
                    'Zone Défensive': player_data.get('Passes dans le tiers défensif', 0) / (player_data['Minutes jouées'] / 90),
                    'Zone Médiane': player_data.get('Passes dans le tiers médian', 0) / (player_data['Minutes jouées'] / 90),
                    'Zone Offensive': player_data.get('Passes dans le dernier tiers', 0) / (player_data['Minutes jouées'] / 90)
                }
                
                # Créer une heatmap moderne
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=[list(progression_data.values())],
                    y=['Progression'],
                    x=list(progression_data.keys()),
                    colorscale='Viridis',
                    text=[[f"{v:.1f}" for v in progression_data.values()]],
                    texttemplate="%{text}",
                    textfont={"size": 14, "color": "white"},
                    hoverongaps=False,
                    hovertemplate='<b>%{x}</b><br>Passes/90min: %{z:.1f}<extra></extra>'
                ))
                
                fig_heatmap.update_layout(
                    **setup_modern_plotly_theme(),
                    height=200,
                    margin=dict(t=20, b=20, l=20, r=20),
                    xaxis=dict(tickfont=dict(color='white')),
                    yaxis=dict(tickfont=dict(color='white'))
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True, key="tech_heatmap")
                
                # Métriques techniques avancées
                technical_stats = [
                    ("📏 Distance Passes", f"{player_data.get('Distance totale des passes', 0):.0f}m"),
                    ("🚀 Distance Progressive", f"{player_data.get('Distance progressive des passes', 0):.0f}m"),
                    ("🎪 Portée Ballon", f"{player_data.get('Distance totale parcourue avec le ballon (en mètres)', 0):.0f}m"),
                    ("🎯 Centres Surface", f"{player_data.get('Centres dans la surface', 0):.0f}"),
                    ("⚡ Indice Technique", f"{(player_data.get('Pourcentage de passes réussies', 0) + player_data.get('Pourcentage de dribbles réussis', 0)) / 2:.1f}%")
                ]
                
                for title, value in technical_stats:
                    st.markdown(create_modern_metric_card(title, value), unsafe_allow_html=True)
        
        with tab4:
            st.markdown("<h2 style='color: #FF6B35; font-family: Inter, sans-serif;'>🔄 Comparaison Pizza Chart</h2>", unsafe_allow_html=True)
            
            # Interface moderne pour la sélection du mode
            mode_container = st.container()
            with mode_container:
                st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(30, 38, 64, 0.6) 0%, rgba(45, 55, 72, 0.6) 100%); 
                            backdrop-filter: blur(15px); padding: 20px; border-radius: 15px; margin-bottom: 20px;
                            border: 1px solid rgba(255, 255, 255, 0.1);'>
                    <h3 style='color: #FF6B35; text-align: center; margin-bottom: 15px; font-family: Inter, sans-serif;'>
                        🎯 Mode de Visualisation
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                mode = st.radio(
                    "Choisissez le mode :",
                    ["🎯 Radar Individuel", "⚔️ Radar Comparatif"],
                    horizontal=True,
                    help="Sélectionnez le type d'analyse radar que vous souhaitez visualiser"
                )
            
            # Chargement des polices pour matplotlib
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            if mode == "🎯 Radar Individuel":
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(0, 200, 150, 0.2) 0%, rgba(255, 107, 53, 0.2) 100%);
                            backdrop-filter: blur(10px); padding: 20px; border-radius: 15px; margin: 20px 0;
                            border: 1px solid rgba(255, 255, 255, 0.1);'>
                    <h3 style='color: #00C896; text-align: center; margin: 0; font-family: Inter, sans-serif;'>
                        🎯 Analyse Individuelle : {selected_player}
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                try:
                    with st.spinner('🎨 Génération du radar individuel...'):
                        values1 = calculate_percentiles(selected_player, df_comparison)
                        
                        # Configuration du pizza chart avec style moderne
                        baker = PyPizza(
                            params=list(RAW_STATS.keys()),
                            background_color="#0E1117",
                            straight_line_color="#FFFFFF",
                            straight_line_lw=2,
                            last_circle_color="#FFFFFF",
                            last_circle_lw=2,
                            other_circle_lw=1,
                            other_circle_color="#888888",
                            inner_circle_size=15
                        )
                        
                        fig, ax = baker.make_pizza(
                            values1,
                            figsize=(14, 16),
                            param_location=110,
                            color_blank_space="same",
                            slice_colors=[COLORS['primary']] * len(values1),
                            value_colors=["#ffffff"] * len(values1),
                            value_bck_colors=[COLORS['primary']] * len(values1),
                            kwargs_slices=dict(
                                edgecolor="#FFFFFF", 
                                zorder=2, 
                                linewidth=2,
                                alpha=0.9
                            ),
                            kwargs_params=dict(
                                color="#ffffff", 
                                fontsize=14, 
                                fontproperties=font_bold.prop,
                                weight='bold'
                            ),
                            kwargs_values=dict(
                                color="#ffffff", 
                                fontsize=12, 
                                fontproperties=font_normal.prop,
                                bbox=dict(
                                    edgecolor="#FFFFFF", 
                                    facecolor=COLORS['primary'], 
                                    boxstyle="round,pad=0.3", 
                                    lw=1.5,
                                    alpha=0.9
                                )
                            )
                        )
                        
                        # Titre et sous-titres modernes
                        fig.text(0.515, 0.96, selected_player, 
                                size=32, ha="center", fontproperties=font_bold.prop, 
                                color="#ffffff", weight='bold')
                        fig.text(0.515, 0.935, f"{player_data['Position']} • {player_data['Équipe']} • {selected_competition}", 
                                size=16, ha="center", fontproperties=font_bold.prop, 
                                color="#E2E8F0")
                        fig.text(0.515, 0.915, "Radar Individuel | Percentiles vs Compétition | Saison 2024-25", 
                                size=14, ha="center", fontproperties=font_bold.prop, 
                                color="#A0AEC0")
                        
                        # Footer moderne
                        fig.text(0.99, 0.01, "🚀 Dashboard Football Pro | Data: FBRef | Design: Modern Analytics",
                                size=9, ha="right", fontproperties=font_italic.prop, 
                                color="#718096")
                        
                        # Gradient de fond
                        ax.set_facecolor('#0E1117')
                        
                        st.pyplot(fig, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors de la création du radar individuel : {str(e)}")
                    st.info("💡 Vérifiez que toutes les colonnes nécessaires sont présentes dans les données.")
            
            elif mode == "⚔️ Radar Comparatif":
                st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(255, 107, 53, 0.2) 0%, rgba(0, 78, 137, 0.2) 100%);
                            backdrop-filter: blur(10px); padding: 20px; border-radius: 15px; margin: 20px 0;
                            border: 1px solid rgba(255, 255, 255, 0.1);'>
                    <h3 style='color: #FF6B35; text-align: center; margin: 0; font-family: Inter, sans-serif;'>
                        ⚔️ Configuration de la Comparaison
                    </h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1], gap="large")
                
                with col1:
                    st.markdown("##### 👤 Joueur 1")
                    ligue1 = st.selectbox("🏆 Ligue Joueur 1", competitions, 
                                         index=competitions.index(selected_competition), key="ligue1_comp")
                    df_j1 = df[df['Compétition'] == ligue1]
                    joueur1 = st.selectbox("👤 Sélectionner Joueur 1", df_j1['Joueur'].sort_values(), 
                                          index=list(df_j1['Joueur'].sort_values()).index(selected_player), key="joueur1_comp")
                    
                    # Infos du joueur 1
                    if joueur1:
                        player1_data = df_j1[df_j1['Joueur'] == joueur1].iloc[0]
                        st.markdown(f"""
                        <div style='background: rgba(255, 107, 53, 0.1); padding: 15px; border-radius: 10px; 
                                    border: 1px solid rgba(255, 107, 53, 0.3);'>
                            <p style='color: white; margin: 0;'><strong>{player1_data['Position']}</strong> • {player1_data['Équipe']}</p>
                            <p style='color: #E2E8F0; margin: 5px 0 0 0;'>{int(player1_data['Minutes jouées'])} minutes jouées</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("##### 👤 Joueur 2")
                    ligue2 = st.selectbox("🏆 Ligue Joueur 2", competitions, key="ligue2_comp")
                    df_j2 = df[df['Compétition'] == ligue2]
                    joueur2 = st.selectbox("👤 Sélectionner Joueur 2", df_j2['Joueur'].sort_values(), key="joueur2_comp")
                    
                    # Infos du joueur 2
                    if joueur2:
                        player2_data = df_j2[df_j2['Joueur'] == joueur2].iloc[0]
                        st.markdown(f"""
                        <div style='background: rgba(0, 78, 137, 0.1); padding: 15px; border-radius: 10px;
                                    border: 1px solid rgba(0, 78, 137, 0.3);'>
                            <p style='color: white; margin: 0;'><strong>{player2_data['Position']}</strong> • {player2_data['Équipe']}</p>
                            <p style='color: #E2E8F0; margin: 5px 0 0 0;'>{int(player2_data['Minutes jouées'])} minutes jouées</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                if joueur1 and joueur2:
                    st.markdown("---")
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(255, 107, 53, 0.3) 0%, rgba(0, 78, 137, 0.3) 100%);
                                backdrop-filter: blur(10px); padding: 20px; border-radius: 15px; margin: 20px 0;
                                border: 1px solid rgba(255, 255, 255, 0.1);'>
                        <h3 style='color: white; text-align: center; margin: 0; font-family: Inter, sans-serif;'>
                            ⚔️ {joueur1} vs {joueur2}
                        </h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        with st.spinner('🎨 Génération du radar comparatif...'):
                            values1 = calculate_percentiles(joueur1, df_j1)
                            values2 = calculate_percentiles(joueur2, df_j2)
                            
                            # Configuration avancée pour le radar comparatif
                            baker = PyPizza(
                                params=list(RAW_STATS.keys()),
                                background_color="#0E1117",
                                straight_line_color="#FFFFFF",
                                straight_line_lw=2,
                                last_circle_color="#FFFFFF",
                                last_circle_lw=2,
                                other_circle_ls="-.",
                                other_circle_lw=1.5,
                                other_circle_color="#666666"
                            )
                            
                            fig, ax = baker.make_pizza(
                                values1,
                                compare_values=values2,
                                figsize=(15, 13),
                                kwargs_slices=dict(
                                    facecolor=COLORS['primary'], 
                                    edgecolor="#FFFFFF", 
                                    linewidth=2, 
                                    zorder=2,
                                    alpha=0.8
                                ),
                                kwargs_compare=dict(
                                    facecolor=COLORS['secondary'], 
                                    edgecolor="#FFFFFF", 
                                    linewidth=2, 
                                    zorder=2,
                                    alpha=0.8
                                ),
                                kwargs_params=dict(
                                    color="#ffffff", 
                                    fontsize=13, 
                                    fontproperties=font_bold.prop,
                                    weight='bold'
                                ),
                                kwargs_values=dict(
                                    color="#ffffff", 
                                    fontsize=11, 
                                    fontproperties=font_normal.prop, 
                                    zorder=3,
                                    bbox=dict(
                                        edgecolor="#FFFFFF", 
                                        facecolor=COLORS['primary'], 
                                        boxstyle="round,pad=0.25", 
                                        lw=1.5,
                                        alpha=0.9
                                    )
                                ),
                                kwargs_compare_values=dict(
                                    color="#ffffff", 
                                    fontsize=11, 
                                    fontproperties=font_normal.prop, 
                                    zorder=3,
                                    bbox=dict(
                                        edgecolor="#FFFFFF", 
                                        facecolor=COLORS['secondary'], 
                                        boxstyle="round,pad=0.25", 
                                        lw=1.5,
                                        alpha=0.9
                                    )
                                )
                            )
                            
                            # Titre principal moderne
                            fig.text(0.515, 0.97, "⚔️ DUEL RADAR",
                                     size=24, ha="center", fontproperties=font_bold.prop, 
                                     color="#ffffff", weight='bold')
                            fig.text(0.515, 0.94, f"{joueur1} vs {joueur2}",
                                     size=20, ha="center", fontproperties=font_bold.prop, 
                                     color="#E2E8F0")
                            fig.text(0.515, 0.92, "Percentiles | Compétitions Respectives | Saison 2024-25",
                                     size=14, ha="center", fontproperties=font_bold.prop, 
                                     color="#A0AEC0")
                            
                            # Légende moderne avec style
                            legend_p1 = mpatches.Patch(color=COLORS['primary'], label=f"{joueur1} ({ligue1})")
                            legend_p2 = mpatches.Patch(color=COLORS['secondary'], label=f"{joueur2} ({ligue2})")
                            legend = ax.legend(
                                handles=[legend_p1, legend_p2], 
                                loc="upper right", 
                                bbox_to_anchor=(1.3, 1.0),
                                fontsize=12,
                                fancybox=True,
                                shadow=True,
                                framealpha=0.9,
                                facecolor='#1E2640',
                                edgecolor='white'
                            )
                            legend.get_frame().set_facecolor('#1E2640')
                            
                            # Footer avec design moderne
                            fig.text(0.99, 0.01, "🚀 Dashboard Football Pro | Inspiration: @Worville, @FootballSlices | Data: FBRef",
                                     size=9, ha="right", fontproperties=font_italic.prop, 
                                     color="#718096")
                            
                            st.pyplot(fig, use_container_width=True)
                            
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la création du radar comparatif : {str(e)}")
                        st.info("💡 Vérifiez que les données des deux joueurs sont complètes.")
        
        with tab5:
            st.markdown("<h2 style='color: #FF6B35; font-family: Inter, sans-serif;'>📈 Analytics Avancées</h2>", unsafe_allow_html=True)
            
            # Section de KPIs avancés
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(30, 38, 64, 0.6) 0%, rgba(45, 55, 72, 0.6) 100%); 
                        backdrop-filter: blur(15px); padding: 25px; border-radius: 20px; margin: 25px 0; 
                        border: 1px solid rgba(255, 255, 255, 0.1);'>
                <h3 style='color: #00C896; text-align: center; margin-bottom: 20px; font-family: Inter, sans-serif;'>
                    🎯 Indices de Performance Avancés
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Calcul d'indices personnalisés avancés
            col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
            
            # Indice de Performance Globale (IPG)
            ipg = (
                (player_data['Buts par 90 minutes'] * 3) +
                (player_data['Passes décisives par 90 minutes'] * 2) +
                (player_data['Actions menant à un tir par 90 minutes'] * 1) +
                ((player_data['Tacles gagnants'] + player_data['Interceptions']) / (player_data['Minutes jouées'] / 90) * 0.5)
            ) / 6.5
            
            # Indice d'Impact Offensif (IIO)
            iio = (
                player_data['Buts attendus par 90 minutes'] +
                player_data['Passes décisives attendues par 90 minutes'] +
                (player_data['Passes clés'] / (player_data['Minutes jouées'] / 90) * 0.1)
            )
            
            # Indice de Solidité Défensive (ISD)
            isd = (
                ((player_data['Tacles gagnants'] + player_data['Interceptions'] + player_data['Ballons récupérés']) / (player_data['Minutes jouées'] / 90)) +
                (player_data['Pourcentage de duels gagnés'] / 10) +
                (player_data['Pourcentage de duels aériens gagnés'] / 10)
            ) / 3
            
            # Indice de Maîtrise Technique (IMT)
            imt = (
                (player_data.get('Pourcentage de passes réussies', 0) / 10) +
                (player_data.get('Pourcentage de dribbles réussis', 0) / 20) +
                ((player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90)) / 10)
            ) / 3
            
            with col_kpi1:
                st.markdown(create_modern_metric_card("🏆 IPG", f"{ipg:.2f}", f"+{ipg-2:.2f}" if ipg > 2 else f"{ipg-2:.2f}"), unsafe_allow_html=True)
            with col_kpi2:
                st.markdown(create_modern_metric_card("⚡ IIO", f"{iio:.2f}", f"+{iio-1:.2f}" if iio > 1 else f"{iio-1:.2f}"), unsafe_allow_html=True)
            with col_kpi3:
                st.markdown(create_modern_metric_card("🛡️ ISD", f"{isd:.2f}", f"+{isd-3:.2f}" if isd > 3 else f"{isd-3:.2f}"), unsafe_allow_html=True)
            
            # Graphique radar combiné des indices
            st.markdown("---")
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px; font-family: Inter, sans-serif;'>🎯 Radar des Indices de Performance</h3>", unsafe_allow_html=True)
            
            col_radar, col_analysis = st.columns([2, 1])
            
            with col_radar:
                # Normaliser les indices pour le radar (0-100)
                indices = {
                    'Performance Globale': min(ipg * 20, 100),  # IPG max ~5
                    'Impact Offensif': min(iio * 25, 100),      # IIO max ~4
                    'Solidité Défensive': min(isd * 10, 100),   # ISD max ~10
                    'Maîtrise Technique': min(imt * 10, 100),   # IMT max ~10
                    'Régularité': min((player_data['Minutes jouées'] / 2700) * 100, 100),  # Sur base de 30 matchs
                    'Polyvalence': min(((ipg + iio + isd + imt) / 4) * 15, 100)  # Moyenne des indices
                }
                
                fig_indices = go.Figure()
                
                fig_indices.add_trace(go.Scatterpolar(
                    r=list(indices.values()),
                    theta=list(indices.keys()),
                    fill='toself',
                    fillcolor='rgba(255, 107, 53, 0.4)',
                    line=dict(color=COLORS['primary'], width=4),
                    marker=dict(color=COLORS['primary'], size=12, symbol='circle',
                               line=dict(color='white', width=3)),
                    name=selected_player,
                    hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}/100<extra></extra>'
                ))
                
                fig_indices.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=12, family='Inter'),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=25
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.3)',
                            tickcolor='white',
                            tickfont=dict(color='white', size=13, family='Inter', weight='bold'),
                            linecolor='rgba(255,255,255,0.4)'
                        ),
                        bgcolor='rgba(30, 38, 64, 0.5)'
                    ),
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text="🎯 Profil de Performance Globale",
                        font=dict(size=18, color='white', family='Inter', weight='bold'),
                        x=0.5,
                        y=0.95
                    ),
                    height=500,
                    showlegend=False
                )
                
                st.plotly_chart(fig_indices, use_container_width=True, key="indices_radar")
            
            with col_analysis:
                st.markdown("##### 📊 Analyse des Forces")
                
                # Identifier les points forts et faibles
                sorted_indices = sorted(indices.items(), key=lambda x: x[1], reverse=True)
                
                # Points forts (top 3)
                st.markdown("**🟢 Points Forts :**")
                for i, (category, score) in enumerate(sorted_indices[:3]):
                    color = "#00C896" if score > 70 else "#F7B801" if score > 50 else "#D62828"
                    st.markdown(f"<span style='color: {color};'>• {category}: {score:.1f}/100</span>", unsafe_allow_html=True)
                
                # Points d'amélioration (bottom 2)
                st.markdown("**🔴 À Améliorer :**")
                for category, score in sorted_indices[-2:]:
                    st.markdown(f"<span style='color: #D62828;'>• {category}: {score:.1f}/100</span>", unsafe_allow_html=True)
                
                # Score global
                overall_score = sum(indices.values()) / len(indices)
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(0, 200, 150, 0.2) 0%, rgba(255, 107, 53, 0.2) 100%);
                            padding: 15px; border-radius: 10px; margin-top: 20px; text-align: center;
                            border: 1px solid rgba(255, 255, 255, 0.2);'>
                    <h4 style='color: white; margin: 0;'>Score Global</h4>
                    <h2 style='color: #00C896; margin: 5px 0 0 0; font-size: 2.5em;'>{overall_score:.1f}/100</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Section d'analyse prédictive
            st.markdown("---")
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px; font-family: Inter, sans-serif;'>🔮 Analyse Prédictive</h3>", unsafe_allow_html=True)
            
            col_pred1, col_pred2 = st.columns([1, 1])
            
            with col_pred1:
                # Projection des performances futures
                st.markdown("##### 📈 Projection Saisonnière")
                
                matches_played = player_data.get('Matchs joués', 1)
                projected_matches = 38  # Saison complète
                
                projections = {
                    'Buts projetés': (player_data['Buts'] / matches_played) * projected_matches,
                    'Passes D. projetées': (player_data['Passes décisives'] / matches_played) * projected_matches,
                    'xG projeté': (player_data['Buts attendus (xG)'] / matches_played) * projected_matches,
                    'Actions→Tir projetées': (player_data.get('Actions menant à un tir', 0) / matches_played) * projected_matches
                }
                
                fig_projection = go.Figure()
                
                fig_projection.add_trace(go.Bar(
                    name='Actuel (extrapolé)',
                    x=list(projections.keys()),
                    y=[player_data['Buts'] * (projected_matches/matches_played),
                       player_data['Passes décisives'] * (projected_matches/matches_played),
                       player_data['Buts attendus (xG)'] * (projected_matches/matches_played),
                       player_data.get('Actions menant à un tir', 0) * (projected_matches/matches_played)],
                    marker_color=COLORS['primary'],
                    opacity=0.8
                ))
                
                fig_projection.add_trace(go.Bar(
                    name='Tendance optimisée',
                    x=list(projections.keys()),
                    y=[v * 1.1 for v in projections.values()],  # +10% d'amélioration
                    marker_color=COLORS['success'],
                    opacity=0.6
                ))
                
                fig_projection.update_layout(
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text="📊 Projections Fin de Saison",
                        font=dict(size=16, color='white', family='Inter'),
                        x=0.5
                    ),
                    barmode='group',
                    height=400,
                    xaxis=dict(tickfont=dict(color='white', family='Inter'), tickangle=45),
                    yaxis=dict(tickfont=dict(color='white', family='Inter'))
                )
                
                st.plotly_chart(fig_projection, use_container_width=True, key="projection")
            
            with col_pred2:
                # Matrice de corrélation des performances
                st.markdown("##### 🔗 Corrélations de Performance")
                
                # Sélectionner les métriques clés pour la corrélation
                correlation_data = df_comparison[[
                    'Buts par 90 minutes', 'Passes décisives par 90 minutes',
                    'Tirs par 90 minutes', 'Actions menant à un tir par 90 minutes',
                    'Pourcentage de passes réussies', 'Minutes jouées'
                ]].corr()
                
                fig_corr = go.Figure(data=go.Heatmap(
                    z=correlation_data.values,
                    x=['Buts/90', 'Passes D./90', 'Tirs/90', 'Actions→Tir/90', '% Passes', 'Minutes'],
                    y=['Buts/90', 'Passes D./90', 'Tirs/90', 'Actions→Tir/90', '% Passes', 'Minutes'],
                    colorscale='RdYlBu',
                    zmid=0,
                    text=correlation_data.values.round(2),
                    texttemplate="%{text}",
                    textfont={"size": 10, "color": "white"},
                    hoverongaps=False,
                    hovertemplate='<b>%{x} vs %{y}</b><br>Corrélation: %{z:.2f}<extra></extra>'
                ))
                
                fig_corr.update_layout(
                    **setup_modern_plotly_theme(),
                    title=dict(
                        text="🔗 Matrice de Corrélation",
                        font=dict(size=16, color='white', family='Inter'),
                        x=0.5
                    ),
                    height=400,
                    margin=dict(t=50, b=50, l=100, r=50)
                )
                
                st.plotly_chart(fig_corr, use_container_width=True, key="correlation")
            
            # Section de recommandations IA
            st.markdown("---")
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px; font-family: Inter, sans-serif;'>🤖 Recommandations Intelligentes</h3>", unsafe_allow_html=True)
            
            # Générer des recommandations basées sur les données
            recommendations = []
            
            if ipg < 2:
                recommendations.append("🎯 **Performance Globale** : Concentrez-vous sur l'amélioration de la contribution offensive et de la régularité.")
            
            if iio < 1:
                recommendations.append("⚡ **Impact Offensif** : Travaillez les finitions et la création d'occasions. Augmentez les tirs et passes clés.")
            
            if isd < 3:
                recommendations.append("🛡️ **Solidité Défensive** : Renforcez les tacles et interceptions. Améliorez le positionnement défensif.")
            
            if imt < 8:
                recommendations.append("🎨 **Maîtrise Technique** : Perfectionnez la précision des passes et la prise de balle sous pression.")
            
            if player_data['Minutes jouées'] < 1800:
                recommendations.append("⏱️ **Temps de jeu** : Cherchez plus de temps de jeu pour démontrer votre potentiel sur la durée.")
            
            # Recommandations spécifiques selon la position
            position = player_data['Position']
            if 'Attaquant' in position or 'AT' in position:
                if player_data['Buts par 90 minutes'] < 0.5:
                    recommendations.append("🥅 **Finition** : En tant qu'attaquant, concentrez-vous sur l'amélioration du ratio buts/90 minutes.")
            elif 'Milieu' in position or 'MI' in position:
                if player_data['Passes décisives par 90 minutes'] < 0.3:
                    recommendations.append("🎯 **Créativité** : Comme milieu de terrain, développez votre capacité à créer des occasions.")
            elif 'Défenseur' in position or 'DF' in position:
                if (player_data['Tacles gagnants'] + player_data['Interceptions']) / (player_data['Minutes jouées'] / 90) < 3:
                    recommendations.append("🛡️ **Défense** : Augmentez votre contribution défensive avec plus de tacles et d'interceptions.")
            
            # Afficher les recommandations
            if recommendations:
                for i, rec in enumerate(recommendations[:4], 1):  # Limiter à 4 recommandations
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(247, 184, 1, 0.1) 0%, rgba(255, 107, 53, 0.1) 100%);
                                padding: 15px; border-radius: 10px; margin: 10px 0;
                                border-left: 4px solid #F7B801;'>
                        <p style='color: white; margin: 0; font-family: Inter, sans-serif;'><strong>{i}.</strong> {rec}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(0, 200, 150, 0.1) 0%, rgba(26, 117, 159, 0.1) 100%);
                            padding: 20px; border-radius: 10px; text-align: center;
                            border: 1px solid rgba(0, 200, 150, 0.3);'>
                    <h4 style='color: #00C896; margin: 0; font-family: Inter, sans-serif;'>
                        🏆 Excellente performance globale ! Continuez sur cette lancée.
                    </h4>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.warning("⚠️ Veuillez ajuster les filtres pour sélectionner un joueur.")

    # Footer modernisé avec design glassmorphism
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 30px; 
                background: linear-gradient(135deg, rgba(30, 38, 64, 0.6) 0%, rgba(45, 55, 72, 0.6) 100%); 
                backdrop-filter: blur(15px); border-radius: 25px; margin-top: 40px;
                border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);'>
        <h3 style='color: #FF6B35; margin: 0; font-size: 1.8em; font-family: Inter, sans-serif; font-weight: 700;'>
            🚀 Dashboard Football Analytics Pro
        </h3>
        <p style='color: #E2E8F0; margin: 15px 0 10px 0; font-size: 1.2em; font-family: Inter, sans-serif;'>
            Analyse avancée des performances avec IA et visualisations modernes
        </p>
        <p style='color: #A0AEC0; margin: 0; font-size: 1em; font-family: Inter, sans-serif;'>
            📊 Données: FBRef | 🎨 Design: Modern Glassmorphism | 🤖 IA: Recommandations Intelligentes | 📅 Saison 2024-25
        </p>
        <div style='margin-top: 20px;'>
            <span style='background: rgba(255, 107, 53, 0.2); padding: 8px 15px; border-radius: 20px; 
                         color: #FF6B35; font-size: 0.9em; margin: 0 10px; border: 1px solid rgba(255, 107, 53, 0.3);'>
                ⚡ Streamlit 2025
            </span>
            <span style='background: rgba(0, 200, 150, 0.2); padding: 8px 15px; border-radius: 20px; 
                         color: #00C896; font-size: 0.9em; margin: 0 10px; border: 1px solid rgba(0, 200, 150, 0.3);'>
                📈 Plotly Advanced
            </span>
            <span style='background: rgba(26, 117, 159, 0.2); padding: 8px 15px; border-radius: 20px; 
                         color: #1A759F; font-size: 0.9em; margin: 0 10px; border: 1px solid rgba(26, 117, 159, 0.3);'>
                🎯 MPLSoccer
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Message d'erreur modernisé
    st.markdown("""
    <div style='text-align: center; padding: 50px; 
                background: linear-gradient(135deg, rgba(214, 40, 40, 0.2) 0%, rgba(247, 119, 0, 0.2) 100%); 
                backdrop-filter: blur(15px); border-radius: 25px; margin: 30px 0;
                border: 1px solid rgba(214, 40, 40, 0.3); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);'>
        <h2 style='color: #D62828; margin: 0; font-size: 2.5em; font-family: Inter, sans-serif; font-weight: 700;'>
            ⚠️ Erreur de Chargement
        </h2>
        <p style='color: #FFE8E8; margin: 20px 0; font-size: 1.3em; font-family: Inter, sans-serif;'>
            Impossible de charger les données du dashboard
        </p>
        <p style='color: #FFB3B3; margin: 10px 0; font-size: 1.1em; font-family: Inter, sans-serif;'>
            Veuillez vérifier que le fichier <strong>'df_BIG2025.csv'</strong> est présent dans le répertoire
        </p>
        <div style='margin-top: 30px; padding: 20px; background: rgba(0, 0, 0, 0.2); border-radius: 15px;'>
            <h4 style='color: #F7B801; margin: 0 0 10px 0; font-family: Inter, sans-serif;'>💡 Instructions :</h4>
            <p style='color: #E2E8F0; margin: 0; font-family: Inter, sans-serif;'>
                1. Assurez-vous que le fichier CSV contient toutes les colonnes requises<br>
                2. Vérifiez les permissions d'accès au fichier<br>
                3. Redémarrez l'application si nécessaire
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exemple de structure de données attendue
    with st.expander("📋 Structure de données requise", expanded=False):
        st.markdown("""
        **Colonnes principales attendues :**
        - Informations générales : `Joueur`, `Âge`, `Position`, `Équipe`, `Nationalité`, `Compétition`
        - Temps de jeu : `Minutes jouées`, `Matchs joués`, `Matchs en 90 min`
        - Statistiques offensives : `Buts`, `Passes décisives`, `Tirs`, `Buts attendus (xG)`, etc.
        - Statistiques défensives : `Tacles gagnants`, `Interceptions`, `Ballons récupérés`, etc.
        - Statistiques techniques : `Passes tentées`, `Touches de balle`, `Dribbles tentés`, etc.
        """)
