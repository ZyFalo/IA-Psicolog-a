"""
Chat interactivo en terminal con Qwen2.5-7B
"""
import sys
from pathlib import Path

# Añadir backend al path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.core.model_manager_mlx import ModelManagerMLX
from app.core.guardrails import GuardrailsEngine
from app.config import settings
import time

def main():
    print("🔄 Cargando modelo Qwen2.5-7B...")
    manager = ModelManagerMLX()
    manager.load_model()
    
    guardrails = GuardrailsEngine(settings)
    
    print("\n" + "="*60)
    print("💬 CHAT CON ASISTENTE PSICOEDUCATIVO")
    print("="*60)
    print("Escribe 'salir' para terminar")
    print("Escribe 'limpiar' para nueva conversación")
    print("Escribe 'guardar' para guardar la conversación")
    print("Escribe 'cargar' para cargar conversación anterior\n")
    
    messages = []
    
    while True:
        try:
            # Input del usuario
            user_input = input("\n👤 Tú: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() == 'salir':
                print("\n👋 ¡Hasta luego! Cuídate.")
                break
                
            if user_input.lower() == 'limpiar':
                messages = []
                print("\n🧹 Conversación reiniciada")
                continue
            
            if user_input.lower() == 'guardar':
                import json
                from datetime import datetime
                filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, ensure_ascii=False, indent=2)
                print(f"\n💾 Conversación guardada en: {filename}")
                continue
            
            if user_input.lower() == 'cargar':
                import json
                import glob
                files = sorted(glob.glob("chat_*.json"), reverse=True)
                if not files:
                    print("\n❌ No hay conversaciones guardadas")
                    continue
                print("\n📂 Conversaciones disponibles:")
                for i, f in enumerate(files[:5], 1):
                    print(f"{i}. {f}")
                choice = input("Número (Enter para cancelar): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(files[:5]):
                    with open(files[int(choice)-1], 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                    print(f"\n📥 Conversación cargada: {len(messages)} mensajes")
                continue
            
            # Check guardrails (crisis detection)
            input_check = guardrails.check_input(user_input)
            
            if input_check.should_terminate:
                print(f"\n🚨 ALERTA: {input_check.risk_level.value}")
                print(f"\n🤖 Asistente: {input_check.emergency_response}")
                continue
            
            # Añadir mensaje del usuario
            messages.append({
                'role': 'user',
                'content': user_input
            })
            
            # Aplicar sistema de resúmenes si hay muchos mensajes
            messages_to_send = messages
            if len(messages) > 40:
                # Generar resumen de primeros 30 mensajes
                summary_msgs = messages[:30]
                recent_msgs = messages[30:]
                
                # Crear resumen simple
                summary_text = f"[Resumen de {len(summary_msgs)} mensajes anteriores: conversación sobre emociones y bienestar]"
                
                # Combinar: resumen + mensajes recientes
                messages_to_send = [
                    {'role': 'system', 'content': summary_text}
                ] + recent_msgs
                
                print(f"\n💡 Usando resumen automático ({len(summary_msgs)} msgs → resumen + {len(recent_msgs)} recientes)")
            
            # Generar respuesta
            start = time.time()
            response = manager.generate_chat(
                messages_to_send,
                max_tokens=512,
                temperature=0.7,
                top_p=0.9
            )
            gen_time = time.time() - start
            
            # Validar respuesta
            is_valid, violated_rules = guardrails.check_output(response)
            if not is_valid:
                print(f"\n⚠️  Respuesta filtrada: {violated_rules}")
                response = guardrails.get_fallback_response()
            
            # Añadir respuesta del asistente
            messages.append({
                'role': 'assistant',
                'content': response
            })
            
            # Mostrar respuesta
            print(f"\n🤖 Asistente: {response}")
            print(f"\n⏱️  [{gen_time:.2f}s]", end="")
            
            # Mantener contexto limitado (últimos 20 mensajes)
            # Puedes ajustar este número: más mensajes = más memoria pero más lento
            if len(messages) > 20:
                messages = messages[-20:]
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
