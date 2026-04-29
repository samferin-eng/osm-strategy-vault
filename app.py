import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION & CHARGEMENT ---
st.set_page_config(page_title="🐍 Guide OSM", layout="wide")
st.title("🐍 Guide OSM")

DATA_FILE = "osm_pro_history.csv"

# Initialisation des colonnes
columns = [
    "Date", "Mon_Equipe", "Mon_Classement", "Mon_Champ", "Diff_Gen", "Diff_Att", "Diff_Mil", "Diff_Def", "Diff_Gar",
    "Mon_Camp", "Lieu", "Niveau_Stade", "Arbitre", "Adversaire", "Type_Coach", "Son_Classement", "Adv_Dispo",
    "Adv_Style", "Adv_Tacles", "Adv_HJ", "Adv_Marquage", "Adv_Camp", "Enjeu", "Mon_Score", "Son_Score", "Resultat", 
    "Tirs_Pour", "Tirs_Contre", "Possession", "Ma_Tactique", "Mon_Style", "Mon_Pres", "Ma_Ment", "Mon_Temp"
]

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=columns)

def save_data(dataframe):
    dataframe.to_csv(DATA_FILE, index=False)

df = load_data()

# --- MENU LATÉRAL ---
menu = st.sidebar.radio("Navigation", ["🧠 Demander une Tactique", "📝 Enregistrer un Match", "📊 Historique", "📖 Guide & Aide"], key="main_menu")

def afficher_formulaire_complet(prefix):
    st.subheader("1. Contexte & Niveaux")
    f1, f2, f3 = st.columns(3)
    with f1:
        mon_e = st.text_input("Mon équipe", "Troyes", key=f"{prefix}_me")
        mon_c = st.number_input("Mon classement", 1, 20, key=f"{prefix}_mc")
    with f2:
        d_gen = st.number_input("Diff. Général", value=0, key=f"{prefix}_dg")
    with f3:
        m_camp = st.checkbox("Mon Camp d'entrainement", key=f"{prefix}_mcp")

    st.subheader("2. Conditions & Adversaire")
    f4, f5, f6 = st.columns(3)
    with f4:
        lieu = st.selectbox("Lieu (D/E)", ["D", "E"], key=f"{prefix}_li")
        arb = st.selectbox("Arbitre (V/B/J/O/R)", ["V", "B", "J", "O", "R"], key=f"{prefix}_ar")
    with f5:
        adv_co = st.selectbox("Coach Joueur ou IA", ["Joueur", "IA"], key=f"{prefix}_ac")
    with f6:
        a_dis = st.text_input("Son dispositif (ex: 433B)", key=f"{prefix}_ad")
    
    return {
        "mon_e": mon_e, "mon_c": mon_c, "d_gen": d_gen, "m_camp": m_camp, 
        "lieu": lieu, "arb": arb, "adv_co": adv_co, "a_dis": a_dis
    }

# --- LOGIQUE DES ONGLETS ---

if menu == "🧠 Demander une Tactique":
    st.header("🧠 Analyseur de Tactique")
    res_search = afficher_formulaire_complet("search")
    
    if st.button("🔍 TROUVER LA MEILLEURE TACTIQUE"):
        if df.empty:
            st.warning("Base de données vide.")
        else:
            potential_matches = df[(df['Resultat'] == 'Victoire') & (df['Adv_Dispo'] == res_search['a_dis'])]
            if potential_matches.empty:
                st.error(f"Aucune victoire contre un {res_search['a_dis']}.")
            else:
                potential_matches = potential_matches.copy()
                potential_matches['Proximite_Niveau'] = (potential_matches['Diff_Gen'] - res_search['d_gen']).abs()
                sorted_matches = potential_matches.sort_values(by=['Type_Coach', 'Proximite_Niveau'], ascending=[False, True])
                final = sorted_matches.iloc[0]
                st.success(f"🏆 Meilleure option : {final['Ma_Tactique']}")
                st.info(f"Paramètres : {final['Mon_Pres']} / {final['Ma_Ment']} / {final['Mon_Temp']}")

elif menu == "📝 Enregistrer un Match":
    st.header("📝 Rapport de Match")
    res_save = afficher_formulaire_complet("save")
    t1, t2, t3, t4, t5 = st.columns(5)
    with t1: ma_tac = st.text_input("Ma Tactique", key="save_ma_tac")
    with t2: ma_sty = st.text_input("Mon Style", key="save_ma_sty")
    with t3: m_pre = st.number_input("Pressing", 0, 99, 50)
    with t4: m_men = st.number_input("Mentalité", 0, 99, 50)
    with t5: m_tem = st.number_input("Tempo", 0, 99, 50)
    
    m_score = st.number_input("Mon Score", 0, 20)
    a_score = st.number_input("Son Score", 0, 20)
    res_fin = st.selectbox("Résultat", ["Victoire", "Nul", "Défaite"])

    if st.button("💾 SAUVEGARDER"):
        nouvelle_ligne = {
            "Date": pd.Timestamp.now().strftime("%d/%m/%Y"), "Mon_Equipe": res_save['mon_e'], 
            "Diff_Gen": res_save['d_gen'], "Type_Coach": res_save['adv_co'], "Adv_Dispo": res_save['a_dis'],
            "Mon_Score": m_score, "Son_Score": a_score, "Resultat": res_fin, 
            "Ma_Tactique": ma_tac, "Mon_Style": ma_sty, "Mon_Pres": m_pre, "Ma_Ment": m_men, "Mon_Temp": m_tem
        }
        df = pd.concat([df, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
        save_data(df)
        st.success("Match enregistré !")

elif menu == "📊 Historique":
    st.header("📊 Historique")
    st.dataframe(df)

# --- NOUVEL ONGLET : GUIDE & AIDE COMPLET ---
elif menu == "📖 Guide & Aide":
    st.header("📖 La Bible Tactique OSM")
    
    with st.expander("🛡️ Étape 1 à 3 : Formations et Lignes", expanded=True):
        st.write("""
        **1. Choisir sa formation :**
        - **Défensives (4-5-1, 5-3-2, 5-4-1, 6-3-1) :** Priorité à la compacité contre les plus forts[cite: 7].
        - **Équilibrées (4-4-2B, 4-2-3-1, 3-5-2) :** Flexibilité et contrôle du milieu[cite: 8].
        - **Attaquantes (4-3-3, 3-4-3) :** Maximisent l'offensive contre les plus faibles[cite: 9].
        
        **2. Plan de match compatible :**
        - **Défensif :** Contre-attaque, Tir à vue, Longue balle[cite: 21].
        - **Équilibré :** Jeu de passe, Contre-attaque[cite: 22].
        - **Attaquant :** Jeu d'aile, Jeu de passe[cite: 22].
        
        **3. Tactiques de ligne :**
        - **Attaquants :** Attaque seulement / Milieu de soutien / Chute profonde[cite: 32].
        - **Milieux :** Pousser en avant / Rester en position / Protéger la défense[cite: 33].
        - **Défenseurs :** Défense profonde / Soutien milieu / Arrières offensifs[cite: 34].
        """)

    with st.expander("⚡ Étape 4 à 6 : Pressing, Style et Tempo"):
        st.write("""
        **4. Pressing :**
        - **Haute pression :** Complément naturel des configurations offensives[cite: 44].
        - **Pressing bas (Assis profond) :** Pour les plans défensifs ou si vous êtes beaucoup plus faible[cite: 45].
        
        **5. Style :**
        - Doit correspondre à la formation. Ne jouez jamais défensivement avec une formation d'attaque[cite: 55, 56].
        
        **6. Tempo :**
        - **Tempo élevé :** Contre adversaires faibles ou à domicile[cite: 65, 70].
        - **Tempo faible :** Contre adversaires plus forts pour préserver la structure[cite: 66, 74].
        - *Règle d'or :* Ne jamais jouer à un rythme élevé contre un meilleur adversaire[cite: 68].
        """)

    with st.expander("⚖️ Étape 7 à 9 : Tacles, Marquage et Hors-jeu"):
        st.write("""
        **7. Tacles :**
        - **Agressif/Téméraire :** Pour perturber les équipes supérieures, mais attention à l'arbitre[cite: 82, 84].
        - *Règle d'or :* Ne jamais jouer en 'Téméraire' avec un arbitre strict (Rouge/Orange)[cite: 80, 161].
        
        **8. Marquage :**
        - **Zonal :** Si vous avez la supériorité numérique défensive (plus de défenseurs que d'attaquants)[cite: 94].
        - **Individuel :** Si les nombres sont pairs[cite: 96].
        
        **9. Piège du hors-jeu :**
        - Uniquement avec 3 ou 4 défenseurs et une pression élevée[cite: 102].
        - **À éviter absolument** avec 5 ou 6 défenseurs ou une faible pression[cite: 103].
        """)

    st.info("💡 **Conseil d'élite :** Un seul match ne prouve rien. Jugez vos tactiques sur plusieurs matchs et restez actif sur le marché des transferts[cite: 168, 171, 176].")
