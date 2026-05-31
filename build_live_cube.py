import pandas as pd
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Chargement de la clé SerpAPI depuis le fichier .env
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

print("=== 🚀 DÉMARRAGE DU PIPELINE ETL : MINI-CUBE LIVE (Version Longue) ===")

# --- ÉTAPE 1 : SENTINELLES ---
def process_sentinelles(nom_fichier="sentinelles_latest.csv", fenetre_semaines=60): # <-- CHANGEMENT ICI (60 semaines)
    print("\n1️⃣ Extraction Sentinelles (Vérité Terrain)...")
    chemin_fichier = os.path.join("data", "brutes", nom_fichier)
    
    df = pd.read_csv(chemin_fichier, skiprows=1)
    # Filtre Île-de-France (Code 11)
    df_idf = df[df['geo_insee'].astype(str) == '11'].copy()
    
    # Transformation de la semaine en date (Dimanche)
    df_idf['date'] = pd.to_datetime(df_idf['week'].astype(str) + '-0', format='%G%V-%w')
    df_idf = df_idf.sort_values('date')[['date', 'inc']].reset_index(drop=True)
    
    # On ne garde que les X dernières semaines
    df_recent = df_idf.tail(fenetre_semaines).reset_index(drop=True)
    
    date_min = df_recent['date'].min()
    date_max = df_recent['date'].max()
    print(f"✅ Sentinelles prêt. Période : {date_min.strftime('%Y-%m-%d')} au {date_max.strftime('%Y-%m-%d')}")
    return df_recent, date_min, date_max

# --- ÉTAPE 2 : MÉTÉO (Open-Meteo - Gratuit) ---
def process_meteo(date_min, date_max):
    print("\n2️⃣ Extraction Météo (Île-de-France)...")
    
    date_fin_meteo = date_max + timedelta(days=7) 
    
    # SÉCURITÉ : L'API Archive ne connaît pas le futur.
    date_limite = datetime.now() - timedelta(days=1)
    if date_fin_meteo > date_limite:
        date_fin_meteo = date_limite
        
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 48.8566, "longitude": 2.3522, # Paris
        "start_date": date_min.strftime('%Y-%m-%d'),
        "end_date": date_fin_meteo.strftime('%Y-%m-%d'),
        "hourly": ["temperature_2m", "relative_humidity_2m"],
        "timezone": "Europe/Paris"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "error" in data:
        raise ValueError(f"❌ Erreur API Météo : {data.get('reason')}")
    
    df_meteo = pd.DataFrame(data["hourly"])
    df_meteo['date'] = pd.to_datetime(df_meteo['time'])
    
    df_meteo = df_meteo[['date', 'temperature_2m', 'relative_humidity_2m']]
    df_meteo = df_meteo.set_index('date').resample('W-SUN').mean().reset_index()
    
    print(f"✅ Météo extraite avec succès (jusqu'au {date_fin_meteo.strftime('%Y-%m-%d')}).")
    return df_meteo

# --- ÉTAPE 3 : GOOGLE TRENDS (SerpAPI) ---
def process_trends(date_min, date_max): # <-- CHANGEMENT ICI (On prend la date de fin en compte)
    print("\n3️⃣ Extraction Infodémiologie (SerpAPI)...")
    if not SERPAPI_KEY:
        raise ValueError("❌ Clé SERPAPI_KEY introuvable dans le .env !")
        
    topics = {"toux": "Topic_Toux", "grippe": "Topic_Grippe", "fievre": "Topic_Fievre"}
    df_master = None
    
    # Période formatée pour Google (Dynamique selon la date de fin)
    date_fin_google = date_max + timedelta(days=30) # On prend une marge de sécurité
    periode_google = f"{date_min.strftime('%Y-%m-%d')} {date_fin_google.strftime('%Y-%m-%d')}"
    
    for requete, col_name in topics.items():
        print(f"   -> Récupération du topic : {requete}")
        params = {
            "engine": "google_trends", "q": requete, "geo": "FR-J", 
            "date": periode_google, "api_key": SERPAPI_KEY
        }
        resp = requests.get("https://serpapi.com/search.json", params=params).json()
        
        try:
            timeline = resp["interest_over_time"]["timeline_data"]
            df_temp = pd.DataFrame(timeline)
            
            df_temp['date'] = pd.to_datetime(df_temp['timestamp'].astype(int), unit='s')
            df_temp = df_temp.rename(columns={'values': col_name})
            df_temp[col_name] = df_temp[col_name].apply(lambda x: x[0]['extracted_value'])
            df_temp = df_temp[['date', col_name]]
            
            if df_master is None:
                df_master = df_temp
            else:
                df_master = pd.merge(df_master, df_temp, on='date', how='outer')
        except KeyError:
            print(f"⚠️ Erreur de parsing pour le topic {requete}. Vérifiez vos crédits SerpAPI.")
            
    print("✅ Tendances Google Trends extraites.")
    return df_master

# --- ÉTAPE 4 : FUSION (Le Cube Final) ---
if __name__ == "__main__":
    # 1. Extraction
    df_sentinelles, d_min, d_max = process_sentinelles(fenetre_semaines=60) # <-- 60 SEMAINES
    df_meteo = process_meteo(d_min, d_max)
    df_trends = process_trends(d_min, d_max) # <-- Passe d_max à la fonction
    
    print("\n4️⃣ Fusion des données (Création du Cube OLAP Live)...")
    
    # 2. Jointure
    cube = pd.merge(df_sentinelles, df_meteo, on='date', how='outer')
    cube = pd.merge(cube, df_trends, on='date', how='outer')
    
    # 3. Traitement des valeurs manquantes et variable "ratio_vacances"
    def calc_ratio_vacances(date_dimanche):
        lundi = date_dimanche - timedelta(days=6)
        jours_semaine = pd.date_range(lundi, date_dimanche)
        
        # Vacances 2025/2026 pour couvrir les 60 semaines
        vacances_printemps_25 = pd.date_range('2025-04-12', '2025-04-28')
        vacances_ete_25 = pd.date_range('2025-07-05', '2025-09-01')
        vacances_toussaint_25 = pd.date_range('2025-10-18', '2025-11-03')
        vacances_noel_25 = pd.date_range('2025-12-20', '2026-01-05')
        vacances_hiver_26 = pd.date_range('2026-02-21', '2026-03-08')
        vacances_printemps_26 = pd.date_range('2026-04-18', '2026-05-03')
        
        toutes_vacances = vacances_printemps_25.union(vacances_ete_25).union(vacances_toussaint_25)\
            .union(vacances_noel_25).union(vacances_hiver_26).union(vacances_printemps_26)
        
        jours_en_vacances = sum(1 for jour in jours_semaine if jour in toutes_vacances)
        return round(jours_en_vacances / 7.0, 2)

    cube['ratio_vacances'] = cube['date'].apply(calc_ratio_vacances)
    
    # On supprime les lignes trop vieilles ou futures inutiles
    cube = cube.dropna(subset=['temperature_2m', 'Topic_Toux'])
    cube = cube.sort_values('date').reset_index(drop=True)
    
    # 4. Sauvegarde
    chemin_sortie = os.path.join("data", "traitees", "epitrace_cube_live.csv")
    cube.to_csv(chemin_sortie, index=False)
    
    print(f"\n🎉 SUCCÈS TOTAL ! Le Cube Live a été généré : {chemin_sortie}")
    print(cube.tail(3).to_string())