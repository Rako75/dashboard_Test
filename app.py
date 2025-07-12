"""
Dashboard Football Professionnel - Version Corrigée
=====================================================

Application Streamlit pour l'analyse avancée des performances footballistiques.
Auteur: Dashboard Pro
Version: 2.1.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import glob
from PIL import Image
import base64
import io
from typing import Dict, List, Optional, Tuple, Union
import warnings
warnings.filterwarnings('ignore')

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
    
    # Configuration des radars - métriques simplifiées pour éviter les erreurs
    RADAR_METRICS = {
        "Buts": "Buts",
        "Passes D.": "Passes décisives", 
        "Passes clés": "Passes clés",
        "Cartons J.": "Cartons jaunes",
        "Passes": "Passes tentées",
        "Dribbles": "Dribbles tentés",
        "Touches": "Touches de balle",
        "Tacles": "Tacles gagnants",
        "Interceptions": "Interceptions",
        "Dégagements": "Dégagements"
    }
    
    # Mapping des dossiers de logos
    LOGO_FOLDERS = {
        'Bundesliga': 'Bundesliga_Logos',
        'La Liga': 'La_Liga_Logos', 
        'Ligue 1': 'Ligue1_Logos',
        'Premier League': 'Premier_League_Logos',
        'Serie A': 'Serie_A_Logos'
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
                clean_value = ''.join(c for c in value if c.isdigit() or c == '.')
                value = float(clean_value) if clean_value else 0
            except (ValueError, TypeError):
                return str(value)
        
        try:
            value = float(value)
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
    
    @staticmethod
    def safe_get_value(series: pd.Series, key: str, default: float = 0.0) -> float:
        """Récupère une valeur de façon sécurisée"""
        try:
            value = series.get(key, default)
            if pd.isna(value) or np.isinf(value):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

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
            # Nettoyer les données
            df = df.fillna(0)
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
        return df[df['Compétition'] == competition].copy()
    
    @staticmethod
    def filter_by_multiple_competitions(df: pd.DataFrame, competitions: List[str]) -> pd.DataFrame:
        """Filtre les données par plusieurs compétitions"""
        return df[df['Compétition'].isin(competitions)].copy()
    
    @staticmethod
    def filter_by_minutes(df: pd.DataFrame, min_minutes: int) -> pd.DataFrame:
        """Filtre les données par minutes jouées"""
        return df[df['Minutes jouées'] >= min_minutes].copy()
    
    @staticmethod
    def get_competitions(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des compétitions"""
        return sorted(df['Compétition'].dropna().unique())
    
    @staticmethod
    def get_players(df: pd.DataFrame) -> List[str]:
        """Récupère la liste des joueurs"""
        return sorted(df['Joueur'].dropna().unique())

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
        
        return None

# ================================================================================================
# CALCULATEUR DE MÉTRIQUES
# ================================================================================================

class MetricsCalculator:
    """Calculateur de métriques et percentiles"""
    
    @staticmethod
    def calculate_percentiles(player_name: str, df: pd.DataFrame, df_comparison: pd.DataFrame = None) -> List[int]:
        """Calcule les percentiles pour le radar chart"""
        if df_comparison is None:
            df_comparison = df
        
        try:
            player = df[df["Joueur"] == player_name].iloc[0]
            percentiles = []

            for label, col in Config.RADAR_METRICS.items():
                try:
                    if col not in df_comparison.columns:
                        percentile = 50  # Valeur par défaut
                    else:
                        val = Utils.safe_get_value(player, col, 0)
                        
                        # Pour les métriques par 90 minutes
                        if col in ['Minutes jouées']:
                            distribution = df_comparison[col].replace([np.inf, -np.inf], np.nan).dropna()
                        else:
                            # Normaliser par 90 minutes si nécessaire
                            player_minutes = Utils.safe_get_value(player, 'Minutes jouées', 90)
                            if player_minutes > 0:
                                val_per_90 = (val / player_minutes) * 90
                            else:
                                val_per_90 = 0
                            
                            # Distribution normalisée
                            minutes_dist = df_comparison['Minutes jouées'].replace([np.inf, -np.inf], np.nan)
                            col_dist = df_comparison[col].replace([np.inf, -np.inf], np.nan)
                            
                            valid_mask = (minutes_dist > 0) & (~pd.isna(minutes_dist)) & (~pd.isna(col_dist))
                            if valid_mask.sum() > 0:
                                distribution = (col_dist[valid_mask] / minutes_dist[valid_mask]) * 90
                                val = val_per_90
                            else:
                                distribution = pd.Series([0])
                                val = 0
                        
                        if len(distribution) > 0 and distribution.std() > 0:
                            percentile = (distribution < val).mean() * 100
                            percentile = max(0, min(100, percentile))
                        else:
                            percentile = 50
                            
                except Exception:
                    percentile = 50
                
                percentiles.append(int(percentile))

            return percentiles
        except Exception as e:
            # En cas d'erreur, retourner des valeurs par défaut
            return [50] * len(Config.RADAR_METRICS)
    
    @staticmethod
    def calculate_offensive_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques offensives"""
        minutes = Utils.safe_get_value(player_data, 'Minutes jouées', 90)
        minutes_90 = minutes / 90 if minutes > 0 else 1
        
        return {
            'Buts/90': Utils.safe_get_value(player_data, 'Buts', 0) / minutes_90,
            'Passes D./90': Utils.safe_get_value(player_data, 'Passes décisives', 0) / minutes_90,
            'Passes clés/90': Utils.safe_get_value(player_data, 'Passes clés', 0) / minutes_90,
            'Tirs/90': Utils.safe_get_value(player_data, 'Tirs', 0) / minutes_90,
            'Dribbles/90': Utils.safe_get_value(player_data, 'Dribbles tentés', 0) / minutes_90,
            'Touches/90': Utils.safe_get_value(player_data, 'Touches de balle', 0) / minutes_90
        }
    
    @staticmethod
    def calculate_defensive_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques défensives"""
        minutes = Utils.safe_get_value(player_data, 'Minutes jouées', 90)
        minutes_90 = minutes / 90 if minutes > 0 else 1
        
        return {
            'Tacles/90': Utils.safe_get_value(player_data, 'Tacles gagnants', 0) / minutes_90,
            'Interceptions/90': Utils.safe_get_value(player_data, 'Interceptions', 0) / minutes_90,
            'Dégagements/90': Utils.safe_get_value(player_data, 'Dégagements', 0) / minutes_90,
            'Duels gagnés/90': Utils.safe_get_value(player_data, 'Duels défensifs gagnés', 0) / minutes_90,
            'Fautes/90': Utils.safe_get_value(player_data, 'Fautes', 0) / minutes_90,
            'Cartons J./90': Utils.safe_get_value(player_data, 'Cartons jaunes', 0) / minutes_90
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
                color=color_palette[:len(data)],
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
                font=dict(size=16, color='white', family='Inter'),
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
    def create_radar_chart(values: List[float], player_name: str, comparison_name: str = "") -> go.Figure:
        """Crée un radar chart avec Plotly"""
        
        categories = list(Config.RADAR_METRICS.keys())
        
        fig = go.Figure()
        
        # Joueur principal
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(31,119,180,0.25)',
            line=dict(color='rgb(31,119,180)', width=2),
            marker=dict(color='rgb(31,119,180)', size=8),
            name=player_name
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(255,255,255,0.2)',
                    tickcolor='white',
                    tickfont=dict(color='white', size=10),
                    showticklabels=True
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.2)',
                    tickcolor='white',
                    tickfont=dict(color='white', size=11),
                    linecolor='rgba(255,255,255,0.3)'
                ),
                bgcolor='rgba(26, 29, 35, 0.8)'
            ),
            showlegend=True,
            title=dict(
                text=f"Analyse Radar - {player_name}",
                font=dict(size=16, color='white'),
                x=0.5
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        
        return fig

# ================================================================================================
# COMPOSANTS UI
# ================================================================================================

class UIComponents:
    """Composants d'interface utilisateur réutilisables"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête principal"""
        st.markdown("""
        <div class='player-header-card'>
            <h1 style='color: white; margin: 0; font-size: 3.5em; font-weight: 800; letter-spacing: -0.02em;'>
                Dashboard Football Professionnel
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 16px 0 0 0; font-size: 1.25em; font-weight: 500;'>
                Analyse avancée des performances - Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte complète du joueur"""
        valeur_marchande = Utils.format_market_value(player_data.get('Valeur marchande', 'N/A'))
        
        col1, col2, col3 = st.columns([1, 2.5, 1], gap="large")
        
        with col1:
            UIComponents._render_player_photo(player_data['Joueur'])
        
        with col2:
            st.markdown(f"""
            <div class='player-info-card'>
                <h2 class='section-title-enhanced' style='margin-bottom: var(--spacing-xl); font-size: 2.5em; color: var(--text-primary);'>
                    {player_data['Joueur']}
                </h2>
                <div class='player-metrics-grid'>
                    <div class='metric-card-enhanced'>
                        <div class='metric-value-enhanced'>{Utils.safe_get_value(player_data, 'Âge', 0):.0f}</div>
                        <div class='metric-label-enhanced'>Âge</div>
                    </div>
                    <div class='metric-card-enhanced'>
                        <div class='metric-value-enhanced'>{player_data.get('Position', 'N/A')}</div>
                        <div class='metric-label-enhanced'>Position</div>
                    </div>
                    <div class='metric-card-enhanced'>
                        <div class='metric-value-enhanced'>{player_data.get('Nationalité', 'N/A')}</div>
                        <div class='metric-label-enhanced'>Nationalité</div>
                    </div>
                    <div class='metric-card-enhanced'>
                        <div class='metric-value-enhanced'>{Utils.safe_get_value(player_data, 'Minutes jouées', 0):.0f}</div>
                        <div class='metric-label-enhanced'>Minutes Jouées</div>
                    </div>
                    <div class='metric-card-enhanced'>
                        <div class='metric-value-enhanced' style='color: var(--accent-color);'>{valeur_marchande}</div>
                        <div class='metric-label-enhanced'>Valeur Marchande</div>
                    </div>
                    <div class='metric-card-enhanced'>
                        <div class='metric-value-enhanced'>{player_data.get('Équipe', 'N/A')}</div>
                        <div class='metric-label-enhanced'>Équipe</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            UIComponents._render_club_logo(player_data.get('Équipe', ''), competition)
    
    @staticmethod
    def _render_player_photo(player_name: str):
        """Affiche la photo du joueur"""
        photo_path = ImageManager.get_player_photo(player_name)
        
        if photo_path:
            try:
                image = Image.open(photo_path)
                st.markdown(f"""
                <div class='image-container'>
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
                <div class='club-logo-container'>
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
        <div class='image-container'>
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
        <div class='club-logo-container'>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 3em; margin-bottom: var(--spacing-md); opacity: 0.5;'>🏟️</div>
                <p style='margin: 0; font-size: 0.8em;'>Logo non disponible</p>
                <p style='font-size: 0.75em; margin-top: var(--spacing-xs); color: var(--primary-color);'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """Affiche le footer"""
        st.markdown("""
        <div class='dashboard-footer'>
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
                index=0 if competitions else None,
                help="Sélectionnez la compétition pour filtrer les joueurs"
            )
            
            # Filtrage par compétition
            df_filtered = DataManager.filter_by_competition(df, selected_competition) if selected_competition else df
            
            st.markdown("---")
            
            # Filtre par minutes jouées
            min_minutes_filter = 0
            if not df_filtered.empty and 'Minutes jouées' in df_filtered.columns:
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
            
            # Application du filtre minutes
            df_filtered_minutes = DataManager.filter_by_minutes(df_filtered, min_minutes_filter)
            
            # Informations sur le filtrage
            nb_joueurs = len(df_filtered_minutes)
            
            if nb_joueurs > 0:
                st.success(f"✅ **{nb_joueurs} joueurs** correspondent aux critères")
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
            
            return selected_competition, selected_player, df_filtered_minutes

# ================================================================================================
# GESTIONNAIRE DE TABS
# ================================================================================================

class TabManager:
    """Gestionnaire pour les différents onglets"""
    
    @staticmethod
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance offensive"""
        st.markdown("<h2 class='section-title-enhanced'>🎯 Performance Offensive</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Métriques offensives de base
            offensive_data = {
                'Buts': Utils.safe_get_value(player_data, 'Buts', 0),
                'Passes décisives': Utils.safe_get_value(player_data, 'Passes décisives', 0),
                'Passes clés': Utils.safe_get_value(player_data, 'Passes clés', 0),
                'Tirs': Utils.safe_get_value(player_data, 'Tirs', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                offensive_data,
                "Actions Offensives Totales",
                Config.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Métriques par 90 minutes
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques par 90min</h3>", unsafe_allow_html=True)
            
            minutes = Utils.safe_get_value(player_data, 'Minutes jouées', 90)
            minutes_90 = minutes / 90 if minutes > 0 else 1
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Buts par 90min",
                    value=f"{Utils.safe_get_value(player_data, 'Buts', 0) / minutes_90:.2f}",
                    help="Nombre de buts marqués par 90 minutes de jeu"
                )
                st.metric(
                    label="Passes clés par 90min",
                    value=f"{Utils.safe_get_value(player_data, 'Passes clés', 0) / minutes_90:.2f}",
                    help="Passes menant à une occasion de but"
                )
            
            with metric_col2:
                st.metric(
                    label="Passes D. par 90min",
                    value=f"{Utils.safe_get_value(player_data, 'Passes décisives', 0) / minutes_90:.2f}",
                    help="Passes menant directement à un but"
                )
                st.metric(
                    label="Tirs par 90min",
                    value=f"{Utils.safe_get_value(player_data, 'Tirs', 0) / minutes_90:.2f}",
                    help="Nombre de tirs tentés par 90 minutes"
                )
        
        with col2:
            # Radar offensif
            percentiles = MetricsCalculator.calculate_percentiles(selected_player, df_comparison, df_comparison)
            fig_radar = ChartManager.create_radar_chart(
                percentiles[:6],  # Prendre les 6 premières métriques pour l'attaque
                selected_player
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
    @staticmethod
    def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance défensive"""
        st.markdown("<h2 class='section-title-enhanced'>🛡️ Performance Défensive</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Métriques défensives de base
            defensive_data = {
                'Tacles': Utils.safe_get_value(player_data, 'Tacles gagnants', 0),
                'Interceptions': Utils.safe_get_value(player_data, 'Interceptions', 0),
                'Dégagements': Utils.safe_get_value(player_data, 'Dégagements', 0),
                'Cartons jaunes': Utils.safe_get_value(player_data, 'Cartons jaunes', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                defensive_data,
                "Actions Défensives Totales",
                Config.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Métriques par 90 minutes
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques par 90min</h3>", unsafe_allow_html=True)
            
            minutes = Utils.safe_get_value(player_data, 'Minutes jouées', 90)
            minutes_90 = minutes / 90 if minutes > 0 else 1
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="Tacles par 90min",
                    value=f"{Utils.safe_get_value(player_data, 'Tacles gagnants', 0) / minutes_90:.2f}",
                    help="Nombre de tacles gagnants par 90 minutes"
                )
                st.metric(
                    label="Dégagements par 90min",
                    value=f"{Utils.safe_get_value(player_data, 'Dégagements', 0) / minutes_90:.2f}",
                    help="Nombre de dégagements par 90 minutes"
                )
            
            with metric_col2:
                st.metric(
                    label="Interceptions par 90min",
                    value=f"{Utils.safe_get_value(player_data, 'Interceptions', 0) / minutes_90:.2f}",
                    help="Nombre d'interceptions par 90 minutes"
                )
                st.metric(
                    label="Cartons par 90min",
                    value=f"{Utils.safe_get_value(player_data, 'Cartons jaunes', 0) / minutes_90:.2f}",
                    help="Nombre de cartons jaunes par 90 minutes"
                )
        
        with col2:
            # Radar défensif
            percentiles = MetricsCalculator.calculate_percentiles(selected_player, df_comparison, df_comparison)
            fig_radar = ChartManager.create_radar_chart(
                percentiles[6:],  # Prendre les métriques défensives
                selected_player
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
    @staticmethod
    def render_technical_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet performance technique"""
        st.markdown("<h2 class='section-title-enhanced'>🎨 Performance Technique</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Métriques techniques de base
            technical_data = {
                'Passes tentées': Utils.safe_get_value(player_data, 'Passes tentées', 0),
                'Dribbles tentés': Utils.safe_get_value(player_data, 'Dribbles tentés', 0),
                'Touches de balle': Utils.safe_get_value(player_data, 'Touches de balle', 0),
                'Centres': Utils.safe_get_value(player_data, 'Centres', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                technical_data,
                "Actions Techniques Totales",
                Config.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Pourcentages de réussite
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Pourcentages de Réussite</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                passes_reussies = Utils.safe_get_value(player_data, 'Pourcentage de passes réussies', 0)
                st.metric(
                    label="% Passes réussies",
                    value=f"{passes_reussies:.1f}%",
                    help="Pourcentage de passes réussies"
                )
                dribbles_reussis = Utils.safe_get_value(player_data, 'Pourcentage de dribbles réussis', 0)
                st.metric(
                    label="% Dribbles réussis",
                    value=f"{dribbles_reussis:.1f}%",
                    help="Pourcentage de dribbles réussis"
                )
            
            with metric_col2:
                duels_gagnes = Utils.safe_get_value(player_data, 'Pourcentage de duels gagnés', 0)
                st.metric(
                    label="% Duels gagnés",
                    value=f"{duels_gagnes:.1f}%",
                    help="Pourcentage de duels gagnés"
                )
                tirs_cadres = Utils.safe_get_value(player_data, 'Pourcentage de tirs cadrés', 0)
                st.metric(
                    label="% Tirs cadrés",
                    value=f"{tirs_cadres:.1f}%",
                    help="Pourcentage de tirs cadrés"
                )
        
        with col2:
            # Radar technique complet
            percentiles = MetricsCalculator.calculate_percentiles(selected_player, df_comparison, df_comparison)
            fig_radar = ChartManager.create_radar_chart(
                percentiles,
                selected_player
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
    @staticmethod
    def render_comparison_tab(df: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet comparaison inter-ligues"""
        st.markdown("<h2 class='section-title-enhanced'>🔄 Comparaison Inter-Ligues</h2>", unsafe_allow_html=True)
        
        competitions = DataManager.get_competitions(df)
        
        # Sélection des compétitions pour la comparaison
        st.markdown("<h3 class='subsection-title-enhanced'>⚙️ Configuration de la Comparaison</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏆 Compétitions de référence**")
            selected_competitions = st.multiselect(
                "Sélectionnez les compétitions à comparer :",
                competitions,
                default=competitions[:3] if len(competitions) >= 3 else competitions,
                help="Choisissez les ligues pour calculer les percentiles de comparaison"
            )
        
        with col2:
            st.markdown("**📊 Type d'analyse**")
            comparison_type = st.radio(
                "Mode de comparaison :",
                ["Radar vs Toutes Ligues", "Radar vs Ligue Spécifique", "Comparaison 2 Joueurs"],
                help="Choisissez le type d'analyse à effectuer"
            )
        
        if not selected_competitions:
            st.warning("⚠️ Veuillez sélectionner au moins une compétition pour la comparaison.")
            return
        
        if comparison_type == "Radar vs Toutes Ligues":
            TabManager._render_multi_league_radar(df, selected_player, selected_competitions)
        elif comparison_type == "Radar vs Ligue Spécifique":
            TabManager._render_specific_league_radar(df, selected_player, selected_competitions)
        else:
            TabManager._render_two_player_comparison(df, competitions)
    
    @staticmethod
    def _render_multi_league_radar(df: pd.DataFrame, selected_player: str, competitions: List[str]):
        """Radar comparé à toutes les ligues sélectionnées"""
        st.markdown(f"<h3 class='subsection-title-enhanced'>🌍 {selected_player} vs Toutes Ligues</h3>", unsafe_allow_html=True)
        
        # Créer un dataset combiné de toutes les ligues sélectionnées
        df_multi_league = DataManager.filter_by_multiple_competitions(df, competitions)
        
        if df_multi_league.empty:
            st.error("Aucune donnée trouvée pour les compétitions sélectionnées.")
            return
        
        # Calculer les percentiles vs toutes les ligues
        percentiles = MetricsCalculator.calculate_percentiles(selected_player, df, df_multi_league)
        
        # Informations sur la comparaison
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"🏆 **Ligues :** {', '.join(competitions)}")
        with col2:
            st.info(f"👥 **Joueurs comparés :** {len(df_multi_league):,}")
        with col3:
            avg_percentile = np.mean(percentiles)
            st.info(f"📊 **Percentile moyen :** {avg_percentile:.1f}%")
        
        # Afficher le radar
        fig_radar = ChartManager.create_radar_chart(
            percentiles,
            selected_player,
            f"vs {len(competitions)} ligues"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Analyse détaillée
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📈 Analyse Détaillée</h3>", unsafe_allow_html=True)
        
        # Créer un dataframe avec les métriques et percentiles
        metrics_df = pd.DataFrame({
            'Métrique': list(Config.RADAR_METRICS.keys()),
            'Percentile': percentiles
        })
        metrics_df = metrics_df.sort_values('Percentile', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔥 Top 5 - Points Forts**")
            top_5 = metrics_df.head()
            for _, row in top_5.iterrows():
                st.write(f"• **{row['Métrique']}** : {row['Percentile']:.0f}%")
        
        with col2:
            st.markdown("**📈 Bottom 5 - Axes d'Amélioration**")
            bottom_5 = metrics_df.tail()
            for _, row in bottom_5.iterrows():
                st.write(f"• **{row['Métrique']}** : {row['Percentile']:.0f}%")
    
    @staticmethod
    def _render_specific_league_radar(df: pd.DataFrame, selected_player: str, competitions: List[str]):
        """Radar comparé à une ligue spécifique"""
        selected_league = st.selectbox(
            "🏆 Choisissez la ligue de référence :",
            competitions,
            help="Le joueur sera comparé uniquement aux joueurs de cette ligue"
        )
        
        if selected_league:
            st.markdown(f"<h3 class='subsection-title-enhanced'>🎯 {selected_player} vs {selected_league}</h3>", unsafe_allow_html=True)
            
            df_league = DataManager.filter_by_competition(df, selected_league)
            
            # Calculer les percentiles vs la ligue spécifique
            percentiles = MetricsCalculator.calculate_percentiles(selected_player, df, df_league)
            
            # Informations sur la comparaison
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"🏆 **Ligue :** {selected_league}")
            with col2:
                st.info(f"👥 **Joueurs comparés :** {len(df_league):,}")
            with col3:
                avg_percentile = np.mean(percentiles)
                st.info(f"📊 **Percentile moyen :** {avg_percentile:.1f}%")
            
            # Afficher le radar
            fig_radar = ChartManager.create_radar_chart(
                percentiles,
                selected_player,
                f"vs {selected_league}"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
    @staticmethod
    def _render_two_player_comparison(df: pd.DataFrame, competitions: List[str]):
        """Comparaison entre deux joueurs"""
        st.markdown("<h3 class='subsection-title-enhanced'>⚔️ Duel de Joueurs</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 Joueur 1**")
            comp1 = st.selectbox("Compétition", competitions, key="comp1")
            df1 = DataManager.filter_by_competition(df, comp1)
            player1 = st.selectbox("Joueur", DataManager.get_players(df1), key="player1")
        
        with col2:
            st.markdown("**👤 Joueur 2**")
            comp2 = st.selectbox("Compétition", competitions, key="comp2")
            df2 = DataManager.filter_by_competition(df, comp2)
            player2 = st.selectbox("Joueur", DataManager.get_players(df2), key="player2")
        
        if player1 and player2:
            st.markdown(f"<h3 class='subsection-title-enhanced'>⚔️ {player1} vs {player2}</h3>", unsafe_allow_html=True)
            
            # Calculer les percentiles pour chaque joueur
            percentiles1 = MetricsCalculator.calculate_percentiles(player1, df1)
            percentiles2 = MetricsCalculator.calculate_percentiles(player2, df2)
            
            # Informations sur les joueurs
            player1_data = df1[df1['Joueur'] == player1].iloc[0]
            player2_data = df2[df2['Joueur'] == player2].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🏆 {comp1} | ⚽ {player1_data.get('Équipe', 'N/A')} | 📍 {player1_data.get('Position', 'N/A')}")
            with col2:
                st.info(f"🏆 {comp2} | ⚽ {player2_data.get('Équipe', 'N/A')} | 📍 {player2_data.get('Position', 'N/A')}")
            
            # Radar comparatif avec Plotly
            fig = go.Figure()
            
            categories = list(Config.RADAR_METRICS.keys())
            
            # Joueur 1
            fig.add_trace(go.Scatterpolar(
                r=percentiles1,
                theta=categories,
                fill='toself',
                fillcolor='rgba(31,119,180,0.25)',
                line=dict(color='rgb(31,119,180)', width=2),
                marker=dict(color='rgb(31,119,180)', size=8),
                name=player1
            ))
            
            # Joueur 2
            fig.add_trace(go.Scatterpolar(
                r=percentiles2,
                theta=categories,
                fill='toself',
                fillcolor='rgba(44,160,44,0.25)',
                line=dict(color='rgb(44,160,44)', width=2),
                marker=dict(color='rgb(44,160,44)', size=8),
                name=player2
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        gridcolor='rgba(255,255,255,0.2)',
                        tickcolor='white',
                        tickfont=dict(color='white', size=10),
                        showticklabels=True
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(255,255,255,0.2)',
                        tickcolor='white',
                        tickfont=dict(color='white', size=11),
                        linecolor='rgba(255,255,255,0.3)'
                    ),
                    bgcolor='rgba(26, 29, 35, 0.8)'
                ),
                showlegend=True,
                title=dict(
                    text=f"Comparaison Radar - {player1} vs {player2}",
                    font=dict(size=16, color='white'),
                    x=0.5
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=500,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistiques de comparaison
            st.markdown("---")
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Statistiques de Comparaison</h3>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg1 = np.mean(percentiles1)
                avg2 = np.mean(percentiles2)
                winner = player1 if avg1 > avg2 else player2
                st.metric("Meilleur Percentile Moyen", winner, f"{max(avg1, avg2):.1f}%")
            
            with col2:
                superior_count1 = sum(1 for p1, p2 in zip(percentiles1, percentiles2) if p1 > p2)
                st.metric(f"{player1} supérieur sur", f"{superior_count1}", f"/ {len(percentiles1)} métriques")
            
            with col3:
                superior_count2 = len(percentiles1) - superior_count1
                st.metric(f"{player2} supérieur sur", f"{superior_count2}", f"/ {len(percentiles1)} métriques")

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
        try:
            # Chargement des données
            with st.spinner("Chargement des données..."):
                df = DataManager.load_data()
            
            if df is None:
                self._render_error_page()
                return
            
            # Vérification que le DataFrame n'est pas vide
            if df.empty:
                st.error("❌ Le fichier de données est vide.")
                return
            
            # Affichage des statistiques générales
            self._render_data_overview(df)
            
            # Rendu de l'en-tête
            UIComponents.render_header()
            
            # Rendu de la sidebar et récupération des sélections
            selected_competition, selected_player, df_filtered = SidebarManager.render_sidebar(df)
            
            if selected_player and not df_filtered.empty:
                # Mise à jour des stats de session
                if selected_player not in st.session_state.selected_player_history:
                    st.session_state.session_stats['players_viewed'] += 1
                    st.session_state.selected_player_history.insert(0, selected_player)
                    st.session_state.selected_player_history = st.session_state.selected_player_history[:5]
                
                # Récupération des données du joueur
                player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
                
                # Breadcrumbs
                st.markdown(f"""
                <div style='background: var(--background-surface); padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid var(--primary-color);'>
                    <span style='color: var(--text-secondary); font-size: 0.9em;'>
                        🏆 {selected_competition} › ⚽ {player_data.get('Équipe', 'N/A')} › 👤 {selected_player}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                # Carte joueur
                UIComponents.render_player_card(player_data, selected_competition)
                
                st.markdown("---")
                
                # Onglets principaux
                self._render_main_tabs(player_data, df_filtered, selected_player, df)
            
            else:
                self._render_no_player_message()
            
            # Footer
            UIComponents.render_footer()
            
        except Exception as e:
            st.error(f"❌ Erreur lors de l'exécution : {str(e)}")
            with st.expander("🔍 Détails de l'erreur", expanded=False):
                import traceback
                st.code(traceback.format_exc())
    
    def _render_data_overview(self, df: pd.DataFrame):
        """Aperçu des données"""
        try:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "👥 Joueurs Total", 
                    f"{len(df):,}",
                    help="Nombre total de joueurs dans la base de données"
                )
            
            with col2:
                competitions_count = df['Compétition'].nunique() if 'Compétition' in df.columns else 0
                st.metric(
                    "🏆 Compétitions", 
                    f"{competitions_count}",
                    help="Nombre de compétitions analysées"
                )
            
            with col3:
                teams_count = df['Équipe'].nunique() if 'Équipe' in df.columns else 0
                st.metric(
                    "⚽ Équipes", 
                    f"{teams_count}",
                    help="Nombre d'équipes représentées"
                )
            
            with col4:
                total_minutes = df['Minutes jouées'].sum() if 'Minutes jouées' in df.columns else 0
                st.metric(
                    "⏱️ Minutes Totales", 
                    f"{total_minutes:,.0f}",
                    help="Total des minutes jouées par tous les joueurs"
                )
            
            with col5:
                avg_age = df['Âge'].mean() if 'Âge' in df.columns else 0
                st.metric(
                    "📅 Âge Moyen", 
                    f"{avg_age:.1f} ans",
                    help="Âge moyen de tous les joueurs"
                )
        except Exception as e:
            st.warning(f"⚠️ Erreur lors de l'affichage des statistiques : {str(e)}")
    
    def _render_main_tabs(self, player_data: pd.Series, df_filtered: pd.DataFrame, 
                         selected_player: str, df_full: pd.DataFrame):
        """Rendu des onglets principaux"""
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Performance Offensive", 
            "🛡️ Performance Défensive", 
            "🎨 Performance Technique", 
            "🔄 Comparaison Inter-Ligues"
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
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Buts, passes décisives, tirs</p>
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
                    <div style='font-size: 3em; margin-bottom: 12px; color: var(--warning);'>🔄</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 8px 0;'>Comparaison Inter-Ligues</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 0.9em;'>Radars et benchmarks multi-ligues</p>
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
                    st.info(f"🔄 {player}")
    
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
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Réessayer", type="primary"):
            st.rerun()

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
