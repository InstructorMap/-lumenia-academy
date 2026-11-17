# YUNA Sound Holistic — módulo de producción semanal

Este módulo pertenece al repositorio YUNA Academy. No modifica la web, el campus, Android ni sus credenciales.

## Objetivo
Una composición instrumental original por semana y tres Shorts derivados, sujetos a revisión artística y de licencias. **No se afirma que exista generación musical gratuita, ilimitada o automática.**

## Flujo
1. Preparar composición original WAV/MP3 con derechos de explotación documentados.
2. Añadir un fondo visual propio o autorizado.
3. Ejecutar el workflow manual `YUNA Sound - render weekly` en GitHub Actions.
4. Descargar el artefacto, revisar audio, video, derechos y metadatos.
5. Publicar manualmente en el canal correcto Yuna Sound Holistic.

## Entradas
Subir los archivos al repositorio en:
- `automation/yuna-sound/input/track.wav` (audio original, opcionalmente generado fuera del workflow)
- `automation/yuna-sound/input/visual.jpg` (imagen original/autorizada)

**Precaución:** GitHub no es el mejor almacenamiento para pistas grandes. No subir material con licencia incierta ni credenciales. El workflow puede ampliarse después para usar almacenamiento privado.

## Salidas
- `yuna-full.mp4` — video horizontal con audio completo.
- `yuna-short-1.mp4`, `yuna-short-2.mp4`, `yuna-short-3.mp4` — cortes verticales de hasta 30 s.
- `metadata.txt` — borrador de descripción.

## Limitaciones actuales
El render es automático; la composición, la imagen y la aprobación son humanas. No hay subida automática a YouTube ni generación de IA sin un proveedor y licencia verificados. Los Shorts usan una misma pista: conviene añadir edición y escenas diferenciadas antes de publicarlos para evitar contenido repetitivo.
