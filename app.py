import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Serpentard Strategy Vault", page_icon="🐍", layout="wide")

CSV_FILE = "osm_pro_history.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["Date", "Adversaire", "Tactique Adv", "Ma Tactique", "Résultat", "Note"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# --- INTERFACE ---
st.title("🐍 Serpentard Strategy Vault")

tab1, tab2, tab3 = st.tabs(["📝 Enregistrer", "📊 Historique", "⚙️ Gestion"])

with tab1:
    st.subheader("Enregistrer un match")
    with st.form("match_form"):
        adv = st.text_input("Nom de l'adversaire")
        tactic_adv = st.selectbox("Sa tactique", ["433A", "433B", "442A", "442B", "532", "541", "451", "4231", "343", "3322"])
        my_tactic = st.text_input("Ma tactique utilisée")
        res = st.selectbox("Résultat", ["Victoire", "Nul", "Défaite"])
        note = st.text_area("Notes (Détails, scores...)")
        
        submitted = st.form_submit_button("SAUVEGARDER")
        if submitted:
            new_data = {
                "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Adversaire": adv,
                "Tactique Adv": tactic_adv,
                "Ma Tactique": my_tactic,
                "Résultat": res,
                "Note": note
            }
            df = load_data()
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            save_data(df)
            st.success("Match enregistré avec succès !")

with tab2:
    st.subheader("Historique des batailles")
    df = load_data()
    if not df.empty:
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("Aucun match enregistré.")

with tab3:
    st.subheader("Supprimer une erreur")
    df = load_data()
    if not df.empty:
        # On crée une liste de matchs pour le menu déroulant
        match_list = df.apply(lambda x: f"{x['Date']} - vs {x['Adversaire']}", axis=1).tolist()
        match_to_delete = st.selectbox("Choisir le match à supprimer", match_list)
        
        if st.button("❌ SUPPRIMER DÉFINITIVEMENT"):
            index_to_drop = match_list.index(match_to_delete)
            df = df.drop(df.index[index_to_drop])
            save_data(df)
            st.warning("Match supprimé. La page va s'actualiser.")
            st.rerun()
    else:
        st.write("Rien à supprimer.")
