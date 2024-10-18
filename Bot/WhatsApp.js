const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');


const client = new Client({
    authStrategy: new LocalAuth() // Armazenar as credenciais localmente
});

// QR Code
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('Cliente está pronto e conectado!');
});

client.on('message', async (msg) => {
    if(msg.from === "anynumber@c.us") {
        console.log(`Mensagem recebida: ${msg.body}`);


        const url = 'http://127.0.0.1:8000/ask/';
        const data = {
            question: msg.body
        };

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na requisição: ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                console.log(data[0]);
                client.sendMessage(msg.from, data[0])
            })
            .catch(error => {
                console.error('Erro ao chamar a API:', error);
                client.sendMessage(msg.from, "Erro ao processar sua requisição");
            });
    }

});

// Inicializar o cliente
client.initialize();
