#!/usr/bin/env bash
set -euo pipefail
umask 077
KEYSTORE="${1:-yuna-academy-release.jks}"
if [[ -e "$KEYSTORE" ]]; then echo "El archivo ya existe: $KEYSTORE"; exit 1; fi
echo "Generación local de la clave de firma de YUNA Academy."
echo "Guardá una copia segura del .jks y su contraseña fuera del repositorio."
keytool -genkeypair -v -keystore "$KEYSTORE" -storetype PKCS12 -alias yunaacademy -keyalg RSA -keysize 3072 -validity 10000
echo "Clave creada: $KEYSTORE"
echo "Alias: yunaacademy"
echo "Para GitHub Actions, codificá el JKS como base64 sin saltos y guardalo en YUNA_KEYSTORE_BASE64."
