"""
Application Streamlit pour l'analyse avancée des performances footballistiques.
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
        
        /* Navigation rapide */
        .quick-nav {
            position: fixed;
            right: var(--spacing-lg);
            top: 50%;
            transform: translateY(-50%);
            z-index: 1000;
            background: var(--background-card);
            border-radius: var(--radius-md);
            padding: var(--spacing-sm);
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-lg);
            opacity: 0.9;
            transition: opacity 0.3s ease;
        }
        
        .quick-nav:hover {
            opacity: 1;
        }
        
        .quick-nav-item {
            display: block;
            padding: var(--spacing-sm);
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
            font-size: 0.8rem;
            margin-bottom: var(--spacing-xs);
        }
        
        .quick-nav-item:hover {
            background: var(--primary-color);
            color: white;
            transform: translateX(-2px);
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
            'Touches/90': player_data.get('Touches de balle', 0) / minutes_90,
            'Passes clés/90': player_data.get('Passes clés', 0) / minutes_90,
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
            name='Moyenne compétition',
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
                          competition: str, color: str) -> go.Figure:
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
        
        # Calcul des moyennes de la compétition
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
                
                avg_metrics[metric_key] = (df_comparison.get(column_name, pd.Series([0]*len(df_comparison))) / minutes_90_comp).mean()
            else:
                avg_metrics[metric_key] = df_comparison.get(metric_key.replace('% ', 'Pourcentage de ').replace(' gagnés', ' gagnés').replace(' aériens', ' aériens gagnés'), pd.Series([0]*len(df_comparison))).mean()
        
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
        
        # Calcul des moyennes de la compétition
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
                Analyse avancée des performances - Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte complète du joueur"""
        valeur_marchande = Utils.format_market_value(player_data.get('Valeur marchande', 'N/A'))
        
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
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
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
                    <span>Moyenne compétition</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
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
            "Performance par 90min vs Moyenne de la Compétition"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
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
                'Duels aériens': player_data.get('Pourcentage de duels aériens gagnés', 0),
                'Passes': player_data.get('Pourcentage de passes réussies', 0)
            }
            
            fig_gauge = ChartManager.create_gauge_chart(success_data, "Pourcentages de Réussite (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar défensif
            st.markdown("<h3 class='subsection-title-enhanced'>🛡️ Analyse Radar</h3>", unsafe_allow_html=True)
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
                Config.COLORS['accent']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    
        @staticmethod
        def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
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
                    <span>Moyenne compétition</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
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
            "Performance par 90min vs Moyenne de la Compétition"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
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
                min_stat = min(values)
                min_index = values.index(min_stat)
                min_param = list(Config.RADAR_METRICS.keys())[min_index]
                st.metric("Axe d'Amélioration", f"{min_param.replace('\\n', ' ')}", f"{min_stat}%")
            
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
            
            # Onglets principaux
            self._render_main_tabs(player_data, df_filtered, selected_player, df)
        
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
