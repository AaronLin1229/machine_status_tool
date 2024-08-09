#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to prompt for confirmation
confirm() {
    read -r -p "${1:-Are you sure? [y/N]} " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            true
            ;;
        *)
            false
            ;;
    esac
}

# Check if MST is installed
if [ ! -f /usr/local/bin/mst ]; then
    echo -e "${RED}Machine Status Tool is not installed on this system.${NC}"
    exit 1
fi

# Get the path of the virtual environment
VENV_PATH=$(grep "source" /usr/local/bin/mst | sed -E 's/source (.+)\/bin\/activate/\1/')

# Confirm before uninstalling
if confirm "Are you sure you want to uninstall Machine Status Tool? [y/N]"; then
    # Remove the command from /usr/local/bin/
    sudo rm /usr/local/bin/mst

    # Remove the virtual environment
    if [ -d "$VENV_PATH" ]; then
        rm -rf "$VENV_PATH"
    fi

    echo -e "${GREEN}Machine Status Tool has been successfully uninstalled.${NC}"
else
    echo "Uninstallation cancelled."
fi
