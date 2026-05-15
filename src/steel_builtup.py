from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


@dataclass
class WeldedISectionInput:
    h: float
    bf_top: float
    tf_top: float
    bf_bottom: float
    tf_bottom: float
    tw: float
    fy: float = 355.0
    gamma_m0: float = 1.05


def validate_welded_i(data: WeldedISectionInput) -> None:
    values = {
        "altezza totale": data.h,
        "ala superiore": data.bf_top,
        "spessore ala superiore": data.tf_top,
        "ala inferiore": data.bf_bottom,
        "spessore ala inferiore": data.tf_bottom,
        "anima": data.tw,
    }
    invalid = [name for name, value in values.items() if value <= 0]
    if invalid:
        raise ValueError("Valori non validi: " + ", ".join(invalid))
    if data.tf_top + data.tf_bottom >= data.h:
        raise ValueError("La somma degli spessori delle ali deve essere minore dell'altezza totale.")
    if data.tw > max(data.bf_top, data.bf_bottom):
        raise ValueError("Lo spessore dell'anima non puo' superare la larghezza massima delle ali.")


def welded_i_properties(data: WeldedISectionInput) -> dict[str, float]:
    validate_welded_i(data)

    hw = data.h - data.tf_top - data.tf_bottom
    rectangles = [
        {"name": "Ala inferiore", "b": data.bf_bottom, "h": data.tf_bottom, "y": data.tf_bottom / 2.0},
        {"name": "Anima", "b": data.tw, "h": hw, "y": data.tf_bottom + hw / 2.0},
        {"name": "Ala superiore", "b": data.bf_top, "h": data.tf_top, "y": data.h - data.tf_top / 2.0},
    ]

    area = sum(item["b"] * item["h"] for item in rectangles)
    yg = sum(item["b"] * item["h"] * item["y"] for item in rectangles) / area
    ixx = sum(
        item["b"] * item["h"] ** 3 / 12.0
        + item["b"] * item["h"] * (item["y"] - yg) ** 2
        for item in rectangles
    )
    iyy = sum(item["h"] * item["b"] ** 3 / 12.0 for item in rectangles)

    y_top = data.h - yg
    y_bottom = yg
    x_edge = max(data.bf_top, data.bf_bottom) / 2.0
    j_torsion = (
        data.bf_top * data.tf_top**3
        + data.bf_bottom * data.tf_bottom**3
        + hw * data.tw**3
    ) / 3.0

    return {
        "A": area,
        "xg": 0.0,
        "yg": yg,
        "Ixx": ixx,
        "Iyy": iyy,
        "J_approx": j_torsion,
        "Wx_top": ixx / y_top,
        "Wx_bottom": ixx / y_bottom,
        "Wy": iyy / x_edge,
        "h_web": hw,
        "y_top": y_top,
        "y_bottom": y_bottom,
        "peso_kg_m": area * 7850.0e-6,
        "fyd": data.fy / data.gamma_m0,
    }


def property_table(name: str, props: dict[str, float]) -> pd.DataFrame:
    rows = [
        ("Sezione", name, "-"),
        ("A", props["A"], "mm2"),
        ("xg", props["xg"], "mm"),
        ("yg", props["yg"], "mm"),
        ("Ixx", props["Ixx"], "mm4"),
        ("Iyy", props["Iyy"], "mm4"),
        ("J torsionale approssimato", props["J_approx"], "mm4"),
        ("Wx superiore", props["Wx_top"], "mm3"),
        ("Wx inferiore", props["Wx_bottom"], "mm3"),
        ("Wy", props["Wy"], "mm3"),
        ("Peso lineare", props["peso_kg_m"], "kg/m"),
        ("fyd", props["fyd"], "MPa"),
    ]
    return pd.DataFrame(rows, columns=["Grandezza", "Valore", "Unita"])


def stress_check_table(
    data: WeldedISectionInput,
    props: dict[str, float],
    n_ed_kn: float,
    mx_ed_knm: float,
    my_ed_knm: float,
) -> pd.DataFrame:
    points = [
        ("sup sx", -data.bf_top / 2.0, props["y_top"]),
        ("sup dx", data.bf_top / 2.0, props["y_top"]),
        ("inf sx", -data.bf_bottom / 2.0, -props["y_bottom"]),
        ("inf dx", data.bf_bottom / 2.0, -props["y_bottom"]),
    ]
    n = n_ed_kn * 1_000.0
    mx = mx_ed_knm * 1_000_000.0
    my = my_ed_knm * 1_000_000.0

    stresses = []
    for label, x, y in points:
        sigma = n / props["A"] + mx * y / props["Ixx"] + my * x / props["Iyy"]
        stresses.append((label, sigma))

    label_max, sigma_max = max(stresses, key=lambda item: abs(item[1]))
    dc = abs(sigma_max) / props["fyd"] if props["fyd"] else 0.0

    return pd.DataFrame(
        [
            ("Sforzo normale", n_ed_kn, "-", "kN", ""),
            ("Momento forte Mx", mx_ed_knm, "-", "kNm", ""),
            ("Momento debole My", my_ed_knm, "-", "kNm", ""),
            ("Tensione massima elastica", sigma_max, props["fyd"], "MPa", label_max),
            ("Rapporto domanda/capacita", dc, 1.0, "-", "OK" if dc <= 1.0 else "NON OK"),
        ],
        columns=["Verifica", "Ed", "Rd", "Unita", "Esito"],
    )


def welded_i_plot(data: WeldedISectionInput, props: dict[str, float]):
    hw = data.h - data.tf_top - data.tf_bottom
    fig, ax = plt.subplots(figsize=(5.2, 5.2))

    shapes = [
        (-data.bf_bottom / 2.0, 0.0, data.bf_bottom, data.tf_bottom),
        (-data.tw / 2.0, data.tf_bottom, data.tw, hw),
        (-data.bf_top / 2.0, data.h - data.tf_top, data.bf_top, data.tf_top),
    ]
    for x, y, b, h in shapes:
        ax.add_patch(Rectangle((x, y), b, h, facecolor="#d9dee3", edgecolor="#1f2933", linewidth=1.4))

    ax.axhline(props["yg"], color="#111111", linewidth=1.0, linestyle="--")
    ax.axvline(0.0, color="#666666", linewidth=0.8, linestyle=":")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]")
    ax.set_title("Sezione composta saldata a doppio T")
    margin = max(data.bf_top, data.bf_bottom, data.h) * 0.12
    ax.set_xlim(-max(data.bf_top, data.bf_bottom) / 2.0 - margin, max(data.bf_top, data.bf_bottom) / 2.0 + margin)
    ax.set_ylim(-margin, data.h + margin)
    ax.grid(True, color="#e6e8eb", linewidth=0.6)
    fig.tight_layout()
    return fig
