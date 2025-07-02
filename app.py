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
import glob
from typing import Dict, List, Optional, Tuple

# ================================================================================================
# CONFIGURATION DE L'APPLICATION
# ================================================================================================

class AppConfig:
    """Configuration centralisée de l'application"""
    
    # Configuration de la page
    PAGE_CONFIG = {
        "page_title": "⚽ Dashboard Football Pro",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Palette de couleurs professionnelle
    COLORS = {
        'primary': '#FF6B35',           # Orange vibrant
        'secondary': '#004E89',         # Bleu marine
        'accent': '#1A759F',           # Bleu clair
        'success': '#00C896',          # Vert emeraude
        'warning': '#F7B801',          # Jaune doré
        'danger': '#D62828',           # Rouge
        'dark': '#1E2640',             # Bleu foncé
        'light': '#F8F9FA',            # Blanc cassé
        'gradient': ['#FF6B35', '#004E89', '#1A759F', '#00C896', '#F7B801']
    }
    
    # Configuration des radars
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

# ================================================================================================
# GESTIONNAIRE DE STYLES CSS
# ================================================================================================

class StyleManager:
    """Gestionnaire centralisé des styles CSS"""
    
    @staticmethod
    def load_custom_css():
        """Charge les styles CSS personnalisés"""
        return """
        <style>
        /* ===== STYLES GLOBAUX ===== */
        .main {
            background: linear-gradient(135deg, #0E1117 0%, #1E2640 100%);
            color: #FFFFFF;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0E1117 0%, #1E2640 100%);
        }
        
        /* ===== STYLES DES ONGLETS ===== */
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%);
            border-radius: 15px;
            padding: 8px;
            margin-bottom: 20px;
            border: 2px solid #FF6B35;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #FFFFFF;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #FF6B35 0%, #F7B801 100%);
            color: #FFFFFF;
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        }
        
        /* ===== CARTES DE CONTENU ===== */
        .dashboard-card {
            background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%);
            padding: 25px;
            border-radius: 20px;
            border: 2px solid #4A5568;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        
        .dashboard-card:hover {
            border-color: #FF6B35;
            box-shadow: 0 12px 35px rgba(255, 107, 53, 0.2);
            transform: translateY(-2px);
        }
        
        .player-header-card {
            background: linear-gradient(135deg, #FF6B35 0%, #F7B801 100%);
            padding: 30px;
            border-radius: 25px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #718096;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: #00C896;
            box-shadow: 0 8px 20px rgba(0, 200, 150, 0.2);
        }
        
        /* ===== CONTENEURS D'IMAGES ===== */
        .image-container {
            background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%);
            border-radius: 20px;
            padding: 20px;
            border: 3px solid #FF6B35;
            overflow: hidden;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        
        .club-logo-container {
            background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%);
            border-radius: 15px;
            padding: 15px;
            border: 2px solid #FF6B35;
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        
        /* ===== STYLES DE TEXTE ===== */
        .section-title {
            color: #FF6B35;
            font-size: 2.5em;
            font-weight: 800;
            text-align: center;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .subsection-title {
            color: #00C896;
            font-size: 1.8em;
            font-weight: 700;
            margin: 25px 0 15px 0;
            border-left: 4px solid #00C896;
            padding-left: 15px;
        }
        
        .metric-value {
            font-size: 2.2em;
            font-weight: 800;
            color: #FF6B35;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #A0AEC0;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* ===== SIDEBAR ===== */
        .sidebar-header {
            background: linear-gradient(135deg, #FF6B35 0%, #F7B801 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 25px;
        }
        
        /* ===== FOOTER ===== */
        .dashboard-footer {
            background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-top: 40px;
            border: 2px solid #4A5568;
        }
        
        /* ===== ANIMATIONS ===== */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animated-card {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* ===== RESPONSIVITÉ ===== */
        @media (max-width: 768px) {
            .dashboard-card {
                padding: 15px;
                margin: 10px 0;
            }
            
            .section-title {
                font-size: 2em;
            }
            
            .subsection-title {
                font-size: 1.4em;
            }
        }
        </style>
        """

# ================================================================================================
# GESTIONNAIRE D'IMAGES
# ================================================================================================

class ImageManager:
    """Gestionnaire centralisé pour les images"""
    
    @staticmethod
    def get_player_photo(player_name: str) -> Optional[str]:
        """Récupère le chemin de la photo du joueur"""
        extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG']
        
        for ext in extensions:
            photo_path = f"images_joueurs/**{player_name}{ext}"
            if os.path.exists(photo_path):
                return photo_path
        
        # Recherche plus flexible
        for ext in extensions:
            pattern = f"images_joueurs/**{player_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
            # Essayer avec nom inversé
            if " " in player_name:
                parts = player_name.split(" ")
                if len(parts) >= 2:
                    reversed_name = " ".join(parts[::-1])
                    pattern = f"images_joueurs/**{reversed_name}*{ext}"
                    files = glob.glob(pattern)
                    if files:
                        return files[0]
        
        return None
    
    @staticmethod
    def get_club_logo(competition: str, team_name: str) -> Optional[str]:
        """Récupère le chemin du logo du club"""
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
        
        # Recherche plus flexible
        for ext in extensions:
            pattern = f"{folder}/**{team_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
            # Variations de nom
            clean_team = team_name.replace(" ", "_").replace("'", "").replace("-", "_")
            pattern = f"{folder}/**{clean_team}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
        
        return None

# ================================================================================================
# ANALYSEUR DE PROFIL JOUEUR
# ================================================================================================

class PlayerProfileAnalyzer:
    """Analyseur de profil complet du joueur"""
    
    # Base de données des trophées par joueur (exemple - à enrichir avec vraie base de données)
    PLAYER_TROPHIES = {
        # Joueurs célèbres et leurs trophées
        "Lionel Messi": {
            "major_trophees": 44,
            "ballons_or": 8,
            "coupes_monde": 1,
            "champions_league": 4,
            "championnats": 12,
            "description": "Génie argentin considéré comme l'un des plus grands joueurs de l'histoire. Maître du dribble et finisseur exceptionnel.",
            "style_jeu": "Attaquant polyvalent, faux-9, créateur et finisseur",
            "points_forts": ["Dribbles", "Finition", "Vision de jeu", "Passes décisives"],
            "records": ["Plus de buts en Liga", "Plus de Ballons d'Or", "Plus de passes décisives en Liga"]
        },
        "Cristiano Ronaldo": {
            "major_trophees": 35,
            "ballons_or": 5,
            "coupes_monde": 0,
            "champions_league": 5,
            "championnats": 7,
            "description": "Machine à buts portugaise, athlète complet avec une mentalité de gagnant incomparable.",
            "style_jeu": "Buteur prolifique, jeu aérien exceptionnel, vitesse",
            "points_forts": ["Finition", "Jeu de tête", "Vitesse", "Mentalité"],
            "records": ["Plus de buts en Champions League", "Plus de buts internationaux", "Plus de buts toutes compétitions"]
        },
        "Kylian Mbappé": {
            "major_trophees": 18,
            "ballons_or": 0,
            "coupes_monde": 1,
            "champions_league": 0,
            "championnats": 6,
            "description": "Prodige français, vitesse fulgurante et finition clinique. Futur du football mondial.",
            "style_jeu": "Ailier rapide, contre-attaques, courses en profondeur",
            "points_forts": ["Vitesse", "Finition", "Dribbles", "Contre-attaques"],
            "records": ["Plus jeune buteur en finale de Coupe du Monde", "Plus jeune à 40 buts en C1"]
        },
        "Erling Haaland": {
            "major_trophees": 12,
            "ballons_or": 0,
            "coupes_monde": 0,
            "champions_league": 1,
            "championnats": 3,
            "description": "Machine à buts norvégienne, physique impressionnant et instinct de buteur exceptionnel.",
            "style_jeu": "Avant-centre pur, finisseur dans la surface, puissance physique",
            "points_forts": ["Finition", "Puissance", "Positionnement", "Efficacité"],
            "records": ["Plus rapide à 50 buts en Premier League", "Meilleur ratio buts/match en C1"]
        }
    }
    
    @staticmethod
    def get_player_profile(player_name: str, player_data: pd.Series) -> Dict:
        """Récupère ou génère le profil complet du joueur"""
        # Vérifier si le joueur est dans la base de données
        if player_name in PlayerProfileAnalyzer.PLAYER_TROPHEES:
            profile = PlayerProfileAnalyzer.PLAYER_TROPHEES[player_name].copy()
        else:
            # Générer un profil basé sur les statistiques
            profile = PlayerProfileAnalyzer._generate_profile_from_stats(player_name, player_data)
        
        # Ajouter l'analyse de performance de la saison actuelle
        profile["performance_analysis"] = PlayerProfileAnalyzer._analyze_current_performance(player_data)
        
        return profile
    
    @staticmethod
    def _generate_profile_from_stats(player_name: str, player_data: pd.Series) -> Dict:
        """Génère un profil basé sur les statistiques du joueur"""
        
        # Analyse du style de jeu basé sur les stats
        style_jeu = PlayerProfileAnalyzer._determine_play_style(player_data)
        points_forts = PlayerProfileAnalyzer._determine_strengths(player_data)
        
        # Estimation des trophées basée sur l'âge et les performances
        age = player_data.get('Âge', 25)
        estimated_trophies = max(0, (age - 18) * 2)  # Estimation simple
        
        return {
            "major_trophees": estimated_trophies,
            "ballons_or": 0,  # Données non disponibles
            "coupes_monde": 0,  # Données non disponibles
            "champions_league": 0,  # Données non disponibles
            "championnats": max(0, (age - 20) // 3),  # Estimation
            "description": f"Joueur talentueux évoluant au poste de {player_data.get('Position', 'N/A')}. " +
                          f"Âgé de {age} ans, il représente {player_data.get('Nationalité', 'son pays')} " +
                          f"et joue actuellement pour {player_data.get('Équipe', 'son club')}.",
            "style_jeu": style_jeu,
            "points_forts": points_forts,
            "records": ["Données non disponibles"]
        }
    
    @staticmethod
    def _determine_play_style(player_data: pd.Series) -> str:
        """Détermine le style de jeu basé sur les statistiques"""
        position = player_data.get('Position', '')
        
        # Ratios pour déterminer le style
        buts_90 = player_data.get('Buts par 90 minutes', 0)
        passes_90 = player_data.get('Passes tentées', 0) / (player_data.get('Minutes jouées', 90) / 90)
        tacles_90 = player_data.get('Tacles gagnants', 0) / (player_data.get('Minutes jouées', 90) / 90)
        
        if 'GK' in position or 'Gardien' in position:
            return "Gardien de but, jeu au pied, réflexes"
        elif buts_90 > 0.5:
            return "Attaquant prolifique, finisseur dans la surface"
        elif passes_90 > 50:
            return "Meneur de jeu, créateur, vision de jeu"
        elif tacles_90 > 3:
            return "Défenseur solide, récupérateur, dueliste"
        else:
            return "Joueur polyvalent, contribution dans tous les secteurs"
    
    @staticmethod
    def _determine_strengths(player_data: pd.Series) -> List[str]:
        """Détermine les points forts basés sur les statistiques"""
        strengths = []
        
        # Analyse des différentes métriques
        if player_data.get('Buts par 90 minutes', 0) > 0.3:
            strengths.append("Finition")
        
        if player_data.get('Passes décisives par 90 minutes', 0) > 0.2:
            strengths.append("Création")
        
        if player_data.get('Pourcentage de passes réussies', 0) > 85:
            strengths.append("Précision des passes")
        
        if player_data.get('Dribbles réussis', 0) / (player_data.get('Minutes jouées', 90) / 90) > 2:
            strengths.append("Dribbles")
        
        if player_data.get('Tacles gagnants', 0) / (player_data.get('Minutes jouées', 90) / 90) > 2:
            strengths.append("Défense")
        
        if player_data.get('Duels aériens gagnés', 0) / (player_data.get('Minutes jouées', 90) / 90) > 3:
            strengths.append("Jeu aérien")
        
        return strengths if strengths else ["Polyvalence"]
    
    @staticmethod
    def _analyze_current_performance(player_data: pd.Series) -> Dict:
        """Analyse la performance de la saison actuelle"""
        
        # Calcul de notes sur 10
        def calculate_rating(value, excellent_threshold, good_threshold):
            if value >= excellent_threshold:
                return min(10, 8 + (value - excellent_threshold) / excellent_threshold * 2)
            elif value >= good_threshold:
                return 6 + (value - good_threshold) / (excellent_threshold - good_threshold) * 2
            else:
                return max(1, value / good_threshold * 6)
        
        # Métriques d'évaluation
        buts_90 = player_data.get('Buts par 90 minutes', 0)
        passes_d_90 = player_data.get('Passes décisives par 90 minutes', 0)
        precision_passes = player_data.get('Pourcentage de passes réussies', 0)
        
        # Calcul des notes
        note_attaque = calculate_rating(buts_90, 0.8, 0.3)
        note_creation = calculate_rating(passes_d_90, 0.5, 0.2)
        note_technique = calculate_rating(precision_passes, 90, 80)
        
        # Note globale
        note_globale = (note_attaque + note_creation + note_technique) / 3
        
        # Détermination du niveau
        if note_globale >= 8:
            niveau = "Exceptionnel ⭐⭐⭐"
        elif note_globale >= 7:
            niveau = "Excellent ⭐⭐"
        elif note_globale >= 6:
            niveau = "Très bon ⭐"
        elif note_globale >= 5:
            niveau = "Bon"
        else:
            niveau = "En progression"
        
        return {
            "note_globale": note_globale,
            "niveau": niveau,
            "note_attaque": note_attaque,
            "note_creation": note_creation,
            "note_technique": note_technique,
            "minutes_jouees": int(player_data.get('Minutes jouées', 0)),
            "matchs_joues": int(player_data.get('Matchs joués', 0))
        }

# ================================================================================================
# MISE À JOUR DES COMPOSANTS UI
# ================================================================================================

class UIComponents:
    """Composants d'interface utilisateur réutilisables"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête principal"""
        st.markdown("""
        <div class='player-header-card animated-card'>
            <h1 style='color: white; margin: 0; font-size: 3.5em; font-weight: 900;'>
                ⚽ Dashboard Football Professionnel
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 15px 0 0 0; font-size: 1.3em; font-weight: 500;'>
                Analyse avancée des performances - Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_header():
        """Affiche l'en-tête de la sidebar"""
        st.markdown("""
        <div class='sidebar-header'>
            <h2 style='color: white; margin: 0; font-weight: 800;'>🎯 Configuration</h2>
            <p style='color: rgba(255,255,255,0.8); margin: 10px 0 0 0; font-size: 0.9em;'>
                Sélectionnez votre joueur
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte complète du joueur"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            UIComponents._render_player_photo(player_data['Joueur'])
        
        with col2:
            UIComponents._render_player_info(player_data)
        
        with col3:
            UIComponents._render_club_logo(player_data['Équipe'], competition)
    
    @staticmethod
    def _render_player_photo(player_name: str):
        """Affiche la photo du joueur"""
        photo_path = ImageManager.get_player_photo(player_name)
        
        if photo_path:
            try:
                image = Image.open(photo_path)
                st.markdown(f"""
                <div class='image-container animated-card'>
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 15px;">
                </div>
                <p style='text-align: center; color: #FF6B35; font-weight: 600; margin-top: 10px;'>
                    📸 {player_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_photo_placeholder(player_name)
            st.markdown("""
            <div class='dashboard-card animated-card' style='text-align: center; padding: 30px; margin-top: 20px;'>
                <h4 style='color: #F7B801; margin-bottom: 15px;'>⚠️ Sélection Incomplète</h4>
                <p style='color: #E2E8F0; margin: 0; font-size: 1.1em;'>
                    Veuillez sélectionner deux joueurs pour activer la comparaison
                </p>
                <div style='display: flex; justify-content: center; gap: 20px; margin-top: 20px;'>
                    <div style='text-align: center;'>
                        <div style='font-size: 2em; margin-bottom: 5px;'>👤</div>
                        <p style='color: #A0AEC0; font-size: 0.9em;'>Joueur 1</p>
                    </div>
                    <div style='text-align: center; color: #FF6B35;'>
                        <div style='font-size: 2em; margin-bottom: 5px;'>⚔️</div>
                        <p style='color: #A0AEC0; font-size: 0.9em;'>VS</p>
                    </div>
                    <div style='text-align: center;'>
                        <div style='font-size: 2em; margin-bottom: 5px;'>👤</div>
                        <p style='color: #A0AEC0; font-size: 0.9em;'>Joueur 2</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            UIComponents._render_photo_placeholder(player_name)
    
    @staticmethod
    def _render_club_logo(team_name: str, competition: str):
        """Affiche le logo du club"""
        logo_path = ImageManager.get_club_logo(competition, team_name)
        
        if logo_path:
            try:
                image = Image.open(logo_path)
                st.markdown(f"""
                <div class='club-logo-container animated-card'>
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain;">
                </div>
                <p style='text-align: center; color: #FF6B35; font-weight: 600; margin-top: 10px;'>
                    🏟️ {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_logo_placeholder(team_name)
        else:
            UIComponents._render_logo_placeholder(team_name)
    
    @staticmethod
    def _render_player_info(player_data: pd.Series):
        """Affiche les informations de base du joueur (version simplifiée)"""
        st.markdown(f"""
        <div class='dashboard-card animated-card' style='text-align: center;'>
            <h2 class='section-title' style='margin-bottom: 30px;'>
                {player_data['Joueur']}
            </h2>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;'>
                <div class='metric-card'>
                    <div class='metric-value'>{player_data['Âge']}</div>
                    <div class='metric-label'>Ans</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{player_data['Position']}</div>
                    <div class='metric-label'>Position</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{int(player_data['Minutes jouées'])}</div>
                    <div class='metric-label'>Minutes</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{player_data['Nationalité']}</div>
                    <div class='metric-label'>Nationalité</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_achievements_sidebar():
        """Affiche les achievements dans la sidebar"""
        st.markdown("---")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FF6B35 0%, #F7B801 100%); 
                    padding: 15px; border-radius: 10px; margin: 15px 0;'>
            <h4 style='color: white; margin: 0 0 10px 0; font-weight: 800;'>🏆 Achievements</h4>
            <div style='display: flex; justify-content: space-around; align-items: center;'>
                <div style='text-align: center;'>
                    <div style='font-size: 1.5em;'>⭐</div>
                    <div style='color: white; font-size: 0.8em;'>Excellence</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 1.5em;'>🎯</div>
                    <div style='color: white; font-size: 0.8em;'>Précision</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 1.5em;'>🔥</div>
                    <div style='color: white; font-size: 0.8em;'>Performance</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_comparison_preview(player_data: pd.Series):
        """Affiche un aperçu de comparaison rapide"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='margin: 20px 0;'>
            <h3 class='subsection-title'>⚡ Comparaison Rapide</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Métriques clés par 90 minutes
        col1, col2, col3 = st.columns(3)
        
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        quick_metrics = [
            ("🎯", "Buts/90", f"{player_data.get('Buts par 90 minutes', 0):.2f}"),
            ("🅰️", "Passes D./90", f"{player_data.get('Passes décisives par 90 minutes', 0):.2f}"),
            ("⚽", "Actions/90", f"{(player_data.get('Buts', 0) + player_data.get('Passes décisives', 0)) / minutes_90:.2f}")
        ]
        
        cols = [col1, col2, col3]
        colors = ["#FF6B35", "#00C896", "#1A759F"]
        
        for i, (icon, label, value) in enumerate(quick_metrics):
            with cols[i]:
                st.markdown(f"""
                <div class='metric-card animated-card' style='border-color: {colors[i]}; 
                     background: linear-gradient(135deg, {colors[i]}20, {colors[i]}05);'>
                    <div style='font-size: 2em; color: {colors[i]}; margin-bottom: 10px;'>{icon}</div>
                    <div class='metric-value' style='color: {colors[i]};'>{value}</div>
                    <div class='metric-label'>{label}</div>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_stats_summary(player_data: pd.Series):
        """Affiche un résumé statistique avancé"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='margin: 20px 0;'>
            <h3 class='subsection-title'>📊 Résumé Statistique</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculs avancés
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        # Statistiques calculées
        impact_offensif = (player_data.get('Buts', 0) + player_data.get('Passes décisives', 0)) / minutes_90
        efficacite_passes = player_data.get('Pourcentage de passes réussies', 0)
        contribution_defensive = (player_data.get('Tacles gagnants', 0) + player_data.get('Interceptions', 0)) / minutes_90
        
        # Détermination du profil de joueur
        if impact_offensif > 0.8:
            profil = "⚡ Joueur Offensif"
            profil_color = "#FF6B35"
        elif contribution_defensive > 3:
            profil = "🛡️ Joueur Défensif"
            profil_color = "#1A759F"
        elif efficacite_passes > 85:
            profil = "🎨 Créateur de Jeu"
            profil_color = "#00C896"
        else:
            profil = "⚽ Joueur Polyvalent"
            profil_color = "#F7B801"
        
        # Affichage du profil
        st.markdown(f"""
        <div style='text-align: center; margin: 20px 0;'>
            <div style='background: linear-gradient(135deg, {profil_color} 0%, {profil_color}80 100%); 
                        color: white; padding: 20px; border-radius: 20px; 
                        box-shadow: 0 8px 25px {profil_color}40;'>
                <h4 style='margin: 0; font-size: 1.5em; font-weight: 800;'>{profil}</h4>
                <p style='margin: 10px 0 0 0; opacity: 0.9;'>
                    Profil déterminé par l'analyse des performances
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistiques détaillées
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='dashboard-card'>
                <h4 style='color: #FF6B35; margin-bottom: 15px;'>🎯 Impact Offensif</h4>
                <div style='margin: 15px 0;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                        <span style='color: #E2E8F0;'>Actions décisives/90:</span>
                        <span style='color: #FF6B35; font-weight: bold;'>{impact_offensif:.2f}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                        <span style='color: #E2E8F0;'>Buts totaux:</span>
                        <span style='color: #FF6B35; font-weight: bold;'>{player_data.get('Buts', 0)}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                        <span style='color: #E2E8F0;'>Passes décisives:</span>
                        <span style='color: #FF6B35; font-weight: bold;'>{player_data.get('Passes décisives', 0)}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='dashboard-card'>
                <h4 style='color: #00C896; margin-bottom: 15px;'>🎨 Qualité Technique</h4>
                <div style='margin: 15px 0;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                        <span style='color: #E2E8F0;'>Précision passes:</span>
                        <span style='color: #00C896; font-weight: bold;'>{efficacite_passes:.1f}%</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                        <span style='color: #E2E8F0;'>Touches de balle:</span>
                        <span style='color: #00C896; font-weight: bold;'>{player_data.get('Touches de balle', 0)}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 10px;'>
                        <span style='color: #E2E8F0;'>Dribbles réussis:</span>
                        <span style='color: #00C896; font-weight: bold;'>{player_data.get('Dribbles réussis', 0)}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def render_loading_animation():
        """Affiche une animation de chargement stylée"""
        st.markdown("""
        <div style='text-align: center; padding: 40px;'>
            <div style='display: inline-block; width: 60px; height: 60px; border: 6px solid #4A5568; 
                        border-radius: 50%; border-top-color: #FF6B35; animation: spin 1s ease-in-out infinite;'>
            </div>
            <p style='color: #E2E8F0; margin-top: 20px; font-size: 1.1em;'>
                Chargement des données du joueur...
            </p>
        </div>
        
        <style>
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;'>
                <div class='metric-card'>
                    <div class='metric-value'>{player_data['Âge']}</div>
                    <div class='metric-label'>Ans</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{player_data['Position']}</div>
                    <div class='metric-label'>Position</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{int(player_data['Minutes jouées'])}</div>
                    <div class='metric-label'>Minutes</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{player_data['Nationalité']}</div>
                    <div class='metric-label'>Nationalité</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_photo_placeholder(player_name: str):
        """Affiche un placeholder pour la photo"""
        st.markdown(f"""
        <div class='image-container animated-card'>
            <div style='text-align: center; color: #A0AEC0;'>
                <div style='font-size: 4em; margin-bottom: 10px;'>👤</div>
                <p>Photo non disponible</p>
                <p style='font-size: 0.8em;'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder(team_name: str):
        """Affiche un placeholder pour le logo"""
        st.markdown(f"""
        <div class='club-logo-container animated-card'>
            <div style='text-align: center; color: #A0AEC0;'>
                <div style='font-size: 3em; margin-bottom: 10px;'>🏟️</div>
                <p style='font-size: 0.9em;'>Logo non disponible</p>
                <p style='font-size: 0.8em;'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _image_to_base64(image: Image.Image) -> str:
        """Convertit une image PIL en base64"""
        import io
        import base64
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    @staticmethod
    def render_footer():
        """Affiche le footer"""
        st.markdown("""
        <div class='dashboard-footer animated-card'>
            <h3 style='color: #FF6B35; margin: 0 0 15px 0; font-weight: 800;'>
                📊 Dashboard Football Professionnel
            </h3>
            <p style='color: #E2E8F0; margin: 0; font-size: 1.1em; font-weight: 500;'>
                Analyse avancée des performances footballistiques
            </p>
            <p style='color: #A0AEC0; margin: 10px 0 0 0; font-size: 0.9em;'>
                Données: FBRef | Design: Dashboard Pro | Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE MÉTRIQUES
# ================================================================================================

class MetricsCalculator:
    """Calculateur de métriques et percentiles"""
    
    @staticmethod
    def calculate_percentiles(player_name: str, df: pd.DataFrame) -> List[int]:
        """Calcule les percentiles pour le pizza chart"""
        player = df[df["Joueur"] == player_name].iloc[0]
        percentiles = []

        for label, col in AppConfig.RAW_STATS.items():
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
                    matches = player.get("Matchs en 90 min", player.get("Matchs joués", 1))
                    if matches == 0:
                        percentile = 0
                    else:
                        val = player[col] / matches
                        dist = df[col] / df.get("Matchs joués", 1)
                        if pd.isna(val) or dist.dropna().empty:
                            percentile = 0
                        else:
                            percentile = round((dist < val).mean() * 100)
            except Exception:
                percentile = 0
            percentiles.append(percentile)

        return percentiles
    
    @staticmethod
    def calculate_offensive_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques offensives"""
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        return {
            'Buts/90': player_data['Buts par 90 minutes'],
            'Passes D./90': player_data['Passes décisives par 90 minutes'],
            'xG/90': player_data['Buts attendus par 90 minutes'],
            'xA/90': player_data['Passes décisives attendues par 90 minutes'],
            'Tirs/90': player_data['Tirs par 90 minutes'],
            'Passes clés/90': player_data['Passes clés'] / minutes_90,
            'Dribbles réussis/90': player_data['Dribbles réussis'] / minutes_90,
            'Actions → Tir/90': player_data['Actions menant à un tir par 90 minutes']
        }
    
    @staticmethod
    def calculate_defensive_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques défensives"""
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        return {
            'Tacles/90': player_data['Tacles gagnants'] / minutes_90,
            'Interceptions/90': player_data['Interceptions'] / minutes_90,
            'Ballons récupérés/90': player_data['Ballons récupérés'] / minutes_90,
            'Duels aériens/90': player_data['Duels aériens gagnés'] / minutes_90,
            'Dégagements/90': player_data['Dégagements'] / minutes_90,
            '% Duels gagnés': player_data.get('Pourcentage de duels gagnés', 0),
            '% Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
            'Tirs bloqués/90': player_data.get('Tirs bloqués', 0) / minutes_90
        }
    
    @staticmethod
    def calculate_technical_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques techniques"""
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        return {
            'Passes tentées/90': player_data['Passes tentées'] / minutes_90,
            'Passes prog./90': player_data.get('Passes progressives', 0) / minutes_90,
            'Dribbles/90': player_data['Dribbles tentés'] / minutes_90,
            'Touches/90': player_data['Touches de balle'] / minutes_90,
            'Passes clés/90': player_data['Passes clés'] / minutes_90,
            '% Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
            '% Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0)
        }

# ================================================================================================
# GESTIONNAIRE DE GRAPHIQUES
# ================================================================================================

class ChartManager:
    """Gestionnaire centralisé pour les graphiques"""
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], title: str, color_palette: List[str]) -> go.Figure:
        """Crée un graphique en barres stylé"""
        fig = go.Figure(data=[go.Bar(
            x=list(data.keys()),
            y=list(data.values()),
            marker=dict(
                color=color_palette,
                line=dict(color='white', width=2)
            ),
            text=[f"{v:.1f}" for v in data.values()],
            textposition='outside',
            textfont=dict(color='white', size=14, family='Arial Black')
        )])
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, color='white', family='Arial Black'),
                x=0.5
            ),
            xaxis=dict(
                tickfont=dict(color='white', size=12),
                tickangle=45,
                gridcolor='rgba(255,255,255,0.1)'
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=12),
                gridcolor='rgba(255,255,255,0.2)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=450
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(data: Dict[str, float], title: str) -> go.Figure:
        """Crée un graphique en jauges"""
        fig = make_subplots(
            rows=1, cols=len(data),
            specs=[[{"type": "indicator"}] * len(data)],
            subplot_titles=list(data.keys())
        )
        
        colors = [AppConfig.COLORS['primary'], AppConfig.COLORS['success'], AppConfig.COLORS['warning']]
        
        for i, (metric, value) in enumerate(data.items()):
            color = colors[i % len(colors)]
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=value,
                    gauge=dict(
                        axis=dict(range=[0, 100]),
                        bar=dict(color=color, thickness=0.8),
                        bgcolor="rgba(0,0,0,0.3)",
                        borderwidth=3,
                        bordercolor="white",
                        steps=[
                            {'range': [0, 33], 'color': 'rgba(255,255,255,0.1)'},
                            {'range': [33, 66], 'color': 'rgba(255,255,255,0.2)'},
                            {'range': [66, 100], 'color': 'rgba(255,255,255,0.3)'}
                        ],
                        threshold={
                            'line': {'color': "white", 'width': 4},
                            'thickness': 0.8,
                            'value': 80
                        }
                    ),
                    number={
                        'suffix': '%', 
                        'font': {'color': 'white', 'size': 16, 'family': 'Arial Black'}
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            height=350,
            title_text=title,
            title_font_color='white',
            title_font_size=18,
            title_font_family='Arial Black',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Arial')
        )
        
        return fig
    
    @staticmethod
    def create_comparison_chart(player_data: Dict[str, float], avg_data: Dict[str, float], 
                              player_name: str, title: str) -> go.Figure:
        """Crée un graphique de comparaison"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=player_name,
            x=list(player_data.keys()),
            y=list(player_data.values()),
            marker_color=AppConfig.COLORS['primary'],
            text=[f"{v:.2f}" for v in player_data.values()],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Moyenne compétition',
            x=list(avg_data.keys()),
            y=list(avg_data.values()),
            marker_color=AppConfig.COLORS['secondary'],
            text=[f"{v:.2f}" for v in avg_data.values()],
            textposition='outside'
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color='white', size=18, family='Arial Black'),
                x=0.5
            ),
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(tickfont=dict(color='white', size=12)),
            yaxis=dict(tickfont=dict(color='white', size=12), gridcolor='rgba(255,255,255,0.2)'),
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
    
    @staticmethod
    def create_radar_chart(metrics: Dict[str, float], percentiles: List[float], 
                          avg_percentiles: List[float], player_name: str, 
                          competition: str, color: str) -> go.Figure:
        """Crée un radar chart professionnel"""
        fig = go.Figure()
        
        # Performance du joueur
        fig.add_trace(go.Scatterpolar(
            r=percentiles,
            theta=list(metrics.keys()),
            fill='toself',
            fillcolor=f'rgba({ChartManager._hex_to_rgb(color)}, 0.3)',
            line=dict(color=color, width=4),
            marker=dict(color=color, size=10, symbol='circle'),
            name=player_name,
            hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
            customdata=list(metrics.values())
        ))
        
        # Moyenne de la compétition
        fig.add_trace(go.Scatterpolar(
            r=avg_percentiles,
            theta=list(metrics.keys()),
            mode='lines',
            line=dict(color='rgba(255,255,255,0.8)', width=3, dash='dash'),
            name=f'Moyenne {competition}',
            showlegend=True,
            hovertemplate='<b>%{theta}</b><br>Moyenne: %{r:.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(255,255,255,0.3)',
                    tickcolor='white',
                    tickfont=dict(color='white', size=11, family='Arial'),
                    showticklabels=True,
                    tickmode='linear',
                    tick0=0,
                    dtick=20
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.3)',
                    tickcolor='white',
                    tickfont=dict(color='white', size=12, family='Arial Black'),
                    linecolor='rgba(255,255,255,0.5)'
                ),
                bgcolor='rgba(30, 38, 64, 0.9)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title=dict(
                text=f"Radar Professionnel - {player_name}",
                font=dict(size=20, color='white', family='Arial Black'),
                x=0.5,
                y=0.95
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color='white', size=12)
            ),
            height=500
        )
        
        return fig
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> str:
        """Convertit une couleur hex en RGB"""
        hex_color = hex_color.lstrip('#')
        return ','.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))

# ================================================================================================
# ANALYSEUR DE PERFORMANCE
# ================================================================================================

class PerformanceAnalyzer:
    """Analyseur de performance pour différents aspects du jeu"""
    
    @staticmethod
    def analyze_offensive_performance(player_data: pd.Series, df_comparison: pd.DataFrame) -> Dict:
        """Analyse complète de la performance offensive"""
        metrics = MetricsCalculator.calculate_offensive_metrics(player_data)
        
        # Calcul des moyennes de la compétition
        avg_metrics = {}
        minutes_90_comp = df_comparison['Minutes jouées'] / 90
        
        avg_metrics['Buts/90'] = df_comparison['Buts par 90 minutes'].mean()
        avg_metrics['Passes D./90'] = df_comparison['Passes décisives par 90 minutes'].mean()
        avg_metrics['xG/90'] = df_comparison['Buts attendus par 90 minutes'].mean()
        avg_metrics['xA/90'] = df_comparison['Passes décisives attendues par 90 minutes'].mean()
        avg_metrics['Tirs/90'] = df_comparison['Tirs par 90 minutes'].mean()
        avg_metrics['Passes clés/90'] = (df_comparison['Passes clés'] / minutes_90_comp).mean()
        avg_metrics['Dribbles réussis/90'] = (df_comparison['Dribbles réussis'] / minutes_90_comp).mean()
        avg_metrics['Actions → Tir/90'] = df_comparison['Actions menant à un tir par 90 minutes'].mean()
        
        # Calcul des percentiles
        percentiles = []
        avg_percentiles = []
        
        for metric, value in metrics.items():
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
            else:
                base_column = metric.replace('/90', '').replace('Passes D.', 'Passes décisives')
                distribution = df_comparison[base_column] / minutes_90_comp
            
            percentile = (distribution < value).mean() * 100
            avg_percentile = (distribution < avg_metrics[metric]).mean() * 100
            
            percentiles.append(min(percentile, 100))
            avg_percentiles.append(avg_percentile)
        
        return {
            'metrics': metrics,
            'avg_metrics': avg_metrics,
            'percentiles': percentiles,
            'avg_percentiles': avg_percentiles
        }
    
    @staticmethod
    def analyze_defensive_performance(player_data: pd.Series, df_comparison: pd.DataFrame) -> Dict:
        """Analyse complète de la performance défensive"""
        metrics = MetricsCalculator.calculate_defensive_metrics(player_data)
        
        # Calcul des moyennes de la compétition
        avg_metrics = {}
        minutes_90_comp = df_comparison['Minutes jouées'] / 90
        
        avg_metrics['Tacles/90'] = (df_comparison['Tacles gagnants'] / minutes_90_comp).mean()
        avg_metrics['Interceptions/90'] = (df_comparison['Interceptions'] / minutes_90_comp).mean()
        avg_metrics['Ballons récupérés/90'] = (df_comparison['Ballons récupérés'] / minutes_90_comp).mean()
        avg_metrics['Duels aériens/90'] = (df_comparison['Duels aériens gagnés'] / minutes_90_comp).mean()
        avg_metrics['Dégagements/90'] = (df_comparison['Dégagements'] / minutes_90_comp).mean()
        avg_metrics['% Duels gagnés'] = df_comparison.get('Pourcentage de duels gagnés', pd.Series([0]*len(df_comparison))).mean()
        avg_metrics['% Duels aériens'] = df_comparison['Pourcentage de duels aériens gagnés'].mean()
        avg_metrics['Tirs bloqués/90'] = (df_comparison.get('Tirs bloqués', pd.Series([0]*len(df_comparison))) / minutes_90_comp).mean()
        
        # Calcul des percentiles
        percentiles = []
        avg_percentiles = []
        
        for metric, value in metrics.items():
            if metric == 'Tacles/90':
                distribution = df_comparison['Tacles gagnants'] / minutes_90_comp
            elif metric == 'Interceptions/90':
                distribution = df_comparison['Interceptions'] / minutes_90_comp
            elif metric == 'Ballons récupérés/90':
                distribution = df_comparison['Ballons récupérés'] / minutes_90_comp
            elif metric == 'Duels aériens/90':
                distribution = df_comparison['Duels aériens gagnés'] / minutes_90_comp
            elif metric == 'Dégagements/90':
                distribution = df_comparison['Dégagements'] / minutes_90_comp
            elif metric == '% Duels gagnés':
                distribution = df_comparison.get('Pourcentage de duels gagnés', pd.Series([0]*len(df_comparison)))
            elif metric == '% Duels aériens':
                distribution = df_comparison['Pourcentage de duels aériens gagnés']
            elif metric == 'Tirs bloqués/90':
                distribution = df_comparison.get('Tirs bloqués', pd.Series([0]*len(df_comparison))) / minutes_90_comp
            
            distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
            value = value if not np.isnan(value) and not np.isinf(value) else 0
            
            if len(distribution) > 0:
                percentile = (distribution < value).mean() * 100
                avg_percentile = (distribution < avg_metrics[metric]).mean() * 100
            else:
                percentile = 50
                avg_percentile = 50
            
            percentiles.append(min(percentile, 100))
            avg_percentiles.append(avg_percentile)
        
        return {
            'metrics': metrics,
            'avg_metrics': avg_metrics,
            'percentiles': percentiles,
            'avg_percentiles': avg_percentiles
        }
    
    @staticmethod
    def analyze_technical_performance(player_data: pd.Series, df_comparison: pd.DataFrame) -> Dict:
        """Analyse complète de la performance technique"""
        metrics = MetricsCalculator.calculate_technical_metrics(player_data)
        
        # Calcul des moyennes de la compétition
        avg_metrics = {}
        minutes_90_comp = df_comparison['Minutes jouées'] / 90
        
        avg_metrics['Passes tentées/90'] = (df_comparison['Passes tentées'] / minutes_90_comp).mean()
        avg_metrics['Passes prog./90'] = (df_comparison.get('Passes progressives', pd.Series([0]*len(df_comparison))) / minutes_90_comp).mean()
        avg_metrics['Dribbles/90'] = (df_comparison['Dribbles tentés'] / minutes_90_comp).mean()
        avg_metrics['Touches/90'] = (df_comparison['Touches de balle'] / minutes_90_comp).mean()
        avg_metrics['Passes clés/90'] = (df_comparison['Passes clés'] / minutes_90_comp).mean()
        avg_metrics['% Passes réussies'] = df_comparison.get('Pourcentage de passes réussies', pd.Series([0]*len(df_comparison))).mean()
        avg_metrics['% Dribbles réussis'] = df_comparison.get('Pourcentage de dribbles réussis', pd.Series([0]*len(df_comparison))).mean()
        
        # Calcul des percentiles
        percentiles = []
        avg_percentiles = []
        
        for metric, value in metrics.items():
            if metric == 'Passes tentées/90':
                distribution = df_comparison['Passes tentées'] / minutes_90_comp
            elif metric == 'Passes prog./90':
                distribution = df_comparison.get('Passes progressives', pd.Series([0]*len(df_comparison))) / minutes_90_comp
            elif metric == 'Dribbles/90':
                distribution = df_comparison['Dribbles tentés'] / minutes_90_comp
            elif metric == 'Touches/90':
                distribution = df_comparison['Touches de balle'] / minutes_90_comp
            elif metric == 'Passes clés/90':
                distribution = df_comparison['Passes clés'] / minutes_90_comp
            elif metric == '% Passes réussies':
                distribution = df_comparison.get('Pourcentage de passes réussies', pd.Series([0]*len(df_comparison)))
            elif metric == '% Dribbles réussis':
                distribution = df_comparison.get('Pourcentage de dribbles réussis', pd.Series([0]*len(df_comparison)))
            
            distribution = distribution.replace([np.inf, -np.inf], np.nan).dropna()
            value = value if not np.isnan(value) and not np.isinf(value) else 0
            
            if len(distribution) > 0:
                percentile = (distribution < value).mean() * 100
                avg_percentile = (distribution < avg_metrics[metric]).mean() * 100
            else:
                percentile = 50
                avg_percentile = 50
            
            percentiles.append(min(percentile, 100))
            avg_percentiles.append(avg_percentile)
        
        return {
            'metrics': metrics,
            'avg_metrics': avg_metrics,
            'percentiles': percentiles,
            'avg_percentiles': avg_percentiles
        }

# ================================================================================================
# GESTIONNAIRE DE TABS
# ================================================================================================

class TabManager:
    """Gestionnaire pour les différents onglets"""
    
    @staticmethod
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance offensive"""
        st.markdown("<h2 class='section-title'>🎯 Performance Offensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_offensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique en barres des actions offensives
            basic_actions = {
                'Buts': player_data['Buts'],
                'Passes décisives': player_data['Passes décisives'],
                'Passes clés': player_data['Passes clés'],
                'Tirs': player_data.get('Tirs', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "Actions Offensives Totales",
                AppConfig.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Radar offensif
            st.markdown("<h3 class='subsection-title'>🎯 Radar Offensif</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
                AppConfig.COLORS['primary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Jauges de pourcentages
            efficiency_data = {
                'Conversion': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                'Efficacité passes': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(efficiency_data, "Efficacité Offensive")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Comparaison par 90 minutes
            comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
            avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
            
            fig_comp = ChartManager.create_comparison_chart(
                comparison_metrics,
                avg_comparison,
                selected_player,
                "Performance par 90min vs Moyenne"
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        # Métriques détaillées
        TabManager._render_detailed_metrics(analysis['metrics'], "📊 Métriques Offensives Détaillées")
    
    @staticmethod
    def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance défensive"""
        st.markdown("<h2 class='section-title'>🛡️ Performance Défensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_defensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Actions défensives
            basic_actions = {
                'Tacles': player_data['Tacles gagnants'],
                'Interceptions': player_data['Interceptions'],
                'Ballons récupérés': player_data['Ballons récupérés'],
                'Duels aériens': player_data['Duels aériens gagnés']
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "Actions Défensives Totales",
                AppConfig.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Radar défensif
            st.markdown("<h3 class='subsection-title'>🛡️ Radar Défensif</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
                AppConfig.COLORS['accent']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Pourcentages de réussite
            success_data = {
                'Duels défensifs': player_data.get('Pourcentage de duels gagnés', 0),
                'Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                'Passes': player_data['Pourcentage de passes réussies']
            }
            
            fig_gauge = ChartManager.create_gauge_chart(success_data, "Pourcentages de Réussite")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Comparaison défensive
            comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
            avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
            
            fig_comp = ChartManager.create_comparison_chart(
                comparison_metrics,
                avg_comparison,
                selected_player,
                "Défense par 90min vs Moyenne"
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        TabManager._render_detailed_metrics(analysis['metrics'], "📊 Métriques Défensives Détaillées")
    
    @staticmethod
    def render_technical_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance technique"""
        st.markdown("<h2 class='section-title'>🎨 Performance Technique</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_technical_performance(player_data, df_comparison)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Actions techniques
            basic_actions = {
                'Passes tentées': player_data['Passes tentées'],
                'Dribbles tentés': player_data['Dribbles tentés'],
                'Touches': player_data['Touches de balle'],
                'Passes clés': player_data['Passes clés']
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "Actions Techniques Totales",
                AppConfig.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Radar technique
            st.markdown("<h3 class='subsection-title'>🎨 Radar Technique</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
                AppConfig.COLORS['success']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Pourcentages techniques
            technical_success = {
                'Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
            }
            
            fig_gauge = ChartManager.create_gauge_chart(technical_success, "Précision Technique")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Comparaison technique
            comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
            avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
            
            fig_comp = ChartManager.create_comparison_chart(
                comparison_metrics,
                avg_comparison,
                selected_player,
                "Technique par 90min vs Moyenne"
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        TabManager._render_detailed_metrics(analysis['metrics'], "📊 Métriques Techniques Détaillées")
    
    @staticmethod
    def render_comparison_tab(df: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet comparaison avec pizza charts"""
        st.markdown("<h2 class='section-title'>🔄 Comparaison Pizza Chart</h2>", unsafe_allow_html=True)
        
        # Mode de visualisation avec design amélioré
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 20px; margin-bottom: 30px;'>
            <h3 style='color: #FF6B35; margin-bottom: 15px;'>📊 Mode de Visualisation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        mode = st.radio(
            "Choisissez votre type d'analyse :",
            ["Radar individuel", "Radar comparatif"],
            horizontal=True,
            help="Le radar individuel montre les percentiles d'un joueur. Le radar comparatif permet de comparer deux joueurs directement."
        )
        
        competitions = sorted(df['Compétition'].dropna().unique())
        
        if mode == "Radar individuel":
            TabManager._render_individual_pizza_chart(df, selected_player, competitions)
        else:
            TabManager._render_comparative_pizza_chart(df, competitions)
    
    @staticmethod
    def _render_individual_pizza_chart(df: pd.DataFrame, selected_player: str, competitions: List[str]):
        """Rendu du pizza chart individuel avec les couleurs de l'interface"""
        st.markdown(f"<h3 class='subsection-title'>🎯 Pizza Chart Individuel : {selected_player}</h3>", unsafe_allow_html=True)
        
        # Section de configuration
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            st.markdown("""
            <div class='dashboard-card' style='padding: 20px;'>
                <h4 style='color: #00C896; margin-bottom: 15px;'>⚙️ Configuration</h4>
            </div>
            """, unsafe_allow_html=True)
            
            competition = st.selectbox(
                "🏆 Compétition de référence :",
                competitions,
                help="Sélectionnez la compétition pour calculer les percentiles"
            )
        
        with col_config2:
            # Informations sur le joueur sélectionné
            player_info = df[df['Joueur'] == selected_player].iloc[0]
            st.markdown(f"""
            <div class='dashboard-card' style='padding: 20px;'>
                <h4 style='color: #00C896; margin-bottom: 15px;'>👤 Joueur Analysé</h4>
                <p style='color: #E2E8F0; margin: 5px 0;'><strong>Nom :</strong> {selected_player}</p>
                <p style='color: #E2E8F0; margin: 5px 0;'><strong>Équipe :</strong> {player_info['Équipe']}</p>
                <p style='color: #E2E8F0; margin: 5px 0;'><strong>Position :</strong> {player_info['Position']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        try:
            df_comp = df[df['Compétition'] == competition]
            values = MetricsCalculator.calculate_percentiles(selected_player, df_comp)
            
            # Charger les polices
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            # Créer le pizza chart avec les couleurs de l'interface
            baker = PyPizza(
                params=list(AppConfig.RAW_STATS.keys()),
                background_color="#0E1117",  # Fond sombre de l'interface
                straight_line_color="#FFFFFF",
                straight_line_lw=2,
                last_circle_color="#FF6B35",  # Couleur primaire
                last_circle_lw=3,
                other_circle_lw=1,
                other_circle_color="#4A5568",  # Couleur secondaire
                inner_circle_size=12
            )
            
            # Couleurs des tranches avec dégradé inspiré de l'interface
            slice_colors = [AppConfig.COLORS['primary']] * len(values)
            
            fig, ax = baker.make_pizza(
                values,
                figsize=(16, 18),
                param_location=110,
                color_blank_space="same",
                slice_colors=slice_colors,
                value_colors=["#FFFFFF"] * len(values),
                value_bck_colors=[AppConfig.COLORS['primary']] * len(values),
                kwargs_slices=dict(
                    edgecolor="#FFFFFF", 
                    zorder=2, 
                    linewidth=2,
                    alpha=0.8
                ),
                kwargs_params=dict(
                    color="#FFFFFF", 
                    fontsize=13, 
                    fontproperties=font_bold.prop,
                    weight='bold'
                ),
                kwargs_values=dict(
                    color="#FFFFFF", 
                    fontsize=12, 
                    fontproperties=font_normal.prop,
                    weight='bold',
                    bbox=dict(
                        edgecolor="#FFFFFF", 
                        facecolor=AppConfig.COLORS['primary'], 
                        boxstyle="round,pad=0.3", 
                        lw=2,
                        alpha=0.9
                    )
                )
            )
            
            # Personnalisation du fond avec dégradé visuel
            fig.patch.set_facecolor('#0E1117')
            ax.set_facecolor('#0E1117')
            
            # Titre principal avec style interface
            fig.text(0.515, 0.975, selected_player, 
                    size=36, ha="center", fontproperties=font_bold.prop, 
                    color="#FFFFFF", weight='bold')
            
            # Sous-titre avec couleurs de l'interface
            fig.text(0.515, 0.945, f"Pizza Chart Individuel | Percentiles vs {competition}", 
                    size=18, ha="center", fontproperties=font_bold.prop, 
                    color="#FF6B35")
            
            fig.text(0.515, 0.925, "Saison 2024-25", 
                    size=16, ha="center", fontproperties=font_normal.prop, 
                    color="#00C896")
            
            # Légende explicative avec style interface
            fig.text(0.515, 0.05, 
                    "Les valeurs représentent les percentiles par rapport aux autres joueurs de la compétition", 
                    size=12, ha="center", fontproperties=font_italic.prop, 
                    color="#A0AEC0", style='italic')
            
            # Footer avec branding cohérent
            fig.text(0.99, 0.01, "Dashboard Football Pro | Données: FBRef", 
                    size=10, ha="right", fontproperties=font_italic.prop, 
                    color="#718096")
            
            # Ajout d'informations contextuelles
            nb_joueurs = len(df_comp)
            fig.text(0.01, 0.01, f"Comparé à {nb_joueurs} joueurs en {competition}", 
                    size=10, ha="left", fontproperties=font_italic.prop, 
                    color="#718096")
            
            st.pyplot(fig, use_container_width=True)
            
            # Légende explicative sous le graphique
            st.markdown("""
            <div class='dashboard-card animated-card' style='text-align: center; padding: 20px; margin-top: 20px;'>
                <h4 style='color: #00C896; margin-bottom: 15px;'>📖 Guide de Lecture</h4>
                <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px;'>
                    <div>
                        <div style='background: #FF6B35; width: 30px; height: 30px; border-radius: 50%; margin: 0 auto 10px; border: 2px solid white;'></div>
                        <p style='color: #E2E8F0; margin: 0; font-size: 0.9em;'><strong>Percentile élevé</strong><br>Performance supérieure</p>
                    </div>
                    <div>
                        <div style='background: linear-gradient(45deg, #FF6B35, #F7B801); width: 30px; height: 30px; border-radius: 50%; margin: 0 auto 10px; border: 2px solid white;'></div>
                        <p style='color: #E2E8F0; margin: 0; font-size: 0.9em;'><strong>Couleurs interface</strong><br>Design cohérent</p>
                    </div>
                    <div>
                        <div style='background: #4A5568; width: 30px; height: 30px; border-radius: 50%; margin: 0 auto 10px; border: 2px solid white;'></div>
                        <p style='color: #E2E8F0; margin: 0; font-size: 0.9em;'><strong>Zones vides</strong><br>Percentiles plus faibles</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la création du pizza chart individuel : {str(e)}")
            st.info("💡 Vérifiez que le joueur existe dans la compétition sélectionnée.")
    
    @staticmethod
    def _render_comparative_pizza_chart(df: pd.DataFrame, competitions: List[str]):
        """Rendu du pizza chart comparatif avec les couleurs de l'interface"""
        st.markdown("<h3 class='subsection-title'>⚔️ Pizza Chart Comparatif</h3>", unsafe_allow_html=True)
        
        # Section de configuration des joueurs
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='dashboard-card' style='padding: 20px; border-color: #FF6B35;'>
                <h4 style='color: #FF6B35; margin-bottom: 15px;'>👤 Joueur 1</h4>
            </div>
            """, unsafe_allow_html=True)
            
            ligue1 = st.selectbox("🏆 Compétition", competitions, key="ligue1_comp")
            df_j1 = df[df['Compétition'] == ligue1]
            joueur1 = st.selectbox("Joueur", df_j1['Joueur'].sort_values(), key="joueur1_comp")
        
        with col2:
            st.markdown("""
            <div class='dashboard-card' style='padding: 20px; border-color: #004E89;'>
                <h4 style='color: #004E89; margin-bottom: 15px;'>👤 Joueur 2</h4>
            </div>
            """, unsafe_allow_html=True)
            
            ligue2 = st.selectbox("🏆 Compétition", competitions, key="ligue2_comp")
            df_j2 = df[df['Compétition'] == ligue2]
            joueur2 = st.selectbox("Joueur", df_j2['Joueur'].sort_values(), key="joueur2_comp")
        
        if joueur1 and joueur2:
            # Informations des joueurs
            player1_info = df_j1[df_j1['Joueur'] == joueur1].iloc[0]
            player2_info = df_j2[df_j2['Joueur'] == joueur2].iloc[0]
            
            st.markdown(f"""
            <div class='dashboard-card animated-card' style='text-align: center; padding: 25px; margin: 20px 0;'>
                <h3 style='color: #FF6B35; margin-bottom: 20px;'>⚔️ Comparaison : {joueur1} vs {joueur2}</h3>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 30px;'>
                    <div style='border-left: 4px solid #FF6B35; padding-left: 15px;'>
                        <h4 style='color: #FF6B35; margin-bottom: 10px;'>{joueur1}</h4>
                        <p style='color: #E2E8F0; margin: 5px 0;'>🏟️ {player1_info['Équipe']}</p>
                        <p style='color: #E2E8F0; margin: 5px 0;'>⚽ {player1_info['Position']}</p>
                        <p style='color: #E2E8F0; margin: 5px 0;'>🏆 {ligue1}</p>
                    </div>
                    <div style='border-left: 4px solid #004E89; padding-left: 15px;'>
                        <h4 style='color: #004E89; margin-bottom: 10px;'>{joueur2}</h4>
                        <p style='color: #E2E8F0; margin: 5px 0;'>🏟️ {player2_info['Équipe']}</p>
                        <p style='color: #E2E8F0; margin: 5px 0;'>⚽ {player2_info['Position']}</p>
                        <p style='color: #E2E8F0; margin: 5px 0;'>🏆 {ligue2}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                values1 = MetricsCalculator.calculate_percentiles(joueur1, df_j1)
                values2 = MetricsCalculator.calculate_percentiles(joueur2, df_j2)
                
                # Charger les polices
                font_normal = FontManager()
                font_bold = FontManager()
                font_italic = FontManager()
                
                # Configuration avancée du pizza chart comparatif
                params_offset = [False] * len(AppConfig.RAW_STATS)
                if len(params_offset) > 9:
                    params_offset[9] = True
                if len(params_offset) > 10:
                    params_offset[10] = True
                
                # Créer le pizza chart avec les couleurs de l'interface
                baker = PyPizza(
                    params=list(AppConfig.RAW_STATS.keys()),
                    background_color="#0E1117",
                    straight_line_color="#FFFFFF",
                    straight_line_lw=2,
                    last_circle_color="#FF6B35",
                    last_circle_lw=3,
                    other_circle_ls="-.",
                    other_circle_lw=1,
                    other_circle_color="#4A5568"
                )
                
                fig, ax = baker.make_pizza(
                    values1,
                    compare_values=values2,
                    figsize=(16, 16),
                    kwargs_slices=dict(
                        facecolor=AppConfig.COLORS['primary'], 
                        edgecolor="#FFFFFF", 
                        linewidth=2, 
                        zorder=2,
                        alpha=0.8
                    ),
                    kwargs_compare=dict(
                        facecolor=AppConfig.COLORS['secondary'], 
                        edgecolor="#FFFFFF", 
                        linewidth=2, 
                        zorder=2,
                        alpha=0.8
                    ),
                    kwargs_params=dict(
                        color="#FFFFFF", 
                        fontsize=13, 
                        fontproperties=font_bold.prop,
                        weight='bold'
                    ),
                    kwargs_values=dict(
                        color="#FFFFFF", 
                        fontsize=11, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        weight='bold',
                        bbox=dict(
                            edgecolor="#FFFFFF", 
                            facecolor=AppConfig.COLORS['primary'], 
                            boxstyle="round,pad=0.25", 
                            lw=2,
                            alpha=0.9
                        )
                    ),
                    kwargs_compare_values=dict(
                        color="#FFFFFF", 
                        fontsize=11, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        weight='bold',
                        bbox=dict(
                            edgecolor="#FFFFFF", 
                            facecolor=AppConfig.COLORS['secondary'], 
                            boxstyle="round,pad=0.25", 
                            lw=2,
                            alpha=0.9
                        )
                    )
                )
                
                # Ajustement des textes si la méthode existe
                try:
                    baker.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)
                except:
                    pass  # Si la méthode n'existe pas, on continue sans ajustement
                
                # Personnalisation du fond
                fig.patch.set_facecolor('#0E1117')
                ax.set_facecolor('#0E1117')
                
                # Titre principal
                fig.text(0.515, 0.97, "Pizza Chart Comparatif | Percentiles | Saison 2024-25",
                         size=20, ha="center", fontproperties=font_bold.prop, color="#FFFFFF")
                
                # Sous-titre avec informations
                fig.text(0.515, 0.945, f"{ligue1} vs {ligue2}",
                         size=16, ha="center", fontproperties=font_bold.prop, color="#00C896")
                
                # Légende avec couleurs de l'interface
                legend_p1 = mpatches.Patch(
                    color=AppConfig.COLORS['primary'], 
                    label=f"{joueur1} ({ligue1})"
                )
                legend_p2 = mpatches.Patch(
                    color=AppConfig.COLORS['secondary'], 
                    label=f"{joueur2} ({ligue2})"
                )
                
                legend = ax.legend(
                    handles=[legend_p1, legend_p2], 
                    loc="upper right", 
                    bbox_to_anchor=(1.35, 1.0),
                    fontsize=12,
                    fancybox=True,
                    shadow=True,
                    framealpha=0.9
                )
                legend.get_frame().set_facecolor('#1E2640')
                legend.get_frame().set_edgecolor('#FF6B35')
                
                # Footer stylé
                fig.text(0.99, 0.01, "Dashboard Football Pro | Source: FBRef\nInspiration: @Worville, @FootballSlices",
                         size=10, ha="right", fontproperties=font_italic.prop, color="#718096")
                
                # Informations contextuelles
                fig.text(0.01, 0.01, f"Percentiles calculés sur leurs compétitions respectives",
                         size=10, ha="left", fontproperties=font_italic.prop, color="#718096")
                
                st.pyplot(fig, use_container_width=True)
                
                # Guide de lecture pour la comparaison
                st.markdown(f"""
                <div class='dashboard-card animated-card' style='text-align: center; padding: 25px; margin-top: 20px;'>
                    <h4 style='color: #00C896; margin-bottom: 20px;'>📊 Analyse Comparative</h4>
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 30px;'>
                        <div style='background: linear-gradient(135deg, #FF6B35, rgba(255,107,53,0.2)); padding: 20px; border-radius: 15px; border: 2px solid #FF6B35;'>
                            <h5 style='color: #FFFFFF; margin-bottom: 15px;'>{joueur1}</h5>
                            <p style='color: #FFFFFF; margin: 0; font-size: 0.9em;'>
                                Représenté par la couleur <strong>orange primaire</strong><br>
                                Percentiles calculés vs {ligue1}
                            </p>
                        </div>
                        <div style='background: linear-gradient(135deg, #004E89, rgba(0,78,137,0.2)); padding: 20px; border-radius: 15px; border: 2px solid #004E89;'>
                            <h5 style='color: #FFFFFF; margin-bottom: 15px;'>{joueur2}</h5>
                            <p style='color: #FFFFFF; margin: 0; font-size: 0.9em;'>
                                Représenté par la couleur <strong>bleu marine</strong><br>
                                Percentiles calculés vs {ligue2}
                            </p>
                        </div>
                    </div>
                    <p style='color: #A0AEC0; margin-top: 20px; font-style: italic;'>
                        Les zones où les couleurs se chevauchent montrent des performances similaires
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la création du pizza chart comparatif : {str(e)}")
                st.info("💡 Vérifiez que les deux joueurs existent dans leurs compétitions respectives.")
        else:
    
    @staticmethod
    def _render_detailed_metrics(metrics: Dict[str, float], title: str):
        """Affiche les métriques détaillées"""
        st.markdown(f"<h3 class='subsection-title'>{title}</h3>", unsafe_allow_html=True)
        
        # Créer des colonnes pour afficher les métriques
        cols = st.columns(min(len(metrics), 5))
        
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i % 5]:
                if '/' in str(value):
                    display_value = f"{value:.2f}"
                elif '%' in metric:
                    display_value = f"{value:.1f}%"
                else:
                    display_value = f"{value:.2f}"
                
                st.markdown(f"""
                <div class='metric-card animated-card'>
                    <div class='metric-value'>{display_value}</div>
                    <div class='metric-label'>{metric}</div>
                </div>
                """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE DONNÉES
# ================================================================================================

class DataManager:
    """Gestionnaire centralisé pour les données"""
    
    @staticmethod
    @st.cache_data
    def load_data(file_path: str = 'df_BIG2025.csv') -> Optional[pd.DataFrame]:
        """Charge les données depuis le fichier CSV"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            return df
        except FileNotFoundError:
            st.error(f"❌ Fichier '{file_path}' non trouvé. Veuillez vous assurer que le fichier est dans le même répertoire.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
            return None
    
    @staticmethod
    def filter_data_by_competition(df: pd.DataFrame, competition: str) -> pd.DataFrame:
        """Filtre les données par compétition"""
        return df[df['Compétition'] == competition]
    
    @staticmethod
    def filter_data_by_minutes(df: pd.DataFrame, min_minutes: int) -> pd.DataFrame:
        """Filtre les données par minutes jouées"""
        return df[df['Minutes jouées'] >= min_minutes]
    
    @staticmethod
    def get_competitions(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des compétitions"""
        return sorted(df['Compétition'].dropna().unique())
    
    @staticmethod
    def get_players(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des joueurs"""
        return sorted(df['Joueur'].dropna().unique())

# ================================================================================================
# GESTIONNAIRE DE SIDEBAR
# ================================================================================================

class SidebarManager:
    """Gestionnaire pour la sidebar"""
    
    @staticmethod
    def render_sidebar(df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
        """Rendu complet de la sidebar"""
        with st.sidebar:
            UIComponents.render_sidebar_header()
            
            # Sélection de la compétition
            competitions = DataManager.get_competitions(df)
            selected_competition = st.selectbox(
                "🏆 Choisir une compétition :",
                competitions,
                index=0,
                help="Sélectionnez la compétition pour filtrer les joueurs"
            )
            
            # Filtrage par compétition
            df_filtered = DataManager.filter_data_by_competition(df, selected_competition)
            
            st.markdown("---")
            
            # Filtre par minutes jouées
            SidebarManager._render_minutes_filter(df_filtered)
            
            # Application du filtre minutes
            min_minutes_filter = st.session_state.get('min_minutes_filter', 0)
            df_filtered_minutes = DataManager.filter_data_by_minutes(df_filtered, min_minutes_filter)
            
            # Informations sur le filtrage
            SidebarManager._render_filter_info(df_filtered_minutes)
            
            st.markdown("---")
            
            # Sélection du joueur
            selected_player = SidebarManager._render_player_selection(df_filtered_minutes)
            
            # Informations additionnelles avec achievements
            SidebarManager._render_sidebar_footer()
            
            # Si un joueur est sélectionné, afficher ses achievements
            if selected_player:
                UIComponents.render_player_achievements_sidebar()
            
            return selected_competition, selected_player, df_filtered_minutes
    
    @staticmethod
    def _render_minutes_filter(df_filtered: pd.DataFrame):
        """Rendu du filtre par minutes"""
        if not df_filtered['Minutes jouées'].empty:
            min_minutes = int(df_filtered['Minutes jouées'].min())
            max_minutes = int(df_filtered['Minutes jouées'].max())
            
            st.markdown("**⏱️ Filtrer par minutes jouées :**")
            
            min_minutes_filter = st.slider(
                "Minutes minimum jouées :",
                min_value=min_minutes,
                max_value=max_minutes,
                value=min_minutes,
                step=90,
                help="Filtrer les joueurs ayant joué au minimum ce nombre de minutes",
                key='min_minutes_filter'
            )
    
    @staticmethod
    def _render_filter_info(df_filtered: pd.DataFrame):
        """Affiche les informations de filtrage"""
        nb_joueurs = len(df_filtered)
        
        if nb_joueurs > 0:
            st.success(f"✅ **{nb_joueurs} joueurs** correspondent aux critères")
        else:
            st.warning("⚠️ Aucun joueur ne correspond aux critères")
    
    @staticmethod
    def _render_player_selection(df_filtered: pd.DataFrame) -> Optional[str]:
        """Rendu de la sélection de joueur"""
        if not df_filtered.empty:
            joueurs = DataManager.get_players(df_filtered)
            if joueurs:
                selected_player = st.selectbox(
                    "👤 Choisir un joueur :",
                    joueurs,
                    index=0,
                    help="Sélectionnez le joueur à analyser"
                )
                return selected_player
        
        st.error("❌ Aucun joueur disponible avec ces critères.")
        return None
    
    @staticmethod
    def _render_sidebar_footer():
        """Rendu du footer de la sidebar"""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%); border-radius: 10px;'>
            <p style='color: #E2E8F0; margin: 0; font-size: 0.9em; font-weight: 600;'>
                📊 Dashboard Pro
            </p>
            <p style='color: #A0AEC0; margin: 5px 0 0 0; font-size: 0.8em;'>
                Analyse Football Avancée
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# APPLICATION PRINCIPALE
# ================================================================================================

class FootballDashboard:
    """Classe principale de l'application Dashboard Football"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self._configure_page()
        self._load_styles()
    
    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(**AppConfig.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS"""
        st.markdown(StyleManager.load_custom_css(), unsafe_allow_html=True)
    
    def run(self):
        """Méthode principale d'exécution de l'application"""
        # Chargement des données
        df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        # Rendu de l'en-tête
        UIComponents.render_header()
        
        # Rendu de la sidebar et récupération des sélections
        selected_competition, selected_player, df_filtered = SidebarManager.render_sidebar(df)
        
        if selected_player:
            # Récupération des données du joueur
            player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
            
            # Affichage de l'animation de chargement temporaire
            loading_placeholder = st.empty()
            with loading_placeholder:
                UIComponents.render_loading_animation()
            
            # Simulation d'un temps de chargement pour l'effet
            import time
            time.sleep(0.5)  # Délai très court pour l'effet visuel
            
            # Effacer l'animation et afficher le contenu
            loading_placeholder.empty()
            
            # Affichage de la carte du joueur avec toutes les informations
            UIComponents.render_player_card(player_data, selected_competition)
            
            # Comparaison rapide
            UIComponents.render_player_comparison_preview(player_data)
            
            # Résumé statistique avancé
            UIComponents.render_player_stats_summary(player_data)
            
            # Métriques de base (version simplifiée maintenant)
            self._render_basic_metrics(player_data)
            
            st.markdown("---")
            
            # Onglets principaux
            self._render_main_tabs(player_data, df_filtered, selected_player, df)
        
        else:
            self._render_no_player_message()
        
        # Footer
        UIComponents.render_footer()
    
    def _render_basic_metrics(self, player_data: pd.Series):
        """Affiche les métriques de base du joueur"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        metrics = [
            ("👤 Âge", f"{player_data['Âge']} ans"),
            ("⚽ Position", player_data['Position']),
            ("🏟️ Équipe", player_data['Équipe']),
            ("🌍 Nationalité", player_data['Nationalité']),
            ("⏱️ Minutes", f"{int(player_data['Minutes jouées'])} min")
        ]
        
        cols = [col1, col2, col3, col4, col5]
        
        for i, (label, value) in enumerate(metrics):
            with cols[i]:
                st.markdown(f"""
                <div class='metric-card animated-card'>
                    <div class='metric-value' style='font-size: 1.5em;'>{value}</div>
                    <div class='metric-label'>{label}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_main_tabs(self, player_data: pd.Series, df_filtered: pd.DataFrame, 
                         selected_player: str, df_full: pd.DataFrame):
        """Rendu des onglets principaux"""
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Performance Offensive", 
            "🛡️ Performance Défensive", 
            "🎨 Performance Technique", 
            "🔄 Comparaison"
        ])
        
        with tab1:
            TabManager.render_offensive_tab(player_data, df_filtered, selected_player)
        
        with tab2:
            TabManager.render_defensive_tab(player_data, df_filtered, selected_player)
        
        with tab3:
            TabManager.render_technical_tab(player_data, df_filtered, selected_player)
        
        with tab4:
            TabManager.render_comparison_tab(df_full, selected_player)
    
    def _render_no_player_message(self):
        """Affiche un message quand aucun joueur n'est sélectionné"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 40px;'>
            <h2 style='color: #FF6B35; margin-bottom: 20px;'>⚠️ Aucun joueur sélectionné</h2>
            <p style='color: #E2E8F0; font-size: 1.2em; margin-bottom: 30px;'>
                Veuillez ajuster les filtres dans la sidebar pour sélectionner un joueur à analyser.
            </p>
            <div style='display: flex; justify-content: center; gap: 30px; margin-top: 30px;'>
                <div style='text-align: center;'>
                    <div style='font-size: 3em; margin-bottom: 10px;'>🎯</div>
                    <p style='color: #A0AEC0;'>Analyse Offensive</p>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 3em; margin-bottom: 10px;'>🛡️</div>
                    <p style='color: #A0AEC0;'>Analyse Défensive</p>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 3em; margin-bottom: 10px;'>🎨</div>
                    <p style='color: #A0AEC0;'>Analyse Technique</p>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 3em; margin-bottom: 10px;'>🔄</div>
                    <p style='color: #A0AEC0;'>Comparaison</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_error_page(self):
        """Affiche la page d'erreur"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 40px; border-color: #D62828;'>
            <h1 style='color: #D62828; margin-bottom: 20px;'>⚠️ Erreur de Chargement</h1>
            <p style='color: #E2E8F0; font-size: 1.2em; margin-bottom: 30px;'>
                Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
            </p>
            <div style='background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%); padding: 20px; border-radius: 15px; margin-top: 30px;'>
                <h3 style='color: #00C896; margin-bottom: 15px;'>📋 Fichiers requis :</h3>
                <ul style='color: #E2E8F0; text-align: left; max-width: 600px; margin: 0 auto;'>
                    <li>df_BIG2025.csv (données principales)</li>
                    <li>images_joueurs/ (photos des joueurs)</li>
                    <li>*_Logos/ (logos des clubs par compétition)</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# ================================================================================================

def main():
    """Point d'entrée principal de l'application"""
    dashboard = FootballDashboard()
    dashboard.run()

# Exécution de l'application
if __name__ == "__main__":
    main()
