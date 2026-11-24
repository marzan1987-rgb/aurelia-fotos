"""Armado de los videos de la serie "No me la prestes" (sin gastar créditos).

Toma los clips animados, las imágenes de las tarjetas, los textos de marca
(marca/overlays.py) y la voz en off, y genera el MP4 vertical final.

Uso:
    python3 armar.py adelanto
    python3 armar.py cap1

Requiere ffmpeg. La voz va en voz/ (no se sube al repositorio).
"""
import os
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "marca"))
import overlays as ov  # noqa: E402

CLIPS = os.path.join(AQUI, "clips")
VOZ = os.path.join(AQUI, "voz")
SALIDA = os.path.join(AQUI, "armado")
NORM = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30"
CALIDO = "colorbalance=rs=0.08:gs=0.03:bs=-0.08:rm=0.05:bm=-0.05,eq=saturation=1.08:gamma=1.02"
FRIO = "colorbalance=rs=-0.04:bs=0.05,eq=saturation=0.95"


def sh(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def subtitulo(lineas, y=0.80):
    return ov.bloque(lineas, ov.H * y, tam=44)


def segmento(tmp, n, dur, fuente, capas=(), filtro="", inicio=0.0, velocidad=1.0, imagen=False):
    """Genera un segmento de video de 'dur' segundos con capas PNG temporizadas.

    capas: lista de (imagen PIL o ruta, t_inicio, t_fin).
    """
    salida = os.path.join(tmp, f"s{n:02d}.mp4")
    entradas, filtros = [], []
    if imagen:
        entradas += ["-loop", "1", "-framerate", "30", "-t", str(dur), "-i", fuente]
        filtros.append(f"[0:v]{NORM},format=rgba[v0]")
    else:
        entradas += ["-ss", str(inicio), "-i", fuente]
        cadena = f"setpts={velocidad}*(PTS-STARTPTS),{NORM}"
        if filtro:
            cadena += "," + filtro
        filtros.append(f"[0:v]{cadena},format=rgba[v0]")
    ultimo = "v0"
    for k, (capa, t0, t1) in enumerate(capas, start=1):
        ruta = capa if isinstance(capa, str) else os.path.join(tmp, f"c{n:02d}_{k}.png")
        if not isinstance(capa, str):
            capa.save(ruta)
        entradas += ["-loop", "1", "-i", ruta]
        filtros.append(f"[{k}:v]format=rgba,fade=in:st={t0}:d=0.25:alpha=1,fade=out:st={max(t0, t1 - 0.2)}:d=0.2:alpha=1[o{k}]")
        filtros.append(f"[{ultimo}][o{k}]overlay=0:0:shortest=1[v{k}]")
        ultimo = f"v{k}"
    filtros.append(f"[{ultimo}]format=yuv420p,trim=duration={dur}[out]")
    # audio de ambiente del clip, bajo; silencio para imágenes
    if imagen:
        audio = ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo"]
        amap = f"{len(capas) + 1}:a"
        aargs = ["-map", amap]
    else:
        audio = []
        aargs = ["-map", "0:a", "-af", f"atempo={1 / velocidad:.4f},volume=0.25"]
    sh(["ffmpeg", "-y", *entradas, *audio, "-filter_complex", ";".join(filtros), "-map", "[out]", *aargs,
        "-t", str(dur), "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-ar", "44100",
        "-ac", "2", salida])
    return salida


def unir(tmp, segmentos, voces, nombre):
    """Concatena los segmentos y mezcla la voz en off: voces = [(archivo, t_desde, t_hasta, t_en_video)]."""
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as f:
        f.writelines(f"file '{s}'\n" for s in segmentos)
    base = os.path.join(tmp, "base.mp4")
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", base])
    entradas, filtros, etiquetas = ["-i", base], [], ["[0:a]"]
    for k, (archivo, a, b, t) in enumerate(voces, start=1):
        entradas += ["-i", archivo]
        ms = int(t * 1000)
        filtros.append(f"[{k}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=44100,"
                       f"aformat=channel_layouts=stereo,adelay={ms}|{ms},volume=1.6[a{k}]")
        etiquetas.append(f"[a{k}]")
    filtros.append(f"{''.join(etiquetas)}amix=inputs={len(etiquetas)}:normalize=0,alimiter=limit=0.95[aout]")
    os.makedirs(SALIDA, exist_ok=True)
    final = os.path.join(SALIDA, nombre)
    sh(["ffmpeg", "-y", *entradas, "-filter_complex", ";".join(filtros), "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", final])
    return final


def adelanto(tmp):
    piezas = os.path.join(tmp, "piezas")
    ov.piezas_extra(piezas)
    s1 = segmento(tmp, 1, 1.5, os.path.join(piezas, "cartel_inicio.png"), imagen=True)
    s2 = segmento(tmp, 2, 6.5, os.path.join(CLIPS, "00_adelanto_closet_colorido_720p.mp4"), velocidad=1.3,
                  capas=[(ov.titulo(["algo desapareció…"], ov.H * 0.80, tam=50), 3.2, 6.5)])
    s3 = segmento(tmp, 3, 3.0, os.path.join(piezas, "titulo_adelanto.png"), imagen=True)
    voces = [(os.path.join(VOZ, "final_adelanto_G.mp3"), 0, 3.7, 2.2)]
    return unir(tmp, [s1, s2, s3], voces, "adelanto_25nov_final.mp4")


def cap1(tmp):
    piezas = os.path.join(tmp, "piezas")
    ov.piezas_extra(piezas)
    flash = ov.etiqueta_flashback()
    D = os.path.join(CLIPS, "cap1_tu_D_720p.mp4")
    segs = [
        segmento(tmp, 1, 2.0, D, filtro=FRIO, capas=[(ov.bloque(["Me robaron."], ov.H * 0.80, tam=64), 0.3, 2.0)]),
        segmento(tmp, 2, 1.5, os.path.join(piezas, "titulo_cap1.png"), imagen=True),
        segmento(tmp, 3, 3.0, os.path.join(CLIPS, "cap1_t1_closet.mp4"), filtro=FRIO,
                 capas=[(ov.titulo(["caso n°1", "blusa colomba"], ov.H * 0.13, tam=56), 0.1, 3.0),
                        (subtitulo(["Bueno, técnicamente,", "me la pidieron prestada."]), 0.2, 3.0)]),
        segmento(tmp, 4, 5.7, os.path.join(CLIPS, "cap1_t2_cata_puerta.mp4"), filtro=CALIDO, velocidad=1.14,
                 capas=[(flash, 0.0, 5.7), (subtitulo(["30 de noviembre."]), 0.1, 1.2),
                        (subtitulo(["Mi hermana me pidió mi blusa Colomba,", "solo para el asado",
                                    "de fin de año de la pega."]), 1.3, 5.7)]),
        segmento(tmp, 5, 2.6, os.path.join(CLIPS, "cap1_t3_asado_ramazzotti.mp4"), filtro=CALIDO,
                 capas=[(flash, 0.0, 2.6), (subtitulo(["Eso fue hace 48 horas…"]), 0.2, 2.6)]),
        segmento(tmp, 6, 5.0, os.path.join(CLIPS, "cap1_t4_amigo_secreto.mp4"), filtro=CALIDO,
                 capas=[(flash, 0.0, 5.0),
                        (subtitulo(["Menos mal su amigo secreto", "le regaló una Gift Card de Aurelia…"]), 0.2, 3.35),
                        (subtitulo(["¡A ver si así me devuelve la mía!"]), 3.35, 5.0)]),
        segmento(tmp, 7, 4.5, D, inicio=0.5, filtro=FRIO,
                 capas=[(ov.titulo(["unidad aurelia", "caso abierto"], ov.H * 0.80, tam=62), 0.3, 4.5)]),
    ]
    fin = os.path.join(tmp, "fin.png")
    ov.overlays(os.path.join(tmp, "ov"))
    os.replace(os.path.join(tmp, "ov", "fin.png"), fin)
    segs.append(segmento(tmp, 8, 4.0, fin, imagen=True))
    v = os.path.join(VOZ, "final_cap1_G.mp3")
    voces = [
        (v, 0.0, 0.75, 0.3),     # Me robaron.
        (v, 1.05, 3.65, 3.7),    # Bueno, técnicamente, me la pidieron prestada.
        (v, 5.30, 6.40, 6.6),    # Treinta de noviembre.
        (v, 7.05, 11.60, 7.8),   # Mi hermana me pidió ... de la pega.
        (v, 12.05, 14.30, 12.4), # Eso fue hace cuarenta y ocho horas.
        # frase regenerada aparte (la toma original repetía "Gift Card")
        (os.path.join(VOZ, "frase_giftcard_B.mp3"), 0.0, 3.25, 15.0),   # Menos mal ... Gift Card de Aurelia.
        (os.path.join(VOZ, "frase_giftcard_B.mp3"), 3.62, 5.25, 18.2),  # ¡A ver si así me devuelve la mía!
        (v, 23.10, 25.50, 20.2), # Unidad Aurelia: caso abierto. (21.0-22.6 es el "a ver si así..." viejo: no usar)
        (os.path.join(VOZ, "final_cierre_G.mp3"), 0, 3.5, 24.6),
    ]
    return unir(tmp, segs, voces, "capitulo1_final.mp4")


if __name__ == "__main__":
    pieza = sys.argv[1] if len(sys.argv) > 1 else "cap1"
    with tempfile.TemporaryDirectory() as tmp:
        print({"adelanto": adelanto, "cap1": cap1}[pieza](tmp))
