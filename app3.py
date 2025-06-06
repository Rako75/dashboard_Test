import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Analyse de Données Football",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stSelectbox label {
        font-weight: bold;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charge et traite les données de football"""
    try:
        # Charger le fichier CSV
        df = pd.read_csv('df_BIG2025.csv')
        
        # Nettoyer les données
        df = df.dropna(subset=['Joueur', 'Compétition'])
        
        # Convertir les colonnes numériques
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remplacer les valeurs manquantes par 0 pour les colonnes numériques
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame()

def get_statistic_columns(df):
    """Retourne les colonnes de statistiques importantes"""
    exclude_cols = ['', 'Joueur', 'Nationalité', 'Position', 'Équipe', 'Compétition', 'Âge', 'Année de naissance']
    return [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['int64', 'float64']]

def create_scatter_plot(df, x_col, y_col, color_by='Compétition', top_n=10):
    """Crée un graphique de dispersion interactif"""
    fig = px.scatter(
        df, 
        x=x_col, 
        y=y_col,
        color=color_by,
        hover_data=['Joueur', 'Équipe', 'Position', 'Minutes jouées'],
        title=f"Analyse: {x_col} vs {y_col}",
        height=600
    )
    
    # Ajouter les labels pour les top joueurs
    if top_n > 0:
        # Calculer un score composite pour identifier les joueurs à labeler
        df_copy = df.copy()
        df_copy['composite_score'] = df_copy[x_col] + df_copy[y_col]
        top_players = df_copy.nlargest(top_n, 'composite_score')
        
        for _, player in top_players.iterrows():
            fig.add_annotation(
                x=player[x_col],
                y=player[y_col],
                text=player['Joueur'],
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=1,
                arrowcolor="black",
                font=dict(size=10, color="black"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="black",
                borderwidth=1
            )
    
    fig.update_layout(
        template="plotly_white",
        font=dict(size=12),
        title_x=0.5,
        showlegend=True
    )
    
    return fig

def create_histogram(df, column, title):
    """Crée un histogramme pour une colonne donnée"""
    fig = px.histogram(
        df, 
        x=column, 
        nbins=20,
        title=f"Distribution: {title}",
        color_discrete_sequence=['#3498db']
    )
    
    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        showlegend=False
    )
    
    return fig

def create_top_players_table(df, column, n=5):
    """Crée un tableau des top joueurs pour une statistique"""
    top_players = df.nlargest(n, column)[['Joueur', 'Équipe', 'Compétition', column]]
    top_players = top_players.reset_index(drop=True)
    top_players.index = top_players.index + 1
    return top_players

def main():
    # Titre principal
    st.markdown('<h1 class="main-header">⚽ Analyse de Données Football 2024/25</h1>', unsafe_allow_html=True)
    
    # Charger les données
    with st.spinner('Chargement des données...'):
        df = load_data()
    
    if df.empty:
        st.error("Impossible de charger les données. Assurez-vous que le fichier 'df_BIG2025.csv' est présent.")
        return
    
    # Sidebar pour les contrôles
    st.sidebar.header("🎛️ Paramètres d'Analyse")
    
    # Obtenir les colonnes de statistiques
    stat_columns = get_statistic_columns(df)
    
    # Sélection des statistiques
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        x_stat = st.selectbox(
            "📊 Statistique X:",
            stat_columns,
            index=stat_columns.index('Buts par 90 minutes') if 'Buts par 90 minutes' in stat_columns else 0
        )
    
    with col2:
        y_stat = st.selectbox(
            "📈 Statistique Y:",
            stat_columns,
            index=stat_columns.index('Passes décisives par 90 minutes') if 'Passes décisives par 90 minutes' in stat_columns else 1
        )
    
    # Filtres
    st.sidebar.subheader("🔍 Filtres")
    
    # Minutes minimum
    min_minutes = st.sidebar.slider(
        "Minutes minimum jouées:",
        min_value=0,
        max_value=int(df['Minutes jouées'].max()),
        value=90,
        step=90
    )
    
    # Sélection des compétitions
    all_competitions = df['Compétition'].unique().tolist()
    selected_competitions = st.sidebar.multiselect(
        "Compétitions:",
        all_competitions,
        default=all_competitions
    )
    
    # Nombre de joueurs à labeler
    num_labels = st.sidebar.slider(
        "Nombre de joueurs étiquetés:",
        min_value=0,
        max_value=20,
        value=5
    )
    
    # Option de couleur
    color_option = st.sidebar.selectbox(
        "Colorier par:",
        ['Compétition', 'Position', 'Équipe']
    )
    
    # Filtrer les données
    filtered_df = df[
        (df['Minutes jouées'] >= min_minutes) & 
        (df['Compétition'].isin(selected_competitions))
    ].copy()
    
    # Retirer les valeurs non-numériques pour les statistiques sélectionnées
    filtered_df = filtered_df.dropna(subset=[x_stat, y_stat])
    
    # Métriques principales
    if not filtered_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Joueurs filtrés", len(filtered_df))
        
        with col2:
            st.metric("🏆 Compétitions", len(selected_competitions))
        
        with col3:
            st.metric(f"🎯 Max {x_stat[:20]}...", f"{filtered_df[x_stat].max():.2f}")
        
        with col4:
            st.metric(f"⭐ Max {y_stat[:20]}...", f"{filtered_df[y_stat].max():.2f}")
        
        # Graphique principal
        st.subheader("📊 Graphique de Dispersion Principal")
        scatter_fig = create_scatter_plot(filtered_df, x_stat, y_stat, color_option, num_labels)
        st.plotly_chart(scatter_fig, use_container_width=True)
        
        # Histogrammes
        st.subheader("📈 Distribution des Statistiques")
        col1, col2 = st.columns(2)
        
        with col1:
            hist_x = create_histogram(filtered_df, x_stat, x_stat)
            st.plotly_chart(hist_x, use_container_width=True)
        
        with col2:
            hist_y = create_histogram(filtered_df, y_stat, y_stat)
            st.plotly_chart(hist_y, use_container_width=True)
        
        # Tableaux Top 5
        st.subheader("🏅 Top 5 Joueurs")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Top 5 - {x_stat}**")
            top_x = create_top_players_table(filtered_df, x_stat)
            st.dataframe(top_x, use_container_width=True)
        
        with col2:
            st.write(f"**Top 5 - {y_stat}**")
            top_y = create_top_players_table(filtered_df, y_stat)
            st.dataframe(top_y, use_container_width=True)
        
        # Statistiques avancées
        with st.expander("📊 Statistiques Avancées"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Moyenne X", f"{filtered_df[x_stat].mean():.2f}")
                st.metric("Médiane X", f"{filtered_df[x_stat].median():.2f}")
            
            with col2:
                st.metric("Moyenne Y", f"{filtered_df[y_stat].mean():.2f}")
                st.metric("Médiane Y", f"{filtered_df[y_stat].median():.2f}")
            
            with col3:
                correlation = filtered_df[x_stat].corr(filtered_df[y_stat])
                st.metric("Corrélation", f"{correlation:.3f}")
                
                # Interprétation de la corrélation
                if abs(correlation) > 0.7:
                    st.success("Corrélation forte")
                elif abs(correlation) > 0.3:
                    st.warning("Corrélation modérée")
                else:
                    st.info("Corrélation faible")
        
        # Données détaillées
        with st.expander("🔍 Données Détaillées"):
            st.dataframe(
                filtered_df[['Joueur', 'Équipe', 'Compétition', 'Position', x_stat, y_stat, 'Minutes jouées']],
                use_container_width=True
            )
            
            # Bouton de téléchargement
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les données filtrées (CSV)",
                data=csv,
                file_name=f"football_analysis_{x_stat}_{y_stat}.csv",
                mime="text/csv"
            )
    
    else:
        st.warning("Aucune donnée ne correspond aux filtres sélectionnés. Veuillez ajuster vos paramètres.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        <p>🚀 Application créée avec Streamlit | 📊 Données saison 2024/25</p>
        <p>Analysez plus de 160 statistiques de football de manière interactive</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
