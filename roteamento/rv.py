# Instâncias de problemas disponíveis em: http://mistic.heig-vd.ch/taillard/problemes.dir/vrp.dir/vrp.html

# Importação das bibliotecas necessárias
import math
import os
import numpy as np
import math
import timeit
import random

# Define o caminho da pasta onde estão os arquivos de instância
caminho_pasta = './'

# Lista e ordena todos os arquivos na pasta, exceto o próprio script
arquivos = sorted([f for f in os.listdir(caminho_pasta) if os.path.isfile(os.path.join(caminho_pasta, f))])
arquivos.remove("rv.py")

def print_resultado(start, rota, custo, melhor_custo):
    print(f"Custo Obtido: {custo:.3f}")
    print(f"Melhor Custo: {melhor_custo:.3f}")
    print(f"Gap de diferença: {(((custo - melhor_custo) / melhor_custo) * 100):.2f}%")

    # Calcula o tempo decorrido
    tempo = timeit.default_timer() - start
    horas = int(tempo // 3600)
    minutos = int((tempo % 3600) // 60)
    segundos = tempo % 60

    print(f"Tempo decorrido: {horas}h {minutos}m {segundos:.3f}s")
    print()

def ler_arquivo(arquivo):
    matriz = None
    clientes = 0
    melhor_solucao = 0
    capacidade_veiculo = 0
    deposito_x = 0
    deposito_y = 0

    i = 0
    # Lê as três primeiras linhas para obter os dados principais do problema
    for linha in arquivo:
        if i == 0:
            clientes = int(linha.split()[0])
            melhor_solucao = float(linha.split()[1])
            i += 1
        elif i == 1:
            capacidade_veiculo = int(linha.split()[0])
            i += 1
        elif i == 2:
            deposito_x = float(linha.split()[0])
            deposito_y = float(linha.split()[1])
            break

    # Inicializa a matriz de distâncias e a lista de demandas
    demandas = []
    matriz = np.zeros((clientes + 1, clientes + 1))

    # Lê os dados dos clientes
    for linha in arquivo:
        if linha.strip() == '':
            break

        valores_linha = linha.split()

        # Coleta as coordenadas do cliente
        x1, y1 = int(valores_linha[1]), int(valores_linha[2])

        # Calcula a distância do depósito até o cliente
        distancia = math.sqrt((x1 - deposito_x) ** 2 + (y1 - deposito_y) ** 2)
        matriz[0][int(valores_linha[0])] = distancia
        matriz[int(valores_linha[0])][0] = distancia

        # Calcula a distância entre todos os clientes
        for cliente in demandas:
            x2, y2 = cliente['x'], cliente['y']
            distancia = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            matriz[cliente['id']][int(valores_linha[0])] = distancia
            matriz[int(valores_linha[0])][cliente['id']] = distancia

        # Adiciona a demanda do cliente
        demandas.append({
            'id': int(valores_linha[0]),
            'x': int(valores_linha[1]),
            'y': int(valores_linha[2]),
            'demanda': int(valores_linha[3])
        })

    return (melhor_solucao, capacidade_veiculo, matriz, demandas)

def grasp(capacidade_veiculo, matriz, demandas, alfa):
    nos = list(range(matriz.shape[1]))  # Lista de nós (clientes e depósito)
    inicial = 0
    nos.remove(inicial)  # Remove o depósito da lista de clientes a visitar

    atual = inicial  # Começa no depósito
    custo_total = 0
    capacidade_atual = capacidade_veiculo
    rotas = []
    rota_atual = [atual]

    while nos:
        vizinhos = []
        for j in nos:
            # Verifica se há conexão e se o veículo pode atender à demanda do cliente
            if matriz[atual][j] != 0 and capacidade_atual >= demandas[j - 1]['demanda']:
                vizinhos.append((j, matriz[atual][j]))

        # Se não houver vizinhos viáveis, retorna ao depósito e inicia nova rota
        if not vizinhos:
            rota_atual.append(inicial)
            custo_total += matriz[atual][inicial]
            rotas.append({'rota': rota_atual, 'capacidade': capacidade_atual})
            rota_atual = [inicial]
            capacidade_atual = capacidade_veiculo
            atual = inicial
            continue

        # Ordena os vizinhos pelo menor custo (distância)
        vizinhos = sorted(vizinhos, key=lambda x: x[1])

        # Calcula o limite da lista restrita de candidatos (LRC)
        primeiro_vizinho = vizinhos[0][1]
        ultimo_vizinho = vizinhos[-1][1]
        lrc = primeiro_vizinho + (alfa * (ultimo_vizinho - primeiro_vizinho))

        # Cria a LRC com candidatos dentro do limite de custo
        vizinhos_lrc = [v[0] for v in vizinhos if v[1] <= lrc]

        # Escolhe aleatoriamente um cliente da LRC
        proximo_no = random.choice(vizinhos_lrc)

        # Atualiza o caminho, custo e capacidade do veículo
        custo_total += matriz[atual][proximo_no]
        rota_atual.append(proximo_no)
        nos.remove(proximo_no)
        capacidade_atual -= demandas[proximo_no - 1]['demanda']
        demandas[proximo_no - 1]['demanda'] = 0
        atual = proximo_no

    # Finaliza a última rota retornando ao depósito
    rota_atual.append(inicial)
    custo_total += matriz[atual][inicial]
    rotas.append({'rota': rota_atual, 'capacidade': capacidade_atual})

    return rotas, custo_total

def dois_opt(custo, caminho, matriz):
    melhorou = True  # Variável para controlar se houve melhoria
    melhor_caminho = caminho[:]  # Copia a rota original
    melhor_custo = custo  # Define o custo inicial da rota

    while melhorou:
        melhorou = False  # Assume que não há melhoria inicial
        for i in range(1, len(melhor_caminho) - 2):
            for j in range(i + 1, len(melhor_caminho) - 1):

                # Calcula o custo ao remover as conexões entre os pontos i e j
                custo_removido = matriz[melhor_caminho[i-1], melhor_caminho[i]] + matriz[melhor_caminho[j], melhor_caminho[j+1]]
                
                # Calcula o custo ao adicionar uma conexão invertendo o trecho entre i e j
                custo_adicionado = matriz[melhor_caminho[i-1], melhor_caminho[j]] + matriz[melhor_caminho[i], melhor_caminho[j+1]]
                
                # Novo custo total após a alteração
                novo_custo = melhor_custo - custo_removido + custo_adicionado

                # Se a nova solução for melhor, realiza a inversão do trecho
                if novo_custo < melhor_custo:
                    melhor_caminho = melhor_caminho[:i] + melhor_caminho[i:j+1][::-1] + melhor_caminho[j+1:]
                    melhor_custo = novo_custo
                    melhorou = True  # Indica que houve uma melhoria
                    break  # Sai do loop para iniciar nova verificação
            if melhorou:
                break  # Sai do laço externo se houve uma melhoria

    return (melhor_caminho, melhor_custo)  # Retorna o caminho otimizado e o novo custo

def swap(custo, caminho, matriz):
    n = len(caminho)
    
    caminho_atual = caminho[:]  # Copia a rota original
    custo_atual = custo  # Define o custo inicial da rota

    while True:
        melhorou = False  # Assume que não há melhoria inicial
        for i in range(1, n - 2):
            for j in range(i + 2, n - 1):
                # Calcula o custo antes da troca
                custo_removido = (matriz[caminho_atual[i]][caminho_atual[i - 1]] +
                                  matriz[caminho_atual[i]][caminho_atual[i + 1]] +
                                  matriz[caminho_atual[j]][caminho_atual[j - 1]] +
                                  matriz[caminho_atual[j]][caminho_atual[j + 1]])

                # Calcula o custo após a troca
                custo_adicionado = (matriz[caminho_atual[j]][caminho_atual[i - 1]] +
                                    matriz[caminho_atual[j]][caminho_atual[i + 1]] +
                                    matriz[caminho_atual[i]][caminho_atual[j + 1]] +
                                    matriz[caminho_atual[i]][caminho_atual[j - 1]])

                # Novo custo total após a troca
                novo_custo = custo_atual - custo_removido + custo_adicionado

                # Se a troca reduzir o custo, realiza a troca dos nós i e j
                if novo_custo < custo_atual:
                    aux = caminho_atual[i]
                    caminho_atual[i] = caminho_atual[j]
                    caminho_atual[j] = aux
                    custo_atual = novo_custo
                    melhorou = True  # Indica que houve uma melhoria
                    break  # Sai do loop interno
            if melhorou:
                break  # Sai do loop externo se houve uma melhoria
        if not melhorou:
            break  # Sai do loop principal se não houver mais melhorias

    return (caminho_atual, custo_atual)  # Retorna o caminho otimizado e o novo custo

def shift(custo, caminho, matriz):
    n = len(caminho)

    caminho_atual = caminho[:]  # Copia a rota original
    custo_atual = custo  # Define o custo inicial da rota

    while True:
        melhorou = False  # Assume que não há melhoria inicial
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                # Calcula o custo antes da movimentação do nó
                custo_removido = (matriz[caminho_atual[i - 1]][caminho_atual[i]] +
                                  matriz[caminho_atual[i]][caminho_atual[i + 1]] +
                                  matriz[caminho_atual[j]][caminho_atual[j + 1]])
                
                # Calcula o custo após movimentar o nó para a nova posição
                custo_adicionado = (matriz[caminho_atual[i - 1]][caminho_atual[i + 1]] +
                                    matriz[caminho_atual[j]][caminho_atual[i]] +
                                    matriz[caminho_atual[i]][caminho_atual[j + 1]])

                # Novo custo total após a movimentação
                novo_custo = custo_atual - custo_removido + custo_adicionado

                # Se a movimentação reduzir o custo, realiza o deslocamento do nó i para j
                if novo_custo < custo_atual:
                    caminho_atual.insert(j, caminho_atual.pop(i))
                    custo_atual = novo_custo
                    melhorou = True  # Indica que houve uma melhoria
                    break  # Sai do loop interno
            if melhorou:
                break  # Sai do loop externo se houve uma melhoria
        if not melhorou:
            break  # Sai do loop principal se não houver mais melhorias

    return (caminho_atual, custo_atual)  # Retorna o caminho otimizado e o novo custo

def vnd(rotas, custo, matriz):
    custo_otimo = custo  # Inicializa o custo ótimo com o custo da solução atual

    for rota in rotas:
        caminho = rota['rota']  # Obtém a rota atual

        heuristicas = [dois_opt, swap, shift]  # Lista de heurísticas a serem aplicadas
        i = 0  # Índice para percorrer as heurísticas
        
        while i < len(heuristicas):
            # Aplica a heurística atual à rota
            novo_tour, novo_custo = heuristicas[i](custo_otimo, caminho, matriz)
            
            # Se a heurística melhorou o custo, reinicia a busca com a nova solução
            if novo_custo < custo_otimo:
                caminho = novo_tour
                custo_otimo = novo_custo
                i = 0  # Retorna para a primeira heurística
            else:
                i += 1  # Passa para a próxima heurística
        
        # Atualiza a rota com a melhor solução encontrada
        rota['rota'] = caminho
    
    return (rotas, custo_otimo)  # Retorna as rotas otimizadas e o custo final

def pertubacao(rotas, custo, matriz, demandas):
    custo_total = custo  # Inicializa o custo total com o custo atual das rotas
    
    # Executa a perturbação para aproximadamente metade das rotas existentes
    for _ in range(int(len(rotas) / 2)):  
        # Seleciona aleatoriamente duas rotas diferentes
        i = random.randint(1, len(rotas) - 2)  # Escolhe uma rota inicial aleatória
        j = random.randint(i + 1, len(rotas) - 1)  # Escolhe outra rota diferente

        # Obtém as rotas e suas respectivas capacidades
        rota1, rota2 = rotas[i]['rota'], rotas[j]['rota']
        capacidade1, capacidade2 = rotas[i]['capacidade'], rotas[j]['capacidade']
        
        # Percorre os pontos dentro das duas rotas selecionadas
        for ponto_a in range(1, len(rota1) - 1):
            for ponto_b in range(1, len(rota2) - 1):
                # Obtém as demandas dos clientes nos pontos selecionados
                demanda_a, demanda_b = demandas[rota1[ponto_a] - 1]['demanda'], demandas[rota2[ponto_b] - 1]['demanda']
                # Verifica se a troca de clientes entre as rotas mantém a capacidade dos veículos válida
                if capacidade1 - demanda_a + demanda_b >= 0 and capacidade2 - demanda_b + demanda_a >= 0:
                    # Calcula o custo antes da troca
                    custoRemover = (
                        matriz[rota1[ponto_a - 1]][rota1[ponto_a]] + matriz[rota1[ponto_a]][rota1[ponto_a + 1]] +  # Removendo cliente de rota1
                        matriz[rota2[ponto_b - 1]][rota2[ponto_b]] + matriz[rota2[ponto_b]][rota2[ponto_b + 1]]    # Removendo cliente de rota2
                    )

                    # Calcula o custo após a troca
                    custoAdicionar = (
                        matriz[rota1[ponto_a - 1]][rota2[ponto_b]] + matriz[rota2[ponto_b]][rota1[ponto_a + 1]] +  # Adicionando cliente de rota2 em rota1
                        matriz[rota2[ponto_b - 1]][rota1[ponto_a]] + matriz[rota1[ponto_a]][rota2[ponto_b + 1]]    # Adicionando cliente de rota1 em rota2
                    )

                    # Calcula o novo custo total após a troca
                    novo_custo = custo_total - custoRemover + custoAdicionar

                    # Se o novo custo for válido e menor que o custo atual, aplica a troca
                    if novo_custo >= 0 and novo_custo < custo_total:
                        # Troca os clientes entre as rotas
                        rotas[i]['rota'][ponto_a], rotas[j]['rota'][ponto_b] = rotas[j]['rota'][ponto_b], rotas[i]['rota'][ponto_a]

                        # Atualiza as capacidades das rotas após a troca
                        rotas[i]['capacidade'], rotas[j]['capacidade'] = capacidade1 - demanda_a + demanda_b, capacidade2 - demanda_b + demanda_a
                        
                        # Atualiza o custo total após a troca bem-sucedida
                        custo_total = novo_custo

    return rotas, custo_total  # Retorna as rotas modificadas e o novo custo total

def resolver(melhor_solucao, capacidade_veiculo, matriz, demandas):
    # Inicia a contagem do tempo de execução
    start = timeit.default_timer()

    # Define o parâmetro alfa para o GRASP (quanto menor, mais guloso)
    alpha = 0.3  

    # Gera uma solução inicial usando o algoritmo GRASP
    caminho, custo = grasp(capacidade_veiculo, matriz, demandas, alpha)

    # Copia a melhor solução encontrada até o momento
    caminho_estrela, custo_estrela = caminho.copy(), custo  

    # Inicializa os parâmetros de controle
    qtd_sem_melhoria = 0  # Contador de iterações sem melhoria
    max_sem_melhoria = 100  # Número máximo de iterações sem melhoria antes de parar
    temperatura = 1000  # Parâmetro do simulated annealing para aceitar soluções piores

    # Loop principal de busca de soluções melhores
    while qtd_sem_melhoria < max_sem_melhoria or temperatura > 100:
        # Realiza uma perturbação na solução atual para explorar novas possibilidades
        novo_caminho, novo_custo = pertubacao(caminho, custo, matriz, demandas)

        # Aplica a busca local VND (Variable Neighborhood Descent) na solução perturbada
        caminho_otimizado, custo_otimizado = vnd(novo_caminho, novo_custo, matriz)

        # Calcula a variação do custo normalizada pela temperatura (Simulated Annealing)
        valor_expo = ((-1 * (custo_otimizado - custo)) / temperatura)

        # Se o valor exponencial for muito alto, considera que a solução é significativamente pior
        if valor_expo > 700:
            qtd_sem_melhoria += 1  # Incrementa contador de iterações sem melhoria
        else:
            # Calcula a probabilidade de aceitação da solução pior no simulated annealing
            calculo_temperatura = math.exp(valor_expo)
            # Se a nova solução for melhor, aceita diretamente
            if custo_otimizado < custo:
                caminho, custo = caminho_otimizado, custo_otimizado
                # Atualiza a melhor solução global se a nova for melhor
                if custo < custo_estrela:
                    caminho_estrela, custo_estrela = caminho.copy(), custo
            # Se a nova solução for pior, pode aceitá-la com certa probabilidade (simulated annealing)
            elif calculo_temperatura > random.random():
                caminho, custo = caminho_otimizado, custo_otimizado
                qtd_sem_melhoria += 1  # Conta a iteração sem melhoria
            else:
                qtd_sem_melhoria += 1  # Conta a iteração sem melhoria

        # Diminui a temperatura para reduzir a aceitação de soluções piores ao longo das iterações
        aux_temperatura = temperatura * 0.95  # Multiplica a temperatura por 0.95
        temperatura = aux_temperatura if aux_temperatura > 1 else 1  # Garante que não seja menor que 1

    # Após o término do loop, verifica se a última solução encontrada foi a melhor
    if custo < custo_estrela:
        caminho_estrela, custo_estrela = caminho.copy(), custo

    # Imprime os resultados finais da melhor solução encontrada
    print_resultado(start, caminho_estrela, custo_estrela, melhor_solucao)

for arquivo in arquivos:
    with open(f"{caminho_pasta}{arquivo}", 'r') as file:
        print(f"Arquivo: {arquivo} ----------------------------------")
        (melhor_solucao, capacidade_veiculo, matriz, demandas) = ler_arquivo(file)
        resolver(melhor_solucao, capacidade_veiculo, matriz, demandas)