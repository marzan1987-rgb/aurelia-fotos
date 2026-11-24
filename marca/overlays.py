"""Genera los textos de pantalla de la serie con el estilo de marca Aurelia.

Fucsia #F0025A y blanco · Montserrat (textos) · Sacramento (acentos) · logo real.
Cada overlay es un PNG transparente de 1080x1920 que luego se monta sobre el clip.
Uso: python3 overlays.py <carpeta_salida>
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FUCSIA = (240, 2, 90)
W, H = 1080, 1920
SEMI = os.path.join(AQUI, "Montserrat-SemiBold.ttf")
LIGHT = os.path.join(AQUI, "Montserrat-Light.ttf")
SCRIPT = os.path.join(AQUI, "Sacramento.ttf")
LOGO = os.path.join(AQUI, "logo_aurelia_blanco.png")


def ancho(texto, fuente, tracking):
    return sum(fuente.getlength(c) for c in texto) + tracking * max(0, len(texto) - 1)


def escribir(d, x, y, texto, fuente, tracking, color):
    for c in texto:
        d.text((x, y), c, font=fuente, fill=color)
        x += fuente.getlength(c) + tracking


def bloque(lineas, y_centro, tam=50, fuente=SEMI, tracking=4, caja=True, color="white",
           interlinea=1.35, mayus=True):
    """Bloque de líneas centradas, opcionalmente sobre una caja fucsia redondeada."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(fuente, tam)
    lineas = [l.upper() if mayus else l for l in lineas]
    alto_linea = tam * interlinea
    total = alto_linea * len(lineas)
    y0 = y_centro - total / 2
    anchos = [ancho(l, f, tracking) for l in lineas]
    if caja:
        pad_x, pad_y = 44, 30
        bw = max(anchos) + 2 * pad_x
        d.rounded_rectangle([(W - bw) / 2, y0 - pad_y, (W + bw) / 2, y0 + total + pad_y - tam * 0.25],
                            radius=28, fill=FUCSIA + (225,))
    for i, l in enumerate(lineas):
        escribir(d, (W - anchos[i]) / 2, y0 + i * alto_linea, l, f, tracking, color)
    return img


def pegar(base, capa):
    base.alpha_composite(capa)
    return base


def logo(base, ancho_logo, y):
    lg = Image.open(LOGO)
    r = ancho_logo / lg.width
    lg = lg.resize((int(lg.width * r), int(lg.height * r)), Image.LANCZOS)
    base.alpha_composite(lg, ((W - lg.width) // 2, int(y)))
    return base


def overlays(out):
    os.makedirs(out, exist_ok=True)
    piezas = {
        # Adelanto
        "a1": bloque(["algo desapareció…"], H * 0.70, tam=56, fuente=LIGHT, tracking=6, caja=False),
        "a2": bloque(["1/12"], H * 0.80, tam=150, tracking=8, caja=False, color=FUCSIA + (255,)),
        # Capítulo 1
        "t1": bloque(["caso n°1:", "blusa colomba"], H * 0.13, tam=58, tracking=6),
        "t2": bloque(["30 de noviembre.", "Mi hermana me la pidió", "“solo para el asado", "de fin de año de la pega”"],
                     H * 0.12, tam=46, tracking=1, mayus=False),
        "t3": bloque(["Eso fue hace 48 horas…"], H * 0.84, tam=50, tracking=1, mayus=False),
        "t4": bloque(["…y encima en el amigo secreto", "le tocó una Gift Card Aurelia"],
                     H * 0.10, tam=44, tracking=1, mayus=False),
        "t5": bloque(["unidad aurelia:", "caso abierto"], H * 0.80, tam=64, tracking=6),
    }
    for nombre, img in piezas.items():
        img.save(os.path.join(out, nombre + ".png"))

    # Pantalla final fucsia con el logo real
    fin = Image.new("RGBA", (W, H), FUCSIA + (255,))
    pegar(fin, bloque(["¿Quién es tu", "ladrona de ropa?"], H * 0.27, tam=120, fuente=SCRIPT, tracking=0,
                      caja=False, mayus=False, interlinea=1.15))
    pegar(fin, bloque(["Etiquétala en los comentarios", "y participa por una"], H * 0.47, tam=44,
                      fuente=LIGHT, tracking=2, caja=False, mayus=False))
    pegar(fin, bloque(["Gift Card de $15.000"], H * 0.555, tam=60, tracking=4, caja=False))
    pegar(fin, bloque(["cap. 2 · viernes 4 de diciembre"], H * 0.66, tam=34, fuente=LIGHT, tracking=6,
                      caja=False))
    logo(fin, 520, H * 0.76)
    fin.convert("RGB").save(os.path.join(out, "fin.png"))


if __name__ == "__main__":
    overlays(sys.argv[1] if len(sys.argv) > 1 else "overlays")
