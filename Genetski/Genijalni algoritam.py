import random
from graph_viz import *
import pygame
import pathfinding

broj = 68
g = load_graph(broj)

populacija = []
for i in range(2*broj):
    l = [[j for j in range(1, broj)], None]
    random.shuffle(l[0])
    populacija.append(l)

print(populacija)
print("Stvorena populacija")

matrica_distanci = g.D

print("Pricanje sa kompjuterom")

recn = {}
for i in range(0, len(matrica_distanci)):
    for j in range(0, len(matrica_distanci)):
        recn[f"{i}-{j}"] = matrica_distanci[i][j]

print("Definisanje svrhe zivota")

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((800, 600))

zadnjeNajbolje = float("inf")
vremeOdZadnjegNajboljeg = 0

hit = pygame.mixer.Sound('TeenFalse.wav')

kraj = False

for i in range(1000000000000000000000000000000000000000):
    if kraj:
        break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            kraj = True
            break

    screen.fill((0, 0, 0))

    """CILJ"""
    for j in populacija:
        b = 0
        for k in range(len(j[0]) - 1):
            b += recn[f"{j[0][k]}-{j[0][k + 1]}"]
        b += recn[f"{0}-{j[0][0]}"]
        b += recn[f"{j[0][-1]}-{0}"]
        j[1] = b

    """PRIKAZ"""
    for j in range(len(populacija)):
        pygame.draw.rect(screen, (255, 0, 0), (j * 4, 0, 4, populacija[j][1] / 50))

    """SELEKCIJA"""
    novaPopulacija = []
    novoL = []
    while populacija:
        for m in range(13):
            if not populacija:
                continue
            novoL.append(populacija.pop(random.randint(0, len(populacija) - 1)))
        novoL = sorted(novoL, key=lambda x: x[1])
        for m in range(13):
            novaPopulacija.append([novoL[0][0][:], novoL[0][1]])
        novoL.clear()

    roditelji = [[r[0][:], r[1]] for r in novaPopulacija]

    """UKRSTANJE"""
    deca = []

    while roditelji:
        roditelj1 = roditelji.pop(random.randint(0, len(roditelji) - 1))

        if roditelji:
            roditelj2 = roditelji.pop(random.randint(0, len(roditelji) - 1))
            n = [[-1 for ni in range(len(roditelj1[0]))], None]
            cx = random.randint(0, len(roditelj1[0]) - 1)
            cy = random.randint(0, len(roditelj1[0]) - 1)
            if cx > cy:
                cx, cy = cy, cx

            for j in range(len(n[0])):
                if cx < j < cy:
                    n[0][j] = roditelj1[0][j]

            ostali = [k for k in roditelj2[0] if k not in n[0]]
            for k in range(len(n[0])):
                if n[0][k] == -1:
                    n[0][k] = ostali.pop(0)
        else:
            n = roditelj1

        deca.append(n)
        deca.append([n[0][:], None])

    populacija = deca.copy()
    deca = []

    """MUTACIJE"""
    if i < 9987:
        for j in populacija:
            if random.random() < 1/13:
                ox, oy = 0, 0
                while ox == oy:
                    ox = random.randint(0, len(j[0]) - 1)
                    oy = random.randint(0, len(j[0]) - 1)
                j[0][ox], j[0][oy] = j[0][oy], j[0][ox]

    """EVALUACIJA PROGRESA I ZVUK"""
    for j in populacija:
        b = 0
        for k in range(len(j[0]) - 1):
            b += recn[f"{j[0][k]}-{j[0][k + 1]}"]
        b += recn[f"{0}-{j[0][0]}"]
        b += recn[f"{j[0][-1]}-{0}"]
        j[1] = b

    sortiranaPopulacija = sorted(populacija.copy(), key=lambda x: x[1])

    if zadnjeNajbolje > sortiranaPopulacija[0][1]:
        vremeOdZadnjegNajboljeg = 0
        zadnjeNajbolje = sortiranaPopulacija[0][1]
        hit.stop()
        hit.play()
    else:
        vremeOdZadnjegNajboljeg += 1

    if vremeOdZadnjegNajboljeg > 10*broj:
        print("Zavrseno zbog stagnacije!")
        kraj = True

    pygame.draw.rect(screen, (255, 255, 0), (0, 0, 4000, zadnjeNajbolje / 50))
    pygame.display.flip()

print(populacija)

oli = [0]
for i in populacija[0][0]:
    oli.append(i)
print(oli)

run(g, oli)