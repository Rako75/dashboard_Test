import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.neighbors import NearestNeighbors

# ==============================================================================
# 1. CONFIGURATION & DESIGN SYSTEM (CSS PRO)
# ==============================================================================
st.set_page_config(
    page_title="RakoStats Elite | Plateforme de Recrutement",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Palette de couleurs "Elite"
COLORS = {
    'bg': '#0e1117',
    'card': '#1a1d24',
    'primary': '#3b82f6',     # Bleu électrique
    'secondary': '#10b981',   # Vert data
    'accent': '#f59e0b',      # Orange focus
    'text': '#e2e8f0',
    'subtext': '#94a3b8'
}

# CSS Injecté pour transformer Streamlit
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: {COLORS['bg']};
        color: {COLORS['text']};
    }}
    
    /* Cartes de statistiques */
    .stat-card {{
        background-color: {COLORS['card']};
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }}
    .stat-card:hover {{
        transform: translateY(-2px);
        border-color: {COLORS['primary']};
    }}
    .stat-value {{
        font-size: 28px;
        font-weight: 700;
        color: {COLORS['primary']};
    }}
    .stat-label {{
        font-size: 13px;
        color: {COLORS['subtext']};
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 5px;
    }}
    
    /* Onglets personnalisés */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['card']};
        border-radius: 6px;
        color: {COLORS['subtext']};
        font-weight: 600;
        border: 1px solid #2d3748;
        padding: 10px 20px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['primary']} !important;
        color: white !important;
        border: none;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #111318;
        border-right: 1px solid #2d3748;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. MOTEUR DE DONNÉES ET CALCULS
# ==============================================================================

@st.cache_data
def load_and_prep_data():
    try:
        df = pd.read_csv('df_BIG2025.csv', sep=';')
        
        # Nettoyage et conversion
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # Filtre de base : éliminer les erreurs de saisie ou joueurs fantômes
        if 'Minutes jouées' in df.columns:
            df = df[df['Minutes jouées'] > 270] # Au moins 3 matchs complets
            
        # --- CRÉATION DE MÉTRIQUES AVANCÉES ---
        # Efficacité devant le but
        if 'Buts' in df.columns and 'Buts attendus (xG)' in df.columns:
            df['Finishing Overperf'] = df['Buts'] - df['Buts attendus (xG)']
            
        # Contribution offensive totale
        if 'Buts' in df.columns and 'Passes décisives' in df.columns:
            df['G+A'] = df['Buts'] + df['Passes décisives']
            
        return df
    except Exception as e:
        st.error(f"Erreur critique de chargement : {e}")
        return pd.DataFrame()

df = load_and_prep_data()

# Dictionnaire de mappage pour les noms de colonnes (UI vs Data)
# Permet d'avoir des noms courts sur les graphiques
METRICS_MAP = {
    'Attaque': {
        'Buts/90': 'Buts par 90 minutes',
        'xG/90': 'Buts attendus par 90 minutes',
        'Tirs/90': 'Tirs par 90 minutes',
        'Dribbles': 'Dribbles réussis',
        'Touchés Surf. Réparation': 'Ballons touchés dans la surface de réparation adverse' 
    },
    'Création': {
        'Passes D/90': 'Passes décisives par 90 minutes',
        'xAG/90': 'Passes décisives attendues par 90 minutes',
        'Passes Clés': 'Passes clés',
        'Passes Prog.': 'Passes progressives',
        'SCA/90': 'Actions menant à un tir par 90 minutes'
    },
    'Défense': {
        'Tacles': 'Tacles réussis',
        'Interceptions': 'Interceptions',
        'Duels Aériens %': 'Pourcentage de duels aériens gagnés',
        'Ballons Récupérés': 'Ballons récupérés'
    }
}

# Fonction pour calculer les percentiles dynamiques
def calculate_percentiles(df, target_player, metrics, position_filter):
    # Filtrer par position pour comparer ce qui est comparable
    cohort = df[df['Position'] == position_filter].copy()
    
    if target_player not in cohort['Joueur'].values:
        return None, None

    player_stats = cohort[cohort['Joueur'] == target_player].iloc[0]
    percentiles = {}
    
    for label, col_name in metrics.items():
        if col_name in cohort.columns:
            # Calcul du rang percentile (0 à 100)
            rank = cohort[col_name].rank(pct=True)
            player_pctl = rank[cohort['Joueur'] == target_player].values[0] * 100
            percentiles[label] = player_pctl
            
    return percentiles, player_stats

# ==============================================================================
# 3. VISUALISATIONS AVANCÉES
# ==============================================================================

def create_pizza_chart(percentiles_dict, player_name, position):
    categories = list(percentiles_dict.keys())
    values = list(percentiles_dict.values())
    
    # Création du Radar Chart "Pizza Style"
    fig = go.Figure()

    fig.add_trace(go.Barpolar(
        r=values,
        theta=categories,
        width=[1]*len(values), # Largeur égale pour faire des tranches
        marker_color=[COLORS['primary'] if v > 80 else COLORS['secondary'] if v > 50 else '#ef4444' for v in values],
        marker_line_color=COLORS['bg'],
        marker_line_width=2,
        opacity=0.8,
        name='Percentile'
    ))

    fig.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(range=[0, 100], showticklabels=False, ticks=''),
            angularaxis=dict(showticklabels=True, tickfont=dict(size=10, color='white'))
        ),
        title=dict(
            text=f"Profil Statistique : {player_name}<br><span style='font-size:12px; color:gray'>vs autres {position}s (Percentiles)</span>",
            y=0.95
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def create_scatter_analysis(df, x_col, y_col, color_col, hover_name, size_col=None):
    fig = px.scatter(
        df, x=x_col, y=y_col, color=color_col, hover_name=hover_name,
        size=size_col, size_max=25,
        color_discrete_sequence=px.colors.qualitative.Bold,
        template='plotly_dark',
        title=f"Analyse Croisée : {x_col} vs {y_col}"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", y=-0.2)
    )
    return fig

# ==============================================================================
# 4. INTERFACE UTILISATEUR
# ==============================================================================

# Sidebar Pro
with st.sidebar:
    st.title("RakoStats **Elite**")
    st.caption("Plateforme d'analyse et de recrutement")
    st.markdown("---")
    
    mode = st.radio("Module", ["👤 Analyse Joueur", "🔍 Smart Scouting", "📈 Data Explorer"], index=0)
    
    st.markdown("---")
    
    # Filtres globaux
    st.subheader("Filtres Globaux")
    selected_leagues = st.multiselect("Compétitions", df['Compétition'].unique(), default=df['Compétition'].unique())
    min_minutes = st.slider("Minutes min.", 0, 3000, 500, step=100)
    
    # Application des filtres
    df_filtered = df[
        (df['Compétition'].isin(selected_leagues)) & 
        (df['Minutes jouées'] >= min_minutes)
    ]

# ------------------------------------------------------------------------------
# MODULE 1 : ANALYSE JOUEUR (Deep Dive)
# ------------------------------------------------------------------------------
if mode == "👤 Analyse Joueur":
    # Sélecteurs en haut de page pour accès rapide
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        selected_pos_player = st.selectbox("Filtrer par Position", ["Toutes"] + sorted(df_filtered['Position'].unique().tolist()))
    
    players_pool = df_filtered if selected_pos_player == "Toutes" else df_filtered[df_filtered['Position'] == selected_pos_player]
    
    with col_sel2:
        selected_player = st.selectbox("Rechercher un joueur", sorted(players_pool['Joueur'].unique()))

    if selected_player:
        # Récupération des données
        player_row = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
        pos = player_row['Position']
        
        # En-tête Joueur
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #1a1d24 0%, #0e1117 100%); padding: 25px; border-radius: 12px; border-left: 5px solid {COLORS['primary']}; margin-bottom: 20px;">
            <h1 style="margin:0; font-size: 3rem;">{player_row['Joueur']}</h1>
            <h3 style="margin:0; color: {COLORS['primary']};">{player_row['Équipe']} • {pos} • {int(player_row['Âge'])} ans</h3>
            <p style="margin-top:10px; color: #94a3b8;">{player_row['Nationalité']} | {player_row['Compétition']}</p>
        </div>
        """, unsafe_allow_html=True)

        # KPIs Principaux
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.markdown(f"<div class='stat-card'><div class='stat-value'>{player_row.get('Matchs joués', 0)}</div><div class='stat-label'>Matchs</div></div>", unsafe_allow_html=True)
        k2.markdown(f"<div class='stat-card'><div class='stat-value'>{player_row.get('Buts', 0)}</div><div class='stat-label'>Buts</div></div>", unsafe_allow_html=True)
        k3.markdown(f"<div class='stat-card'><div class='stat-value'>{player_row.get('Passes décisives', 0)}</div><div class='stat-label'>Passes D</div></div>", unsafe_allow_html=True)
        
        # Gestion safe des xG
        xg_val = round(player_row.get('Buts attendus (xG)', 0), 2)
        k4.markdown(f"<div class='stat-card'><div class='stat-value'>{xg_val}</div><div class='stat-label'>xG Total</div></div>", unsafe_allow_html=True)
        
        # Valeur marchande
        vm = player_row.get('Valeur marchande', 'N/A')
        if isinstance(vm, (int, float)): vm = f"{vm/1000000:.1f}M€"
        k5.markdown(f"<div class='stat-card'><div class='stat-value' style='color:{COLORS['secondary']}'>{vm}</div><div class='stat-label'>Valeur Est.</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        # Analyse détaillée
        col_viz, col_context = st.columns([1.5, 1])
        
        with col_viz:
            # Construction des métriques pour le radar selon la position
            # On fusionne tous les dictionnaires de METRICS_MAP pour le radar global, 
            # ou on peut sélectionner selon la position. Ici, faisons un mix "General".
            radar_metrics = {**METRICS_MAP['Attaque'], **METRICS_MAP['Création']}
            if 'Def' in pos or 'DM' in pos:
                radar_metrics.update(METRICS_MAP['Défense'])
            
            # Calcul percentiles
            percentiles, _ = calculate_percentiles(df_filtered, selected_player, radar_metrics, pos)
            
            if percentiles:
                fig_pizza = create_pizza_chart(percentiles, selected_player, pos)
                st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                st.warning("Données insuffisantes pour le radar.")

        with col_context:
            st.subheader("🔍 Efficacité & Style")
            
            # Scatter Plot Mini : Buts vs xG pour la ligue
            fig_mini = px.scatter(
                df_filtered[df_filtered['Position'] == pos], 
                x='Buts attendus par 90 minutes', 
                y='Buts par 90 minutes',
                hover_name='Joueur',
                color_discrete_sequence=[COLORS['subtext']],
                opacity=0.5,
                title="Positionnement dans la ligue (xG vs Buts)"
            )
            # Mettre en évidence le joueur
            fig_mini.add_trace(go.Scatter(
                x=[player_row.get('Buts attendus par 90 minutes', 0)],
                y=[player_row.get('Buts par 90 minutes', 0)],
                mode='markers',
                marker=dict(color=COLORS['primary'], size=15, line=dict(color='white', width=2)),
                name=selected_player
            ))
            fig_mini.update_layout(template='plotly_dark', showlegend=False, margin=dict(l=0, r=0, t=30, b=0), height=300)
            st.plotly_chart(fig_mini, use_container_width=True)
            
            st.markdown("### Similaires (Mathématiques)")
            # Moteur de similarité rapide
            features = ['Âge', 'Buts par 90 minutes', 'Passes décisives par 90 minutes', 'Passes progressives', 'Dribbles réussis']
            # Nettoyer les features existantes
            features = [f for f in features if f in df_filtered.columns]
            
            if len(features) > 2:
                scaler = StandardScaler()
                # Filtrer par position pour la similarité
                df_sim = df_filtered[df_filtered['Position'] == pos].copy().fillna(0)
                X = scaler.fit_transform(df_sim[features])
                
                nbrs = NearestNeighbors(n_neighbors=4, algorithm='ball_tree').fit(X)
                # Trouver l'index du joueur
                try:
                    idx = df_sim[df_sim['Joueur'] == selected_player].index[0]
                    # Conversion de l'index pandas en index numpy
                    loc_idx = df_sim.index.get_loc(idx)
                    distances, indices = nbrs.kneighbors([X[loc_idx]])
                    
                    for i in range(1, 4): # Ignorer le 0 (lui-même)
                        sim_idx = indices[0][i]
                        sim_player = df_sim.iloc[sim_idx]
                        st.markdown(f"""
                        <div style="border-bottom:1px solid #333; padding:8px; display:flex; justify-content:space-between;">
                            <span><b>{sim_player['Joueur']}</b> <span style='font-size:0.8em; color:gray'>({sim_player['Équipe']})</span></span>
                            <span style="color:{COLORS['accent']}">Similaire</span>
                        </div>
                        """, unsafe_allow_html=True)
                except:
                    st.write("Pas assez de données pour la similarité.")


# ------------------------------------------------------------------------------
# MODULE 2 : SMART SCOUTING (Recherche Avancée)
# ------------------------------------------------------------------------------
elif mode == "🔍 Smart Scouting":
    st.header("🕵️ Moteur de Recherche Avancé")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        target_pos = st.selectbox("Position Cible", sorted(df_filtered['Position'].unique()))
    with c2:
        age_range = st.slider("Tranche d'âge", 15, 40, (17, 25))
    with c3:
        # Sélection des métriques à pondérer
        available_metrics = sorted([c for c in df.select_dtypes(include=np.number).columns if '90' in c or '%' in c])
        metric_1 = st.selectbox("Métrique Prioritaire (Axe X)", available_metrics, index=0)
        metric_2 = st.selectbox("Métrique Secondaire (Axe Y)", available_metrics, index=1)

    st.markdown("---")
    
    # Filtrage
    scout_df = df_filtered[
        (df_filtered['Position'] == target_pos) &
        (df_filtered['Âge'] >= age_range[0]) & 
        (df_filtered['Âge'] <= age_range[1])
    ].copy()
    
    col_res_viz, col_res_table = st.columns([2, 1])
    
    with col_res_viz:
        st.subheader("Distribution des Talents")
        if not scout_df.empty:
            fig_scout = px.scatter(
                scout_df,
                x=metric_1,
                y=metric_2,
                color='Âge',
                size='Valeur marchande' if 'Valeur marchande' in df.columns else None,
                hover_data=['Joueur', 'Équipe'],
                text='Joueur',
                template='plotly_dark',
                color_continuous_scale='Viridis'
            )
            fig_scout.update_traces(textposition='top center')
            fig_scout.update_layout(height=600)
            st.plotly_chart(fig_scout, use_container_width=True)
        else:
            st.info("Aucun joueur ne correspond aux critères.")
            
    with col_res_table:
        st.subheader("Top Profils Détectés")
        if not scout_df.empty:
            # Score simple : Somme normalisée des deux métriques
            m1_norm = (scout_df[metric_1] - scout_df[metric_1].min()) / (scout_df[metric_1].max() - scout_df[metric_1].min())
            m2_norm = (scout_df[metric_2] - scout_df[metric_2].min()) / (scout_df[metric_2].max() - scout_df[metric_2].min())
            scout_df['Scout Score'] = (m1_norm + m2_norm) * 50
            
            top_gems = scout_df.sort_values('Scout Score', ascending=False).head(10)
            
            st.dataframe(
                top_gems[['Joueur', 'Équipe', 'Âge', metric_1, metric_2, 'Scout Score']],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Scout Score": st.column_config.ProgressColumn(
                        "Score",
                        format="%.0f",
                        min_value=0,
                        max_value=100,
                    )
                }
            )

# ------------------------------------------------------------------------------
# MODULE 3 : DATA EXPLORER (Exploration Libre)
# ------------------------------------------------------------------------------
elif mode == "📈 Data Explorer":
    st.header("📈 Exploration Libre des Données")
    
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    with row1_col1:
        x_axis = st.selectbox("Axe X", df.select_dtypes(include=np.number).columns, index=10)
    with row1_col2:
        y_axis = st.selectbox("Axe Y", df.select_dtypes(include=np.number).columns, index=11)
    with row1_col3:
        color_by = st.selectbox("Colorer par", ['Position', 'Compétition', 'Équipe'])
        
    fig_explorer = px.scatter(
        df_filtered,
        x=x_axis,
        y=y_axis,
        color=color_by,
        hover_name='Joueur',
        hover_data=['Équipe', 'Âge'],
        template='plotly_dark',
        height=700
    )
    st.plotly_chart(fig_explorer, use_container_width=True)
