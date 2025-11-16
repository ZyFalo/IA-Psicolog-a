# 🧠 Asistente Psicoeducativo IA

**Sistema funcional de asistencia psicoeducativa con IA local**

[![Estado](https://img.shields.io/badge/Estado-Funcional-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.14-blue)]()
[![MLX](https://img.shields.io/badge/MLX-0.29-orange)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121-teal)]()

---

## 🚀 Inicio Rápido

### Requisitos
- macOS con Apple Silicon (M1/M2/M3/M4)
- Python 3.14
- 16GB RAM mínimo
- ~4GB espacio en disco

### Instalación
```bash
# Clonar proyecto
cd "/Users/williampena/Desktop/Desarrollos/IA Psicología"

# Activar entorno
source venv/bin/activate

# El modelo ya está descargado en models/qwen2.5-7b-mlx/
```

### Usar el Chat
```bash
# Terminal interactivo
python scripts/chat_terminal.py

# O iniciar backend API
cd backend
uvicorn app.main:app --reload

# Luego abrir frontend/chat.html en navegador
```

---

## ✨ Características

### 🤖 Modelo de IA
- **Qwen2.5-7B-Instruct** optimizado con MLX
- Cuantización 4-bit (~4GB)
- ~20 tokens/seg en Apple Silicon
- 100% local y privado

### 💬 Conversación Inteligente
- Memoria de 20 mensajes
- Resúmenes automáticos para sesiones largas
- Tono empático y profesional
- Técnicas psicoeducativas validadas

### 🛡️ Sistema de Seguridad
- Detección de crisis (suicidio, autolesión)
- Filtrado de contenido inapropiado
- Respuestas de emergencia automáticas
- NO diagnostica ni prescribe

### 📊 Backend Robusto
- API REST con FastAPI
- Gestión de sesiones multi-usuario
- WebSocket ready
- Health checks

---

## 📁 Estructura del Proyecto

```
.
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── main.py      # Servidor principal
│   │   ├── core/        # Lógica de negocio
│   │   └── api/         # Endpoints
│   └── requirements-mlx.txt
├── frontend/            # Interfaz web
│   └── chat.html
├── scripts/             # Utilidades
│   └── chat_terminal.py # Chat CLI
├── models/              # Modelo MLX (4GB)
│   └── qwen2.5-7b-mlx/
├── tests/               # Tests unitarios
├── docs/                # Documentación
└── STATUS.md            # 📍 Estado detallado del proyecto
```

---

## 📖 Documentación

- **[STATUS.md](STATUS.md)** - Estado completo del proyecto
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitectura del sistema
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Guía de inicio
- **[docs/MODELO_MLX_SETUP.md](docs/MODELO_MLX_SETUP.md)** - Setup de MLX

---

## 🎯 Casos de Uso

### Check-in Emocional
```
Usuario: Me siento ansioso por el examen de mañana
Asistente: Entiendo que los exámenes pueden generar ansiedad. 
           ¿Te gustaría probar una técnica de respiración rápida?
```

### Técnicas Prácticas
- Respiración 4-7-8
- Grounding 5-4-3-2-1
- Higiene del sueño
- Metas SMART
- Regulación emocional

### Detección de Crisis
```
Usuario: He pensado en hacerme daño
Asistente: 🚨 RESPUESTA DE EMERGENCIA
           Es importante que hables con alguien ahora:
           - Línea de la Vida: 800-911-2000
           - SAPTEL: 55-5259-8121
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Tests específicos
pytest tests/test_guardrails.py
pytest tests/test_session_manager.py
```

---

## 📊 Rendimiento

| Métrica | Valor |
|---------|-------|
| Carga del modelo | ~1.6s |
| Primera respuesta | 2-4s |
| Respuestas siguientes | 2-3s |
| Velocidad | ~20 tokens/seg |
| Memoria RAM | ~5GB |
| Tamaño en disco | 4GB |

---

## 🔧 Tecnologías

- **MLX** - Framework optimizado para Apple Silicon
- **Qwen2.5-7B** - Modelo de lenguaje multilingüe
- **FastAPI** - Backend API REST
- **Transformers** - Hugging Face
- **Pytest** - Testing

---

## 📝 Próximos Pasos

- [ ] Dataset de entrenamiento (500-2000 ejemplos)
- [ ] Fine-tuning con LoRA/MLX
- [ ] Integración de voz (Whisper + Piper)
- [ ] Frontend React
- [ ] Base de datos persistente
- [ ] Autenticación de usuarios

---

## ⚠️ Disclaimer

Este sistema es una **herramienta psicoeducativa**, NO reemplaza atención profesional de salud mental. En situaciones de crisis, siempre busca ayuda de profesionales calificados.

---

## 📞 Recursos de Crisis

**México**:
- Línea de la Vida: 800-911-2000
- SAPTEL: 55-5259-8121

**España**:
- Teléfono de la Esperanza: 717-003-717

**Internacional**:
- https://www.crisistextline.org/

---

## �� Licencia

Ver archivo LICENSE

---

**Desarrollado con ❤️ para Apple Silicon**
