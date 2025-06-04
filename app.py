import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests
from PIL import Image
import io
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, quote

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Joueur Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("⚽ Dashboard Analyse Joueur Football")
st.markdown("---")

@st.cache_data
def load_data():
    """Charge les données depuis le fichier CSV"""
    try:
        df = pd.read_csv('df_BIG2025.csv')
        return df
    except FileNotFoundError:
        st.error("Fichier 'df_BIG2025.csv' non trouvé. Veuillez vous assurer que le fichier est dans le même répertoire.")
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

@st.cache_data
def search_player_on_fbref(player_name, team_name=None):
    """Recherche un joueur sur FBref et retourne l'URL de sa page"""
    try:
        # Nettoyer le nom du joueur pour la recherche
        clean_name = player_name.strip()
        search_query = quote(clean_name)
        
        # URL de recherche FBref
        search_url = f"https://fbref.com/fr/search/search.fcgi?search={search_query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Chercher les résultats de recherche
            search_results = soup.find_all('div', class_='search-item')
            
            if not search_results:
                # Essayer une autre structure de page
                search_results = soup.find_all('a', href=re.compile(r'/fr/joueurs/'))
            
            for result in search_results[:3]:  # Limiter aux 3 premiers résultats
                if isinstance(result, dict):
                    continue
                    
                # Extraire le lien vers la page du joueur
                link = result.find('a') if result.name != 'a' else result
                if link and link.get('href'):
                    href = link.get('href')
                    if '/joueurs/' in href:
                        full_url = urljoin('https://fbref.com', href)
                        
                        # Vérifier si c'est le bon joueur (optionnel avec équipe)
                        result_text = result.get_text().lower()
                        if clean_name.lower() in result_text:
                            return full_url
            
            # Si pas de résultat direct, essayer avec une recherche Google sur FBref
            return search_with_google_fbref(player_name)
            
    except Exception as e:
        print(f"Erreur lors de la recherche FBref pour {player_name}: {e}")
        return None
    
    return None

@st.cache_data
def search_with_google_fbref(player_name):
    """Recherche alternative via Google pour trouver la page FBref du joueur"""
    try:
        # Construire une requête Google spécifique à FBref
        google_query = f"site:fbref.com {player_name} joueur"
        google_url = f"https://www.google.com/search?q={quote(google_query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(google_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Chercher les liens vers FBref dans les résultats Google
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'fbref.com/fr/joueurs/' in href and '/url?q=' in href:
                    # Extraire l'URL réelle depuis Google
                    real_url = href.split('/url?q=')[1].split('&')[0]
                    if 'fbref.com' in real_url:
                        return real_url
                        
    except Exception as e:
        print(f"Erreur recherche Google pour {player_name}: {e}")
        
    return None

@st.cache_data
def get_player_photo_from_fbref(player_url):
    """Extrait la photo d'un joueur depuis sa page FBref"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(player_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Chercher l'image du joueur - plusieurs sélecteurs possibles
            photo_selectors = [
                'img.headshot',  # Sélecteur principal pour les photos de joueurs
                'div.media-item img',
                'div.player-headshot img',
                'img[alt*="Photo"]',
                'img[src*="headshot"]',
                'img[src*="player"]'
            ]
            
            for selector in photo_selectors:
                img_element = soup.select_one(selector)
                if img_element and img_element.get('src'):
                    img_url = img_element['src']
                    
                    # Construire l'URL complète si nécessaire
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://fbref.com' + img_url
                    
                    # Télécharger l'image
                    img_response = requests.get(img_url, headers=headers, timeout=10)
                    if img_response.status_code == 200:
                        try:
                            image = Image.open(io.BytesIO(img_response.content))
                            # Vérifier que l'image est valide et pas trop petite
                            if image.size[0] > 50 and image.size[1] > 50:
                                return image
                        except Exception:
                            continue
            
            # Si aucune image spécifique trouvée, chercher toutes les images
            all_images = soup.find_all('img')
            for img in all_images:
                src = img.get('src', '')
                alt = img.get('alt', '').lower()
                
                # Filtrer les images qui pourraient être des photos de joueurs
                if any(keyword in src.lower() for keyword in ['headshot', 'player', 'photo']) or \
                   any(keyword in alt for keyword in ['photo', 'headshot', 'player']):
                    
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = 'https://fbref.com' + src
                    
                    try:
                        img_response = requests.get(src, headers=headers, timeout=5)
                        if img_response.status_code == 200:
                            image = Image.open(io.BytesIO(img_response.content))
                            if image.size[0] > 50 and image.size[1] > 50:
                                return image
                    except Exception:
                        continue
                        
    except Exception as e:
        print(f"Erreur lors de l'extraction de la photo depuis {player_url}: {e}")
        
    return None

@st.cache_data
def get_player_photo(player_name, team_name):
    """Tente de récupérer la photo d'un joueur depuis FBref puis d'autres sources"""
    try:
        # Option 1: Photo locale si disponible
        local_path = f"photos/{player_name.replace(' ', '_')}.jpg"
        try:
            image = Image.open(local_path)
            return image
        except:
            pass
        
        # Option 2: Scraping FBref
        st.info(f"🔍 Recherche de la photo de {player_name} sur FBref...")
        
        player_url = search_player_on_fbref(player_name, team_name)
        if player_url:
            st.info(f"📄 Page trouvée, extraction de la photo...")
            photo = get_player_photo_from_fbref(player_url)
            if photo:
                st.success(f"✅ Photo trouvée pour {player_name}")
                return photo
            else:
                st.warning(f"📷 Page trouvée mais pas de photo pour {player_name}")
        else:
            st.warning(f"❌ Aucune page trouvée pour {player_name} sur FBref")
        
        # Option 3: Avatar par défaut
        st.info(f"🎨 Génération d'un avatar par défaut pour {player_name}")
        return create_default_avatar(player_name)
        
    except Exception as e:
        st.error(f"Erreur lors de la récupération de la photo de {player_name}: {str(e)}")
        return create_default_avatar(player_name)

def create_default_avatar(player_name):
    """Crée un avatar par défaut avec les initiales du joueur"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Créer une image 200x200 avec fond coloré
        img = Image.new('RGB', (200, 200), color='#4CAF50')
        draw = ImageDraw.Draw(img)
        
        # Obtenir les initiales
        names = player_name.split()
        if len(names) >= 2:
            initials = names[0][0] + names[-1][0]
        else:
            initials = names[0][:2] if len(names[0]) >= 2 else names[0][0]
        
        initials = initials.upper()
        
        # Dessiner les initiales
        try:
            # Essayer d'utiliser une police par défaut
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        # Centrer le texte
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (200 - text_width) // 2
        y = (200 - text_height) // 2
        
        draw.text((x, y), initials, fill='white', font=font)
        
        return img
        
    except Exception:
        # En cas d'erreur, créer une image simple
        img = Image.new('RGB', (200, 200), color='#2196F3')
        return img

# Chargement des données
df = load_data()

if df is not None:
    # Sidebar pour la sélection
    st.sidebar.header("🎯 Sélection du joueur")
    
    # Sélection de la compétition/ligue
    competitions = sorted(df['Compétition'].dropna().unique())
    selected_competition = st.sidebar.selectbox(
        "Choisir une compétition :",
        competitions,
        index=0
    )
    
    # Filtrer les joueurs selon la compétition
    df_filtered = df[df['Compétition'] == selected_competition]
    
    # Sélection du joueur
    joueurs = sorted(df_filtered['Joueur'].dropna().unique())
    selected_player = st.sidebar.selectbox(
        "Choisir un joueur :",
        joueurs,
        index=0
    )
    
    # Obtenir les données du joueur sélectionné
    player_data = df_filtered[df_filtered['Joueur'] == selected_player].iloc[0]
    
    # Affichage des informations générales du joueur
    st.header(f"📊 Profil de {selected_player}")
    
    # Créer deux colonnes : une pour la photo, une pour les infos
    col_photo, col_info = st.columns([1, 3])
    
    with col_photo:
        # Afficher la photo du joueur avec indicateur de chargement
        with st.spinner("Chargement de la photo..."):
            player_image = get_player_photo(selected_player, player_data['Équipe'])
            st.image(player_image, width=200, caption=selected_player)
    
    with col_info:
        # Informations du joueur en grille
        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
        
        with info_col1:
            st.metric("Âge", f"{player_data['Âge']} ans")
            st.metric("Position", player_data['Position'])
        with info_col2:
            st.metric("Équipe", player_data['Équipe'])
            st.metric("Nationalité", player_data['Nationalité'])
        with info_col3:
            st.metric("Matchs joués", int(player_data['Matchs joués']))
            st.metric("Titularisations", int(player_data['Titularisations']))
        with info_col4:
            st.metric("Minutes jouées", f"{int(player_data['Minutes jouées'])} min")
            st.metric("Buts", int(player_data['Buts']))
    
    st.markdown("---")
    
    # Graphiques principaux
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎯 Performance Offensive", "🛡️ Performance Défensive", "📈 Statistiques Avancées", "⚽ Détails Tirs", "🏃 Activité"])
    
    with tab1:
        st.subheader("Performance Offensive")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique radar des performances offensives
            categories = ['Buts', 'Passes décisives', 'Buts attendus (xG)', 'Passes décisives attendues (xAG)', 'Passes clés']
            values = [
                player_data['Buts'],
                player_data['Passes décisives'],
                player_data['Buts attendus (xG)'],
                player_data['Passes décisives attendues (xAG)'],
                player_data['Passes clés']
            ]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=selected_player,
                line_color='rgb(50, 171, 96)'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(values) * 1.2]
                    )),
                title="Radar - Performance Offensive",
                height=400
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # Graphique buts vs buts attendus
            fig_scatter = go.Figure()
            
            # Tous les joueurs de la compétition
            fig_scatter.add_trace(go.Scatter(
                x=df_filtered['Buts attendus (xG)'],
                y=df_filtered['Buts'],
                mode='markers',
                name='Autres joueurs',
                marker=dict(color='lightblue', size=8, opacity=0.6),
                text=df_filtered['Joueur'],
                hovertemplate='<b>%{text}</b><br>xG: %{x}<br>Buts: %{y}<extra></extra>'
            ))
            
            # Joueur sélectionné
            fig_scatter.add_trace(go.Scatter(
                x=[player_data['Buts attendus (xG)']],
                y=[player_data['Buts']],
                mode='markers',
                name=selected_player,
                marker=dict(color='red', size=15),
                hovertemplate=f'<b>{selected_player}</b><br>xG: %{{x}}<br>Buts: %{{y}}<extra></extra>'
            ))
            
            # Ligne de référence (performance attendue)
            max_xg = df_filtered['Buts attendus (xG)'].max()
            fig_scatter.add_trace(go.Scatter(
                x=[0, max_xg],
                y=[0, max_xg],
                mode='lines',
                name='Performance attendue',
                line=dict(dash='dash', color='gray')
            ))
            
            fig_scatter.update_layout(
                title="Buts marqués vs Buts attendus (xG)",
                xaxis_title="Buts attendus (xG)",
                yaxis_title="Buts marqués",
                height=400
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Métriques offensives par 90 minutes
        st.subheader("Moyennes par 90 minutes")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Buts/90min", f"{player_data['Buts par 90 minutes']:.2f}")
        with col2:
            st.metric("Passes D./90min", f"{player_data['Passes décisives par 90 minutes']:.2f}")
        with col3:
            st.metric("xG/90min", f"{player_data['Buts attendus par 90 minutes']:.2f}")
        with col4:
            st.metric("Actions → Tir/90min", f"{player_data['Actions menant à un tir par 90 minutes']:.2f}")
    
    with tab2:
        st.subheader("Performance Défensive")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique des actions défensives
            actions_def = {
                'Tacles gagnants': player_data['Tacles gagnants'],
                'Interceptions': player_data['Interceptions'],
                'Ballons récupérés': player_data['Ballons récupérés'],
                'Duels aériens gagnés': player_data['Duels aériens gagnés'],
                'Dégagements': player_data['Dégagements']
            }
            
            fig_bar = px.bar(
                x=list(actions_def.keys()),
                y=list(actions_def.values()),
                title="Actions Défensives",
                color=list(actions_def.values()),
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Pourcentages de réussite
            pourcentages = {
                'Duels aériens': player_data['Pourcentage de duels aériens gagnés'],
                'Duels défensifs': player_data['Pourcentage de duels gagnés'],
                'Passes réussies': player_data['Pourcentage de passes réussies']
            }
            
            # Nettoyer les valeurs NaN
            pourcentages = {k: v if pd.notna(v) else 0 for k, v in pourcentages.items()}
            
            fig_gauge = make_subplots(
                rows=1, cols=3,
                specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
                subplot_titles=list(pourcentages.keys())
            )
            
            colors = ['red', 'blue', 'green']
            for i, (metric, value) in enumerate(pourcentages.items()):
                fig_gauge.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=value,
                        gauge=dict(
                            axis=dict(range=[0, 100]),
                            bar=dict(color=colors[i]),
                            bgcolor="white",
                            borderwidth=2,
                            bordercolor="gray"
                        ),
                        number={'suffix': '%'}
                    ),
                    row=1, col=i+1
                )
            
            fig_gauge.update_layout(height=300, title_text="Pourcentages de Réussite")
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    with tab3:
        st.subheader("Statistiques Avancées")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Comparaison avec la moyenne de la compétition
            metrics_comparison = ['Buts par 90 minutes', 'Passes décisives par 90 minutes', 
                                'Buts attendus par 90 minutes', 'Passes décisives attendues par 90 minutes']
            
            player_values = [player_data[metric] for metric in metrics_comparison]
            avg_values = [df_filtered[metric].mean() for metric in metrics_comparison]
            
            fig_comparison = go.Figure()
            
            x_labels = ['Buts/90', 'PD/90', 'xG/90', 'xA/90']
            
            fig_comparison.add_trace(go.Bar(
                name=selected_player,
                x=x_labels,
                y=player_values,
                marker_color='rgb(50, 171, 96)'
            ))
            
            fig_comparison.add_trace(go.Bar(
                name='Moyenne compétition',
                x=x_labels,
                y=avg_values,
                marker_color='rgb(255, 144, 14)'
            ))
            
            fig_comparison.update_layout(
                title='Comparaison avec la moyenne de la compétition',
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        with col2:
            # Temps de jeu et efficacité
            temps_jeu = {
                'Minutes jouées': player_data['Minutes jouées'],
                'Titularisations': player_data['Titularisations'],
                'Matchs complets': player_data['Matches joués en intégralité'],
                'Entrées en jeu': player_data["Nombre d’entrées en jeu"]
            }
            
            fig_pie = px.pie(
                values=[player_data['Minutes jouées'], 
                        (player_data['Matchs joués'] * 90) - player_data['Minutes jouées']],
                names=['Minutes jouées', 'Minutes non jouées'],
                title='Répartition du temps de jeu possible'
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab4:
        st.subheader("Analyse des Tirs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Statistiques de tirs
            tirs_data = {
                'Tirs totaux': player_data['Tirs'],
                'Tirs cadrés': player_data['Tirs cadrés'],
                'Buts marqués': player_data['Buts']
            }
            
            fig_funnel = go.Figure(go.Funnel(
                y=list(tirs_data.keys()),
                x=list(tirs_data.values()),
                textinfo="value+percent initial",
                marker_color=["deepskyblue", "lightsalmon", "lightgreen"]
            ))
            
            fig_funnel.update_layout(
                title="Entonnoir de conversion des tirs",
                height=400
            )
            
            st.plotly_chart(fig_funnel, use_container_width=True)
        
        with col2:
            # Métriques de tir
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric("Tirs/90min", f"{player_data['Tirs par 90 minutes']:.2f}")
                st.metric("% Tirs cadrés", f"{player_data['Pourcentage de tirs cadrés']:.1f}%")
                
            with col_b:
                st.metric("Buts/Tir", f"{player_data['Buts par tir']:.2f}")
                st.metric("Distance moy. tirs", f"{player_data['Distance moyenne des tirs']:.1f}m")
            
            # Comparaison xG vs Buts réels
            st.markdown("#### Efficacité vs Attendu")
            xg_diff = player_data['Buts'] - player_data['Buts attendus (xG)']
            if xg_diff > 0:
                st.success(f"Surperformance: +{xg_diff:.2f} buts vs attendu")
            elif xg_diff < 0:
                st.warning(f"Sous-performance: {xg_diff:.2f} buts vs attendu")
            else:
                st.info("Performance conforme aux attentes")
    
    with tab5:
        st.subheader("Activité et Touches de Balle")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Répartition des touches de balle par zone
            zones_touches = {
                'Surface défensive': player_data['Touches de balle dans la surface défensive'],
                'Tiers défensif': player_data['Touches de balle dans le tiers défensif'],
                'Tiers médian': player_data['Touches de balle dans le tiers médian'],
                'Tiers offensif': player_data['Touches de balle dans le tiers offensif'],
                'Surface offensive': player_data['Touches de balle dans la surface offensive']
            }
            
            fig_zones = px.bar(
                x=list(zones_touches.keys()),
                y=list(zones_touches.values()),
                title="Touches de balle par zone du terrain",
                color=list(zones_touches.values()),
                color_continuous_scale='Blues'
            )
            fig_zones.update_xaxis(tickangle=45)
            fig_zones.update_layout(height=400)
            st.plotly_chart(fig_zones, use_container_width=True)
        
        with col2:
            # Dribbles et portées de balle
            st.markdown("#### Dribbles")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Dribbles tentés", int(player_data['Dribbles tentés']))
                st.metric("% Réussite", f"{player_data['Pourcentage de dribbles réussis']:.1f}%")
            with col_b:
                st.metric("Dribbles réussis", int(player_data['Dribbles réussis']))
                st.metric("Portées de balle", int(player_data['Portées de balle']))
            
            st.markdown("#### Activité générale")
            col_c, col_d = st.columns(2)
            with col_c:
                st.metric("Touches totales", int(player_data['Touches de balle']))
                st.metric("Fautes commises", int(player_data['Fautes commises']))
            with col_d:
                st.metric("Fautes subies", int(player_data['Fautes subies']))
                st.metric("Cartons jaunes", int(player_data['Cartons jaunes']))
    
    # Section de comparaison avec d'autres joueurs
    st.markdown("---")
    st.header("🔄 Comparaison avec d'autres joueurs")
    
    # Sélection de joueurs à comparer
    autres_joueurs = st.multiselect(
        "Sélectionner des joueurs à comparer :",
        [j for j in joueurs if j != selected_player],
        max_selections=3
    )
    
    if autres_joueurs:
        # Créer un dataframe de comparaison
        comparison_players = [selected_player] + autres_joueurs
        comparison_data = df_filtered[df_filtered['Joueur'].isin(comparison_players)]
        
        metrics_to_compare = ['Buts', 'Passes décisives', 'Buts attendus (xG)', 
                             'Passes décisives attendues (xAG)', 'Minutes jouées']
        
        fig_comparison_multi = go.Figure()
        
        for metric in metrics_to_compare:
            fig_comparison_multi.add_trace(go.Bar(
                name=metric,
                x=comparison_data['Joueur'],
                y=comparison_data[metric],
                text=comparison_data[metric].round(2),
                textposition='auto'
            ))
        
        fig_comparison_multi.update_layout(
            title='Comparaison multi-joueurs',
            barmode='group',
            height=500,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_comparison_multi, use_container_width=True)

else:
    st.error("Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.")
    st.info("Ce dashboard nécessite un fichier CSV avec les colonnes spécifiées dans les données fournies.")

# Instructions pour les photos
st.sidebar.markdown("---")
st.sidebar.markdown("### 📸 Sources des photos")
st.sidebar.info("""
**Le système recherche automatiquement :**

1. **📁 Photos locales** (dossier `photos/`)
2. **🌐 FBref.com** (scraping automatique)
3. **🎨 Avatar généré** (initiales)

**Performance :** Le scraping peut prendre quelques secondes la première fois, puis les photos sont mises en cache.
""")

# Bouton pour vider le cache des photos
if st.sidebar.button("🔄 Actualiser les photos"):
    st.cache_data.clear()
    st.experimental_rerun()

# Note sur les performances
st.sidebar.success("✅ Scraping FBref activé - Photos haute qualité")
