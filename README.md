# 💬 PytonChat — Chat Multi-Cliente TCP

Projeto de Redes de Computadores — IFSP São Carlos  
Implementação de sockets TCP em Python com suporte a múltiplos clientes simultâneos.

---

## 📁 Estrutura do Projeto

```
chat_tcp/
├── servidor.py   # Servidor TCP (roda uma vez, aceita N clientes)
├── cliente.py    # Cliente TCP (cada usuário executa este arquivo)
└── README.md     # Este arquivo
```

---

## ▶️ Como executar

### Pré-requisito
- Python 3.8 ou superior instalado  
- Nenhuma biblioteca externa necessária (só biblioteca padrão do Python)

### 1. Inicie o servidor

```bash
python servidor.py
```

O servidor ficará aguardando conexões na porta **5000**.

### 2. Conecte clientes (em terminais separados)

```bash
python cliente.py
```

Digite um apelido único quando solicitado.  
Repita em quantos terminais quiser para simular vários usuários.

### 3. Teste em máquinas diferentes

No `cliente.py`, altere a linha:
```python
HOST = '127.0.0.1'
```
Para o IP da máquina onde o servidor está rodando. Ex.:
```python
HOST = '192.168.1.10'
```

---

## 💬 Comandos disponíveis no chat

| Comando | Descrição |
|---|---|
| `<mensagem>` | Envia mensagem para todos |
| `/msg <apelido> <texto>` | Mensagem privada para um usuário |
| `/users` | Lista os usuários online |
| `/ajuda` | Exibe os comandos disponíveis |
| `/sair` | Desconecta do servidor |

---

## 🔧 Como funciona (resumo técnico)

- **Protocolo:** TCP (confiável, orientado a conexão)
- **Servidor:** usa `threading` para atender múltiplos clientes simultaneamente
- **Handshake:** ao conectar, o servidor envia `NICK` e o cliente responde com seu apelido
- **Broadcast:** mensagens são repassadas para todos os clientes conectados
- **Privado:** `/msg` roteia a mensagem apenas para o destinatário correto
- **Thread safety:** uso de `threading.Lock` para proteger as listas compartilhadas

---

## 📹 Vídeo de demonstração

> https://youtu.be/bXtcOT4uLQo

---

## 👥 Integrantes

| Nome | RA |
|---|---|
| Bruno Gabriel | Sc3044122 |
