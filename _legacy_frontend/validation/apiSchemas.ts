import { z } from 'zod';

// Esquema para /mpa/ingestion/upload-file/
// No se puede validar FormData directamente con Zod de esta manera.
// Se omite la validación del lado del cliente para uploads por ahora.

// Esquema para /mpa/quality/report
export const QualityReportPayloadSchema = z.array(
  z.record(z.any())
);

// Esquema para /api/v1/chat/agent/
export const ChatAgentPayloadSchema = z.object({
  message: z.string(),
  data: z.array(z.record(z.any())),
  llm_preference: z.string(),
});

// Esquema para /mpa/ingestion/multi-upload/
// No se puede validar FormData directamente con Zod de esta manera.
// Se omite la validación del lado del cliente para uploads por ahora.
