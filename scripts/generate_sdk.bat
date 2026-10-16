@echo off
echo =======================================================
echo  Generating Python SDK using OpenAPI Generator CLI
echo =======================================================

cd /d "%~dp0.."

echo [1/3] Exporting current OpenAPI JSON from application...
call .\env\Scripts\python.exe -c "import json; from app.main import app; open('openapi.json', 'w').write(json.dumps(app.openapi(), indent=2))"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to export openapi.json
    exit /b %errorlevel%
)

echo [2/3] Generating Python SDK into library_sdk/...
call npx -y @openapitools/openapi-generator-cli generate -i openapi.json -g python -o library_sdk --package-name library_sdk
if %errorlevel% neq 0 (
    echo [ERROR] SDK generation failed. Please verify Node.js and Java are installed.
    exit /b %errorlevel%
)

echo [3/3] Installing generated SDK into virtual environment in editable mode...
call .\env\Scripts\pip.exe install -e ./library_sdk
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install generated SDK into virtual environment.
    exit /b %errorlevel%
)

echo =======================================================
echo  SDK Generation and Installation Succeeded!
echo =======================================================
