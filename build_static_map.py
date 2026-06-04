"""
Render a static PNG and SVG version of the 2026 1V Colombia map
(margin ADLE − Cepeda by municipio), suitable for Wikimedia Commons,
Wikipedia articles, and print embeds.

Reads the same source data as the interactive HTML map.

Output: map_2026_1V_margin.png and map_2026_1V_margin.svg in this folder.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PolyCollection
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D

HERE = Path(__file__).parent
SRC = Path("c:/Users/juanj/Documents/GitHub/YSC_Elecciones/00 MAPA ELECCIONES")
GEOJSON = SRC / "mpio_code.json"
TOTALS = SRC / "data/2026_1V/municipio_totals.csv"
CANDIDATES = SRC / "data/2026_1V/municipio_candidates.csv"

OUT_PNG = HERE / "map_2026_1V_margin.png"
OUT_SVG = HERE / "map_2026_1V_margin.svg"


def fix_mojibake(s: str) -> str:
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def interp(c_brand, steps, target=(252, 248, 244)):
    out = []
    for k in range(steps):
        t = k / (steps - 1)
        r = round(c_brand[0] + (target[0] - c_brand[0]) * t)
        g = round(c_brand[1] + (target[1] - c_brand[1]) * t)
        b = round(c_brand[2] + (target[2] - c_brand[2]) * t)
        out.append((r / 255, g / 255, b / 255))
    return out


CEPEDA = (140, 55, 140)
ADLE = (206, 116, 42)

BINS = [(-100, -80), (-80, -70), (-70, -60), (-60, -50), (-50, -40),
        (-40, -30), (-30, -20), (-20, -10), (-10, 0),
        (0, 10), (10, 20), (20, 30), (30, 40),
        (40, 50), (50, 60), (60, 70), (70, 80), (80, 101)]

COLORS = interp(CEPEDA, 9) + list(reversed(interp(ADLE, 9)))


def bin_color(margin_pct):
    for (lo, hi), col in zip(BINS, COLORS):
        if lo <= margin_pct < hi:
            return col
    return (0.7, 0.7, 0.7)


CAPITALES = {
    "01001": "Medellín", "03001": "Barranquilla", "05001": "Cartagena",
    "07001": "Tunja", "09001": "Manizales", "11001": "Popayán",
    "12001": "Valledupar", "13001": "Montería", "16001": "Bogotá",
    "17001": "Quibdó", "19001": "Neiva", "21001": "Santa Marta",
    "23001": "Pasto", "24001": "Pereira", "25001": "Cúcuta",
    "26001": "Armenia", "27001": "Bucaramanga", "28001": "Sincelejo",
    "29001": "Ibagué", "31001": "Cali", "40001": "Arauca",
    "44001": "Florencia", "46001": "Yopal", "48001": "Riohacha",
    "50001": "Inírida", "52001": "Villavicencio", "54001": "San José del Guaviare",
    "56001": "San Andrés", "60001": "Leticia", "64001": "Mocoa",
    "68001": "Mitú", "72001": "Puerto Carreño",
}


def polygon_centroid(coords):
    a = cx = cy = 0.0
    n = len(coords)
    for i in range(n - 1):
        x0, y0 = coords[i]
        x1, y1 = coords[i + 1]
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a *= 0.5
    if abs(a) < 1e-12:
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        return [sum(xs) / len(xs), sum(ys) / len(ys)]
    return [cx / (6 * a), cy / (6 * a)]


def feature_centroid(feat):
    g = feat["geometry"]
    if g["type"] == "Polygon":
        return polygon_centroid(g["coordinates"][0])
    if g["type"] == "MultiPolygon":
        largest = max(g["coordinates"], key=lambda poly: len(poly[0]))
        return polygon_centroid(largest[0])
    return None


def main():
    totals = {}
    with TOTALS.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            totals[r["scope_code"]] = {
                "name": fix_mojibake(r["scope_name"]),
                "validos": int(r["votos_validos"] or 0),
                "cepeda": 0, "adle": 0,
            }
    with CANDIDATES.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            code = r["scope_code"]
            if code not in totals:
                continue
            if r["codpar"] == "7" and r["codcan"] == "1":
                totals[code]["cepeda"] = int(r["votos"])
            elif r["codpar"] == "10" and r["codcan"] == "4":
                totals[code]["adle"] = int(r["votos"])

    gj = json.loads(GEOJSON.read_text(encoding="utf-8"))

    # Build matplotlib polygons + colors
    polys = []
    poly_colors = []
    cap_points = []  # (lon, lat, name)
    matched = 0
    for feat in gj["features"]:
        code = feat["properties"].get("id", "").zfill(5)
        t = totals.get(code)
        if t is None:
            color = (0.85, 0.85, 0.85)
            margin = None
        else:
            matched += 1
            v = t["validos"]
            margin = (t["adle"] - t["cepeda"]) / v * 100 if v else 0
            color = bin_color(margin)

        g = feat["geometry"]
        rings = []
        if g["type"] == "Polygon":
            rings = [g["coordinates"][0]]
        elif g["type"] == "MultiPolygon":
            rings = [p[0] for p in g["coordinates"]]
        for ring in rings:
            polys.append(ring)
            poly_colors.append(color)

        if code in CAPITALES:
            c = feature_centroid(feat)
            if c is not None:
                cap_points.append((c[0], c[1], CAPITALES[code]))

    print(f"Matched {matched} municipios; rendering {len(polys)} polygons; "
          f"{len(cap_points)} capitals.")

    # ---- Figure ----
    # Colombia rough bounds: lon [-79, -66], lat [-4.5, 13.5]
    fig, ax = plt.subplots(figsize=(12, 14), dpi=180)
    pc = PolyCollection(
        polys, facecolors=poly_colors, edgecolors="#666666",
        linewidths=0.15, antialiased=True,
    )
    ax.add_collection(pc)
    ax.set_xlim(-80.5, -65.5)
    ax.set_ylim(-4.5, 13.7)
    ax.set_aspect(1.0 / abs(0.5 * (1 + 1)))  # near-1:1 for Colombia latitudes
    ax.set_aspect("equal")
    ax.set_axis_off()

    # Capital markers + labels
    for lon, lat, name in cap_points:
        ax.plot(lon, lat, "o", markersize=4, markerfacecolor="#111",
                markeredgecolor="white", markeredgewidth=0.8, zorder=10)
        ax.annotate(
            name, xy=(lon, lat), xytext=(5, 0), textcoords="offset points",
            fontsize=7.5, fontweight="bold", color="#1a1a1a",
            path_effects=[],
            zorder=11,
        )
        # Approximate "halo" via white-outlined text in older mpl style:
    try:
        import matplotlib.patheffects as PE
        for txt in ax.texts:
            txt.set_path_effects([
                PE.withStroke(linewidth=2.0, foreground="white"),
            ])
    except Exception:
        pass

    # Title
    fig.suptitle(
        "Colombia 2026 — Primera vuelta presidencial",
        fontsize=18, fontweight="bold", y=0.96,
    )
    ax.set_title(
        "Margen ADLE − Cepeda por municipio (% sobre votos válidos)\n"
        "31 de mayo de 2026 · 100% de mesas escrutadas",
        fontsize=11, color="#555", pad=12,
    )

    # Legend (discrete swatches)
    legend_patches = []
    legend_labels = []
    # Walk bins from most-Cepeda to most-ADLE
    for (lo, hi), col in zip(BINS, COLORS):
        legend_patches.append(mpatches.Patch(facecolor=col, edgecolor="#999",
                                             linewidth=0.3))
        if lo == -100:
            lbl = "< −80"
        elif hi == 101:
            lbl = "> +80"
        else:
            lbl = f"{lo:+d} a {hi:+d}"
        legend_labels.append(lbl)
    leg = ax.legend(
        legend_patches, legend_labels,
        loc="lower left", bbox_to_anchor=(0.01, 0.01),
        fontsize=7, title="Margen (pp)\nADLE − Cepeda",
        title_fontsize=8, ncol=2, frameon=True, framealpha=0.95,
    )
    leg.get_frame().set_edgecolor("#bbb")

    # Footer / attribution
    fig.text(
        0.5, 0.02,
        "Fuente: Registraduría Nacional del Estado Civil · Yo Sí Cuento",
        ha="center", fontsize=8, color="#777",
    )

    fig.tight_layout(rect=[0, 0.03, 1, 0.93])
    fig.savefig(OUT_PNG, dpi=200, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT_SVG, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUT_PNG} ({OUT_PNG.stat().st_size:,} bytes)")
    print(f"Wrote {OUT_SVG} ({OUT_SVG.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
