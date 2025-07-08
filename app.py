
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

def format_market_value(value):
    """
    Formate une valeur marchande avec des sigles comme 'M' ou 'K' et le symbole Euro.
    
    Args:
        value: La valeur à formater (peut être int, float, ou string)
    
    Returns:
        str: La valeur formatée (ex: "17.0M€", "500.0K€", "1.2B€")
    """
    if pd.isna(value) or value is None:
        return "N/A"
    
    # Conversion en nombre si c'est une chaîne
    if isinstance(value, str):
        try:
            # Nettoyer la chaîne si elle contient déjà des caractères non numériques
            clean_value = ''.join(c for c in value if c.isdigit() or c == '.')
            if clean_value:
                value = float(clean_value)
            else:
                return "N/A"
        except (ValueError, TypeError):
            return str(value)  # Retourner la chaîne telle quelle si conversion impossible
    
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
    
    # Palette de couleurs professionnelle
    COLORS = {
        'primary': '#1f77b4',           # Bleu professionnel
        'secondary': '#2ca02c',         # Vert professionnel
        'accent': '#ff7f0e',           # Orange accent
        'success': '#17a2b8',          # Cyan
        'warning': '#ffc107',          # Jaune
        'danger': '#dc3545',           # Rouge
        'dark': '#212529',             # Gris foncé
        'light': '#f8f9fa',            # Blanc cassé
        'gradient': ['#1f77b4', '#2ca02c', '#ff7f0e', '#17a2b8', '#ffc107']
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
        """Charge les styles CSS personnalisés modernes"""
        return """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* ===== VARIABLES CSS ===== */
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #2ca02c;
            --accent-color: #ff7f0e;
            --background-dark: #0e1117;
            --background-card: #1a1d23;
            --background-surface: #262730;
            --text-primary: #fafafa;
            --text-secondary: #a6a6a6;
            --border-color: #404040;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
        }
        
        /* ===== STYLES GLOBAUX ===== */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--background-dark) 0%, #1a1d23 100%);
            color: var(--text-primary);
        }
        
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        
        /* ===== STYLES DES ONGLETS MODERNES ===== */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--background-card);
            border-radius: 12px;
            padding: 4px;
            margin-bottom: 24px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: var(--text-secondary);
            border-radius: 8px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.2s ease;
            border: none;
            padding: 12px 20px;
            margin: 0 2px;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(31, 119, 180, 0.1);
            color: var(--text-primary);
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--primary-color);
            color: white;
            box-shadow: 0 2px 8px rgba(31, 119, 180, 0.3);
            font-weight: 600;
        }
        
        /* ===== CARTES MODERNES ===== */
        .dashboard-card {
            background: var(--background-card);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
            margin: 16px 0;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .dashboard-card:hover {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }
        
        .player-header-card {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 32px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 32px;
            box-shadow: var(--shadow-lg);
            border: none;
        }
        
        .metric-card {
            background: var(--background-surface);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
            transition: all 0.2s ease;
            height: 100%;
        }
        
        .metric-card:hover {
            border-color: var(--accent-color);
            box-shadow: 0 4px 12px rgba(255, 127, 14, 0.2);
            transform: translateY(-2px);
        }
        
        .metric-card-compact {
            background: var(--background-surface);
            padding: 16px 12px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
            transition: all 0.2s ease;
            min-height: 90px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow: hidden;
        }
        
        .metric-card-compact:hover {
            border-color: var(--accent-color);
            box-shadow: 0 4px 12px rgba(255, 127, 14, 0.2);
            transform: translateY(-1px);
        }
        
        .metric-value-compact {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            line-height: 1.2;
        }
        
        .metric-label-compact {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        /* ===== CONTENEURS D'IMAGES MODERNES ===== */
        .image-container {
            background: var(--background-surface);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid var(--border-color);
            overflow: hidden;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow);
            position: relative;
        }
        
        .image-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent 49%, rgba(31, 119, 180, 0.1) 50%, transparent 51%);
            pointer-events: none;
        }
        
        .club-logo-container {
            background: var(--background-surface);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid var(--border-color);
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow);
            transition: all 0.2s ease;
        }
        
        .club-logo-container:hover {
            border-color: var(--primary-color);
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.2);
        }
        
        /* ===== STYLES DE TEXTE MODERNES ===== */
        .section-title {
            color: var(--text-primary);
            font-size: 2.25rem;
            font-weight: 800;
            text-align: center;
            margin: 32px 0 24px 0;
            letter-spacing: -0.025em;
        }
        
        .subsection-title {
            color: var(--primary-color);
            font-size: 1.5rem;
            font-weight: 600;
            margin: 24px 0 16px 0;
            border-left: 4px solid var(--primary-color);
            padding-left: 16px;
            letter-spacing: -0.025em;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            line-height: 1;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }
        
        /* ===== SIDEBAR MODERNE ===== */
        .sidebar-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 24px;
            border: none;
        }
        
        .sidebar .stSelectbox > div > div {
            background: var(--background-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }
        
        /* ===== FOOTER MODERNE ===== */
        .dashboard-footer {
            background: var(--background-card);
            padding: 24px;
            border-radius: 12px;
            text-align: center;
            margin-top: 40px;
            border: 1px solid var(--border-color);
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
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .animated-card {
            animation: fadeInUp 0.6s ease-out;
        }
        
        .slide-in {
            animation: slideIn 0.4s ease-out;
        }
        
        /* ===== SCROLLBAR MODERNE ===== */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--background-dark);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-color);
        }
        
        /* ===== RESPONSIVE DESIGN ===== */
        @media (max-width: 768px) {
            .dashboard-card {
                padding: 16px;
                margin: 12px 0;
            }
            
            .section-title {
                font-size: 1.875rem;
            }
            
            .subsection-title {
                font-size: 1.25rem;
            }
            
            .metric-card-compact {
                padding: 12px 8px;
                min-height: 80px;
            }
            
            .metric-value-compact {
                font-size: 1.25rem;
            }
            
            .metric-label-compact {
                font-size: 0.7rem;
            }
        }
        
        @media (max-width: 480px) {
            .metric-card-compact {
                padding: 8px 4px;
                min-height: 70px;
            }
            
            .metric-value-compact {
                font-size: 1.125rem;
            }
            
            .metric-label-compact {
                font-size: 0.65rem;
            }
        }
        
        /* ===== NOUVELLES FONCTIONNALITÉS STREAMLIT ===== */
        .stMetric {
            background: var(--background-surface);
            padding: 16px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .stAlert {
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        .stButton > button {
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background: var(--secondary-color);
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(31, 119, 180, 0.3);
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
# COMPOSANTS UI MODERNES
# ================================================================================================

class UIComponents:
    """Composants d'interface utilisateur réutilisables modernes"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête principal moderne"""
        st.markdown("""
        <div class='player-header-card animated-card'>
            <h1 style='color: white; margin: 0; font-size: 3.5em; font-weight: 800; letter-spacing: -0.02em;'>
                Dashboard Football Professionnel
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 16px 0 0 0; font-size: 1.25em; font-weight: 500;'>
                Analyse avancée des performances - Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_header():
        """Affiche l'en-tête de la sidebar moderne"""
        st.markdown("""
        <div class='sidebar-header'>
            <h2 style='color: white; margin: 0; font-weight: 700; font-size: 1.5em;'>Configuration</h2>
            <p style='color: rgba(255,255,255,0.8); margin: 8px 0 0 0; font-size: 0.9em;'>
                Sélectionnez votre joueur
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte complète du joueur avec design moderne"""
        # Layout responsive avec containers
        container = st.container()
        
        with container:
            col1, col2, col3 = st.columns([1, 2.5, 1], gap="large")
            
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
                <p style='text-align: center; color: var(--primary-color); font-weight: 600; margin-top: 12px; font-size: 0.9em;'>
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
                <p style='text-align: center; color: var(--primary-color); font-weight: 600; margin-top: 12px; font-size: 0.9em;'>
                    {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_logo_placeholder(team_name)
        else:
            UIComponents._render_logo_placeholder(team_name)
    
    @staticmethod
    def _render_player_info_modern(player_data: pd.Series):
        """Affiche les informations centrales du joueur avec design moderne"""
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
            <h2 class='section-title' style='margin-bottom: 32px; font-size: 2.5em; color: var(--text-primary);'>
                {player_data['Joueur']}
            </h2>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; margin-top: 24px;'>
                <div class='metric-card-compact slide-in'>
                    <div class='metric-value-compact'>{player_data['Âge']}</div>
                    <div class='metric-label-compact'>Âge</div>
                </div>
                <div class='metric-card-compact slide-in' style='animation-delay: 0.1s;'>
                    <div class='metric-value-compact' title='{player_data['Position']}'>{position_display}</div>
                    <div class='metric-label-compact'>Position</div>
                </div>
                <div class='metric-card-compact slide-in' style='animation-delay: 0.2s;'>
                    <div class='metric-value-compact' title='{player_data['Nationalité']}'>{nationalite_display}</div>
                    <div class='metric-label-compact'>Nationalité</div>
                </div>
                <div class='metric-card-compact slide-in' style='animation-delay: 0.3s;'>
                    <div class='metric-value-compact'>{int(player_data['Minutes jouées'])}</div>
                    <div class='metric-label-compact'>Minutes</div>
                </div>
                <div class='metric-card-compact slide-in' style='animation-delay: 0.4s;'>
                    <div class='metric-value-compact' style='color: var(--accent-color);'>{valeur_marchande}</div>
                    <div class='metric-label-compact'>Val. Marchande</div>
                </div>
                <div class='metric-card-compact slide-in' style='animation-delay: 0.5s;'>
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
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 4em; margin-bottom: 12px; opacity: 0.5;'>👤</div>
                <p style='margin: 0; font-size: 0.9em;'>Photo non disponible</p>
                <p style='font-size: 0.8em; margin-top: 8px; color: var(--primary-color);'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder(team_name: str):
        """Affiche un placeholder moderne pour le logo"""
        st.markdown(f"""
        <div class='club-logo-container animated-card'>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 3em; margin-bottom: 12px; opacity: 0.5;'>🏟️</div>
                <p style='margin: 0; font-size: 0.8em;'>Logo non disponible</p>
                <p style='font-size: 0.75em; margin-top: 6px; color: var(--primary-color);'>{team_name}</p>
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
        """Affiche le footer moderne"""
        st.markdown("""
        <div class='dashboard-footer animated-card'>
            <h3 style='color: var(--primary-color); margin: 0 0 16px 0; font-weight: 700; font-size: 1.25em;'>
                Dashboard Football Professionnel
            </h3>
            <p style='color: var(--text-primary); margin: 0; font-size: 1.1em; font-weight: 500;'>
                Analyse avancée des performances footballistiques
            </p>
            <p style='color: var(--text-secondary); margin: 12px 0 0 0; font-size: 0.9em;'>
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
# GESTIONNAIRE DE GRAPHIQUES MODERNES
# ================================================================================================

class ChartManager:
    """Gestionnaire centralisé pour les graphiques modernes"""
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], title: str, color_palette: List[str]) -> go.Figure:
        """Crée un graphique en barres stylé moderne"""
        fig = go.Figure(data=[go.Bar(
            x=list(data.keys()),
            y=list(data.values()),
            marker=dict(
                color=color_palette,
                line=dict(color='rgba(255,255,255,0.2)', width=1),
                cornerradius=4
            ),
            text=[f"{v:.1f}" for v in data.values()],
            textposition='outside',
            textfont=dict(color='white', size=13, family='Inter')
        )])
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, color='white', family='Inter', weight=600),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                tickfont=dict(color='white', size=11, family='Inter'),
                tickangle=45,
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=False
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=11, family='Inter'),
                gridcolor='rgba(255,255,255,0.15)',
                showgrid=True,
                gridwidth=1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            height=400,
            margin=dict(t=60, b=80, l=60, r=60)
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(data: Dict[str, float], title: str) -> go.Figure:
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
                        axis=dict(range=[0, 100], tickcolor='white', tickfont=dict(size=10)),
                        bar=dict(color=color, thickness=0.7),
                        bgcolor="rgba(26, 29, 35, 0.8)",
                        borderwidth=2,
                        bordercolor="rgba(255,255,255,0.3)",
                        steps=[
                            {'range': [0, 33], 'color': 'rgba(255,255,255,0.05)'},
                            {'range': [33, 66], 'color': 'rgba(255,255,255,0.1)'},
                            {'range': [66, 100], 'color': 'rgba(255,255,255,0.15)'}
                        ],
                        threshold={
                            'line': {'color': "white", 'width': 3},
                            'thickness': 0.75,
                            'value': 80
                        }
                    ),
                    number={
                        'suffix': '%', 
                        'font': {'color': 'white', 'size': 14, 'family': 'Inter', 'weight': 600}
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            height=320,
            title_text=title,
            title_font_color='white',
            title_font_size=16,
            title_font_family='Inter',
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter', size=10),
            margin=dict(t=60, b=40, l=40, r=40)
        )
        
        return fig
    
    @staticmethod
    def create_comparison_chart(player_data: Dict[str, float], avg_data: Dict[str, float], 
                              player_name: str, title: str) -> go.Figure:
        """Crée un graphique de comparaison moderne"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=player_name,
            x=list(player_data.keys()),
            y=list(player_data.values()),
            marker_color=AppConfig.COLORS['primary'],
            marker_line=dict(color='rgba(255,255,255,0.2)', width=1),
            text=[f"{v:.2f}" for v in player_data.values()],
            textposition='outside',
            textfont=dict(size=11)
        ))
        
        fig.add_trace(go.Bar(
            name='Moyenne compétition',
            x=list(avg_data.keys()),
            y=list(avg_data.values()),
            marker_color=AppConfig.COLORS['secondary'],
            marker_line=dict(color='rgba(255,255,255,0.2)', width=1),
            text=[f"{v:.2f}" for v in avg_data.values()],
            textposition='outside',
            textfont=dict(size=11)
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color='white', size=16, family='Inter', weight=600),
                x=0.5
            ),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            xaxis=dict(
                tickfont=dict(color='white', size=11),
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=False
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=11), 
                gridcolor='rgba(255,255,255,0.15)',
                showgrid=True
            ),
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            ),
            margin=dict(t=80, b=60, l=60, r=60)
        )
        
        return fig
    
    @staticmethod
    def create_radar_chart(metrics: Dict[str, float], percentiles: List[float], 
                          avg_percentiles: List[float], player_name: str, 
                          competition: str, color: str) -> go.Figure:
        """Crée un radar chart professionnel moderne"""
        fig = go.Figure()
        
        # Performance du joueur
        fig.add_trace(go.Scatterpolar(
            r=percentiles,
            theta=list(metrics.keys()),
            fill='toself',
            fillcolor=f'rgba({ChartManager._hex_to_rgb(color)}, 0.25)',
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
            line=dict(color='rgba(255,255,255,0.6)', width=2, dash='dash'),
            name=f'Moyenne {competition}',
            showlegend=True,
            hovertemplate='<b>%{theta}</b><br>Moyenne: %{r:.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(255,255,255,0.2)',
                    tickcolor='white',
                    tickfont=dict(color='white', size=10, family='Inter'),
                    showticklabels=True,
                    tickmode='linear',
                    tick0=0,
                    dtick=20
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.2)',
                    tickcolor='white',
                    tickfont=dict(color='white', size=11, family='Inter', weight=500),
                    linecolor='rgba(255,255,255,0.3)'
                ),
                bgcolor='rgba(26, 29, 35, 0.8)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            title=dict(
                text=f"Radar Professionnel - {player_name}",
                font=dict(size=18, color='white', family='Inter', weight=700),
                x=0.5,
                y=0.95
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color='white', size=11)
            ),
            height=480,
            margin=dict(t=80, b=80, l=80, r=80)
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
# GESTIONNAIRE DE TABS MODERNES
# ================================================================================================

class TabManager:
    """Gestionnaire pour les différents onglets avec design moderne"""
    
    @staticmethod
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu moderne de l'onglet performance offensive"""
        st.markdown("<h2 class='section-title'>Performance Offensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_offensive_performance(player_data, df_comparison)
        
        # Layout moderne avec espacement optimal
        col1, col2 = st.columns([1, 1], gap="large")
        
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
            
            # Métriques avec st.metric moderne
            st.markdown("<h3 class='subsection-title'>Métriques Clés</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Buts par 90min",
                    value=f"{analysis['metrics']['Buts/90']:.2f}",
                    delta=f"{analysis['metrics']['Buts/90'] - analysis['avg_metrics']['Buts/90']:.2f}"
                )
                st.metric(
                    label="xG par 90min",
                    value=f"{analysis['metrics']['xG/90']:.2f}",
                    delta=f"{analysis['metrics']['xG/90'] - analysis['avg_metrics']['xG/90']:.2f}"
                )
            
            with metric_col2:
                st.metric(
                    label="Passes D. par 90min",
                    value=f"{analysis['metrics']['Passes D./90']:.2f}",
                    delta=f"{analysis['metrics']['Passes D./90'] - analysis['avg_metrics']['Passes D./90']:.2f}"
                )
                st.metric(
                    label="xA par 90min",
                    value=f"{analysis['metrics']['xA/90']:.2f}",
                    delta=f"{analysis['metrics']['xA/90'] - analysis['avg_metrics']['xA/90']:.2f}"
                )
        
        with col2:
            # Jauges de pourcentages
            efficiency_data = {
                'Conversion': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                'Efficacité passes': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(efficiency_data, "Efficacité Offensive")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar offensif
            st.markdown("<h3 class='subsection-title'>Radar Offensif</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
                AppConfig.COLORS['primary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison détaillée en bas
        st.markdown("---")
        st.markdown("<h3 class='subsection-title'>Comparaison par 90min vs Moyenne</h3>", unsafe_allow_html=True)
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "Performance par 90min vs Moyenne"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu moderne de l'onglet performance défensive"""
        st.markdown("<h2 class='section-title'>Performance Défensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_defensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
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
            
            # Métriques défensives
            st.markdown("<h3 class='subsection-title'>Métriques Défensives</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Tacles par 90min",
                    value=f"{analysis['metrics']['Tacles/90']:.2f}",
                    delta=f"{analysis['metrics']['Tacles/90'] - analysis['avg_metrics']['Tacles/90']:.2f}"
                )
                st.metric(
                    label="Interceptions par 90min",
                    value=f"{analysis['metrics']['Interceptions/90']:.2f}",
                    delta=f"{analysis['metrics']['Interceptions/90'] - analysis['avg_metrics']['Interceptions/90']:.2f}"
                )
            
            with metric_col2:
                st.metric(
                    label="% Duels gagnés",
                    value=f"{analysis['metrics']['% Duels gagnés']:.1f}%",
                    delta=f"{analysis['metrics']['% Duels gagnés'] - analysis['avg_metrics']['% Duels gagnés']:.1f}%"
                )
                st.metric(
                    label="% Duels aériens",
                    value=f"{analysis['metrics']['% Duels aériens']:.1f}%",
                    delta=f"{analysis['metrics']['% Duels aériens'] - analysis['avg_metrics']['% Duels aériens']:.1f}%"
                )
        
        with col2:
            # Pourcentages de réussite
            success_data = {
                'Duels défensifs': player_data.get('Pourcentage de duels gagnés', 0),
                'Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                'Passes': player_data['Pourcentage de passes réussies']
            }
            
            fig_gauge = ChartManager.create_gauge_chart(success_data, "Pourcentages de Réussite")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar défensif
            st.markdown("<h3 class='subsection-title'>Radar Défensif</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
                AppConfig.COLORS['accent']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison défensive
        st.markdown("---")
        st.markdown("<h3 class='subsection-title'>Comparaison Défensive</h3>", unsafe_allow_html=True)
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "Défense par 90min vs Moyenne"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_technical_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu moderne de l'onglet performance technique"""
        st.markdown("<h2 class='section-title'>Performance Technique</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_technical_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
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
            
            # Métriques techniques
            st.markdown("<h3 class='subsection-title'>Métriques Techniques</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Passes par 90min",
                    value=f"{analysis['metrics']['Passes tentées/90']:.1f}",
                    delta=f"{analysis['metrics']['Passes tentées/90'] - analysis['avg_metrics']['Passes tentées/90']:.1f}"
                )
                st.metric(
                    label="Touches par 90min",
                    value=f"{analysis['metrics']['Touches/90']:.1f}",
                    delta=f"{analysis['metrics']['Touches/90'] - analysis['avg_metrics']['Touches/90']:.1f}"
                )
            
            with metric_col2:
                st.metric(
                    label="% Passes réussies",
                    value=f"{analysis['metrics']['% Passes réussies']:.1f}%",
                    delta=f"{analysis['metrics']['% Passes réussies'] - analysis['avg_metrics']['% Passes réussies']:.1f}%"
                )
                st.metric(
                    label="% Dribbles réussis",
                    value=f"{analysis['metrics']['% Dribbles réussis']:.1f}%",
                    delta=f"{analysis['metrics']['% Dribbles réussis'] - analysis['avg_metrics']['% Dribbles réussis']:.1f}%"
                )
        
        with col2:
            # Pourcentages techniques
            technical_success = {
                'Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
            }
            
            fig_gauge = ChartManager.create_gauge_chart(technical_success, "Précision Technique")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar technique
            st.markdown("<h3 class='subsection-title'>Radar Technique</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
                AppConfig.COLORS['secondary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison technique
        st.markdown("---")
        st.markdown("<h3 class='subsection-title'>Comparaison Technique</h3>", unsafe_allow_html=True)
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "Technique par 90min vs Moyenne"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_comparison_tab(df: pd.DataFrame, selected_player: str):
        """Rendu moderne de l'onglet comparaison"""
        st.markdown("<h2 class='section-title'>Comparaison Pizza Chart</h2>", unsafe_allow_html=True)
        
        # Mode de visualisation avec style moderne
        mode = st.radio(
            "Mode de visualisation",
            ["Radar individuel", "Radar comparatif"],
            horizontal=True,
            help="Choisissez le type d'analyse radar à afficher"
        )
        
        competitions = sorted(df['Compétition'].dropna().unique())
        
        if mode == "Radar individuel":
            TabManager._render_individual_radar(df, selected_player, competitions)
        else:
            TabManager._render_comparative_radar(df, competitions)
    
    @staticmethod
    def _render_individual_radar(df: pd.DataFrame, selected_player: str, competitions: List[str]):
        """Rendu moderne du radar individuel"""
        st.markdown(f"<h3 class='subsection-title'>Radar individuel : {selected_player}</h3>", unsafe_allow_html=True)
        
        try:
            # Sélection de la compétition avec style moderne
            col1, col2 = st.columns([2, 1])
            
            with col1:
                competition = st.selectbox(
                    "Compétition de référence", 
                    competitions,
                    help="Sélectionnez la compétition pour le calcul des percentiles"
                )
            
            with col2:
                st.info(f"📊 Analyse basée sur {competition}")
            
            df_comp = df[df['Compétition'] == competition]
            
            values = MetricsCalculator.calculate_percentiles(selected_player, df_comp)
            
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            baker = PyPizza(
                params=list(AppConfig.RAW_STATS.keys()),
                background_color="#0e1117",
                straight_line_color="#FFFFFF",
                straight_line_lw=1,
                last_circle_color="#FFFFFF",
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
                kwargs_slices=dict(edgecolor="#FFFFFF", zorder=2, linewidth=2),
                kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop),
                kwargs_values=dict(
                    color="#ffffff", 
                    fontsize=11, 
                    fontproperties=font_normal.prop,
                    bbox=dict(
                        edgecolor="#FFFFFF", 
                        facecolor=AppConfig.COLORS['primary'], 
                        boxstyle="round,pad=0.3", 
                        lw=1.5
                    )
                )
            )
            
            # Titre moderne
            fig.text(0.515, 0.97, selected_player, size=28, ha="center", 
                    fontproperties=font_bold.prop, color="#ffffff", weight='bold')
            fig.text(0.515, 0.94, f"Radar Individuel | Percentiles vs {competition} | Saison 2024-25", 
                    size=14, ha="center", fontproperties=font_bold.prop, color="#a6a6a6")
            
            # Footer moderne
            fig.text(0.99, 0.01, "Dashboard Football Pro | Données: FBRef", 
                    size=9, ha="right", fontproperties=font_italic.prop, color="#a6a6a6")
            
            st.pyplot(fig, use_container_width=True)
            
            # Statistiques du radar
            st.markdown("---")
            
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                avg_percentile = np.mean(values)
                st.metric("Percentile Moyen", f"{avg_percentile:.1f}%")
            
            with stats_col2:
                max_stat = max(values)
                max_index = values.index(max_stat)
                max_param = list(AppConfig.RAW_STATS.keys())[max_index]
                st.metric("Point Fort", f"{max_param.replace('\\n', ' ')}", f"{max_stat}%")
            
            with stats_col3:
                min_stat = min(values)
                min_index = values.index(min_stat)
                min_param = list(AppConfig.RAW_STATS.keys())[min_index]
                st.metric("Axe d'Amélioration", f"{min_param.replace('\\n', ' ')}", f"{min_stat}%")
            
        except Exception as e:
            st.error(f"Erreur lors de la création du radar individuel : {str(e)}")
    
    @staticmethod
    def _render_comparative_radar(df: pd.DataFrame, competitions: List[str]):
        """Rendu moderne du radar comparatif"""
        # Interface de sélection améliorée
        st.markdown("<h3 class='subsection-title'>Configuration de la Comparaison</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("**👤 Joueur 1**")
            ligue1 = st.selectbox("Compétition", competitions, key="ligue1_comp")
            df_j1 = df[df['Compétition'] == ligue1]
            joueur1 = st.selectbox("Joueur", df_j1['Joueur'].sort_values(), key="joueur1_comp")
        
        with col2:
            st.markdown("**👤 Joueur 2**")
            ligue2 = st.selectbox("Compétition", competitions, key="ligue2_comp")
            df_j2 = df[df['Compétition'] == ligue2]
            joueur2 = st.selectbox("Joueur", df_j2['Joueur'].sort_values(), key="joueur2_comp")
        
        if joueur1 and joueur2:
            st.markdown(f"<h3 class='subsection-title'>{joueur1} vs {joueur2}</h3>", unsafe_allow_html=True)
            
            # Informations sur les joueurs
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                player1_data = df_j1[df_j1['Joueur'] == joueur1].iloc[0]
                st.info(f"🏆 {ligue1} | ⚽ {player1_data['Équipe']} | 📍 {player1_data['Position']}")
            
            with info_col2:
                player2_data = df_j2[df_j2['Joueur'] == joueur2].iloc[0]
                st.info(f"🏆 {ligue2} | ⚽ {player2_data['Équipe']} | 📍 {player2_data['Position']}")
            
            try:
                values1 = MetricsCalculator.calculate_percentiles(joueur1, df_j1)
                values2 = MetricsCalculator.calculate_percentiles(joueur2, df_j2)
                
                font_normal = FontManager()
                font_bold = FontManager()
                font_italic = FontManager()
                
                baker = PyPizza(
                    params=list(AppConfig.RAW_STATS.keys()),
                    background_color="#0e1117",
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
                    figsize=(14, 14),
                    kwargs_slices=dict(
                        facecolor=AppConfig.COLORS['primary'], 
                        edgecolor="#FFFFFF", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_compare=dict(
                        facecolor=AppConfig.COLORS['secondary'], 
                        edgecolor="#FFFFFF", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_params=dict(
                        color="#ffffff", 
                        fontsize=13, 
                        fontproperties=font_bold.prop
                    ),
                    kwargs_values=dict(
                        color="#ffffff", 
                        fontsize=11, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        bbox=dict(
                            edgecolor="#FFFFFF", 
                            facecolor=AppConfig.COLORS['primary'], 
                            boxstyle="round,pad=0.3", 
                            lw=1.5
                        )
                    ),
                    kwargs_compare_values=dict(
                        color="#ffffff", 
                        fontsize=11, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        bbox=dict(
                            edgecolor="#FFFFFF", 
                            facecolor=AppConfig.COLORS['secondary'], 
                            boxstyle="round,pad=0.3", 
                            lw=1.5
                        )
                    )
                )
                
                # Titre moderne
                fig.text(0.515, 0.97, "Radar Comparatif | Percentiles | Saison 2024-25",
                         size=16, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                
                # Légende moderne
                legend_p1 = mpatches.Patch(color=AppConfig.COLORS['primary'], label=joueur1)
                legend_p2 = mpatches.Patch(color=AppConfig.COLORS['secondary'], label=joueur2)
                ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0),
                         frameon=False, labelcolor='white')
                
                # Footer moderne
                fig.text(0.99, 0.01, "Dashboard Football Pro | Source: FBRef",
                         size=9, ha="right", fontproperties=font_italic.prop, color="#a6a6a6")
                
                st.pyplot(fig, use_container_width=True)
                
                # Comparaison statistique
                st.markdown("---")
                st.markdown("<h3 class='subsection-title'>Comparaison Statistique</h3>", unsafe_allow_html=True)
                
                comp_col1, comp_col2, comp_col3 = st.columns(3)
                
                with comp_col1:
                    avg1 = np.mean(values1)
                    avg2 = np.mean(values2)
                    winner = joueur1 if avg1 > avg2 else joueur2
                    st.metric("Meilleur Percentile Moyen", winner, f"{max(avg1, avg2):.1f}%")
                
                with comp_col2:
                    superior_count = sum(1 for v1, v2 in zip(values1, values2) if v1 > v2)
                    st.metric(f"{joueur1} supérieur sur", f"{superior_count}", f"/ {len(values1)} métriques")
                
                with comp_col3:
                    superior_count2 = len(values1) - superior_count
                    st.metric(f"{joueur2} supérieur sur", f"{superior_count2}", f"/ {len(values1)} métriques")
                
            except Exception as e:
                st.error(f"Erreur lors de la création du radar comparatif : {str(e)}")

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
# GESTIONNAIRE DE SIDEBAR MODERNE
# ================================================================================================

class SidebarManager:
    """Gestionnaire moderne pour la sidebar"""
    
    @staticmethod
    def render_sidebar(df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
        """Rendu moderne complet de la sidebar"""
        with st.sidebar:
            UIComponents.render_sidebar_header()
            
            # Sélection de la compétition avec style moderne
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
            
            # Filtre par minutes jouées avec design moderne
            SidebarManager._render_minutes_filter_modern(df_filtered)
            
            # Application du filtre minutes
            min_minutes_filter = st.session_state.get('min_minutes_filter', 0)
            df_filtered_minutes = DataManager.filter_data_by_minutes(df_filtered, min_minutes_filter)
            
            # Informations sur le filtrage avec style moderne
            SidebarManager._render_filter_info_modern(df_filtered_minutes)
            
            st.markdown("---")
            
            # Sélection du joueur
            selected_player = SidebarManager._render_player_selection_modern(df_filtered_minutes)
            
            # Informations additionnelles modernes
            SidebarManager._render_sidebar_footer_modern()
            
            return selected_competition, selected_player, df_filtered_minutes
    
    @staticmethod
    def _render_minutes_filter_modern(df_filtered: pd.DataFrame):
        """Rendu moderne du filtre par minutes"""
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
            
            # Indicateur visuel moderne
            percentage_filtered = (min_minutes_filter - min_minutes) / (max_minutes - min_minutes) * 100
            st.progress(percentage_filtered / 100)
    
    @staticmethod
    def _render_filter_info_modern(df_filtered: pd.DataFrame):
        """Affiche les informations de filtrage avec style moderne"""
        nb_joueurs = len(df_filtered)
        
        if nb_joueurs > 0:
            st.success(f"✅ **{nb_joueurs} joueurs** correspondent aux critères")
            
            # Statistiques additionnelles
            with st.expander("📊 Statistiques du filtrage", expanded=False):
                avg_minutes = df_filtered['Minutes jouées'].mean()
                st.write(f"• Moyenne minutes: {avg_minutes:.0f}")
                st.write(f"• Équipes représentées: {df_filtered['Équipe'].nunique()}")
                st.write(f"• Positions: {df_filtered['Position'].nunique()}")
        else:
            st.warning("⚠️ Aucun joueur ne correspond aux critères")
    
    @staticmethod
    def _render_player_selection_modern(df_filtered: pd.DataFrame) -> Optional[str]:
        """Rendu moderne de la sélection de joueur"""
        if not df_filtered.empty:
            joueurs = DataManager.get_players(df_filtered)
            if joueurs:
                # Option de recherche
                search_term = st.text_input("🔍 Rechercher un joueur :", placeholder="Tapez le nom du joueur...")
                
                if search_term:
                    joueurs_filtered = [j for j in joueurs if search_term.lower() in j.lower()]
                    if joueurs_filtered:
                        selected_player = st.selectbox(
                            "👤 Joueurs trouvés :",
                            joueurs_filtered,
                            help="Sélectionnez le joueur à analyser"
                        )
                    else:
                        st.warning(f"Aucun joueur trouvé pour '{search_term}'")
                        selected_player = st.selectbox(
                            "👤 Tous les joueurs :",
                            joueurs,
                            help="Sélectionnez le joueur à analyser"
                        )
                else:
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
        """Rendu moderne du footer de la sidebar"""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 16px; background: var(--background-surface); border-radius: 12px; border: 1px solid var(--border-color);'>
            <p style='color: var(--text-primary); margin: 0; font-size: 0.9em; font-weight: 600;'>
                📊 Dashboard Pro
            </p>
            <p style='color: var(--text-secondary); margin: 8px 0 0 0; font-size: 0.8em;'>
                Analyse Football Avancée
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# APPLICATION PRINCIPALE MODERNE
# ================================================================================================

class FootballDashboard:
    """Classe principale de l'application Dashboard Football moderne"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self._configure_page()
        self._load_styles()
        self._initialize_session_state()
    
    def _configure_page(self):
        """Configuration moderne de la page Streamlit"""
        st.set_page_config(**AppConfig.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS modernes"""
        st.markdown(StyleManager.load_custom_css(), unsafe_allow_html=True)
    
    def _initialize_session_state(self):
        """Initialise les variables de session"""
        if 'selected_player_history' not in st.session_state:
            st.session_state.selected_player_history = []
        if 'last_competition' not in st.session_state:
            st.session_state.last_competition = None
    
    def run(self):
        """Méthode principale d'exécution de l'application"""
        # Chargement des données avec indication de progression
        with st.spinner("Chargement des données..."):
            df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        # Affichage des statistiques générales en en-tête
        self._render_data_overview(df)
        
        # Rendu de l'en-tête principal
        UIComponents.render_header()
        
        # Rendu de la sidebar et récupération des sélections
        selected_competition, selected_player, df_filtered = SidebarManager.render_sidebar(df)
        
        # Mise à jour de l'historique
        self._update_player_history(selected_player)
        
        if selected_player:
            # Récupération des données du joueur
            player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
            
            # Affichage de la carte du joueur avec fond d'équipe
            self._render_team_background(player_data, selected_competition)
            UIComponents.render_player_card(player_data, selected_competition)
            
            st.markdown("---")
            
            # Onglets principaux avec style moderne
            self._render_main_tabs(player_data, df_filtered, selected_player, df)
        
        else:
            self._render_no_player_message()
        
        # Footer moderne
        UIComponents.render_footer()
    
    def _render_data_overview(self, df: pd.DataFrame):
        """Affiche un aperçu moderne des données"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Joueurs Total", f"{len(df):,}")
        
        with col2:
            st.metric("Compétitions", f"{df['Compétition'].nunique()}")
        
        with col3:
            st.metric("Équipes", f"{df['Équipe'].nunique()}")
        
        with col4:
            total_minutes = df['Minutes jouées'].sum()
            st.metric("Minutes Totales", f"{total_minutes:,.0f}")
        
        with col5:
            avg_age = df['Âge'].mean()
            st.metric("Âge Moyen", f"{avg_age:.1f} ans")
    
    def _render_team_background(self, player_data: pd.Series, competition: str):
        """Affiche le fond avec le logo de l'équipe"""
        logo_path = ImageManager.get_club_logo(competition, player_data['Équipe'])
        
        if logo_path:
            try:
                image = Image.open(logo_path)
                # Créer un effet de fond subtil avec le logo
                st.markdown(f"""
                <div style='
                    position: relative;
                    background: linear-gradient(
                        rgba(14, 17, 23, 0.85), 
                        rgba(14, 17, 23, 0.85)
                    ), 
                    url("data:image/jpeg;base64,{UIComponents._image_to_base64(image)}");
                    background-size: contain;
                    background-repeat: no-repeat;
                    background-position: center;
                    background-attachment: fixed;
                    min-height: 200px;
                    border-radius: 16px;
                    margin: 16px 0;
                    opacity: 0.3;
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    z-index: -1;
                '>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                pass  # Si le logo ne peut pas être chargé, on continue sans fond
    
    def _update_player_history(self, selected_player: str):
        """Met à jour l'historique des joueurs sélectionnés"""
        if selected_player and selected_player not in st.session_state.selected_player_history:
            st.session_state.selected_player_history.insert(0, selected_player)
            # Garder seulement les 5 derniers
            st.session_state.selected_player_history = st.session_state.selected_player_history[:5]
    
    def _render_main_tabs(self, player_data: pd.Series, df_filtered: pd.DataFrame, 
                         selected_player: str, df_full: pd.DataFrame):
        """Rendu moderne des onglets principaux"""
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
            <h2 style='color: var(--primary-color); margin-bottom: 24px; font-size: 2em;'>⚠️ Aucun joueur sélectionné</h2>
            <p style='color: var(--text-primary); font-size: 1.2em; margin-bottom: 32px; line-height: 1.6;'>
                Veuillez ajuster les filtres dans la sidebar pour sélectionner un joueur à analyser.
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px; margin-top: 32px;'>
                <div class='metric-card' style='padding: 24px;'>
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--primary-color);'>🎯</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Analyse Offensive</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Buts, passes décisives, xG</p>
                </div>
                <div class='metric-card' style='padding: 24px;'>
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--accent-color);'>🛡️</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Analyse Défensive</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Tacles, interceptions, duels</p>
                </div>
                <div class='metric-card' style='padding: 24px;'>
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--secondary-color);'>🎨</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Analyse Technique</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Passes, dribbles, touches</p>
                </div>
                <div class='metric-card' style='padding: 24px;'>
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--warning);'>🔄</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Comparaison</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Radars et benchmarks</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Historique des joueurs consultés
        if st.session_state.selected_player_history:
            st.markdown("<h3 class='subsection-title'>📚 Joueurs récemment consultés</h3>", unsafe_allow_html=True)
            
            history_cols = st.columns(min(len(st.session_state.selected_player_history), 5))
            for i, player in enumerate(st.session_state.selected_player_history):
                with history_cols[i]:
                    if st.button(f"🔄 {player}", key=f"history_{i}", use_container_width=True):
                        st.rerun()
    
    def _render_error_page(self):
        """Affiche la page d'erreur moderne"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 48px; border-color: var(--danger);'>
            <h1 style='color: var(--danger); margin-bottom: 24px; font-size: 2.5em;'>⚠️ Erreur de Chargement</h1>
            <p style='color: var(--text-primary); font-size: 1.2em; margin-bottom: 32px; line-height: 1.6;'>
                Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
            </p>
            <div class='dashboard-card' style='max-width: 600px; margin: 32px auto 0 auto; padding: 24px;'>
                <h3 style='color: var(--secondary-color); margin-bottom: 16px; font-size: 1.3em;'>📋 Fichiers requis :</h3>
                <div style='text-align: left; color: var(--text-primary);'>
                    <div style='padding: 8px 0; border-bottom: 1px solid var(--border-color);'>
                        <strong>df_BIG2025.csv</strong> - Données principales des joueurs
                    </div>
                    <div style='padding: 8px 0; border-bottom: 1px solid var(--border-color);'>
                        <strong>images_joueurs/</strong> - Dossier des photos des joueurs
                    </div>
                    <div style='padding: 8px 0;'>
                        <strong>*_Logos/</strong> - Dossiers des logos par compétition
                    </div>
                </div>
            </div>
            <div style='margin-top: 32px;'>
                <button onclick='window.location.reload()' style='
                    background: var(--primary-color);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 1em;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s ease;
                ' onmouseover='this.style.background="var(--secondary-color)"' onmouseout='this.style.background="var(--primary-color)"'>
                    🔄 Réessayer
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# FONCTIONS UTILITAIRES MODERNES
# ================================================================================================

class ModernUtils:
    """Utilitaires modernes pour l'application"""
    
    @staticmethod
    def create_notification(message: str, type: str = "info"):
        """Crée une notification moderne"""
        colors = {
            "info": "var(--primary-color)",
            "success": "var(--secondary-color)",
            "warning": "var(--warning)",
            "error": "var(--danger)"
        }
        
        icons = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌"
        }
        
        st.markdown(f"""
        <div style='
            background: {colors.get(type, colors["info"])};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            margin: 8px 0;
            font-weight: 500;
            box-shadow: var(--shadow);
        '>
            {icons.get(type, icons["info"])} {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_progress_bar(value: float, max_value: float = 100, label: str = ""):
        """Crée une barre de progression moderne"""
        percentage = (value / max_value) * 100
        
        st.markdown(f"""
        <div style='margin: 16px 0;'>
            {f"<label style='color: var(--text-primary); font-weight: 500; margin-bottom: 8px; display: block;'>{label}</label>" if label else ""}
            <div style='
                background: var(--background-surface);
                border-radius: 8px;
                height: 8px;
                overflow: hidden;
                border: 1px solid var(--border-color);
            '>
                <div style='
                    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
                    height: 100%;
                    width: {percentage}%;
                    transition: width 0.3s ease;
                    border-radius: 7px;
                '></div>
            </div>
            <div style='
                display: flex;
                justify-content: space-between;
                font-size: 0.8em;
                color: var(--text-secondary);
                margin-top: 4px;
            '>
                <span>{value:.1f}</span>
                <span>{percentage:.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# ================================================================================================

def main():
    """Point d'entrée principal de l'application moderne"""
    try:
        dashboard = FootballDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Erreur inattendue : {str(e)}")
        ModernUtils.create_notification(
            "Une erreur est survenue. Veuillez recharger la page.", 
            "error"
        )

# Exécution de l'application
if __name__ == "__main__":
    main()
