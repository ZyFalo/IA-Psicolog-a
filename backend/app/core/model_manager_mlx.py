"""
Gestor del modelo Qwen usando MLX (optimizado para Apple Silicon)
"""
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

logger = logging.getLogger(__name__)

class ModelManagerMLX:
    """Gestor del modelo Qwen2.5-7B usando MLX"""
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            # Buscar modelo relativo al directorio del proyecto
            project_root = Path(__file__).parent.parent.parent.parent
            model_path = project_root / "models" / "qwen2.5-7b-mlx"
        self.model_path = Path(model_path)
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """
        Carga el modelo cuantizado con MLX
        
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            if not self.model_path.exists():
                logger.error(f"Modelo no encontrado en {self.model_path}")
                return False
                
            logger.info(f"🔄 Cargando modelo desde {self.model_path}...")
            
            # MLX carga modelo y tokenizer automáticamente
            self.model, self.tokenizer = load(str(self.model_path))
            
            self.is_loaded = True
            logger.info("✅ Modelo cargado exitosamente")
            
            # Información del modelo
            logger.info(f"📊 Memoria GPU: ~4-5GB")
            logger.info(f"⚡ Velocidad estimada: 15-25 tokens/seg")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
        stop_strings: Optional[List[str]] = None
    ) -> str:
        """
        Genera respuesta usando el modelo
        
        Args:
            prompt: Texto de entrada
            max_tokens: Máximo de tokens a generar
            temperature: Control de aleatoriedad (0.0-2.0)
            top_p: Nucleus sampling
            repetition_penalty: Penalización por repetición
            stop_strings: Strings que detienen la generación
            
        Returns:
            str: Texto generado
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo no cargado. Llama a load_model() primero")
        
        try:
            # Crear sampler con parámetros (MLX usa temp/top_p directamente)
            sampler = make_sampler(
                temp=temperature,
                top_p=top_p
            )
            
            # MLX genera directamente
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens,
                sampler=sampler,
                verbose=False
            )
            
            # Limpiar prompt de la respuesta si viene incluido
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            # Aplicar stop strings si se especifican
            if stop_strings:
                for stop in stop_strings:
                    if stop in response:
                        response = response[:response.index(stop)]
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generando respuesta: {e}")
            raise
    
    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1
    ) -> str:
        """
        Genera respuesta en formato chat
        
        Args:
            messages: Lista de mensajes [{"role": "user/assistant", "content": "..."}]
            max_tokens: Máximo de tokens a generar
            temperature: Control de aleatoriedad
            top_p: Nucleus sampling
            repetition_penalty: Penalización por repetición
            
        Returns:
            str: Respuesta del asistente
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo no cargado. Llama a load_model() primero")
        
        try:
            # Aplicar chat template de Qwen
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Generar con stop strings de Qwen
            response = self.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                stop_strings=["<|im_end|>", "<|endoftext|>"]
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generando chat: {e}")
            raise
    
    def cleanup(self):
        """Libera recursos del modelo"""
        if self.is_loaded:
            logger.info("🧹 Liberando recursos del modelo...")
            self.model = None
            self.tokenizer = None
            self.is_loaded = False
            
            # MLX libera memoria automáticamente
            mx.metal.clear_cache()
            
            logger.info("✅ Recursos liberados")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo
        
        Returns:
            Dict con información del modelo
        """
        if not self.is_loaded:
            return {"loaded": False}
        
        return {
            "loaded": True,
            "model_path": str(self.model_path),
            "framework": "MLX",
            "device": "Apple Silicon (Metal)",
            "quantization": "4-bit",
            "estimated_memory_gb": 5,
            "estimated_tokens_per_sec": "15-25"
        }


# Instancia global (se inicializará en main.py)
model_manager: Optional[ModelManagerMLX] = None


def get_model_manager() -> ModelManagerMLX:
    """Obtiene la instancia global del gestor de modelo"""
    if model_manager is None:
        raise RuntimeError("ModelManager no inicializado")
    return model_manager
