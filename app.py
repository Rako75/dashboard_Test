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
    .player-card {
        background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FF6B35;
        margin: 20px 0;
        text-align: center;
    }
    .club-logo {
        max-width: 80px;
        max-height: 80px;
        object-fit: contain;
    }
    .player-photo {
        max-width: 150px;
        max-height: 200px;
        object-fit: cover;
        border-radius: 10px;
        border: 3px solid #FF6B35;
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

# ---------------------- FONCTIONS UTILITAIRES POUR IMAGES ----------------------

def get_player_photo(player_name):
    """Retourne le chemin de la photo du joueur ou None si non trouvée"""
    # Extensions possibles
    extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG']
    
    # Format attendu : **Prenom Nom.extension
    for ext in extensions:
        # Essayer avec le format exact : **Nom Prenom.extension
        photo_path = f"images_joueurs/**{player_name}{ext}"
        if os.path.exists(photo_path):
            return photo_path
    
    # Si pas trouvé avec le format exact, essayer de chercher dans tous les fichiers
    import glob
    for ext in extensions:
        # Chercher tous les fichiers avec cette extension
        pattern = f"images_joueurs/**{player_name}*{ext}"
        files = glob.glob(pattern)
        if files:
            return files[0]  # Retourner le premier fichier trouvé
        
        # Essayer aussi avec des variations de nom
        # Inverser prénom/nom si le nom contient un espace
        if " " in player_name:
            parts = player_name.split(" ")
            if len(parts) >= 2:
                # Essayer Nom Prénom au lieu de Prénom Nom
                reversed_name = " ".join(parts[::-1])
                pattern = f"images_joueurs/**{reversed_name}*{ext}"
                files = glob.glob(pattern)
                if files:
                    return files[0]
    
    return None

def get_club_logo(competition, team_name):
    """Retourne le chemin du logo du club selon la compétition"""
    # Mapping des compétitions vers les dossiers
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
    
    # Extensions possibles
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    
    # Format attendu : **Nom du Club.extension
    for ext in extensions:
        # Essayer avec le format exact : **Nom du Club.extension
        logo_path = f"{folder}/**{team_name}{ext}"
        if os.path.exists(logo_path):
            return logo_path
    
    # Si pas trouvé avec le format exact, essayer de chercher dans tous les fichiers
    import glob
    for ext in extensions:
        # Chercher tous les fichiers avec cette extension et le nom de l'équipe
        pattern = f"{folder}/**{team_name}*{ext}"
        files = glob.glob(pattern)
        if files:
            return files[0]  # Retourner le premier fichier trouvé
        
        # Essayer aussi avec des variations de nom (sans espaces, avec underscores, etc.)
        clean_team = team_name.replace(" ", "_").replace("'", "").replace("-", "_")
        pattern = f"{folder}/**{clean_team}*{ext}"
        files = glob.glob(pattern)
        if files:
            return files[0]
            
        # Essayer aussi de chercher juste par une partie du nom
        if " " in team_name:
            # Prendre le premier mot significatif
            first_word = team_name.split()[0]
            if len(first_word) > 3:  # Éviter les mots courts comme "FC", "AS", etc.
                pattern = f"{folder}/**{first_word}*{ext}"
                files = glob.glob(pattern)
                if files:
                    return files[0]
            
            # Prendre le dernier mot significatif
            last_word = team_name.split()[-1]
            if len(last_word) > 3:
                pattern = f"{folder}/**{last_word}*{ext}"
                files = glob.glob(pattern)
                if files:
                    return files[0]
    
    return None

def display_player_card(player_data, selected_competition):
    """Affiche la carte du joueur avec photo et logo"""
    # Récupérer la photo du joueur
    player_photo_path = get_player_photo(player_data['Joueur'])
    
    # Récupérer le logo du club
    club_logo_path = get_club_logo(selected_competition, player_data['Équipe'])
    
    # Créer la carte du joueur
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Afficher la photo du joueur
        if player_photo_path:
            try:
                player_image = Image.open(player_photo_path)
                st.image(player_image, caption=f"📸 {player_data['Joueur']}", 
                        use_column_width=True, output_format="auto")
            except Exception as e:
                st.info(f"📷 Erreur lors du chargement de la photo: {str(e)}")
                # Debug info
                st.text(f"Chemin tenté: {player_photo_path}")
        else:
            st.info(f"📷 Photo non trouvée pour: {player_data['Joueur']}")
            # Afficher les chemins tentés pour debug
            if st.checkbox("Afficher les détails de recherche"):
                st.text(f"Recherche effectuée pour: **{player_data['Joueur']}.jpg/jpeg")
                st.text(f"Dans le dossier: images_joueurs/")
                
                # Lister les fichiers disponibles dans le dossier
                try:
                    import glob
                    available_files = glob.glob("images_joueurs/**.*")
                    if available_files:
                        st.text("Fichiers disponibles:")
                        for file in available_files[:10]:  # Limiter à 10 fichiers
                            st.text(f"  - {file}")
                        if len(available_files) > 10:
                            st.text(f"  ... et {len(available_files) - 10} autres fichiers")
                    else:
                        st.text("Aucun fichier trouvé dans images_joueurs/")
                except Exception as e:
                    st.text(f"Erreur lors de la liste des fichiers: {str(e)}")
    
    with col2:
        # Informations centrales du joueur
        st.markdown(f"""
        <div class='player-card'>
            <h2 style='color: #FF6B35; margin-bottom: 20px;'>📊 Profil de {player_data['Joueur']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Afficher le logo du club
        if club_logo_path:
            try:
                club_image = Image.open(club_logo_path)
                st.image(club_image, caption=f"🏟️ {player_data['Équipe']}", 
                        use_column_width=True, output_format="auto")
            except Exception as e:
                st.info(f"🏟️ Erreur lors du chargement du logo: {str(e)}")
                st.text(f"Chemin tenté: {club_logo_path}")
        else:
            st.info(f"🏟️ Logo non trouvé pour: {player_data['Équipe']}")
            if st.checkbox("Afficher les détails de recherche logo", key="logo_debug"):
                st.text(f"Compétition: {selected_competition}")
                st.text(f"Équipe: {player_data['Équipe']}")
                
                # Afficher le mapping des dossiers
                league_folders = {
                    'Bundliga': 'Bundliga_Logos',
                    'La Liga': 'La_Liga_Logos', 
                    'Ligue 1': 'Ligue1_Logos',
                    'Premier League': 'Premier_League_Logos',
                    'Serie A': 'Serie_A_Logos'
                }
                expected_folder = league_folders.get(selected_competition, "Dossier non mappé")
                st.text(f"Dossier attendu: {expected_folder}")
                st.text(f"Format recherché: **{player_data['Équipe']}.png/jpg/jpeg")
                
                # Lister les fichiers disponibles dans le dossier du logo
                try:
                    import glob
                    if expected_folder != "Dossier non mappé":
                        available_logos = glob.glob(f"{expected_folder}/**.*")
                        if available_logos:
                            st.text("Logos disponibles (format **Nom.extension):")
                            for logo in available_logos[:15]:  # Limiter à 15 fichiers
                                # Extraire juste le nom du fichier pour l'affichage
                                filename = logo.split('/')[-1] if '/' in logo else logo.split('\\')[-1]
                                st.text(f"  - {filename}")
                            if len(available_logos) > 15:
                                st.text(f"  ... et {len(available_logos) - 15} autres fichiers")
                                
                            # Suggérer des correspondances possibles
                            team_words = player_data['Équipe'].lower().split()
                            suggestions = []
                            for logo in available_logos:
                                filename = logo.split('/')[-1] if '/' in logo else logo.split('\\')[-1]
                                filename_lower = filename.lower()
                                for word in team_words:
                                    if len(word) > 3 and word in filename_lower:
                                        suggestions.append(filename)
                                        break
                            
                            if suggestions:
                                st.text("Correspondances possibles trouvées:")
                                for suggestion in suggestions[:5]:
                                    st.text(f"  → {suggestion}")
                        else:
                            st.text(f"Aucun logo trouvé dans {expected_folder}/")
                            st.text("Vérifiez que le dossier existe et contient des fichiers **Nom.extension")
                except Exception as e:
                    st.text(f"Erreur lors de la liste des logos: {str(e)}")

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
        st.markdown(f"📊 **{nb_joueurs} joueurs** correspondent aux critères")
        
        st.markdown("---")
        
        # Sélection du joueur (maintenant filtré par minutes)
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
        
        # Utiliser df_filtered_minutes pour les comparaisons et calculs
        df_comparison = df_filtered_minutes  # Utiliser les données filtrées par minutes
    
        # Affichage de la carte du joueur avec photo et logo
        display_player_card(player_data, selected_competition)
        
        # Métriques de base
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
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Performance Offensive", "🛡️ Performance Défensive", "🎨 Performance Technique", "🔄 Comparer Joueurs"])
        
        with tab1:
            st.markdown("<h2 style='color: #FF6B35;'>🎯 Performance Offensive</h2>", unsafe_allow_html=True)
            
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
                        line=dict(color='white', width=1)
                    ),
                    text=list(actions_off.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=12)
                )])
                
                fig_bar_off.update_layout(
                    title=dict(
                        text="Actions Offensives",
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
                st.plotly_chart(fig_bar_off, use_container_width=True)
                
                # Radar professionnel des actions offensives
                st.markdown("<h3 style='color: #00C896; margin-top: 30px;'>🎯 Radar Offensif Professionnel</h3>", unsafe_allow_html=True)
                
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
            
            with col2:
                # Pourcentages de réussite offensifs
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
                    subplot_titles=list(pourcentages_off.keys())
                )
                
                colors_off = [COLORS['primary'], COLORS['secondary'], COLORS['success']]
                for i, (metric, value) in enumerate(pourcentages_off.items()):
                    fig_gauge_off.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_off[i]),
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
                
                fig_gauge_off.update_layout(
                    height=300, 
                    title_text="Pourcentages de Réussite Offensive",
                    title_font_color='white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_gauge_off, use_container_width=True)
                
                # Graphique de comparaison offensive
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
                    name=selected_player,
                    x=list(offensive_comparison.keys()),
                    y=list(offensive_comparison.values()),
                    marker_color=COLORS['primary']
                ))
                
                fig_off_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison_off.keys()),
                    y=list(avg_comparison_off.values()),
                    marker_color=COLORS['secondary']
                ))
                
                fig_off_comp.update_layout(
                    title=dict(
                        text='Actions Offensives par 90min vs Moyenne',
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
                
                st.plotly_chart(fig_off_comp, use_container_width=True)
            
            # Scatter plot pour comparaison offensive
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>🔍 Analyse Comparative Offensive</h3>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                # Sélection des métriques pour le scatter plot offensif
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
                    marker=dict(color=COLORS['accent'], size=8, opacity=0.6),
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
                    title=dict(text=f"{x_title} vs {y_title}", font=dict(size=14, color='white'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color='white')), tickfont=dict(color='white')),
                    yaxis=dict(title=dict(text=y_title, font=dict(color='white')), tickfont=dict(color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=400
                )
                
                st.plotly_chart(fig_scatter_off, use_container_width=True)
            
            # Métriques offensives par 90 minutes avec design amélioré
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>📊 Statistiques offensives par 90 minutes</h3>", unsafe_allow_html=True)
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
                
                # Radar professionnel des actions défensives
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
                    'Tacles/90': (df_comparison['Tacles gagnants'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Interceptions/90': (df_comparison['Interceptions'] / (df_comparison['Minutes jouées'] / 90)).mean(),
                    'Ballons récupérés/90': (df_comparison['Ballons récupérés'] / (df_comparison['Minutes jouées'] / 90)).mean()
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
            
            # Scatter plot pour comparaison défensive
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>🔍 Analyse Comparative Défensive</h3>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                # Sélection des métriques pour le scatter plot défensif
                metric_options_def = [
                    'Tacles gagnants', 'Interceptions', 'Ballons récupérés', 
                    'Duels aériens gagnés', 'Dégagements', 'Pourcentage de duels gagnés',
                    'Pourcentage de duels aériens gagnés'
                ]
                
                x_metric_def = st.selectbox("Métrique X", metric_options_def, index=0, key="x_def")
                y_metric_def = st.selectbox("Métrique Y", metric_options_def, index=1, key="y_def")
            
            with col_scatter2:
                # Créer le scatter plot défensif
                fig_scatter_def = go.Figure()
                
                # Convertir en par 90 minutes si nécessaire
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
                
                # Tous les joueurs
                fig_scatter_def.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color=COLORS['accent'], size=8, opacity=0.6),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                # Joueur sélectionné
                fig_scatter_def.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color=COLORS['primary'], size=20, symbol='star'),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_def.update_layout(
                    title=dict(text=f"{x_title} vs {y_title}", font=dict(size=14, color='white'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color='white')), tickfont=dict(color='white')),
                    yaxis=dict(title=dict(text=y_title, font=dict(color='white')), tickfont=dict(color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=400
                )
                
                st.plotly_chart(fig_scatter_def, use_container_width=True)
            
            # Métriques défensives par 90 minutes avec design amélioré
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>📊 Statistiques défensives par 90 min</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns(5)
            
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
            with col5:
                # Nouveau compteur de pourcentage de réussite défensive
                defensive_success = (player_data['Pourcentage de duels gagnés'] + player_data['Pourcentage de duels aériens gagnés']) / 2
                st.metric("Efficacité Défensive", f"{defensive_success:.1f}%")
        
        with tab3:
            st.markdown("<h2 style='color: #FF6B35;'>🎨 Performance Technique</h2>", unsafe_allow_html=True)
            
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
                        line=dict(color='white', width=1)
                    ),
                    text=list(actions_tech.values()),
                    textposition='outside',
                    textfont=dict(color='white', size=12)
                )])
                
                fig_bar_tech.update_layout(
                    title=dict(
                        text="Actions Techniques",
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
                st.plotly_chart(fig_bar_tech, use_container_width=True)
                
                # Radar de Capacité de Progression du Ballon
                st.markdown("<h3 style='color: #00C896; margin-top: 30px;'>🎨 Radar Technique Professionnel</h3>", unsafe_allow_html=True)
                
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
                
                # Calculer les percentiles pour les métriques techniques
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
                        
                        # Nettoyer les valeurs NaN et infinies
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
                
                # Ajouter la performance du joueur
                fig_tech_radar.add_trace(go.Scatterpolar(
                    r=tech_percentile_values,
                    theta=list(technical_metrics.keys()),
                    fill='toself',
                    fillcolor='rgba(0, 200, 150, 0.3)',
                    line=dict(color=COLORS['success'], width=3),
                    marker=dict(color=COLORS['success'], size=8, symbol='circle'),
                    name=f'{selected_player}',
                    hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
                    customdata=list(technical_metrics.values())
                ))
                
                # Calculer les percentiles des moyennes de la compétition
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
                
                # Ajouter une ligne de référence pour la moyenne de la compétition
                fig_tech_radar.add_trace(go.Scatterpolar(
                    r=tech_avg_percentiles,
                    theta=list(technical_metrics.keys()),
                    mode='lines',
                    line=dict(color='rgba(255,255,255,0.7)', width=2, dash='dash'),
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
                            text=f"Performance Technique vs Moyenne {selected_competition}",
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
                
                st.plotly_chart(fig_tech_radar, use_container_width=True)
            
            with col2:
                # Pourcentages de réussite techniques
                pourcentages_tech = {
                    'Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                    'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                    'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
                }
                
                # Nettoyer les valeurs NaN
                pourcentages_tech = {k: v if pd.notna(v) else 0 for k, v in pourcentages_tech.items()}
                
                fig_gauge_tech = make_subplots(
                    rows=1, cols=3,
                    specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                    subplot_titles=list(pourcentages_tech.keys())
                )
                
                colors_tech = [COLORS['success'], COLORS['warning'], COLORS['primary']]
                for i, (metric, value) in enumerate(pourcentages_tech.items()):
                    fig_gauge_tech.add_trace(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            gauge=dict(
                                axis=dict(range=[0, 100]),
                                bar=dict(color=colors_tech[i]),
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
                
                fig_gauge_tech.update_layout(
                    height=300, 
                    title_text="Pourcentages de Réussite Technique",
                    title_font_color='white',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_gauge_tech, use_container_width=True)
                
                # Graphique de comparaison technique
                technical_comparison = {
                    'Passes/90': player_data['Passes tentées'] / (player_data['Minutes jouées'] / 90),
                    'Dribbles/90': player_data['Dribbles tentés'] / (player_data['Minutes jouées'] / 90),
                    'Touches/90': player_data['Touches de balle'] / (player_data['Minutes jouées'] / 90)
                }
                
                # Moyennes de la compétition
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
                    marker_color=COLORS['primary']
                ))
                
                fig_tech_comp.add_trace(go.Bar(
                    name='Moyenne compétition',
                    x=list(avg_comparison_tech.keys()),
                    y=list(avg_comparison_tech.values()),
                    marker_color=COLORS['secondary']
                ))
                
                fig_tech_comp.update_layout(
                    title=dict(
                        text='Actions Techniques par 90min vs Moyenne',
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
                
                st.plotly_chart(fig_tech_comp, use_container_width=True)
            
            # Scatter plot pour comparaison technique
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>🔍 Analyse Comparative Technique</h3>", unsafe_allow_html=True)
            
            col_scatter1, col_scatter2 = st.columns(2)
            
            with col_scatter1:
                # Sélection des métriques pour le scatter plot technique
                metric_options_tech = [
                    'Passes tentées', 'Pourcentage de passes réussies', 'Passes progressives',
                    'Passes clés', 'Dribbles tentés', 'Pourcentage de dribbles réussis',
                    'Touches de balle', 'Distance progressive des passes'
                ]
                
                x_metric_tech = st.selectbox("Métrique X", metric_options_tech, index=0, key="x_tech")
                y_metric_tech = st.selectbox("Métrique Y", metric_options_tech, index=1, key="y_tech")
            
            with col_scatter2:
                # Créer le scatter plot technique
                fig_scatter_tech = go.Figure()
                
                # Convertir en par 90 minutes si nécessaire pour les métriques non-pourcentage
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
                
                # Tous les joueurs
                fig_scatter_tech.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers',
                    name='Autres joueurs',
                    marker=dict(color=COLORS['accent'], size=8, opacity=0.6),
                    text=df_comparison['Joueur'],
                    hovertemplate='<b>%{text}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                # Joueur sélectionné
                fig_scatter_tech.add_trace(go.Scatter(
                    x=[x_player],
                    y=[y_player],
                    mode='markers',
                    name=selected_player,
                    marker=dict(color=COLORS['primary'], size=20, symbol='star'),
                    hovertemplate=f'<b>{selected_player}</b><br>' + x_title + ': %{x:.2f}<br>' + y_title + ': %{y:.2f}<extra></extra>'
                ))
                
                fig_scatter_tech.update_layout(
                    title=dict(text=f"{x_title} vs {y_title}", font=dict(size=14, color='white'), x=0.5),
                    xaxis=dict(title=dict(text=x_title, font=dict(color='white')), tickfont=dict(color='white')),
                    yaxis=dict(title=dict(text=y_title, font=dict(color='white')), tickfont=dict(color='white')),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=400
                )
                
                st.plotly_chart(fig_scatter_tech, use_container_width=True)
            
            # Métriques techniques détaillées
            st.markdown("<h3 style='color: #FF6B35; margin-top: 30px;'>📊 Statistiques Techniques Détaillées</h3>", unsafe_allow_html=True)
            
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
                # Nouveau compteur de pourcentage de réussite des passes en zones critiques
                passes_critiques = (player_data.get('Pourcentage de passes longues réussies', 0) + 
                                   player_data.get('Pourcentage de passes courtes réussies', 0)) / 2
                st.metric("Précision Zones Critiques", f"{passes_critiques:.1f}%")
        
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
                    values1 = calculate_percentiles(selected_player, df_comparison)
                    
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

    else:
        st.warning("Veuillez ajuster les filtres pour sélectionner un joueur.")

    # Footer avec design professionnel (affiché même sans joueur sélectionné)
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
