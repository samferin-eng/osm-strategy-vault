import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIG ---
st.set_page_config(page_title="🐍 Guide OSM", layout="wide")
st.title("🐍 Guide OSM")

# --- SUPABASE CONNECTION ---
url = "https://rbzsbemgcuonwvihuwny.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJienNiZW1nY3Vvbnd2aWh1d255Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0ODUzMTMsImV4cCI6MjA5MzA2MTMxM30.-wsKYzQDCTPhNR37fM4RivwR_nGSyf83tBmGmOi_WPE"

supabase = create_client(url, key)

# --- DB FUNCTIONS ---
def insert_match(data):
    return supabase.table("Matchs").insert(data).execute()

def load_data():
    try:
        response = supabase.table("Matchs").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error("LOAD ERROR:")
        st.error(e)
        return pd.DataFrame()

def delete_match(match_id):
    return supabase.table("Matchs").delete().eq("id", match_id).execute()

# --- MENU ---
menu = st.sidebar.radio("Navigation", [
    "🧠 Demander une Tactique",
    "📝 Enregistrer un Match",
    "📊 Historique",
    "📖 Guide & Aide"
])

# --- FORMULAIRE ---
def form(prefix):
    st.subheader("Contexte")

    mon_e = st.text_input("Mon équipe", key=prefix+"_me")
    mon_c = st.number_input("Classement", 1, 20, key=prefix+"_mc")

    adv_n = st.text_input("Adversaire", key=prefix+"_adv")
    adv_co = st.selectbox("Coach", ["Joueur", "IA"], key=prefix+"_coach")

    return {
        "mon_e": mon_e,
        "mon_c": mon_c,
        "adv_n": adv_n,
        "adv_co": adv_co
    }

# --- ONGLET 1 ---
if menu == "🧠 Demander une Tactique":
    st.header("🧠 Analyse")

    df = load_data()
    st.write("DEBUG DATAFRAME:")
    st.write(df)

    res = form("search")

    if st.button("🔍 TEST"):
        if df.empty:
            st.warning("Aucune donnée")
        else:
            victoires = df[df["Resultat"] == "Victoire"]
            st.write(victoires)

# --- ONGLET 2 ---
elif menu == "📝 Enregistrer un Match":
    st.header("📝 Ajouter match")

    res = form("save")

    m_score = st.number_input("Mon score", 0, 20)
    a_score = st.number_input("Score adverse", 0, 20)

    res_fin = st.selectbox("Résultat", ["Victoire","Nul","Défaite"])

    if st.button("💾 SAUVEGARDER"):
        data = {
            "Date": pd.Timestamp.now().strftime("%d/%m/%Y"),
            "Mon_Equipe": res["mon_e"],
            "Mon_Classement": res["mon_c"],
            "Adversaire": res["adv_n"],
            "Type_Coach": res["adv_co"],
            "Mon_Score": m_score,
            "Son_Score": a_score,
            "Resultat": res_fin
        }

        st.write("DEBUG DATA ENVOYÉ:")
        st.write(data)

        try:
            insert_match(data)
            st.success("✅ Inséré dans Supabase")
        except Exception as e:
            st.error("INSERT ERROR:")
            st.error(e)

# --- ONGLET 3 ---
elif menu == "📊 Historique":
    st.header("📊 Historique")

    df = load_data()
    st.dataframe(df)

    match_id = st.number_input("ID à supprimer", 1)

    if st.button("❌ Supprimer"):
        try:
            delete_match(match_id)
            st.success("Supprimé")
            st.rerun()
        except Exception as e:
            st.error(e)

# --- ONGLET 4 ---
else:
    st.header("📖 Guide")
    st.write("Version simplifiée pour debug")
