import requests
import pandas as pd
import os

def fetch_open_meteo_data(lat, lon, start_date, end_date, filename):
    print(f" Extraction des données météo pour lat:{lat}, lon:{lon}...")
    
    # Endpoint officiel des archives Open-Meteo
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    # Paramètres définis dans l'architecture Epi-Trace
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m"],
        "timezone": "Europe/Paris"
    }

    # Appel à l'API
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Transformation du JSON direct en DataFrame Pandas
        df = pd.DataFrame(data["hourly"])
        df['time'] = pd.to_datetime(df['time'])
        
        # Sauvegarde dans le dossier des données brutes
        chemin_script = os.path.abspath(__file__)
        dossier_src = os.path.dirname(chemin_script)
        dossier_racine = os.path.dirname(dossier_src)
        output_path = os.path.join(dossier_racine,"data", "brutes", filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print(f" Succès ! {len(df)} lignes sauvegardées dans {output_path}")
        return df
    else:
        print(f" Erreur lors de l'appel API: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # Paramètres pour la Phase de Test (France - Coordonnées de Paris)
    # On extrait de début 2021 à fin 2024
    fetch_open_meteo_data(
        lat=48.8566, 
        lon=2.3522, 
        start_date="2021-01-01", 
        end_date="2026-04-30", 
        filename="meteo_france_2021_2026.csv"
    )