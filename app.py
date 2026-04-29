import streamlit as st
import pandas as pd
from supabase import create_client

# --- CONFIGURATION ---
st.set_page_config(page_title="🐍 Guide OSM", layout="wide")
st.title("🐍 Guide OSM")

# --- SUPABASE ---
url = "https://rbzsbemgcuonwvihuwny.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJienNiZW1nY3Vvbnd2aWh1d255Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc0ODUzMTMsImV4cCI6MjA5MzA2MTMxM30.-wsKYzQDCTPhNR37fM4RivwR_nGSyf83tBmGmOi_WPE"

supabase = create_client(url, key)

# --- CHARGEMENT DONNÉES SUPABASE ---
def load_data():
    res = supabase.table("Matchs").select("*").execute()
    return pd.DataFrame(res.data)

df_supabase = load_data()

# Initialisation des colonnes (gardé comme dans ton code)
columns = [
    "Date", "Mon_Equipe", "Mon_Classement", "Mon_Champ", "Diff_Gen", "Diff_Att", "Diff_Mil", "Diff_Def", "Diff_Gar",
    "Mon_Camp", "Lieu", "Niveau_Stade", "Arbitre", "Adversaire", "Type_Coach", "Son_Classement", "Adv_Dispo",
    "Adv_Style", "Adv_Tacles", "Adv_HJ", "Adv_Marquage", "Adv_Camp", "Enjeu", "Mon_Score", "Son_Score", "Resultat", 
    "Tirs_Pour", "Tirs_Contre", "Possession", "Ma_Tactique", "Mon_Style", "Mon_Pres", "Ma_Ment", "Mon_Temp"
]

# --- NAVIGATION ---
menu = st.sidebar.radio(
    "Navigation",
    ["🧠 Demander une Tactique", "📝 Enregistrer un Match", "📊 Historique", "📖 Guide & Aide"],
    key="main_menu"
)

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
        arb = st.selectbox("Arbitre (V/B/J/O/R)", ["V", "B", "J", "O", "R"], key=f"{prefix}_ar")

    with f5:
        adv_n = st.text_input("J'affronte (Nom)", key=f"{prefix}_an")
        adv_co = st.selectbox("Coach Joueur ou IA", ["Joueur", "IA"], key=f"{prefix}_ac")
        adv_cl = st.number_input("Son classement", 1, 20, key=f"{prefix}_acl")

    with f6:
        a_dis = st.text_input("Son dispositif", key=f"{prefix}_ad")
        a_sty = st.text_input("Son style de jeu", key=f"{prefix}_as")
        a_tac = st.selectbox("Ses tacles", ["Prudent", "Normal", "Agressif", "Extrême"], key=f"{prefix}_at")
        a_hj = st.selectbox("Joue-t-il le hors-jeu ?", ["Non", "Oui"], key=f"{prefix}_ah")
        a_mar = st.selectbox("Marquage", ["Zone", "Individuel"], key=f"{prefix}_am")
        a_camp = st.checkbox("Adversaire en Camp ?", key=f"{prefix}_acp")

    enjeu = st.text_area("L'enjeu du match si spécial", key=f"{prefix}_enj")

    return {
        "mon_e": mon_e, "mon_c": mon_c, "mon_ch": mon_ch,
        "d_gen": d_gen, "d_att": d_att, "d_mil": d_mil,
        "d_def": d_def, "d_gar": d_gar, "m_camp": m_camp,
        "lieu": lieu, "stade": stade, "arb": arb,
        "adv_n": adv_n, "adv_co": adv_co, "adv_cl": adv_cl,
        "a_dis": a_dis, "a_sty": a_sty, "a_tac": a_tac,
        "a_hj": a_hj, "a_mar": a_mar, "a_camp": a_camp,
        "enjeu": enjeu
    }

# --- ONGLET 1 ---
if menu == "🧠 Demander une Tactique":
    st.header("🧠 Analyseur de Tactique")

    res_search = afficher_formulaire_complet("search")
    df = load_data()

    if st.button("🔍 TROUVER LA MEILLEURE TACTIQUE"):
        if df.empty:
            st.warning("Base Supabase vide.")
        else:
            victoires = df[df['Resultat'] == 'Victoire']
            match_parfait = victoires[
                (victoires['Adv_Dispo'] == res_search['a_dis']) &
                (victoires['Type_Coach'] == res_search['adv_co'])
            ]

            if not match_parfait.empty:
                final = match_parfait.iloc[-1]
                st.success(f"✅ Victoire trouvée ({final['Mon_Score']}-{final['Son_Score']}) !")
                st.info(
                    f"**Tactique :** {final['Ma_Tactique']} / {final['Mon_Style']}\n\n"
                    f"**Curseurs :** {final['Mon_Pres']} / {final['Ma_Ment']} / {final['Mon_Temp']}"
                )
            else:
                st.error("Aucune archive correspondante trouvée.")

# --- ONGLET 2 ---
elif menu == "📝 Enregistrer un Match":
    st.header("📝 Rapport de Match Complet")

    res_save = afficher_formulaire_complet("save")

    st.subheader("3. Ma Tactique utilisée")
    ma_tac = st.text_input("Dispositif")
    ma_sty = st.text_input("Style")
    m_pre = st.number_input("Pressing", 0, 99, 50)
    m_men = st.number_input("Mentalité", 0, 99, 50)
    m_tem = st.number_input("Tempo", 0, 99, 50)

    st.subheader("4. Statistiques & Score Final")
    m_score = st.number_input("Mon Score", 0, 20, 0)
    a_score = st.number_input("Son Score", 0, 20, 0)
    res_fin = st.selectbox("Résultat final", ["Victoire", "Nul", "Défaite"])
    t_pour = st.number_input("Mes tirs", 0, 50, 0)
    t_contre = st.number_input("Ses tirs", 0, 50, 0)
    poss = st.slider("Possession %", 0, 100, 50)

    if st.button("💾 SAUVEGARDER DANS SUPABASE"):
        nouvelle_ligne = {
            "Date": pd.Timestamp.now().strftime("%d/%m/%Y"),
            **res_save,
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

        supabase.table("Matchs").insert(nouvelle_ligne).execute()

        st.success("Match enregistré dans Supabase !")
        st.rerun()

# --- ONGLET 3 ---
elif menu == "📊 Historique":
    st.header("📊 Historique")

    df = load_data()
    st.dataframe(df)

# --- ONGLET 4 ---
else:
    st.header("📖 Guide Tactique Complet")

    with st.expander("📌 ÉTAPE 1 : Les Formations", expanded=True):
        st.write("""
        - Défensives : 4-5-1, 5-3-2...
        - Équilibrées : 4-4-2, 4-2-3-1...
        - Attaquantes : 4-3-3, 3-4-3...
        """)

    with st.expander("⚽ ÉTAPE 2 & 3 : Plans de jeu"):
        st.write("""
        - Défensif : Contre-attaque
        - Équilibré : Jeu de passe
        - Attaquant : Jeu d'aile
        """)

    with st.expander("⚙️ Curseurs"):
        st.write("""
        - Pressing, mentalité, tempo adaptés au match
        """)

    st.info("🚀 La tactique améliore les chances mais ne garantit rien.")
