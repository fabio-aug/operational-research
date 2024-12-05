import math
import os
import numpy as np
import timeit

caminho_pasta = './'
arquivos = sorted([f for f in os.listdir(caminho_pasta) if os.path.isfile(os.path.join(caminho_pasta, f))])
arquivos.remove("cv.py")

def calcular_distancia(ponto1, ponto2):
    return math.sqrt((ponto1[0] - ponto2[0]) ** 2 + (ponto1[1] - ponto2[1]) ** 2)

def print_resultado(start, caminho, custo):
    print(f"Custo: {custo:.3f}")
    tempo = timeit.default_timer() - start
    horas = int(tempo // 3600)
    minutos = int((tempo % 3600) // 60)
    segundos = tempo % 60
    print(f"Tempo decorrido: {horas}h {minutos}m {segundos:.3f}s")
    print()

def vizinho_mais_proximo(num_vertices, matriz):
    start = timeit.default_timer()
    caminho = [0]
    nao_visiatos = list(range(1, num_vertices))
    custo = 0

    minutos_break = 0
    inicio = 0
    index = inicio
    while len(caminho) < num_vertices and minutos_break < 30:
        menor_distancia = 0
        indice = 0
        for idx in nao_visiatos:
            if matriz[index][idx] != 0:
                if menor_distancia == 0:
                    menor_distancia = matriz[index][idx]
                    indice = idx
                elif matriz[index][idx] < menor_distancia:
                    menor_distancia = matriz[index][idx]
                    indice = idx
        caminho.append(indice)
        nao_visiatos.remove(indice)
        custo += menor_distancia
        index = indice
        tempo = timeit.default_timer() - start
        minutos_break = int((tempo % 3600) // 60)

    custo += matriz[index][inicio]
    caminho.append(0)

    print("Vizinho mais proximo:")
    print_resultado(start, caminho, custo)

def insercao_mais_barata(num_vertices, matriz):
    start = timeit.default_timer()
    caminho = [0, 1, 0]
    visitados = [0, 1]
    nao_visiatos = list(range(2, num_vertices))

    minutos_break = 0
    while len(visitados) < num_vertices and minutos_break < 30:
        melhor_custo = -1
        vertice_caminho = -1
        posicao_caminho = 0

        for vertice_atual in nao_visiatos:
            for i in range(1, len(caminho)):
                vertice_anterior = caminho[i-1]
                vertice_posterior = caminho[i]

                custo_atual = (
                    matriz[vertice_anterior][vertice_atual] +
                    matriz[vertice_atual][vertice_posterior] -
                    matriz[vertice_anterior][vertice_posterior]
                )

                if melhor_custo == -1 or custo_atual < melhor_custo:
                    melhor_custo = custo_atual
                    vertice_caminho = vertice_atual
                    posicao_caminho = i

        nao_visiatos.remove(vertice_caminho)
        caminho.insert(posicao_caminho, vertice_caminho)
        visitados.append(vertice_caminho)
        tempo = timeit.default_timer() - start
        minutos_break = int((tempo % 3600) // 60)

    custo_total = 0
    for i in range(1, len(caminho)):
        custo_total += matriz[caminho[i-1]][caminho[i]]

    print("Inserção mais barata:")
    print_resultado(start, caminho, custo_total)

def munari(num_vertices, matriz):
    start = timeit.default_timer()

    aux_valor = -1
    aux_indice = -1
    for i, valor in enumerate(matriz[0]):
        if i == 0:
            continue
        if aux_valor == -1 or valor > aux_valor:
            aux_valor = valor
            aux_indice = i

    caminho = [0, aux_indice, 0]
    visitados = [0, aux_indice]

    nao_visiatos = list(range(1, num_vertices))
    nao_visiatos.remove(aux_indice)

    minutos_break = 0
    while len(visitados) < num_vertices and minutos_break < 30:
        custos = []
        indices = []

        for lugar_visitado in visitados:
            custo_lugar_visitado = []
            indice_lugar_visitado = []

            for vertice_atual in nao_visiatos:
                custo_lugar_visitado.append(matriz[lugar_visitado][vertice_atual])
                indice_lugar_visitado.append(vertice_atual)

            menor_distancia, indice = min((valor, idx) for idx, valor in enumerate(custo_lugar_visitado))

            custos.append(menor_distancia)
            indices.append(indice_lugar_visitado[indice])

        menor_valor, indice = max((valor, idx) for idx, valor in enumerate(custos))
        item_pra_inserir = indices[indice]

        melhor_custo = -1
        posicao_caminho = 0

        for i in range(1, len(caminho)):
            vertice_anterior = caminho[i-1]
            vertice_posterior = caminho[i]

            custo_atual = (
                matriz[vertice_anterior][item_pra_inserir] +
                matriz[item_pra_inserir][vertice_posterior] -
                matriz[vertice_anterior][vertice_posterior]
            )

            if melhor_custo == -1 or custo_atual < melhor_custo:
                melhor_custo = custo_atual
                posicao_caminho = i

        caminho.insert(posicao_caminho, item_pra_inserir)
        visitados.append(item_pra_inserir)
        nao_visiatos.remove(item_pra_inserir)
        tempo = timeit.default_timer() - start
        minutos_break = int((tempo % 3600) // 60)

    custo_total = 0
    for i in range(1, len(caminho)):
        custo_total += matriz[caminho[i-1]][caminho[i]]

    print("Munari:")
    print_resultado(start, caminho, custo_total)

def read_node_coord(num_vertices, file):
    coordenadas = []
    matriz_montagem = np.zeros((num_vertices, num_vertices))

    for linha in file:
        if linha.strip() == 'EOF':
            break

        valores_linha = linha.split()
        coor_x = float(valores_linha[1])
        coor_y = float(valores_linha[2])

        nova_coord = (coor_x, coor_y)

        for i, coord in enumerate(coordenadas):
            distancia = calcular_distancia(nova_coord, coord)
            matriz_montagem[len(coordenadas)][i] = distancia
            matriz_montagem[i][len(coordenadas)] = distancia

        coordenadas.append(nova_coord)

    return matriz_montagem

for arquivo in arquivos:
    matriz_distancias = None
    num_vertices = 0

    with open(f"{caminho_pasta}{arquivo}", 'r') as file:
        for linha in file:
            if linha.startswith('DIMENSION'):
                num_vertices = int(linha.split()[-1])
            elif linha.strip() == 'NODE_COORD_SECTION':
                break

        matriz_distancias = read_node_coord(num_vertices, file)

        print(f"Arquivo: {arquivo} ----------------------------------")
        vizinho_mais_proximo(num_vertices, matriz_distancias)
        insercao_mais_barata(num_vertices, matriz_distancias)
        munari(num_vertices, matriz_distancias)