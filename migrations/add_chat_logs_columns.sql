-- Migration: Ajouter les colonnes manquantes à chat_logs
ALTER TABLE IF EXISTS public.chat_logs
ADD COLUMN IF NOT EXISTS content TEXT,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_chat_logs_session_id ON public.chat_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_logs_created_at ON public.chat_logs(created_at DESC);
