import streamlit as st


def accueil():
    st.title("Analyse performance volley")
    st.write("Bienvenue dans l’outil d’analyse.")


def import_data():
    st.title("Import des données")

    file = st.file_uploader("Importer fichier", type=["csv", "xlsx"])

    if file:
        st.success("Fichier chargé")


def analyse():
    st.title("Analyse des performances")
    st.info("Zone future analyse")


def visualisations():
    st.title("Visualisations")
    st.info("Zone future graphs")


def parametres():
    st.title("Paramètres")