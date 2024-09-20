import socket
import json

# Configurações do cliente
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 65432        # Porta que o servidor está ouvindo

# Criar socket do cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

print("Conectado ao servidor. Aguarde as perguntas...\n")

# Função para receber perguntas e enviar respostas
def jogo():
    while True:
        # Receber pergunta do servidor
        pergunta = client_socket.recv(1024).decode()
        
        # Verifique o conteúdo recebido antes de tentar decodificar
        print(f"Mensagem recebida do servidor: {pergunta}")
        
        if not pergunta:
            print("Mensagem vazia recebida. Encerrando...")
            break  # Se a mensagem estiver vazia, encerra o loop
        
        # Decodificar a mensagem recebida
        try:
            pergunta = json.loads(pergunta)
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar a pergunta: {e}")
            break

        # Exibir pergunta e opções
        print("\n" + pergunta['text'])
        for idx, opcao in enumerate(pergunta['alternatives']):
            print(f"{idx}) {opcao}")
        
        # Enviar resposta ao servidor (índice da alternativa)
        resposta = input("Digite o número da sua resposta: ")
        client_socket.sendall(resposta.encode())
    
    # Receber e exibir pontuação final
    pontuacao_final = client_socket.recv(1024).decode()
    print(pontuacao_final)

# Iniciar o jogo
jogo()

# Fechar conexão
client_socket.close()
