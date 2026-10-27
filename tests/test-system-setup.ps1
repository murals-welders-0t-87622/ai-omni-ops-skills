$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$script = Join-Path $repo 'skills/00-omni-system-setup/scripts/prepare-new-machine.ps1'
$baseRoot = Join-Path $repo '.local/setup-preflight-tests'
New-Item -ItemType Directory -Force -Path $baseRoot | Out-Null
$base = Join-Path $baseRoot ([guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $base | Out-Null
$resolved = (Resolve-Path $base).Path
if (-not $resolved.StartsWith((Resolve-Path $baseRoot).Path + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'unsafe test directory' }
try {
  $src=Join-Path $base 'source'; New-Item -ItemType Directory -Force -Path (Join-Path $src 'docker') | Out-Null
  'services: {}' | Set-Content -LiteralPath (Join-Path $src 'docker/docker-compose.ontology-lab.yml')
  function docker { $global:LASTEXITCODE=0; if ($args[0] -eq 'info') { 'linux' } }
  function Get-NetTCPConnection { return $null }
  $runtime=Join-Path $base 'runtime'
  & $script -SourceRoot $src -RuntimeRoot $runtime | Out-Null
  if (Test-Path -LiteralPath $runtime) { throw 'preflight unexpectedly wrote files' }
  & $script -SourceRoot $src -RuntimeRoot $runtime -Prepare | Out-Null
  $envFile=Join-Path $runtime 'lab.env';$override=Join-Path $runtime 'install.override.yml'
  if (-not (Test-Path $envFile) -or -not (Test-Path $override)) { throw 'configuration missing' }
  $envText=Get-Content -LiteralPath $envFile
  $secrets=@($envText | Where-Object { $_ -match '^LAB_(DATABASE_PASSWORD|AUTH_TOKEN_SECRET|INSTALL_TOKEN_SECRET|OPERATOR_PASSWORD)=[a-f0-9]{64}$' })
  if ($secrets.Count -ne 4 -or (($secrets | ForEach-Object { ($_ -split '=',2)[1] } | Select-Object -Unique).Count -ne 4)) { throw 'independent configuration not generated' }
  $before=(Get-FileHash -LiteralPath $envFile -Algorithm SHA256).Hash
  $blocked=$false
  try { & $script -SourceRoot $src -RuntimeRoot $runtime -Prepare | Out-Null } catch { $blocked=$true }
  if (-not $blocked -or (Get-FileHash -LiteralPath $envFile -Algorithm SHA256).Hash -ne $before) { throw 'existing runtime not protected' }
  if ((Get-Content -LiteralPath $override -Raw) -notmatch 'read_only: true') { throw 'expert mount not read-only' }
  Write-Output 'PASS: read-only preflight, fresh isolated configuration, existing runtime protection, independent secrets and read-only mount (mock Docker)'
} finally {
  if (Test-Path -LiteralPath $resolved) { Remove-Item -LiteralPath $resolved -Recurse -Force }
}
