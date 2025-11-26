import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import stats

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="PitchPerfect Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ (THE ATHLETIC VIBE) ---
st.markdown("""
<style>
    /* Polices et Couleurs */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700;900&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #FAFAFA;
        color: #121212;
    }
    
    h1, h2, h3 {
        font-family: 'Merriweather', serif;
        color: #121212;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e5e5;
    }
    
    /* Métriques */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Titre Principal */
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        border-bottom: 4px solid #121212;
        margin-bottom: 20px;
        padding-bottom: 10px;
    }
    
    .athletic-red { color: #E90052; }
</style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    try:
        # Tentative de chargement du fichier réel
        df = pd.read_csv('df_BIG2025.csv', sep=';')
        # Nettoyage rapide des colonnes numériques (gestion des virgules vs points)
        cols_to_fix = ['Buts attendus (xG)', 'Passes décisives attendues (xAG)', 
                       'Buts par 90 minutes', 'Passes progressives', 'Courses progressives']
        for col in cols_to_fix:
            if col in df.columns and df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '.').astype(float)
        return df
    except FileNotFoundError:
        # Génération de données de DÉMO si le fichier n'est pas trouvé
        data = {
            'Joueur': ['Haaland', 'Mbappé', 'Kane', 'Salah', 'Saka', 'Vinicius', 'Rodri', 'Wirtz', 'Osimhen', 'Lautaro'],
            'Équipe': ['Man City', 'Real Madrid', 'Bayern', 'Liverpool', 'Arsenal', 'Real Madrid', 'Man City', 'Leverkusen', 'Napoli', 'Inter'],
            'Compétition': ['Premier League', 'La Liga', 'Bundesliga', 'Premier League', 'Premier League', 'La Liga', 'Premier League', 'Bundesliga', 'Serie A', 'Serie A'],
            'Position': ['FW', 'FW', 'FW', 'FW', 'FW', 'FW', 'MF', 'MF', 'FW', 'FW'],
            'Âge': [24, 26, 31, 32, 23, 24, 28, 21, 26, 27],
            'Buts': [29, 24, 28, 18, 14, 12, 7, 11, 15, 22],
            'Passes décisives': [5, 7, 8, 12, 11, 9, 6, 11, 3, 4],
            'Buts attendus (xG)': [28.5, 23.1, 26.2, 19.5, 13.2, 11.5, 5.5, 9.5, 14.5, 20.1],
            'Passes décisives attendues (xAG)': [3.2, 5.4, 6.1, 9.2, 9.5, 7.8, 4.2, 10.2, 1.8, 3.0],
            'Passes progressives': [12, 35, 45, 60, 55, 40, 210, 150, 15, 25],
            'Courses progressives': [45, 120, 30, 85, 110, 145, 60, 105, 50, 40],
            'Actions menant à un tir': [88, 112, 95, 105, 125, 118, 90, 125, 70, 80]
        }
        return pd.DataFrame(data)

df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🔍 SCOUTING TOOL")
    
    # Filtres
    leagues = ['Toutes'] + sorted(df['Compétition'].unique().tolist())
    selected_league = st.selectbox('Compétition', leagues)
    
    if selected_league != 'Toutes':
        filtered_df = df[df['Compétition'] == selected_league]
    else:
        filtered_df = df
        
    teams = ['Toutes'] + sorted(filtered_df['Équipe'].unique().tolist())
    selected_team = st.selectbox('Équipe', teams)
    
    if selected_team != 'Toutes':
        filtered_df = filtered_df[filtered_df['Équipe'] == selected_team]
        
    positions = ['Toutes'] + sorted(filtered_df['Position'].unique().tolist())
    selected_pos = st.selectbox('Position', positions)
    
    if selected_pos != 'Toutes':
        filtered_df = filtered_df[filtered_df['Position'] == selected_pos]
        
    # Sélecteur de joueur
    player_list = sorted(filtered_df['Joueur'].unique().tolist())
    selected_player_name = st.selectbox('Sélectionner un Joueur', player_list)

# --- DATA PROCESSING FOR SELECTED PLAYER ---
player_stats = df[df['Joueur'] == selected_player_name].iloc[0]
player_pos = player_stats['Position']

# Comparaison Cohort (Même position, toutes ligues ou ligue actuelle selon préférence)
# Ici on compare à TOUS les joueurs de la même position dans le dataset pour le percentile
cohort_df = df[df['Position'] == player_pos]

# --- FONCTIONS GRAPHIQUES ---

def create_pizza_chart(player, cohort):
    # Métriques à analyser
    metrics = {
        'Buts': 'Buts',
        'xG': 'Buts attendus (xG)',
        'Passes D.': 'Passes décisives',
        'xAG': 'Passes décisives attendues (xAG)',
        'Tirs Créés': 'Actions menant à un tir',
        'Passe Prog': 'Passes progressives',
        'Course Prog': 'Courses progressives'
    }
    
    r_values = []
    theta_values = []
    
    for label, col in metrics.items():
        if col in cohort.columns:
            # Calcul du percentile
            val = player[col]
            percentile = stats.percentileofscore(cohort[col], val)
            r_values.append(percentile)
            theta_values.append(label)
    
    # Fermer la boucle du radar
    r_values.append(r_values[0])
    theta_values.append(theta_values[0])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=r_values,
        theta=theta_values,
        fill='toself',
        name=player['Joueur'],
        line=dict(color='#E90052', width=2),
        fillcolor='rgba(233, 0, 82, 0.4)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False),
            angularaxis=dict(tickfont=dict(size=12, family="Merriweather", color="black"))
        ),
        showlegend=False,
        height=400,
        margin=dict(t=40, b=40, l=40, r=40),
        font=dict(family="Inter"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_scatter(data, x_col, y_col, highlight_name, title):
    fig = px.scatter(
        data, 
        x=x_col, 
        y=y_col, 
        hover_name='Joueur',
        hover_data=['Équipe'],
        color_discrete_sequence=['#A8A29E'] # Gris par défaut
    )
    
    # Mettre en évidence le joueur sélectionné
    highlight = data[data['Joueur'] == highlight_name]
    
    fig.add_trace(go.Scatter(
        x=highlight[x_col],
        y=highlight[y_col],
        mode='markers',
        marker=dict(color='#E90052', size=15, line=dict(color='white', width=2)),
        name=highlight_name,
        hoverinfo='skip' # Déjà géré par le premier trace ou custom
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(family="Merriweather", size=18)),
        plot_bgcolor='white',
        xaxis=dict(gridcolor='#F3F4F6', title=x_col),
        yaxis=dict(gridcolor='#F3F4F6', title=y_col),
        showlegend=False,
        height=350
    )
    return fig

# --- LAYOUT PRINCIPAL ---

st.markdown(f'<div class="main-title">{selected_player_name}</div>', unsafe_allow_html=True)

# 1. Header Info
col1, col2, col3, col4 = st.columns(4)
col1.metric("Équipe", player_stats['Équipe'])
col2.metric("Position", player_stats['Position'])
col3.metric("Matchs", player_stats.get('Matchs joués', 'N/A'))
col4.metric("Âge", player_stats['Âge'])

st.divider()

# 2. Pizza Chart & Analyse
col_viz, col_context = st.columns([1.5, 1])

with col_viz:
    st.subheader("Profil Statistique (Percentiles)")
    st.caption(f"Comparé aux joueurs de position '{player_pos}'")
    pizza_fig = create_pizza_chart(player_stats, cohort_df)
    st.plotly_chart(pizza_fig, use_container_width=True)

with col_context:
    st.subheader("Performance Offensive")
    
    goals = player_stats.get('Buts', 0)
    xg = player_stats.get('Buts attendus (xG)', 0)
    delta = goals - xg
    
    st.metric("Buts Réels", goals)
    st.metric("Expected Goals (xG)", xg, delta=f"{delta:.2f}", delta_color="normal")
    
    st.markdown("---")
    st.subheader("Création")
    st.metric("Passes Décisives", player_stats.get('Passes décisives', 0))
    st.metric("Expected Assists (xAG)", player_stats.get('Passes décisives attendues (xAG)', 0))

st.divider()

# 3. Deep Dive Visualizations
st.subheader("Analyse Contextuelle")

tab1, tab2 = st.tabs(["🚀 Progression de Balle", "🎯 Efficacité de Finition"])

with tab1:
    st.markdown("Ce graphique montre comment le joueur fait avancer le ballon par rapport à ses pairs.")
    scat_prog = create_scatter(
        cohort_df, 
        'Passes progressives', 
        'Courses progressives', 
        selected_player_name, 
        "Style de Progression : Passe vs Course"
    )
    st.plotly_chart(scat_prog, use_container_width=True)

with tab2:
    st.markdown("Comparaison de la qualité des tirs obtenus (xG) vs la conversion réelle (Buts).")
    scat_shoot = create_scatter(
        cohort_df, 
        'Buts attendus (xG)', 
        'Buts', 
        selected_player_name, 
        "Finition : xG vs Buts"
    )
    # Ajouter une ligne x=y pour référence
    max_val = max(cohort_df['Buts'].max(), cohort_df['Buts attendus (xG)'].max())
    scat_shoot.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="gray", dash="dot"))
    
    st.plotly_chart(scat_shoot, use_container_width=True)

# 4. Footer
st.markdown("""
<div style="text-align: center; color: #888; margin-top: 50px; font-size: 12px;">
    Généré par PitchPerfect Python Engine • Inspiré par The Athletic<br>
    Données basées sur le fichier df_BIG2025.csv
</div>
""", unsafe_allow_html=True)