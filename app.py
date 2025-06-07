import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuration de la page avec thème sombre professionnel
st.set_page_config(
    page_title="Dashboard Joueur Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un look professionnel
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1E2640 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1E2640;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #FFFFFF;
        border-radius: 8px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF6B35;
        color: #FFFFFF;
    }
    .metric-card {
        background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #4A5568;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stMetric {
        background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #718096;
    }
</style>
""", unsafe_allow_html=True)

# Couleurs professionnelles
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
    # Header avec design amélioré
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #FF6B35 0%, #004E89 100%); border-radius: 15px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0; font-size: 3em;'>⚽ Dashboard Analyse Joueur Football</h1>
        <p style='color: #E2E8F0; margin: 10px 0 0 0; font-size: 1.2em;'>Analyse avancée des performances - Saison 2024-25</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar avec design amélioré
    with st.sidebar:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
            <h2 style='color: #FF6B35; text-align: center; margin-bottom: 20px;'>🎯 Sélection du joueur</h2>
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
        
        # Sélection du joueur
        joueurs = sorted(df_filtered['Joueur'].dropna().unique())
        selected_player = st.selectbox(
            "👤 Choisir un joueur :",
            joueurs,
            index=0
        )
    
    # Obtenir les données du joueur sélectionné
    player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
    
    # Affichage des informations générales du joueur avec design amélioré
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%); padding: 25px; border-radius: 15px; margin: 20px 0; border: 2px solid #FF6B35;'>
        <h2 style='color: #FF6B35; text-align: center; margin-bottom: 20px;'>📊 Profil de {selected_player}</h2>
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
        st.metric("Matchs joués", int(player_data['Matchs joués']))
    
    st.markdown("---")
    
    # Graphiques principaux
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Performance Offensive", "🛡️ Performance Défensive", "🎨 Performance Technique", "🔄 Comparer Joueurs"])
    
    with tab1:
        st.markdown("<h2 style='color: #FF6B35;'>🎯 Performance Offensive</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Diagramme circulaire des contributions offensives avec variables supplémentaires
            contribution_data = {
                'Buts': player_data['Buts'],
                'Passes décisives': player_data['Passes décisives'],
                'Passes clés': player_data['Passes clés'],
                'Actions → Tir': player_data.get('Actions menant à un tir', 0),
                'Passes dernier tiers': player_data.get('Passes dans le dernier tiers', 0),
                'Centres réussis': player_data.get('Centres réussis', 0),
                'Passes progressives': player_data.get('Passes progressives', 0),
                'Tirs': player_data.get('Tirs', 0)
            }
            
            # Filtrer les valeurs nulles et créer le diagramme circulaire
            contribution_filtered = {k: v for k, v in contribution_data.items() if v > 0}
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=list(contribution_filtered.keys()),
                values=list(contribution_filtered.values()),
                hole=0.4,
                marker=dict(
                    colors=COLORS['gradient'][:len(contribution_filtered)],
                    line=dict(color='#FFFFFF', width=2)
                ),
                textfont=dict(size=12, color='white'),
                hovertemplate='<b>%{label}</b><br>Valeur: %{value}<br>Pourcentage: %{percent}<extra></extra>'
            )])
            
            fig_pie.update_layout(
                title=dict(
                    text="Radar Technique Professionnel (Percentiles)",
                    font=dict(size=16, color='white', family='Arial Black'),
                    x=0.5,
                    y=0.95
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(color='white', size=10)
                ),
                height=450,
                annotations=[
                    dict(
                        text=f"Progression vs Moyenne {selected_competition}",
                        showarrow=False,
                        x=0.5,
                        y=-0.15,
                        xref="paper",
                        yref="paper",
                        font=dict(color='white', size=12, family='Arial'),
                        bgcolor='rgba(0, 200, 150, 0.8)',
                        bordercolor='white',
                        borderwidth=1
                    )
                ]
            )
            
            st.plotly_chart(fig_prog_radar, use_container_width=True)
            
            # Afficher les valeurs détaillées sous le radar
            st.markdown("<h4 style='color: #00C896; margin-top: 20px;'>📊 Détail des métriques de progression vs moyenne de la compétition</h4>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                for i, (metric, value) in enumerate(list(progression_metrics.items())[:4]):
                    percentile = prog_percentile_values[i]
                    avg_comp = prog_avg_values[i]
                    color = "#00C896" if percentile >= 75 else "#F7B801" if percentile >= 50 else "#D62828"
                    comparison = "↗️" if value > avg_comp else "↘️" if value < avg_comp else "➡️"
                    st.markdown(f"**{metric}**: {value:.2f} {comparison} (Moy: {avg_comp:.2f}) <span style='color: {color}'>({percentile:.0f}e percentile)</span>", unsafe_allow_html=True)
            
            with col_b:
                for i, (metric, value) in enumerate(list(progression_metrics.items())[4:], 4):
                    percentile = prog_percentile_values[i]
                    avg_comp = prog_avg_values[i]
                    color = "#00C896" if percentile >= 75 else "#F7B801" if percentile >= 50 else "#D62828"
                    comparison = "↗️" if value > avg_comp else "↘️" if value < avg_comp else "➡️"
                    st.markdown(f"**{metric}**: {value:.2f} {comparison} (Moy: {avg_comp:.2f}) <span style='color: {color}'>({percentile:.0f}e percentile)</span>", unsafe_allow_html=True)
        
        # Pourcentages de réussite des passes par zone (compteurs)
        st.markdown("<h3 style='color: #00C896; margin-top: 30px;'>📐 Précision par Zone</h3>", unsafe_allow_html=True)
        
        # Compteurs de précision technique
        precision_zones = {
            'Passes courtes': player_data.get('Pourcentage de passes courtes réussies', 0),
            'Passes moyennes': player_data.get('Pourcentage de passes moyennes réussies', 0),
            'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
        }
        
        # Nettoyer les valeurs NaN
        precision_zones = {k: v if pd.notna(v) else 0 for k, v in precision_zones.items()}
        
        fig_precision_gauge = make_subplots(
            rows=1, cols=3,
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
            subplot_titles=list(precision_zones.keys())
        )
        
        colors_precision = [COLORS['success'], COLORS['warning'], COLORS['accent']]
        for i, (metric, value) in enumerate(precision_zones.items()):
            fig_precision_gauge.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=value,
                    gauge=dict(
                        axis=dict(range=[0, 100]),
                        bar=dict(color=colors_precision[i]),
                        bgcolor="rgba(0,0,0,0.3)",
                        borderwidth=2,
                        bordercolor="white",
                        steps=[
                            {'range': [0, 50], 'color': 'rgba(255,255,255,0.1)'},
                            {'range': [50, 80], 'color': 'rgba(255,255,255,0.2)'},
                            {'range': [80, 100], 'color': 'rgba(255,255,255,0.3)'}
                        ]
                    ),
                    number={'suffix': '%', 'font': {'color': 'white'}}
                ),
                row=1, col=i+1
            )
        
        fig_precision_gauge.update_layout(
            height=300, 
            title_text="Pourcentages de Réussite par Type de Passe",
            title_font_color='white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig_precision_gauge, use_container_width=True)
        
        # Scatter plot personnalisable pour la technique
        st.markdown("<h3 style='color: #F7B801; margin-top: 30px;'>📊 Comparaison Technique Personnalisable</h3>", unsafe_allow_html=True)
        
        col_scatter_x, col_scatter_y = st.columns(2)
        
        technical_metrics = {
            'Passes tentées': 'Passes tentées',
            'Pourcentage de passes réussies': 'Pourcentage de passes réussies',
            'Distance totale des passes': 'Distance totale des passes',
            'Distance progressive des passes': 'Distance progressive des passes',
            'Passes progressives': 'Passes progressives',
            'Passes dans le dernier tiers': 'Passes dans le dernier tiers',
            'Passes clés': 'Passes clés',
            'Dribbles tentés': 'Dribbles tentés',
            'Pourcentage de dribbles réussis': 'Pourcentage de dribbles réussis',
            'Touches de balle': 'Touches de balle'
        }
        
        with col_scatter_x:
            x_metric = st.selectbox("Métrique X (horizontal)", list(technical_metrics.keys()), 
                                   index=0, key="tech_x")
        with col_scatter_y:
            y_metric = st.selectbox("Métrique Y (vertical)", list(technical_metrics.keys()), 
                                   index=1, key="tech_y")
        
        # Créer le scatter plot technique
        fig_scatter_tech = go.Figure()
        
        # Tous les joueurs de la compétition
        x_data = df_filtered[technical_metrics[x_metric]].fillna(0)
        y_data = df_filtered[technical_metrics[y_metric]].fillna(0)
        
        fig_scatter_tech.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='markers',
            name='Autres joueurs',
            marker=dict(
                color=COLORS['accent'], 
                size=8, 
                opacity=0.6,
                line=dict(width=1, color='white')
            ),
            text=df_filtered['Joueur'],
            hovertemplate='<b>%{text}</b><br>' + x_metric + ': %{x}<br>' + y_metric + ': %{y}<extra></extra>'
        ))
        
        # Joueur sélectionné
        player_x = player_data[technical_metrics[x_metric]]
        player_y = player_data[technical_metrics[y_metric]]
        
        fig_scatter_tech.add_trace(go.Scatter(
            x=[player_x],
            y=[player_y],
            mode='markers',
            name=selected_player,
            marker=dict(
                color=COLORS['success'], 
                size=20,
                symbol='star',
                line=dict(width=2, color='white')
            ),
            hovertemplate=f'<b>{selected_player}</b><br>' + x_metric + f': {player_x}<br>' + y_metric + f': {player_y}<extra></extra>'
        ))
        
        fig_scatter_tech.update_layout(
            title=dict(
                text=f"{x_metric} vs {y_metric}",
                font=dict(size=16, color='white'),
                x=0.5
            ),
            xaxis=dict(
                title=dict(text=x_metric, font=dict(color='white')),
                tickfont=dict(color='white'),
                gridcolor='rgba(255,255,255,0.2)'
            ),
            yaxis=dict(
                title=dict(text=y_metric, font=dict(color='white')),
                tickfont=dict(color='white'),
                gridcolor='rgba(255,255,255,0.2)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        st.plotly_chart(fig_scatter_tech, use_container_width=True)
        
        # Métriques techniques détaillées
        st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>📊 Statistiques Techniques Détaillées</h3>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
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
            st.metric("Centres dans surface", f"{player_data.get('Centres dans la surface', 0):.0f}")(
                    text="Répartition des Contributions Offensives",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                annotations=[dict(text=f'{selected_player}', x=0.5, y=0.5, 
                                font_size=14, showarrow=False, font_color='white')]
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Radar professionnel des actions offensives avec plus de variables
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
                        distribution = df_filtered['Buts par 90 minutes']
                    elif metric == 'Passes D./90':
                        distribution = df_filtered['Passes décisives par 90 minutes']
                    elif metric == 'xG/90':
                        distribution = df_filtered['Buts attendus par 90 minutes']
                    elif metric == 'xA/90':
                        distribution = df_filtered['Passes décisives attendues par 90 minutes']
                    elif metric == 'Tirs/90':
                        distribution = df_filtered['Tirs par 90 minutes']
                    elif metric == 'Actions → Tir/90':
                        distribution = df_filtered['Actions menant à un tir par 90 minutes']
                    elif metric == 'Passes dernier tiers/90':
                        distribution = df_filtered['Passes dans le dernier tiers'] / (df_filtered['Minutes jouées'] / 90)
                    else:
                        # Calculer pour les autres métriques
                        base_column = metric.replace('/90', '').replace('Passes D.', 'Passes décisives').replace('Passes prog.', 'Passes progressives')
                        distribution = df_filtered[base_column] / (df_filtered['Minutes jouées'] / 90)
                    
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
                fillcolor='rgba(255, 107, 53, 0.3)',
                line=dict(color=COLORS['primary'], width=3),
                marker=dict(color=COLORS['primary'], size=8, symbol='circle'),
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
                        distribution = df_filtered['Buts par 90 minutes']
                    elif metric_name == 'Passes D./90':
                        distribution = df_filtered['Passes décisives par 90 minutes']
                    elif metric_name == 'xG/90':
                        distribution = df_filtered['Buts attendus par 90 minutes']
                    elif metric_name == 'xA/90':
                        distribution = df_filtered['Passes décisives attendues par 90 minutes']
                    elif metric_name == 'Tirs/90':
                        distribution = df_filtered['Tirs par 90 minutes']
                    elif metric_name == 'Actions → Tir/90':
                        distribution = df_filtered['Actions menant à un tir par 90 minutes']
                    elif metric_name == 'Passes dernier tiers/90':
                        distribution = df_filtered['Passes dans le dernier tiers'] / (df_filtered['Minutes jouées'] / 90)
                    else:
                        base_column = metric_name.replace('/90', '').replace('Passes D.', 'Passes décisives').replace('Passes prog.', 'Passes progressives')
                        distribution = df_filtered[base_column] / (df_filtered['Minutes jouées'] / 90)
                    
                    avg_percentile = (distribution < avg_val).mean() * 100
                    avg_percentiles.append(avg_percentile)
                else:
                    avg_percentiles.append(50)
            
            # Ajouter une ligne de référence pour la moyenne de la compétition
            fig_radar.add_trace(go.Scatterpolar(
                r=avg_percentiles,
                theta=list(offensive_metrics.keys()),
                mode='lines',
                line=dict(color='rgba(255,255,255,0.7)', width=2, dash='dash'),
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
                        gridcolor='rgba(255,255,255,0.3)',
                        tickcolor='white',
                        tickfont=dict(color='white', size=10),
                        showticklabels=True,
                        tickmode='linear',
                        tick0=0,
                        dtick=20
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(255,255,255,0.3)',
                        tickcolor='white',
                        tickfont=dict(color='white', size=11, family='Arial Black'),
                        linecolor='rgba(255,255,255,0.5)'
                    ),
                    bgcolor='rgba(30, 38, 64, 0.8)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title=dict(
                    text="Radar Offensif Professionnel (Percentiles)",
                    font=dict(size=16, color='white', family='Arial Black'),
                    x=0.5,
                    y=0.95
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(color='white', size=10)
                ),
                height=450,
                annotations=[
                    dict(
                        text=f"Performance vs Moyenne {selected_competition}",
                        showarrow=False,
                        x=0.5,
                        y=-0.15,
                        xref="paper",
                        yref="paper",
                        font=dict(color='white', size=12, family='Arial'),
                        bgcolor='rgba(255, 107, 53, 0.8)',
                        bordercolor='white',
                        borderwidth=1
                    )
                ]
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Afficher les valeurs détaillées sous le radar
            st.markdown("<h4 style='color: #00C896; margin-top: 20px;'>📊 Détail des métriques offensives vs moyenne de la compétition</h4>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                for i, (metric, value) in enumerate(list(offensive_metrics.items())[:5]):
                    percentile = percentile_values[i]
                    avg_comp = avg_values[i]
                    color = "#00C896" if percentile >= 75 else "#F7B801" if percentile >= 50 else "#D62828"
                    comparison = "↗️" if value > avg_comp else "↘️" if value < avg_comp else "➡️"
                    st.markdown(f"**{metric}**: {value:.2f} {comparison} (Moy: {avg_comp:.2f}) <span style='color: {color}'>({percentile:.0f}e percentile)</span>", unsafe_allow_html=True)
            
            with col_b:
                for i, (metric, value) in enumerate(list(offensive_metrics.items())[5:], 5):
                    percentile = percentile_values[i]
                    avg_comp = avg_values[i]
                    color = "#00C896" if percentile >= 75 else "#F7B801" if percentile >= 50 else "#D62828"
                    comparison = "↗️" if value > avg_comp else "↘️" if value < avg_comp else "➡️"
                    st.markdown(f"**{metric}**: {value:.2f} {comparison} (Moy: {avg_comp:.2f}) <span style='color: {color}'>({percentile:.0f}e percentile)</span>", unsafe_allow_html=True)
        
        with col2:
            # Graphique buts vs buts attendus amélioré
            fig_scatter = go.Figure()
            
            # Tous les joueurs de la compétition
            fig_scatter.add_trace(go.Scatter(
                x=df_filtered['Buts attendus (xG)'],
                y=df_filtered['Buts'],
                mode='markers',
                name='Autres joueurs',
                marker=dict(
                    color=COLORS['accent'], 
                    size=8, 
                    opacity=0.6,
                    line=dict(width=1, color='white')
                ),
                text=df_filtered['Joueur'],
                hovertemplate='<b>%{text}</b><br>xG: %{x}<br>Buts: %{y}<extra></extra>'
            ))
            
            # Joueur sélectionné
            fig_scatter.add_trace(go.Scatter(
                x=[player_data['Buts attendus (xG)']],
                y=[player_data['Buts']],
                mode='markers',
                name=selected_player,
                marker=dict(
                    color=COLORS['primary'], 
                    size=20,
                    symbol='star',
                    line=dict(width=2, color='white')
                ),
                hovertemplate=f'<b>{selected_player}</b><br>xG: %{{x}}<br>Buts: %{{y}}<extra></extra>'
            ))
            
            # Ligne de référence (performance attendue)
            max_xg = df_filtered['Buts attendus (xG)'].max()
            fig_scatter.add_trace(go.Scatter(
                x=[0, max_xg],
                y=[0, max_xg],
                mode='lines',
                name='Performance attendue',
                line=dict(dash='dash', color='rgba(255,255,255,0.5)', width=2)
            ))
            
            fig_scatter.update_layout(
                title=dict(
                    text="Buts marqués vs Buts attendus (xG)",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                xaxis=dict(
                    title=dict(text="Buts attendus (xG)", font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255,255,255,0.2)'
                ),
                yaxis=dict(
                    title=dict(text="Buts marqués", font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255,255,255,0.2)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Graphique en barres horizontales pour l'efficacité
            efficiency_data = {
                'Conversion (Buts/Tirs)': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                'Précision (Tirs cadrés/Tirs)': player_data.get('Pourcentage de tirs cadrés', 0),
                'Efficacité passes clés': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
            }
            
            fig_efficiency = go.Figure(go.Bar(
                x=list(efficiency_data.values()),
                y=list(efficiency_data.keys()),
                orientation='h',
                marker=dict(
                    color=COLORS['gradient'][:len(efficiency_data)],
                    line=dict(color='white', width=1)
                ),
                text=[f"{v:.1f}%" for v in efficiency_data.values()],
                textposition='inside',
                textfont=dict(color='white', size=12)
            ))
            
            fig_efficiency.update_layout(
                title=dict(
                    text="Indicateurs d'Efficacité Offensive",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                xaxis=dict(
                    title=dict(text="Pourcentage (%)", font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255,255,255,0.2)'
                ),
                yaxis=dict(
                    tickfont=dict(color='white')
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            
            st.plotly_chart(fig_efficiency, use_container_width=True)
            
            # Compteur d'efficacité offensive
            st.markdown("<h3 style='color: #00C896; margin-top: 20px;'>🎯 Efficacité Offensive</h3>", unsafe_allow_html=True)
            
            # Compteurs d'efficacité
            efficiency_metrics = {
                'Conversion': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                'Efficacité passes clés': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
            }
            
            # Nettoyer les valeurs NaN
            efficiency_metrics = {k: v if pd.notna(v) else 0 for k, v in efficiency_metrics.items()}
            
            fig_efficiency_gauge = make_subplots(
                rows=1, cols=3,
                specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                subplot_titles=list(efficiency_metrics.keys())
            )
            
            colors_efficiency = [COLORS['success'], COLORS['warning'], COLORS['primary']]
            for i, (metric, value) in enumerate(efficiency_metrics.items()):
                fig_efficiency_gauge.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=value,
                        gauge=dict(
                            axis=dict(range=[0, 100]),
                            bar=dict(color=colors_efficiency[i]),
                            bgcolor="rgba(0,0,0,0.3)",
                            borderwidth=2,
                            bordercolor="white",
                            steps=[
                                {'range': [0, 30], 'color': 'rgba(255,255,255,0.1)'},
                                {'range': [30, 60], 'color': 'rgba(255,255,255,0.2)'},
                                {'range': [60, 100], 'color': 'rgba(255,255,255,0.3)'}
                            ]
                        ),
                        number={'suffix': '%', 'font': {'color': 'white'}}
                    ),
                    row=1, col=i+1
                )
            
            fig_efficiency_gauge.update_layout(
                height=300, 
                title_text="Indicateurs d'Efficacité Offensive",
                title_font_color='white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_efficiency_gauge, use_container_width=True)
        
        # Métriques offensives par 90 minutes avec design amélioré
        st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>📊 Statistiques offensives par 90 minutes</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Buts/90min", f"{player_data['Buts par 90 minutes']:.2f}")
        with col2:
            st.metric("Passes D./90min", f"{player_data['Passes décisives par 90 minutes']:.2f}")
        with col3:
            st.metric("xG/90min", f"{player_data['Buts attendus par 90 minutes']:.2f}")
        with col4:
            st.metric("Actions → Tir/90min", f"{player_data['Actions menant à un tir par 90 minutes']:.2f}")
    
    with tab2:
        st.markdown("<h2 style='color: #FF6B35;'>🛡️ Performance Défensive</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique des actions défensives amélioré
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
                    line=dict(color='white', width=1)
                ),
                text=list(actions_def.values()),
                textposition='outside',
                textfont=dict(color='white', size=12)
            )])
            
            fig_bar.update_layout(
                title=dict(
                    text="Actions Défensives",
                    font=dict(size=16, color='white'),
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
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Pourcentages de réussite avec design amélioré
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
                subplot_titles=list(pourcentages.keys())
            )
            
            colors = [COLORS['danger'], COLORS['secondary'], COLORS['success']]
            for i, (metric, value) in enumerate(pourcentages.items()):
                fig_gauge.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=value,
                        gauge=dict(
                            axis=dict(range=[0, 100]),
                            bar=dict(color=colors[i]),
                            bgcolor="rgba(0,0,0,0.3)",
                            borderwidth=2,
                            bordercolor="white",
                            steps=[
                                {'range': [0, 50], 'color': 'rgba(255,255,255,0.1)'},
                                {'range': [50, 80], 'color': 'rgba(255,255,255,0.2)'},
                                {'range': [80, 100], 'color': 'rgba(255,255,255,0.3)'}
                            ]
                        ),
                        number={'suffix': '%', 'font': {'color': 'white'}}
                    ),
                    row=1, col=i+1
                )
            
            fig_gauge.update_layout(
                height=300, 
                title_text="Pourcentages de Réussite",
                title_font_color='white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
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
                'Tacles/90': (df_filtered['Tacles gagnants'] / (df_filtered['Minutes jouées'] / 90)).mean(),
                'Interceptions/90': (df_filtered['Interceptions'] / (df_filtered['Minutes jouées'] / 90)).mean(),
                'Ballons récupérés/90': (df_filtered['Ballons récupérés'] / (df_filtered['Minutes jouées'] / 90)).mean()
            }
            
            fig_def_comp = go.Figure()
            
            fig_def_comp.add_trace(go.Bar(
                name=selected_player,
                x=list(defensive_comparison.keys()),
                y=list(defensive_comparison.values()),
                marker_color=COLORS['primary']
            ))
            
            fig_def_comp.add_trace(go.Bar(
                name='Moyenne compétition',
                x=list(avg_comparison.keys()),
                y=list(avg_comparison.values()),
                marker_color=COLORS['secondary']
            ))
            
            fig_def_comp.update_layout(
                title=dict(
                    text='Actions Défensives par 90min vs Moyenne',
                    font=dict(color='white'),
                    x=0.5
                ),
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(tickfont=dict(color='white')),
                yaxis=dict(tickfont=dict(color='white'), gridcolor='rgba(255,255,255,0.2)'),
                height=400
            )
            
            st.plotly_chart(fig_def_comp, use_container_width=True)
            
            # Radar professionnel des actions défensives avec plus de variables
            st.markdown("<h3 style='color: #00C896; margin-top: 30px;'>🛡️ Radar Défensif Professionnel</h3>", unsafe_allow_html=True)
            
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
                        distribution = df_filtered['Tacles gagnants'] / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Interceptions/90':
                        distribution = df_filtered['Interceptions'] / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Ballons récupérés/90':
                        distribution = df_filtered['Ballons récupérés'] / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Duels défensifs/90':
                        distribution = df_filtered.get('Duels défensifs gagnés', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Duels aériens/90':
                        distribution = df_filtered['Duels aériens gagnés'] / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Dégagements/90':
                        distribution = df_filtered['Dégagements'] / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Tirs bloqués/90':
                        distribution = df_filtered.get('Tirs bloqués', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    elif metric == '% Duels gagnés':
                        distribution = df_filtered.get('Pourcentage de duels gagnés', pd.Series([0]*len(df_filtered)))
                    elif metric == '% Duels aériens':
                        distribution = df_filtered['Pourcentage de duels aériens gagnés']
                    elif metric == 'Total Blocs/90':
                        distribution = df_filtered.get('Total de blocs (tirs et passes)', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    
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
                fillcolor='rgba(26, 117, 159, 0.3)',
                line=dict(color=COLORS['accent'], width=3),
                marker=dict(color=COLORS['accent'], size=8, symbol='circle'),
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
                            distribution = df_filtered['Tacles gagnants'] / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Interceptions/90':
                            distribution = df_filtered['Interceptions'] / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Ballons récupérés/90':
                            distribution = df_filtered['Ballons récupérés'] / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Duels défensifs/90':
                            distribution = df_filtered.get('Duels défensifs gagnés', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Duels aériens/90':
                            distribution = df_filtered['Duels aériens gagnés'] / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Dégagements/90':
                            distribution = df_filtered['Dégagements'] / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Tirs bloqués/90':
                            distribution = df_filtered.get('Tirs bloqués', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == '% Duels gagnés':
                            distribution = df_filtered.get('Pourcentage de duels gagnés', pd.Series([0]*len(df_filtered)))
                        elif metric_name == '% Duels aériens':
                            distribution = df_filtered['Pourcentage de duels aériens gagnés']
                        elif metric_name == 'Total Blocs/90':
                            distribution = df_filtered.get('Total de blocs (tirs et passes)', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        
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
                line=dict(color='rgba(255,255,255,0.7)', width=2, dash='dash'),
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
                        gridcolor='rgba(255,255,255,0.3)',
                        tickcolor='white',
                        tickfont=dict(color='white', size=10),
                        showticklabels=True,
                        tickmode='linear',
                        tick0=0,
                        dtick=20
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(255,255,255,0.3)',
                        tickcolor='white',
                        tickfont=dict(color='white', size=11, family='Arial Black'),
                        linecolor='rgba(255,255,255,0.5)'
                    ),
                    bgcolor='rgba(30, 38, 64, 0.8)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title=dict(
                    text="Radar Défensif Professionnel (Percentiles)",
                    font=dict(size=16, color='white', family='Arial Black'),
                    x=0.5,
                    y=0.95
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(color='white', size=10)
                ),
                height=450,
                annotations=[
                    dict(
                        text=f"Performance Défensive vs Moyenne {selected_competition}",
                        showarrow=False,
                        x=0.5,
                        y=-0.15,
                        xref="paper",
                        yref="paper",
                        font=dict(color='white', size=12, family='Arial'),
                        bgcolor='rgba(26, 117, 159, 0.8)',
                        bordercolor='white',
                        borderwidth=1
                    )
                ]
            )
            
            st.plotly_chart(fig_def_radar, use_container_width=True)
            
            # Afficher les valeurs détaillées sous le radar défensif
            st.markdown("<h4 style='color: #00C896; margin-top: 20px;'>📊 Détail des métriques défensives vs moyenne de la compétition</h4>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                for i, (metric, value) in enumerate(list(defensive_metrics.items())[:5]):
                    percentile = def_percentile_values[i]
                    avg_comp = def_avg_values[i]
                    color = "#00C896" if percentile >= 75 else "#F7B801" if percentile >= 50 else "#D62828"
                    comparison = "↗️" if value > avg_comp else "↘️" if value < avg_comp else "➡️"
                    if '/' in metric:
                        st.markdown(f"**{metric}**: {value:.2f} {comparison} (Moy: {avg_comp:.2f}) <span style='color: {color}'>({percentile:.0f}e percentile)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{metric}**: {value:.1f}% {comparison} (Moy: {avg_comp:.1f}%) <span style='color: {color}'>({percentile:.0f}e percentile)</span>", unsafe_allow_html=True)
        
        # Scatter plot personnalisable pour la défense
        st.markdown("<h3 style='color: #F7B801; margin-top: 30px;'>📊 Comparaison Défensive Personnalisable</h3>", unsafe_allow_html=True)
        
        col_scatter_x, col_scatter_y = st.columns(2)
        
        defensive_metrics_scatter = {
            'Tacles gagnants': 'Tacles gagnants',
            'Interceptions': 'Interceptions',
            'Ballons récupérés': 'Ballons récupérés',
            'Duels aériens gagnés': 'Duels aériens gagnés',
            'Dégagements': 'Dégagements',
            'Pourcentage de duels aériens gagnés': 'Pourcentage de duels aériens gagnés',
            'Pourcentage de duels gagnés': 'Pourcentage de duels gagnés',
            'Fautes commises': 'Fautes commises',
            'Cartons jaunes': 'Cartons jaunes'
        }
        
        with col_scatter_x:
            x_metric_def = st.selectbox("Métrique X (horizontal)", list(defensive_metrics_scatter.keys()), 
                                       index=0, key="def_x")
        with col_scatter_y:
            y_metric_def = st.selectbox("Métrique Y (vertical)", list(defensive_metrics_scatter.keys()), 
                                       index=1, key="def_y")
        
        # Créer le scatter plot défensif
        fig_scatter_def = go.Figure()
        
        # Tous les joueurs de la compétition
        x_data_def = df_filtered[defensive_metrics_scatter[x_metric_def]].fillna(0)
        y_data_def = df_filtered[defensive_metrics_scatter[y_metric_def]].fillna(0)
        
        fig_scatter_def.add_trace(go.Scatter(
            x=x_data_def,
            y=y_data_def,
            mode='markers',
            name='Autres joueurs',
            marker=dict(
                color=COLORS['accent'], 
                size=8, 
                opacity=0.6,
                line=dict(width=1, color='white')
            ),
            text=df_filtered['Joueur'],
            hovertemplate='<b>%{text}</b><br>' + x_metric_def + ': %{x}<br>' + y_metric_def + ': %{y}<extra></extra>'
        ))
        
        # Joueur sélectionné
        player_x_def = player_data[defensive_metrics_scatter[x_metric_def]]
        player_y_def = player_data[defensive_metrics_scatter[y_metric_def]]
        
        fig_scatter_def.add_trace(go.Scatter(
            x=[player_x_def],
            y=[player_y_def],
            mode='markers',
            name=selected_player,
            marker=dict(
                color=COLORS['accent'], 
                size=20,
                symbol='star',
                line=dict(width=2, color='white')
            ),
            hovertemplate=f'<b>{selected_player}</b><br>' + x_metric_def + f': {player_x_def}<br>' + y_metric_def + f': {player_y_def}<extra></extra>'
        ))
        
        fig_scatter_def.update_layout(
            title=dict(
                text=f"{x_metric_def} vs {y_metric_def}",
                font=dict(size=16, color='white'),
                x=0.5
            ),
            xaxis=dict(
                title=dict(text=x_metric_def, font=dict(color='white')),
                tickfont=dict(color='white'),
                gridcolor='rgba(255,255,255,0.2)'
            ),
            yaxis=dict(
                title=dict(text=y_metric_def, font=dict(color='white')),
                tickfont=dict(color='white'),
                gridcolor='rgba(255,255,255,0.2)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        st.plotly_chart(fig_scatter_def, use_container_width=True)
            
            with col_b:
                for i, (metric, value) in enumerate(list(defensive_metrics.items())[5:], 5):
                    percentile = def_percentile_values[i]
                    avg_comp = def_avg_values[i]
                    color = "#00C896" if percentile >= 75 else "#F7B801" if percentile >= 50 else "#D62828"
                    comparison = "↗️" if value > avg_comp else "↘️" if value < avg_comp else "➡️"
                    if '/' in metric:
                        st.markdown(f"**{metric}**: {value:.2f} {comparison} (Moy: {avg_comp:.2f}) <span style='color: {color}'>({percentile:.0f}e percentile)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{metric}**: {value:.1f}% {comparison} (Moy: {avg_comp:.1f}%) <span style='color: {color}'>({percentile:.0f}e percentile)</span>", unsafe_allow_html=True)
        
        # Métriques défensives par 90 minutes avec design amélioré - UNIQUEMENT DANS CET ONGLET
        st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>📊 Statistiques défensives par 90 min</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        # Calcul des métriques par 90 minutes
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
    
    with tab3:
        st.markdown("<h2 style='color: #FF6B35;'>🎨 Performance Technique</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Répartition du temps de jeu possible (conservé)
            temps_jeu = {
                'Minutes jouées': player_data['Minutes jouées'],
                'Minutes non jouées': (player_data['Matchs joués'] * 90) - player_data['Minutes jouées']
            }
            
            fig_pie_temps = go.Figure(data=[go.Pie(
                labels=['Minutes jouées', 'Minutes non jouées'],
                values=list(temps_jeu.values()),
                hole=0.4,
                marker=dict(
                    colors=[COLORS['success'], COLORS['danger']],
                    line=dict(color='white', width=2)
                ),
                textfont=dict(size=12, color='white')
            )])
            
            fig_pie_temps.update_layout(
                title=dict(
                    text='Répartition du temps de jeu possible',
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                annotations=[dict(
                    text=f'{(player_data["Minutes jouées"]/(player_data["Matchs joués"]*90)*100):.1f}%',
                    x=0.5, y=0.5, font_size=16, showarrow=False, font_color='white'
                )]
            )
            st.plotly_chart(fig_pie_temps, use_container_width=True)
            
            # Répartition des passes selon les zones du terrain
            zones_passes = {
                'Tiers défensif': player_data.get('Touches de balle dans le tiers défensif', 0) * 0.7,  # Estimation des passes
                'Tiers médian': player_data.get('Touches de balle dans le tiers médian', 0) * 0.8,
                'Tiers offensif': player_data.get('Passes dans le dernier tiers', 0),
                'Surface défensive': player_data.get('Touches de balle dans la surface défensive', 0) * 0.6,
                'Surface offensive': player_data.get('Touches de balle dans la surface offensive', 0) * 0.5
            }
            
            fig_zones_passes = go.Figure(data=[go.Bar(
                x=list(zones_passes.keys()),
                y=list(zones_passes.values()),
                marker=dict(
                    color=COLORS['gradient'],
                    line=dict(color='white', width=1)
                ),
                text=[f"{v:.0f}" for v in zones_passes.values()],
                textposition='outside',
                textfont=dict(color='white', size=12)
            )])
            
            fig_zones_passes.update_layout(
                title=dict(
                    text="Répartition des Passes par Zone",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                xaxis=dict(
                    tickfont=dict(color='white'),
                    tickangle=45
                ),
                yaxis=dict(
                    title=dict(text='Nombre estimé de passes', font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255,255,255,0.2)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            st.plotly_chart(fig_zones_passes, use_container_width=True)
        
        with col2:
            # Radar professionnel de la progression du ballon (même style que les autres)
            progression_metrics = {
                'Courses prog./90': player_data.get('Courses progressives', 0) / (player_data['Minutes jouées'] / 90),
                'Passes prog./90': player_data.get('Passes progressives', 0) / (player_data['Minutes jouées'] / 90),
                'Réceptions prog./90': player_data.get('Réceptions progressives', 0) / (player_data['Minutes jouées'] / 90),
                'Portées prog./90': player_data.get('Portées de balle progressives', 0) / (player_data['Minutes jouées'] / 90),
                'Distance prog./90': player_data.get('Distance progressive des passes', 0) / (player_data['Minutes jouées'] / 90),
                'Passes dernier tiers/90': player_data.get('Passes dans le dernier tiers', 0) / (player_data['Minutes jouées'] / 90),
                'Centres/90': player_data.get('Centres', 0) / (player_data['Minutes jouées'] / 90),
                'Dribbles prog./90': player_data.get('Dribbles réussis', 0) / (player_data['Minutes jouées'] / 90)
            }
            
            # Calculer les percentiles par rapport à la compétition
            prog_percentile_values = []
            prog_avg_values = []
            for metric, value in progression_metrics.items():
                try:
                    if metric == 'Courses prog./90':
                        distribution = df_filtered.get('Courses progressives', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Passes prog./90':
                        distribution = df_filtered.get('Passes progressives', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Réceptions prog./90':
                        distribution = df_filtered.get('Réceptions progressives', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Portées prog./90':
                        distribution = df_filtered.get('Portées de balle progressives', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Distance prog./90':
                        distribution = df_filtered.get('Distance progressive des passes', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Passes dernier tiers/90':
                        distribution = df_filtered.get('Passes dans le dernier tiers', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Centres/90':
                        distribution = df_filtered.get('Centres', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                    elif metric == 'Dribbles prog./90':
                        distribution = df_filtered['Dribbles réussis'] / (df_filtered['Minutes jouées'] / 90)
                    
                    # Nettoyer les valeurs NaN et infinies
                    distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                    value = value if not np.isnan(value) and not np.isinf(value) else 0
                    
                    if len(distribution) > 0:
                        percentile = (distribution < value).mean() * 100
                        avg_comp = distribution.mean()
                    else:
                        percentile = 50
                        avg_comp = 0
                    
                    prog_percentile_values.append(min(percentile, 100))
                    prog_avg_values.append(avg_comp)
                except:
                    prog_percentile_values.append(50)
                    prog_avg_values.append(0)
            
            # Créer le radar de progression
            fig_prog_radar = go.Figure()
            
            # Ajouter la performance du joueur
            fig_prog_radar.add_trace(go.Scatterpolar(
                r=prog_percentile_values,
                theta=list(progression_metrics.keys()),
                fill='toself',
                fillcolor='rgba(0, 200, 150, 0.3)',
                line=dict(color=COLORS['success'], width=3),
                marker=dict(color=COLORS['success'], size=8, symbol='circle'),
                name=f'{selected_player}',
                hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                customdata=list(progression_metrics.values())
            ))
            
            # Calculer les percentiles des moyennes de la compétition
            prog_avg_percentiles = []
            for i, avg_val in enumerate(prog_avg_values):
                try:
                    if avg_val > 0:
                        metric_name = list(progression_metrics.keys())[i]
                        if metric_name == 'Courses prog./90':
                            distribution = df_filtered.get('Courses progressives', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Passes prog./90':
                            distribution = df_filtered.get('Passes progressives', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Réceptions prog./90':
                            distribution = df_filtered.get('Réceptions progressives', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Portées prog./90':
                            distribution = df_filtered.get('Portées de balle progressives', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Distance prog./90':
                            distribution = df_filtered.get('Distance progressive des passes', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Passes dernier tiers/90':
                            distribution = df_filtered.get('Passes dans le dernier tiers', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Centres/90':
                            distribution = df_filtered.get('Centres', pd.Series([0]*len(df_filtered))) / (df_filtered['Minutes jouées'] / 90)
                        elif metric_name == 'Dribbles prog./90':
                            distribution = df_filtered['Dribbles réussis'] / (df_filtered['Minutes jouées'] / 90)
                        
                        distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
                        if len(distribution) > 0:
                            avg_percentile = (distribution < avg_val).mean() * 100
                            prog_avg_percentiles.append(avg_percentile)
                        else:
                            prog_avg_percentiles.append(50)
                    else:
                        prog_avg_percentiles.append(50)
                except:
                    prog_avg_percentiles.append(50)
            
            # Ajouter une ligne de référence pour la moyenne de la compétition
            fig_prog_radar.add_trace(go.Scatterpolar(
                r=prog_avg_percentiles,
                theta=list(progression_metrics.keys()),
                mode='lines',
                line=dict(color='rgba(255,255,255,0.7)', width=2, dash='dash'),
                name=f'Moyenne {selected_competition}',
                showlegend=True,
                hovertemplate='<b>%{theta}</b><br>Moyenne ligue: %{customdata:.2f}<extra></extra>',
                customdata=prog_avg_values
            ))
            
            fig_prog_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        gridcolor='rgba(255,255,255,0.3)',
                        tickcolor='white',
                        tickfont=dict(color='white', size=10),
                        showticklabels=True,
                        tickmode='linear',
                        tick0=0,
                        dtick=20
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(255,255,255,0.3)',
                        tickcolor='white',
                        tickfont=dict(color='white', size=11, family='Arial Black'),
                        linecolor='rgba(255,255,255,0.5)'
                    ),
                    bgcolor='rgba(30, 38, 64, 0.8)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title=dict
    
    with tab4:
        st.markdown("<h2 style='color: #FF6B35;'>🔄 Comparaison Pizza Chart</h2>", unsafe_allow_html=True)
        
        # Choix du mode avec design amélioré
        mode = st.radio("Mode de visualisation", ["Radar individuel", "Radar comparatif"], horizontal=True)
        
        font_normal = FontManager()
        font_bold = FontManager()
        font_italic = FontManager()
        
        if mode == "Radar individuel":
            st.markdown(f"<h3 style='color: #00C896;'>🎯 Radar individuel : {selected_player}</h3>", unsafe_allow_html=True)
            
            try:
                values1 = calculate_percentiles(selected_player, df_filtered)
                
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
                    values1,
                    figsize=(12, 14),
                    param_location=110,
                    color_blank_space="same",
                    slice_colors=[COLORS['primary']] * len(values1),
                    value_colors=["#ffffff"] * len(values1),
                    value_bck_colors=[COLORS['primary']] * len(values1),
                    kwargs_slices=dict(edgecolor="#FFFFFF", zorder=2, linewidth=1),
                    kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop),
                    kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop,
                                       bbox=dict(edgecolor="#FFFFFF", facecolor=COLORS['primary'], boxstyle="round,pad=0.2", lw=1))
                )
                
                fig.text(0.515, 0.95, selected_player, size=26, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                fig.text(0.515, 0.925, "Radar Individuel | Percentile | Saison 2024-25", size=14,
                         ha="center", fontproperties=font_bold.prop, color="#ffffff")
                fig.text(0.99, 0.01, "Dashboard Football Pro | Données: FBRef",
                         size=8, ha="right", fontproperties=font_italic.prop, color="#dddddd")
                
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
                st.markdown(f"<h3 style='color: #00C896;'>⚔️ Radar comparatif : {joueur1} vs {joueur2}</h3>", unsafe_allow_html=True)
                
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
                    
                    try:
                        baker.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)
                    except:
                        pass  # Si la méthode n'existe pas, on continue sans ajustement
                    
                    fig.text(0.515, 0.99, f"{joueur1} vs {joueur2}", size=26, ha="center",
                             fontproperties=font_bold.prop, color="#ffffff")
                    
                    fig.text(0.515, 0.955, "Radar comparatif | Percentile | Saison 2024-25",
                             size=14, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                    
                    legend_p1 = mpatches.Patch(color=COLORS['primary'], label=joueur1)
                    legend_p2 = mpatches.Patch(color=COLORS['secondary'], label=joueur2)
                    ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0))
                    
                    fig.text(0.99, 0.01, "Dashboard Football Pro | Source: FBRef\nInspiration: @Worville, @FootballSlices",
                             size=8, ha="right", fontproperties=font_italic.prop, color="#dddddd")
                    
                    st.pyplot(fig)
                    
                except Exception as e:
                    st.error(f"Erreur lors de la création du radar comparatif : {str(e)}")
                    st.info("Vérifiez que les colonnes nécessaires sont présentes dans vos données.")

    # Footer avec design professionnel
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%); border-radius: 15px; margin-top: 30px;'>
        <p style='color: #E2E8F0; margin: 0; font-size: 1.1em;'>
            📊 Dashboard Football Professionnel - Analyse avancée des performances
        </p>
        <p style='color: #A0AEC0; margin: 5px 0 0 0; font-size: 0.9em;'>
            Données: FBRef | Design: Dashboard Pro | Saison 2024-25
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    # Message d'erreur avec design amélioré
    st.markdown("""
    <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #D62828 0%, #F77F00 100%); border-radius: 15px; margin: 20px 0;'>
        <h2 style='color: white; margin: 0;'>⚠️ Erreur de chargement des données</h2>
        <p style='color: #FFE8E8; margin: 15px 0 0 0; font-size: 1.1em;'>
            Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 Ce dashboard nécessite un fichier CSV avec les colonnes spécifiées dans les données fournies.")
