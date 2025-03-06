# Instâncias: http://mistic.heig-vd.ch/taillard/problemes.dir/vrp.dir/vrp.html

import math
import os
import numpy as np
import sys
import math
import timeit
import random

caminho_pasta = './'
arquivos = sorted([f for f in os.listdir(caminho_pasta) if os.path.isfile(os.path.join(caminho_pasta, f))])
arquivos.remove("rv.py")

def print_resultado(start, rota, custo, melhor_custo):
    print(f"Custo Obtido: {custo:.3f}")
    print(f"Melhor Custo: {melhor_custo:.3f}")
    print(f"Gap de diferença: {(((custo - melhor_custo) / melhor_custo) * 100):.2f}%")
    tempo = timeit.default_timer() - start
    horas = int(tempo // 3600)
    minutos = int((tempo % 3600) // 60)
    segundos = tempo % 60
    print(f"Tempo decorrido: {horas}h {minutos}m {segundos:.3f}s")
    # print(f"Rota {rota}")
    print()

def ler_arquivo(arquivo):
    matriz = None
    clientes = 0
    melhor_solucao = 0
    capacidade_veiculo = 0
    deposito_x = 0
    deposito_y = 0

    i = 0
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

    demandas = []
    matriz = np.zeros((clientes + 1, clientes + 1))
    for linha in arquivo:
        if linha.strip() == '':
            break

        valores_linha = linha.split()

        x1, y1 = int(valores_linha[1]), int(valores_linha[2])
        x2, y2 = deposito_x, deposito_y
        distancia = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        matriz[0][int(valores_linha[0])] = distancia
        matriz[int(valores_linha[0])][0] = distancia

        for cliente in demandas:
            x2, y2 = cliente['x'], cliente['y']
            distancia = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            matriz[cliente['id']][int(valores_linha[0])] = distancia
            matriz[int(valores_linha[0])][cliente['id']] = distancia

        demandas.append({
            'id': int(valores_linha[0]),
            'x': int(valores_linha[1]),
            'y': int(valores_linha[2]),
            'demanda': int(valores_linha[3])
        })

    return (melhor_solucao, capacidade_veiculo, matriz, demandas)

def grasp(capacidade_veiculo, matriz, demandas, alfa):
    # Controle de visitados
    nos_visitados = []
    nos = list(range(matriz.shape[1]))
    inicial = 0
    nos.remove(inicial)

    # Valores temporários
    atual = inicial
    custo_total = 0
    capacidade_atual = capacidade_veiculo
    rotas = []
    rota_atual = [atual]
    
    while nos:
        # Vizinhos do nó atual: tupla (vizinho J, custo distância até J)
        vizinhos = []
        for j in nos:
            if matriz[atual][j] != 0 and capacidade_atual >= demandas[j - 1]['demanda']:
                vizinhos.append((j, matriz[atual][j]))
        
        # Caso não exista vizinhos volta para ponto_a origem
        if not vizinhos:
            rota_atual.append(inicial)
            custo_total += matriz[atual][inicial]
            rotas.append({'rota': rota_atual, 'capacidade': capacidade_atual })
            rota_atual = [inicial]
            capacidade_atual = capacidade_veiculo
            atual = inicial
            continue
        
        # Ordena os vizinhos pelo menor custo
        vizinhos = sorted(vizinhos, key=lambda x: x[1])
    
        # lrc
        primeiro_vizinho = vizinhos[0][1]
        ultimo_vizinho = vizinhos[len(vizinhos) - 1][1]
        lrc = primeiro_vizinho + (alfa * (ultimo_vizinho - primeiro_vizinho))
        
        # lrc
        vizinhos_lrc = []
        for v in vizinhos:
            # Custo menor que o valor lrc
            if v[1] <= lrc:
                vizinhos_lrc.append(v[0])
        
        # Random proximo vizinho
        proximo_no = random.choice(vizinhos_lrc)

        # Atualiza o caminho, custo e nós visitados
        custo_total += matriz[atual][proximo_no]
        rota_atual.append(proximo_no)
        nos_visitados.append(proximo_no)
        nos.remove(proximo_no)
        capacidade_atual -= demandas[proximo_no - 1]['demanda']
        demandas[proximo_no - 1]['demanda'] = 0
        atual = proximo_no
    
    rota_atual.append(inicial)
    custo_total += matriz[atual][inicial]
    rotas.append({'rota': rota_atual, 'capacidade': capacidade_atual })

    return (rotas, custo_total)

def dois_opt(custo, caminho, matriz):
    melhorou = True
    melhor_caminho = caminho[:]
    melhor_custo = custo

    while melhorou:
        melhorou = False
        for i in range(1, len(melhor_caminho) - 2):
            for j in range(i + 1, len(melhor_caminho) - 1):

                custo_removido = matriz[melhor_caminho[i-1], melhor_caminho[i]
                                        ] + matriz[melhor_caminho[j], melhor_caminho[j+1]]
                custo_adicionado = matriz[melhor_caminho[i-1], melhor_caminho[j]
                                          ] + matriz[melhor_caminho[i], melhor_caminho[j+1]]
                novo_custo = melhor_custo - custo_removido + custo_adicionado

                if novo_custo < melhor_custo:
                    melhor_caminho = melhor_caminho[:i] + \
                        melhor_caminho[i:j+1][::-1] + melhor_caminho[j+1:]
                    melhor_custo = novo_custo
                    melhorou = True
                    break
            if melhorou:
                break

    return (melhor_caminho, melhor_custo)

def swap(custo, caminho, matriz):
    n = len(caminho)

    caminho_atual = caminho[:]
    custo_atual = custo

    while True:
        melhorou = False
        for i in range(1, n - 2):
            for j in range(i + 2, n - 1):
                custo_removido = (matriz[caminho_atual[i]][caminho_atual[i - 1]] +
                                  matriz[caminho_atual[i]][caminho_atual[i + 1]] +
                                  matriz[caminho_atual[j]][caminho_atual[j - 1]] +
                                  matriz[caminho_atual[j]][caminho_atual[j + 1]])

                custo_adicionado = (matriz[caminho_atual[j]][caminho_atual[i - 1]] +
                                    matriz[caminho_atual[j]][caminho_atual[i + 1]] +
                                    matriz[caminho_atual[i]][caminho_atual[j + 1]] +
                                    matriz[caminho_atual[i]][caminho_atual[j - 1]])

                novo_custo = custo_atual - custo_removido + custo_adicionado

                if novo_custo < custo_atual:
                    aux = caminho_atual[i]
                    caminho_atual[i] = caminho_atual[j]
                    caminho_atual[j] = aux
                    custo_atual = novo_custo
                    melhorou = True
                    break
            if melhorou:
                break
        if not melhorou:
            break

    return (caminho_atual, custo_atual)

def shift(custo, caminho, matriz):
    n = len(caminho)

    caminho_atual = caminho[:]
    custo_atual = custo

    while True:
        melhorou = False
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                custo_removido = (matriz[caminho_atual[i - 1]][caminho_atual[i]] +
                                  matriz[caminho_atual[i]][caminho_atual[i + 1]] +
                                  matriz[caminho_atual[j]][caminho_atual[j + 1]])
                custo_adicionado = (matriz[caminho_atual[i - 1]][caminho_atual[i + 1]] +
                                    matriz[caminho_atual[j]][caminho_atual[i]] +
                                    matriz[caminho_atual[i]][caminho_atual[j + 1]])

                novo_custo = custo_atual - custo_removido + custo_adicionado

                if novo_custo < custo_atual:
                    caminho_atual.insert(j, caminho_atual.pop(i))
                    custo_atual = novo_custo
                    melhorou = True
                    break
            if melhorou:
                break
        if not melhorou:
            break

    return (caminho_atual, custo_atual)

def vnd(rotas, custo, matriz):
    custo_otimo = custo
    for rota in rotas:
        caminho = rota['rota']

        heuristicas = [dois_opt, swap, shift]
        i = 0
        
        while i < len(heuristicas):
            novo_tour, novo_custo = heuristicas[i](custo_otimo, caminho, matriz)
            
            if novo_custo < custo_otimo:
                caminho = novo_tour
                custo_otimo = novo_custo
                i = 0
            else:
                i += 1
        
        rota['rota'] = caminho
    
    return (rotas, custo_otimo)

def pertubacao(rotas, custo, matriz, demandas):
    custo_total = custo
    
    for i in range(len(rotas) - 1):
        for j in range(i + 1, len(rotas)):
            rota1, rota2 = rotas[i]['rota'], rotas[j]['rota']
            capacidade1, capacidade2 = rotas[i]['capacidade'], rotas[j]['capacidade']
            
            for ponto_a in range(1, len(rota1) - 1):
                for ponto_b in range(1, len(rota2) - 1):
                    demanda_a, demanda_b = demandas[rota1[ponto_a] - 1]['demanda'], demandas[rota2[ponto_b] - 1]['demanda']

                    if capacidade1 - demanda_a + demanda_b >= 0 and capacidade2 - demanda_b + demanda_a >= 0:
                        custoRemover = (
                            matriz[rota1[ponto_a - 1]][rota1[ponto_a]] + matriz[rota1[ponto_a]][rota1[ponto_a + 1]] +
                            matriz[rota2[ponto_b - 1]][rota2[ponto_b]] + matriz[rota2[ponto_b]][rota2[ponto_b + 1]]
                        )
                        custoAdicionar = (
                            matriz[rota1[ponto_a - 1]][rota2[ponto_b]] + matriz[rota2[ponto_b]][rota1[ponto_a + 1]] +
                            matriz[rota2[ponto_b - 1]][rota1[ponto_a]] + matriz[rota1[ponto_a]][rota2[ponto_b + 1]]
                        )
                        novo_custo = custo_total - custoRemover + custoAdicionar
                        
                        if novo_custo >= 0 and novo_custo < custo_total:
                            rotas[i]['rota'][ponto_a], rotas[j]['rota'][ponto_b] = rotas[j]['rota'][ponto_b], rotas[i]['rota'][ponto_a]
                            rotas[i]['capacidade'], rotas[j]['capacidade'] = capacidade1 - demanda_a + demanda_b, capacidade2 - demanda_b + demanda_a
                            custo_total = novo_custo
    
    return rotas, custo_total

def resolver(melhor_solucao, capacidade_veiculo, matriz, demandas):
    start = timeit.default_timer()

    alpha = 0.3
    caminho, custo = grasp(capacidade_veiculo, matriz, demandas, alpha)
    caminho_estrela, custo_estrela = caminho.copy(), custo

    qtd_sem_melhoria = 0
    max_sem_melhoria = 100
    temperatura = 1000

    while qtd_sem_melhoria < max_sem_melhoria or temperatura > 100:
        novo_caminho, novo_custo = pertubacao(caminho, custo, matriz, demandas)
        caminho_otimizado, custo_otimizado = vnd(novo_caminho, novo_custo, matriz)

        valor_expo = ((-1 * (custo_otimizado - custo)) / temperatura)
        if valor_expo > 700:
            qtd_sem_melhoria += 1
        else:
            calculo_temperatura = math.exp(valor_expo)
            if custo_otimizado < custo:
                caminho, custo = caminho_otimizado, custo_otimizado
                if custo < custo_estrela:
                    caminho_estrela, custo_estrela = caminho.copy(), custo
            elif calculo_temperatura > random.random():
                caminho, custo = caminho_otimizado, custo_otimizado
                qtd_sem_melhoria += 1
            else:
                qtd_sem_melhoria += 1
        
        aux_temperatura = temperatura * 0.95
        temperatura = aux_temperatura if aux_temperatura > 1 else 1

    if custo < custo_estrela:
        caminho_estrela, custo_estrela = caminho.copy(), custo

    print_resultado(start, caminho_estrela, custo_estrela, melhor_solucao)

for arquivo in arquivos:
    with open(f"{caminho_pasta}{arquivo}", 'r') as file:
        print(f"Arquivo: {arquivo} ----------------------------------")
        (melhor_solucao, capacidade_veiculo, matriz, demandas) = ler_arquivo(file)
        resolver(melhor_solucao, capacidade_veiculo, matriz, demandas)