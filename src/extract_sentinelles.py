import pandas as pd
import os

def clean_local_sentinelles_data(input_filename, output_filename):
    print(f"🔄 Nettoyage du fichier Sentinelles local : {input_filename}...")
    
    input_path = os.path.join("data", "brutes", input_filename)
    output_path = os.path.join("data", "brutes", output_filename)
    
    try:
        # On lit le fichier CSV (skiprows=1 pour ignorer l'entête d'information)
        df = pd.read_csv(input_path, skiprows=1)
        
        # Filtre Géographique : On ne garde que l'Île-de-France (Code Insee : 11)
        # Sentiweb stocke le code région dans la colonne 'geo_insee'
        df_idf = df[df['geo_insee'] == 11]
        
        # Sécurité au cas où le code est lu comme du texte ('11' au lieu de 11)
        if df_idf.empty:
            df_idf = df[df['geo_insee'] == '11']

        # Nettoyage : On ne garde que la Semaine (week) et le nombre de cas (inc)
        df_clean = df_idf[['week', 'inc']] 
        
        # Sauvegarde
        df_clean.to_csv(output_path, index=False)
        
        print(f"✅ Succès ! Vérité terrain nettoyée et sauvegardée dans {output_path}")
        print(f"   -> {len(df_clean)} semaines récupérées pour la région Île-de-France.")
        
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier {input_path} est introuvable.")
        print(f"Avez-vous bien placé '{input_filename}' dans le dossier 'data/brutes/' ?")
    except KeyError as e:
        print(f"❌ Erreur de colonne. Le format du fichier a peut-être changé.")
        print(f"Colonnes trouvées : {list(df.columns)}")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")

if __name__ == "__main__":
    # Nom du nouveau fichier régional téléchargé
    clean_local_sentinelles_data("inc-25-RDD-ds2.csv", "sentinelles_idf_brut.csv")