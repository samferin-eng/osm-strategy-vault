import streamlit as st
import pandas as pd
from supabase import create_client

st.write(supabase.table("Matchs").select("*").execute())

# --- CONFIGURATION ---
st.set_page_config(page_title="🐍 Guide OSM", layout="wide")
st.title("🐍 Guide OSM")

# --- SUPABASE CONNECTION ---
url = "https://rbzsbemgcuonwvihuwny.supabase.co"
key = "TA_CLE_ANON_SUPABASE_ICI"

supabase = create_client(url, key)

# --- DB FUNCTIONS ---
def insert_match(data):
    supabase.table("Matchs").insert(data).execute()

def load_data():
    response = supabase.table("Matchs").select("*").execute()
    return pd.DataFrame(response.data)

def delete_match(match_id):
    supabase.table("Matchs").delete().eq("id", match_id).execute()

# --- MENU ---
menu = st.sidebar.radio("Navigation", [
    "🧠 Demander une Tactique",
    "📝 Enregistrer un Match",
    "📊 Historique",
    "📖 Guide & Aide"
])

# --- FORMULAIRE ---
def afficher_formulaire_complet(prefix):
    st.subheader("1. Contexte & Niveaux")
    f1, f2, f3 = st.columns(3)
    with f1:
        mon_e = st.text_input("Mon équipe", "Troyes", key=f"{prefix}_me")
        mon_c = st.number_input("Mon classement", 1, 20, key=f"{prefix}_mc")
        mon_ch = st.text_input("Mon championnat", key=f"{prefix}_mch")
    with f2:
        d_gen = st.number_input("Diff. Général", value=0, key=f"{prefix}_dg")
        d_att = st.number_input("Diff. Attaque", value=0, key=f"{prefix}_da")
        d_mil = st.number_input("Diff. Milieu", value=0, key=f"{prefix}_dm")
    with f3:
        d_def = st.number_input("Diff. Défense", value=0, key=f"{prefix}_dd")
        d_gar = st.number_input("Diff. Gardien", value=0, key=f"{prefix}_dga")
        m_camp = st.checkbox("Mon Camp d'entrainement", key=f"{prefix}_mcp")

    st.subheader("2. Conditions & Adversaire")
    f4, f5, f6 = st.columns(3)
    with f4:
        lieu = st.selectbox("Lieu (D/E)", ["D", "E"], key=f"{prefix}_li")
        stade = st.slider("Niveau Stade", 0, 3, key=f"{prefix}_st")
        arb = st.selectbox("Arbitre", ["V", "B", "J", "O", "R"], key=f"{prefix}_ar")
    with f5:
        adv_n = st.text_input("Adversaire", key=f"{prefix}_an")
        adv_co = st.selectbox("Coach", ["Joueur", "IA"], key=f"{prefix}_ac")
        adv_cl = st.number_input("Classement adverse", 1, 20, key=f"{prefix}_acl")
    with f6:
        a_dis = st.text_input("Dispositif adverse", key=f"{prefix}_ad")
        a_sty = st.text_input("Style adverse", key=f"{prefix}_as")
        a_tac = st.selectbox("Tacles", ["Prudent", "Normal", "Agressif", "Extrême"], key=f"{prefix}_at")
        a_hj = st.selectbox("Hors-jeu", ["Non", "Oui"], key=f"{prefix}_ah")
        a_mar = st.selectbox("Marquage", ["Zone", "Individuel"], key=f"{prefix}_am")
        a_camp = st.checkbox("Camp adverse", key=f"{prefix}_acp")

    enjeu = st.text_area("Enjeu", key=f"{prefix}_enj")

    return locals()

# --- ONGLET 1 ---
if menu == "🧠 Demander une Tactique":
    st.header("🧠 Analyseur")

    df = load_data()
    if df.empty:
        df = pd.DataFrame()

    res = afficher_formulaire_complet("search")

    if st.button("🔍 TROUVER"):
        if df.empty:
            st.warning("Aucune donnée")
        else:
            victoires = df[df['Resultat'] == 'Victoire']
            filtres = victoires[
                (victoires['Adv_Dispo'] == res['a_dis']) &
                (victoires['Type_Coach'] == res['adv_co'])
            ]

            if not filtres.empty:
                last = filtres.iloc[-1]
                st.success(f"Victoire {last['Mon_Score']}-{last['Son_Score']}")
                st.write(last[['Ma_Tactique','Mon_Style','Mon_Pres','Ma_Ment','Mon_Temp']])
            else:
                st.error("Aucune donnée")

# --- ONGLET 2 ---
elif menu == "📝 Enregistrer un Match":
    st.header("📝 Enregistrer")

    res = afficher_formulaire_complet("save")

    st.subheader("Tactique")
    ma_tac = st.text_input("Dispositif")
    ma_sty = st.text_input("Style")
    m_pre = st.number_input("Pressing", 0, 99, 50)
    m_men = st.number_input("Mentalité", 0, 99, 50)
    m_tem = st.number_input("Tempo", 0, 99, 50)

    st.subheader("Score")
    m_score = st.number_input("Mon Score", 0, 20)
    a_score = st.number_input("Score adverse", 0, 20)
    res_fin = st.selectbox("Résultat", ["Victoire","Nul","Défaite"])
    t_pour = st.number_input("Tirs pour")
    t_contre = st.number_input("Tirs contre")
    poss = st.slider("Possession",0,100)

    if st.button("💾 SAUVEGARDER"):
        data = {
            "Date": pd.Timestamp.now().strftime("%d/%m/%Y"),
            "Mon_Equipe": res['mon_e'],
            "Mon_Classement": res['mon_c'],
            "Mon_Champ": res['mon_ch'],
            "Diff_Gen": res['d_gen'],
            "Diff_Att": res['d_att'],
            "Diff_Mil": res['d_mil'],
            "Diff_Def": res['d_def'],
            "Diff_Gar": res['d_gar'],
            "Mon_Camp": res['m_camp'],
            "Lieu": res['lieu'],
            "Niveau_Stade": res['stade'],
            "Arbitre": res['arb'],
            "Adversaire": res['adv_n'],
            "Type_Coach": res['adv_co'],
            "Son_Classement": res['adv_cl'],
            "Adv_Dispo": res['a_dis'],
            "Adv_Style": res['a_sty'],
            "Adv_Tacles": res['a_tac'],
            "Adv_HJ": res['a_hj'],
            "Adv_Marquage": res['a_mar'],
            "Adv_Camp": res['a_camp'],
            "Enjeu": res['enjeu'],
            "Mon_Score": m_score,
            "Son_Score": a_score,
            "Resultat": res_fin,
            "Tirs_Pour": t_pour,
            "Tirs_Contre": t_contre,
            "Possession": poss,
            "Ma_Tactique": ma_tac,
            "Mon_Style": ma_sty,
            "Mon_Pres": m_pre,
            "Ma_Ment": m_men,
            "Mon_Temp": m_tem
        }

        insert_match(data)
        st.success("✅ Match enregistré définitivement")
        st.rerun()

# --- ONGLET 3 ---
elif menu == "📊 Historique":
    st.header("📊 Historique")

    df = load_data()
    st.dataframe(df)

    st.subheader("🗑️ Supprimer un match")
    match_id = st.number_input("ID du match", 1, 10000)

    if st.button("❌ Supprimer"):
        delete_match(match_id)
        st.success("Supprimé")
        st.rerun()

# --- ONGLET 4 ---
else:
    st.header("📖 Guide")
    st.write("""
        - Défensives : 4-5-1, 5-3-2, 5-4-1, 6-3-1
        - Équilibrées : 4-4-2B, 4-2-3-1, 3-5-2
        - Attaquantes : 4-3-3, 3-4-3
    """)
