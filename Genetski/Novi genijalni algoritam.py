import random
from graph_viz import *
import pygame

from graph_viz import *
import random

broj = 13
g = load_graph(broj)
matricaDistanci = g.D

trenutniGrad = 0
preostaliGradovi = [i for i in range(1, broj)]
put = []

while preostaliGradovi:
    najmanjaDistanca = float("inf")
    sledeciGrad = None

    for grad in preostaliGradovi:
        distanca = matricaDistanci[trenutniGrad][grad]
        if distanca < najmanjaDistanca:
            najmanjaDistanca = distanca
            sledeciGrad = grad

    put.append(sledeciGrad)
    preostaliGradovi.remove(sledeciGrad)
    trenutniGrad = sledeciGrad


def optMutacija(p, k=2):
    n = len(p)
    if n < 4:
        return p[:]
    noviPut = p[:]

    if k == 2 or random.random() < 0.7:
        i, j = sorted(random.sample(range(n), 2))
        noviPut[i:j] = reversed(noviPut[i:j])
    else:
        i, j, m = sorted(random.sample(range(n), 3))
        seg1 = noviPut[:i]
        seg2 = noviPut[i:j]
        seg3 = noviPut[j:m]
        seg4 = noviPut[m:]
        noviPut = seg1 + seg3 + seg2 + seg4

    return noviPut


populacija = []
lNn = [put[:], None]
populacija.append(lNn)

for i in range(max(500, 2 * broj) - 1):
    l = [put[:], None]
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

try:
    hit = pygame.mixer.Sound('TeenFalse.wav')
except:
    hit = None

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

    """ELITIZAM"""
    elitni = min(populacija, key=lambda x: x[1])

    elitni = [
        elitni[0][:],
        elitni[1]
    ]

    """SELEKCIJA"""
    """SELEKCIJA"""
    novaPopulacija = []

    while len(populacija) >= 5:

        turnir = []

        for _ in range(5):
            turnir.append(
                populacija.pop(
                    random.randint(0, len(populacija) - 1)
                )
            )

        turnir.sort(key=lambda x: x[1])

        for _ in range(3):
            novaPopulacija.append([
                turnir[0][0][:],
                turnir[0][1]
            ])

        for _ in range(2):
            novaPopulacija.append([
                turnir[1][0][:],
                turnir[1][1]
            ])

    populacija = novaPopulacija

    roditelji = [[r[0][:], r[1]] for r in novaPopulacija]

    """UKRSTANJE"""
    deca = []

    while roditelji:
        roditelj1 = roditelji.pop(random.randint(0, len(roditelji) - 1))

        if roditelji:
            roditelj2 = roditelji.pop(random.randint(0, len(roditelji) - 1))

            cx = random.randint(0, len(roditelj1[0]) - 1)
            cy = random.randint(0, len(roditelj1[0]) - 1)
            if cx > cy:
                cx, cy = cy, cx

            nPut = [-1] * len(roditelj1[0])
            nPut[cx:cy] = roditelj1[0][cx:cy]

            ostali = [k for k in roditelj2[0] if k not in nPut]
            idx = 0
            for k in range(len(nPut)):
                if nPut[k] == -1:
                    nPut[k] = ostali[idx]
                    idx += 1

            n = [nPut, None]
        else:
            n = roditelj1

        deca.append(n)
        deca.append([n[0][:], None])

    populacija = deca.copy()
    deca = []

    """MUTACIJE"""
    kVal = 2 if vremeOdZadnjegNajboljeg < 100 else 3

    if i < 9987:
        for j in populacija:
            if random.random() < 0.35:
                j[0] = optMutacija(j[0], k=kVal)

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
        if hit:
            hit.stop()
            hit.play()
    else:
        vremeOdZadnjegNajboljeg += 1

    if vremeOdZadnjegNajboljeg > int(50 * broj):
        print("Zavrseno zbog stagnacije!")
        kraj = True
    zelena = min(255, max(0, int(255 * (vremeOdZadnjegNajboljeg / (50*broj)))))
    pygame.draw.rect(screen, (255, zelena, 0), (0, 0, 4000, zadnjeNajbolje / 50))
    pygame.display.flip()

    """ZAMENA ELITIZMA"""
    najgori = max(range(len(populacija)),
                  key=lambda x: populacija[x][1])

    populacija[najgori] = [
        elitni[0][:],
        elitni[1]
    ]

print(populacija)

najbolje = min(populacija, key=lambda x: x[1])

oli = [0] + najbolje[0]
print(oli)

run(g, oli)