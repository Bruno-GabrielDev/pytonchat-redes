"""
PyChat - Cliente TCP
IFSP São Carlos - Redes de Computadores
Projeto de Sockets TCP com chat multi-cliente
"""

import socket
import threading
import sys

HOST = '127.0.0.1'  
PORT = 5000        
rodando = True      


def receber(cliente: socket.socket):
    """
    Thread que fica escutando mensagens vindas do servidor
    e as imprime no terminal do usuário.
    """
    global rodando
    while rodando:
        try:
            dados = cliente.recv(1024)
            if not dados:
                print("\n[Sistema] Servidor encerrou a conexão.")
                rodando = False
                break
            print(dados.decode('utf-8'), end='')
        except OSError:
            break
        except Exception as e:
            if rodando:
                print(f"\n[Erro] {e}")
            break


def enviar(cliente: socket.socket):
    """
    Thread que lê entradas do teclado e as envia ao servidor.
    """
    global rodando
    while rodando:
        try:
            mensagem = input()
            if not rodando:
                break
            cliente.send(mensagem.encode('utf-8'))
            if mensagem.strip() == '/sair':
                rodando = False
                break
        except (EOFError, KeyboardInterrupt):
            rodando = False
            try:
                cliente.send(b'/sair')
            except Exception:
                pass
            break
        except OSError:
            break


def conectar():
    """
    Ponto de entrada do cliente.
    1. Pede o apelido ao usuário.
    2. Conecta ao servidor via TCP.
    3. Realiza o handshake de apelido.
    4. Inicia as threads de envio e recebimento.
    """
    global rodando

    apelido = input("Digite seu apelido: ").strip()
    if not apelido:
        print("[Erro] Apelido não pode ser vazio.")
        sys.exit(1)

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"[Erro] Não foi possível conectar a {HOST}:{PORT}.")
        print("Verifique se o servidor está rodando e se HOST/PORT estão corretos.")
        sys.exit(1)
    try:
        sinal = cliente.recv(1024)

        if sinal == b'NICK':
            cliente.send(apelido.encode('utf-8'))
        elif sinal == b'NICK_TAKEN':
            print(f"[Erro] O apelido '{apelido}' já está em uso. Escolha outro.")
            cliente.close()
            sys.exit(1)
        else:
            print("[Erro] Resposta inesperada do servidor.")
            cliente.close()
            sys.exit(1)
        import select
        pronto, _, _ = select.select([cliente], [], [], 0.3)
        if pronto:
            resposta = cliente.recv(1024)
            if resposta == b'NICK_TAKEN':
                print(f"[Erro] O apelido '{apelido}' já está em uso. Escolha outro.")
                cliente.close()
                sys.exit(1)
            else:
                print(resposta.decode('utf-8'), end='')

    except Exception as e:
        print(f"[Erro] Falha no handshake: {e}")
        cliente.close()
        sys.exit(1)

    print(f"[Sistema] Conectado ao servidor {HOST}:{PORT} como '{apelido}'.")
    print("[Sistema] Digite /ajuda para ver os comandos.\n")

    t_recv = threading.Thread(target=receber, args=(cliente,), daemon=True)
    t_send = threading.Thread(target=enviar,  args=(cliente,), daemon=True)

    t_recv.start()
    t_send.start()
    
    t_recv.join()
    t_send.join()

    print("[Sistema] Desconectado.")
    try:
        cliente.close()
    except Exception:
        pass


if __name__ == '__main__':
    conectar()
