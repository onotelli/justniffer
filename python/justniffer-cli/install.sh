#!/bin/bash
set -euo pipefail

DEFAULT_INSTALL_DIR="/opt/justniffer"
DEFAULT_BIN_DIR="/usr/bin"
INSTALL_DIR="${JUSTNIFFER_INSTALL_DIR:-$DEFAULT_INSTALL_DIR}"
BIN_DIR="${JUSTNIFFER_BIN_DIR:-$DEFAULT_BIN_DIR}"

echo "Using INSTALL_DIR: $INSTALL_DIR"
echo "Using BIN_DIR: $BIN_DIR"

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
    if ! command -v sudo &>/dev/null; then
        echo "Error: sudo is required to install python3-venv." >&2
        exit 1
    fi
fi

if ! dpkg -s python3-venv &>/dev/null; then
    echo "python3-venv module not found. Attempting to install..."
    if command -v apt-get &>/dev/null; then
        $SUDO apt-get update
        $SUDO apt-get install -y python3-venv
    else
        echo "Error: apt-get not found. Please install python3-venv manually." >&2
        exit 1
    fi
else
    echo "python3-venv module is available."
fi

echo "Creating installation directory: ${INSTALL_DIR}"
if [ ! -d "${INSTALL_DIR}" ]; then
    $SUDO mkdir -p "${INSTALL_DIR}"
    $SUDO chown "$(whoami):$(id -gn)" "${INSTALL_DIR}"
fi

ENV_DIR="venv/justniffer-cli"
FULL_PATH_ENV_DIR="${INSTALL_DIR}/${ENV_DIR}"

if [ -d "${FULL_PATH_ENV_DIR}" ]; then
    echo "Removing existing virtual environment at ${FULL_PATH_ENV_DIR}"
    $SUDO rm -rf "${FULL_PATH_ENV_DIR}"
fi

echo "Creating virtual environment at ${FULL_PATH_ENV_DIR}"
python3 -m venv "${FULL_PATH_ENV_DIR}"

echo "Activating virtual environment..."
source "${FULL_PATH_ENV_DIR}/bin/activate"

if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Virtual environment activation failed." >&2
    exit 1
fi

echo "Installing Python packages: poetry and wheel"
pip install --upgrade pip
pip install poetry wheel

if ! command -v poetry &>/dev/null; then
    echo "Error: Poetry installation failed." >&2
    exit 1
fi

echo "Installing project dependencies with Poetry..."
poetry install

CLI_PATH="${FULL_PATH_ENV_DIR}/bin/justniffer-cli"
if [ ! -x "$CLI_PATH" ]; then
    echo "Error: ${CLI_PATH} is missing or not executable." >&2
    exit 1
fi

echo "Creating symbolic link at ${BIN_DIR}/justniffer-cli"
$SUDO ln -sf "${CLI_PATH}" "${BIN_DIR}/justniffer-cli"

echo "Installation completed successfully."

