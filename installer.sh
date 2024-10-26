#!/bin/bash

check_python_version() {
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
        REQUIRED_VERSION="3.11.8"
        if [[ $(printf '%s\n' "$PYTHON_VERSION" "$REQUIRED_VERSION" | sort -V | head -n1) == "$REQUIRED_VERSION" ]]; then
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

create_linux_shortcut() {
    CURRENT_DIR=$(pwd)
    cat <<EOF >"$HOME/.local/share/applications/markdown-stripper.desktop"
[Desktop Entry]
Version=1.0
Name=Markdown Stripper
Comment=Strip markdown from text
Exec=${CURRENT_DIR}/launch_app.sh
Icon=${CURRENT_DIR}/icon.png
Terminal=false
Type=Application
Categories=Utility;TextTools;
EOF
    chmod +x "$HOME/.local/share/applications/markdown-stripper.desktop"
    echo "Created Linux desktop shortcut"
}

create_macos_app() {
    CURRENT_DIR=$(pwd)
    APP_NAME="Markdown Stripper.app"
    APP_CONTENTS="$APP_NAME/Contents"
    mkdir -p "$APP_CONTENTS"/{MacOS,Resources}

    # Copy necessary files into the app bundle
    cp launch_app.sh "$APP_CONTENTS/MacOS/"
    cp -R "$CURRENT_DIR" "$APP_CONTENTS/Resources/app"

    # Create Info.plist
    cat <<EOF >"$APP_CONTENTS/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>markdown-stripper</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.markdownstripper.app</string>
    <key>CFBundleName</key>
    <string>Markdown Stripper</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>CFBundleVersion</key>
    <string>1</string>
</dict>
</plist>
EOF

    # Create the executable script inside the app bundle
    cat <<'EOF' >"$APP_CONTENTS/MacOS/markdown-stripper"
#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
bash ./launch_app.sh > "$HOME/Library/Logs/MarkdownStripper.log" 2>&1 &
exit
EOF
    chmod +x "$APP_CONTENTS/MacOS/markdown-stripper"

    # Copy the icon if it exists
    if [ -f "icon.icns" ]; then
        cp "icon.icns" "$APP_CONTENTS/Resources/"
    fi

    echo "Created macOS application bundle"
}

check_python_version
create_venv
activate_venv
install_requirements

# Update launch_app.sh to use the app's Resources directory
cat <<'EOF' >launch_app.sh
#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
APP_DIR="$(cd "$(dirname "$0")/../Resources/app" && pwd)"
cd "$APP_DIR"
HOSTNAME=$(hostname -s)
VENV_DIR=".venv-${HOSTNAME}"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
python3 markdown_stripper.py
EOF

chmod +x launch_app.sh
chmod +x installer.sh

if [[ "$OSTYPE" == "darwin"* ]]; then
    create_macos_app
    echo "Installation complete. The Markdown Stripper.app has been created."
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    create_linux_shortcut
    echo "Installation complete. You can find Markdown Stripper in your applications menu."
else
    echo "Installation complete. Use ./launch_app.sh to run the application."
fi
