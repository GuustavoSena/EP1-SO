import os
import pandas as pd

# Diretório onde estão os arquivos .txt
diretorio = "logs"

# Lista para armazenar os dados extraídos
dados = []

# Loop para percorrer os arquivos
for filename in os.listdir(diretorio):
    if filename.endswith(".txt"):
        with open(os.path.join(diretorio, filename), 'r') as file:
            linhas = file.readlines()

            # Inicializa variáveis
            media_trocas = None
            media_instrucoes = None
            quantum = None
            
            # Extrai os dados
            for linha in linhas:
                if "MEDIA DE TROCAS" in linha:
                    media_trocas = float(linha.split(":")[1].strip())
                elif "MEDIA DE Instrucoes" in linha:
                    media_instrucoes = float(linha.split(":")[1].strip())
                elif "QUANTUM" in linha:
                    quantum = int(linha.split(":")[1].strip())
            
            # Adiciona os dados à lista
            if media_trocas is not None and media_instrucoes is not None and quantum is not None:
                dados.append([media_trocas, media_instrucoes, quantum])

# Cria um DataFrame com os dados
df = pd.DataFrame(dados, columns=["Média de Trocas", "Média de Instruções", "Quantum"])

# Salva o DataFrame em um arquivo CSV
df.to_csv('resultado.csv', index=False)

print("Dados exportados com sucesso para resultado.csv")
