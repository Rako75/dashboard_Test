# ================================================================================================
# FOOTBALL DASHBOARD PRO - VERSION RESTRUCTURÉE
# ================================================================================================

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
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Imports optionnels pour l'analyse de similarité
try:
    from mplsoccer import PyPizza, FontManager
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import euclidean_distances
    SKLEARN_AVAILABLE = True
    MPLSOCCER_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    MPLSOCCER_AVAILABLE = False

# ================================================================================================
# CONFIGURATION
# ================================================================================================

@dataclass
class AppConfig:
    """Configuration de l'application"""
    
    # Configuration Streamlit
    PAGE_TITLE: str = "Dashboard Football Pro"
    PAGE_ICON: str = "⚽"
    LAYOUT: str = "wide"
    
    # Couleurs
    PRIMARY_COLOR: str = "#1f77b4"
    SECONDARY_COLOR: str = "#2ca02c"
    ACCENT_COLOR: str = "#ff7f0e"
    SUCCESS_COLOR: str = "#17a2b8"
    WARNING_COLOR: str = "#ffc107"
    DANGER_COLOR: str = "#dc3545"
    
    # Chemins
    DATA_FILE: str = "df_BIG2025.csv"
    IMAGES_FOLDER: str = "images_joueurs"
    
    # Mapping des positions
    POSITION_MAPPING: Dict[str, str] = None
    
    # Métriques radar
    RADAR_METRICS: Dict[str, str] = None
    
    # Dossiers logos
    LOGO_FOLDERS: Dict[str, str] = None
    
    def __post_init__(self):
        """Initialisation post-création"""
        if self.POSITION_MAPPING is None:
            self.POSITION_MAPPING = {
                'GK': 'Gardien',
                'DF': 'Défenseur', 
                'MF': 'Milieu',
                'FW': 'Attaquant'
            }
        
        if self.RADAR_METRICS is None:
            self.RADAR_METRICS = {
                "Buts\nsans pénalty": "Buts (sans penalty)",
                "Passes déc.": "Passes décisives", 
                "Buts +\nPasses déc.": "Buts + Passes D",
                "Cartons\njaunes": "Cartons jaunes",
                "Cartons\nrouges": "Cartons rouges",
                "Passes\ntentées": "Passes tentées",
                "Passes\nclés": "Passes clés",
                "Passes\nprogressives": "Passes progressives",
                "Dribbles\ntentés": "Dribbles tentés",
                "Dribbles\nréussis": "Dribbles réussis",
                "Tacles\ngagnants": "Tacles gagnants",
                "Interceptions": "Interceptions",
                "Dégagements": "Dégagements"
            }
        
        if self.LOGO_FOLDERS is None:
            self.LOGO_FOLDERS = {
                'Bundliga': 'Bundliga_Logos',
                'La Liga': 'La_Liga_Logos',
                'Ligue 1': 'Ligue1_Logos',
                'Premier League': 'Premier_League_Logos',
                'Serie A': 'Serie_A_Logos'
            }

config = AppConfig()

# ================================================================================================
# GESTIONNAIRE DE STYLES
# ================================================================================================

class StyleManager:
    """Gestionnaire des styles CSS"""
    
    @staticmethod
    def get_main_styles() -> str:
        """Retourne les styles CSS principaux"""
        return f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        :root {{
            --primary-color: {config.PRIMARY_COLOR};
            --secondary-color: {config.SECONDARY_COLOR};
            --accent-color: {config.ACCENT_COLOR};
            --background-dark: #0e1117;
            --background-card: #1a1d23;
            --background-surface: #262730;
            --text-primary: #ffffff;
            --text-secondary: #e2e8f0;
            --text-muted: #a0aec0;
            --border-color: #4a5568;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            --radius-md: 12px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
        }}
        
        .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, var(--background-dark) 0%, #1a1d23 100%);
            color: var(--text-primary);
        }}
        
        .main .block-container {{
            padding-top: var(--spacing-lg);
            max-width: 1400px;
        }}
        
        .metric-card {{
            background: var(--background-surface);
            padding: var(--spacing-md);
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .metric-card:hover {{
            border-color: var(--primary-color);
            box-shadow: 0 8px 25px rgba(31, 119, 180, 0.3);
            transform: translateY(-3px);
        }}
        
        .metric-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 8px;
        }}
        
        .metric-label {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
        }}
        
        .player-card {{
            background: var(--background-card);
            padding: var(--spacing-lg);
            border-radius: var(--radius-md);
            border: 2px solid var(--border-color);
            box-shadow: var(--shadow);
            text-align: center;
            position: relative;
        }}
        
        .section-title {{
            color: var(--text-primary);
            font-size: 1.5rem;
            font-weight: 700;
            margin: var(--spacing-lg) 0 var(--spacing-md) 0;
            text-align: center;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            background: var(--background-card);
            border-radius: var(--radius-md);
            padding: 8px;
            margin-bottom: var(--spacing-lg);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            color: var(--text-secondary);
            border-radius: 8px;
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: var(--primary-color);
            color: white;
            font-weight: 600;
        }}
        </style>
        """

# ================================================================================================
# GESTIONNAIRE DE DONNÉES
# ================================================================================================

class DataManager:
    """Gestionnaire centralisé pour les données"""
    
    def __init__(self):
        self._data = None
        self._load_data()
    
    @st.cache_data
    def _load_data(_self) -> Optional[pd.DataFrame]:
        """Charge les données depuis le fichier CSV"""
        try:
            df = pd.read_csv(config.DATA_FILE, encoding='utf-8', delimiter=';')
            # Mapper les positions
            if 'Position' in df.columns:
                df['Position'] = df['Position'].map(config.POSITION_MAPPING).fillna(df['Position'])
            return df
        except FileNotFoundError:
            st.error(f"❌ Fichier '{config.DATA_FILE}' non trouvé.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement : {str(e)}")
            return None
    
    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Retourne les données"""
        return self._data
    
    def get_competitions(self) -> List[str]:
        """Récupère la liste des compétitions"""
        if self._data is None:
            return []
        return sorted(self._data['Compétition'].dropna().unique())
    
    def get_clubs(self, competition: str = None) -> List[str]:
        """Récupère la liste des clubs"""
        if self._data is None:
            return []
        df = self._data
        if competition:
            df = df[df['Compétition'] == competition]
        return sorted(df['Équipe'].dropna().unique())
    
    def get_positions(self) -> List[str]:
        """Récupère la liste des positions"""
        if self._data is None:
            return []
        return sorted(self._data['Position'].dropna().unique())
    
    def get_players(self, competition: str = None, club: str = None, position: str = None) -> List[str]:
        """Récupère la liste des joueurs avec filtres"""
        if self._data is None:
            return []
        
        df = self._data
        if competition:
            df = df[df['Compétition'] == competition]
        if club:
            df = df[df['Équipe'] == club]
        if position:
            df = df[df['Position'] == position]
        
        return sorted(df['Joueur'].dropna().unique())
    
    def get_player_data(self, player_name: str) -> Optional[pd.Series]:
        """Récupère les données d'un joueur"""
        if self._data is None:
            return None
        
        player_data = self._data[self._data['Joueur'] == player_name]
        if player_data.empty:
            return None
        
        return player_data.iloc[0]
    
    def filter_data(self, **filters) -> pd.DataFrame:
        """Filtre les données selon les critères fournis"""
        if self._data is None:
            return pd.DataFrame()
        
        df = self._data.copy()
        
        for key, value in filters.items():
            if value and key in df.columns:
                df = df[df[key] == value]
        
        return df

# ================================================================================================
# GESTIONNAIRE D'IMAGES
# ================================================================================================

class ImageManager:
    """Gestionnaire pour les images et logos"""
    
    @staticmethod
    def get_player_photo(player_name: str) -> Optional[str]:
        """Récupère le chemin de la photo du joueur"""
        extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
        
        for ext in extensions:
            photo_path = f"{config.IMAGES_FOLDER}/{player_name}{ext}"
            if os.path.exists(photo_path):
                return photo_path
        
        # Recherche avec patterns
        for ext in extensions:
            pattern = f"{config.IMAGES_FOLDER}/*{player_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
        
        return None
    
    @staticmethod
    def get_club_logo(competition: str, team_name: str) -> Optional[str]:
        """Récupère le chemin du logo du club"""
        folder = config.LOGO_FOLDERS.get(competition)
        if not folder:
            return None
        
        extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
        
        for ext in extensions:
            logo_path = f"{folder}/{team_name}{ext}"
            if os.path.exists(logo_path):
                return logo_path
        
        return None
    
    @staticmethod
    def image_to_base64(image_path: str) -> Optional[str]:
        """Convertit une image en base64"""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            return None

# ================================================================================================
# CALCULATEUR DE MÉTRIQUES
# ================================================================================================

class MetricsCalculator:
    """Calculateur de métriques de performance"""
    
    @staticmethod
    def format_market_value(value: Union[str, int, float]) -> str:
        """Formate une valeur marchande"""
        if pd.isna(value) or value is None:
            return "N/A"
        
        try:
            if isinstance(value, str):
                # Nettoyer la chaîne
                clean_value = value.replace('€', '').replace('M', '').replace('K', '').replace(',', '').strip()
                if 'M' in value.upper():
                    value = float(clean_value) * 1_000_000
                elif 'K' in value.upper():
                    value = float(clean_value) * 1_000
                else:
                    value = float(clean_value)
            else:
                value = float(value)
            
            if value >= 1_000_000:
                return f"{value/1_000_000:.1f}M€"
            elif value >= 1_000:
                return f"{value/1_000:.1f}K€"
            else:
                return f"{value:.0f}€"
        except:
            return "N/A"
    
    @staticmethod
    def calculate_offensive_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques offensives"""
        minutes_90 = player_data.get('Minutes jouées', 0) / 90 if player_data.get('Minutes jouées', 0) > 0 else 1
        
        return {
            'Buts/90': player_data.get('Buts', 0) / minutes_90,
            'Passes D./90': player_data.get('Passes décisives', 0) / minutes_90,
            'Tirs/90': player_data.get('Tirs', 0) / minutes_90,
            'Passes clés/90': player_data.get('Passes clés', 0) / minutes_90,
            'Dribbles/90': player_data.get('Dribbles réussis', 0) / minutes_90,
            '% Passes réussies': player_data.get('Pourcentage de passes réussies', 0)
        }
    
    @staticmethod
    def calculate_defensive_metrics(player_data: pd.Series) -> Dict[str, float]:
        """Calcule les métriques défensives"""
        minutes_90 = player_data.get('Minutes jouées', 0) / 90 if player_data.get('Minutes jouées', 0) > 0 else 1
        
        return {
            'Tacles/90': player_data.get('Tacles gagnants', 0) / minutes_90,
            'Interceptions/90': player_data.get('Interceptions', 0) / minutes_90,
            'Duels gagnés/90': player_data.get('Duels défensifs gagnés', 0) / minutes_90,
            'Dégagements/90': player_data.get('Dégagements', 0) / minutes_90,
            '% Duels gagnés': player_data.get('Pourcentage de duels gagnés', 0)
        }
    
    @staticmethod
    def calculate_percentiles(player_name: str, df: pd.DataFrame) -> List[int]:
        """Calcule les percentiles pour le radar chart"""
        if df.empty:
            return [0] * len(config.RADAR_METRICS)
        
        player_data = df[df["Joueur"] == player_name]
        if player_data.empty:
            return [0] * len(config.RADAR_METRICS)
        
        player = player_data.iloc[0]
        percentiles = []

        for label, col in config.RADAR_METRICS.items():
            try:
                if col not in df.columns or pd.isna(player[col]):
                    percentile = 0
                else:
                    val = player[col]
                    dist = df[col].dropna()
                    if dist.empty:
                        percentile = 0
                    else:
                        percentile = int((dist < val).mean() * 100)
            except Exception:
                percentile = 0
            percentiles.append(percentile)

        return percentiles

# ================================================================================================
# COMPOSANTS UI
# ================================================================================================

class UIComponents:
    """Composants d'interface utilisateur"""
    
    @staticmethod
    def render_header():
        """Affiche l'en-tête de l'application"""
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0; margin-bottom: 2rem;'>
            <h1 style='color: var(--primary-color); font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem;'>
                ⚽ Dashboard Football Pro
            </h1>
            <p style='color: var(--text-secondary); font-size: 1.2rem; margin: 0;'>
                Analyse avancée des performances footballistiques • Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str):
        """Affiche la carte du joueur"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Photo du joueur
            photo_path = ImageManager.get_player_photo(player_data['Joueur'])
            if photo_path:
                try:
                    st.image(photo_path, width=200, caption=f"📸 {player_data['Joueur']}")
                except:
                    st.info("📷 Photo non disponible")
            else:
                st.info("📷 Photo non disponible")
        
        with col2:
            # Informations principales
            st.markdown(f"""
            <div class='player-card'>
                <h2 style='color: var(--primary-color); margin-bottom: 1rem; font-size: 2rem;'>
                    {player_data['Joueur']}
                </h2>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; text-align: left;'>
                    <div><strong>🏆 Compétition:</strong> {competition}</div>
                    <div><strong>⚽ Club:</strong> {player_data['Équipe']}</div>
                    <div><strong>📍 Position:</strong> {player_data['Position']}</div>
                    <div><strong>🎂 Âge:</strong> {player_data['Âge']} ans</div>
                    <div><strong>🌍 Nationalité:</strong> {player_data.get('Nationalité', 'N/A')}</div>
                    <div><strong>💰 Valeur:</strong> {MetricsCalculator.format_market_value(player_data.get('Valeur marchande', 0))}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Logo du club
            logo_path = ImageManager.get_club_logo(competition, player_data['Équipe'])
            if logo_path:
                try:
                    st.image(logo_path, width=150, caption=f"🏠 {player_data['Équipe']}")
                except:
                    st.info("🏠 Logo non disponible")
            else:
                st.info("🏠 Logo non disponible")
    
    @staticmethod
    def render_metrics_grid(metrics: Dict[str, float], title: str):
        """Affiche une grille de métriques"""
        st.markdown(f"<h3 class='section-title'>{title}</h3>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, (metric_name, value) in enumerate(metrics.items()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{value:.2f}</div>
                    <div class='metric-label'>{metric_name}</div>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_comparison_chart(player1_metrics: Dict[str, float], 
                              player2_metrics: Dict[str, float],
                              player1_name: str, player2_name: str):
        """Affiche un graphique de comparaison"""
        metrics = list(player1_metrics.keys())
        values1 = list(player1_metrics.values())
        values2 = list(player2_metrics.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values1,
            theta=metrics,
            fill='toself',
            name=player1_name,
            line_color=config.PRIMARY_COLOR
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=values2,
            theta=metrics,
            fill='toself',
            name=player2_name,
            line_color=config.SECONDARY_COLOR
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, max(max(values1), max(values2)) * 1.1])
            ),
            showlegend=True,
            title=f"Comparaison: {player1_name} vs {player2_name}",
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ================================================================================================
# GESTIONNAIRE DE SIDEBAR
# ================================================================================================

class SidebarManager:
    """Gestionnaire de la barre latérale"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def render(self) -> Tuple[str, str, str, str]:
        """Affiche la sidebar et retourne les sélections"""
        with st.sidebar:
            st.markdown("""
            <div style='text-align: center; padding: 1rem; background: var(--background-card); 
                        border-radius: var(--radius-md); margin-bottom: 1rem;'>
                <h3 style='color: var(--primary-color); margin: 0;'>🎯 Filtres de Sélection</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Sélection de la compétition
            competitions = self.data_manager.get_competitions()
            selected_competition = st.selectbox(
                "🏆 Compétition",
                ["Toutes"] + competitions,
                index=0
            )
            
            # Sélection du club
            clubs = self.data_manager.get_clubs(
                selected_competition if selected_competition != "Toutes" else None
            )
            selected_club = st.selectbox(
                "⚽ Club",
                ["Tous"] + clubs,
                index=0
            )
            
            # Sélection de la position
            positions = self.data_manager.get_positions()
            selected_position = st.selectbox(
                "📍 Position",
                ["Toutes"] + positions,
                index=0
            )
            
            # Sélection du joueur
            players = self.data_manager.get_players(
                selected_competition if selected_competition != "Toutes" else None,
                selected_club if selected_club != "Tous" else None,
                selected_position if selected_position != "Toutes" else None
            )
            selected_player = st.selectbox(
                "👤 Joueur",
                ["Sélectionner un joueur..."] + players,
                index=0
            )
            
            # Informations statistiques
            st.markdown("---")
            st.markdown("### 📊 Statistiques")
            
            total_players = len(self.data_manager.get_players())
            filtered_count = len(players)
            
            st.metric("Total joueurs", total_players)
            st.metric("Joueurs filtrés", filtered_count)
            
            if filtered_count > 0:
                percentage = (filtered_count / total_players) * 100
                st.metric("Pourcentage", f"{percentage:.1f}%")
        
        # Convertir les sélections "Tous/Toutes" en None
        competition = selected_competition if selected_competition != "Toutes" else None
        club = selected_club if selected_club != "Tous" else None
        position = selected_position if selected_position != "Toutes" else None
        player = selected_player if selected_player != "Sélectionner un joueur..." else None
        
        return competition, club, position, player

# ================================================================================================
# GESTIONNAIRE D'ONGLETS
# ================================================================================================

class TabManager:
    """Gestionnaire des onglets principaux"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def render_offensive_tab(self, player_data: pd.Series):
        """Onglet performance offensive"""
        st.markdown("### 🎯 Analyse Offensive")
        
        metrics = MetricsCalculator.calculate_offensive_metrics(player_data)
        UIComponents.render_metrics_grid(metrics, "Métriques Offensives")
        
        # Graphique des buts et passes décisives
        fig = go.Figure()
        
        minutes = player_data.get('Minutes jouées', 0)
        if minutes > 0:
            minutes_90 = minutes / 90
            
            categories = ['Buts', 'Passes décisives', 'Tirs', 'Passes clés']
            values = [
                player_data.get('Buts', 0) / minutes_90,
                player_data.get('Passes décisives', 0) / minutes_90,
                player_data.get('Tirs', 0) / minutes_90,
                player_data.get('Passes clés', 0) / minutes_90
            ]
            
            fig.add_trace(go.Bar(
                x=categories,
                y=values,
                marker_color=config.PRIMARY_COLOR,
                name="Par 90 minutes"
            ))
            
            fig.update_layout(
                title="Performance Offensive (par 90 minutes)",
                yaxis_title="Valeur",
                xaxis_title="Métriques",
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_defensive_tab(self, player_data: pd.Series):
        """Onglet performance défensive"""
        st.markdown("### 🛡️ Analyse Défensive")
        
        metrics = MetricsCalculator.calculate_defensive_metrics(player_data)
        UIComponents.render_metrics_grid(metrics, "Métriques Défensives")
        
        # Graphique défensif
        fig = go.Figure()
        
        minutes = player_data.get('Minutes jouées', 0)
        if minutes > 0:
            minutes_90 = minutes / 90
            
            categories = ['Tacles', 'Interceptions', 'Duels gagnés', 'Dégagements']
            values = [
                player_data.get('Tacles gagnants', 0) / minutes_90,
                player_data.get('Interceptions', 0) / minutes_90,
                player_data.get('Duels défensifs gagnés', 0) / minutes_90,
                player_data.get('Dégagements', 0) / minutes_90
            ]
            
            fig.add_trace(go.Bar(
                x=categories,
                y=values,
                marker_color=config.SECONDARY_COLOR,
                name="Par 90 minutes"
            ))
            
            fig.update_layout(
                title="Performance Défensive (par 90 minutes)",
                yaxis_title="Valeur",
                xaxis_title="Métriques",
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_technical_tab(self, player_data: pd.Series):
        """Onglet performance technique"""
        st.markdown("### 🎨 Analyse Technique")
        
        # Métriques techniques de base
        minutes = player_data.get('Minutes jouées', 0)
        if minutes > 0:
            minutes_90 = minutes / 90
            
            technical_metrics = {
                'Passes/90': player_data.get('Passes tentées', 0) / minutes_90,
                'Passes réussies %': player_data.get('Pourcentage de passes réussies', 0),
                'Dribbles/90': player_data.get('Dribbles tentés', 0) / minutes_90,
                'Dribbles réussis %': player_data.get('Pourcentage de dribbles réussis', 0),
                'Touches/90': player_data.get('Touches de balle', 0) / minutes_90,
                'Passes progressives/90': player_data.get('Passes progressives', 0) / minutes_90
            }
            
            UIComponents.render_metrics_grid(technical_metrics, "Métriques Techniques")
    
    def render_comparison_tab(self, selected_player: str):
        """Onglet de comparaison"""
        st.markdown("### 🔄 Comparaison de Joueurs")
        
        # Sélection du joueur à comparer
        all_players = self.data_manager.get_players()
        other_players = [p for p in all_players if p != selected_player]
        
        if other_players:
            comparison_player = st.selectbox(
                "Choisir un joueur à comparer",
                other_players
            )
            
            if comparison_player:
                player1_data = self.data_manager.get_player_data(selected_player)
                player2_data = self.data_manager.get_player_data(comparison_player)
                
                if player1_data is not None and player2_data is not None:
                    # Métriques de comparaison
                    metrics1 = MetricsCalculator.calculate_offensive_metrics(player1_data)
                    metrics2 = MetricsCalculator.calculate_offensive_metrics(player2_data)
                    
                    UIComponents.render_comparison_chart(
                        metrics1, metrics2, selected_player, comparison_player
                    )
        else:
            st.info("Aucun autre joueur disponible pour la comparaison")

# ================================================================================================
# APPLICATION PRINCIPALE
# ================================================================================================

class FootballDashboard:
    """Application principale du dashboard"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.sidebar_manager = SidebarManager(self.data_manager)
        self.tab_manager = TabManager(self.data_manager)
        self._setup_page()
    
    def _setup_page(self):
        """Configuration de la page"""
        st.set_page_config(
            page_title=config.PAGE_TITLE,
            page_icon=config.PAGE_ICON,
            layout=config.LAYOUT,
            initial_sidebar_state="expanded"
        )
        
        # Application des styles
        st.markdown(StyleManager.get_main_styles(), unsafe_allow_html=True)
    
    def run(self):
        """Méthode principale d'exécution"""
        # Vérification des données
        if self.data_manager.data is None:
            self._render_error_page()
            return
        
        # En-tête
        UIComponents.render_header()
        
        # Aperçu des données
        self._render_data_overview()
        
        # Gestion de la sidebar
        competition, club, position, player = self.sidebar_manager.render()
        
        if player:
            # Récupération des données du joueur
            player_data = self.data_manager.get_player_data(player)
            if player_data is not None:
                # Affichage de la carte du joueur
                UIComponents.render_player_card(player_data, competition or "Non spécifiée")
                
                st.markdown("---")
                
                # Onglets principaux
                self._render_main_tabs(player_data, player)
            else:
                st.error("❌ Données du joueur non trouvées")
        else:
            self._render_welcome_message()
    
    def _render_data_overview(self):
        """Aperçu des données"""
        if self.data_manager.data is not None:
            df = self.data_manager.data
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 Joueurs", f"{len(df):,}")
            
            with col2:
                st.metric("🏆 Compétitions", f"{df['Compétition'].nunique()}")
            
            with col3:
                st.metric("⚽ Équipes", f"{df['Équipe'].nunique()}")
            
            with col4:
                avg_age = df['Âge'].mean()
                st.metric("📅 Âge Moyen", f"{avg_age:.1f} ans")
    
    def _render_main_tabs(self, player_data: pd.Series, selected_player: str):
        """Rendu des onglets principaux"""
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Performance Offensive",
            "🛡️ Performance Défensive", 
            "🎨 Performance Technique",
            "🔄 Comparaison"
        ])
        
        with tab1:
            self.tab_manager.render_offensive_tab(player_data)
        
        with tab2:
            self.tab_manager.render_defensive_tab(player_data)
        
        with tab3:
            self.tab_manager.render_technical_tab(player_data)
        
        with tab4:
            self.tab_manager.render_comparison_tab(selected_player)
    
    def _render_welcome_message(self):
        """Message d'accueil"""
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: var(--background-card); 
                    border-radius: var(--radius-md); margin: 2rem 0;'>
            <h2 style='color: var(--primary-color); margin-bottom: 1rem;'>
                👋 Bienvenue sur le Dashboard Football Pro
            </h2>
            <p style='color: var(--text-secondary); font-size: 1.1rem; line-height: 1.6;'>
                Utilisez les filtres de la barre latérale pour sélectionner un joueur et commencer l'analyse.
            </p>
            <div style='margin-top: 2rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;'>
                <div class='metric-card'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🎯</div>
                    <div class='metric-label'>Analyse Offensive</div>
                </div>
                <div class='metric-card'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🛡️</div>
                    <div class='metric-label'>Analyse Défensive</div>
                </div>
                <div class='metric-card'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🎨</div>
                    <div class='metric-label'>Analyse Technique</div>
                </div>
                <div class='metric-card'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🔄</div>
                    <div class='metric-label'>Comparaison</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_error_page(self):
        """Page d'erreur"""
        st.markdown(f"""
        <div style='text-align: center; padding: 3rem; background: var(--background-card); 
                    border-radius: var(--radius-md); border: 2px solid var(--danger-color);'>
            <h1 style='color: var(--danger-color); margin-bottom: 1rem;'>⚠️ Erreur de Chargement</h1>
            <p style='color: var(--text-primary); font-size: 1.1rem; margin-bottom: 2rem;'>
                Impossible de charger les données. Veuillez vérifier que le fichier '{config.DATA_FILE}' est présent.
            </p>
            <div style='background: var(--background-surface); padding: 1.5rem; border-radius: 8px; 
                        border: 1px solid var(--border-color); max-width: 500px; margin: 0 auto;'>
                <h3 style='color: var(--secondary-color); margin-bottom: 1rem;'>Fichiers requis :</h3>
                <ul style='text-align: left; color: var(--text-primary);'>
                    <li>{config.DATA_FILE} - Données principales</li>
                    <li>{config.IMAGES_FOLDER}/ - Photos des joueurs</li>
                    <li>*_Logos/ - Logos des clubs</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# POINT D'ENTRÉE
# ================================================================================================

def main():
    """Point d'entrée principal"""
    try:
        dashboard = FootballDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"❌ Erreur inattendue : {str(e)}")
        
        with st.expander("🔍 Détails de l'erreur"):
            import traceback
            st.code(traceback.format_exc())
        
        if st.button("🔄 Relancer l'application"):
            st.rerun()

if __name__ == "__main__":
    main()
