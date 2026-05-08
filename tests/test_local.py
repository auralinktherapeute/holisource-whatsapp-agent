#!/usr/bin/env python3
# tests/test_local.py — Simulateur de chat pour tester l'agent localement

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.brain import get_brain
from agent.memory import get_memory, get_history, save_message

# Número de teléfono para pruebas locales
NUMERO_TEST = "test-local-001"


async def main():
    """Loop principal del chat de prueba"""
    brain = get_brain()
    memory = get_memory()

    print()
    print("=" * 70)
    print("   🧪 Holisource WhatsApp Agent — Test Local")
    print("=" * 70)
    print()
    print("  Escribe mensajes como si fueras un cliente que busca un terapeuta.")
    print()
    print("  Comandos especiales:")
    print("    'limpiar'  — borra el historial")
    print("    'salir'    — termina el test")
    print()
    print("-" * 70)
    print()

    while True:
        try:
            mensaje = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n✅ Test finalizado.")
            break

        if not mensaje:
            continue

        if mensaje.lower() == "salir":
            print("\n✅ Test finalizado.")
            break

        if mensaje.lower() == "limpiar":
            await memory.clear_history(NUMERO_TEST)
            print("[Historial borrado]\n")
            continue

        # Obtener historial ANTES de procesar
        historial = await get_history(NUMERO_TEST)

        # Guardar mensaje del usuario
        await save_message(NUMERO_TEST, "user", mensaje)

        # Procesar con el brain (detecta intent, routea, etc.)
        print("\n🤖 Sofia: ", end="", flush=True)
        respuesta = await brain.process_conversation(
            user_message=mensaje,
            numero_client=NUMERO_TEST,
            chat_history=historial,
        )
        print(respuesta)
        print()


if __name__ == "__main__":
    asyncio.run(main())
