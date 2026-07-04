# Score de Fuerza — Endpoints completos + Conexión Flutter

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extender la API con los datos que necesitan las pantallas de detalle y conectar la app Flutter a datos reales, eliminando todos los datos hardcodeados.

**Architecture:** Dos repos en paralelo. En `elmetodo_api` (FastAPI): extender `GET /score` con métricas derivadas y añadir dos endpoints nuevos (`GET /score/groups/{group}` y `GET /score/exercises/{exercise_id}`). En `elmetodo_app` (Flutter): capa de datos (entidades + repositorio + providers Riverpod) que consume esos endpoints, y pantallas que los consumen via `AsyncValue`.

**Tech Stack:** Python 3.13 / FastAPI / SQLAlchemy 2.x / Pydantic v2 (API). Flutter / Riverpod (`@riverpod` annotation) / Dio / `riverpod_annotation` (app).

## Global Constraints

- API: rama nueva sobre `main` (después del merge de PR #129). NUNCA a `main` directamente.
- Flutter: rama nueva sobre `main` (después del merge de PR #1). NUNCA a `main` directamente.
- Convención tests API: sin mocks de BD — tests de integración con BD real (harness Docker). Tests puros con `--noconftest`.
- Convención Flutter: misma estructura que `lib/features/ranking/` (entidades plain Dart + `fromJson`, repositorio impl + interfaz, providers `@riverpod`).
- `score_math.LEVELS`: `[(0,'Principiante'),(50,'Novato'),(100,'Experimentado'),(150,'Pro'),(200,'Atleta'),(250,'Élite'),(300,'Olímpico')]`. Los umbrales son el límite inferior de cada nivel.
- `elmetodo_api` usa `uv run pytest`. `elmetodo_app` usa `flutter test`.
- Ambos PRs van separados: uno para la API, otro para Flutter.

---

## Mapa de ficheros

### elmetodo_api
| Fichero | Acción | Responsabilidad |
|---|---|---|
| `app/services/score_math.py` | Modificar | Añadir `progress_within_level()` |
| `app/services/score_service.py` | Modificar | Añadir `weekly_delta()`, `group_detail()`, `exercise_detail()` |
| `app/schemas/score.py` | Modificar | Nuevos schemas: `ScoreGroupDetail` ampliado, `GroupDetailResponse`, `ExerciseDetailResponse` |
| `app/api/routes/mobile/score.py` | Modificar | Añadir 2 endpoints nuevos |
| `tests/test_score_math.py` | Modificar | Tests de `progress_within_level` |
| `tests/test_score_endpoints.py` | Modificar | Tests de los 2 endpoints nuevos |

### elmetodo_app
| Fichero | Acción | Responsabilidad |
|---|---|---|
| `lib/features/puntuaciones/domain/entities/score_entities.dart` | Crear | Entidades Dart: `ScoreData`, `ScoreGroup`, `ScoreHistoryPoint`, `GroupDetail`, `ExerciseDetail`, `PrRecord` |
| `lib/features/puntuaciones/domain/repositories/score_repository.dart` | Crear | Interfaz abstracta del repositorio |
| `lib/features/puntuaciones/data/repositories/score_repository_impl.dart` | Crear | Impl con Dio: llama a los 3 endpoints |
| `lib/core/config/api_config.dart` | Modificar | Añadir constantes de URLs de score |
| `lib/features/puntuaciones/presentation/providers/score_providers.dart` | Crear | Providers Riverpod: `scoreProvider`, `scoreHistoryProvider`, `groupDetailProvider`, `exerciseDetailProvider` |
| `lib/features/puntuaciones/presentation/screens/puntuacion_screen.dart` | Modificar | Consumir `scoreProvider` |
| `lib/features/puntuaciones/presentation/widgets/evolucion_fuerza_section.dart` | Modificar | Recibir datos reales del historial |
| `lib/features/puntuaciones/presentation/widgets/grupos_fuerza_grid.dart` | Modificar | Consumir grupos reales |
| `lib/features/puntuaciones/presentation/screens/grupo_detalle_screen.dart` | Modificar | Consumir `groupDetailProvider` |
| `lib/features/puntuaciones/presentation/screens/ejercicio_detalle_screen.dart` | Modificar | Consumir `exerciseDetailProvider` |

---

## Tarea 1 — `progress_within_level` en score_math (API)

**Ficheros:**
- Modificar: `app/services/score_math.py`
- Test: `tests/test_score_math.py`

**Produce:** `progress_within_level(score: float) -> tuple[float, int | None]`
- Devuelve `(pct, points_to_next)` donde `pct` es 0.0–1.0 (progreso dentro del nivel actual) y `points_to_next` es cuántos puntos faltan para el siguiente nivel (`None` si es Olímpico).

- [ ] **Escribe el test que falla**

```python
# En tests/test_score_math.py, añadir al final:

def test_progress_within_level_mitad():
    # Score 125 está en Experimentado (100–150). Mitad del tramo → 50%.
    pct, to_next = score_math.progress_within_level(125)
    assert pct == pytest.approx(0.5)
    assert to_next == 25

def test_progress_within_level_inicio_nivel():
    # Score 100 es el inicio exacto de Experimentado.
    pct, to_next = score_math.progress_within_level(100)
    assert pct == pytest.approx(0.0)
    assert to_next == 50

def test_progress_within_level_olimpico():
    # Nivel máximo: pct=1.0, sin siguiente nivel.
    pct, to_next = score_math.progress_within_level(310)
    assert pct == pytest.approx(1.0)
    assert to_next is None

def test_progress_within_level_principiante():
    # Score 30 en Principiante (0–50). 60% del tramo.
    pct, to_next = score_math.progress_within_level(30)
    assert pct == pytest.approx(0.6)
    assert to_next == 20
```

- [ ] **Corre el test para confirmar que falla**

```bash
cd /Users/kataiturriaga/repos/elmetodo_api
LC_ALL="en_US.UTF-8" uv run pytest tests/test_score_math.py::test_progress_within_level_mitad -v --noconftest
```
Esperado: `FAILED` con `AttributeError: module 'app.services.score_math' has no attribute 'progress_within_level'`

- [ ] **Implementa la función**

En `app/services/score_math.py`, añadir después de `level_name()`:

```python
def progress_within_level(score: float) -> tuple[float, int | None]:
    """Progreso (0–1) dentro del nivel actual y puntos para el siguiente.

    Devuelve (pct, points_to_next). Si el score está en el nivel máximo
    (Olímpico, ≥300), devuelve (1.0, None).
    """
    # Encontrar el nivel actual y el siguiente.
    current_floor = LEVELS[0][0]
    next_floor: int | None = None
    for i, (threshold, _) in enumerate(LEVELS):
        if score >= threshold:
            current_floor = threshold
            next_floor = LEVELS[i + 1][0] if i + 1 < len(LEVELS) else None
        else:
            break

    if next_floor is None:
        return (1.0, None)

    pct = (score - current_floor) / (next_floor - current_floor)
    points_to_next = int(next_floor - score)
    return (min(pct, 1.0), max(points_to_next, 0))
```

- [ ] **Corre todos los tests nuevos**

```bash
LC_ALL="en_US.UTF-8" uv run pytest tests/test_score_math.py -v --noconftest
```
Esperado: todos en verde.

- [ ] **Commit**

```bash
cd /Users/kataiturriaga/repos/elmetodo_api
git add app/services/score_math.py tests/test_score_math.py
git commit -m "feat(score): progress_within_level — pct + points_to_next dentro del nivel"
```

---

## Tarea 2 — Extender `GET /score` con métricas derivadas (API)

**Ficheros:**
- Modificar: `app/schemas/score.py` — añadir campos a `ScoreGroupDetail` y `ScoreResponse`
- Modificar: `app/services/score_service.py` — calcular `weekly_delta`, `progress_pct`, `points_to_next`
- Modificar: `app/api/routes/mobile/score.py` — rellenar los campos nuevos

**Consume:** `score_math.progress_within_level()` (Tarea 1)

**Produce:** `GET /score` devuelve también:
- `weekly_delta: float | None` — diferencia de score vs hace 7 días
- En cada grupo: `progress_pct: float`, `points_to_next: int | None`

- [ ] **Escribe los tests que fallan**

```python
# En tests/test_score_endpoints.py, añadir en TestGetScore:

def test_respuesta_incluye_weekly_delta(self, test_client, db_session: Session):
    u = _user(db_session, "score_delta@test.com")
    _questionnaire(db_session, u.id)
    resp = test_client.get("/api/score", headers=_headers(u))
    body = resp.json()
    # weekly_delta puede ser None (sin historial) pero el campo debe existir.
    assert "weekly_delta" in body

def test_grupos_incluyen_progress_pct(self, test_client, db_session: Session):
    u = _user(db_session, "score_pct@test.com")
    _questionnaire(db_session, u.id)
    resp = test_client.get("/api/score", headers=_headers(u))
    body = resp.json()
    # Con 0 grupos cubiertos no hay grupos en la respuesta; el campo existe
    # a nivel de schema pero la lista estará vacía.
    assert "groups" in body
```

- [ ] **Actualiza el schema** en `app/schemas/score.py`

Sustituir `ScoreGroupDetail` y `ScoreResponse` por:

```python
class ScoreGroupDetail(BaseModel):
    muscle_group: str
    score: Optional[float] = None
    level: Optional[str] = None
    progress_pct: Optional[float] = None   # 0.0–1.0 dentro del nivel actual
    points_to_next: Optional[int] = None   # puntos para el siguiente nivel


class ScoreResponse(BaseModel):
    total_score: Optional[float] = None
    level: str
    groups_covered: int
    total_groups: int
    coverage_note: Optional[str] = None
    bodyweight: Optional[float] = None
    weekly_delta: Optional[float] = None   # cambio de score en últimos 7 días
    missing: list[str] = []
    groups: list[ScoreGroupDetail] = []
```

- [ ] **Añade `weekly_delta` al service** en `app/services/score_service.py`

Añadir después de `has_snapshots()`:

```python
def weekly_delta(db: Session, user_id: int) -> Optional[float]:
    """Diferencia de score total entre hoy y hace 7 días.

    Busca el snapshot más reciente antes de hace 7 días y lo compara con
    el más reciente de hoy. Devuelve None si no hay suficientes datos.
    """
    now = datetime.now(tz=timezone.utc)
    week_ago = now - timedelta(days=7)

    latest = (
        db.query(ScoreSnapshot)
        .filter(ScoreSnapshot.user_id == user_id, ScoreSnapshot.total_score.isnot(None))
        .order_by(ScoreSnapshot.computed_at.desc())
        .first()
    )
    week_ago_snap = (
        db.query(ScoreSnapshot)
        .filter(
            ScoreSnapshot.user_id == user_id,
            ScoreSnapshot.total_score.isnot(None),
            ScoreSnapshot.computed_at <= week_ago,
        )
        .order_by(ScoreSnapshot.computed_at.desc())
        .first()
    )
    if not latest or not week_ago_snap:
        return None
    return latest.total_score - week_ago_snap.total_score
```

- [ ] **Actualiza el endpoint** en `app/api/routes/mobile/score.py`

En `get_score()`, reemplazar la construcción de `groups` y el `return`:

```python
    groups_raw: dict = result.get("groups") or {}
    groups = []
    for mg, info in groups_raw.items():
        score_val = info.get("score")
        pct, to_next = (
            score_math.progress_within_level(score_val)
            if score_val is not None
            else (None, None)
        )
        groups.append(ScoreGroupDetail(
            muscle_group=mg,
            score=score_val,
            level=info.get("level"),
            progress_pct=pct,
            points_to_next=to_next,
        ))

    delta = score_service.weekly_delta(db, current_user.id)

    # ... (el resto igual, añadir weekly_delta al return)
    return ScoreResponse(
        total_score=result.get("total_score"),
        level=result.get("level", "—"),
        groups_covered=covered,
        total_groups=total,
        coverage_note=coverage_note,
        bodyweight=result.get("bodyweight"),
        weekly_delta=delta,
        missing=result.get("missing", []),
        groups=groups,
    )
```

Añadir el import al inicio del fichero:
```python
from app.services import score_math
```

- [ ] **Corre los tests**

```bash
LC_ALL="en_US.UTF-8" uv run pytest tests/test_score_math.py tests/test_score_service.py -v --noconftest
```
Esperado: todos en verde.

- [ ] **Commit**

```bash
git add app/schemas/score.py app/services/score_service.py app/api/routes/mobile/score.py tests/test_score_endpoints.py
git commit -m "feat(score): GET /score añade weekly_delta, progress_pct y points_to_next por grupo"
```

---

## Tarea 3 — `GET /score/groups/{muscle_group}` (API)

**Ficheros:**
- Modificar: `app/schemas/score.py` — añadir `ExerciseInGroup`, `GroupDetailResponse`
- Modificar: `app/services/score_service.py` — añadir `group_detail()`
- Modificar: `app/api/routes/mobile/score.py` — añadir endpoint
- Modificar: `tests/test_score_endpoints.py`

**Produce:** `GET /score/groups/{muscle_group}` con:
```json
{
  "muscle_group": "pectorales",
  "score": 118,
  "level": "Experimentado",
  "progress_pct": 0.36,
  "points_to_next": 32,
  "delta_3m": 14.0,
  "exercises": [
    {"exercise_id": 5, "name": "Press banca", "best_mark": "96 kg", "is_anchor": true},
    {"exercise_id": 12, "name": "Press inclinado", "best_mark": "80 kg", "is_anchor": false}
  ],
  "history": [
    {"computed_at": "2026-05-01T12:00:00Z", "score": 104.0},
    {"computed_at": "2026-06-01T12:00:00Z", "score": 118.0}
  ]
}
```

- [ ] **Añade los schemas** en `app/schemas/score.py`

```python
class ExerciseInGroup(BaseModel):
    exercise_id: int
    name: str
    best_mark: Optional[str] = None   # "96 kg" / "90 kg × 3" / None si sin datos
    is_anchor: bool


class GroupDetailResponse(BaseModel):
    muscle_group: str
    score: Optional[float] = None
    level: str
    progress_pct: Optional[float] = None
    points_to_next: Optional[int] = None
    delta_3m: Optional[float] = None       # cambio de score en 3 meses
    exercises: list[ExerciseInGroup] = []
    history: list[ScoreHistoryPoint] = []  # evolución del score de este grupo
```

- [ ] **Escribe el test que falla**

```python
# En tests/test_score_endpoints.py, nueva clase al final:

class TestGroupDetail:
    def test_grupo_no_existente_devuelve_404(self, test_client, db_session: Session):
        u = _user(db_session, "grp_404@test.com")
        resp = test_client.get("/api/score/groups/inexistente", headers=_headers(u))
        assert resp.status_code == 404

    def test_grupo_existente_devuelve_200_con_campos(self, test_client, db_session: Session):
        u = _user(db_session, "grp_ok@test.com")
        _questionnaire(db_session, u.id)
        # "pectorales" es un grupo válido en score_exercise_muscle_groups
        resp = test_client.get("/api/score/groups/pectorales", headers=_headers(u))
        assert resp.status_code == 200
        body = resp.json()
        for key in ("muscle_group", "level", "exercises", "history", "delta_3m"):
            assert key in body

    def test_requiere_autenticacion(self, test_client):
        resp = test_client.get("/api/score/groups/pectorales")
        assert resp.status_code == 401
```

- [ ] **Corre los tests para confirmar que fallan**

```bash
LC_ALL="en_US.UTF-8" uv run pytest tests/test_score_endpoints.py::TestGroupDetail -v --noconftest
```
Esperado: `FAILED` con `404` (el endpoint no existe aún, FastAPI devuelve 404).

- [ ] **Añade `group_detail()` al service** en `app/services/score_service.py`

```python
def group_detail(db: Session, user_id: int, muscle_group: str, today: Optional[date] = None) -> Optional[dict]:
    """Datos completos de un grupo muscular para la pantalla de detalle.

    Devuelve None si el grupo no existe en el catálogo curado.
    """
    today = today or date.today()
    since = today - timedelta(days=WINDOW_DAYS)
    since_3m = today - timedelta(days=90)

    # Verificar que el grupo existe en el catálogo.
    from app.models.exercise import Exercise
    rows = (
        db.query(
            ScoreExerciseMuscleGroup.exercise_id,
            ScoreExerciseMuscleGroup.is_anchor,
            Exercise.name,
        )
        .join(Exercise, ScoreExerciseMuscleGroup.exercise_id == Exercise.id)
        .filter(ScoreExerciseMuscleGroup.muscle_group == muscle_group)
        .all()
    )
    if not rows:
        return None

    exercise_ids = [r[0] for r in rows]

    # Mejor 1RM por ejercicio en la ventana actual.
    best_1rm = _load_best_1rm_by_exercise(db, user_id, exercise_ids, since, until=today)
    bodyweight = _load_bodyweight(db, user_id, as_of=today)
    gender, age = _load_demographics(db, user_id, today)
    standards = _load_standards(db)

    # Score del grupo ahora.
    current_score: Optional[float] = None
    if bodyweight and gender:
        thresholds = standards.get((muscle_group, gender), [])
        if thresholds:
            best_for_group = max(
                (best_1rm.get(eid, 0) for eid, _, _ in rows),
                default=0,
            )
            if best_for_group > 0:
                from app.services import score_math
                coef = score_math.age_coefficient(age) if age else 1.0
                rel = score_math.relative_strength(best_for_group, bodyweight) * coef
                current_score = score_math.score_from_ratio(rel, thresholds)

    # Score del grupo hace 3 meses (para delta).
    score_3m: Optional[float] = None
    if bodyweight and gender:
        best_3m = _load_best_1rm_by_exercise(db, user_id, exercise_ids, since_3m - timedelta(days=WINDOW_DAYS), until=since_3m)
        thresholds = standards.get((muscle_group, gender), [])
        if thresholds and best_3m:
            best_for_group_3m = max((best_3m.get(eid, 0) for eid, _, _ in rows), default=0)
            if best_for_group_3m > 0:
                from app.services import score_math
                coef = score_math.age_coefficient(age) if age else 1.0
                rel = score_math.relative_strength(best_for_group_3m, bodyweight) * coef
                score_3m = score_math.score_from_ratio(rel, thresholds)

    delta_3m = (current_score - score_3m) if (current_score is not None and score_3m is not None) else None

    # Lista de ejercicios con mejor marca formateada.
    from app.services.marca_value import format_weight
    exercises = []
    for eid, is_anchor, name in rows:
        one_rm = best_1rm.get(eid)
        mark = f"{one_rm:.0f} kg" if one_rm else None
        exercises.append({"exercise_id": eid, "name": name, "best_mark": mark, "is_anchor": bool(is_anchor)})
    exercises.sort(key=lambda e: (not e["is_anchor"], -(best_1rm.get(e["exercise_id"]) or 0)))

    # Historial del grupo desde snapshots (campo breakdown JSON).
    history = []
    snaps = (
        db.query(ScoreSnapshot)
        .filter(ScoreSnapshot.user_id == user_id, ScoreSnapshot.breakdown.isnot(None))
        .order_by(ScoreSnapshot.computed_at.asc())
        .all()
    )
    for s in snaps:
        group_data = (s.breakdown or {}).get(muscle_group)
        if group_data and group_data.get("score") is not None:
            history.append({"computed_at": s.computed_at, "score": group_data["score"]})

    from app.services import score_math as sm
    level = sm.level_name(current_score)
    pct, to_next = sm.progress_within_level(current_score) if current_score is not None else (None, None)

    return {
        "muscle_group": muscle_group,
        "score": current_score,
        "level": level,
        "progress_pct": pct,
        "points_to_next": to_next,
        "delta_3m": delta_3m,
        "exercises": exercises,
        "history": history,
    }
```

- [ ] **Añade el endpoint** en `app/api/routes/mobile/score.py`

```python
from fastapi import APIRouter, Depends, Query, HTTPException
# (añadir HTTPException al import existente)

from app.schemas.score import (
    ScoreGroupDetail, ScoreResponse, ScoreHistoryPoint, ScoreHistoryResponse,
    ExerciseInGroup, GroupDetailResponse,   # añadir
)

@router.get("/groups/{muscle_group}", response_model=GroupDetailResponse)
async def get_group_detail(
    muscle_group: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Datos completos de un grupo muscular: score, progreso, ejercicios e historial."""
    detail = score_service.group_detail(db, current_user.id, muscle_group)
    if detail is None:
        raise HTTPException(status_code=404, detail="Grupo muscular no encontrado en el catálogo")

    return GroupDetailResponse(
        muscle_group=detail["muscle_group"],
        score=detail["score"],
        level=detail["level"],
        progress_pct=detail["progress_pct"],
        points_to_next=detail["points_to_next"],
        delta_3m=detail["delta_3m"],
        exercises=[ExerciseInGroup(**e) for e in detail["exercises"]],
        history=[ScoreHistoryPoint(**h) for h in detail["history"]],
    )
```

- [ ] **Corre los tests**

```bash
LC_ALL="en_US.UTF-8" uv run pytest tests/test_score_endpoints.py -v --noconftest
```
Esperado: todos en verde.

- [ ] **Commit**

```bash
git add app/schemas/score.py app/services/score_service.py app/api/routes/mobile/score.py tests/test_score_endpoints.py
git commit -m "feat(score): GET /score/groups/{group} — detalle con ejercicios, delta y historial"
```

---

## Tarea 4 — `GET /score/exercises/{exercise_id}` (API)

**Ficheros:**
- Modificar: `app/schemas/score.py` — añadir `PrRecord`, `ExerciseDetailResponse`
- Modificar: `app/services/score_service.py` — añadir `exercise_detail()`
- Modificar: `app/api/routes/mobile/score.py` — añadir endpoint
- Modificar: `tests/test_score_endpoints.py`

**Produce:** `GET /score/exercises/{exercise_id}` con:
```json
{
  "exercise_id": 5,
  "name": "Press banca",
  "best_mark": "96 kg",
  "best_1rm": 96.0,
  "delta_3m_label": "+11 kg en 3 meses",
  "pr_history": [
    {"date": "2026-06-28", "weight_reps_label": "85 kg × 4", "projected_1rm": 96.0},
    {"date": "2026-06-07", "weight_reps_label": "78 kg × 5", "projected_1rm": 91.0}
  ],
  "history": [
    {"computed_at": "2026-05-01T12:00:00Z", "score": 85.0},
    {"computed_at": "2026-06-01T12:00:00Z", "score": 96.0}
  ]
}
```

- [ ] **Añade los schemas** en `app/schemas/score.py`

```python
class PrRecord(BaseModel):
    date: date
    weight_reps_label: str    # "85 kg × 4"
    projected_1rm: float


class ExerciseDetailResponse(BaseModel):
    exercise_id: int
    name: str
    best_mark: Optional[str] = None       # "96 kg"
    best_1rm: Optional[float] = None
    delta_3m_label: Optional[str] = None  # "+11 kg en 3 meses" / None
    pr_history: list[PrRecord] = []
    history: list[ScoreHistoryPoint] = [] # serie 1RM para la gráfica
```

- [ ] **Escribe el test que falla**

```python
# En tests/test_score_endpoints.py, nueva clase al final:

class TestExerciseDetail:
    def test_ejercicio_no_en_catalogo_devuelve_404(self, test_client, db_session: Session):
        u = _user(db_session, "ex_404@test.com")
        resp = test_client.get("/api/score/exercises/999999", headers=_headers(u))
        assert resp.status_code == 404

    def test_ejercicio_valido_devuelve_200_con_campos(self, test_client, db_session: Session):
        from app.models.score_exercise_muscle_group import ScoreExerciseMuscleGroup
        # Obtener un exercise_id real del catálogo curado.
        u = _user(db_session, "ex_ok@test.com")
        mapping = db_session.query(ScoreExerciseMuscleGroup).first()
        if mapping is None:
            pytest.skip("No hay ejercicios en el catálogo curado")
        resp = test_client.get(f"/api/score/exercises/{mapping.exercise_id}", headers=_headers(u))
        assert resp.status_code == 200
        body = resp.json()
        for key in ("exercise_id", "name", "pr_history", "history"):
            assert key in body

    def test_requiere_autenticacion(self, test_client):
        resp = test_client.get("/api/score/exercises/1")
        assert resp.status_code == 401
```

- [ ] **Corre el test para confirmar que falla**

```bash
LC_ALL="en_US.UTF-8" uv run pytest tests/test_score_endpoints.py::TestExerciseDetail -v --noconftest
```

- [ ] **Añade `exercise_detail()` al service** en `app/services/score_service.py`

```python
def exercise_detail(db: Session, user_id: int, exercise_id: int, today: Optional[date] = None) -> Optional[dict]:
    """Datos completos de un ejercicio para la pantalla de detalle.

    Devuelve None si el exercise_id no está en el catálogo curado.
    """
    from app.models.exercise import Exercise
    from app.services import score_math
    from app.services.marca_value import parse_numeric

    today = today or date.today()
    since = today - timedelta(days=WINDOW_DAYS)
    since_3m = today - timedelta(days=90)

    # Verificar que el ejercicio está en el catálogo.
    mapping = (
        db.query(ScoreExerciseMuscleGroup)
        .filter(ScoreExerciseMuscleGroup.exercise_id == exercise_id)
        .first()
    )
    if not mapping:
        return None

    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    name = exercise.name if exercise else str(exercise_id)

    # Todos los logs del usuario para este ejercicio en la ventana (para PRs).
    rows = (
        db.query(UserExerciseLog.logged_sets, UserExerciseLog.completed_at)
        .join(TrainingDayExerciseV2, UserExerciseLog.training_day_exercise_v2_id == TrainingDayExerciseV2.id)
        .filter(
            UserExerciseLog.user_id == user_id,
            TrainingDayExerciseV2.exercise_id == exercise_id,
            UserExerciseLog.completed_at.isnot(None),
            UserExerciseLog.completed_at >= since,
            UserExerciseLog.logged_sets.isnot(None),
        )
        .order_by(UserExerciseLog.completed_at.desc())
        .all()
    )

    # Construir historial de PRs: mejor set de cada sesión.
    pr_history = []
    best_1rm_overall: Optional[float] = None
    best_1rm_3m: Optional[float] = None

    for logged_sets, completed_at in rows:
        session_1rm = score_calculator.best_projected_1rm(logged_sets or [])
        if session_1rm is None:
            continue
        if best_1rm_overall is None or session_1rm > best_1rm_overall:
            best_1rm_overall = session_1rm
        session_date = completed_at.date() if hasattr(completed_at, 'date') else completed_at
        if session_date >= since_3m and (best_1rm_3m is None or session_1rm > best_1rm_3m):
            best_1rm_3m = session_1rm

        # Mejor set de la sesión para la etiqueta "X kg × N".
        best_set = max(
            (s for s in (logged_sets or []) if parse_numeric(s.get("logged_value", ""))),
            key=lambda s: score_calculator._projected_1rm_from_set(s) or 0,
            default=None,
        )
        if best_set:
            w = parse_numeric(best_set.get("logged_value", "")) or 0
            r = best_set.get("logged_reps") or 1
            pr_history.append({
                "date": session_date,
                "weight_reps_label": f"{w:.0f} kg × {r}",
                "projected_1rm": round(session_1rm, 1),
            })

    # Delta vs hace 3 meses.
    best_1rm_before_3m: Optional[float] = None
    rows_3m = (
        db.query(UserExerciseLog.logged_sets)
        .join(TrainingDayExerciseV2, UserExerciseLog.training_day_exercise_v2_id == TrainingDayExerciseV2.id)
        .filter(
            UserExerciseLog.user_id == user_id,
            TrainingDayExerciseV2.exercise_id == exercise_id,
            UserExerciseLog.completed_at.isnot(None),
            UserExerciseLog.completed_at >= since_3m - timedelta(days=WINDOW_DAYS),
            UserExerciseLog.completed_at < since_3m,
            UserExerciseLog.logged_sets.isnot(None),
        )
        .all()
    )
    for (logged_sets,) in rows_3m:
        rm = score_calculator.best_projected_1rm(logged_sets or [])
        if rm and (best_1rm_before_3m is None or rm > best_1rm_before_3m):
            best_1rm_before_3m = rm

    delta_3m_label: Optional[str] = None
    if best_1rm_overall is not None and best_1rm_before_3m is not None:
        diff = best_1rm_overall - best_1rm_before_3m
        sign = "+" if diff >= 0 else ""
        delta_3m_label = f"{sign}{diff:.0f} kg en 3 meses"

    # Serie histórica de 1RM desde los snapshots (campo breakdown JSON).
    history = []
    snaps = (
        db.query(ScoreSnapshot)
        .filter(ScoreSnapshot.user_id == user_id, ScoreSnapshot.breakdown.isnot(None))
        .order_by(ScoreSnapshot.computed_at.asc())
        .all()
    )
    for s in snaps:
        group_data = (s.breakdown or {}).get(mapping.muscle_group)
        if group_data and group_data.get("score") is not None:
            history.append({"computed_at": s.computed_at, "score": group_data["score"]})

    best_mark = f"{best_1rm_overall:.0f} kg" if best_1rm_overall else None

    return {
        "exercise_id": exercise_id,
        "name": name,
        "best_mark": best_mark,
        "best_1rm": best_1rm_overall,
        "delta_3m_label": delta_3m_label,
        "pr_history": pr_history,
        "history": history,
    }
```

- [ ] **Añade el endpoint** en `app/api/routes/mobile/score.py`

```python
from app.schemas.score import (
    ScoreGroupDetail, ScoreResponse, ScoreHistoryPoint, ScoreHistoryResponse,
    ExerciseInGroup, GroupDetailResponse,
    PrRecord, ExerciseDetailResponse,   # añadir
)

@router.get("/exercises/{exercise_id}", response_model=ExerciseDetailResponse)
async def get_exercise_detail(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Datos completos de un ejercicio: mejor marca, historial de PRs y progresión."""
    detail = score_service.exercise_detail(db, current_user.id, exercise_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado en el catálogo curado")

    return ExerciseDetailResponse(
        exercise_id=detail["exercise_id"],
        name=detail["name"],
        best_mark=detail["best_mark"],
        best_1rm=detail["best_1rm"],
        delta_3m_label=detail["delta_3m_label"],
        pr_history=[PrRecord(**p) for p in detail["pr_history"]],
        history=[ScoreHistoryPoint(**h) for h in detail["history"]],
    )
```

- [ ] **Corre todos los tests de la feature**

```bash
LC_ALL="en_US.UTF-8" uv run pytest tests/test_score_math.py tests/test_score_calculator.py tests/test_score_service.py -v --noconftest
```
Esperado: todos en verde.

- [ ] **Commit y PR**

```bash
git add app/schemas/score.py app/services/score_service.py app/api/routes/mobile/score.py tests/test_score_endpoints.py
git commit -m "feat(score): GET /score/exercises/{id} — mejor marca, PRs e historial de 1RM"
```

Abrir PR hacia `main` con título: `feat(score): endpoints de detalle por grupo y ejercicio (§7 completo)`

---

## Tarea 5 — Entidades y repositorio Flutter

**Prerequisito:** PR de API mergeado.

**Ficheros:**
- Crear: `lib/features/puntuaciones/domain/entities/score_entities.dart`
- Crear: `lib/features/puntuaciones/domain/repositories/score_repository.dart`
- Crear: `lib/features/puntuaciones/data/repositories/score_repository_impl.dart`
- Modificar: `lib/core/config/api_config.dart`

**Produce:** `ScoreRepository` con 4 métodos que consumen la API real.

- [ ] **Añade las URLs** en `lib/core/config/api_config.dart`

```dart
// Score de Fuerza
static const String score = '/score';
static const String scoreHistory = '/score/history';
static String scoreGroup(String muscleGroup) => '/score/groups/$muscleGroup';
static String scoreExercise(int exerciseId) => '/score/exercises/$exerciseId';
```

- [ ] **Crea las entidades** en `lib/features/puntuaciones/domain/entities/score_entities.dart`

```dart
class ScoreGroup {
  const ScoreGroup({
    required this.muscleGroup,
    this.score,
    this.level,
    this.progressPct,
    this.pointsToNext,
  });
  final String muscleGroup;
  final double? score;
  final String? level;
  final double? progressPct;
  final int? pointsToNext;

  factory ScoreGroup.fromJson(Map<String, dynamic> j) => ScoreGroup(
        muscleGroup: j['muscle_group'] as String,
        score: (j['score'] as num?)?.toDouble(),
        level: j['level'] as String?,
        progressPct: (j['progress_pct'] as num?)?.toDouble(),
        pointsToNext: j['points_to_next'] as int?,
      );
}

class ScoreData {
  const ScoreData({
    this.totalScore,
    required this.level,
    required this.groupsCovered,
    required this.totalGroups,
    this.coverageNote,
    this.bodyweight,
    this.weeklyDelta,
    this.missing = const [],
    this.groups = const [],
  });
  final double? totalScore;
  final String level;
  final int groupsCovered;
  final int totalGroups;
  final String? coverageNote;
  final double? bodyweight;
  final double? weeklyDelta;
  final List<String> missing;
  final List<ScoreGroup> groups;

  factory ScoreData.fromJson(Map<String, dynamic> j) => ScoreData(
        totalScore: (j['total_score'] as num?)?.toDouble(),
        level: j['level'] as String,
        groupsCovered: j['groups_covered'] as int,
        totalGroups: j['total_groups'] as int,
        coverageNote: j['coverage_note'] as String?,
        bodyweight: (j['bodyweight'] as num?)?.toDouble(),
        weeklyDelta: (j['weekly_delta'] as num?)?.toDouble(),
        missing: List<String>.from(j['missing'] as List? ?? []),
        groups: ((j['groups'] as List?) ?? [])
            .map((e) => ScoreGroup.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class ScoreHistoryPoint {
  const ScoreHistoryPoint({required this.computedAt, required this.score});
  final DateTime computedAt;
  final double score;

  factory ScoreHistoryPoint.fromJson(Map<String, dynamic> j) => ScoreHistoryPoint(
        computedAt: DateTime.parse(j['computed_at'] as String),
        score: (j['total_score'] as num).toDouble(),
      );
}

class ExerciseInGroup {
  const ExerciseInGroup({
    required this.exerciseId,
    required this.name,
    this.bestMark,
    required this.isAnchor,
  });
  final int exerciseId;
  final String name;
  final String? bestMark;
  final bool isAnchor;

  factory ExerciseInGroup.fromJson(Map<String, dynamic> j) => ExerciseInGroup(
        exerciseId: j['exercise_id'] as int,
        name: j['name'] as String,
        bestMark: j['best_mark'] as String?,
        isAnchor: j['is_anchor'] as bool,
      );
}

class GroupDetail {
  const GroupDetail({
    required this.muscleGroup,
    this.score,
    required this.level,
    this.progressPct,
    this.pointsToNext,
    this.delta3m,
    this.exercises = const [],
    this.history = const [],
  });
  final String muscleGroup;
  final double? score;
  final String level;
  final double? progressPct;
  final int? pointsToNext;
  final double? delta3m;
  final List<ExerciseInGroup> exercises;
  final List<ScoreHistoryPoint> history;

  factory GroupDetail.fromJson(Map<String, dynamic> j) => GroupDetail(
        muscleGroup: j['muscle_group'] as String,
        score: (j['score'] as num?)?.toDouble(),
        level: j['level'] as String,
        progressPct: (j['progress_pct'] as num?)?.toDouble(),
        pointsToNext: j['points_to_next'] as int?,
        delta3m: (j['delta_3m'] as num?)?.toDouble(),
        exercises: ((j['exercises'] as List?) ?? [])
            .map((e) => ExerciseInGroup.fromJson(e as Map<String, dynamic>))
            .toList(),
        history: ((j['history'] as List?) ?? [])
            .map((e) => ScoreHistoryPoint.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class PrRecord {
  const PrRecord({
    required this.date,
    required this.weightRepsLabel,
    required this.projectedOnerm,
  });
  final DateTime date;
  final String weightRepsLabel;
  final double projectedOnerm;

  factory PrRecord.fromJson(Map<String, dynamic> j) => PrRecord(
        date: DateTime.parse(j['date'] as String),
        weightRepsLabel: j['weight_reps_label'] as String,
        projectedOnerm: (j['projected_1rm'] as num).toDouble(),
      );
}

class ExerciseDetail {
  const ExerciseDetail({
    required this.exerciseId,
    required this.name,
    this.bestMark,
    this.best1rm,
    this.delta3mLabel,
    this.prHistory = const [],
    this.history = const [],
  });
  final int exerciseId;
  final String name;
  final String? bestMark;
  final double? best1rm;
  final String? delta3mLabel;
  final List<PrRecord> prHistory;
  final List<ScoreHistoryPoint> history;

  factory ExerciseDetail.fromJson(Map<String, dynamic> j) => ExerciseDetail(
        exerciseId: j['exercise_id'] as int,
        name: j['name'] as String,
        bestMark: j['best_mark'] as String?,
        best1rm: (j['best_1rm'] as num?)?.toDouble(),
        delta3mLabel: j['delta_3m_label'] as String?,
        prHistory: ((j['pr_history'] as List?) ?? [])
            .map((e) => PrRecord.fromJson(e as Map<String, dynamic>))
            .toList(),
        history: ((j['history'] as List?) ?? [])
            .map((e) => ScoreHistoryPoint.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}
```

- [ ] **Crea la interfaz** en `lib/features/puntuaciones/domain/repositories/score_repository.dart`

```dart
import '../entities/score_entities.dart';

abstract class ScoreRepository {
  Future<ScoreData> getScore();
  Future<List<ScoreHistoryPoint>> getHistory(String window);
  Future<GroupDetail> getGroupDetail(String muscleGroup);
  Future<ExerciseDetail> getExerciseDetail(int exerciseId);
}
```

- [ ] **Crea la implementación** en `lib/features/puntuaciones/data/repositories/score_repository_impl.dart`

```dart
import 'package:dio/dio.dart';
import '../../../../core/config/api_config.dart';
import '../../domain/entities/score_entities.dart';
import '../../domain/repositories/score_repository.dart';

class ScoreRepositoryImpl implements ScoreRepository {
  ScoreRepositoryImpl(this._dio);
  final Dio _dio;

  @override
  Future<ScoreData> getScore() async {
    final r = await _dio.get(ApiConfig.score);
    return ScoreData.fromJson(r.data as Map<String, dynamic>);
  }

  @override
  Future<List<ScoreHistoryPoint>> getHistory(String window) async {
    final r = await _dio.get(ApiConfig.scoreHistory, queryParameters: {'window': window});
    final data = r.data as Map<String, dynamic>;
    return (data['points'] as List)
        .map((e) => ScoreHistoryPoint.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  @override
  Future<GroupDetail> getGroupDetail(String muscleGroup) async {
    final r = await _dio.get(ApiConfig.scoreGroup(muscleGroup));
    return GroupDetail.fromJson(r.data as Map<String, dynamic>);
  }

  @override
  Future<ExerciseDetail> getExerciseDetail(int exerciseId) async {
    final r = await _dio.get(ApiConfig.scoreExercise(exerciseId));
    return ExerciseDetail.fromJson(r.data as Map<String, dynamic>);
  }
}
```

- [ ] **Compila para verificar que no hay errores de tipos**

```bash
cd /Users/kataiturriaga/repos/elmetodo_app
flutter analyze lib/features/puntuaciones/
```
Esperado: sin errores.

- [ ] **Commit**

```bash
git add lib/features/puntuaciones/domain/ lib/features/puntuaciones/data/repositories/score_repository_impl.dart lib/core/config/api_config.dart
git commit -m "feat(score): entidades Dart + repositorio (ScoreRepository) para los 4 endpoints"
```

---

## Tarea 6 — Providers Riverpod Flutter

**Ficheros:**
- Crear: `lib/features/puntuaciones/presentation/providers/score_providers.dart`
- Crear: `lib/features/puntuaciones/presentation/providers/score_providers.g.dart` (generado)

**Produce:** 4 providers: `scoreProvider`, `scoreHistoryProvider(window)`, `groupDetailProvider(group)`, `exerciseDetailProvider(id)`

- [ ] **Crea el fichero de providers**

```dart
// lib/features/puntuaciones/presentation/providers/score_providers.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../../core/network/dio_client.dart';
import '../../data/repositories/score_repository_impl.dart';
import '../../domain/entities/score_entities.dart';
import '../../domain/repositories/score_repository.dart';

part 'score_providers.g.dart';

@Riverpod(keepAlive: false)
ScoreRepository scoreRepository(Ref ref) {
  return ScoreRepositoryImpl(ref.watch(dioProvider));
}

@riverpod
Future<ScoreData> score(Ref ref) {
  return ref.watch(scoreRepositoryProvider).getScore();
}

@riverpod
Future<List<ScoreHistoryPoint>> scoreHistory(Ref ref, String window) {
  return ref.watch(scoreRepositoryProvider).getHistory(window);
}

@riverpod
Future<GroupDetail> groupDetail(Ref ref, String muscleGroup) {
  return ref.watch(scoreRepositoryProvider).getGroupDetail(muscleGroup);
}

@riverpod
Future<ExerciseDetail> exerciseDetail(Ref ref, int exerciseId) {
  return ref.watch(scoreRepositoryProvider).getExerciseDetail(exerciseId);
}
```

- [ ] **Genera el código Riverpod**

```bash
cd /Users/kataiturriaga/repos/elmetodo_app
dart run build_runner build --delete-conflicting-outputs
```
Esperado: se crea `score_providers.g.dart` sin errores.

- [ ] **Commit**

```bash
git add lib/features/puntuaciones/presentation/providers/
git commit -m "feat(score): providers Riverpod — score, history, groupDetail, exerciseDetail"
```

---

## Tarea 7 — Conectar pantalla principal a datos reales

**Ficheros:**
- Modificar: `lib/features/puntuaciones/presentation/screens/puntuacion_screen.dart`
- Modificar: `lib/features/puntuaciones/presentation/widgets/grupos_fuerza_grid.dart`
- Modificar: `lib/features/puntuaciones/presentation/widgets/evolucion_fuerza_section.dart`

**Regla:** cuando los datos estén cargando, mostrar un `CircularProgressIndicator`. Cuando haya error, mostrar un `Text` con el mensaje. Eliminar todos los datos demo de estas pantallas.

- [ ] **Convierte `PuntuacionContent` a `ConsumerWidget`**

En `puntuacion_screen.dart`, sustituir la clase `PuntuacionContent`:

```dart
class PuntuacionContent extends ConsumerWidget {
  const PuntuacionContent({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scoreAsync = ref.watch(scoreProvider);

    return scoreAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => Center(child: Text('Error al cargar el score: $e')),
      data: (score) => SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _ScorePager(score: score),
            const SizedBox(height: 16),
            EvolucionFuerzaSection(mostrarTitulo: false),
            const SizedBox(height: 24),
            GruposFuerzaGrid(grupos: score.groups),
          ],
        ),
      ),
    );
  }
}
```

Añadir import al inicio:
```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/score_providers.dart';
import '../../domain/entities/score_entities.dart' as entities;
```

Actualizar `_ScorePager` para recibir `ScoreData score` y usar `score.totalScore`, `score.level` en `PuntuacionHeroCard`.

- [ ] **Actualiza `GruposFuerzaGrid`** para aceptar `List<entities.ScoreGroup>` en vez de `List<GrupoFuerza>` del demo, mapeando los campos.

- [ ] **Actualiza `EvolucionFuerzaSection`** para ser `ConsumerStatefulWidget` y consumir `scoreHistoryProvider(window)` donde `window` es el chip seleccionado.

- [ ] **Arranca la app en el simulador y verifica**

```bash
# Asegúrate de que la API local está corriendo en el puerto 8000
# (o que el simulador apunta al entorno de dev)
flutter run
```
Verifica: la pantalla principal carga con datos reales (o muestra el spinner/error apropiado si la API no responde).

- [ ] **Commit**

```bash
git add lib/features/puntuaciones/
git commit -m "feat(score): pantalla principal conectada a API real — elimina datos demo"
```

---

## Tarea 8 — Conectar detalle de grupo y ejercicio

**Ficheros:**
- Modificar: `lib/features/puntuaciones/presentation/screens/grupo_detalle_screen.dart`
- Modificar: `lib/features/puntuaciones/presentation/screens/ejercicio_detalle_screen.dart`

- [ ] **Convierte `GrupoDetalleScreen` a `ConsumerWidget`**

```dart
class GrupoDetalleScreen extends ConsumerWidget {
  const GrupoDetalleScreen({super.key, required this.muscleGroup});
  final String muscleGroup;  // antes recibía GrupoFuerza; ahora solo el nombre

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(groupDetailProvider(muscleGroup));
    final colors = context.colors;

    return Scaffold(
      backgroundColor: colors.bgApp,
      appBar: AppBar(
        backgroundColor: colors.bgApp,
        elevation: 0,
        iconTheme: IconThemeData(color: colors.textPrimary),
        title: Text(muscleGroup, style: /* mismo estilo */ ...),
        centerTitle: true,
      ),
      body: detailAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (detail) => SafeArea(
          top: false,
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                GrupoHeroCard(
                  nombre: detail.muscleGroup,
                  score: detail.score?.toInt() ?? 0,
                  level: _toScoreLevel(detail.level),
                  deltaText: detail.delta3m != null
                      ? '${detail.delta3m! >= 0 ? '+' : ''}${detail.delta3m!.toInt()} pt en 3 meses'
                      : 'Sin historial',
                  progreso: detail.progressPct ?? 0,
                  paraProText: detail.pointsToNext != null
                      ? '${detail.pointsToNext} para ${_nextLevelName(detail.level)}'
                      : 'Nivel máximo',
                ),
                const SizedBox(height: 24),
                _titulo('Lista de ejercicios', colors),
                const SizedBox(height: 16),
                EjerciciosList(
                  ejercicios: detail.exercises.map((e) => EjercicioFuerza(
                    nombre: e.name,
                    marca: e.bestMark ?? '—',
                    esMejor: e.isAnchor,
                    exerciseId: e.exerciseId,
                  )).toList(),
                  onEjercicioTap: (e) => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => EjercicioDetalleScreen(exerciseId: e.exerciseId)),
                  ),
                ),
                const SizedBox(height: 24),
                _titulo('Progreso', colors),
                const SizedBox(height: 16),
                EvolucionFuerzaSection(mostrarTitulo: false, historyPoints: detail.history),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

Añadir helper `_toScoreLevel(String levelName) -> ScoreLevel` que convierte "Experimentado" → `ScoreLevel.experimentado`, etc.

- [ ] **Actualizar `EjercicioFuerza`** en `ejercicios_list.dart` para incluir `exerciseId: int`.

- [ ] **Convierte `EjercicioDetalleScreen`** de forma análoga, consumiendo `exerciseDetailProvider(exerciseId)`. El campo `exerciseId` reemplaza al objeto `EjercicioFuerza` completo.

- [ ] **Actualiza `EvolucionFuerzaSection`** para aceptar `List<ScoreHistoryPoint>? historyPoints` opcional (si se pasa, usa esos datos en vez de llamar al provider).

- [ ] **Actualiza la navegación en `GruposFuerzaGrid`**: pasar `muscleGroup` string en vez de `GrupoFuerza` a `GrupoDetalleScreen`.

- [ ] **Arranca en simulador y recorre el flujo completo**

```bash
flutter run
```
Verifica: pantalla principal → toca un grupo → pantalla de detalle con datos reales → toca un ejercicio → pantalla de ejercicio con historial de PRs.

- [ ] **Commit y PR**

```bash
git add lib/features/puntuaciones/
git commit -m "feat(score): detalle de grupo y ejercicio conectados a API real — elimina todos los datos demo"
```

Abrir PR hacia `main` con título: `feat(score): app Flutter conectada a la API real (§8 completo)`

---

## Self-review

**Cobertura del spec vs tareas:**
- ✅ `GET /score` con `progress_pct`, `points_to_next`, `weekly_delta` → Tarea 2
- ✅ `GET /score/groups/{group}` → Tarea 3
- ✅ `GET /score/exercises/{exercise_id}` → Tarea 4
- ✅ Entidades Dart + repositorio → Tarea 5
- ✅ Providers Riverpod → Tarea 6
- ✅ Pantalla principal con datos reales → Tarea 7
- ✅ Detalle de grupo y ejercicio con datos reales → Tarea 8
- ⚠️ **Empty states** (sin datos, sin peso, cold-start) — quedan fuera de este plan; corresponden al §6 del plan original y merecen su propio plan.
- ⚠️ **Strings l10n** — quedan fuera; son un PR de limpieza independiente.

**Tipos consistentes:**
- `ScoreHistoryPoint.fromJson` usa `j['total_score']` en la Tarea 5 — verificar que la API de history devuelve `total_score` (sí, es el campo de `ScoreHistoryPoint` del schema Python).
- `EvolucionFuerzaSection` se modifica en Tareas 7 y 8 — la interfaz con `historyPoints` opcional debe definirse en Tarea 7 para que Tarea 8 la pueda usar.
