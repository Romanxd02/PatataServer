#!/usr/bin/env python3
"""
Instala Forge 1.20.1-47.4.23 para el servidor de Minecraft en el Codespace.

Uso:
    python3 install_forge.py
    python3 install_forge.py /ruta/a/mi/servidor   # destino personalizado
"""

import os
import shutil
import subprocess
import sys
import urllib.request

MC_VERSION = "1.20.1"
FORGE_VERSION = "47.4.23"
FULL_VERSION = f"{MC_VERSION}-{FORGE_VERSION}"

DEFAULT_TARGET_DIR = "/workspaces/PatataServer/servidor_minecraft"
INSTALLER_NAME = f"forge-{FULL_VERSION}-installer.jar"
INSTALLER_URL = (
    f"https://maven.minecraftforge.net/net/minecraftforge/forge/"
    f"{FULL_VERSION}/{INSTALLER_NAME}"
)


def check_java():
    """Verifica que java esté instalado y sea versión 17+."""
    java_path = shutil.which("java")
    if not java_path:
        print("ERROR: no se encontró 'java' en el PATH. Instalá Java 17 antes de continuar.")
        sys.exit(1)

    result = subprocess.run(
        ["java", "-version"], capture_output=True, text=True
    )
    # java -version imprime en stderr, ej: 'openjdk version "17.0.9" ...'
    version_line = (result.stderr or result.stdout).splitlines()[0]
    try:
        version_str = version_line.split('"')[1]
        major = int(version_str.split(".")[0])
    except (IndexError, ValueError):
        major = None

    if major is not None and major < 17:
        print(f"ADVERTENCIA: se detectó Java {major}. Forge 1.20.1 requiere Java 17 o superior.")
        print("Si falla la instalación, instalá Java 17 "
              "(ej: sudo apt-get install -y openjdk-17-jdk-headless).")


def download_installer(target_dir: str) -> str:
    """Descarga el instalador de Forge si no existe ya."""
    installer_path = os.path.join(target_dir, INSTALLER_NAME)

    if os.path.exists(installer_path):
        print(f"El instalador ya existe, se reutiliza: {INSTALLER_NAME}")
        return installer_path

    print(f"Descargando {INSTALLER_URL} ...")
    try:
        request = urllib.request.Request(
            INSTALLER_URL,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "*/*",
            },
        )
        with urllib.request.urlopen(request) as response, open(installer_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        print(f"ERROR al descargar el instalador: {e}")
        sys.exit(1)

    return installer_path


def run_installer(installer_path: str, target_dir: str):
    """Ejecuta el instalador de Forge en modo servidor."""
    print(f"\nInstalando Forge {FULL_VERSION} como servidor...")
    result = subprocess.run(
        ["java", "-jar", os.path.basename(installer_path), "--installServer"],
        cwd=target_dir,
    )
    if result.returncode != 0:
        print("ERROR: la instalación de Forge falló. Revisá el log de arriba.")
        sys.exit(1)


def write_eula(target_dir: str):
    eula_path = os.path.join(target_dir, "eula.txt")
    with open(eula_path, "w") as f:
        f.write("eula=true\n")
    print("EULA aceptado (eula.txt creado).")


def cleanup(target_dir: str, installer_path: str):
    for fname in (installer_path, os.path.join(target_dir, "installer.log")):
        if os.path.exists(fname):
            os.remove(fname)


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TARGET_DIR

    print(f"== Instalador de Forge {FULL_VERSION} ==")
    print(f"Destino: {target_dir}\n")

    check_java()

    os.makedirs(target_dir, exist_ok=True)

    installer_path = download_installer(target_dir)
    run_installer(installer_path, target_dir)
    write_eula(target_dir)
    cleanup(target_dir, installer_path)

    print("\n== Instalación completa ==")
    print(f"Carpeta del servidor: {target_dir}")

    run_sh = os.path.join(target_dir, "run.sh")
    if os.path.exists(run_sh):
        os.chmod(run_sh, 0o755)
        print("Para iniciar el servidor:")
        print(f"  cd {target_dir} && ./run.sh")
    else:
        print(f"Buscá el .jar generado (forge-{FULL_VERSION}.jar o similar) para arrancar el servidor manualmente,")
        print(f"por ejemplo: java -jar forge-{FULL_VERSION}.jar nogui")


if __name__ == "__main__":
    main()
