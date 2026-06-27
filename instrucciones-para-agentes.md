# Instrucciones para agentes (Cursor) — Plataforma El Metodo

> **Para qué es este documento.** Da el contexto mínimo para que un agente de IA
> (Cursor) empiece a trabajar en la plataforma **El Metodo** sin romper nada y
> siguiendo cómo construimos. Léelo entero antes de tocar código.
>
> Puedes renombrar este archivo a `AGENTS.md` o `.cursorrules` dentro de cualquier
> repo para que Cursor lo cargue como reglas del proyecto.

---

## 1. Qué es El Metodo

SaaS de coaching fitness con **dos productos**:

- **App (Automática)** — programas de entrenamiento para usuarios finales (free + pago).
- **Dashboard (coached)** — herramienta para que los coaches gestionen a sus clientes.
- **V2 · Asesorías** — tier de consultoría donde los coaches venden asesorías a través de la plataforma.

**Un único backend** (monolito) sirve a todos los productos.

---

## 2. Mapa de repos

Todos los repos se clonan bajo una misma carpeta padre. En este equipo es:

```
/Users/kaitu/Library/CloudStorage/OneDrive-Personal/workspace/
```

La pieza clave es que **la documentación vive separada del código**.

### Repos de CÓDIGO

| Repo (carpeta) | Ruta completa | Qué es | Stack |
|------|------|--------|-------|
| **`metodo_api`** | `…/workspace/metodo_api` | **Backend: monolito único** que sirve a apps + dashboard. | **FastAPI / Python** · SQLAlchemy · Alembic (migraciones) · pytest · Celery (tareas). Estructura: `app/services`, `app/repositories`, `app/api/routes`, `app/models`, `app/tasks`, `tests/`. Endpoints REST, casi todos síncronos. |
| **`elmetodo_app-auto`** | `…/workspace/elmetodo_app-auto` | App móvil **Automática** (la de suscripción, end-users). | **Flutter / Dart** · estructura `lib/core` (widgets, router, tema) + `lib/features` (por feature). |
| **`elmetodo-app-asesorias`** | `…/workspace/elmetodo-app-asesorias` | App móvil **Asesorías** (tier consultoría, V2). | **Flutter / Dart** |
| **`elmetodo_dashboard`** | `…/workspace/elmetodo_dashboard` | Dashboard web para coaches. | **Next.js 15 / React 19** · Radix UI + Tailwind (`class-variance-authority`, `clsx`) · `openapi-fetch` (cliente tipado contra el OpenAPI del backend) · `lucide-react`, `motion`. Prod: https://dashboard.apps.elmetodoapp.com/ |

### Repos de DOCUMENTACIÓN (sin código de producto, solo Markdown)

| Repo (carpeta) | Ruta completa | Qué documenta |
|------|------|----------------|
| **`elmetodo-automatica`** | `…/workspace/elmetodo-automatica` | **Este repo.** Docs de producto/diseño de la app **Automática**: analítica, definiciones, specs, planes de implementación, decisiones de código y aprendizajes. **Es la fuente de verdad de QUÉ y POR QUÉ construimos.** |
| **`elmetodo-asesorias`** | `…/workspace/elmetodo-asesorias` | Docs de producto/diseño del tier **asesorías** + scripts de evaluación de IA. |

> `…/workspace/` = `/Users/kaitu/Library/CloudStorage/OneDrive-Personal/workspace/`

> **Regla de oro:** el QUÉ y el POR QUÉ se deciden y documentan en los repos de
> **docs** (`elmetodo-automatica` / `elmetodo-asesorias`). El CÓMO (implementación) va en
> los repos de **código**. Antes de implementar una feature, busca su spec/plan en
> el repo de docs correspondiente.

---

## 3. Cómo construimos (workflow — OBLIGATORIO)

Estas reglas aplican a **todos los repos de código**:

1. **Nunca hagas `git push` sin que te lo pidan explícitamente.** Avisa antes y
   espera el "ok / súbelo".
2. **Trabaja siempre en una rama feature.** Nunca commitees ni pushees directo a
   `main`.
3. **PRs pequeñas e incrementales.** Una unidad de trabajo entendible por PR
   (p.ej. "modelo de datos", "fórmulas", "endpoint"). Si una feature es grande,
   pártela en PRs encadenadas (stacked).
4. **TDD (test-driven development).** Primero el test que falla (RED), luego el
   código mínimo para que pase (GREEN), luego refactor. No escribas código de
   producción sin un test que falle antes.
5. **Explica en cristiano.** El equipo de producto no es técnico: al proponer
   cambios, explica qué haces, por qué, y **avisa siempre del nivel de riesgo**
   (🟢 bajo / 🟡 medio / 🔴 alto). Pregunta cuando haya dudas en vez de asumir.
6. **Migraciones de BD (Alembic):** son **historia inmutable** — cada cambio es un
   archivo nuevo, nunca edites una migración ya fusionada. Los *seeds* deben ser
   **idempotentes** (`ON CONFLICT DO UPDATE`) y **defensivos** (no fallar si falta
   un dato de referencia; loggear `WARNING` en vez de petar). Nada de fallos
   silenciosos.
7. **Decisiones y aprendizajes se documentan** en `elmetodo-automatica/Decisiones Código/`
   y `elmetodo-automatica/aprendizajes/`, en lenguaje claro.

### Flujo típico de una tarea
1. Buscar la spec/plan en el repo de docs.
2. Crear rama feature en el repo de código.
3. TDD: test que falla → código mínimo → verde → refactor.
4. Explicar los cambios y el riesgo a la persona de producto.
5. Pushear **solo** cuando lo confirmen → abrir PR pequeña.
6. Atender el review (con rigor técnico, sin "tienes toda la razón" automático;
   verificar antes de implementar).

---

## 4. Convenciones por repo

### `metodo_api` (FastAPI)
- Lógica de negocio en `app/services/` (funciones puras separadas de la capa que
  lee BD cuando tiene sentido). Modelos en `app/models/`, rutas en `app/api/routes/`.
- Tests con pytest en `tests/`. Para tests de funciones puras (sin BD) se puede
  usar `--noconftest` y evitar el harness de Docker.
- Migraciones en `migrations/versions/` (Alembic). Ver regla 6 arriba.
- Datos de referencia versionados en módulos importables (`app/data/...`), no
  hardcodeados dentro de la migración.

### `elmetodo_app-auto` (Flutter)
- Widgets reutilizables en `lib/core/widgets/`; pantallas y lógica por feature en
  `lib/features/<feature>/`.
- Flujo para UI: diseñar en Figma → construir el widget con **tokens del DS** (no
  hex ni fuentes hardcodeadas) → previsualizar aislado en la `DesignSystemScreen`
  (galería de dev tools) → iterar con **hot reload** → ensamblar pantalla →
  conectar a la API real en una PR aparte.

### `elmetodo_dashboard` (Next.js)
- Cliente de API **tipado** vía `openapi-fetch` contra el OpenAPI del backend: si
  cambian endpoints, regenerar/usar los tipos en vez de llamadas manuales.
- UI con Radix + Tailwind; sigue los componentes existentes antes de crear nuevos.

---

## 5. Diseño / Figma

- Design system propio: **EMP DS Library**.
- Figma app Automática: file `629ryw0MF7hzDxIFiZJ5Un`. Figma Dashboard: file
  `E6H45ej75HO6fL2SOnQNL5`.
- Al crear componentes: vincular fills/strokes a **variables** y textos a **estilos
  de texto** (nunca valores hardcodeados). Crear siempre dentro de un Frame/Section.

---

## 6. Infraestructura

- **BD**: PostgreSQL en **DigitalOcean** (prod). La BD de prod suele dar timeout por
  firewall desde fuera; para métricas usar la **API HTTPS**, no conexión directa.
- **Storage de fotos**: **AWS S3** (`eu-west-3`, URLs públicas guardadas en la tabla
  `reviews`). No Firebase para storage.
- **Firebase**: solo **FCM/push** y **GA4** (analítica), dentro de `metodo_api`.
- **Google Drive** (service-account): destino de outputs generados (p.ej. collages).

---

## 7. Estado actual del trabajo

**Feature en curso: Puntuaciones de Entrenamiento (Score de Fuerza).** Sistema que
da al usuario una puntuación de fuerza estilo Gravl, calculada a partir de sus
marcas reales. Spec y plan en `elmetodo-automatica/plans/tareas-implementacion-puntuaciones.md`
y `elmetodo-automatica/Funcionalidades/puntuaciones-entreno/`.

Se está construyendo en PRs pequeñas y encadenadas en `metodo_api` (modelo de
datos → fórmulas → calculadora+servicio → endpoints) y luego las pantallas en
`elmetodo_app-auto`.

---

## 8. Antes de empezar, recuerda

- [ ] ¿Está la spec/plan de lo que voy a hacer en el repo de docs? (si no, preguntar)
- [ ] ¿Estoy en una **rama feature**, no en `main`?
- [ ] ¿Escribí el **test que falla** antes del código?
- [ ] ¿Expliqué el cambio y su **nivel de riesgo** a producto?
- [ ] ¿Tengo confirmación explícita antes de **pushear**?
