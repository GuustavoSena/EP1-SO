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

# Função para carregar os programas e criar os processos
def carregar_programas(pasta_programas, arquivo_prioridades):
    tabela_processos = []

    # Carregar os nomes dos arquivos de programas
    arquivos_programas = sorted(os.listdir(pasta_programas))
    print(f'Nomes dos arquivos de programas: {arquivos_programas}')

    prioridades = []
    # Carregar as prioridades
    with open(arquivo_prioridades, 'r') as f:
        prioridades = [int(linha.strip()) for linha in f.readlines()]
    print(f'Prioridades carregadas: {prioridades}')

    # Carregar os programas
    for idx, arquivo_programa in enumerate(arquivos_programas):
        caminho_programa = os.path.join(pasta_programas, arquivo_programa)
        print(f'\nCarregando o programa {arquivo_programa} (caminho: {caminho_programa})')

        with open(caminho_programa, 'r') as f:
            linhas = [linha.strip() for linha in f.readlines()]
            nome_programa = linhas[0]
            instrucoes = linhas[1:]
            print(f'Nome do Programa: {nome_programa}')
            print(f'Instruções do Programa: {instrucoes}')

            processo = BCP(nome_programa, prioridades[idx], instrucoes)
            print(f'Processo {idx + 1} criado: Nome={processo.nome}, Prioridade={processo.prioridade}, Créditos={processo.creditos}')
            
            tabela_processos.append(processo)
    
    print(f'\nTabela de processos carregada: {[p.nome for p in tabela_processos]}')
    print("-----------------------------------------------------------")
    return tabela_processos



# Função para carregar o quantum
def carregar_quantum(arquivo_quantum):
    with open(arquivo_quantum, 'r') as f:
        return int(f.read().strip())

# Função para executar o escalonador
def executar_escalonador(tabela_processos, quantum):
    # Ordena os processos prontos de acordo com os créditos (maior prioridade primeiro)
    prontos = sorted(tabela_processos, key=lambda p: p.creditos, reverse=True)
    print(f"Fila inicial de processos prontos: {[p.nome for p in prontos]} com créditos: {[p.creditos for p in prontos]}")
    
    # Fila de processos bloqueados (será preenchida conforme processos entram em E/S)
    bloqueados = deque()

    # Log de eventos do escalonador (será salvo no arquivo final)
    logfile = []

    # Loop principal do escalonador que roda até que não haja mais processos prontos ou bloqueados
    while prontos or bloqueados:
        print("\n----- Novo Ciclo -----")
        print(f"Fila de prontos: {[p.nome for p in prontos]} com créditos: {[p.creditos for p in prontos]}")
        print(f"Fila de bloqueados: {[p.nome for p in bloqueados]}")
        
        # Se não houver processos prontos, decrementa o tempo dos bloqueados até que um seja liberado
        if not prontos:
            print("Nenhum processo pronto. Diminuindo os créditos dos bloqueados.")
            for processo in bloqueados:
                # Diminui os créditos dos processos bloqueados a cada iteração
                processo.creditos -= 1
                print(f"Processo bloqueado {processo.nome} agora tem {processo.creditos} créditos.")
            
            # Remove processos bloqueados que ficaram sem créditos (caso raro, mas possível)
            bloqueados = deque([p for p in bloqueados if p.creditos > 0])
            
            # Continua o loop até que haja algum processo pronto
            continue
        
        # Pega o primeiro processo da fila de prontos (o de maior crédito)
        processo_atual = prontos.pop(0)
        print(f"\nExecutando processo: {processo_atual.nome} com {processo_atual.creditos} créditos restantes.")
        logfile.append(f"Executando {processo_atual.nome}")  # Log de início da execução do processo
        
        # Contador de instruções executadas neste quantum
        instrucoes_executadas = 0
        
        # Executa até atingir o quantum ou até o fim do programa (quantum é o limite de instruções a serem rodadas)
        while instrucoes_executadas < quantum and processo_atual.pc < len(processo_atual.programa):
            instrucao = processo_atual.programa[processo_atual.pc]  # Pega a próxima instrução para executar
            print(f"Executando instrução: {instrucao}")

            # Executa a instrução de atribuição para o registrador X
            if instrucao.startswith('X='):
                processo_atual.registradores['X'] = int(instrucao[2:])
                print(f"Registrador X atualizado para: {processo_atual.registradores['X']}")
            
            # Executa a instrução de atribuição para o registrador Y
            elif instrucao.startswith('Y='):
                processo_atual.registradores['Y'] = int(instrucao[2:])
                print(f"Registrador Y atualizado para: {processo_atual.registradores['Y']}")
            
            # Executa o comando genérico 'COM'
            elif instrucao == 'COM':
                print(f"Comando COM executado.")
            
            # Instrução de E/S (bloqueia o processo)
            elif instrucao == 'E/S':
                processo_atual.estado = 'Bloqueado'  # Muda o estado do processo para 'Bloqueado'
                bloqueados.append(processo_atual)  # Adiciona o processo à fila de bloqueados
                logfile.append(f"E/S iniciada em {processo_atual.nome}")  # Log de que o processo foi bloqueado
                print(f"Processo {processo_atual.nome} bloqueado por E/S.")
                break  # Sai do loop porque o processo foi bloqueado
            
            # Instrução de término do programa (SAIDA)
            elif instrucao == 'SAIDA':
                logfile.append(f"{processo_atual.nome} terminado. X={processo_atual.registradores['X']}. Y={processo_atual.registradores['Y']}")
                processo_atual.estado = 'Terminado'  # Muda o estado para 'Terminado'
                print(f"Processo {processo_atual.nome} terminado. Registradores: X={processo_atual.registradores['X']}, Y={processo_atual.registradores['Y']}")
                break  # Sai do loop porque o processo terminou

            # Atualiza o contador de programa para a próxima instrução
            processo_atual.pc += 1

            # Incrementa o número de instruções executadas
            instrucoes_executadas += 1
            processo_atual.instrucoes_executadas += 1  # Contabiliza o total de instruções executadas pelo processo
            print(f"Instruções executadas neste quantum: {instrucoes_executadas}")
        
        # Se o processo não foi bloqueado ou terminado, ele é interrompido por fim de quantum
        if processo_atual.estado == 'Pronto':
            processo_atual.creditos -= 1  # Decrementa os créditos do processo
            logfile.append(f"Interrompendo {processo_atual.nome} após {instrucoes_executadas} instruções")
            print(f"Processo {processo_atual.nome} interrompido após {instrucoes_executadas} instruções. Créditos restantes: {processo_atual.creditos}")
            
            # Coloca o processo de volta na fila de prontos, reordenando pelos créditos restantes
            prontos.append(processo_atual)
            prontos = sorted(prontos, key=lambda p: p.creditos, reverse=True)  # Ordena a fila de prontos novamente

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
