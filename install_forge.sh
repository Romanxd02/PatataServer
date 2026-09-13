#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Instala Forge 1.20.1-47.4.23 para el servidor de Minecraft en el Codespace.
#
# Uso:
#   chmod +x install_forge.sh
#   ./install_forge.sh
#
# Por defecto instala en:
#   /workspaces/PatataServer/servidor_minecraft
# Podés cambiar el destino pasándolo como primer argumento:
#   ./install_forge.sh /ruta/a/mi/servidor
# ---------------------------------------------------------------------------
set -euo pipefail

MC_VERSION="1.20.1"
FORGE_VERSION="47.4.23"
FULL_VERSION="${MC_VERSION}-${FORGE_VERSION}"

TARGET_DIR="${1:-/workspaces/PatataServer/servidor_minecraft}"
INSTALLER_NAME="forge-${FULL_VERSION}-installer.jar"
INSTALLER_URL="https://maven.minecraftforge.net/net/minecraftforge/forge/${FULL_VERSION}/${INSTALLER_NAME}"

echo "== Instalador de Forge ${FULL_VERSION} =="
echo "Destino: ${TARGET_DIR}"
echo

# 1) Verificar que Java esté disponible (Forge 1.20.1 requiere Java 17)
if ! command -v java &>/dev/null; then
  echo "ERROR: no se encontró 'java' en el PATH. Instalá Java 17 antes de continuar."
  exit 1
fi

JAVA_MAJOR="$(java -version 2>&1 | head -n1 | grep -oE '"[0-9]+' | tr -d '"')"
if [ "${JAVA_MAJOR}" -lt 17 ]; then
  echo "ADVERTENCIA: se detectó Java ${JAVA_MAJOR}. Forge 1.20.1 requiere Java 17 o superior."
  echo "Si falla la instalación, instalá Java 17 (ej: sudo apt-get install -y openjdk-17-jdk-headless)."
fi

# 2) Crear carpeta destino
mkdir -p "${TARGET_DIR}"
cd "${TARGET_DIR}"

# 3) Descargar el instalador (si no está ya presente)
if [ -f "${INSTALLER_NAME}" ]; then
  echo "El instalador ya existe, se reutiliza: ${INSTALLER_NAME}"
else
  echo "Descargando ${INSTALLER_URL} ..."
  if command -v curl &>/dev/null; then
    curl -fL -o "${INSTALLER_NAME}" "${INSTALLER_URL}"
  elif command -v wget &>/dev/null; then
    wget -O "${INSTALLER_NAME}" "${INSTALLER_URL}"
  else
    echo "ERROR: necesitás curl o wget instalado para descargar el instalador."
    exit 1
  fi
fi

# 4) Ejecutar el instalador en modo servidor
echo
echo "Instalando Forge ${FULL_VERSION} como servidor..."
java -jar "${INSTALLER_NAME}" --installServer

# 5) Aceptar el EULA automáticamente
echo "eula=true" > eula.txt
echo "EULA aceptado (eula.txt creado)."

# 6) Limpieza opcional del instalador y sus logs
rm -f "${INSTALLER_NAME}" "installer.log" 2>/dev/null || true

echo
echo "== Instalación completa =="
echo "Carpeta del servidor: ${TARGET_DIR}"
if [ -f "run.sh" ]; then
  echo "Para iniciar el servidor:"
  echo "  cd ${TARGET_DIR} && ./run.sh"
  chmod +x run.sh 2>/dev/null || true
else
  echo "Buscá el .jar generado (forge-${FULL_VERSION}.jar o similar) para arrancar el servidor manualmente,"
  echo "por ejemplo: java -jar forge-${FULL_VERSION}.jar nogui"
fi
