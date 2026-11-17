# YUNA Academy para Android

Aplicación Android basada en WebView segura para https://yuna-academy.vercel.app/.
La APK es un contenedor de la web pública y el campus; no duplica los cursos.

## Generar APK
GitHub → Actions → Build YUNA Academy APK → Run workflow.
Descargar el artefacto **YUNA-Academy-Android-APK** del último workflow exitoso.
Dentro del ZIP estará **app-debug.apk**, instalable para pruebas.

## Advertencias para lanzamiento
- APK de prueba firmada con clave debug; NO es una versión de producción ni sirve para Play Store.
- Para distribuir profesionalmente se necesita firma release propia, política de privacidad, ícono personalizado y pruebas de Android.
- La música depende de las reglas de reproducción del WebView y del gesto permitido por Android.
- Requiere internet. El contenido no se descarga para uso sin conexión.
- La navegación a sitios externos se abre en el navegador.
