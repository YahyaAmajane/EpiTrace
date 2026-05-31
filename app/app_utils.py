import pandas as pd
import numpy as np
import joblib
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Masque les alertes TensorFlow inutiles
from tensorflow.keras.models import load_model

def load_ml_assets(scaler_path, forecaster_path, nowcaster_path):
    """
    Charge le traducteur (scaler) et les deux cerveaux IA.
    """
    try:
        scaler = joblib.load(scaler_path)
        forecaster = load_model(forecaster_path)
        nowcaster = load_model(nowcaster_path)
        return scaler, forecaster, nowcaster
    except Exception as e:
        print(f"⚠️ Erreur critique de chargement des modèles : {e}")
        return None, None, None

def get_latest_data(csv_path, lookback_window=12):
    """
    Récupère l'historique récent pour nourrir les modèles.
    """
    try:
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        # On extrait uniquement la fenêtre nécessaire (12 semaines)
        df_recent = df.tail(lookback_window).copy()
        return df, df_recent
    except Exception as e:
        print(f"⚠️ Erreur de lecture des données : {e}")
        return None, None

def predict_standard_forecast(forecaster, scaler, data_scaled, feature_columns):
    """
    MODE 1 : Prévision classique (Forecasting).
    Utilise les données réelles pour prédire la semaine suivante (J+7).
    """
    # Format 3D requis par le LSTM : (1 sample, 12 timesteps, 7 features)
    X_input = np.array([data_scaled])
    
    # Prédiction
    pred_scaled = forecaster.predict(X_input, verbose=0)
    
    # Dénormalisation
    dummy = np.zeros((1, len(feature_columns)))
    dummy[0, 0] = pred_scaled[0, 0] # On place la prédiction dans la colonne 'inc'
    pred_real = scaler.inverse_transform(dummy)[0, 0]
    
    return int(max(0, pred_real)) # Évite les valeurs négatives impossibles

def predict_cascade_nowcast(nowcaster, scaler, data_scaled, feature_columns):
    """
    MODE 2 : L'estimation du présent (Nowcasting).
    Devine l'incidence actuelle à l'aveugle via la technique du Delta.
    """
    seq = data_scaled.copy()
    
    # On mémorise la semaine précédente (T-1)
    inc_t_minus_1 = seq[-2, 0] 
    
    # On masque volontairement l'incidence de la semaine actuelle (T)
    seq[-1, 0] = 0 
    
    # On demande au modèle de deviner la VARIATION
    X_input = np.array([seq])
    delta_scaled = nowcaster.predict(X_input, verbose=0)
    
    # Reconstruction mathématique : Valeur absolue = (T-1) + Delta
    pred_abs_scaled = inc_t_minus_1 + delta_scaled[0, 0]
    
    # Dénormalisation
    dummy = np.zeros((1, len(feature_columns)))
    dummy[0, 0] = pred_abs_scaled
    pred_real = scaler.inverse_transform(dummy)[0, 0]
    
    return int(max(0, pred_real)), pred_abs_scaled