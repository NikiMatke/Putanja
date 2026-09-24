import difflib
import json
import math
import time
import urllib.request
from dataclasses import dataclass

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.collections import LineCollection

USE_DRIVING_DISTANCES = True

OSRM_URL = "https://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"

INK, MUTED, EDGE, LAND, BORDER, TOUR = "#12233F", "#5A6779", "#8E9AAB", "#EEF1EA", "#9AA5B1", "#D1495B"

CITIES = [
    ("Beograd", 44.8125, 20.4612), ("Novi Sad", 45.2671, 19.8335), ("Niš", 43.3209, 21.8954),
    ("Priština", 42.6629, 21.1655), ("Kragujevac", 44.0128, 20.9114), ("Prizren", 42.2139, 20.7397),
    ("Subotica", 46.1000, 19.6667), ("Pančevo", 44.8708, 20.6403), ("Zrenjanin", 45.3836, 20.3819),
    ("Čačak", 43.8914, 20.3497), ("Novi Pazar", 43.1367, 20.5122), ("Kraljevo", 43.7258, 20.6897),
    ("Smederevo", 44.6628, 20.9300), ("Peć", 42.6593, 20.2883), ("Leskovac", 42.9981, 21.9461),
    ("Kruševac", 43.5800, 21.3339), ("Valjevo", 44.2751, 19.8903), ("Vranje", 42.5514, 21.9003),
    ("Šabac", 44.7550, 19.6922), ("Užice", 43.8556, 19.8425), ("Kosovska Mitrovica", 42.8914, 20.8660),
    ("Gnjilane", 42.4635, 21.4694), ("Sombor", 45.7733, 19.1122), ("Požarevac", 44.6206, 21.1878),
    ("Pirot", 43.1531, 22.5861), ("Zaječar", 43.9036, 22.2644), ("Kikinda", 45.8297, 20.4653),
    ("Sremska Mitrovica", 44.9764, 19.6122), ("Jagodina", 43.9772, 21.2611), ("Uroševac", 42.3702, 21.1483),
    ("Vršac", 45.1167, 21.3000), ("Bor", 44.0749, 22.0959), ("Đakovica", 42.3803, 20.4308),
    ("Prokuplje", 43.2342, 21.5881), ("Loznica", 44.5333, 19.2258), ("Ruma", 45.0081, 19.8222),
    ("Inđija", 45.0483, 20.0817), ("Aranđelovac", 44.3061, 20.5600), ("Negotin", 44.2264, 22.5308),
    ("Prijepolje", 43.3906, 19.6489), ("Bečej", 45.6178, 20.0350), ("Senta", 45.9275, 20.0778),
    ("Bajina Bašta", 43.9722, 19.5686), ("Kladovo", 44.6058, 22.6089), ("Sjenica", 43.2708, 20.0003),
    ("Preševo", 42.3053, 21.6494), ("Apatin", 45.6711, 18.9814),
    ("Ćuprija", 43.9269, 21.3703), ("Paraćin", 43.8608, 21.4078), ("Smederevska Palanka", 44.3667, 20.9500),
    ("Obrenovac", 44.6536, 20.2003), ("Lazarevac", 44.3833, 20.2583), ("Vrbas", 45.5711, 19.6417),
    ("Bačka Palanka", 45.2506, 19.3953), ("Bačka Topola", 45.8144, 19.6336), ("Aleksinac", 43.5417, 21.7167),
    ("Trstenik", 43.6167, 20.9997), ("Ivanjica", 43.5808, 20.2306), ("Priboj", 43.5836, 19.5256),
    ("Kuršumlija", 43.1453, 21.2708), ("Bujanovac", 42.4653, 21.7683), ("Vlasotince", 42.9686, 22.1272),
    ("Knjaževac", 43.5667, 22.2578), ("Majdanpek", 44.4231, 21.9394), ("Petrovac na Mlavi", 44.3758, 21.4189),
    ("Podujevo", 42.9106, 21.1933), ("Vučitrn", 42.8231, 20.9975), ("Leposavić", 43.1017, 20.8028),
]
MAX_CITIES = len(CITIES)

SERBIA_OUTLINE = [
    (20.874313, 45.416375), (21.483526, 45.18117), (21.562023, 44.768947), (22.145088, 44.478422),
    (22.459022, 44.702517), (22.705726, 44.578003), (22.474008, 44.409228), (22.65715, 44.234923),
    (22.410446, 44.008063), (22.500157, 43.642814), (22.986019, 43.211161), (22.604801, 42.898519),
    (22.436595, 42.580321), (22.545012, 42.461362), (22.380526, 42.32026), (21.91708, 42.30364),
    (21.576636, 42.245224), (21.54332, 42.32025), (21.66292, 42.43922), (21.77505, 42.6827),
    (21.63302, 42.67717), (21.43866, 42.86255), (21.27421, 42.90959), (21.143395, 43.068685),
    (20.95651, 43.13094), (20.81448, 43.27205), (20.63508, 43.21671), (20.49679, 42.88469),
    (20.25758, 42.81275), (20.3398, 42.89852), (19.95857, 43.10604), (19.63, 43.21378),
    (19.48389, 43.35229), (19.21852, 43.52384), (19.454, 43.5681), (19.59976, 44.03847),
    (19.11761, 44.42307), (19.36803, 44.863), (19.00548, 44.86023), (19.390476, 45.236516),
    (19.072769, 45.521511), (18.82982, 45.90888), (19.596045, 46.17173), (20.220192, 46.127469),
    (20.762175, 45.734573),
]
KOSOVO_OUTLINE = [
    (20.76216, 42.05186), (20.71731, 41.84711), (20.59023, 41.85541), (20.52295, 42.21787),
    (20.28374, 42.32025), (20.0707, 42.58863), (20.25758, 42.81275), (20.49679, 42.88469),
    (20.63508, 43.21671), (20.81448, 43.27205), (20.95651, 43.13094), (21.143395, 43.068685),
    (21.27421, 42.90959), (21.43866, 42.86255), (21.63302, 42.67717), (21.77505, 42.6827),
    (21.66292, 42.43922), (21.54332, 42.32025), (21.576636, 42.245224), (21.3527, 42.2068),
]
OUTLINE = [SERBIA_OUTLINE, KOSOVO_OUTLINE]


@dataclass
class Graph:
    n: int      #broj cvorova
    names: list #imena čvorova
    coords: list #geografske koordinate (služi samo za crtanje)
    D: list     #matrica grafa
    kind: str   #vezano za to kako su podaci preuzeti (da li je offline ili online)


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


def _outer_edges(polygons):
    count = {}
    for poly in polygons:
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if a != b:
                key = frozenset((a, b))
                count[key] = count.get(key, 0) + 1
    return [tuple(key) for key, c in count.items() if c == 1]


def _base_map(g):
    fig, ax = plt.subplots(figsize=(10, 11))
    for poly in OUTLINE:
        xs, ys = zip(*poly)
        ax.fill(xs, ys, facecolor=LAND, edgecolor=LAND, lw=1.5, zorder=0)
    ax.add_collection(LineCollection(_outer_edges(OUTLINE), colors=BORDER, linewidths=1.4, capstyle="round", zorder=1))
    allx = [p[0] for poly in OUTLINE for p in poly]
    ally = [p[1] for poly in OUTLINE for p in poly]
    ax.set_xlim(min(allx) - .15, max(allx) + .15)
    ax.set_ylim(min(ally) - .1, max(ally) + .1)
    cos0 = math.cos(math.radians(sum(ally) / len(ally)))
    ax.set_aspect(1 / cos0)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    return fig, ax, cos0


def _label_edge(ax, g, i, j, cos0, fs, t=0.5):
    (lat_i, lon_i), (lat_j, lon_j) = g.coords[i], g.coords[j]
    x, y = lon_i + t * (lon_j - lon_i), lat_i + t * (lat_j - lat_i)
    ang = math.degrees(math.atan2(lat_j - lat_i, (lon_j - lon_i) * cos0))
    if ang > 90: ang -= 180
    if ang <= -90: ang += 180
    ax.text(x, y, f"{g.D[i][j]:.0f}", fontsize=fs, color=MUTED, ha="center", va="center",
            rotation=ang, rotation_mode="anchor", zorder=4,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=.9))


def _draw_cities(ax, g, start=None):
    lat = [c[0] for c in g.coords]; lon = [c[1] for c in g.coords]
    ax.scatter(lon, lat, s=70 if g.n <= 30 else 40, color=INK, edgecolor="white", linewidth=1.5, zorder=5)
    if start is not None:
        ax.scatter([lon[start]], [lat[start]], s=150, color=TOUR, edgecolor="white", linewidth=1.5, zorder=6)
    fs = 10 if g.n <= 20 else 8 if g.n <= 40 else 6.5
    halo = [pe.withStroke(linewidth=2.2, foreground="white")]
    for i, nm in enumerate(g.names):
        ax.annotate(nm, (lon[i], lat[i]), xytext=(7, 6), textcoords="offset points",
                    fontsize=fs, fontweight="bold", color=INK, path_effects=halo, zorder=7)


def _distance_note(g):
    return "driving distance, km" if g.kind == "driving" else "straight-line distance, km (no route data available)"


def show_graph(g, edges=None, labels=None):
    n = g.n
    edges = n <= 30 if edges is None else edges
    labels = n <= 15 if labels is None else labels
    fig, ax, cos0 = _base_map(g)
    fs = max(4.5, 9.5 - 0.35 * n)
    if edges:
        for i in range(n):
            for j in range(i + 1, n):
                ax.plot([g.coords[i][1], g.coords[j][1]], [g.coords[i][0], g.coords[j][0]],
                        color=EDGE, lw=0.9, alpha=.85 if n <= 12 else .35, zorder=2)
                if labels:
                    t = 0.5 + 0.16 * ((i * 7 + j * 3) % 5 - 2) / 2
                    _label_edge(ax, g, i, j, cos0, fs, t)
    _draw_cities(ax, g)
    ax.set_title(f"{n} cities, {n * (n - 1) // 2} connections", loc="left", fontsize=16, fontweight="bold", color=INK)
    ax.set_xlabel(f"Number on each line: {_distance_note(g)}", loc="left", color=MUTED)
    plt.show()


def show_tour(g, tour, title=None):
    length = tour_length(g, tour)
    n = g.n
    fig, ax, cos0 = _base_map(g)
    fs = max(4.5, 9.5 - 0.35 * n)
    for k in range(n):
        i, j = tour[k], tour[(k + 1) % n]
        ax.annotate("", xy=(g.coords[j][1], g.coords[j][0]), xytext=(g.coords[i][1], g.coords[i][0]),
                    arrowprops=dict(arrowstyle="-|>", color=TOUR, lw=2, shrinkA=5, shrinkB=5, mutation_scale=14),
                    zorder=3)
        if n <= 15:
            _label_edge(ax, g, i, j, cos0, fs)
    _draw_cities(ax, g, start=tour[0])
    ax.set_title(title or f"Tour through {n} cities: {length:,.0f} km", loc="left",
                 fontsize=16, fontweight="bold", color=INK)
    plt.show()