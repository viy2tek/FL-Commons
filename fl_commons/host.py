"""Read-only Windows host inventory through documented OS interfaces."""
import os
import ntpath
import re
from pathlib import Path
import subprocess
import sys

from flcommons_common.validation import ProtocolError, strict_json
from .errors import OperationError

QUERY = r'''
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$installationRecords = @()
$processRecords = @()
$searchRoots = @($env:ProgramFiles, ${env:ProgramFiles(x86)}) | Select-Object -Unique
foreach ($searchRoot in $searchRoots) {
    if (-not $searchRoot) { continue }
    $vendorDirectory = Join-Path $searchRoot 'Image-Line'
    if (-not (Test-Path -LiteralPath $vendorDirectory -PathType Container)) { continue }
    $candidateDirectories = Get-ChildItem -LiteralPath $vendorDirectory -Directory |
        Where-Object { $_.Name -match '^FL Studio [0-9]' }
    foreach ($candidateDirectory in $candidateDirectories) {
        foreach ($executableName in @('FL64.exe', 'FL64 (scaled).exe', 'FL.exe')) {
            $executablePath = Join-Path $candidateDirectory.FullName $executableName
            if (Test-Path -LiteralPath $executablePath -PathType Leaf) {
                $executable = Get-Item -LiteralPath $executablePath
                $installationRecords += @{
                    path = $executable.FullName
                    version = $executable.VersionInfo.ProductVersion
                }
            }
        }
    }
}
$matchingProcesses = @(Get-Process | Where-Object { $_.ProcessName -in @('FL64', 'FL64 (scaled)', 'FL') })
foreach ($matchingProcess in $matchingProcesses) {
    $processPath = $null
    try { $processPath = $matchingProcess.Path } catch { }
    $verifiedIdentity = $false
    if ($processPath) {
        $verifiedIdentity = @($installationRecords | Where-Object { $_.path -eq $processPath }).Count -gt 0
    }
    $processRecords += @{
        pid = $matchingProcess.Id
        name = $matchingProcess.ProcessName
        path = $processPath
        identity_verified = $verifiedIdentity
    }
}
@{ installations = @($installationRecords); processes = @($processRecords) } | ConvertTo-Json -Depth 4 -Compress
'''


def inspect_host():
    if sys.platform != 'win32':
        raise OperationError('unsupported_platform', 'Host inspection currently supports Windows only')
    executable = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32' / 'WindowsPowerShell' / 'v1.0' / 'powershell.exe'
    try:
        result = subprocess.run([str(executable), '-NoLogo', '-NoProfile', '-NonInteractive', '-Command', QUERY],
                                capture_output=True, text=True, encoding='utf-8', timeout=5,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if result.returncode or len(result.stdout) > 131072:
            raise ProtocolError('Host query failed or exceeded output limit')
        data = strict_json(result.stdout.lstrip('\ufeff'))
        if not _valid_inventory(data):
            raise ProtocolError('Invalid host inventory')
        data = _latest_only(data)
    except (OSError, subprocess.SubprocessError, ProtocolError, UnicodeError) as exc:
        raise OperationError('host_inspection_failed', 'Windows host query failed; no absence inferred') from exc
    return dict(data, platform='windows', control_connected=False,
                coverage='latest-known-version-in-standard-install-locations')


def _latest_only(data):
    versions = []
    for item in data['installations']:
        version = item['version']
        if not isinstance(version, str) or not re.fullmatch(r'[0-9]{1,5}(?:\.[0-9]{1,5}){3}', version):
            raise ProtocolError('Cannot select latest installation with unknown version metadata')
        versions.append(tuple(int(part) for part in version.split('.')))
    if not versions:
        return {'installations': [], 'processes': [], 'selected_version': None}
    latest = max(versions)
    installations = [item for item, version in zip(data['installations'], versions) if version == latest]
    paths = {ntpath.normcase(item['path']) for item in installations}
    processes = [item for item in data['processes'] if item['path'] is not None and
                 ntpath.normcase(item['path']) in paths and item['identity_verified']]
    return {'installations': installations, 'processes': processes,
            'selected_version': '.'.join(str(part) for part in latest)}


def _valid_inventory(data):
    if not isinstance(data, dict) or set(data) != {'installations', 'processes'}:
        return False
    if not isinstance(data['installations'], list) or not isinstance(data['processes'], list):
        return False
    for item in data['installations']:
        if (not isinstance(item, dict) or set(item) != {'path', 'version'} or
                not isinstance(item['path'], str) or
                not (item['version'] is None or isinstance(item['version'], str))):
            return False
    for item in data['processes']:
        if (not isinstance(item, dict) or set(item) != {'pid', 'name', 'path', 'identity_verified'} or
                type(item['pid']) is not int or item['pid'] <= 0 or
                not isinstance(item['name'], str) or type(item['identity_verified']) is not bool or
                not (item['path'] is None or isinstance(item['path'], str))):
            return False
    return True
