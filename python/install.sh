#!/bin/bash
set -euo pipefail

# Debian best practices:
# - Self-contained application installs belong under /opt.
# - Executable binaries should be placed in /usr/bin for system-wide access.
INSTALL_DIR="/opt/justniffer"
BIN_DIR="/usr/bin"

# Check that python3 is installed.
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is required but not installed." >&2
    exit 1
fi

# Verify that the python3-venv module is available; if it isn’t, attempt to install it using apt-get.
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "python3-venv module not found. Attempting to install..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-venv
    else
        echo "Error: apt-get not found. Please install python3-venv manually." >&2
        exit 1
    fi
else
    echo "python3-venv is available."
fi

# Create the installation directory (under /opt) if it doesn't exist.
echo "Creating installation directory: ${INSTALL_DIR}"
if [ ! -d "${INSTALL_DIR}" ]; then
    sudo mkdir -p "${INSTALL_DIR}"
    sudo chown "$(whoami)":"$(whoami)" "${INSTALL_DIR}"
fi

# Define the virtual environment directory within the installation directory.
ENV_DIR="venv"
FULL_PATH_ENV_DIR="${INSTALL_DIR}/${ENV_DIR}"

# Create the virtual environment.
echo "Creating virtual environment at ${FULL_PATH_ENV_DIR}"
python3 -m venv "${FULL_PATH_ENV_DIR}"

# Activate the virtual environment.
echo "Activating virtual environment..."
source "${FULL_PATH_ENV_DIR}/bin/activate"

# Upgrade pip and install required packages (poetry and wheel).
echo "Installing Python packages: poetry and wheel"
pip install --upgrade pip
pip install poetry wheel

# Install project dependencies using Poetry.
echo "Installing project dependencies with Poetry..."
poetry install

# Create a symbolic link in BIN_DIR for the CLI executable.
CLI_PATH="${FULL_PATH_ENV_DIR}/bin/justniffer-cli"
if [ -e "${CLI_PATH}" ]; then
    echo "Creating symbolic link at ${BIN_DIR}/justniffer-cli"
    sudo ln -sf "${CLI_PATH}" "${BIN_DIR}/justniffer-cli"
else
    echo "Error: ${CLI_PATH} does not exist. Cannot create symbolic link." >&2
    exit 1
fi

echo "Installation completed successfully."
