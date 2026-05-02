# ===========================================
# DR. AYRTON - CIRCULO NASCER
# Deploy isolado no Render.com
# ===========================================

import os
import json
import threading
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, flash
import requests

# Configuração Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'circulo-nascer-secret-2026')

# ===========================================
# TELEGRAM BOT CONFIG (integrado)
# ===========================================

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_NASCER', '8102603154:AAG7J6AJkT4pSzEEN-0Rfso4Pnjmio5Hcnk')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '5842787913')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cal.com URL
CALCOM_URL = "https://cal.com/dr-ayrton-daniel-5t0h6e/30min"
TELEGRAM_DR = "https://t.me/dr_ayrton"

# Respostas do bot
RESPOSTAS = {
    'ola': """Olá! 👋 Sou o assistente do Círculo Nascer.

Estou aqui para te acolher e direcionar ao cuidado que você precisa.

Como posso te ajudar?

1️⃣ Informações sobre planos e valores
2️⃣ Agendar consulta gratuita
3️⃣ Sobre o Dr. Ayrton
4️⃣ Falar com atendente""",

    'preco': """💰 *Planos de Acompanhamento*

➤ *Essencial* - R$ 290/mês
  Consultoria por mensagens, vídeos de orientação

➤ *Acompanhamento* - R$ 490/mês
  Reuniões presenciais, suporte prioritário

➤ *Integral* - R$ 890/mês
  Cuidado completo, atenção dedicada

✨ _Primeiro encontro gratuito!_""",

    'horario': """🕐 *Horários de Atendimento*

Consultório em Campinas/SP:
Segunda a Sexta: 8h às 18h

Atendimento online: Todo o Brasil""",

    'como_funciona': """🤔 *Como funciona?*

1️⃣ Você preenche o quiz de triagem
2️⃣ Indicamos o plano ideal pra você
3️⃣ Agendamos consulta gratuita
4️⃣ Começamos o acompanhamento

Simples assim!""",

    'default': """Desculpe, não entendi. Me avisa o que precisa:

1️⃣ Informações sobre planos
2️⃣ Agendar consulta
3️⃣ Sobre o Dr. Ayrton
4️⃣ Falar com atendente"""
}

def keyboards_principais():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("💰 Planos e Valores", callback_data="preco")],
        [InlineKeyboardButton("📅 Agendar Consulta", callback_data="agendar")],
        [InlineKeyboardButton("👨‍⚕️ Sobre o Dr. Ayrton", callback_data="sobre")],
        [InlineKeyboardButton("❓ Como Funciona", callback_data="como")],
    ]
    return InlineKeyboardMarkup(keyboard)

def keyboard_agendar():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("📅 Agendar Online", url=CALCOM_URL)],
        [InlineKeyboardButton("💬 Falar no Telegram", url=TELEGRAM_DR)],
        [InlineKeyboardButton("📋 Ver Planos", callback_data="preco")],
        [InlineKeyboardButton("⬅️ Voltar", callback_data="voltar")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_update(update, context):
    """Handler das mensagens do bot"""
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

    if update.message:
        texto = update.message.text.lower()
        chat_id = update.message.chat_id

        # Comandos
        if texto in ['/start', 'oi', 'olá', 'iniciar']:
            await context.bot.send_message(
                chat_id=chat_id,
                text=RESPOSTAS['ola'],
                parse_mode='Markdown',
                reply_markup=keyboards_principais()
            )
        elif any(p in texto for p in ['preço', 'valor', 'plano', 'custa']):
            await context.bot.send_message(
                chat_id=chat_id,
                text=RESPOSTAS['preco'],
                parse_mode='Markdown',
                reply_markup=keyboard_agendar()
            )
        elif any(p in texto for p in ['horário', 'horario', 'agenda']):
            await context.bot.send_message(
                chat_id=chat_id,
                text=RESPOSTAS['horario'],
                parse_mode='Markdown',
                reply_markup=keyboard_agendar()
            )
        elif any(p in texto for p in ['funciona', 'como']):
            await context.bot.send_message(
                chat_id=chat_id,
                text=RESPOSTAS['como_funciona'],
                parse_mode='Markdown',
                reply_markup=keyboard_agendar()
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=RESPOSTAS['default'],
                parse_mode='Markdown',
                reply_markup=keyboards_principais()
            )

    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id

        if query.data == 'agendar':
            await context.bot.send_message(
                chat_id=chat_id,
                text="📅 Escolha como prefere ser atendido:",
                reply_markup=keyboard_agendar()
            )
        elif query.data == 'preco':
            await context.bot.send_message(
                chat_id=chat_id,
                text=RESPOSTAS['preco'],
                parse_mode='Markdown',
                reply_markup=keyboard_agendar()
            )
        elif query.data == 'sobre':
            await context.bot.send_message(
                chat_id=chat_id,
                text="👨‍⚕️ *Dr. Ayrton Daniel*\n\n30 anos de experiência\nFormação UFRJ/Unicamp\n\nAgende uma conversa sem compromisso!",
                parse_mode='Markdown',
                reply_markup=keyboard_agendar()
            )
        elif query.data == 'como':
            await context.bot.send_message(
                chat_id=chat_id,
                text=RESPOSTAS['como_funciona'],
                parse_mode='Markdown',
                reply_markup=keyboard_agendar()
            )
        elif query.data == 'voltar':
            await context.bot.send_message(
                chat_id=chat_id,
                text=RESPOSTAS['ola'],
                parse_mode='Markdown',
                reply_markup=keyboards_principais()
            )

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
    'calcom_username': 'dr-ayrton-daniel-5t0h6e',
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

@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    """Webhook para receber mensagens do Telegram"""
    try:
        data = request.get_json()
        logger.info(f"Telegram webhook received: {data}")

        # Extrai dados da mensagem
        message = data.get('message', {})
        text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')

        if not text or not chat_id:
            return jsonify({'ok': True})

        # Responde baseado no texto
        if text in ['/start', 'oi', 'olá', 'iniciar', '/start@NascerBot']:
            response_text = RESPOSTAS['ola']
        elif any(p in text.lower() for p in ['preço', 'valor', 'plano', 'custa']):
            response_text = RESPOSTAS['preco']
        elif any(p in text.lower() for p in ['horário', 'horario', 'agenda']):
            response_text = RESPOSTAS['horario']
        elif any(p in text.lower() for p in ['funciona', 'como']):
            response_text = RESPOSTAS['como_funciona']
        else:
            response_text = RESPOSTAS['default']

        # Envia resposta via Telegram Bot API (sem usar biblioteca telegram)
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': response_text,
            'parse_mode': 'Markdown'
        }
        requests.post(url, json=payload, timeout=10)

    except Exception as e:
        logger.error(f"Erro no webhook: {e}")

    return jsonify({'ok': True})

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