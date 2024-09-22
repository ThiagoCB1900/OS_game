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
MAX_PLAYERS = int(input("Quantos Players vao jogar?\n"))

# Criar o socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Servidor iniciado e aguardando até {MAX_PLAYERS} jogadores...")

conexoes = []
pontuacao = [0] * MAX_PLAYERS
jogadores_prontos = threading.Event()
jogadores_finalizados = threading.Event()
jogadores_finalizados_count = 0

# Barreira para sincronizar a resposta de todos os jogadores
barreira = threading.Barrier(MAX_PLAYERS)
lock = threading.Lock()
pontuou = False  # Flag para verificar se já houve pontuação

# Função para gerenciar o encerramento seguro do jogo
def finalizar_jogo():
    global jogadores_finalizados_count
    jogadores_finalizados_count += 1
    if jogadores_finalizados_count == MAX_PLAYERS:
        jogadores_finalizados.set()

# Aceitar conexões de jogadores até o número máximo
while len(conexoes) < MAX_PLAYERS:
    conn, addr = server_socket.accept()
    conexoes.append(conn)
    print(f"Jogador {len(conexoes)} conectado: {addr}")

print("Todos os jogadores conectados. Iniciando o jogo...")
jogadores_prontos.set()

def handle_player(conn, player_id):
    global pontuou
    jogadores_prontos.wait()
    try:
        for pergunta in perguntas:
            # Esperar que todos os jogadores cheguem aqui
            barreira.wait()
            
            # Reiniciar a flag para nova pergunta
            with lock:
                pontuou = False
            
            # Enviar a pergunta para o jogador
            mensagem = json.dumps(pergunta)
            conn.sendall(mensagem.encode())  # Enviar pergunta

            # Tente receber resposta do jogador
            try:
                resposta = conn.recv(1024).decode()
            except socket.error:
                print(f"Erro na comunicação com o jogador {player_id + 1}.")
                break
            
            # Verificar se a resposta é válida e se foi o primeiro a responder corretamente
            with lock:
                if not pontuou and resposta.isdigit() and int(resposta) == pergunta['awnser_index']:
                    pontuacao[player_id] += 1
                    pontuou = True  # Marcar como já pontuado
                    print(f"Jogador {player_id + 1} foi o primeiro a responder corretamente e pontuou.")

            # Esperar que todos os jogadores respondam antes de enviar a próxima pergunta
            barreira.wait()

    except (ConnectionResetError, BrokenPipeError):
        print(f"Jogador {player_id + 1} desconectado.")
    finally:
        try:
            conn.sendall("Jogo finalizado. Obrigado por jogar!".encode())
        except:
            pass  # Ignore o erro se não conseguir enviar a mensagem
        conn.close()  # Garantir que a conexão seja fechada
        finalizar_jogo()  # Marcar jogador como finalizado

# Iniciar threads para cada jogador
for i, conn in enumerate(conexoes):
    threading.Thread(target=handle_player, args=(conn, i)).start()

# Esperar que todos os jogadores finalizem o jogo
jogadores_finalizados.wait()

# Exibir pontuação final
print("Pontuações finais:", pontuacao)

# Fechar o socket do servidor
server_socket.close()
print("Servidor encerrado.")
