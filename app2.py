import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("df_BIG2025.csv")
    return df

df = load_data()

# Titre du dashboard
st.title("📊 Dashboard Interactif - Analyse d'un Joueur")

# Sélection de la compétition
competitions = df["Compétition"].dropna().unique()
selected_league = st.selectbox("Choisir une ligue :", sorted(competitions))

# Filtrage par ligue
df_league = df[df["Compétition"] == selected_league]

# Sélection du joueur
players = df_league["Joueur"].dropna().unique()
selected_player = st.selectbox("Choisir un joueur :", sorted(players))

# Filtrage par joueur
player_data = df_league[df_league["Joueur"] == selected_player].iloc[0]

# Affichage de quelques stats clés
st.subheader("📌 Statistiques principales")
st.markdown(f"""
- **Âge** : {player_data['Âge']}
- **Position** : {player_data['Position']}
- **Équipe** : {player_data['Équipe']}
- **Matchs joués** : {player_data['Matchs joués']}
- **Minutes jouées** : {player_data['Minutes jouées']}
""")

# Graphique 1 : Répartition buts / passes décisives
st.subheader("⚽ Répartition Buts / Passes décisives")
fig1, ax1 = plt.subplots()
ax1.pie(
    [player_data['Buts'], player_data['Passes décisives']],
    labels=['Buts', 'Passes décisives'],
    autopct='%1.1f%%',
    startangle=90,
    colors=['#ff9999','#66b3ff']
)
ax1.axis('equal')
st.pyplot(fig1)

# Graphique 2 : Comparaison stats offensives par 90 min
st.subheader("📈 Stats offensives par 90 minutes")
stats_off = {
    "Buts/90": player_data["Buts par 90 minutes"],
    "Passes D/90": player_data["Passes décisives par 90 minutes"],
    "xG/90": player_data["Buts attendus par 90 minutes"],
    "xA/90": player_data["Passes décisives attendues par 90 minutes"],
}
fig2 = px.bar(x=list(stats_off.keys()), y=list(stats_off.values()), labels={"x": "Stat", "y": "Valeur"}, color=list(stats_off.keys()))
st.plotly_chart(fig2)

# Graphique 3 : Activité défensive
st.subheader("🛡️ Activité défensive")
defense_stats = {
    "Tacles réussis": player_data["Tacles réussis"],
    "Interceptions": player_data["Interceptions"],
    "Duels gagnés": player_data["Duels défensifs gagnés"],
    "Tirs bloqués": player_data["Tirs bloqués"]
}
fig3 = px.bar(x=list(defense_stats.keys()), y=list(defense_stats.values()), labels={"x": "Stat", "y": "Valeur"}, color=list(defense_stats.keys()))
st.plotly_chart(fig3)

# Graphique 4 : Radar offensif
st.subheader("🎯 Radar offensif")
from math import pi

categories = ['Buts/90', 'Passes D/90', 'xG/90', 'xA/90', 'Tirs/90', 'Dribbles réussis']
values = [
    player_data["Buts par 90 minutes"],
    player_data["Passes décisives par 90 minutes"],
    player_data["Buts attendus par 90 minutes"],
    player_data["Passes décisives attendues par 90 minutes"],
    player_data["Tirs par 90 minutes"],
    player_data["Dribbles réussis"]
]

values += values[:1]  # Boucle pour le radar
angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
angles += angles[:1]

fig4, ax4 = plt.subplots(subplot_kw={'polar': True})
ax4.plot(angles, values, linewidth=2, linestyle='solid')
ax4.fill(angles, values, alpha=0.3)
ax4.set_xticks(angles[:-1])
ax4.set_xticklabels(categories)
st.pyplot(fig4)

# Footer
st.markdown("---")
st.markdown("📊 Créé avec ❤️ par ChatGPT – Données : df_BIG2025")
