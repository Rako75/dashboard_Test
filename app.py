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
        "initial_sidebar_state": "expanded"
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
# GESTIONNAIRE DE STYLES CSS MODERNE
# ================================================================================================

class ModernStyleManager:
    """Gestionnaire des styles CSS modernes et sûrs"""
    
    @staticmethod
    def get_modern_css() -> str:
        """Retourne le CSS moderne sans casser Streamlit"""
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
        }
        
        /* BASE STYLING */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background: linear-gradient(135deg, var(--bg-primary) 0%, #1a202c 50%, var(--bg-secondary) 100%) !important;
            color: var(--text-primary) !important;
        }
        
        /* MASQUER SEULEMENT LES ÉLÉMENTS NON ESSENTIELS */
        .stDeployButton,
        [data-testid="manage-app-button"],
        .stDecoration,
        #MainMenu,
        footer {
            display: none !important;
        }
        
        /* HEADER MODERNE */
        .main-header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            padding: 2rem;
            border-radius: var(--radius-2xl);
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: var(--shadow-xl);
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
        }
        
        .main-title {
            font-size: 3rem;
            font-weight: 900;
            color: white;
            margin: 0;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-subtitle {
            font-size: 1.25rem;
            color: rgba(255, 255, 255, 0.9);
            margin: 1rem 0 0 0;
            position: relative;
            z-index: 1;
        }
        
        /* SIDEBAR MODERNE */
        .sidebar .sidebar-content {
            background: var(--bg-secondary) !important;
            border-right: 1px solid var(--border-primary) !important;
        }
        
        .sidebar-header-custom {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            padding: 1.5rem;
            border-radius: var(--radius-xl);
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
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
        
        /* COMPOSANTS STREAMLIT STYLÉS */
        .stSelectbox > div > div {
            background: var(--bg-tertiary) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
        }
        
        .stSlider > div > div {
            background: var(--bg-tertiary) !important;
        }
        
        .stTextInput > div > div > input {
            background: var(--bg-tertiary) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        }
        
        /* MÉTRIQUES MODERNES */
        .metric-card-modern {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            text-align: center;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
            margin-bottom: 1rem;
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
        
        /* GRILLE DE MÉTRIQUES */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        /* PLAYER HERO SECTION */
        .player-hero {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            padding: 3rem 2rem;
            border-radius: var(--radius-2xl);
            text-align: center;
            margin-bottom: 3rem;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: var(--shadow-xl);
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
        
        /* CARTES MODERNES */
        .modern-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-xl);
            padding: 2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            transition: var(--transition);
            box-shadow: var(--shadow-md);
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
        
        /* NAVIGATION TABS STYLÉE */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--bg-secondary) !important;
            border-radius: var(--radius-xl) !important;
            padding: 0.5rem !important;
            border: 1px solid var(--border-primary) !important;
            gap: 0.25rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border: none !important;
            border-radius: var(--radius-lg) !important;
            color: var(--text-muted) !important;
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            padding: 1rem 1.5rem !important;
            transition: var(--transition) !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: var(--bg-tertiary) !important;
            color: var(--text-secondary) !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--primary) !important;
            color: white !important;
            box-shadow: var(--shadow-md) !important;
        }
        
        /* MÉTRIQUES STREAMLIT STYLÉES */
        [data-testid="metric-container"] {
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-primary) !important;
            padding: 1rem !important;
            border-radius: var(--radius-lg) !important;
            box-shadow: var(--shadow-sm) !important;
        }
        
        [data-testid="metric-container"]:hover {
            border-color: var(--primary) !important;
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-md) !important;
        }
        
        [data-testid="metric-container"] > div {
            color: var(--text-primary) !important;
        }
        
        [data-testid="metric-container"] [data-testid="metric-value"] {
            color: var(--primary) !important;
            font-weight: 700 !important;
        }
        
        /* BOUTONS MODERNES */
        .stButton > button {
            background: var(--primary) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            transition: var(--transition) !important;
            box-shadow: var(--shadow-sm) !important;
        }
        
        .stButton > button:hover {
            background: #5b61d8 !important;
            transform: translateY(-1px) !important;
            box-shadow: var(--shadow-md) !important;
        }
        
        /* COLONNES STYLÉES */
        .stColumns > div {
            background: transparent !important;
            padding: 0.5rem !important;
        }
        
        /* TEXTE MODERNE */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        p, span, div {
            color: var(--text-secondary) !important;
        }
        
        /* PROGRESS BAR */
        .stProgress > div > div {
            background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
            border-radius: var(--radius-sm) !important;
        }
        
        /* EXPANDER */
        .streamlit-expanderHeader {
            background: var(--bg-tertiary) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
        }
        
        .streamlit-expanderContent {
            background: var(--bg-secondary) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: var(--radius-md) !important;
        }
        
        /* ALERTS ET MESSAGES */
        .stAlert {
            background: var(--bg-tertiary) !important;
            border: 1px solid var(--border-primary) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
        }
        
        .stSuccess {
            background: rgba(6, 214, 160, 0.1) !important;
            border-color: var(--success) !important;
        }
        
        .stWarning {
            background: rgba(251, 191, 36, 0.1) !important;
            border-color: var(--warning) !important;
        }
        
        .stError {
            background: rgba(239, 68, 68, 0.1) !important;
            border-color: var(--danger) !important;
        }
        
        .stInfo {
            background: rgba(99, 102, 241, 0.1) !important;
            border-color: var(--primary) !important;
        }
        
        /* ANIMATIONS */
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
        
        .animate-fade-in {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* RESPONSIVE DESIGN */
        @media (max-width: 768px) {
            .main-title {
                font-size: 2rem;
            }
            
            .player-name {
                font-size: 2rem;
            }
            
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }
            
            .modern-card {
                padding: 1rem;
            }
        }
        
        /* SCROLLBAR PERSONNALISÉE */
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

# ================================================================================================
# UTILITAIRES
# ================================================================================================

class Utils:
    """Fonctions utilitaires"""
    
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
            'Market_Value', 'Valeur_marchande'
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
# GESTIONNAIRE DE DONNÉES
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
        return df[df['Compétition'] == competition]
    
    @staticmethod
    def filter_by_minutes(df: pd.DataFrame, min_minutes: int) -> pd.DataFrame:
        return df[df['Minutes jouées'] >= min_minutes]
    
    @staticmethod
    def get_competitions(df: pd.DataFrame) -> List[str]:
        return sorted(df['Compétition'].dropna().unique())
    
    @staticmethod
    def get_players(df: pd.DataFrame) -> List[str]:
        return sorted(df['Joueur'].dropna().unique())
    
    @staticmethod
    def get_other_leagues_data(df: pd.DataFrame, player_competition: str) -> pd.DataFrame:
        return df[df['Compétition'] != player_competition]

# ================================================================================================
# GESTIONNAIRE D'IMAGES
# ================================================================================================

class ImageManager:
    """Gestionnaire pour les images"""
    
    @staticmethod
    def get_player_photo(player_name: str) -> Optional[str]:
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
# CALCULATEUR DE MÉTRIQUES
# ================================================================================================

class MetricsCalculator:
    """Calculateur de métriques et percentiles"""
    
    @staticmethod
    def calculate_percentiles(player_name: str, df: pd.DataFrame) -> List[int]:
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
# ANALYSEUR DE JOUEURS SIMILAIRES
# ================================================================================================

class SimilarPlayerAnalyzer:
    """Analyseur pour trouver des joueurs similaires"""
    
    @staticmethod
    def calculate_similarity(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        try:
            similarity_df, available_metrics = SimilarPlayerAnalyzer.prepare_similarity_data(df)
            
            if similarity_df.empty or not available_metrics:
                return []
            
            target_data = similarity_df[similarity_df['Joueur'] == target_player]
            if target_data.empty:
                return []
            
            target_values = target_data[available_metrics].iloc[0]
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                return []
            
            similarities = []
            
            for idx, player_row in other_players.iterrows():
                player_values = player_row[available_metrics]
                
                total_diff = 0
                valid_metrics = 0
                
                for metric in available_metrics:
                    target_val = float(target_values[metric])
                    player_val = float(player_values[metric])
                    
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
            
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similarities[:num_similar]
            
        except Exception as e:
            st.error(f"Erreur lors du calcul de similarité : {str(e)}")
            return []
    
    @staticmethod
    def prepare_similarity_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        available_metrics = []
        for metric in Config.SIMILARITY_METRICS:
            if metric in df.columns:
                available_metrics.append(metric)
        
        if not available_metrics:
            return pd.DataFrame(), []
        
        required_cols = ['Joueur', 'Équipe', 'Compétition', 'Position', 'Âge']
        similarity_df = df[required_cols + available_metrics].copy()
        
        for col in available_metrics:
            similarity_df[col] = pd.to_numeric(similarity_df[col], errors='coerce').fillna(0)
        
        similarity_df = similarity_df.dropna(subset=['Joueur'])
        similarity_df = similarity_df.drop_duplicates(subset=['Joueur'], keep='first')
        
        return similarity_df, available_metrics

# ================================================================================================
# GESTIONNAIRE DE GRAPHIQUES
# ================================================================================================

class ChartManager:
    """Gestionnaire centralisé pour les graphiques"""
    
    @staticmethod
    def create_modern_chart(data: Dict[str, float], title: str, chart_type: str = 'bar') -> go.Figure:
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
# COMPOSANTS UI MODERNES
# ================================================================================================

class ModernUIComponents:
    """Composants d'interface utilisateur modernes"""
    
    @staticmethod
    def render_main_header():
        """Affiche l'en-tête principal moderne"""
        st.markdown("""
        <div class='main-header animate-fade-in'>
            <h1 class='main-title'>
                <i class="fas fa-futbol"></i> Football Analytics Pro
            </h1>
            <p class='main-subtitle'>
                Analyse avancée des performances footballistiques - Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_header():
        """Affiche l'en-tête de la sidebar"""
        st.markdown("""
        <div class='sidebar-header-custom'>
            <h2 class='sidebar-title'>
                <i class="fas fa-cogs"></i> Configuration
            </h2>
            <p class='sidebar-subtitle'>Sélectionnez votre analyse</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_hero(player_data: pd.Series, competition: str):
        """Affiche le hero section du joueur"""
        valeur_marchande = Utils.get_market_value_safe(player_data)
        
        # Photo et logo
        photo_html = ""
        logo_html = ""
        
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
        
        # Métriques principales avec Streamlit metrics stylées
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "⏱️ Minutes Jouées", 
                f"{int(player_data['Minutes jouées']):,}",
                help="Total des minutes jouées cette saison"
            )
        
        with col2:
            st.metric(
                "💰 Valeur Marchande", 
                valeur_marchande,
                help="Valeur marchande estimée"
            )
        
        with col3:
            st.metric(
                "🏟️ Équipe", 
                player_data['Équipe'],
                help="Club actuel"
            )
        
        with col4:
            st.metric(
                "🏆 Compétition", 
                competition,
                help="Championnat"
            )
    
    @staticmethod
    def render_similar_player_card(player_info: Dict, rank: int):
        """Affiche une carte de joueur similaire moderne"""
        similarity_score = player_info['similarity_score']
        player_data = player_info['data']
        
        if similarity_score >= 85:
            score_color = Config.COLORS['success']
        elif similarity_score >= 70:
            score_color = Config.COLORS['warning']
        else:
            score_color = Config.COLORS['primary']
        
        valeur_marchande = Utils.get_market_value_safe(player_data)
        
        st.markdown(f"""
        <div class="modern-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                <div>
                    <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0; font-size: 1.25rem;">
                        #{rank} {player_info['joueur']}
                    </h4>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                        <span style="color: var(--text-secondary);"><i class="fas fa-shield-alt"></i> {player_info['equipe']}</span>
                        <span style="color: var(--text-secondary);"><i class="fas fa-trophy"></i> {player_info['competition']}</span>
                        <span style="color: var(--text-secondary);"><i class="fas fa-map-marker-alt"></i> {player_info['position']}</span>
                        <span style="color: var(--text-secondary);"><i class="fas fa-calendar"></i> {player_info['age']} ans</span>
                    </div>
                </div>
                <div style="text-align: center;">
                    <div style="background: {score_color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700; margin-bottom: 0.5rem;">
                        {similarity_score:.1f}% similaire
                    </div>
                    <div style="color: var(--accent); font-weight: 600;">
                        {valeur_marchande}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# APPLICATION PRINCIPALE
# ================================================================================================

class ModernFootballDashboard:
    """Classe principale de l'application moderne"""
    
    def __init__(self):
        self._configure_page()
        self._load_styles()
    
    def _configure_page(self):
        st.set_page_config(**Config.PAGE_CONFIG)
    
    def _load_styles(self):
        st.markdown(ModernStyleManager.get_modern_css(), unsafe_allow_html=True)
    
    def run(self):
        # Chargement des données
        df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        # En-tête principal
        ModernUIComponents.render_main_header()
        
        # Affichage des statistiques générales
        self._render_data_overview(df)
        
        # Sidebar avec sélections
        selected_competition, selected_player, df_filtered = self._render_modern_sidebar(df)
        
        if selected_player:
            # Données du joueur
            player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
            
            # Hero section du joueur
            ModernUIComponents.render_player_hero(player_data, selected_competition)
            
            # Onglets d'analyse
            self._render_analysis_tabs(player_data, df, selected_competition, selected_player)
        
        else:
            self._render_no_player_selected()
    
    def _render_data_overview(self, df: pd.DataFrame):
        """Aperçu des données avec métriques stylées"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("👥 Joueurs", f"{len(df):,}")
        
        with col2:
            st.metric("🏆 Compétitions", f"{df['Compétition'].nunique()}")
        
        with col3:
            st.metric("⚽ Équipes", f"{df['Équipe'].nunique()}")
        
        with col4:
            total_minutes = df['Minutes jouées'].sum()
            st.metric("⏱️ Minutes", f"{total_minutes:,.0f}")
        
        with col5:
            avg_age = df['Âge'].mean()
            st.metric("📅 Âge Moyen", f"{avg_age:.1f} ans")
    
    def _render_modern_sidebar(self, df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
        """Rendu de la sidebar moderne"""
        with st.sidebar:
            ModernUIComponents.render_sidebar_header()
            
            # Sélection de la compétition
            st.markdown("**🏆 Compétition**")
            competitions = DataManager.get_competitions(df)
            selected_competition = st.selectbox(
                "", 
                competitions,
                index=0,
                label_visibility="collapsed"
            )
            
            df_filtered = DataManager.filter_by_competition(df, selected_competition)
            
            st.markdown("---")
            
            # Filtre par minutes
            st.markdown("**⏱️ Minutes Jouées (Minimum)**")
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
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Joueurs", nb_joueurs)
            with col2:
                st.metric("Équipes", df_filtered_minutes['Équipe'].nunique())
            
            st.markdown("---")
            
            # Sélection du joueur
            st.markdown("**👤 Joueur**")
            selected_player = None
            if not df_filtered_minutes.empty:
                search_term = st.text_input(
                    "", 
                    placeholder="🔍 Rechercher un joueur...",
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
                        label_visibility="collapsed"
                    )
            
            # Footer sidebar
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; padding: 1rem; background: var(--bg-tertiary); border-radius: 12px;">
                <h4 style="color: var(--primary); margin: 0 0 0.5rem 0;">
                    <i class="fas fa-chart-line"></i> Analytics Pro
                </h4>
                <p style="color: var(--text-muted); margin: 0; font-size: 0.8rem;">
                    Analyse Football Avancée
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            return selected_competition, selected_player, df_filtered_minutes
    
    def _render_analysis_tabs(self, player_data: pd.Series, df: pd.DataFrame, 
                             competition: str, selected_player: str):
        """Rendu des onglets d'analyse"""
        
        df_other_leagues = DataManager.get_other_leagues_data(df, competition)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Performance Offensive", 
            "🛡️ Performance Défensive", 
            "🎨 Performance Technique",
            "👥 Profils Similaires", 
            "🔄 Comparaison"
        ])
        
        with tab1:
            self._render_offensive_analysis(player_data, df_other_leagues)
        
        with tab2:
            self._render_defensive_analysis(player_data, df_other_leagues)
        
        with tab3:
            self._render_technical_analysis(player_data, df_other_leagues)
        
        with tab4:
            self._render_similar_players_analysis(selected_player, df)
        
        with tab5:
            self._render_comparison_analysis(df, selected_player)
    
    def _render_offensive_analysis(self, player_data: pd.Series, df_comparison: pd.DataFrame):
        """Analyse offensive"""
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: var(--primary); margin: 0 0 1rem 0;">
                🎯 Analyse Performance Offensive
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Métriques offensives
        offensive_metrics = {
            'Buts': player_data.get('Buts', 0),
            'Passes décisives': player_data.get('Passes décisives', 0),
            'Tirs': player_data.get('Tirs', 0),
            'Passes clés': player_data.get('Passes clés', 0)
        }
        
        fig = ChartManager.create_modern_chart(
            offensive_metrics, 
            "Actions Offensives Totales"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Métriques par 90 minutes
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Buts / 90min", f"{player_data.get('Buts', 0) / minutes_90:.2f}")
        
        with col2:
            st.metric("Passes D. / 90min", f"{player_data.get('Passes décisives', 0) / minutes_90:.2f}")
        
        with col3:
            st.metric("Tirs / 90min", f"{player_data.get('Tirs', 0) / minutes_90:.2f}")
        
        with col4:
            st.metric("Passes Clés / 90min", f"{player_data.get('Passes clés', 0) / minutes_90:.2f}")
    
    def _render_defensive_analysis(self, player_data: pd.Series, df_comparison: pd.DataFrame):
        """Analyse défensive"""
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: var(--accent); margin: 0 0 1rem 0;">
                🛡️ Analyse Performance Défensive
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        defensive_metrics = {
            'Tacles': player_data.get('Tacles gagnants', 0),
            'Interceptions': player_data.get('Interceptions', 0),
            'Ballons récupérés': player_data.get('Ballons récupérés', 0),
            'Duels aériens': player_data.get('Duels aériens gagnés', 0)
        }
        
        fig = ChartManager.create_modern_chart(defensive_metrics, "Actions Défensives Totales")
        st.plotly_chart(fig, use_container_width=True)
        
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tacles / 90min", f"{player_data.get('Tacles gagnants', 0) / minutes_90:.2f}")
        
        with col2:
            st.metric("Interceptions / 90min", f"{player_data.get('Interceptions', 0) / minutes_90:.2f}")
        
        with col3:
            st.metric("% Duels Gagnés", f"{player_data.get('Pourcentage de duels gagnés', 0):.1f}%")
        
        with col4:
            st.metric("% Duels Aériens", f"{player_data.get('Pourcentage de duels aériens gagnés', 0):.1f}%")
    
    def _render_technical_analysis(self, player_data: pd.Series, df_comparison: pd.DataFrame):
        """Analyse technique"""
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: var(--secondary); margin: 0 0 1rem 0;">
                🎨 Analyse Performance Technique
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        technical_metrics = {
            'Passes tentées': player_data.get('Passes tentées', 0),
            'Dribbles tentés': player_data.get('Dribbles tentés', 0),
            'Touches': player_data.get('Touches de balle', 0),
            'Passes progressives': player_data.get('Passes progressives', 0)
        }
        
        fig = ChartManager.create_modern_chart(technical_metrics, "Actions Techniques Totales")
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("% Passes Réussies", f"{player_data.get('Pourcentage de passes réussies', 0):.1f}%")
        
        with col2:
            st.metric("% Dribbles Réussis", f"{player_data.get('Pourcentage de dribbles réussis', 0):.1f}%")
        
        with col3:
            st.metric("Passes Progressives", f"{player_data.get('Passes progressives', 0)}")
        
        with col4:
            st.metric("Passes Dernier Tiers", f"{player_data.get('Passes dans le dernier tiers', 0)}")
    
    def _render_similar_players_analysis(self, selected_player: str, df: pd.DataFrame):
        """Analyse des joueurs similaires"""
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: var(--secondary); margin: 0 0 1rem 0;">
                👥 Profils Similaires
            </h3>
            <p style="color: var(--text-secondary); margin: 0;">
                Utilise 20+ métriques pour identifier des profils de jeu similaires
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Configuration
        col1, col2 = st.columns([3, 1])
        
        with col2:
            num_similar = st.slider("Nombre de joueurs", 1, 10, 5)
        
        # Calcul des joueurs similaires
        with st.spinner("Recherche de profils similaires..."):
            similar_players = SimilarPlayerAnalyzer.calculate_similarity(selected_player, df, num_similar)
        
        if similar_players:
            st.success(f"✅ {len(similar_players)} profils trouvés !")
            
            # Affichage des joueurs similaires
            for i, player_info in enumerate(similar_players):
                ModernUIComponents.render_similar_player_card(player_info, i + 1)
        
        else:
            st.warning("⚠️ Aucun profil similaire trouvé")
    
    def _render_comparison_analysis(self, df: pd.DataFrame, selected_player: str):
        """Analyse comparative"""
        st.markdown("""
        <div class="modern-card">
            <h3 style="color: var(--primary); margin: 0 0 1rem 0;">
                🔄 Analyse Comparative
            </h3>
            <p style="color: var(--text-secondary); margin: 0;">
                Comparez les performances avec d'autres joueurs
            </p>
        </div>
        """, unsafe_allow_html=True)
        
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
            p1_data = df_comp1[df_comp1['Joueur'] == player1].iloc[0]
            p2_data = df_comp2[df_comp2['Joueur'] == player2].iloc[0]
            
            st.markdown(f"""
            <div class="modern-card">
                <h4 style="color: var(--accent); margin: 0 0 1.5rem 0; text-align: center;">
                    ⚔️ {player1} vs {player2}
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Comparaison des métriques principales
            comparison_metrics = ['Buts', 'Passes décisives', 'Tirs', 'Passes clés', 'Minutes jouées']
            
            for metric in comparison_metrics:
                val1 = p1_data.get(metric, 0)
                val2 = p2_data.get(metric, 0)
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    st.metric(f"{player1} - {metric}", f"{val1}", 
                             delta=f"{val1-val2}" if val1 > val2 else None)
                
                with col2:
                    st.markdown(f"<div style='text-align: center; padding: 1rem; color: var(--text-muted);'>{metric}</div>", 
                               unsafe_allow_html=True)
                
                with col3:
                    st.metric(f"{player2} - {metric}", f"{val2}",
                             delta=f"{val2-val1}" if val2 > val1 else None)
    
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
        </div>
        """, unsafe_allow_html=True)
    
    def _render_error_page(self):
        """Affiche la page d'erreur"""
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 4rem 2rem; border-color: var(--danger);">
            <div style="font-size: 4rem; margin-bottom: 2rem; color: var(--danger);">⚠️</div>
            <h1 style="color: var(--danger); margin: 0 0 1rem 0; font-size: 2.5rem;">
                Erreur de Chargement
            </h1>
            <p style="color: var(--text-secondary); font-size: 1.1rem; margin: 0 0 2rem 0;">
                Impossible de charger les données. Veuillez vérifier la présence du fichier 'df_BIG2025.csv'.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# POINT D'ENTRÉE
# ================================================================================================

def main():
    """Point d'entrée principal"""
    try:
        dashboard = ModernFootballDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")

if __name__ == "__main__":
    main()
