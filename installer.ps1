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
    return $venvDir
}
function Install-Requirements {
    param (
        [string]$VenvDir
    )
    $pythonPath = Join-Path $VenvDir "Scripts\python.exe"
    & $pythonPath -m pip install --upgrade pip
    & $pythonPath -m pip install -r requirements.txt
}
Check-PythonVersion
$venvDir = Create-Venv
$venvScript = Join-Path $venvDir "Scripts\Activate.ps1"
& $venvScript
Install-Requirements -VenvDir $venvDir
$launchScript = @'
$hostname = $env:COMPUTERNAME
$venvDir = ".venv-$hostname"
$venvScript = Join-Path $venvDir "Scripts\Activate.ps1"
if (-not (Test-Path $venvDir)) {
    python -m venv $venvDir
}
& "$venvScript"
python markdown_stripper.py
'@
Set-Content -Path "launch_app.ps1" -Value $launchScript -Encoding UTF8
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$(Get-Location)\Launch Markdown Stripper.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$(Get-Location)\launch_app.ps1`""
$Shortcut.WorkingDirectory = "$(Get-Location)"
$Shortcut.WindowStyle = 7
$Shortcut.Save()
Write-Host "Installation complete. Use ./launch_app.ps1 or the 'Launch Markdown Stripper' shortcut to run the application."