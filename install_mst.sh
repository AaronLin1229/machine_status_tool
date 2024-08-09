#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo -e "${RED}pip3 is not installed. Please install pip3 and try again.${NC}"
    exit 1
fi

# Create a virtual environment
python3 -m venv mst_env
source mst_env/bin/activate

# Install the package
pip install -e .

# Get the path of the virtual environment
VENV_PATH=$(pwd)/mst_env

# Create a wrapper script
cat > mst << EOL
#!/bin/bash
source ${VENV_PATH}/bin/activate
python -m machine_status_tool \$@
deactivate
EOL

# Make the wrapper script executable
chmod +x mst

# Move the wrapper script to a directory in PATH
sudo mv mst /usr/local/bin/

echo -e "${GREEN}Machine Status Tool has been successfully installed!${NC}"
echo -e "You can now use the 'mst' command from anywhere in your terminal."

# Create uninstall script
cat > uninstall_mst.sh << EOL
#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to prompt for confirmation
confirm() {
    read -r -p "\${1:-Are you sure? [y/N]} " response
    case "\$response" in
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
    echo -e "\${RED}Machine Status Tool is not installed on this system.\${NC}"
    exit 1
fi

# Get the path of the virtual environment
VENV_PATH=\$(grep "source" /usr/local/bin/mst | sed -E 's/source (.+)\/bin\/activate/\\1/')

# Confirm before uninstalling
if confirm "Are you sure you want to uninstall Machine Status Tool? [y/N]"; then
    # Remove the command from /usr/local/bin/
    sudo rm /usr/local/bin/mst

    # Remove the virtual environment
    if [ -d "\$VENV_PATH" ]; then
        rm -rf "\$VENV_PATH"
    fi

    echo -e "\${GREEN}Machine Status Tool has been successfully uninstalled.\${NC}"
else
    echo "Uninstallation cancelled."
fi
EOL

# Make the uninstall script executable
chmod +x uninstall_mst.sh

echo -e "An uninstallation script has been created. To uninstall Machine Status Tool in the future, run: ./uninstall_mst.sh"