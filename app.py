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
# CONFIGURATION ET CONSTANTES - COULEURS AMÉLIORÉES
# ================================================================================================

class Config:
    """Configuration centralisée de l'application avec couleurs améliorées"""
    
    # Configuration de la page Streamlit
    PAGE_CONFIG = {
        "page_title": "Football Analytics Pro",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "expanded"  # Sidebar ouverte par défaut
    }
    
    # Palette de couleurs améliorée pour une meilleure visibilité
    COLORS = {
        'primary': '#3b82f6',      # Blue-500 - Plus vif
        'secondary': '#10b981',    # Emerald-500 - Plus saturé
        'accent': '#f59e0b',       # Amber-500 - Plus visible
        'success': '#22c55e',      # Green-500 - Plus lumineux
        'warning': '#ef4444',      # Red-500 - Plus visible
        'danger': '#dc2626',       # Red-600
        'dark': '#1e293b',         # Slate-800 - Moins sombre
        'light': '#f8fafc',        # Slate-50
        'muted': '#94a3b8',        # Slate-400 - Plus clair
        'text_primary': '#f1f5f9',    # Slate-100 - Très lisible
        'text_secondary': '#cbd5e1',  # Slate-300 - Bien contrasté
        'background': '#0f172a',      # Slate-900 - Background principal
        'surface': '#1e293b',         # Slate-800 - Surfaces
        'gradient': ['#3b82f6', '#10b981', '#f59e0b', '#22c55e', '#ef4444']
    }
    
    # Configuration des radars (identique)
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
    
    # Mapping des dossiers de logos (identique)
    LOGO_FOLDERS = {
        'Bundliga': 'Bundliga_Logos',
        'La Liga': 'La_Liga_Logos',
        'Ligue 1': 'Ligue1_Logos',
        'Premier League': 'Premier_League_Logos',
        'Serie A': 'Serie_A_Logos'
    }
    
    # Métriques pour l'analyse de similarité (identique)
    SIMILARITY_METRICS = [
        'Minutes jouées', 'Buts', 'Passes décisives', 'Tirs', 'Passes clés',
        'Passes tentées', 'Dribbles tentés', 'Dribbles réussis', 'Tacles gagnants',
        'Interceptions', 'Pourcentage de passes réussies', 'Pourcentage de dribbles réussis',
        'Ballons récupérés', 'Passes progressives', 'Courses progressives',
        'Passes dans le dernier tiers', 'Duels aériens gagnés', 'Duels défensifs gagnés',
        'Tirs cadrés', 'Actions menant à un tir'
    ]

# ================================================================================================
# UTILITAIRES (code identique)
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
        """Récupère la valeur marchande exacte depuis les données du joueur"""
        possible_columns = [
            'Valeur marchande', 'Market Value', 'valeur_marchande', 
            'Valeur', 'Value', 'market_value', 'Valeur en €', 'Valeur (€)',
            'Market_Value', 'Valeur_marchande', 'VALEUR_MARCHANDE',
            'Valeur_Marchande', 'MARKET_VALUE', 'MarketValue', 'market_val',
            'val_marchande', 'VM', 'vm', 'valeur_m', 'valeur_marche',
            'Transfer Value', 'transfer_value', 'Prix', 'price', 'Price'
        ]
        
        for col in possible_columns:
            if col in player_data.index and pd.notna(player_data.get(col)):
                value = player_data[col]
                if value != 0 and str(value).lower() not in ['nan', 'null', '', '0', 'none', 'n/a', 'na']:
                    formatted_value = Utils.format_market_value(value)
                    if formatted_value != "N/A":
                        return formatted_value
        
        for col in player_data.index:
            if any(keyword in col.lower() for keyword in ['val', 'market', 'price', 'prix', 'cost', 'worth']):
                if pd.notna(player_data.get(col)):
                    value = player_data[col]
                    if value != 0 and str(value).lower() not in ['nan', 'null', '', '0', 'none', 'n/a', 'na']:
                        formatted_value = Utils.format_market_value(value)
                        if formatted_value != "N/A":
                            return formatted_value
        
        for col in player_data.index:
            if pd.notna(player_data.get(col)):
                try:
                    value = float(player_data[col])
                    if 50_000 <= value <= 200_000_000:
                        formatted_value = Utils.format_market_value(value)
                        if formatted_value != "N/A":
                            return formatted_value
                except (ValueError, TypeError):
                    continue
        
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
# GESTIONNAIRE DE STYLES CSS - VERSION AMÉLIORÉE POUR VISIBILITÉ
# ================================================================================================

class StyleManager:
    """Gestionnaire des styles CSS - Version améliorée avec meilleure visibilité"""
    
    @staticmethod
    def get_css() -> str:
        """Retourne le CSS personnalisé avec meilleure visibilité"""
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* =====================================================================
           TRANSFORMATION STREAMLIT - INTERFACE MODERNE ET LISIBLE
        ===================================================================== */

        /* Supprimer tous les éléments Streamlit non nécessaires */
        #MainMenu, footer, header, .stDeployButton, .stDecoration,
        [data-testid="stHeader"], [data-testid="manage-app-button"],
        .reportview-container .main footer, .reportview-container .main header { 
            display: none !important; 
        }

        /* Container principal */
        .main .block-container {
            padding: 1rem !important;
            max-width: none !important;
        }

        /* Variables de couleurs améliorées pour la visibilité */
        :root {
            --primary: #3b82f6;
            --primary-gradient: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            --secondary: #10b981;
            --secondary-gradient: linear-gradient(135deg, #10b981 0%, #047857 100%);
            --accent: #f59e0b;
            --accent-gradient: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            --surface: rgba(30, 41, 59, 0.95);
            --surface-light: rgba(51, 65, 85, 0.8);
            --glass: rgba(30, 41, 59, 0.85);
            --border: rgba(203, 213, 225, 0.2);
            --border-bright: rgba(203, 213, 225, 0.4);
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --text-accent: #ffffff;
            --shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            --shadow-xl: 0 20px 40px rgba(0, 0, 0, 0.4);
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
        }

        /* Background de l'application - Gradient plus doux */
        .stApp {
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* =====================================================================
           SIDEBAR AMÉLIORÉE
        ===================================================================== */

        /* Sidebar personnalisée */
        section[data-testid="sidebar"] {
            background: var(--glass) !important;
            backdrop-filter: blur(20px) !important;
            border-right: 1px solid var(--border-bright) !important;
        }

        section[data-testid="sidebar"] > div {
            background: transparent !important;
            padding: 1rem !important;
        }

        /* Titre de la sidebar */
        .sidebar-title {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-align: center;
            padding: 1rem;
            border: 1px solid var(--border-bright);
            border-radius: 12px;
            background-color: var(--surface-light);
        }

        /* =====================================================================
           HEADER COMPACT ET VISIBLE
        ===================================================================== */

        .compact-header {
            background: var(--glass);
            backdrop-filter: blur(20px);
            border-bottom: 2px solid var(--border-bright);
            padding: 1rem 2rem;
            margin: -1rem -1rem 1.5rem -1rem;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: var(--shadow);
        }

        .header-container {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-brand {
            display: flex;
            align-items: center;
            gap: 15px;
            color: var(--text-primary);
            font-weight: 800;
            font-size: 1.75rem;
        }

        .header-brand-icon {
            width: 50px;
            height: 50px;
            background: var(--primary-gradient);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
        }

        .header-info {
            color: var(--text-secondary);
            font-size: 0.95rem;
            font-weight: 500;
        }

        /* =====================================================================
           CARTES MODERNES AVEC MEILLEURE VISIBILITÉ
        ===================================================================== */

        .modern-card {
            background: var(--surface);
            backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid var(--border-bright);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            position: relative;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow);
        }

        .modern-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--primary-gradient);
        }

        .modern-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-xl);
            border-color: rgba(59, 130, 246, 0.4);
        }

        /* Player info card avec meilleur contraste */
        .player-info-card {
            background: var(--surface);
            backdrop-filter: blur(20px) saturate(180%);
            border: 2px solid var(--border-bright);
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            box-shadow: var(--shadow-xl);
            position: relative;
            overflow: hidden;
        }
        
        .player-info-card h2 {
            margin: 0 0 1.5rem 0;
            font-size: 2.25rem;
            font-weight: 800;
            color: var(--text-accent);
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        /* =====================================================================
           MÉTRIQUES AVEC CONTRASTE AMÉLIORÉ
        ===================================================================== */

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }

        .metric-card {
            background: var(--surface-light);
            border: 1px solid var(--border-bright);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            position: relative;
            transition: all 0.3s ease;
            cursor: pointer;
            backdrop-filter: blur(10px);
        }

        .metric-card:hover {
            transform: translateY(-3px) scale(1.02);
            border-color: var(--primary);
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            display: block;
            text-shadow: none;
        }

        .metric-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* =====================================================================
           NAVIGATION MODERNE ET VISIBLE
        ===================================================================== */

        .navigation-container {
            background: var(--surface);
            border: 1px solid var(--border-bright);
            border-radius: 16px;
            padding: 1rem;
            margin: 1.5rem 0;
            backdrop-filter: blur(20px);
        }

        /* Amélioration des boutons Streamlit */
        .stButton > button {
            background: var(--surface-light) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-bright) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(10px) !important;
        }

        .stButton > button:hover {
            background: var(--primary) !important;
            border-color: var(--primary) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4) !important;
        }

        .stButton > button[data-baseweb="button"][kind="primary"] {
            background: var(--primary-gradient) !important;
            border-color: var(--primary) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        }

        /* =====================================================================
           TEXTE ET TITRES AVEC MEILLEUR CONTRASTE
        ===================================================================== */

        .section-title {
            color: var(--text-accent);
            font-size: 2rem;
            font-weight: 800;
            text-align: center;
            margin: 2rem 0 1.5rem 0;
            position: relative;
            padding-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 4px;
            background: var(--primary-gradient);
            border-radius: 2px;
        }
        
        .subsection-title {
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.375rem;
            font-weight: 700;
            margin: 1.5rem 0 1rem 0;
            border-left: 4px solid var(--accent);
            padding-left: 1rem;
        }

        /* Breadcrumbs plus visibles */
        .breadcrumbs {
            background: var(--surface-light);
            border: 1px solid var(--border-bright);
            border-radius: 12px;
            padding: 0.75rem 1.25rem;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
            font-weight: 500;
        }
        
        .breadcrumbs .active {
            color: var(--text-accent);
            font-weight: 600;
        }

        /* =====================================================================
           AMÉLIORATIONS STREAMLIT SPÉCIFIQUES
        ===================================================================== */

        /* Selectboxes plus visibles */
        .stSelectbox > div > div {
            background: var(--surface-light) !important;
            border: 1px solid var(--border-bright) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .stSelectbox label {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }

        /* Métriques Streamlit améliorées */
        .stMetric {
            background: var(--surface-light) !important;
            border: 1px solid var(--border-bright) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .stMetric label {
            color: var(--text-secondary) !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        
        .stMetric [data-testid="metric-value"] {
            color: var(--text-accent) !important;
            font-size: 1.75rem !important;
            font-weight: 700 !important;
        }

        /* Sliders plus visibles */
        .stSlider > div > div > div {
            color: var(--text-primary) !important;
        }

        .stSlider label {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }

        /* Info boxes améliorées */
        .stInfo, .stSuccess, .stWarning, .stError {
            border-radius: 12px !important;
            border-left: 4px solid !important;
            backdrop-filter: blur(10px) !important;
        }

        .stInfo {
            background: rgba(59, 130, 246, 0.1) !important;
            border-left-color: var(--primary) !important;
            color: var(--text-primary) !important;
        }

        .stSuccess {
            background: rgba(16, 185, 129, 0.1) !important;
            border-left-color: var(--secondary) !important;
            color: var(--text-primary) !important;
        }

        .stWarning {
            background: rgba(245, 158, 11, 0.1) !important;
            border-left-color: var(--accent) !important;
            color: var(--text-primary) !important;
        }

        /* =====================================================================
           RESPONSIVE AMÉLIORÉ
        ===================================================================== */

        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 0.75rem;
            }
            
            .modern-card {
                padding: 1rem;
                margin: 0.75rem 0;
            }
            
            .compact-header {
                padding: 0.75rem 1rem;
            }

            .header-brand {
                font-size: 1.5rem;
            }
        }

        @media (max-width: 480px) {
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }

        /* =====================================================================
           SCROLLBAR AMÉLIORÉE
        ===================================================================== */

        ::-webkit-scrollbar {
            width: 10px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--primary-gradient);
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary);
        }

        /* =====================================================================
           ANIMATIONS DOUCES
        ===================================================================== */

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

        .fade-in {
            animation: fadeInUp 0.5s ease forwards;
        }
        </style>
        """
    
    @staticmethod
    def get_javascript() -> str:
        """Retourne le JavaScript pour les animations"""
        return """
        <script>
        // JavaScript pour les animations et interactions améliorées
        class EnhancedAnimations {
            constructor() {
                this.init();
            }
            
            init() {
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', () => {
                        this.setupAnimations();
                    });
                } else {
                    this.setupAnimations();
                }
            }
            
            setupAnimations() {
                this.setupScrollAnimations();
                this.setupInteractions();
                console.log('✅ Animations améliorées activées');
            }
            
            setupScrollAnimations() {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('fade-in');
                        }
                    });
                }, { threshold: 0.1 });
                
                const observeElements = () => {
                    document.querySelectorAll('.modern-card, .metric-card, .player-info-card').forEach(el => {
                        if (!el.classList.contains('observed')) {
                            observer.observe(el);
                            el.classList.add('observed');
                        }
                    });
                };
                
                observeElements();
                setInterval(observeElements, 1000);
            }
            
            setupInteractions() {
                // Améliorations des interactions avec les cartes
                document.addEventListener('mouseenter', (e) => {
                    if (e.target.matches('.metric-card')) {
                        e.target.style.transform = 'translateY(-5px) scale(1.05)';
                        e.target.style.boxShadow = '0 15px 30px rgba(59, 130, 246, 0.4)';
                    }
                });
                
                document.addEventListener('mouseleave', (e) => {
                    if (e.target.matches('.metric-card')) {
                        e.target.style.transform = '';
                        e.target.style.boxShadow = '';
                    }
                });
            }
        }

        // Initialiser les animations améliorées
        new EnhancedAnimations();
        </script>
        """

# ================================================================================================
# GESTIONNAIRE DE DONNÉES (identique)
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
# GESTIONNAIRE D'IMAGES (identique)
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
        
        for ext in extensions:
            logo_path = f"{folder}/{team_name}{ext}"
            if os.path.exists(logo_path):
                return logo_path
        
        for ext in extensions:
            pattern = f"{folder}/*{team_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
            clean_team = team_name.replace(" ", "_").replace("'", "").replace("-", "_")
            pattern = f"{folder}/*{clean_team}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
        
        return None

# ================================================================================================
# CALCULATEUR DE MÉTRIQUES (identique)
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
# ANALYSEUR DE JOUEURS SIMILAIRES (identique)
# ================================================================================================

class SimilarPlayerAnalyzer:
    """Analyseur pour trouver des joueurs similaires"""
    
    @staticmethod
    def prepare_similarity_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Prépare les données pour l'analyse de similarité"""
        available_metrics = []
        for metric in Config.SIMILARITY_METRICS:
            if metric in df.columns:
                available_metrics.append(metric)
        
        if not available_metrics:
            st.warning("⚠️ Aucune métrique disponible pour l'analyse de similarité")
            return pd.DataFrame(), []
        
        required_cols = ['Joueur', 'Équipe', 'Compétition', 'Position', 'Âge', 'Valeur marchande']
        similarity_df = df[required_cols + available_metrics].copy()
        
        for col in available_metrics:
            similarity_df[col] = pd.to_numeric(similarity_df[col], errors='coerce').fillna(0)
        
        similarity_df = similarity_df.dropna(subset=['Joueur'])
        similarity_df = similarity_df.drop_duplicates(subset=['Joueur'], keep='first')
        
        return similarity_df, available_metrics
    
    @staticmethod
    def calculate_similarity_simple(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Calcule la similarité sans sklearn"""
        try:
            similarity_df, available_metrics = SimilarPlayerAnalyzer.prepare_similarity_data(df)
            
            if similarity_df.empty or not available_metrics:
                return []
            
            target_data = similarity_df[similarity_df['Joueur'] == target_player]
            if target_data.empty:
                return []
            
            target_values = target_data[available_metrics].iloc[0]
            target_info = target_data.iloc[0]
            
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                return []
            
            metric_ranges = {}
            for metric in available_metrics:
                all_values = similarity_df[metric].astype(float)
                min_val = all_values.min()
                max_val = all_values.max()
                range_val = max_val - min_val
                metric_ranges[metric] = {
                    'min': min_val,
                    'max': max_val,
                    'range': range_val if range_val > 0 else 1
                }
            
            similarities = []
            
            for idx, player_row in other_players.iterrows():
                player_values = player_row[available_metrics]
                
                total_diff = 0
                valid_metrics = 0
                
                for metric in available_metrics:
                    target_val = float(target_values[metric])
                    player_val = float(player_values[metric])
                    
                    metric_range = metric_ranges[metric]
                    if metric_range['range'] > 0:
                        norm_target = (target_val - metric_range['min']) / metric_range['range']
                        norm_player = (player_val - metric_range['min']) / metric_range['range']
                        
                        diff = abs(norm_target - norm_player)
                    else:
                        diff = 0
                    
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
    def calculate_similarity_advanced(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Calcule la similarité avec sklearn"""
        try:
            similarity_df, available_metrics = SimilarPlayerAnalyzer.prepare_similarity_data(df)
            
            if similarity_df.empty or not available_metrics:
                return []
            
            target_data = similarity_df[similarity_df['Joueur'] == target_player]
            if target_data.empty:
                return []
            
            target_values = target_data[available_metrics].values[0]
            target_info = target_data.iloc[0]
            
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                return []
            
            scaler = StandardScaler()
            
            all_data = similarity_df[available_metrics].values
            scaler.fit(all_data)
            
            target_normalized = scaler.transform([target_values])[0]
            others_normalized = scaler.transform(other_players[available_metrics].values)
            
            distances = euclidean_distances([target_normalized], others_normalized)[0]
            
            max_distance = np.max(distances) if len(distances) > 0 else 1
            similarity_scores = 100 * (1 - distances / max_distance) if max_distance > 0 else [100] * len(distances)
            
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
# GESTIONNAIRE DE GRAPHIQUES AVEC COULEURS AMÉLIORÉES
# ================================================================================================

class ChartManager:
    """Gestionnaire centralisé pour les graphiques avec couleurs améliorées"""
    
    @staticmethod
    def create_bar_chart(data: Dict[str, float], title: str, color_palette: List[str]) -> go.Figure:
        """Crée un graphique en barres stylé avec meilleure visibilité"""
        fig = go.Figure(data=[go.Bar(
            x=list(data.keys()),
            y=list(data.values()),
            marker=dict(
                color=color_palette,
                line=dict(color='rgba(30,41,59,0.3)', width=2),
                cornerradius=6
            ),
            text=[f"{v:.1f}" for v in data.values()],
            textposition='outside',
            textfont=dict(color='#f1f5f9', size=14, family='Inter', weight=600)
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
                color='#cbd5e1'
            ),
            yaxis=dict(
                tickfont=dict(color='#cbd5e1', size=12, family='Inter'),
                gridcolor='rgba(203,213,225,0.3)',
                showgrid=True,
                color='#cbd5e1'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', family='Inter'),
            height=400,
            margin=dict(t=60, b=80, l=60, r=60)
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(data: Dict[str, float], title: str) -> go.Figure:
        """Crée un graphique en jauges avec meilleure visibilité"""
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
                            tickcolor='#cbd5e1', 
                            tickfont=dict(size=11, family='Inter', color='#cbd5e1'),
                            ticksuffix='%'
                        ),
                        bar=dict(color=color, thickness=0.8),
                        bgcolor="rgba(30, 41, 59, 0.8)",
                        borderwidth=2,
                        bordercolor="rgba(203,213,225,0.3)",
                        steps=[
                            {'range': [0, 33], 'color': 'rgba(51,65,85,0.5)'},
                            {'range': [33, 66], 'color': 'rgba(71,85,105,0.5)'},
                            {'range': [66, 100], 'color': 'rgba(100,116,139,0.5)'}
                        ],
                        threshold={
                            'line': {'color': "#f1f5f9", 'width': 3},
                            'thickness': 0.75,
                            'value': 80
                        }
                    ),
                    number={
                        'suffix': '%', 
                        'font': {'color': '#f1f5f9', 'size': 16, 'family': 'Inter', 'weight': 700}
                    }
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            height=340,
            title_text=title,
            title_font_color='#f1f5f9',
            title_font_size=18,
            title_font_family='Inter',
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', family='Inter', size=11),
            margin=dict(t=80, b=60, l=40, r=40)
        )
        
        # Mettre à jour la couleur des sous-titres
        for annotation in fig['layout']['annotations']:
            annotation['font']['color'] = '#cbd5e1'
        
        return fig
    
    @staticmethod
    def create_comparison_chart(player_data: Dict[str, float], avg_data: Dict[str, float], 
                              player_name: str, title: str) -> go.Figure:
        """Crée un graphique de comparaison avec meilleure visibilité"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=player_name,
            x=list(player_data.keys()),
            y=list(player_data.values()),
            marker_color=Config.COLORS['primary'],
            marker_line=dict(color='rgba(30,41,59,0.3)', width=2),
            text=[f"{v:.2f}" for v in player_data.values()],
            textposition='outside',
            textfont=dict(size=12, family='Inter', weight=600, color='#f1f5f9')
        ))
        
        fig.add_trace(go.Bar(
            name='Moyenne autres ligues',
            x=list(avg_data.keys()),
            y=list(avg_data.values()),
            marker_color=Config.COLORS['secondary'],
            marker_line=dict(color='rgba(30,41,59,0.3)', width=2),
            text=[f"{v:.2f}" for v in avg_data.values()],
            textposition='outside',
            textfont=dict(size=12, family='Inter', weight=600, color='#f1f5f9')
        ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(color='#f1f5f9', size=18, family='Inter', weight=700),
                x=0.5
            ),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', family='Inter'),
            xaxis=dict(
                tickfont=dict(color='#cbd5e1', size=12),
                showgrid=False,
                color='#cbd5e1'
            ),
            yaxis=dict(
                tickfont=dict(color='#cbd5e1', size=12), 
                gridcolor='rgba(203,213,225,0.3)',
                showgrid=True,
                color='#cbd5e1'
            ),
            height=420,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=12, family='Inter', color='#f1f5f9'),
                bgcolor='rgba(30, 41, 59, 0.8)',
                bordercolor='rgba(203,213,225,0.3)',
                borderwidth=1
            ),
            margin=dict(t=100, b=60, l=60, r=60)
        )
        
        return fig
    
    @staticmethod
    def create_radar_chart(metrics: Dict[str, float], percentiles: List[float], 
                          avg_percentiles: List[float], player_name: str, 
                          comparison_label: str, color: str) -> go.Figure:
        """Crée un radar chart avec meilleure visibilité"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=percentiles,
            theta=list(metrics.keys()),
            fill='toself',
            fillcolor=f'rgba({Utils.hex_to_rgb(color)}, 0.3)',
            line=dict(color=color, width=3),
            marker=dict(color=color, size=8, symbol='circle'),
            name=f"{player_name}",
            hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.0f}<br>Valeur: %{customdata:.2f}<extra></extra>',
            customdata=list(metrics.values())
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=avg_percentiles,
            theta=list(metrics.keys()),
            mode='lines',
            line=dict(color='rgba(148,163,184,0.8)', width=2, dash='dash'),
            name=f'Moyenne {comparison_label}',
            showlegend=True,
            hovertemplate='<b>%{theta}</b><br>Moyenne: %{r:.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='rgba(203,213,225,0.4)',
                    tickcolor='#cbd5e1',
                    tickfont=dict(color='#cbd5e1', size=11, family='Inter'),
                    showticklabels=True,
                    tickmode='linear',
                    tick0=0,
                    dtick=20,
                    ticksuffix='%'
                ),
                angularaxis=dict(
                    gridcolor='rgba(203,213,225,0.4)',
                    tickcolor='#cbd5e1',
                    tickfont=dict(color='#f1f5f9', size=12, family='Inter', weight=600),
                    linecolor='rgba(203,213,225,0.4)'
                ),
                bgcolor='rgba(30, 41, 59, 0.6)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', family='Inter'),
            title=dict(
                text=f"Analyse Radar - {player_name}",
                font=dict(size=18, color='#f1f5f9', family='Inter', weight=700),
                x=0.5,
                y=0.95
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color='#f1f5f9', size=12),
                bgcolor='rgba(30, 41, 59, 0.8)',
                bordercolor='rgba(203,213,225,0.3)',
                borderwidth=1
            ),
            height=500,
            margin=dict(t=80, b=100, l=80, r=80)
        )
        
        return fig
    
    @staticmethod
    def create_histogram_comparison(target_player: str, similar_players: List[Dict], 
                                  df: pd.DataFrame, metric: str) -> go.Figure:
        """Crée un histogramme de comparaison avec meilleure visibilité"""
        
        def find_column_name(metric_name: str, df_columns: List[str]) -> Optional[str]:
            """Trouve le nom exact de la colonne correspondant à la métrique"""
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
            
            if metric_name in df_columns:
                return metric_name
            
            possible_names = column_mappings.get(metric_name, [metric_name])
            for name in possible_names:
                if name in df_columns:
                    return name
            
            for col in df_columns:
                if metric_name.lower() in col.lower() or col.lower() in metric_name.lower():
                    return col
            
            return None
        
        actual_column = find_column_name(metric, df.columns.tolist())
        
        if not actual_column:
            st.error(f"La métrique '{metric}' n'existe pas dans les données")
            return go.Figure()
        
        target_data = df[df['Joueur'] == target_player]
        if target_data.empty:
            st.error(f"Joueur '{target_player}' non trouvé")
            return go.Figure()
        
        target_value = target_data[actual_column].iloc[0]
        if pd.isna(target_value):
            target_value = 0
        
        player_names = [target_player]
        player_values = [float(target_value)]
        player_colors = [Config.COLORS['primary']]
        data_quality = []
        
        if pd.isna(target_data[actual_column].iloc[0]):
            data_quality.append("⚠️ Données manquantes")
        else:
            data_quality.append("✅ Données disponibles")
        
        missing_data_count = 0
        for i, player_info in enumerate(similar_players):
            player_name = player_info['joueur']
            
            player_data_from_df = df[df['Joueur'] == player_name]
            
            if player_data_from_df.empty:
                value = 0
                missing_data_count += 1
                data_quality.append("⚠️ Joueur non trouvé")
            else:
                raw_value = player_data_from_df[actual_column].iloc[0]
                
                if pd.isna(raw_value) or raw_value is None:
                    value = 0
                    missing_data_count += 1
                    data_quality.append("⚠️ Données manquantes")
                else:
                    value = float(raw_value)
                    data_quality.append("✅ Données disponibles")
            
            player_names.append(player_name)
            player_values.append(value)
            
            similarity_score = player_info['similarity_score']
            if similarity_score >= 85:
                color = Config.COLORS['secondary']
            elif similarity_score >= 70:
                color = Config.COLORS['accent']
            else:
                color = Config.COLORS['warning']
            
            player_colors.append(color)
        
        if missing_data_count > len(similar_players) * 0.5:
            st.warning(f"⚠️ Attention: {missing_data_count}/{len(similar_players)} joueurs similaires ont des données manquantes pour '{metric}' (colonne: '{actual_column}')")
        
        fig = go.Figure(data=[go.Bar(
            x=player_names,
            y=player_values,
            marker=dict(
                color=player_colors,
                line=dict(color='rgba(30,41,59,0.4)', width=2),
                opacity=0.9
            ),
            text=[f"{v:.1f}" if v > 0 else "N/A" for v in player_values],
            textposition='outside',
            textfont=dict(color='#f1f5f9', size=14, family='Inter', weight=600),
            hovertemplate='<b>%{x}</b><br>' + f'{metric}: %{{y:.2f}}<br>' + 
                         f'Colonne: {actual_column}<extra></extra>'
        )])
        
        non_zero_values = [v for v in player_values if v > 0]
        if non_zero_values:
            avg_value = np.mean(non_zero_values)
            fig.add_hline(
                y=avg_value,
                line_dash="dash",
                line_color="rgba(148,163,184,0.8)",
                line_width=3,
                annotation_text=f"Moyenne (données valides): {avg_value:.1f}",
                annotation_position="top right",
                annotation_font_color="#cbd5e1",
                annotation_font_size=12
            )
        
        fig.update_layout(
            title=dict(
                text=f"Comparaison: {metric}",
                font=dict(size=20, color='#f1f5f9', family='Inter', weight=700),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                tickfont=dict(color='#cbd5e1', size=12, family='Inter'),
                tickangle=45,
                showgrid=False,
                title=dict(text="Joueurs", font=dict(color='#cbd5e1', size=14, family='Inter')),
                color='#cbd5e1'
            ),
            yaxis=dict(
                tickfont=dict(color='#cbd5e1', size=12, family='Inter'),
                gridcolor='rgba(203,213,225,0.3)',
                showgrid=True,
                title=dict(text=metric, font=dict(color='#cbd5e1', size=14, family='Inter')),
                color='#cbd5e1'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f1f5f9', family='Inter'),
            height=600,
            margin=dict(t=100, b=150, l=80, r=80),
            showlegend=False
        )
        
        return fig

# ================================================================================================
# ANALYSEUR DE PERFORMANCE (identique)
# ================================================================================================

class PerformanceAnalyzer:
    """Analyseur de performance pour différents aspects du jeu"""
    
    @staticmethod
    def analyze_offensive_performance(player_data: pd.Series, df_comparison: pd.DataFrame) -> Dict:
        """Analyse complète de la performance offensive"""
        metrics = MetricsCalculator.calculate_offensive_metrics(player_data)
        
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
# COMPOSANTS UI AMÉLIORÉS
# ================================================================================================

class UIComponents:
    """Composants d'interface utilisateur avec meilleure visibilité"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête compact et moderne"""
        st.markdown("""
        <div class='compact-header fade-in'>
            <div class="header-container">
                <div class="header-brand">
                    <div class="header-brand-icon">⚽</div>
                    <div>
                        <div style="font-size: 1.75rem; font-weight: 800; color: #f1f5f9;">Football Analytics Pro</div>
                        <div class="header-info">Analyse avancée des performances • Saison 2024-25</div>
                    </div>
                </div>
                <div style="color: #94a3b8; font-size: 0.875rem; text-align: right;">
                    <div style="font-weight: 600;">Données: FBRef</div>
                    <div>Mise à jour quotidienne</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_breadcrumbs(competition, team, player):
        """Affiche le fil d'Ariane avec meilleure visibilité"""
        st.markdown(
            f"""
            <div class='breadcrumbs fade-in'>
                <strong style="color: #3b82f6;">{competition}</strong> / 
                <strong style="color: #10b981;">{team}</strong> / 
                <span class='active' style="color: #f1f5f9; font-weight: 700;">{player}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_similar_player_card(player_info: Dict, rank: int):
        """Carte de joueur similaire avec meilleure visibilité"""
        similarity_score = player_info['similarity_score']
        player_data = player_info['data']

        if similarity_score >= 85:
            score_color = "#10b981"
            score_gradient = "linear-gradient(135deg, #10b981 0%, #047857 100%)"
        elif similarity_score >= 70:
            score_color = "#f59e0b"
            score_gradient = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
        else:
            score_color = "#3b82f6"
            score_gradient = "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)"

        valeur_marchande = Utils.get_market_value_safe(player_data)

        logo_path = ImageManager.get_club_logo(player_info['competition'], player_info['equipe'])
        logo_html = ""
        if logo_path and os.path.exists(logo_path):
            try:
                image = Image.open(logo_path)
                logo_base64 = Utils.image_to_base64(image)
                logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="club-logo-small" alt="{player_info["equipe"]}" style="width: 40px; height: 40px; object-fit: contain; border-radius: 8px; background: rgba(203, 213, 225, 0.1); padding: 4px;">'
            except Exception:
                logo_html = '<div style="width: 40px; height: 40px; background: rgba(203, 213, 225, 0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.8em; color: #94a3b8;">🏟️</div>'
        else:
            logo_html = '<div style="width: 40px; height: 40px; background: rgba(203, 213, 225, 0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.8em; color: #94a3b8;">🏟️</div>'

        photo_path = ImageManager.get_player_photo(player_info['joueur'])
        if photo_path and os.path.exists(photo_path):
            image = Image.open(photo_path)
            photo_html = f'<img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" style="width:48px; height:48px; border-radius:50%; object-fit:cover; margin-right:12px; border: 2px solid rgba(203, 213, 225, 0.3);">'
        else:
            photo_html = '<div style="width:48px; height:48px; border-radius:50%; background: rgba(203, 213, 225, 0.1); color: #94a3b8; display:inline-flex; align-items:center; justify-content:center; font-size:1.5em; margin-right:12px; border: 2px solid rgba(203, 213, 225, 0.3);">👤</div>'

        st.markdown(f"""
        <div class='modern-card fade-in' style='background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(203, 213, 225, 0.3);'>
            <div style='position: absolute; top: 1rem; right: 1rem; background: {score_gradient}; color: white; padding: 0.5rem 1rem; border-radius: 12px; font-size: 0.875rem; font-weight: 700; box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                #{rank} • {similarity_score:.1f}% similaire
            </div>
            <div style='display: flex; align-items: center; margin-bottom: 1.5rem; padding-top: 0.5rem;'>
                {photo_html}
                {logo_html}
                <h3 style='color: #f1f5f9; margin: 0; font-size: 1.375rem; font-weight: 700; flex: 1; margin-left: 0.75rem;'>
                    {player_info['joueur']}
                </h3>
            </div>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem;'>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div class='metric-value' style='font-size: 1rem; color: #f1f5f9;'>{player_info['equipe']}</div>
                    <div class='metric-label'>Équipe</div>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div class='metric-value' style='font-size: 1rem; color: #f1f5f9;'>{player_info['position']}</div>
                    <div class='metric-label'>Position</div>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div class='metric-value' style='font-size: 1rem; color: #f1f5f9;'>{player_info['age']}</div>
                    <div class='metric-label'>Âge</div>
                </div>
            </div>
            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;'>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div class='metric-value' style='font-size: 0.9rem; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>{valeur_marchande}</div>
                    <div class='metric-label'>Valeur Marchande</div>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div class='metric-value' style='font-size: 0.9rem; color: #f1f5f9;'>{player_info['competition']}</div>
                    <div class='metric-label'>Compétition</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_player_photo(player_name: str):
        """Affiche la photo du joueur avec meilleure visibilité"""
        photo_path = ImageManager.get_player_photo(player_name)
        
        if photo_path:
            try:
                image = Image.open(photo_path)
                st.markdown(f"""
                <div style='background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(203, 213, 225, 0.3); border-radius: 16px; padding: 1.5rem; height: 320px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3); transition: all 0.3s ease;' class='modern-card fade-in'>
                    <img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 12px; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);">
                </div>
                <p style='text-align: center; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700; margin-top: 1rem; font-size: 0.95rem;'>
                    📸 {player_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_photo_placeholder(player_name)
        else:
            UIComponents._render_photo_placeholder(player_name)
    
    @staticmethod
    def _render_club_logo(team_name: str, competition: str):
        """Affiche le logo du club avec meilleure visibilité"""
        logo_path = ImageManager.get_club_logo(competition, team_name)
        
        if logo_path:
            try:
                image = Image.open(logo_path)
                st.markdown(f"""
                <div style='background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(203, 213, 225, 0.3); border-radius: 16px; padding: 1.5rem; height: 200px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3); transition: all 0.3s ease;' class='modern-card fade-in'>
                    <img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));">
                </div>
                <p style='text-align: center; background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700; margin-top: 1rem; font-size: 0.95rem;'>
                    🏟️ {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_logo_placeholder(team_name)
        else:
            UIComponents._render_logo_placeholder(team_name)
    
    @staticmethod
    def _render_photo_placeholder(player_name: str):
        """Placeholder avec meilleure visibilité pour photo"""
        st.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(203, 213, 225, 0.3); border-radius: 16px; padding: 1.5rem; height: 320px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);' class='modern-card fade-in'>
            <div style='text-align: center; color: #94a3b8;'>
                <div style='font-size: 4rem; margin-bottom: 1rem; opacity: 0.6;'>👤</div>
                <p style='margin: 0; font-size: 0.95rem; color: #cbd5e1; font-weight: 600;'>Photo non disponible</p>
                <p style='font-size: 0.8rem; margin-top: 0.5rem; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 600;'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder(team_name: str):
        """Placeholder avec meilleure visibilité pour logo"""
        st.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(203, 213, 225, 0.3); border-radius: 16px; padding: 1.5rem; height: 200px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);' class='modern-card fade-in'>
            <div style='text-align: center; color: #94a3b8;'>
                <div style='font-size: 3rem; margin-bottom: 1rem; opacity: 0.6;'>🏟️</div>
                <p style='margin: 0; font-size: 0.8rem; color: #cbd5e1; font-weight: 600;'>Logo non disponible</p>
                <p style='font-size: 0.75rem; margin-top: 0.25rem; background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 600;'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """Footer moderne avec meilleure visibilité"""
        st.markdown("""
        <div style='background: rgba(30, 41, 59, 0.95); border-top: 1px solid rgba(203, 213, 225, 0.3); padding: 2rem; text-align: center; margin-top: 3rem; backdrop-filter: blur(20px);' class='fade-in'>
            <h3 style='margin: 0 0 0.5rem 0; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700; font-size: 1.25rem;'>Football Analytics Pro</h3>
            <p style='color: #cbd5e1; margin: 0 0 1rem 0; font-weight: 500;'>Analyse avancée des performances footballistiques</p>
            <p style='margin-top: 1rem; font-size: 0.875rem; color: #94a3b8; font-weight: 500;'>
                Données: FBRef • Design: Professional Dashboard • Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte du joueur avec meilleure lisibilité"""
        valeur_marchande = Utils.get_market_value_safe(player_data)
        
        container = st.container()
        
        with container:
            col1, col2, col3 = st.columns([1, 2.5, 1], gap="large")
            
            with col1:
                UIComponents._render_player_photo(player_data['Joueur'])
            
            with col2:
                st.markdown(f"""
                <div class='player-info-card modern-card fade-in'>
                    <h2 style="color: #f1f5f9; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">{player_data['Joueur']}</h2>
                    <div class='metrics-grid'>
                        <div class='metric-card'>
                            <div class='metric-value'>{player_data['Âge']}</div>
                            <div class='metric-label'>Âge</div>
                        </div>
                        <div class='metric-card'>
                            <div class='metric-value' style='font-size: 1.25rem;'>{player_data['Position']}</div>
                            <div class='metric-label'>Position</div>
                        </div>
                        <div class='metric-card'>
                            <div class='metric-value' style='font-size: 1rem;'>{player_data['Nationalité']}</div>
                            <div class='metric-label'>Nationalité</div>
                        </div>
                        <div class='metric-card'>
                            <div class='metric-value'>{int(player_data['Minutes jouées'])}</div>
                            <div class='metric-label'>Minutes Jouées</div>
                        </div>
                        <div class='metric-card'>
                            <div class='metric-value' style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>{valeur_marchande}</div>
                            <div class='metric-label'>Valeur Marchande</div>
                        </div>
                        <div class='metric-card'>
                            <div class='metric-value' style='font-size: 1rem;'>{player_data['Équipe']}</div>
                            <div class='metric-label'>Équipe</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_photo_placeholder(player_name)
        else:
            UIComponents._render_photo_placeholder(player_name)
    
    @staticmethod
    def _render_club_logo(team_name: str, competition: str):
        """Affiche le logo du club avec meilleure visibilité"""
        logo_path = ImageManager.get_club_logo(competition, team_name)
        
        if logo_path:
            try:
                image = Image.open(logo_path)
                st.markdown(f"""
                <div style='background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(203, 213, 225, 0.3); border-radius: 16px; padding: 1.5rem; height: 200px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3); transition: all 0.3s ease;' class='modern-card fade-in'>
                    <img src="data:image/jpeg;base64,{Utils.image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));">
                </div>
                <p style='text-align: center; background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700; margin-top: 1rem; font-size: 0.95rem;'>
                    🏟️ {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_logo_placeholder(team_name)
        else:
            UIComponents._render_logo_placeholder(team_name)
    
    @staticmethod
    def _render_photo_placeholder(player_name: str):
        """Placeholder avec meilleure visibilité pour photo"""
        st.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(203, 213, 225, 0.3); border-radius: 16px; padding: 1.5rem; height: 320px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);' class='modern-card fade-in'>
            <div style='text-align: center; color: #94a3b8;'>
                <div style='font-size: 4rem; margin-bottom: 1rem; opacity: 0.6;'>👤</div>
                <p style='margin: 0; font-size: 0.95rem; color: #cbd5e1; font-weight: 600;'>Photo non disponible</p>
                <p style='font-size: 0.8rem; margin-top: 0.5rem; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 600;'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder(team_name: str):
        """Placeholder avec meilleure visibilité pour logo"""
        st.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.95); border: 1px solid rgba(203, 213, 225, 0.3); border-radius: 16px; padding: 1.5rem; height: 200px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);' class='modern-card fade-in'>
            <div style='text-align: center; color: #94a3b8;'>
                <div style='font-size: 3rem; margin-bottom: 1rem; opacity: 0.6;'>🏟️</div>
                <p style='margin: 0; font-size: 0.8rem; color: #cbd5e1; font-weight: 600;'>Logo non disponible</p>
                <p style='font-size: 0.75rem; margin-top: 0.25rem; background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 600;'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """Footer moderne avec meilleure visibilité"""
        st.markdown("""
        <div style='background: rgba(30, 41, 59, 0.95); border-top: 1px solid rgba(203, 213, 225, 0.3); padding: 2rem; text-align: center; margin-top: 3rem; backdrop-filter: blur(20px);' class='fade-in'>
            <h3 style='margin: 0 0 0.5rem 0; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: 700; font-size: 1.25rem;'>Football Analytics Pro</h3>
            <p style='color: #cbd5e1; margin: 0 0 1rem 0; font-weight: 500;'>Analyse avancée des performances footballistiques</p>
            <p style='margin-top: 1rem; font-size: 0.875rem; color: #94a3b8; font-weight: 500;'>
                Données: FBRef • Design: Professional Dashboard • Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE SIDEBAR AMÉLIORÉ
# ================================================================================================

class SidebarManager:
    """Gestionnaire amélioré pour la sélection de joueurs dans la sidebar"""
    
    @staticmethod
    def render_player_selector(df: pd.DataFrame) -> Tuple[str, str, pd.DataFrame]:
        """Rendu du sélecteur de joueurs dans la sidebar avec meilleure visibilité"""
        
        with st.sidebar:
            st.markdown("""
            <div class='sidebar-title'>
                🎯 Sélection du Joueur
            </div>
            """, unsafe_allow_html=True)
            
            # Sélection de la compétition
            st.markdown("**🏆 Compétition**")
            competitions = DataManager.get_competitions(df)
            selected_competition = st.selectbox(
                "Choisissez une compétition",
                competitions,
                index=0,
                help="Sélectionnez la compétition pour filtrer les joueurs",
                label_visibility="collapsed"
            )
            
            # Filtrage des données par compétition
            df_filtered = DataManager.filter_by_competition(df, selected_competition)
            
            st.markdown("**👤 Joueur**")
            joueurs = DataManager.get_players(df_filtered)
            
            if joueurs:
                selected_player = st.selectbox(
                    "Choisissez un joueur",
                    joueurs,
                    index=0,
                    help="Sélectionnez le joueur à analyser",
                    label_visibility="collapsed"
                )
            else:
                selected_player = None
                st.error("❌ Aucun joueur disponible")
            
            # Informations sur les données filtrées
            st.markdown("---")
            st.markdown("**📊 Statistiques**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("**Joueurs**", len(df_filtered), help="Nombre total de joueurs dans cette compétition")
            with col2:
                st.metric("**Équipes**", df_filtered['Équipe'].nunique(), help="Nombre d'équipes différentes")
            
            # Filtres avancés
            st.markdown("---")
            with st.expander("⚙️ **Filtres avancés**", expanded=False):
                if not df_filtered.empty:
                    min_minutes = int(df_filtered['Minutes jouées'].min())
                    max_minutes = int(df_filtered['Minutes jouées'].max())
                    
                    min_minutes_filter = st.slider(
                        "**Minutes minimum jouées**",
                        min_value=min_minutes,
                        max_value=max_minutes,
                        value=min_minutes,
                        step=90,
                        help="Filtrer les joueurs ayant joué au minimum ce nombre de minutes"
                    )
                    
                    df_filtered = DataManager.filter_by_minutes(df_filtered, min_minutes_filter)
                    
                    st.info(f"🔍 **{len(df_filtered)}** joueurs correspondent aux critères")
                    
                    if len(df_filtered) > 0:
                        avg_minutes = df_filtered['Minutes jouées'].mean()
                        st.metric("Moyenne minutes", f"{avg_minutes:.0f}")
            
            # Historique et favoris dans la sidebar
            st.markdown("---")
            st.markdown("**📚 Historique récent**")
            
            if 'selected_player_history' in st.session_state and st.session_state.selected_player_history:
                for i, player in enumerate(st.session_state.selected_player_history[:3]):
                    if st.button(f"🔄 {player}", key=f"sidebar_history_{i}", use_container_width=True):
                        # Logic pour rappeler un joueur de l'historique
                        st.success(f"📌 {player} sélectionné")
                        st.rerun()
            else:
                st.info("Aucun joueur consulté récemment")
        
        return selected_competition, selected_player, df_filtered

# ================================================================================================
# GESTIONNAIRE DE NAVIGATION AMÉLIORÉ
# ================================================================================================

class NavigationManager:
    """Gestionnaire de navigation moderne avec meilleure visibilité"""
    
    @staticmethod
    def render_navigation() -> str:
        """Rendu de la navigation avec boutons améliorés"""
        
        # Initialiser la session state pour l'onglet actif
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = "offensive"
        
        st.markdown("""
        <div class='navigation-container fade-in'>
            <h3 style='margin: 0 0 1rem 0; color: #f1f5f9; font-weight: 700; font-size: 1.125rem; text-align: center;'>
                📊 Analyses Disponibles
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Interface avec colonnes pour les boutons
        col1, col2, col3, col4, col5 = st.columns(5, gap="small")
        
        with col1:
            if st.button("🎯 **Offensive**", key="btn_offensive", use_container_width=True, 
                        type="primary" if st.session_state.active_tab == "offensive" else "secondary",
                        help="Analyse des statistiques offensives"):
                st.session_state.active_tab = "offensive"
                st.success("🎯 Analyse offensive activée")
        
        with col2:
            if st.button("🛡️ **Défensive**", key="btn_defensive", use_container_width=True,
                        type="primary" if st.session_state.active_tab == "defensive" else "secondary",
                        help="Analyse des statistiques défensives"):
                st.session_state.active_tab = "defensive"
                st.success("🛡️ Analyse défensive activée")
        
        with col3:
            if st.button("🎨 **Technique**", key="btn_technical", use_container_width=True,
                        type="primary" if st.session_state.active_tab == "technical" else "secondary",
                        help="Analyse des aspects techniques"):
                st.session_state.active_tab = "technical"
                st.success("🎨 Analyse technique activée")
        
        with col4:
            if st.button("👥 **Similaires**", key="btn_similar", use_container_width=True,
                        type="primary" if st.session_state.active_tab == "similar" else "secondary",
                        help="Recherche de profils similaires"):
                st.session_state.active_tab = "similar"
                st.info("👥 Recherche de profils similaires")
        
        with col5:
            if st.button("🔄 **Comparaison**", key="btn_comparison", use_container_width=True,
                        type="primary" if st.session_state.active_tab == "comparison" else "secondary",
                        help="Comparaisons et radars"):
                st.session_state.active_tab = "comparison"
                st.info("🔄 Mode comparaison activé")
        
        return st.session_state.active_tab

# ================================================================================================
# GESTIONNAIRE DE TABS AVEC MEILLEURE VISIBILITÉ
# ================================================================================================

class TabManager:
    """Gestionnaire pour les différents onglets avec contenu inchangé mais meilleure présentation"""
    
    @staticmethod
    def render_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str, player_competition: str):
        """Rendu de l'onglet performance offensive avec meilleure visibilité"""
        st.markdown("<h2 class='section-title'>🎯 Performance Offensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_offensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            
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
            
    @staticmethod
    def _render_comparative_radar(df: pd.DataFrame, competitions: List[str]):
        """Rendu du radar comparatif avec meilleure visibilité"""
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("<h3 class='subsection-title'>⚙️ Configuration de la Comparaison</h3>", unsafe_allow_html=True)
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if joueur1 and joueur2:
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            st.markdown(f"<h3 class='subsection-title'>⚔️ {joueur1} vs {joueur2}</h3>", unsafe_allow_html=True)
            
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                player1_data = df_j1[df_j1['Joueur'] == joueur1].iloc[0]
                st.info(f"🏆 **{ligue1}** | ⚽ **{player1_data['Équipe']}** | 📍 **{player1_data['Position']}**")
            
            with info_col2:
                player2_data = df_j2[df_j2['Joueur'] == joueur2].iloc[0]
                st.info(f"🏆 **{ligue2}** | ⚽ **{player2_data['Équipe']}** | 📍 **{player2_data['Position']}**")
            
            try:
                values1 = MetricsCalculator.calculate_percentiles(joueur1, df_j1)
                values2 = MetricsCalculator.calculate_percentiles(joueur2, df_j2)
                
                font_normal = FontManager()
                font_bold = FontManager()
                font_italic = FontManager()
                
                baker = PyPizza(
                    params=list(Config.RADAR_METRICS.keys()),
                    background_color="#0f172a",
                    straight_line_color="#cbd5e1",
                    straight_line_lw=1,
                    last_circle_color="#cbd5e1",
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
                        edgecolor="#cbd5e1", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_compare=dict(
                        facecolor=Config.COLORS['secondary'], 
                        edgecolor="#cbd5e1", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_params=dict(
                        color="#f1f5f9", 
                        fontsize=13, 
                        fontproperties=font_bold.prop
                    ),
                    kwargs_values=dict(
                        color="#f1f5f9", 
                        fontsize=11, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        bbox=dict(
                            edgecolor="#cbd5e1", 
                            facecolor=Config.COLORS['primary'], 
                            boxstyle="round,pad=0.3", 
                            lw=1.5
                        )
                    ),
                    kwargs_compare_values=dict(
                        color="#f1f5f9", 
                        fontsize=11, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        bbox=dict(
                            edgecolor="#cbd5e1", 
                            facecolor=Config.COLORS['secondary'], 
                            boxstyle="round,pad=0.3", 
                            lw=1.5
                        )
                    )
                )
                
                # Titre unifié
                fig.text(0.515, 0.97, "Analyse Radar Comparative | Percentiles | Saison 2024-25",
                         size=16, ha="center", fontproperties=font_bold.prop, color="#f1f5f9")
                
                # Légende
                legend_p1 = mpatches.Patch(color=Config.COLORS['primary'], label=joueur1)
                legend_p2 = mpatches.Patch(color=Config.COLORS['secondary'], label=joueur2)
                ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0),
                         frameon=False, labelcolor='#f1f5f9')
                
                # Footer
                fig.text(0.99, 0.01, "Football Analytics Pro | Source: FBRef",
                         size=9, ha="right", fontproperties=font_italic.prop, color="#94a3b8")
                
                st.pyplot(fig, use_container_width=True)
                
                # Notification de succès
                st.success("✅ Comparaison radar générée avec succès!")
                
                # Comparaison statistique
                st.markdown("<h3 class='subsection-title'>📊 Comparaison Statistique</h3>", unsafe_allow_html=True)
                
                comp_col1, comp_col2, comp_col3 = st.columns(3)
                
                with comp_col1:
                    avg1 = np.mean(values1)
                    avg2 = np.mean(values2)
                    winner = joueur1 if avg1 > avg2 else joueur2
                    st.metric("**Meilleur Percentile Moyen**", winner, f"{max(avg1, avg2):.1f}%")
                
                with comp_col2:
                    superior_count = sum(1 for v1, v2 in zip(values1, values2) if v1 > v2)
                    st.metric(f"**{joueur1} supérieur sur**", f"{superior_count}", f"/ {len(values1)} métriques")
                
                with comp_col3:
                    superior_count2 = len(values1) - superior_count
                    st.metric(f"**{joueur2} supérieur sur**", f"{superior_count2}", f"/ {len(values1)} métriques")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la création du radar comparatif : {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)

# ================================================================================================
# APPLICATION PRINCIPALE AMÉLIORÉE
# ================================================================================================

class FootballDashboard:
    """Classe principale de l'application Dashboard Football avec interface améliorée"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self._configure_page()
        self._load_styles()
        self._initialize_session_state()
    
    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(**Config.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS et JavaScript améliorés"""
        st.markdown(StyleManager.get_css(), unsafe_allow_html=True)
        st.markdown(StyleManager.get_javascript(), unsafe_allow_html=True)
    
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
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = "offensive"
    
    def run(self):
        """Méthode principale d'exécution de l'application"""
        # Chargement des données
        with st.spinner("⏳ Chargement des données..."):
            df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        # Rendu de l'en-tête compact
        UIComponents.render_header()
        
        # Rendu du sélecteur de joueurs dans la sidebar
        selected_competition, selected_player, df_filtered = SidebarManager.render_player_selector(df)
        
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
            
            # Navigation et contenu des onglets
            active_tab = NavigationManager.render_navigation()
            
            # Affichage du contenu selon l'onglet actif
            self._render_tab_content(active_tab, player_data, selected_competition, selected_player, df)
        
        else:
            self._render_no_player_message()
        
        # Footer
        UIComponents.render_footer()
    
    def _render_tab_content(self, active_tab: str, player_data: pd.Series, 
                           player_competition: str, selected_player: str, df_full: pd.DataFrame):
        """Rendu du contenu des onglets selon l'onglet actif"""
        # Obtenir les données des autres ligues pour comparaison
        df_other_leagues = DataManager.get_other_leagues_data(df_full, player_competition)
        
        if active_tab == "offensive":
            TabManager.render_offensive_tab(player_data, df_other_leagues, selected_player, player_competition)
        elif active_tab == "defensive":
            TabManager.render_defensive_tab(player_data, df_other_leagues, selected_player, player_competition)
        elif active_tab == "technical":
            TabManager.render_technical_tab(player_data, df_other_leagues, selected_player, player_competition)
        elif active_tab == "similar":
            TabManager.render_similar_players_tab(selected_player, df_full)
        elif active_tab == "comparison":
            TabManager.render_comparison_tab(df_full, selected_player)
    
    def _render_no_player_message(self):
        """Affiche un message moderne quand aucun joueur n'est sélectionné"""
        st.markdown("""
        <div class='modern-card' style='text-align: center; padding: 3rem; margin: 2rem 0;'>
            <h2 style='background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1.5rem; font-size: 2.25rem;'>⚠️ Aucun joueur sélectionné</h2>
            <p style='color: #cbd5e1; font-size: 1.25rem; margin-bottom: 2rem; font-weight: 500;'>
                Veuillez sélectionner un joueur dans la <strong>sidebar</strong> pour commencer l'analyse.
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 2rem;'>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🎯</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Analyse Offensive</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Buts, passes décisives, xG</p>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🛡️</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Analyse Défensive</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Tacles, interceptions, duels</p>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🎨</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Analyse Technique</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Passes, dribbles, touches</p>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>👥</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Profils Similaires</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Joueurs au style proche</p>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🔄</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Comparaison</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Radars et benchmarks</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Historique des joueurs consultés
        if st.session_state.selected_player_history:
            st.markdown("""
            <div class='modern-card'>
                <h3 class='subsection-title'>📚 Joueurs récemment consultés</h3>
            </div>
            """, unsafe_allow_html=True)
            
            history_cols = st.columns(min(len(st.session_state.selected_player_history), 5))
            for i, player in enumerate(st.session_state.selected_player_history):
                with history_cols[i]:
                    if st.button(f"🔄 **{player}**", key=f"history_{i}", use_container_width=True, type="secondary"):
                        st.success(f"📌 Chargement de {player}...")
                        st.rerun()
    
    def _render_error_page(self):
        """Affiche la page d'erreur avec meilleure visibilité"""
        st.markdown("""
        <div class='modern-card' style='text-align: center; padding: 3rem; border-color: rgba(239, 68, 68, 0.4); margin: 2rem 0;'>
            <h1 style='background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1.5rem; font-size: 2.5rem;'>⚠️ Erreur de Chargement</h1>
            <p style='color: #f1f5f9; font-size: 1.25rem; margin-bottom: 2rem; font-weight: 500;'>
                Impossible de charger les données. Veuillez vérifier que le fichier <strong>'df_BIG2025.csv'</strong> est présent.
            </p>
            <div style='background: rgba(51, 65, 85, 0.8); max-width: 600px; margin: 2rem auto; 
                        padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(203, 213, 225, 0.3);'>
                <h3 style='background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1rem; font-weight: 700;'>📋 Fichiers requis :</h3>
                <div style='text-align: left; color: #f1f5f9;'>
                    <div style='padding: 0.75rem 0; border-bottom: 1px solid rgba(203, 213, 225, 0.2);'>
                        <strong>df_BIG2025.csv</strong> - Données principales des joueurs
                    </div>
                    <div style='padding: 0.75rem 0; border-bottom: 1px solid rgba(203, 213, 225, 0.2);'>
                        <strong>images_joueurs/</strong> - Dossier des photos des joueurs
                    </div>
                    <div style='padding: 0.75rem 0;'>
                        <strong>*_Logos/</strong> - Dossiers des logos par compétition
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 **Réessayer**", type="primary", use_container_width=True):
                st.success("⏳ Rechargement en cours...")
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
        with st.expander("🔍 **Détails de l'erreur (Debug)**", expanded=False):
            import traceback
            st.code(traceback.format_exc())
        
        # Bouton pour relancer l'application
        if st.button("🔄 **Relancer l'application**", type="primary"):
            st.rerun()

# ================================================================================================
# EXÉCUTION DE L'APPLICATION
# ================================================================================================

if __name__ == "__main__":
    main()
            
            # Métriques avec st.metric dans une carte moderne
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            st.markdown("<h3 class='subsection-title'>📊 Métriques Clés</h3>", unsafe_allow_html=True)
            
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
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            
            # Métriques offensives en jauges
            efficiency_data = {
                'Tirs cadrés': player_data.get('Pourcentage de tirs cadrés', 0),
                'Dribbles réussis': player_data.get('Pourcentage de dribbles réussis', 0),
                'Conversion buts': (player_data.get('Buts', 0) / player_data.get('Tirs', 1) * 100) if player_data.get('Tirs', 0) > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(efficiency_data, "Efficacité Offensive (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Radar
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            st.markdown("<h3 class='subsection-title'>🎯 Analyse Radar</h3>", unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "autres ligues",
                Config.COLORS['primary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Comparaison détaillée
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("<h3 class='subsection-title'>📈 Comparaison Détaillée</h3>", unsafe_allow_html=True)
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "Performance par 90min vs Moyenne des Autres Ligues"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_defensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str, player_competition: str):
        """Rendu de l'onglet performance défensive avec meilleure visibilité"""
        st.markdown("<h2 class='section-title'>🛡️ Performance Défensive</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_defensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            
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
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Métriques défensives
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            st.markdown("<h3 class='subsection-title'>📊 Métriques Défensives</h3>", unsafe_allow_html=True)
            
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
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            
            # Pourcentages défensifs
            success_data = {
                'Duels défensifs': player_data.get('Pourcentage de duels gagnés', 0),
                'Duels aériens': player_data.get('Pourcentage de duels aériens gagnés', 0),
                'Récupérations': min(100, (player_data.get('Ballons récupérés', 0) / max(player_data.get('Minutes jouées', 90), 1) * 90 * 10)) if player_data.get('Ballons récupérés', 0) > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(success_data, "Efficacité Défensive (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Radar défensif
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            st.markdown("<h3 class='subsection-title'>🛡️ Analyse Radar</h3>", unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "autres ligues",
                Config.COLORS['warning']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Comparaison détaillée
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("<h3 class='subsection-title'>📈 Comparaison Détaillée</h3>", unsafe_allow_html=True)
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = ChartManager.create_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "Performance par 90min vs Moyenne des Autres Ligues"
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_technical_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str, player_competition: str):
        """Rendu de l'onglet performance technique avec meilleure visibilité"""
        st.markdown("<h2 class='section-title'>🎨 Performance Technique</h2>", unsafe_allow_html=True)
        
        analysis = PerformanceAnalyzer.analyze_technical_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            
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
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Métriques techniques
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            st.markdown("<h3 class='subsection-title'>📊 Métriques Techniques</h3>", unsafe_allow_html=True)
            
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
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            
            # Pourcentages techniques
            technical_success = {
                'Passes prog.': player_data.get('Pourcentage de passes progressives réussies', player_data.get('Pourcentage de passes réussies', 0)),
                'Courses prog.': min(100, (player_data.get('Courses progressives', player_data.get('Dribbles réussis', 0)) / max(player_data.get('Minutes jouées', 90), 1) * 90 * 10)) if player_data.get('Courses progressives', player_data.get('Dribbles réussis', 0)) > 0 else 0,
                'Touches/90': min(100, (player_data.get('Touches de balle', 0) / max(player_data.get('Minutes jouées', 90), 1) * 90 / 100 * 100)) if player_data.get('Touches de balle', 0) > 0 else 0
            }
            
            fig_gauge = ChartManager.create_gauge_chart(technical_success, "Maîtrise Technique (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Radar technique
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            st.markdown("<h3 class='subsection-title'>🎨 Analyse Radar</h3>", unsafe_allow_html=True)
            
            fig_radar = ChartManager.create_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "autres ligues",
                Config.COLORS['secondary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Comparaison détaillée
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("<h3 class='subsection-title'>📈 Comparaison Détaillée</h3>", unsafe_allow_html=True)
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_similar_players_tab(selected_player: str, df: pd.DataFrame):
        """Rendu de l'onglet joueurs similaires avec meilleure visibilité"""
        st.markdown("<h2 class='section-title'>👥 Profils Similaires</h2>", unsafe_allow_html=True)
        
        # Configuration dans une carte moderne
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("<h3 class='subsection-title'>⚙️ Configuration de l'Analyse</h3>", unsafe_allow_html=True)
            st.info("🎯 **Analyse enrichie** : Utilise 21 métriques couvrant le volume, l'efficacité, la progression, l'aspect physique et la finition pour une similarité plus précise.")
        
        with col2:
            num_similar = st.slider(
                "**Nombre de joueurs similaires :**",
                min_value=1,
                max_value=10,
                value=5,
                help="Choisissez combien de joueurs similaires vous voulez voir"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Message d'information sur sklearn
        if not SKLEARN_AVAILABLE:
            st.info("ℹ️ Analyse de similarité en mode simplifié (scikit-learn non disponible)")
        
        # Détails des métriques utilisées
        with st.expander("📊 **Voir les métriques utilisées pour l'analyse**", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📈 Volume & Base**")
                st.markdown("• Minutes jouées\n• Buts\n• Passes décisives\n• Tirs\n• Passes clés\n• Passes tentées\n• Dribbles tentés")
                
            with col2:
                st.markdown("**🎯 Qualité & Progression**")
                st.markdown("• % Passes réussies\n• % Dribbles réussis\n• Passes progressives\n• Courses progressives\n• Passes dernier tiers\n• Ballons récupérés")
                
            with col3:
                st.markdown("**💪 Physique & Finition**")
                st.markdown("• Duels aériens gagnés\n• Duels défensifs gagnés\n• Tirs cadrés\n• Actions → Tir\n• Tacles gagnants\n• Interceptions")
        
        # Calcul des joueurs similaires avec notification
        with st.spinner("🔍 Recherche de joueurs similaires..."):
            similar_players = SimilarPlayerAnalyzer.calculate_similarity(selected_player, df, num_similar)
            
            # Notification de succès
            if similar_players:
                st.success("✅ Profils similaires trouvés avec succès!")
        
        if not similar_players:
            st.warning("⚠️ Aucun joueur similaire trouvé. Vérifiez que le joueur sélectionné existe dans les données.")
            return
        
        # Affichage des résultats dans une carte moderne
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown(f"<h3 class='subsection-title'>🎯 Top {len(similar_players)} joueurs les plus similaires à {selected_player}</h3>", unsafe_allow_html=True)
        
        # Métriques de résumé
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            avg_similarity = np.mean([p['similarity_score'] for p in similar_players])
            st.metric("**Score de Similarité Moyen**", f"{avg_similarity:.1f}%", 
                     help="Score moyen de similarité des joueurs trouvés")
        
        with metrics_col2:
            best_match = similar_players[0] if similar_players else None
            if best_match:
                st.metric("**Meilleure Correspondance**", best_match['joueur'], 
                         f"{best_match['similarity_score']:.1f}%")
        
        with metrics_col3:
            unique_competitions = len(set(p['competition'] for p in similar_players))
            st.metric("**Compétitions Représentées**", f"{unique_competitions}", 
                     help="Nombre de compétitions différentes")
        
        with metrics_col4:
            high_similarity_count = len([p for p in similar_players if p['similarity_score'] >= 80])
            st.metric("**Similarité Élevée (≥80%)**", f"{high_similarity_count}/{len(similar_players)}", 
                     help="Nombre de joueurs avec une similarité très élevée")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Cartes des joueurs similaires
        cols_per_row = 2
        for i in range(0, len(similar_players), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(similar_players):
                    with col:
                        UIComponents.render_similar_player_card(similar_players[i + j], i + j + 1)
        
        # Section pour les histogrammes de comparaison
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("<h3 class='subsection-title'>📊 Histogrammes de Comparaison</h3>", unsafe_allow_html=True)
        
        # Obtenir TOUTES les métriques numériques disponibles
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
            metric_col1, metric_col2, metric_col3 = st.columns([2, 1, 1])
            
            with metric_col1:
                selected_metric = st.selectbox(
                    f"**📈 Choisissez une métrique pour l'histogramme ({len(available_histogram_metrics)} disponibles) :**",
                    available_histogram_metrics,
                    index=0,
                    help="Sélectionnez n'importe quelle métrique numérique du dataset pour comparer les joueurs"
                )
            
            with metric_col2:
                st.info(f"🎯 **{selected_metric}**")
            
            with metric_col3:
                if selected_metric in df.columns:
                    non_null_count = df[selected_metric].count()
                    total_count = len(df)
                    coverage = (non_null_count / total_count) * 100
                    st.metric("**Couverture données**", f"{coverage:.0f}%", 
                             help=f"{non_null_count}/{total_count} joueurs ont des données pour cette métrique")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Histogramme dans une carte séparée
        if available_histogram_metrics and selected_metric:
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            
            fig_histogram = ChartManager.create_histogram_comparison(
                selected_player, similar_players, df, selected_metric
            )
            st.plotly_chart(fig_histogram, use_container_width=True)
            
            # Informations supplémentaires sur l'histogramme
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
                        
                        st.markdown("**📊 Statistiques de comparaison**")
                        
                        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                        
                        with stats_col1:
                            st.metric(f"**{selected_player}**", f"{target_value:.1f}", 
                                     help=f"Valeur du joueur sélectionné pour {selected_metric}")
                        
                        with stats_col2:
                            st.metric("**Moyenne Similaires**", f"{avg_similar:.1f}",
                                     delta=f"{target_value - avg_similar:.1f}",
                                     help="Moyenne des joueurs similaires")
                        
                        with stats_col3:
                            st.metric("**Maximum**", f"{max_similar:.1f}",
                                     delta=max_player,
                                     help="Valeur maximale parmi les joueurs similaires")
                        
                        with stats_col4:
                            st.metric("**Minimum**", f"{min_similar:.1f}",
                                     delta=min_player,
                                     help="Valeur minimale parmi les joueurs similaires")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.warning("⚠️ Aucune métrique numérique disponible pour les histogrammes de comparaison")
    
    @staticmethod
    def render_comparison_tab(df: pd.DataFrame, selected_player: str):
        """Rendu de l'onglet comparaison avec meilleure visibilité"""
        st.markdown("<h2 class='section-title'>🔄 Comparaison Pizza Chart</h2>", unsafe_allow_html=True)
        
        # Mode de visualisation dans une carte moderne
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        
        mode = st.radio(
            "**Mode de visualisation**",
            ["Radar individuel", "Radar comparatif"],
            horizontal=True,
            help="Choisissez le type d'analyse radar à afficher"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        competitions = sorted(df['Compétition'].dropna().unique())
        
        if mode == "Radar individuel":
            TabManager._render_individual_radar(df, selected_player, competitions)
        else:
            TabManager._render_comparative_radar(df, competitions)
    
    @staticmethod
    def _render_individual_radar(df: pd.DataFrame, selected_player: str, competitions: List[str]):
        """Rendu du radar individuel avec meilleure visibilité"""
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown(f"<h3 class='subsection-title'>🎯 Radar individuel : {selected_player}</h3>", unsafe_allow_html=True)
        
        try:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                competition = st.selectbox(
                    "**Compétition de référence**", 
                    competitions,
                    help="Sélectionnez la compétition pour le calcul des percentiles"
                )
            
            with col2:
                st.info(f"📊 Analyse basée sur **{competition}**")
            
            df_comp = df[df['Compétition'] == competition]
            
            values = MetricsCalculator.calculate_percentiles(selected_player, df_comp)
            
            font_normal = FontManager()
            font_bold = FontManager()
            font_italic = FontManager()
            
            baker = PyPizza(
                params=list(Config.RADAR_METRICS.keys()),
                background_color="#0f172a",
                straight_line_color="#cbd5e1",
                straight_line_lw=1,
                last_circle_color="#cbd5e1",
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
                value_colors=["#f1f5f9"] * len(values),
                value_bck_colors=[Config.COLORS['primary']] * len(values),
                kwargs_slices=dict(edgecolor="#cbd5e1", zorder=2, linewidth=2),
                kwargs_params=dict(color="#f1f5f9", fontsize=13, fontproperties=font_bold.prop),
                kwargs_values=dict(
                    color="#f1f5f9", 
                    fontsize=11, 
                    fontproperties=font_normal.prop,
                    bbox=dict(
                        edgecolor="#cbd5e1", 
                        facecolor=Config.COLORS['primary'], 
                        boxstyle="round,pad=0.3", 
                        lw=1.5
                    )
                )
            )
            
            # Titre unifié
            fig.text(0.515, 0.97, selected_player, size=28, ha="center", 
                    fontproperties=font_bold.prop, color="#f1f5f9", weight='bold')
            fig.text(0.515, 0.94, f"Analyse Radar Individuelle | Percentiles vs {competition} | Saison 2024-25", 
                    size=14, ha="center", fontproperties=font_bold.prop, color="#cbd5e1")
            
            fig.text(0.99, 0.01, "Football Analytics Pro | Données: FBRef", 
                    size=9, ha="right", fontproperties=font_italic.prop, color="#94a3b8")
            
            st.pyplot(fig, use_container_width=True)
            
            # Statistiques du radar
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                avg_percentile = np.mean(values)
                st.metric("**Percentile Moyen**", f"{avg_percentile:.1f}%")
            
            with stats_col2:
                max_stat = max(values)
                max_index = values.index(max_stat)
                max_param = list(Config.RADAR_METRICS.keys())[max_index]
                st.metric("**Point Fort**", f"{max_param.replace('\\n', ' ')}", f"{max_stat}%")
            
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
                    st.metric("**Axe d'Amélioration**", f"{min_param.replace('\\n', ' ')}", f"{min_stat}%")
                else:
                    st.metric("**Axe d'Amélioration**", "Excellent partout", "✨")
            
        except Exception as e:
            st.error(f"❌ Erreur lors de la création du radar individuel : {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_comparative_radar(df: pd.DataFrame, competitions: List[str]):
        """Rendu du radar comparatif avec meilleure visibilité"""
        st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
        st.markdown("<h3 class='subsection-title'>⚙️ Configuration de la Comparaison</h3>", unsafe_allow_html=True)
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if joueur1 and joueur2:
            st.markdown('<div class="modern-card fade-in">', unsafe_allow_html=True)
            st.markdown(f"<h3 class='subsection-title'>⚔️ {joueur1} vs {joueur2}</h3>", unsafe_allow_html=True)
            
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                player1_data = df_j1[df_j1['Joueur'] == joueur1].iloc[0]
                st.info(f"🏆 **{ligue1}** | ⚽ **{player1_data['Équipe']}** | 📍 **{player1_data['Position']}**")
            
            with info_col2:
                player2_data = df_j2[df_j2['Joueur'] == joueur2].iloc[0]
                st.info(f"🏆 **{ligue2}** | ⚽ **{player2_data['Équipe']}** | 📍 **{player2_data['Position']}**")
            
            try:
                values1 = MetricsCalculator.calculate_percentiles(joueur1, df_j1)
                values2 = MetricsCalculator.calculate_percentiles(joueur2, df_j2)
                
                font_normal = FontManager()
                font_bold = FontManager()
                font_italic = FontManager()
                
                baker = PyPizza(
                    params=list(Config.RADAR_METRICS.keys()),
                    background_color="#0f172a",
                    straight_line_color="#cbd5e1",
                    straight_line_lw=1,
                    last_circle_color="#cbd5e1",
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
                        edgecolor="#cbd5e1", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_compare=dict(
                        facecolor=Config.COLORS['secondary'], 
                        edgecolor="#cbd5e1", 
                        linewidth=2, 
                        zorder=2
                    ),
                    kwargs_params=dict(
                        color="#f1f5f9", 
                        fontsize=13, 
                        fontproperties=font_bold.prop
                    ),
                    kwargs_values=dict(
                        color="#f1f5f9", 
                        fontsize=11, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        bbox=dict(
                            edgecolor="#cbd5e1", 
                            facecolor=Config.COLORS['primary'], 
                            boxstyle="round,pad=0.3", 
                            lw=1.5
                        )
                    ),
                    kwargs_compare_values=dict(
                        color="#f1f5f9", 
                        fontsize=11, 
                        fontproperties=font_normal.prop, 
                        zorder=3,
                        bbox=dict(
                            edgecolor="#cbd5e1", 
                            facecolor=Config.COLORS['secondary'], 
                            boxstyle="round,pad=0.3", 
                            lw=1.5
                        )
                    )
                )
                
                # Titre unifié
                fig.text(0.515, 0.97, "Analyse Radar Comparative | Percentiles | Saison 2024-25",
                         size=16, ha="center", fontproperties=font_bold.prop, color="#f1f5f9")
                
                # Légende
                legend_p1 = mpatches.Patch(color=Config.COLORS['primary'], label=joueur1)
                legend_p2 = mpatches.Patch(color=Config.COLORS['secondary'], label=joueur2)
                ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0),
                         frameon=False, labelcolor='#f1f5f9')
                
                # Footer
                fig.text(0.99, 0.01, "Football Analytics Pro | Source: FBRef",
                         size=9, ha="right", fontproperties=font_italic.prop, color="#94a3b8")
                
                st.pyplot(fig, use_container_width=True)
                
                # Notification de succès
                st.success("✅ Comparaison radar générée avec succès!")
                
                # Comparaison statistique
                st.markdown("<h3 class='subsection-title'>📊 Comparaison Statistique</h3>", unsafe_allow_html=True)
                
                comp_col1, comp_col2, comp_col3 = st.columns(3)
                
                with comp_col1:
                    avg1 = np.mean(values1)
                    avg2 = np.mean(values2)
                    winner = joueur1 if avg1 > avg2 else joueur2
                    st.metric("**Meilleur Percentile Moyen**", winner, f"{max(avg1, avg2):.1f}%")
                
                with comp_col2:
                    superior_count = sum(1 for v1, v2 in zip(values1, values2) if v1 > v2)
                    st.metric(f"**{joueur1} supérieur sur**", f"{superior_count}", f"/ {len(values1)} métriques")
                
                with comp_col3:
                    superior_count2 = len(values1) - superior_count
                    st.metric(f"**{joueur2} supérieur sur**", f"{superior_count2}", f"/ {len(values1)} métriques")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la création du radar comparatif : {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)

# ================================================================================================
# APPLICATION PRINCIPALE AMÉLIORÉE
# ================================================================================================

class FootballDashboard:
    """Classe principale de l'application Dashboard Football avec interface améliorée"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self._configure_page()
        self._load_styles()
        self._initialize_session_state()
    
    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(**Config.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS et JavaScript améliorés"""
        st.markdown(StyleManager.get_css(), unsafe_allow_html=True)
        st.markdown(StyleManager.get_javascript(), unsafe_allow_html=True)
    
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
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = "offensive"
    
    def run(self):
        """Méthode principale d'exécution de l'application"""
        # Chargement des données
        with st.spinner("⏳ Chargement des données..."):
            df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        # Rendu de l'en-tête compact
        UIComponents.render_header()
        
        # Rendu du sélecteur de joueurs dans la sidebar
        selected_competition, selected_player, df_filtered = SidebarManager.render_player_selector(df)
        
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
            
            # Navigation et contenu des onglets
            active_tab = NavigationManager.render_navigation()
            
            # Affichage du contenu selon l'onglet actif
            self._render_tab_content(active_tab, player_data, selected_competition, selected_player, df)
        
        else:
            self._render_no_player_message()
        
        # Footer
        UIComponents.render_footer()
    
    def _render_tab_content(self, active_tab: str, player_data: pd.Series, 
                           player_competition: str, selected_player: str, df_full: pd.DataFrame):
        """Rendu du contenu des onglets selon l'onglet actif"""
        # Obtenir les données des autres ligues pour comparaison
        df_other_leagues = DataManager.get_other_leagues_data(df_full, player_competition)
        
        if active_tab == "offensive":
            TabManager.render_offensive_tab(player_data, df_other_leagues, selected_player, player_competition)
        elif active_tab == "defensive":
            TabManager.render_defensive_tab(player_data, df_other_leagues, selected_player, player_competition)
        elif active_tab == "technical":
            TabManager.render_technical_tab(player_data, df_other_leagues, selected_player, player_competition)
        elif active_tab == "similar":
            TabManager.render_similar_players_tab(selected_player, df_full)
        elif active_tab == "comparison":
            TabManager.render_comparison_tab(df_full, selected_player)
    
    def _render_no_player_message(self):
        """Affiche un message moderne quand aucun joueur n'est sélectionné"""
        st.markdown("""
        <div class='modern-card' style='text-align: center; padding: 3rem; margin: 2rem 0;'>
            <h2 style='background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1.5rem; font-size: 2.25rem;'>⚠️ Aucun joueur sélectionné</h2>
            <p style='color: #cbd5e1; font-size: 1.25rem; margin-bottom: 2rem; font-weight: 500;'>
                Veuillez sélectionner un joueur dans la <strong>sidebar</strong> pour commencer l'analyse.
            </p>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 2rem;'>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🎯</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Analyse Offensive</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Buts, passes décisives, xG</p>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🛡️</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Analyse Défensive</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Tacles, interceptions, duels</p>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🎨</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Analyse Technique</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Passes, dribbles, touches</p>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>👥</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Profils Similaires</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Joueurs au style proche</p>
                </div>
                <div class='metric-card' style='background: rgba(51, 65, 85, 0.8);'>
                    <div style='font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🔄</div>
                    <h4 style='color: #f1f5f9; margin: 0 0 0.5rem 0; font-weight: 700;'>Comparaison</h4>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.875rem;'>Radars et benchmarks</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Historique des joueurs consultés
        if st.session_state.selected_player_history:
            st.markdown("""
            <div class='modern-card'>
                <h3 class='subsection-title'>📚 Joueurs récemment consultés</h3>
            </div>
            """, unsafe_allow_html=True)
            
            history_cols = st.columns(min(len(st.session_state.selected_player_history), 5))
            for i, player in enumerate(st.session_state.selected_player_history):
                with history_cols[i]:
                    if st.button(f"🔄 **{player}**", key=f"history_{i}", use_container_width=True, type="secondary"):
                        st.success(f"📌 Chargement de {player}...")
                        st.rerun()
    
    def _render_error_page(self):
        """Affiche la page d'erreur avec meilleure visibilité"""
        st.markdown("""
        <div class='modern-card' style='text-align: center; padding: 3rem; border-color: rgba(239, 68, 68, 0.4); margin: 2rem 0;'>
            <h1 style='background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1.5rem; font-size: 2.5rem;'>⚠️ Erreur de Chargement</h1>
            <p style='color: #f1f5f9; font-size: 1.25rem; margin-bottom: 2rem; font-weight: 500;'>
                Impossible de charger les données. Veuillez vérifier que le fichier <strong>'df_BIG2025.csv'</strong> est présent.
            </p>
            <div style='background: rgba(51, 65, 85, 0.8); max-width: 600px; margin: 2rem auto; 
                        padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(203, 213, 225, 0.3);'>
                <h3 style='background: linear-gradient(135deg, #10b981 0%, #047857 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 1rem; font-weight: 700;'>📋 Fichiers requis :</h3>
                <div style='text-align: left; color: #f1f5f9;'>
                    <div style='padding: 0.75rem 0; border-bottom: 1px solid rgba(203, 213, 225, 0.2);'>
                        <strong>df_BIG2025.csv</strong> - Données principales des joueurs
                    </div>
                    <div style='padding: 0.75rem 0; border-bottom: 1px solid rgba(203, 213, 225, 0.2);'>
                        <strong>images_joueurs/</strong> - Dossier des photos des joueurs
                    </div>
                    <div style='padding: 0.75rem 0;'>
                        <strong>*_Logos/</strong> - Dossiers des logos par compétition
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 **Réessayer**", type="primary", use_container_width=True):
                st.success("⏳ Rechargement en cours...")
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
        with st.expander("🔍 **Détails de l'erreur (Debug)**", expanded=False):
            import traceback
            st.code(traceback.format_exc())
        
        # Bouton pour relancer l'application
        if st.button("🔄 **Relancer l'application**", type="primary"):
            st.rerun()

# ================================================================================================
# EXÉCUTION DE L'APPLICATION
# ================================================================================================

if __name__ == "__main__":
    main()
