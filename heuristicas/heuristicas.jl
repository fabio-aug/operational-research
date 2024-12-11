using LinearAlgebra
using DelimitedFiles
using Printf
using Dates

caminho_pasta = "./"
arquivos = sort(filter(x -> isfile(joinpath(caminho_pasta, x)), readdir(caminho_pasta)))
filter!(x -> x != "heuristicas.jl", arquivos)

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
    println("Custo: $(round(custo, digits=3))")
    tempo = Dates.now() - start
    total_segundos = Millisecond(tempo).value / 1000
    horas = div(total_segundos, 3600)
    minutos = div(total_segundos % 3600, 60)
    segundos = total_segundos % 60
    println("Tempo decorrido: $(horas)h $(minutos)m $(round(segundos, digits=3))s")
    println()
end

function vizinho_mais_proximo(num_vertices, matriz)
    start = Dates.now()
    caminho = [1]
    nao_visitados = collect(2:num_vertices)
    custo = 0.0

    minutos_break = 0
    inicio = 1
    index = inicio
    while length(caminho) < num_vertices && minutos_break < 30
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
        tempo = Dates.now() - start
        minutos_break = floor(Int, (tempo % Dates.Hour(1)).value / Minute(1).value)
    end

    custo += matriz[index, inicio]
    push!(caminho, 1)

    println("Vizinho mais próximo:")
    print_resultado(start, custo)

    return caminho, custo
end

function calcula_custo(matriz_distancias, caminho)
    custo = 0
    for i in 1:length(caminho)-1
        custo += matriz_distancias[caminho[i], caminho[i+1]]
    end
    custo += matriz_distancias[caminho[end], caminho[1]] # Retorna ao ponto inicial
    return custo
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
                    novo_caminho = vcat(caminho_atual[1:i-1], reverse(caminho_atual[i:j]), caminho_atual[j+1:end])
    
                    custo_removido = matriz_distancias[caminho_atual[i-1], caminho_atual[i]] + matriz_distancias[caminho_atual[j], caminho_atual[j+1]]
                    custo_adicionado = matriz_distancias[caminho_atual[i-1], caminho_atual[j]] + matriz_distancias[caminho_atual[i], caminho_atual[j+1]]
    
                    novo_custo = custo_atual - custo_removido + custo_adicionado
    
                    if novo_custo < custo_atual
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
                for j in i+1:n-1
                    novo_caminho = vcat(caminho_atual[1:i-1], reverse(caminho_atual[i:j]), caminho_atual[j+1:end])
    
                    custo_removido = matriz_distancias[caminho_atual[i-1], caminho_atual[i]] + matriz_distancias[caminho_atual[j], caminho_atual[j+1]]
                    custo_adicionado = matriz_distancias[caminho_atual[i-1], caminho_atual[j]] + matriz_distancias[caminho_atual[i], caminho_atual[j+1]]
    
                    novo_custo = custo_atual - custo_removido + custo_adicionado
    
                    if novo_custo < melhor_custo
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
        println("2-opt first_improvement: ")
    else
        println("2-opt best_improvement: ")
    end
    print_resultado(start, custo_atual)
end

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
    dois_opt(matriz_distancias, caminho_inicial, custo_inicial, true)
    dois_opt(matriz_distancias, caminho_inicial, custo_inicial, false)
end
