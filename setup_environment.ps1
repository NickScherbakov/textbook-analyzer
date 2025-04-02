# Script for setting up Python virtual environment for Textbook Analyzer project

# Set error action preference to stop on error
$ErrorActionPreference = "Stop"

Write-Host "╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Textbook Analyzer Environment Setup Script   ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝" -ForegroundColor Cyan

# Function to check if command exists
function Test-CommandExists {
    param ($command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try {
        if (Get-Command $command) { return $true }
    }
    catch { return $false }
    finally { $ErrorActionPreference = $oldPreference }
}

# Step 1: Check Python version
Write-Host "`n[Step 1/4] Checking Python version..." -ForegroundColor Green
if (-not (Test-CommandExists python)) {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.9+." -ForegroundColor Red
    exit 1
}

$pythonVersion = python --version
Write-Host "Detected: $pythonVersion" -ForegroundColor Yellow

# Extract version number
$versionMatch = $pythonVersion | Select-String -Pattern 'Python (\d+\.\d+\.\d+)'
if ($versionMatch) {
    $versionNumber = $versionMatch.Matches[0].Groups[1].Value
    $majorMinor = $versionNumber -split "\." | Select-Object -First 2
    $major = [int]$majorMinor[0]
    $minor = [int]$majorMinor[1]
    
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 7)) {
        Write-Host "Python version 3.7+ is required. Please install a compatible version." -ForegroundColor Red
        exit 1
    }
    elseif ($major -eq 3 -and $minor -lt 9) {
        Write-Host "Python 3.9+ is recommended for best compatibility." -ForegroundColor Yellow
    }
}

# Step 2: Create virtual environment
Write-Host "`n[Step 2/4] Creating virtual environment..." -ForegroundColor Green
$venvPath = Join-Path -Path (Get-Location) -ChildPath "venv"

if (Test-Path $venvPath) {
    $response = Read-Host "Virtual environment already exists. Do you want to recreate it? (y/n)"
    if ($response -eq "y") {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Path $venvPath -Recurse -Force
    }
    else {
        Write-Host "Using existing virtual environment." -ForegroundColor Yellow
        $skipVenvCreation = $true
    }
}

if (-not $skipVenvCreation) {
    try {
        python -m venv venv
        Write-Host "Virtual environment created successfully." -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to create virtual environment: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 3: Activate virtual environment
Write-Host "`n[Step 3/4] Activating virtual environment..." -ForegroundColor Green
$activateScript = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Host "Activation script not found at: $activateScript" -ForegroundColor Red
    exit 1
}

try {
    & $activateScript
    Write-Host "Virtual environment activated." -ForegroundColor Green
}
catch {
    Write-Host "Failed to activate virtual environment: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Install dependencies
Write-Host "`n[Step 4/4] Installing dependencies..." -ForegroundColor Green
$requirementsFile = Join-Path -Path (Get-Location) -ChildPath "requirements.txt"

if (-not (Test-Path $requirementsFile)) {
    Write-Host "Requirements file not found at: $requirementsFile" -ForegroundColor Red
    exit 1
}

try {
    pip install -r $requirementsFile
    Write-Host "Dependencies installed successfully." -ForegroundColor Green
}
catch {
    Write-Host "Failed to install dependencies: $_" -ForegroundColor Red
    exit 1
}

# Setup environment file if not exists
$envExample = Join-Path -Path (Get-Location) -ChildPath ".env.example"
$envFile = Join-Path -Path (Get-Location) -ChildPath ".env"

if ((Test-Path $envExample) -and (-not (Test-Path $envFile))) {
    Write-Host "`nCreating .env file from example..." -ForegroundColor Green
    Copy-Item -Path $envExample -Destination $envFile
    Write-Host "Created .env file. Please edit it with your configuration values." -ForegroundColor Yellow
}

# Completion message
Write-Host "`n╔═══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            Setup Completed Successfully       ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`nTo run the application, use the following command:" -ForegroundColor Green
Write-Host "python run.py" -ForegroundColor Yellow
Write-Host "`nNotes:" -ForegroundColor Green
Write-Host "1. Ensure you've configured your .env file with Tesseract path for OCR functionality" -ForegroundColor Yellow
Write-Host "2. Make sure Yandex Cloud credentials are properly set in .env if using GPT features" -ForegroundColor Yellow
Write-Host "3. The virtual environment needs to be activated each time you open a new terminal" -ForegroundColor Yellow
Write-Host "   with: venv\Scripts\Activate.ps1" -ForegroundColor Yellow
