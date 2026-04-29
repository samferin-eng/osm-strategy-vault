import streamlit as st
import pandas as pd
import sqlite3

# --- CONFIGURATION ---
st.set_page_config(page_title="🐍 Guide OSM", layout="wide")
st.title("🐍 Guide OSM")

DB_FILE = "osm_pro.db"

# --- INIT DATABASE ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS matchs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT,
        Mon_Equipe TEXT,
        Mon_Classement INTEGER,
        Mon_Champ TEXT,
        Diff_Gen INTEGER,
        Diff_Att INTEGER,
        Diff_Mil INTEGER,
        Diff_Def INTEGER,
        Diff_Gar INTEGER,
        Mon_Camp BOOLEAN,
        Lieu TEXT,
        Niveau_Stade INTEGER,
        Arbitre TEXT,
        Adversaire TEXT,
        Type_Coach TEXT,
        Son_Classement INTEGER,
        Adv_Dispo TEXT,
        Adv_Style TEXT,
        Adv_Tacles TEXT,
        Adv_HJ TEXT,
        Adv_Marquage TEXT,
        Adv_Camp BOOLEAN,
        Enjeu TEXT,
        Mon_Score INTEGER,
        Son_Score INTEGER,
        Resultat TEXT,
        Tirs_Pour INTEGER,
        Tirs_Contre INTEGER,
        Possession INTEGER,
        Ma_Tactique TEXT,
        Mon_Style TEXT,
        Mon_Pres INTEGER,
        Ma_Ment INTEGER,
        Mon_Temp INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# --- DB FUNCTIONS ---
def insert_match(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    INSERT INTO matchs (
        Date, Mon_Equipe, Mon_Classement, Mon_Champ, Diff_Gen, Diff_Att, Diff_Mil,
        Diff_Def, Diff_Gar, Mon_Camp, Lieu, Niveau_Stade, Arbitre, Adversaire,
        Type_Coach, Son_Classement, Adv_Dispo, Adv_Style, Adv_Tacles, Adv_HJ,
        Adv_Marquage, Adv_Camp, Enjeu, Mon_Score, Son_Score, Resultat,
        Tirs_Pour, Tirs_Contre, Possession, Ma_Tactique, Mon_Style,
        Mon_Pres, Ma_Ment, Mon_Temp
    )
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, tuple(data.values()))

    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM matchs", conn)
    conn.close()
    return df

def delete_match(match_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM matchs WHERE id = ?", (match_id,))
    conn.commit()
    conn.close()

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

    res = afficher_formulaire_complet("search")

    if st.button("🔍 TROUVER"):
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
    
