#!/bin/bash
check_python_version() {
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
        REQUIRED_VERSION="3.11.8"
        if [[ $(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1) == "$REQUIRED_VERSION" ]]; then
            return 0
        else
            echo "Python 3.11.8 or higher is required."
            exit 1
        fi
    else
        echo "Python is not installed. Please install Python 3.11.8 or higher."
        exit 1
    fi
}
create_venv() {
    HOSTNAME=$(hostname -s)
    VENV_DIR=".venv-${HOSTNAME}"
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        echo "Virtual environment created: $VENV_DIR"
    else
        echo "Virtual environment already exists: $VENV_DIR"
    fi
}
activate_venv() {
    HOSTNAME=$(hostname -s)
    VENV_DIR=".venv-${HOSTNAME}"
    source "$VENV_DIR/bin/activate"
}
install_requirements() {
    pip install --upgrade pip
    pip install -r requirements.txt
}
check_python_version
create_venv
activate_venv
install_requirements
cat << 'EOF' > launch_app.sh
#!/bin/bash
HOSTNAME=$(hostname -s)
VENV_DIR=".venv-${HOSTNAME}"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
python3 markdown_stripper.py &
EOF
chmod +x launch_app.sh
chmod +x installer.sh
echo "Installation complete. Use ./launch_app.sh to run the application."
