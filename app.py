"""
Dashboard Football Professionnel - Version Corrigée
=================================================

Application Streamlit pour l'analyse avancée des performances footballistiques.
Auteur: Dashboard Pro
Version: 2.2.0 - Version corrigée sans erreurs de syntaxe
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
        'Minutes jouées',
        'Buts',
        'Passes décisives',
        'Tirs',
        'Passes clés',
        'Passes tentées',
        'Dribbles tentés',
        'Dribbles réussis',
        'Tacles gagnants',
        'Interceptions'
    ]
    
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
                # Nettoyer la chaîne
                clean_value = str(value).replace('€', '').replace('$', '').replace(',', '').replace(' ', '').strip()
                
                # Gérer les multiplicateurs
                multiplier = 1
                if 'B' in clean_value.upper():
                    multiplier = 1000000000
                    clean_value = clean_value.upper().replace('B', '')
                elif 'M' in clean_value.upper():
                    multiplier = 1000000
                    clean_value = clean_value.upper().replace('M', '')
                elif 'K' in clean_value.upper():
                    multiplier = 1000
                    clean_value = clean_value.upper().replace('K', '')
                
                # Garder seulement les chiffres et le point
                clean_value = ''.join(c for c in clean_value if c.isdigit() or c == '.')
                
                if clean_value and clean_value != '.':
                    value = float(clean_value) * multiplier
                else:
                    return "N/A"
            except (ValueError, TypeError):
                return "N/A"
        
        try:
            value = float(value)
            if value <= 0 or value > 1000000000000:
                return "N/A"
        except (ValueError, TypeError):
            return "N/A"
        
        # Formatage
        if value >= 1000000000:
            return f"{value/1000000000:.1f}B€"
        elif value >= 1000000:
            return f"{value/1000000:.1f}M€"
        elif value >= 1000:
            return f"{value/1000:.1f}K€"
        else:
            return f"{value:.0f}€"
    
    @staticmethod
    def get_market_value_safe(player_data: pd.Series) -> str:
        """Récupère la valeur marchande exacte depuis les données du joueur"""
        # Liste des colonnes possibles pour la valeur marchande
        possible_columns = [
            'Valeur marchande', 'Market Value', 'valeur_marchande', 
            'Valeur', 'Value', 'market_value', 'Valeur en €', 'Valeur (€)',
            'Market_Value', 'Valeur_marchande', 'VALEUR_MARCHANDE',
            'Valeur_Marchande', 'MARKET_VALUE', 'MarketValue', 'market_val',
            'val_marchande', 'VM', 'vm', 'valeur_m', 'valeur_marche',
            'Transfer Value', 'transfer_value', 'Prix', 'price', 'Price'
        ]
        
        # Recherche directe dans les colonnes
        for col in possible_columns:
            if col in player_data.index and pd.notna(player_data.get(col)):
                value = player_data[col]
                if value != 0 and str(value).lower() not in ['nan', 'null', '', '0', 'none', 'n/a', 'na']:
                    formatted_value = Utils.format_market_value(value)
                    if formatted_value != "N/A":
                        return formatted_value
        
        # Recherche par mots-clés
        for col in player_data.index:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['val', 'market', 'price', 'prix', 'cost', 'worth', 'transfer']):
                if pd.notna(player_data.get(col)):
                    value = player_data[col]
                    if value != 0 and str(value).lower() not in ['nan', 'null', '', '0', 'none', 'n/a', 'na']:
                        formatted_value = Utils.format_market_value(value)
                        if formatted_value != "N/A":
                            return formatted_value
        
        # Recherche dans les plages de valeurs typiques
        for col in player_data.index:
            if pd.notna(player_data.get(col)):
                try:
                    value = float(player_data[col])
                    # Valeurs typiques de valeurs marchandes
                    if 100000 <= value <= 500000000:
                        # Exclure les colonnes qui ne sont pas des valeurs marchandes
                        if col.lower() not in ['age', 'âge', 'minutes', 'matchs', 'buts', 'passes', 'tirs']:
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
        
        /* Cartes de joueurs similaires */
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
        """Récupère les données de toutes les autres ligues"""
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
        required_cols = ['Joueur', 'Équipe', 'Compétition', 'Position', 'Âge']
        similarity_df = df[required_cols + available_metrics].copy()
        
        # Remplacer les valeurs manquantes par 0
        for col in available_metrics:
            similarity_df[col] = pd.to_numeric(similarity_df[col], errors='coerce').fillna(0)
        
        # Filtrer les lignes avec des données valides
        similarity_df = similarity_df.dropna(subset=['Joueur'])
        
        return similarity_df, available_metrics
    
    @staticmethod
    def calculate_similarity_simple(target_player: str, df: pd.DataFrame, num_similar: int = 5) -> List[Dict]:
        """Calcule la similarité sans sklearn"""
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
            
            # Filtrer les autres joueurs
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                return []
            
            # Calculer la similarité
            similarities = []
            
            for idx, player_row in other_players.iterrows():
                player_values = player_row[available_metrics]
                
                # Calculer la différence relative pour chaque métrique
                total_diff = 0
                valid_metrics = 0
                
                for metric in available_metrics:
                    target_val = float(target_values[metric])
                    player_val = float(player_values[metric])
                    
                    # Éviter la division par zéro
                    max_val = max(abs(target_val), abs(player_val), 1)
                    diff = abs(target_val - player_val) / max_val
                    total_diff += diff
                    valid_metrics += 1
                
                # Score de similarité
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
        """Calcule la similarité avec sklearn"""
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
            
            # Filtrer les autres joueurs
            other_players = similarity_df[similarity_df['Joueur'] != target_player].copy()
            
            if other_players.empty:
                return []
            
            # Normaliser les données
            scaler = StandardScaler()
            
            # Données pour normalisation
            all_data = similarity_df[available_metrics].values
            scaler.fit(all_data)
            
            # Normaliser les données
            target_normalized = scaler.transform([target_values])[0]
            others_normalized = scaler.transform(other_players[available_metrics].values)
            
            # Calculer les distances euclidiennes
            distances = euclidean_distances([target_normalized], others_normalized)[0]
            
            # Convertir en scores de similarité
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
    def create_histogram_comparison(target_player: str, similar_players: List[Dict], 
                                  df: pd.DataFrame, metric: str) -> go.Figure:
        """Crée un histogramme de comparaison haute qualité"""
        
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
            
            # Couleur selon la similarité
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
        
        # Mise en page
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
        """Affiche une carte pour un joueur similaire"""
        similarity_score = player_info['similarity_score']
        player_data = player_info['data']
        
        # Couleur basée sur le score de similarité
        if similarity_score >= 85:
            score_color = "#2ca02c"
        elif similarity_score >= 70:
            score_color = "#ff7f0e"
        else:
            score_color = "#1f77b4"
        
        # Valeur marchande
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
                logo_html = '<div style="width: 40px; height: 40px; background: rgba(255,255,255,0.1); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.8em; color: white;">🏟️</div>'
        else:
            logo_html = '<div style="width: 40px; height: 40px; background: rgba(255,255,255,0.1); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.8em; color: white;">🏟️</div>'
        
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
            
            return selected_competition, selected_player, df_filtered_minutes

# ================================================================================================
# GESTIONNAIRE D'ONGLETS
# ================================================================================================

class TabManager:
    """Gestionnaire pour les différents onglets"""
    
    @staticmethod
    def render_similar_players_tab(selected_player: str, df: pd.DataFrame):
        """Rendu de l'onglet joueurs similaires"""
        st.markdown("<h2 class='section-title-enhanced'>👥 Profils Similaires</h2>", unsafe_allow_html=True)
        
        # Configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("<h3 class='subsection-title-enhanced'>⚙️ Configuration de l'Analyse</h3>", unsafe_allow_html=True)
        
        with col2:
            num_similar = st.slider(
                "Nombre de joueurs similaires :",
                min_value=1,
                max_value=10,
                value=5,
                help="Nombre de joueurs similaires à afficher"
            )
        
        # Afficher les métriques analysées
        st.markdown("<h3 class='subsection-title-enhanced'>📊 Métriques Analysées</h3>", unsafe_allow_html=True)
        
        # Récupérer les métriques analysées
        similarity_df, available_metrics = SimilarPlayerAnalyzer.prepare_similarity_data(df)
        
        if available_metrics:
            # Afficher les métriques sous forme de badges
            metrics_html = ""
            for i, metric in enumerate(available_metrics):
                color_class = ['primary', 'secondary', 'accent', 'success', 'warning'][i % 5]
                metrics_html += f"""
                <span style="display: inline-block; background: var(--{color_class}-color); color: white; 
                           padding: 6px 12px; border-radius: 20px; margin: 4px; font-size: 0.9em; font-weight: 500;">
                    {metric}
                </span>
                """
            
            st.markdown(f"""
            <div style="background: var(--background-surface); padding: 20px; border-radius: 12px; 
                       border: 1px solid var(--border-color); margin: 16px 0;">
                <p style="color: var(--text-primary); margin-bottom: 12px; font-weight: 600;">
                    🔍 <strong>{len(available_metrics)} métriques</strong> utilisées pour calculer la similarité :
                </p>
                {metrics_html}
            </div>
            """, unsafe_allow_html=True)
        
        # Message d'information sur sklearn
        if not SKLEARN_AVAILABLE:
            st.info("ℹ️ Analyse de similarité en mode simplifié (scikit-learn non disponible)")
        
        # Calcul des joueurs similaires
        with st.spinner("🔍 Recherche de joueurs similaires..."):
            similar_players = SimilarPlayerAnalyzer.calculate_similarity(selected_player, df, num_similar)
        
        if not similar_players:
            st.warning("⚠️ Aucun joueur similaire trouvé.")
            return
        
        # Affichage des résultats
        st.markdown(f"<h3 class='subsection-title-enhanced'>🎯 Top {len(similar_players)} joueurs similaires</h3>", unsafe_allow_html=True)
        
        # Métriques de résumé
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            avg_similarity = np.mean([p['similarity_score'] for p in similar_players])
            st.metric("Score Moyen", f"{avg_similarity:.1f}%")
        
        with metrics_col2:
            best_match = similar_players[0] if similar_players else None
            if best_match:
                st.metric("Meilleur Match", best_match['joueur'][:15] + "..." if len(best_match['joueur']) > 15 else best_match['joueur'])
        
        with metrics_col3:
            unique_competitions = len(set(p['competition'] for p in similar_players))
            st.metric("Compétitions", f"{unique_competitions}")
        
        with metrics_col4:
            st.metric("Métriques", f"{len(available_metrics)}")
        
        # Cartes des joueurs similaires
        st.markdown("---")
        
        cols_per_row = 2
        for i in range(0, len(similar_players), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(similar_players):
                    with col:
                        UIComponents.render_similar_player_card(similar_players[i + j], i + j + 1)
        
        # Histogrammes de comparaison
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>📊 Histogrammes de Comparaison</h3>", unsafe_allow_html=True)
        
        # Sélection de la métrique
        available_histogram_metrics = [metric for metric in Config.HISTOGRAM_METRICS if metric in df.columns]
        
        if available_histogram_metrics:
            metric_col1, metric_col2 = st.columns([2, 1])
            
            with metric_col1:
                selected_metric = st.selectbox(
                    "📈 Choisissez une métrique :",
                    available_histogram_metrics,
                    index=0,
                    help="Métrique à comparer"
                )
            
            with metric_col2:
                st.info(f"🎯 **{selected_metric}**")
            
            # Créer l'histogramme
            if selected_metric:
                fig_histogram = ChartManager.create_histogram_comparison(
                    selected_player, similar_players, df, selected_metric
                )
                st.plotly_chart(fig_histogram, use_container_width=True)
                
                # Statistiques
                target_data = df[df['Joueur'] == selected_player]
                if not target_data.empty:
                    target_value = target_data[selected_metric].iloc[0]
                    if not pd.isna(target_value):
                        similar_values = []
                        for player_info in similar_players:
                            value = player_info['data'].get(selected_metric, 0)
                            if not pd.isna(value):
                                similar_values.append(value)
                        
                        if similar_values:
                            avg_similar = np.mean(similar_values)
                            max_similar = np.max(similar_values)
                            min_similar = np.min(similar_values)
                            
                            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                            
                            with stats_col1:
                                st.metric(f"{selected_player[:10]}...", f"{target_value:.1f}")
                            
                            with stats_col2:
                                st.metric("Moyenne", f"{avg_similar:.1f}",
                                         delta=f"{target_value - avg_similar:.1f}")
                            
                            with stats_col3:
                                st.metric("Maximum", f"{max_similar:.1f}")
                            
                            with stats_col4:
                                st.metric("Minimum", f"{min_similar:.1f}")
        
        # Analyse des valeurs marchandes
        st.markdown("---")
        st.markdown("<h3 class='subsection-title-enhanced'>💰 Valeurs Marchandes</h3>", unsafe_allow_html=True)
        
        # Récupérer les valeurs marchandes
        target_data = df[df['Joueur'] == selected_player]
        if not target_data.empty:
            target_market_value = Utils.get_market_value_safe(target_data.iloc[0])
            
            market_values = []
            for player_info in similar_players:
                player_data = player_info['data']
                market_value = Utils.get_market_value_safe(player_data)
                market_values.append({
                    'joueur': player_info['joueur'],
                    'valeur': market_value,
                    'similarity': player_info['similarity_score']
                })
            
            # Afficher les valeurs
            value_col1, value_col2 = st.columns([1, 2])
            
            with value_col1:
                st.markdown(f"""
                <div style="background: var(--background-surface); padding: 20px; border-radius: 12px; 
                           border: 2px solid var(--primary-color); text-align: center;">
                    <h4 style="color: var(--primary-color); margin: 0 0 12px 0;">🎯 Joueur Principal</h4>
                    <p style="color: var(--text-primary); margin: 0; font-size: 1.1em; font-weight: 600;">
                        {selected_player}
                    </p>
                    <p style="color: var(--accent-color); margin: 8px 0 0 0; font-size: 1.3em; font-weight: 700;">
                        {target_market_value}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with value_col2:
                st.markdown("**💰 Valeurs Marchandes des Joueurs Similaires :**")
                
                for i, mv_info in enumerate(market_values):
                    similarity_color = "#2ca02c" if mv_info['similarity'] >= 85 else "#ff7f0e" if mv_info['similarity'] >= 70 else "#1f77b4"
                    
                    st.markdown(f"""
                    <div style="background: var(--background-surface); padding: 12px; border-radius: 8px; 
                               border-left: 4px solid {similarity_color}; margin: 8px 0; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: var(--text-primary);">#{i+1} {mv_info['joueur']}</strong>
                            <span style="color: var(--text-secondary); font-size: 0.9em; margin-left: 12px;">
                                ({mv_info['similarity']:.1f}% similaire)
                            </span>
                        </div>
                        <div style="color: var(--accent-color); font-weight: 700; font-size: 1.1em;">
                            {mv_info['valeur']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# ================================================================================================
# APPLICATION PRINCIPALE
# ================================================================================================

class FootballDashboard:
    """Classe principale de l'application"""
    
    def __init__(self):
        """Initialisation de l'application"""
        self._configure_page()
        self._load_styles()
    
    def _configure_page(self):
        """Configuration de la page Streamlit"""
        st.set_page_config(**Config.PAGE_CONFIG)
    
    def _load_styles(self):
        """Chargement des styles CSS"""
        st.markdown(StyleManager.get_css(), unsafe_allow_html=True)
    
    def run(self):
        """Méthode principale d'exécution"""
        # Chargement des données
        with st.spinner("Chargement des données..."):
            df = DataManager.load_data()
        
        if df is None:
            st.error("❌ Impossible de charger les données")
            return
        
        # En-tête
        UIComponents.render_header()
        
        # Sidebar
        selected_competition, selected_player, df_filtered = SidebarManager.render_sidebar(df)
        
        if selected_player:
            # Données du joueur
            player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
            
            # Breadcrumbs
            UIComponents.render_breadcrumbs(
                selected_competition, 
                player_data['Équipe'], 
                selected_player
            )
            
            # Carte joueur
            UIComponents.render_player_card(player_data, selected_competition)
            
            st.markdown("---")
            
            # Onglet Profils Similaires
            TabManager.render_similar_players_tab(selected_player, df)
        
        else:
            st.markdown("""
            <div style='background: var(--background-card); padding: 48px; border-radius: var(--radius-lg); 
                        text-align: center; border: 2px solid var(--border-color); margin: 32px 0;'>
                <h2 style='color: var(--primary-color); margin-bottom: 24px; font-size: 2em;'>⚠️ Aucun joueur sélectionné</h2>
                <p style='color: var(--text-primary); font-size: 1.2em; margin-bottom: 32px;'>
                    Veuillez sélectionner un joueur dans la sidebar pour commencer l'analyse.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Footer
        UIComponents.render_footer()

# ================================================================================================
# POINT D'ENTRÉE
# ================================================================================================

def main():
    """Point d'entrée principal"""
    try:
        dashboard = FootballDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")
        
        with st.expander("🔍 Détails de l'erreur", expanded=False):
            import traceback
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
