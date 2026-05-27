import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Charger les clés API
load_dotenv()

def fetch_aggregated_trends(query, column_name, geo, api_key):
    print(f"  -> Extraction du Topic personnalisé : {column_name}...")
    
    # ASTUCE DE DATA ENGINEER : On découpe le temps en "Chunks" de moins de 5 ans
    # pour forcer Google Trends à nous renvoyer des données Hebdomadaires (Semaines)
    periodes = ["2021-01-01 2024-12-31", "2025-01-01 2026-04-30"]
    df_combined = pd.DataFrame()
    
    for period in periodes:
        params = {
            "engine": "google_trends",
            "q": query,
            "geo": geo,
            "date": period,
            "api_key": api_key
        }
        
        try:
            response = requests.get("https://serpapi.com/search.json", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "interest_over_time" in data and "timeline_data" in data["interest_over_time"]:
                    timeline = data["interest_over_time"]["timeline_data"]
                    df_temp = pd.DataFrame(timeline)
                    
                    # On convertit le timestamp en date
                    df_temp['date'] = pd.to_datetime(df_temp['timestamp'].astype(int), unit='s')
                    df_temp[column_name] = df_temp['values'].apply(lambda x: x[0]['extracted_value'] if len(x) > 0 else 0)
                    
                    # On colle ce morceau avec le précédent
                    df_combined = pd.concat([df_combined, df_temp[['date', column_name]]], ignore_index=True)
                else:
                    print(f"  [ATTENTION] Pas de données temporelles pour '{column_name}' sur la période {period}.")
            else:
                print(f"[ERREUR] Erreur API ({response.status_code}) pour '{column_name}'.")
                
        except Exception as e:
            print(f"[ERREUR] Système pour '{column_name}': {e}")
            
        time.sleep(1.5) # Pause anti-blocage de l'API

    if not df_combined.empty:
        df_combined = df_combined.drop_duplicates(subset=['date'], keep='first')    
    return df_combined

def build_candidates_matrix():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        print(" ERREUR : Clé SerpAPI introuvable dans le fichier .env.")
        return

    # Nos 9 "Topics" purifiés
    topics_custom = {
        "grippe + etat grippal + symptome grippe": "Topic_Grippe",
        "fièvre + fievre + etat febrile": "Topic_Fievre", 
        "toux + toux seche + tousser + sirop toux": "Topic_Toux",
        "fatigue + epuisement + courbature": "Topic_Fatigue",
        "mal de gorge + angine + pastille gorge": "Topic_Mal_Gorge",
        "paracetamol + doliprane + efferalgan + dafalgan": "Topic_Paracetamol",
        "ibuprofene + advil + nurofen": "Topic_Ibuprofene",
        "pharmacie de garde + pharmacie ouverte + pharmacie proche": "Topic_Pharmacie",
        "urgences + sos medecin + hopital": "Topic_Urgences"
    }
    
    df_master = None
    
    for query, col_name in topics_custom.items():
        # Plus besoin de passer la date en paramètre, la fonction gère les chunks
        df_topic = fetch_aggregated_trends(query, col_name, "FR-J", api_key)
        
        if df_topic is not None and not df_topic.empty:
            if df_master is None:
                df_master = df_topic
            else:
                # On fusionne sur la date pour ajouter la nouvelle colonne
                df_master = pd.merge(df_master, df_topic, on='date', how='outer')
        
    if df_master is not None:
        # Trier par date pour que l'ordre soit chronologique de 2021 à 2026
        df_master = df_master.sort_values('date').reset_index(drop=True)
        
        # Sauvegarde
        output_path = os.path.join("data", "brutes", "trends_9_topics_idf.csv")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_master.to_csv(output_path, index=False)
        print(f"\n Terminé ! Matrice sauvegardée avec {len(df_master)} lignes hebdomadaires dans {output_path}")

if __name__ == "__main__":
    print(" Lancement de l'extraction des Topics (Contournement de la limite des 5 ans)...")
    build_candidates_matrix()