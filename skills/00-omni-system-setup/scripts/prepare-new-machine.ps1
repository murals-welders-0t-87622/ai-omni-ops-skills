# Run with PowerShell 7 on the NEW computer. Default is read-only preflight.
param(
  [Parameter(Mandatory=$true)][string]$SourceRoot,
  [Parameter(Mandatory=$true)][string]$RuntimeRoot,
  [switch]$Prepare
)
$ErrorActionPreference='Stop'
if ($PSVersionTable.PSVersion.Major -lt 7 -or -not $IsWindows) { throw 'Windows PowerShell 7 is required.' }
$source=[IO.Path]::GetFullPath($SourceRoot)
$runtime=[IO.Path]::GetFullPath($RuntimeRoot)
if (-not (Test-Path -LiteralPath (Join-Path $source 'docker/docker-compose.ontology-lab.yml') -PathType Leaf)) { throw 'Current Lab source missing.' }
if ($runtime -eq [IO.Path]::GetPathRoot($runtime) -or $runtime.TrimEnd('\') -eq $env:USERPROFILE.TrimEnd('\')) { throw 'Choose a dedicated runtime directory.' }
if ($source.TrimEnd('\') -eq $runtime.TrimEnd('\') -or $runtime.StartsWith($source.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Runtime must stay outside source.' }
if (Test-Path -LiteralPath $runtime) { throw 'Runtime already exists. Inspect/reuse or choose a new directory; do not replace keys.' }
foreach ($name in @('LAB_DATABASE_PASSWORD','LAB_AUTH_TOKEN_SECRET','LAB_INSTALL_TOKEN_SECRET','LAB_OPERATOR_PASSWORD','LAB_APP_RUNTIME_MODE','WORKBUDDY_EXPERT_SOURCE_HOST_PATH','EXPERT_CONFIG_WRITE_ENABLED','EXPERT_CONFIG_LOCAL_WRITEBACK_EXECUTOR_ENABLED')) {
  if ([Environment]::GetEnvironmentVariable($name,'Process')) { throw "Inherited $name would override the new env file. Inspect and isolate this installation process first; do not change global environment values." }
}
foreach ($name in @('docker')) { if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { throw "Required tool missing: $name" } }
$osType=& docker info --format '{{.OSType}}'
if ($LASTEXITCODE -ne 0 -or $osType.Trim() -ne 'linux') { throw 'Start Docker Desktop Linux containers first.' }
$priorContainers=@(& docker ps -aq --filter 'label=com.docker.compose.project=ai-omni-ontology-lab')
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect existing containers.' }
$priorVolumes=@(& docker volume ls -q --filter 'label=com.docker.compose.project=ai-omni-ontology-lab')
if ($LASTEXITCODE -ne 0) { throw 'Could not inspect existing volumes.' }
if ($priorContainers.Count -gt 0 -or $priorVolumes.Count -gt 0) { throw 'This Lab project already has containers/volumes. Use existing-install or migration instructions; do not initialize a new database.' }
foreach ($port in @(23001,23011)) {
  if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) { throw "Port $port is occupied; do not stop an unknown process." }
}
if (-not $Prepare) { Write-Output 'Preflight passed; no files/containers changed. Add -Prepare on the NEW computer to create fresh runtime.'; return }
$null=New-Item -ItemType Directory -Path $runtime
$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User
$acl=[Security.AccessControl.DirectorySecurity]::new();$acl.SetOwner($sid);$acl.SetAccessRuleProtection($true,$false)
foreach($identity in @($sid,[Security.Principal.SecurityIdentifier]::new('S-1-5-18'))) {
  $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($identity,'FullControl','ContainerInherit,ObjectInherit','None','Allow'))
}
Set-Acl -LiteralPath $runtime -AclObject $acl
$empty=Join-Path $runtime 'expert-source';$null=New-Item -ItemType Directory -Path $empty
$lines=foreach($key in @('LAB_DATABASE_PASSWORD','LAB_AUTH_TOKEN_SECRET','LAB_INSTALL_TOKEN_SECRET','LAB_OPERATOR_PASSWORD')) {
  $secret=[Convert]::ToHexString([Security.Cryptography.RandomNumberGenerator]::GetBytes(32)).ToLowerInvariant()
  "$key=$secret"
}
$lines+=@('LAB_APP_RUNTIME_MODE=standard','INSTALL_LOCAL_OCR=1','INSTALL_LOCAL_ASR=0','EXPERT_CONFIG_WRITE_ENABLED=0','EXPERT_CONFIG_LOCAL_WRITEBACK_EXECUTOR_ENABLED=0',('WORKBUDDY_EXPERT_SOURCE_HOST_PATH='+$empty.Replace('\','/')))
[IO.File]::WriteAllText((Join-Path $runtime 'lab.env'),($lines -join "`n")+"`n",[Text.UTF8Encoding]::new($false))
$mount=$empty.Replace('\','/').Replace("'","''")
$override=@"
services:
  server:
    volumes:
      - type: bind
        source: '$mount'
        target: /expert-source
        read_only: true
"@
[IO.File]::WriteAllText((Join-Path $runtime 'install.override.yml'),$override,[Text.UTF8Encoding]::new($false))
Write-Output "Prepared fresh private runtime: $runtime"
Write-Output 'No secrets printed. No containers built or started. Empty expert source is intentional; Codex skills install separately.'
