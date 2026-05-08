# agent/main.py — Serveur FastAPI principal pour Holisource WhatsApp Agent

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

from agent.brain import get_brain
from agent.memory import get_memory, get_history, save_message
from agent.providers import obtener_proveedor
from agent.supabase_client import get_supabase_client

load_dotenv()

# Configuración de logging
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
log_level = logging.DEBUG if ENVIRONMENT == "development" else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("holisource_agent")

# Inicialización de componentes
proveedor = obtener_proveedor()
supabase = get_supabase_client()
memory = get_memory()
brain = get_brain()
PORT = int(os.getenv("PORT", 8000))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización y limpieza de la aplicación"""
    logger.info("=" * 60)
    logger.info("🚀 Holisource WhatsApp Agent iniciando...")
    logger.info("=" * 60)

    # Health check Supabase
    is_healthy = await supabase.health_check()
    if is_healthy:
        logger.info("✅ Supabase connected")
    else:
        logger.warning("⚠️  Supabase health check failed")

    logger.info(f"📱 Provider WhatsApp: {proveedor.__class__.__name__}")
    logger.info(f"🔌 Server running on port {PORT}")
    logger.info("=" * 60)

    yield

    logger.info("🛑 Agent shutting down...")


app = FastAPI(
    title="Holisource WhatsApp Agent",
    version="1.0.0",
    description="AI Agent for holistic therapist directory in Alsace",
    lifespan=lifespan,
)


# ════════════════════════════════════════════════════════════
# HEALTH & MONITORING
# ════════════════════════════════════════════════════════════

@app.get("/")
async def health_check():
    """Endpoint de santé para monitoreo (Railway, etc.)"""
    return {
        "status": "ok",
        "service": "holisource-whatsapp-agent",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
    }


@app.get("/health")
async def detailed_health():
    """Health check detallado"""
    supabase_ok = await supabase.health_check()

    return {
        "status": "ok" if supabase_ok else "degraded",
        "supabase": "healthy" if supabase_ok else "unhealthy",
        "provider": proveedor.__class__.__name__,
        "timestamp": os.popen("date").read(),
    }


# ════════════════════════════════════════════════════════════
# WEBHOOK HANDLERS
# ════════════════════════════════════════════════════════════

@app.get("/webhook")
async def webhook_get_verification(request: Request):
    """
    Verificación GET del webhook (requerido por Meta Cloud API)
    Twilio no requiere esto
    """
    try:
        resultado = await proveedor.validar_webhook(request)
        if resultado is not None:
            return PlainTextResponse(str(resultado))
        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Error webhook GET verification: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


@app.post("/webhook")
async def webhook_handler(request: Request):
    """
    Webhook principal que recibe mensajes de WhatsApp
    Procesa el mensaje, genera respuesta con Claude y la envía de vuelta
    """
    try:
        # Parsear webhook — el proveedor normaliza el formato
        mensajes = await proveedor.parsear_webhook(request)

        for msg in mensajes:
            # Ignorar mensajes propios o vacíos
            if msg.es_propio or not msg.texto:
                logger.debug(f"Mensaje ignorado (propio o vacío)")
                continue

            logger.info(f"📱 Mensaje de {msg.telefono}: {msg.texto[:50]}...")

            # Obtener historial de la conversación
            historial = await get_history(msg.telefono)

            # Procesar con el brain (detecta intent, routea, etc.)
            respuesta = await brain.process_conversation(
                user_message=msg.texto,
                numero_client=msg.telefono,
                chat_history=historial,
            )

            # Guardar la respuesta en memoria
            await save_message(msg.telefono, "assistant", respuesta)

            # Enviar respuesta por WhatsApp
            success = await proveedor.enviar_mensaje(msg.telefono, respuesta)

            if success:
                logger.info(f"✅ Respuesta enviada a {msg.telefono}")
            else:
                logger.error(f"❌ Error enviando respuesta a {msg.telefono}")

        return JSONResponse({"status": "ok", "messages_processed": len(mensajes)})

    except Exception as e:
        logger.error(f"❌ Error en webhook handler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ════════════════════════════════════════════════════════════
# API ENDPOINTS (para testing, admin, etc.)
# ════════════════════════════════════════════════════════════

@app.post("/api/test-message")
async def test_message(numero: str, mensaje: str):
    """
    Endpoint para testear el agent (solo en desarrollo)
    Simula el recepción de un mensaje
    """
    if ENVIRONMENT != "development":
        raise HTTPException(status_code=403, detail="Solo disponible en development")

    try:
        historial = await get_history(numero)
        respuesta = await brain.process_conversation(
            user_message=mensaje,
            numero_client=numero,
            chat_history=historial,
        )

        await save_message(numero, "user", mensaje)
        await save_message(numero, "assistant", respuesta)

        return {
            "numero": numero,
            "mensaje": mensaje,
            "respuesta": respuesta,
            "historial_length": len(historial),
        }
    except Exception as e:
        logger.error(f"Error test-message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{numero}")
async def get_conversation_history(numero: str):
    """Obtiene el historial de una conversación"""
    try:
        history = await get_history(numero, limit=50)
        return {"numero": numero, "messages": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Error get_conversation_history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/send-message")
async def send_direct_message(numero: str, mensaje: str):
    """
    Envía un mensaje directamente al cliente
    (útil para escaladas, notificaciones, etc.)
    """
    if not numero or not mensaje:
        raise HTTPException(status_code=400, detail="numero y mensaje requeridos")

    try:
        success = await proveedor.enviar_mensaje(numero, mensaje)

        if success:
            await save_message(numero, "system", f"[Mensaje enviado] {mensaje}")
            return {"status": "sent", "numero": numero, "mensaje": mensaje}
        else:
            return {"status": "failed", "numero": numero, "error": "Provider error"}

    except Exception as e:
        logger.error(f"Error send_direct_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ════════════════════════════════════════════════════════════
# STARTUP/SHUTDOWN EVENTS
# ════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Inicialización en startup"""
    logger.info("🚀 Application startup event")


@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza en shutdown"""
    logger.info("🛑 Application shutdown event")


# ════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ════════════════════════════════════════════════════════════

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.status_code} — {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level=log_level)
