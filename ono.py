from graph_viz import *

g = load_graph(5)


#mozda bude kasnije trebalo
matrica_distanci = g.D

alphabet = "ΩABCDEFGHIJKLMNOPQRSTUVWXYZ"

optimal = float("inf")

def konvertuj(n):
    text = ""
    while n > 0:
        text += alphabet[n%27]
        n //= 27
    text = text[::-1]
    return text

n = 0
lista = []

for i in range(g.n):
    lista.append(konvertuj(i))

recn = {}
for i in range(0,len(matrica_distanci)):
    for j in range(0,len(matrica_distanci)):
        recn[f"{konvertuj(i)}{konvertuj(j)}"] = matrica_distanci[i][j]

print("Gledanje...")

print(matrica_distanci)
for i in range(0,len(lista)):
    for j in range(0,len(lista) - 1):
        for k in range(0,len(lista) - 2):
            for l in range(0,len(lista) - 3):
                data = lista.copy()
                sadasnji = 0
                text = ""
                Index = 0
                pt = data[0]
                t = data[(i + Index)%len(data)]
                sadasnji += recn[f"{pt}{t}"]
                text += data[(i + Index)%len(data)]
                del data[(i + Index)%len(data)]
                Index += i
                text += data[(j + Index)%len(data)]
                pt = t
                t = data[(i + Index)%len(data)]
                sadasnji += recn[f"{pt}{t}"]
                del data[(j + Index)%len(data)]
                Index += j
                text += data[(k + Index)%len(data)]
                pt = t
                t = data[(j + Index)%len(data)]
                sadasnji += recn[f"{pt}{t}"]
                del data[(k + Index)%len(data)]
                Index += k
                text += data[(l + Index)%len(data)]
                pt = t
                t = data[(k + Index)%len(data)]
                sadasnji += recn[f"{pt}{t}"]
                del data[(l + Index)%len(data)]
                Index += l
                text += data[0]
                pt = t
                t = data[(l + Index)%len(data)]
                sadasnji += recn[f"{pt}{t}"]
                del data[0]
                if sadasnji < optimal:
                    print(f"Novi najbolji: {sadasnji} za {text}")
                    optimal = sadasnji
                    ot = text
                Index = 0
                n += 1
                data = lista

print(ot)
