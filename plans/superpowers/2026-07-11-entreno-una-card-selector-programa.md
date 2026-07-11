# Entreno — Una card + selector de programa · Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar la pestaña "Entreno": sustituir el carrusel de programas + la card "Siguiente entreno" por (a) un header con el nombre del programa como título-dropdown + menú ⋮, (b) una barra de progreso de la semana con 3 estados, y (c) **una card héroe única, sin botón**, que muestra el entreno del día sobre la imagen del programa y se desliza entre los días de la semana actual.

**Architecture:** 100 % **frontend Flutter** (`elmetodo_app`). **Cero cambios de backend.** Todo sale de `GET /api/training/content`, que ya devuelve la estructura completa `phases → weeks → days` con el completado de cada día. El programa activo se elige **en local**; el progreso semanal se **calcula en local**.

**Tech Stack:** Flutter, Riverpod (`@riverpod`), go_router, golden/widget tests.

## Global Constraints

- **Repo:** `/Users/kataiturriaga/repos/elmetodo_app`. Rama: `ux/entreno-card-siguiente-v-b`.
- **CERO backend.** Si algo parece necesitar un endpoint nuevo, PARAR y consultar.
- **Tokens de diseño:** siempre `context.colors.<token>`, nunca hex. Espaciados `AppSpacing.sN`. Tipografía `AppTypography.*`. Barrel: `import '../../../../core/theme/theme.dart';`.
- **Localización:** todo texto vía `S.of(context)`, claves en `app_es.arb` **y** `app_en.arb`; regenerar con `flutter gen-l10n`.
- **"Terminar programa"** usa `archiveProgram(id)` (archiva, **conserva el progreso**). **NUNCA `unsubscribeFromProgram`** — es un borrado duro que destruye el progreso.
- **Tests:** cada widget lleva golden test siguiendo `test/features/training/next_training_card_preview_test.dart` (carga fuentes OpenSans + MaterialIcons en `setUpAll`, o los textos salen como cajas). Regenerar con `--update-goldens`.

## Decisiones de producto ya cerradas (no re-abrir)

| Tema | Decisión |
|---|---|
| **Botón "Entrenar"** | **NO existe.** La card entera es tocable. El tag comunica el estado. |
| **Semana** | Es la **semana del programa**, no la natural. No se resetea los lunes: avanza al completar sus días. Copy: "Semana N · X de N entrenos" (nunca "esta semana"). |
| **Deslizar** | Solo entre los días de la **semana actual**. Para ver el resto del programa → "Ver programa" (⋮). |
| **Reemplazar programa** | **Fuera de alcance.** Se consigue con Terminar + Añadir. |
| **Saltar un entreno** | **Fuera de alcance.** Requeriría backend. Quien quiera avanzar, marca el entreno como completado. |
| **Duración del entreno** | **No se muestra.** El dato NO existe en el backend. No inventarlo. |
| **Título de la card** | El campo `name` del día ("Tren superior"). **NO usar `training_type`**: contiene una lista larga de músculos ("Pecho, espalda, hombros…") que no cabe. |
| **Días opcionales** | Kata los está limpiando del contenido (tarea aparte). No hacer nada en la app. |

---

## Mapa de archivos

**Ya hecho (fuera de las tareas):**
- ✅ `lib/core/theme/app_colors.dart` — añadido `AppColors.orange500` (#E88710) y el token semántico `context.colors.warning` (naranja en **ambos** temas; en Figma el modo claro está mal puesto en blanco). Test: `test/core/warning_token_test.dart`.

**Nuevos:**
- `lib/features/training/presentation/providers/current_week_provider.dart` — `selectedCurrentWeekProvider` (`TrainingWeek?`) + `selectedDayIndexProvider` (`StateProvider<int>`).
- `lib/features/training/presentation/widgets/program_selector_button.dart` — título-programa con dropdown.
- `lib/features/training/presentation/widgets/program_actions_menu.dart` — kebab ⋮ (Ver programa / Terminar programa).
- `lib/features/training/presentation/widgets/program_header_row.dart` — compone selector + kebab.
- `lib/features/training/presentation/widgets/weekly_progress_bar.dart` — barra con 3 estados.
- `lib/features/training/presentation/widgets/next_workout_card.dart` — la card héroe (4 tags, **sin botón**).
- `lib/features/training/presentation/widgets/week_days_pager.dart` — el carrusel de días + dots.
- `lib/core/widgets/common/end_program_dialog.dart` — `showEndProgramDialog`.

**Modificados:**
- `lib/features/training/presentation/screens/main_entreno_screen.dart` — `_ProgramsTab` (L206–275).
- `lib/l10n/app_es.arb`, `lib/l10n/app_en.arb`.

**Se conservan:** `SegmentedTabBar` (tab Entreno/Seguimiento), `MarcasSection` ("Tus marcas"), `_EmptyProgramsTab`, `ProgramCompletedCard`, `_LoadingState`, `_ErrorState`.

**Quedan sin uso** (NO borrar en este plan): `active_programs_section.dart`, `next_training_card.dart`.

---

## Anatomía de la pantalla final

```
[ Entreno | Seguimiento ]          ← tab bar (existente, NO tocar)
Masa magra - 4 días  ▾       ⋮     ← Task 7
▓▓░░   Semana 1 · 2 de 4 entrenos  ← Task 3
┌───────────────────────────┐
│ [TAG]                     │      ← Task 8 + 9 (carrusel de días)
│                           │        card ENTERA tocable, SIN botón
│  Tren superior            │
│  7 ejercicios             │
└───────────────────────────┘
        • • ● •                     ← dots del carrusel
Tus marcas (chips + gráfica)       ← existente, NO tocar
```

---

### Task 1: Providers de la semana actual y del día seleccionado

**Files:**
- Create: `lib/features/training/presentation/providers/current_week_provider.dart`
- Test: `test/features/training/current_week_provider_test.dart`

**Interfaces:**
- Consumes: `selectedSubscriptionProvider` → `SubscriptionDetail?` (`training_providers.dart:294`); entidades `SubscriptionDetail`, `ProgramPhase`, `TrainingWeek`, `TrainingDay`.
- Produces:
  - `selectedCurrentWeekProvider` → `TrainingWeek?` — la primera semana (recorriendo `phases → weeks`) con algún día `!isCompleted`. Si todo está completo → la última. Si no hay datos → `null`.
  - `selectedDayIndexProvider` → `StateProvider<int>` — índice del día que el carrusel está mostrando, dentro de `currentWeek.days`. Arranca en el primer día no completado (o 0).
  - `initialDayIndexProvider` → `Provider<int>` — el índice inicial calculado (primer día sin completar de la semana, o 0 si todos hechos).

- [ ] **Step 1: Escribir el test que falla**

```dart
// test/features/training/current_week_provider_test.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:elmetodo_app/features/training/domain/entities/subscription_detail.dart';
import 'package:elmetodo_app/features/training/domain/entities/training_location.dart';
import 'package:elmetodo_app/features/training/presentation/providers/training_providers.dart';
import 'package:elmetodo_app/features/training/presentation/providers/current_week_provider.dart';

TrainingDay _day(int id, {required bool done}) =>
    TrainingDay(id: id, dayOrder: id, name: 'Día $id', isCompleted: done);

SubscriptionDetail _sub(List<TrainingWeek> weeks) => SubscriptionDetail(
      id: 1, programId: 1, programName: 'Masa magra',
      location: TrainingLocation.gym, zones: const [],
      completedDays: 0, totalDays: 4,
      enrolledAt: DateTime(2026, 1, 1), isActive: true, isCompleted: false,
      phases: [ProgramPhase(
        id: 1, phaseOrder: 1, name: 'F1',
        totalWeeks: weeks.length, completedWeeks: 0, weeks: weeks)],
    );

void main() {
  test('la semana actual es la que tiene el primer día sin completar', () {
    final w1 = TrainingWeek(weekNumber: 1, days: [_day(1, done: true), _day(2, done: true)]);
    final w2 = TrainingWeek(weekNumber: 2, days: [_day(3, done: false), _day(4, done: false)]);
    final c = ProviderContainer(overrides: [
      selectedSubscriptionProvider.overrideWith((ref) => _sub([w1, w2])),
    ]);
    addTearDown(c.dispose);
    expect(c.read(selectedCurrentWeekProvider)?.weekNumber, 2);
  });

  test('si todo está completo, devuelve la última semana', () {
    final w1 = TrainingWeek(weekNumber: 1, days: [_day(1, done: true)]);
    final w2 = TrainingWeek(weekNumber: 2, days: [_day(2, done: true)]);
    final c = ProviderContainer(overrides: [
      selectedSubscriptionProvider.overrideWith((ref) => _sub([w1, w2])),
    ]);
    addTearDown(c.dispose);
    expect(c.read(selectedCurrentWeekProvider)?.weekNumber, 2);
  });

  test('sin subscripción devuelve null', () {
    final c = ProviderContainer(overrides: [
      selectedSubscriptionProvider.overrideWith((ref) => null),
    ]);
    addTearDown(c.dispose);
    expect(c.read(selectedCurrentWeekProvider), isNull);
  });

  test('el día inicial es el primero sin completar de la semana', () {
    final w = TrainingWeek(weekNumber: 1, days: [
      _day(1, done: true), _day(2, done: true), _day(3, done: false), _day(4, done: false),
    ]);
    final c = ProviderContainer(overrides: [
      selectedSubscriptionProvider.overrideWith((ref) => _sub([w])),
    ]);
    addTearDown(c.dispose);
    expect(c.read(initialDayIndexProvider), 2); // índice 2 = tercer día
  });

  test('si la semana está entera hecha, el día inicial es 0', () {
    final w = TrainingWeek(weekNumber: 1, days: [_day(1, done: true), _day(2, done: true)]);
    final c = ProviderContainer(overrides: [
      selectedSubscriptionProvider.overrideWith((ref) => _sub([w])),
    ]);
    addTearDown(c.dispose);
    expect(c.read(initialDayIndexProvider), 0);
  });
}
```

> Verificar los parámetros `required` reales de `SubscriptionDetail` / `ProgramPhase` / `TrainingWeek` / `TrainingDay` en `domain/entities/subscription_detail.dart` y ajustar el fixture. Si `selectedSubscriptionProvider` es generado, comprobar la firma correcta de `overrideWith`.

- [ ] **Step 2: Ejecutar el test y ver que falla**

Run: `cd /Users/kataiturriaga/repos/elmetodo_app && flutter test test/features/training/current_week_provider_test.dart`
Expected: FAIL — `current_week_provider.dart` no existe.

- [ ] **Step 3: Implementar**

```dart
// lib/features/training/presentation/providers/current_week_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/subscription_detail.dart';
import 'training_providers.dart';

/// La "semana actual" del PROGRAMA (no la natural): la primera semana,
/// recorriendo phases → weeks en orden, que tiene algún día sin completar.
/// Si todas están completas devuelve la última. Null si no hay datos.
///
/// Ojo: no avanza por calendario. Avanza cuando se completan los días.
final selectedCurrentWeekProvider = Provider<TrainingWeek?>((ref) {
  final sub = ref.watch(selectedSubscriptionProvider);
  if (sub == null) return null;

  TrainingWeek? last;
  for (final phase in sub.phases) {
    for (final week in phase.weeks) {
      last = week;
      if (week.days.any((d) => !d.isCompleted)) return week;
    }
  }
  return last;
});

/// Índice, dentro de la semana actual, del primer día sin completar
/// (= el "próximo entreno"). Si la semana está entera hecha → 0.
///
/// Cambia solo cuando cambian los DATOS (al completar un entreno, al cambiar
/// de programa). No cambia al deslizar el carrusel.
final initialDayIndexProvider = Provider<int>((ref) {
  final week = ref.watch(selectedCurrentWeekProvider);
  if (week == null || week.days.isEmpty) return 0;
  final i = week.days.indexWhere((d) => !d.isCompleted);
  return i < 0 ? 0 : i;
});

/// Día que el carrusel muestra ahora mismo. Lo escribe SOLO el PageView
/// (`onPageChanged`) y el propio pager cuando se reposiciona.
///
/// ⚠️ Es un StateProvider PURO a propósito: NO debe hacer `ref.watch` de
/// `initialDayIndexProvider`. Si lo hiciera, se reiniciaría solo al recargarse
/// los datos y quedaría desincronizado del PageController (que no se entera).
/// La sincronización se hace explícitamente en [WeekDaysPager] con `ref.listen`.
final selectedDayIndexProvider = StateProvider<int>((ref) => 0);
```

- [ ] **Step 4: Ejecutar y ver que pasa**

Run: `flutter test test/features/training/current_week_provider_test.dart`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add lib/features/training/presentation/providers/current_week_provider.dart test/features/training/current_week_provider_test.dart
git commit -m "feat(entreno): providers de semana actual y dia seleccionado"
```

---

### Task 2: Textos (localización)

**Files:** Modify `lib/l10n/app_es.arb`, `lib/l10n/app_en.arb`

**Interfaces:**
- Produces (getters en `S`): `viewProgram`, `endProgram`, `addProgram`, `programWeekProgress(int week, int completed, int total)`, `tagNextWorkout`, `tagCompleted`, `tagInProgress`, `endProgramTitle`, `endProgramMessage(String programName)`, `endProgramConfirm`.
- Reutiliza los existentes: `exercise`, `exercises`, `days`, `cancel`.

- [ ] **Step 1: Añadir a `app_es.arb`**

```json
  "viewProgram": "Ver programa",
  "endProgram": "Terminar programa",
  "addProgram": "Añadir programa",
  "tagNextWorkout": "PRÓXIMO ENTRENO",
  "tagCompleted": "COMPLETADO",
  "tagInProgress": "EN CURSO",
  "programWeekProgress": "Semana {week} · {completed} de {total} entrenos",
  "@programWeekProgress": {
    "description": "Progreso de la SEMANA DEL PROGRAMA (no la natural). No se resetea por calendario.",
    "placeholders": { "week": {"type":"int"}, "completed": {"type":"int"}, "total": {"type":"int"} }
  },
  "endProgramTitle": "¿Terminar programa?",
  "endProgramMessage": "Guardaremos tu progreso de {programName} en el historial. Podrás volver a empezarlo cuando quieras.",
  "@endProgramMessage": {
    "placeholders": { "programName": {"type":"String"} }
  },
  "endProgramConfirm": "Terminar"
```

- [ ] **Step 2: Añadir a `app_en.arb`**

```json
  "viewProgram": "View program",
  "endProgram": "End program",
  "addProgram": "Add program",
  "tagNextWorkout": "NEXT WORKOUT",
  "tagCompleted": "COMPLETED",
  "tagInProgress": "IN PROGRESS",
  "programWeekProgress": "Week {week} · {completed} of {total} workouts",
  "@programWeekProgress": {
    "description": "PROGRAM week progress (not the calendar week). Does not reset on Mondays.",
    "placeholders": { "week": {"type":"int"}, "completed": {"type":"int"}, "total": {"type":"int"} }
  },
  "endProgramTitle": "End program?",
  "endProgramMessage": "We'll save your {programName} progress to your history. You can start it again anytime.",
  "@endProgramMessage": {
    "placeholders": { "programName": {"type":"String"} }
  },
  "endProgramConfirm": "End"
```

- [ ] **Step 3: Regenerar y comprobar**

Run: `flutter gen-l10n && flutter analyze lib/l10n`
Expected: sin errores; los getters nuevos existen.

- [ ] **Step 4: Commit**

```bash
git add lib/l10n/
git commit -m "i18n(entreno): textos del selector, tags y gestion de programa"
```

---

### Task 3: Barra de progreso de la semana (3 estados)

**Files:**
- Create: `lib/features/training/presentation/widgets/weekly_progress_bar.dart`
- Test: `test/features/training/weekly_progress_bar_preview_test.dart`

**Interfaces:**
- Consumes: `TrainingWeek` (`weekNumber`, `days`, `completedDays`, `totalDays`), `TrainingDay.isCompleted`, `S.programWeekProgress`.
- Produces: `class WeeklyProgressBar extends StatelessWidget` con
  `const WeeklyProgressBar({super.key, required this.week, required this.selectedDayIndex})`.

**🎨 Tres estados por casilla — el verde SIEMPRE gana:**

| Casilla | Token | Color (oscuro) |
|---|---|---|
| **Hecho** (`isCompleted`) — aunque esté seleccionada | `colors.brandPrimary` | `#00EE00` verde |
| **Seleccionada** y NO hecha | `colors.strokeStrong` | `#6B6D71` gris claro |
| **Pendiente** | `colors.strokeDivider` | `#3C3E41` gris oscuro |

Orden obligatorio: `isCompleted` → verde; si no, `index == selectedDayIndex` → gris claro; si no → gris oscuro.

- [ ] **Step 1: Implementar**

```dart
// lib/features/training/presentation/widgets/weekly_progress_bar.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/entities/subscription_detail.dart';

/// Progreso de la semana DEL PROGRAMA (no la natural). Una casilla por día.
/// No se resetea por calendario: avanza al completar los días.
class WeeklyProgressBar extends StatelessWidget {
  const WeeklyProgressBar({
    super.key,
    required this.week,
    required this.selectedDayIndex,
  });

  final TrainingWeek week;

  /// Índice, dentro de [week.days], del día que muestra el carrusel.
  final int selectedDayIndex;

  Color _segmentColor(BuildContext context, int index) {
    final colors = context.colors;
    // El verde manda: un día hecho sigue verde aunque esté seleccionado.
    if (week.days[index].isCompleted) return colors.brandPrimary;
    if (index == selectedDayIndex) return colors.strokeStrong;
    return colors.strokeDivider;
  }

  @override
  Widget build(BuildContext context) {
    final l10n = S.of(context);
    final colors = context.colors;
    final total = week.totalDays;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            for (int i = 0; i < total; i++) ...[
              Expanded(
                child: Container(
                  height: 5,
                  decoration: BoxDecoration(
                    color: _segmentColor(context, i),
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
              if (i < total - 1) const SizedBox(width: AppSpacing.s4),
            ],
          ],
        ),
        const SizedBox(height: AppSpacing.s8),
        Text(
          l10n.programWeekProgress(week.weekNumber, week.completedDays, total),
          style: AppTypography.bodySmall.copyWith(color: colors.textSecondary),
        ),
      ],
    );
  }
}
```

- [ ] **Step 2: Golden test** (copiar `_loadFonts` y `_pump` de `next_training_card_preview_test.dart`)

```dart
// test/features/training/weekly_progress_bar_preview_test.dart
TrainingWeek _week(int done, int total) => TrainingWeek(
      weekNumber: 1,
      days: List.generate(total,
        (i) => TrainingDay(id: i, dayOrder: i, name: 'D$i', isCompleted: i < done)),
    );

void main() {
  setUpAll(_loadFonts);

  final scenarios = <String, Widget>{
    // 2 verdes · la 3ª gris claro (seleccionada) · la 4ª gris oscuro
    'tres_estados': WeeklyProgressBar(week: _week(2, 4), selectedDayIndex: 2),
    // CLAVE: el día seleccionado ya está hecho → debe salir VERDE, no gris claro
    'hecho_y_seleccionado': WeeklyProgressBar(week: _week(3, 4), selectedDayIndex: 1),
    'todo_hecho': WeeklyProgressBar(week: _week(4, 4), selectedDayIndex: 3),
  };

  for (final e in scenarios.entries) {
    for (final theme in [ThemeMode.dark, ThemeMode.light]) {
      final t = theme == ThemeMode.dark ? 'dark' : 'light';
      testWidgets('weekly_progress ${e.key} $t', (tester) async {
        await _pump(tester,
            child: Padding(padding: const EdgeInsets.all(16), child: e.value),
            themeMode: theme);
        await expectLater(find.byType(WeeklyProgressBar),
            matchesGoldenFile('goldens/weekly_progress_${e.key}_$t.png'));
      });
    }
  }
}
```

- [ ] **Step 3: Generar y revisar a ojo**

Run: `flutter test test/features/training/weekly_progress_bar_preview_test.dart --update-goldens`
Expected: PASS (6). Abrir los PNG y confirmar:
- `tres_estados_dark` → 2 verdes, 1 gris claro, 1 gris oscuro. Texto "Semana 1 · 2 de 4 entrenos".
- `hecho_y_seleccionado_dark` → **3 verdes** (la 2ª está seleccionada pero hecha → verde). ← valida la regla.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/weekly_progress_bar.dart test/features/training/weekly_progress_bar_preview_test.dart test/features/training/goldens/weekly_progress_*.png
git commit -m "feat(entreno): barra de progreso semanal con tres estados"
```

---

### Task 4: Card del entreno (4 tags, SIN botón)

**Files:**
- Create: `lib/features/training/presentation/widgets/next_workout_card.dart`
- Test: `test/features/training/next_workout_card_preview_test.dart`

**Diseño:** Figma `NextWorkoutCard` (node `1275:3358`, EMP DS Library). Component set con eje `State`: `Default` / `NextSesion` / `Completed`. **El botón existe en el componente pero está oculto en todas las variantes** → no implementarlo. Añadimos un 4º estado `InProgress` (naranja) que aún no está en Figma.

**Interfaces:**
- Consumes: `SubscriptionDetail.programImageUrl`; `TrainingDay` (`displayName`, `totalExercises`, `isCompleted`, `hasAnyExerciseStarted`); `AnimatedNetworkImage`, `AppEffects.gradientBlack`; `S.tagNextWorkout/tagCompleted/tagInProgress/exercise/exercises`; `context.colors.warning` (ya añadido).
- Produces:
  ```dart
  enum WorkoutCardState { none, next, inProgress, completed }

  class NextWorkoutCard extends StatelessWidget {
    const NextWorkoutCard({
      super.key,
      required this.imageUrl,     // String? — imagen del programa
      required this.trainingDay,
      required this.state,
      required this.onTap,        // la card ENTERA es tocable
    });
  }
  ```

**Los 4 estados:**

| Estado | Tag | Color del tag | Cuándo |
|---|---|---|---|
| `completed` | COMPLETADO | verde `brandPrimary` | `day.isCompleted` |
| `inProgress` | EN CURSO | **naranja `warning`** | `!isCompleted && hasAnyExerciseStarted` |
| `next` | PRÓXIMO ENTRENO | verde `brandPrimary` | es el primer día sin completar de la semana |
| `none` | *(sin tag)* | — | el resto (días futuros de la semana) |

Prioridad al calcular: `completed` → `inProgress` → `next` → `none`.

- [ ] **Step 1: Implementar**

```dart
// lib/features/training/presentation/widgets/next_workout_card.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../core/widgets/images/animated_network_image.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/entities/subscription_detail.dart';

/// Estado visual de la card (lo comunica el tag; no hay botón).
enum WorkoutCardState { none, next, inProgress, completed }

/// Deriva el estado de un día. [isNext] = es el primer día sin completar
/// de la semana.
WorkoutCardState workoutCardStateFor(TrainingDay day, {required bool isNext}) {
  if (day.isCompleted) return WorkoutCardState.completed;
  if (day.hasAnyExerciseStarted) return WorkoutCardState.inProgress;
  if (isNext) return WorkoutCardState.next;
  return WorkoutCardState.none;
}

/// Card del entreno del día, sobre la imagen del programa.
///
/// NO tiene botón: la card entera es tocable (Figma: NextWorkoutCard, donde
/// el botón está oculto en todas las variantes). El tag comunica el estado.
class NextWorkoutCard extends StatelessWidget {
  const NextWorkoutCard({
    super.key,
    required this.imageUrl,
    required this.trainingDay,
    required this.state,
    required this.onTap,
  });

  final String? imageUrl;
  final TrainingDay trainingDay;
  final WorkoutCardState state;
  final VoidCallback onTap;

  ({String label, Color bg})? _tag(BuildContext context, S l10n) {
    final colors = context.colors;
    return switch (state) {
      WorkoutCardState.completed =>
        (label: l10n.tagCompleted, bg: colors.brandPrimary),
      WorkoutCardState.inProgress =>
        (label: l10n.tagInProgress, bg: colors.warning),
      WorkoutCardState.next =>
        (label: l10n.tagNextWorkout, bg: colors.brandPrimary),
      WorkoutCardState.none => null,
    };
  }

  @override
  Widget build(BuildContext context) {
    final l10n = S.of(context);
    final colors = context.colors;
    final count = trainingDay.totalExercises;
    final tag = _tag(context, l10n);

    return GestureDetector(
      onTap: onTap,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(AppSpacing.s16),
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (imageUrl != null)
              AnimatedNetworkImage(
                imageUrl: imageUrl!,
                fit: BoxFit.cover,
                errorWidget: Container(color: colors.bgSurface1),
              )
            else
              Container(color: colors.bgSurface1),

            Container(
              decoration: BoxDecoration(
                gradient: AppEffects.gradientBlack,
                backgroundBlendMode: BlendMode.multiply,
              ),
            ),

            // Tag (arriba-izquierda). Sin tag en el estado `none`.
            if (tag != null)
              Positioned(
                top: AppSpacing.s16,
                left: AppSpacing.s16,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.s16, vertical: AppSpacing.s6),
                  decoration: BoxDecoration(
                    color: tag.bg,
                    borderRadius: BorderRadius.circular(100),
                  ),
                  child: Text(
                    tag.label,
                    style: AppTypography.bodyXSmallBold.copyWith(
                      color: colors.brandText, // negro sobre verde/naranja
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ),

            // Contenido inferior: nombre del día + nº de ejercicios.
            // NO hay botón (decisión de diseño).
            Positioned(
              left: AppSpacing.s16,
              right: AppSpacing.s16,
              bottom: AppSpacing.s16,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    trainingDay.displayName,
                    style: AppTypography.bodyLarge.copyWith(
                      color: colors.brandTextInverse,
                      fontSize: 24,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: AppSpacing.s4),
                  Text(
                    '$count ${count == 1 ? l10n.exercise : l10n.exercises}',
                    style: AppTypography.bodySmall
                        .copyWith(color: colors.brandTextInverse),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

> Nota: el nombre del día viene de `displayName` (= `name`, p. ej. "Tren superior"). **No usar `trainingType`** (es una lista larga de músculos).

- [ ] **Step 2: Golden test — los 4 estados**

```dart
// test/features/training/next_workout_card_preview_test.dart
// (copiar _loadFonts / _pump; surface 390x340; imageUrl: null para render determinista)
TrainingDay _day({bool done = false, bool started = false}) => TrainingDay(
      id: 1, dayOrder: 1, name: 'Tren superior', isCompleted: done,
      exercises: List.generate(7, (i) => DayExercise(
        id: i, exerciseId: i, name: 'E$i', position: i,
        planType: 'strength', logType: 'weight_reps',
        completedSets: started ? 2 : null)),
    );

void main() {
  setUpAll(_loadFonts);
  final scenarios = {
    'next': (day: _day(), state: WorkoutCardState.next),
    'completed': (day: _day(done: true), state: WorkoutCardState.completed),
    'in_progress': (day: _day(started: true), state: WorkoutCardState.inProgress),
    'none': (day: _day(), state: WorkoutCardState.none),
  };
  for (final e in scenarios.entries) {
    testWidgets('next_workout_card ${e.key} dark', (tester) async {
      await _pump(tester,
          child: SizedBox(height: 300, child: NextWorkoutCard(
            imageUrl: null, trainingDay: e.value.day,
            state: e.value.state, onTap: () {})),
          themeMode: ThemeMode.dark);
      await expectLater(find.byType(NextWorkoutCard),
          matchesGoldenFile('goldens/workout_card_${e.key}.png'));
    });
  }
}
```

- [ ] **Step 3: Generar y revisar**

Run: `flutter test test/features/training/next_workout_card_preview_test.dart --update-goldens`
Expected: PASS (4). Revisar los PNG: tag verde en `next`/`completed`, **tag naranja en `in_progress`**, **sin tag** en `none`, y **ningún botón** en ninguno.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/next_workout_card.dart test/features/training/next_workout_card_preview_test.dart test/features/training/goldens/workout_card_*.png
git commit -m "feat(entreno): card del entreno con 4 tags y sin boton"
```

---

### Task 5: Carrusel de los días de la semana

**Files:**
- Create: `lib/features/training/presentation/widgets/week_days_pager.dart`
- Test: `test/features/training/week_days_pager_test.dart`

**Interfaces:**
- Consumes: `NextWorkoutCard` + `workoutCardStateFor` (Task 4); providers `selectedCurrentWeekProvider`, `selectedDayIndexProvider`, `initialDayIndexProvider`, `selectedSubscriptionProvider`; ruta `AppRoutes.trainingDay`.
- Produces: `class WeekDaysPager extends ConsumerStatefulWidget` — `const WeekDaysPager({super.key})`. Un `PageView` sobre `currentWeek.days` **solo de la semana actual**, arrancando en `initialDayIndexProvider`, con **dots debajo** (affordance: sin ellos el gesto es invisible). Al cambiar de página escribe `selectedDayIndexProvider`. Al tocar una card, navega al día.

- [ ] **Step 1: Implementar**

```dart
// lib/features/training/presentation/widgets/week_days_pager.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/theme/theme.dart';
import '../../domain/entities/subscription_detail.dart';
import '../providers/current_week_provider.dart';
import '../providers/training_providers.dart';
import 'next_workout_card.dart';

/// Carrusel de los días de la SEMANA ACTUAL. No llega a otras semanas
/// (para eso está "Ver programa" en el menú ⋮).
class WeekDaysPager extends ConsumerStatefulWidget {
  const WeekDaysPager({super.key});

  @override
  ConsumerState<WeekDaysPager> createState() => _WeekDaysPagerState();
}

class _WeekDaysPagerState extends ConsumerState<WeekDaysPager> {
  PageController? _controller;

  /// Identidad del carrusel: (enrollment, semana, nº de días). Si cambia
  /// (p. ej. el usuario elige otro programa), se RECREA el PageController.
  ({int subId, int week, int dayCount})? _key;

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  /// Mueve el carrusel al día [target] y actualiza el provider, de forma que
  /// la barra de progreso y la card muestren SIEMPRE el mismo día.
  void _goTo(int target, {required bool animate}) {
    final c = _controller;
    if (c == null) return;
    if (animate && c.hasClients) {
      c.animateToPage(target,
          duration: const Duration(milliseconds: 350), curve: Curves.easeOutCubic);
    } else if (c.hasClients) {
      c.jumpToPage(target);
    }
    // Fuera del frame de build: el provider lo escribe el propio pager.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        ref.read(selectedDayIndexProvider.notifier).state = target;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final week = ref.watch(selectedCurrentWeekProvider);
    final sub = ref.watch(selectedSubscriptionProvider);
    if (week == null || week.days.isEmpty || sub == null) {
      return const SizedBox.shrink();
    }

    final initial = ref.watch(initialDayIndexProvider);
    final lastIndex = week.days.length - 1;

    // (1) Cambió el programa o la semana → recrear el controller desde cero.
    //     `??=` NO vale: el índice podría quedar fuera de rango si el programa
    //     nuevo tiene menos días.
    final key = (subId: sub.id, week: week.weekNumber, dayCount: week.days.length);
    if (_key != key) {
      _key = key;
      _controller?.dispose();
      _controller = PageController(
        initialPage: initial.clamp(0, lastIndex),
        viewportFraction: 1.0,
      );
      _goTo(initial.clamp(0, lastIndex), animate: false);
    }

    // (2) Cambió el "próximo entreno" SIN cambiar de semana → es el caso de
    //     completar un entreno y volver (training_day_screen.dart:62 invalida
    //     el contenido). El carrusel debe AVANZAR solo al nuevo próximo, o
    //     se queda mostrando un día distinto del que marca la barra.
    ref.listen<int>(initialDayIndexProvider, (prev, next) {
      if (prev == next) return;
      _goTo(next.clamp(0, lastIndex), animate: true);
    });

    final selected = ref.watch(selectedDayIndexProvider);
    // El "próximo" es el primer día sin completar de la semana.
    final nextIndex = week.days.indexWhere((d) => !d.isCompleted);

    return Column(
      children: [
        SizedBox(
          height: 300,
          child: PageView.builder(
            controller: _controller,
            itemCount: week.days.length,
            onPageChanged: (i) =>
                ref.read(selectedDayIndexProvider.notifier).state = i,
            itemBuilder: (context, i) {
              final day = week.days[i];
              return Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: AppSpacing.s16),
                child: NextWorkoutCard(
                  imageUrl: sub.programImageUrl,
                  trainingDay: day,
                  state: workoutCardStateFor(day, isNext: i == nextIndex),
                  onTap: () => _openDay(context, sub, week, day),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: AppSpacing.s8),
        // Dots: sin esto, nadie descubre que la card se desliza.
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(week.days.length, (i) {
            final isSel = i == selected;
            final isDone = week.days[i].isCompleted;
            return AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin: const EdgeInsets.symmetric(horizontal: 3),
              width: isSel ? 18 : 6,
              height: 6,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(4),
                color: isDone
                    ? context.colors.brandPrimary
                    : isSel
                        ? context.colors.strokeStrong
                        : context.colors.strokeDivider,
              ),
            );
          }),
        ),
      ],
    );
  }

  void _openDay(BuildContext context, SubscriptionDetail sub,
      TrainingWeek week, TrainingDay day) {
    context.push(AppRoutes.trainingDay, extra: {
      'trainingDay': day,
      'totalDaysInWeek': week.days.length,
      'subscriptionId': sub.id,
      'weekNumber': week.weekNumber,
    });
  }
}
```

- [ ] **Step 2: Widget test** (patrón de `marcas_section_test.dart`, con overrides)

```dart
// test/features/training/week_days_pager_test.dart
// ProviderScope(overrides: [selectedSubscriptionProvider, selectedCurrentWeekProvider...])
//
// 1. Arranque: se ve la card del primer día SIN completar; hay tantos dots
//    como días tiene la semana.
//
// 2. REGRESIÓN "completar un entreno" (el caso MÁS común):
//    Semana de 4 días con el día 3 (índice 2) como próximo.
//    Cambiar el override para que el día 3 pase a isCompleted: true
//    (simula volver de completarlo) y `await tester.pumpAndSettle()`.
//    → El carrusel debe haber AVANZADO al día 4 (índice 3), y
//      `selectedDayIndexProvider` debe valer 3.
//    → Barra y card deben coincidir. Antes del fix, el carrusel se quedaba
//      en el índice 2 mientras la barra marcaba el 3.
//
// 3. REGRESIÓN "cambiar de programa":
//    Sustituir la subscripción por otra con MENOS días (4 → 3) y re-pump.
//    → No debe lanzar excepción ni quedar fuera de rango; el carrusel se
//      recrea en el primer día sin completar del programa nuevo.
```

- [ ] **Step 3: Ejecutar**

Run: `flutter test test/features/training/week_days_pager_test.dart`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/week_days_pager.dart test/features/training/week_days_pager_test.dart
git commit -m "feat(entreno): carrusel de dias de la semana con dots"
```

---

### Task 6: Selector de programa (título-dropdown)

**Files:**
- Create: `lib/features/training/presentation/widgets/program_selector_button.dart`
- Test: `test/features/training/program_selector_button_preview_test.dart`

**Interfaces:**
- Consumes: `List<SubscriptionDetail>`, `int selectedIndex`, `ValueChanged<int> onSelect`, `VoidCallback onAddProgram`; `SubscriptionDetail.programName`, `.location`, `.daysPerWeek`; `S.addProgram`, `S.days`, **`S.locationGym` / `S.locationHomeBands` / `S.locationHomeDumbbells`** (ya existen en los .arb). Patrón visual: `MarcaSelector` (`widgets/marcas/marca_dropdown.dart`) — el dropdown canónico de la app.
- Produces: `class ProgramSelectorButton extends StatelessWidget` con
  `const ProgramSelectorButton({super.key, required this.subscriptions, required this.selectedIndex, required this.onSelect, required this.onAddProgram})`, y el helper público `String locationLabel(TrainingLocation, S)`.

**🚨 La ubicación es OBLIGATORIA para desambiguar.** Un usuario puede estar inscrito al **mismo programa en dos sitios** (p. ej. *Masa magra* en gimnasio para entre semana y en casa el finde) — caso real y frecuente. Sin la ubicación, el dropdown mostraría dos ítems **idénticos** y el título no diría cuál estás viendo.

| Dónde | Formato | Ejemplo |
|---|---|---|
| **Título del header** | `nombre · ubicación` | **"Masa magra · Gimnasio"** |
| **Ítems del dropdown** | `nombre · ubicación · días` | **"Masa magra · Gimnasio · 4 días"** |

> Los días **solo** van en el dropdown (en el título quedaban raros). `daysPerWeek` cuenta los días reales (3/4/5 según el programa).
> **Usar las claves l10n oficiales**, no los literales hardcodeados de `active_programs_section.dart` (que además dicen "Casa - Gomas" en vez de "Casa con gomas").

- [ ] **Step 1: Implementar**

```dart
// lib/features/training/presentation/widgets/program_selector_button.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/entities/subscription_detail.dart';
import '../../domain/entities/training_location.dart';

const int _kAddProgram = -1;

/// Etiqueta de la ubicación, desde l10n (NO hardcodear: `active_programs_section`
/// tiene literales antiguos que no coinciden con los .arb).
String locationLabel(TrainingLocation location, S l10n) => switch (location) {
      TrainingLocation.gym => l10n.locationGym,
      TrainingLocation.home => l10n.locationHomeBands,
      TrainingLocation.homeWithMaterial => l10n.locationHomeDumbbells,
    };

/// Programa activo como botón-dropdown.
///
/// Título: "Masa magra · Gimnasio ▾"
/// Ítems:  "Masa magra · Gimnasio · 4 días"
///
/// La ubicación es imprescindible: el mismo programa puede estar activo en
/// gimnasio Y en casa a la vez, y sin ella los ítems serían indistinguibles.
class ProgramSelectorButton extends StatelessWidget {
  const ProgramSelectorButton({
    super.key,
    required this.subscriptions,
    required this.selectedIndex,
    required this.onSelect,
    required this.onAddProgram,
  });

  final List<SubscriptionDetail> subscriptions;
  final int selectedIndex;
  final ValueChanged<int> onSelect;
  final VoidCallback onAddProgram;

  @override
  Widget build(BuildContext context) {
    final l10n = S.of(context);
    final colors = context.colors;
    final i = selectedIndex.clamp(0, subscriptions.length - 1);
    final current = subscriptions[i];

    // Título: nombre + ubicación (sin días — quedaban raros).
    final title =
        '${current.programName.trim()} · ${locationLabel(current.location, l10n)}';

    return PopupMenuButton<int>(
      offset: const Offset(0, 44),
      color: colors.bgSurface2,
      // Un usuario puede acumular muchos programas activos (el usuario de test
      // tiene 10). Sin tope, el menú se saldría de la pantalla.
      constraints: const BoxConstraints(maxHeight: 360),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        side: BorderSide(color: colors.strokeDivider),
      ),
      onSelected: (v) => v == _kAddProgram ? onAddProgram() : onSelect(v),
      itemBuilder: (context) => [
        for (int j = 0; j < subscriptions.length; j++)
          PopupMenuItem<int>(
            value: j,
            child: Row(children: [
              Expanded(child: Text(
                // En el dropdown SÍ van los días: aquí es donde se elige.
                '${subscriptions[j].programName.trim()} · '
                '${locationLabel(subscriptions[j].location, l10n)} · '
                '${subscriptions[j].daysPerWeek} ${l10n.days}',
                style: AppTypography.bodyMedium.copyWith(
                  color: j == i ? colors.brandPrimary : colors.textPrimary,
                  fontWeight: j == i ? FontWeight.w700 : FontWeight.w400,
                ),
              )),
              if (j == i) Icon(Icons.check, size: 18, color: colors.brandPrimary),
            ]),
          ),
        const PopupMenuDivider(),
        PopupMenuItem<int>(
          value: _kAddProgram,
          child: Row(children: [
            Icon(Icons.add, size: 18, color: colors.brandPrimary),
            const SizedBox(width: AppSpacing.s8),
            Text(l10n.addProgram,
                style: AppTypography.bodyMedium
                    .copyWith(color: colors.textSecondary)),
          ]),
        ),
      ],
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Flexible(child: Text(
            title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: AppTypography.bodyLarge.copyWith(color: colors.textPrimary),
          )),
          const SizedBox(width: AppSpacing.s6),
          Icon(Icons.keyboard_arrow_down, size: 20, color: colors.textSecondary),
        ],
      ),
    );
  }
}
```

- [ ] **Step 2: Golden test** (2 subscripciones, `selectedIndex: 0`, dark + light) → `goldens/program_selector_<theme>.png`. Confirmar que muestra **"Masa magra - 4 días ▾"**.

- [ ] **Step 3:** `flutter test test/features/training/program_selector_button_preview_test.dart --update-goldens` → PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/program_selector_button.dart test/features/training/program_selector_button_preview_test.dart test/features/training/goldens/program_selector_*.png
git commit -m "feat(entreno): selector de programa (titulo-dropdown)"
```

---

### Task 7: Diálogo "Terminar programa"

**Files:**
- Create: `lib/core/widgets/common/end_program_dialog.dart`
- Test: `test/features/training/end_program_dialog_test.dart`

**Interfaces:**
- Consumes: `S.endProgramTitle/endProgramMessage/endProgramConfirm/cancel`; `AppButton` + `AppButtonVariant.outlined` / `.destructive`. Patrón: `DeleteActivityDialog` (`features/activities/presentation/widgets/delete_activity_dialog.dart`).
- Produces: `Future<bool> showEndProgramDialog({required BuildContext context, required String programName})` — `true` si confirma.

- [ ] **Step 1: Implementar** (calcar `DeleteActivityDialog`, cambiando textos)

```dart
// lib/core/widgets/common/end_program_dialog.dart
import 'package:flutter/material.dart';

import '../../theme/theme.dart';
import '../../../l10n/app_localizations.dart';
import '../buttons/app_button.dart';

/// Confirmación para terminar un programa. Archiva: CONSERVA el progreso.
Future<bool> showEndProgramDialog({
  required BuildContext context,
  required String programName,
}) async {
  final result = await showDialog<bool>(
    context: context,
    builder: (context) {
      final l10n = S.of(context);
      final colors = context.colors;
      return Dialog(
        backgroundColor: colors.bgSurface1,
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSpacing.s16)),
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.s24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(l10n.endProgramTitle,
                  style: AppTypography.bodyLarge
                      .copyWith(color: colors.textPrimary),
                  textAlign: TextAlign.center),
              const SizedBox(height: AppSpacing.s8),
              Text(l10n.endProgramMessage(programName),
                  style: AppTypography.bodySmall
                      .copyWith(color: colors.textSecondary),
                  textAlign: TextAlign.center),
              const SizedBox(height: AppSpacing.s24),
              Row(children: [
                Expanded(child: AppButton(
                  label: l10n.cancel,
                  variant: AppButtonVariant.outlined,
                  onPressed: () => Navigator.of(context).pop(false),
                )),
                const SizedBox(width: AppSpacing.s8),
                Expanded(child: AppButton(
                  label: l10n.endProgramConfirm,
                  variant: AppButtonVariant.destructive,
                  onPressed: () => Navigator.of(context).pop(true),
                )),
              ]),
            ],
          ),
        ),
      );
    },
  );
  return result ?? false;
}
```

> Verificar la firma real de `AppButton` en `lib/core/widgets/buttons/app_button.dart`.

- [ ] **Step 2: Widget test** — tocar "Terminar" devuelve `true`; tocar "Cancelar" devuelve `false`.

- [ ] **Step 3:** `flutter test test/features/training/end_program_dialog_test.dart` → PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/core/widgets/common/end_program_dialog.dart test/features/training/end_program_dialog_test.dart
git commit -m "feat(entreno): dialogo de confirmacion terminar programa"
```

---

### Task 8: Menú ⋮ (Ver programa / Terminar programa)

**Files:**
- Create: `lib/features/training/presentation/widgets/program_actions_menu.dart`
- Test: `test/features/training/program_actions_menu_test.dart`

**Interfaces:**
- Consumes: `VoidCallback onViewProgram`, `onEndProgram`; `S.viewProgram/endProgram`.
- Produces: `class ProgramActionsMenu extends StatelessWidget` —
  `const ProgramActionsMenu({super.key, required this.onViewProgram, required this.onEndProgram})`. `PopupMenuButton` con `Icons.more_vert` y **2 items**; "Terminar" en `colors.destructive`.

- [ ] **Step 1: Implementar**

```dart
// lib/features/training/presentation/widgets/program_actions_menu.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../l10n/app_localizations.dart';

enum _ProgramAction { view, end }

class ProgramActionsMenu extends StatelessWidget {
  const ProgramActionsMenu({
    super.key,
    required this.onViewProgram,
    required this.onEndProgram,
  });

  final VoidCallback onViewProgram;
  final VoidCallback onEndProgram;

  @override
  Widget build(BuildContext context) {
    final l10n = S.of(context);
    final colors = context.colors;
    return PopupMenuButton<_ProgramAction>(
      icon: Icon(Icons.more_vert, color: colors.textSecondary),
      color: colors.bgSurface2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        side: BorderSide(color: colors.strokeDivider),
      ),
      onSelected: (a) => switch (a) {
        _ProgramAction.view => onViewProgram(),
        _ProgramAction.end => onEndProgram(),
      },
      itemBuilder: (context) => [
        PopupMenuItem(value: _ProgramAction.view,
          child: Text(l10n.viewProgram,
            style: AppTypography.bodyMedium.copyWith(color: colors.textPrimary))),
        PopupMenuItem(value: _ProgramAction.end,
          child: Text(l10n.endProgram,
            style: AppTypography.bodyMedium.copyWith(color: colors.destructive))),
      ],
    );
  }
}
```

- [ ] **Step 2: Widget test** — abrir el menú, ver los 2 textos, comprobar que cada uno dispara su callback.

- [ ] **Step 3:** `flutter test test/features/training/program_actions_menu_test.dart` → PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/program_actions_menu.dart test/features/training/program_actions_menu_test.dart
git commit -m "feat(entreno): menu de acciones del programa"
```

---

### Task 9: Fila de header (selector + ⋮ + acciones)

**Files:**
- Create: `lib/features/training/presentation/widgets/program_header_row.dart`
- Test: `test/features/training/program_header_row_test.dart`

**Interfaces:**
- Consumes: `ProgramSelectorButton` (T6), `ProgramActionsMenu` (T8), `showEndProgramDialog` (T7); providers `selectedSubscriptionIndexProvider`, `selectedSubscriptionProvider`, `trainingContentNotifierProvider`, `hasActiveSubscriptionsNotifierProvider`, `trainingRepositoryProvider`; rutas `AppRoutes.programsCatalog`, **`AppRoutes.trainingSession`**.
- Produces: `class ProgramHeaderRow extends ConsumerWidget` — `const ProgramHeaderRow({super.key, required this.subscriptions})`.

> ⚠️ **"Ver programa" va a `AppRoutes.trainingSession`** (`TrainingSessionScreen` = la estructura de TU programa: fases, pestañas de semana y cards de día). **NO** a `AppRoutes.programDetail`, que es la ficha del **catálogo** para inscribirse. Este era el destino original de la card de programa (`active_programs_section.dart:55`).

- [ ] **Step 1: Implementar**

```dart
// lib/features/training/presentation/widgets/program_header_row.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/widgets/common/end_program_dialog.dart';
import '../../domain/entities/subscription_detail.dart';
import '../providers/training_providers.dart';
import 'program_actions_menu.dart';
import 'program_selector_button.dart';

class ProgramHeaderRow extends ConsumerWidget {
  const ProgramHeaderRow({super.key, required this.subscriptions});

  final List<SubscriptionDetail> subscriptions;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedIndex = ref.watch(selectedSubscriptionIndexProvider);
    final current = ref.watch(selectedSubscriptionProvider);

    return Row(
      children: [
        Expanded(
          child: ProgramSelectorButton(
            subscriptions: subscriptions,
            selectedIndex: selectedIndex,
            onSelect: (i) =>
                ref.read(selectedSubscriptionIndexProvider.notifier).state = i,
            onAddProgram: () => context.push(AppRoutes.programsCatalog),
          ),
        ),
        ProgramActionsMenu(
          // Estructura del programa inscrito (fases/semanas/días), NO el catálogo.
          onViewProgram: () => context.push(AppRoutes.trainingSession),
          onEndProgram: () => _endProgram(context, ref, current),
        ),
      ],
    );
  }

  /// Terminar = archivar (CONSERVA el progreso en el historial).
  /// NUNCA usar unsubscribeFromProgram: borra el progreso para siempre.
  Future<void> _endProgram(
      BuildContext context, WidgetRef ref, SubscriptionDetail? sub) async {
    if (sub == null) return;
    final ok = await showEndProgramDialog(
        context: context, programName: sub.programName);
    if (!ok) return;
    await ref.read(trainingRepositoryProvider).archiveProgram(sub.id);
    ref.read(selectedSubscriptionIndexProvider.notifier).state = 0;
    ref.invalidate(trainingContentNotifierProvider);
    ref.invalidate(hasActiveSubscriptionsNotifierProvider);
  }
}
```

> Verificar la firma `archiveProgram(int id, {bool keepProgress = true})` (repo interface L102): por defecto archiva conservando el progreso. Copiar el patrón de invalidación de `program_completed_card.dart:57-141`.

- [ ] **Step 2: Widget test** con overrides: se ve "Masa magra - 4 días"; al tocar ⋮ aparecen "Ver programa" y "Terminar programa".

- [ ] **Step 3:** `flutter test test/features/training/program_header_row_test.dart` → PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/program_header_row.dart test/features/training/program_header_row_test.dart
git commit -m "feat(entreno): header con selector y gestion de programa"
```

---

### Task 10: Integrar todo en MainEntrenoScreen

**Files:** Modify `lib/features/training/presentation/screens/main_entreno_screen.dart` (`_ProgramsTab`, L206–275)

- [ ] **Step 1: Reemplazar el contenido del `Column` de `_ProgramsTab`** (L231–270). Quitar `ActiveProgramsSection` y `_NextTrainingSection`. Conservar el branch `isSelectedCompleted → ProgramCompletedCard` y `_PreviousRecordsSection`.

```dart
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: AppSpacing.s16),

            if (content.subscriptions.isNotEmpty) ...[
              // 1. Header: "Masa magra - 4 días ▾"  +  ⋮
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: AppSpacing.s16),
                child: ProgramHeaderRow(subscriptions: content.subscriptions),
              ),
              const SizedBox(height: AppSpacing.s16),

              // 2. Progreso de la semana del programa (3 estados)
              Consumer(builder: (context, ref, _) {
                final week = ref.watch(selectedCurrentWeekProvider);
                final dayIndex = ref.watch(selectedDayIndexProvider);
                if (week == null || week.totalDays == 0) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: AppSpacing.s16),
                  child: WeeklyProgressBar(
                    week: week,
                    selectedDayIndex: dayIndex,
                  ),
                );
              }),
              const SizedBox(height: AppSpacing.s16),

              if (isSelectedCompleted) ...[
                // Programa terminado: la barra (arriba) se ve TODA VERDE y
                // debajo la card de completado, que YA trae los botones
                // "Archivar programa" y "Reiniciar programa" (no hay que
                // construirlos: program_completed_card.dart:208-221).
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: AppSpacing.s16),
                  child: ProgramCompletedCard(
                    subscriptionId: selectedSubscription!.id,
                    programId: selectedSubscription.programId,
                    programName: selectedSubscription.programName,
                    location: selectedSubscription.location.apiValue,
                  ),
                ),
              ] else ...[
                // 3. Carrusel de los días de la semana (cards sin botón)
                const WeekDaysPager(),

                const SizedBox(height: AppSpacing.s24),

                // 4. Tus marcas (sin cambios)
                _PreviousRecordsSection(ref: ref),
              ],
            ],

            SizedBox(height: MediaQuery.of(context).padding.bottom + 80),
          ],
        ),
```

Añadir imports:
```dart
import '../providers/current_week_provider.dart';
import '../widgets/program_header_row.dart';
import '../widgets/weekly_progress_bar.dart';
import '../widgets/week_days_pager.dart';
```
Quitar los imports de `active_programs_section.dart` y `next_training_card.dart` si quedan sin uso (`flutter analyze` lo dirá). **Conservar** `_NextTrainingSection` solo si algo más lo usa; si no, borrarlo del archivo.

- [ ] **Step 2: Analizar**

Run: `flutter analyze lib/features/training`
Expected: `No issues found!`

- [ ] **Step 3: Toda la batería de tests**

Run: `flutter test test/features/training/`
Expected: todo PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/screens/main_entreno_screen.dart
git commit -m "feat(entreno): integrar header, progreso semanal y carrusel de dias"
```

---

### Task 11: Verificación en el simulador

- [ ] **Step 1: Arrancar**

`flutter run -d <sim-id> --dart-define=APP_ENV=development`
Usuario con programas: `ana.garcia.test@mailinator.com` / `Test1234!` (10 subscripciones). Ir al tab Entreno.

- [ ] **Step 2: Checklist visual**
  - [ ] El tab "Entreno / Seguimiento" sigue arriba, intacto.
  - [ ] Título **"Masa magra · Gimnasio ▾"** a la izquierda; **⋮** a la derecha.
  - [ ] Tocar el título → lista con **"Masa magra · Gimnasio · 4 días"** (✓ en el activo) + "＋ Añadir programa".
  - [ ] **Desambiguación:** Ana tiene el mismo programa en varias ubicaciones. Comprobar que los ítems **se distinguen** (no salen dos "Masa magra" idénticos).
  - [ ] **Regresión del carrusel:** cambiar de programa desde el dropdown → el carrusel y la barra deben **reposicionarse juntos** en el día correcto del programa nuevo (no quedarse en el día viejo ni petar).
  - [ ] **Regresión al volver de un entreno (el caso más común):** completar un día y volver → el carrusel **se desliza solo** al siguiente entreno, **con la barra sincronizada** (el día que marca la barra en gris claro es el mismo que muestra la card). Antes del fix quedaban desincronizados.
  - [ ] **Menú largo:** con el usuario de test (10 programas) el desplegable **hace scroll** y no se sale de la pantalla.
  - [ ] **Programa terminado:** barra toda verde + card de completado con sus botones **"Archivar programa"** / **"Reiniciar programa"** (ya existen, no se construyen).
  - [ ] Tocar ⋮ → **Ver programa** (lleva a la estructura del programa con semanas) y **Terminar programa** (pide confirmación; conserva el progreso).
  - [ ] Barra: casillas verdes (hechas), gris claro (la que ves), gris oscuro (pendientes). Texto **"Semana N · X de N entrenos"**.
  - [ ] Card **sin botón**, con la foto del programa. Tag correcto: PRÓXIMO ENTRENO / COMPLETADO / **EN CURSO (naranja)** / sin tag.
  - [ ] **Deslizar** la card cambia de día dentro de la semana; los **dots** se mueven; la barra marca en gris claro el día que ves.
  - [ ] Tocar la card (en cualquier estado) abre el entreno. En un día completado, las series salen **rellenadas** y se pueden sobreescribir.
  - [ ] "Tus marcas" sigue debajo, intacto.

- [ ] **Step 3: Captura** y adjuntar al caso de estudio (`casos-de-estudio/entreno-arquitectura-dos-cards.md` §G).

---

## Pendiente en Figma (no bloquea el código)

1. **`message/warning` en modo Light está en blanco** (`#FFFFFF`) — es un bug del design system. En el código ya está corregido (naranja en ambos temas).
2. **`NextWorkoutCard` no tiene la variante "EN CURSO"** (naranja). El código ya la implementa; convendría añadirla al componente.
3. Typo menor: la variante se llama `NextSesion` (una sola "s").

## Riesgo conocido (aceptado, no se resuelve aquí)

**Si el usuario se salta un día**, la card le seguirá proponiendo ese día como "próximo entreno" y la barra se quedará anclada en esa semana, aunque él siga entrenando por "Ver programa". **No está bloqueado** (puede entrenar cualquier día desde ahí), pero la pantalla principal muestra información desfasada. Un botón de "saltar entreno" requeriría backend (el sistema solo conoce "hecho"/"no hecho") y **queda fuera de alcance por decisión de producto**. Workaround para el usuario: marcar el entreno como completado.

## Self-Review

**Cobertura:** header con dropdown ✅ T6+T9 · menú ⋮ (Ver/Terminar) ✅ T8+T9 · confirmación destructiva ✅ T7 · barra 3 estados ✅ T1+T3 · card sin botón con 4 tags ✅ T4 · carrusel de días de la semana + dots ✅ T5 · integración ✅ T10 · tab bar y "Tus marcas" intactos ✅ T10.

**Consistencia de tipos:** `selectedCurrentWeekProvider` (`TrainingWeek?`), `selectedDayIndexProvider` (`int`) e `initialDayIndexProvider` (`int`) se usan igual en T3/T5/T10. `WorkoutCardState` + `workoutCardStateFor(day, isNext:)` definidos en T4 y consumidos en T5. `showEndProgramDialog(context:, programName:) → Future<bool>` definido en T7 y usado en T9.

**Verificado contra datos reales (API dev):**
- "Masa magra" tiene **4 días/semana**; los días son "Tren superior", "Pierna + Core", "Fullbody"…; con 7/5/5/4 ejercicios.
- `training_type` contiene listas largas de músculos ("Pecho, espalda, hombros…") → **no se muestra**.
- La duración del entreno **no existe** → no se muestra.
- **El mismo programa puede estar activo en varias ubicaciones a la vez** (gym + casa) → sin la ubicación, el dropdown mostraría ítems idénticos. **Por eso la ubicación es obligatoria.**
- Los ejercicios por día van de **1 a 13**; no hay días con 0 (el singular "1 ejercicio" está contemplado).
- Nombres cortos: programa máx. 16 caracteres, día máx. 29 → sin riesgo de desbordamiento (aun así, `maxLines: 2` + ellipsis en la card).
- Hoy todos los programas tienen **1 fase** y **todas las semanas con los mismos días**. `daysPerWeek` se calcula de la primera semana: si en el futuro hubiera semanas desiguales, el número mostrado no valdría para todas. *(Riesgo anotado, no se materializa hoy.)*

**A verificar al implementar:** parámetros `required` reales de las entidades de dominio (fixtures de test); firma exacta de `AppButton`; `withValues(alpha:)` vs `withOpacity` según la versión de Flutter.

## Materiales

- Caso de estudio: `casos-de-estudio/entreno-arquitectura-dos-cards.md`
- Figma: `NextWorkoutCard` node `1275:3358` (EMP DS - Library, `LOFKz4g6bswukPAJfWR0Ts`)
- Prototipos: `entreno-una-card.html`, `entreno-selector-programa.html` (opción 2 elegida)
- Estados y datos: `entreno-estados-datos.html`
- Rama: `ux/entreno-card-siguiente-v-b`
