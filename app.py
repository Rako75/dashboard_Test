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
import base64

# ================================================================================================
# CONFIGURATION DE L'APPLICATION
# ================================================================================================

def format_market_value(value):
    """
    Formate une valeur marchande avec des sigles comme 'M' ou 'K' et le symbole Euro.
    """
    if pd.isna(value) or value is None:
        return "N/A"
    
    if isinstance(value, str):
        try:
            clean_value = ''.join(c for c in value if c.isdigit() or c == '.')
            if clean_value:
                value = float(clean_value)
            else:
                return "N/A"
        except (ValueError, TypeError):
            return str(value)
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "N/A"
    
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f}B€"
    elif value >= 1_000_000:
        return f"{value/1_000_000:.1f}M€"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K€"
    else:
        return f"{value:.0f}€"

class AppConfig:
    """Configuration centralisée de l'application"""
    
    PAGE_CONFIG = {
        "page_title": "Football Dashboard Pro",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    COLORS = {
        'primary': '#0078FF',
        'secondary': '#1E40AF',
        'accent': '#3B82F6',
        'success': '#10B981',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'dark': '#111827',
        'light': '#F9FAFB',
        'gradient': ['#0078FF', '#1E40AF', '#3B82F6', '#10B981', '#F59E0B']
    }
    
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
    """Gestionnaire centralisé des styles CSS modernes"""
    
    @staticmethod
    def load_custom_css():
        """Charge les styles CSS personnalisés avec les dernières fonctionnalités"""
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        :root {
            --primary-color: #0078FF;
            --secondary-color: #1E40AF;
            --accent-color: #3B82F6;
            --success-color: #10B981;
            --warning-color: #F59E0B;
            --danger-color: #EF4444;
            --dark-color: #111827;
            --surface-color: #1F2937;
            --card-color: #374151;
            --text-primary: #F9FAFB;
            --text-secondary: #D1D5DB;
            --text-muted: #9CA3AF;
            --border-color: #4B5563;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --border-radius: 12px;
            --border-radius-lg: 16px;
        }
        
        * {
            transition: all 0.2s ease-in-out;
        }
        
        .main {
            background: linear-gradient(135deg, var(--dark-color) 0%, var(--surface-color) 100%);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, var(--dark-color) 0%, var(--surface-color) 100%);
        }
        
        .modern-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 2rem;
            border-radius: var(--border-radius-lg);
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .modern-header h1 {
            color: white;
            margin: 0;
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: -0.02em;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .modern-header p {
            color: rgba(255, 255, 255, 0.9);
            margin: 1rem 0 0 0;
            font-size: 1.2rem;
            font-weight: 500;
        }
        
        .sidebar-modern {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 1.5rem;
            border-radius: var(--border-radius-lg);
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .sidebar-modern h2 {
            color: white;
            margin: 0;
            font-weight: 800;
            font-size: 1.5rem;
        }
        
        .sidebar-modern p {
            color: rgba(255, 255, 255, 0.8);
            margin: 0.5rem 0 0 0;
            font-size: 0.9rem;
        }
        
        .modern-card {
            background: var(--card-color);
            padding: 1.5rem;
            border-radius: var(--border-radius-lg);
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
            margin: 1rem 0;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        
        .modern-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color), var(--success-color));
        }
        
        .modern-card:hover {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }
        
        .player-card {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 2rem;
            border-radius: var(--border-radius-lg);
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric-card-modern {
            background: var(--surface-color);
            padding: 1rem;
            border-radius: var(--border-radius);
            border: 1px solid var(--border-color);
            text-align: center;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        
        .metric-card-modern::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        }
        
        .metric-card-modern:hover {
            border-color: var(--accent-color);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
            transform: translateY(-1px);
        }
        
        .metric-value-modern {
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--primary-color);
            margin-bottom: 0.25rem;
            line-height: 1.2;
        }
        
        .metric-label-modern {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .image-container-modern {
            background: var(--card-color);
            border-radius: var(--border-radius-lg);
            padding: 1rem;
            border: 2px solid var(--border-color);
            overflow: hidden;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow);
            position: relative;
        }
        
        .image-container-modern::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        }
        
        .club-logo-modern {
            background: var(--card-color);
            border-radius: var(--border-radius);
            padding: 1rem;
            border: 2px solid var(--border-color);
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow);
            position: relative;
        }
        
        .club-logo-modern::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        }
        
        .section-title-modern {
            color: var(--primary-color);
            font-size: 2.5rem;
            font-weight: 900;
            text-align: center;
            margin: 2rem 0;
            letter-spacing: -0.02em;
        }
        
        .subsection-title-modern {
            color: var(--accent-color);
            font-size: 1.5rem;
            font-weight: 700;
            margin: 1.5rem 0;
            padding-left: 1rem;
            border-left: 4px solid var(--accent-color);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background: var(--surface-color);
            border-radius: var(--border-radius-lg);
            padding: 0.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: var(--text-secondary);
            border-radius: var(--border-radius);
            font-weight: 600;
            font-size: 0.9rem;
            padding: 0.75rem 1.5rem;
            border: none;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(0, 120, 255, 0.3);
        }
        
        .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
            background: rgba(59, 130, 246, 0.1);
            color: var(--text-primary);
        }
        
        .stSelectbox > div > div > div {
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: var(--border-radius);
        }
        
        .stSlider > div > div > div > div {
            background: var(--primary-color);
        }
        
        .footer-modern {
            background: var(--surface-color);
            padding: 2rem;
            border-radius: var(--border-radius-lg);
            text-align: center;
            margin-top: 3rem;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
        }
        
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
        
        .animate-in {
            animation: fadeInUp 0.6s ease-out;
        }
        
        .glass-effect {
            backdrop-filter: blur(10px);
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .text-gradient {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .team-background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.03;
            background-size: 200px 200px;
            background-repeat: repeat;
            background-position: center;
        }
        
        @media (max-width: 768px) {
            .modern-header h1 {
                font-size: 2rem;
            }
            
            .section-title-modern {
                font-size: 2rem;
            }
            
            .metric-card-modern {
                padding: 0.75rem;
            }
            
            .metric-value-modern {
                font-size: 1.25rem;
            }
        }
        
        .stSelectbox:focus-within > div > div > div,
        .stSlider:focus-within > div > div > div > div {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
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
        
        for ext in extensions:
            pattern = f"images_joueurs/**{player_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
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
        
        for ext in extensions:
            pattern = f"{folder}/**{team_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
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
    """Composants d'interface utilisateur modernes et réutilisables"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête principal moderne"""
        st.markdown("""
        <div class='modern-header animate-in'>
            <h1>⚽ Football Dashboard Pro</h1>
            <p>Analyse avancée des performances - Saison 2024-25</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_header():
        """Affiche l'en-tête de la sidebar moderne"""
        st.markdown("""
        <div class='sidebar-modern'>
            <h2>🎯 Configuration</h2>
            <p>Sélectionnez votre joueur</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def add_team_background(team_name: str, competition: str):
        """Ajoute le logo de l'équipe en arrière-plan"""
        logo_path = ImageManager.get_club_logo(competition, team_name)
        if logo_path:
            try:
                with open(logo_path, "rb") as f:
                    logo_data = base64.b64encode(f.read()).decode()
                
                st.markdown(f"""
                <div class="team-background" style="background-image: url(data:image/png;base64,{logo_data});"></div>
                """, unsafe_allow_html=True)
            except Exception:
                pass
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte complète du joueur avec design moderne"""
        UIComponents.add_team_background(player_data['Équipe'], competition)
        
        container = st.container()
        
        with container:
            col1, col2, col3 = st.columns([1, 2.5, 1], gap="medium")
            
            with col1:
                UIComponents._render_player_photo_modern(player_data['Joueur'])
            
            with col2:
                UIComponents._render_player_info_modern(player_data)
            
            with col3:
                UIComponents._render_club_logo_modern(player_data['Équipe'], competition)
    
    @staticmethod
    def _render_player_photo_modern(player_name: str):
        """Affiche la photo du joueur avec style moderne"""
        photo_path = ImageManager.get_player_photo(player_name)
        
        if photo_path:
            try:
                image = Image.open(photo_path)
                st.markdown(f"""
                <div class='image-container-modern animate-in'>
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 12px;">
                </div>
                <p style='text-align: center; color: var(--primary-color); font-weight: 600; margin-top: 10px;'>
                    📸 {player_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_photo_placeholder_modern(player_name)
        else:
            UIComponents._render_photo_placeholder_modern(player_name)
    
    @staticmethod
    def _render_club_logo_modern(team_name: str, competition: str):
        """Affiche le logo du club avec style moderne"""
        logo_path = ImageManager.get_club_logo(competition, team_name)
        
        if logo_path:
            try:
                image = Image.open(logo_path)
                st.markdown(f"""
                <div class='club-logo-modern animate-in'>
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain;">
                </div>
                <p style='text-align: center; color: var(--primary-color); font-weight: 600; margin-top: 10px;'>
                    🏟️ {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_logo_placeholder_modern(team_name)
        else:
            UIComponents._render_logo_placeholder_modern(team_name)
    
    @staticmethod
    def _render_player_info_modern(player_data: pd.Series):
        """Affiche les informations centrales du joueur avec design moderne"""
        valeur_marchande = "N/A"
        if 'Valeur marchande' in player_data.index:
            valeur_marchande = format_market_value(player_data['Valeur marchande'])
        
        equipe_display = player_data['Équipe'][:15] + "..." if len(str(player_data['Équipe'])) > 15 else player_data['Équipe']
        nationalite_display = player_data['Nationalité'][:10] + "..." if len(str(player_data['Nationalité'])) > 10 else player_data['Nationalité']
        position_display = player_data['Position'][:8] + "..." if len(str(player_data['Position'])) > 8 else player_data['Position']
        
        st.markdown(f"""
        <div class='player-card animate-in'>
            <h2 class='text-gradient' style='margin-bottom: 25px; font-size: 2.2rem; color: white; font-weight: 900;'>
                {player_data['Joueur']}
            </h2>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px; max-width: 100%;'>
                <div class='metric-card-modern glass-effect'>
                    <div class='metric-value-modern' style='color: white;'>{player_data['Âge']}</div>
                    <div class='metric-label-modern'>Âge</div>
                </div>
                <div class='metric-card-modern glass-effect'>
                    <div class='metric-value-modern' title='{player_data['Position']}' style='color: white;'>{position_display}</div>
                    <div class='metric-label-modern'>Position</div>
                </div>
                <div class='metric-card-modern glass-effect'>
                    <div class='metric-value-modern' title='{player_data['Nationalité']}' style='color: white;'>{nationalite_display}</div>
                    <div class='metric-label-modern'>Nationalité</div>
                </div>
                <div class='metric-card-modern glass-effect'>
                    <div class='metric-value-modern' style='color: white;'>{int(player_data['Minutes jouées'])}</div>
                    <div class='metric-label-modern'>Minutes</div>
                </div>
                <div class='metric-card-modern glass-effect'>
                    <div class='metric-value-modern' style='color: #F59E0B;'>{valeur_marchande}</div>
                    <div class='metric-label-modern'>Val. Marchande</div>
                </div>
                <div class='metric-card-modern glass-effect'>
                    <div class='metric-value-modern' title='{player_data['Équipe']}' style='color: white;'>{equipe_display}</div>
                    <div class='metric-label-modern'>Équipe</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_photo_placeholder_modern(player_name: str):
        """Affiche un placeholder moderne pour la photo"""
        st.markdown(f"""
        <div class='image-container-modern animate-in'>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 4rem; margin-bottom: 10px;'>👤</div>
                <p>Photo non disponible</p>
                <p style='font-size: 0.8rem;'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder_modern(team_name: str):
        """Affiche un placeholder moderne pour le logo"""
        st.markdown(f"""
        <div class='club-logo-modern animate-in'>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 3rem; margin-bottom: 10px;'>🏟️</div>
                <p style='font-size: 0.9rem;'>Logo non disponible</p>
                <p style='font-size: 0.8rem;'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _image_to_base64(image: Image.Image) -> str:
        """Convertit une image PIL en base64"""
        import io
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    @staticmethod
    def render_footer():
        """Affiche le footer moderne"""
        st.markdown("""
        <div class='footer-modern animate-in'>
            <h3 style='color: var(--primary-color); margin: 0 0 15px 0; font-weight: 800;'>
                📊 Football Dashboard Pro
            </h3>
            <p style='color: var(--text-primary); margin: 0; font-size: 1.1rem; font-weight: 500;'>
                Analyse avancée des performances footballistiques
            </p>
            <p style='color: var(--text-secondary); margin: 10px 0 0 0; font-size: 0.9rem;'>
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
                    matches = player


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
    """Gestionnaire centralisé pour les graphiques avec design moderne"""
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], title: str, color_palette: List[str]) -> go.Figure:
        """Crée un graphique en barres stylé moderne"""
        fig = go.Figure(data=[go.Bar(
            x=list(data.keys()),
            y=list(data.values()),
            marker=dict(
                color=color_palette,
                line=dict(color='rgba(255,255,255,0.2)', width=1),
                opacity=0.9
            ),
            text=[f"{v:.1f}" for v in data.values()],
            textposition='outside',
            textfont=dict(color='white', size=14, family='Inter'),
            hovertemplate='<b>%{x}</b><br>Valeur: %{y:.2f}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=20, color='white', family='Inter'),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                tickfont=dict(color='white', size=12, family='Inter'),
                tickangle=45,
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=False
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=12, family='Inter'),
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=True,
                gridwidth=1
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            height=450,
            margin=dict(t=80, b=80, l=60, r=60)
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
                        axis=dict(range=[0, 100], tickcolor='white', tickfont=dict(color='white', family='Inter')),
                        bar=dict(color=color, thickness=0.7),
                        bgcolor="rgba(55, 65, 81, 0.8)",
                        borderwidth=2,
                        bordercolor="rgba(255,255,255,0.3)",
                        steps=[
                            {'range': [0, 33], 'color': 'rgba(239, 68, 68, 0.2)'},
                            {'range': [33, 66], 'color': 'rgba(245, 158, 11, 0.2)'},
                            {'range': [66, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
                        ],
                        threshold={
                            'line': {'color': "white", 'width': 3},
                            'thickness': 0.8,
                            'value': 80
                        }
                    ),
                    number={
                        'suffix': '%', 
                        'font': {'color': 'white', 'size': 16, 'family': 'Inter'}
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            height=350,
            title_text=title,
            title_font_color='white',
            title_font_size=20,
            title_font_family='Inter',
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            margin=dict(t=80, b=40, l=40, r=40)
        )
        
        fig.update_annotations(font=dict(color='white', size=14, family='Inter'))
        
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
            text=[f"{v:.2f}" for v in player_data.values()],
            textposition='outside',
            textfont=dict(color='white', family='Inter'),
            opacity=0.9,
            hovertemplate='<b>%{fullData.name}</b><br>%{x}: %{y:.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            name='Moyenne compétition',
            x=list(avg_data.keys()),
            y=list(avg_data.values()),
            marker_color=AppConfig.COLORS['accent'],
            text=[f"{v:.2f}" for v in avg_data.values()],
            textposition='outside',
            textfont=dict(color='white', family='Inter'),
            opacity=0.7,
            hovertemplate='<b>%{fullData.name}</b><br>%{x}: %{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color='white', size=20, family='Inter'),
                x=0.5,
                y=0.95
            ),
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            xaxis=dict(
                tickfont=dict(color='white', size=12, family='Inter'),
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=False
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=12, family='Inter'), 
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=True,
                gridwidth=1
            ),
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color='white', family='Inter')
            ),
            margin=dict(t=100, b=80, l=60, r=60)
        )
        
        return fig
    
    @staticmethod
    def create_radar_chart(metrics: Dict[str, float], percentiles: List[float], 
                          avg_percentiles: List[float], player_name: str, 
                          competition: str, color: str) -> go.Figure:
        """Crée un radar chart moderne et professionnel"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=percentiles,
            theta=list(metrics.keys()),
            fill='toself',
            fillcolor=f'rgba({ChartManager._hex_to_rgb(color)}, 0.4)',
            line=dict(color=color, width=3),
            marker=dict(color=color, size=8, symbol='circle'),
            name=player_name,
            hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
            customdata=list(metrics.values())
        ))
        
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
                    tickfont=dict(color='white', size=11, family='Inter'),
                    showticklabels=True,
                    tickmode='linear',
                    tick0=0,
                    dtick=20,
                    linecolor='rgba(255,255,255,0.3)'
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.2)',
                    tickcolor='white',
                    tickfont=dict(color='white', size=12, family='Inter'),
                    linecolor='rgba(255,255,255,0.3)'
                ),
                bgcolor='rgba(17, 24, 39, 0.8)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            title=dict(
                text=f"Performance Radar - {player_name}",
                font=dict(size=20, color='white', family='Inter'),
                x=0.5,
                y=0.95
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color='white', size=12, family='Inter')
            ),
            height=500,
            margin=dict(t=80, b=80, l=60, r=60)
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
        
        avg_metrics = {}
        minutes_90_comp = df_comparison['Minutes jouées'] / 90
        
        avg_metrics['Passes tentées/90'] = (df_comparison['Passes tentées'] / minutes_90_comp).mean()
        avg_metrics['Passes prog./90'] = (df_comparison.get('Passes progressives', pd.Series([0]*len(df_comparison))) / minutes_90_comp).mean()
        avg_metrics['Dribbles/90'] = (df_comparison['Dribbles tentés'] / minutes_90_comp).mean()
        avg_metrics['Touches/90'] = (df_comparison['Touches de balle'] / minutes_90_comp).mean()
        avg_metrics['Passes clés/90'] = (df_comparison['Passes clés'] / minutes_90_comp).mean()
        avg_metrics['% Passes réussies'] = df_comparison.get('Pourcentage de passes réussies', pd.Series([0]*len(df_comparison))).mean()
        avg_metrics['% Dribbles réussis'] = df_comparison.get('Pourcentage de dribbles réussis', pd.Series([0]*len(df_comparison))).mean()
        
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
    """Gestionnaire moderne pour la sidebar"""
    
    @staticmethod
    def render_sidebar(df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
        """Rendu complet de la sidebar moderne"""
        with st.sidebar:
            UIComponents.render_sidebar_header()
            
            st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
            competitions = DataManager.get_competitions(df)
            selected_competition = st.selectbox(
                "🏆 **Choisir une compétition**",
                competitions,
                index=0,
                help="Sélectionnez la compétition pour filtrer les joueurs"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            df_filtered = DataManager.filter_data_by_competition(df, selected_competition)
            
            st.markdown("---")
            
            SidebarManager._render_minutes_filter_modern(df_filtered)
            
            min_minutes_filter = st.session_state.get('min_minutes_filter', 0)
            df_filtered_minutes = DataManager.filter_data_by_minutes(df_filtered, min_minutes_filter)
            
            SidebarManager._render_filter_info_modern(df_filtered_minutes)
            
            st.markdown("---")
            
            selected_player = SidebarManager._render_player_selection_modern(df_filtered_minutes)
            
            SidebarManager._render_sidebar_footer_modern()
            
            return selected_competition, selected_player, df_filtered_minutes
    
    @staticmethod
    def _render_minutes_filter_modern(df_filtered: pd.DataFrame):
        """Rendu moderne du filtre par minutes"""
        if not df_filtered['Minutes jouées'].empty:
            min_minutes = int(df_filtered['Minutes jouées'].min())
            max_minutes = int(df_filtered['Minutes jouées'].max())
            
            st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
            st.markdown("**⏱️ Filtrer par minutes jouées**")
            
            min_minutes_filter = st.slider(
                "Minutes minimum",
                min_value=min_minutes,
                max_value=max_minutes,
                value=min_minutes,
                step=90,
                help="Filtrer les joueurs ayant joué au minimum ce nombre de minutes",
                key='min_minutes_filter'
            )
            st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def _render_filter_info_modern(df_filtered: pd.DataFrame):
        """Affiche les informations de filtrage modernes"""
        nb_joueurs = len(df_filtered)
        
        st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
        if nb_joueurs > 0:
            st.success(f"✅ **{nb_joueurs} joueurs** correspondent aux critères")
        else:
            st.warning("⚠️ Aucun joueur ne correspond aux critères")
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def _render_player_selection_modern(df_filtered: pd.DataFrame) -> Optional[str]:
        """Rendu moderne de la sélection de joueur"""
        if not df_filtered.empty:
            joueurs = DataManager.get_players(df_filtered)
            if joueurs:
                st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
                selected_player = st.selectbox(
                    "👤 **Choisir un joueur**",
                    joueurs,
                    index=0,
                    help="Sélectionnez le joueur à analyser"
                )
                st.markdown("</div>", unsafe_allow_html=True)
                return selected_player
        
        st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
        st.error("❌ Aucun joueur disponible avec ces critères.")
        st.markdown("</div>", unsafe_allow_html=True)
        return None
    
    @staticmethod
    def _render_sidebar_footer_modern():
        """Rendu moderne du footer de la sidebar"""
        st.markdown("---")
        st.markdown("""
        <div class='modern-card glass-effect' style='text-align: center;'>
            <h4 style='color: var(--primary-color); margin: 0 0 10px 0; font-weight: 800;'>
                📊 Dashboard Pro
            </h4>
            <p style='color: var(--text-primary); margin: 0; font-size: 0.9rem; font-weight: 500;'>
                Analyse Football Avancée
            </p>
            <p style='color: var(--text-secondary); margin: 8px 0 0 0; font-size: 0.8rem;'>
                Interface moderne & intuitive
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE TABS
# ================================================================================================

class TabManager:
    """Gestionnaire pour les différents onglets"""
    
    @staticmethod
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance offensive"""
        st.markdown("<h2 class='section-title-modern'>🎯 Performance Offensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_offensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns(2)
        
        with col1:
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
            
            st.markdown("<h3 class='subsection-title-modern'>🎯 Radar Offensif</h3>", unsafe_allow_html=True)
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
            efficiency_data = {
                'Conversion': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                'Efficacité passes': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(efficiency_data, "Efficacité Offensive")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
            avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
            
            fig_comp = ChartManager.create_comparison_chart(
                comparison_metrics,
                avg_comparison,
                selected_player,
                "Performance par 90min vs Moyenne"
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        TabManager._render_detailed_metrics(analysis['metrics'], "📊 Métriques Offensives Détaillées")
    
    @staticmethod
    def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance défensive"""
        st.markdown("<h2 class='section-title-modern'>🛡️ Performance Défensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_defensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns(2)
        
        with col1:
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
            
            st.markdown("<h3 class='subsection-title-modern'>🛡️ Radar Défensif</h3>", unsafe_allow_html=True)
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
            success_data = {
                'Duels défensifs': player_data.get('Pourcentage de duels gagnés', 0),
                'Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                'Passes': player_data['Pourcentage de passes réussies']
            }
            
            fig_gauge = ChartManager.create_gauge_chart(success_data, "Pourcentages de Réussite")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
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
        st.markdown("<h2 class='section-title-modern'>🎨 Performance Technique</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_technical_performance(player_data, df_comparison)
        
        col1, col2 = st.columns(2)
        
        with col1:
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
            
            st.markdown("<h3 class='subsection-title-modern'>🎨 Radar Technique</h3>", unsafe_allow_html=True)
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
            technical_success = {
                'Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
            }
            
            fig_gauge = ChartManager.create_gauge_chart(technical_success, "Précision Technique")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
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
        """Rendu de l'onglet comparaison"""
        st.markdown("<h2 class='section-title-modern'>🔄 Comparaison Pizza Chart</h2>", unsafe_allow_html=True)
        
        st.markdown("<div class='modern-card animate-in'>", unsafe_allow_html=True)
        mode = st.radio(
            "**Mode de visualisation**",
            ["Radar individuel", "Radar comparatif"],
            horizontal=True,
            help="Choisissez le type d'analyse radar"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        competitions = sorted(df['Compétition'].dropna().unique())
        
        if mode == "Radar individuel":
            TabManager._render_individual_radar(df, selected_player, competitions)
        else:
            TabManager._render_comparative_radar(df, competitions)
    
    @staticmethod
    def _render_individual_radar(df: pd.DataFrame, selected_player: str, competitions: List[str]):
        """Rendu du radar individuel moderne"""
        st.markdown(f"<h3 class='subsection-title-modern'>🎯 Radar individuel : {selected_player}</h3>", unsafe_allow_html=True)
        
        try:
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("<div class='modern-card'>", unsafe_allow_html=True)
                    competition = st.selectbox(
                        "**🏆 Compétition de référence**", 
                        competitions,
                        help="Sélectionnez la compétition pour calculer les percentiles"
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
            
            df_comp = df[df['Compétition'] == competition]
            values = MetricsCalculator.calculate_percentiles(selected_player, df_comp)
            
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            baker = PyPizza(
                params=list(AppConfig.RAW_STATS.keys()),
                background_color="#111827",
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
                kwargs_params=dict(color="#ffffff", fontsize=14, fontproperties=font_bold.prop),
                kwargs_values=dict(
                    color="#ffffff", 
                    fontsize=12, 
                    fontproperties=font_normal.prop,
                    bbox=dict(
                        edgecolor="#FFFFFF", 
                        facecolor=AppConfig.COLORS['primary'], 
                        boxstyle="round,pad=0.3", 
                        lw=2
                    )
                )
            )
            
            fig.text(0.515, 0.97, selected_player, size=32, ha="center", 
                    fontproperties=font_bold.prop, color="#ffffff", weight='bold')
            fig.text(0.515, 0.94, f"Radar Individuel | Percentiles vs {competition} | Saison 2024-25", 
                    size=16, ha="center", fontproperties=font_bold.prop, color="#ffffff")
            
            fig.text(0.99, 0.01, "Football Dashboard Pro | Données: FBRef", 
                    size=10, ha="right", fontproperties=font_italic.prop, color="#dddddd")
            
            st.pyplot(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Erreur lors de la création du radar individuel : {str(e)}")
    
    @staticmethod
    def _render_comparative_radar(df: pd.DataFrame, competitions: List[str]):
        """Rendu du radar comparatif moderne"""
        st.markdown("<div class='modern-card animate-in'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 Joueur 1**")
            ligue1 = st.selectbox("🏆 Compétition", competitions, key="ligue1_comp")
            df_j1 = df[df['Compétition'] == ligue1]
            joueur1 = st.selectbox("Joueur", df_j1['Joueur'].sort_values(), key="joueur1_comp")
        
        with col2:
            st.markdown("**👤 Joueur 2**")
            ligue2 = st.selectbox("🏆 Compétition", competitions, key="ligue2_comp")
            df_j2 = df[df['Compétition'] == ligue2]
            joueur2 = st.selectbox("Joueur", df_j2['Joueur'].sort_values(), key="joueur2_comp")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if joueur1 and joueur2:
            st.markdown(f"<h3 class='subsection-title-modern'>⚔️ {joueur1} vs {joueur2}</h3>", unsafe_allow_html=True)
            
            try:
                values1 = MetricsCalculator.calculate_percentiles(joueur1, df_j1)
                values2 = MetricsCalculator.calculate_percentiles(joueur2, df_j2)
                
                font_normal = FontManager()
                font_bold = FontManager()
                font_italic = FontManager()
                
                baker = PyPizza(
                    params=list(AppConfig.RAW_STATS.keys()),
                    background_color="#111827",
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
                        facecolor=AppConfig.COLORS['accent'], 
                        edgecolor="#FFFFFF", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_params=dict(
                        color="#ffffff", 
                        fontsize=14, 
                        fontproperties=font_bold.prop
                    ),
                    kwargs_values=dict(
                        color="#ffffff", 
                        fontsize=12, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        bbox=dict(
                            edgecolor="#FFFFFF", 
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
                            edgecolor="#FFFFFF", 
                            facecolor=AppConfig.COLORS['accent'], 
                            boxstyle="round,pad=0.3", 
                            lw=2
                        )
                    )
                )
                
                fig.text(0.515, 0.97, "Radar Comparatif | Percentiles | Saison 2024-25",
                         size=18, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                
                legend_p1 = mpatches.Patch(color=AppConfig.COLORS['primary'], label=joueur1)
                legend_p2 = mpatches.Patch(color=AppConfig.COLORS['accent'], label=joueur2)
                ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0),
                         facecolor='#374151', edgecolor='white')
                
                fig.text(0.99, 0.01, "Football Dashboard Pro | Source: FBRef",
                         size=10, ha="right", fontproperties=font_italic.prop, color="#dddddd")
                
                st.pyplot(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Erreur lors de la création du radar comparatif : {str(e)}")
    
    @staticmethod
    def _render_detailed_metrics(metrics: Dict[str, float], title: str):
        """Affiche les métriques détaillées avec design moderne"""
        st.markdown(f"<h3 class='subsection-title-modern'>{title}</h3>", unsafe_allow_html=True)
        
        st.markdown("<div class='modern-card animate-in'>", unsafe_allow_html=True)
        
        cols = st.columns(min(len(metrics), 4))
        
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i % 4]:
                if '/' in str(value):
                    display_value = f"{value:.2f}"
                elif '%' in metric:
                    display_value = f"{value:.1f}%"
                else:
                    display_value = f"{value:.2f}"
                
                st.markdown(f"""
                <div class='metric-card-modern animate-in' style='margin-bottom: 1rem;'>
                    <div class='metric-value-modern'>{display_value}</div>
                    <div class='metric-label-modern'>{metric}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

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
        df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        UIComponents.render_header()
        
        selected_competition, selected_player, df_filtered = SidebarManager.render_sidebar(df)
        
        if selected_player:
            player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
            
            UIComponents.render_player_card(player_data, selected_competition)
            
            st.markdown("---")
            
            self._render_main_tabs(player_data, df_filtered, selected_player, df)
        
        else:
            self._render_no_player_message()
        
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
        <div class='modern-card animate-in' style='text-align: center; padding: 3rem;'>
            <h2 style='color: var(--primary-color); margin-bottom: 1.5rem; font-weight: 900;'>
                ⚠️ Aucun joueur sélectionné
            </h2>
            <p style='color: var(--text-primary); font-size: 1.2rem; margin-bottom: 2rem; line-height: 1.6;'>
                Veuillez ajuster les filtres dans la sidebar pour sélectionner un joueur à analyser.
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; margin-top: 2rem;'>
                <div class='metric-card-modern' style='text-align: center; padding: 2rem;'>
                    <div style='font-size: 3rem; margin-bottom: 1rem;'>🎯</div>
                    <h4 style='color: var(--primary-color); margin: 0;'>Analyse Offensive</h4>
                    <p style='color: var(--text-secondary); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                        Buts, passes, créativité
                    </p>
                </div>
                <div class='metric-card-modern' style='text-align: center; padding: 2rem;'>
                    <div style='font-size: 3rem; margin-bottom: 1rem;'>🛡️</div>
                    <h4 style='color: var(--accent-color); margin: 0;'>Analyse Défensive</h4>
                    <p style='color: var(--text-secondary); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                        Tacles, interceptions, duels
                    </p>
                </div>
                <div class='metric-card-modern' style='text-align: center; padding: 2rem;'>
                    <div style='font-size: 3rem; margin-bottom: 1rem;'>🎨</div>
                    <h4 style='color: var(--success-color); margin: 0;'>Analyse Technique</h4>
                    <p style='color: var(--text-secondary); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                        Passes, dribbles, précision
                    </p>
                </div>
                <div class='metric-card-modern' style='text-align: center; padding: 2rem;'>
                    <div style='font-size: 3rem; margin-bottom: 1rem;'>🔄</div>
                    <h4 style='color: var(--warning-color); margin: 0;'>Comparaison</h4>
                    <p style='color: var(--text-secondary); margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                        Radars comparatifs
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_error_page(self):
        """Affiche la page d'erreur moderne"""
        st.markdown("""
        <div class='modern-card animate-in' style='text-align: center; padding: 3rem; border-color: var(--danger-color);'>
            <h1 style='color: var(--danger-color); margin-bottom: 1.5rem; font-weight: 900;'>
                ⚠️ Erreur de Chargement
            </h1>
            <p style='color: var(--text-primary); font-size: 1.2rem; margin-bottom: 2rem; line-height: 1.6;'>
                Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
            </p>
            <div class='modern-card glass-effect' style='padding: 2rem; margin-top: 2rem;'>
                <h3 style='color: var(--success-color); margin-bottom: 1rem; font-weight: 700;'>
                    📋 Fichiers requis
                </h3>
                <div style='text-align: left; max-width: 600px; margin: 0 auto;'>
                    <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                        <span style='color: var(--primary-color); margin-right: 0.5rem;'>📄</span>
                        <span style='color: var(--text-primary);'>df_BIG2025.csv (données principales)</span>
                    </div>
                    <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                        <span style='color: var(--primary-color); margin-right: 0.5rem;'>📁</span>
                        <span style='color: var(--text-primary);'>images_joueurs/ (photos des joueurs)</span>
                    </div>
                    <div style='display: flex; align-items: center;'>
                        <span style='color: var(--primary-color); margin-right: 0.5rem;'>🏟️</span>
                        <span style='color: var(--text-primary);'>*_Logos/ (logos des clubs par compétition)</span>
                    </div>
                </div>
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
