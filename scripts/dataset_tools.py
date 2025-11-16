"""
Herramientas para generar y validar dataset de entrenamiento
"""

import json
import os
import re
from typing import List, Dict
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatasetStats:
    """Estadísticas del dataset"""
    total: int
    by_category: Dict[str, int]
    by_risk_level: Dict[str, int]
    avg_length: float
    techniques_count: Dict[str, int]


class DatasetValidator:
    """Validador de ejemplos del dataset"""
    
    VALID_CATEGORIES = [
        "check_in", "tecnica", "conversacion", "crisis", "resumen"
    ]
    
    VALID_RISK_LEVELS = ["low", "medium", "high", "critical"]
    
    FORBIDDEN_WORDS = [
        "diagnóstico", "diagnostico", "prescribo", "receto",
        "tienes depresión", "tienes ansiedad", "sufres de"
    ]
    
    def validate_example(self, example: Dict) -> tuple[bool, List[str]]:
        """
        Valida un ejemplo del dataset
        
        Args:
            example: Ejemplo a validar
            
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # 1. Estructura básica
        if "messages" not in example:
            errors.append("Falta campo 'messages'")
            return False, errors
        
        if "metadata" not in example:
            errors.append("Falta campo 'metadata'")
        
        messages = example["messages"]
        metadata = example.get("metadata", {})
        
        # 2. Validar mensajes
        if len(messages) < 2:
            errors.append("Se requieren al menos 2 mensajes")
        
        for i, msg in enumerate(messages):
            if "role" not in msg or "content" not in msg:
                errors.append(f"Mensaje {i} incompleto (falta role o content)")
            
            if msg.get("role") not in ["system", "user", "assistant"]:
                errors.append(f"Mensaje {i} tiene role inválido: {msg.get('role')}")
        
        # 3. Validar metadata
        if "category" in metadata:
            if metadata["category"] not in self.VALID_CATEGORIES:
                errors.append(f"Categoría inválida: {metadata['category']}")
        
        if "risk_level" in metadata:
            if metadata["risk_level"] not in self.VALID_RISK_LEVELS:
                errors.append(f"Nivel de riesgo inválido: {metadata['risk_level']}")
        
        # 4. Validar contenido
        for msg in messages:
            if msg.get("role") == "assistant":
                content = msg["content"].lower()
                
                # Buscar palabras prohibidas
                for word in self.FORBIDDEN_WORDS:
                    if word in content:
                        errors.append(f"Contiene palabra prohibida: '{word}'")
                
                # Validar longitud
                word_count = len(content.split())
                if word_count > 300:
                    errors.append(f"Respuesta muy larga: {word_count} palabras (max 300)")
        
        # 5. Validar derivación en crisis
        if metadata.get("risk_level") in ["high", "critical"]:
            assistant_msgs = [m["content"] for m in messages if m["role"] == "assistant"]
            has_crisis_keywords = any(
                keyword in " ".join(assistant_msgs).lower()
                for keyword in ["988", "741741", "911", "emergencia", "profesional"]
            )
            
            if not has_crisis_keywords:
                errors.append("Caso de crisis sin derivación apropiada")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_dataset(self, dataset_path: str) -> Dict:
        """
        Valida un dataset completo
        
        Args:
            dataset_path: Ruta al archivo JSONL
            
        Returns:
            Reporte de validación
        """
        logger.info(f"🔍 Validando dataset: {dataset_path}")
        
        valid_count = 0
        invalid_count = 0
        all_errors = []
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                try:
                    example = json.loads(line)
                    is_valid, errors = self.validate_example(example)
                    
                    if is_valid:
                        valid_count += 1
                    else:
                        invalid_count += 1
                        all_errors.append({
                            "line": i,
                            "errors": errors
                        })
                
                except json.JSONDecodeError as e:
                    invalid_count += 1
                    all_errors.append({
                        "line": i,
                        "errors": [f"JSON inválido: {e}"]
                    })
        
        report = {
            "total": valid_count + invalid_count,
            "valid": valid_count,
            "invalid": invalid_count,
            "errors": all_errors
        }
        
        logger.info(f"✅ Válidos: {valid_count}")
        logger.info(f"❌ Inválidos: {invalid_count}")
        
        return report


class DatasetAnalyzer:
    """Analizador de estadísticas del dataset"""
    
    def analyze(self, dataset_path: str) -> DatasetStats:
        """
        Analiza estadísticas del dataset
        
        Args:
            dataset_path: Ruta al archivo JSONL
            
        Returns:
            DatasetStats
        """
        logger.info(f"📊 Analizando dataset: {dataset_path}")
        
        total = 0
        by_category = {}
        by_risk_level = {}
        techniques_count = {}
        total_length = 0
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                example = json.loads(line)
                total += 1
                
                metadata = example.get("metadata", {})
                
                # Categoría
                category = metadata.get("category", "unknown")
                by_category[category] = by_category.get(category, 0) + 1
                
                # Nivel de riesgo
                risk = metadata.get("risk_level", "unknown")
                by_risk_level[risk] = by_risk_level.get(risk, 0) + 1
                
                # Técnicas
                techniques = metadata.get("techniques_mentioned", [])
                for tech in techniques:
                    techniques_count[tech] = techniques_count.get(tech, 0) + 1
                
                # Longitud promedio
                for msg in example["messages"]:
                    if msg["role"] == "assistant":
                        total_length += len(msg["content"].split())
        
        avg_length = total_length / total if total > 0 else 0
        
        stats = DatasetStats(
            total=total,
            by_category=by_category,
            by_risk_level=by_risk_level,
            avg_length=avg_length,
            techniques_count=techniques_count
        )
        
        # Log stats
        logger.info(f"📊 Total ejemplos: {stats.total}")
        logger.info(f"📊 Por categoría: {stats.by_category}")
        logger.info(f"📊 Por riesgo: {stats.by_risk_level}")
        logger.info(f"📊 Longitud promedio: {stats.avg_length:.1f} palabras")
        logger.info(f"📊 Técnicas: {stats.techniques_count}")
        
        return stats


def create_template_dataset(output_path: str):
    """
    Crea un dataset template con ejemplos básicos
    
    Args:
        output_path: Ruta de salida
    """
    logger.info(f"📝 Creando dataset template: {output_path}")
    
    templates = [
        # Check-in básico
        {
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un asistente de psicoeducación empático. Ofreces orientación práctica, NO diagnósticos. Ante crisis, derivas inmediatamente."
                },
                {
                    "role": "user",
                    "content": "Hola"
                },
                {
                    "role": "assistant",
                    "content": "¡Hola! Me alegra que estés aquí. Soy un asistente de psicoeducación y estoy para apoyarte. ¿Cómo te sientes hoy?"
                }
            ],
            "metadata": {
                "category": "check_in",
                "risk_level": "low",
                "techniques_mentioned": []
            }
        },
        # Técnica básica
        {
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un asistente de psicoeducación empático. Ofreces orientación práctica, NO diagnósticos. Ante crisis, derivas inmediatamente."
                },
                {
                    "role": "user",
                    "content": "Estoy muy ansioso"
                },
                {
                    "role": "assistant",
                    "content": "Entiendo que te sientes ansioso. Te comparto una técnica que puede ayudarte: la respiración 4-7-8. Inhala por 4 segundos, retén 7 segundos, y exhala por 8 segundos. ¿Quieres probarlo?"
                }
            ],
            "metadata": {
                "category": "tecnica",
                "risk_level": "medium",
                "techniques_mentioned": ["respiracion_4_7_8"]
            }
        }
    ]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for template in templates:
            f.write(json.dumps(template, ensure_ascii=False) + '\n')
    
    logger.info(f"✅ Dataset template creado con {len(templates)} ejemplos")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Herramientas de dataset")
    parser.add_argument("action", choices=["validate", "analyze", "create-template"])
    parser.add_argument("--input", type=str, help="Archivo de entrada")
    parser.add_argument("--output", type=str, help="Archivo de salida")
    
    args = parser.parse_args()
    
    if args.action == "validate":
        validator = DatasetValidator()
        report = validator.validate_dataset(args.input)
        
        # Guardar reporte
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"📄 Reporte guardado en: {args.output}")
    
    elif args.action == "analyze":
        analyzer = DatasetAnalyzer()
        stats = analyzer.analyze(args.input)
    
    elif args.action == "create-template":
        output = args.output or "./data/training/template.jsonl"
        create_template_dataset(output)
