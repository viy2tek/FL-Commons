param(
    [Parameter(Mandatory=$true)][string]$SdkDirectory,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$sdkPath = (Resolve-Path -LiteralPath $SdkDirectory).Path
$pluginPath = Join-Path $PSScriptRoot 'plugin.cpp'
$sdkBasePath = Join-Path $sdkPath 'source/c/fp_plugclass.cpp'
if (-not (Test-Path -LiteralPath $sdkBasePath)) { throw 'Official SDK source/c/fp_plugclass.cpp is required externally' }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$outputPath = (Resolve-Path -LiteralPath $OutputDirectory).Path
$compilerSetup = 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/Build/vcvars64.bat'
$environmentLines = & $env:ComSpec /d /c ('"' + $compilerSetup + '" >nul && set')
if ($LASTEXITCODE -ne 0) { throw 'MSVC x64 environment unavailable' }
foreach ($line in $environmentLines) {
    if ($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') }
}
# One translation unit avoids duplicate definitions in the supplied 2021 SDK headers.
$unitPath = Join-Path $outputPath 'plugin-unit.cpp'
$factoryContractPath = Join-Path $PSScriptRoot 'tests/factory_contract.h'
@(
    ('#include "' + $pluginPath.Replace('\','/') + '"')
    ('#include "' + $sdkBasePath.Replace('\','/') + '"')
    ('#include "' + $factoryContractPath.Replace('\','/') + '"')
) | Set-Content -LiteralPath $unitPath -Encoding utf8
$dllPath = Join-Path $outputPath 'FL Commons API.dll'
& cl.exe /nologo /std:c++17 /EHsc /W4 /O2 /MT /LD "/I$sdkPath/source/c" $unitPath "/Fo:$outputPath/plugin.obj" /link "/OUT:$dllPath" "/IMPLIB:$outputPath/plugin.lib" /DYNAMICBASE /NXCOMPAT
if ($LASTEXITCODE -ne 0) { throw 'Native plugin compilation failed' }
$testPath = Join-Path $PSScriptRoot 'tests/api_host.cpp'
& cl.exe /nologo /std:c++17 /EHsc /W4 /O2 /MT $testPath "/Fe:$outputPath/api_host.exe" "/Fo:$outputPath/api_host.obj"
if ($LASTEXITCODE -ne 0) { throw 'Controlled host compilation failed' }
Write-Output "Built $dllPath; loading in FL still requires separate validation."
$tokenTestPath = Join-Path $PSScriptRoot 'tests/token_provider_test.cpp'
& cl.exe /nologo /std:c++17 /EHsc /W4 /O2 /MT $tokenTestPath "/Fe:$outputPath/token_provider_test.exe" "/Fo:$outputPath/token_provider_test.obj"
if ($LASTEXITCODE -ne 0) { throw 'Token provider compilation failed' }
