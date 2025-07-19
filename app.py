import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import glob
from PIL import Image
import base64
import io
from typing import Dict, List, Optional, Tuple, Union

# Imports pour l'analyse de similarité
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import euclidean_distances
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# ================================================================================================
# CONFIGURATION ET CONSTANTES
# ================================================================================================

class Config:
    """Configuration centralisée de l'application"""
    
    # Configuration de la page Streamlit
    PAGE_CONFIG = {
        "page_title": "Football Analytics Pro",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "collapsed"
    }
    
    # Palette de couleurs modernes
    COLORS = {
        'primary': '#6366f1',
        'secondary': '#10b981',
        'accent': '#f59e0b',
        'success': '#06d6a0',
        'warning': '#fbbf24',
        'danger': '#ef4444',
        'dark': '#111827',
        'surface': '#1f2937',
        'background': '#0f172a',
        'text': '#f1f5f9',
        'text_secondary': '#94a3b8',
        'border': '#374151',
        'gradient': ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899']
    }
    
    # Configuration des radars
    RADAR_METRICS = {
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
    
    # Mapping des dossiers de logos
    LOGO_FOLDERS = {
        'Bundliga': 'Bundliga_Logos',
        'La Liga': 'La_Liga_Logos',
        'Ligue 1': 'Ligue1_Logos',
        'Premier League': 'Premier_League_Logos',
        'Serie A': 'Serie_A_Logos'
    }
    
    # Métriques pour l'analyse de similarité
    SIMILARITY_METRICS = [
        'Minutes jouées', 'Buts', 'Passes décisives', 'Tirs', 'Passes clés',
        'Passes tentées', 'Dribbles tentés', 'Dribbles réussis', 'Tacles gagnants',
        'Interceptions', 'Pourcentage de passes réussies', 'Pourcentage de dribbles réussis',
        'Ballons récupérés', 'Passes progressives', 'Courses progressives',
        'Passes dans le dernier tiers', 'Duels aériens gagnés', 'Duels défensifs gagnés',
        'Tirs cadrés', 'Actions menant à un tir'
    ]

# ================================================================================================
# GESTIONNAIRE DE STYLES CSS AVANCÉ
# ================================================================================================

class AdvancedStyleManager:
    """Gestionnaire des styles CSS ultra-personnalisés"""
    
    @staticmethod
    def get_custom_css() -> str:
        """Retourne le CSS ultra-personnalisé pour masquer Streamlit"""
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
        
        /* VARIABLES CSS MODERNES */
        :root {
            --primary: #6366f1;
            --secondary: #10b981;
            --accent: #f59e0b;
            --danger: #ef4444;
            --warning: #fbbf24;
            --success: #06d6a0;
            
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --bg-surface: #475569;
            
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            
            --border-primary: #475569;
            --border-secondary: #64748b;
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            
            --radius-sm: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-xl: 16px;
            --radius-2xl: 24px;
            
            --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            --transition-slow: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* RESET ET BASE */
        * {
            box-sizing: border-box;
        }
        
        /* MASQUER COMPLÈTEMENT STREAMLIT */
        .stApp > header,
        .stApp > .main > div:first-child,
        .stDeployButton,
        .stDecoration,
        [data-testid="manage-app-button"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        .stMainBlockContainer > div:first-child,
        .stAppViewContainer > .main > div:first-child,
        #MainMenu,
        footer,
        .stException {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            position: absolute !important;
            z-index: -1000 !important;
        }
        
        /* STRUCTURE PRINCIPALE */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, #1a202c 50%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .main .block-container {
            padding: 0 !important;
            max-width: 100% !important;
            margin: 0 !important;
        }
        
        /* NAVBAR PERSONNALISÉE */
        .custom-navbar {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border-primary);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: var(--shadow-lg);
        }
        
        .navbar-brand {
            font-size: 1.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .navbar-stats {
            display: flex;
            gap: 2rem;
            align-items: center;
        }
        
        .navbar-stat {
            text-align: center;
        }
        
        .navbar-stat-value {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .navbar-stat-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* LAYOUT PRINCIPAL */
        .app-container {
            display: flex;
            min-height: calc(100vh - 80px);
        }
        
        .sidebar-custom {
            width: 350px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-primary);
            padding: 2rem;
            overflow-y: auto;
            position: sticky;
            top: 80px;
            height: calc(100vh - 80px);
        }
        
        .main-content {
            flex: 1;
            padding: 2rem;
            overflow-y: auto;
        }
        
        /* SIDEBAR PERSONNALISÉE */
        .sidebar-header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            padding: 1.5rem;
            border-radius: var(--radius-xl);
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }
        
        .sidebar-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }
        
        .sidebar-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: white;
            margin: 0;
            position: relative;
            z-index: 1;
        }
        
        .sidebar-subtitle {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.8);
            margin: 0.5rem 0 0 0;
            position: relative;
            z-index: 1;
        }
        
        /* FORMULAIRES PERSONNALISÉS */
        .custom-select {
            position: relative;
            margin-bottom: 1.5rem;
        }
        
        .custom-select label {
            display: block;
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .custom-input {
            width: 100%;
            padding: 0.75rem 1rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            font-size: 0.875rem;
            transition: var(--transition);
        }
        
        .custom-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }
        
        /* BOUTONS PERSONNALISÉS */
        .custom-button {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            text-decoration: none;
        }
        
        .custom-button:hover {
            background: #5b61d8;
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .custom-button-secondary {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-primary);
        }
        
        .custom-button-secondary:hover {
            background: var(--bg-surface);
            border-color: var(--primary);
        }
        
        /* CARTES MODERNES */
        .modern-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-xl);
            padding: 2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            transition: var(--transition-slow);
        }
        
        .modern-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
        }
        
        .modern-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
            border-color: var(--primary);
        }
        
        /* PLAYER HEADER */
        .player-hero {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            padding: 3rem 2rem;
            border-radius: var(--radius-2xl);
            text-align: center;
            margin-bottom: 3rem;
            position: relative;
            overflow: hidden;
        }
        
        .player-hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 80%, rgba(255,255,255,0.1) 0%, transparent 50%);
        }
        
        .player-name {
            font-size: 3rem;
            font-weight: 900;
            color: white;
            margin: 0;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .player-subtitle {
            font-size: 1.25rem;
            color: rgba(255, 255, 255, 0.9);
            margin: 1rem 0 0 0;
            position: relative;
            z-index: 1;
        }
        
        /* MÉTRIQUES MODERNES */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .metric-card-modern {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            text-align: center;
            transition: var(--transition-slow);
            position: relative;
            overflow: hidden;
        }
        
        .metric-card-modern::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            transform: scaleX(0);
            transition: var(--transition);
        }
        
        .metric-card-modern:hover::before {
            transform: scaleX(1);
        }
        
        .metric-card-modern:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary);
        }
        
        .metric-value-modern {
            font-size: 2rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 0.5rem;
            line-height: 1;
        }
        
        .metric-label-modern {
            font-size: 0.875rem;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* NAVIGATION TABS PERSONNALISÉE */
        .custom-tabs {
            display: flex;
            background: var(--bg-secondary);
            border-radius: var(--radius-xl);
            padding: 0.5rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border-primary);
            gap: 0.25rem;
        }
        
        .custom-tab {
            flex: 1;
            padding: 1rem 1.5rem;
            background: transparent;
            border: none;
            border-radius: var(--radius-lg);
            color: var(--text-muted);
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            text-align: center;
        }
        
        .custom-tab:hover {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
        }
        
        .custom-tab.active {
            background: var(--primary);
            color: white;
            box-shadow: var(--shadow-md);
        }
        
        /* MASQUER LES ÉLÉMENTS STREAMLIT NATIFS */
        .stSelectbox, .stSlider, .stTabs, .stColumns, .stMetric {
            background: transparent !important;
        }
        
        .stSelectbox > div > div {
            background: var(--bg-tertiary) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            display: none !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        
        /* RESPONSIVE DESIGN */
        @media (max-width: 1024px) {
            .app-container {
                flex-direction: column;
            }
            
            .sidebar-custom {
                width: 100%;
                height: auto;
                position: relative;
                top: 0;
            }
            
            .custom-navbar {
                padding: 1rem;
            }
            
            .navbar-stats {
                gap: 1rem;
            }
            
            .player-name {
                font-size: 2rem;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }
        }
        
        @media (max-width: 640px) {
            .navbar-stats {
                display: none;
            }
            
            .player-name {
                font-size: 1.5rem;
            }
            
            .metrics-grid {
                grid-template-columns: 1fr 1fr;
            }
            
            .custom-tabs {
                flex-direction: column;
            }
        }
        
        /* ANIMATIONS AVANCÉES */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.8;
            }
        }
        
        .animate-fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
        
        .animate-slide-in {
            animation: slideInLeft 0.4s ease-out;
        }
        
        .animate-pulse {
            animation: pulse 2s infinite;
        }
        
        /* LOADING STATES */
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: var(--primary);
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* TOOLTIPS PERSONNALISÉS */
        .tooltip {
            position: relative;
            cursor: help;
        }
        
        .tooltip::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-tertiary);
            color: var(--text-primary);
            padding: 0.5rem 0.75rem;
            border-radius: var(--radius-md);
            font-size: 0.75rem;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: var(--transition);
            border: 1px solid var(--border-primary);
            z-index: 1000;
        }
        
        .tooltip:hover::after {
            opacity: 1;
            visibility: visible;
        }
        
        /* SCROLLBARS PERSONNALISÉS */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border-primary);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary);
        }
        </style>
        """
    
    @staticmethod
    def render_custom_navbar(df: pd.DataFrame):
        """Rendu de la navbar personnalisée"""
        total_players = len(df)
        total_competitions = df['Compétition'].nunique()
        total_teams = df['Équipe'].nunique()
        total_minutes = int(df['Minutes jouées'].sum())
        avg_age = df['Âge'].mean()
        
        st.markdown(f"""
        <div class="custom-navbar">
            <div class="navbar-brand">
                <i class="fas fa-futbol"></i> Football Analytics Pro
            </div>
            <div class="navbar-stats">
                <div class="navbar-stat">
                    <div class="navbar-stat-value">{total_players:,}</div>
                    <div class="navbar-stat-label">Joueurs</div>
                </div>
                <div class="navbar-stat">
                    <div class="navbar-stat-value">{total_competitions}</div>
                    <div class="navbar-stat-label">Ligues</div>
                </div>
                <div class="navbar-stat">
                    <div class="navbar-stat-value">{total_teams}</div>
                    <div class="navbar-stat-label">Équipes</div>
                </div>
                <div class="navbar-stat">
                    <div class="navbar-stat-value">{total_minutes:,}</div>
                    <div class="navbar-stat-label">Minutes</div>
                </div>
                <div class="navbar-stat">
                    <div class="navbar-stat-value">{avg_age:.1f}</div>
                    <div class="navbar-stat-label">Âge Moyen</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# UTILITAIRES AMÉLIORÉS
# ================================================================================================

class Utils:
    """Fonctions utilitaires améliorées"""
    
    @staticmethod
    def format_market_value(value: Union[str, int, float]) -> str:
        """Formate une valeur marchande avec des sigles et le symbole Euro"""
        if pd.isna(value) or value is None:
            return "N/A"
        
        if isinstance(value, str):
            try:
                clean_value = value.replace('€', '').replace('M', '').replace('K', '').replace('B', '').replace(',', '').replace(' ', '')
                if 'M' in value.upper():
                    clean_value = str(float(clean_value) * 1_000_000)
                elif 'K' in value.upper():
                    clean_value = str(float(clean_value) * 1_000)
                elif 'B' in value.upper():
                    clean_value = str(float(clean_value) * 1_000_000_000)
                
                if clean_value and clean_value != '.':
                    value = float(clean_value)
                else:
                    return "N/A"
            except (ValueError, TypeError):
                return "N/A"
        
        try:
            value = float(value)
            if value <= 0 or value > 1_000_000_000_000:
                return "N/A"
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
    
    @staticmethod
    def get_market_value_safe(player_data: pd.Series) -> str:
        """Récupère la valeur marchande depuis les données du joueur"""
        possible_columns = [
            'Valeur marchande', 'Market Value', 'valeur_marchande', 
            'Valeur', 'Value', 'market_value', 'Valeur en €', 'Valeur (€)',
            'Market_Value', 'Valeur_marchande', 'VALEUR_MARCHANDE',
            'Valeur_Marchande', 'MARKET_VALUE', 'MarketValue'
        ]
        
        for col in possible_columns:
            if col in player_data.index and pd.notna(player_data.get(col)):
                value = player_data[col]
                if value != 0 and str(value).lower() not in ['nan', 'null', '', '0', 'none', 'n/a', 'na']:
                    formatted_value = Utils.format_market_value(value)
                    if formatted_value != "N/A":
                        return formatted_value
        
        return "N/A"
    
    @staticmethod
    def image_to_base64(image: Image.Image) -> str:
        """Convertit une image PIL en base64"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()

# ================================================================================================
# GESTIONNAIRE DE DONNÉES AMÉLIORÉ
# ================================================================================================

class DataManager:
    """Gestionnaire centralisé pour les données"""
    
    @staticmethod
    @st.cache_data
    def load_data(file_path: str = 'df_BIG2025.csv') -> Optional[pd.DataFrame]:
        """Charge les données depuis le fichier CSV"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8', delimiter=';')
            return df
        except FileNotFoundError:
            st.error(f"❌ Fichier '{file_path}' non trouvé.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement : {str(e)}")
            return None
    
    @staticmethod
    def filter_by_competition(df: pd.DataFrame, competition: str) -> pd.DataFrame:
        """Filtre les données par compétition"""
        return df[df['Compétition'] == competition]
    
    @staticmethod
    def filter_by_minutes(df: pd.DataFrame, min_minutes: int) -> pd.DataFrame:
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
    
    @staticmethod
    def get_other_leagues_data(df: pd.DataFrame, player_competition: str) -> pd.DataFrame:
        """Récupère les données de toutes les autres ligues"""
        return df[df['Compétition'] != player_competition]

# ================================================================================================
# GESTIONNAIRE D'IMAGES AMÉLIORÉ
# ================================================================================================

class ImageManager:
    """Gestionnaire pour les images"""
    
    @staticmethod
    def get_player_photo(player_name: str) -> Optional[str]:
        """Récupère le chemin de la photo du joueur"""
        extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG']
        
        for ext in extensions:
            photo_path = f"images_joueurs/{player_name}{ext}"
            if os.path.exists(photo_path):
                return photo_path
        
        for ext in extensions:
            pattern = f"images_joueurs/*{player_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
        
        return None
    
    @staticmethod
    def get_club_logo(competition: str, team_name: str) -> Optional[str]:
        """Récupère le chemin du logo du club"""
        folder = Config.LOGO_FOLDERS.get(competition)
        if not folder:
            return None
        
        extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
        
        for ext in extensions:
            logo_path = f"{folder}/{team_name}{ext}"
            if os.path.exists(logo_path):
                return logo_path
        
        return None

# ================================================================================================
# COMPOSANTS UI MODERNES
# ================================================================================================

class ModernUIComponents:
    """Composants d'interface utilisateur ultra-modernes"""
    
    @staticmethod
    def render_custom_sidebar(df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
        """Rendu de la sidebar personnalisée"""
        
        # Conteneur principal de la sidebar
        sidebar_html = f"""
        <div class="sidebar-custom animate-slide-in">
            <div class="sidebar-header">
                <h2 class="sidebar-title">
                    <i class="fas fa-cogs"></i> Configuration
                </h2>
                <p class="sidebar-subtitle">Sélectionnez votre analyse</p>
            </div>
        """
        
        st.markdown(sidebar_html, unsafe_allow_html=True)
        
        # Sélection de la compétition avec style personnalisé
        st.markdown("""
        <div class="custom-select">
            <label><i class="fas fa-trophy"></i> Compétition</label>
        </div>
        """, unsafe_allow_html=True)
        
        competitions = DataManager.get_competitions(df)
        selected_competition = st.selectbox(
            "", 
            competitions,
            index=0,
            key="comp_select",
            label_visibility="collapsed"
        )
        
        df_filtered = DataManager.filter_by_competition(df, selected_competition)
        
        # Filtre par minutes avec slider personnalisé
        st.markdown("""
        <div class="custom-select">
            <label><i class="fas fa-clock"></i> Minutes Jouées (Minimum)</label>
        </div>
        """, unsafe_allow_html=True)
        
        min_minutes_filter = 0
        if not df_filtered['Minutes jouées'].empty:
            min_minutes = int(df_filtered['Minutes jouées'].min())
            max_minutes = int(df_filtered['Minutes jouées'].max())
            
            min_minutes_filter = st.slider(
                "",
                min_value=min_minutes,
                max_value=max_minutes,
                value=min_minutes,
                step=90,
                label_visibility="collapsed"
            )
        
        df_filtered_minutes = DataManager.filter_by_minutes(df_filtered, min_minutes_filter)
        nb_joueurs = len(df_filtered_minutes)
        
        # Statistiques du filtrage
        st.markdown(f"""
        <div class="modern-card" style="margin: 1rem 0; padding: 1rem;">
            <div class="metrics-grid" style="grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                <div class="metric-card-modern" style="padding: 1rem;">
                    <div class="metric-value-modern" style="font-size: 1.5rem;">{nb_joueurs}</div>
                    <div class="metric-label-modern">Joueurs</div>
                </div>
                <div class="metric-card-modern" style="padding: 1rem;">
                    <div class="metric-value-modern" style="font-size: 1.5rem;">{df_filtered_minutes['Équipe'].nunique()}</div>
                    <div class="metric-label-modern">Équipes</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection du joueur
        st.markdown("""
        <div class="custom-select">
            <label><i class="fas fa-user"></i> Joueur</label>
        </div>
        """, unsafe_allow_html=True)
        
        selected_player = None
        if not df_filtered_minutes.empty:
            # Recherche de joueur
            search_term = st.text_input(
                "", 
                placeholder="🔍 Rechercher un joueur...",
                key="player_search",
                label_visibility="collapsed"
            )
            
            joueurs = DataManager.get_players(df_filtered_minutes)
            if search_term:
                joueurs = [j for j in joueurs if search_term.lower() in j.lower()]
            
            if joueurs:
                selected_player = st.selectbox(
                    "",
                    joueurs,
                    index=0,
                    key="player_select",
                    label_visibility="collapsed"
                )
        
        # Footer de la sidebar
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 1.5rem; margin-top: 2rem;">
            <h4 style="color: var(--primary); margin: 0 0 0.5rem 0;">
                <i class="fas fa-chart-line"></i> Analytics Pro
            </h4>
            <p style="color: var(--text-muted); margin: 0; font-size: 0.8rem;">
                Analyse Football Avancée
            </p>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        return selected_competition, selected_player, df_filtered_minutes
    
    @staticmethod
    def render_player_hero(player_data: pd.Series, competition: str):
        """Affiche le hero section du joueur"""
        valeur_marchande = Utils.get_market_value_safe(player_data)
        
        # Photo du joueur
        photo_html = ""
        photo_path = ImageManager.get_player_photo(player_data['Joueur'])
        if photo_path and os.path.exists(photo_path):
            try:
                image = Image.open(photo_path)
                photo_base64 = Utils.image_to_base64(image)
                photo_html = f"""
                <div style="position: absolute; top: 1rem; left: 1rem; width: 80px; height: 80px; 
                           border-radius: 50%; overflow: hidden; border: 3px solid rgba(255,255,255,0.3);">
                    <img src="data:image/jpeg;base64,{photo_base64}" 
                         style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                """
            except Exception:
                pass
        
        # Logo du club
        logo_html = ""
        logo_path = ImageManager.get_club_logo(competition, player_data['Équipe'])
        if logo_path and os.path.exists(logo_path):
            try:
                image = Image.open(logo_path)
                logo_base64 = Utils.image_to_base64(image)
                logo_html = f"""
                <div style="position: absolute; top: 1rem; right: 1rem; width: 60px; height: 60px;">
                    <img src="data:image/png;base64,{logo_base64}" 
                         style="width: 100%; height: 100%; object-fit: contain;">
                </div>
                """
            except Exception:
                pass
        
        st.markdown(f"""
        <div class="player-hero animate-fade-in">
            {photo_html}
            {logo_html}
            <h1 class="player-name">{player_data['Joueur']}</h1>
            <p class="player-subtitle">
                <i class="fas fa-map-marker-alt"></i> {player_data['Position']} • 
                <i class="fas fa-flag"></i> {player_data['Nationalité']} • 
                <i class="fas fa-calendar"></i> {player_data['Âge']} ans
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Métriques principales
        st.markdown(f"""
        <div class="metrics-grid animate-fade-in">
            <div class="metric-card-modern">
                <div class="metric-value-modern">
                    <i class="fas fa-running"></i> {int(player_data['Minutes jouées'])}
                </div>
                <div class="metric-label-modern">Minutes Jouées</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">
                    <i class="fas fa-euro-sign"></i> {valeur_marchande}
                </div>
                <div class="metric-label-modern">Valeur Marchande</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">
                    <i class="fas fa-shield-alt"></i> {player_data['Équipe']}
                </div>
                <div class="metric-label-modern">Équipe</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">
                    <i class="fas fa-trophy"></i> {competition}
                </div>
                <div class="metric-label-modern">Compétition</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_custom_tabs():
        """Rendu des onglets personnalisés avec JavaScript"""
        st.markdown("""
        <div class="custom-tabs" id="customTabs">
            <button class="custom-tab active" onclick="switchTab(0)" id="tab0">
                <i class="fas fa-crosshairs"></i> Performance Offensive
            </button>
            <button class="custom-tab" onclick="switchTab(1)" id="tab1">
                <i class="fas fa-shield-alt"></i> Performance Défensive
            </button>
            <button class="custom-tab" onclick="switchTab(2)" id="tab2">
                <i class="fas fa-magic"></i> Performance Technique
            </button>
            <button class="custom-tab" onclick="switchTab(3)" id="tab3">
                <i class="fas fa-users"></i> Profils Similaires
            </button>
            <button class="custom-tab" onclick="switchTab(4)" id="tab4">
                <i class="fas fa-exchange-alt"></i> Comparaison
            </button>
        </div>
        
        <script>
        function switchTab(tabIndex) {
            // Retirer la classe active de tous les onglets
            document.querySelectorAll('.custom-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Ajouter la classe active à l'onglet sélectionné
            document.getElementById('tab' + tabIndex).classList.add('active');
            
            // Stocker l'onglet actif dans le sessionStorage
            sessionStorage.setItem('activeTab', tabIndex);
        }
        
        // Restaurer l'onglet actif au chargement de la page
        document.addEventListener('DOMContentLoaded', function() {
            const activeTab = sessionStorage.getItem('activeTab') || 0;
            switchTab(parseInt(activeTab));
        });
        </script>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_loading_state(message: str = "Chargement en cours..."):
        """Affiche un état de chargement moderne"""
        st.markdown(f"""
        <div class="modern-card" style="text-align: center; padding: 3rem;">
            <div class="loading-spinner" style="margin: 0 auto 1rem auto;"></div>
            <h3 style="color: var(--text-secondary); margin: 0; font-weight: 500;">
                {message}
            </h3>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# CALCULATEUR DE MÉTRIQUES AMÉLIORÉ
# ================================================================================================

class MetricsCalculator:
    """Calculateur de métriques et percentiles amélioré"""
    
    @staticmethod
    def calculate_percentiles(player_name: str, df: pd.DataFrame) -> List[int]:
        """Calcule les percentiles pour le pizza chart"""
        player = df[df["Joueur"] == player_name].iloc[0]
        percentiles = []

        for label, col in Config.RADAR_METRICS.items():
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

# ================================================================================================
# ANALYSEUR DE JOUEURS SIMILAIRES AMÉLIORÉ
# ================================================================================================

class SimilarPlayerAnalyzer:
    """Analyseur pour trouver des joueurs similaires amélioré"""
    
    @staticmethod
    def calculate_similarity(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Calcule la similarité entre joueurs"""
        try:
            # Préparer les données
            similarity_df, available_metrics = SimilarPlayerAnalyzer.prepare_similarity_data(df)
            
            if similarity_df.empty or not available_metrics:
                return []
            
            # Obtenir les données du joueur cible
            target_data = similarity_df[similarity_df['Joueur'] == target_player]
            if target_data.empty:
                return []
            
            target_values = target_data[available_metrics].iloc[0]
            
            # Filtrer les autres joueurs
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                return []
            
            # Calcul de similarité simple
            similarities = []
            
            for idx, player_row in other_players.iterrows():
                player_values = player_row[available_metrics]
                
                # Calculer la similarité
                total_diff = 0
                valid_metrics = 0
                
                for metric in available_metrics:
                    target_val = float(target_values[metric])
                    player_val = float(player_values[metric])
                    
                    # Normalisation simple
                    max_val = max(target_val, player_val, 1)
                    diff = abs(target_val - player_val) / max_val
                    
                    total_diff += diff
                    valid_metrics += 1
                
                if valid_metrics > 0:
                    avg_diff = total_diff / valid_metrics
                    similarity_score = max(0, 100 * (1 - avg_diff))
                else:
                    similarity_score = 0
                
                similarities.append({
                    'joueur': player_row['Joueur'],
                    'equipe': player_row['Équipe'],
                    'competition': player_row['Compétition'],
                    'position': player_row['Position'],
                    'age': player_row['Âge'],
                    'similarity_score': similarity_score,
                    'data': player_row
                })
            
            # Trier par score de similarité
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similarities[:num_similar]
            
        except Exception as e:
            st.error(f"Erreur lors du calcul de similarité : {str(e)}")
            return []
    
    @staticmethod
    def prepare_similarity_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Prépare les données pour l'analyse de similarité"""
        available_metrics = []
        for metric in Config.SIMILARITY_METRICS:
            if metric in df.columns:
                available_metrics.append(metric)
        
        if not available_metrics:
            return pd.DataFrame(), []
        
        required_cols = ['Joueur', 'Équipe', 'Compétition', 'Position', 'Âge']
        similarity_df = df[required_cols + available_metrics].copy()
        
        # Remplacer les valeurs manquantes par 0
        for col in available_metrics:
            similarity_df[col] = pd.to_numeric(similarity_df[col], errors='coerce').fillna(0)
        
        similarity_df = similarity_df.dropna(subset=['Joueur'])
        similarity_df = similarity_df.drop_duplicates(subset=['Joueur'], keep='first')
        
        return similarity_df, available_metrics

# ================================================================================================
# GESTIONNAIRE DE GRAPHIQUES AMÉLIORÉ
# ================================================================================================

class ChartManager:
    """Gestionnaire centralisé pour les graphiques amélioré"""
    
    @staticmethod
    def create_modern_chart(data: Dict[str, float], title: str, chart_type: str = 'bar') -> go.Figure:
        """Crée un graphique moderne avec le nouveau style"""
        if chart_type == 'bar':
            fig = go.Figure(data=[go.Bar(
                x=list(data.keys()),
                y=list(data.values()),
                marker=dict(
                    color=Config.COLORS['gradient'],
                    line=dict(color='rgba(255,255,255,0.1)', width=1),
                    cornerradius=8
                ),
                text=[f"{v:.1f}" for v in data.values()],
                textposition='outside',
                textfont=dict(color='#f1f5f9', size=14, family='Inter')
            )])
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, color='#f1f5f9', family='Inter', weight=700),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                tickfont=dict(color='#cbd5e1', size=12, family='Inter'),
                tickangle=45,
                showgrid=False,
                linecolor='#475569'
            ),
            yaxis=dict(
                tickfont=dict(color='#cbd5e1', size=12, family='Inter'),
                gridcolor='rgba(203, 213, 225, 0.1)',
                showgrid=True,
                linecolor='#475569'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', family='Inter'),
            height=450,
            margin=dict(t=80, b=80, l=60, r=60)
        )
        
        return fig

# ================================================================================================
# APPLICATION PRINCIPALE MODERNISÉE
# ================================================================================================

class ModernFootballDashboard:
    """Classe principale de l'application modernisée"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self._configure_page()
        self._load_styles()
    
    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(**Config.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS personnalisés"""
        st.markdown(AdvancedStyleManager.get_custom_css(), unsafe_allow_html=True)
    
    def run(self):
        """Méthode principale d'exécution de l'application"""
        # Chargement des données avec état de loading moderne
        with st.spinner(""):
            ModernUIComponents.render_loading_state("Chargement des données...")
            df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        # Structure principale de l'application
        st.markdown('<div class="app-container">', unsafe_allow_html=True)
        
        # Navbar personnalisée
        AdvancedStyleManager.render_custom_navbar(df)
        
        # Sidebar personnalisée (maintenant intégrée dans le layout)
        selected_competition, selected_player, df_filtered = ModernUIComponents.render_custom_sidebar(df)
        
        # Contenu principal
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        if selected_player:
            # Données du joueur
            player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
            
            # Hero section du joueur
            ModernUIComponents.render_player_hero(player_data, selected_competition)
            
            # Navigation par onglets personnalisée
            ModernUIComponents.render_custom_tabs()
            
            # Contenu des onglets (utilisation des onglets Streamlit mais masqués)
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Offensive", "Défensive", "Technique", "Similaires", "Comparaison"])
            
            with tab1:
                self._render_offensive_analysis(player_data, df, selected_competition)
            
            with tab2:
                self._render_defensive_analysis(player_data, df, selected_competition)
            
            with tab3:
                self._render_technical_analysis(player_data, df, selected_competition)
            
            with tab4:
                self._render_similar_players_analysis(selected_player, df)
            
            with tab5:
                self._render_comparison_analysis(df, selected_player)
        
        else:
            self._render_no_player_selected()
        
        st.markdown('</div>', unsafe_allow_html=True)  # fin main-content
        st.markdown('</div>', unsafe_allow_html=True)  # fin app-container
    
    def _render_offensive_analysis(self, player_data: pd.Series, df: pd.DataFrame, competition: str):
        """Analyse offensive moderne"""
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        
        # Métriques offensives principales
        offensive_metrics = {
            'Buts': player_data.get('Buts', 0),
            'Passes décisives': player_data.get('Passes décisives', 0),
            'Tirs': player_data.get('Tirs', 0),
            'Passes clés': player_data.get('Passes clés', 0)
        }
        
        fig = ChartManager.create_modern_chart(
            offensive_metrics, 
            "🎯 Performance Offensive - Actions Totales",
            'bar'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Métriques par 90 minutes
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        st.markdown(f"""
        <div class="metrics-grid" style="margin: 2rem 0;">
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Buts', 0) / minutes_90:.2f}</div>
                <div class="metric-label-modern">Buts / 90min</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Passes décisives', 0) / minutes_90:.2f}</div>
                <div class="metric-label-modern">Passes D. / 90min</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Tirs', 0) / minutes_90:.2f}</div>
                <div class="metric-label-modern">Tirs / 90min</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Passes clés', 0) / minutes_90:.2f}</div>
                <div class="metric-label-modern">Passes Clés / 90min</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_defensive_analysis(self, player_data: pd.Series, df: pd.DataFrame, competition: str):
        """Analyse défensive moderne"""
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        
        defensive_metrics = {
            'Tacles': player_data.get('Tacles gagnants', 0),
            'Interceptions': player_data.get('Interceptions', 0),
            'Ballons récupérés': player_data.get('Ballons récupérés', 0),
            'Duels aériens': player_data.get('Duels aériens gagnés', 0)
        }
        
        fig = ChartManager.create_modern_chart(
            defensive_metrics, 
            "🛡️ Performance Défensive - Actions Totales",
            'bar'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        st.markdown(f"""
        <div class="metrics-grid" style="margin: 2rem 0;">
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Tacles gagnants', 0) / minutes_90:.2f}</div>
                <div class="metric-label-modern">Tacles / 90min</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Interceptions', 0) / minutes_90:.2f}</div>
                <div class="metric-label-modern">Interceptions / 90min</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Pourcentage de duels gagnés', 0):.1f}%</div>
                <div class="metric-label-modern">% Duels Gagnés</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Pourcentage de duels aériens gagnés', 0):.1f}%</div>
                <div class="metric-label-modern">% Duels Aériens</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_technical_analysis(self, player_data: pd.Series, df: pd.DataFrame, competition: str):
        """Analyse technique moderne"""
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        
        technical_metrics = {
            'Passes tentées': player_data.get('Passes tentées', 0),
            'Dribbles tentés': player_data.get('Dribbles tentés', 0),
            'Touches': player_data.get('Touches de balle', 0),
            'Passes progressives': player_data.get('Passes progressives', 0)
        }
        
        fig = ChartManager.create_modern_chart(
            technical_metrics, 
            "🎨 Performance Technique - Actions Totales",
            'bar'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"""
        <div class="metrics-grid" style="margin: 2rem 0;">
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Pourcentage de passes réussies', 0):.1f}%</div>
                <div class="metric-label-modern">% Passes Réussies</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Pourcentage de dribbles réussis', 0):.1f}%</div>
                <div class="metric-label-modern">% Dribbles Réussis</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Passes progressives', 0)}</div>
                <div class="metric-label-modern">Passes Progressives</div>
            </div>
            <div class="metric-card-modern">
                <div class="metric-value-modern">{player_data.get('Passes dans le dernier tiers', 0)}</div>
                <div class="metric-label-modern">Passes Dernier Tiers</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_similar_players_analysis(self, selected_player: str, df: pd.DataFrame):
        """Analyse des joueurs similaires moderne"""
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        
        # Configuration
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            <div class="modern-card">
                <h3 style="color: var(--primary); margin: 0 0 1rem 0;">
                    <i class="fas fa-search"></i> Analyse de Similarité
                </h3>
                <p style="color: var(--text-secondary); margin: 0;">
                    Utilise 20+ métriques pour identifier des profils de jeu similaires
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            num_similar = st.slider("Nombre de joueurs", 1, 10, 5)
        
        # Calcul des joueurs similaires
        with st.spinner(""):
            ModernUIComponents.render_loading_state("Recherche de profils similaires...")
            similar_players = SimilarPlayerAnalyzer.calculate_similarity(selected_player, df, num_similar)
        
        if similar_players:
            # Affichage moderne des résultats
            st.markdown(f"""
            <div class="modern-card">
                <h3 style="color: var(--secondary); margin: 0 0 1rem 0;">
                    <i class="fas fa-users"></i> Top {len(similar_players)} Profils Similaires
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Cartes des joueurs similaires
            for i, player_info in enumerate(similar_players):
                similarity_score = player_info['similarity_score']
                
                # Couleur selon le score
                if similarity_score >= 85:
                    score_color = Config.COLORS['success']
                elif similarity_score >= 70:
                    score_color = Config.COLORS['warning']
                else:
                    score_color = Config.COLORS['primary']
                
                valeur_marchande = Utils.get_market_value_safe(player_info['data'])
                
                st.markdown(f"""
                <div class="modern-card" style="margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                        <div>
                            <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0; font-size: 1.25rem;">
                                #{i+1} {player_info['joueur']}
                            </h4>
                            <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                                <span style="color: var(--text-secondary);"><i class="fas fa-shield-alt"></i> {player_info['equipe']}</span>
                                <span style="color: var(--text-secondary);"><i class="fas fa-trophy"></i> {player_info['competition']}</span>
                                <span style="color: var(--text-secondary);"><i class="fas fa-map-marker-alt"></i> {player_info['position']}</span>
                                <span style="color: var(--text-secondary);"><i class="fas fa-calendar"></i> {player_info['age']} ans</span>
                            </div>
                        </div>
                        <div style="text-align: center;">
                            <div style="background: {score_color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700;">
                                {similarity_score:.1f}% similaire
                            </div>
                            <div style="color: var(--accent); font-weight: 600; margin-top: 0.5rem;">
                                {valeur_marchande}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div class="modern-card" style="text-align: center; padding: 3rem;">
                <h3 style="color: var(--warning); margin: 0 0 1rem 0;">
                    <i class="fas fa-exclamation-triangle"></i> Aucun profil trouvé
                </h3>
                <p style="color: var(--text-secondary); margin: 0;">
                    Impossible de trouver des joueurs similaires avec les données disponibles.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_comparison_analysis(self, df: pd.DataFrame, selected_player: str):
        """Analyse comparative moderne"""
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: var(--primary); margin: 0 0 1rem 0;">
                <i class="fas fa-exchange-alt"></i> Analyse Comparative
            </h3>
            <p style="color: var(--text-secondary); margin: 0;">
                Comparez les performances avec d'autres joueurs ou la moyenne de la ligue
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuration de la comparaison
        competitions = sorted(df['Compétition'].dropna().unique())
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🥇 Joueur 1**")
            comp1 = st.selectbox("Compétition", competitions, key="comp1")
            df_comp1 = df[df['Compétition'] == comp1]
            player1 = st.selectbox("Joueur", df_comp1['Joueur'].sort_values(), 
                                 index=df_comp1['Joueur'].sort_values().tolist().index(selected_player) 
                                 if selected_player in df_comp1['Joueur'].values else 0, key="player1")
        
        with col2:
            st.markdown("**🥈 Joueur 2**")
            comp2 = st.selectbox("Compétition", competitions, key="comp2")
            df_comp2 = df[df['Compétition'] == comp2]
            player2 = st.selectbox("Joueur", df_comp2['Joueur'].sort_values(), key="player2")
        
        if player1 and player2 and player1 != player2:
            # Données des joueurs
            p1_data = df_comp1[df_comp1['Joueur'] == player1].iloc[0]
            p2_data = df_comp2[df_comp2['Joueur'] == player2].iloc[0]
            
            # Comparaison visuelle
            st.markdown(f"""
            <div class="modern-card">
                <h4 style="color: var(--accent); margin: 0 0 1.5rem 0; text-align: center;">
                    <i class="fas fa-vs"></i> {player1} vs {player2}
                </h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                    <div style="text-align: center;">
                        <h5 style="color: var(--primary); margin: 0 0 1rem 0;">{player1}</h5>
                        <div style="color: var(--text-secondary); margin-bottom: 0.5rem;">{comp1} • {p1_data['Équipe']}</div>
                        <div style="color: var(--text-secondary);">{p1_data['Position']} • {p1_data['Âge']} ans</div>
                    </div>
                    <div style="text-align: center;">
                        <h5 style="color: var(--secondary); margin: 0 0 1rem 0;">{player2}</h5>
                        <div style="color: var(--text-secondary); margin-bottom: 0.5rem;">{comp2} • {p2_data['Équipe']}</div>
                        <div style="color: var(--text-secondary);">{p2_data['Position']} • {p2_data['Âge']} ans</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Métriques de comparaison
            comparison_metrics = ['Buts', 'Passes décisives', 'Tirs', 'Passes clés', 'Minutes jouées']
            
            st.markdown('<div class="metrics-grid" style="margin: 2rem 0;">', unsafe_allow_html=True)
            
            for metric in comparison_metrics:
                val1 = p1_data.get(metric, 0)
                val2 = p2_data.get(metric, 0)
                
                winner_color = Config.COLORS['primary'] if val1 > val2 else Config.COLORS['secondary']
                
                st.markdown(f"""
                <div class="metric-card-modern">
                    <div class="metric-label-modern">{metric}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                        <span style="color: {'var(--primary)' if val1 > val2 else 'var(--text-secondary)'}; font-weight: {'700' if val1 > val2 else '500'};">
                            {val1}
                        </span>
                        <span style="color: var(--text-muted);">vs</span>
                        <span style="color: {'var(--secondary)' if val2 > val1 else 'var(--text-secondary)'}; font-weight: {'700' if val2 > val1 else '500'};">
                            {val2}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_no_player_selected(self):
        """Affiche le message quand aucun joueur n'est sélectionné"""
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 2rem; opacity: 0.5;">⚽</div>
            <h2 style="color: var(--primary); margin: 0 0 1rem 0; font-size: 2rem;">
                Sélectionnez un joueur pour commencer
            </h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem; margin: 0 0 2rem 0; line-height: 1.6;">
                Utilisez les filtres dans la sidebar pour choisir une compétition et un joueur à analyser.
            </p>
            
            <div class="metrics-grid" style="max-width: 800px; margin: 0 auto;">
                <div class="metric-card-modern" style="padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem; color: var(--primary);">🎯</div>
                    <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0;">Performance Offensive</h4>
                    <p style="color: var(--text-muted); margin: 0; font-size: 0.9rem;">Buts, passes, actions offensives</p>
                </div>
                <div class="metric-card-modern" style="padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem; color: var(--accent);">🛡️</div>
                    <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0;">Performance Défensive</h4>
                    <p style="color: var(--text-muted); margin: 0; font-size: 0.9rem;">Tacles, interceptions, duels</p>
                </div>
                <div class="metric-card-modern" style="padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem; color: var(--secondary);">🎨</div>
                    <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0;">Performance Technique</h4>
                    <p style="color: var(--text-muted); margin: 0; font-size: 0.9rem;">Passes, dribbles, technique</p>
                </div>
                <div class="metric-card-modern" style="padding: 2rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem; color: var(--warning);">👥</div>
                    <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0;">Profils Similaires</h4>
                    <p style="color: var(--text-muted); margin: 0; font-size: 0.9rem;">Joueurs au style proche</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_error_page(self):
        """Affiche la page d'erreur moderne"""
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 4rem 2rem; border-color: var(--danger);">
            <div style="font-size: 4rem; margin-bottom: 2rem; color: var(--danger);">⚠️</div>
            <h1 style="color: var(--danger); margin: 0 0 1rem 0; font-size: 2.5rem;">
                Erreur de Chargement
            </h1>
            <p style="color: var(--text-secondary); font-size: 1.1rem; margin: 0 0 2rem 0; line-height: 1.6;">
                Impossible de charger les données. Veuillez vérifier la présence du fichier de données.
            </p>
            
            <div class="modern-card" style="max-width: 600px; margin: 2rem auto 0 auto; padding: 2rem;">
                <h3 style="color: var(--secondary); margin: 0 0 1rem 0;">📋 Fichiers requis</h3>
                <div style="text-align: left; color: var(--text-primary);">
                    <div style="padding: 0.75rem 0; border-bottom: 1px solid var(--border-primary);">
                        <strong>df_BIG2025.csv</strong> - Données principales
                    </div>
                    <div style="padding: 0.75rem 0; border-bottom: 1px solid var(--border-primary);">
                        <strong>images_joueurs/</strong> - Photos des joueurs
                    </div>
                    <div style="padding: 0.75rem 0;">
                        <strong>*_Logos/</strong> - Logos des équipes
                    </div>
                </div>
            </div>
            
            <button onclick="window.location.reload()" 
                    class="custom-button" style="margin-top: 2rem;">
                <i class="fas fa-redo"></i> Réessayer
            </button>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# ================================================================================================

def main():
    """Point d'entrée principal de l'application"""
    try:
        dashboard = ModernFootballDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"❌ Erreur inattendue : {str(e)}")
        
        with st.expander("🔍 Détails de l'erreur", expanded=False):
            import traceback
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
