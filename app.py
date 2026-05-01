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

# ===========================================
# SERVIDOR
# ===========================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)