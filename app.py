import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
from PIL import Image
import glob
from typing import Dict, List, Optional, Tuple

# ================================================================================================
# CONFIGURATION DE L'APPLICATION
# ================================================================================================

class AppConfig:
    """Configuration centralisée de l'application"""
    
    # Configuration de la page
    PAGE_CONFIG = {
        "page_title": "⚽ Dashboard Football Pro",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Palette de couleurs professionnelle
    COLORS = {
        'primary': '#FF6B35',           # Orange vibrant
        'secondary': '#004E89',         # Bleu marine
        'accent': '#1A759F',           # Bleu clair
        'success': '#00C896',          # Vert emeraude
        'warning': '#F7B801',          # Jaune doré
        'danger': '#D62828',           # Rouge
        'dark': '#1E2640',             # Bleu foncé
        'light': '#F8F9FA',            # Blanc cassé
        'gradient': ['#FF6B35', '#004E89', '#1A759F', '#00C896', '#F7B801']
    }

# ================================================================================================
# GESTIONNAIRE DE MAPPING DES COLONNES
# ================================================================================================

class ColumnMapper:
    """Gestionnaire pour mapper les noms de colonnes possibles"""
    
    # Mapping des colonnes essentielles avec plusieurs variantes possibles
    COLUMN_MAPPINGS = {
        'competition': ['Compétition', 'Competition', 'League', 'Ligue', 'Championnat'],
        'player': ['Joueur', 'Player', 'Nom', 'Name'],
        'team': ['Équipe', 'Equipe', 'Team', 'Club'],
        'age': ['Âge', 'Age'],
        'position': ['Position', 'Pos'],
        'nationality': ['Nationalité', 'Nationality', 'Nation'],
        'minutes': ['Minutes jouées', 'Minutes', 'Min'],
        'market_value': ['Valeur marchande', 'Market Value', 'Valeur', 'Value'],
        'goals': ['Buts', 'Goals'],
        'assists': ['Passes décisives', 'Assists'],
        'yellow_cards': ['Cartons jaunes', 'Yellow Cards'],
        'red_cards': ['Cartons rouges', 'Red Cards'],
        'passes': ['Passes tentées', 'Passes'],
        'key_passes': ['Passes clés', 'Key Passes'],
        'touches': ['Touches de balle', 'Touches'],
        'dribbles': ['Dribbles tentés', 'Dribbles'],
        'successful_dribbles': ['Dribbles réussis', 'Successful Dribbles'],
        'tackles': ['Tacles gagnants', 'Tackles'],
        'interceptions': ['Interceptions'],
        'clearances': ['Dégagements', 'Clearances']
    }
    
    @staticmethod
    def find_column(df: pd.DataFrame, column_key: str) -> Optional[str]:
        """Trouve la colonne correspondante dans le DataFrame"""
        possible_names = ColumnMapper.COLUMN_MAPPINGS.get(column_key, [])
        
        for name in possible_names:
            if name in df.columns:
                return name
        
        # Recherche plus flexible (ignore case et espaces)
        df_columns_lower = [col.lower().strip() for col in df.columns]
        for name in possible_names:
            name_lower = name.lower().strip()
            for i, col_lower in enumerate(df_columns_lower):
                if name_lower == col_lower or name_lower in col_lower:
                    return df.columns[i]
        
        return None
    
    @staticmethod
    def get_safe_value(series: pd.Series, default=0):
        """Récupère une valeur de manière sécurisée"""
        if pd.isna(series):
            return default
        return series

# ================================================================================================
# GESTIONNAIRE DE STYLES CSS
# ================================================================================================

class StyleManager:
    """Gestionnaire centralisé des styles CSS"""
    
    @staticmethod
    def load_custom_css():
        """Charge les styles CSS personnalisés"""
        return """
        <style>
        /* ===== STYLES GLOBAUX ===== */
        .main {
            background: linear-gradient(135deg, #0E1117 0%, #1E2640 100%);
            color: #FFFFFF;
        }
        
        .stApp {
            background: linear-gradient(135deg, #0E1117 0%, #1E2640 100%);
        }
        
        /* ===== STYLES DES ONGLETS ===== */
        .stTabs [data-baseweb="tab-list"] {
            background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%);
            border-radius: 15px;
            padding: 8px;
            margin-bottom: 20px;
            border: 2px solid #FF6B35;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #FFFFFF;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #FF6B35 0%, #F7B801 100%);
            color: #FFFFFF;
            box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        }
        
        /* ===== CARTES DE CONTENU ===== */
        .dashboard-card {
            background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%);
            padding: 25px;
            border-radius: 20px;
            border: 2px solid #4A5568;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            margin: 15px 0;
            transition: all 0.3s ease;
        }
        
        .dashboard-card:hover {
            border-color: #FF6B35;
            box-shadow: 0 12px 35px rgba(255, 107, 53, 0.2);
            transform: translateY(-2px);
        }
        
        .player-header-card {
            background: linear-gradient(135deg, #FF6B35 0%, #F7B801 100%);
            padding: 30px;
            border-radius: 25px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(255, 107, 53, 0.3);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #718096;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: #00C896;
            box-shadow: 0 8px 20px rgba(0, 200, 150, 0.2);
        }
        
        /* ===== CONTENEURS D'IMAGES ===== */
        .image-container {
            background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%);
            border-radius: 20px;
            padding: 20px;
            border: 3px solid #FF6B35;
            overflow: hidden;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        
        .club-logo-container {
            background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%);
            border-radius: 15px;
            padding: 15px;
            border: 2px solid #FF6B35;
            height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        
        /* ===== STYLES DE TEXTE ===== */
        .section-title {
            color: #FF6B35;
            font-size: 2.5em;
            font-weight: 800;
            text-align: center;
            margin: 30px 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .subsection-title {
            color: #00C896;
            font-size: 1.8em;
            font-weight: 700;
            margin: 25px 0 15px 0;
            border-left: 4px solid #00C896;
            padding-left: 15px;
        }
        
        .metric-value {
            font-size: 2.2em;
            font-weight: 800;
            color: #FF6B35;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #A0AEC0;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* ===== SIDEBAR ===== */
        .sidebar-header {
            background: linear-gradient(135deg, #FF6B35 0%, #F7B801 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 25px;
        }
        
        /* ===== FOOTER ===== */
        .dashboard-footer {
            background: linear-gradient(135deg, #1E2640 0%, #2D3748 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-top: 40px;
            border: 2px solid #4A5568;
        }
        
        /* ===== ANIMATIONS ===== */
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
        
        .animated-card {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* ===== RESPONSIVITÉ ===== */
        @media (max-width: 768px) {
            .dashboard-card {
                padding: 15px;
                margin: 10px 0;
            }
            
            .section-title {
                font-size: 2em;
            }
            
            .subsection-title {
                font-size: 1.4em;
            }
        }
        </style>
        """

# ================================================================================================
# GESTIONNAIRE D'IMAGES
# ================================================================================================

class ImageManager:
    """Gestionnaire centralisé pour les images"""
    
    @staticmethod
    def get_player_photo(player_name: str) -> Optional[str]:
        """Récupère le chemin de la photo du joueur"""
        extensions = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG']
        
        for ext in extensions:
            photo_path = f"images_joueurs/**{player_name}{ext}"
            if os.path.exists(photo_path):
                return photo_path
        
        # Recherche plus flexible
        for ext in extensions:
            pattern = f"images_joueurs/**{player_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
            # Essayer avec nom inversé
            if " " in player_name:
                parts = player_name.split(" ")
                if len(parts) >= 2:
                    reversed_name = " ".join(parts[::-1])
                    pattern = f"images_joueurs/**{reversed_name}*{ext}"
                    files = glob.glob(pattern)
                    if files:
                        return files[0]
        
        return None
    
    @staticmethod
    def get_club_logo(competition: str, team_name: str) -> Optional[str]:
        """Récupère le chemin du logo du club"""
        league_folders = {
            'Bundliga': 'Bundliga_Logos',
            'La Liga': 'La_Liga_Logos',
            'Ligue 1': 'Ligue1_Logos',
            'Premier League': 'Premier_League_Logos',
            'Serie A': 'Serie_A_Logos'
        }
        
        folder = league_folders.get(competition)
        if not folder:
            return None
        
        extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
        
        for ext in extensions:
            logo_path = f"{folder}/**{team_name}{ext}"
            if os.path.exists(logo_path):
                return logo_path
        
        # Recherche plus flexible
        for ext in extensions:
            pattern = f"{folder}/**{team_name}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
                
            # Variations de nom
            clean_team = team_name.replace(" ", "_").replace("'", "").replace("-", "_")
            pattern = f"{folder}/**{clean_team}*{ext}"
            files = glob.glob(pattern)
            if files:
                return files[0]
        
        return None

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
            <h1 style='color: white; margin: 0; font-size: 3.5em; font-weight: 900;'>
                ⚽ Dashboard Football Professionnel
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 15px 0 0 0; font-size: 1.3em; font-weight: 500;'>
                Analyse avancée des performances - Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_header():
        """Affiche l'en-tête de la sidebar"""
        st.markdown("""
        <div class='sidebar-header'>
            <h2 style='color: white; margin: 0; font-weight: 800;'>🎯 Configuration</h2>
            <p style='color: rgba(255,255,255,0.8); margin: 10px 0 0 0; font-size: 0.9em;'>
                Sélectionnez votre joueur
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_player_card(player_data: pd.Series, competition: str, column_mapping: dict):
        """Affiche la carte complète du joueur"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        player_col = column_mapping.get('player')
        team_col = column_mapping.get('team')
        
        with col1:
            if player_col:
                UIComponents._render_player_photo(player_data[player_col])
        
        with col2:
            UIComponents._render_player_info(player_data, column_mapping)
        
        with col3:
            if team_col:
                UIComponents._render_club_logo(player_data[team_col], competition)
    
    @staticmethod
    def _render_player_photo(player_name: str):
        """Affiche la photo du joueur"""
        photo_path = ImageManager.get_player_photo(player_name)
        
        if photo_path:
            try:
                image = Image.open(photo_path)
                st.markdown(f"""
                <div class='image-container animated-card'>
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 15px;">
                </div>
                <p style='text-align: center; color: #FF6B35; font-weight: 600; margin-top: 10px;'>
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
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain;">
                </div>
                <p style='text-align: center; color: #FF6B35; font-weight: 600; margin-top: 10px;'>
                    🏟️ {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                UIComponents._render_logo_placeholder(team_name)
        else:
            UIComponents._render_logo_placeholder(team_name)
    
    @staticmethod
    def _render_player_info(player_data: pd.Series, column_mapping: dict):
        """Affiche les informations centrales du joueur"""
        # Récupération sécurisée des données
        player_name = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('player', ''), 'N/A'), 'N/A')
        age = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('age', ''), 'N/A'), 'N/A')
        position = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('position', ''), 'N/A'), 'N/A')
        nationality = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('nationality', ''), 'N/A'), 'N/A')
        minutes = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('minutes', ''), 0), 0)
        team = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('team', ''), 'N/A'), 'N/A')
        
        # Récupération et formatage de la valeur marchande
        valeur_marchande = "N/A"
        market_value_col = column_mapping.get('market_value')
        if market_value_col and market_value_col in player_data.index and pd.notna(player_data[market_value_col]):
            vm = player_data[market_value_col]
            if isinstance(vm, (int, float)):
                if vm >= 1000000:
                    valeur_marchande = f"{vm/1000000:.1f}M€"
                elif vm >= 1000:
                    valeur_marchande = f"{vm/1000:.0f}K€"
                else:
                    valeur_marchande = f"{vm:.0f}€"
            else:
                valeur_marchande = str(vm)
        
        st.markdown(f"""
        <div class='dashboard-card animated-card' style='text-align: center;'>
            <h2 class='section-title' style='margin-bottom: 30px;'>
                {player_name}
            </h2>
            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px;'>
                <div class='metric-card'>
                    <div class='metric-value'>{age}</div>
                    <div class='metric-label'>Ans</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{position}</div>
                    <div class='metric-label'>Position</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{nationality}</div>
                    <div class='metric-label'>Nationalité</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{int(minutes) if isinstance(minutes, (int, float)) else minutes}</div>
                    <div class='metric-label'>Minutes</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value' style='color: #F7B801;'>{valeur_marchande}</div>
                    <div class='metric-label'>Valeur Marchande</div>
                </div>
                <div class='metric-card'>
                    <div class='metric-value'>{team}</div>
                    <div class='metric-label'>Équipe</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_photo_placeholder(player_name: str):
        """Affiche un placeholder pour la photo"""
        st.markdown(f"""
        <div class='image-container animated-card'>
            <div style='text-align: center; color: #A0AEC0;'>
                <div style='font-size: 4em; margin-bottom: 10px;'>👤</div>
                <p>Photo non disponible</p>
                <p style='font-size: 0.8em;'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder(team_name: str):
        """Affiche un placeholder pour le logo"""
        st.markdown(f"""
        <div class='club-logo-container animated-card'>
            <div style='text-align: center; color: #A0AEC0;'>
                <div style='font-size: 3em; margin-bottom: 10px;'>🏟️</div>
                <p style='font-size: 0.9em;'>Logo non disponible</p>
                <p style='font-size: 0.8em;'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _image_to_base64(image: Image.Image) -> str:
        """Convertit une image PIL en base64"""
        import io
        import base64
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    @staticmethod
    def render_footer():
        """Affiche le footer"""
        st.markdown("""
        <div class='dashboard-footer animated-card'>
            <h3 style='color: #FF6B35; margin: 0 0 15px 0; font-weight: 800;'>
                📊 Dashboard Football Professionnel
            </h3>
            <p style='color: #E2E8F0; margin: 0; font-size: 1.1em; font-weight: 500;'>
                Analyse avancée des performances footballistiques
            </p>
            <p style='color: #A0AEC0; margin: 10px 0 0 0; font-size: 0.9em;'>
                Données: FBRef | Design: Dashboard Pro | Saison 2024-25
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE DONNÉES
# ================================================================================================

class DataManager:
    """Gestionnaire centralisé pour les données"""
    
    @staticmethod
    @st.cache_data
    def load_data(file_path: str = 'df_BIG2025.csv') -> Optional[Tuple[pd.DataFrame, dict]]:
        """Charge les données depuis le fichier CSV et mappe les colonnes"""
        try:
            df = pd.read_csv(file_path, encoding='latin1', delimiter=';')
            
            # Mapping des colonnes
            column_mapping = {}
            for key in ColumnMapper.COLUMN_MAPPINGS.keys():
                found_col = ColumnMapper.find_column(df, key)
                if found_col:
                    column_mapping[key] = found_col
            
            return df, column_mapping
            
        except FileNotFoundError:
            st.error(f"❌ Fichier '{file_path}' non trouvé. Veuillez vous assurer que le fichier est dans le même répertoire.")
            return None, None
        except UnicodeDecodeError:
            # Essayer avec d'autres encodages
            try:
                df = pd.read_csv(file_path, encoding='utf-8', delimiter=';')
                st.warning("⚠️ Chargé avec encoding UTF-8 au lieu de latin1")
            except:
                try:
                    df = pd.read_csv(file_path, encoding='cp1252', delimiter=';')
                    st.warning("⚠️ Chargé avec encoding cp1252")
                except Exception as e:
                    st.error(f"❌ Erreur d'encodage. Essayé latin1, utf-8 et cp1252 : {str(e)}")
                    return None, None
            
            # Mapping des colonnes
            column_mapping = {}
            for key in ColumnMapper.COLUMN_MAPPINGS.keys():
                found_col = ColumnMapper.find_column(df, key)
                if found_col:
                    column_mapping[key] = found_col
            
            return df, column_mapping
            
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
            return None, None
    
    @staticmethod
    def filter_data_by_competition(df: pd.DataFrame, competition: str, competition_col: str) -> pd.DataFrame:
        """Filtre les données par compétition"""
        if competition_col and competition_col in df.columns:
            return df[df[competition_col] == competition]
        return df
    
    @staticmethod
    def filter_data_by_minutes(df: pd.DataFrame, min_minutes: int, minutes_col: str) -> pd.DataFrame:
        """Filtre les données par minutes jouées"""
        if minutes_col and minutes_col in df.columns:
            return df[df[minutes_col] >= min_minutes]
        return df
    
    @staticmethod
    def get_competitions(df: pd.DataFrame, competition_col: str) -> List[str]:
        """Récupère la liste des compétitions"""
        if competition_col and competition_col in df.columns:
            return sorted(df[competition_col].dropna().unique())
        return ['Aucune compétition trouvée']
    
    @staticmethod
    def get_players(df: pd.DataFrame, player_col: str) -> List[str]:
        """Récupère la liste des joueurs"""
        if player_col and player_col in df.columns:
            return sorted(df[player_col].dropna().unique())
        return []

# ================================================================================================
# GESTIONNAIRE DE SIDEBAR
# ================================================================================================

class SidebarManager:
    """Gestionnaire pour la sidebar"""
    
    @staticmethod
    def render_sidebar(df: pd.DataFrame, column_mapping: dict) -> Tuple[str, str, pd.DataFrame]:
        """Rendu complet de la sidebar"""
        with st.sidebar:
            UIComponents.render_sidebar_header()
            
            competition_col = column_mapping.get('competition')
            player_col = column_mapping.get('player')
            minutes_col = column_mapping.get('minutes')
            
            if not competition_col:
                st.error("❌ Colonne 'Compétition' non trouvée dans le fichier")
                st.write("**Colonnes disponibles:**")
                for i, col in enumerate(df.columns):
                    st.write(f"{i+1}. {col}")
                return None, None, df
            
            # Sélection de la compétition
            competitions = DataManager.get_competitions(df, competition_col)
            selected_competition = st.selectbox(
                "🏆 Choisir une compétition :",
                competitions,
                index=0,
                help="Sélectionnez la compétition pour filtrer les joueurs"
            )
            
            # Filtrage par compétition
            df_filtered = DataManager.filter_data_by_competition(df, selected_competition, competition_col)
            
            st.markdown("---")
            
            # Filtre par minutes jouées
            if minutes_col:
                SidebarManager._render_minutes_filter(df_filtered, minutes_col)
                
                # Application du filtre minutes
                min_minutes_filter = st.session_state.get('min_minutes_filter', 0)
                df_filtered_minutes = DataManager.filter_data_by_minutes(df_filtered, min_minutes_filter, minutes_col)
            else:
                df_filtered_minutes = df_filtered
                st.warning("⚠️ Colonne 'Minutes' non trouvée - filtre désactivé")
            
            # Informations sur le filtrage
            SidebarManager._render_filter_info(df_filtered_minutes)
            
            st.markdown("---")
            
            # Sélection du joueur
            selected_player = SidebarManager._render_player_selection(df_filtered_minutes, player_col)
            
            # Informations additionnelles
            SidebarManager._render_sidebar_footer()
            
            return selected_competition, selected_player, df_filtered_minutes
    
    @staticmethod
    def _render_minutes_filter(df_filtered: pd.DataFrame, minutes_col: str):
        """Rendu du filtre par minutes"""
        if minutes_col in df_filtered.columns and not df_filtered[minutes_col].empty:
            min_minutes = int(df_filtered[minutes_col].min())
            max_minutes = int(df_filtered[minutes_col].max())
            
            st.markdown("**⏱️ Filtrer par minutes jouées :**")
            
            min_minutes_filter = st.slider(
                "Minutes minimum jouées :",
                min_value=min_minutes,
                max_value=max_minutes,
                value=min_minutes,
                step=90,
                help="Filtrer les joueurs ayant joué au minimum ce nombre de minutes",
                key='min_minutes_filter'
            )
    
    @staticmethod
    def _render_filter_info(df_filtered: pd.DataFrame):
        """Affiche les informations de filtrage"""
        nb_joueurs = len(df_filtered)
        
        if nb_joueurs > 0:
            st.success(f"✅ **{nb_joueurs} joueurs** correspondent aux critères")
        else:
            st.warning("⚠️ Aucun joueur ne correspond aux critères")
    
    @staticmethod
    def _render_player_selection(df_filtered: pd.DataFrame, player_col: str) -> Optional[str]:
        """Rendu de la sélection de joueur"""
        if not df_filtered.empty and player_col:
            joueurs = DataManager.get_players(df_filtered, player_col)
            if joueurs:
                selected_player = st.selectbox(
                    "👤 Choisir un joueur :",
                    joueurs,
                    index=0,
                    help="Sélectionnez le joueur à analyser"
                )
                return selected_player
        
        st.error("❌ Aucun joueur disponible avec ces critères.")
        return None
    
    @staticmethod
    def _render_sidebar_footer():
        """Rendu du footer de la sidebar"""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 15px; background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%); border-radius: 10px;'>
            <p style='color: #E2E8F0; margin: 0; font-size: 0.9em; font-weight: 600;'>
                📊 Dashboard Pro
            </p>
            <p style='color: #A0AEC0; margin: 5px 0 0 0; font-size: 0.8em;'>
                Analyse Football Avancée
            </p>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE MÉTRIQUES SIMPLIFIÉES
# ================================================================================================

class SimpleMetricsCalculator:
    """Calculateur de métriques simplifiées pour données variables"""
    
    @staticmethod
    def calculate_basic_metrics(player_data: pd.Series, column_mapping: dict) -> Dict[str, float]:
        """Calcule les métriques de base disponibles"""
        metrics = {}
        
        # Métriques offensives
        goals_col = column_mapping.get('goals')
        assists_col = column_mapping.get('assists')
        minutes_col = column_mapping.get('minutes')
        
        if goals_col and goals_col in player_data.index:
            metrics['Buts'] = ColumnMapper.get_safe_value(player_data[goals_col], 0)
        
        if assists_col and assists_col in player_data.index:
            metrics['Passes décisives'] = ColumnMapper.get_safe_value(player_data[assists_col], 0)
        
        if minutes_col and minutes_col in player_data.index:
            minutes = ColumnMapper.get_safe_value(player_data[minutes_col], 1)
            minutes_90 = minutes / 90 if minutes > 0 else 1
            
            if goals_col and goals_col in player_data.index:
                metrics['Buts/90'] = metrics.get('Buts', 0) / minutes_90
            
            if assists_col and assists_col in player_data.index:
                metrics['Passes D./90'] = metrics.get('Passes décisives', 0) / minutes_90
        
        return metrics

# ================================================================================================
# GESTIONNAIRE DE GRAPHIQUES SIMPLIFIÉS
# ================================================================================================

class SimpleChartManager:
    """Gestionnaire pour graphiques avec données variables"""
    
    @staticmethod
    def create_simple_bar_chart(data: Dict[str, float], title: str) -> go.Figure:
        """Crée un graphique en barres simple"""
        if not data:
            # Graphique vide si pas de données
            fig = go.Figure()
            fig.add_annotation(
                text="Données non disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=16, color="white")
            )
        else:
            fig = go.Figure(data=[go.Bar(
                x=list(data.keys()),
                y=list(data.values()),
                marker=dict(
                    color=AppConfig.COLORS['gradient'][:len(data)],
                    line=dict(color='white', width=2)
                ),
                text=[f"{v:.1f}" for v in data.values()],
                textposition='outside',
                textfont=dict(color='white', size=14, family='Arial Black')
            )])
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, color='white', family='Arial Black'),
                x=0.5
            ),
            xaxis=dict(
                tickfont=dict(color='white', size=12),
                tickangle=45,
                gridcolor='rgba(255,255,255,0.1)'
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=12),
                gridcolor='rgba(255,255,255,0.2)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400
        )
        
        return fig

# ================================================================================================
# GESTIONNAIRE D'ONGLETS SIMPLIFIÉS
# ================================================================================================

class SimpleTabManager:
    """Gestionnaire pour onglets avec fonctionnalités réduites"""
    
    @staticmethod
    def render_basic_stats_tab(player_data: pd.Series, column_mapping: dict):
        """Rendu de l'onglet statistiques de base"""
        st.markdown("<h2 class='section-title'>📊 Statistiques de Base</h2>", unsafe_allow_html=True)
        
        metrics = SimpleMetricsCalculator.calculate_basic_metrics(player_data, column_mapping)
        
        if metrics:
            col1, col2 = st.columns(2)
            
            with col1:
                # Graphique des statistiques totales
                total_stats = {k: v for k, v in metrics.items() if '/90' not in k}
                if total_stats:
                    fig = SimpleChartManager.create_simple_bar_chart(
                        total_stats, 
                        "Statistiques Totales"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Graphique par 90 minutes
                per_90_stats = {k: v for k, v in metrics.items() if '/90' in k}
                if per_90_stats:
                    fig = SimpleChartManager.create_simple_bar_chart(
                        per_90_stats, 
                        "Statistiques par 90 minutes"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Affichage des métriques détaillées
            SimpleTabManager._render_metrics_cards(metrics)
        else:
            st.warning("⚠️ Aucune métrique calculable trouvée dans les données")
    
    @staticmethod
    def render_data_exploration_tab(df: pd.DataFrame, column_mapping: dict):
        """Rendu de l'onglet exploration des données"""
        st.markdown("<h2 class='section-title'>🔍 Exploration des Données</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Colonnes Mappées")
            for key, col_name in column_mapping.items():
                st.write(f"**{key.title()}**: {col_name}")
        
        with col2:
            st.markdown("### 📊 Aperçu des Données")
            st.write(f"**Nombre de lignes**: {len(df)}")
            st.write(f"**Nombre de colonnes**: {len(df.columns)}")
        
        st.markdown("### 🗂️ Toutes les Colonnes Disponibles")
        cols_display = st.columns(3)
        for i, col in enumerate(df.columns):
            with cols_display[i % 3]:
                st.write(f"{i+1}. {col}")
        
        st.markdown("### 📈 Aperçu du DataFrame")
        st.dataframe(df.head(10))
    
    @staticmethod
    def _render_metrics_cards(metrics: Dict[str, float]):
        """Affiche les métriques sous forme de cartes"""
        st.markdown("<h3 class='subsection-title'>📊 Métriques Détaillées</h3>", unsafe_allow_html=True)
        
        cols = st.columns(min(len(metrics), 4))
        
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i % 4]:
                display_value = f"{value:.2f}"
                
                st.markdown(f"""
                <div class='metric-card animated-card'>
                    <div class='metric-value'>{display_value}</div>
                    <div class='metric-label'>{metric}</div>
                </div>
                """, unsafe_allow_html=True)

# ================================================================================================
# APPLICATION PRINCIPALE SIMPLIFIÉE
# ================================================================================================

class FootballDashboard:
    """Classe principale de l'application Dashboard Football"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self._configure_page()
        self._load_styles()
    
    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(**AppConfig.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS"""
        st.markdown(StyleManager.load_custom_css(), unsafe_allow_html=True)
    
    def run(self):
        """Méthode principale d'exécution de l'application"""
        # Chargement des données
        result = DataManager.load_data()
        
        if result[0] is None:
            self._render_error_page()
            return
        
        df, column_mapping = result
        
        # Rendu de l'en-tête
        UIComponents.render_header()
        
        # Information sur les colonnes trouvées
        if not column_mapping.get('competition'):
            st.error("⚠️ Colonne 'Compétition' non trouvée. L'application fonctionnera en mode simplifié.")
        
        # Rendu de la sidebar et récupération des sélections
        selected_competition, selected_player, df_filtered = SidebarManager.render_sidebar(df, column_mapping)
        
        if selected_player:
            # Récupération des données du joueur
            player_col = column_mapping.get('player')
            if player_col:
                player_data = df_filtered[df_filtered[player_col] == selected_player].iloc[0]
                
                # Affichage de la carte du joueur
                UIComponents.render_player_card(player_data, selected_competition or "N/A", column_mapping)
                
                # Métriques de base
                self._render_basic_metrics(player_data, column_mapping)
                
                st.markdown("---")
                
                # Onglets principaux
                self._render_main_tabs(player_data, df_filtered, column_mapping)
        else:
            self._render_no_player_message()
        
        # Footer
        UIComponents.render_footer()
    
    def _render_basic_metrics(self, player_data: pd.Series, column_mapping: dict):
        """Affiche les métriques de base du joueur"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Récupération sécurisée des données
        age = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('age', ''), 'N/A'), 'N/A')
        position = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('position', ''), 'N/A'), 'N/A')
        team = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('team', ''), 'N/A'), 'N/A')
        nationality = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('nationality', ''), 'N/A'), 'N/A')
        minutes = ColumnMapper.get_safe_value(player_data.get(column_mapping.get('minutes', ''), 0), 0)
        
        metrics = [
            ("👤 Âge", f"{age}"),
            ("⚽ Position", f"{position}"),
            ("🏟️ Équipe", f"{team}"),
            ("🌍 Nationalité", f"{nationality}"),
            ("⏱️ Minutes", f"{int(minutes) if isinstance(minutes, (int, float)) else minutes}")
        ]
        
        cols = [col1, col2, col3, col4, col5]
        
        for i, (label, value) in enumerate(metrics):
            with cols[i]:
                st.markdown(f"""
                <div class='metric-card animated-card'>
                    <div class='metric-value' style='font-size: 1.5em;'>{value}</div>
                    <div class='metric-label'>{label}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_main_tabs(self, player_data: pd.Series, df_filtered: pd.DataFrame, column_mapping: dict):
        """Rendu des onglets principaux"""
        tab1, tab2 = st.tabs([
            "📊 Statistiques de Base", 
            "🔍 Exploration des Données"
        ])
        
        with tab1:
            SimpleTabManager.render_basic_stats_tab(player_data, column_mapping)
        
        with tab2:
            SimpleTabManager.render_data_exploration_tab(df_filtered, column_mapping)
    
    def _render_no_player_message(self):
        """Affiche un message quand aucun joueur n'est sélectionné"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 40px;'>
            <h2 style='color: #FF6B35; margin-bottom: 20px;'>⚠️ Aucun joueur sélectionné</h2>
            <p style='color: #E2E8F0; font-size: 1.2em; margin-bottom: 30px;'>
                Veuillez ajuster les filtres dans la sidebar pour sélectionner un joueur à analyser.
            </p>
            <div style='display: flex; justify-content: center; gap: 30px; margin-top: 30px;'>
                <div style='text-align: center;'>
                    <div style='font-size: 3em; margin-bottom: 10px;'>📊</div>
                    <p style='color: #A0AEC0;'>Statistiques de Base</p>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 3em; margin-bottom: 10px;'>🔍</div>
                    <p style='color: #A0AEC0;'>Exploration des Données</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_error_page(self):
        """Affiche la page d'erreur"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 40px; border-color: #D62828;'>
            <h1 style='color: #D62828; margin-bottom: 20px;'>⚠️ Erreur de Chargement</h1>
            <p style='color: #E2E8F0; font-size: 1.2em; margin-bottom: 30px;'>
                Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
            </p>
            <div style='background: linear-gradient(135deg, #2D3748 0%, #4A5568 100%); padding: 20px; border-radius: 15px; margin-top: 30px;'>
                <h3 style='color: #00C896; margin-bottom: 15px;'>📋 Fichiers requis :</h3>
                <ul style='color: #E2E8F0; text-align: left; max-width: 600px; margin: 0 auto;'>
                    <li>df_BIG2025.csv (données principales)</li>
                    <li>images_joueurs/ (photos des joueurs)</li>
                    <li>*_Logos/ (logos des clubs par compétition)</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# POINT D'ENTRÉE DE L'APPLICATION
# ================================================================================================

def main():
    """Point d'entrée principal de l'application"""
    dashboard = FootballDashboard()
    dashboard.run()

# Exécution de l'application
if __name__ == "__main__":
    main()
