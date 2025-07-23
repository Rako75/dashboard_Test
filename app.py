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
    """Configuration centralisée de l'application"""
    
    # Configuration de la page Streamlit
    PAGE_CONFIG = {
        "page_title": "Dashboard Football Pro",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Palette de couleurs
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
    
    # Mapping des positions
    POSITION_MAPPING = {
        'GK': 'Gardien',
        'DF': 'Défenseur', 
        'MF': 'Milieu',
        'FW': 'Attaquant'
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
    
    # Métriques pour l'analyse de similarité (version enrichie)
    SIMILARITY_METRICS = [
        # Métriques de base (volume)
        'Minutes jouées',
        'Buts',
        'Passes décisives',
        'Tirs',
        'Passes clés',
        'Passes tentées',
        'Dribbles tentés',
        'Dribbles réussis',
        'Tacles gagnants',
        'Interceptions',
        
        # Métriques de qualité/efficacité
        'Pourcentage de passes réussies',
        'Pourcentage de dribbles réussis',
        'Ballons récupérés',
        
        # Métriques de progression
        'Passes progressives',
        'Courses progressives',
        'Passes dans le dernier tiers',
        
        # Métriques physiques/aériennes
        'Duels aériens gagnés',
        'Duels défensifs gagnés',
        
        # Métriques de finition
        'Tirs cadrés',
        'Actions menant à un tir'
    ]
    
    # Métriques étendues pour l'analyse comparative
    COMPREHENSIVE_METRICS = {
        'offensive': [
            'Buts', 'Passes décisives', 'Tirs', 'Tirs cadrés', 'Passes clés',
            'Actions menant à un tir', 'Actions menant à un but', 'Dribbles réussis',
            'Buts attendus', 'Passes décisives attendues', 'Centres réussis', 'Buts de la tête'
        ],
        'defensive': [
            'Tacles gagnants', 'Interceptions', 'Ballons récupérés', 'Dégagements',
            'Duels défensifs gagnés', 'Duels aériens gagnés', 'Tirs bloqués',
            'Fautes commises', 'Cartons jaunes', 'Cartons rouges', 'Duels gagnés', 'Erreurs menant à un tir'
        ],
        'technical': [
            'Passes tentées', 'Passes progressives', 'Passes dans le dernier tiers',
            'Passes dans la surface', 'Centres tentés', 'Centres réussis',
            'Dribbles tentés', 'Touches de balle', 'Ballons perdus', 'Passes longues tentées',
            'Passes longues réussies', 'Passes courtes tentées'
        ],
        'passing': [
            'Passes tentées', 'Passes réussies', 'Passes progressives', 'Passes clés',
            'Passes dans le dernier tiers', 'Passes dans la surface', 'Passes longues tentées',
            'Passes longues réussies', 'Passes courtes tentées', 'Passes courtes réussies',
            'Centres tentés', 'Centres réussis'
        ]
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
            # Mapper les positions vers les nouveaux noms
            if 'Position' in df.columns:
                df['Position'] = df['Position'].map(Config.POSITION_MAPPING).fillna(df['Position'])
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
    def filter_by_club(df: pd.DataFrame, club: str) -> pd.DataFrame:
        """Filtre les données par club"""
        return df[df['Équipe'] == club]
    
    @staticmethod
    def filter_by_position(df: pd.DataFrame, position: str) -> pd.DataFrame:
        """Filtre les données par position"""
        return df[df['Position'] == position]
    
    @staticmethod
    def filter_by_minutes(df: pd.DataFrame, min_minutes: int) -> pd.DataFrame:
        """Filtre les données par minutes jouées"""
        return df[df['Minutes jouées'] >= min_minutes]
    
    @staticmethod
    def get_competitions(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des compétitions"""
        return sorted(df['Compétition'].dropna().unique())
    
    @staticmethod 
    def get_clubs(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des clubs"""
        return sorted(df['Équipe'].dropna().unique())
    
    @staticmethod
    def get_positions(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des positions"""
        positions = sorted(df['Position'].dropna().unique())
        # S'assurer que les positions mappées sont utilisées
        mapped_positions = []
        for pos in positions:
            if pos in Config.POSITION_MAPPING.values():
                mapped_positions.append(pos)
            elif pos in Config.POSITION_MAPPING:
                mapped_positions.append(Config.POSITION_MAPPING[pos])
            else:
                mapped_positions.append(pos)
        return sorted(list(set(mapped_positions)))
    
    @staticmethod
    def get_players(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des joueurs"""
        return sorted(df['Joueur'].dropna().unique())
    
    @staticmethod
    def get_other_leagues_data(df: pd.DataFrame, player_competition: str) -> pd.DataFrame:
        """Récupère les données de toutes les autres ligues (sauf celle du joueur)"""
        return df[df['Compétition'] != player_competition]
    
    @staticmethod
    def get_players_by_position_from_other_leagues(df: pd.DataFrame, player_position: str, player_competition: str) -> pd.DataFrame:
        """Récupère les joueurs du même poste dans les autres ligues"""
        other_leagues_df = DataManager.get_other_leagues_data(df, player_competition)
        return other_leagues_df[other_leagues_df['Position'] == player_position]

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
    """Calculateur de métriques et percentiles"""
    
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
    """Configuration centralisée de l'application"""
    
    # Configuration de la page Streamlit
    PAGE_CONFIG = {
        "page_title": "Dashboard Football Pro",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Palette de couleurs
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
    
    # Mapping des positions
    POSITION_MAPPING = {
        'GK': 'Gardien',
        'DF': 'Défenseur', 
        'MF': 'Milieu',
        'FW': 'Attaquant'
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
    
    # Métriques pour l'analyse de similarité (version enrichie)
    SIMILARITY_METRICS = [
        # Métriques de base (volume)
        'Minutes jouées',
        'Buts',
        'Passes décisives',
        'Tirs',
        'Passes clés',
        'Passes tentées',
        'Dribbles tentés',
        'Dribbles réussis',
        'Tacles gagnants',
        'Interceptions',
        
        # Métriques de qualité/efficacité
        'Pourcentage de passes réussies',
        'Pourcentage de dribbles réussis',
        'Ballons récupérés',
        
        # Métriques de progression
        'Passes progressives',
        'Courses progressives',
        'Passes dans le dernier tiers',
        
        # Métriques physiques/aériennes
        'Duels aériens gagnés',
        'Duels défensifs gagnés',
        
        # Métriques de finition
        'Tirs cadrés',
        'Actions menant à un tir'
    ]
    
    # Métriques étendues pour l'analyse comparative
    COMPREHENSIVE_METRICS = {
        'offensive': [
            'Buts', 'Passes décisives', 'Tirs', 'Tirs cadrés', 'Passes clés',
            'Actions menant à un tir', 'Actions menant à un but', 'Dribbles réussis',
            'Buts attendus', 'Passes décisives attendues', 'Centres réussis', 'Buts de la tête'
        ],
        'defensive': [
            'Tacles gagnants', 'Interceptions', 'Ballons récupérés', 'Dégagements',
            'Duels défensifs gagnés', 'Duels aériens gagnés', 'Tirs bloqués',
            'Fautes commises', 'Cartons jaunes', 'Cartons rouges', 'Duels gagnés', 'Erreurs menant à un tir'
        ],
        'technical': [
            'Passes tentées', 'Passes progressives', 'Passes dans le dernier tiers',
            'Passes dans la surface', 'Centres tentés', 'Centres réussis',
            'Dribbles tentés', 'Touches de balle', 'Ballons perdus', 'Passes longues tentées',
            'Passes longues réussies', 'Passes courtes tentées'
        ],
        'passing': [
            'Passes tentées', 'Passes réussies', 'Passes progressives', 'Passes clés',
            'Passes dans le dernier tiers', 'Passes dans la surface', 'Passes longues tentées',
            'Passes longues réussies', 'Passes courtes tentées', 'Passes courtes réussies',
            'Centres tentés', 'Centres réussis'
        ]
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
            # Mapper les positions vers les nouveaux noms
            if 'Position' in df.columns:
                df['Position'] = df['Position'].map(Config.POSITION_MAPPING).fillna(df['Position'])
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
    def filter_by_club(df: pd.DataFrame, club: str) -> pd.DataFrame:
        """Filtre les données par club"""
        return df[df['Équipe'] == club]
    
    @staticmethod
    def filter_by_position(df: pd.DataFrame, position: str) -> pd.DataFrame:
        """Filtre les données par position"""
        return df[df['Position'] == position]
    
    @staticmethod
    def filter_by_minutes(df: pd.DataFrame, min_minutes: int) -> pd.DataFrame:
        """Filtre les données par minutes jouées"""
        return df[df['Minutes jouées'] >= min_minutes]
    
    @staticmethod
    def get_competitions(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des compétitions"""
        return sorted(df['Compétition'].dropna().unique())
    
    @staticmethod 
    def get_clubs(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des clubs"""
        return sorted(df['Équipe'].dropna().unique())
    
    @staticmethod
    def get_positions(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des positions"""
        positions = sorted(df['Position'].dropna().unique())
        # S'assurer que les positions mappées sont utilisées
        mapped_positions = []
        for pos in positions:
            if pos in Config.POSITION_MAPPING.values():
                mapped_positions.append(pos)
            elif pos in Config.POSITION_MAPPING:
                mapped_positions.append(Config.POSITION_MAPPING[pos])
            else:
                mapped_positions.append(pos)
        return sorted(list(set(mapped_positions)))
    
    @staticmethod
    def get_players(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des joueurs"""
        return sorted(df['Joueur'].dropna().unique())
    
    @staticmethod
    def get_other_leagues_data(df: pd.DataFrame, player_competition: str) -> pd.DataFrame:
        """Récupère les données de toutes les autres ligues (sauf celle du joueur)"""
        return df[df['Compétition'] != player_competition]
    
    @staticmethod
    def get_players_by_position_from_other_leagues(df: pd.DataFrame, player_position: str, player_competition: str) -> pd.DataFrame:
        """Récupère les joueurs du même poste dans les autres ligues"""
        other_leagues_df = DataManager.get_other_leagues_data(df, player_competition)
        return other_leagues_df[other_leagues_df['Position'] == player_position]

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
    """Calculateur de métriques et percentiles"""
    
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
        

    @staticmethod
    def _render_comparative_radar(df: pd.DataFrame, competitions: List[str]):
        """Rendu du radar comparatif"""
        st.markdown("<h3 class='subsection-title-enhanced'>⚙️ Configuration de la Comparaison</h3>", unsafe_allow_html=True)
        
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
            st.markdown(f"<h3 class='subsection-title-enhanced'>⚔️ {joueur1} vs {joueur2}</h3>", unsafe_allow_html=True)
            
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
                    params=list(Config.RADAR_METRICS.keys()),
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
                        facecolor=Config.COLORS['primary'], 
                        edgecolor="#FFFFFF", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_compare=dict(
                        facecolor=Config.COLORS['secondary'], 
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
                            facecolor=Config.COLORS['primary'], 
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
                            facecolor=Config.COLORS['secondary'], 
                            boxstyle="round,pad=0.3", 
                            lw=1.5
                        )
                    )
                )
                
                # Titre unifié
                fig.text(0.515, 0.97, "Analyse Radar Comparative | Percentiles | Saison 2024-25",
                         size=16, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                
                # Légende
                legend_p1 = mpatches.Patch(color=Config.COLORS['primary'], label=joueur1)
                legend_p2 = mpatches.Patch(color=Config.COLORS['secondary'], label=joueur2)
                ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0),
                         frameon=False, labelcolor='white')
                
                # Footer
                fig.text(0.99, 0.01, "Dashboard Football Pro | Source: FBRef",
                         size=9, ha="right", fontproperties=font_italic.prop, color="#a6a6a6")
                
                st.pyplot(fig, use_container_width=True)
                
                # Comparaison statistique
                st.markdown("---")
                st.markdown("<h3 class='subsection-title-enhanced'>📊 Comparaison Statistique</h3>", unsafe_allow_html=True)
                
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
# APPLICATION PRINCIPALE - VERSION MODIFIÉE
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
            
            # Onglets principaux avec comparaison par poste
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
        """Rendu des onglets principaux avec comparaison par poste"""
        # Obtenir les données des joueurs du même poste dans les autres ligues
        df_same_position_other_leagues = DataManager.get_players_by_position_from_other_leagues(
            df_full, player_data['Position'], player_competition
        )
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Performance Offensive", 
            "🛡️ Performance Défensive", 
            "🎨 Performance Technique",
            "👥 Profils Similaires", 
            "🔄 Comparaison"
        ])
        
        with tab1:
            TabManager.render_offensive_tab(player_data, df_same_position_other_leagues, selected_player, player_competition)
        
        with tab2:
            TabManager.render_defensive_tab(player_data, df_same_position_other_leagues, selected_player, player_competition)
        
        with tab3:
            TabManager.render_technical_tab(player_data, df_same_position_other_leagues, selected_player, player_competition)
        
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
