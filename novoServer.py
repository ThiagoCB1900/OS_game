import socket
import json
import threading

# Carregar perguntas do arquivo JSON
with open('questions.json', 'r') as f:
    data = json.load(f)
    perguntas = data['questions']

# Configurações do servidor
HOST = '127.0.0.1'
PORT = 65432
MAX_PLAYERS = 4

# Criar o socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Servidor iniciado e aguardando até {MAX_PLAYERS} jogadores...")

conexoes = []
pontuacao = [0] * MAX_PLAYERS
jogadores_prontos = threading.Event()

# Aceitar conexões de jogadores até o número máximo
while len(conexoes) < MAX_PLAYERS:
    conn, addr = server_socket.accept()
    conexoes.append(conn)
    print(f"Jogador {len(conexoes)} conectado: {addr}")

print("Todos os jogadores conectados. Iniciando o jogo...")
jogadores_prontos.set()

def handle_player(conn, player_id):
    jogadores_prontos.wait()
    try:
        for pergunta in perguntas:
            mensagem = json.dumps(pergunta)
            conn.sendall(mensagem.encode())  # Enviar pergunta
            resposta = conn.recv(1024).decode()  # Receber resposta
            if resposta.isdigit() and int(resposta) == pergunta['awnser_index']:
                pontuacao[player_id] += 1
    except (ConnectionResetError, BrokenPipeError):
        print(f"Jogador {player_id + 1} desconectado.")
    finally:
        try:
            conn.sendall("Jogo finalizado.".encode())
        except:
            pass  # Ignore o erro se não conseguir enviar a mensagem
        conn.close()  # Garantir que a conexão seja fechada

# Iniciar threads para cada jogador
for i, conn in enumerate(conexoes):
    threading.Thread(target=handle_player, args=(conn, i)).start()

# Esperar as threads terminarem antes de exibir pontuação final
for thread in threading.enumerate():
    if thread is not threading.main_thread():
        thread.join()

# Exibir pontuação final
print("Pontuações finais:", pontuacao)
