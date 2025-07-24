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
    st.warning("⚠️ scikit-learn n'est pas installé. La fonctionnalité de joueurs similaires sera limitée.")

# ================================================================================================
# CONFIGURATION ET CONSTANTES
# ================================================================================================

class Config:
    """Configuration centralisée de l'application - Version étendue"""
    
    # Configuration existante (à garder)...
    PAGE_CONFIG = {
        "page_title": "Dashboard Football Pro",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    COLORS = {
        'primary': '#1f77b4',
        'secondary': '#2ca02c',
        'accent': '#ff7f0e',
        'success': '#17a2b8',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'dark': '#212529',
        'light': '#f8f9fa',
        'gradient': ['#1f77b4', '#2ca02c', '#ff7f0e', '#17a2b8', '#ffc107']
    }
    
    # Nouveaux : types de références pour les radars
    REFERENCE_TYPES = {
        'median': {
            'name': 'Médiane (50e percentile)',
            'value': 50,
            'description': 'Niveau médian des joueurs du même poste',
            'color': '#6c757d'
        },
        'good_starter': {
            'name': 'Bon titulaire (60e percentile)',
            'value': 60,
            'description': 'Niveau d\'un bon joueur titulaire',
            'color': '#28a745'
        },
        'top_quartile': {
            'name': 'Bon niveau (75e percentile)',
            'value': 75,
            'description': 'Top 25% des joueurs du poste',
            'color': '#ffc107'
        },
        'top_10': {
            'name': 'Très haut niveau (90e percentile)',
            'value': 90,
            'description': 'Top 10% des joueurs du poste',
            'color': '#dc3545'
        }
    }
    
    # Métriques par domaine
    METRICS_DOMAINS = {
        'offensive': {
            'icon': '🎯',
            'color': '#1f77b4',
            'description': 'Métriques de création et finition'
        },
        'defensive': {
            'icon': '🛡️', 
            'color': '#ff7f0e',
            'description': 'Métriques de récupération et défense'
        },
        'technical': {
            'icon': '🎨',
            'color': '#2ca02c',
            'description': 'Métriques de technique et maîtrise'
        }
    }

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
        
        # Conversion en nombre si c'est une chaîne
        if isinstance(value, str):
            try:
                # Nettoyer la chaîne: enlever €, M, K, etc. et garder seulement les chiffres et le point décimal
                clean_value = value.replace('€', '').replace('M', '').replace('K', '').replace('B', '').replace(',', '').replace(' ', '')
                # Gérer les cas comme "50.5M" ou "2.3K"
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
            # Vérifier que la valeur est positive et raisonnable
            if value <= 0 or value > 1_000_000_000_000:  # Plus de 1000 milliards semble irréaliste
                return "N/A"
        except (ValueError, TypeError):
            return "N/A"
        
        # Formatage selon les seuils
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
        """Récupère la valeur marchande exacte depuis les données du joueur"""
        # Liste étendue des colonnes possibles pour la valeur marchande
        possible_columns = [
            'Valeur marchande', 'Market Value', 'valeur_marchande', 
            'Valeur', 'Value', 'market_value', 'Valeur en €', 'Valeur (€)',
            'Market_Value', 'Valeur_marchande', 'VALEUR_MARCHANDE',
            'Valeur_Marchande', 'MARKET_VALUE', 'MarketValue', 'market_val',
            'val_marchande', 'VM', 'vm', 'valeur_m', 'valeur_marche',
            'Transfer Value', 'transfer_value', 'Prix', 'price', 'Price'
        ]
        
        # Essayer de récupérer la vraie valeur marchande depuis les données exactes du joueur
        for col in possible_columns:
            if col in player_data.index and pd.notna(player_data.get(col)):
                value = player_data[col]
                # Vérifier que ce n'est pas une valeur vide ou zéro
                if value != 0 and str(value).lower() not in ['nan', 'null', '', '0', 'none', 'n/a', 'na']:
                    formatted_value = Utils.format_market_value(value)
                    if formatted_value != "N/A":
                        return formatted_value
        
        # Si aucune valeur trouvée, essayer les colonnes numériques qui pourraient être des valeurs marchandes
        for col in player_data.index:
            if any(keyword in col.lower() for keyword in ['val', 'market', 'price', 'prix', 'cost', 'worth']):
                if pd.notna(player_data.get(col)):
                    value = player_data[col]
                    if value != 0 and str(value).lower() not in ['nan', 'null', '', '0', 'none', 'n/a', 'na']:
                        formatted_value = Utils.format_market_value(value)
                        if formatted_value != "N/A":
                            return formatted_value
        
        # Dernière tentative : chercher des colonnes numériques avec des valeurs dans la fourchette des valeurs marchandes
        for col in player_data.index:
            if pd.notna(player_data.get(col)):
                try:
                    value = float(player_data[col])
                    # Valeurs typiques de valeurs marchandes (entre 50K et 200M)
                    if 50_000 <= value <= 200_000_000:
                        formatted_value = Utils.format_market_value(value)
                        if formatted_value != "N/A":
                            return formatted_value
                except (ValueError, TypeError):
                    continue
        
        # Si vraiment aucune valeur marchande trouvée, retourner N/A
        return "N/A"
    
    @staticmethod
    def image_to_base64(image: Image.Image) -> str:
        """Convertit une image PIL en base64"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> str:
        """Convertit une couleur hex en RGB"""
        hex_color = hex_color.lstrip('#')
        return ','.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))


class PositionUtils:
    """Utilitaires pour la gestion des postes et des comparaisons"""
    
    @staticmethod
    def get_position_display_name(position_code: str) -> str:
        """Convertit les codes de position en noms complets"""
        position_mapping = {
            'GK': 'Gardien de but',
            'DF': 'Défenseur', 
            'MF': 'Milieu de terrain',
            'FW': 'Attaquant'
        }
        return position_mapping.get(position_code, position_code)
    
    @staticmethod
    def get_position_emoji(position_code: str) -> str:
        """Retourne l'emoji correspondant au poste"""
        emoji_mapping = {
            'GK': '🥅',
            'DF': '🛡️', 
            'MF': '⚙️',
            'FW': '⚽'
        }
        return emoji_mapping.get(position_code, '👤')
    
    @staticmethod
    def get_position_color(position_code: str) -> str:
        """Retourne la couleur associée au poste"""
        color_mapping = {
            'GK': '#17a2b8',  # Cyan
            'DF': '#dc3545',  # Rouge
            'MF': '#28a745',  # Vert
            'FW': '#ffc107'   # Jaune
        }
        return color_mapping.get(position_code, '#6c757d')
    
    @staticmethod
    def get_position_stats(df: pd.DataFrame, position: str, min_minutes: int = 900) -> Dict:
        """Retourne des statistiques sur les joueurs d'un poste"""
        position_df = df[
            (df['Position'] == position) & 
            (df['Minutes jouées'] >= min_minutes)
        ]
        
        return {
            'count': len(position_df),
            'avg_age': position_df['Âge'].mean() if len(position_df) > 0 else 0,
            'avg_minutes': position_df['Minutes jouées'].mean() if len(position_df) > 0 else 0,
            'competitions': position_df['Compétition'].nunique() if len(position_df) > 0 else 0
        }


# ================================================================================================
# GESTIONNAIRE DE STYLES CSS
# ================================================================================================

class StyleManager:
    """Gestionnaire des styles CSS"""
    
    @staticmethod
    def get_css() -> str:
        """Retourne le CSS personnalisé"""
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #2ca02c;
            --accent-color: #ff7f0e;
            --background-dark: #0e1117;
            --background-card: #1a1d23;
            --background-surface: #262730;
            --text-primary: #ffffff;
            --text-secondary: #e2e8f0;
            --text-muted: #a0aec0;
            --border-color: #4a5568;
            --border-light: #2d3748;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --spacing-xs: 4px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
        }
        
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--background-dark) 0%, #1a1d23 100%);
            color: var(--text-primary);
        }
        
        .main .block-container {
            padding-top: var(--spacing-lg);
            padding-bottom: var(--spacing-lg);
            max-width: 1400px;
        }
        
        /* Onglets améliorés */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--background-card);
            border-radius: var(--radius-md);
            padding: var(--spacing-xs);
            margin-bottom: var(--spacing-lg);
            border: 2px solid var(--border-color);
            box-shadow: var(--shadow);
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: var(--text-secondary);
            border-radius: var(--radius-sm);
            font-weight: 500;
            font-size: 14px;
            transition: all 0.3s ease;
            border: none;
            padding: var(--spacing-md) var(--spacing-lg);
            margin: 0 var(--spacing-xs);
            position: relative;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(31, 119, 180, 0.1);
            color: var(--text-primary);
            transform: translateY(-1px);
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--primary-color);
            color: white;
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.4);
            font-weight: 600;
            border-bottom: 3px solid var(--accent-color);
        }
        
        /* Cartes joueur */
        .player-header-card {
            background: linear-gradient(135deg, var(--background-dark) 0%, #1a1d23 100%);
            padding: var(--spacing-xl);
            border-radius: var(--radius-lg);
            text-align: center;
            margin-bottom: var(--spacing-xl);
            box-shadow: var(--shadow-lg);
            border: 2px solid #fff;
        }
        
        .player-info-card {
            background: var(--background-card);
            padding: var(--spacing-xl);
            border-radius: var(--radius-lg);
            border: 2px solid var(--border-color);
            box-shadow: var(--shadow-lg);
            margin: var(--spacing-lg) 0;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .player-info-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
        }
        
        .player-metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--spacing-md);
            margin-top: var(--spacing-xl);
            max-width: 100%;
        }
        
        @media (max-width: 768px) {
            .player-metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 480px) {
            .player-metrics-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .metric-card-enhanced {
            background: var(--background-surface);
            padding: var(--spacing-md);
            border-radius: var(--radius-md);
            border: 1px solid var(--border-light);
            text-align: center;
            transition: all 0.3s ease;
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card-enhanced:hover {
            border-color: var(--primary-color);
            box-shadow: 0 8px 25px rgba(31, 119, 180, 0.3);
            transform: translateY(-3px);
        }
        
        .metric-value-enhanced {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: var(--spacing-xs);
            line-height: 1.2;
            word-break: break-word;
        }
        
        .metric-label-enhanced {
            font-size: 0.8rem;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            line-height: 1.3;
        }
        
        /* Cartes de joueurs similaires avec logo */
        .similar-player-card {
            background: var(--background-card);
            padding: var(--spacing-lg);
            border-radius: var(--radius-lg);
            border: 2px solid var(--border-color);
            box-shadow: var(--shadow);
            margin: var(--spacing-md) 0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .similar-player-card:hover {
            border-color: var(--secondary-color);
            box-shadow: 0 12px 30px rgba(44, 160, 44, 0.3);
            transform: translateY(-5px);
        }
        
        .similar-player-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--secondary-color), var(--accent-color));
        }
        
        .similarity-score {
            background: var(--secondary-color);
            color: white;
            padding: var(--spacing-xs) var(--spacing-md);
            border-radius: var(--radius-sm);
            font-weight: 600;
            font-size: 0.9em;
            position: absolute;
            top: var(--spacing-md);
            right: var(--spacing-md);
        }
        
        .player-header-with-logo {
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-md);
        }
        
        .club-logo-small {
            width: 40px;
            height: 40px;
            object-fit: contain;
            border-radius: var(--radius-sm);
            background: rgba(255, 255, 255, 0.1);
            padding: 4px;
        }
        
        /* Titres de sections */
        .section-title-enhanced {
            color: var(--text-primary);
            font-size: 2rem;
            font-weight: 800;
            text-align: center;
            margin: var(--spacing-xl) 0 var(--spacing-lg) 0;
            letter-spacing: -0.025em;
            position: relative;
            padding-bottom: var(--spacing-md);
        }
        
        .section-title-enhanced::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            border-radius: 2px;
        }
        
        .subsection-title-enhanced {
            color: var(--primary-color);
            font-size: 1.25rem;
            font-weight: 600;
            margin: var(--spacing-lg) 0 var(--spacing-md) 0;
            border-left: 4px solid var(--primary-color);
            padding-left: var(--spacing-md);
            letter-spacing: -0.025em;
        }
        
        /* Conteneurs d'images */
        .image-container {
            background: var(--background-surface);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            border: 2px solid var(--border-color);
            overflow: hidden;
            height: 320px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow-lg);
        }
        
        .club-logo-container {
            background: var(--background-surface);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            border: 2px solid var(--border-color);
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }
        
        .club-logo-container:hover {
            border-color: var(--primary-color);
            box-shadow: 0 8px 25px rgba(31, 119, 180, 0.3);
        }
        
        /* Légendes */
        .chart-legend {
            background: var(--background-surface);
            border: 1px solid var(--border-light);
            border-radius: var(--radius-sm);
            padding: var(--spacing-sm) var(--spacing-md);
            margin: var(--spacing-md) 0;
            display: inline-flex;
            align-items: center;
            gap: var(--spacing-md);
            font-size: 0.85rem;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        /* Breadcrumbs */
        .breadcrumbs {
            background: var(--background-surface);
            padding: 12px 20px;
            border-radius: var(--radius-sm);
            margin-bottom: 20px;
            border-left: 4px solid var(--primary-color);
        }
        
        /* Sidebar */
        .sidebar-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 20px;
            border-radius: var(--radius-md);
            text-align: center;
            margin-bottom: var(--spacing-lg);
        }
        
        /* Footer */
        .dashboard-footer {
            background: var(--background-card);
            padding: var(--spacing-lg);
            border-radius: var(--radius-md);
            text-align: center;
            margin-top: 40px;
            border: 1px solid var(--border-color);
        }
        
        /* Animations */
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
        
        .animated-card {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* Masquer éléments inutiles */
        .stDeployButton, .stDecoration, [data-testid="manage-app-button"] {
            display: none !important;
        }
        </style>
        """

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
        """Récupère les données de toutes les autres ligues (sauf celle du joueur)"""
        return df[df['Compétition'] != player_competition]

# ================================================================================================
# GESTIONNAIRE D'IMAGES
# ================================================================================================

class ImageManager:
    """Gestionnaire pour les images"""
    
    @staticmethod
    def get_player_photo(player_name: str) -> Optional[str]:
        """Récupère le chemin de la photo du joueur"""
        extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG']
        
        # Recherche directe
        for ext in extensions:
            photo_path = f"images_joueurs/{player_name}{ext}"
            if os.path.exists(photo_path):
                return photo_path
        
        # Recherche avec patterns
        for ext in extensions:
            pattern = f"images_joueurs/*{player_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
            # Essayer avec nom inversé
            if " " in player_name:
                parts = player_name.split(" ")
                if len(parts) >= 2:
                    reversed_name = " ".join(parts[::-1])
                    pattern = f"images_joueurs/*{reversed_name}*{ext}"
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
        
        # Recherche directe
        for ext in extensions:
            logo_path = f"{folder}/{team_name}{ext}"
            if os.path.exists(logo_path):
                return logo_path
        
        # Recherche avec patterns
        for ext in extensions:
            pattern = f"{folder}/*{team_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
            # Variations de nom
            clean_team = team_name.replace(" ", "_").replace("'", "").replace("-", "_")
            pattern = f"{folder}/*{clean_team}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
        
        return None

# ================================================================================================
# CALCULATEUR DE MÉTRIQUES
# ================================================================================================

class MetricsCalculator:
    """Calculateur de métriques (garder les méthodes existantes)"""
    
    @staticmethod
    def calculate_offensive_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques offensives"""
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        return {
            'Buts/90': player_data.get('Buts par 90 minutes', 0),
            'Passes D./90': player_data.get('Passes décisives par 90 minutes', 0),
            'xG/90': player_data.get('Buts attendus par 90 minutes', 0),
            'xA/90': player_data.get('Passes décisives attendues par 90 minutes', 0),
            'Tirs/90': player_data.get('Tirs par 90 minutes', 0),
            'Passes clés/90': player_data.get('Passes clés', 0) / minutes_90,
            'Dribbles réussis/90': player_data.get('Dribbles réussis', 0) / minutes_90,
            'Actions → Tir/90': player_data.get('Actions menant à un tir par 90 minutes', 0)
        }
    
    @staticmethod
    def calculate_defensive_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques défensives"""
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        return {
            'Tacles/90': player_data.get('Tacles gagnants', 0) / minutes_90,
            'Interceptions/90': player_data.get('Interceptions', 0) / minutes_90,
            'Ballons récupérés/90': player_data.get('Ballons récupérés', 0) / minutes_90,
            'Duels aériens/90': player_data.get('Duels aériens gagnés', 0) / minutes_90,
            'Dégagements/90': player_data.get('Dégagements', 0) / minutes_90,
            '% Duels gagnés': player_data.get('Pourcentage de duels gagnés', 0),
            '% Duels aériens': player_data.get('Pourcentage de duels aériens gagnés', 0),
            'Tirs bloqués/90': player_data.get('Tirs bloqués', 0) / minutes_90
        }
    
    @staticmethod
    def calculate_technical_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques techniques"""
        minutes_90 = player_data['Minutes jouées'] / 90 if player_data['Minutes jouées'] > 0 else 1
        
        return {
            'Passes tentées/90': player_data.get('Passes tentées', 0) / minutes_90,
            'Passes prog./90': player_data.get('Passes progressives', 0) / minutes_90,
            'Dribbles/90': player_data.get('Dribbles tentés', 0) / minutes_90,
            'Passes clés/90': player_data.get('Passes clés', 0) / minutes_90,
            '% Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
            '% Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0)
        }

# ================================================================================================
# ANALYSEUR DE JOUEURS SIMILAIRES
# ================================================================================================

class SimilarPlayerAnalyzer:
    """Analyseur pour trouver des joueurs similaires"""
    
    @staticmethod
    def prepare_similarity_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Prépare les données pour l'analyse de similarité"""
        # Sélectionner les colonnes disponibles pour l'analyse
        available_metrics = []
        for metric in Config.SIMILARITY_METRICS:
            if metric in df.columns:
                available_metrics.append(metric)
        
        if not available_metrics:
            st.warning("⚠️ Aucune métrique disponible pour l'analyse de similarité")
            return pd.DataFrame(), []
        
        # Créer le DataFrame avec les métriques disponibles
        required_cols = ['Joueur', 'Équipe', 'Compétition', 'Position', 'Âge', 'Valeur marchande']
        similarity_df = df[required_cols + available_metrics].copy()
        
        # Remplacer les valeurs manquantes par 0
        for col in available_metrics:
            similarity_df[col] = pd.to_numeric(similarity_df[col], errors='coerce').fillna(0)
        
        # Filtrer les lignes avec des données valides
        similarity_df = similarity_df.dropna(subset=['Joueur'])
        
        # Supprimer les doublons basés sur le nom du joueur (garder le premier)
        similarity_df = similarity_df.drop_duplicates(subset=['Joueur'], keep='first')
        
        return similarity_df, available_metrics
    
    @staticmethod
    def calculate_similarity_simple(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Calcule la similarité sans sklearn (version simplifiée avec normalisation globale)"""
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
            target_info = target_data.iloc[0]
            
            # Filtrer les autres joueurs (exclure le joueur cible)
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                return []
            
            # Normalisation globale pour garantir la symétrie
            # Calculer les min/max pour chaque métrique sur l'ensemble du dataset
            metric_ranges = {}
            for metric in available_metrics:
                all_values = similarity_df[metric].astype(float)
                min_val = all_values.min()
                max_val = all_values.max()
                range_val = max_val - min_val
                metric_ranges[metric] = {
                    'min': min_val,
                    'max': max_val,
                    'range': range_val if range_val > 0 else 1  # Éviter division par zéro
                }
            
            # Calculer la similarité avec normalisation globale
            similarities = []
            
            for idx, player_row in other_players.iterrows():
                player_values = player_row[available_metrics]
                
                # Calculer la différence normalisée pour chaque métrique
                total_diff = 0
                valid_metrics = 0
                
                for metric in available_metrics:
                    target_val = float(target_values[metric])
                    player_val = float(player_values[metric])
                    
                    # Normalisation basée sur l'étendue globale de la métrique
                    metric_range = metric_ranges[metric]
                    if metric_range['range'] > 0:
                        # Normaliser les valeurs entre 0 et 1
                        norm_target = (target_val - metric_range['min']) / metric_range['range']
                        norm_player = (player_val - metric_range['min']) / metric_range['range']
                        
                        # Différence normalisée (entre 0 et 1)
                        diff = abs(norm_target - norm_player)
                    else:
                        # Si toutes les valeurs sont identiques, différence = 0
                        diff = 0
                    
                    total_diff += diff
                    valid_metrics += 1
                
                # Score de similarité (0-100)
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
            
            # Trier par score de similarité décroissant
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similarities[:num_similar]
            
        except Exception as e:
            st.error(f"Erreur lors du calcul de similarité : {str(e)}")
            return []
    
    @staticmethod
    def calculate_similarity_advanced(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Calcule la similarité avec sklearn (version avancée)"""
        try:
            # Préparer les données
            similarity_df, available_metrics = SimilarPlayerAnalyzer.prepare_similarity_data(df)
            
            if similarity_df.empty or not available_metrics:
                return []
            
            # Obtenir les données du joueur cible
            target_data = similarity_df[similarity_df['Joueur'] == target_player]
            if target_data.empty:
                return []
            
            target_values = target_data[available_metrics].values[0]
            target_info = target_data.iloc[0]
            
            # Filtrer les autres joueurs (exclure le joueur cible)
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                return []
            
            # Normaliser les données
            scaler = StandardScaler()
            
            # Données pour normalisation (inclut le joueur cible)
            all_data = similarity_df[available_metrics].values
            scaler.fit(all_data)
            
            # Normaliser les données du joueur cible et des autres
            target_normalized = scaler.transform([target_values])[0]
            others_normalized = scaler.transform(other_players[available_metrics].values)
            
            # Calculer les distances euclidiennes
            distances = euclidean_distances([target_normalized], others_normalized)[0]
            
            # Convertir en scores de similarité (0-100)
            max_distance = np.max(distances) if len(distances) > 0 else 1
            similarity_scores = 100 * (1 - distances / max_distance) if max_distance > 0 else [100] * len(distances)
            
            # Créer la liste des joueurs similaires
            similar_players = []
            for i, (idx, row) in enumerate(other_players.iterrows()):
                similar_players.append({
                    'joueur': row['Joueur'],
                    'equipe': row['Équipe'],
                    'competition': row['Compétition'],
                    'position': row['Position'],
                    'age': row['Âge'],
                    'similarity_score': similarity_scores[i],
                    'distance': distances[i],
                    'data': row
                })
            
            # Trier par score de similarité décroissant
            similar_players.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_players[:num_similar]
            
        except Exception as e:
            st.error(f"Erreur lors du calcul de similarité avancé : {str(e)}")
            return []
    
    @staticmethod
    def calculate_similarity(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Point d'entrée principal pour le calcul de similarité"""
        if SKLEARN_AVAILABLE:
            return SimilarPlayerAnalyzer.calculate_similarity_advanced(target_player, df, num_similar)
        else:
            return SimilarPlayerAnalyzer.calculate_similarity_simple(target_player, df, num_similar)

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
                showgrid=False
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=11, family='Inter'),
                gridcolor='rgba(255,255,255,0.15)',
                showgrid=True
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
        """Crée un graphique en jauges"""
        fig = make_subplots(
            rows=1, cols=len(data),
            specs=[[{"type": "indicator"}] * len(data)],
            subplot_titles=list(data.keys())
        )
        
        colors = [Config.COLORS['primary'], Config.COLORS['secondary'], Config.COLORS['warning']]
        
        for i, (metric, value) in enumerate(data.items()):
            color = colors[i % len(colors)]
            display_value = min(max(value, 0), 100)
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=display_value,
                    gauge=dict(
                        axis=dict(
                            range=[0, 100], 
                            tickcolor='white', 
                            tickfont=dict(size=10, family='Inter'),
                            ticksuffix='%'
                        ),
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
                        'font': {'color': 'white', 'size': 16, 'family': 'Inter', 'weight': 600}
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            height=340,
            title_text=title,
            title_font_color='white',
            title_font_size=18,
            title_font_family='Inter',
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter', size=11),
            margin=dict(t=80, b=60, l=40, r=40)
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
            marker_color=Config.COLORS['primary'],
            marker_line=dict(color='rgba(255,255,255,0.2)', width=1),
            text=[f"{v:.2f}" for v in player_data.values()],
            textposition='outside',
            textfont=dict(size=11, family='Inter', weight=600)
        ))
        
        fig.add_trace(go.Bar(
            name='Moyenne autres ligues',
            x=list(avg_data.keys()),
            y=list(avg_data.values()),
            marker_color=Config.COLORS['secondary'],
            marker_line=dict(color='rgba(255,255,255,0.2)', width=1),
            text=[f"{v:.2f}" for v in avg_data.values()],
            textposition='outside',
            textfont=dict(size=11, family='Inter', weight=600)
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color='white', size=18, family='Inter', weight=700),
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
                showgrid=False
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=11), 
                gridcolor='rgba(255,255,255,0.15)',
                showgrid=True
            ),
            height=420,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=12, family='Inter'),
                bgcolor='rgba(26, 29, 35, 0.8)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1
            ),
            margin=dict(t=100, b=60, l=60, r=60)
        )
        
        return fig
    
    @staticmethod
    def create_radar_chart(metrics: Dict[str, float], percentiles: List[float], 
                          avg_percentiles: List[float], player_name: str, 
                          comparison_label: str, color: str) -> go.Figure:
        """Crée un radar chart professionnel"""
        fig = go.Figure()
        
        # Performance du joueur
        fig.add_trace(go.Scatterpolar(
            r=percentiles,
            theta=list(metrics.keys()),
            fill='toself',
            fillcolor=f'rgba({Utils.hex_to_rgb(color)}, 0.25)',
            line=dict(color=color, width=3),
            marker=dict(color=color, size=8, symbol='circle'),
            name=f"{player_name}",
            hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
            customdata=list(metrics.values())
        ))
        
        # Moyenne de comparaison
        fig.add_trace(go.Scatterpolar(
            r=avg_percentiles,
            theta=list(metrics.keys()),
            mode='lines',
            line=dict(color='rgba(255,255,255,0.6)', width=2, dash='dash'),
            name=f'Moyenne {comparison_label}',
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
                    dtick=20,
                    ticksuffix='%'
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
                text=f"Analyse Radar - {player_name}",
                font=dict(size=18, color='white', family='Inter', weight=700),
                x=0.5,
                y=0.95
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color='white', size=12),
                bgcolor='rgba(26, 29, 35, 0.8)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1
            ),
            height=500,
            margin=dict(t=80, b=100, l=80, r=80)
        )
        
        return fig
    
    @staticmethod
    def create_histogram_comparison(target_player: str, similar_players: List[Dict], 
                                  df: pd.DataFrame, metric: str) -> go.Figure:
        """Crée un histogramme de comparaison haute qualité pour une métrique spécifique"""
        
        # Fonction pour trouver la colonne correspondante
        def find_column_name(metric_name: str, df_columns: List[str]) -> Optional[str]:
            """Trouve le nom exact de la colonne correspondant à la métrique"""
            # Correspondances spéciales pour les noms de colonnes
            column_mappings = {
                'Actions menant à un tir': ['Actions menant à un tir', 'Actions menant à un tir par 90 minutes', 'Actions → Tir', 'Actions menant à un tir par 90min'],
                'Buts attendus': ['Buts attendus', 'Buts attendus par 90 minutes', 'xG', 'Expected Goals'],
                'Passes décisives attendues': ['Passes décisives attendues', 'Passes décisives attendues par 90 minutes', 'xA', 'Expected Assists'],
                'Passes dans le dernier tiers': ['Passes dans le dernier tiers', 'Passes dernier 1/3', 'Passes dernier tiers'],
                'Passes dans la surface': ['Passes dans la surface', 'Passes dans la surface de réparation'],
                'Duels aériens gagnés': ['Duels aériens gagnés', 'Duels aériens', 'Duels aériens réussis'],
                'Duels défensifs gagnés': ['Duels défensifs gagnés', 'Duels gagnés', 'Duels défensifs'],
                'Centres réussis': ['Centres réussis', 'Centres', 'Pourcentage de centres réussis'],
                'Ballons récupérés': ['Ballons récupérés', 'Récupérations', 'Ballons récupérés par 90 minutes'],
                'Fautes commises': ['Fautes commises', 'Fautes', 'Fautes par 90 minutes'],
                'Touches de balle': ['Touches de balle', 'Touches', 'Touches par 90 minutes'],
                'Passes progressives': ['Passes progressives', 'Passes prog.', 'Progressive passes'],
                'Courses progressives': ['Courses progressives', 'Courses prog.', 'Progressive carries', 'Conduites progressives'],
                'Tirs cadrés': ['Tirs cadrés', 'Tirs en cadre', 'Shots on target'],
                'Pourcentage de passes réussies': ['Pourcentage de passes réussies', '% passes réussies', 'Pass completion %', 'Précision passes'],
                'Pourcentage de dribbles réussis': ['Pourcentage de dribbles réussis', '% dribbles réussis', 'Dribble success %', 'Précision dribbles'],
                'Pourcentage de tirs cadrés': ['Pourcentage de tirs cadrés', '% tirs cadrés', 'Shot accuracy %', 'Précision tirs'],
                'Pourcentage de duels gagnés': ['Pourcentage de duels gagnés', '% duels gagnés', 'Duel success %'],
                'Pourcentage de duels aériens gagnés': ['Pourcentage de duels aériens gagnés', '% duels aériens gagnés', 'Aerial duel success %']
            }
            
            # Recherche directe
            if metric_name in df_columns:
                return metric_name
            
            # Recherche dans les mappings
            possible_names = column_mappings.get(metric_name, [metric_name])
            for name in possible_names:
                if name in df_columns:
                    return name
            
            # Recherche approximative (contient le mot clé)
            for col in df_columns:
                if metric_name.lower() in col.lower() or col.lower() in metric_name.lower():
                    return col
            
            return None
        
        # Trouver le nom exact de la colonne
        actual_column = find_column_name(metric, df.columns.tolist())
        
        if not actual_column:
            st.error(f"La métrique '{metric}' n'existe pas dans les données")
            return go.Figure()
        
        # Obtenir les données du joueur cible
        target_data = df[df['Joueur'] == target_player]
        if target_data.empty:
            st.error(f"Joueur '{target_player}' non trouvé")
            return go.Figure()
        
        target_value = target_data[actual_column].iloc[0]
        if pd.isna(target_value):
            target_value = 0
        
        # Préparer les données pour l'histogramme
        player_names = [target_player]
        player_values = [float(target_value)]
        player_colors = [Config.COLORS['primary']]
        data_quality = []
        
        # Vérifier la qualité des données du joueur cible
        if pd.isna(target_data[actual_column].iloc[0]):
            data_quality.append("⚠️ Données manquantes")
        else:
            data_quality.append("✅ Données disponibles")
        
        # Ajouter les joueurs similaires en accédant directement au DataFrame principal
        missing_data_count = 0
        for i, player_info in enumerate(similar_players):
            player_name = player_info['joueur']
            
            # Accéder directement aux données du DataFrame principal
            player_data_from_df = df[df['Joueur'] == player_name]
            
            if player_data_from_df.empty:
                value = 0
                missing_data_count += 1
                data_quality.append("⚠️ Joueur non trouvé")
            else:
                raw_value = player_data_from_df[actual_column].iloc[0]
                
                # Gestion améliorée des valeurs manquantes
                if pd.isna(raw_value) or raw_value is None:
                    value = 0
                    missing_data_count += 1
                    data_quality.append("⚠️ Données manquantes")
                else:
                    value = float(raw_value)
                    data_quality.append("✅ Données disponibles")
            
            player_names.append(player_name)
            player_values.append(value)
            
            # Couleur dégradée selon la similarité
            similarity_score = player_info['similarity_score']
            if similarity_score >= 85:
                color = Config.COLORS['secondary']
            elif similarity_score >= 70:
                color = Config.COLORS['warning']
            else:
                color = Config.COLORS['accent']
            
            player_colors.append(color)
        
        # Afficher un avertissement seulement si vraiment beaucoup de données manquantes
        if missing_data_count > len(similar_players) * 0.5:
            st.warning(f"⚠️ Attention: {missing_data_count}/{len(similar_players)} joueurs similaires ont des données manquantes pour '{metric}' (colonne: '{actual_column}')")
        
        # Créer l'histogramme avec informations sur la qualité des données
        fig = go.Figure(data=[go.Bar(
            x=player_names,
            y=player_values,
            marker=dict(
                color=player_colors,
                line=dict(color='rgba(255,255,255,0.3)', width=2),
                opacity=0.8
            ),
            text=[f"{v:.1f}" if v > 0 else "N/A" for v in player_values],
            textposition='outside',
            textfont=dict(color='white', size=14, family='Inter', weight=600),
            hovertemplate='<b>%{x}</b><br>' + f'{metric}: %{{y:.2f}}<br>' + 
                         f'Colonne: {actual_column}<extra></extra>'
        )])
        
        # Ajouter une ligne horizontale pour la moyenne (seulement sur les valeurs > 0)
        non_zero_values = [v for v in player_values if v > 0]
        if non_zero_values:
            avg_value = np.mean(non_zero_values)
            fig.add_hline(
                y=avg_value,
                line_dash="dash",
                line_color="rgba(255,255,255,0.6)",
                line_width=2,
                annotation_text=f"Moyenne (données valides): {avg_value:.1f}",
                annotation_position="top right",
                annotation_font_color="white",
                annotation_font_size=12
            )
        
        # Mise en page haute qualité
        fig.update_layout(
            title=dict(
                text=f"Comparaison: {metric}",
                font=dict(size=24, color='white', family='Inter', weight=700),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                tickfont=dict(color='white', size=14, family='Inter'),
                tickangle=45,
                showgrid=False,
                title=dict(text="Joueurs", font=dict(color='white', size=16, family='Inter'))
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=14, family='Inter'),
                gridcolor='rgba(255,255,255,0.15)',
                showgrid=True,
                title=dict(text=metric, font=dict(color='white', size=16, family='Inter'))
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            height=600,
            margin=dict(t=100, b=150, l=80, r=80),
            showlegend=False
        )
        
        return fig

# ================================================================================================
# ANALYSEUR DE PERFORMANCE
# ================================================================================================

class PerformanceAnalyzer:
    """Analyseur de performance avec comparaison intelligente par poste"""
    
    @staticmethod
    def calculate_position_percentiles(player_data: pd.Series, df_comparison: pd.DataFrame, 
                                     metrics_dict: Dict[str, str], 
                                     reference_type: str = "top_quartile",
                                     min_minutes: int = 900) -> Tuple[List[float], List[float], Dict]:
        """
        Calcule les percentiles du joueur comparé aux autres joueurs du même poste
        
        Args:
            player_data: Données du joueur sélectionné
            df_comparison: DataFrame des autres ligues
            metrics_dict: Dictionnaire {metric_key: column_name}
            reference_type: Type de référence ("median", "mean", "top_quartile", "top_10", "good_starter")
            min_minutes: Minutes minimum pour être inclus dans la comparaison
            
        Returns:
            Tuple[List[float], List[float], Dict]: (percentiles_joueur, percentiles_reference, metadata)
        """
        player_position = player_data['Position']
        
        # Filtrer les joueurs du même poste dans les autres ligues
        df_same_position = df_comparison[df_comparison['Position'] == player_position].copy()
        
        # Filtrer par minutes jouées (joueurs réguliers seulement)
        if not df_same_position.empty:
            df_same_position = df_same_position[df_same_position['Minutes jouées'] >= min_minutes]
        
        # Fallback si pas assez de joueurs du même poste
        if len(df_same_position) < 10:
            df_same_position = df_comparison[df_comparison['Minutes jouées'] >= min_minutes].copy()
            fallback_used = True
        else:
            fallback_used = False
        
        # Métadonnées pour information
        metadata = {
            'position': player_position,
            'comparison_count': len(df_same_position),
            'fallback_used': fallback_used,
            'reference_type': reference_type,
            'min_minutes': min_minutes
        }
        
        percentiles_player = []
        percentiles_reference = []
        
        # Calculer les minutes jouées pour normalisation
        player_minutes_90 = max(player_data['Minutes jouées'] / 90, 1)
        comparison_minutes_90 = df_same_position['Minutes jouées'] / 90
        comparison_minutes_90 = comparison_minutes_90.replace([np.inf, -np.inf], 1).fillna(1)
        
        for metric_key, column_name in metrics_dict.items():
            try:
                # === CALCUL DE LA VALEUR DU JOUEUR ===
                player_val = PerformanceAnalyzer._calculate_metric_value(
                    player_data, metric_key, column_name, player_minutes_90
                )
                
                # === CALCUL DES VALEURS DE COMPARAISON ===
                comparison_vals = PerformanceAnalyzer._calculate_comparison_values(
                    df_same_position, metric_key, column_name, comparison_minutes_90
                )
                
                # === CALCUL DES PERCENTILES ===
                percentile_player = PerformanceAnalyzer._calculate_percentile(player_val, comparison_vals)
                percentile_reference = PerformanceAnalyzer._calculate_reference_percentile(
                    comparison_vals, reference_type
                )
                
                percentiles_player.append(percentile_player)
                percentiles_reference.append(percentile_reference)
                
            except Exception as e:
                # Valeurs par défaut en cas d'erreur
                percentiles_player.append(50)
                percentiles_reference.append(PerformanceAnalyzer._get_default_reference(reference_type))
        
        return percentiles_player, percentiles_reference, metadata
    
    @staticmethod
    def _calculate_metric_value(player_data: pd.Series, metric_key: str, column_name: str, minutes_90: float) -> float:
        """Calcule la valeur d'une métrique pour le joueur"""
        if metric_key.endswith('/90'):
            # Métrique par 90 minutes
            if 'par 90 minutes' in str(column_name):
                # Colonne déjà normalisée
                return player_data.get(column_name, 0)
            else:
                # Normaliser par les minutes jouées
                raw_value = player_data.get(column_name, 0)
                return raw_value / minutes_90
        else:
            # Métrique directe (pourcentages, totaux, etc.)
            return player_data.get(column_name, 0)
    
    @staticmethod
    def _calculate_comparison_values(df_comparison: pd.DataFrame, metric_key: str, 
                                   column_name: str, minutes_90: pd.Series) -> pd.Series:
        """Calcule les valeurs de comparaison pour une métrique"""
        if metric_key.endswith('/90'):
            # Métrique par 90 minutes
            if 'par 90 minutes' in str(column_name):
                # Colonne déjà normalisée
                values = df_comparison.get(column_name, pd.Series([0]*len(df_comparison)))
            else:
                # Normaliser par les minutes jouées
                raw_values = df_comparison.get(column_name, pd.Series([0]*len(df_comparison)))
                values = raw_values / minutes_90
        else:
            # Métrique directe
            values = df_comparison.get(column_name, pd.Series([0]*len(df_comparison)))
        
        # Nettoyer les valeurs invalides
        return values.replace([np.inf, -np.inf], np.nan).dropna()
    
    @staticmethod
    def _calculate_percentile(player_val: float, comparison_vals: pd.Series) -> float:
        """Calcule le percentile du joueur"""
        if len(comparison_vals) == 0 or pd.isna(player_val) or np.isinf(player_val):
            return 50.0
        
        percentile = (comparison_vals < player_val).mean() * 100
        return min(max(percentile, 0), 100)
    
    @staticmethod
    def _calculate_reference_percentile(comparison_vals: pd.Series, reference_type: str) -> float:
        """Calcule le percentile de référence selon le type choisi"""
        if len(comparison_vals) == 0:
            return PerformanceAnalyzer._get_default_reference(reference_type)
        
        reference_mapping = {
            "median": 50,
            "good_starter": 60,
            "top_quartile": 75,
            "top_10": 90,
            "mean": (comparison_vals < comparison_vals.mean()).mean() * 100
        }
        
        return reference_mapping.get(reference_type, 75)  # Default: top_quartile
    
    @staticmethod
    def _get_default_reference(reference_type: str) -> float:
        """Retourne la valeur par défaut selon le type de référence"""
        defaults = {
            "median": 50,
            "good_starter": 60,
            "top_quartile": 75,
            "top_10": 90,
            "mean": 50
        }
        return defaults.get(reference_type, 75)
    
    @staticmethod
    def get_reference_label(reference_type: str, position: str) -> str:
        """Retourne le label pour la légende selon le type de référence"""
        labels = {
            "median": f"Médiane {position}s autres ligues",
            "good_starter": f"Bon titulaire {position} (60e percentile)",
            "top_quartile": f"Bon niveau {position} (75e percentile)",
            "top_10": f"Très haut niveau {position} (90e percentile)",
            "mean": f"Moyenne {position}s autres ligues"
        }
        return labels.get(reference_type, f"Référence {position}s autres ligues")
    
    # ============================================================================================
    # ANALYSES PAR DOMAINE (OFFENSIVE, DÉFENSIVE, TECHNIQUE)
    # ============================================================================================
    
    @staticmethod
    def analyze_offensive_performance(player_data: pd.Series, df_comparison: pd.DataFrame, 
                                    reference_type: str = "top_quartile") -> Dict:
        """Analyse complète de la performance offensive avec comparaison par poste"""
        
        # Métriques et mapping des colonnes
        metrics = MetricsCalculator.calculate_offensive_metrics(player_data)
        
        metrics_mapping = {
            'Buts/90': 'Buts par 90 minutes',
            'Passes D./90': 'Passes décisives par 90 minutes', 
            'xG/90': 'Buts attendus par 90 minutes',
            'xA/90': 'Passes décisives attendues par 90 minutes',
            'Tirs/90': 'Tirs par 90 minutes',
            'Passes clés/90': 'Passes clés',
            'Dribbles réussis/90': 'Dribbles réussis',
            'Actions → Tir/90': 'Actions menant à un tir par 90 minutes'
        }
        
        # Calcul des percentiles avec comparaison par poste
        percentiles, avg_percentiles, metadata = PerformanceAnalyzer.calculate_position_percentiles(
            player_data, df_comparison, metrics_mapping, reference_type
        )
        
        # Calcul des moyennes pour affichage (joueurs du même poste uniquement)
        avg_metrics = PerformanceAnalyzer._calculate_average_metrics(
            df_comparison, metadata['position'], metrics_mapping, metadata['min_minutes']
        )
        
        return {
            'metrics': metrics,
            'avg_metrics': avg_metrics,
            'percentiles': percentiles,
            'avg_percentiles': avg_percentiles,
            'metadata': metadata
        }
    
    @staticmethod
    def analyze_defensive_performance(player_data: pd.Series, df_comparison: pd.DataFrame,
                                    reference_type: str = "top_quartile") -> Dict:
        """Analyse complète de la performance défensive avec comparaison par poste"""
        
        # Métriques et mapping des colonnes
        metrics = MetricsCalculator.calculate_defensive_metrics(player_data)
        
        metrics_mapping = {
            'Tacles/90': 'Tacles gagnants',
            'Interceptions/90': 'Interceptions',
            'Ballons récupérés/90': 'Ballons récupérés',
            'Duels aériens/90': 'Duels aériens gagnés',
            'Dégagements/90': 'Dégagements',
            '% Duels gagnés': 'Pourcentage de duels gagnés',
            '% Duels aériens': 'Pourcentage de duels aériens gagnés',
            'Tirs bloqués/90': 'Tirs bloqués'
        }
        
        # Calcul des percentiles avec comparaison par poste
        percentiles, avg_percentiles, metadata = PerformanceAnalyzer.calculate_position_percentiles(
            player_data, df_comparison, metrics_mapping, reference_type
        )
        
        # Calcul des moyennes pour affichage
        avg_metrics = PerformanceAnalyzer._calculate_average_metrics(
            df_comparison, metadata['position'], metrics_mapping, metadata['min_minutes']
        )
        
        return {
            'metrics': metrics,
            'avg_metrics': avg_metrics,
            'percentiles': percentiles,
            'avg_percentiles': avg_percentiles,
            'metadata': metadata
        }
    
    @staticmethod
    def analyze_technical_performance(player_data: pd.Series, df_comparison: pd.DataFrame,
                                     reference_type: str = "top_quartile") -> Dict:
        """Analyse complète de la performance technique avec comparaison par poste"""
        
        # Métriques et mapping des colonnes
        metrics = MetricsCalculator.calculate_technical_metrics(player_data)
        
        metrics_mapping = {
            'Passes tentées/90': 'Passes tentées',
            'Passes prog./90': 'Passes progressives',
            'Dribbles/90': 'Dribbles tentés',
            'Passes clés/90': 'Passes clés',
            '% Passes réussies': 'Pourcentage de passes réussies',
            '% Dribbles réussis': 'Pourcentage de dribbles réussis'
        }
        
        # Calcul des percentiles avec comparaison par poste
        percentiles, avg_percentiles, metadata = PerformanceAnalyzer.calculate_position_percentiles(
            player_data, df_comparison, metrics_mapping, reference_type
        )
        
        # Calcul des moyennes pour affichage
        avg_metrics = PerformanceAnalyzer._calculate_average_metrics(
            df_comparison, metadata['position'], metrics_mapping, metadata['min_minutes']
        )
        
        return {
            'metrics': metrics,
            'avg_metrics': avg_metrics,
            'percentiles': percentiles,
            'avg_percentiles': avg_percentiles,
            'metadata': metadata
        }
    
    @staticmethod
    def _calculate_average_metrics(df_comparison: pd.DataFrame, position: str, 
                                 metrics_mapping: Dict[str, str], min_minutes: int) -> Dict[str, float]:
        """Calcule les moyennes des métriques pour le poste donné"""
        # Filtrer par poste et minutes
        df_filtered = df_comparison[
            (df_comparison['Position'] == position) & 
            (df_comparison['Minutes jouées'] >= min_minutes)
        ].copy()
        
        if df_filtered.empty:
            df_filtered = df_comparison[df_comparison['Minutes jouées'] >= min_minutes].copy()
        
        avg_metrics = {}
        minutes_90 = df_filtered['Minutes jouées'] / 90
        minutes_90 = minutes_90.replace([np.inf, -np.inf], 1).fillna(1)
        
        for metric_key, column_name in metrics_mapping.items():
            try:
                if metric_key.endswith('/90'):
                    if 'par 90 minutes' in str(column_name):
                        avg_val = df_filtered.get(column_name, pd.Series([0]*len(df_filtered))).mean()
                    else:
                        raw_vals = df_filtered.get(column_name, pd.Series([0]*len(df_filtered)))
                        avg_val = (raw_vals / minutes_90).mean()
                else:
                    avg_val = df_filtered.get(column_name, pd.Series([0]*len(df_filtered))).mean()
                
                avg_metrics[metric_key] = avg_val if not pd.isna(avg_val) else 0
            except:
                avg_metrics[metric_key] = 0
        
        return avg_metrics


# ================================================================================================
# COMPOSANTS UI
# ================================================================================================

class UIComponents:
    """Composants d'interface utilisateur réutilisables"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête principal avec les logos"""
        # Chargement et encodage des logos
        big5_logo_html = UIComponents._get_logo_html('Big5_logos.png', 'Big 5 Championships', width=200, height=200)        
        st.markdown(f"""
        <div class='player-header-card animated-card' style='display: flex; align-items: center; justify-content: space-between;'
                <div style='flex: 1; text-align: left;'>
                    <h1 style='color: white; margin: 0; font-size: 3.5em; font-weight: 800; letter-spacing: -0.02em;'>
                        RakoStats
                    </h1>
                    <p style='color: rgba(255,255,255,0.8); margin: 8px 0 0; font-size: 1.25em; font-weight: 500;'>
                    Analyse avancée des performances - Saison 2024-2025
                    </p>
                <div>
            <div style='flex: 0; text-align: right; margin-left: 32px;'>
                {big5_logo_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_breadcrumbs(competition, team, player):
        """Affiche le fil d'Ariane (breadcrumbs)"""
        st.markdown(
            f"""
            <div class='breadcrumbs'>
                <span style='color:var(--primary-color); font-weight:600;'>{competition}</span> &nbsp;›&nbsp;
                <span style='color:var(--accent-color); font-weight:600;'>{team}</span> &nbsp;›&nbsp;
                <span style='color:var(--text-primary); font-weight:600;'>{player}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte complète du joueur"""
        valeur_marchande = Utils.get_market_value_safe(player_data)
        
        container = st.container()
        
        with container:
            col1, col2, col3 = st.columns([1, 2.5, 1], gap="large")
            
            with col1:
                UIComponents._render_player_photo(player_data['Joueur'])
            
            with col2:
                st.markdown(f"""
                <div class='player-info-card animated-card'>
                    <h2 class='section-title-enhanced' style='margin-bottom: var(--spacing-xl); font-size: 2.5em; color: var(--text-primary);'>
                        {player_data['Joueur']}
                    </h2>
                    <div class='player-metrics-grid'>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced'>{player_data['Âge']}</div>
                            <div class='metric-label-enhanced'>Âge</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced'>{player_data['Position']}</div>
                            <div class='metric-label-enhanced'>Position</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced'>{player_data['Nationalité']}</div>
                            <div class='metric-label-enhanced'>Nationalité</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced'>{int(player_data['Minutes jouées'])}</div>
                            <div class='metric-label-enhanced'>Minutes Jouées</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced' style='color: var(--accent-color);'>{valeur_marchande}</div>
                            <div class='metric-label-enhanced'>Valeur Marchande</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced'>{player_data['Équipe']}</div>
                            <div class='metric-label-enhanced'>Équipe</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                UIComponents._render_club_logo(player_data['Équipe'], competition)
    
    @staticmethod
    def render_similar_player_card(player_info: Dict, rank: int):
        similarity_score = player_info['similarity_score']
        player_data = player_info['data']

        # Couleur basée sur le score de similarité
        if similarity_score >= 85:
            score_color = "#2ca02c"  # Vert
        elif similarity_score >= 70:
            score_color = "#ff7f0e"  # Orange
        else:
            score_color = "#1f77b4"  # Bleu

        valeur_marchande = Utils.get_market_value_safe(player_data)

        # Logo du club (déjà existant)
        logo_path = ImageManager.get_club_logo(player_info['competition'], player_info['equipe'])
        logo_html = ""
        if logo_path and os.path.exists(logo_path):
            try:
                image = Image.open(logo_path)
                logo_base64 = Utils.image_to_base64(image)
                logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="club-logo-small" alt="{player_info["equipe"]}">'
            except Exception:
                logo_html = f'<div style="width: 40px; height: 40px; background: rgba(255,255,255,0.1); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.8em; color: white;">🏟️</div>'
        else:
            logo_html = f'<div style="width: 40px; height: 40px; background: rgba(255,255,255,0.1); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.8em; color: white;">🏟️</div>'

        # --- AJOUT : Photo du joueur ---
        photo_path = ImageManager.get_player_photo(player_info['joueur'])
        if photo_path and os.path.exists(photo_path):
            image = Image.open(photo_path)
            photo_html = f'<img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" style="width:48px; height:48px; border-radius:50%; object-fit:cover; margin-right:8px;">'
        else:
            photo_html = '<div style="width:48px; height:48px; border-radius:50%; background:#eee; color:#bbb; display:inline-flex; align-items:center; justify-content:center; font-size:2em; margin-right:8px;">👤</div>'
        # --- FIN AJOUT ---

        st.markdown(f"""
        <div class='similar-player-card animated-card'>
            <div class='similarity-score' style='background: {score_color};'>
                #{rank} • {similarity_score:.1f}% similaire
            </div>
            <div class='player-header-with-logo' style="display:flex; align-items:center; gap:10px;">
                {photo_html}
                {logo_html}
                <h3 style='color: var(--text-primary); margin: 0; font-size: 1.4em; font-weight: 700; flex: 1;'>
                    {player_info['joueur']}
                </h3>
            </div>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px;'>
                <div class='metric-card-enhanced' style='min-height: 70px; padding: 12px;'>
                    <div class='metric-value-enhanced' style='font-size: 1.1em;'>{player_info['equipe']}</div>
                    <div class='metric-label-enhanced'>Équipe</div>
                </div>
                <div class='metric-card-enhanced' style='min-height: 70px; padding: 12px;'>
                    <div class='metric-value-enhanced' style='font-size: 1.1em;'>{player_info['position']}</div>
                    <div class='metric-label-enhanced'>Position</div>
                </div>
                <div class='metric-card-enhanced' style='min-height: 70px; padding: 12px;'>
                    <div class='metric-value-enhanced' style='font-size: 1.1em;'>{player_info['age']}</div>
                    <div class='metric-label-enhanced'>Âge</div>
                </div>
            </div>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;'>
                <div class='metric-card-enhanced' style='min-height: 60px; padding: 10px;'>
                    <div class='metric-value-enhanced' style='font-size: 1em; color: var(--accent-color);'>{valeur_marchande}</div>
                    <div class='metric-label-enhanced'>Valeur Marchande</div>
                </div>
                <div class='metric-card-enhanced' style='min-height: 60px; padding: 10px;'>
                    <div class='metric-value-enhanced' style='font-size: 1em;'>{player_info['competition']}</div>
                    <div class='metric-label-enhanced'>Compétition</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_player_photo(player_name: str):
        """Affiche la photo du joueur"""
        photo_path = ImageManager.get_player_photo(player_name)
        
        if photo_path:
            try:
                image = Image.open(photo_path)
                st.markdown(f"""
                <div class='image-container animated-card'>
                    <img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: var(--radius-md);">
                </div>
                <p style='text-align: center; color: var(--primary-color); font-weight: 600; margin-top: var(--spacing-md); font-size: 0.9em;'>
                    📸 {player_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_photo_placeholder(player_name)
        else:
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
                    <img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain;">
                </div>
                <p style='text-align: center; color: var(--primary-color); font-weight: 600; margin-top: var(--spacing-md); font-size: 0.9em;'>
                    🏟️ {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_logo_placeholder(team_name)
        else:
            UIComponents._render_logo_placeholder(team_name)
    
    @staticmethod
    def _render_photo_placeholder(player_name: str):
        """Affiche un placeholder pour la photo"""
        st.markdown(f"""
        <div class='image-container animated-card'>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 4em; margin-bottom: var(--spacing-md); opacity: 0.5;'>👤</div>
                <p style='margin: 0; font-size: 0.9em;'>Photo non disponible</p>
                <p style='font-size: 0.8em; margin-top: var(--spacing-sm); color: var(--primary-color);'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder(team_name: str):
        """Affiche un placeholder pour le logo"""
        st.markdown(f"""
        <div class='club-logo-container animated-card'>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 3em; margin-bottom: var(--spacing-md); opacity: 0.5;'>🏟️</div>
                <p style='margin: 0; font-size: 0.8em;'>Logo non disponible</p>
                <p style='font-size: 0.75em; margin-top: var(--spacing-xs); color: var(--primary-color);'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_breadcrumbs(competition: str, team: str, player: str):
        """Affiche un fil d'Ariane"""
        st.markdown(f"""
        <div class='breadcrumbs'>
            <span style='color: var(--text-secondary); font-size: 0.9em;'>
                🏆 {competition} › ⚽ {team} › 👤 {player}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """Affiche le footer"""
        st.markdown(f"""
        <div class='dashboard-footer animated-card' style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='flex: 1;'>
                <h3 style='color: var(--primary-color); margin: 0 0 16px 0; font-weight: 900; font-size: 2.25em;'>
                    RakoStats
            <h3>            
            <p style='color: var(--text-primary); margin: 0; font-size: 1.1em; font-weight: 200;'>
                Analyse avancée des performances
            </p>
            <p style='color: var(--text-secondary); margin: 12px 0 0 0; font-size: 0.9em;'>
                Données: Opta via FBref | Saison 2024-25 | @Alex Rakotomalala
            </p>
        </div>
    </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def _get_logo_html(logo_path: str, alt_text: str, width: int = 80, height: int = 60) -> str:
        """Récupère le HTML pour afficher un logo"""
        if os.path.exists(logo_path):
            try:
                image = Image.open(logo_path)
                # Redimensionner si nécessaire
                if image.size != (width, height):
                    image = image.resize((width, height), Image.Resampling.LANCZOS)
                logo_base64 = Utils.image_to_base64(image)
                return f'<img src="data:image/png;base64,{logo_base64}" alt="{alt_text}" style="width:{width}px; height:{height}px; object-fit:contain;">'
            except Exception:
                return f'<div style="width:{width}px; height:{height}px; background:rgba(255,255,255,0.1); border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-size:0.8em;">Logo</div>'
        else:
            return f'<div style="width:{width}px; height:{height}px; background:rgba(255,255,255,0.1); border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-size:0.8em;">{alt_text}</div>'

# ================================================================================================
# GESTIONNAIRE DE SIDEBAR
# ================================================================================================

class SidebarManager:
    """Gestionnaire pour la sidebar"""
    
    @staticmethod
    def get_position_display_name(position: str) -> str:
        """Convertit les codes de position en noms affichables"""
        position_mapping = {
            'GK': 'Gardien',
            'DF': 'Défenseur', 
            'MF': 'Milieu',
            'FW': 'Attaquant'
        }
        return position_mapping.get(position, position)
    
    @staticmethod
    def render_sidebar(df: pd.DataFrame) -> Tuple[str, str, str, str, pd.DataFrame]:
        """Rendu complet de la sidebar"""
        with st.sidebar:
            # En-tête
            st.markdown("""
            <div class='sidebar-header'>
                <h2 style='color: white; margin: 0; font-weight: 700;'>⚙️ Configuration</h2>
                <p style='color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 0.9em;'>
                    Sélectionnez votre joueur
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Sélection de la compétition
            competitions = DataManager.get_competitions(df)
            selected_competition = st.selectbox(
                "🏆 Choisir une compétition :",
                competitions,
                index=0,
                help="Sélectionnez la compétition pour filtrer les joueurs"
            )
            
            # Filtrage par compétition
            df_filtered = DataManager.filter_by_competition(df, selected_competition)
            
            st.markdown("---")
            
            # Sélection du club
            clubs = ["Tous les clubs"] + sorted(df_filtered['Équipe'].unique().tolist())
            selected_club = st.selectbox(
                "🏟️ Choisir un club :",
                clubs,
                index=0,
                help="Sélectionnez un club pour filtrer les joueurs"
            )
            
            # Filtrage par club
            if selected_club != "Tous les clubs":
                df_filtered = df_filtered[df_filtered['Équipe'] == selected_club]
            
            # Sélection du poste
            positions_raw = df_filtered['Position'].unique()
            positions_display = ["Tous les postes"] + [SidebarManager.get_position_display_name(pos) for pos in sorted(positions_raw)]
            
            selected_position_display = st.selectbox(
                "⚽ Choisir un poste :",
                positions_display,
                index=0,
                help="Sélectionnez un poste pour filtrer les joueurs"
            )
            
            # Conversion du nom d'affichage vers le code original
            selected_position = None
            if selected_position_display != "Tous les postes":
                position_reverse_mapping = {
                    'Gardien': 'GK',
                    'Défenseur': 'DF', 
                    'Milieu': 'MF',
                    'Attaquant': 'FW'
                }
                selected_position = position_reverse_mapping.get(selected_position_display, selected_position_display)
                df_filtered = df_filtered[df_filtered['Position'] == selected_position]
            
            st.markdown("---")
            
            # Suppression du filtre minutes jouées et des statistiques
            df_filtered_minutes = df_filtered  # Utilise tel quel
            
            # Sélection du joueur
            selected_player = None
            if not df_filtered_minutes.empty:
                joueurs = DataManager.get_players(df_filtered_minutes)
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
                else:
                    st.error("❌ Aucun joueur disponible avec ces critères.")
            else:
                st.error("❌ Aucun joueur disponible avec ces critères.")
            
            return selected_competition, selected_club, selected_position_display, selected_player, df_filtered_minutes

# ================================================================================================
# GESTIONNAIRE DE TABS
# ================================================================================================

class TabManager:
    """Gestionnaire pour les différents onglets avec comparaison intelligente par poste"""
    
    @staticmethod
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, 
                           selected_player: str, player_competition: str):
        """Rendu de l'onglet performance offensive avec comparaison par poste"""
        import streamlit as st
        
        st.markdown("<h2 class='section-title-enhanced'>🎯 Performance Offensive</h2>", unsafe_allow_html=True)
        
        # === CONFIGURATION DE LA COMPARAISON ===
        reference_type = st.selectbox(
            "Niveau de référence pour le radar :",
            ["top_quartile", "good_starter", "median", "top_10"],
            index=0,
            format_func=lambda x: {
                "top_quartile": "Bon niveau (75e percentile)",
                "good_starter": "Bon titulaire (60e percentile)", 
                "median": "Médiane (50e percentile)",
                "top_10": "Très haut niveau (90e percentile)"
            }[x],
            help="Choisissez le niveau de référence pour comparer le joueur aux autres de son poste"
        )
        
        # Analyse avec comparaison par poste
        analysis = PerformanceAnalyzer.analyze_offensive_performance(
            player_data, df_comparison, reference_type
        )
        metadata = analysis['metadata']
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # === GRAPHIQUE EN BARRES ===
            basic_actions = {
                'Buts': player_data.get('Buts', 0),
                'Passes décisives': player_data.get('Passes décisives', 0),
                'Passes clés': player_data.get('Passes clés', 0),
                'Tirs': player_data.get('Tirs', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "Actions Offensives Totales",
                Config.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # === MÉTRIQUES CLÉS ===
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques Clés</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Buts par 90min",
                    value=f"{analysis['metrics']['Buts/90']:.2f}",
                    delta=f"{analysis['metrics']['Buts/90'] - analysis['avg_metrics']['Buts/90']:.2f}",
                    help=f"Comparé à la moyenne des {metadata['position']}s des autres ligues"
                )
                st.metric(
                    label="xG par 90min",
                    value=f"{analysis['metrics']['xG/90']:.2f}",
                    delta=f"{analysis['metrics']['xG/90'] - analysis['avg_metrics']['xG/90']:.2f}",
                    help="Expected Goals - Probabilité de marquer"
                )
            
            with metric_col2:
                st.metric(
                    label="Passes D. par 90min",
                    value=f"{analysis['metrics']['Passes D./90']:.2f}",
                    delta=f"{analysis['metrics']['Passes D./90'] - analysis['avg_metrics']['Passes D./90']:.2f}",
                    help="Passes menant directement à un but"
                )
                st.metric(
                    label="xA par 90min",
                    value=f"{analysis['metrics']['xA/90']:.2f}",
                    delta=f"{analysis['metrics']['xA/90'] - analysis['avg_metrics']['xA/90']:.2f}",
                    help="Expected Assists - Probabilité d'assister"
                )
        
        with col2:
            # === GRAPHIQUE EN JAUGES ===
            efficiency_data = {
                'Tirs cadrés': player_data.get('Pourcentage de tirs cadrés', 0),
                'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                'Conversion buts': (player_data.get('Buts', 0) / player_data.get('Tirs', 1) * 100) if player_data.get('Tirs', 0) > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(efficiency_data, "Efficacité Offensive (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # === ANALYSE RADAR ===
            st.markdown("<h3 class='subsection-title-enhanced'>🎯 Analyse Radar</h3>", unsafe_allow_html=True)
            
            # Information sur la comparaison
            TabManager._render_comparison_info(metadata, selected_player)
            
            # Légende
            reference_label = PerformanceAnalyzer.get_reference_label(reference_type, metadata['position'])
            TabManager._render_radar_legend(selected_player, metadata['position'], reference_label, 'primary')
            
            # Radar chart
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                reference_label,
                Config.COLORS['accent']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # === COMPARAISON DÉTAILLÉE ===
        TabManager._render_detailed_comparison(analysis, selected_player, metadata['position'], "defensive")
    
    @staticmethod
    def render_technical_tab(player_data: pd.Series, df_comparison: pd.DataFrame,
                           selected_player: str, player_competition: str):
        """Rendu de l'onglet performance technique avec comparaison par poste"""
        import streamlit as st
        
        st.markdown("<h2 class='section-title-enhanced'>🎨 Performance Technique</h2>", unsafe_allow_html=True)
        
        # === CONFIGURATION DE LA COMPARAISON ===
        reference_type = st.selectbox(
            "Niveau de référence pour le radar :",
            ["top_quartile", "good_starter", "median", "top_10"],
            index=0,
            format_func=lambda x: {
                "top_quartile": "Bon niveau (75e percentile)",
                "good_starter": "Bon titulaire (60e percentile)",
                "median": "Médiane (50e percentile)",
                "top_10": "Très haut niveau (90e percentile)"
            }[x],
            key="technical_reference",
            help="Choisissez le niveau de référence pour comparer le joueur aux autres de son poste"
        )
        
        # Analyse avec comparaison par poste
        analysis = PerformanceAnalyzer.analyze_technical_performance(
            player_data, df_comparison, reference_type
        )
        metadata = analysis['metadata']
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # === GRAPHIQUE EN BARRES ===
            basic_actions = {
                'Passes tentées': player_data.get('Passes tentées', 0),
                'Dribbles tentés': player_data.get('Dribbles tentés', 0),
                'Passes clés': player_data.get('Passes clés', 0),
                'Passes progressives': player_data.get('Passes progressives', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "Actions Techniques Totales",
                Config.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # === MÉTRIQUES TECHNIQUES ===
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques Techniques</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Passes par 90min",
                    value=f"{analysis['metrics']['Passes tentées/90']:.1f}",
                    delta=f"{analysis['metrics']['Passes tentées/90'] - analysis['avg_metrics']['Passes tentées/90']:.1f}",
                    help=f"Comparé à la moyenne des {metadata['position']}s des autres ligues"
                )
                st.metric(
                    label="Passes clés par 90min",
                    value=f"{analysis['metrics']['Passes clés/90']:.1f}",
                    delta=f"{analysis['metrics']['Passes clés/90'] - analysis['avg_metrics']['Passes clés/90']:.1f}",
                    help="Nombre de passes clés par 90 minutes de jeu"
                )
            
            with metric_col2:
                st.metric(
                    label="% Passes réussies",
                    value=f"{analysis['metrics']['% Passes réussies']:.1f}%",
                    delta=f"{analysis['metrics']['% Passes réussies'] - analysis['avg_metrics']['% Passes réussies']:.1f}%",
                    help="Pourcentage de passes réussies"
                )
                st.metric(
                    label="% Dribbles réussis",
                    value=f"{analysis['metrics']['% Dribbles réussis']:.1f}%",
                    delta=f"{analysis['metrics']['% Dribbles réussis'] - analysis['avg_metrics']['% Dribbles réussis']:.1f}%",
                    help="Pourcentage de dribbles réussis"
                )
        
        with col2:
            # === GRAPHIQUE EN JAUGES ===
            technical_success = {
                'Passes prog.': player_data.get('Pourcentage de passes progressives réussies', player_data.get('Pourcentage de passes réussies', 0)),
                'Courses prog.': min(100, (player_data.get('Courses progressives', player_data.get('Dribbles réussis', 0)) / max(player_data.get('Minutes jouées', 90), 1) * 90 * 10)) if player_data.get('Courses progressives', player_data.get('Dribbles réussis', 0)) > 0 else 0,
                'Touches/90': min(100, (player_data.get('Touches de balle', 0) / max(player_data.get('Minutes jouées', 90), 1) * 90 / 100 * 100)) if player_data.get('Touches de balle', 0) > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(technical_success, "Maîtrise Technique (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # === ANALYSE RADAR ===
            st.markdown("<h3 class='subsection-title-enhanced'>🎨 Analyse Radar</h3>", unsafe_allow_html=True)
            
            # Information sur la comparaison
            TabManager._render_comparison_info(metadata, selected_player)
            
            # Légende
            reference_label = PerformanceAnalyzer.get_reference_label(reference_type, metadata['position'])
            TabManager._render_radar_legend(selected_player, metadata['position'], reference_label, 'secondary')
            
            # Radar chart
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                reference_label,
                Config.COLORS['secondary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # === COMPARAISON DÉTAILLÉE ===
        TabManager._render_detailed_comparison(analysis, selected_player, metadata['position'], "technical")
    
    # ============================================================================================
    # MÉTHODES UTILITAIRES POUR L'AFFICHAGE
    # ============================================================================================
    
    @staticmethod
    def _render_comparison_info(metadata: Dict, selected_player: str):
        """Affiche les informations sur la comparaison"""
        import streamlit as st
        
        position_emoji = {
            'GK': '🥅', 'DF': '🛡️', 'MF': '⚙️', 'FW': '⚽'
        }.get(metadata['position'], '👤')
        
        position_name = {
            'GK': 'Gardien', 'DF': 'Défenseur', 'MF': 'Milieu', 'FW': 'Attaquant'
        }.get(metadata['position'], metadata['position'])
        
        # Message principal
        if metadata['fallback_used']:
            st.warning(f"⚠️ Peu de {position_name}s disponibles. Comparaison élargie à {metadata['comparison_count']} joueurs.")
        else:
            st.info(f"{position_emoji} Comparé à **{metadata['comparison_count']} {position_name}s** des autres ligues (min. {metadata['min_minutes']}min)")
        
        # Informations supplémentaires
        reference_info = {
            "median": "La ligne représente la médiane (50e percentile)",
            "good_starter": "La ligne représente un bon titulaire (60e percentile)",
            "top_quartile": "La ligne représente un bon niveau (75e percentile)",
            "top_10": "La ligne représente un très haut niveau (90e percentile)"
        }
        
        st.caption(f"💡 {reference_info.get(metadata['reference_type'], 'Ligne de référence')}")
    
    @staticmethod
    def _render_radar_legend(selected_player: str, position: str, reference_label: str, color_key: str):
        """Affiche la légende du radar"""
        import streamlit as st
        
        color_var = f"var(--{color_key}-color)" if color_key != 'accent' else "var(--accent-color)"
        
        st.markdown(f"""
        <div class='chart-legend'>
            <div class='legend-item'>
                <div class='legend-color' style='background: {color_var};'></div>
                <span><strong>{selected_player}</strong> ({position})</span>
            </div>
            <div class='legend-item'>
                <div class='legend-color' style='background: rgba(255,255,255,0.6);'></div>
                <span>{reference_label}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_detailed_comparison(analysis: Dict, selected_player: str, position: str, domain: str):
        """Affiche la comparaison détaillée"""
        import streamlit as st
        
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📈 Comparaison Détaillée</h3>", unsafe_allow_html=True)
        
        # Sélectionner les 4 premières métriques pour la comparaison
        metrics_keys = list(analysis['metrics'].keys())[:4]
        comparison_metrics = {k: analysis['metrics'][k] for k in metrics_keys}
        avg_comparison = {k: analysis['avg_metrics'][k] for k in metrics_keys}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            f"Performance par 90min vs Moyenne des {position}s des Autres Ligues"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Statistiques de performance
        TabManager._render_performance_stats(analysis, selected_player, position)
    
    @staticmethod
    def _render_performance_stats(analysis: Dict, selected_player: str, position: str):
        """Affiche les statistiques de performance"""
        import streamlit as st
        
        percentiles = analysis['percentiles']
        metadata = analysis['metadata']
        
        # Calculs statistiques
        avg_percentile = np.mean(percentiles)
        above_reference = sum(1 for p in percentiles if p >= metadata.get('reference_type', 75))
        total_metrics = len(percentiles)
        
        # Trouver les points forts et axes d'amélioration
        metrics_names = list(analysis['metrics'].keys())
        max_percentile = max(percentiles)
        min_percentile = min(percentiles)
        max_metric = metrics_names[percentiles.index(max_percentile)]
        min_metric = metrics_names[percentiles.index(min_percentile)]
        
        # Affichage des stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Percentile Moyen",
                f"{avg_percentile:.1f}%",
                help=f"Percentile moyen de {selected_player} sur toutes les métriques"
            )
        
        with col2:
            reference_pct = {
                "median": 50, "good_starter": 60, "top_quartile": 75, "top_10": 90
            }.get(metadata.get('reference_type', 'top_quartile'), 75)
            
            st.metric(
                "Au-dessus référence",
                f"{above_reference}/{total_metrics}",
                help=f"Nombre de métriques au-dessus du {reference_pct}e percentile"
            )
        
        with col3:
            st.metric(
                "Point Fort",
                max_metric.replace('/90', '').replace('/', ' '),
                f"{max_percentile:.0f}%",
                help="Métrique avec le percentile le plus élevé"
            )
        
        with col4:
            st.metric(
                "Axe d'Amélioration", 
                min_metric.replace('/90', '').replace('/', ' '),
                f"{min_percentile:.0f}%",
                help="Métrique avec le percentile le plus bas"
            )



# ================================================================================================
# APPLICATION PRINCIPALE
# ================================================================================================

class FootballDashboard:
    """Classe principale de l'application Dashboard Football"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self._configure_page()
        self._load_styles()
        self._initialize_session_state()
    
    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(**Config.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS"""
        st.markdown(StyleManager.get_css(), unsafe_allow_html=True)
    
    def _initialize_session_state(self):
        """Initialise les variables de session"""
        if 'selected_player_history' not in st.session_state:
            st.session_state.selected_player_history = []
        if 'favorites' not in st.session_state:
            st.session_state.favorites = []
        if 'session_stats' not in st.session_state:
            st.session_state.session_stats = {
                'players_viewed': 0,
                'start_time': pd.Timestamp.now()
            }
    
    def run(self):
        """Méthode principale d'exécution de l'application"""
        # Chargement des données
        with st.spinner("Chargement des données..."):
            df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        # Affichage des statistiques générales
        self._render_data_overview(df)
        
        # Rendu de l'en-tête
        UIComponents.render_header()
        
        # Rendu de la sidebar et récupération des sélections
        selected_competition, selected_club, selected_position, selected_player, df_filtered = SidebarManager.render_sidebar(df)
        
        if selected_player:
            # Mise à jour des stats de session
            if selected_player not in st.session_state.selected_player_history:
                st.session_state.session_stats['players_viewed'] += 1
                st.session_state.selected_player_history.insert(0, selected_player)
                st.session_state.selected_player_history = st.session_state.selected_player_history[:5]
            
            # Breadcrumbs
            player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
            UIComponents.render_breadcrumbs(
                selected_competition, 
                player_data['Équipe'], 
                selected_player
            )
            
            # Carte joueur
            UIComponents.render_player_card(player_data, selected_competition)
            
            st.markdown("---")
            
            # Onglets principaux avec données des autres ligues et nouveau tab Profils Similaires
            self._render_main_tabs(player_data, selected_competition, selected_player, df)
        
        else:
            self._render_no_player_message()
        
        # Footer
        UIComponents.render_footer()
    
    def _render_data_overview(self, df: pd.DataFrame):
        """Aperçu des données"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "👥 Joueurs", 
                f"{len(df):,}",
                help="Nombre total de joueurs dans la base de données"
            )
        
        with col2:
            st.metric(
                "🏆 Compétitions", 
                f"{df['Compétition'].nunique()}",
                help="Nombre de compétitions analysées"
            )
        
        with col3:
            st.metric(
                "⚽ Équipes", 
                f"{df['Équipe'].nunique()}",
                help="Nombre d'équipes représentées"
            )
        
        with col4:
            st.metric(
                "🌐 Nations", 
                f"{df['Nationalité'].nunique()}",
                help="Nombre de nationalités représentées"
            )
        
        with col5:
            avg_age = df['Âge'].mean()
            st.metric(
                "📅 Âge Moyen", 
                f"{avg_age:.1f} ans",
                help="Âge moyen de tous les joueurs"
            )
    
    def _render_main_tabs(self, player_data: pd.Series, player_competition: str, 
                         selected_player: str, df_full: pd.DataFrame):
        """Rendu des onglets principaux"""
        # Obtenir les données des autres ligues pour comparaison
        df_other_leagues = DataManager.get_other_leagues_data(df_full, player_competition)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Performance Offensive", 
            "🛡️ Performance Défensive", 
            "🎨 Performance Technique",
            "👥 Profils Similaires", 
            "🔄 Comparaison"
        ])
        
        with tab1:
            TabManager.render_offensive_tab(player_data, df_other_leagues, selected_player, player_competition)
        
        with tab2:
            TabManager.render_defensive_tab(player_data, df_other_leagues, selected_player, player_competition)
        
        with tab3:
            TabManager.render_technical_tab(player_data, df_other_leagues, selected_player, player_competition)
        
        with tab4:
            TabManager.render_similar_players_tab(selected_player, df_full)
        
        with tab5:
            TabManager.render_comparison_tab(df_full, selected_player)
    
    def _render_no_player_message(self):
        """Affiche un message quand aucun joueur n'est sélectionné"""
        st.markdown("""
        <div style='background: var(--background-card); padding: 48px; border-radius: var(--radius-lg); 
                    text-align: center; border: 2px solid var(--border-color); margin: 32px 0;'>
            <h2 style='color: var(--primary-color); margin-bottom: 24px; font-size: 2em;'>⚠️ Aucun joueur sélectionné</h2>
            <p style='color: var(--text-primary); font-size: 1.2em; margin-bottom: 32px; line-height: 1.6;'>
                Veuillez ajuster les filtres dans la sidebar pour sélectionner un joueur à analyser.
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px; margin-top: 32px;'>
                <div class='metric-card-enhanced' style='padding: 24px;'>
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--primary-color);'>🎯</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Analyse Offensive</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Buts, passes décisives, xG</p>
                </div>
                <div class='metric-card-enhanced' style='padding: 24px;'>
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--accent-color);'>🛡️</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Analyse Défensive</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Tacles, interceptions, duels</p>
                </div>
                <div class='metric-card-enhanced' style='padding: 24px;'>
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--secondary-color);'>🎨</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Analyse Technique</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Passes, dribbles, touches</p>
                </div>
                <div class='metric-card-enhanced' style='padding: 24px;'>
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--secondary-color);'>👥</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Profils Similaires</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Joueurs au style proche</p>
                </div>
                <div class='metric-card-enhanced' style='padding: 24px;'>
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--warning);'>🔄</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Comparaison</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Radars et benchmarks</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Historique des joueurs consultés
        if st.session_state.selected_player_history:
            st.markdown("<h3 class='subsection-title-enhanced'>📚 Joueurs récemment consultés</h3>", unsafe_allow_html=True)
            
            history_cols = st.columns(min(len(st.session_state.selected_player_history), 5))
            for i, player in enumerate(st.session_state.selected_player_history):
                with history_cols[i]:
                    if st.button(f"🔄 {player}", key=f"history_{i}", use_container_width=True):
                        st.rerun()
    
    def _render_error_page(self):
        """Affiche la page d'erreur"""
        st.markdown("""
        <div style='background: var(--background-card); padding: 48px; border-radius: var(--radius-lg); 
                    text-align: center; border: 2px solid var(--danger); margin: 32px 0;'>
            <h1 style='color: var(--danger); margin-bottom: 24px; font-size: 2.5em;'>⚠️ Erreur de Chargement</h1>
            <p style='color: var(--text-primary); font-size: 1.2em; margin-bottom: 32px; line-height: 1.6;'>
                Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
            </p>
            <div style='background: var(--background-surface); max-width: 600px; margin: 32px auto 0 auto; 
                        padding: 24px; border-radius: var(--radius-md); border: 1px solid var(--border-color);'>
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
                    background: var(--primary-color); color: white; border: none; padding: 12px 24px;
                    border-radius: 8px; font-size: 1em; font-weight: 600; cursor: pointer; transition: all 0.2s ease;
                ' onmouseover='this.style.background="var(--secondary-color)"' 
                  onmouseout='this.style.background="var(--primary-color)"'>
                    🔄 Réessayer
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# ================================================================================================

def main():
    """Point d'entrée principal de l'application"""
    try:
        dashboard = FootballDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"❌ Erreur inattendue : {str(e)}")
        
        # Affichage détaillé de l'erreur en mode debug
        with st.expander("🔍 Détails de l'erreur (Debug)", expanded=False):
            import traceback
            st.code(traceback.format_exc())
        
        # Bouton pour relancer l'application
        if st.button("🔄 Relancer l'application", type="primary"):
            st.rerun()

# ================================================================================================
# EXÉCUTION DE L'APPLICATION
# ================================================================================================

if __name__ == "__main__":
    main()
