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
    
    # Palette de couleurs professionnelle
    COLORS = {
        'primary': '#0052CC',      # Bleu premium
        'secondary': '#00B8A3',    # Turquoise élégant
        'accent': '#FF6B35',       # Orange énergique
        'success': '#00875A',      # Vert succès
        'warning': '#FFAB00',      # Ambre
        'danger': '#DE350B',       # Rouge alerte
        'dark': '#091E42',         # Bleu très foncé
        'light': '#F4F5F7',        # Gris très clair
        'gradient': ['#0052CC', '#00B8A3', '#FF6B35', '#00875A', '#FFAB00'],
        'background': '#0A0E17',   # Noir professionnel
        'surface': '#161B26',      # Surface sombre
        'card': '#1C2333',         # Carte sombre
        'border': '#2A3441',       # Bordure subtile
        'text': '#E6EAEF',         # Texte principal
        'text_secondary': '#B3BAC5', # Texte secondaire
        'text_muted': '#8993A4'    # Texte atténué
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
# GESTIONNAIRE DE STYLES CSS ULTRA-PROFESSIONNEL
# ================================================================================================

class StyleManager:
    """Gestionnaire des styles CSS ultra-professionnels"""
    
    @staticmethod
    def get_css() -> str:
        """Retourne le CSS ultra-professionnel"""
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        /* Variables CSS professionnelles */
        :root {
            --primary: #0052CC;
            --primary-light: #4C9AFF;
            --primary-dark: #0047B3;
            --secondary: #00B8A3;
            --secondary-light: #79E2F2;
            --secondary-dark: #008DA6;
            --accent: #FF6B35;
            --accent-light: #FF8F73;
            --accent-dark: #E55100;
            --success: #00875A;
            --warning: #FFAB00;
            --danger: #DE350B;
            --info: #0065FF;
            
            /* Backgrounds */
            --bg-primary: #0A0E17;
            --bg-secondary: #161B26;
            --bg-tertiary: #1C2333;
            --bg-surface: #212936;
            --bg-elevated: #2A3441;
            --bg-glass: rgba(44, 52, 64, 0.7);
            --bg-overlay: rgba(10, 14, 23, 0.95);
            
            /* Text colors */
            --text-primary: #E6EAEF;
            --text-secondary: #B3BAC5;
            --text-tertiary: #8993A4;
            --text-muted: #6B7280;
            --text-accent: var(--accent);
            
            /* Borders & Shadows */
            --border-primary: #2A3441;
            --border-secondary: #384250;
            --border-accent: var(--accent);
            --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.2);
            --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 8px 25px rgba(0, 0, 0, 0.4);
            --shadow-xl: 0 20px 40px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 20px rgba(0, 82, 204, 0.3);
            
            /* Gradients */
            --gradient-primary: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            --gradient-accent: linear-gradient(135deg, var(--accent) 0%, var(--warning) 100%);
            --gradient-surface: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-surface) 100%);
            --gradient-hero: linear-gradient(135deg, #0052CC 0%, #00B8A3 50%, #FF6B35 100%);
            --gradient-overlay: linear-gradient(135deg, rgba(0, 82, 204, 0.1) 0%, rgba(0, 184, 163, 0.1) 100%);
            
            /* Spacing */
            --space-xs: 4px;
            --space-sm: 8px;
            --space-md: 16px;
            --space-lg: 24px;
            --space-xl: 32px;
            --space-2xl: 48px;
            --space-3xl: 64px;
            
            /* Border radius */
            --radius-xs: 4px;
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
            --radius-full: 50%;
            
            /* Typography */
            --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
            
            /* Transitions */
            --transition-fast: 0.15s ease;
            --transition-normal: 0.3s ease;
            --transition-slow: 0.5s ease;
            
            /* Z-indexes */
            --z-header: 1000;
            --z-sidebar: 900;
            --z-modal: 1100;
            --z-tooltip: 1200;
        }
        
        /* Reset et base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* Application principale */
        .stApp {
            font-family: var(--font-primary);
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            overflow-x: hidden;
        }
        
        /* Layout principal */
        .main .block-container {
            padding: var(--space-xl) var(--space-lg);
            max-width: 1600px;
            margin: 0 auto;
        }
        
        /* Header ultra-professionnel */
        .pro-header {
            background: var(--gradient-hero);
            padding: var(--space-3xl) var(--space-xl);
            border-radius: var(--radius-xl);
            text-align: center;
            margin-bottom: var(--space-3xl);
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-xl);
        }
        
        .pro-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs><pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grid)"/></svg>');
            opacity: 0.3;
        }
        
        .pro-header h1 {
            font-size: clamp(2.5rem, 5vw, 4.5rem);
            font-weight: 900;
            margin: 0;
            color: white;
            text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            letter-spacing: -0.02em;
            position: relative;
            z-index: 2;
        }
        
        .pro-header p {
            font-size: clamp(1rem, 2vw, 1.5rem);
            margin-top: var(--space-md);
            color: rgba(255, 255, 255, 0.9);
            font-weight: 500;
            position: relative;
            z-index: 2;
        }
        
        /* Navigation tabs ultra-moderne */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--bg-tertiary);
            border-radius: var(--radius-lg);
            padding: var(--space-sm);
            margin-bottom: var(--space-2xl);
            border: 2px solid var(--border-primary);
            box-shadow: var(--shadow-lg);
            position: sticky;
            top: var(--space-md);
            z-index: var(--z-header);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: var(--text-secondary);
            border-radius: var(--radius-md);
            font-weight: 600;
            font-size: 15px;
            transition: all var(--transition-normal);
            border: none;
            padding: var(--space-md) var(--space-xl);
            margin: 0 var(--space-xs);
            position: relative;
            overflow: hidden;
        }
        
        .stTabs [data-baseweb="tab"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--gradient-primary);
            opacity: 0;
            transition: all var(--transition-normal);
            border-radius: var(--radius-md);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: var(--text-primary);
            transform: translateY(-2px);
        }
        
        .stTabs [data-baseweb="tab"]:hover::before {
            opacity: 0.1;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--gradient-primary);
            color: white;
            box-shadow: var(--shadow-glow);
            font-weight: 700;
            transform: translateY(-2px);
        }
        
        .stTabs [aria-selected="true"]::before {
            opacity: 0;
        }
        
        /* Cards ultra-professionnelles */
        .pro-card {
            background: var(--gradient-surface);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            padding: var(--space-xl);
            margin: var(--space-lg) 0;
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
            transition: all var(--transition-normal);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        
        .pro-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-primary);
            transition: all var(--transition-normal);
        }
        
        .pro-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
            border-color: var(--primary);
        }
        
        .pro-card:hover::before {
            height: 4px;
            background: var(--gradient-accent);
        }
        
        /* Player info card avec design premium */
        .player-info-card {
            background: var(--gradient-surface);
            padding: var(--space-2xl);
            border-radius: var(--radius-xl);
            border: 2px solid var(--border-primary);
            box-shadow: var(--shadow-xl);
            margin: var(--space-xl) 0;
            text-align: center;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
        }
        
        .player-info-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--gradient-hero);
        }
        
        .player-info-card::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(transparent, rgba(0, 82, 204, 0.03), transparent);
            animation: rotate 20s linear infinite;
            pointer-events: none;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        /* Grid des métriques ultra-moderne */
        .player-metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: var(--space-lg);
            margin-top: var(--space-xl);
            position: relative;
            z-index: 2;
        }
        
        /* Cartes de métriques avec animations */
        .metric-card-enhanced {
            background: var(--bg-elevated);
            padding: var(--space-lg);
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-secondary);
            text-align: center;
            transition: all var(--transition-normal);
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        
        .metric-card-enhanced::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--gradient-overlay);
            opacity: 0;
            transition: all var(--transition-normal);
        }
        
        .metric-card-enhanced:hover {
            border-color: var(--primary);
            box-shadow: var(--shadow-glow);
            transform: translateY(-4px) scale(1.02);
        }
        
        .metric-card-enhanced:hover::before {
            opacity: 1;
        }
        
        .metric-value-enhanced {
            font-size: 2rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: var(--space-sm);
            line-height: 1.1;
            word-break: break-word;
            position: relative;
            z-index: 2;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .metric-label-enhanced {
            font-size: 0.85rem;
            color: var(--text-tertiary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            line-height: 1.3;
            position: relative;
            z-index: 2;
        }
        
        /* Cartes joueurs similaires avec design premium */
        .similar-player-card {
            background: var(--gradient-surface);
            padding: var(--space-xl);
            border-radius: var(--radius-xl);
            border: 2px solid var(--border-primary);
            box-shadow: var(--shadow-lg);
            margin: var(--space-lg) 0;
            transition: all var(--transition-normal);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
        }
        
        .similar-player-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--secondary), var(--accent));
            transition: all var(--transition-normal);
        }
        
        .similar-player-card:hover {
            border-color: var(--secondary);
            box-shadow: 0 12px 40px rgba(0, 184, 163, 0.2);
            transform: translateY(-6px);
        }
        
        .similar-player-card:hover::before {
            height: 4px;
        }
        
        .similarity-score {
            background: var(--gradient-primary);
            color: white;
            padding: var(--space-sm) var(--space-md);
            border-radius: var(--radius-md);
            font-weight: 700;
            font-size: 0.9em;
            position: absolute;
            top: var(--space-lg);
            right: var(--space-lg);
            box-shadow: var(--shadow-md);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        
        .player-header-with-logo {
            display: flex;
            align-items: center;
            gap: var(--space-md);
            margin-bottom: var(--space-lg);
        }
        
        .club-logo-small {
            width: 48px;
            height: 48px;
            object-fit: contain;
            border-radius: var(--radius-md);
            background: rgba(255, 255, 255, 0.05);
            padding: var(--space-xs);
            transition: all var(--transition-normal);
        }
        
        .club-logo-small:hover {
            transform: scale(1.1);
            background: rgba(255, 255, 255, 0.1);
        }
        
        /* Titres avec design premium */
        .section-title-enhanced {
            color: var(--text-primary);
            font-size: clamp(1.75rem, 4vw, 2.5rem);
            font-weight: 800;
            text-align: center;
            margin: var(--space-3xl) 0 var(--space-xl) 0;
            letter-spacing: -0.02em;
            position: relative;
            padding-bottom: var(--space-lg);
        }
        
        .section-title-enhanced::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 4px;
            background: var(--gradient-primary);
            border-radius: var(--radius-full);
            box-shadow: var(--shadow-glow);
        }
        
        .subsection-title-enhanced {
            color: var(--primary);
            font-size: 1.5rem;
            font-weight: 700;
            margin: var(--space-xl) 0 var(--space-lg) 0;
            border-left: 4px solid var(--primary);
            padding-left: var(--space-md);
            letter-spacing: -0.01em;
            position: relative;
        }
        
        .subsection-title-enhanced::before {
            content: '';
            position: absolute;
            left: -4px;
            top: 0;
            bottom: 0;
            width: 4px;
            background: var(--gradient-primary);
            border-radius: 0 var(--radius-xs) var(--radius-xs) 0;
        }
        
        /* Conteneurs d'images avec effet glass */
        .image-container {
            background: var(--bg-elevated);
            border-radius: var(--radius-xl);
            padding: var(--space-xl);
            border: 2px solid var(--border-primary);
            overflow: hidden;
            height: 360px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow-xl);
            position: relative;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }
        
        .image-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--gradient-overlay);
            opacity: 0.3;
            pointer-events: none;
        }
        
        .club-logo-container {
            background: var(--bg-elevated);
            border-radius: var(--radius-lg);
            padding: var(--space-xl);
            border: 2px solid var(--border-primary);
            height: 220px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow-lg);
            transition: all var(--transition-normal);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
        }
        
        .club-logo-container:hover {
            border-color: var(--primary);
            box-shadow: var(--shadow-glow);
            transform: scale(1.02);
        }
        
        /* Légendes avec style premium */
        .chart-legend {
            background: var(--bg-elevated);
            border: 1px solid var(--border-secondary);
            border-radius: var(--radius-md);
            padding: var(--space-md) var(--space-lg);
            margin: var(--space-lg) 0;
            display: inline-flex;
            align-items: center;
            gap: var(--space-lg);
            font-size: 0.9rem;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: var(--shadow-md);
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            font-weight: 500;
        }
        
        .legend-color {
            width: 14px;
            height: 14px;
            border-radius: var(--radius-full);
            box-shadow: var(--shadow-sm);
        }
        
        /* Breadcrumbs avec style moderne */
        .breadcrumbs {
            background: var(--bg-elevated);
            padding: var(--space-md) var(--space-xl);
            border-radius: var(--radius-lg);
            margin-bottom: var(--space-xl);
            border-left: 4px solid var(--primary);
            box-shadow: var(--shadow-md);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            font-weight: 500;
        }
        
        /* Sidebar ultra-moderne */
        .sidebar-header {
            background: var(--gradient-primary);
            padding: var(--space-xl);
            border-radius: var(--radius-lg);
            text-align: center;
            margin-bottom: var(--space-xl);
            box-shadow: var(--shadow-xl);
            position: relative;
            overflow: hidden;
        }
        
        .sidebar-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(transparent, rgba(255, 255, 255, 0.1), transparent);
            animation: rotate 15s linear infinite;
        }
        
        /* Footer premium */
        .dashboard-footer {
            background: var(--gradient-surface);
            padding: var(--space-2xl);
            border-radius: var(--radius-lg);
            text-align: center;
            margin-top: var(--space-3xl);
            border: 1px solid var(--border-primary);
            box-shadow: var(--shadow-lg);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
        }
        
        /* Animations avancées */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-40px);
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
                opacity: 0.7;
            }
        }
        
        @keyframes glow {
            0%, 100% {
                box-shadow: var(--shadow-lg);
            }
            50% {
                box-shadow: var(--shadow-glow);
            }
        }
        
        .animated-card {
            animation: fadeInUp 0.8s ease-out;
        }
        
        .animated-slide {
            animation: slideInLeft 0.6s ease-out;
        }
        
        /* Responsive design avancé */
        @media (max-width: 1200px) {
            .player-metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            }
        }
        
        @media (max-width: 768px) {
            .player-metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .pro-header {
                padding: var(--space-xl);
            }
            
            .main .block-container {
                padding: var(--space-lg) var(--space-md);
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: var(--space-sm) var(--space-md);
                font-size: 14px;
            }
        }
        
        @media (max-width: 480px) {
            .player-metrics-grid {
                grid-template-columns: 1fr;
            }
            
            .pro-header h1 {
                font-size: 2rem;
            }
            
            .section-title-enhanced {
                font-size: 1.5rem;
            }
        }
        
        /* Masquer éléments Streamlit */
        .stDeployButton, 
        .stDecoration, 
        [data-testid="manage-app-button"],
        [data-testid="collapsedControl"],
        .stActionButton,
        header[data-testid="stHeader"],
        .stToolbar,
        .stStatusWidget,
        #MainMenu,
        footer,
        .stException {
            display: none !important;
        }
        
        /* Masquer le footer Streamlit */
        .stApp > footer {
            display: none;
        }
        
        /* Masquer l'indicateur de running */
        .stSpinner {
            display: none !important;
        }
        
        /* Personnalisation des selectbox */
        .stSelectbox > div > div {
            background: var(--bg-elevated);
            border: 2px solid var(--border-primary);
            border-radius: var(--radius-md);
            color: var(--text-primary);
        }
        
        .stSelectbox > div > div:focus-within {
            border-color: var(--primary);
            box-shadow: var(--shadow-glow);
        }
        
        /* Personnalisation des sliders */
        .stSlider > div > div > div {
            background: var(--primary);
        }
        
        .stSlider > div > div > div > div {
            background: var(--primary);
            border: 2px solid white;
            box-shadow: var(--shadow-md);
        }
        
        /* Personnalisation des métriques Streamlit */
        [data-testid="metric-container"] {
            background: var(--bg-elevated);
            border: 1px solid var(--border-primary);
            padding: var(--space-lg);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            transition: all var(--transition-normal);
        }
        
        [data-testid="metric-container"]:hover {
            border-color: var(--primary);
            box-shadow: var(--shadow-glow);
            transform: translateY(-2px);
        }
        
        [data-testid="metric-container"] > div:first-child {
            color: var(--text-tertiary);
            font-weight: 600;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        [data-testid="metric-container"] > div:nth-child(2) {
            color: var(--primary);
            font-weight: 800;
            font-size: 2rem;
        }
        
        /* Personnalisation des expandeurs */
        .streamlit-expanderHeader {
            background: var(--bg-elevated);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            font-weight: 600;
        }
        
        .streamlit-expanderContent {
            background: var(--bg-elevated);
            border: 1px solid var(--border-primary);
            border-top: none;
            border-radius: 0 0 var(--radius-md) var(--radius-md);
        }
        
        /* Personnalisation des boutons */
        .stButton > button {
            background: var(--gradient-primary);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            padding: var(--space-md) var(--space-xl);
            font-weight: 600;
            font-size: 1rem;
            transition: all var(--transition-normal);
            box-shadow: var(--shadow-md);
        }
        
        .stButton > button:hover {
            background: var(--gradient-accent);
            box-shadow: var(--shadow-glow);
            transform: translateY(-2px);
        }
        
        /* Personnalisation des inputs */
        .stTextInput > div > div > input {
            background: var(--bg-elevated);
            border: 2px solid var(--border-primary);
            border-radius: var(--radius-md);
            color: var(--text-primary);
            font-weight: 500;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary);
            box-shadow: var(--shadow-glow);
        }
        
        /* Personnalisation des radios */
        .stRadio > div {
            background: var(--bg-elevated);
            border-radius: var(--radius-md);
            padding: var(--space-md);
            border: 1px solid var(--border-primary);
        }
        
        /* Progress bar personnalisée */
        .stProgress > div > div > div {
            background: var(--gradient-primary);
            border-radius: var(--radius-full);
        }
        
        /* Success/Warning/Error messages */
        .stAlert > div {
            border-radius: var(--radius-md);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        
        .stSuccess > div {
            background: rgba(0, 135, 90, 0.2);
            border: 1px solid var(--success);
        }
        
        .stWarning > div {
            background: rgba(255, 171, 0, 0.2);
            border: 1px solid var(--warning);
        }
        
        .stError > div {
            background: rgba(222, 53, 11, 0.2);
            border: 1px solid var(--danger);
        }
        
        .stInfo > div {
            background: rgba(0, 101, 255, 0.2);
            border: 1px solid var(--info);
        }
        
        /* Loading spinner personnalisé */
        .stSpinner > div {
            border-color: var(--primary) transparent var(--primary) transparent;
        }
        
        /* Sidebar personnalisée */
        .css-1d391kg {
            background: var(--bg-secondary);
            border-right: 2px solid var(--border-primary);
        }
        
        /* Colonnes avec gap amélioré */
        .row-widget.stHorizontal > div {
            gap: var(--space-lg);
        }
        
        /* Scrollbar personnalisée */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: var(--radius-full);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: var(--radius-full);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-light);
        }
        
        /* Effet de focus global */
        *:focus {
            outline: 2px solid var(--primary);
            outline-offset: 2px;
        }
        
        /* Amélioration de l'accessibilité */
        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
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

# ================================================================================================
# GESTIONNAIRE DE GRAPHIQUES
# ================================================================================================

class ChartManager:
    """Gestionnaire centralisé pour les graphiques"""
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], title: str, color_palette: List[str]) -> go.Figure:
        """Crée un graphique en barres ultra-stylé"""
        fig = go.Figure(data=[go.Bar(
            x=list(data.keys()),
            y=list(data.values()),
            marker=dict(
                color=color_palette,
                line=dict(color='rgba(255,255,255,0.2)', width=2),
                cornerradius=8
            ),
            text=[f"{v:.1f}" for v in data.values()],
            textposition='outside',
            textfont=dict(color='white', size=14, family='Inter', weight=600)
        )])
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=20, color='white', family='Inter', weight=700),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                tickfont=dict(color='white', size=12, family='Inter'),
                tickangle=45,
                showgrid=False,
                showline=True,
                linecolor='rgba(255,255,255,0.2)',
                linewidth=2
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=12, family='Inter'),
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=True,
                showline=True,
                linecolor='rgba(255,255,255,0.2)',
                linewidth=2
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            height=450,
            margin=dict(t=80, b=100, l=70, r=70)
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(data: Dict[str, float], title: str) -> go.Figure:
        """Crée un graphique en jauges ultra-professionnel"""
        fig = make_subplots(
            rows=1, cols=len(data),
            specs=[[{"type": "indicator"}] * len(data)],
            subplot_titles=list(data.keys())
        )
        
        colors = [Config.COLORS['primary'], Config.COLORS['secondary'], Config.COLORS['accent']]
        
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
                            tickfont=dict(size=11, family='Inter', weight=500),
                            ticksuffix='%'
                        ),
                        bar=dict(color=color, thickness=0.8),
                        bgcolor="rgba(28, 35, 51, 0.8)",
                        borderwidth=3,
                        bordercolor="rgba(255,255,255,0.2)",
                        steps=[
                            {'range': [0, 33], 'color': 'rgba(255,255,255,0.03)'},
                            {'range': [33, 66], 'color': 'rgba(255,255,255,0.06)'},
                            {'range': [66, 100], 'color': 'rgba(255,255,255,0.09)'}
                        ],
                        threshold={
                            'line': {'color': "white", 'width': 4},
                            'thickness': 0.8,
                            'value': 80
                        }
                    ),
                    number={
                        'suffix': '%', 
                        'font': {'color': 'white', 'size': 18, 'family': 'Inter', 'weight': 700}
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            height=380,
            title_text=title,
            title_font_color='white',
            title_font_size=20,
            title_font_family='Inter',
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter', size=12),
            margin=dict(t=90, b=70, l=50, r=50)
        )
        
        return fig
    
    @staticmethod
    def create_comparison_chart(player_data: Dict[str, float], avg_data: Dict[str, float], 
                              player_name: str, title: str) -> go.Figure:
        """Crée un graphique de comparaison ultra-professionnel"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=player_name,
            x=list(player_data.keys()),
            y=list(player_data.values()),
            marker_color=Config.COLORS['primary'],
            marker_line=dict(color='rgba(255,255,255,0.3)', width=2),
            text=[f"{v:.2f}" for v in player_data.values()],
            textposition='outside',
            textfont=dict(size=12, family='Inter', weight=600),
            cornerradius=6
        ))
        
        fig.add_trace(go.Bar(
            name='Moyenne autres ligues',
            x=list(avg_data.keys()),
            y=list(avg_data.values()),
            marker_color=Config.COLORS['secondary'],
            marker_line=dict(color='rgba(255,255,255,0.3)', width=2),
            text=[f"{v:.2f}" for v in avg_data.values()],
            textposition='outside',
            textfont=dict(size=12, family='Inter', weight=600),
            cornerradius=6
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color='white', size=22, family='Inter', weight=800),
                x=0.5
            ),
            barmode='group',
            bargap=0.2,
            bargroupgap=0.15,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            xaxis=dict(
                tickfont=dict(color='white', size=12),
                showgrid=False,
                showline=True,
                linecolor='rgba(255,255,255,0.2)',
                linewidth=2
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=12), 
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=True,
                showline=True,
                linecolor='rgba(255,255,255,0.2)',
                linewidth=2
            ),
            height=460,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=13, family='Inter', weight=500),
                bgcolor='rgba(28, 35, 51, 0.8)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=2
            ),
            margin=dict(t=110, b=70, r=70, l=70)
        )
        
        return fig
    
    @staticmethod
    def create_radar_chart(metrics: Dict[str, float], percentiles: List[float], 
                          avg_percentiles: List[float], player_name: str, 
                          comparison_label: str, color: str) -> go.Figure:
        """Crée un radar chart ultra-professionnel"""
        fig = go.Figure()
        
        # Performance du joueur
        fig.add_trace(go.Scatterpolar(
            r=percentiles,
            theta=list(metrics.keys()),
            fill='toself',
            fillcolor=f'rgba({Utils.hex_to_rgb(color)}, 0.3)',
            line=dict(color=color, width=4),
            marker=dict(color=color, size=10, symbol='circle'),
            name=f"{player_name}",
            hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
            customdata=list(metrics.values())
        ))
        
        # Moyenne de comparaison
        fig.add_trace(go.Scatterpolar(
            r=avg_percentiles,
            theta=list(metrics.keys()),
            mode='lines',
            line=dict(color='rgba(255,255,255,0.7)', width=3, dash='dash'),
            name=f'Moyenne {comparison_label}',
            showlegend=True,
            hovertemplate='<b>%{theta}</b><br>Moyenne: %{r:.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(255,255,255,0.15)',
                    tickcolor='white',
                    tickfont=dict(color='white', size=11, family='Inter'),
                    showticklabels=True,
                    tickmode='linear',
                    tick0=0,
                    dtick=20,
                    ticksuffix='%'
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.15)',
                    tickcolor='white',
                    tickfont=dict(color='white', size=12, family='Inter', weight=500),
                    linecolor='rgba(255,255,255,0.2)'
                ),
                bgcolor='rgba(28, 35, 51, 0.7)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            title=dict(
                text=f"Analyse Radar - {player_name}",
                font=dict(size=20, color='white', family='Inter', weight=700),
                x=0.5,
                y=0.95
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(color='white', size=13),
                bgcolor='rgba(28, 35, 51, 0.8)',
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=2
            ),
            height=550,
            margin=dict(t=90, b=120, l=90, r=90)
        )
        
        return fig
    
    @staticmethod
    def create_histogram_comparison(target_player: str, similar_players: List[Dict], 
                                  df: pd.DataFrame, metric: str) -> go.Figure:
        """Crée un histogramme de comparaison ultra-professionnel pour une métrique spécifique"""
        
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
                line=dict(color='rgba(255,255,255,0.4)', width=3),
                opacity=0.9,
                cornerradius=8
            ),
            text=[f"{v:.1f}" if v > 0 else "N/A" for v in player_values],
            textposition='outside',
            textfont=dict(color='white', size=15, family='Inter', weight=700),
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
                line_color="rgba(255,255,255,0.8)",
                line_width=3,
                annotation_text=f"Moyenne (données valides): {avg_value:.1f}",
                annotation_position="top right",
                annotation_font_color="white",
                annotation_font_size=13
            )
        
        # Mise en page ultra-professionnelle
        fig.update_layout(
            title=dict(
                text=f"Comparaison: {metric}",
                font=dict(size=26, color='white', family='Inter', weight=800),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                tickfont=dict(color='white', size=15, family='Inter'),
                tickangle=45,
                showgrid=False,
                title=dict(text="Joueurs", font=dict(color='white', size=17, family='Inter')),
                showline=True,
                linecolor='rgba(255,255,255,0.3)',
                linewidth=2
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=15, family='Inter'),
                gridcolor='rgba(255,255,255,0.12)',
                showgrid=True,
                title=dict(text=metric, font=dict(color='white', size=17, family='Inter')),
                showline=True,
                linecolor='rgba(255,255,255,0.3)',
                linewidth=2
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family='Inter'),
            height=650,
            margin=dict(t=110, b=160, l=90, r=90),
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
# COMPOSANTS UI ULTRA-PROFESSIONNELS
# ================================================================================================

class UIComponents:
    """Composants d'interface utilisateur ultra-professionnels"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête ultra-professionnel"""
        st.markdown("""
        <div class='pro-header animated-card'>
            <h1>FOOTBALL ANALYTICS PRO</h1>
            <p>Plateforme d'Analyse Avancée des Performances • Saison 2024-25 • Elite Dashboard</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_breadcrumbs(competition, team, player):
        """Affiche le fil d'Ariane ultra-moderne"""
        st.markdown(
            f"""
            <div class='breadcrumbs animated-slide'>
                <span style='color:var(--primary); font-weight:700; font-size: 1.1em;'>🏆 {competition}</span> 
                <span style='color:var(--text-secondary); margin: 0 12px;'>›</span>
                <span style='color:var(--accent); font-weight:700; font-size: 1.1em;'>⚽ {team}</span> 
                <span style='color:var(--text-secondary); margin: 0 12px;'>›</span>
                <span style='color:var(--text-primary); font-weight:800; font-size: 1.1em;'>👤 {player}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte complète du joueur avec design ultra-premium"""
        valeur_marchande = Utils.get_market_value_safe(player_data)
        
        container = st.container()
        
        with container:
            col1, col2, col3 = st.columns([1, 3, 1], gap="large")
            
            with col1:
                UIComponents._render_player_photo(player_data['Joueur'])
            
            with col2:
                st.markdown(f"""
                <div class='player-info-card animated-card'>
                    <h2 class='section-title-enhanced' style='margin-bottom: var(--space-2xl); font-size: clamp(2rem, 5vw, 3.5rem); color: var(--text-primary);'>
                        {player_data['Joueur']}
                    </h2>
                    <div class='player-metrics-grid'>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced' style='color: var(--accent);'>{player_data['Âge']}</div>
                            <div class='metric-label-enhanced'>Âge</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced' style='color: var(--primary);'>{player_data['Position']}</div>
                            <div class='metric-label-enhanced'>Position</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced' style='color: var(--secondary);'>{player_data['Nationalité']}</div>
                            <div class='metric-label-enhanced'>Nationalité</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced' style='color: var(--warning);'>{int(player_data['Minutes jouées'])}</div>
                            <div class='metric-label-enhanced'>Minutes Jouées</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced' style='color: var(--success); font-size: 1.5rem;'>{valeur_marchande}</div>
                            <div class='metric-label-enhanced'>Valeur Marchande</div>
                        </div>
                        <div class='metric-card-enhanced'>
                            <div class='metric-value-enhanced' style='color: var(--info);'>{player_data['Équipe']}</div>
                            <div class='metric-label-enhanced'>Équipe</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                UIComponents._render_club_logo(player_data['Équipe'], competition)
    
    @staticmethod
    def render_similar_player_card(player_info: Dict, rank: int):
        """Affiche une carte de joueur similaire avec design ultra-premium"""
        similarity_score = player_info['similarity_score']
        player_data = player_info['data']

        # Couleur basée sur le score de similarité
        if similarity_score >= 85:
            score_color = "var(--success)"
            score_gradient = "linear-gradient(135deg, var(--success), var(--secondary))"
        elif similarity_score >= 70:
            score_color = "var(--warning)"
            score_gradient = "linear-gradient(135deg, var(--warning), var(--accent))"
        else:
            score_color = "var(--info)"
            score_gradient = "linear-gradient(135deg, var(--info), var(--primary))"

        valeur_marchande = Utils.get_market_value_safe(player_data)

        # Logo du club
        logo_path = ImageManager.get_club_logo(player_info['competition'], player_info['equipe'])
        logo_html = ""
        if logo_path and os.path.exists(logo_path):
            try:
                image = Image.open(logo_path)
                logo_base64 = Utils.image_to_base64(image)
                logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="club-logo-small" alt="{player_info["equipe"]}">'
            except Exception:
                logo_html = f'<div style="width: 48px; height: 48px; background: var(--bg-elevated); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 1.2em; color: var(--text-secondary);">🏟️</div>'
        else:
            logo_html = f'<div style="width: 48px; height: 48px; background: var(--bg-elevated); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 1.2em; color: var(--text-secondary);">🏟️</div>'

        # Photo du joueur
        photo_path = ImageManager.get_player_photo(player_info['joueur'])
        if photo_path and os.path.exists(photo_path):
            image = Image.open(photo_path)
            photo_html = f'<img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" style="width:52px; height:52px; border-radius:50%; object-fit:cover; margin-right:12px; border: 3px solid var(--border-secondary);">'
        else:
            photo_html = '<div style="width:52px; height:52px; border-radius:50%; background: var(--bg-elevated); color: var(--text-tertiary); display:inline-flex; align-items:center; justify-content:center; font-size:1.8em; margin-right:12px; border: 3px solid var(--border-secondary);">👤</div>'

        st.markdown(f"""
        <div class='similar-player-card animated-card'>
            <div class='similarity-score' style='background: {score_gradient}; box-shadow: 0 4px 15px rgba(0, 82, 204, 0.3);'>
                #{rank} • {similarity_score:.1f}% Match
            </div>
            <div class='player-header-with-logo' style="display:flex; align-items:center; gap:15px; margin-bottom: var(--space-lg);">
                {photo_html}
                {logo_html}
                <div style="flex: 1;">
                    <h3 style='color: var(--text-primary); margin: 0; font-size: 1.5em; font-weight: 800; line-height: 1.2;'>
                        {player_info['joueur']}
                    </h3>
                    <p style='color: var(--text-secondary); margin: 4px 0 0 0; font-size: 0.9em; font-weight: 500;'>
                        {player_info['competition']} • {player_info['position']}
                    </p>
                </div>
            </div>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-md); margin-bottom: var(--space-lg);'>
                <div class='metric-card-enhanced' style='min-height: 80px; padding: var(--space-md);'>
                    <div class='metric-value-enhanced' style='font-size: 1.2em; color: var(--primary);'>{player_info['equipe']}</div>
                    <div class='metric-label-enhanced'>Équipe</div>
                </div>
                <div class='metric-card-enhanced' style='min-height: 80px; padding: var(--space-md);'>
                    <div class='metric-value-enhanced' style='font-size: 1.2em; color: var(--secondary);'>{player_info['position']}</div>
                    <div class='metric-label-enhanced'>Position</div>
                </div>
                <div class='metric-card-enhanced' style='min-height: 80px; padding: var(--space-md);'>
                    <div class='metric-value-enhanced' style='font-size: 1.2em; color: var(--accent);'>{player_info['age']}</div>
                    <div class='metric-label-enhanced'>Âge</div>
                </div>
            </div>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-md);'>
                <div class='metric-card-enhanced' style='min-height: 70px; padding: var(--space-md);'>
                    <div class='metric-value-enhanced' style='font-size: 1.1em; color: var(--success);'>{valeur_marchande}</div>
                    <div class='metric-label-enhanced'>Valeur Marchande</div>
                </div>
                <div class='metric-card-enhanced' style='min-height: 70px; padding: var(--space-md);'>
                    <div class='metric-value-enhanced' style='font-size: 1.1em; color: var(--warning);'>{player_info['competition']}</div>
                    <div class='metric-label-enhanced'>Compétition</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_player_photo(player_name: str):
        """Affiche la photo du joueur avec design premium"""
        photo_path = ImageManager.get_player_photo(player_name)
        
        if photo_path:
            try:
                image = Image.open(photo_path)
                st.markdown(f"""
                <div class='image-container animated-card'>
                    <img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: var(--radius-lg); box-shadow: var(--shadow-lg);">
                </div>
                <p style='text-align: center; color: var(--primary); font-weight: 700; margin-top: var(--space-lg); font-size: 1rem; letter-spacing: 0.5px;'>
                    📸 {player_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_photo_placeholder(player_name)
        else:
            UIComponents._render_photo_placeholder(player_name)
    
    @staticmethod
    def _render_club_logo(team_name: str, competition: str):
        """Affiche le logo du club avec design premium"""
        logo_path = ImageManager.get_club_logo(competition, team_name)
        
        if logo_path:
            try:
                image = Image.open(logo_path)
                st.markdown(f"""
                <div class='club-logo-container animated-card'>
                    <img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));">
                </div>
                <p style='text-align: center; color: var(--primary); font-weight: 700; margin-top: var(--space-lg); font-size: 1rem; letter-spacing: 0.5px;'>
                    🏟️ {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_logo_placeholder(team_name)
        else:
            UIComponents._render_logo_placeholder(team_name)
    
    @staticmethod
    def _render_photo_placeholder(player_name: str):
        """Affiche un placeholder premium pour la photo"""
        st.markdown(f"""
        <div class='image-container animated-card'>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 5em; margin-bottom: var(--space-lg); opacity: 0.6; color: var(--primary);'>👤</div>
                <p style='margin: 0; font-size: 1.1em; font-weight: 600; color: var(--text-primary);'>Photo non disponible</p>
                <p style='font-size: 0.9em; margin-top: var(--space-md); color: var(--primary); font-weight: 500;'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder(team_name: str):
        """Affiche un placeholder premium pour le logo"""
        st.markdown(f"""
        <div class='club-logo-container animated-card'>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 4em; margin-bottom: var(--space-lg); opacity: 0.6; color: var(--primary);'>🏟️</div>
                <p style='margin: 0; font-size: 0.9em; font-weight: 600; color: var(--text-primary);'>Logo non disponible</p>
                <p style='font-size: 0.8em; margin-top: var(--space-sm); color: var(--primary); font-weight: 500;'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """Affiche le footer ultra-professionnel"""
        st.markdown("""
        <div class='dashboard-footer animated-card'>
            <h3 style='color: var(--primary); margin: 0 0 var(--space-lg) 0; font-weight: 800; font-size: 1.5em;'>
                Football Analytics Pro
            </h3>
            <p style='color: var(--text-primary); margin: 0; font-size: 1.2em; font-weight: 600;'>
                🚀 Analyse Elite des Performances Footballistiques
            </p>
            <p style='color: var(--text-secondary); margin: var(--space-md) 0 0 0; font-size: 1rem; font-weight: 500;'>
                📊 Data: FBRef | 🎨 Design: Elite Dashboard | ⚽ Saison 2024-25
            </p>
            <div style='margin-top: var(--space-lg); padding-top: var(--space-lg); border-top: 1px solid var(--border-primary);'>
                <span style='color: var(--primary); font-weight: 700; font-size: 0.9em;'>
                    Powered by Advanced Analytics • Built for Professional Football
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE SIDEBAR ULTRA-MODERNE
# ================================================================================================

class SidebarManager:
    """Gestionnaire pour la sidebar ultra-moderne"""
    
    @staticmethod
    def render_sidebar(df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
        """Rendu complet de la sidebar ultra-professionnelle"""
        with st.sidebar:
            # En-tête ultra-moderne
            st.markdown("""
            <div class='sidebar-header'>
                <h2 style='color: white; margin: 0; font-weight: 800; font-size: 1.4em; position: relative; z-index: 2;'>⚙️ CENTRE DE CONTRÔLE</h2>
                <p style='color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 1rem; font-weight: 500; position: relative; z-index: 2;'>
                    Configuration Avancée
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Sélection de la compétition avec style premium
            st.markdown("### 🏆 Compétition Elite")
            competitions = DataManager.get_competitions(df)
            selected_competition = st.selectbox(
                "Sélectionnez la compétition :",
                competitions,
                index=0,
                help="🎯 Filtrez par compétition pour une analyse ciblée"
            )
            
            # Filtrage par compétition
            df_filtered = DataManager.filter_by_competition(df, selected_competition)
            
            st.markdown("---")
            
            # Filtre par minutes jouées avec design premium
            min_minutes_filter = 0
            if not df_filtered['Minutes jouées'].empty:
                min_minutes = int(df_filtered['Minutes jouées'].min())
                max_minutes = int(df_filtered['Minutes jouées'].max())
                
                st.markdown("### ⏱️ Filtre Temps de Jeu")
                st.markdown("**Filtrage par minutes jouées**")
                
                min_minutes_filter = st.slider(
                    "Minutes minimum :",
                    min_value=min_minutes,
                    max_value=max_minutes,
                    value=min_minutes,
                    step=90,
                    help="🎯 Filtrez les joueurs selon leur temps de jeu minimum"
                )
                
                # Progress bar stylée
                if max_minutes > min_minutes:
                    percentage_filtered = (min_minutes_filter - min_minutes) / (max_minutes - min_minutes) * 100
                    st.progress(percentage_filtered / 100)
                    st.caption(f"📊 Filtre appliqué: {percentage_filtered:.1f}%")
            
            # Application du filtre minutes
            df_filtered_minutes = DataManager.filter_by_minutes(df_filtered, min_minutes_filter)
            
            # Informations sur le filtrage avec design premium
            nb_joueurs = len(df_filtered_minutes)
            
            if nb_joueurs > 0:
                st.success(f"✅ **{nb_joueurs} joueurs** sélectionnés")
                
                # Statistiques additionnelles avec design premium
                with st.expander("📊 Analytics du Filtrage", expanded=False):
                    avg_minutes = df_filtered_minutes['Minutes jouées'].mean()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Moy. Minutes", f"{avg_minutes:.0f}")
                        st.metric("Équipes", f"{df_filtered_minutes['Équipe'].nunique()}")
                    with col2:
                        st.metric("Positions", f"{df_filtered_minutes['Position'].nunique()}")
                        st.metric("Âge Moyen", f"{df_filtered_minutes['Âge'].mean():.1f}")
            else:
                st.warning("⚠️ Aucun joueur ne correspond aux critères")
            
            st.markdown("---")
            
            # Sélection du joueur avec design premium
            selected_player = None
            if not df_filtered_minutes.empty:
                joueurs = DataManager.get_players(df_filtered_minutes)
                if joueurs:
                    st.markdown("### 👤 Sélection Joueur")
                    
                    # Option de recherche premium
                    search_term = st.text_input(
                        "🔍 Recherche intelligente :", 
                        placeholder="Tapez le nom du joueur...",
                        help="🎯 Recherche en temps réel dans la base de données"
                    )
                    
                    if search_term:
                        joueurs_filtered = [j for j in joueurs if search_term.lower() in j.lower()]
                        if joueurs_filtered:
                            selected_player = st.selectbox(
                                "👤 Résultats de recherche :",
                                joueurs_filtered,
                                help="✨ Joueur trouvé avec la recherche"
                            )
                        else:
                            st.warning(f"🔍 Aucun résultat pour '{search_term}'")
                            selected_player = st.selectbox(
                                "👤 Tous les joueurs :",
                                joueurs,
                                help="📋 Liste complète des joueurs disponibles"
                            )
                    else:
                        selected_player = st.selectbox(
                            "👤 Sélectionnez un joueur :",
                            joueurs,
                            index=0,
                            help="🎯 Choisissez le joueur à analyser"
                        )
                else:
                    st.error("❌ Aucun joueur disponible avec ces critères.")
            else:
                st.error("❌ Aucun joueur disponible avec ces critères.")
            
            # Stats de session premium
            if selected_player:
                st.markdown("---")
                st.markdown("### 📈 Session Analytics")
                player_data = df_filtered_minutes[df_filtered_minutes['Joueur'] == selected_player].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Position", player_data['Position'])
                with col2:
                    st.metric("Équipe", player_data['Équipe'])
            
            # Footer sidebar premium
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; padding: var(--space-xl); background: var(--gradient-surface); border-radius: var(--radius-lg); border: 1px solid var(--border-primary); position: relative; overflow: hidden;'>
                <div style='position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--gradient-primary);'></div>
                <p style='color: var(--text-primary); margin: 0; font-size: 1.1em; font-weight: 700;'>
                    🚀 Analytics Pro
                </p>
                <p style='color: var(--text-secondary); margin: 8px 0 0 0; font-size: 0.9em; font-weight: 500;'>
                    Elite Football Dashboard
                </p>
                <div style='margin-top: 12px; padding: 8px; background: rgba(0, 82, 204, 0.1); border-radius: 6px; border: 1px solid var(--primary);'>
                    <span style='color: var(--primary); font-size: 0.8em; font-weight: 600;'>
                        Powered by Advanced AI
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            return selected_competition, selected_player, df_filtered_minutes

# ================================================================================================
# GESTIONNAIRE DE TABS ULTRA-MODERNE
# ================================================================================================

class TabManager:
    """Gestionnaire pour les différents onglets ultra-modernes"""
    
    @staticmethod
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str, player_competition: str):
        """Rendu de l'onglet performance offensive ultra-professionnel"""
        st.markdown("<h2 class='section-title-enhanced'>🎯 PERFORMANCE OFFENSIVE ELITE</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_offensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Graphique en barres des actions offensives ultra-stylé
            basic_actions = {
                'Buts': player_data.get('Buts', 0),
                'Passes décisives': player_data.get('Passes décisives', 0),
                'Passes clés': player_data.get('Passes clés', 0),
                'Tirs': player_data.get('Tirs', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "🎯 Actions Offensives Elite",
                Config.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Métriques avec design ultra-moderne
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques Elite</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="🎯 Buts par 90min",
                    value=f"{analysis['metrics']['Buts/90']:.2f}",
                    delta=f"{analysis['metrics']['Buts/90'] - analysis['avg_metrics']['Buts/90']:.2f}",
                    help="⚽ Efficacité de finition par 90 minutes"
                )
                st.metric(
                    label="🎲 xG par 90min",
                    value=f"{analysis['metrics']['xG/90']:.2f}",
                    delta=f"{analysis['metrics']['xG/90'] - analysis['avg_metrics']['xG/90']:.2f}",
                    help="📈 Expected Goals - Qualité des occasions"
                )
            
            with metric_col2:
                st.metric(
                    label="🎯 Passes D. par 90min",
                    value=f"{analysis['metrics']['Passes D./90']:.2f}",
                    delta=f"{analysis['metrics']['Passes D./90'] - analysis['avg_metrics']['Passes D./90']:.2f}",
                    help="🔄 Créativité et vision de jeu"
                )
                st.metric(
                    label="🎲 xA par 90min",
                    value=f"{analysis['metrics']['xA/90']:.2f}",
                    delta=f"{analysis['metrics']['xA/90'] - analysis['avg_metrics']['xA/90']:.2f}",
                    help="📊 Expected Assists - Qualité des passes"
                )
        
        with col2:
            # Métriques d'efficacité ultra-modernes
            efficiency_data = {
                'Précision Tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                'Réussite Dribbles': player_data.get('Pourcentage de dribbles réussis', 0),
                'Conversion': (player_data.get('Buts', 0) / player_data.get('Tirs', 1) * 100) if player_data.get('Tirs', 0) > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(efficiency_data, "🔥 Efficacité Offensive Elite (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar ultra-professionnel
            st.markdown("<h3 class='subsection-title-enhanced'>🎯 Radar Elite</h3>", unsafe_allow_html=True)
            
            # Légende ultra-moderne
            st.markdown(f"""
            <div class='chart-legend'>
                <div class='legend-item'>
                    <div class='legend-color' style='background: var(--primary); box-shadow: 0 2px 8px rgba(0, 82, 204, 0.4);'></div>
                    <span style='font-weight: 700;'>{selected_player}</span>
                </div>
                <div class='legend-item'>
                    <div class='legend-color' style='background: rgba(255,255,255,0.7); box-shadow: 0 2px 8px rgba(255, 255, 255, 0.3);'></div>
                    <span style='font-weight: 600;'>Moyenne Elite</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "autres ligues elite",
                Config.COLORS['primary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison détaillée ultra-professionnelle
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📈 Benchmark Elite vs Compétition</h3>", unsafe_allow_html=True)
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "🚀 Performance Elite par 90min vs Benchmark Compétition"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str, player_competition: str):
        """Rendu de l'onglet performance défensive ultra-professionnel"""
        st.markdown("<h2 class='section-title-enhanced'>🛡️ PERFORMANCE DÉFENSIVE ELITE</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_defensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Actions défensives ultra-stylées
            basic_actions = {
                'Tacles': player_data.get('Tacles gagnants', 0),
                'Interceptions': player_data.get('Interceptions', 0),
                'Récupérations': player_data.get('Ballons récupérés', 0),
                'Duels Aériens': player_data.get('Duels aériens gagnés', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "🛡️ Actions Défensives Elite",
                Config.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Métriques défensives ultra-modernes
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques Défense Elite</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="⚔️ Tacles par 90min",
                    value=f"{analysis['metrics']['Tacles/90']:.2f}",
                    delta=f"{analysis['metrics']['Tacles/90'] - analysis['avg_metrics']['Tacles/90']:.2f}",
                    help="🔥 Intensité défensive et pressing"
                )
                st.metric(
                    label="🎯 Interceptions par 90min",
                    value=f"{analysis['metrics']['Interceptions/90']:.2f}",
                    delta=f"{analysis['metrics']['Interceptions/90'] - analysis['avg_metrics']['Interceptions/90']:.2f}",
                    help="🧠 Intelligence tactique et anticipation"
                )
            
            with metric_col2:
                st.metric(
                    label="💪 % Duels gagnés",
                    value=f"{analysis['metrics']['% Duels gagnés']:.1f}%",
                    delta=f"{analysis['metrics']['% Duels gagnés'] - analysis['avg_metrics']['% Duels gagnés']:.1f}%",
                    help="🏆 Domination physique au sol"
                )
                st.metric(
                    label="🚀 % Duels aériens",
                    value=f"{analysis['metrics']['% Duels aériens']:.1f}%",
                    delta=f"{analysis['metrics']['% Duels aériens'] - analysis['avg_metrics']['% Duels aériens']:.1f}%",
                    help="✈️ Supériorité aérienne"
                )
        
        with col2:
            # Efficacité défensive ultra-moderne
            success_data = {
                'Duels Sol': player_data.get('Pourcentage de duels gagnés', 0),
                'Duels Aériens': player_data.get('Pourcentage de duels aériens gagnés', 0),
                'Impact Récup.': min(100, (player_data.get('Ballons récupérés', 0) / max(player_data.get('Minutes jouées', 90), 1) * 90 * 8)) if player_data.get('Ballons récupérés', 0) > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(success_data, "🔥 Efficacité Défensive Elite (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar défensif ultra-professionnel
            st.markdown("<h3 class='subsection-title-enhanced'>🛡️ Radar Défense Elite</h3>", unsafe_allow_html=True)
            
            # Légende ultra-moderne
            st.markdown(f"""
            <div class='chart-legend'>
                <div class='legend-item'>
                    <div class='legend-color' style='background: var(--accent); box-shadow: 0 2px 8px rgba(255, 107, 53, 0.4);'></div>
                    <span style='font-weight: 700;'>{selected_player}</span>
                </div>
                <div class='legend-item'>
                    <div class='legend-color' style='background: rgba(255,255,255,0.7); box-shadow: 0 2px 8px rgba(255, 255, 255, 0.3);'></div>
                    <span style='font-weight: 600;'>Benchmark Elite</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "autres ligues elite",
                Config.COLORS['accent']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison détaillée ultra-professionnelle
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📈 Benchmark Défensif Elite</h3>", unsafe_allow_html=True)
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "🛡️ Performance Défensive Elite par 90min vs Benchmark"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_technical_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str, player_competition: str):
        """Rendu de l'onglet performance technique ultra-professionnel"""
        st.markdown("<h2 class='section-title-enhanced'>🎨 MAÎTRISE TECHNIQUE ELITE</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_technical_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Actions techniques ultra-stylées
            basic_actions = {
                'Passes Tentées': player_data.get('Passes tentées', 0),
                'Dribbles': player_data.get('Dribbles tentés', 0),
                'Passes Clés': player_data.get('Passes clés', 0),
                'Passes Prog.': player_data.get('Passes progressives', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "🎨 Maîtrise Technique Elite",
                Config.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Métriques techniques ultra-modernes
            st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques Technique Elite</h3>", unsafe_allow_html=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric(
                    label="🎯 Passes par 90min",
                    value=f"{analysis['metrics']['Passes tentées/90']:.1f}",
                    delta=f"{analysis['metrics']['Passes tentées/90'] - analysis['avg_metrics']['Passes tentées/90']:.1f}",
                    help="📊 Volume de jeu et implication"
                )
                st.metric(
                    label="🔑 Passes clés par 90min",
                    value=f"{analysis['metrics']['Passes clés/90']:.1f}",
                    delta=f"{analysis['metrics']['Passes clés/90'] - analysis['avg_metrics']['Passes clés/90']:.1f}",
                    help="✨ Créativité et vision tactique"
                )
            
            with metric_col2:
                st.metric(
                    label="🎯 % Passes réussies",
                    value=f"{analysis['metrics']['% Passes réussies']:.1f}%",
                    delta=f"{analysis['metrics']['% Passes réussies'] - analysis['avg_metrics']['% Passes réussies']:.1f}%",
                    help="🎨 Précision technique"
                )
                st.metric(
                    label="⚡ % Dribbles réussis",
                    value=f"{analysis['metrics']['% Dribbles réussis']:.1f}%",
                    delta=f"{analysis['metrics']['% Dribbles réussis'] - analysis['avg_metrics']['% Dribbles réussis']:.1f}%",
                    help="🔥 Maîtrise individuelle"
                )
        
        with col2:
            # Maîtrise technique ultra-moderne
            technical_success = {
                'Précision Passes': player_data.get('Pourcentage de passes progressives réussies', player_data.get('Pourcentage de passes réussies', 0)),
                'Impact Progressif': min(100, (player_data.get('Courses progressives', player_data.get('Dribbles réussis', 0)) / max(player_data.get('Minutes jouées', 90), 1) * 90 * 8)) if player_data.get('Courses progressives', player_data.get('Dribbles réussis', 0)) > 0 else 0,
                'Influence Jeu': min(100, (player_data.get('Touches de balle', 0) / max(player_data.get('Minutes jouées', 90), 1) * 90 / 80 * 100)) if player_data.get('Touches de balle', 0) > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(technical_success, "🎨 Maîtrise Technique Elite (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar technique ultra-professionnel
            st.markdown("<h3 class='subsection-title-enhanced'>🎨 Radar Technique Elite</h3>", unsafe_allow_html=True)
            
            # Légende ultra-moderne
            st.markdown(f"""
            <div class='chart-legend'>
                <div class='legend-item'>
                    <div class='legend-color' style='background: var(--secondary); box-shadow: 0 2px 8px rgba(0, 184, 163, 0.4);'></div>
                    <span style='font-weight: 700;'>{selected_player}</span>
                </div>
                <div class='legend-item'>
                    <div class='legend-color' style='background: rgba(255,255,255,0.7); box-shadow: 0 2px 8px rgba(255, 255, 255, 0.3);'></div>
                    <span style='font-weight: 600;'>Elite Standard</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "standard elite",
                Config.COLORS['secondary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison technique ultra-professionnelle
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📈 Benchmark Technique Elite</h3>", unsafe_allow_html=True)
        
        selected_metrics = ['Passes tentées/90', 'Passes prog./90', 'Dribbles/90', 'Passes clés/90']
        comparison_metrics = {k: analysis['metrics'][k] for k in selected_metrics if k in analysis['metrics']}
        avg_comparison = {k: analysis['avg_metrics'][k] for k in selected_metrics if k in analysis['avg_metrics']}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "🎨 Maîtrise Technique Elite par 90min vs Standard Elite"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    @staticmethod
    def render_similar_players_tab(selected_player: str, df: pd.DataFrame):
        """Rendu de l'onglet joueurs similaires ultra-professionnel"""
        st.markdown("<h2 class='section-title-enhanced'>👥 PROFILS SIMILAIRES ELITE</h2>", unsafe_allow_html=True)
        
        # Configuration ultra-moderne
        col1, col2 = st.columns([2.5, 1])
        
        with col1:
            st.markdown("<h3 class='subsection-title-enhanced'>⚙️ Moteur d'Analyse Elite</h3>", unsafe_allow_html=True)
            st.markdown("""
            <div class='pro-card' style='padding: var(--space-lg);'>
                <p style='color: var(--text-primary); font-size: 1.1em; font-weight: 500; margin: 0;'>
                    🚀 <strong>Intelligence Artificielle Avancée</strong> : Utilise 21+ métriques multidimensionnelles 
                    couvrant le volume, l'efficacité, la progression, l'aspect physique et la finition pour une 
                    précision de matching élite.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            num_similar = st.slider(
                "🎯 Nombre de profils similaires :",
                min_value=1,
                max_value=10,
                value=5,
                help="🔥 Sélectionnez le nombre de joueurs similaires elite"
            )
        
        # Status de l'IA
        if not SKLEARN_AVAILABLE:
            st.info("🤖 IA en mode standard (scikit-learn non disponible)")
        else:
            st.success("🚀 IA Elite activée avec algorithmes avancés")
        
        # Métriques détaillées ultra-modernes
        with st.expander("🔬 Voir les 21+ Métriques Elite utilisées", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **🎯 Volume & Impact**
                • Minutes jouées
                • Buts & Passes décisives  
                • Tirs & Passes clés
                • Passes tentées
                • Dribbles tentés
                • Tacles gagnants
                • Interceptions
                """)
                
            with col2:
                st.markdown("""
                **🔥 Qualité & Progression**
                • % Passes réussies
                • % Dribbles réussis
                • Passes progressives
                • Courses progressives
                • Passes dernier tiers
                • Ballons récupérés
                • Précision technique
                """)
                
            with col3:
                st.markdown("""
                **💪 Physique & Finition**
                • Duels aériens gagnés
                • Duels défensifs gagnés
                • Tirs cadrés
                • Actions → Tir
                • Domination physique
                • Intelligence tactique
                • Impact global
                """)
        
        # Calcul avec IA avancée
        with st.spinner("🔍 IA Elite en cours d'analyse..."):
            similar_players = SimilarPlayerAnalyzer.calculate_similarity(selected_player, df, num_similar)
        
        if not similar_players:
            st.warning("⚠️ Aucun profil similaire détecté. Vérifiez la base de données.")
            return
        
        # Résultats ultra-professionnels
        st.markdown(f"<h3 class='subsection-title-enhanced'>🎯 Top {len(similar_players)} Profils Elite similaires à {selected_player}</h3>", unsafe_allow_html=True)
        st.caption("*Analyse IA basée sur 21+ métriques multidimensionnelles couvrant tous les aspects du jeu moderne*")
        
        # Dashboard de métriques elite
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            avg_similarity = np.mean([p['similarity_score'] for p in similar_players])
            st.metric("🎯 Similarité Moyenne", f"{avg_similarity:.1f}%", 
                     help="Score IA moyen de correspondance des profils")
        
        with metrics_col2:
            best_match = similar_players[0] if similar_players else None
            if best_match:
                st.metric("🏆 Meilleur Match Elite", best_match['joueur'], 
                         f"{best_match['similarity_score']:.1f}%")
        
        with metrics_col3:
            unique_competitions = len(set(p['competition'] for p in similar_players))
            st.metric("🌍 Compétitions Elite", f"{unique_competitions}", 
                     help="Diversité géographique des profils")
        
        with metrics_col4:
            high_similarity_count = len([p for p in similar_players if p['similarity_score'] >= 80])
            st.metric("🔥 Matches Elite (≥80%)", f"{high_similarity_count}/{len(similar_players)}", 
                     help="Profils avec correspondance très élevée")
        
        # Cartes des joueurs similaires ultra-modernes
        st.markdown("---")
        
        # Affichage en colonnes premium
        cols_per_row = 2
        for i in range(0, len(similar_players), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(similar_players):
                    with col:
                        UIComponents.render_similar_player_card(similar_players[i + j], i + j + 1)
        
        # Section histogrammes ultra-professionnelle
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📊 Analyse Comparative Elite</h3>", unsafe_allow_html=True)
        st.caption("*Comparez n'importe quelle métrique entre le joueur sélectionné et ses profils similaires elite*")
        
        # Métriques disponibles ultra-organisées
        excluded_columns = [
            'Joueur', 'Équipe', 'Compétition', 'Position', 'Nationalité', 
            'Âge', 'Valeur marchande', 'Nom', 'Club', 'League', 'Team',
            'Player', 'Nation', 'Age', 'Market Value', 'Column1'
        ]
        
        available_histogram_metrics = []
        for col in df.columns:
            if col not in excluded_columns:
                try:
                    pd.to_numeric(df[col].dropna().iloc[:5], errors='raise')
                    available_histogram_metrics.append(col)
                except (ValueError, TypeError, IndexError):
                    continue
        
        available_histogram_metrics = sorted(available_histogram_metrics)
        
        if available_histogram_metrics:
            # Interface ultra-moderne
            metric_col1, metric_col2, metric_col3 = st.columns([2.5, 1, 1])
            
            with metric_col1:
                selected_metric = st.selectbox(
                    f"📈 Sélectionnez une métrique elite ({len(available_histogram_metrics)} disponibles) :",
                    available_histogram_metrics,
                    index=0,
                    help="🎯 Analysez n'importe quelle métrique du dataset elite"
                )
            
            with metric_col2:
                st.markdown(f"""
                <div class='pro-card' style='padding: var(--space-md); text-align: center;'>
                    <p style='color: var(--primary); font-weight: 700; margin: 0; font-size: 1.1em;'>
                        🎯 {selected_metric}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col3:
                if selected_metric in df.columns:
                    non_null_count = df[selected_metric].count()
                    total_count = len(df)
                    coverage = (non_null_count / total_count) * 100
                    st.metric("📊 Couverture Elite", f"{coverage:.0f}%", 
                             help=f"{non_null_count}/{total_count} joueurs dans la base")
            
            # Histogramme ultra-professionnel
            if selected_metric:
                fig_histogram = ChartManager.create_histogram_comparison(
                    selected_player, similar_players, df, selected_metric
                )
                st.plotly_chart(fig_histogram, use_container_width=True)
                
                # Analytics détaillés ultra-modernes
                target_data = df[df['Joueur'] == selected_player]
                if not target_data.empty:
                    def find_column_name_quick(metric_name: str, df_columns: List[str]) -> Optional[str]:
                        if metric_name in df_columns:
                            return metric_name
                        for col in df_columns:
                            if metric_name.lower() in col.lower() or col.lower() in metric_name.lower():
                                return col
                        return metric_name
                    
                    actual_column = find_column_name_quick(selected_metric, df.columns.tolist())
                    target_value = target_data[actual_column].iloc[0]
                    
                    if not pd.isna(target_value):
                        similar_values = []
                        valid_players = []
                        
                        for player_info in similar_players:
                            player_name = player_info['joueur']
                            player_data_from_df = df[df['Joueur'] == player_name]
                            
                            if not player_data_from_df.empty:
                                value = player_data_from_df[actual_column].iloc[0]
                                if not pd.isna(value):
                                    similar_values.append(value)
                                    valid_players.append(player_name)
                        
                        if similar_values:
                            avg_similar = np.mean(similar_values)
                            max_similar = np.max(similar_values)
                            min_similar = np.min(similar_values)
                            
                            max_player = valid_players[similar_values.index(max_similar)]
                            min_player = valid_players[similar_values.index(min_similar)]
                            
                            st.markdown("---")
                            st.markdown("**📊 Analytics Elite de Comparaison**")
                            
                            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                            
                            with stats_col1:
                                st.metric(f"🎯 {selected_player}", f"{target_value:.1f}", 
                                         help=f"Performance elite du joueur pour {selected_metric}")
                            
                            with stats_col2:
                                st.metric("📊 Moyenne Elite", f"{avg_similar:.1f}",
                                         delta=f"{target_value - avg_similar:.1f}",
                                         help="Moyenne des joueurs similaires elite")
                            
                            with stats_col3:
                                st.metric("🏆 Performance Max", f"{max_similar:.1f}",
                                         delta=max_player,
                                         help="Meilleure performance du groupe")
                            
                            with stats_col4:
                                st.metric("📉 Performance Min", f"{min_similar:.1f}",
                                         delta=min_player,
                                         help="Performance minimale du groupe")
        else:
            st.warning("⚠️ Aucune métrique numérique disponible pour l'analyse elite")
            
        # Catalogue des métriques ultra-organisé
        if available_histogram_metrics:
            with st.expander(f"📋 Catalogue Complet : {len(available_histogram_metrics)} Métriques Elite", expanded=False):
                offensive_metrics = [m for m in available_histogram_metrics if any(keyword in m.lower() for keyword in ['but', 'tir', 'pass', 'assist', 'xg', 'xa', 'action'])]
                defensive_metrics = [m for m in available_histogram_metrics if any(keyword in m.lower() for keyword in ['tacl', 'intercept', 'duel', 'récup', 'dégage', 'bloc'])]
                technical_metrics = [m for m in available_histogram_metrics if any(keyword in m.lower() for keyword in ['dribbl', 'touch', 'course', 'progress', 'centr', 'pourc'])]
                other_metrics = [m for m in available_histogram_metrics if m not in offensive_metrics + defensive_metrics + technical_metrics]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if offensive_metrics:
                        st.markdown("**🎯 Offensives Elite**")
                        for metric in offensive_metrics[:10]:
                            st.markdown(f"• {metric}")
                        if len(offensive_metrics) > 10:
                            st.markdown(f"• ... et {len(offensive_metrics) - 10} autres")
                
                with col2:
                    if defensive_metrics:
                        st.markdown("**🛡️ Défensives Elite**")
                        for metric in defensive_metrics[:10]:
                            st.markdown(f"• {metric}")
                        if len(defensive_metrics) > 10:
                            st.markdown(f"• ... et {len(defensive_metrics) - 10} autres")
                
                with col3:
                    if technical_metrics:
                        st.markdown("**🎨 Techniques Elite**")
                        for metric in technical_metrics[:10]:
                            st.markdown(f"• {metric}")
                        if len(technical_metrics) > 10:
                            st.markdown(f"• ... et {len(technical_metrics) - 10} autres")
                
                with col4:
                    if other_metrics:
                        st.markdown("**📊 Autres Elite**")
                        for metric in other_metrics[:10]:
                            st.markdown(f"• {metric}")
                        if len(other_metrics) > 10:
                            st.markdown(f"• ... et {len(other_metrics) - 10} autres")
    
    @staticmethod
    def render_comparison_tab(df: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet comparaison ultra-professionnel"""
        st.markdown("<h2 class='section-title-enhanced'>🔄 COMPARAISON RADAR ELITE</h2>", unsafe_allow_html=True)
        
        # Mode de visualisation ultra-moderne
        mode = st.radio(
            "🎯 Mode d'Analyse Elite",
            ["🎯 Radar Individuel Elite", "⚔️ Duel Radar Elite"],
            horizontal=True,
            help="🚀 Choisissez le type d'analyse radar elite"
        )
        
        competitions = sorted(df['Compétition'].dropna().unique())
        
        if mode == "🎯 Radar Individuel Elite":
            TabManager._render_individual_radar(df, selected_player, competitions)
        else:
            TabManager._render_comparative_radar(df, competitions)
    
    @staticmethod
    def _render_individual_radar(df: pd.DataFrame, selected_player: str, competitions: List[str]):
        """Rendu du radar individuel ultra-professionnel"""
        st.markdown(f"<h3 class='subsection-title-enhanced'>🎯 Analyse Radar Elite : {selected_player}</h3>", unsafe_allow_html=True)
        
        try:
            col1, col2 = st.columns([2.5, 1])
            
            with col1:
                competition = st.selectbox(
                    "🏆 Compétition de Référence Elite", 
                    competitions,
                    help="🎯 Benchmark elite pour le calcul des percentiles"
                )
            
            with col2:
                st.markdown(f"""
                <div class='pro-card' style='padding: var(--space-lg); text-align: center;'>
                    <p style='color: var(--primary); font-weight: 700; margin: 0; font-size: 1.1em;'>
                        📊 Analyse vs {competition}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            df_comp = df[df['Compétition'] == competition]
            
            values = MetricsCalculator.calculate_percentiles(selected_player, df_comp)
            
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            baker = PyPizza(
                params=list(Config.RADAR_METRICS.keys()),
                background_color="#0A0E17",
                straight_line_color="#FFFFFF",
                straight_line_lw=2,
                last_circle_color="#FFFFFF",
                last_circle_lw=2,
                other_circle_lw=0,
                inner_circle_size=12
            )
            
            fig, ax = baker.make_pizza(
                values,
                figsize=(16, 18),
                param_location=110,
                color_blank_space="same",
                slice_colors=[Config.COLORS['primary']] * len(values),
                value_colors=["#ffffff"] * len(values),
                value_bck_colors=[Config.COLORS['primary']] * len(values),
                kwargs_slices=dict(edgecolor="#FFFFFF", zorder=2, linewidth=3),
                kwargs_params=dict(color="#ffffff", fontsize=14, fontproperties=font_bold.prop),
                kwargs_values=dict(
                    color="#ffffff", 
                    fontsize=12, 
                    fontproperties=font_normal.prop,
                    bbox=dict(
                        edgecolor="#FFFFFF", 
                        facecolor=Config.COLORS['primary'], 
                        boxstyle="round,pad=0.4", 
                        lw=2
                    )
                )
            )
            
            # Titre ultra-professionnel
            fig.text(0.515, 0.97, selected_player, size=32, ha="center", 
                    fontproperties=font_bold.prop, color="#ffffff", weight='bold')
            fig.text(0.515, 0.94, f"ANALYSE RADAR ELITE | Percentiles vs {competition} | Saison 2024-25", 
                    size=16, ha="center", fontproperties=font_bold.prop, color="#B3BAC5")
            
            fig.text(0.99, 0.01, "Football Analytics Pro | Elite Dashboard | Data: FBRef", 
                    size=10, ha="right", fontproperties=font_italic.prop, color="#8993A4")
            
            st.pyplot(fig, use_container_width=True)
            
            # Analytics du radar ultra-modernes
            st.markdown("---")
            
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                avg_percentile = np.mean(values)
                st.metric("🎯 Percentile Elite Moyen", f"{avg_percentile:.1f}%",
                         help="Performance moyenne elite tous domaines")
            
            with stats_col2:
                max_stat = max(values)
                max_index = values.index(max_stat)
                max_param = list(Config.RADAR_METRICS.keys())[max_index]
                st.metric("🏆 Force Elite Majeure", f"{max_param.replace('\\n', ' ')}", 
                         f"{max_stat}%", help="Domaine de supériorité elite")
            
            with stats_col3:
                negative_metrics = ["Cartons\njaunes", "Cartons\nrouges", "Ballons perdus\nsous pression", "Ballons perdus\nen conduite"]
                
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
                    st.metric("🚀 Potentiel d'Amélioration", f"{min_param.replace('\\n', ' ')}", 
                             f"{min_stat}%", help="Axe de développement prioritaire")
                else:
                    st.metric("🏆 Profil Elite", "Excellence Globale", "✨",
                             help="Joueur elite dans tous les domaines")
            
        except Exception as e:
            st.error(f"Erreur lors de la création du radar elite : {str(e)}")
    
    @staticmethod
    def _render_comparative_radar(df: pd.DataFrame, competitions: List[str]):
        """Rendu du radar comparatif ultra-professionnel"""
        st.markdown("<h3 class='subsection-title-enhanced'>⚙️ Configuration Duel Elite</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("**👤 JOUEUR ELITE 1**")
            ligue1 = st.selectbox("🏆 Compétition", competitions, key="ligue1_comp")
            df_j1 = df[df['Compétition'] == ligue1]
            joueur1 = st.selectbox("⭐ Joueur", df_j1['Joueur'].sort_values(), key="joueur1_comp")
        
        with col2:
            st.markdown("**👤 JOUEUR ELITE 2**")
            ligue2 = st.selectbox("🏆 Compétition", competitions, key="ligue2_comp")
            df_j2 = df[df['Compétition'] == ligue2]
            joueur2 = st.selectbox("⭐ Joueur", df_j2['Joueur'].sort_values(), key="joueur2_comp")
        
        if joueur1 and joueur2:
            st.markdown(f"<h3 class='subsection-title-enhanced'>⚔️ DUEL ELITE : {joueur1} vs {joueur2}</h3>", unsafe_allow_html=True)
            
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                player1_data = df_j1[df_j1['Joueur'] == joueur1].iloc[0]
                st.markdown(f"""
                <div class='pro-card' style='padding: var(--space-lg); border-left: 4px solid var(--primary);'>
                    <h4 style='color: var(--primary); margin: 0 0 var(--space-md) 0;'>{joueur1}</h4>
                    <p style='margin: 0; color: var(--text-primary);'>🏆 {ligue1} | ⚽ {player1_data['Équipe']} | 📍 {player1_data['Position']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with info_col2:
                player2_data = df_j2[df_j2['Joueur'] == joueur2].iloc[0]
                st.markdown(f"""
                <div class='pro-card' style='padding: var(--space-lg); border-left: 4px solid var(--secondary);'>
                    <h4 style='color: var(--secondary); margin: 0 0 var(--space-md) 0;'>{joueur2}</h4>
                    <p style='margin: 0; color: var(--text-primary);'>🏆 {ligue2} | ⚽ {player2_data['Équipe']} | 📍 {player2_data['Position']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            try:
                values1 = MetricsCalculator.calculate_percentiles(joueur1, df_j1)
                values2 = MetricsCalculator.calculate_percentiles(joueur2, df_j2)
                
                font_normal = FontManager()
                font_bold = FontManager()
                font_italic = FontManager()
                
                baker = PyPizza(
                    params=list(Config.RADAR_METRICS.keys()),
                    background_color="#0A0E17",
                    straight_line_color="#FFFFFF",
                    straight_line_lw=2,
                    last_circle_color="#FFFFFF",
                    last_circle_lw=2,
                    other_circle_ls="-.",
                    other_circle_lw=2
                )
                
                fig, ax = baker.make_pizza(
                    values1,
                    compare_values=values2,
                    figsize=(16, 16),
                    kwargs_slices=dict(
                        facecolor=Config.COLORS['primary'], 
                        edgecolor="#FFFFFF", 
                        linewidth=3, 
                        zorder=2
                    ),
                    kwargs_compare=dict(
                        facecolor=Config.COLORS['secondary'], 
                        edgecolor="#FFFFFF", 
                        linewidth=3, 
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
                            facecolor=Config.COLORS['primary'], 
                            boxstyle="round,pad=0.4", 
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
                            facecolor=Config.COLORS['secondary'], 
                            boxstyle="round,pad=0.4", 
                            lw=2
                        )
                    )
                )
                
                # Titre ultra-professionnel
                fig.text(0.515, 0.97, "DUEL ELITE | Analyse Radar Comparative | Saison 2024-25",
                         size=18, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                
                # Légende ultra-moderne
                legend_p1 = mpatches.Patch(color=Config.COLORS['primary'], label=joueur1)
                legend_p2 = mpatches.Patch(color=Config.COLORS['secondary'], label=joueur2)
                ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.35, 1.0),
                         frameon=False, labelcolor='white', fontsize=14)
                
                # Footer elite
                fig.text(0.99, 0.01, "Football Analytics Pro | Elite Dashboard | FBRef Data",
                         size=11, ha="right", fontproperties=font_italic.prop, color="#8993A4")
                
                st.pyplot(fig, use_container_width=True)
                
                # Analytics comparative ultra-modernes
                st.markdown("---")
                st.markdown("<h3 class='subsection-title-enhanced'>📊 Analytics Comparative Elite</h3>", unsafe_allow_html=True)
                
                comp_col1, comp_col2, comp_col3 = st.columns(3)
                
                with comp_col1:
                    avg1 = np.mean(values1)
                    avg2 = np.mean(values2)
                    winner = joueur1 if avg1 > avg2 else joueur2
                    winner_color = Config.COLORS['primary'] if avg1 > avg2 else Config.COLORS['secondary']
                    st.markdown(f"""
                    <div class='metric-card-enhanced' style='border-color: {winner_color};'>
                        <div class='metric-value-enhanced' style='color: {winner_color};'>{winner}</div>
                        <div class='metric-label-enhanced'>Supériorité Elite Globale</div>
                        <div style='color: var(--text-secondary); font-size: 0.9em; margin-top: 4px;'>{max(avg1, avg2):.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with comp_col2:
                    superior_count = sum(1 for v1, v2 in zip(values1, values2) if v1 > v2)
                    st.metric(f"🎯 {joueur1} supérieur", f"{superior_count}", 
                             f"/ {len(values1)} métriques elite")
                
                with comp_col3:
                    superior_count2 = len(values1) - superior_count
                    st.metric(f"🎯 {joueur2} supérieur", f"{superior_count2}", 
                             f"/ {len(values1)} métriques elite")
                
            except Exception as e:
                st.error(f"Erreur lors de la création du duel elite : {str(e)}")

# ================================================================================================
# APPLICATION PRINCIPALE ULTRA-PROFESSIONNELLE
# ================================================================================================

class FootballDashboard:
    """Classe principale de l'application Dashboard Football Ultra-Pro"""
    
    def __init__(self):
        """Initialisation de l'application elite"""
        self._configure_page()
        self._load_styles()
        self._initialize_session_state()
    
    def _configure_page(self):
        """Configuration de la page Streamlit ultra-professionnelle"""
        st.set_page_config(**Config.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS ultra-professionnels"""
        st.markdown(StyleManager.get_css(), unsafe_allow_html=True)
    
    def _initialize_session_state(self):
        """Initialise les variables de session elite"""
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
        """Méthode principale d'exécution de l'application elite"""
        # Chargement des données avec spinner elite
        with st.spinner("🚀 Chargement de la base de données elite..."):
            df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        # Affichage des statistiques générales ultra-modernes
        self._render_data_overview(df)
        
        # Rendu de l'en-tête ultra-professionnel
        UIComponents.render_header()
        
        # Rendu de la sidebar et récupération des sélections
        selected_competition, selected_player, df_filtered = SidebarManager.render_sidebar(df)
        
        if selected_player:
            # Mise à jour des stats de session elite
            if selected_player not in st.session_state.selected_player_history:
                st.session_state.session_stats['players_viewed'] += 1
                st.session_state.selected_player_history.insert(0, selected_player)
                st.session_state.selected_player_history = st.session_state.selected_player_history[:5]
            
            # Breadcrumbs ultra-modernes
            player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
            UIComponents.render_breadcrumbs(
                selected_competition, 
                player_data['Équipe'], 
                selected_player
            )
            
            # Carte joueur ultra-professionnelle
            UIComponents.render_player_card(player_data, selected_competition)
            
            st.markdown("---")
            
            # Onglets principaux ultra-modernes
            self._render_main_tabs(player_data, selected_competition, selected_player, df)
        
        else:
            self._render_no_player_message()
        
        # Footer ultra-professionnel
        UIComponents.render_footer()
    
    def _render_data_overview(self, df: pd.DataFrame):
        """Aperçu des données ultra-moderne"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "👥 Base Elite", 
                f"{len(df):,}",
                help="Joueurs dans la base de données elite"
            )
        
        with col2:
            st.metric(
                "🏆 Compétitions Elite", 
                f"{df['Compétition'].nunique()}",
                help="Compétitions de niveau elite analysées"
            )
        
        with col3:
            st.metric(
                "⚽ Clubs Elite", 
                f"{df['Équipe'].nunique()}",
                help="Clubs représentés dans l'analyse"
            )
        
        with col4:
            total_minutes = df['Minutes jouées'].sum()
            st.metric(
                "⏱️ Volume Elite", 
                f"{total_minutes:,.0f}min",
                help="Minutes totales analysées"
            )
        
        with col5:
            avg_age = df['Âge'].mean()
            st.metric(
                "📅 Âge Elite Moyen", 
                f"{avg_age:.1f}ans",
                help="Âge moyen des joueurs elite"
            )
    
    def _render_main_tabs(self, player_data: pd.Series, player_competition: str, 
                         selected_player: str, df_full: pd.DataFrame):
        """Rendu des onglets principaux ultra-modernes"""
        # Obtenir les données des autres ligues pour comparaison elite
        df_other_leagues = DataManager.get_other_leagues_data(df_full, player_competition)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 OFFENSIVE ELITE", 
            "🛡️ DÉFENSIVE ELITE", 
            "🎨 TECHNIQUE ELITE",
            "👥 PROFILS ELITE", 
            "🔄 DUEL ELITE"
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
        """Affiche un message ultra-moderne quand aucun joueur n'est sélectionné"""
        st.markdown("""
        <div style='background: var(--gradient-surface); padding: var(--space-3xl); border-radius: var(--radius-xl); 
                    text-align: center; border: 2px solid var(--border-primary); margin: var(--space-2xl) 0;
                    box-shadow: var(--shadow-xl); position: relative; overflow: hidden;'>
            <div style='position: absolute; top: 0; left: 0; right: 0; height: 4px; background: var(--gradient-hero);'></div>
            <h2 style='color: var(--primary); margin-bottom: var(--space-xl); font-size: 2.5em; font-weight: 800;'>
                ⚡ CENTRE DE CONTRÔLE ELITE
            </h2>
            <p style='color: var(--text-primary); font-size: 1.3em; margin-bottom: var(--space-2xl); line-height: 1.6; font-weight: 500;'>
                Configurez les filtres dans le panneau de contrôle pour sélectionner un joueur elite à analyser.
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--space-xl); margin-top: var(--space-2xl);'>
                <div class='metric-card-enhanced' style='padding: var(--space-xl); border: 2px solid var(--primary);'>
                    <div style='font-size: 4em; margin-bottom: var(--space-lg); color: var(--primary);'>🎯</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 var(--space-md) 0; font-size: 1.2em; font-weight: 700;'>Offensive Elite</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 1rem; line-height: 1.4;'>IA avancée, joueurs similaires</p>
                </div>
                <div class='metric-card-enhanced' style='padding: var(--space-xl); border: 2px solid var(--warning);'>
                    <div style='font-size: 4em; margin-bottom: var(--space-lg); color: var(--warning);'>🔄</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 var(--space-md) 0; font-size: 1.2em; font-weight: 700;'>Duel Elite</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 1rem; line-height: 1.4;'>Radars comparatifs, benchmarks</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Historique des joueurs consultés ultra-moderne
        if st.session_state.selected_player_history:
            st.markdown("<h3 class='subsection-title-enhanced'>📚 Historique Elite Récent</h3>", unsafe_allow_html=True)
            
            history_cols = st.columns(min(len(st.session_state.selected_player_history), 5))
            for i, player in enumerate(st.session_state.selected_player_history):
                with history_cols[i]:
                    if st.button(f"🔄 {player}", key=f"history_{i}", use_container_width=True, type="secondary"):
                        st.rerun()
    
    def _render_error_page(self):
        """Affiche la page d'erreur ultra-professionnelle"""
        st.markdown("""
        <div style='background: var(--gradient-surface); padding: var(--space-3xl); border-radius: var(--radius-xl); 
                    text-align: center; border: 2px solid var(--danger); margin: var(--space-2xl) 0;
                    box-shadow: var(--shadow-xl); position: relative; overflow: hidden;'>
            <div style='position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, var(--danger), var(--accent));'></div>
            <h1 style='color: var(--danger); margin-bottom: var(--space-xl); font-size: 3em; font-weight: 900;'>
                ⚠️ ERREUR SYSTÈME ELITE
            </h1>
            <p style='color: var(--text-primary); font-size: 1.3em; margin-bottom: var(--space-2xl); line-height: 1.6; font-weight: 500;'>
                Impossible de charger la base de données elite. Vérifiez que le fichier 'df_BIG2025.csv' est présent dans le répertoire.
            </p>
            <div style='background: var(--bg-elevated); max-width: 700px; margin: var(--space-2xl) auto 0 auto; 
                        padding: var(--space-2xl); border-radius: var(--radius-lg); border: 2px solid var(--border-primary);
                        box-shadow: var(--shadow-lg);'>
                <h3 style='color: var(--secondary); margin-bottom: var(--space-lg); font-size: 1.5em; font-weight: 700;'>
                    📋 Architecture Système Requise :
                </h3>
                <div style='text-align: left; color: var(--text-primary); font-size: 1.1em;'>
                    <div style='padding: var(--space-md) 0; border-bottom: 1px solid var(--border-primary); display: flex; align-items: center;'>
                        <span style='color: var(--primary); margin-right: var(--space-md); font-size: 1.2em;'>📊</span>
                        <strong>df_BIG2025.csv</strong> - Base de données principale des joueurs elite
                    </div>
                    <div style='padding: var(--space-md) 0; border-bottom: 1px solid var(--border-primary); display: flex; align-items: center;'>
                        <span style='color: var(--secondary); margin-right: var(--space-md); font-size: 1.2em;'>📸</span>
                        <strong>images_joueurs/</strong> - Répertoire des photos des joueurs
                    </div>
                    <div style='padding: var(--space-md) 0; display: flex; align-items: center;'>
                        <span style='color: var(--accent); margin-right: var(--space-md); font-size: 1.2em;'>🏟️</span>
                        <strong>*_Logos/</strong> - Répertoires des logos par compétition elite
                    </div>
                </div>
            </div>
            <div style='margin-top: var(--space-2xl);'>
                <button onclick='window.location.reload()' style='
                    background: var(--gradient-primary); color: white; border: none; 
                    padding: var(--space-lg) var(--space-2xl); border-radius: var(--radius-md); 
                    font-size: 1.1em; font-weight: 700; cursor: pointer; 
                    transition: all var(--transition-normal); box-shadow: var(--shadow-md);
                ' onmouseover='this.style.background="var(--gradient-accent)"; this.style.transform="translateY(-2px)"; this.style.boxShadow="var(--shadow-glow)";' 
                  onmouseout='this.style.background="var(--gradient-primary)"; this.style.transform="translateY(0)"; this.style.boxShadow="var(--shadow-md)";'>
                    🔄 RELANCER SYSTÈME ELITE
                </button>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# POINT D'ENTRÉE DE L'APPLICATION ULTRA-PROFESSIONNELLE
# ================================================================================================

def main():
    """Point d'entrée principal de l'application elite"""
    try:
        dashboard = FootballDashboard()
        dashboard.run()
    except Exception as e:
        st.markdown(f"""
        <div style='background: var(--gradient-surface); padding: var(--space-2xl); border-radius: var(--radius-lg); 
                    border: 2px solid var(--danger); margin: var(--space-xl) 0; box-shadow: var(--shadow-lg);'>
            <h2 style='color: var(--danger); margin: 0 0 var(--space-lg) 0; font-weight: 800;'>
                ❌ ERREUR SYSTÈME CRITIQUE
            </h2>
            <p style='color: var(--text-primary); margin: 0; font-size: 1.1em; font-weight: 500;'>
                {str(e)}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Affichage détaillé de l'erreur en mode debug elite
        with st.expander("🔍 Diagnostic Système Elite (Debug)", expanded=False):
            import traceback
            st.code(traceback.format_exc(), language='python')
        
        # Bouton pour relancer l'application elite
        if st.button("🚀 RELANCER DASHBOARD ELITE", type="primary", use_container_width=True):
            st.rerun()

# ================================================================================================
# EXÉCUTION DE L'APPLICATION ELITE
# ================================================================================================

if __name__ == "__main__":
    main() line-height: 1.4;'>Buts, xG, passes décisives, créativité</p>
                </div>
                <div class='metric-card-enhanced' style='padding: var(--space-xl); border: 2px solid var(--accent);'>
                    <div style='font-size: 4em; margin-bottom: var(--space-lg); color: var(--accent);'>🛡️</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 var(--space-md) 0; font-size: 1.2em; font-weight: 700;'>Défensive Elite</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 1rem; line-height: 1.4;'>Tacles, interceptions, duels, récupérations</p>
                </div>
                <div class='metric-card-enhanced' style='padding: var(--space-xl); border: 2px solid var(--secondary);'>
                    <div style='font-size: 4em; margin-bottom: var(--space-lg); color: var(--secondary);'>🎨</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 var(--space-md) 0; font-size: 1.2em; font-weight: 700;'>Technique Elite</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 1rem; line-height: 1.4;'>Passes, dribbles, progression, maîtrise</p>
                </div>
                <div class='metric-card-enhanced' style='padding: var(--space-xl); border: 2px solid var(--success);'>
                    <div style='font-size: 4em; margin-bottom: var(--space-lg); color: var(--success);'>👥</div>
                    <h4 style='color: var(--text-primary); margin: 0 0 var(--space-md) 0; font-size: 1.2em; font-weight: 700;'>Profils Elite</h4>
                    <p style='color: var(--text-secondary); margin: 0; font-size: 1rem;
