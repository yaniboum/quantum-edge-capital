import requests
import json

class Myfxbook:
    def __init__(self, email, password):
        self.session = requests.Session()
        self.base_url = "https://www.myfxbook.com/api"
        self.email = email
        self.password = password
        self.session_id = None
        try:
            self._login()
        except Exception as e:
            print(f"ERREUR LORS DE L'INITIALISATION DE MYFXBOOK : {e}")
            raise

    def _login(self):
        """Se connecte à Myfxbook et stocke l'ID de session."""
        endpoint = "/login.json"
        params = {'email': self.email, 'password': self.password}
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("error", False):
            raise Exception(f"La connexion à Myfxbook a échoué : {data.get('message', 'Erreur inconnue')}")
        self.session_id = data.get("session")
        print("Connexion à Myfxbook réussie.")

    def get_daily_gain_history(self, account_id):
        """Récupère l'historique des gains quotidiens pour un compte spécifique."""
        if not self.session_id:
            raise Exception("Non connecté à Myfxbook.")
        
        endpoint = "/get-data-daily.json"
        params = {'session': self.session_id, 'id': str(account_id)}
        response = self.session.get(f"{self.base_url}{endpoint}", params=params)
        
        # Affiche la réponse brute de Myfxbook pour le diagnostic
        print("\n--- Réponse Brute de Myfxbook ---")
        print(response.text)
        print("---------------------------------\n")

        response.raise_for_status()
        data = response.json()

        if data.get("error", False):
            # Fournit une erreur plus détaillée
            error_message = data.get('message', 'Erreur inconnue de Myfxbook.')
            if "Required fields missing" in error_message:
                raise Exception(f"Échec de la récupération des données : {error_message}. Cela indique presque toujours un problème de permissions sur Myfxbook. Veuillez revérifier les permissions de votre compte.")
            else:
                raise Exception(f"Échec de la récupération des données : {error_message}")
        
        # Convertit les données en un format plus facile à utiliser : {date: gain_cumulatif}
        performance_history = {}
        daily_data = data.get("dataDaily", [])
        if not daily_data:
            print("AVERTISSEMENT : Aucune donnée quotidienne n'a été trouvée dans la réponse de Myfxbook.")

        for day_data in daily_data:
            performance_history[day_data['date']] = day_data['gain']
        return performance_history

    def logout(self):
        """Se déconnecte de Myfxbook."""
        if not self.session_id: return
        endpoint = "/logout.json"
        params = {'session': self.session_id}
        self.session.get(f"{self.base_url}{endpoint}", params=params)
        print("Déconnecté de Myfxbook.")

