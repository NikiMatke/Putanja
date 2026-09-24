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

put.append(0)

print("Svima njima ce crći krava:", put)
run(g, put)