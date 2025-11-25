import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import euclidean_distances

# ==============================================================================
# CONFIGURATION & STYLE
# ==============================================================================
st.set_page_config(
    page_title="ScoutVision Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un look "Dashboard Professionnel"
st.markdown("""
    <style>
    /* Fond global et typographie */
    .stApp {
        background-color: #0e1117;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Styles des cartes (métriques, graphiques) */
    div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
        background-color: #1a1d24;
        border: 1px solid #2d313a;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Titres */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700;
    }
    h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.8rem; margin-top: 2rem; border-bottom: 2px solid #3b82f6; display: inline-block; padding-bottom: 5px; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #151922;
        border-right: 1px solid #2d313a;
    }
    
    /* Métriques clés (KPIs) */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        color: #3b82f6 !important;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #a0a0a0 !important;
    }
    
    /* Boutons et Widgets */
    .stSelectbox > div > div {
        background-color: #262730;
        color: white;
        border: 1px solid #4a4e5a;
    }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1a1d24;
        border-radius: 5px;
        color: #fff;
        font-weight: 600;
        border: 1px solid #2d313a;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# CHARGEMENT ET PRÉPARATION DES DONNÉES
# ==============================================================================
@st.cache_data
def load_data():
    # Chargement du CSV (séparateur point-virgule selon le fichier fourni)
    df = pd.read_csv('df_BIG2025.csv', sep=';', encoding='utf-8')
    
    # Nettoyage basique
    if 'Minutes jouées' in df.columns:
        df = df[df['Minutes jouées'] > 200]  # Filtre pour éviter les joueurs avec peu de temps de jeu
        
    # Remplacer les NaN par 0 pour les calculs
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur lors du chargement des données : {e}")
    st.stop()

# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================

def create_radar_chart(player_data, categories, title, color='#3b82f6', comparison_data=None, comparison_name=None):
    """Crée un radar chart interactif avec Plotly"""
    
    fig = go.Figure()

    # Joueur principal
    fig.add_trace(go.Scatterpolar(
        r=player_data,
        theta=categories,
        fill='toself',
        name=title,
        line=dict(color=color, width=3),
        fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.3,)}"
    ))

    # Joueur de comparaison (optionnel)
    if comparison_data is not None:
        fig.add_trace(go.Scatterpolar(
            r=comparison_data,
            theta=categories,
            fill='toself',
            name=comparison_name,
            line=dict(color='#ef4444', width=3),
            fillcolor='rgba(239, 68, 68, 0.3)'
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                gridcolor='#444'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def get_player_percentiles(df, player_name, metrics, position_filter=True):
    """Calcule les percentiles d'un joueur par rapport à sa position"""
    player_row = df[df['Joueur'] == player_name].iloc[0]
    
    if position_filter:
        # Filtrer par position similaire
        df_filtered = df[df['Position'] == player_row['Position']]
    else:
        df_filtered = df
        
    percentiles = []
    for metric in metrics:
        if metric in df.columns:
            # Calcul du rang percentile
            score = pd.qcut(df_filtered[metric].rank(method='first'), 100, labels=False).iloc[df_filtered.index.get_loc(player_row.name)]
            percentiles.append(score)
        else:
            percentiles.append(0)
            
    return percentiles

def find_similar_players(df, player_name, metrics, n=5):
    """Trouve les joueurs les plus similaires basés sur une liste de métriques"""
    if player_name not in df['Joueur'].values:
        return None
    
    # Filtrer par même position pour la pertinence
    target_pos = df[df['Joueur'] == player_name]['Position'].values[0]
    df_pos = df[df['Position'] == target_pos].copy().reset_index(drop=True)
    
    # Normalisation des données
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df_pos[metrics])
    
    # Index du joueur cible
    player_idx = df_pos[df_pos['Joueur'] == player_name].index[0]
    
    # Calcul distances
    distances = euclidean_distances(data_scaled[player_idx].reshape(1, -1), data_scaled)[0]
    
    # Créer dataframe de résultats
    similar_indices = distances.argsort()[1:n+1] # Exclure le joueur lui-même (index 0)
    result = df_pos.iloc[similar_indices].copy()
    result['Similarité'] = (1 - distances[similar_indices]) * 100 # Score de similarité inversé
    
    return result

# ==============================================================================
# INTERFACE PRINCIPALE
# ==============================================================================

# Sidebar
with st.sidebar:
    st.title("🔍 ScoutVision")
    st.markdown("---")
    
    # Filtres
    leagues = ["Toutes"] + sorted(df['Compétition'].dropna().unique().tolist())
    selected_league = st.selectbox("Compétition", leagues)
    
    if selected_league != "Toutes":
        df_filtered = df[df['Compétition'] == selected_league]
    else:
        df_filtered = df
        
    teams = ["Toutes"] + sorted(df_filtered['Équipe'].dropna().unique().tolist())
    selected_team = st.selectbox("Club", teams)
    
    if selected_team != "Toutes":
        df_filtered = df_filtered[df_filtered['Équipe'] == selected_team]
        
    positions = ["Toutes"] + sorted(df_filtered['Position'].dropna().unique().tolist())
    selected_pos = st.selectbox("Position", positions)
    
    if selected_pos != "Toutes":
        df_filtered = df_filtered[df_filtered['Position'] == selected_pos]
        
    st.markdown("---")
    
    # Sélection du joueur
    players_list = sorted(df_filtered['Joueur'].unique().tolist())
    selected_player = st.selectbox("Sélectionner un joueur", players_list)

# Main Content
if selected_player:
    player_data = df[df['Joueur'] == selected_player].iloc[0]
    
    # Header du joueur
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
    with col1:
        # Placeholder pour image (à remplacer par url réelle si dispo)
        st.image("https://img.freepik.com/vecteurs-libre/cercle-bleu-utilisateur-blanc_78370-4707.jpg", width=100)
    with col2:
        st.title(player_data['Joueur'])
        st.markdown(f"**{player_data['Équipe']}** | {player_data['Position']} | {int(player_data['Âge'])} ans | {player_data['Nationalité']}")
    with col3:
        try:
            val_market = player_data.get('Valeur marchande', 'N/A')
            if isinstance(val_market, (int, float)):
                 val_market = f"{val_market:,.0f} €"
        except:
            val_market = "N/A"
        st.metric("Valeur Marchande", val_market)
    with col4:
        st.metric("Minutes Jouées", int(player_data.get('Minutes jouées', 0)))

    st.markdown("---")

    # Onglets de navigation
    tab1, tab2, tab3 = st.tabs(["📊 Analyse Performance", "🆚 Comparaison", "🔎 Profils Similaires"])

    with tab1:
        # Définition des métriques pour le radar selon la position (simplifié)
        # Dans une V2, on peut rendre ça dynamique selon la position exacte (FW, DF, MF)
        radar_metrics = [
            'Buts hors penalty par 90 minutes', 
            'Passes décisives par 90 minutes', 
            'Passes clés', 
            'Dribbles réussis',
            'Actions menant à un tir par 90 minutes',
            'Passes progressives',
            'Tacles réussis',
            'Interceptions'
        ]
        
        # Nettoyage des noms pour l'affichage
        display_metrics = [m.replace('par 90 minutes', '/90').replace('Actions menant à un tir', 'SCA') for m in radar_metrics]
        
        # Calcul des percentiles
        percentiles = get_player_percentiles(df, selected_player, radar_metrics)
        
        col_radar, col_stats = st.columns([1, 1])
        
        with col_radar:
            st.subheader("Radar de Performance (Percentiles)")
            fig = create_radar_chart(percentiles, display_metrics, selected_player)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_stats:
            st.subheader("Statistiques Clés / 90 min")
            
            # Grille de métriques
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("xG (Expected Goals)", round(player_data.get('Buts attendus par 90 minutes', 0), 2))
            kpi2.metric("Buts", round(player_data.get('Buts par 90 minutes', 0), 2))
            kpi3.metric("Passes D", round(player_data.get('Passes décisives par 90 minutes', 0), 2))
            
            kpi4, kpi5, kpi6 = st.columns(3)
            kpi4.metric("Tirs", round(player_data.get('Tirs par 90 minutes', 0), 2))
            kpi5.metric("Passes Prog.", int(player_data.get('Passes progressives', 0))) # Total ou /90 à vérifier dans dataset
            kpi6.metric("Dribbles Réussis", int(player_data.get('Dribbles réussis', 0)))

    with tab2:
        st.subheader("Comparer avec un autre joueur")
        
        # Sélection du joueur à comparer
        all_players = sorted(df['Joueur'].unique().tolist())
        compare_player_name = st.selectbox("Choisir un adversaire", all_players, index=0)
        
        if compare_player_name:
            comp_col1, comp_col2 = st.columns(2)
            
            # Calcul des données pour le 2ème joueur
            p2_percentiles = get_player_percentiles(df, compare_player_name, radar_metrics)
            
            with comp_col1:
                # Radar de comparaison
                fig_comp = create_radar_chart(
                    percentiles, 
                    display_metrics, 
                    selected_player, 
                    comparison_data=p2_percentiles, 
                    comparison_name=compare_player_name
                )
                st.plotly_chart(fig_comp, use_container_width=True)
            
            with comp_col2:
                # Tableau comparatif
                p2_data = df[df['Joueur'] == compare_player_name].iloc[0]
                
                comp_data = {
                    'Métrique': radar_metrics,
                    f'{selected_player}': [player_data.get(m, 0) for m in radar_metrics],
                    f'{compare_player_name}': [p2_data.get(m, 0) for m in radar_metrics]
                }
                df_comp = pd.DataFrame(comp_data)
                st.dataframe(df_comp, hide_index=True, use_container_width=True)

    with tab3:
        st.subheader("Joueurs au profil similaire")
        st.write(f"Basé sur l'analyse statistique, voici les joueurs qui ressemblent le plus à **{selected_player}** dans le dataset.")
        
        # Métriques utilisées pour la similarité (à adapter selon position idéale)
        sim_metrics = [
            'Buts par 90 minutes', 'Passes décisives par 90 minutes', 'Tirs par 90 minutes',
            'Passes progressives', 'Dribbles réussis', 'Tacles réussis', 
            'Interceptions', 'Duels aériens gagnés'
        ]
        # Filtrer les métriques qui existent vraiment dans le DF
        valid_sim_metrics = [m for m in sim_metrics if m in df.columns]
        
        similar_players = find_similar_players(df, selected_player, valid_sim_metrics)
        
        if similar_players is not None and not similar_players.empty:
            # Affichage en cartes
            cols = st.columns(4)
            for idx, (i, row) in enumerate(similar_players.iterrows()):
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div style="background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #3b82f6; margin-bottom: 10px;">
                        <h4 style="color: white; margin:0;">{row['Joueur']}</h4>
                        <p style="color: #a0a0a0; font-size: 12px; margin-bottom: 5px;">{row['Équipe']}</p>
                        <p style="font-size: 20px; font-weight: bold; color: #3b82f6;">{row['Similarité']:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Pas assez de données pour trouver des profils similaires.")

else:
    st.info("Veuillez sélectionner un joueur dans la barre latérale pour commencer l'analyse.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>ScoutVision Pro © 2025 - Powered by Streamlit & Data Science</div>", unsafe_allow_html=True)
