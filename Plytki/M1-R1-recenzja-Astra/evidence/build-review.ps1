$ErrorActionPreference='Stop'
$repoRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$env:IDF_PATH=Join-Path $repoRoot '.egrlab-toolchains/esp-idf'
$env:IDF_TOOLS_PATH=Join-Path $repoRoot '.egrlab-toolchains/tools'
$env:IDF_PYTHON_ENV_PATH=Join-Path $env:IDF_TOOLS_PATH 'python_env/idf5.4_py3.12_env'
$py=Join-Path $env:IDF_PYTHON_ENV_PATH 'Scripts/python.exe'
$paths=@((Split-Path $py),(Join-Path $env:IDF_TOOLS_PATH 'tools/cmake/3.30.2/bin'),(Join-Path $env:IDF_TOOLS_PATH 'tools/ninja/1.12.1'),(Join-Path $env:IDF_TOOLS_PATH 'tools/xtensa-esp-elf/esp-14.2.0_20250730/xtensa-esp-elf/bin'),'C:/Users/tgorbacz/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd')
$env:PATH=($paths -join ';')+';'+$env:PATH
$firmware=Join-Path $repoRoot 'M1-R1-recenzja-Astra/work/Rewizje/EGRLab-v6.3-m1/firmware'
Set-Location -LiteralPath $firmware
foreach($variant in @('test','logger','core','minimal','wifi')) {
    & $py (Join-Path $env:IDF_PATH 'tools/idf.py') -B "build-review-$variant" '-DIDF_TARGET=esp32s3' "-DSDKCONFIG=sdkconfig.review-$variant" "-DSDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.$variant.defaults" build *> (Join-Path $PSScriptRoot "build-$variant.log")
    $result=$LASTEXITCODE
    Write-Output "$variant exit=$result"
    if($result -ne 0) { Get-Content (Join-Path $PSScriptRoot "build-$variant.log") -Tail 35; exit $result }
}
