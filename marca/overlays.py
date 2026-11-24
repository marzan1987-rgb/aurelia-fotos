"""Textos de pantalla de la serie con el manual de marca Aurelia (aproximación).

Manual: Halimun (logo) · Brandon Grotesque Light · Open Sans Regular.
Aquí: logo real vectorizado · Halimun (oficial; los signos ¿ ? que no trae se
toman de Sacramento) · Coves Light (alternativa gratis a Brandon) · Open Sans.
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

LIGHT = os.path.join(AQUI, "Coves-Light.otf")            # ≈ Brandon Grotesque Light
TEXTO = os.path.join(AQUI, "OpenSans-Regular.ttf")       # oficial
TEXTO_B = os.path.join(AQUI, "OpenSans-SemiBold.ttf")
SCRIPT = os.path.join(AQUI, "Halimun.ttf")               # oficial del manual
RESPALDO = {SCRIPT: os.path.join(AQUI, "Sacramento.ttf")}  # para glifos que falten
LOGO = os.path.join(AQUI, "logo_aurelia_blanco.png")     # logo real
LOGO_CORTE_TIENDA = 292   # filas 0-291: "Aurelia"; 372-456: "TIENDA"


_CMAPS = {}


def _tiene(ruta, c):
    if ruta not in _CMAPS:
        from fontTools.ttLib import TTFont
        _CMAPS[ruta] = set(TTFont(ruta).getBestCmap())
    return c == " " or ord(c) in _CMAPS[ruta]


def _tramos(t, ruta, tam):
    """Divide el texto en tramos por fuente: la principal o la de respaldo si falta el glifo."""
    principal = ImageFont.truetype(ruta, tam)
    resp = RESPALDO.get(ruta)
    fr = ImageFont.truetype(resp, tam) if resp else None
    out = []
    for c in t:
        f = principal if (fr is None or _tiene(ruta, c)) else fr
        if out and out[-1][1] is f:
            out[-1][0] += c
        else:
            out.append([c, f])
    return out


def _ancho(t, ruta, tam, tr):
    if tr:
        return sum(f.getlength(c) for txt, f in _tramos(t, ruta, tam) for c in txt) + tr * max(0, len(t) - 1)
    return sum(f.getlength(txt) for txt, f in _tramos(t, ruta, tam))


# Halimun no trae tildes ni ñ: dibuja la letra base. Se agrega el signo a mano.
SIN_TILDE = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n",
             "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N"}


def _signo(d, f, x, y, base, c, tam, color):
    """Dibuja tilde (o virgulilla de la ñ) sobre la letra base ya dibujada en (x, y).
    Se mide con la altura real de la letra, porque Halimun tiene una altura x muy baja."""
    l, t, r, b = f.getbbox(base)
    alto = b - t
    cx = x + (l + r) / 2 - alto * 0.55
    top = y + t - alto * 0.22
    g = max(4, int(round(alto * 0.16)))
    if c in "ñÑ":
        pts = [(cx - alto * 0.35 + i * alto * 0.07, top - alto * (0.12 if i % 2 else 0.0)) for i in range(11)]
        d.line(pts, fill=color, width=g, joint="curve")
    else:
        p0, p1 = (cx - alto * 0.18, top), (cx + alto * 0.32, top - alto * 0.80)
        d.line([p0, p1], fill=color, width=g)
        for px, py in (p0, p1):  # puntas redondeadas como el trazo de la manuscrita
            d.ellipse([px - g / 2, py - g / 2, px + g / 2, py + g / 2], fill=color)


def _escribir(d, x, y, t, ruta, tam, tr, color):
    for txt, f in _tramos(t, ruta, tam):
        if ruta == SCRIPT and not tr and any(c in SIN_TILDE for c in txt) and f.path == SCRIPT:
            plano = "".join(SIN_TILDE.get(c, c) for c in txt)
            d.text((x, y), plano, font=f, fill=color)
            for i, c in enumerate(txt):
                if c in SIN_TILDE:
                    _signo(d, f, x + f.getlength(plano[:i]), y, SIN_TILDE[c], c, tam, color)
            x += f.getlength(plano)
            continue
        if tr:
            for c in txt:
                d.text((x, y), c, font=f, fill=color)
                x += f.getlength(c) + tr
        else:  # sin espaciado: se dibuja el tramo entero para conservar las uniones de la manuscrita
            d.text((x, y), txt, font=f, fill=color)
            x += f.getlength(txt)


def bloque(lineas, y_centro, tam=48, fuente=TEXTO, tracking=0, caja=MORADO, color="white",
           interlinea=1.4, mayus=False, alfa_caja=235, max_ancho=W - 140):
    """Líneas centradas; con caja = rectángulo de color secundario (uso correcto del manual).
    Si alguna línea no cabe en max_ancho, el tamaño se reduce hasta que quepa."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lineas = [l.upper() if mayus else l for l in lineas]
    rel_tr = tracking / tam if tam else 0
    while tam > 12 and max(_ancho(l, fuente, tam, rel_tr * tam) for l in lineas) > max_ancho - (96 if caja else 0):
        tam -= 2
    tracking = rel_tr * tam
    alto = tam * interlinea
    total = alto * len(lineas)
    y0 = y_centro - total / 2
    anchos = [_ancho(l, fuente, tam, tracking) for l in lineas]
    if caja:
        px, py = 48, 34
        bw = max(anchos) + 2 * px
        d.rectangle([(W - bw) / 2, y0 - py, (W + bw) / 2, y0 + total + py - tam * 0.3],
                    fill=caja + (alfa_caja,))
    for i, l in enumerate(lineas):
        _escribir(d, (W - anchos[i]) / 2, y0 + i * alto, l, fuente, tam, tracking, color)
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


def tarjeta_titulo(subtitulo="Capítulo 1"):
    """Tarjeta de título de la serie: fondo coral, trazos de la A, título en Halimun y logo."""
    t = Image.new("RGBA", (W, H), CORAL + (255,))
    trazos_A(t)
    t.alpha_composite(bloque(["No me la prestes"], H * 0.40, tam=170, fuente=SCRIPT, caja=None, interlinea=1.1))
    t.alpha_composite(titulo(["una serie de aurelia"], H * 0.50, tam=40, caja=None))
    t.alpha_composite(titulo([subtitulo], H * 0.58, tam=58, caja=MORADO))
    pegar_logo(t, 420, H * 0.74)
    return t.convert("RGB")


def cartel_inicio(texto="Santiago, 30 de noviembre"):
    """Cartel negro de inicio del adelanto."""
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(titulo([texto], H * 0.5, tam=46, caja=None))
    return c.convert("RGB")


def etiqueta_flashback():
    """Etiqueta 'FLASHBACK' para las escenas del pasado."""
    return titulo(["flashback"], H * 0.93, tam=40, caja=MORADO)


def piezas_extra(out):
    os.makedirs(out, exist_ok=True)
    tarjeta_titulo("Capítulo 1").save(os.path.join(out, "titulo_cap1.png"))
    tarjeta_titulo("1/12").save(os.path.join(out, "titulo_adelanto.png"))
    cartel_inicio().save(os.path.join(out, "cartel_inicio.png"))
    etiqueta_flashback().save(os.path.join(out, "flashback.png"))
    bloque(["Me robaron."], H * 0.82, tam=64).save(os.path.join(out, "gancho.png"))
