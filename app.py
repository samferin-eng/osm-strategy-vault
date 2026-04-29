import streamlit as st
import pandas as pd
import requests
import io

# --- CONFIGURATION DÉFINITIVE ---
# Ces IDs permettent d'écrire dans le Sheets via le Formulaire
FORM_ID = "1SPnIB2p_Hxg5Mfsauc0bxb0F1B9bDfjia3HZuGmJz-o" 
ENTRY_ID = "entry.1326482362"

# Ce lien permet de lire le Sheets sans autorisation complexe
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQB-NQA0TQjYK9uEcCIC2pnJ3DlwDqrUFUdXdbJ-4lFaLGssQ54xQspcSCTroZSTwQdKFYNPb5hqNrW/pub?gid=534124765&single=true&output=csv"

st.set_page_config(page_title="🐍 Guide OSM PRO", layout="wide")
st.title("🐍 Guide OSM PRO")

# Liste officielle des 34 colonnes
columns = [
    "Date", "Mon_Equipe", "Mon_Classement", "Mon_Champ", "Diff_Gen", "Diff_Att", "Diff_Mil", "Diff_Def", "Diff_Gar",
    "Mon_Camp", "Lieu", "Niveau_Stade", "Arbitre", "Adversaire", "Type_Coach", "Son_Classement", "Adv_Dispo",
    "Adv_Style", "Adv_Tacles", "Adv_HJ", "Adv_Marquage", "Adv_Camp", "Enjeu", "Mon_Score", "Son_Score", "Resultat", 
    "Tirs_Pour", "Tirs_Contre", "Possession", "Ma_Tactique", "Mon_Style", "Mon_Pres", "Ma_Ment", "Mon_Temp"
]

# --- CHARGEMENT DE L'HISTORIQUE ---
@st.cache_data(ttl=10)
def load_data():
    try:
        raw_df = pd.read_csv(CSV_URL)
        # On récupère la colonne 'data' (la dernière colonne créée par Google Forms)
        data_col = raw_df.iloc[:, -1] 
        
        # On transforme chaque ligne de texte en colonnes réelles
        rows = []
        for val in data_col.dropna():
            parts = str(val).split(',')
            if len(parts) == len(columns):
                rows.append(parts)
        
        return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        return pd.DataFrame(columns=columns)

df = load_data()

# --- MENU DE NAVIGATION ---
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

# --- LOGIQUE DES ONGLETS ---

if menu == "🧠 Demander une Tactique":
    st.header("🧠 Analyseur de Tactique")
    res_search = afficher_formulaire_complet("search")
    if st.button("🔍 TROUVER LA MEILLEURE TACTIQUE"):
        if df.empty:
            st.warning("Historique vide. Enregistre des matchs pour nourrir l'IA.")
        else:
            vics = df[df['Resultat'] == 'Victoire']
            match = vics[(vics['Adv_Dispo'] == res_search['a_dis']) & (vics['Type_Coach'] == res_search['adv_co'])]
            if not match.empty:
                final = match.iloc[-1]
                st.success(f"✅ Victoire trouvée : {final['Ma_Tactique']} / {final['Mon_Style']}")
                st.info(f"**Curseurs :** {final['Mon_Pres']} / {final['Ma_Ment']} / {final['Mon_Temp']}")
            else:
                st.error("Aucune victoire enregistrée contre ce dispositif pour le moment.")

elif menu == "📝 Enregistrer un Match":
    st.header("📝 Rapport de Match")
    res_save = afficher_formulaire_complet("save")
    
    st.subheader("3. Ma Tactique & Score")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: ma_tac = st.text_input("Dispositif", key="s_tac")
    with c2: ma_sty = st.text_input("Style", key="s_sty")
    with c3: m_pre = st.number_input("Pressing", 0, 99, 50)
    with c4: m_men = st.number_input("Mentalité", 0, 99, 50)
    with c5: m_tem = st.number_input("Tempo", 0, 99, 50)

    s1, s2, s3, s4, s5, s6 = st.columns(6)
    with s1: m_score = st.number_input("Mon Score", 0, 20)
    with s2: a_score = st.number_input("Son Score", 0, 20)
    with s3: res_fin = st.selectbox("Résultat", ["Victoire", "Nul", "Défaite"])
    with s4: t_pour = st.number_input("Mes tirs", 0, 50)
    with s5: t_contre = st.number_input("Ses tirs", 0, 50)
    with s6: poss = st.slider("Possession %", 0, 100, 50)

    if st.button("💾 SAUVEGARDER DANS LE CLOUD"):
        data_list = [
            pd.Timestamp.now().strftime("%d/%m/%Y"), res_save['mon_e'], res_save['mon_c'], res_save['mon_ch'],
            res_save['d_gen'], res_save['d_att'], res_save['d_mil'], res_save['d_def'], res_save['d_gar'],
            res_save['m_camp'], res_save['lieu'], res_save['stade'], res_save['arb'], res_save['adv_n'],
            res_save['adv_co'], res_save['adv_cl'], res_save['a_dis'], res_save['a_sty'], res_save['a_tac'],
            res_save['a_hj'], res_save['a_mar'], res_save['a_camp'], res_save['enjeu'].replace(","," "),
            m_score, a_score, res_fin, t_pour, t_contre, poss, ma_tac, ma_sty, m_pre, m_men, m_tem
        ]
        csv_line = ",".join(map(str, data_list))
        
        try:
            post_url = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"
            requests.post(post_url, data={ENTRY_ID: csv_line})
            st.success("✅ Match envoyé avec succès ! Ton historique s'actualisera sous peu.")
            st.cache_data.clear()
        except:
            st.error("Erreur de connexion. Vérifie ta connexion internet.")

elif menu == "📊 Historique":
    st.header("📊 Historique des matchs")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucun match trouvé dans la base de données.")

# --- ONGLET 4 : GUIDE & AIDE (Contenu intégral du PDF) ---
else:
    st.header("📖 Guide Tactique Complet")
    
    with st.expander("📌 ÉTAPE 1 : Les Formations", expanded=True):
        st.write("""
        - **Défensives (4-5-1, 5-3-2, 5-4-1, 6-3-1) :** Priorité à la compacité. Idéales contre plus fort.
        - **Équilibrées (4-4-2B, 4-2-3-1, 3-5-2) :** Flexibilité et contrôle du milieu.
        - **Attaquantes (4-3-3, 3-4-3) :** Présence offensive maximale contre les plus faibles.
        - **Principe :** Ne jamais forcer une formation hors de son rôle naturel (ex: pas d'attaque agressive en 6-3-1).
        """)

    with st.expander("⚽ ÉTAPE 2 & 3 : Plans de jeu & Tactiques de ligne"):
        st.write("""
        **Plans de jeu compatibles:**
        - **Défensif :** Contre-attaque, Tir à vue, Longue balle.
        - **Équilibré :** Jeu de passe, Contre-attaque, Tir à vue.
        - **Attaquant :** Jeu d'aile, Jeu de passe.
        
        **Tactiques de ligne:**
        - **Attaque :** Attaque seulement / Milieu de soutien / Chute profonde.
        - **Milieu :** Pousser en avant / Rester en position / Protéger la défense.
        - **Défense :** Défense profonde / Milieu de soutien / Arrières offensifs.
        """)

    with st.expander("⚙️ ÉTAPE 4 à 6 : Curseurs (Pressing, Style, Tempo)"):
        st.write("""
        - **Pressing :** Élevé pour les plans d'attaque. Bas/Équilibré pour les plans défensifs.
        - **Style :** Doit correspondre à la formation. Ne jamais jouer défensif avec un 4-3-3.
        - **Tempo :** Haute vitesse contre les faibles. Lent/Construction pour les formations défensives contre plus fort.
        - **Règle d'or :** Ne jamais jouer à un rythme élevé contre un meilleur adversaire.
        """)

    with st.expander("🛡️ ÉTAPE 7 à 9 : Défense (Tacles, Marquage, Hors-jeu)"):
        st.write("""
        - **Tacles :** Ajuster selon l'arbitre. Ne jamais jouer 'Téméraire' avec un arbitre strict.
        - **Marquage Zonal :** En cas de supériorité numérique (plus de défenseurs que d'attaquants).
        - **Marquage Individuel :** Si les nombres sont pairs ou pour perturber le rythme.
        - **Piège Hors-jeu :** Uniquement avec peu de défenseurs (3 ou 4) et pression élevée. À éviter avec 5 ou 6 défenseurs.
        """)

    st.info("""
    🚀 **Le secret du succès :** La tactique augmente vos probabilités, mais la chance existe. 
    Développez votre équipe quotidiennement via les transferts et l'entraînement pour maximiser vos résultats.
    """)
    
