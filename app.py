import streamlit as st
import pandas as pd
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="🐍 Guide OSM", layout="wide")
st.title("🐍 Guide OSM")

# TES IDENTIFIANTS
FORM_ID = "1FAIpQLScRz0wdM-3cV95JkKs3X0BCJQkTeel2QJy4MojN0bCueA3JDw"
ENTRY_ID = "entry.1264469444"
SHEET_ID = "1rLlCkWvZqwfuMaRjtzDW2ffxzM7AHtEExnMpgyBHlIw"

# Liste des colonnes pour reconstruire le tableau
columns = [
    "Date", "Mon_Equipe", "Mon_Classement", "Mon_Champ", "Diff_Gen", "Diff_Att", "Diff_Mil", "Diff_Def", "Diff_Gar",
    "Mon_Camp", "Lieu", "Niveau_Stade", "Arbitre", "Adversaire", "Type_Coach", "Son_Classement", "Adv_Dispo",
    "Adv_Style", "Adv_Tacles", "Adv_HJ", "Adv_Marquage", "Adv_Camp", "Enjeu", "Mon_Score", "Son_Score", "Resultat", 
    "Tirs_Pour", "Tirs_Contre", "Possession", "Ma_Tactique", "Mon_Style", "Mon_Pres", "Ma_Ment", "Mon_Temp"
]

# --- LECTURE DES DONNÉES ---
@st.cache_data(ttl=10) # Rafraîchit toutes les 10 secondes
def load_data():
    try:
        # URL de secours simplifiée (Export CSV direct du Sheets publié)
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/pub?output=csv"
        raw_df = pd.read_csv(url)
        
        # On cherche la colonne qui contient nos données (celle avec le plus de virgules)
        clean_rows = []
        for index, row in raw_df.iterrows():
            line_content = str(row.iloc[-1]) # On prend la dernière cellule de la ligne
            parts = line_content.split(',')
            if len(parts) >= 30: # On vérifie que c'est bien une ligne de match
                clean_rows.append(parts[:34]) # On s'arrête à 34 colonnes
        
        return pd.DataFrame(clean_rows, columns=columns)
    except:
        return pd.DataFrame(columns=columns)

df = load_data()

# MENU
menu = st.sidebar.radio("Navigation", ["🧠 Demander une Tactique", "📝 Enregistrer un Match", "📊 Historique", "📖 Guide & Aide"])

def afficher_formulaire_complet(prefix):
    st.subheader("1. Contexte & Niveaux")
    col1, col2, col3 = st.columns(3)
    with col1:
        mon_e = st.text_input("Mon équipe", "Troyes", key=f"{prefix}_me")
        mon_c = st.number_input("Mon classement", 1, 20, key=f"{prefix}_mc")
        mon_ch = st.text_input("Mon championnat", key=f"{prefix}_mch")
    with col2:
        dg, da, dm = st.columns(3)
        d_gen = dg.number_input("Diff. G", 0, key=f"{prefix}_dg")
        d_att = da.number_input("Diff. A", 0, key=f"{prefix}_da")
        d_mil = dm.number_input("Diff. M", 0, key=f"{prefix}_dm")
    with col3:
        d_def = st.number_input("Diff. D", 0, key=f"{prefix}_dd")
        d_gar = st.number_input("Diff. G", 0, key=f"{prefix}_dga")
        m_camp = st.checkbox("Mon Camp", key=f"{prefix}_mcp")

    st.subheader("2. Adversaire")
    col4, col5, col6 = st.columns(3)
    with col4:
        lieu = st.selectbox("Lieu", ["D", "E"], key=f"{prefix}_li")
        stade = st.slider("Stade", 0, 3, key=f"{prefix}_st")
        arb = st.selectbox("Arbitre", ["V", "B", "J", "O", "R"], key=f"{prefix}_ar")
    with col5:
        adv_n = st.text_input("Nom Adversaire", key=f"{prefix}_an")
        adv_co = st.selectbox("Type Coach", ["Joueur", "IA"], key=f"{prefix}_ac")
        a_dis = st.text_input("Dispositif (ex: 442A)", key=f"{prefix}_ad")
    with col6:
        a_sty = st.text_input("Style Adv", key=f"{prefix}_as")
        a_tac = st.selectbox("Tacles Adv", ["Normal", "Prudent", "Agressif"], key=f"{prefix}_at")
        a_hj = st.selectbox("Hors-jeu ?", ["Non", "Oui"], key=f"{prefix}_ah")
    
    return {
        "mon_e": mon_e, "mon_c": mon_c, "mon_ch": mon_ch, "d_gen": d_gen, "d_att": d_att, "d_mil": d_mil,
        "d_def": d_def, "d_gar": d_gar, "m_camp": m_camp, "lieu": lieu, "stade": stade, "arb": arb,
        "adv_n": adv_n, "adv_co": adv_co, "a_dis": a_dis, "a_sty": a_sty, "a_tac": a_tac, "a_hj": a_hj
    }

if menu == "🧠 Demander une Tactique":
    res_search = afficher_formulaire_complet("search")
    if st.button("🔍 ANALYSER"):
        match_ok = df[df['Adv_Dispo'] == res_search['a_dis']]
        if not match_ok.empty:
            st.success("Tactique trouvée dans l'historique !")
            st.table(match_ok[['Ma_Tactique', 'Mon_Pres', 'Ma_Ment', 'Mon_Temp', 'Resultat']])
        else:
            st.warning("Aucun match trouvé contre ce dispositif.")

elif menu == "📝 Enregistrer un Match":
    res_save = afficher_formulaire_complet("save")
    st.subheader("3. Ma Tactique & Score")
    c1, c2, c3, c4, c5 = st.columns(5)
    ma_tac = c1.text_input("Ma Tactique", "433B")
    ma_sty = c2.text_input("Mon Style", "Ailes")
    m_pre = c3.number_input("Pres", 0, 99, 70)
    m_men = c4.number_input("Ment", 0, 99, 70)
    m_tem = c5.number_input("Temp", 0, 99, 70)

    s1, s2, s3 = st.columns(3)
    m_score = s1.number_input("Mon Score", 0)
    a_score = s2.number_input("Son Score", 0)
    res_fin = s3.selectbox("Résultat", ["Victoire", "Nul", "Défaite"])

    if st.button("💾 ENREGISTRER"):
        # On crée la ligne sans virgules parasites dans les textes
        data_line = f"{pd.Timestamp.now().strftime('%d/%m/%Y')},{res_save['mon_e']},{res_save['mon_c']},{res_save['mon_ch']},{res_save['d_gen']},{res_save['d_att']},{res_save['d_mil']},{res_save['d_def']},{res_save['d_gar']},{res_save['m_camp']},{res_save['lieu']},{res_save['stade']},{res_save['arb']},{res_save['adv_n']},{res_save['adv_co']},10,{res_save['a_dis']},{res_save['a_sty']},{res_save['a_tac']},{res_save['a_hj']},Zone,False,Match,{m_score},{a_score},{res_fin},10,5,55,{ma_tac},{ma_sty},{m_pre},{m_men},{m_tem}"
        
        try:
            url_form = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"
            requests.post(url_form, data={ENTRY_ID: data_line})
            st.success("Match enregistré ! Patientez 5s pour l'historique.")
            st.cache_data.clear()
        except:
            st.error("Erreur de connexion au serveur Google.")

elif menu == "📊 Historique":
    st.header("📊 Tes Matchs")
    st.dataframe(df)

elif menu == "📖 Guide & Aide":
    st.info("Utilise 'Enregistrer' pour nourrir ton IA et 'Demander' pour gagner tes matchs.")
