const { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const ws = require('ws');
const qrcode = require('qrcode-terminal');
const pino = require('pino');
const path = require('path');
const fs = require('fs');

const WS_PORT = 3001;
const AUTH_DIR = process.env.AUTH_DIR || path.join(__dirname, 'auth_info_baileys');

// Create auth dir if it doesn't exist
if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
}

const wss = new ws.WebSocketServer({ port: WS_PORT });
let activeSocket = null;
let wsClients = new Set();

console.log(`[Bridge Server] Starting on ws://localhost:${WS_PORT}`);

wss.on('connection', (socket) => {
    console.log('[Bridge Server] Python client connected via WebSocket');
    wsClients.add(socket);

    socket.on('message', async (message) => {
        try {
            const data = JSON.parse(message.toString());
            
            if (data.type === 'auth') {
                console.log(`[Bridge Server] Authenticated client with token: ${data.token ? '***' : 'none'}`);
            } else if (data.type === 'send' && activeSocket) {
                // Send text message via Baileys
                console.log(`[WhatsApp] Sending message to ${data.to}`);
                await activeSocket.sendMessage(data.to, { text: data.text });
            }
        } catch (err) {
            console.error('[Bridge Server] Error processing message:', err.message);
        }
    });

    socket.on('close', () => {
        console.log('[Bridge Server] Python client disconnected');
        wsClients.delete(socket);
    });
});

function broadcast(data) {
    const payload = JSON.stringify(data);
    for (const client of wsClients) {
        if (client.readyState === ws.WebSocket.OPEN) {
            client.send(payload);
        }
    }
}

async function startWhatsApp() {
    console.log('[WhatsApp] Initializing Baileys...');
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`[WhatsApp] using WA v${version.join('.')}, isLatest: ${isLatest}`);

    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        logger: pino({ level: "silent" }) // Disable excessive logging from Baileys
    });

    activeSocket = sock;

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            console.log('\n[WhatsApp] Please scan the QR code to connect:\n');
            qrcode.generate(qr, { small: true });
            broadcast({ type: 'qr', qr: qr });
        }

        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('[WhatsApp] Connection closed due to', lastDisconnect?.error, ', reconnecting:', shouldReconnect);
            broadcast({ type: 'status', status: 'disconnected' });
            
            if (shouldReconnect) {
                startWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('[WhatsApp] Connected and ready!');
            broadcast({ type: 'status', status: 'connected' });
        }
    });

    sock.ev.on('messages.upsert', async (m) => {
        if (m.type !== 'notify') return;
        
        const msg = m.messages[0];
        if (!msg.message || msg.key.fromMe) return; // Skip our own messages
        
        const sender = msg.key.remoteJid;
        
        // Extract text message content
        const messageType = Object.keys(msg.message)[0];
        let content = '';
        if (messageType === 'conversation') {
            content = msg.message.conversation;
        } else if (messageType === 'extendedTextMessage') {
            content = msg.message.extendedTextMessage.text;
        } else {
            console.log(`[WhatsApp] Skipping message type: ${messageType}`);
            return;
        }

        if (!content) return;

        console.log(`[WhatsApp] Received message from ${sender}: ${content}`);

        // Broadcast to Python client
        broadcast({
            type: 'message',
            id: msg.key.id,
            sender: sender,
            content: content,
            timestamp: msg.messageTimestamp,
            isGroup: sender.endsWith('@g.us')
        });
    });
}

// Start WhatsApp on script start
startWhatsApp();
