param([int]$Port = 8001)
Set-Location -LiteralPath $PSScriptRoot
$aquaPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $aquaPython)) {
    Write-Host '缺少 Python 虚拟环境，请先按照 README.md 安装依赖。'
    exit 1
}
Write-Host "AquaSync 落雪同步页面：http://127.0.0.1:$Port/"
Write-Host '保持此窗口开启。停止服务请按 Ctrl+C。'
& $aquaPython -m uvicorn app.main:app --host 127.0.0.1 --port $Port
