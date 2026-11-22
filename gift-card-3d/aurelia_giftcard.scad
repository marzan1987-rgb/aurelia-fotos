// Gift Card Aurelia Tienda — formato para impresión 3D (FDM)
// Tamaño tarjeta de crédito: 85,6 x 54 mm. Dos colores:
//   BASE   (fucsia Aurelia)  : 0 a 1,6 mm
//   RELIEVE (blanco o dorado): 1,6 a 2,2 mm  -> logo, borde, textos y monto
// Impresora multicolor: exportar part="base" y part="relieve" y cargarlos
// como un solo objeto de dos partes. Impresora de un color: imprimir
// part="todo" y cambiar el filamento (pausa) en la capa de 1,6 mm.

part   = "todo";      // "base" | "relieve" | "todo"
monto  = "$30.000";   // texto del monto
$fn    = 64;

W = 85.6; H = 54; R = 3.5;     // tarjeta
BASE = 1.6;  REL = 0.6;        // espesores
GRABADO = 0.4;                 // profundidad grabados del reverso
AGUJERO = [8, 46]; D_AG = 4.5; // agujero para la cinta del regalo

module redondeado(w, h, r) {
    offset(r = r) offset(delta = -r) square([w, h]);
}

// ---------- 2D del relieve frontal ----------
module logo2d() {
    // logo vectorizado del original; se engrosa para que la boquilla 0,4 lo imprima
    // el SVG importado mide 501,85 x 161,04 unidades; se centra y se lleva a 56 mm
    translate([W/2, 31.5])
        offset(r = 0.3)
            scale(56 / 501.85)
                translate([-501.85/2, -161.04/2])
                    import("logo_aurelia.svg");
}
module borde2d() {
    difference() {
        redondeado(W - 5, H - 5, R - 1);
        offset(delta = -0.8) redondeado(W - 5, H - 5, R - 1);
    }
}
module relieve2d() {
    logo2d();
    translate([2.5, 2.5]) borde2d();
    // anillo alrededor del agujero de la cinta
    translate(AGUJERO) difference() { circle(d = D_AG + 2.4); circle(d = D_AG); }
    translate([8, 8.2])
        text("GIFT CARD", size = 3.4, font = "Liberation Sans:style=Bold", spacing = 1.25);
    translate([W - 8, 7.6])
        text(monto, size = 6.2, font = "Liberation Sans:style=Bold", halign = "right");
}

// ---------- 2D de los grabados del reverso (en espejo) ----------
module reverso2d() {
    mirror([1, 0])  translate([-W, 0]) {
        translate([W/2, 33])
            text("aureliatienda.cl", size = 4.2, font = "Liberation Sans:style=Bold", halign = "center");
        translate([W/2, 26])
            text("Canjeable en tienda online", size = 2.8, font = "Liberation Sans", halign = "center");
    }
    // bolsillo para pegar el sticker con el código único
    translate([W/2 - 20, 9]) square([40, 9]);
}

// ---------- 3D ----------
module base3d() {
    difference() {
        linear_extrude(BASE) redondeado(W, H, R);
        translate([AGUJERO[0], AGUJERO[1], -1]) cylinder(d = D_AG, h = BASE + 2);
        translate([0, 0, -0.01]) linear_extrude(GRABADO + 0.01) reverso2d();
    }
}
module relieve3d() {
    translate([0, 0, BASE]) linear_extrude(REL)
        intersection() {
            relieve2d();
            difference() {
                offset(delta = -1.2) redondeado(W, H, R);
                translate(AGUJERO) circle(d = D_AG);
            }
        }
}

if (part == "base")    base3d();
if (part == "relieve") relieve3d();
if (part == "todo") {
    color("#E6005C") base3d();
    color("#FFFFFF") relieve3d();
}
