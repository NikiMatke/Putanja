import difflib
import json
import math
import time
import urllib.request
from dataclasses import dataclass

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon

USE_DRIVING_DISTANCES = True

OSRM_URL = "https://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"

INK, MUTED, EDGE, LAND, BORDER, TOUR = "#12233F", "#5A6779", "#8E9AAB", "#EEF1EA", "#9AA5B1", "#D1495B"
BOJE_OPISA = {"ulaz": "#2A9D8F", "stepenice": "#E9A23B"}

OBOD_REDOM = [f"T{i}" for i in range(1, 12)]

CITIES = [
    ("S", 0.00, 0.00), ("T1", -7.13, 12.35), ("T2", -7.84, 10.40),
    ("T3", -9.50, 3.27), ("T4", -7.97, 0.84), ("T5", -7.93, -1.40),
    ("T6", -8.43, -7.08), ("T7", -10.30, -12.27), ("T8", -8.53, -14.77),
    ("T9", 12.00, 0.00), ("T10", 6.98, 4.03), ("T11", 6.17, 5.18),
]
MAX_CITIES = len(CITIES)


@dataclass
class Graph:
    n: int        # broj čvorova
    names: list   # imena čvorova
    coords: list  # koordinate
    D: list       # matrica rastojanja
    kind: str     # tip razdaljine


def load_graph(n=8):
    if not 2 <= n <= MAX_CITIES:
        raise ValueError(f"Choose between 2 and {MAX_CITIES} cities (you asked for {n}).")
    cities = CITIES[:n]
    D, kind = _get_distances(cities)
    return Graph(n, [c[0] for c in cities], [(c[1], c[2]) for c in cities], D, kind)


def _straight_line_km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def _straight_line_matrix(cities):
    n = len(cities)
    return [[round(_straight_line_km(cities[i][1:], cities[j][1:]), 1) for j in range(n)] for i in range(n)]


def _driving_matrix(cities):
    coords = ";".join(f"{lon:.6f},{lat:.6f}" for _, lat, lon in cities)
    req = urllib.request.Request(OSRM_URL.format(coords=coords), headers={"User-Agent": "tsp-serbia-teaching-demo"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.load(r)
    if data.get("code") != "Ok":
        raise RuntimeError(f"OSRM answered: {data.get('code')}")
    raw, n = data["distances"], len(cities)
    M = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            a, b = raw[i][j], raw[j][i]
            if a is None or b is None:
                raise RuntimeError("OSRM could not route between some cities")
            M[i][j] = round((a + b) / 2000, 1)
    return M


def _get_distances(cities):
    if USE_DRIVING_DISTANCES:
        try:
            print("Getting driving distances...")
            return _driving_matrix(cities), "driving"
        except Exception as e:
            print(f"Could not get driving distances ({e}). Using straight-line distances instead.")
    return _straight_line_matrix(cities), "straight-line"


def check_tour(g, tour):
    if not isinstance(tour, (list, tuple)):
        raise TypeError("A tour must be a list of city numbers, like [0, 3, 1, 2].")
    if len(tour) != g.n:
        raise ValueError(f"Your tour has {len(tour)} cities, but the map has {g.n}.")
    seen = set()
    for i in tour:
        if i not in range(g.n):
            raise ValueError(f"{i!r} is not a valid city number (use 0 to {g.n - 1}).")
        if i in seen:
            raise ValueError(f"{g.names[i]} appears twice in your tour.")
        seen.add(i)


def tour_length(g, tour):
    check_tour(g, tour)
    return sum(g.D[tour[k]][tour[(k + 1) % g.n]] for k in range(g.n))


def print_distances(g):
    w = max(len(s) for s in g.names)
    print(" " * (w + 1) + " ".join(f"{s[:5]:>5}" for s in g.names))
    for i, s in enumerate(g.names):
        print(f"{s:<{w}} " + " ".join(f"{g.D[i][j]:5.0f}" for j in range(g.n)))


def _as_indices(g, tour):
    if not isinstance(tour, (list, tuple)):
        return tour
    out = []
    for c in tour:
        if isinstance(c, str):
            if c not in g.names:
                close = difflib.get_close_matches(c, g.names, n=1)
                hint = f" Did you mean {close[0]}?" if close else ""
                raise ValueError(f"'{c}' is not one of the {g.n} cities on the map.{hint}")
            out.append(g.names.index(c))
        else:
            out.append(c)
    return out


def run(g, algorithm, plot=True):
    print(f"\n{g.n} cities, {g.kind} distances")
    if g.n <= 20:
        print("  ".join(f"{i}={nm}" for i, nm in enumerate(g.names)))

    seconds = None
    if callable(algorithm):
        t0 = time.perf_counter()
        tour = algorithm(g)
        seconds = time.perf_counter() - t0
        method = algorithm.__name__
    else:
        tour, method = algorithm, "tour typed by hand"
    tour = _as_indices(g, tour)
    length = tour_length(g, tour)

    print("\n=== Result ===")
    print(f"Method:          {method}")
    print(f"Tour:            {' -> '.join(g.names[i] for i in tour)} -> {g.names[tour[0]]}")
    print(f"Length:          {length:,.0f} km")
    if seconds is not None:
        print(f"Time:            {'under 0.001' if seconds < 0.001 else f'{seconds:.3f}'} s")
    print()
    if plot:
        show_tour(g, tour)


# --- NOVE POMOĆNE I ISCRTAVAČKE FUNKCIJE ZASNOVANE NA PEĆINI ---

def _base_pecina_map(g):
    fig, ax = plt.subplots(figsize=(9, 10))

    # Crtanje unutrašnjosti pećine na osnovu obodnih tačaka koje postoje u grafu
    obod_tacke = [g.coords[g.names.index(nm)] for nm in OBOD_REDOM if nm in g.names]
    if len(obod_tacke) > 2:
        ax.add_patch(Polygon([(p[1], p[0]) for p in obod_tacke], closed=True,
                             facecolor=LAND, edgecolor="none", zorder=0))

    xs = [p[1] for p in g.coords]
    ys = [p[0] for p in g.coords]

    ax.set_xlim(min(xs) - 3, max(xs) + 3)
    ax.set_ylim(min(ys) - 3, max(ys) + 3)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    # Oznaka za sever
    ax.annotate("sever", xy=(0.96, 0.95), xytext=(0.96, 0.88), xycoords="axes fraction",
                ha="center", va="center", fontsize=11, fontweight="bold", color=MUTED,
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.5))

    return fig, ax


def _oznaka_ivice(ax, g, i, j, fs, t=0.5):
    (lat_i, lon_i), (lat_j, lon_j) = g.coords[i], g.coords[j]
    x, y = lon_i + t * (lon_j - lon_i), lat_i + t * (lat_j - lat_i)
    ugao = math.degrees(math.atan2(lat_j - lat_i, lon_j - lon_i))
    if ugao > 90:
        ugao -= 180
    if ugao <= -90:
        ugao += 180
    ax.text(x, y, f"{g.D[i][j]:.1f}", fontsize=fs, color=MUTED, ha="center", va="center",
            rotation=ugao, rotation_mode="anchor", zorder=4, linespacing=0.95,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=.9))


def _draw_cities(ax, g, start=None):
    xs = [c[1] for c in g.coords]
    ys = [c[0] for c in g.coords]
    ax.scatter(xs, ys, s=70, color=INK, edgecolor="white", linewidth=1.5, zorder=5)

    if start is not None:
        ax.scatter([xs[start]], [ys[start]], s=150, color=TOUR, edgecolor="white", linewidth=1.5, zorder=6)

    halo = [pe.withStroke(linewidth=2.2, foreground="white")]
    for i, nm in enumerate(g.names):
        ax.scatter([xs[i]], [ys[i]], color=TOUR if nm == "S" else INK, zorder=6 if nm == "S" else 5)
        ax.annotate(nm, (xs[i], ys[i]), xytext=(7, 6), textcoords="offset points",
                    fontsize=10, fontweight="bold", color=INK, path_effects=halo, zorder=7)


def show_graph(g, merenja=True, oznake=True):
    """Prikazuje mrežu pećine sa mogućnošću uključivanja/isključivanja merenja i oznaka."""
    fig, ax = _base_pecina_map(g)
    fs = max(4.5, 9.5 - 0.35 * g.n)

    n_ivica = 0
    for i in range(g.n):
        for j in range(i + 1, g.n):
            je_merenje = (g.names[i] == "S" or g.names[j] == "S")
            if je_merenje and not merenja:
                continue

            boja, lw, alpha, z = (EDGE, 0.9, 0.6, 2) if je_merenje else (BORDER, 2.6, 1.0, 3)
            ax.plot([g.coords[i][1], g.coords[j][1]], [g.coords[i][0], g.coords[j][0]],
                    color=boja, lw=lw, alpha=alpha, solid_capstyle="round", zorder=z)
            n_ivica += 1

            if oznake:
                t = 0.62 if je_merenje else 0.5
                _oznaka_ivice(ax, g, i, j, fs, t)

    _draw_cities(ax, g)
    ax.set_title(f"Pećina: {g.n} čvorova, {n_ivica} grana", loc="left",
                 fontsize=16, fontweight="bold", color=INK)
    ax.set_xlabel("Broj na svakoj grani: stvarna distanca u metrima", loc="left", color=MUTED)
    plt.show()


def show_tour(g, tour, title=None):
    """Prikazuje izračunatu TSP turu u pećini sa usmerenim strelicama."""
    length = tour_length(g, tour)
    fig, ax = _base_pecina_map(g)
    fs = max(4.5, 9.5 - 0.35 * g.n)

    for k in range(g.n):
        i, j = tour[k], tour[(k + 1) % g.n]
        ax.annotate("", xy=(g.coords[j][1], g.coords[j][0]), xytext=(g.coords[i][1], g.coords[i][0]),
                    arrowprops=dict(arrowstyle="-|>", color=TOUR, lw=2, shrinkA=5, shrinkB=5, mutation_scale=14),
                    zorder=3)
        if g.n <= 15:
            _oznaka_ivice(ax, g, i, j, fs)

    _draw_cities(ax, g, start=tour[0])
    ax.set_title(title or f"Tura kroz pećinu ({g.n} stanica): {length:,.1f} m", loc="left",
                 fontsize=16, fontweight="bold", color=INK)
    plt.show()