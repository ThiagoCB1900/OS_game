import socket
import json

# Carregar perguntas do arquivo JSON
with open('questions.json', 'r') as f:
    data = json.load(f)
    perguntas = data['questions']  # Acessar a lista de perguntas

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 65432        # Porta que o servidor vai ouvir

# Criar o socket do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print("Servidor iniciado e aguardando conexões...")

# Conexões dos jogadores
conexoes = []
pontuacao = [0, 0]  # Pontuação dos jogadores

# Aceitar conexões de 2 jogadores
for i in range(2):
    conn, addr = server_socket.accept()
    conexoes.append(conn)
    print(f"Jogador {i + 1} conectado: {addr}")

# Função para enviar perguntas e receber respostas
def jogo():
    for pergunta in perguntas:
        mensagem = json.dumps(pergunta)  # Converter a pergunta para JSON
        
        # Enviar pergunta para todos os jogadores
        for conn in conexoes:
            conn.sendall(mensagem.encode())

        # Receber respostas dos jogadores
        respostas = []
        for conn in conexoes:
            resposta = conn.recv(1024).decode()
            respostas.append(resposta)

        # Verificar respostas e atualizar pontuação
        for i, resposta in enumerate(respostas):
            if int(resposta) == pergunta['awnser_index']:
                pontuacao[i] += 1

    # Enviar pontuação final para os jogadores
    for conn in conexoes:
        conn.sendall(f"Pontuação final: {pontuacao}".encode())

# Iniciar o jogo
jogo()

# Fechar conexões
for conn in conexoes:
    conn.close()
server_socket.close()
