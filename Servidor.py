"""
PyChat - Servidor TCP
IFSP São Carlos - Redes de Computadores
Projeto de Sockets TCP com chat multi-cliente
"""

import socket
import threading
from datetime import datetime

# ─── Configurações ────────────────────────────────────────────────────────────
HOST = '0.0.0.0'   # Aceita conexões de qualquer interface de rede
PORT = 5000        # Porta que o servidor irá escutar

# ─── Estado global do servidor ────────────────────────────────────────────────
clientes   = []   # Lista de sockets conectados
apelidos   = []   # Lista de apelidos (mesma ordem que `clientes`)
lock       = threading.Lock()  # Evita condições de corrida ao alterar as listas

# ─── Utilitários ──────────────────────────────────────────────────────────────

def timestamp():
    """Retorna a hora atual formatada para logs."""
    return datetime.now().strftime('%H:%M:%S')


def log(msg):
    """Imprime uma mensagem de log no console do servidor."""
    print(f"[{timestamp()}] {msg}")


def broadcast(mensagem: bytes, remetente=None):
    """
    Envia `mensagem` para todos os clientes conectados.
    Se `remetente` for fornecido, ele não recebe a própria mensagem.
    """
    with lock:
        destinos = list(clientes)  # cópia para iterar com segurança

    for cliente in destinos:
        if cliente != remetente:
            try:
                cliente.send(mensagem)
            except Exception:
                remover_cliente(cliente)


def remover_cliente(cliente):
    """Remove um cliente da lista e fecha sua conexão."""
    with lock:
        if cliente not in clientes:
            return
        idx = clientes.index(cliente)
        apelido = apelidos[idx]
        clientes.pop(idx)
        apelidos.pop(idx)

    try:
        cliente.close()
    except Exception:
        pass

    log(f"{apelido} desconectou.")
    broadcast(f"[Sistema] {apelido} saiu do chat.\n".encode('utf-8'))


def enviar_privado(remetente_socket, remetente_nick, destinatario_nick, conteudo):
    """Envia uma mensagem privada entre dois usuários."""
    with lock:
        if destinatario_nick not in apelidos:
            remetente_socket.send(
                f"[Sistema] Usuário '{destinatario_nick}' não encontrado.\n".encode('utf-8')
            )
            return
        idx = apelidos.index(destinatario_nick)
        dest_socket = clientes[idx]

    dest_socket.send(f"[Privado de {remetente_nick}]: {conteudo}\n".encode('utf-8'))
    remetente_socket.send(f"[Privado para {destinatario_nick}]: {conteudo}\n".encode('utf-8'))


# ─── Handler de cada cliente ──────────────────────────────────────────────────

def handle_cliente(cliente_socket):
    """
    Roda em uma thread separada para cada cliente.
    Processa mensagens recebidas e as trata como comandos ou texto comum.
    """
    while True:
        try:
            dados = cliente_socket.recv(1024)
            if not dados:
                break

            mensagem = dados.decode('utf-8').strip()

            with lock:
                if cliente_socket not in clientes:
                    break
                apelido = apelidos[clientes.index(cliente_socket)]

            # ── Comandos ──────────────────────────────────────────────────────

            # /msg <destinatario> <texto>  →  mensagem privada
            if mensagem.startswith('/msg '):
                partes = mensagem.split(' ', 2)
                if len(partes) < 3:
                    cliente_socket.send(b"[Sistema] Uso: /msg <apelido> <mensagem>\n")
                else:
                    enviar_privado(cliente_socket, apelido, partes[1], partes[2])

            # /users  →  lista de usuários online
            elif mensagem == '/users':
                with lock:
                    lista = ', '.join(apelidos) if apelidos else '(ninguém)'
                cliente_socket.send(
                    f"[Sistema] Usuários online ({len(apelidos)}): {lista}\n".encode('utf-8')
                )

            # /sair  →  desconexão voluntária
            elif mensagem == '/sair':
                break

            # /ajuda  →  lista de comandos
            elif mensagem == '/ajuda':
                ajuda = (
                    "[Sistema] Comandos disponíveis:\n"
                    "  /users              → lista usuários online\n"
                    "  /msg <nick> <texto> → mensagem privada\n"
                    "  /sair               → desconectar\n"
                    "  /ajuda              → esta mensagem\n"
                )
                cliente_socket.send(ajuda.encode('utf-8'))

            # ── Mensagem comum ────────────────────────────────────────────────
            else:
                log(f"{apelido}: {mensagem}")
                broadcast(
                    f"[{apelido}]: {mensagem}\n".encode('utf-8'),
                    remetente=cliente_socket
                )

        except ConnectionResetError:
            break
        except Exception as e:
            log(f"Erro no cliente: {e}")
            break

    remover_cliente(cliente_socket)


# ─── Loop principal do servidor ───────────────────────────────────────────────

def iniciar():
    """Inicializa o servidor e aguarda conexões indefinidamente."""
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()

    log(f"Servidor PyChat iniciado em {HOST}:{PORT}")
    log("Aguardando conexões...")

    while True:
        cliente_socket, endereco = servidor.accept()
        log(f"Nova conexão de {endereco[0]}:{endereco[1]}")

        # Protocolo de handshake: pede o apelido ao cliente
        try:
            cliente_socket.send(b'NICK')
            apelido = cliente_socket.recv(1024).decode('utf-8').strip()

            # Verifica se o apelido já está em uso
            with lock:
                if apelido in apelidos:
                    cliente_socket.send(b'NICK_TAKEN')
                    cliente_socket.close()
                    log(f"Apelido '{apelido}' já em uso. Conexão recusada.")
                    continue

                clientes.append(cliente_socket)
                apelidos.append(apelido)

            log(f"{apelido} entrou no chat.")
            broadcast(f"[Sistema] {apelido} entrou no chat!\n".encode('utf-8'),
                      remetente=cliente_socket)

            boas_vindas = (
                f"[Sistema] Bem-vindo(a), {apelido}!\n"
                "[Sistema] Digite /ajuda para ver os comandos disponíveis.\n"
            )
            cliente_socket.send(boas_vindas.encode('utf-8'))

            # Inicia thread para este cliente
            t = threading.Thread(target=handle_cliente, args=(cliente_socket,), daemon=True)
            t.start()

        except Exception as e:
            log(f"Erro ao aceitar cliente: {e}")
            cliente_socket.close()


if __name__ == '__main__':
    iniciar()