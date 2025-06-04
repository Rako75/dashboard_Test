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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Performance Offensive", "🛡️ Performance Défensive", "📈 Statistiques Avancées", "⚽ Détails Tirs", "🏃 Activité", "🔄 Comparer Joueurs"])
    
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
            
            # Graphique radar des actions offensives
            offensive_actions = {
                'Tirs': player_data.get('Tirs', 0),
                'Tirs cadrés': player_data.get('Tirs cadrés', 0),
                'Dribbles réussis': player_data.get('Dribbles réussis', 0),
                'Passes clés': player_data.get('Passes clés', 0),
                'Centres': player_data.get('Centres', 0)
            }
            
            # Normaliser les valeurs pour le radar
            max_val = max(offensive_actions.values()) if max(offensive_actions.values()) > 0 else 1
            normalized_values = [v/max_val * 100 for v in offensive_actions.values()]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=normalized_values,
                theta=list(offensive_actions.keys()),
                fill='toself',
                fillcolor=f'rgba(255, 107, 53, 0.3)',
                line=dict(color=COLORS['primary'], width=3),
                name='Actions Offensives'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        gridcolor='rgba(255,255,255,0.2)',
                        tickcolor='white'
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(255,255,255,0.2)',
                        tickcolor='white'
                    )
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title=dict(
                    text="Radar des Actions Offensives",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                height=400
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
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
        
        # Métriques offensives par 90 minutes avec design amélioré
        st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>📊 Moyennes par 90 minutes</h3>", unsafe_allow_html=True)
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
    
    # Métriques défensives par 90 minutes avec design amélioré
    st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>📊 Moyennes par 90 minutes</h3>", unsafe_allow_html=True)
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
        st.markdown("<h2 style='color: #FF6B35;'>📈 Statistiques Avancées</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Comparaison avec la moyenne de la compétition améliorée
            metrics_comparison = ['Buts par 90 minutes', 'Passes décisives par 90 minutes', 
                                'Buts attendus par 90 minutes', 'Passes décisives attendues par 90 minutes']
            
            player_values = [player_data[metric] for metric in metrics_comparison]
            avg_values = [df_filtered[metric].mean() for metric in metrics_comparison]
            
            fig_comparison = go.Figure()
            
            x_labels = ['Buts/90', 'PD/90', 'xG/90', 'xA/90']
            
            fig_comparison.add_trace(go.Bar(
                name=selected_player,
                x=x_labels,
                y=player_values,
                marker=dict(
                    color=COLORS['primary'],
                    line=dict(color='white', width=1)
                ),
                text=[f"{v:.2f}" for v in player_values],
                textposition='outside',
                textfont=dict(color='white')
            ))
            
            fig_comparison.add_trace(go.Bar(
                name='Moyenne compétition',
                x=x_labels,
                y=avg_values,
                marker=dict(
                    color=COLORS['secondary'],
                    line=dict(color='white', width=1)
                ),
                text=[f"{v:.2f}" for v in avg_values],
                textposition='outside',
                textfont=dict(color='white')
            ))
            
            fig_comparison.update_layout(
                title=dict(
                    text='Comparaison avec la moyenne de la compétition',
                    font=dict(size=16, color='white'),
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
            
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Graphique de performance globale (radar)
            performance_metrics = {
                'Offensive': (player_data['Buts par 90 minutes'] + player_data['Passes décisives par 90 minutes']) * 10,
                'Créativité': player_data['Passes clés'] / player_data['Matchs joués'] * 10,
                'Efficacité': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                'Défensive': (player_data['Tacles gagnants'] + player_data['Interceptions']) / player_data['Matchs joués'] * 10,
                'Physique': player_data['Duels aériens gagnés'] / player_data['Matchs joués'] * 10
            }
            
            fig_perf_radar = go.Figure()
            fig_perf_radar.add_trace(go.Scatterpolar(
                r=list(performance_metrics.values()),
                theta=list(performance_metrics.keys()),
                fill='toself',
                fillcolor=f'rgba(255, 107, 53, 0.3)',
                line=dict(color=COLORS['primary'], width=3),
                marker=dict(color=COLORS['primary'], size=8),
                name='Performance Globale'
            ))
            
            fig_perf_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(performance_metrics.values()) * 1.1],
                        gridcolor='rgba(255,255,255,0.2)',
                        tickcolor='white'
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(255,255,255,0.2)',
                        tickcolor='white'
                    )
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title=dict(
                    text="Radar de Performance Globale",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                height=400
            )
            
            st.plotly_chart(fig_perf_radar, use_container_width=True)
        
        with col2:
            # Temps de jeu et efficacité amélioré
            temps_jeu = {
                'Minutes jouées': player_data['Minutes jouées'],
                'Minutes possibles': (player_data['Matchs joués'] * 90) - player_data['Minutes jouées']
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
    
    with tab4:
        st.markdown("<h2 style='color: #FF6B35;'>⚽ Analyse des Tirs</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Statistiques de tirs améliorées
            tirs_data = {
                'Tirs totaux': player_data['Tirs'],
                'Tirs cadrés': player_data['Tirs cadrés'],
                'Buts marqués': player_data['Buts']
            }
            
            fig_funnel = go.Figure(go.Funnel(
                y=list(tirs_data.keys()),
                x=list(tirs_data.values()),
                textinfo="value+percent initial",
                marker=dict(
                    color=[COLORS['accent'], COLORS['warning'], COLORS['success']],
                    line=dict(color='white', width=2)
                ),
                textfont=dict(color='white', size=12)
            ))
            
            fig_funnel.update_layout(
                title=dict(
                    text="Entonnoir de conversion des tirs",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            
            st.plotly_chart(fig_funnel, use_container_width=True)
        
        with col2:
            # Métriques de tir avec design amélioré
            st.markdown("<h3 style='color: #00C896;'>📊 Métriques de Tir</h3>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric("Tirs/90min", f"{player_data['Tirs par 90 minutes']:.2f}")
                st.metric("% Tirs cadrés", f"{player_data['Pourcentage de tirs cadrés']:.1f}%")
                
            with col_b:
                st.metric("Buts/Tir", f"{player_data['Buts par tir']:.2f}")
                st.metric("Distance moy. tirs", f"{player_data['Distance moyenne des tirs']:.1f}m")
            
            # Comparaison xG vs Buts réels avec indicateur visuel
            st.markdown("<h3 style='color: #00C896; margin-top: 30px;'>🎯 Efficacité vs Attendu</h3>", unsafe_allow_html=True)
            
            xg_diff = player_data['Buts'] - player_data['Buts attendus (xG)']
            
            # Gauge pour la différence xG
            fig_xg_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = player_data['Buts'],
                delta = {'reference': player_data['Buts attendus (xG)'], 'position': "top"},
                gauge = {
                    'axis': {'range': [None, max(player_data['Buts'], player_data['Buts attendus (xG)']) * 1.5]},
                    'bar': {'color': COLORS['primary'] if xg_diff >= 0 else COLORS['danger']},
                    'steps': [
                        {'range': [0, player_data['Buts attendus (xG)']], 'color': "rgba(255,255,255,0.2)"}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': player_data['Buts attendus (xG)']
                    }
                },
                number = {'font': {'color': 'white'}},
                title = {'text': "Buts vs xG", 'font': {'color': 'white'}}
            ))
            
            fig_xg_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300
            )
            
            st.plotly_chart(fig_xg_gauge, use_container_width=True)
            
            if xg_diff > 0:
                st.success(f"✅ Surperformance: +{xg_diff:.2f} buts vs attendu")
            elif xg_diff < 0:
                st.warning(f"⚠️ Sous-performance: {xg_diff:.2f} buts vs attendu")
            else:
                st.info("ℹ️ Performance conforme aux attentes")
            
            # Graphique de qualité des occasions
            occasions_quality = {
                'Grandes occasions': player_data.get('Grandes occasions', 0),
                'Grandes occ. manquées': player_data.get('Grandes occasions manquées', 0),
                'Tirs de la tête': player_data.get('Tirs de la tête', 0),
                'Tirs du pied fort': player_data.get('Tirs du pied fort', 0)
            }
            
            fig_occasions = go.Figure(data=[go.Pie(
                labels=list(occasions_quality.keys()),
                values=list(occasions_quality.values()),
                hole=0.3,
                marker=dict(
                    colors=COLORS['gradient'][:len(occasions_quality)],
                    line=dict(color='white', width=2)
                ),
                textfont=dict(size=10, color='white')
            )])
            
            fig_occasions.update_layout(
                title=dict(
                    text='Qualité des Occasions',
                    font=dict(size=14, color='white'),
                    x=0.5
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300
            )
            
            st.plotly_chart(fig_occasions, use_container_width=True)
    
    with tab5:
        st.markdown("<h2 style='color: #FF6B35;'>🏃 Activité et Touches de Balle</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Répartition des touches de balle par zone améliorée
            zones_touches = {
                'Surface défensive': player_data['Touches de balle dans la surface défensive'],
                'Tiers défensif': player_data['Touches de balle dans le tiers défensif'],
                'Tiers médian': player_data['Touches de balle dans le tiers médian'],
                'Tiers offensif': player_data['Touches de balle dans le tiers offensif'],
                'Surface offensive': player_data['Touches de balle dans la surface offensive']
            }
            
            fig_zones = go.Figure(data=[go.Bar(
                x=list(zones_touches.keys()),
                y=list(zones_touches.values()),
                marker=dict(
                    color=COLORS['gradient'],
                    line=dict(color='white', width=1)
                ),
                text=list(zones_touches.values()),
                textposition='outside',
                textfont=dict(color='white', size=12)
            )])
            
            fig_zones.update_layout(
                title=dict(
                    text="Touches de balle par zone du terrain",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                xaxis=dict(
                    tickangle=45,
                    tickfont=dict(color='white')
                ),
                yaxis=dict(
                    title=dict(text='Nombre de touches', font=dict(color='white')),
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255,255,255,0.2)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            st.plotly_chart(fig_zones, use_container_width=True)
            
            # Heatmap d'activité par position
            position_activity = {
                'Milieu de terrain': player_data['Touches de balle dans le tiers médian'],
                'Zone offensive': player_data['Touches de balle dans le tiers offensif'],
                'Zone défensive': player_data['Touches de balle dans le tiers défensif']
            }
            
            # Normaliser pour créer une heatmap
            max_activity = max(position_activity.values())
            normalized_activity = [v/max_activity for v in position_activity.values()]
            
            fig_heatmap_activity = go.Figure(data=go.Heatmap(
                z=[normalized_activity],
                x=list(position_activity.keys()),
                y=['Activité'],
                colorscale='Viridis',
                showscale=True,
                text=[[f"{v}" for v in position_activity.values()]],
                texttemplate="%{text}",
                textfont={"size": 14, "color": "white"}
            ))
            
            fig_heatmap_activity.update_layout(
                title=dict(
                    text="Heatmap - Activité par Zone",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300,
                xaxis=dict(tickangle=45, tickfont=dict(color='white')),
                yaxis=dict(tickfont=dict(color='white'))
            )
            
            st.plotly_chart(fig_heatmap_activity, use_container_width=True)
        
        with col2:
            # Dribbles et portées de balle avec design amélioré
            st.markdown("<h3 style='color: #00C896;'>🎭 Dribbles</h3>", unsafe_allow_html=True)
            
            # Gauge de réussite des dribbles
            dribble_success = player_data['Pourcentage de dribbles réussis']
            
            fig_dribble_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = dribble_success,
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': COLORS['success']},
                    'steps': [
                        {'range': [0, 50], 'color': "rgba(255,255,255,0.1)"},
                        {'range': [50, 75], 'color': "rgba(255,255,255,0.2)"},
                        {'range': [75, 100], 'color': "rgba(255,255,255,0.3)"}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                },
                number = {'suffix': '%', 'font': {'color': 'white', 'size': 20}},
                title = {'text': "% Réussite Dribbles", 'font': {'color': 'white'}}
            ))
            
            fig_dribble_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=250
            )
            
            st.plotly_chart(fig_dribble_gauge, use_container_width=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Dribbles tentés", int(player_data['Dribbles tentés']))
                st.metric("Dribbles réussis", int(player_data['Dribbles réussis']))
            with col_b:
                st.metric("Portées de balle", int(player_data['Portées de balle']))
                st.metric("Centres tentés", int(player_data.get('Centres', 0)))
            
            st.markdown("<h3 style='color: #00C896; margin-top: 30px;'>⚡ Activité générale</h3>", unsafe_allow_html=True)
            
            # Graphique des interactions sur le terrain
            interactions = {
                'Touches totales': player_data['Touches de balle'],
                'Fautes commises': player_data['Fautes commises'],
                'Fautes subies': player_data['Fautes subies'],
                'Hors-jeux': player_data.get('Hors-jeux', 0)
            }
            
            fig_interactions = go.Figure(data=[go.Bar(
                x=list(interactions.keys()),
                y=list(interactions.values()),
                marker=dict(
                    color=[COLORS['primary'], COLORS['danger'], COLORS['warning'], COLORS['accent']],
                    line=dict(color='white', width=1)
                ),
                text=list(interactions.values()),
                textposition='outside',
                textfont=dict(color='white')
            )])
            
            fig_interactions.update_layout(
                title=dict(
                    text="Interactions sur le Terrain",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                xaxis=dict(
                    tickangle=45,
                    tickfont=dict(color='white')
                ),
                yaxis=dict(
                    tickfont=dict(color='white'),
                    gridcolor='rgba(255,255,255,0.2)'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300
            )
            
            st.plotly_chart(fig_interactions, use_container_width=True)
            
            col_c, col_d = st.columns(2)
            with col_c:
                st.metric("Cartons jaunes", int(player_data['Cartons jaunes']))
                st.metric("Cartons rouges", int(player_data['Cartons rouges']))
            with col_d:
                minutes_per_yellow = player_data['Minutes jouées'] / max(player_data['Cartons jaunes'], 1)
                st.metric("Min/Carton J.", f"{minutes_per_yellow:.0f}")
                st.metric("Fautes subies", int(player_data.get('Fautes subies', 0)))
    
    with tab6:
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
