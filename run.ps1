param([ValidateSet('setup','run','build','voices','ollama','test')][string]$Target = 'run')
$ErrorActionPreference = 'Stop'
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 "$PSScriptRoot\scripts\manage.py" $Target
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python "$PSScriptRoot\scripts\manage.py" $Target
} else {
    throw 'Install Python 3.11 or newer, enable Add Python to PATH, then reopen PowerShell.'
}
exit $LASTEXITCODE
