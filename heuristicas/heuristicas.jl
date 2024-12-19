using Pkg
Pkg.add("StatsBase")
using LinearAlgebra
using DelimitedFiles
using Printf
using Dates
using StatsBase

function read_node_coord(num_vertices, file)
    coordenadas = []
    matriz_montagem = zeros(num_vertices, num_vertices)

    for linha in file
        linha = strip(linha)
        if linha == "EOF"
            break
        end

        valores_linha = split(linha)
        coor_x = parse(Float64, valores_linha[2])
        coor_y = parse(Float64, valores_linha[3])

        nova_coord = (coor_x, coor_y)

        for (i, coord) in enumerate(coordenadas)
            distancia = sqrt((nova_coord[1] - coord[1])^2 + (nova_coord[2] - coord[2])^2)
            matriz_montagem[length(coordenadas)+1, i] = distancia
            matriz_montagem[i, length(coordenadas)+1] = distancia
        end

        push!(coordenadas, nova_coord)
    end

    return matriz_montagem
end

function print_resultado(start, custo)
    tempo = Dates.now() - start
    total_segundos = Millisecond(tempo).value / 1000
    horas = div(total_segundos, 3600)
    minutos = div(total_segundos % 3600, 60)
    segundos = total_segundos % 60
    println("Custo: $(round(custo, digits=3)) | Tempo decorrido: $(horas)h $(minutos)m $(round(segundos, digits=3))s")
    println()
end

function vizinho_mais_proximo(num_vertices, matriz)
    start = Dates.now()
    caminho = [1]
    nao_visitados = collect(2:num_vertices)
    custo = 0.0
    inicio = 1
    index = inicio

    while length(caminho) < num_vertices
        menor_distancia = Inf
        indice = 0
        for idx in nao_visitados
            if matriz[index, idx] != 0.0 && matriz[index, idx] < menor_distancia
                menor_distancia = matriz[index, idx]
                indice = idx
            end
        end
        push!(caminho, indice)
        deleteat!(nao_visitados, findfirst(==(indice), nao_visitados))
        custo += menor_distancia
        index = indice
    end

    custo += matriz[index, inicio]
    push!(caminho, 1)

    #= println("vizinho mais proximo:")
    print_resultado(start, custo) =#

    return caminho, custo
end

function shift(matriz_distancias, caminho_inicial, custo_inicial, is_first_improvement)
    start = Dates.now()
    n = length(caminho_inicial)

    caminho_atual = copy(caminho_inicial)
    custo_atual = custo_inicial

    if is_first_improvement
        while true
            melhorou = false
    
            for i in 2:n-2
                for j in i+1:n-1
                    custo_removido = matriz_distancias[caminho_atual[i-1], caminho_atual[i]] + matriz_distancias[caminho_atual[i], caminho_atual[i+1]] + matriz_distancias[caminho_atual[j], caminho_atual[j+1]]
                    custo_adicionado = matriz_distancias[caminho_atual[i-1], caminho_atual[i+1]] + matriz_distancias[caminho_atual[j], caminho_atual[i]] + matriz_distancias[caminho_atual[i], caminho_atual[j+1]]
    
                    novo_custo = custo_atual - custo_removido + custo_adicionado
    
                    if novo_custo < custo_atual
                        custo_atual = novo_custo
                        vertice = caminho_atual[i]
                        deleteat!(caminho_atual, i)
                        insert!(caminho_atual, j, vertice)
                        melhorou = true
    
                        break
                    end
                end
                if melhorou
                    break
                end
            end
    
            if !melhorou
                break
            end
        end
    else
        while true
            melhorou = false
            melhor_custo = custo_atual
            melhor_i = 0
            melhor_j = 0

            for i in 2:n-2
                for j in i+1:n-1
                    custo_removido = matriz_distancias[caminho_atual[i-1], caminho_atual[i]] + matriz_distancias[caminho_atual[i], caminho_atual[i+1]] + matriz_distancias[caminho_atual[j], caminho_atual[j+1]]
                    custo_adicionado = matriz_distancias[caminho_atual[i-1], caminho_atual[i+1]] + matriz_distancias[caminho_atual[j], caminho_atual[i]] + matriz_distancias[caminho_atual[i], caminho_atual[j+1]]
    
                    novo_custo = custo_atual - custo_removido + custo_adicionado

                    if novo_custo < melhor_custo
                        melhor_custo = novo_custo
                        melhor_i = i
                        melhor_j = j
                        melhorou = true
                    end
                end
            end

            if melhorou && melhor_i != 0 && melhor_j != 0
                custo_atual = melhor_custo
                vertice = caminho_atual[melhor_i]
                deleteat!(caminho_atual, melhor_i)
                insert!(caminho_atual, melhor_j, vertice)
            else
                break
            end
        end
    end

    if is_first_improvement
        println("Shift (First Improvement):")
    else
        println("Shift (Best Improvement):")
    end
    print_resultado(start, custo_atual)
end

function swap(matriz_distancias, caminho_inicial, custo_inicial, is_first_improvement)
    start = Dates.now()
    n = length(caminho_inicial)

    caminho_atual = caminho_inicial
    custo_atual = custo_inicial

    if is_first_improvement
        while true
            melhorou = false

            for i in 2:n-2
                for j in i+2:n-1
                    custo_removido = matriz_distancias[caminho_atual[i], caminho_atual[i-1]] + matriz_distancias[caminho_atual[i], caminho_atual[i+1]] + matriz_distancias[caminho_atual[j], caminho_atual[j-1]] + matriz_distancias[caminho_atual[j], caminho_atual[j+1]]
                    custo_adicionado = matriz_distancias[caminho_atual[j], caminho_atual[i-1]] + matriz_distancias[caminho_atual[j], caminho_atual[i+1]] + matriz_distancias[caminho_atual[i], caminho_atual[j+1]] + matriz_distancias[caminho_atual[i], caminho_atual[j-1]]

                    novo_custo = custo_atual - custo_removido + custo_adicionado

                    if novo_custo < custo_atual
                        novo_caminho = copy(caminho_atual)
                        novo_caminho[i], novo_caminho[j] = novo_caminho[j], novo_caminho[i]

                        caminho_atual = novo_caminho
                        custo_atual = novo_custo
                        melhorou = true
                        break
                    end
                end
                if melhorou
                    break
                end
            end

            if !melhorou
                break
            end
        end
    else
        while true
            melhorou = false
            melhor_caminho = caminho_atual
            melhor_custo = custo_atual

            for i in 2:n-2
                for j in i+2:n-1
                    custo_removido = matriz_distancias[caminho_atual[i], caminho_atual[i-1]] + matriz_distancias[caminho_atual[i], caminho_atual[i+1]] + matriz_distancias[caminho_atual[j], caminho_atual[j-1]] + matriz_distancias[caminho_atual[j], caminho_atual[j+1]]
                    custo_adicionado = matriz_distancias[caminho_atual[j], caminho_atual[i-1]] + matriz_distancias[caminho_atual[j], caminho_atual[i+1]] + matriz_distancias[caminho_atual[i], caminho_atual[j+1]] + matriz_distancias[caminho_atual[i], caminho_atual[j-1]]

                    novo_custo = custo_atual - custo_removido + custo_adicionado

                    if novo_custo < melhor_custo
                        novo_caminho = copy(caminho_atual)
                        novo_caminho[i], novo_caminho[j] = novo_caminho[j], novo_caminho[i]

                        melhor_caminho = novo_caminho
                        melhor_custo = novo_custo
                        melhorou = true
                    end
                end
            end

            if melhorou
                caminho_atual = melhor_caminho
                custo_atual = melhor_custo
            else
                break
            end
        end
    end

    if is_first_improvement
        println("Swap (First Improvement):")
    else
        println("Swap (Best Improvement):")
    end

    print_resultado(start, custo_atual)
end

function dois_opt(matriz_distancias, caminho_inicial, custo_inicial, is_first_improvement)
    start = Dates.now()
    n = length(caminho_inicial)

    caminho_atual = caminho_inicial
    custo_atual = custo_inicial

    if is_first_improvement
        while true
            melhorou = false

            for i in 2:n-2
                for j in i+1:n-1
                    custo_removido = matriz_distancias[caminho_atual[i-1], caminho_atual[i]] + matriz_distancias[caminho_atual[j], caminho_atual[j+1]]
                    custo_adicionado = matriz_distancias[caminho_atual[i-1], caminho_atual[j]] + matriz_distancias[caminho_atual[i], caminho_atual[j+1]]

                    novo_custo = custo_atual - custo_removido + custo_adicionado

                    if novo_custo < custo_atual
                        caminho_atual = vcat(caminho_atual[1:i-1], reverse(caminho_atual[i:j]), caminho_atual[j+1:end])
                        custo_atual = novo_custo
                        melhorou = true
                        break
                    end
                end
                if melhorou
                    break
                end
            end

            if !melhorou
                break
            end
        end
    else
        while true
            melhorou = false
            melhor_caminho = caminho_atual
            melhor_custo = custo_atual

            for i in 2:n-2
                for j in i+1:n-1
                    custo_removido = matriz_distancias[caminho_atual[i-1], caminho_atual[i]] + matriz_distancias[caminho_atual[j], caminho_atual[j+1]]
                    custo_adicionado = matriz_distancias[caminho_atual[i-1], caminho_atual[j]] + matriz_distancias[caminho_atual[i], caminho_atual[j+1]]

                    novo_custo = custo_atual - custo_removido + custo_adicionado

                    if novo_custo < melhor_custo
                        melhor_caminho = vcat(caminho_atual[1:i-1], reverse(caminho_atual[i:j]), caminho_atual[j+1:end])
                        melhor_custo = novo_custo
                        melhorou = true
                    end
                end
            end

            if melhorou
                caminho_atual = melhor_caminho
                custo_atual = melhor_custo
            else
                break
            end
        end
    end

    if is_first_improvement
        println("2-OPT (First Improvement):")
    else
        println("2-OPT (Best Improvement):")
    end
    print_resultado(start, custo_atual)
end

function double_bridge(matriz_distancias, caminho_inicial, custo_inicial, is_first_improvement)
    n = length(caminho_inicial)
    start = Dates.now()

    function calcular_custo(caminho)
        custo = 0
        for i in 1:n
            origem = caminho[i]
            destino = caminho[mod1(i + 1, n)]
            custo += matriz_distancias[origem, destino]
        end
        return custo
    end

    function aplicar_double_bridge(caminho, a, b, c, tipo_troca)
        if tipo_troca == 1
            return vcat(
                caminho[1:a],
                caminho[b+1:c],
                caminho[b+1:c],
                caminho[b+1:c],
                caminho[a+1:b],
                caminho[c+1:end]
            )
        elseif tipo_troca == 2
            return vcat(
                caminho[1:a],
                caminho[c+1:end],
                caminho[b+1:c],
                caminho[a+1:b]
            )
        else
            tipo_troca == 3
            return vcat(
                caminho[1:a],
                caminho[a+1:b],
                caminho[c+1:end],
                caminho[b+1:c]
            )
        end
    end

    melhor_caminho = copy(caminho_inicial)
    melhor_custo = custo_inicial

    a, b, c = sort(sample(2:n-1, 3, replace=false))

    melhoria = false
    while true
        melhoria = false
        for i in 1:3
            novo_caminho = aplicar_double_bridge(caminho_inicial, a, b, c, i)
            novo_custo = calcular_custo(novo_caminho)

            if novo_custo < melhor_custo
                melhor_caminho = novo_caminho
                melhor_custo = novo_custo
                melhoria = true

                if is_first_improvement
                    break
                end
            end
        end
        if !melhoria
            break
        end
    end

    if is_first_improvement
        println("Double Bridge (First Improvement):")
    else
        println("Double Bridge (Best Improvement):")
    end
    print_resultado(start, melhor_custo)
end

caminho_pasta = "./heuristicas/"
arquivos = sort(filter(x -> isfile(joinpath(caminho_pasta, x)), readdir(caminho_pasta)))
filter!(x -> x != "heuristicas.jl", arquivos)
filter!(x -> x != "dependencias.jl", arquivos)

for arquivo in arquivos
    matriz_distancias = nothing
    num_vertices = 0

    open(joinpath(caminho_pasta, arquivo)) do file
        for linha in eachline(file)
            if startswith(linha, "DIMENSION")
                num_vertices = parse(Int, split(linha)[end])
            elseif strip(linha) == "NODE_COORD_SECTION"
                break
            end
        end

        matriz_distancias = read_node_coord(num_vertices, eachline(file))
    end

    println("Arquivo: $(arquivo) ----------------------------------")
    caminho_inicial, custo_inicial = vizinho_mais_proximo(num_vertices, matriz_distancias)
    shift(matriz_distancias, caminho_inicial, custo_inicial, true)
    shift(matriz_distancias, caminho_inicial, custo_inicial, false)
    swap(matriz_distancias, caminho_inicial, custo_inicial, true)
    swap(matriz_distancias, caminho_inicial, custo_inicial, false)
    dois_opt(matriz_distancias, caminho_inicial, custo_inicial, true)
    dois_opt(matriz_distancias, caminho_inicial, custo_inicial, false)
    double_bridge(matriz_distancias, caminho_inicial, custo_inicial, true)
    double_bridge(matriz_distancias, caminho_inicial, custo_inicial, false)
end