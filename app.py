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
import base64
import io

# ================================================================================================
# CONFIGURATION DE L'APPLICATION
# ================================================================================================

def format_market_value(value):
    """
    Formate une valeur marchande avec des sigles comme 'M' ou 'K' et le symbole Euro.
    """
    if pd.isna(value) or value is None:
        return "N/A"
    
    # Conversion en nombre si c'est une chaîne
    if isinstance(value, str):
        try:
            clean_value = ''.join(c for c in value if c.isdigit() or c == '.')
            if clean_value:
                value = float(clean_value)
            else:
                return "N/A"
        except (ValueError, TypeError):
            return str(value)
    
    # Conversion en float pour les calculs
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "N/A"
    
    # Formatage selon les seuils
    if value >= 1_000_000_000:  # Milliards
        return f"{value/1_000_000_000:.1f}B€"
    elif value >= 1_000_000:  # Millions
        return f"{value/1_000_000:.1f}M€"
    elif value >= 1_000:  # Milliers
        return f"{value/1_000:.1f}K€"
    else:  # Moins de 1000
        return f"{value:.0f}€"

class AppConfig:
    """Configuration centralisée de l'application"""
    
    # Configuration de la page
    PAGE_CONFIG = {
        "page_title": "Dashboard Football Pro",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Palette de couleurs moderne et sobre
    COLORS = {
        'primary': '#1E40AF',           # Bleu professionnel
        'secondary': '#0F172A',         # Noir moderne
        'accent': '#3B82F6',           # Bleu clair
        'success': '#10B981',          # Vert moderne
        'warning': '#F59E0B',          # Orange
        'danger': '#EF4444',           # Rouge moderne
        'dark': '#0F172A',             # Très foncé
        'light': '#F8FAFC',            # Blanc pur
        'text': '#1F2937',             # Gris foncé pour texte
        'muted': '#6B7280',            # Gris moyen
        'gradient': ['#1E40AF', '#3B82F6', '#10B981', '#F59E0B']
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
        """Charge les styles CSS personnalisés modernes et sobres"""
        return """
        <style>
        /* ===== IMPORTATION DE POLICES MODERNES ===== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* ===== STYLES GLOBAUX ===== */
        .main {
            background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
            color: #1F2937;
            font-family: 'Inter', sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
            font-family: 'Inter', sans-serif;
        }
        
        /* ===== BACKGROUND DYNAMIQUE AVEC LOGO D'ÉQUIPE ===== */
        .team-background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.03;
            background-size: 300px 300px;
            background-repeat: repeat;
            background-position: center;
            pointer-events: none;
        }
        
        /* ===== STYLES DES ONGLETS MODERNES ===== */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 4px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 20px;
            z-index: 100;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #6B7280;
            border-radius: 8px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s ease;
            padding: 12px 20px;
            font-family: 'Inter', sans-serif;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(30, 64, 175, 0.05);
            color: #1E40AF;
        }
        
        .stTabs [aria-selected="true"] {
            background: #1E40AF;
            color: white;
            box-shadow: 0 2px 8px rgba(30, 64, 175, 0.3);
            font-weight: 600;
        }
        
        /* ===== CARTES MODERNES ===== */
        .dashboard-card {
            background: rgba(255, 255, 255, 0.98);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin: 16px 0;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .dashboard-card:hover {
            border-color: #1E40AF;
            box-shadow: 0 10px 25px -3px rgba(30, 64, 175, 0.1);
            transform: translateY(-2px);
        }
        
        .player-header-card {
            background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
            padding: 32px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 32px;
            box-shadow: 0 20px 25px -5px rgba(30, 64, 175, 0.2);
            border: none;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            text-align: center;
            transition: all 0.2s ease;
            backdrop-filter: blur(10px);
        }
        
        .metric-card:hover {
            border-color: #10B981;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
            transform: translateY(-1px);
        }
        
        .metric-card-compact {
            background: rgba(255, 255, 255, 0.95);
            padding: 16px 12px;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
            text-align: center;
            transition: all 0.2s ease;
            min-height: 90px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            backdrop-filter: blur(10px);
        }
        
        .metric-card-compact:hover {
            border-color: #10B981;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
            transform: translateY(-1px);
        }
        
        .metric-value-compact {
            font-size: 1.5em;
            font-weight: 700;
            color: #1E40AF;
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            line-height: 1.2;
            font-family: 'Inter', sans-serif;
        }
        
        .metric-label-compact {
            font-size: 0.75em;
            color: #6B7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-family: 'Inter', sans-serif;
        }
        
        /* ===== CONTENEURS D'IMAGES MODERNES ===== */
        .image-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 20px;
            border: 2px solid #E5E7EB;
            overflow: hidden;
            height: 320px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .image-container:hover {
            border-color: #1E40AF;
            box-shadow: 0 10px 25px -3px rgba(30, 64, 175, 0.1);
        }
        
        .club-logo-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 20px;
            border: 2px solid #E5E7EB;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .club-logo-container:hover {
            border-color: #1E40AF;
            box-shadow: 0 10px 25px -3px rgba(30, 64, 175, 0.1);
        }
        
        /* ===== STYLES DE TEXTE MODERNES ===== */
        .section-title {
            color: #1F2937;
            font-size: 2.25em;
            font-weight: 800;
            text-align: center;
            margin: 32px 0 24px 0;
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.025em;
        }
        
        .subsection-title {
            color: #1E40AF;
            font-size: 1.5em;
            font-weight: 700;
            margin: 24px 0 16px 0;
            border-left: 4px solid #1E40AF;
            padding-left: 16px;
            font-family: 'Inter', sans-serif;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: 800;
            color: #1E40AF;
            font-family: 'Inter', sans-serif;
        }
        
        .metric-label {
            font-size: 0.875em;
            color: #6B7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-family: 'Inter', sans-serif;
        }
        
        /* ===== SIDEBAR MODERNE ===== */
        .sidebar-header {
            background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
            padding: 24px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(30, 64, 175, 0.2);
        }
        
        /* ===== FOOTER MODERNE ===== */
        .dashboard-footer {
            background: rgba(255, 255, 255, 0.95);
            padding: 32px;
            border-radius: 16px;
            text-align: center;
            margin-top: 48px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        
        /* ===== ANIMATIONS MODERNES ===== */
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
            animation: fadeInUp 0.5s ease-out;
        }
        
        /* ===== INDICATEURS DE PERFORMANCE ===== */
        .performance-indicator {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .performance-excellent {
            background: rgba(16, 185, 129, 0.1);
            color: #059669;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        
        .performance-good {
            background: rgba(245, 158, 11, 0.1);
            color: #D97706;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        
        .performance-average {
            background: rgba(107, 114, 128, 0.1);
            color: #4B5563;
            border: 1px solid rgba(107, 114, 128, 0.2);
        }
        
        /* ===== RESPONSIVITÉ ===== */
        @media (max-width: 768px) {
            .dashboard-card {
                padding: 16px;
                margin: 12px 0;
            }
            
            .section-title {
                font-size: 1.875em;
            }
            
            .subsection-title {
                font-size: 1.25em;
            }
            
            .metric-card-compact {
                padding: 12px 8px;
                min-height: 80px;
            }
            
            .metric-value-compact {
                font-size: 1.25em;
            }
            
            .metric-label-compact {
                font-size: 0.7em;
            }
        }
        
        /* ===== MASQUAGE DES ÉLÉMENTS STREAMLIT ===== */
        .stDeployButton {
            display: none;
        }
        
        #MainMenu {
            visibility: hidden;
        }
        
        footer {
            visibility: hidden;
        }
        
        .stException {
            display: none;
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
            photo_path = f"images_joueurs/{player_name}{ext}"
            if os.path.exists(photo_path):
                return photo_path
        
        # Recherche plus flexible
        for ext in extensions:
            pattern = f"images_joueurs/{player_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
            # Essayer avec nom inversé
            if " " in player_name:
                parts = player_name.split(" ")
                if len(parts) >= 2:
                    reversed_name = " ".join(parts[::-1])
                    pattern = f"images_joueurs/{reversed_name}*{ext}"
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
            logo_path = f"{folder}/{team_name}{ext}"
            if os.path.exists(logo_path):
                return logo_path
        
        # Recherche plus flexible
        for ext in extensions:
            pattern = f"{folder}/{team_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
            # Variations de nom
            clean_team = team_name.replace(" ", "_").replace("'", "").replace("-", "_")
            pattern = f"{folder}/{clean_team}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
        
        return None
    
    @staticmethod
    def create_team_background(team_name: str, competition: str) -> str:
        """Crée un background CSS avec le logo de l'équipe"""
        logo_path = ImageManager.get_club_logo(competition, team_name)
        
        if logo_path and os.path.exists(logo_path):
            try:
                with open(logo_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    return f"data:image/png;base64,{img_data}"
            except Exception:
                pass
        
        return ""

# ================================================================================================
# COMPOSANTS UI
# ================================================================================================

class UIComponents:
    """Composants d'interface utilisateur réutilisables"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête principal moderne"""
        st.markdown("""
        <div class='player-header-card animated-card'>
            <h1 style='color: white; margin: 0; font-size: 3em; font-weight: 800; font-family: "Inter", sans-serif;'>
                Dashboard Football Pro
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 16px 0 0 0; font-size: 1.1em; font-weight: 400;'>
                Analyse professionnelle des performances - Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_header():
        """Affiche l'en-tête de la sidebar"""
        st.markdown("""
        <div class='sidebar-header'>
            <h2 style='color: white; margin: 0; font-weight: 700; font-size: 1.5em;'>Configuration</h2>
            <p style='color: rgba(255,255,255,0.8); margin: 12px 0 0 0; font-size: 0.9em;'>
                Sélectionnez votre analyse
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_team_background(team_name: str, competition: str):
        """Affiche le background avec le logo de l'équipe"""
        bg_image = ImageManager.create_team_background(team_name, competition)
        
        if bg_image:
            st.markdown(f"""
            <div class="team-background" style="background-image: url('{bg_image}');"></div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte complète du joueur avec background d'équipe"""
        # Affichage du background de l'équipe
        UIComponents.render_team_background(player_data['Équipe'], competition)
        
        container = st.container()
        
        with container:
            col1, col2, col3 = st.columns([1, 2.5, 1], gap="medium")
            
            with col1:
                UIComponents._render_player_photo(player_data['Joueur'])
            
            with col2:
                UIComponents._render_player_info_modern(player_data)
            
            with col3:
                UIComponents._render_club_logo(player_data['Équipe'], competition)
    
    @staticmethod
    def _render_player_photo(player_name: str):
        """Affiche la photo du joueur avec style moderne"""
        photo_path = ImageManager.get_player_photo(player_name)
        
        if photo_path:
            try:
                image = Image.open(photo_path)
                st.markdown(f"""
                <div class='image-container animated-card'>
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 12px;">
                </div>
                <p style='text-align: center; color: #1E40AF; font-weight: 600; margin-top: 12px; font-size: 0.9em;'>
                    {player_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_photo_placeholder(player_name)
        else:
            UIComponents._render_photo_placeholder(player_name)
    
    @staticmethod
    def _render_club_logo(team_name: str, competition: str):
        """Affiche le logo du club avec style moderne"""
        logo_path = ImageManager.get_club_logo(competition, team_name)
        
        if logo_path:
            try:
                image = Image.open(logo_path)
                st.markdown(f"""
                <div class='club-logo-container animated-card'>
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain;">
                </div>
                <p style='text-align: center; color: #1E40AF; font-weight: 600; margin-top: 12px; font-size: 0.9em;'>
                    {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_logo_placeholder(team_name)
        else:
            UIComponents._render_logo_placeholder(team_name)
    
    @staticmethod
    def _render_player_info_modern(player_data: pd.Series):
        """Affiche les informations centrales du joueur avec style moderne"""
        # Récupération et formatage de la valeur marchande
        valeur_marchande = "N/A"
        if 'Valeur marchande' in player_data.index:
            valeur_marchande = format_market_value(player_data['Valeur marchande'])
        
        # Tronquer les textes longs pour éviter le débordement
        equipe_display = player_data['Équipe'][:15] + "..." if len(str(player_data['Équipe'])) > 15 else player_data['Équipe']
        nationalite_display = player_data['Nationalité'][:10] + "..." if len(str(player_data['Nationalité'])) > 10 else player_data['Nationalité']
        position_display = player_data['Position'][:8] + "..." if len(str(player_data['Position'])) > 8 else player_data['Position']
        
        st.markdown(f"""
        <div class='dashboard-card animated-card' style='text-align: center;'>
            <h2 class='section-title' style='margin-bottom: 28px; font-size: 2em; color: #1F2937;'>
                {player_data['Joueur']}
            </h2>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 24px; max-width: 100%;'>
                <div class='metric-card-compact'>
                    <div class='metric-value-compact'>{player_data['Âge']}</div>
                    <div class='metric-label-compact'>Âge</div>
                </div>
                <div class='metric-card-compact'>
                    <div class='metric-value-compact' title='{player_data['Position']}'>{position_display}</div>
                    <div class='metric-label-compact'>Position</div>
                </div>
                <div class='metric-card-compact'>
                    <div class='metric-value-compact' title='{player_data['Nationalité']}'>{nationalite_display}</div>
                    <div class='metric-label-compact'>Nationalité</div>
                </div>
                <div class='metric-card-compact'>
                    <div class='metric-value-compact'>{int(player_data['Minutes jouées'])}</div>
                    <div class='metric-label-compact'>Minutes</div>
                </div>
                <div class='metric-card-compact'>
                    <div class='metric-value-compact' style='color: #F59E0B;'>{valeur_marchande}</div>
                    <div class='metric-label-compact'>Val. Marchande</div>
                </div>
                <div class='metric-card-compact'>
                    <div class='metric-value-compact' title='{player_data['Équipe']}'>{equipe_display}</div>
                    <div class='metric-label-compact'>Équipe</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_photo_placeholder(player_name: str):
        """Affiche un placeholder moderne pour la photo"""
        st.markdown(f"""
        <div class='image-container animated-card'>
            <div style='text-align: center; color: #6B7280;'>
                <div style='font-size: 4em; margin-bottom: 12px;'>👤</div>
                <p style='margin: 0; font-weight: 500;'>Photo non disponible</p>
                <p style='font-size: 0.8em; margin: 8px 0 0 0; color: #9CA3AF;'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder(team_name: str):
        """Affiche un placeholder moderne pour le logo"""
        st.markdown(f"""
        <div class='club-logo-container animated-card'>
            <div style='text-align: center; color: #6B7280;'>
                <div style='font-size: 3em; margin-bottom: 12px;'>🏟️</div>
                <p style='margin: 0; font-weight: 500;'>Logo non disponible</p>
                <p style='font-size: 0.8em; margin: 8px 0 0 0; color: #9CA3AF;'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _image_to_base64(image: Image.Image) -> str:
        """Convertit une image PIL en base64"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    @staticmethod
    def render_footer():
        """Affiche le footer moderne"""
        st.markdown("""
        <div class='dashboard-footer animated-card'>
            <h3 style='color: #1E40AF; margin: 0 0 16px 0; font-weight: 700; font-size: 1.25em;'>
                Dashboard Football Professionnel
            </h3>
            <p style='color: #1F2937; margin: 0; font-size: 1em; font-weight: 500;'>
                Analyse avancée des performances footballistiques
            </p>
            <p style='color: #6B7280; margin: 12px 0 0 0; font-size: 0.875em;'>
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
    """Gestionnaire centralisé pour les graphiques modernes"""
    
    @staticmethod
    def create_modern_bar_chart(data: Dict[str, float], title: str, color_palette: List[str]) -> go.Figure:
        """Crée un graphique en barres moderne"""
        fig = go.Figure(data=[go.Bar(
            x=list(data.keys()),
            y=list(data.values()),
            marker=dict(
                color=color_palette,
                line=dict(color='rgba(30, 64, 175, 0.1)', width=1),
                cornerradius=8
            ),
            text=[f"{v:.1f}" for v in data.values()],
            textposition='outside',
            textfont=dict(color='#1F2937', size=14, family='Inter')
        )])
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, color='#1F2937', family='Inter', weight=600),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                tickfont=dict(color='#374151', size=12, family='Inter'),
                tickangle=0,
                gridcolor='rgba(229, 231, 235, 0.6)',
                showgrid=False,
                linecolor='#E5E7EB'
            ),
            yaxis=dict(
                tickfont=dict(color='#374151', size=12, family='Inter'),
                gridcolor='rgba(229, 231, 235, 0.4)',
                linecolor='#E5E7EB'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.95)',
            font=dict(color='#1F2937', family='Inter'),
            height=450,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    @staticmethod
    def create_modern_gauge_chart(data: Dict[str, float], title: str) -> go.Figure:
        """Crée un graphique en jauges moderne"""
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
                        axis=dict(range=[0, 100], tickcolor='#374151'),
                        bar=dict(color=color, thickness=0.7),
                        bgcolor="rgba(229, 231, 235, 0.3)",
                        borderwidth=2,
                        bordercolor="#E5E7EB",
                        steps=[
                            {'range': [0, 33], 'color': 'rgba(229, 231, 235, 0.2)'},
                            {'range': [33, 66], 'color': 'rgba(229, 231, 235, 0.3)'},
                            {'range': [66, 100], 'color': 'rgba(229, 231, 235, 0.4)'}
                        ],
                        threshold={
                            'line': {'color': "#1F2937", 'width': 3},
                            'thickness': 0.8,
                            'value': 80
                        }
                    ),
                    number={
                        'suffix': '%', 
                        'font': {'color': '#1F2937', 'size': 16, 'family': 'Inter'}
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            height=350,
            title_text=title,
            title_font_color='#1F2937',
            title_font_size=18,
            title_font_family='Inter',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.95)',
            font=dict(color='#1F2937', family='Inter'),
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        return fig
    
    @staticmethod
    def create_modern_comparison_chart(player_data: Dict[str, float], avg_data: Dict[str, float], 
                                     player_name: str, title: str) -> go.Figure:
        """Crée un graphique de comparaison moderne"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=player_name,
            x=list(player_data.keys()),
            y=list(player_data.values()),
            marker_color=AppConfig.COLORS['primary'],
            marker_line=dict(color='rgba(30, 64, 175, 0.2)', width=1),
            text=[f"{v:.2f}" for v in player_data.values()],
            textposition='outside',
            textfont=dict(color='#1F2937', family='Inter')
        ))
        
        fig.add_trace(go.Bar(
            name='Moyenne compétition',
            x=list(avg_data.keys()),
            y=list(avg_data.values()),
            marker_color=AppConfig.COLORS['accent'],
            marker_line=dict(color='rgba(59, 130, 246, 0.2)', width=1),
            text=[f"{v:.2f}" for v in avg_data.values()],
            textposition='outside',
            textfont=dict(color='#1F2937', family='Inter')
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color='#1F2937', size=18, family='Inter', weight=600),
                x=0.5
            ),
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.95)',
            font=dict(color='#1F2937', family='Inter'),
            xaxis=dict(
                tickfont=dict(color='#374151', size=12, family='Inter'),
                linecolor='#E5E7EB'
            ),
            yaxis=dict(
                tickfont=dict(color='#374151', size=12, family='Inter'), 
                gridcolor='rgba(229, 231, 235, 0.4)',
                linecolor='#E5E7EB'
            ),
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color='#1F2937', family='Inter')
            ),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    @staticmethod
    def create_modern_radar_chart(metrics: Dict[str, float], percentiles: List[float], 
                                avg_percentiles: List[float], player_name: str, 
                                competition: str, color: str) -> go.Figure:
        """Crée un radar chart moderne"""
        fig = go.Figure()
        
        # Performance du joueur
        fig.add_trace(go.Scatterpolar(
            r=percentiles,
            theta=list(metrics.keys()),
            fill='toself',
            fillcolor=f'rgba({ChartManager._hex_to_rgb(color)}, 0.2)',
            line=dict(color=color, width=3),
            marker=dict(color=color, size=8, symbol='circle'),
            name=player_name,
            hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
            customdata=list(metrics.values())
        ))
        
        # Moyenne de la compétition
        fig.add_trace(go.Scatterpolar(
            r=avg_percentiles,
            theta=list(metrics.keys()),
            mode='lines',
            line=dict(color='rgba(107, 114, 128, 0.8)', width=2, dash='dash'),
            name=f'Moyenne {competition}',
            showlegend=True,
            hovertemplate='<b>%{theta}</b><br>Moyenne: %{r:.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(229, 231, 235, 0.5)',
                    tickcolor='#6B7280',
                    tickfont=dict(color='#6B7280', size=11, family='Inter'),
                    showticklabels=True,
                    tickmode='linear',
                    tick0=0,
                    dtick=20
                ),
                angularaxis=dict(
                    gridcolor='rgba(229, 231, 235, 0.5)',
                    tickcolor='#374151',
                    tickfont=dict(color='#374151', size=12, family='Inter', weight=500),
                    linecolor='rgba(229, 231, 235, 0.7)'
                ),
                bgcolor='rgba(255, 255, 255, 0.95)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1F2937', family='Inter'),
            title=dict(
                text=f"Radar Professionnel - {player_name}",
                font=dict(size=18, color='#1F2937', family='Inter', weight=600),
                x=0.5,
                y=0.95
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color='#1F2937', size=12, family='Inter')
            ),
            height=500,
            margin=dict(l=50, r=50, t=80, b=50)
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
    """Gestionnaire pour les différents onglets avec style moderne"""
    
    @staticmethod
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance offensive moderne"""
        st.markdown("<h2 class='section-title'>Performance Offensive</h2>", unsafe_allow_html=True)
        
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
            
            fig_bar = ChartManager.create_modern_bar_chart(
                basic_actions,
                "Actions Offensives Totales",
                AppConfig.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Radar offensif
            st.markdown("<h3 class='subsection-title'>Radar Offensif</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_modern_radar_chart(
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
            
            fig_gauge = ChartManager.create_modern_gauge_chart(efficiency_data, "Efficacité Offensive")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Comparaison par 90 minutes
            comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
            avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
            
            fig_comp = ChartManager.create_modern_comparison_chart(
                comparison_metrics,
                avg_comparison,
                selected_player,
                "Performance par 90min vs Moyenne"
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        # Métriques détaillées
        TabManager._render_detailed_metrics_modern(analysis['metrics'], "Métriques Offensives")
    
    @staticmethod
    def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance défensive moderne"""
        st.markdown("<h2 class='section-title'>Performance Défensive</h2>", unsafe_allow_html=True)
        
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
            
            fig_bar = ChartManager.create_modern_bar_chart(
                basic_actions,
                "Actions Défensives Totales",
                AppConfig.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Radar défensif
            st.markdown("<h3 class='subsection-title'>Radar Défensif</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_modern_radar_chart(
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
            
            fig_gauge = ChartManager.create_modern_gauge_chart(success_data, "Pourcentages de Réussite")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Comparaison défensive
            comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
            avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
            
            fig_comp = ChartManager.create_modern_comparison_chart(
                comparison_metrics,
                avg_comparison,
                selected_player,
                "Défense par 90min vs Moyenne"
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        TabManager._render_detailed_metrics_modern(analysis['metrics'], "Métriques Défensives")
    
    @staticmethod
    def render_technical_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance technique moderne"""
        st.markdown("<h2 class='section-title'>Performance Technique</h2>", unsafe_allow_html=True)
        
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
            
            fig_bar = ChartManager.create_modern_bar_chart(
                basic_actions,
                "Actions Techniques Totales",
                AppConfig.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Radar technique
            st.markdown("<h3 class='subsection-title'>Radar Technique</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_modern_radar_chart(
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
            
            fig_gauge = ChartManager.create_modern_gauge_chart(technical_success, "Précision Technique")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Comparaison technique
            comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
            avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
            
            fig_comp = ChartManager.create_modern_comparison_chart(
                comparison_metrics,
                avg_comparison,
                selected_player,
                "Technique par 90min vs Moyenne"
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        TabManager._render_detailed_metrics_modern(analysis['metrics'], "Métriques Techniques")
    
    @staticmethod
    def render_comparison_tab(df: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet comparaison moderne"""
        st.markdown("<h2 class='section-title'>Comparaison Pizza Chart</h2>", unsafe_allow_html=True)
        
        # Mode de visualisation
        mode = st.radio(
            "Mode de visualisation",
            ["Radar individuel", "Radar comparatif"],
            horizontal=True
        )
        
        competitions = sorted(df['Compétition'].dropna().unique())
        
        if mode == "Radar individuel":
            TabManager._render_individual_radar_modern(df, selected_player, competitions)
        else:
            TabManager._render_comparative_radar_modern(df, competitions)
    
    @staticmethod
    def _render_individual_radar_modern(df: pd.DataFrame, selected_player: str, competitions: List[str]):
        """Rendu du radar individuel moderne"""
        st.markdown(f"<h3 class='subsection-title'>Radar individuel : {selected_player}</h3>", unsafe_allow_html=True)
        
        try:
            # Sélection de la compétition pour comparaison
            competition = st.selectbox("Compétition de référence", competitions)
            df_comp = df[df['Compétition'] == competition]
            
            values = MetricsCalculator.calculate_percentiles(selected_player, df_comp)
            
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            baker = PyPizza(
                params=list(AppConfig.RAW_STATS.keys()),
                background_color="#F8FAFC",
                straight_line_color="#1F2937",
                straight_line_lw=1,
                last_circle_color="#1F2937",
                last_circle_lw=1,
                other_circle_lw=0,
                inner_circle_size=11
            )
            
            fig, ax = baker.make_pizza(
                values,
                figsize=(14, 16),
                param_location=110,
                color_blank_space="same",
                slice_colors=[AppConfig.COLORS['primary']] * len(values),
                value_colors=["#ffffff"] * len(values),
                value_bck_colors=[AppConfig.COLORS['primary']] * len(values),
                kwargs_slices=dict(edgecolor="#1F2937", zorder=2, linewidth=2),
                kwargs_params=dict(color="#1F2937", fontsize=14, fontproperties=font_bold.prop),
                kwargs_values=dict(
                    color="#ffffff", 
                    fontsize=12, 
                    fontproperties=font_normal.prop,
                    bbox=dict(
                        edgecolor="#1F2937", 
                        facecolor=AppConfig.COLORS['primary'], 
                        boxstyle="round,pad=0.3", 
                        lw=2
                    )
                )
            )
            
            # Titre et sous-titre modernes
            fig.text(0.515, 0.97, selected_player, size=32, ha="center", 
                    fontproperties=font_bold.prop, color="#1F2937", weight='bold')
            fig.text(0.515, 0.94, f"Radar Individuel | Percentiles vs {competition} | Saison 2024-25", 
                    size=16, ha="center", fontproperties=font_bold.prop, color="#374151")
            
            # Footer moderne
            fig.text(0.99, 0.01, "Dashboard Football Pro | Données: FBRef", 
                    size=10, ha="right", fontproperties=font_italic.prop, color="#6B7280")
            
            st.pyplot(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erreur lors de la création du radar individuel : {str(e)}")
    
    @staticmethod
    def _render_comparative_radar_modern(df: pd.DataFrame, competitions: List[str]):
        """Rendu du radar comparatif moderne"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Joueur 1**")
            ligue1 = st.selectbox("Compétition", competitions, key="ligue1_comp")
            df_j1 = df[df['Compétition'] == ligue1]
            joueur1 = st.selectbox("Joueur", df_j1['Joueur'].sort_values(), key="joueur1_comp")
        
        with col2:
            st.markdown("**Joueur 2**")
            ligue2 = st.selectbox("Compétition", competitions, key="ligue2_comp")
            df_j2 = df[df['Compétition'] == ligue2]
            joueur2 = st.selectbox("Joueur", df_j2['Joueur'].sort_values(), key="joueur2_comp")
        
        if joueur1 and joueur2:
            st.markdown(f"<h3 class='subsection-title'>{joueur1} vs {joueur2}</h3>", unsafe_allow_html=True)
            
            try:
                values1 = MetricsCalculator.calculate_percentiles(joueur1, df_j1)
                values2 = MetricsCalculator.calculate_percentiles(joueur2, df_j2)
                
                font_normal = FontManager()
                font_bold = FontManager()
                font_italic = FontManager()
                
                baker = PyPizza(
                    params=list(AppConfig.RAW_STATS.keys()),
                    background_color="#F8FAFC",
                    straight_line_color="#1F2937",
                    straight_line_lw=1,
                    last_circle_color="#1F2937",
                    last_circle_lw=1,
                    other_circle_ls="-.",
                    other_circle_lw=1
                )
                
                fig, ax = baker.make_pizza(
                    values1,
                    compare_values=values2,
                    figsize=(14, 14),
                    kwargs_slices=dict(
                        facecolor=AppConfig.COLORS['primary'], 
                        edgecolor="#1F2937", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_compare=dict(
                        facecolor=AppConfig.COLORS['accent'], 
                        edgecolor="#1F2937", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_params=dict(
                        color="#1F2937", 
                        fontsize=14, 
                        fontproperties=font_bold.prop
                    ),
                    kwargs_values=dict(
                        color="#ffffff", 
                        fontsize=12, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        bbox=dict(
                            edgecolor="#1F2937", 
                            facecolor=AppConfig.COLORS['primary'], 
                            boxstyle="round,pad=0.3", 
                            lw=2
                        )
                    ),
                    kwargs_compare_values=dict(
                        color="#ffffff", 
                        fontsize=12, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        bbox=dict(
                            edgecolor="#1F2937", 
                            facecolor=AppConfig.COLORS['accent'], 
                            boxstyle="round,pad=0.3", 
                            lw=2
                        )
                    )
                )
                
                # Titre moderne
                fig.text(0.515, 0.97, "Radar Comparatif | Percentiles | Saison 2024-25",
                         size=18, ha="center", fontproperties=font_bold.prop, color="#1F2937")
                
                # Légende moderne
                legend_p1 = mpatches.Patch(color=AppConfig.COLORS['primary'], label=joueur1)
                legend_p2 = mpatches.Patch(color=AppConfig.COLORS['accent'], label=joueur2)
                ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0))
                
                # Footer moderne
                fig.text(0.99, 0.01, "Dashboard Football Pro | Source: FBRef",
                         size=10, ha="right", fontproperties=font_italic.prop, color="#6B7280")
                
                st.pyplot(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erreur lors de la création du radar comparatif : {str(e)}")
    
    @staticmethod
    def _render_detailed_metrics_modern(metrics: Dict[str, float], title: str):
        """Affiche les métriques détaillées avec style moderne"""
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
                
                # Déterminer la classe de performance
                performance_class = "performance-average"
                if '%' in metric and value > 80:
                    performance_class = "performance-excellent"
                elif '%' in metric and value > 60:
                    performance_class = "performance-good"
                elif '90' in metric and value > 1.0:
                    performance_class = "performance-good"
                elif '90' in metric and value > 0.5:
                    performance_class = "performance-average"
                
                st.markdown(f"""
                <div class='metric-card animated-card'>
                    <div class='metric-value'>{display_value}</div>
                    <div class='metric-label'>{metric}</div>
                    <div class='performance-indicator {performance_class}'>
                        Performance
                    </div>
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
            df = pd.read_csv("df_BIG2025.csv", encoding='utf-8', delimiter=',')
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
    """Gestionnaire pour la sidebar moderne"""
    
    @staticmethod
    def render_sidebar(df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
        """Rendu complet de la sidebar moderne"""
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
            SidebarManager._render_filter_info_modern(df_filtered_minutes)
            
            st.markdown("---")
            
            # Sélection du joueur
            selected_player = SidebarManager._render_player_selection(df_filtered_minutes)
            
            # Informations additionnelles
            SidebarManager._render_sidebar_footer_modern()
            
            return selected_competition, selected_player, df_filtered_minutes
    
    @staticmethod
    def _render_minutes_filter(df_filtered: pd.DataFrame):
        """Rendu du filtre par minutes moderne"""
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
    def _render_filter_info_modern(df_filtered: pd.DataFrame):
        """Affiche les informations de filtrage modernes"""
        nb_joueurs = len(df_filtered)
        
        if nb_joueurs > 0:
            st.markdown(f"""
            <div style='background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 8px; border-left: 4px solid #10B981; margin: 16px 0;'>
                <p style='color: #059669; margin: 0; font-weight: 600; font-size: 0.9em;'>
                    ✅ {nb_joueurs} joueurs correspondent aux critères
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background: rgba(245, 158, 11, 0.1); padding: 12px; border-radius: 8px; border-left: 4px solid #F59E0B; margin: 16px 0;'>
                <p style='color: #D97706; margin: 0; font-weight: 600; font-size: 0.9em;'>
                    ⚠️ Aucun joueur ne correspond aux critères
                </p>
            </div>
            """, unsafe_allow_html=True)
    
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
    def _render_sidebar_footer_modern():
        """Rendu du footer de la sidebar moderne"""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 16px; background: rgba(255, 255, 255, 0.95); border-radius: 12px; border: 1px solid #E5E7EB;'>
            <p style='color: #1E40AF; margin: 0; font-size: 0.9em; font-weight: 600;'>
                📊 Dashboard Pro
            </p>
            <p style='color: #6B7280; margin: 8px 0 0 0; font-size: 0.8em;'>
                Analyse Football Avancée
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# APPLICATION PRINCIPALE
# ================================================================================================

class FootballDashboard:
    """Classe principale de l'application Dashboard Football moderne"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self._configure_page()
        self._load_styles()
    
    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(**AppConfig.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS modernes"""
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
            
            # Affichage de la carte du joueur avec background d'équipe
            UIComponents.render_player_card(player_data, selected_competition)
            
            st.markdown("---")
            
            # Onglets principaux
            self._render_main_tabs(player_data, df_filtered, selected_player, df)
        
        else:
            self._render_no_player_message()
        
        # Footer
        UIComponents.render_footer()
    
    def _render_main_tabs(self, player_data: pd.Series, df_filtered: pd.DataFrame, 
                         selected_player: str, df_full: pd.DataFrame):
        """Rendu des onglets principaux modernes"""
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
        """Affiche un message moderne quand aucun joueur n'est sélectionné"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 48px;'>
            <h2 style='color: #1E40AF; margin-bottom: 24px; font-weight: 700;'>Aucun joueur sélectionné</h2>
    def _render_error_page(self):
        """Affiche la page d'erreur moderne"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 48px; border-color: #EF4444;'>
            <h1 style='color: #EF4444; margin-bottom: 24px; font-weight: 800;'>Erreur de Chargement</h1>
            <p style='color: #6B7280; font-size: 1.1em; margin-bottom: 32px; line-height: 1.6;'>
                Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
            </p>
            <div style='background: rgba(255, 255, 255, 0.95); padding: 24px; border-radius: 12px; margin-top: 32px; border: 1px solid #E5E7EB;'>
                <h3 style='color: #10B981; margin-bottom: 16px; font-weight: 600;'>📋 Fichiers requis :</h3>
                <ul style='color: #6B7280; text-align: left; max-width: 600px; margin: 0 auto; line-height: 1.8;'>
                    <li><strong>df_BIG2025.csv</strong> - Données principales des joueurs</li>
                    <li><strong>images_joueurs/</strong> - Photos des joueurs</li>
                    <li><strong>*_Logos/</strong> - Logos des clubs par compétition</li>
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
    main()size: 1.1em; margin-bottom: 32px; line-height: 1.6;'>
                Veuillez ajuster les filtres dans la sidebar pour sélectionner un joueur à analyser.
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px; margin-top: 32px;'>
                <div style='text-align: center; padding: 24px; background: rgba(30, 64, 175, 0.05); border-radius: 12px; border: 1px solid rgba(30, 64, 175, 0.1);'>
                    <div style='font-size: 2.5em; margin-bottom: 12px;'>🎯</div>
                    <h4 style='color: #1E40AF; margin: 0; font-weight: 600;'>Analyse Offensive</h4>
                    <p style='color: #6B7280; margin: 8px 0 0 0; font-size: 0.9em;'>Buts, passes décisives, créativité</p>
                </div>
                <div style='text-align: center; padding: 24px; background: rgba(59, 130, 246, 0.05); border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.1);'>
                    <div style='font-size: 2.5em; margin-bottom: 12px;'>🛡️</div>
                    <h4 style='color: #3B82F6; margin: 0; font-weight: 600;'>Analyse Défensive</h4>
                    <p style='color: #6B7280; margin: 8px 0 0 0; font-size: 0.9em;'>Tacles, interceptions, duels</p>
                </div>
                <div style='text-align: center; padding: 24px; background: rgba(16, 185, 129, 0.05); border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.1);'>
                    <div style='font-size: 2.5em; margin-bottom: 12px;'>🎨</div>
                    <h4 style='color: #10B981; margin: 0; font-weight: 600;'>Analyse Technique</h4>
                    <p style='color: #6B7280; margin: 8px 0 0 0; font-size: 0.9em;'>Passes, dribbles, précision</p>
                </div>
                <div style='text-align: center; padding: 24px; background: rgba(245, 158, 11, 0.05); border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.1);'>
                    <div style='font-size: 2.5em; margin-bottom: 12px;'>🔄</div>
                    <h4 style='color: #F59E0B; margin: 0; font-weight: 600;'>Comparaison</h4>
                    <p style='color: #6B7280; margin: 8px 0 0 0; font-size: 0.9em;'>Radars, percentiles, benchmarks</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_error_page(self):
        """Affiche la page d'erreur moderne"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 48px; border-color: #EF4444;'>
            <h1 style='color: #EF4444; margin-bottom: 24px; font-weight: 800;'>Erreur de Chargement</h1>
            <p style='color: #6B7280; font-import streamlit as st
