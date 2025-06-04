import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from mplsoccer import PyPizza, FontManager
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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

# ---------------------- PARAMÈTRES DU RADAR ----------------------

RAW_STATS = {
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

COLOR_1 = "#1A78CF"
COLOR_2 = "#FF9300"
SLICE_COLORS = [COLOR_1] * len(RAW_STATS)

def calculate_percentiles(player_name, df):
    """Calcule les percentiles pour le pizza chart"""
    player = df[df["Joueur"] == player_name].iloc[0]
    percentiles = []

    for label, col in RAW_STATS.items():
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
                if player.get("Matchs en 90 min", 0) == 0:
                    # Utiliser les matchs joués si "Matchs en 90 min" n'existe pas
                    matches = player.get("Matchs joués", 1)
                    if matches == 0:
                        percentile = 0
                    else:
                        val = player[col] / matches
                        dist = df[col] / df.get("Matchs joués", 1)
                        if pd.isna(val) or dist.dropna().empty:
                            percentile = 0
                        else:
                            percentile = round((dist < val).mean() * 100)
                else:
                    val = player[col] / player["Matchs en 90 min"]
                    dist = df[col] / df["Matchs en 90 min"]
                    if pd.isna(val) or dist.dropna().empty:
                        percentile = 0
                    else:
                        percentile = round((dist < val).mean() * 100)
        except Exception as e:
            percentile = 0
        percentiles.append(percentile)

    return percentiles

@st.cache_data
def load_data():
    """Charge les données depuis le fichier CSV"""
    try:
        df = pd.read_csv('df_BIG2025.csv', encoding='utf-8')
        return df
    except FileNotFoundError:
        st.error("Fichier 'df_BIG2025.csv' non trouvé. Veuillez vous assurer que le fichier est dans le même répertoire.")
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {str(e)}")
        return None

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
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Âge", f"{player_data['Âge']} ans")
    with col2:
        st.metric("Position", player_data['Position'])
    with col3:
        st.metric("Équipe", player_data['Équipe'])
    with col4:
        st.metric("Nationalité", player_data['Nationalité'])
    with col5:
        st.metric("Matchs joués", int(player_data['Matchs joués']))
    
    st.markdown("---")
    
    # Graphiques principaux
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎯 Performance Offensive", "🛡️ Performance Défensive", "📈 Statistiques Avancées", "⚽ Détails Tirs", "🏃 Activité", "🔄 Comparer Joueurs"])
    
    with tab1:
        st.subheader("Performance Offensive")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique heatmap des contributions offensives
            contribution_data = {
                'Buts': player_data['Buts'],
                'Passes décisives': player_data['Passes décisives'],
                'Passes clés': player_data['Passes clés'],
                'Actions → Tir': player_data.get('Actions menant à un tir', 0),
                'Passes dernier tiers': player_data.get('Passes dans le dernier tiers', 0)
            }
            
            # Normaliser les valeurs pour créer une heatmap
            max_val = max(contribution_data.values()) if max(contribution_data.values()) > 0 else 1
            normalized_values = [v/max_val for v in contribution_data.values()]
            
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=[normalized_values],
                x=list(contribution_data.keys()),
                y=['Contribution'],
                colorscale='Viridis',
                showscale=True,
                text=[[f"{v}" for v in contribution_data.values()]],
                texttemplate="%{text}",
                textfont={"size": 14, "color": "white"}
            ))
            
            fig_heatmap.update_layout(
                title="Heatmap - Contributions Offensives",
                height=300,
                xaxis=dict(tickangle=45)
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Graphique en aires empilées pour l'évolution offensive
            offensive_metrics = ['Buts', 'Passes décisives', 'Passes clés']
            fig_area = go.Figure()
            
            for i, metric in enumerate(offensive_metrics):
                fig_area.add_trace(go.Scatter(
                    x=[0, 1],
                    y=[0, player_data[metric]],
                    fill='tonexty' if i > 0 else 'tozeroy',
                    mode='lines',
                    name=metric,
                    line=dict(width=0.5),
                ))
            
            fig_area.update_layout(
                title="Répartition des Contributions Offensives",
                xaxis=dict(showticklabels=False),
                yaxis_title="Valeurs",
                height=300
            )
            
            st.plotly_chart(fig_area, use_container_width=True)
        
        with col2:
            # Graphique buts vs buts attendus (conservé)
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
                'Entrées en jeu': player_data["Nombre d'entrées en jeu"]
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
            fig_zones.update_layout(
                xaxis={'tickangle': 45},
                height=400
            )
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
    
    with tab6:
        st.subheader("🔄 Comparaison Pizza Chart")
        
        # Choix du mode
        mode = st.radio("Mode de visualisation", ["Radar individuel", "Radar comparatif"], horizontal=True)
        
        font_normal = FontManager()
        font_bold = FontManager()
        font_italic = FontManager()
        
        if mode == "Radar individuel":
            st.subheader(f"🎯 Radar individuel : {selected_player}")
            
            try:
                values1 = calculate_percentiles(selected_player, df_filtered)
                
                baker = PyPizza(
                    params=list(RAW_STATS.keys()),
                    background_color="#132257",
                    straight_line_color="#000000",
                    straight_line_lw=1,
                    last_circle_color="#000000",
                    last_circle_lw=1,
                    other_circle_lw=0,
                    inner_circle_size=11
                )
                
                fig, ax = baker.make_pizza(
                    values1,
                    figsize=(10, 12),
                    param_location=110,
                    color_blank_space="same",
                    slice_colors=SLICE_COLORS,
                    value_colors=["#ffffff"] * len(values1),
                    value_bck_colors=SLICE_COLORS,
                    kwargs_slices=dict(edgecolor="#000000", zorder=2, linewidth=1),
                    kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop),
                    kwargs_values=dict(color="#ffffff", fontsize=11, fontproperties=font_normal.prop,
                                       bbox=dict(edgecolor="#000000", facecolor=COLOR_1, boxstyle="round,pad=0.2", lw=1))
                )
                
                fig.text(0.515, 0.95, selected_player, size=24, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                fig.text(0.515, 0.925, "Radar Individuel | Percentile | Saison 2024-25", size=13,
                         ha="center", fontproperties=font_bold.prop, color="#ffffff")
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Erreur lors de la création du radar individuel : {str(e)}")
        
        elif mode == "Radar comparatif":
            col1, col2 = st.columns(2)
            
            with col1:
                ligue1 = st.selectbox("Ligue Joueur 1", competitions, 
                                     index=competitions.index(selected_competition), key="ligue1_comp")
                df_j1 = df[df['Compétition'] == ligue1]
                joueur1 = st.selectbox("Joueur 1", df_j1['Joueur'].sort_values(), 
                                      index=list(df_j1['Joueur'].sort_values()).index(selected_player), key="joueur1_comp")
            
            with col2:
                ligue2 = st.selectbox("Ligue Joueur 2", competitions, key="ligue2_comp")
                df_j2 = df[df['Compétition'] == ligue2]
                joueur2 = st.selectbox("Joueur 2", df_j2['Joueur'].sort_values(), key="joueur2_comp")
            
            if joueur1 and joueur2:
                st.subheader(f"⚔️ Radar comparatif : {joueur1} vs {joueur2}")
                
                try:
                    values1 = calculate_percentiles(joueur1, df_j1)
                    values2 = calculate_percentiles(joueur2, df_j2)
                    
                    params_offset = [False] * len(RAW_STATS)
                    if len(params_offset) > 9:
                        params_offset[9] = True
                    if len(params_offset) > 10:
                        params_offset[10] = True
                    
                    baker = PyPizza(
                        params=list(RAW_STATS.keys()),
                        background_color="#132257",
                        straight_line_color="#000000",
                        straight_line_lw=1,
                        last_circle_color="#000000",
                        last_circle_lw=1,
                        other_circle_ls="-.",
                        other_circle_lw=1
                    )
                    
                    fig, ax = baker.make_pizza(
                        values1,
                        compare_values=values2,
                        figsize=(10, 10),
                        kwargs_slices=dict(facecolor=COLOR_1, edgecolor="#222222", linewidth=1, zorder=2),
                        kwargs_compare=dict(facecolor=COLOR_2, edgecolor="#222222", linewidth=1, zorder=2),
                        kwargs_params=dict(color="#ffffff", fontsize=13, fontproperties=font_bold.prop),
                        kwargs_values=dict(
                            color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                            bbox=dict(edgecolor="#000000", facecolor=COLOR_1, boxstyle="round,pad=0.2", lw=1)
                        ),
                        kwargs_compare_values=dict(
                            color="#ffffff", fontsize=11, fontproperties=font_normal.prop, zorder=3,
                            bbox=dict(edgecolor="#000000", facecolor=COLOR_2, boxstyle="round,pad=0.2", lw=1)
                        )
                    )
                    
                    try:
                        baker.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)
                    except:
                        pass  # Si la méthode n'existe pas, on continue sans ajustement
                    
                    fig.text(0.515, 0.99, f"{joueur1} vs {joueur2}", size=24, ha="center",
                             fontproperties=font_bold.prop, color="#ffffff")
                    
                    fig.text(0.515, 0.955, "Radar comparatif | Percentile | Saison 2024-25",
                             size=13, ha="center", fontproperties=font_bold.prop, color="#ffffff")
                    
                    legend_p1 = mpatches.Patch(color=COLOR_1, label=joueur1)
                    legend_p2 = mpatches.Patch(color=COLOR_2, label=joueur2)
                    ax.legend(handles=[legend_p1, legend_p2], loc="upper right", bbox_to_anchor=(1.3, 1.0))
                    
                    fig.text(0.99, 0.01, "Réalisé par : @AlexRakotomalala \nSource: FBRef\nInspiration: @Worville, @FootballSlices",
                             size=8, ha="right", fontproperties=font_italic.prop, color="#dddddd")
                    
                    st.pyplot(fig)
                    
                except Exception as e:
                    st.error(f"Erreur lors de la création du radar comparatif : {str(e)}")
                    st.info("Vérifiez que les colonnes nécessaires sont présentes dans vos données.")

else:
    st.error("Impossible de charger les données. Veuillez vérifier que le fichier 'df_BIG2025.csv' est présent.")
    st.info("Ce dashboard nécessite un fichier CSV avec les colonnes spécifiées dans les données fournies.")
