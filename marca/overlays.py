"""Textos de pantalla de la serie con el manual de marca Aurelia (aproximación).

Manual: Halimun (logo) · Brandon Grotesque Light · Open Sans Regular.
Aquí: logo real vectorizado · Montserrat Light (en lugar de Brandon) ·
Open Sans (oficial) · Sacramento (en lugar de Halimun, solo acentos).
Colores: primario coral #E74152 · secundarios #F10159, #C21C8B, #913C78.
Rectángulos de texto en morado #913C78 (mejor contraste con blanco, 6,7:1).

Cada overlay es un PNG transparente de 1080x1920 que se monta sobre el clip.
Uso: python3 overlays.py <carpeta_salida>
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
CORAL = (231, 65, 82)      # primario #E74152
FUCSIA = (241, 1, 89)      # secundario #F10159
MAGENTA = (194, 28, 139)   # secundario #C21C8B
MORADO = (145, 60, 120)    # secundario #913C78
W, H = 1080, 1920

LIGHT = os.path.join(AQUI, "Montserrat-Light.ttf")       # ≈ Brandon Grotesque Light
TEXTO = os.path.join(AQUI, "OpenSans-Regular.ttf")       # oficial
TEXTO_B = os.path.join(AQUI, "OpenSans-SemiBold.ttf")
SCRIPT = os.path.join(AQUI, "Sacramento.ttf")            # ≈ Halimun (solo acentos)
LOGO = os.path.join(AQUI, "logo_aurelia_blanco.png")     # logo real
LOGO_CORTE_TIENDA = 292   # filas 0-291: "Aurelia"; 372-456: "TIENDA"


def _ancho(t, f, tr):
    return sum(f.getlength(c) for c in t) + tr * max(0, len(t) - 1)


def _escribir(d, x, y, t, f, tr, color):
    for c in t:
        d.text((x, y), c, font=f, fill=color)
        x += f.getlength(c) + tr


def bloque(lineas, y_centro, tam=48, fuente=TEXTO, tracking=0, caja=MORADO, color="white",
           interlinea=1.4, mayus=False, alfa_caja=235):
    """Líneas centradas; con caja = rectángulo de color secundario (uso correcto del manual)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(fuente, tam)
    lineas = [l.upper() if mayus else l for l in lineas]
    alto = tam * interlinea
    total = alto * len(lineas)
    y0 = y_centro - total / 2
    anchos = [_ancho(l, f, tracking) for l in lineas]
    if caja:
        px, py = 48, 34
        bw = max(anchos) + 2 * px
        d.rectangle([(W - bw) / 2, y0 - py, (W + bw) / 2, y0 + total + py - tam * 0.3],
                    fill=caja + (alfa_caja,))
    for i, l in enumerate(lineas):
        _escribir(d, (W - anchos[i]) / 2, y0 + i * alto, l, f, tracking, color)
    return img


def titulo(lineas, y_centro, tam=60, caja=MORADO):
    """Títulos al estilo 'VISTE QUIEN AMAS SER': mayúsculas finas y espaciadas."""
    return bloque(lineas, y_centro, tam=tam, fuente=LIGHT, tracking=tam * 0.22, caja=caja, mayus=True,
                  interlinea=1.35)


def logo_img(parte="completo"):
    lg = Image.open(LOGO)
    if parte == "aurelia":
        lg = lg.crop((0, 0, lg.width, LOGO_CORTE_TIENDA))
    elif parte == "A":
        lg = lg.crop((0, 0, 560, LOGO_CORTE_TIENDA))
    return lg


def pegar_logo(base, ancho, y, parte="completo", x=None):
    lg = logo_img(parte)
    r = ancho / lg.width
    lg = lg.resize((int(lg.width * r), int(lg.height * r)), Image.LANCZOS)
    base.alpha_composite(lg, (int((W - lg.width) / 2 if x is None else x), int(y)))
    return lg.height


def logo_secundario(base, ancho, y):
    """Logo secundario del manual: 'Aurelia' + 'VISTE QUIEN AMAS SER'."""
    alto = pegar_logo(base, ancho, y, parte="aurelia")
    base.alpha_composite(titulo(["viste quien amas ser"], y + alto + ancho * 0.07, tam=int(ancho * 0.065),
                                caja=None))


def trazos_A(base):
    """Elemento gráfico del manual: la 'A' del logo, grande, en dos esquinas."""
    a = logo_img("A")
    r = 620 / a.width
    a = a.resize((int(a.width * r), int(a.height * r)), Image.LANCZOS)
    base.alpha_composite(a, (W - int(a.width * 0.72), -int(a.height * 0.30)))
    b = a.rotate(180)
    base.alpha_composite(b, (-int(b.width * 0.28), H - int(b.height * 0.70)))


def overlays(out):
    os.makedirs(out, exist_ok=True)
    piezas = {
        # Adelanto: sin caja, sobre la escena oscura
        "a1": titulo(["algo desapareció…"], H * 0.80, tam=50),
        "a2": bloque(["1/12"], H * 0.885, tam=120, fuente=TEXTO_B, caja=CORAL, interlinea=1.15),
        # Capítulo 1
        "t1": titulo(["caso n°1", "blusa colomba"], H * 0.13, tam=56),
        "t2": bloque(["30 de noviembre.", "Mi hermana me la pidió", "“solo para el asado", "de fin de año de la pega”"],
                     H * 0.12, tam=44),
        "t3": bloque(["Eso fue hace 48 horas…"], H * 0.84, tam=48),
        "t4": bloque(["…y encima en el amigo secreto", "le tocó una Gift Card Aurelia"], H * 0.10, tam=42),
        "t5": titulo(["unidad aurelia", "caso abierto"], H * 0.80, tam=62),
    }
    for nombre, img in piezas.items():
        img.save(os.path.join(out, nombre + ".png"))

    # Pantalla final: fondo coral (primario), trazos de la A y logo secundario
    fin = Image.new("RGBA", (W, H), CORAL + (255,))
    trazos_A(fin)
    fin.alpha_composite(bloque(["¿Quién es tu", "ladrona de ropa?"], H * 0.29, tam=124, fuente=SCRIPT, caja=None,
                               interlinea=1.1))
    fin.alpha_composite(bloque(["Etiquétala en los comentarios", "y participa por una"], H * 0.475, tam=44))
    fin.alpha_composite(titulo(["gift card $15.000"], H * 0.565, tam=58, caja=None))
    fin.alpha_composite(bloque(["Cap. 2 · viernes 4 de diciembre"], H * 0.645, tam=34, caja=None,
                               color=(255, 255, 255, 220)))
    logo_secundario(fin, 560, H * 0.73)
    fin.convert("RGB").save(os.path.join(out, "fin.png"))


if __name__ == "__main__":
    overlays(sys.argv[1] if len(sys.argv) > 1 else "overlays")
