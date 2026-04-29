import streamlit as st
import pandas as pd
from supabase import create_client

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="🐍 Guide OSM", layout="wide")
st.title("🐍 Guide OSM - Pro Version")

url = "https://rbzsbemgcuonwvihuwny.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJienNiZW1nY3Vvbnd2aWh1d255Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0ODUzMTMsImV4cCI6MjA5MzA2MTMxM30.-wsKYzQDCTPhNR37fM4RivwR_nGSyf83tBmGmOi_WPE"

supabase = create_client(url, key)

# =====================
# DB FUNCTIONS
# =====================
def insert_match(data):
    return supabase.table("Matchs").insert(data).execute()

def load_data():
    res = supabase.table("Matchs").select("*").execute()
    return pd.DataFrame(res.data)

def delete_match(match_id):
    return supabase.table("Matchs").delete().eq("id", match_id).execute()

# =====================
# FORMULAIRE COMPLET
# =====================
def form(prefix):
    st.subheader("1. Contexte équipe")

    c1, c2, c3 = st.columns(3)
    with c1:
        mon_e = st.text_input("Mon équipe", key=prefix+"_e")
        mon_c = st.number_input("Classement", 1, 20, key=prefix+"_c")
        mon_ch = st.text_input("Championnat", key=prefix+"_ch")

    with c2:
        d_gen = st.number_input("Diff général", key=prefix+"_dg")
        d_att = st.number_input("Diff attaque", key=prefix+"_da")
        d_mil = st.number_input("Diff milieu", key=prefix+"_dm")

    with c3:
        d_def = st.number_input("Diff défense", key=prefix+"_dd")
        d_gar = st.number_input("Diff gardien", key=prefix+"_dgk")
        m_camp = st.checkbox("Mon camp", key=prefix+"_camp")

    st.subheader("2. Adversaire")

    c4, c5, c6 = st.columns(3)
    with c4:
        adv = st.text_input("Adversaire", key=prefix+"_adv")
        coach = st.selectbox("Coach", ["Joueur", "IA"], key=prefix+"_coach")
        adv_cl = st.number_input("Classement adv", 1, 20, key=prefix+"_acl")

    with c5:
        dispo = st.text_input("Dispositif adv", key=prefix+"_disp")
        style = st.text_input("Style adv", key=prefix+"_sty")
        tacles = st.selectbox("Tacles", ["Prudent","Normal","Agressif","Extrême"], key=prefix+"_tac")

    with c6:
        hj = st.selectbox("Hors-jeu", ["Non","Oui"], key=prefix+"_hj")
        marq = st.selectbox("Marquage", ["Zone","Individuel"], key=prefix+"_mar")
        camp_adv = st.checkbox("Camp adverse", key=prefix+"_campadv")

    enjeu = st.text_area("Enjeu", key=prefix+"_enjeu")

    return {
        "mon_e": mon_e,
        "mon_c": mon_c,
        "mon_ch": mon_ch,
        "d_gen": d_gen,
        "d_att": d_att,
        "d_mil": d_mil,
        "d_def": d_def,
        "d_gar": d_gar,
        "mon_camp": m_camp,
        "adv": adv,
        "coach": coach,
        "adv_cl": adv_cl,
        "dispo": dispo,
        "style": style,
        "tacles": tacles,
        "hj": hj,
        "marq": marq,
        "camp_adv": camp_adv,
        "enjeu": enjeu
    }

# =====================
# MENU
# =====================
menu = st.sidebar.radio("Navigation", [
    "🧠 Tactique IA",
    "📝 Enregistrer",
    "📊 Historique",
    "📖 Guide"
])

# =====================
# 1. IA TACTIQUE
# =====================
if menu == "🧠 Tactique IA":
    st.header("🧠 Analyse des matchs")

    df = load_data()
    st.dataframe(df)

    form_data = form("ia")

    if st.button("🔍 Analyser"):
        if df.empty:
            st.warning("Aucune donnée")
        else:
            wins = df[df["Resultat"] == "Victoire"]
            st.write("Matchs gagnés :", len(wins))

# =====================
# 2. AJOUT MATCH
# =====================
elif menu == "📝 Enregistrer":
    st.header("📝 Ajouter un match")

    data = form("save")

    st.subheader("Résultat")

    score_me = st.number_input("Mon score", 0, 20)
    score_adv = st.number_input("Score adverse", 0, 20)
    result = st.selectbox("Résultat", ["Victoire","Nul","Défaite"])

    if st.button("💾 Sauvegarder"):
        payload = {
            "Date": pd.Timestamp.now().strftime("%d/%m/%Y"),
            "Mon_Equipe": data["mon_e"],
            "Mon_Classement": data["mon_c"],
            "Mon_Champ": data["mon_ch"],
            "Diff_Gen": data["d_gen"],
            "Diff_Att": data["d_att"],
            "Diff_Mil": data["d_mil"],
            "Diff_Def": data["d_def"],
            "Diff_Gar": data["d_gar"],
            "Mon_Camp": data["mon_camp"],
            "Adversaire": data["adv"],
            "Type_Coach": data["coach"],
            "Son_Classement": data["adv_cl"],
            "Adv_Dispo": data["dispo"],
            "Adv_Style": data["style"],
            "Adv_Tacles": data["tacles"],
            "Adv_HJ": data["hj"],
            "Adv_Marquage": data["marq"],
            "Adv_Camp": data["camp_adv"],
            "Enjeu": data["enjeu"],
            "Mon_Score": score_me,
            "Son_Score": score_adv,
            "Resultat": result
        }

        insert_match(payload)
        st.success("Match enregistré ✔️")
        st.rerun()

# =====================
# 3. HISTORIQUE
# =====================
elif menu == "📊 Historique":
    st.header("📊 Historique")

    df = load_data()
    st.dataframe(df)

    st.subheader("🗑️ Supprimer")

    match_id = st.number_input("ID match", 1)

    if st.button("Supprimer"):
        delete_match(match_id)
        st.success("Supprimé")
        st.rerun()

# =====================
# 4. GUIDE
# =====================
else:
    st.header("📖 Guide tactique")

    st.write("""
- Défensif : 5-4-1 / 5-3-2  
- Équilibré : 4-2-3-1 / 4-4-2  
- Offensif : 4-3-3 / 3-4-3  

Règle : adapter selon niveau adversaire + style + arbitre.
""")
