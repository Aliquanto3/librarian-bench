"""Charte générique v2.1 : thèmes, contrastes et règles vérifiables de la page d'annotation."""

import re

from librarian_bench.report.page_annotation import HTML

CSS = HTML.split("<style>", 1)[1].split("</style>", 1)[0]
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")


def _jetons(bloc: str) -> dict[str, str]:
    return {m[0]: m[1].upper() for m in re.findall(r"--([a-z-]+):(#[0-9A-Fa-f]{6})", bloc)}


def _themes() -> dict[str, dict[str, str]]:
    sombre = CSS.split(":root{", 1)[1].split("}", 1)[0]
    clair_media = CSS.split("@media (prefers-color-scheme:light){", 1)[1].split("\n", 1)[0]
    clair_force = CSS.split('[data-theme="clair"],[data-theme="light"]{', 1)[1].split("\n", 1)[0]
    return {"sombre": _jetons(sombre), "clair": _jetons(clair_force), "media": _jetons(clair_media)}


def _lum(h: str) -> float:
    c = [int(h[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _ratio(a: str, b: str) -> float:
    x, y = sorted((_lum(a), _lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


TEXTE = [  # (premier plan, fond) : 4,5:1
    ("texte", "fond"),
    ("texte", "surface"),
    ("texte", "surface-alt"),
    ("texte-attenue", "surface"),
    ("texte-attenue", "surface-alt"),
    ("primaire", "surface"),
    ("primaire", "surface-alt"),
    ("succes", "fond"),
    ("sur-bouton", "bouton"),
    ("sur-bouton", "bouton-survol"),
    ("sur-statut", "succes"),
    ("sur-statut", "erreur"),
    ("sur-bouton", "bouton"),
]
NON_TEXTE = [  # 3:1
    ("trait-fort", "surface"),
    ("trait-fort", "fond"),
    ("focus", "surface"),
    ("focus", "fond"),
    ("primaire", "trait"),
    ("primaire", "surface-alt"),
    ("accent", "fond"),
    ("succes", "surface"),
    ("erreur", "surface"),
]


def test_les_deux_themes_ont_les_memes_jetons_et_le_media_egale_le_force() -> None:
    t = _themes()
    assert set(t["sombre"]) == set(t["clair"])
    assert t["media"] == t["clair"]
    assert t["sombre"]["fond"] == "#0F1318" and t["clair"]["fond"] == "#F6F8FB"


def test_theme_sombre_par_defaut_et_selecteurs_de_theme() -> None:
    assert "color-scheme:dark" in CSS.split("}", 1)[0]
    assert ':root:not([data-theme="sombre"]):not([data-theme="dark"])' in CSS


def test_contrastes_texte_4_5_dans_les_deux_themes() -> None:
    for nom, j in _themes().items():
        for av, ar in TEXTE:
            assert _ratio(j[av], j[ar]) >= 4.5, (nom, av, ar)


def test_contrastes_non_texte_3_dans_les_deux_themes() -> None:
    for nom, j in _themes().items():
        for av, ar in NON_TEXTE:
            assert _ratio(j[av], j[ar]) >= 3.0, (nom, av, ar)


def test_le_bleu_n_est_jamais_un_aplat_de_bouton() -> None:
    for sel, corps in re.findall(r"([^{}]+)\{([^{}]*)\}", CSS):
        if "button" in sel or "#exp" in sel:
            assert not re.search(r"background(-color)?:[^;]*var\(--primaire", corps), sel


def test_aucun_hex_hors_des_blocs_de_theme() -> None:
    reste = re.sub(r"--[a-z-]+:#[0-9A-Fa-f]{6}", "", CSS)
    assert not HEX.search(reste)
    assert not re.search(r"#(fff|000)\b|rgb\(", reste)


def test_aucune_couleur_de_repli_dans_var() -> None:
    assert not re.search(r"var\(--[a-z-]+\s*,", CSS)


def test_polices_et_filet_or_de_la_charte() -> None:
    assert "Sora" in CSS and "Atkinson Hyperlegible" in CSS
    assert "font-weight:600" in CSS
    assert "Fredoka" not in CSS and "system-ui,Segoe UI" not in CSS
    assert re.search(r"h1::after\{[^}]*background:var\(--accent\)", CSS)
    assert "outline:2px solid var(--focus)" in CSS
