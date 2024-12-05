import os

class ItemMochila:
    def __init__(self, numero_item, valor, peso):
        self.numero_item = numero_item
        self.valor = valor
        self.peso = peso
    
    def __str__(self):
        return f"Item: {self.peso} - Peso: {self.peso} - Valor: {self.valor}"

caminho_pasta = './'

arquivos = sorted([f for f in os.listdir(caminho_pasta) if os.path.isfile(os.path.join(caminho_pasta, f))])
arquivos.remove("mochila.py")

for arquivo in arquivos:
    linhas_arquivo = open(f"./{arquivo}", "r")

    primeira_linha = linhas_arquivo.readline().strip().split(" ")
    capacidade = int(primeira_linha[1])
    tamanho_total = int(primeira_linha[0])

    itens = [ItemMochila(0, 0, 0)] * tamanho_total

    for indice, linha in enumerate(linhas_arquivo):
        valores_linha = linha.strip().split(" ")
        if len(valores_linha) == 2:
            itens[indice] = ItemMochila(indice, int(valores_linha[0]), int(valores_linha[1]))

    linhas_arquivo.close()

    def print_resultado(valores):
        for item in valores:
            print(item)

        valor_total = sum(item.valor for item in valores)
        peso_total = sum(item.peso for item in valores)
        print(f"\nValor total da mochila: {valor_total}")
        print(f"Capacidade mochila: {capacidade}")
        print(f"Capacidade utilizada: {peso_total}")
        print(f"Capacidade restante: {capacidade - peso_total}")

    selecionados = []
    maximo_mochila = capacidade
    for i in range(tamanho_total):
        for j in range(i + 1, tamanho_total):
            if (itens[i].valor / itens[i].peso) < (itens[j].valor / itens[j].peso):
                itens[i], itens[j] = itens[j], itens[i]

    for item in itens:
        if item.peso <= maximo_mochila:
            maximo_mochila -= item.peso
            selecionados.append(item)

    print("_____________________________________________________________")
    print(f"Problema {arquivo}\n")
    print_resultado(selecionados)