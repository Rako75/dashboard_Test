import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration de la page avec thème professionnel
st.set_page_config(
    page_title="Dashboard Joueur Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé avec thème football
st.markdown("""
<style>
    .main {
        background-color: #F1F8E9;
        color: #1B5E20;
    }
    .stApp {
        background: linear-gradient(135deg, #F1F8E9 0%, #E8F5E8 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 2px solid #2E7D32;
        box-shadow: 0 2px 8px rgba(46, 125, 50, 0.15);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #1B5E20;
        border-radius: 6px;
        font-weight: 500;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2E7D32;
        color: #FFFFFF;
        font-weight: 600;
    }
    .metric-card {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #81C784;
        box-shadow: 0 3px 6px rgba(46, 125, 50, 0.1);
    }
    .stMetric {
        background: linear-gradient(135deg, #FFFFFF 0%, #F1F8E9 100%);
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #81C784;
        box-shadow: 0 2px 4px rgba(46, 125, 50, 0.08);
    }
    .sidebar .stSelectbox > div > div {
        background-color: #FFFFFF;
        border: 2px solid #4CAF50;
    }
    .stSidebar {
        background: linear-gradient(180deg, #E8F5E8 0%, #C8E6C9 100%);
    }
    h1, h2, h3 {
        color: #1B5E20;
        font-weight: 700;
    }
    .professional-header {
        background: linear-gradient(135deg, #2E7D32 0%, #388E3C 100%);
        padding: 24px;
        border-radius: 8px;
        margin-bottom: 24px;
        border: 2px solid #1B5E20;
        box-shadow: 0 4px 8px rgba(27, 94, 32, 0.2);
    }
    .section-header {
        background: linear-gradient(135deg, #FFFFFF 0%, #F1F8E9 100%);
        padding: 16px;
        border-radius: 6px;
        margin: 16px 0;
        border: 1px solid #81C784;
        border-left: 4px solid #2E7D32;
        box-shadow: 0 2px 4px rgba(46, 125, 50, 0.1);
    }
    .football-accent {
        background: linear-gradient(45deg, #FFFFFF 0%, #F1F8E9 50%, #FFFFFF 100%);
        border: 2px solid #4CAF50;
        border-radius: 50%;
        display: inline-block;
        padding: 8px;
        margin: 0 8px;
    }
</style>
""", unsafe_allow_html=True)

# Couleurs thème football
COLORS = {
    'primary': '#2E7D32',      # Vert gazon foncé
    'secondary': '#388E3C',    # Vert gazon moyen
    'accent': '#81C784',       # Vert gazon clair
    'success': '#4CAF50',      # Vert victoire
    'warning': '#FF9800',      # Orange carton/arbitre
    'danger': '#F44336',       # Rouge carton
    'info': '#2196F3',         # Bleu maillot
    'light': '#F1F8E9',        # Vert très clair
    'white': '#FFFFFF',        # Blanc maillot
    'dark': '#1B5E20',         # Vert très foncé
    'gradient': ['#2E7D32', '#4CAF50', '#81C784', '#FF9800', '#2196F3']
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
    # Header avec design football
    st.markdown("""
    <div class='professional-header'>
        <h1 style='color: white; margin: 0; font-size: 2.5em; text-align: center;'>⚽ Dashboard Analyse Football</h1>
        <p style='color: #C8E6C9; margin: 8px 0 0 0; font-size: 1.1em; text-align: center;'>🏟️ Analyse Professionnelle des Performances - Saison 2024-25 🏆</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar avec design professionnel
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FFFFFF 0%, #F1F8E9 100%); padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 2px solid #4CAF50; box-shadow: 0 3px 6px rgba(76, 175, 80, 0.15);'>
            <h3 style='color: #1B5E20; text-align: center; margin-bottom: 16px; border-bottom: 2px solid #81C784; padding-bottom: 8px;'>🎯 Sélection du joueur ⚽</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection de la compétition/ligue
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
        st.markdown("**⏱️ Filtrer par minutes jouées :**")
        
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
        <div style='background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%); padding: 12px; border-radius: 6px; border: 2px solid #4CAF50; margin: 8px 0;'>
            <p style='color: #1B5E20; margin: 0; font-weight: 600; text-align: center;'>⚽ {nb_joueurs} joueurs correspondent aux critères 🏟️</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sélection du joueur
        if not df_filtered_minutes.empty:
            joueurs = sorted(df_filtered_minutes['Joueur'].dropna().unique())
            selected_player = st.selectbox(
                "👤 Choisir un joueur :",
                joueurs,
                index=0
            )
        else:
            st.error("Aucun joueur ne correspond aux critères sélectionnés.")
            selected_player = None
    
    # Obtenir les données du joueur sélectionné
    if selected_player:
        player_data = df_filtered_minutes[df_filtered_minutes['Joueur'] == selected_player].iloc[0]
        df_comparison = df_filtered_minutes
    
        # Affichage des informations générales du joueur
        st.markdown(f"""
        <div class='section-header'>
            <h2 style='color: #1B5E20; margin: 0;'>⚽ Profil de {selected_player} 🏟️</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Âge", f"{player_data['Âge']} ans")
        with col2:
            st.metric("Position", player_data['Position'])
        with col3:
            st.metric("Équipe", player_data['Équipe'])
        with col4:
            st.metric("Nationalité", player_data['Nationalité'])
        with col5:
            st.metric("Minutes jouées", f"{int(player_data['Minutes jouées'])} min")
        
        st.markdown("---")
    
        # Graphiques principaux
        tab1, tab2, tab3, tab4 = st.tabs(["⚽ Performance Offensive", "🛡️ Performance Défensive", "🎨 Performance Technique", "🔄 Comparer Joueurs"])
        
        with tab1:
            st.markdown("<div class='section-header'><h2 style='color: #1B5E20; margin: 0;'>⚽ Performance Offensive 🥅</h2></div>", unsafe_allow_html=True)
            
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
                        color=COLORS['gradient'],
                        line=dict(color=COLORS['white'], width=2)
                    ),
                    text=list(actions_off.values()),
                    textposition='outside',
                    textfont=dict(color=COLORS['dark'], size=12, family='Arial Black')
                )])
                
                fig_bar_off.update_layout(
                    title=dict(
                        text="🥅 Actions Offensives ⚽",
                        font=dict(size=18, color=COLORS['dark'], family='Arial Black'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color=COLORS['dark'], size=11),
                        tickangle=45,
                        gridcolor='rgba(46, 125, 50, 0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color=COLORS['dark'], size=11),
                        gridcolor='rgba(46, 125, 50, 0.1)'
                    ),
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(241,248,233,0.8)',
                    font=dict(color=COLORS['dark']),
                    height=400
                )
                st.plotly_chart(fig_bar_off, use_container_width=True)
                
                # Radar professionnel des actions offensives
                st.markdown(f"<h3 style='color: #4CAF50; font-weight: 600;'>⚽ Radar individuel : {selected_player} 🏆</h3>", unsafe_allow_html=True)
                
                try:
                    values1 = calculate_percentiles(selected_player, df_comparison)
                    
                    baker = PyPizza(
                        params=list(RAW_STATS.keys()),
                        background_color="#F1F8E9",
                        straight_line_color="#1B5E20",
                        straight_line_lw=1,
                        last_circle_color="#1B5E20",
                        last_circle_lw=1,
                        other_circle_lw=0,
                        inner_circle_size=11
                    )
                    
                    fig, ax = baker.make_pizza(
                        values1,
                        figsize=(12, 14),
                        param_location=110,
                        color_blank_space="same",
                        slice_colors=[COLORS['primary']] * len(values1),
                        value_colors=["#ffffff"] * len(values1),
                        value_bck_colors=[COLORS['primary']] * len(values1),
                        kwargs_slices=dict(edgecolor="#1B5E20", zorder=2, linewidth=1),
                        kwargs_params=dict(color="#1B5E20", fontsize=13, fontproperties=font_bold.prop),
                        kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop,
                                           bbox=dict(edgecolor="#1B5E20", facecolor=COLORS['primary'], boxstyle="round,pad=0.2", lw=1))
                    )
                    
                    fig.text(0.515, 0.95, f"⚽ {selected_player} 🏆", size=26, ha="center", fontproperties=font_bold.prop, color="#1B5E20")
                    fig.text(0.515, 0.925, "🏟️ Radar Individuel | Percentile | Saison 2024-25 ⚽", size=14,
                             ha="center", fontproperties=font_bold.prop, color="#2E7D32")
                    fig.text(0.99, 0.01, "⚽ Dashboard Football Pro | Données: FBRef 🏟️",
                             size=8, ha="right", fontproperties=font_italic.prop, color="#4CAF50")
                    
                    st.pyplot(fig)
                    
                except Exception as e:
                    st.error(f"Erreur lors de la création du radar individuel : {str(e)}")
            
            elif mode == "Radar comparatif":
                col1, col2 = st.columns(2)
                
                with col1:
                    ligue1 = st.selectbox("🏆 Ligue Joueur 1", competitions, 
                                         index=competitions.index(selected_competition), key="ligue1_comp")
                    df_j1 = df[df['Compétition'] == ligue1]
                    joueur1 = st.selectbox("⚽ Joueur 1", df_j1['Joueur'].sort_values(), 
                                          index=list(df_j1['Joueur'].sort_values()).index(selected_player), key="joueur1_comp")
                
                with col2:
                    ligue2 = st.selectbox("🏆 Ligue Joueur 2", competitions, key="ligue2_comp")
                    df_j2 = df[df['Compétition'] == ligue2]
                    joueur2 = st.selectbox("⚽ Joueur 2", df_j2['Joueur'].sort_values(), key="joueur2_comp")
                
                if joueur1 and joueur2:
                    st.markdown(f"<h3 style='color: #4CAF50; font-weight: 600;'>⚔️ Radar comparatif : {joueur1} ⚽ vs ⚽ {joueur2} 🏟️</h3>", unsafe_allow_html=True)
                    
                    try:
                        values1 = calculate_percentiles(joueur1, df_j1)
                        values2 = calculate_percentiles(joueur2, df_j2)
                        
                        params_offset = [False] * len(RAW_STATS)
                        if len(params_offset) > 9:
                            params_offset[9] = True
                        if len(params_offset) > 10:
                            params_offset[10] = True
                        
                        baker = PyPizza(
                            params=list(RAW_STATS.keys()),
                            background_color="#F1F8E9",
                            straight_line_color="#1B5E20",
                            straight_line_lw=1,
                            last_circle_color="#1B5E20",
                            last_circle_lw=1,
                            other_circle_ls="-.",
                            other_circle_lw=1
                        )
                        
                        fig, ax = baker.make_pizza(
                            values1,
                            compare_values=values2,
                            figsize=(12, 12),
                            kwargs_slices=dict(facecolor=COLORS['primary'], edgecolor="#1B5E20", linewidth=1, zorder=2),
                            kwargs_compare=dict(facecolor=COLORS['info'], edgecolor="#1B5E20", linewidth=1, zorder=2),
                            kwargs_params=dict(color="#1B5E20", fontsize=13, fontproperties=font_bold.prop),
                            kwargs_values=dict(
                                color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                                bbox=dict(edgecolor="#1B5E20", facecolor=COLORS['primary'], boxstyle="round,pad=0.2", lw=1)
                            ),
                            kwargs_compare_values=dict(
                                color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                                bbox=dict(edgecolor="#1B5E20", facecolor=COLORS['info'], boxstyle="round,pad=0.2", lw=1)
                            )
                        )
                        
                        try:
                            baker.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)
                        except:
                            pass
                        
                        fig.text(0.515, 0.955, "⚽ Radar comparatif | Percentile | Saison 2024-25 🏟️",
                                 size=14, ha="center", fontproperties=font_bold.prop, color="#1B5E20")
                        
                        legend_p1 = mpatches.Patch(color=COLORS['primary'], label=f"⚽ {joueur1}")
                        legend_p2 = mpatches.Patch(color=COLORS['info'], label=f"⚽ {joueur2}")
                        ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0))
                        
                        fig.text(0.99, 0.01, "⚽ Dashboard Football Pro | Source: FBRef 🏟️\nInspiration: @Worville, @FootballSlices",
                                 size=8, ha="right", fontproperties=font_italic.prop, color="#4CAF50")
                        
                        st.pyplot(fig)
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la création du radar comparatif : {str(e)}")

    else:
        st.warning("Veuillez ajuster les filtres pour sélectionner un joueur.")

    # Footer thème football
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FFFFFF 0%, #F1F8E9 100%); padding: 20px; border-radius: 8px; margin-top: 30px; border: 2px solid #4CAF50; box-shadow: 0 3px 6px rgba(76, 175, 80, 0.15);'>
        <div style='text-align: center;'>
            <h4 style='color: #1B5E20; margin: 0; font-size: 1.3em; font-weight: 600;'>
                ⚽ Dashboard Football Professionnel 🏟️
            </h4>
            <p style='color: #2E7D32; margin: 8px 0 0 0; font-size: 1em;'>
                🏆 Analyse Avancée des Performances | Données: FBRef | Saison 2024-25 ⚽
            </p>
            <hr style='border: none; border-top: 2px solid #81C784; margin: 12px 0;'>
            <p style='color: #388E3C; margin: 0; font-size: 0.9em;'>
                🥅 Design thème football pour une analyse passionnée des statistiques du ballon rond 🏟️
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Message d'erreur thème football
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%); padding: 30px; border-radius: 8px; margin: 20px 0; border: 2px solid #F44336; box-shadow: 0 3px 6px rgba(244, 67, 54, 0.15);'>
        <div style='text-align: center;'>
            <h2 style='color: #C62828; margin: 0; font-weight: 600;'>⚠️ Carton Rouge - Erreur de chargement des données 🚫</h2>
            <p style='color: #D32F2F; margin: 15px 0 0 0; font-size: 1.1em;'>
                ⚽ Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent dans le vestiaire (répertoire).
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); padding: 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #2196F3; box-shadow: 0 3px 6px rgba(33, 150, 243, 0.15);'>
        <p style='color: #1565C0; margin: 0; font-size: 1em; text-align: center;'>
            ⚽ Ce dashboard nécessite un fichier CSV avec les colonnes spécifiées dans les données fournies pour entrer sur le terrain ! 🏟️
        </p>
    </div>
    """, unsafe_allow_html=True)"<h3 style='color: #4CAF50; margin-top: 30px; font-weight: 600;'>⚽ Radar Offensif - Terrain de Football 🏟️</h3>", unsafe_allow_html=True))
                
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
                
                # Calculer les percentiles
                percentile_values = []
                avg_values = []
                for metric, value in offensive_metrics.items():
                    if metric.endswith('/90'):
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
                            base_column = metric.replace('/90', '').replace('Passes D.', 'Passes décisives').replace('Passes prog.', 'Passes progressives')
                            distribution = df_comparison[base_column] / (df_comparison['Minutes jouées'] / 90)
                        
                        percentile = (distribution < value).mean() * 100
                        avg_comp = distribution.mean()
                        percentile_values.append(min(percentile, 100))
                        avg_values.append(avg_comp)
                    else:
                        percentile_values.append(50)
                        avg_values.append(0)
                
                # Créer le radar avec style professionnel
                fig_radar = go.Figure()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=percentile_values,
                    theta=list(offensive_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(46, 125, 50, 0.2)',
                    line=dict(color=COLORS['primary'], width=3),
                    marker=dict(color=COLORS['primary'], size=8, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(offensive_metrics.values())
                ))
                
                # Ligne de référence pour la moyenne
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
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=avg_percentiles,
                    theta=list(offensive_metrics.keys()),
                    mode='lines',
                    line=dict(color=COLORS['warning'], width=2, dash='dash'),
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
                            gridcolor='rgba(46, 125, 50, 0.3)',
                            tickcolor=COLORS['dark'],
                            tickfont=dict(color=COLORS['dark'], size=10),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(46, 125, 50, 0.3)',
                            tickcolor=COLORS['dark'],
                            tickfont=dict(color=COLORS['dark'], size=11, family='Arial Black'),
                            linecolor='rgba(46, 125, 50, 0.4)'
                        ),
                        bgcolor='rgba(232, 245, 233, 0.9)'
                    ),
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(241,248,233,0.8)',
                    font=dict(color=COLORS['dark']),
                    title=dict(
                        text="⚽ Radar Offensif - Performance sur le Terrain 🥅",
                        font=dict(size=16, color=COLORS['dark'], family='Arial Black'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color=COLORS['dark'], size=10)
                    ),
                    height=450
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite offensifs
                pourcentages_off = {
                    'Conversion (Buts/Tirs)': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                    'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                    'Efficacité passes clés': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
                }
                
                pourcentages_off = {k: v if pd.notna(v) else 0 for k, v in pourcentages_off.items()}
                
                fig_gauge_off = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_off.keys())
                )
                
                colors_off = [COLORS['primary'], COLORS['info'], COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages_off.items()):
                    fig_gauge_off.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_off[i]),
                                bgcolor="rgba(248,249,250,0.8)",
                                borderwidth=2,
                                bordercolor=COLORS['accent'],
                                steps=[
                                    {'range': [0, 50], 'color': 'rgba(226,232,240,0.3)'},
                                    {'range': [50, 80], 'color': 'rgba(226,232,240,0.5)'},
                                    {'range': [80, 100], 'color': 'rgba(226,232,240,0.7)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': COLORS['dark'], 'size': 14}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_off.update_layout(
                    height=300, 
                    title_text="🎯 Pourcentages de Réussite Offensive ⚽",
                    title_font_color=COLORS['dark'],
                    title_font_size=16,
                    title_font_family='Arial Black',
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(241,248,233,0.8)',
                    font=dict(color=COLORS['dark'])
                )
                st.plotly_chart(fig_gauge_off, use_container_width=True)
                
                # Graphique de comparaison offensive
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
                
                fig_off_comp.add_trace(go.Bar(
                    name=selected_player,
                    x=list(offensive_comparison.keys()),
                    y=list(offensive_comparison.values()),
                    marker_color=COLORS['primary'],
                    marker_line=dict(color=COLORS['white'], width=2)
                ))
                
                fig_off_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison_off.keys()),
                    y=list(avg_comparison_off.values()),
                    marker_color=COLORS['accent'],
                    marker_line=dict(color=COLORS['white'], width=2)
                ))
                
                fig_off_comp.update_layout(
                    title=dict(
                        text='🥅 Actions Offensives par 90min vs Moyenne 📊',
                        font=dict(color=COLORS['dark'], size=16, family='Arial Black'),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(241,248,233,0.8)',
                    font=dict(color=COLORS['dark']),
                    xaxis=dict(
                        tickfont=dict(color=COLORS['dark'], size=11),
                        gridcolor='rgba(46, 125, 50, 0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color=COLORS['dark'], size=11),
                        gridcolor='rgba(46, 125, 50, 0.1)'
                    ),
                    height=400
                )
                
                st.plotly_chart(fig_off_comp, use_container_width=True)
            
            # Scatter plot pour comparaison offensive
            st.markdown("<h3 style='color: #1B5E20; margin-top: 30px; font-weight: 600;'>🔍 Analyse Comparative Offensive ⚽</h3>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                metric_options_off = [
                    'Buts', 'Passes décisives', 'Tirs', 'Buts attendus (xG)',
                    'Passes décisives attendues (xAG)', 'Passes clés', 'Actions menant à un tir',
                    'Pourcentage de tirs cadrés'
                ]
                
                x_metric_off = st.selectbox("Métrique X", metric_options_off, index=0, key="x_off")
                y_metric_off = st.selectbox("Métrique Y", metric_options_off, index=1, key="y_off")
            
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
                    marker=dict(color=COLORS['accent'], size=8, opacity=0.7),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                # Joueur sélectionné
                fig_scatter_off.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color=COLORS['primary'], size=20, symbol='star'),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_off.update_layout(
                    title=dict(text=f"{x_title} vs {y_title}", font=dict(size=14, color=COLORS['dark'], family='Arial Black'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color=COLORS['dark'])), tickfont=dict(color=COLORS['dark'])),
                    yaxis=dict(title=dict(text=y_title, font=dict(color=COLORS['dark'])), tickfont=dict(color=COLORS['dark'])),
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(241,248,233,0.8)',
                    font=dict(color=COLORS['dark']),
                    height=400
                )
                
                st.plotly_chart(fig_scatter_off, use_container_width=True)
            
            # Métriques offensives par 90 minutes
            st.markdown("<h3 style='color: #1B5E20; margin-top: 30px; font-weight: 600;'>📊 Statistiques offensives par 90 minutes ⚽</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Buts/90min", f"{player_data['Buts par 90 minutes']:.2f}")
            with col2:
                st.metric("Passes D./90min", f"{player_data['Passes décisives par 90 minutes']:.2f}")
            with col3:
                st.metric("xG/90min", f"{player_data['Buts attendus par 90 minutes']:.2f}")
            with col4:
                st.metric("Actions → Tir/90min", f"{player_data['Actions menant à un tir par 90 minutes']:.2f}")
            with col5:
                efficiency_off = (player_data['Buts'] + player_data['Passes décisives']) / player_data.get('Tirs', 1) * 100 if player_data.get('Tirs', 0) > 0 else 0
                st.metric("Efficacité Offensive", f"{efficiency_off:.1f}%")
    
        with tab2:
            st.markdown("<div class='section-header'><h2 style='color: #1B5E20; margin: 0;'>🛡️ Performance Défensive 🔒</h2></div>", unsafe_allow_html=True)
            
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
                
                fig_bar = go.Figure(data=[go.Bar(
                    x=list(actions_def.keys()),
                    y=list(actions_def.values()),
                    marker=dict(
                        color=COLORS['gradient'],
                        line=dict(color='white', width=2)
                    ),
                    text=list(actions_def.values()),
                    textposition='outside',
                    textfont=dict(color=COLORS['dark'], size=12, family='Arial Black')
                )])
                
                fig_bar.update_layout(
                    title=dict(
                        text="🛡️ Actions Défensives 🔒",
                        font=dict(size=18, color=COLORS['dark'], family='Arial Black'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color=COLORS['dark'], size=11),
                        tickangle=45,
                        gridcolor='rgba(46, 125, 50, 0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color=COLORS['dark'], size=11),
                        gridcolor='rgba(46, 125, 50, 0.1)'
                    ),
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(241,248,233,0.8)',
                    font=dict(color=COLORS['dark']),
                    height=400
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Radar défensif professionnel
                st.markdown("<h3 style='color: #4CAF50; margin-top: 30px; font-weight: 600;'>🛡️ Radar Défensif - Forteresse 🏰</h3>", unsafe_allow_html=True)
                
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
                
                fig_def_radar.add_trace(go.Scatterpolar(
                    r=def_percentile_values,
                    theta=list(defensive_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(33, 150, 243, 0.2)',
                    line=dict(color=COLORS['info'], width=3),
                    marker=dict(color=COLORS['info'], size=8, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(defensive_metrics.values())
                ))
                
                # Ligne de référence moyenne
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
                
                fig_def_radar.add_trace(go.Scatterpolar(
                    r=def_avg_percentiles,
                    theta=list(defensive_metrics.keys()),
                    mode='lines',
                    line=dict(color=COLORS['warning'], width=2, dash='dash'),
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
                            gridcolor='rgba(46, 125, 50, 0.3)',
                            tickcolor=COLORS['dark'],
                            tickfont=dict(color=COLORS['dark'], size=10),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(46, 125, 50, 0.3)',
                            tickcolor=COLORS['dark'],
                            tickfont=dict(color=COLORS['dark'], size=11, family='Arial Black'),
                            linecolor='rgba(46, 125, 50, 0.4)'
                        ),
                        bgcolor='rgba(232, 245, 233, 0.9)'
                    ),
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(241,248,233,0.8)',
                    font=dict(color=COLORS['dark']),
                    title=dict(
                        text="🛡️ Radar Défensif - Mur Infranchissable 🔒",
                        font=dict(size=16, color=COLORS['dark'], family='Arial Black'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color=COLORS['dark'], size=10)
                    ),
                    height=450
                )
                
                st.plotly_chart(fig_def_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite défensifs
                pourcentages = {
                    'Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                    'Duels défensifs': player_data['Pourcentage de duels gagnés'],
                    'Passes réussies': player_data['Pourcentage de passes réussies']
                }
                
                pourcentages = {k: v if pd.notna(v) else 0 for k, v in pourcentages.items()}
                
                fig_gauge = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages.keys())
                )
                
                colors = [COLORS['danger'], COLORS['info'], COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages.items()):
                    fig_gauge.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors[i]),
                                bgcolor="rgba(248,249,250,0.8)",
                                borderwidth=2,
                                bordercolor=COLORS['accent'],
                                steps=[
                                    {'range': [0, 50], 'color': 'rgba(226,232,240,0.3)'},
                                    {'range': [50, 80], 'color': 'rgba(226,232,240,0.5)'},
                                    {'range': [80, 100], 'color': 'rgba(226,232,240,0.7)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': COLORS['primary'], 'size': 14}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge.update_layout(
                    height=300, 
                    title_text="🛡️ Pourcentages de Réussite Défensive 📊",
                    title_font_color=COLORS['dark'],
                    title_font_size=16,
                    title_font_family='Arial Black',
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(241,248,233,0.8)',
                    font=dict(color=COLORS['dark'])
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Graphique de comparaison défensive
                defensive_comparison = {
                    'Tacles/90': player_data['Tacles gagnants'] / (player_data['Minutes jouées'] / 90),
                    'Interceptions/90': player_data['Interceptions'] / (player_data['Minutes jouées'] / 90),
                    'Ballons récupérés/90': player_data['Ballons récupérés'] / (player_data['Minutes jouées'] / 90)
                }
                
                avg_comparison = {
                    'Tacles/90': (df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Interceptions/90': (df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Ballons récupérés/90': (df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)).mean()
                }
                
                fig_def_comp = go.Figure()
                
                fig_def_comp.add_trace(go.Bar(
                    name=selected_player,
                    x=list(defensive_comparison.keys()),
                    y=list(defensive_comparison.values()),
                    marker_color=COLORS['primary'],
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_def_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison.keys()),
                    y=list(avg_comparison.values()),
                    marker_color=COLORS['accent'],
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_def_comp.update_layout(
                    title=dict(
                        text='Actions Défensives par 90min vs Moyenne',
                        font=dict(color=COLORS['primary'], size=16, family='Arial Black'),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    plot_bgcolor='rgba(248,249,250,0.5)',
                    font=dict(color=COLORS['primary']),
                    xaxis=dict(
                        tickfont=dict(color=COLORS['primary'], size=11),
                        gridcolor='rgba(45, 55, 72, 0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color=COLORS['primary'], size=11),
                        gridcolor='rgba(45, 55, 72, 0.1)'
                    ),
                    height=400
                )
                
                st.plotly_chart(fig_def_comp, use_container_width=True)
            
            # Scatter plot défensif
            st.markdown("<h3 style='color: #2D3748; margin-top: 30px; font-weight: 600;'>🔍 Analyse Comparative Défensive</h3>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                metric_options_def = [
                    'Tacles gagnants', 'Interceptions', 'Ballons récupérés', 
                    'Duels aériens gagnés', 'Dégagements', 'Pourcentage de duels gagnés',
                    'Pourcentage de duels aériens gagnés'
                ]
                
                x_metric_def = st.selectbox("Métrique X", metric_options_def, index=0, key="x_def")
                y_metric_def = st.selectbox("Métrique Y", metric_options_def, index=1, key="y_def")
            
            with col_scatter2:
                fig_scatter_def = go.Figure()
                
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
                
                fig_scatter_def.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color=COLORS['accent'], size=8, opacity=0.7),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_def.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color=COLORS['primary'], size=20, symbol='star'),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_def.update_layout(
                    title=dict(text=f"{x_title} vs {y_title}", font=dict(size=14, color=COLORS['primary'], family='Arial Black'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color=COLORS['primary'])), tickfont=dict(color=COLORS['primary'])),
                    yaxis=dict(title=dict(text=y_title, font=dict(color=COLORS['primary'])), tickfont=dict(color=COLORS['primary'])),
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    plot_bgcolor='rgba(248,249,250,0.5)',
                    font=dict(color=COLORS['primary']),
                    height=400
                )
                
                st.plotly_chart(fig_scatter_def, use_container_width=True)
            
            # Métriques défensives par 90 minutes
            st.markdown("<h3 style='color: #2D3748; margin-top: 30px; font-weight: 600;'>📊 Statistiques défensives par 90 min</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            
            minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
            
            with col1:
                tacles_90 = player_data['Tacles gagnants'] / minutes_90
                st.metric("Tacles/90min", f"{tacles_90:.2f}")
            with col2:
                interceptions_90 = player_data['Interceptions'] / minutes_90
                st.metric("Interceptions/90min", f"{interceptions_90:.2f}")
            with col3:
                ballons_90 = player_data['Ballons récupérés'] / minutes_90
                st.metric("Ballons récupérés/90min", f"{ballons_90:.2f}")
            with col4:
                duels_90 = player_data['Duels aériens gagnés'] / minutes_90
                st.metric("Duels aériens/90min", f"{duels_90:.2f}")
            with col5:
                defensive_success = (player_data['Pourcentage de duels gagnés'] + player_data['Pourcentage de duels aériens gagnés']) / 2
                st.metric("Efficacité Défensive", f"{defensive_success:.1f}%")
        
        with tab3:
            st.markdown("<div class='section-header'><h2 style='color: #1B5E20; margin: 0;'>🎨 Performance Technique ⚽</h2></div>", unsafe_allow_html=True)
            
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
                        color=COLORS['gradient'],
                        line=dict(color='white', width=2)
                    ),
                    text=list(actions_tech.values()),
                    textposition='outside',
                    textfont=dict(color=COLORS['primary'], size=12, family='Arial Black')
                )])
                
                fig_bar_tech.update_layout(
                    title=dict(
                        text="Actions Techniques",
                        font=dict(size=18, color=COLORS['primary'], family='Arial Black'),
                        x=0.5
                    ),
                    xaxis=dict(
                        tickfont=dict(color=COLORS['primary'], size=11),
                        tickangle=45,
                        gridcolor='rgba(45, 55, 72, 0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color=COLORS['primary'], size=11),
                        gridcolor='rgba(45, 55, 72, 0.1)'
                    ),
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    plot_bgcolor='rgba(248,249,250,0.5)',
                    font=dict(color=COLORS['primary']),
                    height=400
                )
                st.plotly_chart(fig_bar_tech, use_container_width=True)
                
                # Radar technique professionnel
                st.markdown("<h3 style='color: #4CAF50; margin-top: 30px; font-weight: 600;'>🎨 Radar Technique - Virtuosité Footballistique ⚽</h3>", unsafe_allow_html=True)
                
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
                
                fig_tech_radar.add_trace(go.Scatterpolar(
                    r=tech_percentile_values,
                    theta=list(technical_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(76, 175, 80, 0.2)',
                    line=dict(color=COLORS['success'], width=3),
                    marker=dict(color=COLORS['success'], size=8, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(technical_metrics.values())
                ))
                
                # Ligne de référence moyenne
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
                
                fig_tech_radar.add_trace(go.Scatterpolar(
                    r=tech_avg_percentiles,
                    theta=list(technical_metrics.keys()),
                    mode='lines',
                    line=dict(color=COLORS['warning'], width=2, dash='dash'),
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
                            gridcolor='rgba(46, 125, 50, 0.3)',
                            tickcolor=COLORS['dark'],
                            tickfont=dict(color=COLORS['dark'], size=10),
                            showticklabels=True,
                            tickmode='linear',
                            tick0=0,
                            dtick=20
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(46, 125, 50, 0.3)',
                            tickcolor=COLORS['dark'],
                            tickfont=dict(color=COLORS['dark'], size=11, family='Arial Black'),
                            linecolor='rgba(46, 125, 50, 0.4)'
                        ),
                        bgcolor='rgba(232, 245, 233, 0.9)'
                    ),
                    paper_bgcolor='rgba(255,255,255,0.95)',
                    plot_bgcolor='rgba(241,248,233,0.8)',
                    font=dict(color=COLORS['dark']),
                    title=dict(
                        text="🎨 Radar Technique - Maîtrise du Ballon ⚽",
                        font=dict(size=16, color=COLORS['dark'], family='Arial Black'),
                        x=0.5,
                        y=0.95
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5,
                        font=dict(color=COLORS['dark'], size=10)
                    ),
                    height=450
                )
                
                st.plotly_chart(fig_tech_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite techniques
                pourcentages_tech = {
                    'Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                    'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                    'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
                }
                
                pourcentages_tech = {k: v if pd.notna(v) else 0 for k, v in pourcentages_tech.items()}
                
                fig_gauge_tech = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_tech.keys())
                )
                
                colors_tech = [COLORS['success'], COLORS['warning'], COLORS['info']]
                for i, (metric, value) in enumerate(pourcentages_tech.items()):
                    fig_gauge_tech.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_tech[i]),
                                bgcolor="rgba(248,249,250,0.8)",
                                borderwidth=2,
                                bordercolor=COLORS['accent'],
                                steps=[
                                    {'range': [0, 50], 'color': 'rgba(226,232,240,0.3)'},
                                    {'range': [50, 80], 'color': 'rgba(226,232,240,0.5)'},
                                    {'range': [80, 100], 'color': 'rgba(226,232,240,0.7)'}
                                ]
                            ),
                            number={'suffix': '%', 'font': {'color': COLORS['primary'], 'size': 14}}
                        ),
                        row=1, col=i+1
                    )
                
                fig_gauge_tech.update_layout(
                    height=300, 
                    title_text="Pourcentages de Réussite Technique",
                    title_font_color=COLORS['primary'],
                    title_font_size=16,
                    title_font_family='Arial Black',
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    plot_bgcolor='rgba(248,249,250,0.5)',
                    font=dict(color=COLORS['primary'])
                )
                st.plotly_chart(fig_gauge_tech, use_container_width=True)
                
                # Graphique de comparaison technique
                technical_comparison = {
                    'Passes/90': player_data['Passes tentées'] / (player_data['Minutes jouées'] / 90),
                    'Dribbles/90': player_data['Dribbles tentés'] / (player_data['Minutes jouées'] / 90),
                    'Touches/90': player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90)
                }
                
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
                    marker_color=COLORS['primary'],
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_tech_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison_tech.keys()),
                    y=list(avg_comparison_tech.values()),
                    marker_color=COLORS['accent'],
                    marker_line=dict(color='white', width=2)
                ))
                
                fig_tech_comp.update_layout(
                    title=dict(
                        text='Actions Techniques par 90min vs Moyenne',
                        font=dict(color=COLORS['primary'], size=16, family='Arial Black'),
                        x=0.5
                    ),
                    barmode='group',
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    plot_bgcolor='rgba(248,249,250,0.5)',
                    font=dict(color=COLORS['primary']),
                    xaxis=dict(
                        tickfont=dict(color=COLORS['primary'], size=11),
                        gridcolor='rgba(45, 55, 72, 0.1)'
                    ),
                    yaxis=dict(
                        tickfont=dict(color=COLORS['primary'], size=11),
                        gridcolor='rgba(45, 55, 72, 0.1)'
                    ),
                    height=400
                )
                
                st.plotly_chart(fig_tech_comp, use_container_width=True)
            
            # Scatter plot technique
            st.markdown("<h3 style='color: #2D3748; margin-top: 30px; font-weight: 600;'>🔍 Analyse Comparative Technique</h3>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                metric_options_tech = [
                    'Passes tentées', 'Pourcentage de passes réussies', 'Passes progressives',
                    'Passes clés', 'Dribbles tentés', 'Pourcentage de dribbles réussis',
                    'Touches de balle', 'Distance progressive des passes'
                ]
                
                x_metric_tech = st.selectbox("Métrique X", metric_options_tech, index=0, key="x_tech")
                y_metric_tech = st.selectbox("Métrique Y", metric_options_tech, index=1, key="y_tech")
            
            with col_scatter2:
                fig_scatter_tech = go.Figure()
                
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
                
                fig_scatter_tech.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color=COLORS['accent'], size=8, opacity=0.7),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_tech.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color=COLORS['primary'], size=20, symbol='star'),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_tech.update_layout(
                    title=dict(text=f"{x_title} vs {y_title}", font=dict(size=14, color=COLORS['primary'], family='Arial Black'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color=COLORS['primary'])), tickfont=dict(color=COLORS['primary'])),
                    yaxis=dict(title=dict(text=y_title, font=dict(color=COLORS['primary'])), tickfont=dict(color=COLORS['primary'])),
                    paper_bgcolor='rgba(255,255,255,0.9)',
                    plot_bgcolor='rgba(248,249,250,0.5)',
                    font=dict(color=COLORS['primary']),
                    height=400
                )
                
                st.plotly_chart(fig_scatter_tech, use_container_width=True)
            
            # Métriques techniques détaillées
            st.markdown("<h3 style='color: #2D3748; margin-top: 30px; font-weight: 600;'>📊 Statistiques Techniques Détaillées</h3>", unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Distance passes", f"{player_data.get('Distance totale des passes', 0):.0f}m")
                st.metric("Distance progressive", f"{player_data.get('Distance progressive des passes', 0):.0f}m")
            
            with col2:
                st.metric("Passes tentées", f"{player_data.get('Passes tentées', 0):.0f}")
                st.metric("% Réussite passes", f"{player_data.get('Pourcentage de passes réussies', 0):.1f}%")
            
            with col3:
                touches_90 = player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90)
                st.metric("Touches/90min", f"{touches_90:.1f}")
                st.metric("Passes clés", f"{player_data.get('Passes clés', 0):.0f}")
            
            with col4:
                distance_portee = player_data.get('Distance totale parcourue avec le ballon (en mètres)', 0)
                st.metric("Distance portée", f"{distance_portee:.0f}m")
                st.metric("Centres dans surface", f"{player_data.get('Centres dans la surface', 0):.0f}")
            
            with col5:
                passes_critiques = (player_data.get('Pourcentage de passes longues réussies', 0) + 
                                   player_data.get('Pourcentage de passes courtes réussies', 0)) / 2
                st.metric("Précision Zones Critiques", f"{passes_critiques:.1f}%")
        
        with tab4:
            st.markdown("<div class='section-header'><h2 style='color: #1B5E20; margin: 0;'>🔄 Comparaison Pizza Chart ⚽</h2></div>", unsafe_allow_html=True)
            
            mode = st.radio("Mode de visualisation", ["Radar individuel", "Radar comparatif"], horizontal=True)
            
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            if mode == "Radar individuel":
                st.markdown(f"<h3 style='color: #38A169; font-weight: 600;'>🎯 Radar individuel : {selected_player}</h3>", unsafe_allow_html=True)
                
                try:
                    values1 = calculate_percentiles(selected_player, df_comparison)
                    
                    baker = PyPizza(
                        params=list(RAW_STATS.keys()),
                        background_color="#F8F9FA",
                        straight_line_color="#2D3748",
                        straight_line_lw=1,
                        last_circle_color="#2D3748",
                        last_circle_lw=1,
                        other_circle_lw=0,
                        inner_circle_size=11
                    )
                    
                    fig, ax = baker.make_pizza(
                        values1,
                        figsize=(12, 14),
                        param_location=110,
                        color_blank_space="same",
                        slice_colors=[COLORS['primary']] * len(values1),
                        value_colors=["#ffffff"] * len(values1),
                        value_bck_colors=[COLORS['primary']] * len(values1),
                        kwargs_slices=dict(edgecolor="#2D3748", zorder=2, linewidth=1),
                        kwargs_params=dict(color="#2D3748", fontsize=13, fontproperties=font_bold.prop),
                        kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop,
                                           bbox=dict(edgecolor="#2D3748", facecolor=COLORS['primary'], boxstyle="round,pad=0.2", lw=1))
                    )
                    
                    fig.text(0.515, 0.95, selected_player, size=26, ha="center", fontproperties=font_bold.prop, color="#2D3748")
                    fig.text(0.515, 0.925, "Radar Individuel | Percentile | Saison 2024-25", size=14,
                             ha="center", fontproperties=font_bold.prop, color="#4A5568")
                    fig.text(0.99, 0.01, "Dashboard Football Pro | Données: FBRef",
                             size=8, ha="right", fontproperties=font_italic.prop, color="#718096")
                    
                    st.pyplot(fig)
                    
                except Exception as e:
                    st.error(f"Erreur lors de la création du radar individuel : {str(e)}")
            
            elif mode == "Radar comparatif":
                col1, col2 = st.columns(2)
                
                with col1:
                    ligue1 = st.selectbox("🏆 Ligue Joueur 1", competitions, 
                                         index=competitions.index(selected_competition), key="ligue1_comp")
                    df_j1 = df[df['Compétition'] == ligue1]
                    joueur1 = st.selectbox("👤 Joueur 1", df_j1['Joueur'].sort_values(), 
                                          index=list(df_j1['Joueur'].sort_values()).index(selected_player), key="joueur1_comp")
                
                with col2:
                    ligue2 = st.selectbox("🏆 Ligue Joueur 2", competitions, key="ligue2_comp")
                    df_j2 = df[df['Compétition'] == ligue2]
                    joueur2 = st.selectbox("👤 Joueur 2", df_j2['Joueur'].sort_values(), key="joueur2_comp")
                
                if joueur1 and joueur2:
                    st.markdown(f"<h3 style='color: #38A169; font-weight: 600;'>⚔️ Radar comparatif : {joueur1} vs {joueur2}</h3>", unsafe_allow_html=True)
                    
                    try:
                        values1 = calculate_percentiles(joueur1, df_j1)
                        values2 = calculate_percentiles(joueur2, df_j2)
                        
                        params_offset = [False] * len(RAW_STATS)
                        if len(params_offset) > 9:
                            params_offset[9] = True
                        if len(params_offset) > 10:
                            params_offset[10] = True
                        
                        baker = PyPizza(
                            params=list(RAW_STATS.keys()),
                            background_color="#F8F9FA",
                            straight_line_color="#2D3748",
                            straight_line_lw=1,
                            last_circle_color="#2D3748",
                            last_circle_lw=1,
                            other_circle_ls="-.",
                            other_circle_lw=1
                        )
                        
                        fig, ax = baker.make_pizza(
                            values1,
                            compare_values=values2,
                            figsize=(12, 12),
                            kwargs_slices=dict(facecolor=COLORS['primary'], edgecolor="#2D3748", linewidth=1, zorder=2),
                            kwargs_compare=dict(facecolor=COLORS['secondary'], edgecolor="#2D3748", linewidth=1, zorder=2),
                            kwargs_params=dict(color="#2D3748", fontsize=13, fontproperties=font_bold.prop),
                            kwargs_values=dict(
                                color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                                bbox=dict(edgecolor="#2D3748", facecolor=COLORS['primary'], boxstyle="round,pad=0.2", lw=1)
                            ),
                            kwargs_compare_values=dict(
                                color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                                bbox=dict(edgecolor="#2D3748", facecolor=COLORS['secondary'], boxstyle="round,pad=0.2", lw=1)
                            )
                        )
                        
                        try:
                            baker.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)
                        except:
                            pass
                        
                        fig.text(0.515, 0.955, "Radar comparatif | Percentile | Saison 2024-25",
                                 size=14, ha="center", fontproperties=font_bold.prop, color="#2D3748")
                        
                        legend_p1 = mpatches.Patch(color=COLORS['primary'], label=joueur1)
                        legend_p2 = mpatches.Patch(color=COLORS['secondary'], label=joueur2)
                        ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0))
                        
                        fig.text(0.99, 0.01, "Dashboard Football Pro | Source: FBRef\nInspiration: @Worville, @FootballSlices",
                                 size=8, ha="right", fontproperties=font_italic.prop, color="#718096")
                        
                        st.pyplot(fig)
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la création du radar comparatif : {str(e)}")

    else:
        st.warning("Veuillez ajuster les filtres pour sélectionner un joueur.")

    # Footer professionnel
    st.markdown("---")
    st.markdown("""
    <div style='background: #FFFFFF; padding: 20px; border-radius: 8px; margin-top: 30px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>
        <div style='text-align: center;'>
            <h4 style='color: #2D3748; margin: 0; font-size: 1.2em; font-weight: 600;'>
                📊 Dashboard Football Professionnel
            </h4>
            <p style='color: #4A5568; margin: 8px 0 0 0; font-size: 1em;'>
                Analyse Avancée des Performances | Données: FBRef | Saison 2024-25
            </p>
            <hr style='border: none; border-top: 1px solid #E2E8F0; margin: 12px 0;'>
            <p style='color: #718096; margin: 0; font-size: 0.9em;'>
                Design professionnel sobre pour une analyse précise et élégante des statistiques footballistiques
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Message d'erreur professionnel
    st.markdown("""
    <div style='background: #FEF2F2; padding: 30px; border-radius: 8px; margin: 20px 0; border: 1px solid #FCA5A5; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>
        <div style='text-align: center;'>
            <h2 style='color: #991B1B; margin: 0; font-weight: 600;'>⚠️ Erreur de chargement des données</h2>
            <p style='color: #7F1D1D; margin: 15px 0 0 0; font-size: 1.1em;'>
                Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent dans le répertoire.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: #EBF8FF; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #90CDF4; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>
        <p style='color: #2C5282; margin: 0; font-size: 1em; text-align: center;'>
            💡 Ce dashboard nécessite un fichier CSV avec les colonnes spécifiées dans les données fournies.
        </p>
    </div>
    """, unsafe_allow_html=True)
