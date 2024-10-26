function Check-PythonVersion {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "Python is not installed. Please install Python 3.11.8 or higher."
        exit 1
    }
    $versionOutput = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
    $version = [Version]$versionOutput
    $requiredVersion = [Version]"3.11.8"
    if ($version -ge $requiredVersion) {
        return $true
    } else {
        Write-Host "Python 3.11.8 or higher is required."
        exit 1
    }
}
function Create-Venv {
    $hostname = $env:COMPUTERNAME
    $venvDir = ".venv-$hostname"
    if (-not (Test-Path $venvDir)) {
        python -m venv $venvDir
        Write-Host "Virtual environment created: $venvDir"
    } else {
        Write-Host "Virtual environment already exists: $venvDir"
    }
}
function Activate-Venv {
    $hostname = $env:COMPUTERNAME
    $venvDir = ".venv-$hostname"
    $venvScript = Join-Path $venvDir "Scripts\Activate.ps1"
    if (Test-Path $venvScript) {
        & $venvScript
    }
}
function Install-Requirements {
    pip install --upgrade pip
    pip install -r requirements.txt
}
Check-PythonVersion
Create-Venv
Activate-Venv
Install-Requirements

# Create launch_app.ps1 with proper PowerShell syntax
$launchScript = @'
$hostname = $env:COMPUTERNAME
$venvDir = ".venv-$hostname"
$venvScript = Join-Path $venvDir "Scripts\Activate.ps1"
if (-not (Test-Path $venvDir)) {
    python -m venv $venvDir
}
& "$venvScript"
pip install --upgrade pip
pip install -r requirements.txt
python markdown_stripper.py
'@

Set-Content -Path "launch_app.ps1" -Value $launchScript -Encoding UTF8
Write-Host "Installation complete. Use ./launch_app.ps1 to run the application."
