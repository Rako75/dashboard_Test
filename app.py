"""
Dashboard Football Professionnel - Version Restructurée avec Cosine Similarity
===============================================================================

Application Streamlit pour l'analyse avancée des performances footballistiques.
Auteur: Dashboard Pro
Version: 2.2.0 - Cosine Similarity avec toutes les métriques
"""

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
    from sklearn.metrics.pairwise import cosine_similarity
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
    
    # Colonnes à exclure pour l'analyse de similarité (non numériques ou non pertinentes)
    EXCLUDED_SIMILARITY_COLUMNS = {
        'Joueur', 'Équipe', 'Compétition', 'Position', 'Nationalité', 'Né',
        'Matchs', 'Titulaire', 'Remplaçant', 'Équipe non renseignée', 'Saison',
        'Unnamed: 0', 'index', 'level_0', 'level_1', 'ID', 'id', 'player_id',
        'team_id', 'competition_id', 'url', 'photo', 'link', 'href'
    }
    
    # Métriques pour les histogrammes de comparaison
    HISTOGRAM_METRICS = [
        'Buts',
        'Passes décisives',
        'Tirs',
        'Passes clés',
        'Dribbles réussis',
        'Tacles gagnants',
        'Interceptions',
        'Passes tentées',
        'Passes progressives',
        'Ballons récupérés',
        'Duels aériens gagnés',
        'Centres réussis',
        'Actions menant à un tir',
        'Passes dans le dernier tiers',
        'Passes dans la surface',
        'Dribbles tentés',
        'Touches de balle',
        'Dégagements',
        'Fautes commises',
        'Cartons jaunes'
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
    def cosine_similarity_manual(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcule la similarité cosinus manuellement"""
        try:
            # Vérifier que les vecteurs ne sont pas vides
            if len(vec1) == 0 or len(vec2) == 0:
                return 0.0
            
            # Vérifier que les vecteurs ont la même longueur
            if len(vec1) != len(vec2):
                return 0.0
            
            # Convertir en numpy arrays si nécessaire
            vec1 = np.array(vec1, dtype=float)
            vec2 = np.array(vec2, dtype=float)
            
            # Vérifier qu'il n'y a pas de NaN ou d'infinis
            if np.any(np.isnan(vec1)) or np.any(np.isnan(vec2)) or np.any(np.isinf(vec1)) or np.any(np.isinf(vec2)):
                return 0.0
            
            # Calculer le produit scalaire
            dot_product = np.dot(vec1, vec2)
            
            # Calculer les normes
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            # Éviter la division par zéro
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculer la similarité cosinus
            similarity = dot_product / (norm1 * norm2)
            
            # S'assurer que la valeur est entre -1 et 1
            similarity = np.clip(similarity, -1.0, 1.0)
            
            return float(similarity)
        
        except Exception as e:
            # En cas d'erreur, retourner 0
            return 0.0
    
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
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: var(--spacing-xl);
            border-radius: var(--radius-lg);
            text-align: center;
            margin-bottom: var(--spacing-xl);
            box-shadow: var(--shadow-lg);
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
            df = pd.read_csv(file_path, encoding='utf-8', delimiter=',')
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
    
    @staticmethod
    def get_numeric_columns(df: pd.DataFrame) -> List[str]:
        """Récupère toutes les colonnes numériques disponibles pour l'analyse de similarité"""
        # Sélectionner toutes les colonnes numériques
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Exclure les colonnes non pertinentes
        relevant_columns = [col for col in numeric_columns if col not in Config.EXCLUDED_SIMILARITY_COLUMNS]
        
        # Vérifier qu'il y a bien des colonnes numériques
        if not relevant_columns:
            st.warning("⚠️ Aucune colonne numérique trouvée pour l'analyse de similarité")
            return []
        
        return relevant_columns

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
# ANALYSEUR DE JOUEURS SIMILAIRES AVEC COSINE SIMILARITY
# ================================================================================================

class SimilarPlayerAnalyzer:
    """Analyseur pour trouver des joueurs similaires avec Cosine Similarity"""
    
    @staticmethod
    def prepare_similarity_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Prépare les données pour l'analyse de similarité avec toutes les métriques numériques"""
        # Obtenir toutes les colonnes numériques pertinentes
        numeric_columns = DataManager.get_numeric_columns(df)
        
        if not numeric_columns:
            st.warning("⚠️ Aucune métrique numérique disponible pour l'analyse de similarité")
            return pd.DataFrame(), []
        
        # Créer le DataFrame avec toutes les métriques disponibles
        required_cols = ['Joueur', 'Équipe', 'Compétition', 'Position', 'Âge']
        available_required = [col for col in required_cols if col in df.columns]
        
        if not available_required:
            st.error("❌ Colonnes essentielles manquantes pour l'analyse")
            return pd.DataFrame(), []
        
        # Vérifier que les colonnes numériques existent vraiment dans le DataFrame
        existing_numeric_cols = [col for col in numeric_columns if col in df.columns]
        
        if not existing_numeric_cols:
            st.error("❌ Aucune colonne numérique valide trouvée")
            return pd.DataFrame(), []
        
        try:
            similarity_df = df[available_required + existing_numeric_cols].copy()
            
            # Remplacer les valeurs manquantes par 0 pour toutes les colonnes numériques
            for col in existing_numeric_cols:
                similarity_df[col] = pd.to_numeric(similarity_df[col], errors='coerce').fillna(0)
            
            # Filtrer les lignes avec des données valides
            similarity_df = similarity_df.dropna(subset=['Joueur'])
            
            # Vérifier qu'il reste des données
            if similarity_df.empty:
                st.error("❌ Aucune donnée valide après nettoyage")
                return pd.DataFrame(), []
            
            # Afficher les métriques utilisées
            st.info(f"📊 Analyse de similarité basée sur **{len(existing_numeric_cols)}** métriques : {', '.join(existing_numeric_cols[:10])}{'...' if len(existing_numeric_cols) > 10 else ''}")
            
            return similarity_df, existing_numeric_cols
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la préparation des données : {str(e)}")
            return pd.DataFrame(), []
    
    @staticmethod
    def calculate_similarity_with_cosine(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Calcule la similarité avec Cosine Similarity (sklearn)"""
        try:
            # Préparer les données
            similarity_df, available_metrics = SimilarPlayerAnalyzer.prepare_similarity_data(df)
            
            if similarity_df.empty or not available_metrics:
                return []
            
            # Obtenir les données du joueur cible
            target_data = similarity_df[similarity_df['Joueur'] == target_player]
            if target_data.empty:
                st.error(f"❌ Joueur '{target_player}' non trouvé dans les données")
                return []
            
            # Extraire les valeurs numériques du joueur cible
            target_values = target_data[available_metrics].iloc[0].values
            
            # Vérifier que les valeurs sont bien numériques
            if not all(isinstance(val, (int, float, np.number)) for val in target_values):
                st.error("❌ Données non numériques détectées pour le joueur cible")
                return []
            
            # Filtrer les autres joueurs (exclure le joueur cible)
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                st.warning("⚠️ Aucun autre joueur trouvé pour la comparaison")
                return []
            
            # Extraire les valeurs numériques des autres joueurs
            others_values = other_players[available_metrics].values
            
            # Vérifier la forme des données
            if others_values.shape[0] == 0 or others_values.shape[1] == 0:
                st.error("❌ Données vides pour les autres joueurs")
                return []
            
            # Normaliser les données
            scaler = StandardScaler()
            
            # Préparer toutes les données pour la normalisation
            all_data = similarity_df[available_metrics].values
            
            # Vérifier que les données sont valides
            if all_data.shape[0] == 0 or all_data.shape[1] == 0:
                st.error("❌ Données insuffisantes pour l'analyse")
                return []
            
            # Ajuster le scaler sur toutes les données
            scaler.fit(all_data)
            
            # Normaliser les données
            target_normalized = scaler.transform(target_values.reshape(1, -1))
            others_normalized = scaler.transform(others_values)
            
            # Calculer la similarité cosinus
            similarities = cosine_similarity(target_normalized, others_normalized)[0]
            
            # Convertir en scores de similarité (0-100)
            similarity_scores = np.clip(similarities * 100, 0, 100).tolist()
            
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
                    'data': row
                })
            
            # Trier par score de similarité décroissant
            similar_players.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_players[:num_similar]
            
        except Exception as e:
            st.error(f"❌ Erreur lors du calcul de similarité avec sklearn : {str(e)}")
            import traceback
            with st.expander("🔍 Détails de l'erreur", expanded=False):
                st.code(traceback.format_exc())
            return []
    
    @staticmethod
    def calculate_similarity_manual_cosine(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Calcule la similarité avec Cosine Similarity (implémentation manuelle)"""
        try:
            # Préparer les données
            similarity_df, available_metrics = SimilarPlayerAnalyzer.prepare_similarity_data(df)
            
            if similarity_df.empty or not available_metrics:
                return []
            
            # Obtenir les données du joueur cible
            target_data = similarity_df[similarity_df['Joueur'] == target_player]
            if target_data.empty:
                st.error(f"❌ Joueur '{target_player}' non trouvé dans les données")
                return []
            
            # Extraire les valeurs numériques du joueur cible
            target_values = target_data[available_metrics].iloc[0].values
            
            # Vérifier que les valeurs sont bien numériques
            if not all(isinstance(val, (int, float, np.number)) for val in target_values):
                st.error("❌ Données non numériques détectées pour le joueur cible")
                return []
            
            # Filtrer les autres joueurs (exclure le joueur cible)
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                st.warning("⚠️ Aucun autre joueur trouvé pour la comparaison")
                return []
            
            # Normaliser les données manuellement
            all_data = similarity_df[available_metrics].values
            mean_vals = np.mean(all_data, axis=0)
            std_vals = np.std(all_data, axis=0)
            
            # Éviter division par zéro
            std_vals[std_vals == 0] = 1
            
            # Normaliser le joueur cible
            target_normalized = (target_values - mean_vals) / std_vals
            
            # Calculer la similarité cosinus avec chaque joueur
            similarities = []
            
            for idx, player_row in other_players.iterrows():
                try:
                    player_values = player_row[available_metrics].values
                    
                    # Vérifier que les valeurs sont numériques
                    if not all(isinstance(val, (int, float, np.number)) for val in player_values):
                        continue
                    
                    player_normalized = (player_values - mean_vals) / std_vals
                    
                    # Calculer la similarité cosinus
                    cosine_sim = Utils.cosine_similarity_manual(target_normalized, player_normalized)
                    
                    # Convertir en score de similarité (0-100)
                    similarity_score = np.clip(cosine_sim * 100, 0, 100)
                    
                    similarities.append({
                        'joueur': player_row['Joueur'],
                        'equipe': player_row['Équipe'],
                        'competition': player_row['Compétition'],
                        'position': player_row['Position'],
                        'age': player_row['Âge'],
                        'similarity_score': similarity_score,
                        'data': player_row
                    })
                    
                except Exception as e:
                    # Ignorer les joueurs avec des données problématiques
                    continue
            
            # Trier par score de similarité décroissant
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similarities[:num_similar]
            
        except Exception as e:
            st.error(f"❌ Erreur lors du calcul de similarité manuelle : {str(e)}")
            import traceback
            with st.expander("🔍 Détails de l'erreur", expanded=False):
                st.code(traceback.format_exc())
            return []
    
    @staticmethod
    def calculate_similarity(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Point d'entrée principal pour le calcul de similarité avec Cosine Similarity"""
        if SKLEARN_AVAILABLE:
            return SimilarPlayerAnalyzer.calculate_similarity_with_cosine(target_player, df, num_similar)
        else:
            return SimilarPlayerAnalyzer.calculate_similarity_manual_cosine(target_player, df, num_similar)

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
        
        # Vérifier que la métrique existe
        if metric not in df.columns:
            st.error(f"La métrique '{metric}' n'existe pas dans les données")
            return go.Figure()
        
        # Obtenir les données du joueur cible
        target_data = df[df['Joueur'] == target_player]
        if target_data.empty:
            st.error(f"Joueur '{target_player}' non trouvé")
            return go.Figure()
        
        target_value = target_data[metric].iloc[0]
        if pd.isna(target_value):
            target_value = 0
        
        # Préparer les données pour l'histogramme
        player_names = [target_player]
        player_values = [float(target_value)]
        player_colors = [Config.COLORS['primary']]
        
        # Ajouter les joueurs similaires
        for i, player_info in enumerate(similar_players):
            player_data = player_info['data']
            value = player_data.get(metric, 0)
            if pd.isna(value):
                value = 0
            
            player_names.append(player_info['joueur'])
            player_values.append(float(value))
            
            # Couleur dégradée selon la similarité
            similarity_score = player_info['similarity_score']
            if similarity_score >= 85:
                color = Config.COLORS['secondary']
            elif similarity_score >= 70:
                color = Config.COLORS['warning']
            else:
                color = Config.COLORS['accent']
            
            player_colors.append(color)
        
        # Créer l'histogramme
        fig = go.Figure(data=[go.Bar(
            x=player_names,
            y=player_values,
            marker=dict(
                color=player_colors,
                line=dict(color='rgba(255,255,255,0.3)', width=2),
                opacity=0.8
            ),
            text=[f"{v:.1f}" for v in player_values],
            textposition='outside',
            textfont=dict(color='white', size=14, family='Inter', weight=600),
            hovertemplate='<b>%{x}</b><br>' + f'{metric}: %{{y:.2f}}<extra></extra>'
        )])
        
        # Ajouter une ligne horizontale pour la moyenne
        avg_value = np.mean(player_values)
        fig.add_hline(
            y=avg_value,
            line_dash="dash",
            line_color="rgba(255,255,255,0.6)",
            line_width=2,
            annotation_text=f"Moyenne: {avg_value:.1f}",
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
    """Analyseur de performance pour différents aspects du jeu"""
    
    @staticmethod
    def analyze_offensive_performance(player_data: pd.Series, df_comparison: pd.DataFrame) -> Dict:
        """Analyse complète de la performance offensive"""
        metrics = MetricsCalculator.calculate_offensive_metrics(player_data)
        
        # Calcul des moyennes des autres ligues
        avg_metrics = {}
        minutes_90_comp = df_comparison['Minutes jouées'] / 90
        
        avg_metrics['Buts/90'] = df_comparison.get('Buts par 90 minutes', pd.Series([0]*len(df_comparison))).mean()
        avg_metrics['Passes D./90'] = df_comparison.get('Passes décisives par 90 minutes', pd.Series([0]*len(df_comparison))).mean()
        avg_metrics['xG/90'] = df_comparison.get('Buts attendus par 90 minutes', pd.Series([0]*len(df_comparison))).mean()
        avg_metrics['xA/90'] = df_comparison.get('Passes décisives attendues par 90 minutes', pd.Series([0]*len(df_comparison))).mean()
        avg_metrics['Tirs/90'] = df_comparison.get('Tirs par 90 minutes', pd.Series([0]*len(df_comparison))).mean()
        avg_metrics['Passes clés/90'] = (df_comparison.get('Passes clés', pd.Series([0]*len(df_comparison))) / minutes_90_comp).mean()
        avg_metrics['Dribbles réussis/90'] = (df_comparison.get('Dribbles réussis', pd.Series([0]*len(df_comparison))) / minutes_90_comp).mean()
        avg_metrics['Actions → Tir/90'] = df_comparison.get('Actions menant à un tir par 90 minutes', pd.Series([0]*len(df_comparison))).mean()
        
        # Calcul des percentiles
        percentiles = []
        avg_percentiles = []
        
        for metric, value in metrics.items():
            if metric in ['Buts/90', 'Passes D./90', 'xG/90', 'xA/90', 'Tirs/90', 'Actions → Tir/90']:
                column_name = metric.replace('/90', ' par 90 minutes').replace('Passes D.', 'Passes décisives').replace('Actions → Tir', 'Actions menant à un tir')
                distribution = df_comparison.get(column_name, pd.Series([0]*len(df_comparison)))
            else:
                base_column = metric.replace('/90', '').replace('Passes D.', 'Passes décisives')
                distribution = df_comparison.get(base_column, pd.Series([0]*len(df_comparison))) / minutes_90_comp
            
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
    def analyze_defensive_performance(player_data: pd.Series, df_comparison: pd.DataFrame) -> Dict:
        """Analyse complète de la performance défensive"""
        metrics = MetricsCalculator.calculate_defensive_metrics(player_data)
        
        # Calcul des moyennes des autres ligues
        avg_metrics = {}
        minutes_90_comp = df_comparison['Minutes jouées'] / 90
        
        for metric_key in metrics.keys():
            if metric_key.endswith('/90'):
                base_metric = metric_key.replace('/90', '')
                column_name = base_metric
                if base_metric == 'Tacles':
                    column_name = 'Tacles gagnants'
                elif base_metric == 'Duels aériens':
                    column_name = 'Duels aériens gagnés'
                elif base_metric == 'Tirs bloqués':
                    column_name = 'Tirs bloqués'
                elif base_metric == 'Ballons récupérés':
                    column_name = 'Ballons récupérés'
                
                avg_metrics[metric_key] = (df_comparison.get(column_name, pd.Series([0]*len(df_comparison))) / minutes_90_comp).mean()
            else:
                column_name = metric_key.replace('% ', 'Pourcentage de ').replace(' gagnés', ' gagnés').replace(' aériens', ' aériens gagnés')
                avg_metrics[metric_key] = df_comparison.get(column_name, pd.Series([0]*len(df_comparison))).mean()
        
        # Calcul des percentiles
        percentiles = []
        avg_percentiles = []
        
        for metric, value in metrics.items():
            if metric.endswith('/90'):
                base_metric = metric.replace('/90', '')
                column_name = base_metric
                if base_metric == 'Tacles':
                    column_name = 'Tacles gagnants'
                elif base_metric == 'Duels aériens':
                    column_name = 'Duels aériens gagnés'
                elif base_metric == 'Tirs bloqués':
                    column_name = 'Tirs bloqués'
                elif base_metric == 'Ballons récupérés':
                    column_name = 'Ballons récupérés'
                
                distribution = df_comparison.get(column_name, pd.Series([0]*len(df_comparison))) / minutes_90_comp
            else:
                column_name = metric.replace('% ', 'Pourcentage de ').replace(' gagnés', ' gagnés').replace(' aériens', ' aériens gagnés')
                distribution = df_comparison.get(column_name, pd.Series([0]*len(df_comparison)))
            
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
        
        # Calcul des moyennes des autres ligues
        avg_metrics = {}
        minutes_90_comp = df_comparison['Minutes jouées'] / 90
        
        for metric_key in metrics.keys():
            if metric_key.endswith('/90'):
                base_metric = metric_key.replace('/90', '')
                column_name = base_metric
                if base_metric == 'Passes prog.':
                    column_name = 'Passes progressives'
                elif base_metric == 'Dribbles':
                    column_name = 'Dribbles tentés'
                elif base_metric == 'Passes tentées':
                    column_name = 'Passes tentées'
                elif base_metric == 'Passes clés':
                    column_name = 'Passes clés'
                
                avg_metrics[metric_key] = (df_comparison.get(column_name, pd.Series([0]*len(df_comparison))) / minutes_90_comp).mean()
            else:
                column_name = metric_key.replace('% ', 'Pourcentage de ').replace(' réussies', ' réussies').replace(' réussis', ' réussis')
                avg_metrics[metric_key] = df_comparison.get(column_name, pd.Series([0]*len(df_comparison))).mean()
        
        # Calcul des percentiles
        percentiles = []
        avg_percentiles = []
        
        for metric, value in metrics.items():
            if metric.endswith('/90'):
                base_metric = metric.replace('/90', '')
                column_name = base_metric
                if base_metric == 'Passes prog.':
                    column_name = 'Passes progressives'
                elif base_metric == 'Dribbles':
                    column_name = 'Dribbles tentés'
                elif base_metric == 'Passes tentées':
                    column_name = 'Passes tentées'
                elif base_metric == 'Passes clés':
                    column_name = 'Passes clés'
                
                distribution = df_comparison.get(column_name, pd.Series([0]*len(df_comparison))) / minutes_90_comp
            else:
                column_name = metric.replace('% ', 'Pourcentage de ').replace(' réussies', ' réussies').replace(' réussis', ' réussis')
                distribution = df_comparison.get(column_name, pd.Series([0]*len(df_comparison)))
            
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
# COMPOSANTS UI
# ================================================================================================

class UIComponents:
    """Composants d'interface utilisateur réutilisables"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête principal"""
        st.markdown("""
        <div class='player-header-card animated-card'>
            <h1 style='color: white; margin: 0; font-size: 3.5em; font-weight: 800; letter-spacing: -0.02em;'>
                Dashboard Football Professionnel
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 16px 0 0 0; font-size: 1.25em; font-weight: 500;'>
                Analyse avancée avec Cosine Similarity - Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
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
        """Affiche une carte pour un joueur similaire avec logo du club"""
        similarity_score = player_info['similarity_score']
        player_data = player_info['data']
        
        # Couleur basée sur le score de similarité
        if similarity_score >= 85:
            score_color = "#2ca02c"  # Vert
        elif similarity_score >= 70:
            score_color = "#ff7f0e"  # Orange
        else:
            score_color = "#1f77b4"  # Bleu
        
        # Utiliser la vraie valeur marchande du joueur depuis ses données
        valeur_marchande = Utils.get_market_value_safe(player_data)
        
        # Obtenir le logo du club
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
        
        st.markdown(f"""
        <div class='similar-player-card animated-card'>
            <div class='similarity-score' style='background: {score_color};'>
                #{rank} • {similarity_score:.1f}% similaire
            </div>
            <div class='player-header-with-logo'>
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
        st.markdown("""
        <div class='dashboard-footer animated-card'>
            <h3 style='color: var(--primary-color); margin: 0 0 16px 0; font-weight: 700; font-size: 1.25em;'>
                Dashboard Football Professionnel
            </h3>
            <p style='color: var(--text-primary); margin: 0; font-size: 1.1em; font-weight: 500;'>
                Analyse avancée avec Cosine Similarity
            </p>
            <p style='color: var(--text-secondary); margin: 12px 0 0 0; font-size: 0.9em;'>
                Données: FBRef | Design: Dashboard Pro | Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE SIDEBAR
# ================================================================================================

class SidebarManager:
    """Gestionnaire pour la sidebar"""
    
    @staticmethod
    def render_sidebar(df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
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
            
            # Filtre par minutes jouées
            min_minutes_filter = 0
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
                    help="Filtrer les joueurs ayant joué au minimum ce nombre de minutes"
                )
                
                # Progress bar
                if max_minutes > min_minutes:
                    percentage_filtered = (min_minutes_filter - min_minutes) / (max_minutes - min_minutes) * 100
                    st.progress(percentage_filtered / 100)
            
            # Application du filtre minutes
            df_filtered_minutes = DataManager.filter_by_minutes(df_filtered, min_minutes_filter)
            
            # Informations sur le filtrage
            nb_joueurs = len(df_filtered_minutes)
            
            if nb_joueurs > 0:
                st.success(f"✅ **{nb_joueurs} joueurs** correspondent aux critères")
                
                # Statistiques additionnelles
                with st.expander("📊 Statistiques du filtrage", expanded=False):
                    avg_minutes = df_filtered_minutes['Minutes jouées'].mean()
                    st.write(f"• Moyenne minutes: {avg_minutes:.0f}")
                    st.write(f"• Équipes représentées: {df_filtered_minutes['Équipe'].nunique()}")
                    st.write(f"• Positions: {df_filtered_minutes['Position'].nunique()}")
            else:
                st.warning("⚠️ Aucun joueur ne correspond aux critères")
            
            st.markdown("---")
            
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
            
            # Footer sidebar
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
            
            return selected_competition, selected_player, df_filtered_minutes

# ================================================================================================
# GESTIONNAIRE DE TABS
# ================================================================================================

class TabManager:
    """Gestionnaire pour les différents onglets"""
    
    @staticmethod
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str, player_competition: str):
        """Rendu de l'onglet performance offensive"""
        st.markdown("<h2 class='section-title-enhanced'>🎯 Performance Offensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_offensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Graphique en barres des actions offensives
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
            
            # Métriques avec st.metric
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques Clés</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Buts par 90min",
                    value=f"{analysis['metrics']['Buts/90']:.2f}",
                    delta=f"{analysis['metrics']['Buts/90'] - analysis['avg_metrics']['Buts/90']:.2f}",
                    help="Nombre de buts marqués par 90 minutes de jeu"
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
            # Jauges avec % explicites
            efficiency_data = {
                'Conversion': (player_data.get('Buts', 0) / player_data.get('Tirs', 1) * 100) if player_data.get('Tirs', 0) > 0 else 0,
                'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                'Efficacité passes': (player_data.get('Passes décisives', 0) / player_data.get('Passes clés', 1) * 100) if player_data.get('Passes clés', 0) > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(efficiency_data, "Efficacité Offensive (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar avec titre unifié et légende
            st.markdown("<h3 class='subsection-title-enhanced'>🎯 Analyse Radar</h3>", unsafe_allow_html=True)
            
            # Légende explicite
            st.markdown(f"""
            <div class='chart-legend'>
                <div class='legend-item'>
                    <div class='legend-color' style='background: var(--primary-color);'></div>
                    <span>{selected_player}</span>
                </div>
                <div class='legend-item'>
                    <div class='legend-color' style='background: rgba(255,255,255,0.6);'></div>
                    <span>Moyenne autres ligues</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "autres ligues",
                Config.COLORS['primary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison détaillée
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📈 Comparaison Détaillée</h3>", unsafe_allow_html=True)
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "Performance par 90min vs Moyenne des Autres Ligues"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str, player_competition: str):
        """Rendu de l'onglet performance défensive"""
        st.markdown("<h2 class='section-title-enhanced'>🛡️ Performance Défensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_defensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Actions défensives
            basic_actions = {
                'Tacles': player_data.get('Tacles gagnants', 0),
                'Interceptions': player_data.get('Interceptions', 0),
                'Ballons récupérés': player_data.get('Ballons récupérés', 0),
                'Duels aériens': player_data.get('Duels aériens gagnés', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "Actions Défensives Totales",
                Config.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Métriques défensives
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques Défensives</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Tacles par 90min",
                    value=f"{analysis['metrics']['Tacles/90']:.2f}",
                    delta=f"{analysis['metrics']['Tacles/90'] - analysis['avg_metrics']['Tacles/90']:.2f}",
                    help="Nombre de tacles gagnants par 90 minutes de jeu"
                )
                st.metric(
                    label="Interceptions par 90min",
                    value=f"{analysis['metrics']['Interceptions/90']:.2f}",
                    delta=f"{analysis['metrics']['Interceptions/90'] - analysis['avg_metrics']['Interceptions/90']:.2f}",
                    help="Nombre d'interceptions par 90 minutes de jeu"
                )
            
            with metric_col2:
                st.metric(
                    label="% Duels gagnés",
                    value=f"{analysis['metrics']['% Duels gagnés']:.1f}%",
                    delta=f"{analysis['metrics']['% Duels gagnés'] - analysis['avg_metrics']['% Duels gagnés']:.1f}%",
                    help="Pourcentage de duels défensifs remportés"
                )
                st.metric(
                    label="% Duels aériens",
                    value=f"{analysis['metrics']['% Duels aériens']:.1f}%",
                    delta=f"{analysis['metrics']['% Duels aériens'] - analysis['avg_metrics']['% Duels aériens']:.1f}%",
                    help="Pourcentage de duels aériens remportés"
                )
        
        with col2:
            # Pourcentages de réussite
            success_data = {
                'Duels défensifs': player_data.get('Pourcentage de duels gagnés', 0),
                'Duels aériens': player_data.get('Pourcentage de duels aériens gagnés', 0),
                'Passes': player_data.get('Pourcentage de passes réussies', 0)
            }
            
            fig_gauge = ChartManager.create_gauge_chart(success_data, "Pourcentages de Réussite (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar défensif
            st.markdown("<h3 class='subsection-title-enhanced'>🛡️ Analyse Radar</h3>", unsafe_allow_html=True)
            
            # Légende explicite
            st.markdown(f"""
            <div class='chart-legend'>
                <div class='legend-item'>
                    <div class='legend-color' style='background: var(--accent-color);'></div>
                    <span>{selected_player}</span>
                </div>
                <div class='legend-item'>
                    <div class='legend-color' style='background: rgba(255,255,255,0.6);'></div>
                    <span>Moyenne autres ligues</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "autres ligues",
                Config.COLORS['accent']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison détaillée
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📈 Comparaison Détaillée</h3>", unsafe_allow_html=True)
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "Performance par 90min vs Moyenne des Autres Ligues"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_technical_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str, player_competition: str):
        """Rendu de l'onglet performance technique"""
        st.markdown("<h2 class='section-title-enhanced'>🎨 Performance Technique</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_technical_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Actions techniques
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
            
            # Métriques techniques
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques Techniques</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Passes par 90min",
                    value=f"{analysis['metrics']['Passes tentées/90']:.1f}",
                    delta=f"{analysis['metrics']['Passes tentées/90'] - analysis['avg_metrics']['Passes tentées/90']:.1f}",
                    help="Nombre de passes tentées par 90 minutes de jeu"
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
            # Pourcentages techniques
            technical_success = {
                'Passes réussies': player_data.get('Pourcentage de passes réussies', 0),
                'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                'Passes longues': player_data.get('Pourcentage de passes longues réussies', 0)
            }
            
            fig_gauge = ChartManager.create_gauge_chart(technical_success, "Précision Technique (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar technique
            st.markdown("<h3 class='subsection-title-enhanced'>🎨 Analyse Radar</h3>", unsafe_allow_html=True)
            
            # Légende explicite
            st.markdown(f"""
            <div class='chart-legend'>
                <div class='legend-item'>
                    <div class='legend-color' style='background: var(--secondary-color);'></div>
                    <span>{selected_player}</span>
                </div>
                <div class='legend-item'>
                    <div class='legend-color' style='background: rgba(255,255,255,0.6);'></div>
                    <span>Moyenne autres ligues</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "autres ligues",
                Config.COLORS['secondary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison détaillée
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📈 Comparaison Détaillée</h3>", unsafe_allow_html=True)
        
        selected_metrics = ['Passes tentées/90', 'Passes prog./90', 'Dribbles/90', 'Passes clés/90']
        comparison_metrics = {k: analysis['metrics'][k] for k in selected_metrics if k in analysis['metrics']}
        avg_comparison = {k: analysis['avg_metrics'][k] for k in selected_metrics if k in analysis['avg_metrics']}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "Performance par 90min vs Moyenne des Autres Ligues"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_similar_players_tab(selected_player: str, df: pd.DataFrame):
        """Rendu de l'onglet joueurs similaires avec Cosine Similarity et histogrammes de comparaison"""
        st.markdown("<h2 class='section-title-enhanced'>👥 Profils Similaires - Cosine Similarity</h2>", unsafe_allow_html=True)
        
        # Message d'information sur l'algorithme utilisé
        algorithm_info = "Cosine Similarity avec sklearn" if SKLEARN_AVAILABLE else "Cosine Similarity (implémentation manuelle)"
        st.info(f"🔬 **Algorithme utilisé**: {algorithm_info} - Analyse basée sur toutes les métriques numériques disponibles")
        
        # Diagnostic des données (optionnel)
        with st.expander("🔍 Diagnostic des données", expanded=False):
            st.write("**Informations sur les données:**")
            st.write(f"- Nombre total de joueurs: {len(df)}")
            st.write(f"- Nombre de colonnes: {len(df.columns)}")
            
            # Vérifier les colonnes numériques
            numeric_cols = DataManager.get_numeric_columns(df)
            st.write(f"- Colonnes numériques détectées: {len(numeric_cols)}")
            
            if numeric_cols:
                st.write("- Exemples de colonnes numériques:")
                for col in numeric_cols[:10]:  # Montrer les 10 premières
                    st.write(f"  • {col}")
                if len(numeric_cols) > 10:
                    st.write(f"  ... et {len(numeric_cols) - 10} autres")
            
            # Vérifier les données du joueur sélectionné
            player_data = df[df['Joueur'] == selected_player]
            if not player_data.empty:
                st.write(f"- Joueur '{selected_player}' trouvé ✅")
                # Compter combien de métriques numériques ont des valeurs non-nulles
                non_null_metrics = 0
                for col in numeric_cols:
                    if col in player_data.columns:
                        val = player_data[col].iloc[0]
                        if pd.notna(val) and val != 0:
                            non_null_metrics += 1
                st.write(f"- Métriques non-nulles pour ce joueur: {non_null_metrics}/{len(numeric_cols)}")
            else:
                st.write(f"- Joueur '{selected_player}' NON trouvé ❌")
        
        # Configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("<h3 class='subsection-title-enhanced'>⚙️ Configuration de l'Analyse</h3>", unsafe_allow_html=True)
        
        with col2:
            num_similar = st.slider(
                "Nombre de joueurs similaires à afficher :",
                min_value=1,
                max_value=10,
                value=5,
                help="Choisissez combien de joueurs similaires vous voulez voir"
            )
        
        # Calcul des joueurs similaires
        with st.spinner("🔍 Recherche de joueurs similaires avec Cosine Similarity..."):
            similar_players = SimilarPlayerAnalyzer.calculate_similarity(selected_player, df, num_similar)
        
        if not similar_players:
            st.warning("⚠️ Aucun joueur similaire trouvé. Vérifiez que le joueur sélectionné existe dans les données.")
            return
        
        # Affichage des résultats
        st.markdown(f"<h3 class='subsection-title-enhanced'>🎯 Top {len(similar_players)} joueurs les plus similaires à {selected_player}</h3>", unsafe_allow_html=True)
        
        # Métriques de résumé
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            avg_similarity = np.mean([p['similarity_score'] for p in similar_players])
            st.metric("Score de Similarité Moyen", f"{avg_similarity:.1f}%", 
                     help="Score moyen de similarité cosinus des joueurs trouvés")
        
        with metrics_col2:
            best_match = similar_players[0] if similar_players else None
            if best_match:
                st.metric("Meilleure Correspondance", best_match['joueur'], 
                         f"{best_match['similarity_score']:.1f}%")
        
        with metrics_col3:
            unique_competitions = len(set(p['competition'] for p in similar_players))
            st.metric("Compétitions Représentées", f"{unique_competitions}", 
                     help="Nombre de compétitions différentes")
        
        with metrics_col4:
            # Compter les métriques disponibles pour l'analyse
            similarity_df, available_metrics = SimilarPlayerAnalyzer.prepare_similarity_data(df)
            st.metric("Métriques Analysées", f"{len(available_metrics)}", 
                     help="Nombre de métriques numériques utilisées pour calculer la similarité cosinus")
        
        # Cartes des joueurs similaires
        st.markdown("---")
        
        # Affichage en colonnes
        cols_per_row = 2
        for i in range(0, len(similar_players), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(similar_players):
                    with col:
                        UIComponents.render_similar_player_card(similar_players[i + j], i + j + 1)
        
        # Section pour les histogrammes de comparaison
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📊 Histogrammes de Comparaison</h3>", unsafe_allow_html=True)
        
        # Sélection de la métrique pour l'histogramme
        available_histogram_metrics = [metric for metric in Config.HISTOGRAM_METRICS if metric in df.columns]
        
        if available_histogram_metrics:
            # Interface pour choisir la métrique
            metric_col1, metric_col2 = st.columns([2, 1])
            
            with metric_col1:
                selected_metric = st.selectbox(
                    "📈 Choisissez une métrique pour l'histogramme de comparaison :",
                    available_histogram_metrics,
                    index=0,
                    help="Sélectionnez la métrique à comparer entre le joueur sélectionné et les joueurs similaires"
                )
            
            with metric_col2:
                st.info(f"🎯 Comparaison sur : **{selected_metric}**")
            
            # Créer et afficher l'histogramme haute qualité
            if selected_metric:
                fig_histogram = ChartManager.create_histogram_comparison(
                    selected_player, similar_players, df, selected_metric
                )
                st.plotly_chart(fig_histogram, use_container_width=True)
                
                # Informations supplémentaires sur l'histogramme
                target_data = df[df['Joueur'] == selected_player]
                if not target_data.empty:
                    target_value = target_data[selected_metric].iloc[0]
                    if not pd.isna(target_value):
                        similar_values = []
                        for player_info in similar_players:
                            player_data = player_info['data']
                            value = player_data.get(selected_metric, 0)
                            if not pd.isna(value):
                                similar_values.append(value)
                        
                        if similar_values:
                            avg_similar = np.mean(similar_values)
                            max_similar = np.max(similar_values)
                            min_similar = np.min(similar_values)
                            
                            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                            
                            with stats_col1:
                                st.metric(f"{selected_player}", f"{target_value:.1f}", 
                                         help=f"Valeur du joueur sélectionné pour {selected_metric}")
                            
                            with stats_col2:
                                st.metric("Moyenne Similaires", f"{avg_similar:.1f}",
                                         delta=f"{target_value - avg_similar:.1f}",
                                         help="Moyenne des joueurs similaires")
                            
                            with stats_col3:
                                st.metric("Maximum", f"{max_similar:.1f}",
                                         help="Valeur maximale parmi les joueurs similaires")
                            
                            with stats_col4:
                                st.metric("Minimum", f"{min_similar:.1f}",
                                         help="Valeur minimale parmi les joueurs similaires")
        else:
            st.warning("⚠️ Aucune métrique disponible pour les histogrammes de comparaison")
    
    @staticmethod
    def render_comparison_tab(df: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet comparaison"""
        st.markdown("<h2 class='section-title-enhanced'>🔄 Comparaison Pizza Chart</h2>", unsafe_allow_html=True)
        
        # Mode de visualisation
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
        """Rendu du radar individuel"""
        st.markdown(f"<h3 class='subsection-title-enhanced'>🎯 Radar individuel : {selected_player}</h3>", unsafe_allow_html=True)
        
        try:
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
                params=list(Config.RADAR_METRICS.keys()),
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
                slice_colors=[Config.COLORS['primary']] * len(values),
                value_colors=["#ffffff"] * len(values),
                value_bck_colors=[Config.COLORS['primary']] * len(values),
                kwargs_slices=dict(edgecolor="#FFFFFF", zorder=2, linewidth=2),
                kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop),
                kwargs_values=dict(
                    color="#ffffff", 
                    fontsize=11, 
                    fontproperties=font_normal.prop,
                    bbox=dict(
                        edgecolor="#FFFFFF", 
                        facecolor=Config.COLORS['primary'], 
                        boxstyle="round,pad=0.3", 
                        lw=1.5
                    )
                )
            )
            
            # Titre unifié
            fig.text(0.515, 0.97, selected_player, size=28, ha="center", 
                    fontproperties=font_bold.prop, color="#ffffff", weight='bold')
            fig.text(0.515, 0.94, f"Analyse Radar Individuelle | Percentiles vs {competition} | Saison 2024-25", 
                    size=14, ha="center", fontproperties=font_bold.prop, color="#a6a6a6")
            
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
                max_param = list(Config.RADAR_METRICS.keys())[max_index]
                st.metric("Point Fort", f"{max_param.replace('\\n', ' ')}", f"{max_stat}%")
            
            with stats_col3:
                # Métriques où une valeur faible est positive (à exclure des axes d'amélioration)
                negative_metrics = ["Cartons\njaunes", "Cartons\nrouges", "Ballons perdus\nsous pression", "Ballons perdus\nen conduite"]
                
                # Filtrer les métriques pour l'axe d'amélioration
                filtered_values = []
                filtered_params = []
                
                for i, (param, value) in enumerate(zip(Config.RADAR_METRICS.keys(), values)):
                    if param not in negative_metrics:
                        filtered_values.append(value)
                        filtered_params.append(param)
                
                if filtered_values:
                    min_stat = min(filtered_values)
                    min_index = filtered_values.index(min_stat)
                    min_param = filtered_params[min_index]
                    st.metric("Axe d'Amélioration", f"{min_param.replace('\\n', ' ')}", f"{min_stat}%")
                else:
                    st.metric("Axe d'Amélioration", "Excellent partout", "✨")
            
        except Exception as e:
            st.error(f"Erreur lors de la création du radar individuel : {str(e)}")
    
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
        selected_competition, selected_player, df_filtered = SidebarManager.render_sidebar(df)
        
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
                "👥 Joueurs Total", 
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
            total_minutes = df['Minutes jouées'].sum()
            st.metric(
                "⏱️ Minutes Totales", 
                f"{total_minutes:,.0f}",
                help="Total des minutes jouées par tous les joueurs"
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
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Cosine Similarity</p>
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
