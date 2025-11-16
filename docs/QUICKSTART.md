# Guía de Inicio Rápido

## 1. Instalación del Entorno

### Prerrequisitos
- macOS con Apple Silicon (M4)
- Python 3.10+
- ~20 GB espacio libre

### Configurar entorno virtual

```bash
# Crear entorno
python3 -m venv venv

# Activar
source venv/bin/activate

# Instalar dependencias
cd backend
pip install -r requirements.txt
```

## 2. Descargar Modelo Base

```bash
# Descargar y cuantizar Qwen2.5-7B
cd ..
python scripts/download_model.py \
    --model-name Qwen/Qwen2.5-7B-Instruct \
    --output-dir ./models/qwen2.5-7b \
    --quantization 4bit
```

**Tiempo estimado:** 20-30 minutos  
**Tamaño descarga:** ~15 GB → ~4 GB cuantizado

## 3. Preparar Dataset

### Crear dataset template

```bash
python scripts/dataset_tools.py create-template \
    --output ./data/training/psicoeducacion.jsonl
```

### Añadir tus propios ejemplos

Edita `data/training/psicoeducacion.jsonl` siguiendo el formato en `data/DATASET_FORMAT.md`.

**Objetivo:** 500-2000 ejemplos distribuidos:
- 40% Check-ins y conversaciones
- 30% Técnicas psicoeducativas
- 20% Crisis y derivación
- 10% Resúmenes

### Validar dataset

```bash
python scripts/dataset_tools.py validate \
    --input ./data/training/psicoeducacion.jsonl \
    --output ./data/training/validation_report.json
```

## 4. Fine-tuning con LoRA

```bash
python scripts/finetune.py
```

**Configuración por defecto:**
- LoRA rank: 16
- Batch size: 1
- Gradient accumulation: 4
- Epochs: 3
- Cuantización: 4-bit

**Tiempo estimado:** 2-4 horas (depende del tamaño del dataset)

### Probar modelo fine-tuned

```bash
python scripts/finetune.py --test
```

## 5. Configurar Backend

### Crear archivo .env

```bash
cd backend
cp .env.example .env
```

Edita `.env` y ajusta:
- `MODEL_PATH`: Ruta al modelo base
- `LORA_PATH`: Ruta a adaptadores LoRA
- Recursos de crisis (números de teléfono locales)

## 6. Ejecutar Backend

```bash
# Desde /backend
python -m app.main
```

El servidor estará en: `http://localhost:8000`

### Probar API

```bash
# Health check
curl http://localhost:8000/api/health

# Crear sesión
curl -X POST http://localhost:8000/api/chat/sessions

# Enviar mensaje
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_AQUI",
    "message": "Hola, estoy muy estresado"
  }'
```

## 7. Ejecutar Tests

```bash
# Instalar dependencias de test
pip install pytest pytest-asyncio pytest-cov

# Ejecutar tests
pytest

# Con coverage
pytest --cov=app --cov-report=html
```

## 8. Frontend (Próximo)

El frontend React se desarrollará en la carpeta `frontend/` con:
- Vite + React + TypeScript
- TailwindCSS
- Interfaz de chat
- Integración de voz

## Troubleshooting

### Error: Out of Memory

Reduce batch size o context length en `backend/app/config.py`:
```python
MAX_CONTEXT_LENGTH = 2048  # En vez de 4096
```

### Error: Model loading failed

Verifica que el modelo esté descargado:
```bash
ls -lh models/qwen2.5-7b/
```

### Error: CUDA not available

En M4, se usa MPS (Metal). Verifica:
```python
import torch
print(torch.backends.mps.is_available())  # Debe ser True
```

### Latencia muy alta

Considera usar MLX en vez de PyTorch:
```bash
pip install mlx mlx-lm
```

Cambia en `.env`:
```
USE_MLX=True
```

## Próximos Pasos

1. ✅ Backend funcionando
2. ⏳ Crear dataset completo (500+ ejemplos)
3. ⏳ Fine-tuning con dataset real
4. ⏳ Implementar frontend React
5. ⏳ Integrar Whisper (ASR)
6. ⏳ Integrar Piper/Coqui (TTS)
7. ⏳ Avatar animado
8. ⏳ Testing con usuarios piloto

## Recursos

- **Modelo:** https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
- **Documentación FastAPI:** https://fastapi.tiangolo.com/
- **LoRA/PEFT:** https://huggingface.co/docs/peft
- **Transformers:** https://huggingface.co/docs/transformers

## Soporte

Para dudas o problemas, revisa:
1. `README.md` principal
2. `data/DATASET_FORMAT.md`
3. Logs del backend en consola
4. Tests en `tests/`
