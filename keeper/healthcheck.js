/**
 * Keeper - Health Check para Círculo Nascer
 * Envia ping para o endpoint /ping do Render.com
 */

const https = require('https');

const PING_URL = 'https://circulo-nascer.onrender.com/ping';
const TIMEOUT = 10000; // 10 segundos

console.log(`[${new Date().toISOString()}] Keeper: Ping em ${PING_URL}`);

const req = https.get(PING_URL, { timeout: TIMEOUT }, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    if (res.statusCode === 200 && data.trim() === 'ok') {
      console.log(`[${new Date().toISOString()}] ✅ SUCESSO: ${PING_URL} retornou "ok"`);
      process.exit(0);
    } else {
      console.error(`[${new Date().toISOString()}] ❌ FALHA: Status ${res.statusCode}, body: "${data.trim()}"`);
      process.exit(1);
    }
  });
});

req.on('error', (err) => {
  console.error(`[${new Date().toISOString()}] ❌ ERRO: ${err.message}`);
  process.exit(1);
});

req.on('timeout', () => {
  console.error(`[${new Date().toISOString()}] ❌ TIMEOUT: ${TIMEOUT}ms`);
  req.destroy();
  process.exit(1);
});
