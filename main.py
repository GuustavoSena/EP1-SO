import os
from collections import deque

# Definição da classe BCP (Bloco de Controle de Processos)
class BCP:
    def __init__(self, nome, prioridade, programa):
        self.nome = nome
        self.prioridade = prioridade
        self.creditos = prioridade
        self.pc = 0  # Contador de Programa
        self.estado = 'Pronto'
        self.registradores = {'X': 0, 'Y': 0}
        self.programa = programa
        self.instrucoes_executadas = 0
        self.trocas = 0  # Número de vezes que o processo foi interrompido

# Função para carregar os programas e criar os processos
def carregar_programas(pasta_programas, arquivo_prioridades):
    tabela_processos = []

    # Carregar os nomes dos arquivos de programas
    arquivos_programas = sorted(os.listdir(pasta_programas))

    prioridades = []
    # Carregar as prioridades
    with open(arquivo_prioridades, 'r') as f:
        prioridades = [int(linha.strip()) for linha in f.readlines()]

    # Carregar os programas
    for idx, arquivo_programa in enumerate(arquivos_programas):
        caminho_programa = os.path.join(pasta_programas, arquivo_programa)

        with open(caminho_programa, 'r') as f:
            linhas = [linha.strip() for linha in f.readlines()]
            nome_programa = linhas[0]
            instrucoes = linhas[1:]

            processo = BCP(nome_programa, prioridades[idx], instrucoes)
            tabela_processos.append(processo)

    return tabela_processos

# Função para carregar o quantum
def carregar_quantum(arquivo_quantum):
    with open(arquivo_quantum, 'r') as f:
        return int(f.read().strip())

# Função para executar o escalonador
def executar_escalonador(tabela_processos, quantum):
    # Ordena os processos prontos de acordo com os creditos (maior prioridade primeiro)
    prontos = sorted(tabela_processos, key=lambda p: p.creditos, reverse=True)
    
    # Fila de processos bloqueados (será preenchida conforme processos entram em E/S)
    bloqueados = deque()

    # Um dicionário para manter o tempo de espera de cada processo bloqueado
    tempo_bloqueado = {}

    # Log de eventos do escalonador (será salvo no arquivo final)
    logfile = []

    # Registrar os processos carregados
    for processo in prontos:
        logfile.append(f"Carregando {processo.nome}")

    # Variáveis para estatísticas
    total_trocas = 0
    total_instrucoes = 0

    # Loop principal do escalonador que roda até que não haja mais processos prontos ou bloqueados
    while prontos or bloqueados:
        
        # Reabastece os creditos se todos forem zero
        if not any(processo.creditos > 0 for processo in prontos + list(bloqueados)):
            for processo in prontos + list(bloqueados):
                processo.creditos = processo.prioridade
            logfile.append("Reiniciando creditos dos processos")

        # Se não houver processos prontos, decrementa o tempo dos bloqueados até que um seja liberado
        if not prontos:
            for processo in bloqueados:
                tempo_bloqueado[processo.nome] -= 1
            
            # Remove processos bloqueados que ficaram sem tempo de espera
            for processo in list(bloqueados):
                if tempo_bloqueado[processo.nome] <= 0:
                    processo.estado = 'Pronto'
                    prontos.append(processo)
                    bloqueados.remove(processo)
                    del tempo_bloqueado[processo.nome]
                    prontos = sorted(prontos, key=lambda p: p.creditos, reverse=True)
                    logfile.append(f"{processo.nome} retornando da E/S para a fila de prontos")
            continue
        
        # Pega o primeiro processo da fila de prontos (o de maior crédito)
        processo_atual = prontos.pop(0)
        logfile.append(f"Executando {processo_atual.nome}")
        
        # Contador de Instrucoes executadas neste quantum
        instrucoes_executadas = 0
        e_s_iniciada = False  # Flag para verificar se houve E/S

        # Executa até atingir o quantum ou até o fim do programa (quantum é o limite de Instrucoes a serem rodadas)
        while instrucoes_executadas < quantum and processo_atual.pc < len(processo_atual.programa):
            instrucao = processo_atual.programa[processo_atual.pc]

            # Executa a instrucao de atribuição para o registrador X
            if instrucao.startswith('X='):
                processo_atual.registradores['X'] = int(instrucao[2:])   
            # Executa a instrucao de atribuição para o registrador Y
            elif instrucao.startswith('Y='):
                processo_atual.registradores['Y'] = int(instrucao[2:])   
            # Executa o comando genérico 'COM'
            elif instrucao == 'COM':
                pass       
            # instrucao de E/S (bloqueia o processo)
            elif instrucao == 'E/S':
                processo_atual.estado = 'Bloqueado'
                bloqueados.append(processo_atual)
                tempo_bloqueado[processo_atual.nome] = 3  # Espera de três quantums
                logfile.append(f"E/S iniciada em {processo_atual.nome}")
                e_s_iniciada = True
                processo_atual.pc += 1
                instrucoes_executadas += 1
                processo_atual.instrucoes_executadas += 1
                break  # Sai do loop porque o processo foi bloqueado
            
            # instrucao de término do programa (SAIDA)
            elif instrucao == 'SAIDA':
                logfile.append(f"{processo_atual.nome} terminado. X={processo_atual.registradores['X']}. Y={processo_atual.registradores['Y']}")
                processo_atual.estado = 'Terminado'
                instrucoes_executadas += 1
                processo_atual.instrucoes_executadas += 1
                processo_atual.trocas += 1
                total_trocas += 1
                break

            # Atualiza o contador de programa para a próxima instrucao
            processo_atual.pc += 1

            # Incrementa o número de Instrucoes executadas
            instrucoes_executadas += 1
            processo_atual.instrucoes_executadas += 1  # Contabiliza o total de Instrucoes executadas pelo processo
        
        # Sempre atualiza total_instrucoes
        total_instrucoes += instrucoes_executadas

        # Verificação de interrupção por fim de quantum ou por E/S
        if processo_atual.estado == 'Pronto' or processo_atual.estado == 'Bloqueado':
            processo_atual.creditos -= 1
            if e_s_iniciada:
                if instrucoes_executadas == 1:
                    logfile.append(f"Interrompendo {processo_atual.nome} apos {instrucoes_executadas} instrucao")
                else:
                    logfile.append(f"Interrompendo {processo_atual.nome} apos {instrucoes_executadas} Instrucoes")
            else:
                logfile.append(f"Interrompendo {processo_atual.nome} apos {instrucoes_executadas} Instrucoes")
            
            processo_atual.trocas += 1
            total_trocas += 1

            if processo_atual.estado == 'Pronto':
                # Coloca o processo de volta na fila de prontos, reordenando pelos creditos restantes
                prontos.append(processo_atual)
                prontos = sorted(prontos, key=lambda p: p.creditos, reverse=True)

        # A cada quantum, decrementa o tempo dos processos bloqueados
        for processo in list(bloqueados):
            tempo_bloqueado[processo.nome] -= 1

            if tempo_bloqueado[processo.nome] <= 0:
                processo.estado = 'Pronto'
                prontos.append(processo)
                bloqueados.remove(processo)
                del tempo_bloqueado[processo.nome]
                prontos = sorted(prontos, key=lambda p: p.creditos, reverse=True)
                logfile.append(f"{processo.nome} retornando da E/S para a fila de prontos")

    # Estatísticas finais
    num_processos = len(tabela_processos)
    media_trocas = total_trocas / num_processos if num_processos > 0 else 0
    media_instrucoes = total_instrucoes / total_trocas if total_trocas > 0 else 0

    logfile.append(f"MEDIA DE TROCAS: {media_trocas:.2f}")
    logfile.append(f"MEDIA DE Instrucoes: {media_instrucoes:.2f}")
    logfile.append(f"QUANTUM: {quantum}")
    
    # Retorna o log gerado durante a execução
    return logfile


# Função principal para carregar os dados e executar o escalonador
def main():
    pasta_programas = 'programas'
    arquivo_prioridades = 'prioridades.txt'
    arquivo_quantum = 'quantum.txt'

    tabela_processos = carregar_programas(pasta_programas, arquivo_prioridades)
    quantum = carregar_quantum(arquivo_quantum)
    logfile = executar_escalonador(tabela_processos, quantum)

    # Salvando o logfile
    with open(f"log{quantum:02d}.txt", 'w') as f:
        for linha in logfile:
            f.write(linha + '\n')

if __name__ == "__main__":
    main()
    
    # Notebook com começo da analise: https://colab.research.google.com/drive/1f1oTjhXcrlSewJ2zf4piUJ6Ivnbj19RQ#scrollTo=jZCKptiofKnH
