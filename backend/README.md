# LUMENIA backend — Cloudflare Workers + D1

**Estado:** código inicial incorporado; no desplegado ni conectado a una base real.

## Instalación
1. Instalar Node.js 20+ y ejecutar `npm install` dentro de `backend`.
2. Autenticarse con `npx wrangler login` en la cuenta Cloudflare del proyecto.
3. Crear la base con `npx wrangler d1 create lumenia-db`.
4. Copiar el ID devuelto a `wrangler.toml`, descomentando el bloque `[[d1_databases]]`.
5. Ejecutar `npm run db:remote` para crear las tablas.
6. Ejecutar `npm run deploy` para desplegar la API.

## Endpoints disponibles
- `GET /api/health`: estado del servicio y configuración de D1.
- `GET /api/courses`: lista de cursos publicados (vacía hasta cargar y publicar cursos).

No existe todavía un sistema de autenticación, pagos ni emisión de certificados. Las tablas preparan el esquema, pero no habilitan esas funciones. No introducir datos de alumnos reales hasta implementar autenticación, autorización y políticas de privacidad. No publicar secretos en GitHub.

La carpeta de Google Drive es **solo una fuente de referencia**; ningún documento se ha importado ni modificado.
