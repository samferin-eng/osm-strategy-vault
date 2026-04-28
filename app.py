import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION & CHARGEMENT ---
st.set_page_config(page_title="Serpentard Strategy Vault PRO", layout="wide")
st.title("🐍 Serpentard Strategy Vault PRO")

DATA_FILE = "osm_pro_history.csv"

# Fonctions utilitaires pour la gestion du fichier
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=columns)

def save_data(dataframe):
    dataframe.to_csv(DATA_FILE, index=False)

# Initialisation des colonnes
columns = [
    "Date", "Mon_Equipe", "Mon_Classement", "Mon_Champ", "Diff_Gen", "Diff_Att", "Diff_Mil", "Diff_Def", "Diff_Gar",
    "Mon_Camp", "Lieu", "Niveau_Stade", "Arbitre", "Adversaire", "Type_Coach", "Son_Classement", "Adv_Dispo",
    "Adv_Style", "Adv_Tacles", "Adv_HJ", "Adv_Marquage", "Adv_Camp", "Enjeu", "Mon_Score", "Son_Score", "Resultat", 
    "Tirs_Pour", "Tirs_Contre", "Possession", "Ma_Tactique", "Mon_Style", "Mon_Pres", "Ma_Ment", "Mon_Temp"
]

df = load_data()

# --- MENU LATÉRAL ---
menu = st.sidebar.radio("Navigation", ["🧠 Demander une Tactique", "📝 Enregistrer un Match", "📊 Historique"], key="main_menu")

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
            st.warning("Base vide.")
        else:
            victoires = df[df['Resultat'] == 'Victoire']
            match_parfait = victoires[(victoires['Adv_Dispo'] == res_search['a_dis']) & (victoires['Type_Coach'] == res_search['adv_co'])]
            
            if not match_parfait.empty:
                final = match_parfait.iloc[-1]
                st.success(f"✅ Victoire trouvée ({final['Mon_Score']}-{final['Son_Score']}) !")
                st.info(f"**Tactique :** {final['Ma_Tactique']} / {final['Mon_Style']}\n\n**Curseurs :** {final['Mon_Pres']} / {final['Ma_Ment']} / {final['Mon_Temp']}")
            else:
                st.error("Aucune archive correspondante trouvée contre ce dispositif et ce type de coach.")

# --- ONGLET 2 : ENREGISTREMENT ---
elif menu == "📝 Enregistrer un Match":
    st.header("📝 Rapport de Match Complet")
    res_save = afficher_formulaire_complet("save")
    
    st.subheader("3. Ma Tactique utilisée")
    t1, t2, t3, t4, t5 = st.columns(5)
    with t1: ma_tac = st.text_input("Dispositif (ex: 433B)", key="save_ma_tac")
    with t2: ma_sty = st.text_input("Style (ex: Ailes)", key="save_ma_sty")
    with t3: m_pre = st.number_input("Pressing", 0, 99, 50, key="save_m_pre")
    with t4: m_men = st.number_input("Mentalité", 0, 99, 50, key="save_m_men")
    with t5: m_tem = st.number_input("Tempo", 0, 99, 50, key="save_m_tem")

    st.subheader("4. Statistiques & Score Final")
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    with s1: m_score = st.number_input("Mon Score", 0, 20, 0, key="save_m_score")
    with s2: a_score = st.number_input("Son Score", 0, 20, 0, key="save_a_score")
    with s3: res_fin = st.selectbox("Résultat final", ["Victoire", "Nul", "Défaite"], key="save_res")
    with s4: t_pour = st.number_input("Mes tirs", 0, 50, 0, key="save_tp")
    with s5: t_contre = st.number_input("Ses tirs", 0, 50, 0, key="save_tc")
    with s6: poss = st.slider("Possession %", 0, 100, 50, key="save_poss")

    if st.button("💾 SAUVEGARDER DANS LA MÉMOIRE"):
        nouvelle_ligne = {
            "Date": pd.Timestamp.now().strftime("%d/%m/%Y"), "Mon_Equipe": res_save['mon_e'], "Mon_Classement": res_save['mon_c'],
            "Mon_Champ": res_save['mon_ch'], "Diff_Gen": res_save['d_gen'], "Diff_Att": res_save['d_att'], "Diff_Mil": res_save['d_mil'],
            "Diff_Def": res_save['d_def'], "Diff_Gar": res_save['d_gar'], "Mon_Camp": res_save['m_camp'], "Lieu": res_save['lieu'],
            "Niveau_Stade": res_save['stade'], "Arbitre": res_save['arb'], "Adversaire": res_save['adv_n'], "Type_Coach": res_save['adv_co'],
            "Son_Classement": res_save['adv_cl'], "Adv_Dispo": res_save['a_dis'], "Adv_Style": res_save['a_sty'],
            "Adv_Tacles": res_save['a_tac'], "Adv_HJ": res_save['a_hj'], "Adv_Marquage": res_save['a_mar'], "Adv_Camp": res_save['a_camp'],
            "Enjeu": res_save['enjeu'], "Mon_Score": m_score, "Son_Score": a_score, "Resultat": res_fin, 
            "Tirs_Pour": t_pour, "Tirs_Contre": t_contre, "Possession": poss,
            "Ma_Tactique": ma_tac, "Mon_Style": ma_sty, "Mon_Pres": m_pre, "Ma_Ment": m_men, "Mon_Temp": m_tem
        }
        df = pd.concat([df, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
        save_data(df)
        st.success(f"Match enregistré avec succès !")
        st.rerun()

# --- ONGLET 3 : HISTORIQUE & SUPPRESSION ---
else:
    st.header("📊 Historique des matchs")
    if not df.empty:
        st.dataframe(df.sort_index(ascending=False))
        
        st.markdown("---")
        st.subheader("🗑️ Supprimer une erreur")
        
        # Liste déroulante pour identifier le match à supprimer
        match_list = df.apply(lambda x: f"{x['Date']} - vs {x['Adversaire']} ({x['Resultat']})", axis=1).tolist()
        match_to_delete = st.selectbox("Choisir le match à supprimer", match_list)
        
        if st.button("❌ SUPPRIMER DÉFINITIVEMENT"):
            index_to_drop = match_list.index(match_to_delete)
            df = df.drop(df.index[index_to_drop])
            save_data(df)
            st.warning("Match supprimé. La page va s'actualiser.")
            st.rerun()
    else:
        st.info("L'historique est vide.")
