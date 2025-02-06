using Random, LinearAlgebra, Printf

function print_resultado(start, caminho, custo)
    println(@sprintf("Custo: %.3f", custo))
    tempo = time() - start
    horas = Int(floor(tempo / 3600))
    minutos = Int(floor((tempo % 3600) / 60))
    segundos = tempo % 60
    println(@sprintf("Tempo decorrido: %dh %dm %.3fs", horas, minutos, segundos))
    println()
end

function ler_coordenadas(num_vertices, arquivo)
    coordenadas = []
    matriz_montagem = zeros(num_vertices, num_vertices)
    
    for linha in eachline(arquivo)
        if strip(linha) == "EOF"
            break
        end
        
        valores_linha = split(linha)
        coor_x = parse(Float64, valores_linha[2])
        coor_y = parse(Float64, valores_linha[3])
        
        nova_coord = (coor_x, coor_y)
        
        for (i, coord) in enumerate(coordenadas)
            distancia = sqrt((nova_coord[1] - coord[1])^2 + (nova_coord[2] - coord[2])^2)
            matriz_montagem[i, length(coordenadas)+1] = distancia
            matriz_montagem[length(coordenadas)+1, i] = distancia
        end
        
        push!(coordenadas, nova_coord)
    end
    return matriz_montagem
end

function grasp(matriz, alfa)
    start = time()
    nos = collect(1:size(matriz, 1))
    inicial = 1
    deleteat!(nos, inicial)
    atual = inicial
    custo = 0
    caminho = [atual]
    
    while !isempty(nos)
        vizinhos = [(j, matriz[atual, j]) for j in nos if matriz[atual, j] != 0]
        sort!(vizinhos, by=x->x[2])
        
        primeiro_vizinho = vizinhos[1][2]
        ultimo_vizinho = vizinhos[end][2]
        lrc = primeiro_vizinho + alfa * (ultimo_vizinho - primeiro_vizinho)
        
        vizinhos_lrc = [tupla[1] for tupla in vizinhos if tupla[2] <= lrc]
        proximo_no = rand(vizinhos_lrc)
        
        custo += matriz[atual, proximo_no]
        push!(caminho, proximo_no)
        deleteat!(nos, findfirst(==(proximo_no), nos))
        atual = proximo_no
    end
    
    custo += matriz[atual, inicial]
    push!(caminho, inicial)
    return caminho, custo
end

function dois_opt(custo, caminho, matriz)
    start = time()
    melhor_caminho = copy(caminho)
    melhor_custo = custo
    melhorou = true
    
    while melhorou
        melhorou = false
        for i in 2:length(melhor_caminho)-2
            for j in i+1:length(melhor_caminho)-1
                custo_removido = matriz[melhor_caminho[i-1], melhor_caminho[i]] + matriz[melhor_caminho[j], melhor_caminho[j+1]]
                custo_adicionado = matriz[melhor_caminho[i-1], melhor_caminho[j]] + matriz[melhor_caminho[i], melhor_caminho[j+1]]
                novo_custo = melhor_custo - custo_removido + custo_adicionado
                
                if novo_custo < melhor_custo
                    melhor_caminho = vcat(melhor_caminho[1:i-1], reverse(melhor_caminho[i:j]), melhor_caminho[j+1:end])
                    melhor_custo = novo_custo
                    melhorou = true
                    break
                end
            end
            if melhorou
                break
            end
        end
    end
    return melhor_caminho, melhor_custo
end

function multistart_aleatorio(num_vertices, matriz)
    start = time()
    div = num_vertices ÷ 5
    num_solucoes = min(div, 20)
    melhor_caminho, melhor_custo = nothing, Inf
    
    for _ in 1:num_solucoes
        caminho_aleatorio = [1; shuffle(2:num_vertices); 1]
        custo_aleatorio = sum(matriz[caminho_aleatorio[i], caminho_aleatorio[i+1]] for i in 1:length(caminho_aleatorio)-1)
        caminho_otimizado, custo_otimizado = dois_opt(custo_aleatorio, caminho_aleatorio, matriz)
        
        if custo_otimizado < melhor_custo
            melhor_caminho, melhor_custo = caminho_otimizado, custo_otimizado
        end
    end
    
    println("Melhor solução encontrada com MultiStart Aleatório:")
    print_resultado(start, melhor_caminho, melhor_custo)
    return melhor_caminho, melhor_custo
end

function multistart_grasp(matriz)
    start = time()
    melhor_caminho, melhor_custo = nothing, Inf
    
    for i in 0:10
        alpha = i / 10
        caminho_grasp, custo_grasp = grasp(matriz, alpha)
        caminho_otimizado, custo_otimizado = dois_opt(custo_grasp, caminho_grasp, matriz)
        
        if custo_otimizado < melhor_custo
            melhor_caminho, melhor_custo = caminho_otimizado, custo_otimizado
        end
    end
    
    println("Melhor solução encontrada com MultiStart Grasp:")
    print_resultado(start, melhor_caminho, melhor_custo)
    return melhor_caminho, melhor_custo
end