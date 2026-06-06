# Historia de Usuario #004 — Día 4: Generación de Código y Pipeline End-to-End

**Fecha:** 7 de junio de 2026  
**Sprint:** Día 4 de 10  
**Épica:** Motor de Generación (Paso 3)  
**Estado:** ✅ Implementado

---

## Historia

**Como** usuaria del agente Quimera,  
**quiero** recibir un componente React listo para usar después de enviar mi brief de diseño,  
**para** poder copiar el código directamente a mi proyecto sin necesidad de diseñar desde cero.

---

## Criterios de Aceptación

### CA-001: Paso 3 — Generación de código
- [ ] `POST /generar-diseno` acepta un `design_brief` y devuelve respuesta SSE (`text/event-stream`)
- [ ] El pipeline ejecuta los 3 pasos en secuencia: análisis → evaluación → generación
- [ ] Si el score es < 85 (máx. 3 iteraciones), el diseño se corrige antes de generar
- [ ] La respuesta final incluye: `react_component` (TSX), `design_tokens_css` (`:root { --vars }`) y `rationale_document` (Markdown)
- [ ] El componente React es funcional: tiene `export default`, usa las variables CSS del diseño, es compatible con Tailwind

### CA-002: Streaming SSE
- [ ] El cliente recibe eventos de progreso en tiempo real (no espera 30-45s sin feedback)
- [ ] Eventos emitidos: `inicio` → `analisis` → `evaluacion` → `generacion` → `guardando` → `completado`
- [ ] Cada evento incluye `step`, `status` y metadata relevante (score, iteraciones, etc.)
- [ ] El evento `completado` contiene los 3 artefactos de código

### CA-003: Persistencia (Firestore + GCS)
- [ ] El contexto del diseño se guarda en Firestore en `/projects/{project_id}/`
- [ ] Los 3 artefactos (`.tsx`, `.css`, `.md`) se suben a GCS en `gs://quimera-ai-prod-outputs/projects/{project_id}/`
- [ ] `GET /proyecto/{project_id}` retorna el contexto guardado
- [ ] Si Firestore o GCS fallan, el pipeline retorna igualmente el resultado (errores no fatales)

### CA-004: Validación de sintaxis JSX
- [ ] `_validate_react_syntax()` llama a `node validate_jsx.js` con `@babel/parser`
- [ ] Si Node no está disponible, hace fallback a `_basic_python_validation()`
- [ ] En caso de error de sintaxis, reintenta el prompt de generación una vez
- [ ] Si el reintento también falla, usa `_get_fallback_component()` con los colores del contexto

### CA-005: Tests unitarios (sin Gemini)
- [ ] `test_generate_code_raises_si_no_aprobado` — ValueError si `context.approved == False`
- [ ] `test_parse_code_output_extrae_tres_secciones` — parsing de delimitadores correcto
- [ ] `test_parse_code_output_secciones_vacias_si_no_hay_delimitadores` — graceful empty
- [ ] `test_fallback_component_incluye_colores_del_context` — fallback usa colores del DesignContext
- [ ] `test_fallback_tokens_incluye_todas_las_variables` — CSS variables requeridas presentes
- [ ] `test_basic_python_validation_acepta_componente_valido` — acepta TSX bien formado
- [ ] `test_basic_python_validation_rechaza_sin_export` — rechaza código sin `export default`

---

## Decisiones técnicas

### Formato de salida con delimitadores (no JSON)
El código React/TypeScript contiene backticks, comillas simples y dobles, y JSX que rompen la serialización JSON. Se usa un formato de secciones con delimitadores únicos:
```
===REACT_COMPONENT===
[código TSX]
===DESIGN_TOKENS_CSS===
[variables CSS]
===RATIONALE===
[documento Markdown]
===END===
```
Esto elimina toda necesidad de escaping y hace el parsing robusto.

### Gemini Flash para Step 3
Se usa `gemini-2.5-flash` (temperatura=0.4) en lugar de Pro para reducir latencia. La generación de código es una tarea más mecánica que la evaluación estética; Flash es suficiente y ~3x más rápido.

### Fallback de 2 niveles
1. **Nivel 1**: Si el componente generado tiene sintaxis inválida → reformatear con nuevo prompt
2. **Nivel 2**: Si el reintento también falla → `_get_fallback_component()` con colores del contexto garantiza que siempre se retorna algo útil

### Docker + Node.js
El `Dockerfile` instala `nodejs npm` via `apt-get` e instala `@babel/parser` vía `npm install --production`. El validador es un script ligero de 27 líneas que lee stdin y sale con código 0 (válido) o 1 (inválido).

---

## Archivos modificados / creados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `backend/pipeline/step3_generate.py` | ✅ Nuevo | Paso 3 completo (439 líneas) |
| `backend/validate_jsx.js` | ✅ Nuevo | Validador Babel vía stdin/stdout |
| `backend/package.json` | ✅ Nuevo | Dependencia @babel/parser |
| `backend/services/firestore_client.py` | ✅ Reescrito | AsyncClient para Firestore |
| `backend/services/storage_client.py` | ✅ Reescrito | Upload a GCS con asyncio.to_thread |
| `backend/main.py` | ✅ Reescrito | SSE endpoint + /proyecto/{id} |
| `backend/Dockerfile` | ✅ Actualizado | Node.js + npm install |
| `tests/test_pipeline.py` | ✅ Actualizado | TestStep3Generate (7 tests unitarios) |

---

## Comandos de verificación

```bash
# 1. Instalar dependencias Node (primera vez)
cd backend && npm install

# 2. Correr todos los tests unitarios (sin Gemini)
$env:PYTHONPATH="backend"; pytest tests/ -m "not slow" -v --cache-clear

# 3. Levantar el backend
cd backend && uvicorn main:app --reload --port 8000

# 4. Probar el endpoint SSE con curl
curl -X POST http://localhost:8000/generar-diseno \
  -H "Content-Type: application/json" \
  -d '{"design_brief": "Landing page para startup fintech. Colores azul y blanco. Jóvenes 25-35 años."}' \
  --no-buffer

# 5. Verificar sintaxis de todos los archivos Python
cd backend && python -m py_compile main.py models.py pipeline/step1_analyze.py pipeline/step2_evaluate.py pipeline/step3_generate.py pipeline/scorers/color_harmony.py pipeline/scorers/wcag_contrast.py pipeline/scorers/llm_scorers.py services/gemini_client.py services/firestore_client.py services/storage_client.py
```

---

## Métricas esperadas

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| Tests unitarios pasando | 40+ | ⏳ Verificar |
| Latencia pipeline completo | < 45s | ⏳ Medir en tests slow |
| Componente válido (sin fallback) | > 90% de briefs | ⏳ Medir en tests slow |
| Eventos SSE emitidos | ≥ 6 por request | ⏳ Verificar |

---

## Pendiente para días siguientes

- **Día 5**: Frontend Next.js que consume el SSE y renderiza el componente en vivo
- **Día 6**: Matriz de confusión — 50 briefs × 8 criterios, F1-score vs diseñador humano
- **Día 7-8**: Deploy a Cloud Run + CI/CD con Cloud Build (`setup_gcp.sh`)
