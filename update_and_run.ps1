Write-Host "Проверка виртуального окружения..." -ForegroundColor Green
$venvPath = "$PSScriptRoot\venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvPath)) {
    Write-Host "Виртуальное окружение не найдено! Создание нового окружения..." -ForegroundColor Yellow
    python -m venv "$PSScriptRoot\venv"
}

try {
    Write-Host "Активация виртуального окружения..." -ForegroundColor Green
    & "$PSScriptRoot\venv\Scripts\Activate.ps1"
    
    Write-Host "Обновление SQLAlchemy до последней версии..." -ForegroundColor Green
    pip install --upgrade sqlalchemy==2.0.27

    $runPath = "$PSScriptRoot\run.py"
    if (-not (Test-Path $runPath)) {
        Write-Host "Ошибка: Файл run.py не найден по пути: $runPath" -ForegroundColor Red
    } else {
        Write-Host "Запуск проекта..." -ForegroundColor Green
        python "$runPath"
    }
} catch {
    Write-Host "Произошла ошибка: $_" -ForegroundColor Red
}

Write-Host "Нажмите любую клавишу для выхода..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
