import math
import os
import numpy as np
import timeit
import random

caminho_pasta = './'
arquivos = sorted([f for f in os.listdir(caminho_pasta)
                  if os.path.isfile(os.path.join(caminho_pasta, f))])
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
            distancia = math.sqrt(
                (nova_coord[0] - coord[0]) ** 2 + (nova_coord[1] - coord[1]) ** 2)
            matriz_montagem[len(coordenadas)][i] = distancia
            matriz_montagem[i][len(coordenadas)] = distancia

        coordenadas.append(nova_coord)

    return matriz_montagem

def grasp(matriz, alfa):
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
        vizinhos = [(j, matriz[atual][j])
                    for j in nos if matriz[atual][j] != 0]
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

    return (caminho, custo)

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
                    melhor_caminho = melhor_caminho[:i] + melhor_caminho[i:j+1][::-1] + melhor_caminho[j+1:]
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
                    caminho_atual[i], caminho_atual[j] = caminho_atual[j], caminho_atual[i]
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

def vnd(custo, caminho, matriz):
    estruturas = [dois_opt, swap, shift]
    i = 0

    while i < len(estruturas):
        novo_caminho, novo_custo = estruturas[i](custo, caminho, matriz)

        if novo_custo < custo:
            caminho, custo = novo_caminho, novo_custo
            i = 0
        else:
            i += 1

    return (caminho, custo)

def vns(custo, caminho, matriz, vizinhanca):
    i = random.randint(1, len(matriz[0]) - 2)
    j = random.randint(i + 1, len(matriz[0]) - 1)

    # dois_opt
    if (vizinhanca == 0):
        custo_removido = matriz[caminho[i-1], caminho[i]
                                ] + matriz[caminho[j], caminho[j+1]]
        custo_adicionado = matriz[caminho[i-1],
                                  caminho[j]] + matriz[caminho[i], caminho[j+1]]
        novo_custo = custo - custo_removido + custo_adicionado

        novo_caminho = caminho[:i] + caminho[i:j+1][::-1] + caminho[j+1:]

        return (novo_caminho, novo_custo)
    # swap
    elif vizinhanca == 1:
        custo_removido = (matriz[caminho[i]][caminho[i - 1]] +
                          matriz[caminho[i]][caminho[i + 1]] +
                          matriz[caminho[j]][caminho[j - 1]] +
                          matriz[caminho[j]][caminho[j + 1]])
        custo_adicionado = (matriz[caminho[j]][caminho[i - 1]] +
                            matriz[caminho[j]][caminho[i + 1]] +
                            matriz[caminho[i]][caminho[j + 1]] +
                            matriz[caminho[i]][caminho[j - 1]])
        novo_custo = custo - custo_removido + custo_adicionado

        novo_caminho = caminho.copy()
        novo_caminho[i], novo_caminho[j] = novo_caminho[j], novo_caminho[i]

        return (novo_caminho, novo_custo)
    # shift
    else:
        custo_removido = (matriz[caminho[i - 1]][caminho[i]] +
                          matriz[caminho[i]][caminho[i + 1]] +
                          matriz[caminho[j]][caminho[j + 1]])
        custo_adicionado = (matriz[caminho[i - 1]][caminho[i + 1]] +
                            matriz[caminho[j]][caminho[i]] +
                            matriz[caminho[i]][caminho[j + 1]])
        novo_custo = custo - custo_removido + custo_adicionado

        novo_caminho = caminho.copy()
        novo_caminho.insert(j, novo_caminho.pop(i))

        return (caminho, custo)

def grasp_vnd(matriz):
    start = timeit.default_timer()
    melhor_caminho = None
    melhor_custo = float('inf')

    alpha = 0.3
    caminho_grasp, custo_grasp = grasp(matriz, alpha)
    caminho_otimizado, custo_otimizado = vnd(
        custo_grasp, caminho_grasp, matriz)

    if custo_otimizado < melhor_custo:
        melhor_caminho, melhor_custo = caminho_otimizado, custo_otimizado

    print_resultado(start, melhor_caminho, melhor_custo)

    return (melhor_caminho, melhor_custo)

def grasp_vns_nds(matriz):
    start = timeit.default_timer()
    caminho, custo = grasp(matriz, 0.3)
    vizinhanca = 0

    while vizinhanca < 3:
        novo_caminho, novo_custo = vns(custo, caminho, matriz, vizinhanca)
        caminho_otimizado, custo_otimizado = vnd(novo_custo, novo_caminho, matriz)

        if custo_otimizado < custo:
            caminho, custo = caminho_otimizado, custo_otimizado
            vizinhanca = 0
        else:
            vizinhanca += 1
    
    print_resultado(start, caminho, custo)
    return (caminho, custo)

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
        print("VND")
        (custo, caminho) = grasp_vnd(matriz_distancias)
        print("VNS")
        (custo, caminho) = grasp_vns_nds(matriz_distancias)
