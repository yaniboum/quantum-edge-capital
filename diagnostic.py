# Fichier : diagnostic.py
# Objectif : Isoler et tester la connexion à l'API de Myfxbook.

# On a toujours besoin de notre "téléphone" pour appeler Myfxbook
from myfxbook import Myfxbook
import sys

print("--- Lancement du Script de Diagnostic Myfxbook ---")
print("Ce script va tenter de se connecter et de récupérer les données de votre compte.\n")

# --- CONFIGURATION ---
# IMPORTANT : Remplissez ces trois lignes avec vos vrais identifiants.
MYFXBOOK_EMAIL = "yanib25@outlook.com"
MYFXBOOK_PASSWORD = "ibtissamMV25"
MYFXBOOK_ACCOUNT_ID = 11730697 # Remplacez par l'ID numérique de votre compte

# --- LE TEST ---
try:
    # Étape 1 : Tentative de connexion
    print(f"1. Tentative de connexion avec l'email : {MYFXBOOK_EMAIL}...")
    client = Myfxbook(email=MYFXBOOK_EMAIL, password=MYFXBOOK_PASSWORD)
    print("   -> SUCCÈS : Connexion et session obtenues.\n")

    # Étape 2 : Tentative de récupération des données
    print(f"2. Tentative de récupération des données pour l'ID de compte : {MYFXBOOK_ACCOUNT_ID}...")
    
    # La fonction get_daily_gain_history va maintenant afficher la réponse brute de Myfxbook
    daily_data = client.get_daily_gain_history(account_id=MYFXBOOK_ACCOUNT_ID)
    
    # Étape 3 : Analyse du résultat
    print("3. Analyse des résultats...")
    if daily_data:
        print(f"   -> SUCCÈS FINAL : {len(daily_data)} jours de données ont été trouvés et lus correctement.")
        print("\n--- DIAGNOSTIC ---")
        print("Conclusion : La connexion à Myfxbook fonctionne parfaitement.")
        print("Le problème se trouve probablement dans la manière dont le serveur 'app.py' gère les données.")
    else:
        print("   -> ERREUR : La connexion a réussi, mais aucune donnée n'a été retournée par Myfxbook.")
        print("\n--- DIAGNOSTIC ---")
        print("Conclusion : Le problème vient des permissions sur votre compte Myfxbook.")
        print("Même une requête directe ne peut pas lire les données.")

    # Déconnexion propre
    client.logout()

except Exception as e:
    print(f"\n   -> ERREUR CRITIQUE PENDANT LE TEST : {e}")
    print("\n--- DIAGNOSTIC ---")
    print("Conclusion : Une erreur a empêché le script de se terminer.")
    print("Veuillez copier tout ce message et le renvoyer pour analyse.")
    # On force la sortie pour s'assurer que le message d'erreur est bien visible
    sys.exit(1)

print("\n--- Test Terminé ---")

