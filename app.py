import streamlit as st
import pandas as pd
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="🐍 Guide OSM", layout="wide")
st.title("🐍 Guide OSM")

# IDENTIFIANTS QUE TU AS FOURNIS
FORM_ID = "1FAIpQLScRz0wdM-3cV95JkKs3X0BCJQkTeel2QJy4MojN0bCueA3JDw"
ENTRY_ID = "entry.1264469444"

# CONFIGURATION DU SHEETS
SHEET_ID = "1rLlCkWvZqwfuMaRjtzDW2ffxzM7AHtEExnMpgyBHlIw"
# Si ça ne marche pas, vérifie si l'onglet ne s'appelle pas "Feuille 1" ou "Form Responses 1"
NOM_ONGLET = "Réponses au formulaire 1" 

# URL de lecture publique (Format CSV)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={NOM_ONGLET.replace(' ', '%20')}"

# Structure des colonnes (34 colonnes au total)
columns = [
    "Date", "Mon_Equipe", "Mon_Classement", "Mon_Champ", "Diff_Gen", "Diff_Att", "Diff_Mil", "Diff_Def", "Diff_Gar",
    "Mon_Camp", "Lieu", "Niveau_Stade", "Arbitre", "Adversaire", "Type_Coach", "Son_Classement", "Adv_Dispo",
    "Adv_Style", "Adv_Tacles", "Adv_HJ", "Adv_Marquage", "Adv_Camp", "Enjeu", "Mon_Score", "Son_Score", "Resultat", 
    "Tirs_Pour", "Tirs_Contre", "Possession", "Ma_Tactique", "Mon_Style", "Mon_Pres", "Ma_Ment", "Mon_Temp"
]

# --- CHARGEMENT & NETTOYAGE ---
try:
    # On tente de lire le CSV
    raw_df = pd.read_csv(SHEET_URL)
    
    # Google Forms met l'horodatage en colonne A, et ta donnée compactée en colonne B
    # On prend donc la dernière colonne du tableau
    data_column = raw_df.iloc[:, -1] 
    
    clean_data = []
    for row in data_column.dropna():
        parts = str(row).split(',')
        # On vérifie que la ligne est complète (34 éléments)
        if len(parts) == len(columns):
            clean_data.append(parts)
    
    df = pd.DataFrame(clean_data, columns=columns)
    
    # Nettoyage des types de données pour la recherche
    df["Mon_Score"] = pd.to_numeric(df["Mon_Score"], errors='coerce')
    df["Son_Score"] = pd.to_numeric(df["Son_Score"], errors='coerce')

except Exception as e:
    # Si le chargement échoue (ex: fichier non publié), on crée un tableau vide avec les colonnes
    df = pd.DataFrame(columns=columns)

# MENU
menu = st.sidebar.radio("Navigation", ["🧠 Demander une Tactique", "📝 Enregistrer un Match", "📊 Historique", "📖 Guide & Aide"])

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
        a_dis = st.text_input("Son dispositif (ex: 442A)", key=f"{prefix}_ad")
        a_sty = st.text_input("Son style de jeu", key=f"{prefix}_as")
        a_tac = st.selectbox("Ses tacles", ["Prudent", "Normal", "Agressif", "Extrême"], key=f"{prefix}_at")
        a_hj = st.selectbox("Joue-t-il le hors-jeu ?", ["Non", "Oui"], key=f"{prefix}_ah")
        a_mar = st.selectbox("Marquage", ["Zone", "Individuel"], key=f"{prefix}_am")
        a_camp = st.checkbox("Adversaire en Camp ?", key=f"{prefix}_acp")
    
    enjeu = st.text_area("L'enjeu du match si spécial", key=f"{prefix}_enj")
    
    return {
        "mon_e": mon_e, "mon_c": mon_c, "mon_ch": mon_ch, "d_gen": d_gen, "d_att": d_att, "d_mil": d_mil,
        "d_def": d_def, "d_gar": d_gar, "m_camp": m_camp, "lieu": lieu, "stade": stade, "arb": arb,
        "adv_n": adv_n, "adv_co": adv_co, "adv_cl": adv_cl, "a_dis": a_dis, "a_sty": a_sty,
        "a_tac": a_tac, "a_hj": a_hj, "a_mar": a_mar, "a_camp": a_camp, "enjeu": enjeu
    }

# --- ONGLET 1 : CONSEIL ---
if menu == "🧠 Demander une Tactique":
    st.header("🧠 Analyseur de Tactique")
    res_search = afficher_formulaire_complet("search")
    if st.button("🔍 TROUVER LA MEILLEURE TACTIQUE"):
        if df.empty:
            st.warning("Aucune donnée disponible. Connecte ton Sheets et enregistre un match.")
        else:
            match_parfait = df[(df['Adv_Dispo'] == res_search['a_dis']) & (df['Resultat'] == 'Victoire')]
            if not match_parfait.empty:
                final = match_parfait.iloc[-1]
                st.success(f"✅ Victoire trouvée !")
                st.write(f"**Ma Tactique :** {final['Ma_Tactique']} ({final['Mon_Style']})")
                st.write(f"**Curseurs :** {final['Mon_Pres']} / {final['Ma_Ment']} / {final['Mon_Temp']}")
            else:
                st.error("Aucune victoire enregistrée contre ce dispositif.")

# --- ONGLET 2 : ENREGISTREMENT ---
elif menu == "📝 Enregistrer un Match":
    st.header("📝 Rapport de Match")
    res_save = afficher_formulaire_complet("save")
    
    st.subheader("3. Ma Tactique & Résultat")
    t1, t2, t3, t4, t5 = st.columns(5)
    with t1: ma_tac = st.text_input("Dispositif", key="save_ma_tac")
    with t2: ma_sty = st.text_input("Style", key="save_ma_sty")
    with t3: m_pre = st.number_input("Pressing", 0, 99, 50)
    with t4: m_men = st.number_input("Mentalité", 0, 99, 50)
    with t5: m_tem = st.number_input("Tempo", 0, 99, 50)

    s1, s2, s3, s4, s5, s6 = st.columns(6)
    with s1: m_score = st.number_input("Mon Score", 0, 20)
    with s2: a_score = st.number_input("Son Score", 0, 20)
    with s3: res_fin = st.selectbox("Résultat", ["Victoire", "Nul", "Défaite"])
    with s4: tp = st.number_input("Mes tirs", 0, 50)
    with s5: tc = st.number_input("Ses tirs", 0, 50)
    with s6: po = st.slider("Possession", 0, 100, 50)

    if st.button("💾 ENREGISTRER DÉFINITIVEMENT"):
        # Construction de la ligne CSV
        data_line = f"{pd.Timestamp.now().strftime('%d/%m/%Y')},{res_save['mon_e']},{res_save['mon_c']},{res_save['mon_ch']},{res_save['d_gen']},{res_save['d_att']},{res_save['d_mil']},{res_save['d_def']},{res_save['d_gar']},{res_save['m_camp']},{res_save['lieu']},{res_save['stade']},{res_save['arb']},{res_save['adv_n']},{res_save['adv_co']},{res_save['adv_cl']},{res_save['a_dis']},{res_save['a_sty']},{res_save['a_tac']},{res_save['a_hj']},{res_save['a_mar']},{res_save['a_camp']},{res_save['enjeu']},{m_score},{a_score},{res_fin},{tp},{tc},{po},{ma_tac},{ma_sty},{m_pre},{m_men},{m_tem}"
        
        try:
            requests.post(f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse", data={ENTRY_ID: data_line})
            st.success("Match enregistré ! Actualise l'historique dans quelques secondes.")
            st.rerun()
        except:
            st.error("Erreur de connexion au formulaire.")

# --- ONGLET 3 : HISTORIQUE ---
elif menu == "📊 Historique":
    st.header("📊 Historique")
    if df.empty:
        st.info("L'historique est vide ou le Sheets n'est pas 'Publié sur le web'.")
    else:
        st.dataframe(df)

# --- ONGLET 4 : GUIDE ---
elif menu == "📖 Guide & Aide":
    st.header("📖 Guide")
    st.write("Utilise les expanders pour voir les conseils tactiques.")
