# Caso de estudio: App Automática

**Producto:** El Metodo — tier suscripción (app de entrenamiento)
**Rol:** Product Designer + PM
**Período:** ~2023–2026 (3 años)
**Estado:** En producción

---

## El problema

Los programas de entrenamiento genéricos compiten solo en contenido (rutinas, vídeos). Una vez que el usuario loguea sus entrenamientos, ese dato "muere" — no devuelve nada al usuario, no diferencia el producto. La app necesita una razón propia para existir frente a la competencia y una palanca para mejorar conversión en el free trial (7 días).

## El contexto

- Equipo de 2 personas
- App móvil (Flutter) para usuarios de suscripción
- Diseño del sistema completo: onboarding, home, entreno, dieta, notificaciones
- Design system propio: EMP DS Library
- Stack: API FastAPI/SQLAlchemy, DB Postgres, app Riverpod/Freezed
- Infraestructura existente: logs de fuerza (`UserExerciseLog`), histórico de peso (`Progress`), feature "Tus marcas" (parseo de logs), sistema de ranking por pasos

## Decisiones clave

### Sistema de Puntuación de Entrenamiento (en planificación)
- **Apuesta:** diferenciación competitiva mediante un score 0–300+ objetivo (fuerza + running + híbrido), comparable contra estándares poblacionales.
- **Métrica de éxito:** conversión trial→pago. El score debe entregar valor dentro de los 7 días del trial.
- **Cold-start:** sesiones de evaluación al inicio de cada programa (bloque de fuerza con 7 grupos musculares, test ligero de running), para poblar el score desde el día 1.
- **MVP:** score de fuerza en programas de fuerza pura (cierre de scope para validar hipótesis barato). Running e híbrido son fase 2.

## Trabajo en progreso (junio 2026)

**Puntuación de Entrenamiento — fase de planificación y auditoría:**
- ✅ Spec técnico completo (fórmulas, grupos musculares, algoritmo de cálculo).
- ✅ Visión de producto (problema → métrica → deseabilidad → MVP scope).
- ✅ Solución cold-start (sesiones de evaluación).
- ✅ Plan de tareas de implementación end-to-end (modelos, motor de cálculo, API, Flutter UI, Figma specs).
- ✅ Prompt para auditoría paralela de todos los programas en producción (plan de cómo aplicar sesiones de evaluación).
- 🔄 **En progreso:** auditoría de cobertura de ejercicios y running tests en prod (otro chat).
- ⏳ Pendiente: decisiones de contenido (¿añadir bloque eval vs modificar sesiones?), tablas de estándares reales, calibrado anti-desmotivación.

## El resultado

- App en producción con usuarios reales (stats: 228 entrenos completados por algunos usuarios en 30 días, alto engagement).
- Referencia de calidad para el resto de productos de El Metodo
- Pipeline de feature major (puntuación) planificada y lista para ejecutar con claridad de apuesta, riesgo y scope.

## Materiales

- Figma: https://www.figma.com/design/629ryw0MF7hzDxIFiZJ5Un/App-Automatica
- Dashboard: https://dashboard.apps.elmetodoapp.com/
