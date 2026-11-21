# Mini estudio casero para ropa — Solución mínima factible

**Espacio:** pieza de 3,5 m × 2,3 m (se asume techo ~2,4 m).
**Producto:** ropa. **Modelo:** la dueña de la tienda, que además dispara las fotos.

El estudio tiene **dos estaciones** que comparten luces:

| Estación | Para qué | Dónde |
|---|---|---|
| A. Modelo | Foto principal (la que vende) | Fondo en muro corto |
| B. Prenda plana (*flat lay*) | Detalle + **toma automática de medidas** | En el piso, cámara cenital |

---

## 1. Decisiones

- **Fondo: blanco roto o gris claro, no verde.** El verde se refleja en piel, pelo y telas claras, y una prenda verde desaparece al recortar. Un gris claro / blanco roto se ve limpio, no necesita luces extra para "quemarlo" a blanco y se puede aclarar en edición.
- **Modelo + prenda sola, las dos.** La foto con modelo convierte mejor (muestra caída, largo y calce). La prenda plana muestra detalle y sirve para medir. Mínimo por producto: 2–3 fotos con modelo + 1 plana.
- **Todo fijo con cinta en el piso:** posición de la modelo, luces y trípode. La consistencia entre productos importa más que el equipo.

---

## 2. Estación A — Modelo (cuerpo entero)

```
          MURO CORTO (2,3 m)
 ┌─────────────────────────────────┐
 │▒▒▒▒▒ FONDO GRIS/BLANCO ~2 m ▒▒▒▒│  0,0 m  (baja y cubre el piso ~1 m)
 │                                 │
 │              (X) modelo         │  0,9–1,0 m
 │  [L1] key 45°                   │
 │                       [rebote]  │  1,6 m
 │                                 │
 │            [CELULAR]            │  2,8–3,0 m  lente 1x, altura ~cintura
 │            (trípode)            │
 └─────────────────────────────────┘  3,5 m
```

- Con el lente **1x** del celular y el trípode a ~2 m de la modelo, entra el cuerpo entero en vertical. **No usar 2x/3x:** no alcanza la distancia de la pieza.
- Cámara a la **altura de la cintura**, perfectamente vertical → menos deformación (piernas no se acortan).
- **Auto-disparo:** control remoto Bluetooth o la app del celular desde un reloj/segundo teléfono, en ráfaga. Marcar con cinta dónde pararse.
- Poses fijas para todo el catálogo: frente, 3/4, espalda, detalle en movimiento.

## 3. Estación B — Prenda plana + medidas

- Superficie mate de **color que contraste** con la prenda (gris medio sirve para casi todo; tener una blanca y una oscura para prendas extremas).
- Celular **cenital** (mirando recto al piso) a **1,3–1,5 m** de altura: trípode con brazo horizontal o soporte cenital. Más alto = menos error de perspectiva.
- **4 marcadores impresos** (tipo ArUco, gratis) en las esquinas del área, de tamaño conocido → dan la escala px→cm y corrigen la inclinación.
- La prenda se extiende siempre igual: estirada sin tensionar, mangas abiertas en ángulo fijo, cierres cerrados.

---

## 4. Lista de compras (mínimo factible)

Precios referenciales en CLP. Verificar al comprar.

| # | Ítem | Especificación mínima | Ref. CLP |
|---|------|----------------------|---------:|
| 1 | Fondo | Papel continuo o tela mate gris claro / blanco roto, ~1,35–2 m de ancho | 25.000 – 45.000 |
| 2 | Soporte de fondo | Kit telescópico 2 × 2 m + pinzas | 25.000 – 40.000 |
| 3 | 2 luces LED con softbox | Luz continua, **5.500 K, CRI ≥ 95**, softbox ≥ 50×70 cm | 45.000 – 75.000 |
| 4 | Trípode con brazo horizontal | Altura ≥ 1,6 m, sirve para modelo y cenital | 25.000 – 50.000 |
| 5 | Control remoto Bluetooth | Para auto-disparo | 3.000 – 8.000 |
| 6 | Rebotador | Foam / cartulina blanca grande | 2.000 – 5.000 |
| 7 | Superficie flat lay + marcadores | Cartón/goma EVA gris + 4 marcadores impresos | 5.000 – 10.000 |
| | **Total aprox.** | | **~130.000 – 230.000** |

---

## 5. Automatización de la tabla de medidas

**Es factible.** Cómo funciona:

1. Foto cenital de la prenda plana con los 4 marcadores visibles.
2. Script detecta los marcadores → corrige perspectiva y calcula cm por píxel.
3. Separa la prenda del fondo (por contraste).
4. Mide según tipo de prenda: largo total, ancho de pecho (axila a axila), hombros, largo de manga, cintura, cadera, tiro, largo de pierna.
5. Genera la fila de la tabla (CSV) lista para la tienda. Los contornos se publican como ancho plano × 2.

Dos niveles:
- **Semiautomático (recomendado para partir):** el script corrige y escala la foto; la usuaria marca 2 puntos por medida con clics. Rápido, confiable, ±0,5–1 cm.
- **Automático:** el script encuentra los puntos solo con reglas por tipo de prenda (p. ej. pecho = ancho a 2,5 cm bajo la axila). Funciona bien en poleras, polerones y pantalones; falla más en prendas con volados, escotes o telas muy blandas → siempre revisar.

Precisión: depende de que la cámara esté cenital, la prenda bien extendida y los marcadores en el mismo plano. Para tallas, ±1 cm es aceptable.

---

## 6. Flujo por producto

1. Estación B: extender prenda → foto cenital → medidas automáticas → revisar.
2. Estación A: vestirse → 3–4 poses con remoto.
3. Edición: recorte/limpieza de fondo, mismo balance de blancos, exportar **4:5 o 1:1**, mismo encuadre.
4. Subir fotos + tabla de medidas a la tienda.

## 7. Checklist

- [ ] Comprar ítems 1–7
- [ ] Montar fondo en muro corto, marcar posiciones con cinta
- [ ] Imprimir marcadores y armar superficie flat lay
- [ ] Prueba con 3 prendas: fotos + medidas manuales con huincha para comparar
- [ ] Construir script de medidas (semiautomático) y validar contra la huincha
