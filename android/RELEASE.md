# YUNA Academy — publicación Android
## Firma segura
Crear una clave de producción en un entorno seguro y conservar una copia privada. No subir archivos .jks, contraseñas ni datos privados a GitHub.
Configurar en GitHub Actions → Settings → Secrets and variables → Actions:
- YUNA_KEYSTORE_BASE64: archivo JKS codificado en Base64 (sin saltos)
- YUNA_KEYSTORE_PASSWORD
- YUNA_KEY_ALIAS
- YUNA_KEY_PASSWORD
El flujo de trabajo genera una APK Release **solo** cuando existen los cuatro secretos; si faltan, falla expresamente. Nunca utiliza firma debug para la versión comercial.
La APK de producción y la APK de prueba tienen la misma applicationId, pero firmas diferentes. Para instalar la Release encima de la debug puede ser necesario desinstalar la debug; eso borra los datos locales de la aplicación.
## Identidad
La versión inicial incluye un símbolo vectorial YUNA en dorado/marfil. Pendiente de aprobación visual y, si se desea fidelidad exacta, convertir el logotipo PNG oficial de la web en los recursos Android correspondientes.
## Privacidad
No afirmar que existe una política verificada hasta revisar los datos del responsable, categorías de datos, proveedores, retención, derechos y canal de contacto. Debe publicarse en una URL estable accesible desde la app.
