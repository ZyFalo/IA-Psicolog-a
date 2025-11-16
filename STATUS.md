# 🧠 Asistente Psicoeducativo IA - Estado del Proyecto

**Última actualización**: 16 de noviembre de 2025  
**Versión**: 1.0 - Funcional  
**Hardware**: MacBook Air M4, 16GB RAM

---

## ✅ COMPONENTES FUNCIONALES

### 🤖 Modelo de IA
- **Modelo**: Qwen/Qwen2.5-7B-Instruct
- **Framework**: MLX (optimizado para Apple Silicon)
- **Cuantización**: 4-bit (~4GB)
- **Ubicación**: `models/qwen2.5-7b-mlx/`
- **Rendimiento**: 
  - Carga: ~1.6s
  - Velocidad: ~20 tokens/seg
  - Memoria: ~5GB RAM

### 🖥️ Backend API (FastAPI)
**Estado**: ✅ Completamente funcional

**Archivos principales**:
```
backend/app/
├── main.py                    # Servidor FastAPI
├── config.py                  # Configuración
├── core/
│   ├── model_manager_mlx.py  # Gestor del modelo MLX
│   ├── session_manager.py    # Sesiones + resúmenes automáticos
│   └── guardrails.py         # Detección de crisis
└── api/
    ├── chat.py               # Endpoints de chat
    ├── health.py             # Health checks
    └── voice.py              # ⚠️ Placeholders (no implementado)
```

**Endpoints disponibles**:
- `POST /api/chat/message` - Enviar mensaje
- `GET /api/chat/sessions/{id}/history` - Historial
- `POST /api/chat/sessions` - Nueva sesión
- `GET /api/health` - Estado del sistema

**Iniciar servidor**:
```bash
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload
```

### 💬 Chat en Terminal
**Estado**: ✅ Completamente funcional

**Archivo**: `scripts/chat_terminal.py`

**Características**:
- Memoria de 20 mensajes
- Resúmenes automáticos >40 mensajes
- Detección de crisis con guardrails
- Comandos: `salir`, `limpiar`, `guardar`, `cargar`

**Ejecutar**:
```bash
source venv/bin/activate
python scripts/chat_terminal.py
```

### 🌐 Interfaz Web
**Estado**: ✅ Lista (requiere backend activo)

**Archivo**: `frontend/chat.html`

**Abrir**:
```bash
# Terminal 1: Iniciar backend
cd backend && uvicorn app.main:app --reload

# Terminal 2 o navegador:
open frontend/chat.html
```

### 🛡️ Sistema de Guardrails
**Estado**: ✅ Funcional

**Archivo**: `backend/app/core/guardrails.py`

**Capacidades**:
- Detección de crisis (suicidio, autolesión)
- Filtrado de contenido inapropiado
- Niveles de riesgo: LOW, MEDIUM, HIGH, CRITICAL
- Respuestas de emergencia automáticas
- ~350 líneas, 20+ tests

### 📝 Gestión de Sesiones
**Estado**: ✅ Funcional con resúmenes automáticos

**Archivo**: `backend/app/core/session_manager.py`

**Características**:
- Ventanas de contexto configurables
- Resúmenes automáticos al superar 40 mensajes
- Expiración de sesiones inactivas
- Sistema de mensajes con timestamps
- ~200 líneas, 15+ tests

---

## 📦 DEPENDENCIAS INSTALADAS

**Archivo**: `backend/requirements-mlx.txt`

```
mlx>=0.29.0              # Framework Apple Silicon
mlx-lm>=0.28.0           # Modelos de lenguaje
torch>=2.0.0             # PyTorch base
transformers>=4.39.0     # Hugging Face
fastapi>=0.100.0         # API REST
uvicorn[standard]        # Servidor ASGI
pydantic>=2.0.0          # Validación
```

**Instaladas exitosamente**:
- ✅ MLX 0.29.4
- ✅ torch 2.9.1
- ✅ transformers 4.57.1
- ✅ fastapi 0.121.2
- ✅ accelerate 1.11.0
- ✅ bitsandbytes 0.42.0
- ✅ scipy 1.16.3

---

## 🧪 TESTING

**Ubicación**: `tests/`

**Tests disponibles**:
- `test_guardrails.py` - 20+ tests de detección de crisis
- `test_session_manager.py` - 15+ tests de sesiones

**Ejecutar**:
```bash
pytest tests/ -v
```

---

## 📚 DOCUMENTACIÓN

```
docs/
├── ARCHITECTURE.md      # Arquitectura del sistema
├── QUICKSTART.md        # Guía de inicio rápido
└── MODELO_MLX_SETUP.md  # Setup y rendimiento de MLX
```

**Dataset**:
- `data/DATASET_FORMAT.md` - Especificación completa con ejemplos

---

## 🚀 COMANDOS RÁPIDOS

### Probar el modelo
```bash
python -c "
from backend.app.core.model_manager_mlx import ModelManagerMLX
manager = ModelManagerMLX()
manager.load_model()
print(manager.generate_chat([{'role': 'user', 'content': 'Hola'}]))
"
```

### Chat interactivo
```bash
python scripts/chat_terminal.py
```

### Iniciar backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Ver info del modelo
```bash
python -c "
from backend.app.core.model_manager_mlx import ModelManagerMLX
m = ModelManagerMLX()
m.load_model()
print(m.get_model_info())
"
```

---

## 📊 CARACTERÍSTICAS DEL SISTEMA

### Memoria y Contexto
- **Configuración actual**: 20 mensajes en memoria
- **Resúmenes automáticos**: Se activan >40 mensajes
- **Persistencia**: Guardar/cargar conversaciones en JSON
- **Ventana máxima**: ~32,768 tokens (límite del modelo)

### Guardrails
- **Palabras clave crisis**: ~50 patrones
- **Patrones regex**: Detección avanzada
- **Respuestas emergencia**: Automáticas con recursos
- **Filtros contenido**: Diagnósticos, prescripciones

### Rendimiento
- **Carga inicial**: 1.6 segundos
- **Primera respuesta**: 2-4 segundos
- **Respuestas siguientes**: 2-3 segundos
- **Velocidad**: ~20 tokens/seg (~12 palabras/seg)
- **Memoria RAM**: ~5GB durante uso

---

## ⚠️ PENDIENTES / NO IMPLEMENTADOS

### Fine-tuning
- ❌ Script de fine-tuning con MLX
- ❌ Dataset de entrenamiento (500-2000 ejemplos)
- 📝 Formato documentado en `data/DATASET_FORMAT.md`

### Voice Features
- ❌ Whisper ASR (speech-to-text)
- ❌ Piper TTS (text-to-speech)
- 📝 Placeholders en `backend/app/api/voice.py` (88 líneas de esqueleto)

### Mejoras Futuras
- [ ] Integración con base de datos
- [ ] Autenticación de usuarios
- [ ] Dashboard de métricas
- [ ] Logs estructurados
- [ ] Docker deployment
- [ ] Tests de integración E2E

---

## 🗂️ ARCHIVOS OBSOLETOS

Movidos a `_obsolete/`:
- `model_manager.py` - Versión PyTorch (reemplazada por MLX)
- `download_model.py` - Usaba bitsandbytes incompatible
- `finetune.py` - LoRA para PyTorch (no MLX)
- `export_to_ollama.sh` - No necesario
- Documentación antigua

---

## 📈 PRÓXIMOS PASOS SUGERIDOS

1. **Crear dataset de entrenamiento**
   - Formato: JSONL según `data/DATASET_FORMAT.md`
   - Cantidad: 500-2000 ejemplos
   - Distribución: 40% check-in, 30% técnicas, 20% crisis, 10% resúmenes

2. **Adaptar fine-tuning a MLX**
   - Usar `mlx-lm.tune` o `mlx-lm.fuse`
   - LoRA con rank 8-16
   - Cuantización 4-bit

3. **Mejorar guardrails**
   - Reducir falsos positivos
   - Más patrones de crisis
   - Niveles de riesgo más granulares

4. **Frontend mejorado**
   - React o Vue.js
   - WebSocket para streaming
   - Historial de sesiones

---

## 📞 RECURSOS DE CRISIS

El sistema recomienda estos recursos en crisis:

- **México**:
  - Línea de la Vida: 800-911-2000
  - SAPTEL: 55-5259-8121

- **España**:
  - Teléfono de la Esperanza: 717-003-717

- **Internacional**:
  - Crisis Text Line: https://www.crisistextline.org/

---

**Estado**: 🟢 Sistema funcional y listo para uso  
**Hardware**: Optimizado para Apple Silicon (M1/M2/M3/M4)  
**Licencia**: Ver LICENSE (si aplica)
