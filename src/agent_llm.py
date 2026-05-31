import os
from google import genai
from dotenv import load_dotenv

# 1. Chargement sécurisé de la clé API
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = None
if api_key:
    # 2. Initialisation du nouveau Client Google GenAI
    client = genai.Client(api_key=api_key)

def generer_bulletin_alerte(cas_prevus, niveau_alerte, chemin_protocole="docs/protocole_orsan_reb.md"):
    """
    Agent RAG : Lit le protocole officiel et génère une alerte logistique 
    basée sur les prédictions du modèle BiLSTM.
    """
    if client is None:
        return (
            "⚠️ **L'Agent IA RAG est désactivé** car la clé `GEMINI_API_KEY` est manquante ou "
            "incorrecte dans le fichier `.env`.\n\n"
            "Pour l'activer :\n"
            "1. Créez un fichier `.env` à la racine du projet.\n"
            "2. Ajoutez la ligne : `GEMINI_API_KEY=votre_cle_gemini`.\n"
            "3. Redémarrez l'application."
        )
    
    # Extraction du contexte (Le RAG)
    try:
        with open(chemin_protocole, "r", encoding="utf-8") as file:
            protocole_texte = file.read()
    except FileNotFoundError:
        return "Erreur : Le fichier de protocole est introuvable. Vérifiez le chemin."

    # Construction du Prompt Structuré
    prompt = f"""
    Tu es le Système d'Aide à la Décision (SAD) du projet Epi-Trace, conçu par des ingénieurs en IA.
    Ton rôle est de rédiger un bulletin d'alerte logistique et médical clair, direct et professionnel.

    Voici les données prédictives actuelles (Forecasting) :
    - Prédiction d'incidence pour J+7 : {cas_prevus} cas.
    - Niveau de tension estimé : Niveau {niveau_alerte}.

    Voici le protocole sanitaire officiel (ORSAN REB) que tu DOIS respecter à la lettre :
    {protocole_texte}

    Instructions strictes :
    1. Identifie le niveau d'alerte correspondant à la prédiction dans le protocole.
    2. Rédige le bulletin en listant EXCLUSIVEMENT les actions requises pour ce niveau précis.
    3. Divise ta réponse avec ces titres précis : 
       - 🏥 DIRECTIVES HÔPITAUX
       - 💊 DIRECTIVES PHARMACIES
       - 🩺 DIRECTIVES MÉDECINE DE VILLE
    4. N'invente AUCUNE procédure médicale. Si ce n'est pas dans le texte du protocole, ne le dis pas.
    """

    # Inférence LLM avec la nouvelle syntaxe
    try:
        # On utilise gemini-2.5-flash, la dernière version ultra-rapide
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Erreur de l'API Gemini : {e}"

# --- Test du script ---
if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    print(" Lancement de l'Agent Epi-Trace (Nouvelle Architecture GenAI)...")
    
    # Simulation d'une prédiction de votre BiLSTM (ex: 1450 cas -> Niveau 3)
    bulletin = generer_bulletin_alerte(cas_prevus=1450, niveau_alerte=3)
    
    print("\n" + "="*50)
    print(" BULLETIN D'ALERTE GÉNÉRÉ ")
    print("="*50 + "\n")
    print(bulletin)