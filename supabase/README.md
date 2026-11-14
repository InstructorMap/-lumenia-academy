# Supabase LUMENIA

Proyecto independiente: `ejfdwwolmwwrvaxvkdlw` (Primary, sa-east-1).

Se aplicó la migración `initialize_lumenia_academy_schema` desde la integración Supabase. El proyecto tiene 13 tablas con RLS activado. No reutilizar las migraciones SQLite de `backend/` en Supabase; son un prototipo anterior de Cloudflare.

El campus de GitHub Pages usa la clave **publishable** pública; nunca introducir `service_role`, `secret` ni contraseñas en archivos públicos. Las inscripciones se gestionarán desde un backend verificado cuando se integren los pagos.

Estado: registro/login, visualización de matrículas y catálogo publicado. Todavía no hay administración, examen funcional, emisión de certificados ni checkout.
