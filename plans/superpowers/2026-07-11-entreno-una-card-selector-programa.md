# Entreno — Una card + selector de programa · Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar la pestaña "Entreno" de la app: sustituir el carrusel de programas + card "Siguiente entreno" separada por (a) un header con el nombre del programa como título-dropdown + menú ⋮ de gestión, (b) una barra de progreso semanal, y (c) una card héroe única = el siguiente entreno sobre la imagen del programa, con botón verde sólido.

**Architecture:** Todo el trabajo es **frontend Flutter** (repo `elmetodo_app`). El backend ya expone lo necesario vía `GET /api/training/content` (estructura completa `phases → weeks → days` con completion por día). El "programa activo" se selecciona **client-side** (no hay ni hace falta endpoint de "programa actual"); el progreso semanal se **deriva client-side** contando `is_completed` en la semana actual. Se reutilizan patrones existentes: `PopupMenuButton` (de `MarcaSelector`) para dropdown y kebab, `DeleteActivityDialog` para confirmaciones destructivas, y la base visual de `_ActiveProgramCard` (imagen + gradiente) para la card héroe.

**Tech Stack:** Flutter, Riverpod (riverpod_generator / `@riverpod`), go_router, golden/widget tests con `flutter_test`.

## Global Constraints

- **Repo de código:** `/Users/kataiturriaga/repos/elmetodo_app`. Rama de trabajo: `ux/entreno-card-siguiente-v-b` (ya creada, ya contiene la card `next_training_card.dart` con botón verde + su golden test).
- **Sin cambios de backend.** Todo se resuelve con datos de `GET /api/training/content` (ya consumido por `trainingContentNotifierProvider`).
- **Tokens de diseño:** usar siempre `context.colors.<token>` (nunca hex). Verde de marca = `context.colors.brandPrimary`. Espaciados = `AppSpacing.sN`. Tipografía = `AppTypography.*`. Import barrel: `import '../../../../core/theme/theme.dart';`.
- **Localización:** todo texto visible vía `S.of(context)` con claves en `lib/l10n/app_es.arb` **y** `app_en.arb`; regenerar con `flutter gen-l10n` (o `flutter pub get` según config) tras editar los `.arb`. Idioma primario ES.
- **"Terminar programa" NO usa `unsubscribeFromProgram` (DELETE duro que borra progreso).** Usa `archiveProgram(id, keepProgress: true)` que conserva historial.
- **Acciones destructivas (Terminar, Reemplazar) requieren diálogo de confirmación.**
- **Providers nuevos:** si se añade un `@riverpod`, regenerar con `dart run build_runner build --delete-conflicting-outputs`.
- **Tests:** cada widget nuevo lleva golden test siguiendo el patrón de `test/features/training/next_training_card_preview_test.dart` (carga fuentes OpenSans + MaterialIcons en `setUpAll`). Regenerar goldens con `--update-goldens`.
- **Fuera de alcance de este plan (Fase 2, documentado al final):** scroll horizontal entre días de la semana dentro de la card héroe.

---

## Mapa de archivos

**Nuevos:**
- `lib/features/training/presentation/providers/current_week_provider.dart` — provider `selectedCurrentWeekProvider` (`TrainingWeek?`).
- `lib/features/training/presentation/widgets/program_selector_button.dart` — el título-programa con dropdown.
- `lib/features/training/presentation/widgets/program_actions_menu.dart` — el kebab ⋮ (Ver / Reemplazar / Terminar).
- `lib/features/training/presentation/widgets/program_header_row.dart` — compone selector + kebab en una fila.
- `lib/features/training/presentation/widgets/weekly_progress_bar.dart` — barra + "X de N completados esta semana".
- `lib/features/training/presentation/widgets/next_training_hero_card.dart` — card héroe (imagen programa + siguiente entreno + botón verde).
- `lib/core/widgets/common/end_program_dialog.dart` — `showEndProgramDialog`.
- Tests golden/widget para cada widget en `test/features/training/`.

**Modificados:**
- `lib/features/training/presentation/screens/main_entreno_screen.dart` — `_ProgramsTab` (L206–275): insertar header + weekly progress + hero card; retirar `ActiveProgramsSection` y `_NextTrainingSection`.
- `lib/l10n/app_es.arb` y `lib/l10n/app_en.arb` — claves nuevas.

**Se conservan sin tocar:** `_PreviousRecordsSection` / `MarcasSection` ("Tus marcas"), `SegmentedTabBar` (tab Entreno/Seguimiento), `_EmptyProgramsTab`, `ProgramCompletedCard`, `_LoadingState`, `_ErrorState`.

**Posible retirada tras integración:** `active_programs_section.dart` y `next_training_card.dart` quedan sin uso en `_ProgramsTab`. NO borrar en este plan (pueden usarse en otros sitios / como fallback). Marcar como candidatos a limpieza en un PR posterior.

---

## FASE 1 — Núcleo (pantalla nueva funcional, card fija en el siguiente entreno)

### Task 1: Provider de la semana actual

**Files:**
- Create: `lib/features/training/presentation/providers/current_week_provider.dart`
- Test: `test/features/training/current_week_provider_test.dart`

**Interfaces:**
- Consumes: `selectedSubscriptionProvider` → `SubscriptionDetail?` (de `training_providers.dart:294`); entidades `SubscriptionDetail`, `ProgramPhase`, `TrainingWeek`, `TrainingDay` (de `domain/entities/subscription_detail.dart`).
- Produces: `selectedCurrentWeekProvider` → `TrainingWeek?` — la primera semana (recorriendo `phases → weeks`) que contiene algún día `!isCompleted`; si todas completas, la última semana; si no hay datos, `null`.

- [ ] **Step 1: Write the failing test**

```dart
// test/features/training/current_week_provider_test.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:elmetodo_app/features/training/domain/entities/subscription_detail.dart';
import 'package:elmetodo_app/features/training/domain/entities/training_location.dart';
import 'package:elmetodo_app/features/training/presentation/providers/training_providers.dart';
import 'package:elmetodo_app/features/training/presentation/providers/current_week_provider.dart';

TrainingDay _day(int id, {required bool done}) => TrainingDay(
      id: id, dayOrder: id, name: 'Día $id', isCompleted: done,
    );

SubscriptionDetail _sub(List<TrainingWeek> weeks) => SubscriptionDetail(
      id: 1, programId: 1, programName: 'Test', location: TrainingLocation.gym,
      zones: const [], completedDays: 0, totalDays: 6,
      enrolledAt: DateTime(2026, 1, 1), isActive: true, isCompleted: false,
      phases: [ProgramPhase(id: 1, phaseOrder: 1, name: 'F1', totalWeeks: weeks.length, completedWeeks: 0, weeks: weeks)],
    );

void main() {
  test('devuelve la semana que contiene el primer día no completado', () {
    final w1 = TrainingWeek(weekNumber: 1, days: [_day(1, done: true), _day(2, done: true)]);
    final w2 = TrainingWeek(weekNumber: 2, days: [_day(3, done: false), _day(4, done: false)]);
    final container = ProviderContainer(overrides: [
      selectedSubscriptionProvider.overrideWith((ref) => _sub([w1, w2])),
    ]);
    addTearDown(container.dispose);
    expect(container.read(selectedCurrentWeekProvider)?.weekNumber, 2);
  });

  test('si todo está completo, devuelve la última semana', () {
    final w1 = TrainingWeek(weekNumber: 1, days: [_day(1, done: true)]);
    final w2 = TrainingWeek(weekNumber: 2, days: [_day(2, done: true)]);
    final container = ProviderContainer(overrides: [
      selectedSubscriptionProvider.overrideWith((ref) => _sub([w1, w2])),
    ]);
    addTearDown(container.dispose);
    expect(container.read(selectedCurrentWeekProvider)?.weekNumber, 2);
  });

  test('sin subscripción devuelve null', () {
    final container = ProviderContainer(overrides: [
      selectedSubscriptionProvider.overrideWith((ref) => null),
    ]);
    addTearDown(container.dispose);
    expect(container.read(selectedCurrentWeekProvider), isNull);
  });
}
```

> Nota: verificar los constructores exactos de `SubscriptionDetail`/`ProgramPhase`/`TrainingWeek`/`TrainingDay` en `domain/entities/subscription_detail.dart` y ajustar los parámetros nombrados requeridos (los mostrados son los que el entity marca `required`). Si `selectedSubscriptionProvider` es un provider de función generado, usar `overrideWith` con la firma correcta (puede requerir `overrideWithValue` si no es generado — comprobar `training_providers.dart:294`).

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/kataiturriaga/repos/elmetodo_app && flutter test test/features/training/current_week_provider_test.dart`
Expected: FAIL — `selectedCurrentWeekProvider` no existe.

- [ ] **Step 3: Write minimal implementation**

```dart
// lib/features/training/presentation/providers/current_week_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/subscription_detail.dart';
import 'training_providers.dart';

/// La "semana actual" de la subscripción seleccionada: la primera semana
/// (recorriendo phases → weeks en orden) que contiene algún día sin completar.
/// Si todas las semanas están completas, devuelve la última. Null si no hay datos.
final selectedCurrentWeekProvider = Provider<TrainingWeek?>((ref) {
  final sub = ref.watch(selectedSubscriptionProvider);
  if (sub == null) return null;

  TrainingWeek? last;
  for (final phase in sub.phases) {
    for (final week in phase.weeks) {
      last = week;
      if (week.days.any((d) => !d.isCompleted)) {
        return week;
      }
    }
  }
  return last; // todo completo → última semana (o null si no había semanas)
});
```

- [ ] **Step 4: Run test to verify it passes**

Run: `flutter test test/features/training/current_week_provider_test.dart`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add lib/features/training/presentation/providers/current_week_provider.dart test/features/training/current_week_provider_test.dart
git commit -m "feat(entreno): provider de la semana actual para progreso semanal"
```

---

### Task 2: Claves de localización

**Files:**
- Modify: `lib/l10n/app_es.arb`, `lib/l10n/app_en.arb`
- (Regenera `lib/l10n/app_localizations*.dart`)

**Interfaces:**
- Produces (getters en `S`): `viewProgram`, `replaceProgram`, `endProgram`, `addProgram`, `programWeekProgress(int week, int completed, int total)`, `endProgramTitle`, `endProgramMessage(String programName)`, `endProgramConfirm`, `replaceProgramTitle`, `replaceProgramMessage(String programName)`, `replaceProgramConfirm`.

- [ ] **Step 1: Añadir claves a `app_es.arb`**

Insertar (respetando el formato JSON del archivo; los parametrizados llevan bloque `"placeholders"`):

```json
  "viewProgram": "Ver programa",
  "replaceProgram": "Reemplazar programa",
  "endProgram": "Terminar programa",
  "addProgram": "Añadir programa",
  "programWeekProgress": "Semana {week} · {completed} de {total} entrenos",
  "@programWeekProgress": {
    "description": "Progreso de la SEMANA DEL PROGRAMA (no la semana natural). No se resetea por calendario: avanza al completar los días.",
    "placeholders": { "week": { "type": "int" }, "completed": { "type": "int" }, "total": { "type": "int" } }
  },
  "endProgramTitle": "¿Terminar programa?",
  "endProgramMessage": "Guardaremos tu progreso de {programName} en el historial. Podrás volver a empezarlo cuando quieras.",
  "@endProgramMessage": {
    "placeholders": { "programName": { "type": "String" } }
  },
  "endProgramConfirm": "Terminar",
  "replaceProgramTitle": "¿Reemplazar programa?",
  "replaceProgramMessage": "Guardaremos el progreso de {programName} y elegirás un programa nuevo.",
  "@replaceProgramMessage": {
    "placeholders": { "programName": { "type": "String" } }
  },
  "replaceProgramConfirm": "Elegir nuevo"
```

- [ ] **Step 2: Añadir las mismas claves a `app_en.arb`**

```json
  "viewProgram": "View program",
  "replaceProgram": "Replace program",
  "endProgram": "End program",
  "addProgram": "Add program",
  "programWeekProgress": "Week {week} · {completed} of {total} workouts",
  "@programWeekProgress": {
    "description": "PROGRAM week progress (not the calendar week). Does not reset on Mondays: it advances as days are completed.",
    "placeholders": { "week": { "type": "int" }, "completed": { "type": "int" }, "total": { "type": "int" } }
  },
  "endProgramTitle": "End program?",
  "endProgramMessage": "We'll save your {programName} progress to your history. You can start it again anytime.",
  "@endProgramMessage": {
    "placeholders": { "programName": { "type": "String" } }
  },
  "endProgramConfirm": "End",
  "replaceProgramTitle": "Replace program?",
  "replaceProgramMessage": "We'll save your {programName} progress and you'll pick a new program.",
  "@replaceProgramMessage": {
    "placeholders": { "programName": { "type": "String" } }
  },
  "replaceProgramConfirm": "Pick new"
```

- [ ] **Step 3: Regenerar y verificar compilación**

Run: `cd /Users/kataiturriaga/repos/elmetodo_app && flutter gen-l10n && flutter analyze lib/l10n`
Expected: sin errores; getters nuevos presentes en `lib/l10n/app_localizations.dart`.

- [ ] **Step 4: Commit**

```bash
git add lib/l10n/app_es.arb lib/l10n/app_en.arb lib/l10n/app_localizations*.dart
git commit -m "i18n(entreno): claves para selector y gestión de programa"
```

---

### Task 3: Barra de progreso semanal

**Files:**
- Create: `lib/features/training/presentation/widgets/weekly_progress_bar.dart`
- Test: `test/features/training/weekly_progress_bar_preview_test.dart`

**Interfaces:**
- Consumes: `TrainingWeek` (`weekNumber`, `completedDays`, `totalDays`); `S.programWeekProgress`.
- Produces: `class WeeklyProgressBar extends StatelessWidget` con constructor `const WeeklyProgressBar({super.key, required this.week})` donde `final TrainingWeek week;`. Renderiza una barra segmentada (una casilla por día, verde = completado) + label `programWeekProgress(week.weekNumber, week.completedDays, week.totalDays)` → **"Semana 1 · 1 de 6 entrenos"**.

> **⚠️ Semántica de "semana" (decisión de producto, verificada en código):** la semana es la **del programa**, NO la natural del calendario. Verificado: `TrainingWeek` (front) y `MobileWeek` (API) solo tienen `weekNumber` (un contador 1,2,3…) y `days`; no hay fechas ni lógica de calendario (`isocalendar`/`weekday`/`timedelta`) en ninguno de los dos repos. **La barra NO se resetea los lunes**: la semana avanza solo cuando se completan sus días. Por eso el copy NO debe decir "esta semana" (implicaría calendario) sino **"Semana N"**.

- [ ] **Step 1: Write the widget**

```dart
// lib/features/training/presentation/widgets/weekly_progress_bar.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/entities/subscription_detail.dart';

/// Barra de progreso de la semana **del programa** (no la natural): una
/// casilla por día (verde = completado) + "Semana N · X de N entrenos".
///
/// No se resetea por calendario: la semana avanza cuando se completan sus días.
class WeeklyProgressBar extends StatelessWidget {
  const WeeklyProgressBar({super.key, required this.week});

  final TrainingWeek week;

  @override
  Widget build(BuildContext context) {
    final l10n = S.of(context);
    final colors = context.colors;
    final total = week.totalDays;
    final done = week.completedDays;

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
                    color: i < done ? colors.brandPrimary : colors.strokeDivider,
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
          l10n.programWeekProgress(week.weekNumber, done, total),
          style: AppTypography.bodySmall.copyWith(color: colors.textSecondary),
        ),
      ],
    );
  }
}
```

- [ ] **Step 2: Write the golden test** (patrón de `next_training_card_preview_test.dart` — copiar `setUpAll(_loadFonts)` y `_pump` de ese archivo)

```dart
// test/features/training/weekly_progress_bar_preview_test.dart
// (copiar _loadFonts y _pump de next_training_card_preview_test.dart)
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:elmetodo_app/features/training/domain/entities/subscription_detail.dart';
import 'package:elmetodo_app/features/training/presentation/widgets/weekly_progress_bar.dart';
// + imports de tema/l10n/fuentes idénticos al test de referencia

TrainingWeek _week(int done, int total) => TrainingWeek(
      weekNumber: 1,
      days: List.generate(total, (i) => TrainingDay(
        id: i, dayOrder: i, name: 'D$i', isCompleted: i < done)),
    );

void main() {
  setUpAll(_loadFonts);
  for (final theme in [ThemeMode.dark, ThemeMode.light]) {
    final t = theme == ThemeMode.dark ? 'dark' : 'light';
    testWidgets('weekly_progress 2de6 $t', (tester) async {
      await _pump(tester, child: Padding(
        padding: const EdgeInsets.all(16), child: WeeklyProgressBar(week: _week(2, 6))),
        themeMode: theme);
      await expectLater(find.byType(WeeklyProgressBar),
        matchesGoldenFile('goldens/weekly_progress_2de6_$t.png'));
    });
  }
}
```

- [ ] **Step 3: Generate goldens & verify**

Run: `flutter test test/features/training/weekly_progress_bar_preview_test.dart --update-goldens`
Expected: PASS; PNGs en `test/features/training/goldens/`. Abrir `weekly_progress_2de6_dark.png` y confirmar 2 casillas verdes de 6 + texto legible.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/weekly_progress_bar.dart test/features/training/weekly_progress_bar_preview_test.dart test/features/training/goldens/weekly_progress_2de6_*.png
git commit -m "feat(entreno): barra de progreso semanal"
```

---

### Task 4: Selector de programa (título-dropdown)

**Files:**
- Create: `lib/features/training/presentation/widgets/program_selector_button.dart`
- Test: `test/features/training/program_selector_button_preview_test.dart`

**Interfaces:**
- Consumes: `List<SubscriptionDetail> subscriptions`, `int selectedIndex`, callbacks `ValueChanged<int> onSelect` y `VoidCallback onAddProgram`. Campos de `SubscriptionDetail`: `programName`, `daysPerWeek`. `S.addProgram`, `S.days`.
- Produces: `class ProgramSelectorButton extends StatelessWidget` con:
  ```dart
  const ProgramSelectorButton({
    super.key,
    required this.subscriptions,
    required this.selectedIndex,
    required this.onSelect,
    required this.onAddProgram,
  });
  ```
  Título grande = `"${sub.programName} - ${sub.daysPerWeek} ${l10n.days}"` con `Icon(Icons.keyboard_arrow_down)`. Al pulsar abre un `PopupMenuButton`-equivalente (patrón `MarcaSelector`, `marca_dropdown.dart`): items = cada subscripción (marcada con check si es la seleccionada, en `brandPrimary`) + separador + item "＋ Añadir programa". Selección → `onSelect(index)`; añadir → `onAddProgram()`.

- [ ] **Step 1: Implement widget** (seguir el patrón visual de `MarcaSelector` en `lib/features/training/presentation/widgets/marcas/marca_dropdown.dart`)

```dart
// lib/features/training/presentation/widgets/program_selector_button.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/entities/subscription_detail.dart';

/// Valor especial para el item "Añadir programa" del menú.
const int _kAddProgram = -1;

/// Título del programa como botón-dropdown. Muestra
/// "Nombre - N días ▾" y abre un menú para cambiar de programa activo
/// o añadir uno nuevo.
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
    final safeIndex = selectedIndex.clamp(0, subscriptions.length - 1);
    final current = subscriptions[safeIndex];
    final title = '${current.programName} - ${current.daysPerWeek} ${l10n.days}';

    return PopupMenuButton<int>(
      offset: const Offset(0, 44),
      color: colors.bgSurface2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMedium),
        side: BorderSide(color: colors.strokeDivider),
      ),
      onSelected: (value) {
        if (value == _kAddProgram) {
          onAddProgram();
        } else {
          onSelect(value);
        }
      },
      itemBuilder: (context) => [
        for (int i = 0; i < subscriptions.length; i++)
          PopupMenuItem<int>(
            value: i,
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    subscriptions[i].programName,
                    style: AppTypography.bodyMedium.copyWith(
                      color: i == safeIndex ? colors.brandPrimary : colors.textPrimary,
                      fontWeight: i == safeIndex ? FontWeight.w700 : FontWeight.w400,
                    ),
                  ),
                ),
                if (i == safeIndex)
                  Icon(Icons.check, size: 18, color: colors.brandPrimary),
              ],
            ),
          ),
        const PopupMenuDivider(),
        PopupMenuItem<int>(
          value: _kAddProgram,
          child: Row(
            children: [
              Icon(Icons.add, size: 18, color: colors.brandPrimary),
              const SizedBox(width: AppSpacing.s8),
              Text(l10n.addProgram,
                  style: AppTypography.bodyMedium.copyWith(color: colors.textSecondary)),
            ],
          ),
        ),
      ],
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Flexible(
            child: Text(
              title,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: AppTypography.bodyLarge.copyWith(color: colors.textPrimary),
            ),
          ),
          const SizedBox(width: AppSpacing.s6),
          Icon(Icons.keyboard_arrow_down, size: 20, color: colors.textSecondary),
        ],
      ),
    );
  }
}
```

> Verificar que `AppSpacing.radiusMedium` existe (el informe lo lista); si no, usar `AppSpacing.s8`.

- [ ] **Step 2: Golden test** (dropdown cerrado, dark + light) — mismo patrón. Escenario: 2 subscripciones, `selectedIndex: 0`.

```dart
// test/features/training/program_selector_button_preview_test.dart
// (copiar _loadFonts / _pump). Construir 2 SubscriptionDetail de prueba.
// Render: ProgramSelectorButton(subscriptions: subs, selectedIndex: 0, onSelect: (_) {}, onAddProgram: () {})
// expectLater → goldens/program_selector_<theme>.png
```

- [ ] **Step 3: Generate & verify**

Run: `flutter test test/features/training/program_selector_button_preview_test.dart --update-goldens`
Expected: PASS; el golden muestra "Nombre - 6 días ▾".

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/program_selector_button.dart test/features/training/program_selector_button_preview_test.dart test/features/training/goldens/program_selector_*.png
git commit -m "feat(entreno): selector de programa (titulo-dropdown)"
```

---

### Task 5: Diálogo de confirmación "Terminar programa"

**Files:**
- Create: `lib/core/widgets/common/end_program_dialog.dart`
- Test: `test/features/training/end_program_dialog_test.dart`

**Interfaces:**
- Consumes: `S.endProgramTitle`, `S.endProgramMessage(programName)`, `S.endProgramConfirm`, `S.cancel`; patrón visual de `DeleteActivityDialog` (`lib/features/activities/presentation/widgets/delete_activity_dialog.dart`); `AppButton` + `AppButtonVariant.outlined` / `AppButtonVariant.destructive`.
- Produces: `Future<bool> showEndProgramDialog({required BuildContext context, required String programName})` — devuelve `true` si el usuario confirma, `false`/`null→false` si cancela.

- [ ] **Step 1: Implement dialog** (calcar `DeleteActivityDialog.show`, cambiando textos)

```dart
// lib/core/widgets/common/end_program_dialog.dart
import 'package:flutter/material.dart';

import '../../theme/theme.dart';
import '../../../l10n/app_localizations.dart';
import '../buttons/app_button.dart';

/// Confirmación para terminar (archivar) un programa. Conserva el progreso.
/// Devuelve true si el usuario confirma.
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
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppSpacing.s16)),
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.s24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(l10n.endProgramTitle,
                  style: AppTypography.bodyLarge.copyWith(color: colors.textPrimary),
                  textAlign: TextAlign.center),
              const SizedBox(height: AppSpacing.s8),
              Text(l10n.endProgramMessage(programName),
                  style: AppTypography.bodySmall.copyWith(color: colors.textSecondary),
                  textAlign: TextAlign.center),
              const SizedBox(height: AppSpacing.s24),
              Row(
                children: [
                  Expanded(
                    child: AppButton(
                      label: l10n.cancel,
                      variant: AppButtonVariant.outlined,
                      onPressed: () => Navigator.of(context).pop(false),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.s8),
                  Expanded(
                    child: AppButton(
                      label: l10n.endProgramConfirm,
                      variant: AppButtonVariant.destructive,
                      onPressed: () => Navigator.of(context).pop(true),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      );
    },
  );
  return result ?? false;
}
```

> Verificar la firma real de `AppButton` (props `label`, `variant`, `onPressed`) en `lib/core/widgets/buttons/app_button.dart` y ajustar (el informe confirma `AppButtonVariant.outlined` y `.destructive`).

- [ ] **Step 2: Write widget test** (verifica que confirmar devuelve true)

```dart
// test/features/training/end_program_dialog_test.dart
// Bombear un Scaffold con un botón que llame showEndProgramDialog y guarde el resultado.
// tester.tap del botón → pumpAndSettle → tap en "Terminar" → expect result == true.
// Repetir tap en "Cancelar" → expect result == false.
```

- [ ] **Step 3: Run test**

Run: `flutter test test/features/training/end_program_dialog_test.dart`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/core/widgets/common/end_program_dialog.dart test/features/training/end_program_dialog_test.dart
git commit -m "feat(entreno): dialogo de confirmacion terminar programa"
```

---

### Task 6: Menú de acciones del programa (kebab ⋮)

**Files:**
- Create: `lib/features/training/presentation/widgets/program_actions_menu.dart`
- Test: `test/features/training/program_actions_menu_test.dart`

**Interfaces:**
- Consumes: callbacks `VoidCallback onViewProgram`, `onReplaceProgram`, `onEndProgram`; `S.viewProgram/replaceProgram/endProgram`; patrón `PopupMenuButton` con `Icons.more_vert`.
- Produces: `class ProgramActionsMenu extends StatelessWidget`:
  ```dart
  const ProgramActionsMenu({
    super.key,
    required this.onViewProgram,
    required this.onReplaceProgram,
    required this.onEndProgram,
  });
  ```
  Un `PopupMenuButton<_ProgramAction>` con icono `Icons.more_vert` y 3 items; "Terminar" en `colors.destructive`.

- [ ] **Step 1: Implement widget**

```dart
// lib/features/training/presentation/widgets/program_actions_menu.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../l10n/app_localizations.dart';

enum _ProgramAction { view, replace, end }

class ProgramActionsMenu extends StatelessWidget {
  const ProgramActionsMenu({
    super.key,
    required this.onViewProgram,
    required this.onReplaceProgram,
    required this.onEndProgram,
  });

  final VoidCallback onViewProgram;
  final VoidCallback onReplaceProgram;
  final VoidCallback onEndProgram;

  @override
  Widget build(BuildContext context) {
    final l10n = S.of(context);
    final colors = context.colors;
    return PopupMenuButton<_ProgramAction>(
      icon: Icon(Icons.more_vert, color: colors.textSecondary),
      color: colors.bgSurface2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMedium),
        side: BorderSide(color: colors.strokeDivider),
      ),
      onSelected: (action) {
        switch (action) {
          case _ProgramAction.view: onViewProgram();
          case _ProgramAction.replace: onReplaceProgram();
          case _ProgramAction.end: onEndProgram();
        }
      },
      itemBuilder: (context) => [
        PopupMenuItem(value: _ProgramAction.view,
          child: Text(l10n.viewProgram,
            style: AppTypography.bodyMedium.copyWith(color: colors.textPrimary))),
        PopupMenuItem(value: _ProgramAction.replace,
          child: Text(l10n.replaceProgram,
            style: AppTypography.bodyMedium.copyWith(color: colors.textPrimary))),
        PopupMenuItem(value: _ProgramAction.end,
          child: Text(l10n.endProgram,
            style: AppTypography.bodyMedium.copyWith(color: colors.destructive))),
      ],
    );
  }
}
```

- [ ] **Step 2: Widget test** — abrir el menú y verificar que aparecen los 3 labels y que tocar cada uno dispara su callback.

```dart
// test/features/training/program_actions_menu_test.dart
// Render ProgramActionsMenu con 3 flags booleanas en callbacks.
// tester.tap(find.byIcon(Icons.more_vert)); pumpAndSettle();
// expect(find.text('Ver programa'), findsOneWidget); etc.
// tap en 'Terminar programa' → expect endTapped == true.
```

- [ ] **Step 3: Run test**

Run: `flutter test test/features/training/program_actions_menu_test.dart`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/program_actions_menu.dart test/features/training/program_actions_menu_test.dart
git commit -m "feat(entreno): menu de acciones del programa (kebab)"
```

---

### Task 7: Fila de header (selector + kebab) con lógica de acciones

**Files:**
- Create: `lib/features/training/presentation/widgets/program_header_row.dart`
- Test: `test/features/training/program_header_row_test.dart`

**Interfaces:**
- Consumes: `ProgramSelectorButton` (Task 4), `ProgramActionsMenu` (Task 6), `showEndProgramDialog` (Task 5); providers `trainingContentNotifierProvider`, `selectedSubscriptionIndexProvider`, `selectedSubscriptionProvider`, `hasActiveSubscriptionsNotifierProvider`, `trainingRepositoryProvider` (`.archiveProgram`); rutas `AppRoutes.programsCatalog`, `AppRoutes.programDetail`.
- Produces: `class ProgramHeaderRow extends ConsumerWidget` con `const ProgramHeaderRow({super.key, required this.subscriptions})` (`final List<SubscriptionDetail> subscriptions;`). Compone la fila y contiene los handlers de navegación/gestión.

- [ ] **Step 1: Implement widget con handlers**

```dart
// lib/features/training/presentation/widgets/program_header_row.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/theme/theme.dart';
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
          onViewProgram: () {
            if (current != null) {
              context.push(AppRoutes.programDetail, extra: current.programId);
            }
          },
          onReplaceProgram: () => _replaceProgram(context, ref, current),
          onEndProgram: () => _endProgram(context, ref, current),
        ),
      ],
    );
  }

  Future<void> _endProgram(
      BuildContext context, WidgetRef ref, SubscriptionDetail? sub) async {
    if (sub == null) return;
    final confirmed = await showEndProgramDialog(
        context: context, programName: sub.programName);
    if (!confirmed) return;
    await ref.read(trainingRepositoryProvider).archiveProgram(sub.id);
    ref.read(selectedSubscriptionIndexProvider.notifier).state = 0;
    ref.invalidate(trainingContentNotifierProvider);
    ref.invalidate(hasActiveSubscriptionsNotifierProvider);
  }

  Future<void> _replaceProgram(
      BuildContext context, WidgetRef ref, SubscriptionDetail? sub) async {
    if (sub == null) return;
    // Reemplazar = archivar el actual (conserva progreso) y elegir uno nuevo
    // en el catálogo. (El endpoint v2 /replace no está cableado en la app.)
    final confirmed = await showEndProgramDialog(
        context: context, programName: sub.programName);
    if (!confirmed) return;
    await ref.read(trainingRepositoryProvider).archiveProgram(sub.id);
    ref.read(selectedSubscriptionIndexProvider.notifier).state = 0;
    ref.invalidate(trainingContentNotifierProvider);
    ref.invalidate(hasActiveSubscriptionsNotifierProvider);
    if (context.mounted) context.push(AppRoutes.programsCatalog);
  }
}
```

> Nota de diseño: "Reemplazar" reutiliza el diálogo de terminar (misma consecuencia: se archiva el actual). Si se quiere un copy propio, usar `S.replaceProgramTitle/Message/Confirm` con un diálogo hermano. Para MVP se acepta reutilizar. Verificar firma `archiveProgram(int id, {bool keepProgress = true})` — por defecto archiva conservando progreso (repo interface L102).

- [ ] **Step 2: Widget test con overrides** (patrón `marcas_section_test.dart`)

```dart
// test/features/training/program_header_row_test.dart
// ProviderScope(overrides: [
//   trainingContentNotifierProvider.overrideWith(...),  // 2 subs
//   selectedSubscriptionIndexProvider / selectedSubscriptionProvider según haga falta
// ]) → MaterialApp(theme: AppTheme.dark(), home: Scaffold(body: ProgramHeaderRow(subscriptions: subs)))
// Verificar: aparece el título "Nombre - N días", y el icono more_vert.
// tap more_vert → pumpAndSettle → find.text('Ver programa') findsOneWidget.
```

- [ ] **Step 3: Run test**

Run: `flutter test test/features/training/program_header_row_test.dart`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/program_header_row.dart test/features/training/program_header_row_test.dart
git commit -m "feat(entreno): fila de header con selector y gestion de programa"
```

---

### Task 8: Card héroe = siguiente entreno sobre imagen del programa

**Files:**
- Create: `lib/features/training/presentation/widgets/next_training_hero_card.dart`
- Test: `test/features/training/next_training_hero_card_preview_test.dart`

**Interfaces:**
- Consumes: `SubscriptionDetail` (`programImageUrl`), `TrainingDay` (`displayName`, `trainingType`, `totalExercises`); `AnimatedNetworkImage`, `AppEffects.gradientBlack`, `S.nextWorkout/train/exercise/exercises`; callback `VoidCallback onStartTraining`.
- Produces: `class NextTrainingHeroCard extends StatelessWidget`:
  ```dart
  const NextTrainingHeroCard({
    super.key,
    required this.subscription,
    required this.trainingDay,
    required this.onStartTraining,
  });
  ```
  Card con la imagen del programa a sangre + gradiente (base de `_ActiveProgramCard`), badge "PRÓXIMO ENTRENO" (verde) arriba-izquierda, y sobre el gradiente inferior: nombre del día (`displayName`), meta (`trainingType` + `totalExercises` ejercicios), y **botón verde sólido "Entrenar →"** (mismo estilo que `NextTrainingCard` ya redisñada).

- [ ] **Step 1: Implement widget** (combina imagen de `_ActiveProgramCard` + contenido/botón de `NextTrainingCard`)

```dart
// lib/features/training/presentation/widgets/next_training_hero_card.dart
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../core/widgets/images/animated_network_image.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/entities/subscription_detail.dart';

/// Card héroe única de la pantalla Entreno: la sesión que toca ("siguiente
/// entreno") sobre la imagen del programa, con botón verde sólido.
class NextTrainingHeroCard extends StatelessWidget {
  const NextTrainingHeroCard({
    super.key,
    required this.subscription,
    required this.trainingDay,
    required this.onStartTraining,
  });

  final SubscriptionDetail subscription;
  final TrainingDay trainingDay;
  final VoidCallback onStartTraining;

  @override
  Widget build(BuildContext context) {
    final l10n = S.of(context);
    final colors = context.colors;
    final focus = trainingDay.trainingType;
    final count = trainingDay.totalExercises;

    return ClipRRect(
      borderRadius: BorderRadius.circular(AppSpacing.s16),
      child: SizedBox(
        height: 300,
        child: Stack(
          fit: StackFit.expand,
          children: [
            if (subscription.programImageUrl != null)
              AnimatedNetworkImage(
                imageUrl: subscription.programImageUrl!,
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
            // Badge
            Positioned(
              top: AppSpacing.s16, left: AppSpacing.s16,
              child: Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.s16, vertical: AppSpacing.s6),
                decoration: BoxDecoration(
                  color: colors.brandPrimary,
                  borderRadius: BorderRadius.circular(100),
                ),
                child: Text(
                  l10n.nextWorkout.replaceAll(':', '').toUpperCase(),
                  style: AppTypography.bodyXSmallBold.copyWith(
                      color: colors.brandText, letterSpacing: 0.5),
                ),
              ),
            ),
            // Contenido inferior
            Positioned(
              left: AppSpacing.s16, right: AppSpacing.s16, bottom: AppSpacing.s16,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    trainingDay.displayName,
                    style: AppTypography.bodyLarge.copyWith(
                        color: colors.brandTextInverse, fontSize: 24),
                  ),
                  const SizedBox(height: AppSpacing.s4),
                  Text(
                    [
                      if (focus != null && focus.isNotEmpty) focus,
                      '$count ${count == 1 ? l10n.exercise : l10n.exercises}',
                    ].join(' · '),
                    style: AppTypography.bodySmall.copyWith(
                        color: colors.brandTextInverse.withValues(alpha: 0.85)),
                  ),
                  const SizedBox(height: AppSpacing.s16),
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: Material(
                      color: colors.brandPrimary,
                      borderRadius: BorderRadius.circular(AppSpacing.s8),
                      child: InkWell(
                        onTap: onStartTraining,
                        borderRadius: BorderRadius.circular(AppSpacing.s8),
                        child: Center(
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(l10n.train,
                                  style: AppTypography.bodyMediumBold
                                      .copyWith(color: colors.brandText)),
                              const SizedBox(width: AppSpacing.s6),
                              Icon(Icons.arrow_forward,
                                  size: 18, color: colors.brandText),
                            ],
                          ),
                        ),
                      ),
                    ),
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

> Verificar el nombre del método de alpha (`withValues(alpha:)` en Flutter reciente vs `withOpacity`) según la versión del repo — usar el que ya use `_ActiveProgramCard`. En golden test, `programImageUrl` null → cae al `Container` de color (la red no carga en test).

- [ ] **Step 2: Golden test** (dark + light; imageUrl null para render determinista)

```dart
// test/features/training/next_training_hero_card_preview_test.dart
// (copiar _loadFonts / _pump; surface 390x360)
// sub con programImageUrl: null; day con trainingType 'Tren superior' y 6 exercises.
// expectLater → goldens/hero_card_<theme>.png
```

- [ ] **Step 3: Generate & verify**

Run: `flutter test test/features/training/next_training_hero_card_preview_test.dart --update-goldens`
Expected: PASS; abrir `hero_card_dark.png` → badge verde, título del día, meta, botón verde "Entrenar →".

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/widgets/next_training_hero_card.dart test/features/training/next_training_hero_card_preview_test.dart test/features/training/goldens/hero_card_*.png
git commit -m "feat(entreno): card heroe del siguiente entreno sobre imagen del programa"
```

---

### Task 9: Integración en MainEntrenoScreen

**Files:**
- Modify: `lib/features/training/presentation/screens/main_entreno_screen.dart:206-275` (`_ProgramsTab`)
- Test: manual en simulador (ver Task 10) + análisis estático.

**Interfaces:**
- Consumes: `ProgramHeaderRow` (Task 7), `WeeklyProgressBar` (Task 3), `NextTrainingHeroCard` (Task 8), `selectedCurrentWeekProvider` (Task 1), `selectedNextTrainingDayWithWeekProvider`, `selectedSubscriptionProvider`.
- Produces: `_ProgramsTab` renderiza header → weekly progress → hero card → `_PreviousRecordsSection`.

- [ ] **Step 1: Editar `_ProgramsTab.build`** — reemplazar el bloque `ActiveProgramsSection(...)` (L237–240) y `_NextTrainingSection` (L259) por la nueva composición. Conservar el branch `isSelectedCompleted → ProgramCompletedCard`.

Reemplazar el `Column(children: [...])` interno (L231–270) por:

```dart
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: AppSpacing.s16),

            if (content.subscriptions.isNotEmpty) ...[
              // Header: título-programa (dropdown) + kebab de gestión
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: AppSpacing.s16),
                child: ProgramHeaderRow(subscriptions: content.subscriptions),
              ),
              const SizedBox(height: AppSpacing.s12),

              // Progreso semanal
              Consumer(builder: (context, ref, _) {
                final week = ref.watch(selectedCurrentWeekProvider);
                if (week == null || week.totalDays == 0) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: AppSpacing.s16),
                  child: WeeklyProgressBar(week: week),
                );
              }),
              const SizedBox(height: AppSpacing.s16),

              if (isSelectedCompleted) ...[
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: AppSpacing.s16),
                  child: ProgramCompletedCard(
                    subscriptionId: selectedSubscription!.id,
                    programId: selectedSubscription.programId,
                    programName: selectedSubscription.programName,
                    location: selectedSubscription.location.apiValue,
                  ),
                ),
              ] else ...[
                // Card héroe = siguiente entreno
                Consumer(builder: (context, ref, _) {
                  final sub = ref.watch(selectedSubscriptionProvider);
                  final nextInfo = ref.watch(selectedNextTrainingDayWithWeekProvider);
                  if (sub == null || nextInfo == null) {
                    return const NoNextTrainingCard();
                  }
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: AppSpacing.s16),
                    child: NextTrainingHeroCard(
                      subscription: sub,
                      trainingDay: nextInfo.day,
                      onStartTraining: () {
                        context.push(AppRoutes.trainingDay, extra: {
                          'trainingDay': nextInfo.day,
                          'totalDaysInWeek': nextInfo.totalDaysInWeek,
                          'subscriptionId': sub.id,
                          'weekNumber': nextInfo.weekNumber,
                        });
                      },
                    ),
                  );
                }),

                const SizedBox(height: AppSpacing.s24),

                // Tus marcas (sin cambios)
                _PreviousRecordsSection(ref: ref),
              ],
            ],

            SizedBox(height: MediaQuery.of(context).padding.bottom + 80),
          ],
        ),
```

Añadir imports al principio del archivo:
```dart
import '../widgets/program_header_row.dart';
import '../widgets/weekly_progress_bar.dart';
import '../widgets/next_training_hero_card.dart';
import '../providers/current_week_provider.dart';
```
Retirar los imports/usos de `ActiveProgramsSection` y `NextTrainingCard` si quedan sin usar (dejar `NoNextTrainingCard` que sigue usándose). `flutter analyze` avisará de imports sin uso.

- [ ] **Step 2: Análisis estático**

Run: `cd /Users/kataiturriaga/repos/elmetodo_app && flutter analyze lib/features/training/presentation/screens/main_entreno_screen.dart`
Expected: `No issues found!` (corregir imports sin usar si los marca).

- [ ] **Step 3: Verificar que compila el árbol de training**

Run: `flutter analyze lib/features/training`
Expected: sin errores.

- [ ] **Step 4: Commit**

```bash
git add lib/features/training/presentation/screens/main_entreno_screen.dart
git commit -m "feat(entreno): integrar header + progreso semanal + card heroe en la pantalla"
```

---

### Task 10: Verificación visual en simulador

**Files:** ninguno (verificación).

- [ ] **Step 1: Lanzar la app en el simulador contra dev**

Run (background): `cd /Users/kataiturriaga/repos/elmetodo_app && flutter run -d <sim-id> --dart-define=APP_ENV=development`

- [ ] **Step 2: Iniciar sesión con un usuario dev con ≥1 programa activo**

Usuario de prueba con programas: `ana.garcia.test@mailinator.com` / `Test1234!` (tiene 10 subscripciones — ver memoria `reference_db_prod`). Navegar al tab Entreno.

- [ ] **Step 3: Checklist visual**
  - [ ] El tab "Entreno / Seguimiento" sigue arriba.
  - [ ] Debajo, el título del programa "Nombre - N días ▾" a la izquierda; ⋮ a la derecha.
  - [ ] Tocar el título abre el menú con las subscripciones + "＋ Añadir programa"; cambiar de programa actualiza la card.
  - [ ] Tocar ⋮ muestra Ver / Reemplazar / Terminar; "Terminar" pide confirmación y conserva historial.
  - [ ] Barra de progreso + **"Semana N · X de N entrenos"** con el conteo correcto de la semana **del programa** (no del calendario).
  - [ ] Card héroe con imagen del programa + "PRÓXIMO ENTRENO" + día + botón verde "Entrenar →"; el botón navega a la sesión.
  - [ ] "Tus marcas" intacto debajo.

- [ ] **Step 4: Capturar pantalla y adjuntar al caso de estudio**

`xcrun simctl io <sim-id> screenshot <ruta>` y guardar referencia en `casos-de-estudio/entreno-arquitectura-dos-cards.md` §G.

---

## FASE 2 — Scroll horizontal entre días de la semana (posterior, opcional)

> **Decisión de diseño pendiente de validar con usuarios** (documentada en el caso de estudio §G): al deslizar la card a otro día de la semana, ¿el botón "Entrenar" cambia a ese día? ¿Los días completados muestran estado "Completado" + opción repetir? Riesgo principal: **descubribilidad del gesto** (necesita peek del día siguiente + dots).

**Esbozo (no desglosado en pasos hasta validar):**
- Convertir la card héroe en un `PageView` sobre `selectedCurrentWeekProvider.days`, con `PageController(initialPage: indexOf(nextTrainingDay))`.
- Añadir **affordance**: dots debajo (uno por día, verde=completado, resaltado=actual) y/o peek del borde del día siguiente.
- Estado por día: pendiente → botón "Entrenar"; completado → estado "Completado ✓" + acción secundaria "Repetir".
- Golden tests por estado (pendiente/completado, primer/último día).

---

## Self-Review

**Cobertura del spec (decisión de Kata + maqueta):**
- Título-programa con dropdown ✅ Task 4 + 7. "Añadir programa" ✅ (onAddProgram → catálogo).
- Menú ⋮ Ver / Reemplazar / Terminar ✅ Task 6 + 7. Confirmación destructiva ✅ Task 5.
- Progreso de la semana **del programa** "Semana 1 · 0 de 6 entrenos" ✅ Task 1 + 3 (semántica verificada en front y API: no hay semana natural).
- Card héroe única = siguiente entreno sobre imagen, botón verde ✅ Task 8.
- Tab bar conservado, "Tus marcas" conservado ✅ Task 9.
- Scroll de días ✅ diferido a Fase 2 (documentado).

**Type consistency:** `selectedCurrentWeekProvider` (`TrainingWeek?`) usado igual en Task 3/9. `ProgramSelectorButton`/`ProgramActionsMenu`/`NextTrainingHeroCard`/`ProgramHeaderRow` firmas idénticas entre su definición y su uso en Task 7/9. `showEndProgramDialog(context:, programName:) → Future<bool>` usado consistente en Task 7. `archiveProgram(id, {keepProgress=true})` conserva progreso (default) — coherente con "Terminar" no destructivo.

**Placeholders:** los tests de Task 5/6/7 describen el escenario en comentario en vez de código completo (widget tests de interacción); el implementador debe escribir el `tester.tap`/`expect` siguiendo el patrón de `marcas_section_test.dart`. Los constructores de fixtures (`SubscriptionDetail`, `TrainingWeek`) deben verificarse contra `domain/entities/subscription_detail.dart` (parámetros `required` reales) — señalado en Task 1.

**Riesgos abiertos:**
1. Constructores exactos de las entidades de dominio (verificar `required` reales antes de escribir fixtures).
2. `AppSpacing.radiusMedium` / `AppSpacing.s12` — confirmar que existen (si no, usar `s8`/`s16`).
3. `withValues(alpha:)` vs `withOpacity` según versión de Flutter del repo.
4. Firma de `AppButton` (props exactas).

---

## Materiales de referencia

- Caso de estudio: `casos-de-estudio/entreno-arquitectura-dos-cards.md` (§G = decisión final).
- Prototipos: `entreno-una-card.html`, `entreno-selector-programa.html` (opción 2 elegida).
- Informe API (endpoints, gaps): resumen en el caso de estudio — sin backend nuevo para Fase 1.
- Rama: `ux/entreno-card-siguiente-v-b` (ya con `next_training_card.dart` verde + golden).
