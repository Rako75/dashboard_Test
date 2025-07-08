# AMÉLIORATIONS UX/UI BASÉES SUR VOS SUGGESTIONS

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
# STYLES CSS AMÉLIORÉS POUR UX/UI
# ================================================================================================

class ImprovedStyleManager:
    """Gestionnaire de styles amélioré avec les suggestions UX/UI"""
    
    @staticmethod
    def load_improved_css():
        """Styles CSS améliorés pour une meilleure UX/UI"""
        return """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* ===== VARIABLES CSS AMÉLIORÉES ===== */
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
        
        /* ===== STYLES GLOBAUX ===== */
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
        
        /* ===== ONGLETS STICKY ET AMÉLIORÉS ===== */
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
        
        .stTabs [aria-selected="true"]::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 50%;
            transform: translateX(-50%);
            width: 60%;
            height: 3px;
            background: var(--accent-color);
            border-radius: 2px;
        }
        
        /* ===== CARTES JOUEUR AMÉLIORÉES ===== */
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
                gap: var(--spacing-sm);
            }
        }
        
        @media (max-width: 480px) {
            .player-metrics-grid {
                grid-template-columns: 1fr;
                gap: var(--spacing-sm);
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
        
        .metric-card-enhanced::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: var(--primary-color);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .metric-card-enhanced:hover::before {
            transform: scaleX(1);
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
        
        /* ===== SECTIONS AVEC ANCRES ===== */
        .section-anchor {
            position: relative;
        }
        
        .section-anchor::before {
            content: '';
            position: absolute;
            top: -80px;
            left: 0;
            height: 1px;
            width: 1px;
        }
        
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
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        /* ===== BOUTONS DE NAVIGATION RAPIDE ===== */
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
        
        /* ===== LÉGENDES ET TOOLTIPS AMÉLIORÉS ===== */
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
        
        .tooltip-trigger {
            position: relative;
            display: inline-block;
            cursor: help;
            color: var(--primary-color);
            font-weight: 600;
            border-bottom: 1px dotted var(--primary-color);
        }
        
        .tooltip-content {
            visibility: hidden;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            background: var(--background-dark);
            color: var(--text-primary);
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            white-space: nowrap;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
        }
        
        .tooltip-trigger:hover .tooltip-content {
            visibility: visible;
        }
        
        /* ===== JAUGES AVEC UNITÉS ===== */
        .gauge-container {
            position: relative;
        }
        
        .gauge-label {
            text-align: center;
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: var(--spacing-xs);
            font-weight: 500;
        }
        
        .gauge-value {
            position: absolute;
            top: 60%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
        }
        
        /* ===== BOUTON RETOUR EN HAUT ===== */
        .back-to-top {
            position: fixed;
            bottom: var(--spacing-lg);
            right: var(--spacing-lg);
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: var(--shadow-lg);
            transition: all 0.3s ease;
            z-index: 1000;
            opacity: 0;
            transform: translateY(20px);
        }
        
        .back-to-top.visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        .back-to-top:hover {
            background: var(--secondary-color);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(31, 119, 180, 0.4);
        }
        
        /* ===== MASQUER LES ÉLÉMENTS INUTILES ===== */
        .stDeployButton {
            display: none !important;
        }
        
        .stDecoration {
            display: none !important;
        }
        
        [data-testid="manage-app-button"] {
            display: none !important;
        }
        
        /* ===== RESPONSIVE AMÉLIORÉ ===== */
        @media (max-width: 768px) {
            .main .block-container {
                padding: var(--spacing-md);
            }
            
            .section-title-enhanced {
                font-size: 1.5rem;
            }
            
            .subsection-title-enhanced {
                font-size: 1.1rem;
            }
            
            .quick-nav {
                display: none;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: var(--spacing-sm) var(--spacing-md);
                font-size: 0.8rem;
            }
            
            .player-info-card {
                padding: var(--spacing-lg);
            }
        }
        
        @media (max-width: 480px) {
            .section-title-enhanced {
                font-size: 1.3rem;
            }
            
            .metric-value-enhanced {
                font-size: 1.4rem;
            }
            
            .metric-label-enhanced {
                font-size: 0.7rem;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: var(--spacing-xs) var(--spacing-sm);
                font-size: 0.75rem;
            }
        }
        
        /* ===== ANIMATIONS D'ENTRÉE ===== */
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
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .animated-card {
            animation: fadeInUp 0.6s ease-out;
        }
        
        .slide-in {
            animation: slideInRight 0.4s ease-out;
        }
        
        /* ===== INDICATEURS DE CHARGEMENT ===== */
        .loading-indicator {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: var(--spacing-xl);
            color: var(--text-secondary);
        }
        
        .loading-spinner {
            border: 3px solid var(--border-light);
            border-top: 3px solid var(--primary-color);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin-right: var(--spacing-md);
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """

# ================================================================================================
# COMPOSANTS UI AMÉLIORÉS
# ================================================================================================

class EnhancedUIComponents:
    """Composants UI améliorés avec les suggestions UX/UI"""
    
    @staticmethod
    def render_enhanced_player_card(player_data: pd.Series, competition: str):
        """Carte joueur améliorée avec meilleur espacement et visibilité"""
        
        # Données du joueur avec noms complets
        equipe_complete = player_data['Équipe']  # Nom complet sans troncature
        nationalite_complete = player_data['Nationalité']
        position_complete = player_data['Position']
        
        # Valeur marchande formatée
        valeur_marchande = "N/A"
        if 'Valeur marchande' in player_data.index:
            valeur_marchande = format_market_value(player_data['Valeur marchande'])
        
        col1, col2, col3 = st.columns([1, 2.5, 1], gap="large")
        
        with col1:
            EnhancedUIComponents._render_player_photo_enhanced(player_data['Joueur'])
        
        with col2:
            st.markdown(f"""
            <div class='player-info-card animated-card'>
                <h2 class='section-title-enhanced' style='margin-bottom: var(--spacing-xl); font-size: 2.5em; color: var(--text-primary);'>
                    {player_data['Joueur']}
                </h2>
                <div class='player-metrics-grid'>
                    <div class='metric-card-enhanced slide-in' style='animation-delay: 0.1s;'>
                        <div class='metric-value-enhanced'>{player_data['Âge']}</div>
                        <div class='metric-label-enhanced'>Âge</div>
                    </div>
                    <div class='metric-card-enhanced slide-in' style='animation-delay: 0.2s;'>
                        <div class='metric-value-enhanced' title='{position_complete}'>{position_complete}</div>
                        <div class='metric-label-enhanced'>Position</div>
                    </div>
                    <div class='metric-card-enhanced slide-in' style='animation-delay: 0.3s;'>
                        <div class='metric-value-enhanced' title='{nationalite_complete}'>{nationalite_complete}</div>
                        <div class='metric-label-enhanced'>Nationalité</div>
                    </div>
                    <div class='metric-card-enhanced slide-in' style='animation-delay: 0.4s;'>
                        <div class='metric-value-enhanced'>{int(player_data['Minutes jouées'])}</div>
                        <div class='metric-label-enhanced'>Minutes Jouées</div>
                    </div>
                    <div class='metric-card-enhanced slide-in' style='animation-delay: 0.5s;'>
                        <div class='metric-value-enhanced' style='color: var(--accent-color);'>{valeur_marchande}</div>
                        <div class='metric-label-enhanced'>Valeur Marchande</div>
                    </div>
                    <div class='metric-card-enhanced slide-in' style='animation-delay: 0.6s;'>
                        <div class='metric-value-enhanced' title='{equipe_complete}'>{equipe_complete}</div>
                        <div class='metric-label-enhanced'>Équipe</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            EnhancedUIComponents._render_club_logo_enhanced(player_data['Équipe'], competition)
    
    @staticmethod
    def _render_player_photo_enhanced(player_name: str):
        """Photo joueur avec style amélioré"""
        photo_path = ImageManager.get_player_photo(player_name)
        
        if photo_path:
            try:
                image = Image.open(photo_path)
                st.markdown(f"""
                <div class='image-container animated-card' style='
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
                    position: relative;
                '>
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: var(--radius-md);">
                </div>
                <p style='text-align: center; color: var(--primary-color); font-weight: 600; margin-top: var(--spacing-md); font-size: 0.9em;'>
                    📸 {player_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                EnhancedUIComponents._render_photo_placeholder_enhanced(player_name)
        else:
            EnhancedUIComponents._render_photo_placeholder_enhanced(player_name)
    
    @staticmethod
    def _render_club_logo_enhanced(team_name: str, competition: str):
        """Logo club avec style amélioré"""
        logo_path = ImageManager.get_club_logo(competition, team_name)
        
        if logo_path:
            try:
                image = Image.open(logo_path)
                st.markdown(f"""
                <div class='club-logo-container animated-card' style='
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
                '>
                    <img src="data:image/jpeg;base64,{UIComponents._image_to_base64(image)}" 
                         style="max-width: 100%; max-height: 100%; object-fit: contain;">
                </div>
                <p style='text-align: center; color: var(--primary-color); font-weight: 600; margin-top: var(--spacing-md); font-size: 0.9em;'>
                    🏟️ {team_name}
                </p>
                """, unsafe_allow_html=True)
            except Exception:
                EnhancedUIComponents._render_logo_placeholder_enhanced(team_name)
        else:
            EnhancedUIComponents._render_logo_placeholder_enhanced(team_name)
    
    @staticmethod
    def _render_photo_placeholder_enhanced(player_name: str):
        """Placeholder photo amélioré"""
        st.markdown(f"""
        <div class='image-container animated-card' style='
            background: var(--background-surface);
            border-radius: var(--radius-lg);
            padding: var(--spacing-lg);
            border: 2px solid var(--border-color);
            height: 320px;
            display: flex;
            align-items: center;
            justify-content: center;
        '>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 4em; margin-bottom: var(--spacing-md); opacity: 0.5;'>👤</div>
                <p style='margin: 0; font-size: 0.9em;'>Photo non disponible</p>
                <p style='font-size: 0.8em; margin-top: var(--spacing-sm); color: var(--primary-color);'>{player_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_logo_placeholder_enhanced(team_name: str):
        """Placeholder logo amélioré"""
        st.markdown(f"""
        <div class='club-logo-container animated-card' style='
            background: var(--background-surface);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            border: 2px solid var(--border-color);
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        '>
            <div style='text-align: center; color: var(--text-secondary);'>
                <div style='font-size: 3em; margin-bottom: var(--spacing-md); opacity: 0.5;'>🏟️</div>
                <p style='margin: 0; font-size: 0.8em;'>Logo non disponible</p>
                <p style='font-size: 0.75em; margin-top: var(--spacing-xs); color: var(--primary-color);'>{team_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_quick_navigation():
        """Navigation rapide entre sections"""
        st.markdown("""
        <div class='quick-nav'>
            <a href='#offensive' class='quick-nav-item'>🎯 Offensif</a>
            <a href='#defensive' class='quick-nav-item'>🛡️ Défensif</a>
            <a href='#technique' class='quick-nav-item'>🎨 Technique</a>
            <a href='#comparaison' class='quick-nav-item'>🔄 Comparaison</a>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_back_to_top():
        """Bouton retour en haut"""
        st.markdown("""
        <button class='back-to-top' onclick='window.scrollTo({top: 0, behavior: "smooth"})'>
            ↑
        </button>
        
        <script>
        window.addEventListener('scroll', function() {
            const button = document.querySelector('.back-to-top');
            if (window.pageYOffset > 300) {
                button.classList.add('visible');
            } else {
                button.classList.remove('visible');
            }
        });
        </script>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE GRAPHIQUES AMÉLIORÉ
# ================================================================================================

class EnhancedChartManager:
    """Gestionnaire de graphiques avec légendes et unités améliorées"""
    
    @staticmethod
    def create_enhanced_gauge_chart(data: Dict[str, float], title: str) -> go.Figure:
        """Jauges avec unités % explicites"""
        fig = make_subplots(
            rows=1, cols=len(data),
            specs=[[{"type": "indicator"}] * len(data)],
            subplot_titles=[f"{key}" for key in data.keys()]
        )
        
        colors = [AppConfig.COLORS['primary'], AppConfig.COLORS['secondary'], AppConfig.COLORS['warning']]
        
        for i, (metric, value) in enumerate(data.items()):
            color = colors[i % len(colors)]
            
            # S'assurer que la valeur est entre 0 et 100
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
    def create_enhanced_radar_chart(metrics: Dict[str, float], percentiles: List[float], 
                                  avg_percentiles: List[float], player_name: str, 
                                  competition: str, color: str) -> go.Figure:
        """Radar chart avec légende explicite et titre unifié"""
        fig = go.Figure()
        
        # Performance du joueur
        fig.add_trace(go.Scatterpolar(
            r=percentiles,
            theta=list(metrics.keys()),
            fill='toself',
            fillcolor=f'rgba({EnhancedChartManager._hex_to_rgb(color)}, 0.25)',
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
    
    @staticmethod
    def create_enhanced_comparison_chart(player_data: Dict[str, float], avg_data: Dict[str, float], 
                                       player_name: str, title: str) -> go.Figure:
        """Graphique de comparaison avec légendes explicites"""
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=player_name,
            x=list(player_data.keys()),
            y=list(player_data.values()),
            marker_color=AppConfig.COLORS['primary'],
            marker_line=dict(color='rgba(255,255,255,0.2)', width=1),
            text=[f"{v:.2f}" for v in player_data.values()],
            textposition='outside',
            textfont=dict(size=11, family='Inter', weight=600)
        ))
        
        fig.add_trace(go.Bar(
            name='Moyenne compétition',
            x=list(avg_data.keys()),
            y=list(avg_data.values()),
            marker_color=AppConfig.COLORS['secondary'],
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
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=False,
                title_font=dict(size=12, family='Inter')
            ),
            yaxis=dict(
                tickfont=dict(color='white', size=11), 
                gridcolor='rgba(255,255,255,0.15)',
                showgrid=True,
                title_font=dict(size=12, family='Inter')
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
    def _hex_to_rgb(hex_color: str) -> str:
        """Convertit une couleur hex en RGB"""
        hex_color = hex_color.lstrip('#')
        return ','.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))
    
    @staticmethod
    def render_chart_legend(player_name: str, competition: str):
        """Légende explicite pour les graphiques"""
        st.markdown(f"""
        <div class='chart-legend'>
            <div class='legend-item'>
                <div class='legend-color' style='background: var(--primary-color);'></div>
                <span>{player_name}</span>
            </div>
            <div class='legend-item'>
                <div class='legend-color' style='background: rgba(255,255,255,0.6);'></div>
                <span>Moyenne {competition}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE SECTIONS AVEC ANCRES
# ================================================================================================

class SectionManager:
    """Gestionnaire de sections avec ancres et navigation"""
    
    @staticmethod
    def render_section_with_anchor(title: str, anchor_id: str, icon: str = ""):
        """Section avec ancre pour navigation"""
        st.markdown(f"""
        <div class='section-anchor' id='{anchor_id}'>
            <h2 class='section-title-enhanced'>
                {icon} {title}
            </h2>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_subsection_with_help(title: str, help_text: str = "", icon: str = ""):
        """Sous-section avec aide contextuelle"""
        help_button = ""
        if help_text:
            help_button = f"""
            <span class='tooltip-trigger'>
                ❓
                <span class='tooltip-content'>{help_text}</span>
            </span>
            """
        
        st.markdown(f"""
        <h3 class='subsection-title-enhanced'>
            <span>{icon} {title}</span>
            {help_button}
        </h3>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE DE MÉTRIQUES AVEC UNITÉS
# ================================================================================================

class MetricsWithUnits:
    """Métriques avec unités explicites et tooltips"""
    
    @staticmethod
    def render_metric_with_tooltip(label: str, value: float, unit: str = "", 
                                 tooltip: str = "", delta: float = None):
        """Métrique avec tooltip et unité"""
        
        # Formatage de la valeur avec unité
        if unit == "%":
            display_value = f"{value:.1f}%"
        elif unit == "/90":
            display_value = f"{value:.2f}/90min"
        else:
            display_value = f"{value:.2f}{unit}"
        
        # Delta si fourni
        delta_html = ""
        if delta is not None:
            delta_color = "green" if delta > 0 else "red" if delta < 0 else "gray"
            delta_html = f"""
            <div style='font-size: 0.8em; color: {delta_color}; margin-top: 4px;'>
                {"+" if delta > 0 else ""}{delta:.2f}
            </div>
            """
        
        # Tooltip si fourni
        tooltip_html = ""
        if tooltip:
            tooltip_html = f"""
            <span class='tooltip-trigger'>
                {label} ❓
                <span class='tooltip-content'>{tooltip}</span>
            </span>
            """
        else:
            tooltip_html = label
        
        st.markdown(f"""
        <div class='metric-card-enhanced'>
            <div class='metric-value-enhanced'>{display_value}</div>
            <div class='metric-label-enhanced'>{tooltip_html}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

# ================================================================================================
# GESTIONNAIRE D'ONGLETS AMÉLIORÉ
# ================================================================================================

class EnhancedTabManager:
    """Gestionnaire d'onglets avec améliorations UX/UI"""
    
    @staticmethod
    def render_enhanced_offensive_tab(player_data: pd.Series, df_comparison: pd.DataFrame, selected_player: str):
        """Onglet offensif amélioré"""
        SectionManager.render_section_with_anchor("Performance Offensive", "offensive", "🎯")
        
        analysis = PerformanceAnalyzer.analyze_offensive_performance(player_data, df_comparison)
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Actions offensives avec unités
            basic_actions = {
                'Buts': player_data['Buts'],
                'Passes décisives': player_data['Passes décisives'],
                'Passes clés': player_data['Passes clés'],
                'Tirs': player_data.get('Tirs', 0)
            }
            
            fig_bar = ChartManager.create_bar_chart(
                basic_actions,
                "Actions Offensives Totales",
                AppConfig.COLORS['gradient']
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Métriques avec tooltips
            SectionManager.render_subsection_with_help(
                "Métriques Clés", 
                "Statistiques offensives normalisées par 90 minutes",
                "📊"
            )
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                MetricsWithUnits.render_metric_with_tooltip(
                    "Buts", 
                    analysis['metrics']['Buts/90'], 
                    "/90",
                    "Nombre de buts marqués par 90 minutes de jeu",
                    analysis['metrics']['Buts/90'] - analysis['avg_metrics']['Buts/90']
                )
                MetricsWithUnits.render_metric_with_tooltip(
                    "xG", 
                    analysis['metrics']['xG/90'], 
                    "/90",
                    "Expected Goals - Probabilité de marquer basée sur la qualité des occasions",
                    analysis['metrics']['xG/90'] - analysis['avg_metrics']['xG/90']
                )
            
            with metric_col2:
                MetricsWithUnits.render_metric_with_tooltip(
                    "Passes D.", 
                    analysis['metrics']['Passes D./90'], 
                    "/90",
                    "Passes menant directement à un but par 90 minutes",
                    analysis['metrics']['Passes D./90'] - analysis['avg_metrics']['Passes D./90']
                )
                MetricsWithUnits.render_metric_with_tooltip(
                    "xA", 
                    analysis['metrics']['xA/90'], 
                    "/90",
                    "Expected Assists - Probabilité que les passes mènent à un but",
                    analysis['metrics']['xA/90'] - analysis['avg_metrics']['xA/90']
                )
        
        with col2:
            # Jauges avec unités % explicites
            efficiency_data = {
                'Conversion': (player_data['Buts'] / player_data['Tirs'] * 100) if player_data['Tirs'] > 0 else 0,
                'Précision tirs': player_data.get('Pourcentage de tirs cadrés', 0),
                'Efficacité passes': (player_data['Passes décisives'] / player_data['Passes clés'] * 100) if player_data['Passes clés'] > 0 else 0
            }
            
            fig_gauge = EnhancedChartManager.create_enhanced_gauge_chart(efficiency_data, "Efficacité Offensive (%)")
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Radar avec titre unifié et légende
            SectionManager.render_subsection_with_help(
                "Analyse Radar", 
                "Comparaison en percentiles avec la moyenne de la compétition",
                "🎯"
            )
            
            EnhancedChartManager.render_chart_legend(selected_player, "compétition")
            
            fig_radar = EnhancedChartManager.create_enhanced_radar_chart(
                analysis['metrics'],
                analysis['percentiles'],
                analysis['avg_percentiles'],
                selected_player,
                "compétition",
                AppConfig.COLORS['primary']
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparaison détaillée
        st.markdown("---")
        SectionManager.render_subsection_with_help(
            "Comparaison Détaillée", 
            "Performance par 90 minutes comparée à la moyenne de la compétition",
            "📈"
        )
        
        comparison_metrics = {k: v for k, v in list(analysis['metrics'].items())[:4]}
        avg_comparison = {k: v for k, v in list(analysis['avg_metrics'].items())[:4]}
        
        fig_comp = EnhancedChartManager.create_enhanced_comparison_chart(
            comparison_metrics,
            avg_comparison,
            selected_player,
            "Performance par 90min vs Moyenne de la Compétition"
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# ================================================================================================
# APPLICATION PRINCIPALE AMÉLIORÉE
# ================================================================================================

class EnhancedFootballDashboard:
    """Dashboard football avec toutes les améliorations UX/UI"""
    
    def __init__(self):
        """Initialisation avec améliorations"""
        self._configure_page()
        self._load_enhanced_styles()
        self._initialize_session_state()
    
    def _configure_page(self):
        """Configuration de page améliorée"""
        st.set_page_config(
            page_title="Dashboard Football Pro",
            page_icon="⚽",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def _load_enhanced_styles(self):
        """Chargement des styles améliorés"""
        st.markdown(ImprovedStyleManager.load_improved_css(), unsafe_allow_html=True)
    
    def _initialize_session_state(self):
        """Initialisation des états de session"""
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
        """Exécution principale avec améliorations"""
        # Chargement des données
        with st.spinner("Chargement des données..."):
            df = DataManager.load_data()
        
        if df is None:
            self._render_error_page()
            return
        
        # Statistiques générales
        self._render_data_overview(df)
        
        # En-tête
        UIComponents.render_header()
        
        # Navigation rapide et bouton retour
        EnhancedUIComponents.render_quick_navigation()
        EnhancedUIComponents.render_back_to_top()
        
        # Sidebar et sélections
        selected_competition, selected_player, df_filtered = SidebarManager.render_sidebar(df)
        
        if selected_player:
            # Mise à jour des stats de session
            st.session_state.session_stats['players_viewed'] += 1
            
            # Breadcrumbs
            player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
            NavigationManager.render_breadcrumbs(
                selected_competition, 
                player_data['Équipe'], 
                selected_player
            )
            
            # Carte joueur améliorée
            EnhancedUIComponents.render_enhanced_player_card(player_data, selected_competition)
            
            st.markdown("---")
            
            # Onglets principaux améliorés
            self._render_enhanced_main_tabs(player_data, df_filtered, selected_player, df)
        
        else:
            self._render_no_player_message()
        
        # Footer
        UIComponents.render_footer()
    
    def _render_data_overview(self, df: pd.DataFrame):
        """Aperçu des données amélioré"""
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
    
    def _render_enhanced_main_tabs(self, player_data: pd.Series, df_filtered: pd.DataFrame, 
                                 selected_player: str, df_full: pd.DataFrame):
        """Onglets principaux améliorés"""
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Performance Offensive", 
            "🛡️ Performance Défensive", 
            "🎨 Performance Technique", 
            "🔄 Comparaison"
        ])
        
        with tab1:
            EnhancedTabManager.render_enhanced_offensive_tab(player_data, df_filtered, selected_player)
        
        with tab2:
            # Utiliser la même structure pour les autres onglets
            TabManager.render_defensive_tab(player_data, df_filtered, selected_player)
        
        with tab3:
            TabManager.render_technical_tab(player_data, df_filtered, selected_player)
        
        with tab4:
            TabManager.render_comparison_tab(df_full, selected_player)
    
    def _render_no_player_message(self):
        """Message d'absence de joueur amélioré"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 48px;'>
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
    
    def _render_error_page(self):
        """Page d'erreur améliorée"""
        st.markdown("""
        <div class='dashboard-card animated-card' style='text-align: center; padding: 48px; border-color: var(--danger);'>
            <h1 style='color: var(--danger); margin-bottom: 24px; font-size: 2.5em;'>⚠️ Erreur de Chargement</h1>
            <p style='color: var(--text-primary); font-size: 1.2em; margin-bottom: 32px; line-height: 1.6;'>
                Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Point d'entrée amélioré
def main():
    """Point d'entrée principal amélioré"""
    try:
        dashboard = EnhancedFootballDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Erreur inattendue : {str(e)}")

if __name__ == "__main__":
    main()
