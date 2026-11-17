# YUNA Sound Holistic — producción semanal sin suscripciones

Integrado exclusivamente en `InstructorMap/yuna-academy`. No altera la web, el campus, pagos ni Android.

## Automatización disponible
- Cada lunes a las **09:00 de Argentina** (12:00 UTC) GitHub Actions intenta generar un **borrador**.
- También puede iniciarse manualmente desde Actions → YUNA Sound - weekly draft → Run workflow.
- Un generador local de código abierto crea una **pieza ambiental procedimental original** de ~150 segundos (sintetizadores sencillos, no IA) y una imagen japonesa abstracta.
- FFmpeg monta **1 MP4 horizontal** y **3 MP4 verticales**.
- El workflow verifica presencia de audio/video y entrega un artefacto descargable, retenido 7 días.
- **No publica en YouTube automáticamente.** Requiere revisión y aprobación.

## Derechos, calidad y límites
El código sintetiza sonidos sin importar grabaciones de terceros, pero **la originalidad jurídica absoluta y la monetización no están garantizadas**. El generador utiliza progresiones sencillas y una imagen estática: son bocetos para evaluación, **no equivalentes en calidad** a Sakura Dreams ni a Moonlight Kyoto. Para publicación profesional, mejorar instrumentación, mezcla, movimiento visual y diferenciación de cada Short. El flujo es gratuito dentro de los límites de GitHub Actions, sin promesa de ejecución ilimitada.

## Archivos
- `scripts/generate.py`: composición y arte procedimental, semilla semanal reproducible.
- `scripts/render.sh`: montaje FFmpeg.
- `input/`: entradas generadas en el runner, no subidas al repositorio.
- `output/`: MP4 y metadatos, publicados como artefacto del workflow.

## Próximo paso
Ejecutar una prueba del workflow y escuchar el resultado. Si la calidad no alcanza el estándar del canal, usar el módulo para montar pistas originales producidas y aprobadas por otros medios.
