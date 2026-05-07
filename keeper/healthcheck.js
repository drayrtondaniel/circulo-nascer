/**
 * Keeper - Health Check para Círculo Nascer
 * Envia ping para o endpoint /ping do Render.com
 * Com retry para lidar com cold starts do Render
 */

const https = require('https');

const PING_URL = 'https://circulo-nascer.onrender.com/ping';
const TIMEOUT = 10000; // 10 segundos
const MAX_RETRIES = 3;
const INITIAL_DELAY = 2000; // 2 segundos

function tentarPing(tentativa = 1) {
  return new Promise((resolve, reject) => {
    console.log(`[${new Date().toISOString()}] Keeper: Tentativa ${tentativa}/${MAX_RETRIES} - Ping em ${PING_URL}`);

    const req = https.get(PING_URL, { timeout: TIMEOUT }, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        if (res.statusCode === 200 && data.trim() === 'ok') {
          console.log(`[${new Date().toISOString()}] ✅ SUCESSO: ${PING_URL} retornou "ok"`);
          resolve();
        } else {
          reject(new Error(`Status ${res.statusCode}: ${data.trim()}`));
        }
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error(`Timeout ${TIMEOUT}ms`));
    });
  });
}

async function executarKeeper() {
  for (let tentativa = 1; tentativa <= MAX_RETRIES; tentativa++) {
    try {
      await tentarPing(tentativa);
      console.log(`[${new Date().toISOString()}] ✅ Health check completado com sucesso`);
      process.exit(0);
    } catch (err) {
      console.error(`[${new Date().toISOString()}] ❌ Erro tentativa ${tentativa}: ${err.message}`);

      if (tentativa < MAX_RETRIES) {
        const delay = INITIAL_DELAY * Math.pow(2, tentativa - 1); // Backoff exponencial: 2s, 4s, 8s
        console.log(`[${new Date().toISOString()}] ⏳ Aguardando ${delay}ms antes de retry...`);
        await new Promise(r => setTimeout(r, delay));
      } else {
        console.error(`[${new Date().toISOString()}] ❌ FALHA: Todas as ${MAX_RETRIES} tentativas falharam`);
        process.exit(1);
      }
    }
  }
}

executarKeeper();
