# Traspaso de cambios locales — Medalla del Score (app Flutter)

> **Qué es esto.** En el ordenador A construimos el widget de la **Medalla del Score
> de Fuerza** en la app Flutter, pero **NO se ha pusheado** (sigue en local). Esta
> guía sirve para recrear esos cambios en el ordenador B sin perder nada.
>
> **Repo destino:** la app Automática → en el ordenador B se llama **`elmetodo_app-auto`**
> (`…/workspace/elmetodo_app-auto`). En el ordenador A se llamaba `elmetodo_app`.

---

## Archivos afectados (solo 3)

| Archivo | Cambio |
|---|---|
| `lib/core/widgets/score/puntuacion_medalla.dart` | **NUEVO** — el widget de la medalla |
| `lib/features/dev_tools/presentation/screens/design_system_screen.dart` | **MODIFICADO** — añade una sección "Puntuación — Medalla" a la galería del Design System |
| `lib/core/router/app_router.dart` | **MODIFICADO (⚠️ HACK TEMPORAL)** — abre la app directamente en la galería para previsualizar. **Hay que revertirlo antes de cualquier PR.** |

---

## Vía rápida: aplicar el parche

En el ordenador B, desde la raíz del repo de la app:

```bash
cd ~/.../workspace/elmetodo_app-auto

# 1. Comprobar que el parche encaja (no aplica nada, solo verifica)
git apply --check /ruta/a/medalla.patch

# 2. Si no da error, aplicarlo
git apply /ruta/a/medalla.patch
```

El `medalla.patch` está junto a este archivo (en el repo de docs `elmetodo-automatica`,
carpeta `traspaso-cambios-locales/`).

- Si `--check` **no da error** → aplica y listo. Verás los 3 archivos como cambios locales.
- Si `--check` **da error** (porque el código base difiere) → usa el **Plan B** de abajo.

---

## Plan B: aplicar a mano

### 1. Crear el archivo nuevo `lib/core/widgets/score/puntuacion_medalla.dart`

Con este contenido exacto:

```dart
import 'package:flutter/material.dart';

/// Niveles del Score de Fuerza. Determinan el color del aro de la medalla.
enum ScoreLevel { principiante, novato, experimentado, pro, atleta, elite, olimpico }

/// Gradientes del aro por nivel. Spec exacta de Figma (EMP DS · `Medalla-Puntuacion`).
const Map<ScoreLevel, List<Color>> _medalGradients = {
  ScoreLevel.principiante: [Color(0xFFD6DAE1), Color(0xFFAAB0BB), Color(0xFF5E6571), Color(0xFFC2C7D0), Color(0xFF868D99)],
  ScoreLevel.novato: [Color(0xFFC9F7F0), Color(0xFF5FD6C8), Color(0xFF138B7F), Color(0xFFAEF0E6), Color(0xFF2BB0A3)],
  ScoreLevel.experimentado: [Color(0xFFCFE4FF), Color(0xFF6FA9F5), Color(0xFF1E5FBF), Color(0xFFBCD6FF), Color(0xFF3D8BF0)],
  ScoreLevel.pro: [Color(0xFFDDD2FF), Color(0xFFA98FFF), Color(0xFF5436C4), Color(0xFFCBBCFF), Color(0xFF7C5CFF)],
  ScoreLevel.atleta: [Color(0xFFF6D2F4), Color(0xFFDB86D6), Color(0xFF9C2AA6), Color(0xFFEFBCEC), Color(0xFFC44AD0)],
  ScoreLevel.elite: [Color(0xFFFFE2C2), Color(0xFFF5B06A), Color(0xFFC26A18), Color(0xFFFFD6A8), Color(0xFFF0913C)],
  ScoreLevel.olimpico: [Color(0xFFFFF0C2), Color(0xFFF5D76A), Color(0xFFC29618), Color(0xFFFBEAA6), Color(0xFFF4C63D)],
};

/// Gris apagado para el estado sin datos ("?").
const List<Color> _unknownGradient = [
  Color(0xFF6B7280), Color(0xFF4B5563), Color(0xFF374151), Color(0xFF6B7280), Color(0xFF4B5563),
];

const List<double> _gradientStops = [0.0, 0.32, 0.55, 0.75, 1.0];

// Colores internos (literal de Figma; pendiente de mapear a tokens del tema).
const Color _kInnerFill = Color(0xFF0E1116);
const Color _kInnerStroke = Color(0xFFC9CED6);
const Color _kNumberColor = Color(0xFFF2F2F7);

/// Medalla circular del Score de Fuerza: aro con gradiente según el nivel,
/// círculo interior oscuro y el número del score (o "?" si no hay datos).
///
/// Componente presentacional puro: recibe `score` y `level` por parámetro.
/// `size` por defecto 150 (tamaño del componente en Figma); el resto se escala.
class PuntuacionMedalla extends StatelessWidget {
  final int? score;
  final ScoreLevel? level;
  final double size;

  const PuntuacionMedalla({
    super.key,
    required this.score,
    this.level,
    this.size = 150,
  });

  @override
  Widget build(BuildContext context) {
    final bool isUnknown = score == null || level == null;
    final List<Color> gradient = isUnknown ? _unknownGradient : _medalGradients[level]!;

    // Proporciones respecto al diseño de 150px (aro 112, interior 84, núm 38…).
    final double ringSize = size * (112 / 150);
    final double ringStroke = size * (8 / 150);
    final double ringRadius = ringSize * (44 / 112);
    final double innerSize = size * (84 / 150);
    final double innerRadius = innerSize * (34 / 84);
    final double innerStroke = size * (3 / 150);
    final double fontSize = size * (38 / 150);

    return SizedBox(
      width: size,
      height: size,
      child: Center(
        child: SizedBox(
          width: ringSize,
          height: ringSize,
          child: CustomPaint(
            painter: _GradientRingPainter(
              colors: gradient,
              stops: _gradientStops,
              strokeWidth: ringStroke,
              radius: ringRadius,
            ),
            child: Center(
              child: Container(
                width: innerSize,
                height: innerSize,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: _kInnerFill,
                  borderRadius: BorderRadius.circular(innerRadius),
                  border: Border.all(color: _kInnerStroke, width: innerStroke),
                ),
                child: Text(
                  isUnknown ? '?' : '$score',
                  style: TextStyle(
                    color: _kNumberColor,
                    fontSize: fontSize,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// Pinta el aro (squircle) con un gradiente lineal diagonal como borde.
class _GradientRingPainter extends CustomPainter {
  final List<Color> colors;
  final List<double> stops;
  final double strokeWidth;
  final double radius;

  _GradientRingPainter({
    required this.colors,
    required this.stops,
    required this.strokeWidth,
    required this.radius,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final Rect rect = Offset.zero & size;
    final Paint paint = Paint()
      ..shader = LinearGradient(
        colors: colors,
        stops: stops,
        begin: Alignment.topLeft, // gradiente diagonal ~45° (spec Figma)
        end: Alignment.bottomRight,
      ).createShader(rect)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth;

    // El stroke se dibuja centrado en el borde: encogemos media anchura.
    final double inset = strokeWidth / 2;
    final RRect rrect = RRect.fromRectAndRadius(
      Rect.fromLTWH(inset, inset, size.width - strokeWidth, size.height - strokeWidth),
      Radius.circular(radius),
    );
    canvas.drawRRect(rrect, paint);
  }

  @override
  bool shouldRepaint(_GradientRingPainter old) =>
      old.colors != colors || old.strokeWidth != strokeWidth || old.radius != radius;
}
```

### 2. Editar `design_system_screen.dart`

**a)** Añadir el import al principio (junto a los otros imports):

```dart
import '../../../../core/widgets/score/puntuacion_medalla.dart';
```

**b)** Dentro del `build`, justo **antes** de la línea `_section('Colors', _buildColorPalette(colors)),`
añadir esta sección:

```dart
                  _section(
                    'Puntuación — Medalla',
                    Wrap(
                      spacing: 16,
                      runSpacing: 16,
                      children: [
                        for (final m in const [
                          (25, ScoreLevel.principiante, 'Principiante'),
                          (75, ScoreLevel.novato, 'Novato'),
                          (125, ScoreLevel.experimentado, 'Experimentado'),
                          (175, ScoreLevel.pro, 'Pro'),
                          (225, ScoreLevel.atleta, 'Atleta'),
                          (275, ScoreLevel.elite, 'Élite'),
                          (320, ScoreLevel.olimpico, 'Olímpico'),
                        ])
                          Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              PuntuacionMedalla(score: m.$1, level: m.$2, size: 88),
                              const SizedBox(height: 4),
                              Text(m.$3, style: TextStyle(color: colors.textSecondary, fontSize: 12)),
                            ],
                          ),
                        Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const PuntuacionMedalla(score: null, level: null, size: 88),
                            const SizedBox(height: 4),
                            Text('Sin datos', style: TextStyle(color: colors.textSecondary, fontSize: 12)),
                          ],
                        ),
                      ],
                    ),
                  ),
```

### 3. Editar `app_router.dart` — ⚠️ HACK TEMPORAL para previsualizar

> **Esto es solo para poder ver la galería rápido en local. NO debe llegar a una PR.**
> Apunta esto para **revertirlo** después.

**a)** Cambiar la línea de `initialLocation`:

```dart
// ANTES:
    initialLocation: AppRoutes.home,
// DESPUÉS:
    initialLocation: AppRoutes.designSystem, // [TEMP dev] previsualizar componentes
```

**b)** Dentro de la función `redirect`, justo después de `final currentPath = state.matchedLocation;`,
añadir:

```dart
      // [TEMP dev] permitir la galería del Design System sin redirecciones.
      if (currentPath == AppRoutes.designSystem) return null;
```

---

## Ver el resultado en local

Con los cambios aplicados, arrancar la app (ver guía `compilar-app-en-local.md`):

```bash
flutter run --dart-define=APP_ENV=development
```

La app abrirá directamente en la galería del Design System y verás la fila de
**medallas** (7 niveles + "Sin datos"). Para iterar, edita y pulsa `r` (hot reload).

---

## ⚠️ Antes de hacer cualquier PR

**Revertir el hack de `app_router.dart`** (los dos cambios `[TEMP dev]`): dejar
`initialLocation: AppRoutes.home` y quitar la línea del `return null`. El widget de
la medalla y la sección de la galería **sí** se quedan.
