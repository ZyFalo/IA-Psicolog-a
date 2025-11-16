# Arquitectura del Proyecto

## Vista General

```
IA Psicología/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Entry point
│   │   ├── config.py          # Configuración
│   │   ├── core/              # Lógica core
│   │   │   ├── model_manager.py      # Gestión modelo
│   │   │   ├── session_manager.py    # Gestión sesiones
│   │   │   └── guardrails.py         # Sistema seguridad
│   │   └── api/               # Endpoints API
│   │       ├── chat.py        # Chat endpoints
│   │       ├── voice.py       # Voz endpoints
│   │       └── health.py      # Health checks
│   ├── requirements.txt
│   ├── .env.example
│   └── pytest.ini
│
├── frontend/                   # Frontend React (futuro)
│   └── [Por implementar]
│
├── models/                     # Modelos ML
│   ├── qwen2.5-7b/           # Modelo base
│   └── lora_adapters/        # Adaptadores LoRA
│
├── data/                      # Datasets
│   ├── training/             # Dataset entrenamiento
│   ├── validation/           # Dataset validación
│   └── DATASET_FORMAT.md     # Documentación formato
│
├── scripts/                   # Scripts utilidad
│   ├── download_model.py     # Descarga modelo
│   ├── finetune.py          # Fine-tuning
│   └── dataset_tools.py     # Herramientas dataset
│
├── tests/                     # Tests
│   ├── test_guardrails.py
│   └── test_session_manager.py
│
├── docs/                      # Documentación
│   ├── QUICKSTART.md
│   └── ARCHITECTURE.md       # Este archivo
│
├── README.md                  # Documentación principal
├── .gitignore
└── setup.sh                   # Setup automático
```

## Flujo de Datos

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │ Texto/Voz
       ▼
┌─────────────────────┐
│  Frontend (React)   │
│  - Chat UI          │
│  - Voice recorder   │
│  - Avatar           │
└──────┬──────────────┘
       │ HTTP/WebSocket
       ▼
┌──────────────────────────────────────┐
│       FastAPI Backend                │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  API Layer                     │ │
│  │  - /api/chat/message           │ │
│  │  - /api/voice/transcribe       │ │
│  │  - /api/voice/synthesize       │ │
│  └───────────┬────────────────────┘ │
│              │                       │
│  ┌───────────▼────────────────────┐ │
│  │  Guardrails Engine             │ │
│  │  - Pre-filtro (crisis input)   │ │
│  │  - Post-filtro (valid output)  │ │
│  └───────────┬────────────────────┘ │
│              │                       │
│  ┌───────────▼────────────────────┐ │
│  │  Session Manager               │ │
│  │  - Context window              │ │
│  │  - Conversation memory         │ │
│  │  - Prompt formatting           │ │
│  └───────────┬────────────────────┘ │
│              │                       │
│  ┌───────────▼────────────────────┐ │
│  │  Model Manager                 │ │
│  │  - Qwen2.5-7B + LoRA           │ │
│  │  - Inference (MPS)             │ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│  Respuesta  │
└─────────────┘
```

## Componentes Principales

### 1. Model Manager

**Responsabilidades:**
- Cargar modelo base (Qwen2.5-7B)
- Aplicar cuantización (4-bit/8-bit)
- Cargar adaptadores LoRA si existen
- Ejecutar inferencia
- Gestionar recursos GPU/MPS

**Métodos clave:**
```python
async def load_model()
async def generate(prompt, max_tokens, temperature, top_p)
async def cleanup()
```

### 2. Session Manager

**Responsabilidades:**
- Crear y gestionar sesiones de usuario
- Mantener contexto conversacional
- Formatear prompts para el modelo
- Limpiar sesiones expiradas

**Métodos clave:**
```python
def create_session() -> str
def add_message(session_id, role, content)
def get_conversation_history(session_id)
def format_for_model(session_id) -> str
```

### 3. Guardrails Engine

**Responsabilidades:**
- Detectar crisis en input del usuario
- Validar respuestas del modelo
- Activar protocolo de derivación
- Filtrar contenido inapropiado

**Componentes:**
- **CrisisDetector:** Keywords + patterns de crisis
- **ContentFilter:** Validar no diagnóstico/prescripción
- **GuardrailResult:** Estructura de respuesta

**Métodos clave:**
```python
def check_input(text) -> GuardrailResult
def check_output(response) -> (is_valid, violations)
def get_fallback_response() -> str
```

## Decisiones de Diseño

### ¿Por qué FastAPI?

✅ Async/await nativo (importante para streaming)  
✅ Documentación automática (OpenAPI)  
✅ Type hints con Pydantic  
✅ WebSocket support  
✅ Alto performance

### ¿Por qué LoRA/QLoRA?

✅ Fine-tuning eficiente en 16GB RAM  
✅ Solo entrena ~1% de parámetros  
✅ Rápido (horas vs días)  
✅ Múltiples adaptadores posibles  
✅ Fácil de iterar

### ¿Por qué Cuantización 4-bit?

✅ Reduce ~14GB → ~4GB  
✅ Viable en MacBook Air M4 16GB  
✅ Pérdida mínima de calidad  
✅ Latencia aceptable (2-5 tokens/seg)

### ¿Por qué MPS (Metal)?

✅ Optimizado para Apple Silicon  
✅ Mejor que CPU (3-5x más rápido)  
✅ Integrado en PyTorch  
✅ Sin dependencias externas

### ¿Por qué Local vs Cloud?

✅ **Privacidad total:** Datos no salen del dispositivo  
✅ **Sin costos API:** No pagar por token  
✅ **Offline:** Funciona sin internet  
✅ **Control total:** Sobre modelo y guardrails  
✅ **Cumplimiento:** GDPR/HIPAA friendly

## Patrones de Código

### Dependency Injection

```python
def get_model_manager() -> ModelManager:
    from app.main import model_manager
    return model_manager

@router.post("/message")
async def send_message(
    request: ChatRequest,
    model_manager: ModelManager = Depends(get_model_manager)
):
    ...
```

### Lifecycle Management

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    model_manager = ModelManager(settings)
    await model_manager.load_model()
    
    yield
    
    # Shutdown
    await model_manager.cleanup()
```

### Structured Logging (sin PII)

```python
logger.info(
    f"🔍 Crisis detection: risk_level={risk_level.value}, "
    f"score={risk_score:.2f}, rules={len(triggered_rules)}"
)
# NO incluir contenido del mensaje
```

## Seguridad

### Guardrails Multi-capa

1. **Pre-filtro (Input):**
   - Detectar crisis keywords
   - Detectar patterns de riesgo
   - Calcular risk score

2. **Generación:**
   - Prompt engineering (system prompt)
   - Temperature control
   - Max tokens limit

3. **Post-filtro (Output):**
   - Validar no diagnóstico
   - Validar no prescripción
   - Fallback si inválido

### Protocolo de Crisis

```python
if risk_level == CRITICAL:
    return emergency_response
    terminate_session()
    log_activation(no_pii=True)
```

## Performance

### Optimizaciones

- ✅ Cuantización 4-bit
- ✅ Gradient checkpointing (training)
- ✅ KV-cache (inference)
- ✅ Batch size = 1 (baja latencia)
- ✅ MPS device (Apple Silicon)

### Métricas Objetivo

- **Latencia:** < 3s para texto, < 5s para voz
- **Throughput:** 2-5 tokens/seg
- **Memoria:** < 8GB durante inferencia
- **CPU:** < 60% uso promedio

## Extensibilidad

### Añadir Nueva Técnica

1. Actualizar `DATASET_FORMAT.md`
2. Añadir ejemplos al dataset
3. Re-entrenar con LoRA
4. Actualizar tests

### Añadir Nuevo Guardrail

1. Crear clase en `guardrails.py`
2. Añadir a `GuardrailsEngine`
3. Escribir tests
4. Documentar en README

### Integrar Nueva Modalidad

1. Crear endpoint en `api/`
2. Implementar procesamiento
3. Integrar con pipeline existente
4. Actualizar frontend

## Testing

### Capas de Testing

```
Unit Tests
  ↓ test_guardrails.py
  ↓ test_session_manager.py
  ↓ test_model_manager.py

Integration Tests
  ↓ test_api_chat.py
  ↓ test_full_flow.py

E2E Tests
  ↓ test_frontend_integration.py
```

### Cobertura Objetivo

- **Core:** > 90%
- **API:** > 80%
- **Total:** > 85%

## Deployment

### Desarrollo

```bash
uvicorn app.main:app --reload --port 8000
```

### Producción

```bash
uvicorn app.main:app --workers 1 --port 8000
```

**Nota:** Workers=1 porque el modelo consume mucha RAM

## Monitoreo

### Métricas (sin PII)

- Latencia promedio por request
- Activaciones de guardrails (por tipo)
- Sesiones activas
- Uso de memoria/CPU
- Errores y excepciones

### Logs

```
INFO: Nueva sesión creada
INFO: Crisis detection: risk_level=high
WARNING: Respuesta inválida, usando fallback
ERROR: Error en generación
```

## Roadmap Técnico

### v0.1 (Actual)
- ✅ Backend básico
- ✅ Guardrails
- ✅ Session management
- ✅ Model inference

### v0.2 (Próximo)
- ⏳ Frontend React
- ⏳ Whisper integration
- ⏳ TTS integration
- ⏳ Avatar básico

### v0.3 (Futuro)
- ⏳ Emotion detection en voz
- ⏳ Resumen automático
- ⏳ Métricas avanzadas
- ⏳ A/B testing framework

### v1.0 (Release)
- ⏳ Testing completo
- ⏳ Documentación usuario
- ⏳ Instalador
- ⏳ Despliegue piloto
