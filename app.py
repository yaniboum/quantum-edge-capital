from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
import pandas as pd
import json
import random
import requests
import os # Outil pour lire les variables secrètes

app = Flask(__name__, template_folder='templates')
app.secret_key = 'une-cle-secrete-tres-solide-et-longue'

# --- CONFIGURATION POUR L'ENVOI D'EMAILS (SÉCURISÉE) ---
# Le serveur lit maintenant les identifiants depuis les variables d'environnement de Render
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

ADMIN_PASSWORD = "admin_password_123"

MOCK_PERFORMANCE_HISTORY = {
    "2024-01-15": 0.0, "2024-03-01": 8.0, "2024-07-22": 15.0, "2025-10-01": 25.0
}
MOCK_ASSET_PERFORMANCE = {
    "EUR/USD": 12540.30, "XAU/USD": 8750.10, "GBP/JPY": 4120.50, "USO/USD": 2030.00
}

def get_client_data():
    try: return pd.read_csv('clients.csv', sep=',')
    except FileNotFoundError: return None

# --- ROUTES API POUR GEMINI ---
@app.route('/api/strategy-insight', methods=['POST'])
def get_strategy_insight():
    # ... (code inchangé)
    data = request.get_json()
    risk_level = data.get('risk_level', 'Modéré')
    if risk_level == 'Prudent': insight = "Pour un profil prudent..."
    elif risk_level == 'Agressif': insight = "Avec un profil agressif..."
    else: insight = "Pour un profil modéré..."
    return jsonify({'insight': insight})

@app.route('/api/market-summary')
def get_market_summary():
    # ... (code inchangé)
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key: return jsonify({'summary': "Erreur: clé API manquante."}), 500
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
    prompt = "Agis comme un analyste financier... (prompt complet)"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}
    try:
        response = requests.post(api_url, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        summary = data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'summary': "Analyse non disponible (problème de connexion)."}), 500

# --- ROUTES UTILISATEURS ET ADMIN (avec envoi d'email) ---
@app.route('/')
def home(): return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ... (code inchangé)
    if request.method == 'POST':
        email, password = request.form['email'], request.form['password']
        clients_df = get_client_data()
        if clients_df is not None:
            clients_df.columns = clients_df.columns.str.strip()
            user_data = clients_df[clients_df['email'] == email]
            if not user_data.empty and str(user_data.iloc[0]['password']) == str(password):
                session['user_id'] = int(user_data.iloc[0]['client_id'])
                return redirect(url_for('dashboard'))
        flash('Email ou mot de passe incorrect.', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # ... (code inchangé)
    if 'user_id' not in session: return redirect(url_for('login'))
    client_id = session['user_id']
    clients_df = get_client_data()
    clients_df.columns = clients_df.columns.str.strip()
    client_info = clients_df[clients_df['client_id'] == client_id].iloc[0]
    initial_investment = client_info['initial_investment']
    investment_date_str = client_info['investment_date']
    investment_date = datetime.strptime(investment_date_str, '%Y-%m-%d').date()
    closest_start_date = min(MOCK_PERFORMANCE_HISTORY.keys(), key=lambda d: abs(datetime.strptime(d, '%Y-%m-%d').date() - investment_date))
    start_gain_percent = MOCK_PERFORMANCE_HISTORY.get(closest_start_date, 0)
    latest_date = max(MOCK_PERFORMANCE_HISTORY.keys())
    current_gain_percent = MOCK_PERFORMANCE_HISTORY[latest_date]
    performance_gain_during_period = current_gain_percent - start_gain_percent
    performance_multiplier = 1 + (performance_gain_during_period / 100)
    current_balance = initial_investment * performance_multiplier
    profit_loss = current_balance - initial_investment
    percentage_return = (profit_loss / initial_investment) * 100
    dashboard_data = {
        "client_name": client_info['client_name'], "current_balance": f"${current_balance:,.2f}",
        "profit_loss": f"${profit_loss:,.2f}", "percentage_return": f"{percentage_return:.2f}%",
        "profit_loss_color": "text-[#64ffda]" if profit_loss >= 0 else "text-red-500"
    }
    equity_chart_data = [float(initial_investment), float(initial_investment * 1.05), float(initial_investment * 0.98), float(current_balance)]
    donut_chart_data = {'labels': list(MOCK_ASSET_PERFORMANCE.keys()), 'data': list(MOCK_ASSET_PERFORMANCE.values())}
    return render_template('dashboard.html', data=dashboard_data, equity_chart_data=json.dumps(equity_chart_data), donut_chart_data=json.dumps(donut_chart_data))

@app.route('/reports')
def reports():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('reports.html')

@app.route('/settings')
def settings():
    if 'user_id' not in session: return redirect(url_for('login'))
    client_id = session['user_id']
    clients_df = get_client_data()
    clients_df.columns = clients_df.columns.str.strip()
    client_info = clients_df[clients_df['client_id'] == client_id].iloc[0]
    user_data = {'client_name': client_info['client_name'], 'email': client_info['email']}
    return render_template('settings.html', user=user_data)

@app.route('/change_password', methods=['POST'])
def change_password():
    # ... (code inchangé)
    if 'user_id' not in session: return redirect(url_for('login'))
    client_id = session['user_id']
    clients_df = get_client_data()
    clients_df.columns = clients_df.columns.str.strip()
    user_index = clients_df[clients_df['client_id'] == client_id].index
    if not user_index.empty and str(clients_df.loc[user_index[0], 'password']) == request.form['current_password']:
        clients_df.loc[user_index[0], 'password'] = request.form['new_password']
        clients_df.to_csv('clients.csv', index=False)
        flash('Mot de passe mis à jour avec succès !', 'success')
    else:
        flash('Le mot de passe actuel est incorrect.', 'error')
    return redirect(url_for('settings'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # ... (code inchangé)
    if request.method == 'POST' and request.form['password'] == ADMIN_PASSWORD:
        session['is_admin'] = True
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    # ... (code admin inchangé, mais l'envoi d'email fonctionnera maintenant)
    if not session.get('is_admin'): return redirect(url_for('admin_login'))
    clients_df = get_client_data()
    if request.method == 'POST':
        new_id = clients_df['client_id'].max() + 1 if not clients_df.empty else 1
        temp_password = f"temp{random.randint(1000, 9999)}"
        # ... (logique d'ajout au CSV)
        new_client_data = f"\n{new_id},{request.form['client_name']},{request.form['email']},{temp_password},{request.form['initial_investment']},{request.form['investment_date']}"
        with open('clients.csv', 'a') as f: f.write(new_client_data)
        
        try:
            subject = "Bienvenue chez Quantum Edge Capital"
            sender = app.config['MAIL_USERNAME']
            recipients = [request.form['email']]
            body = f"Bonjour {request.form['client_name']},\n\nBienvenue ! Votre compte est créé.\n\nEmail : {request.form['email']}\nMot de passe temporaire : {temp_password}\n\nVeuillez vous connecter et changer votre mot de passe.\n\nCordialement,\nL'équipe de Quantum Edge Capital"
            msg = Message(subject=subject, sender=sender, recipients=recipients, body=body)
            mail.send(msg)
            flash(f"Client '{request.form['client_name']}' ajouté et email envoyé.", "success")
        except Exception as e:
            flash(f"Client ajouté, mais l'envoi de l'email a échoué : {e}", "error")
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_dashboard.html', clients=clients_df.to_dict('records'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)

