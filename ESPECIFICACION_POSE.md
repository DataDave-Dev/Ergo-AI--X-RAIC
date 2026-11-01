# ErgoAI — Especificación para Cursor: módulo de pose, vectores y ángulos (MediaPipe + REBA)

> **Cómo usar este archivo en Cursor**
> 1. Guárdalo en la raíz del repo como `ESPECIFICACION_POSE.md`.
> 2. En Cursor, modo **Agent**, escribe:
>    `Lee @ESPECIFICACION_POSE.md completo antes de escribir código. Implementa SOLO la Fase 0 y la Fase 1. Corre pytest, muéstrame el resultado y detente.`
> 3. Pide cada fase siguiente por separado (“Implementa la Fase 2 de @ESPECIFICACION_POSE.md…”).

---

## 0. Rol y contexto

Eres un ingeniero senior de Python y visión por computadora. Vas a construir el módulo de estimación de pose de **ErgoAI**, un agente de evaluación ergonómica para la competencia X-RAIC 2026, Track 4 (reto de Jabil).

El módulo recibe fotos de una estación de trabajo y entrega:

1. Landmarks del cuerpo (MediaPipe Pose Landmarker).
2. Vectores de cada segmento corporal.
3. Ángulos por segmento, con su vista de origen, confianza y banderas.
4. La banda REBA de cada segmento y el puntaje REBA completo con su nivel de riesgo.

**Cómo se califica (define las prioridades):**

- Criterio 1 (20 pts): el puntaje REBA y el nivel de riesgo deben coincidir con la referencia de Jabil en 6 casos.
- Criterio 2 (15 pts): al menos el 90 % de los segmentos corporales deben caer en la misma banda REBA que la referencia.
- Un error de pocos grados solo cambia el resultado si el ángulo está cerca de un umbral de banda. Por eso todo ángulo cercano a un umbral se marca para revisión humana.

**Entradas por caso:** hasta 3 fotos (frente, costado, vista aérea), **sin rostro**, más un `contexto.json` con lo que no sale de una foto (carga, agarre, actividad).

---

## 1. Reglas no negociables

1. **API de MediaPipe:** usa SOLO MediaPipe **Tasks** (`vision.PoseLandmarker`). **NO uses `mp.solutions.pose` ni `mp.solutions.drawing_utils`**: la API “Solutions” se eliminó desde mediapipe 0.10.30 y ese código falla con `ImportError`. Dibuja con OpenCV.
2. **Todo local.** Ninguna llamada a servicios externos ni subida de imágenes. Los datos del reto son confidenciales. `data/`, `out/` y `models/` van en `.gitignore`.
3. **Cero umbrales inventados.** Todo umbral ergonómico vive en `config/umbrales.yaml` con un comentario de fuente: `# REBA (Hignett y McAtamney, 2000)`, `# Excel Jabil 00014, hoja EAWS` o `# SUPUESTO: confirmar con Jabil`. En el código no hay números mágicos de ergonomía.
4. **Si no se puede medir, no se adivina.** Un ángulo que no se puede medir devuelve `None` con un `motivo` y se agrega a `pendientes_manuales`. Nunca rellenes con un valor “típico”.
5. **Determinista y probado.** Este módulo no usa LLM. Geometría y REBA son funciones puras con pruebas `pytest`. No avances de fase con pruebas fallando.
6. **Trabaja por fases** (secciones 5 a 10). Al terminar cada fase: corre `pytest`, muestra el resultado, lista lo que quedó pendiente y **detente**.
7. Type hints en todo, modelos con `dataclasses` o Pydantic v2, docstrings en español.

---

## 2. Stack

- Python 3.12 en un entorno `uv` (`uv venv --python 3.12`). Verificado: `mediapipe==1.1.1` se instala en Linux con Python 3.13 (wheel `py3-none-manylinux_2_28_x86_64`).
- Dependencias: `mediapipe==1.1.1`, `opencv-python`, `numpy`, `pillow`, `pyyaml`, `pydantic>=2`, `pytest`.
- Modelo: `pose_landmarker_heavy.task`, el más preciso. La velocidad no importa porque son fotos. El script `scripts/descargar_modelo.py` lo baja a `models/` desde:
  `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task`

**Imports y uso verificados en mediapipe 1.1.1** (úsalos tal cual):

```python
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

options = vision.PoseLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path="models/pose_landmarker_heavy.task"),
    running_mode=vision.RunningMode.IMAGE,
    num_poses=3,
    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    output_segmentation_masks=False,
)
with vision.PoseLandmarker.create_from_options(options) as landmarker:
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_uint8_array)
    result = landmarker.detect(mp_image)
    # result.pose_landmarks: list[list[NormalizedLandmark]]  -> x, y (0–1), z, visibility, presence
    # result.pose_world_landmarks: list[list[Landmark]]      -> x, y, z en metros, origen en el centro de caderas
    # vision.PoseLandmark es un enum con los 33 índices (NOSE=0 ... RIGHT_FOOT_INDEX=32)
```

---

## 3. Estructura del proyecto

```
ergoai-pose/
├── pyproject.toml
├── .gitignore                 # data/ out/ models/ .venv/
├── config/
│   └── umbrales.yaml          # TODOS los umbrales, con fuente
├── models/                    # pose_landmarker_heavy.task (no se versiona)
├── data/
│   ├── casos/<caso_id>/       # frente.jpg costado.jpg aerea.jpg contexto.json
│   └── validacion/<caso_id>/  # mismas fotos + referencia.json (Fase 4)
├── src/ergoai/
│   ├── config.py              # carga y valida umbrales.yaml (Pydantic)
│   ├── modelos.py             # dataclasses / Pydantic de entrada y salida
│   ├── io_imagenes.py         # carga con EXIF, RGB, tamaño
│   ├── landmarks.py           # índices y nombres en español
│   ├── pose.py                # PoseBackend (Protocol) + MediaPipeBackend
│   ├── geometria.py           # operaciones de vectores y ángulos (puras)
│   ├── angulos.py             # ángulos por segmento y vista
│   ├── fusion.py              # elige vista y lado, confianza, banderas
│   ├── reba.py                # bandas, tablas A/B/C, puntaje y nivel
│   ├── anotacion.py           # imágenes anotadas con OpenCV
│   └── cli.py                 # python -m ergoai.cli ...
├── scripts/
│   ├── descargar_modelo.py
│   ├── anotar_manual.py       # Fase 4
│   └── evaluar_precision.py   # Fase 4
└── tests/
    ├── fixtures/              # landmarks sintéticos en JSON (sin fotos reales)
    ├── test_geometria.py
    ├── test_angulos.py
    ├── test_reba.py
    └── test_pipeline.py
```

---

## 4. Entrada: `contexto.json`

Los comentarios son ilustrativos; el archivo real es JSON válido. Todo campo es opcional salvo `caso_id`.

```jsonc
{
  "caso_id": "caso01",
  "tipo_tarea": "levantamiento",        // levantamiento | transporte_con_auxiliar | transporte_sin_auxiliar | estacion
  "postura": "de_pie",                  // de_pie | sentado | alternada
  "orientacion_costado": null,          // "derecha" | "izquierda" | null = autodetectar
  "carga_kg": 8.0,
  "fuerza_brusca": false,               // choque o aumento rápido de fuerza (+1 en carga REBA)
  "agarre": "regular",                  // bueno | regular | malo | inaceptable
  "actividad": {
    "estatica_mas_1min": true,
    "repetitiva_mas_4_por_min": false,
    "cambios_bruscos_o_base_inestable": false
  },
  "hombro_elevado":        {"izquierdo": null, "derecho": null},
  "brazo_apoyado":         {"izquierdo": false, "derecho": false},
  "muneca_desviada_o_torcida": {"izquierdo": null, "derecho": null},
  "vertical_referencia":   {"costado": null, "frente": null},   // [[x1,y1],[x2,y2]] en px de una línea vertical real
  "persona_indice":        {"frente": null, "costado": null, "aerea": null},
  "overrides": {}                       // p. ej. {"tronco_flexion": 35}: valor del especialista
}
```

---

## 5. Fase 0 — Preparación

- `pyproject.toml` con las dependencias fijadas, paquete `src/ergoai`, `pytest` configurado.
- `.gitignore`, `scripts/descargar_modelo.py` y `config/umbrales.yaml` **exactamente** como el esqueleto de la sección 11.
- `config.py` valida el YAML con Pydantic y falla con un mensaje claro si falta una clave.

**Aceptación:** `pytest` corre (aunque haya pocas pruebas) y `python scripts/descargar_modelo.py` deja el modelo en `models/`.

---

## 6. Fase 1 — Carga de imágenes y pose

1. **Carga:** Pillow + `ImageOps.exif_transpose` (las fotos de celular vienen rotadas por EXIF), convertir a RGB, `np.asarray(..., dtype=np.uint8)`.
2. **Detección:** `RunningMode.IMAGE`, `num_poses=3` y confianzas tomadas de la config. Si hay varias personas, elegir la de mayor caja envolvente de landmarks visibles, salvo que `persona_indice` diga otra. Registrar cuántas personas se detectaron.
3. **Píxeles, no normalizados:** `x_px = x * ancho`, `y_px = y * alto`. **Todos los ángulos 2D se calculan en píxeles.** En coordenadas normalizadas, una imagen no cuadrada distorsiona los ángulos.
4. **Guardar por landmark:** `x_px, y_px, z, visibility, presence`. Guardar también `pose_world_landmarks` para las verificaciones 3D.
5. Un landmark es **utilizable** si `visibility >= vis_min` (config, por defecto 0.5).
6. **Sin detección en una vista:** no fallar. La vista queda `detectado=false` con su motivo.
7. **Riesgos que el código debe manejar y reportar:**
   - Fotos sin rostro (recortado o difuminado): los landmarks 0–10 pueden faltar o venir con baja visibilidad. Entonces el ángulo de cuello queda `None` y pasa a `pendientes_manuales`.
   - Vista aérea: no hay garantía de que BlazePose detecte bien desde arriba. Si hombros y caderas no son utilizables, esa vista no aporta y se reporta.
8. **Backend intercambiable:** `PoseBackend` (Protocol) con `detect(image) -> list[PoseResult]`. `MediaPipeBackend` lo implementa. Así se puede probar otro modelo (por ejemplo RTMPose) sin tocar el resto.

Índices que se usan (de `vision.PoseLandmark`): 0 nariz · 2/5 ojo izq./der. · 7/8 oreja izq./der. · 11/12 hombro · 13/14 codo · 15/16 muñeca · 17/18 meñique · 19/20 índice · 23/24 cadera · 25/26 rodilla · 27/28 tobillo · 29/30 talón · 31/32 punta del pie.

**Aceptación:** `python -m ergoai.cli pose data/casos/caso01` genera `out/caso01/pose.json` y una imagen por vista con el esqueleto dibujado con OpenCV, sin dibujar landmarks de la cara (0–10).

---

## 7. Fase 2 — Vectores y ángulos

### 7.1 Convenciones

- Coordenadas de imagen en píxeles; **y crece hacia abajo**.
- Puntos medios: `hombro_medio`, `cadera_media`, `oreja_media`; `mano_L = (índice_L + meñique_L) / 2` (igual para R).
- **Corrección de cámara inclinada:** si `vertical_referencia` existe para una vista, rotar todos los puntos de esa vista para que esa línea quede vertical antes de medir.
- **Dirección de mirada en la vista de costado:** `s = +1` si la persona mira hacia +x (derecha de la imagen) y `s = −1` si mira a la izquierda. Se determina en este orden:
  1. `orientacion_costado` del contexto.
  2. Promedio de `x(punta_pie) − x(talón)` de los pies utilizables.
  3. `x(nariz) − x(oreja_media)`, si son utilizables.
  4. Si nada funciona, `None`: los ángulos con signo de esa vista quedan pendientes.

  Registrar qué método se usó.
- **Lado cercano a la cámara (costado):** el lado (L/R) con mayor visibilidad promedio en hombro, codo, muñeca, cadera y rodilla. Si los dos lados superan `vis_min`, calcular ambos.

### 7.2 Vectores

Guardar todos en la salida, en píxeles y como unitarios.

| Vector | Definición |
|---|---|
| `v_tronco` | hombro_medio − cadera_media |
| `v_cuello` | oreja (lado cercano; si no, oreja_media) − hombro (lado cercano; si no, hombro_medio) |
| `v_brazo[L/R]` | codo − hombro |
| `v_antebrazo[L/R]` | muñeca − codo |
| `v_mano[L/R]` | mano − muñeca |
| `v_muslo[L/R]` | rodilla − cadera |
| `v_pierna[L/R]` | tobillo − rodilla |
| `linea_hombros` | hombro_R − hombro_L |
| `linea_caderas` | cadera_R − cadera_L |

### 7.3 Fórmulas (grados)

```text
angulo_entre(u, v) = degrees(arccos(clip(dot(u, v) / (|u|·|v|), −1, 1)))   ∈ [0, 180]
theta_arriba(v)    = degrees(atan2(s·v.x, −v.y))   # respecto a la vertical hacia ARRIBA; + = hacia donde mira (flexión)
theta_abajo(v)     = degrees(atan2(s·v.x,  v.y))   # respecto a la vertical hacia ABAJO;  + = hacia adelante
normalizar(a)      → (−180, 180]
```

| Medida | Vista primaria | Cálculo | Respaldo |
|---|---|---|---|
| Flexión de tronco | costado | `theta_arriba(v_tronco)`; + flexión, − extensión | 3D (world) |
| Flexión de cuello | costado | `theta_arriba(v_cuello) − theta_arriba(v_tronco) − cuello_offset_neutro` | 3D; sin oreja → `None` |
| Flexión de brazo L/R | costado | `theta_abajo(v_brazo) − theta_abajo(−v_tronco)` (relativa al tronco); + flexión, − extensión | 3D |
| Flexión de codo L/R | costado | `angulo_entre(v_brazo, v_antebrazo)` (0 = brazo recto) | frente, 3D |
| Flexión/extensión de muñeca L/R | costado | `angulo_entre(v_antebrazo, v_mano)` | siempre con bandera `baja_confianza_metodo` |
| Flexión de rodilla L/R | costado | `angulo_entre(v_muslo, v_pierna)` | frente |
| Inclinación lateral de tronco | frente | `abs(degrees(atan2(v_tronco.x, −v_tronco.y)))` | 3D |
| Torsión de tronco | aérea | ángulo entre `linea_hombros` y `linea_caderas`, plegado: `min(a, 180 − a)` | 3D: las mismas líneas proyectadas en el plano horizontal (x, z) de `pose_world_landmarks` |
| Abducción de brazo L/R | frente | `abs(normalizar(phi(v_brazo) − phi(−v_tronco)))` con `phi(v) = degrees(atan2(v.x, v.y))` | aérea |
| Inclinación o rotación de cuello | frente | vector cabeza (hombro_medio → nariz u ojos) contra `v_tronco` | sin cara → `None` |
| Apoyo de piernas | frente | unilateral si `abs(y_tobillo_L − y_tobillo_R) > umbral_pie_levantado × largo_pierna` | `postura` del contexto |
| Sentado | contexto | `postura` del contexto manda. Heurística solo como bandera: muslo a más de 60° de la vertical | — |

### 7.4 Verificación 3D y banderas

- Para codo, rodilla y la magnitud de la flexión de tronco, calcular también el ángulo con `pose_world_landmarks`. Si difiere del 2D en más de `umbral_discrepancia_3d_deg`, poner la bandera `posible_escorzo` (el segmento sale del plano de la foto).
- Banderas por ángulo:
  - `cerca_de_umbral`: a `margen_umbral_deg` o menos del límite de banda REBA más cercano.
  - `baja_visibilidad`: algún landmark usado tiene `visibility < vis_confiable`.
  - `posible_escorzo`: ver arriba.
  - `vista_respaldo`: se midió con la vista de respaldo.
  - `baja_confianza_metodo`: muñeca, o cuello sin oreja.
- `confianza` de cada ángulo = mínima visibilidad entre los landmarks que usa.

### 7.5 Anotación

Por vista, una imagen `out/<caso>/<vista>_angulos.png` con:
- El esqueleto, sin la cara.
- Los vectores usados dibujados como flechas.
- El valor de cada ángulo junto a su articulación, coloreado por su puntaje de banda REBA: 1 verde, 2 amarillo, 3 naranja, 4 o más rojo.
- Un “?” junto a cada ángulo con banderas.

**Aceptación:** pruebas de la sección 8.3 que aplican a geometría, y `python -m ergoai.cli angulos data/casos/caso01` genera `angulos.json` y las imágenes anotadas.

---

## 8. Fase 3 — Bandas y puntaje REBA

Fuente: Hignett, S. y McAtamney, L. (2000), *Rapid Entire Body Assessment (REBA)*, Applied Ergonomics 31: 201–205. **Copia las tablas exactamente.**

### 8.1 Bandas por segmento

Convención de límites (configurable con `limite_superior_inclusivo: true`): “0–20°” incluye 20°. **SUPUESTO: confirmar con Jabil.**

| Segmento | Puntaje base | Ajustes |
|---|---|---|
| Tronco | erguido (`abs(θ) <= tolerancia_neutro_deg`) → 1; flexión 0–20° o extensión 0–20° → 2; flexión 20–60° o extensión >20° → 3; flexión >60° → 4 | +1 si torsión > `umbral_torsion_tronco_deg` o inclinación lateral > `umbral_inclinacion_lateral_tronco_deg` |
| Cuello | flexión 0–20° → 1; flexión >20° o extensión (< −`tolerancia_neutro_deg`) → 2 | +1 si rotación o inclinación lateral > `umbral_cuello_lateral_rotacion_deg` |
| Piernas | apoyo bilateral, caminando o sentado → 1; apoyo unilateral, ligero o inestable → 2 | +1 si rodilla 30–60°; +2 si rodilla >60° (no aplica sentado) |
| Brazo | extensión 20° a flexión 20° → 1; extensión >20° o flexión 20–45° → 2; flexión 45–90° → 3; flexión >90° → 4 | +1 abducido (> `umbral_abduccion_brazo_deg`) o rotado; +1 hombro elevado; −1 brazo apoyado o asistido por gravedad (mínimo 1) |
| Antebrazo | flexión 60–100° → 1; <60° o >100° → 2 | — |
| Muñeca | flexión/extensión 0–15° → 1; >15° → 2 | +1 desviada o torcida |

Las bandas de tronco coinciden con la imagen de referencia de la hoja EAWS del Excel de Jabil (0° neutro; −20° a 20°; menos de −20° o 20–60°; más de 60°).

### 8.2 Tablas

**Tabla A** (tronco × cuello × piernas):

| Tronco \ Piernas | C1: 1 | 2 | 3 | 4 | C2: 1 | 2 | 3 | 4 | C3: 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 2 | 3 | 4 | 1 | 2 | 3 | 4 | 3 | 3 | 5 | 6 |
| 2 | 2 | 3 | 4 | 5 | 3 | 4 | 5 | 6 | 4 | 5 | 6 | 7 |
| 3 | 2 | 4 | 5 | 6 | 4 | 5 | 6 | 7 | 5 | 6 | 7 | 8 |
| 4 | 3 | 5 | 6 | 7 | 5 | 6 | 7 | 8 | 6 | 7 | 8 | 9 |
| 5 | 4 | 6 | 7 | 8 | 6 | 7 | 8 | 9 | 7 | 8 | 9 | 9 |

(C1, C2, C3 = puntaje de cuello 1, 2, 3.)

**Carga/fuerza:** menos de 5 kg → 0; 5–10 kg → 1; más de 10 kg → 2; +1 si `fuerza_brusca`. **Puntaje A = Tabla A + carga.**

**Tabla B** (brazo × antebrazo × muñeca):

| Brazo \ Muñeca | AB1: 1 | 2 | 3 | AB2: 1 | 2 | 3 |
|---|---|---|---|---|---|---|
| 1 | 1 | 2 | 2 | 1 | 2 | 3 |
| 2 | 1 | 2 | 3 | 2 | 3 | 4 |
| 3 | 3 | 4 | 5 | 4 | 5 | 5 |
| 4 | 4 | 5 | 5 | 5 | 6 | 7 |
| 5 | 6 | 7 | 8 | 7 | 8 | 8 |
| 6 | 7 | 8 | 8 | 8 | 9 | 9 |

(AB1, AB2 = puntaje de antebrazo 1, 2.)

**Agarre:** bueno 0; regular 1; malo 2; inaceptable 3. **Puntaje B = Tabla B + agarre.**

**Tabla C** (filas = Puntaje A 1–12; columnas = Puntaje B 1–12):

| A \ B | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 1 | 2 | 3 | 3 | 4 | 5 | 6 | 7 | 7 | 7 |
| 2 | 1 | 2 | 2 | 3 | 4 | 4 | 5 | 6 | 6 | 7 | 7 | 8 |
| 3 | 2 | 3 | 3 | 3 | 4 | 5 | 6 | 7 | 7 | 8 | 8 | 8 |
| 4 | 3 | 4 | 4 | 4 | 5 | 6 | 7 | 8 | 8 | 9 | 9 | 9 |
| 5 | 4 | 4 | 4 | 5 | 6 | 7 | 8 | 8 | 9 | 9 | 9 | 9 |
| 6 | 6 | 6 | 6 | 7 | 8 | 8 | 9 | 9 | 10 | 10 | 10 | 10 |
| 7 | 7 | 7 | 7 | 8 | 9 | 9 | 9 | 10 | 10 | 11 | 11 | 11 |
| 8 | 8 | 8 | 8 | 9 | 10 | 10 | 10 | 10 | 10 | 11 | 11 | 11 |
| 9 | 9 | 9 | 9 | 10 | 10 | 10 | 11 | 11 | 11 | 12 | 12 | 12 |
| 10 | 10 | 10 | 10 | 11 | 11 | 11 | 11 | 12 | 12 | 12 | 12 | 12 |
| 11 | 11 | 11 | 11 | 11 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 |
| 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 |

**Actividad:** +1 por cada uno: estática más de 1 min; repetitiva más de 4 veces/min; cambios bruscos o base inestable.

**REBA final = Tabla C + actividad.**

| REBA | Nivel de riesgo | Nivel de acción |
|---|---|---|
| 1 | Inapreciable | 0 |
| 2–3 | Bajo | 1 |
| 4–7 | Medio | 2 |
| 8–10 | Alto | 3 |
| 11–15 | Muy alto | 4 |

### 8.3 Reglas de cálculo

- El Grupo B (brazo, antebrazo, muñeca) se calcula para **izquierdo y derecho**. Se reporta REBA por lado y un REBA final según `lado_reportado` (config: `peor` | `izquierdo` | `derecho`; por defecto `peor`). **SUPUESTO: confirmar con Jabil.**
- Si un insumo es `None`, el REBA final es `None` y se listan los pendientes. No se calcula con valores supuestos.
- `overrides` del contexto reemplaza el valor medido. Se registra `fuente: "especialista"` y se conserva el valor medido para la bitácora.

### 8.4 Pruebas obligatorias (`tests/test_reba.py`, `tests/test_geometria.py`)

1. **Caso completo calculado a mano:** tronco 3, cuello 2, piernas 2 → Tabla A = 5; carga 8 kg → +1 → A = 6. Brazo 3, antebrazo 2, muñeca 2 → Tabla B = 5; agarre regular → +1 → B = 6. Tabla C(6, 6) = 8; actividad estática → +1 → **REBA 9, “Alto”, nivel de acción 3**.
2. **Esquinas de tablas:** A(tronco 1, cuello 1, piernas 1) = 1; A(5, 3, 4) = 9; B(brazo 1, antebrazo 1, muñeca 1) = 1; B(6, 2, 3) = 9; C(1, 1) = 1; C(12, 12) = 12.
3. **Límites de banda:** 19.9°, 20°, 20.1°, 45°, 60°, 90° y 100° para cada segmento, según la convención configurada.
4. **Signo:** un tronco inclinado 30° hacia adelante debe dar +30° tanto mirando a la derecha (`s = +1`) como a la izquierda (`s = −1`). Hacia atrás debe dar −30°.
5. **Relación de aspecto:** imagen de 1920 × 1080 con un tronco realmente a 45°. Tras convertir a píxeles debe dar 45°. La prueba también demuestra que en coordenadas normalizadas daría otro valor.
6. **Brazo:** colgando con tronco erguido → 0°; horizontal al frente → 90°; 30° hacia atrás → −30°.
7. **Pipeline sin MediaPipe:** un JSON de landmarks sintéticos en `tests/fixtures/` produce el REBA esperado de punta a punta.

**Aceptación:** todas las pruebas pasan y `python -m ergoai.cli evaluar data/casos/caso01` genera `out/caso01/resultado.json`.

---

## 9. Salida: `out/<caso_id>/resultado.json`

```jsonc
{
  "caso_id": "caso01",
  "version_modelo": "pose_landmarker_heavy / mediapipe 1.1.1",
  "vistas": {
    "costado": {"detectado": true, "personas_detectadas": 1, "orientacion": {"s": 1, "metodo": "pies"},
                "lado_cercano": "R", "landmarks": [...], "world_landmarks": [...]}
  },
  "vectores": {"costado": {"v_tronco": {"px": [12.0, -310.5], "unitario": [0.04, -0.99]}}},
  "angulos": [
    {"medida": "tronco_flexion", "lado": null, "valor_deg": 34.2, "vista": "costado",
     "metodo": "theta_arriba(v_tronco)", "confianza": 0.93, "valor_3d_deg": 36.0,
     "banda_reba": 3, "fuente": "automatico", "banderas": []}
  ],
  "reba": {
    "grupo_a": {"tronco": 3, "cuello": 2, "piernas": 2, "tabla_a": 5, "carga": 1, "puntaje_a": 6},
    "grupo_b": {"R": {"brazo": 3, "antebrazo": 2, "muneca": 2, "tabla_b": 5, "agarre": 1, "puntaje_b": 6},
                "L": {"...": "..."}},
    "tabla_c": {"R": 8, "L": 7}, "actividad": 1,
    "final": {"R": 9, "L": 8, "reportado": 9, "lado": "R"},
    "nivel_riesgo": "Alto", "nivel_accion": 3
  },
  "pendientes_manuales": [{"medida": "cuello_flexion", "motivo": "orejas no visibles (foto sin rostro)"}],
  "advertencias": ["vista aerea: sin deteccion"]
}
```

---

## 10. Fase 4 — Medir la precisión antes de la competencia

Sin esto no se sabe si se llega al 90 % del criterio 2.

1. `scripts/anotar_manual.py`: herramienta OpenCV. Abre una foto, pide hacer clic en las articulaciones en un orden fijo (hombro, codo, muñeca, mano, cadera, rodilla, tobillo, talón, punta del pie, oreja, por lado) y guarda `referencia.json` en el mismo formato de landmarks. Los ángulos de referencia se calculan con **las mismas fórmulas** de la Fase 2.
2. `scripts/evaluar_precision.py`: compara lo automático contra la referencia en todos los casos de `data/validacion/` y reporta:
   - Error absoluto por segmento (media y máximo).
   - **% de segmentos en la misma banda REBA** (métrica del criterio 2).
   - **% de casos con el mismo puntaje y nivel REBA** (métrica del criterio 1).
   - Tabla de fallos ordenada por error, con vista y banderas.

   Salida: CSV y un resumen en consola.
3. Meta: 90 % o más de segmentos en la misma banda. Si no se alcanza, reportar qué segmentos y vistas fallan. No ajustar umbrales para “ganar” la métrica.

---

## 11. Esqueleto de `config/umbrales.yaml`

```yaml
pose:
  modelo: models/pose_landmarker_heavy.task
  num_poses: 3
  min_pose_detection_confidence: 0.5
  min_pose_presence_confidence: 0.5
  vis_min: 0.5                 # landmark utilizable
  vis_confiable: 0.7           # por debajo -> bandera baja_visibilidad

angulos:
  cuello_offset_neutro_deg: 0           # SUPUESTO: calibrar con una foto en postura neutra
  umbral_discrepancia_3d_deg: 15        # SUPUESTO
  umbral_pie_levantado: 0.10            # fracción del largo de pierna; SUPUESTO
  margen_umbral_deg: 5                  # bandera cerca_de_umbral

reba:                                   # Hignett y McAtamney (2000)
  limite_superior_inclusivo: true       # SUPUESTO: confirmar con Jabil
  tolerancia_neutro_deg: 5              # "erguido"; SUPUESTO: confirmar con Jabil
  tronco: {leve: 20, moderado: 60}
  cuello: {flexion: 20}
  brazo: {neutro: 20, medio: 45, alto: 90}
  antebrazo: {min: 60, max: 100}
  muneca: {flexion: 15}
  rodilla: {leve: 30, alta: 60}
  carga_kg: {baja: 5, alta: 10}
  umbral_torsion_tronco_deg: 20         # Excel Jabil 00014, hoja EAWS (torsión >= 20° suma); REBA no da número
  umbral_inclinacion_lateral_tronco_deg: 10   # SUPUESTO: confirmar con Jabil
  umbral_cuello_lateral_rotacion_deg: 10      # SUPUESTO: confirmar con Jabil
  umbral_abduccion_brazo_deg: 20              # SUPUESTO: confirmar con Jabil
  lado_reportado: peor                        # SUPUESTO: confirmar con Jabil

jabil:
  angulo_apertura: null                 # PENDIENTE: estudio de Jabil, se pide el 28 oct
```

---

## 12. Fase 5 (opcional, solo con F1–F4 completas): complementos

Cada uno es un módulo aparte con sus pruebas y **no cambia el REBA**.

### 12.1 RULA (Excel Jabil 00014, hoja “Mov”; idéntico a McAtamney y Corlett, 1993)

Bandas:
- Brazo: −20° a 20° → 1; extensión >20° o 20–45° → 2; 45–90° → 3; >90° → 4. +1 hombro elevado; +1 abducido; −1 apoyado.
- Antebrazo: 60–100° → 1; 0–60° o >100° → 2. +1 si cruza la línea media o sale del cuerpo.
- Muñeca: 0° → 1; 0–15° → 2; >15° → 3. +1 desviada. Giro: rango medio → 1; final → 2.
- Cuello: 0–10° → 1; 10–20° → 2; >20° → 3; extensión → 4. +1 rotado; +1 inclinado.
- Tronco: erguido o sentado bien apoyado → 1; 0–20° → 2; 20–60° → 3; >60° → 4. +1 torsión; +1 inclinación lateral.
- Piernas: apoyadas y equilibradas → 1; si no → 2.
- Actividad muscular: estática >1 min o ≥4 veces/min → +1.
- Carga: <2 kg intermitente → 0; 2–10 kg intermitente → 1; 2–10 kg estática/repetitiva o >10 kg intermitente → 2; >10 kg estática/repetitiva o golpes → 3.

Tabla A (filas brazo-antebrazo; columnas muñeca 1–4 × giro 1–2):

| Brazo | Antebrazo | M1 G1 | M1 G2 | M2 G1 | M2 G2 | M3 G1 | M3 G2 | M4 G1 | M4 G2 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 1 | 2 | 2 | 2 | 2 | 3 | 3 | 3 |
| 1 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 3 | 3 |
| 1 | 3 | 2 | 3 | 3 | 3 | 3 | 3 | 4 | 4 |
| 2 | 1 | 2 | 3 | 3 | 3 | 3 | 4 | 4 | 4 |
| 2 | 2 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 4 |
| 2 | 3 | 3 | 4 | 4 | 4 | 4 | 4 | 5 | 5 |
| 3 | 1 | 3 | 3 | 4 | 4 | 4 | 4 | 5 | 5 |
| 3 | 2 | 3 | 4 | 4 | 4 | 4 | 4 | 5 | 5 |
| 3 | 3 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 5 |
| 4 | 1 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 5 |
| 4 | 2 | 4 | 4 | 4 | 4 | 4 | 5 | 5 | 5 |
| 4 | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 6 | 6 |
| 5 | 1 | 5 | 5 | 5 | 5 | 5 | 6 | 6 | 7 |
| 5 | 2 | 5 | 6 | 6 | 6 | 6 | 7 | 7 | 7 |
| 5 | 3 | 6 | 6 | 6 | 7 | 7 | 7 | 7 | 8 |
| 6 | 1 | 7 | 7 | 7 | 7 | 7 | 8 | 8 | 9 |
| 6 | 2 | 8 | 8 | 8 | 8 | 8 | 9 | 9 | 9 |
| 6 | 3 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |

Tabla B (filas cuello 1–6; columnas tronco 1–6 × piernas 1–2):

| Cuello | T1 P1 | T1 P2 | T2 P1 | T2 P2 | T3 P1 | T3 P2 | T4 P1 | T4 P2 | T5 P1 | T5 P2 | T6 P1 | T6 P2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 3 | 2 | 3 | 3 | 4 | 5 | 5 | 6 | 6 | 7 | 7 |
| 2 | 2 | 3 | 2 | 3 | 4 | 5 | 5 | 5 | 6 | 7 | 7 | 7 |
| 3 | 3 | 3 | 3 | 4 | 4 | 5 | 5 | 6 | 6 | 7 | 7 | 7 |
| 4 | 5 | 5 | 5 | 6 | 6 | 7 | 7 | 7 | 7 | 7 | 8 | 8 |
| 5 | 7 | 7 | 7 | 7 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |
| 6 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 9 | 9 | 9 | 9 | 9 |

Puntaje C = Tabla A + actividad + carga (tope 8). Puntaje D = Tabla B + actividad + carga (tope 7).

Tabla C (filas C 1–8+; columnas D 1–7+):

| C \ D | 1 | 2 | 3 | 4 | 5 | 6 | 7+ |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 2 | 3 | 3 | 4 | 5 | 5 |
| 2 | 2 | 2 | 3 | 4 | 4 | 5 | 5 |
| 3 | 3 | 3 | 3 | 4 | 4 | 5 | 6 |
| 4 | 3 | 3 | 3 | 4 | 5 | 6 | 6 |
| 5 | 4 | 4 | 4 | 5 | 6 | 7 | 7 |
| 6 | 4 | 4 | 5 | 6 | 6 | 7 | 7 |
| 7 | 5 | 5 | 6 | 6 | 7 | 7 | 7 |
| 8+ | 5 | 5 | 6 | 7 | 7 | 7 | 7 |

Nivel: 1–2 → 1; 3–4 → 2; 5–6 → 3; 7 → 4.

### 12.2 EAWS simplificado (Excel Jabil 00014, hoja “EAWS”)

Entradas: tiempo de ciclo (s), frecuencia (veces/ciclo), fuerza (kg), flexión de tronco (°), torsión de tronco (°), trabajo sobre el hombro (0/1), trabajo bajo la rodilla (0/1), duración del turno (h), tiempo del movimiento evaluado (s).

```text
duracion_min_turno = (t_mov · frecuencia · (3600 / t_ciclo) · horas_turno) / 60
postura    = (1 si flexion < 20; 3 si < 45; si no 6) + (0 si torsion < 20; si no 2) + 2·sobre_hombro + 2·bajo_rodilla
fuerza     = 1 si kg < 5; 3 si < 10; si no 6
acciones   = (duracion_min_turno · 60 / t_ciclo) · frecuencia
frecuencia = 1 si acciones < 100; 3 si < 500; si no 6
total      = postura + fuerza + frecuencia  →  ≤5 Bajo; ≤10 Medio; >10 Alto
```

### 12.3 Sugerencias visuales NOM-036-1-STPS-2018 (Apéndices I y II)

Siempre marcadas como `sugerencia: confirmar por el especialista`. Los umbrales de “torso inclinado” van en la config como SUPUESTO.

- **Levantamiento, distancia horizontal manos–espalda baja:** brazos verticales y torso erguido → verde 0; brazos alejados del cuerpo → naranja 3; torso inclinado hacia adelante → naranja 3; brazos alejados y torso inclinado → rojo 6.
- **Región vertical de las manos:** sobre la rodilla y bajo el codo → verde 0; bajo la rodilla o sobre el codo → naranja 1; a nivel del piso o a la altura de la cabeza o más arriba → rojo 3.
- **Torsión y flexión lateral del torso:** poca o ninguna → 0; torsión o flexión lateral → 1; torsión y flexión lateral → 2.
- **Transporte, carga asimétrica:** carga y manos simétricas al frente → 0; asimétricas con el cuerpo vertical → 1; con una mano a un lado → 2; carga sobre un hombro → 3.
- **Empuje/arrastre, postura:** torso vertical sin torsión y manos entre cadera y hombro → 0; cuerpo inclinado hacia el esfuerzo, torso visiblemente flexionado o torcido, o manos bajo la cadera → 3; cuerpo muy inclinado, en cuclillas o arrodillado, torso severamente flexionado o torcido, o manos detrás, a un lado o sobre el hombro → 6.

### 12.4 Muñeca con HandLandmarker

Recortar la región de cada mano alrededor de la muñeca, correr `vision.HandLandmarker` y medir la flexión con el eje de los metacarpianos. Comparar contra la Fase 4 antes de adoptarlo.
