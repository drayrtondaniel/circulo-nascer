# ===========================================
# DR. AYRTON - CIRCULO NASCER
# Deploy isolado no Render.com
# ===========================================

import os
from flask import Flask, render_template, request, jsonify, redirect, flash
from datetime import datetime
import requests
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'circulo-nascer-secret-2026')

# ===========================================
# CONFIGURAÇÕES DO CLIENTE
# ===========================================

CLIENT_CONFIG = {
    'id': 'dr_ayrton_daniel',
    'nome': 'Dr. Ayrton Daniel',
    'slug': 'circulo-nascer',
    'theme': {
        'primary': '#4a5d52',  # sage-deep
        'secondary': '#c9b896',  # champagne
        'offwhite': '#faf9f6',
        'charcoal': '#2c2c2c'
    },
    'whatsapp': '5519999462258',
    'calcom_username': 'dr-ayrton',
    'analytics_gtm': 'GTM-CIRCULONASCER'
}

# Sendpulse config
SENDPULSE_API_KEY = os.getenv('SENDPULSE_API_KEY', 'sp_apikey_a05039a079f133206d81f2482d0a6023f49f63d31d9da2041444a146c39d3649')
SENDPULSE_LIST_ID = '14509883'

# ===========================================
# ROTAS
# ===========================================

@app.route('/')
def landing():
    """Landing principal do Dr. Ayrton"""
    return render_template('index.html', client=CLIENT_CONFIG)

@app.route('/onboarding')
def onboarding():
    """Quiz de triagem"""
    return render_template('quiz.html', client=CLIENT_CONFIG)

@app.route('/agendamento')
def agendamento():
    """Página de agendamento via Cal.com"""
    return redirect(f"https://cal.com/{CLIENT_CONFIG['calcom_username']}?origem=site")

@app.route('/obrigado')
def obrigado():
    """Página de obrigado após quiz"""
    plano = request.args.get('plano', 'essential')
    return render_template('obrigado.html', client=CLIENT_CONFIG, plano=plano)

@app.route('/lead', methods=['POST'])
def capturar_lead():
    """Captura lead do quiz"""
    data = request.json
    lead = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'data': datetime.now().isoformat(),
        'nome': data.get('nome', ''),
        'email': data.get('email', ''),
        'whatsapp': data.get('whatsapp', ''),
        'trimestre': data.get('trimestre', ''),
        'plano': data.get('plano', ''),
        'origem': 'quiz_onboarding'
    }

    # Salvar lead
    salvar_lead(lead)

    # Notificar Telegram se configurado
    notificar_telegram(lead)

    # Enviar para Sendpulse
    enviar_sendpulse(lead)

    return jsonify({'status': 'ok', 'lead_id': lead['id']})

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'cliente': CLIENT_CONFIG['nome'],
        'timestamp': datetime.now().isoformat()
    })

# ===========================================
# UTILITÁRIOS
# ===========================================

def salvar_lead(lead):
    """Salva lead em arquivo JSON"""
    try:
        os.makedirs('data/leads', exist_ok=True)
        arquivo = f"data/leads/{lead['id']}.json"
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(lead, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar lead: {e}")

def notificar_telegram(lead):
    """Envia notificação de novo lead"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat = os.getenv('TELEGRAM_CHAT_ID')

    if not telegram_token or not telegram_chat:
        return

    try:
        mensagem = f"""🔔 Novo Lead - Círculo Nascer

👤 {lead['nome']}
📧 {lead['email']}
📱 {lead['whatsapp']}
📅 Trimestre: {lead['trimestre']}
💰 Plano: {lead['plano']}

🌐 Origem: Quiz Onboarding"""

        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        requests.post(url, json={
            'chat_id': telegram_chat,
            'text': mensagem,
            'parse_mode': 'HTML'
        }, timeout=10)
    except Exception as e:
        print(f"Erro Telegram: {e}")

def enviar_sendpulse(lead):
    """Envia lead para lista do Sendpulse"""
    if not SENDPULSE_API_KEY:
        print("Sendpulse: API key não configurada")
        return

    try:
        url = "https://api.sendpulse.com/rest/addressbooks/" + SENDPULSE_LIST_ID + "/emails"
        payload = {
            "email": lead.get('email', ''),
            "variables": {
                "name": lead.get('nome', ''),
                "phone": lead.get('whatsapp', ''),
                "trimestre": lead.get('trimestre', ''),
                "plano": lead.get('plano', ''),
                "origem": lead.get('origem', '')
            }
        }
        headers = {
            "Authorization": "Bearer " + SENDPULSE_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            print(f"Sendpulse: Email {lead.get('email')} adicionado à lista")
        else:
            print(f"Sendpulse: Erro {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro Sendpulse: {e}")

# ===========================================
# SERVIDOR
# ===========================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)