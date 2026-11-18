$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptDir

try {
    $pythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"
    if (-not (Test-Path $pythonExe)) {
        $pythonExe = "python"
    }

    # Ensure instance/ directory exists for SQLite books.db
    New-Item -ItemType Directory -Force -Path (Join-Path $ScriptDir "instance") | Out-Null

    # Start Flask Books API in background
    $server = Start-Process -FilePath $pythonExe -ArgumentList "-m", "app", "--port", "5000" -PassThru -WindowStyle Hidden

    # Wait until /health responds
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $resp = Invoke-WebRequest -Uri "http://127.0.0.1:5000/health" -UseBasicParsing -TimeoutSec 2
            if ($resp.StatusCode -eq 200) {
                $ready = $true
                break
            }
        } catch {
            Start-Sleep -Milliseconds 300
        }
    }

    if (-not $ready) {
        throw "Books API failed to start on http://127.0.0.1:5000"
    }

    # Run Newman with CLI + JUnit reporters
    newman run books-api.postman_collection.json `
        -e postman/local.postman_environment.json `
        -r "cli,junit" `
        --reporter-junit-export reports/junit.xml
    $exitCode = $LASTEXITCODE
    exit $exitCode
}
finally {
    if ($server -and -not $server.HasExited) {
        Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
    }
    Pop-Location
}
