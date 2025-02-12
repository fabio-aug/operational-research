import math
import os
import numpy as np
import timeit
import sys
import random

caminho_pasta = './'
arquivos = sorted([f for f in os.listdir(caminho_pasta) if os.path.isfile(os.path.join(caminho_pasta, f))])
arquivos.remove("cv.py")

def print_resultado(start, caminho, custo):
    print(f"Custo: {custo:.3f}")
    tempo = timeit.default_timer() - start
    horas = int(tempo // 3600)
    minutos = int((tempo % 3600) // 60)
    segundos = tempo % 60
    print(f"Tempo decorrido: {horas}h {minutos}m {segundos:.3f}s")
    print()

def ler_coordenadas(num_vertices, arquivo):
    coordenadas = []
    matriz_montagem = np.zeros((num_vertices, num_vertices))

    for linha in arquivo:
        if linha.strip() == 'EOF':
            break

        valores_linha = linha.split()
        coor_x = float(valores_linha[1])
        coor_y = float(valores_linha[2])

        nova_coord = (coor_x, coor_y)

        for i, coord in enumerate(coordenadas):
            distancia = math.sqrt((nova_coord[0] - coord[0]) ** 2 + (nova_coord[1] - coord[1]) ** 2)
            matriz_montagem[len(coordenadas)][i] = distancia
            matriz_montagem[i][len(coordenadas)] = distancia

        coordenadas.append(nova_coord)

    return matriz_montagem

def grasp(matriz, alfa):
    # Temporizador
    start = timeit.default_timer()

    # Controle de visitados
    nos_visitados = []
    nos = list(range(matriz.shape[1]))
    inicial = 0
    nos.remove(inicial)

    # Valores temporários
    atual = inicial
    custo = 0
    caminho = [atual]

    while nos != []:
        # Vizinhos do nó atual: tupla (vizinho J, custo distância até J)
        vizinhos = [(j, matriz[atual][j]) for j in nos if matriz[atual][j] != 0]
        # Ordena os vizinhos pelo menor custo
        vizinhos = sorted(vizinhos, key=lambda x: x[1])

        # lrc
        primeiro_vizinho = vizinhos[0][1]
        ultimos_vizinho = vizinhos[len(vizinhos) - 1][1]
        lrc = primeiro_vizinho + (alfa * (ultimos_vizinho - primeiro_vizinho))

        # vizinhos lrc
        vizinhos_lrc = [tupla[0] for tupla in vizinhos if tupla[1] <= lrc]

        proximo_no = random.choice(vizinhos_lrc)

        # Atualiza o caminho, custo e nós visitados
        custo += matriz[atual][proximo_no]
        caminho.append(proximo_no)
        nos_visitados.append(proximo_no)
        nos.remove(proximo_no)
        atual = proximo_no

    custo += matriz[atual][inicial]
    caminho.append(inicial)

    # print_resultado(start, caminho, custo)

    return (caminho, custo)

def dois_opt(custo, caminho, matriz):
    start = timeit.default_timer()
    melhorou = True
    melhor_caminho = caminho[:]
    melhor_custo = custo

    # First Option
    while melhorou:
        melhorou = False
        for i in range(1, len(melhor_caminho) - 2):
            for j in range(i + 1, len(melhor_caminho) - 1):

                custo_removido = matriz[melhor_caminho[i-1], melhor_caminho[i]] + matriz[melhor_caminho[j], melhor_caminho[j+1]]
                custo_adicionado = matriz[melhor_caminho[i-1], melhor_caminho[j]] + matriz[melhor_caminho[i], melhor_caminho[j+1]]
                novo_custo = melhor_custo - custo_removido + custo_adicionado

                if novo_custo < melhor_custo:
                    melhor_caminho = melhor_caminho[:i] + melhor_caminho[i:j+1][::-1] + melhor_caminho[j+1:]
                    melhor_custo = novo_custo
                    melhorou = True
                    break
            if melhorou:
                break

    # print_resultado(start, melhor_caminho, melhor_custo)

    return (melhor_caminho, melhor_custo)

def multistart_aleatorio(num_vertices, matriz):
    start = timeit.default_timer()
    div = num_vertices // 5
    num_solucoes = div if div <= 20 else 20
    melhor_caminho = None
    melhor_custo = float('inf')

    for _ in range(num_solucoes):
        # Cria caminho aleatorio com o inicio e fim 0
        caminho_aleatorio = [0]
        outros_elementos = list(range(1, num_vertices))
        random.shuffle(outros_elementos)
        caminho_aleatorio.extend(outros_elementos)
        caminho_aleatorio.append(caminho_aleatorio[0])

        # Calcula custo do caminho aleatorio
        cusro_aleatorio = sum(matriz[caminho_aleatorio[i]][caminho_aleatorio[i+1]] for i in range(len(caminho_aleatorio)-1))

        # Otimiza o caminho com 2opt
        caminho_otimizado, custo_otimizado = dois_opt(cusro_aleatorio, caminho_aleatorio, matriz)

        if custo_otimizado < melhor_custo:
            melhor_caminho = caminho_otimizado
            melhor_custo = custo_otimizado

    print("Melhor solução encontrada com MultiStart Aleatório:")
    print_resultado(start, melhor_caminho, melhor_custo)

    return melhor_caminho, melhor_custo

def multistart_grasp(matriz):
    start = timeit.default_timer()
    melhor_caminho = None
    melhor_custo = float('inf')

    for i in range(11):
        # Valor de alpha para o Grasp
        alpha = i/10

        # Cria o caminho com o Grasp
        caminho_grasp, custo_grasp = grasp(matriz, alpha)

        # Otimiza o caminho com 2opt
        caminho_otimizado, custo_otimizado = dois_opt(custo_grasp, caminho_grasp, matriz)

        if custo_otimizado < melhor_custo:
            melhor_caminho = caminho_otimizado
            melhor_custo = custo_otimizado

    print("Melhor solução encontrada com MultiStart Grasp:")
    print_resultado(start, melhor_caminho, melhor_custo)

    return melhor_caminho, melhor_custo

for arquivo in arquivos:
    matriz_distancias = None
    num_vertices = 0

    with open(f"{caminho_pasta}{arquivo}", 'r') as file:
        for linha in file:
            if linha.startswith('DIMENSION'):
                num_vertices = int(linha.split()[-1])
            elif linha.strip() == 'NODE_COORD_SECTION':
                break

        matriz_distancias = ler_coordenadas(num_vertices, file)

        print(f"Arquivo: {arquivo} ----------------------------------")
        (custo, caminho) = multistart_aleatorio(num_vertices, matriz_distancias)
        (custo, caminho) = multistart_grasp(matriz_distancias)
