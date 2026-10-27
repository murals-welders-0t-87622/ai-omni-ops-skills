# AI 全域运营中台：新电脑 Docker 安装与后续更新（直接交给 Codex）

**使用方法：**安装本技能后，向新电脑 Codex 说“安装整套系统”或“更新整套系统”。由 Codex 检查环境、执行、验证并报告，不要求用户手工拼命令。默认对象是 Windows 本机 Docker 安装；如果不是 Windows，先说明需要适配，不能照搬。

**版本基准（2026-10-27，仅供核对，不是永久锁版）：**

- 中台仓库：`https://github.com/murals-welders-0t-87622/ai-omni-ops-system-lab.git`，**私有**，安装分支 `feature/7tab-dashboard-and-brand-library`；本文件制定时已验证提交 `f355dde39d3a72ad0429c31c0cd27c95a66a7b46`。不是仓库默认的 main。
- 技能仓库：`https://github.com/murals-welders-0t-87622/ai-omni-ops-skills.git`，**公开**，`main`；`a22ca2c9e8682652f1d5ee25fe137645e30abe5f` 是旧基准（23 项，不含本安装技能）；应使用包含本技能的更新提交，以当前 registry 为准。
- 首装与升级按授权分支当前经过验证的最新提交，并记录实际 SHA；若取到的提交早于以上基准或无法证明来源，不得称安装了最新版。两个仓库不是同一个仓库，技能版本与中台版本分别记录。
- 旧的 `品牌增长AI中台-Docker安装资料包-20261026-V2.zip` 及其快照是**历史备用**，不包含以上后续电商更新；不能把它当最新版。若私有仓无法访问，可将旧包用于经用户知情的离线旧版安装，并明确缺少更新；不能宣称已完成最新安装或后续联网更新。

## 0. 执行边界和任务选择

1. 当前机器是否已有本中台？先只读检查 Git 目录、Docker Compose 项目、卷、端口和运行配置，检查后分别走 **A 全新安装** 或 **B 已有系统更新**。有既存中台或数据卷时绝不按新机分支生成新密钥或初始化新库。
2. 默认新机建在 `D:\AI-Omni`；无 D 盘或目标已占用时选一个空的专用目录，并在回执中记下实际路径。源码、技能源码、运行配置、备份各有独立目录，不能放入原有系统或别的应用目录。保留并隔离原有系统、Docker 项目和用户文件。
3. 中台前端、后端、数据库、初始化和入口在 Docker 内运行；Codex 和技能在宿主机。首次新机创建独立数据库和随机密钥，**不自动迁移其他电脑的品牌数据、素材、连接器授权或聊天记录**。旧机数据迁移走第 6 节。
4. 不输出、上传或提交密码、API 密钥、Token、数据库备份及品牌资料；不强推 Git，不用 `down -v`、`docker volume rm`、全局 prune、`--force-reset` 或 `--accept-data-loss`。不自动投放、发消息、发布或调用付费生成。
5. 操作前读当前两个仓库的 `AGENTS.md`、中台 `docker/docker-compose.ontology-lab.yml`、`docker/ontology-lab.Dockerfile`、`scripts/init-ontology-lab.cjs`、`docs/ontology-lab-runtime.md`、技能仓 `README.md` 和 `scripts/manage.py`。如果当前版本和下文的服务名、端口、参数、初始化或依赖不一致，按当前源码检查并调整；无法安全判断时停在相关步骤说明原因。
6. 不把“文件装好了”说成“Codex 已发现技能”，也不把连接配置好说成“实际品牌/第三方业务可用”。分别检查并报告。

## 1. 安装前检查与获取源码

- 要求 Windows、Docker Desktop 使用 Linux 容器、PowerShell 7、Git、Python 3.10+、已安装并登录的 Codex；检查 Docker 引擎、可用内存和磁盘、网络、GitHub 登录及目录写权限。中台 Node/npm/Prisma 在镜像构建，不需要宿主机 Node 来启动中台；**电商按钮的宿主执行器另需 Node 和 Codex CLI**，见第 5 节。Docker 下载/本地媒体制作还依赖网络和按需组件。
- 私有中台仓需用户在新电脑登录**有该仓库读取权限的 GitHub 账号**。必要的系统安装、账户登录、重启或验证由用户在自己的设备上完成；不要索取密码、粘贴旧机凭据或关闭安全校验。技能仓为公开仓，但其依赖和来源访问仍需验证。
- 克隆中台指定分支；若已经取得当前技能仓，直接复用该仓作为 `$SkillsPath`，不要重复克隆或因该目录存在而中止。以下是**两仓都尚未克隆**时的示例，路径按实际调整：

```powershell
$InstallRoot = 'D:\AI-Omni'
$SystemPath = Join-Path $InstallRoot 'system-source'
$SkillsPath = Join-Path $InstallRoot 'skills-source'
$RuntimePath = Join-Path $InstallRoot 'runtime'
$ProjectName = 'ai-omni-ontology-lab'
if ((Test-Path -LiteralPath $SystemPath) -or (Test-Path -LiteralPath $SkillsPath)) { throw '源码目录已有内容：先按已有安装检查，不能覆盖。' }
New-Item -ItemType Directory -Force -Path $InstallRoot | Out-Null
git clone --branch feature/7tab-dashboard-and-brand-library --single-branch https://github.com/murals-welders-0t-87622/ai-omni-ops-system-lab.git $SystemPath
if ($LASTEXITCODE -ne 0) { throw '中台源码获取失败；核对授权和网络。' }
git clone --branch main --single-branch https://github.com/murals-welders-0t-87622/ai-omni-ops-skills.git $SkillsPath
if ($LASTEXITCODE -ne 0) { throw '技能源码获取失败；保留已取得的中台目录，不重复覆盖。' }
git -C $SystemPath rev-parse HEAD
git -C $SkillsPath rev-parse HEAD
```

- 检查 `git status --short --branch`、目标分支与远端关系；不要把其他项目的未提交改动或历史自动清空。直连 GitHub 失败时先查网络和账号；只用当前 GitHub 正式支持的、安全的授权途径，不能依赖本文件提供任何令牌。部分克隆成功时从实际状态继续，不重复覆盖。

## 2. A：全新电脑首次安装

**仅当目标运行目录不存在、项目容器和卷不存在、端口 23001/23011 空闲时执行。** 保持 `InstallRoot`、`SystemPath`、`SkillsPath`、`RuntimePath` 和 `ProjectName` 对同一次安装一致。以下准备脚本只生成受限配置，不启动服务。直接调用本技能的 `scripts/prepare-new-machine.ps1`；以下为同一准备脚本的参考内容。若技能已安装，使用技能目录中的实际路径；若在仓库内，使用 `skills/00-omni-system-setup/scripts/prepare-new-machine.ps1`。它在 PowerShell 7 内运行。

```powershell
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
```

```powershell
# 如果使用仓库目录；若已安装到其他目录则改为当前技能的实际绝对路径。
$PrepareScript = Join-Path $SkillsPath 'skills/00-omni-system-setup/scripts/prepare-new-machine.ps1'
& $PrepareScript -SourceRoot $SystemPath -RuntimeRoot $RuntimePath
if (-not $?) { throw '预检失败' }
& $PrepareScript -SourceRoot $SystemPath -RuntimeRoot $RuntimePath -Prepare
if (-not $?) { throw '生成运行配置失败' }
$ComposeArgs = @('--project-name',$ProjectName,'--env-file',(Join-Path $RuntimePath 'lab.env'),
  '-f',(Join-Path $SystemPath 'docker/docker-compose.ontology-lab.yml'),
  '-f',(Join-Path $RuntimePath 'install.override.yml'))
docker compose @ComposeArgs config --quiet
if ($LASTEXITCODE -ne 0) { throw 'Compose 检查失败' }
foreach ($service in @('server','web','ingress')) {
  docker compose @ComposeArgs build $service
  if ($LASTEXITCODE -ne 0) { throw "构建失败：$service" }
}
docker compose @ComposeArgs up -d
if ($LASTEXITCODE -ne 0) { throw '启动失败，查看本项目日志' }
docker compose @ComposeArgs ps -a
```

- 命令仅用于首次空环境：`db-init` 使用当前仓库 `prisma db push`、不允许破坏性参数，并创建独立测试账号/品牌；它不是完整的旧数据迁移方案。用户第一次登录 `http://127.0.0.1:23001/login`，账号是 `operator@ontology-lab.invalid`，密码只从该机器受限 `runtime/lab.env` 中由用户本机安全查看；不得在聊天/日志中显示。新机的测试品牌不是真实品牌。
- 确认 `db-init` 成功退出、数据库健康、server 健康、web/ingress 运行，打开本机网页并实测登录；检查 `http://127.0.0.1:23011/api/health`。有限等待后还不可用就查**本项目**日志并报告失败，不删除卷、不称成功。
- 每次管理时重建同一组 `$ComposeArgs`。启动 `docker compose @ComposeArgs up -d`，停止 `docker compose @ComposeArgs stop`，查看 `docker compose @ComposeArgs ps -a`；不要操作其他 Docker 项目。默认只绑定本机回环地址，远程访问需另行设计授权。

## 3. 安装或更新 Codex 技能

- 在 `$SkillsPath` 使用当前仓库脚本。新机默认用户目录 `~/.agents/skills`；如果同一套已安装在 `~/.codex/skills`，使用安装器的 `--target` 指定原目录，避免两个作用域重复发现。先核是否存在用户自己的同名技能和本地修改；冲突时保留原文件，按安装器信息处理，**不能强制覆盖**。

```powershell
Push-Location $SkillsPath
try {
  python scripts/validate.py
  if ($LASTEXITCODE -ne 0) { throw '技能发布清单校验失败' }
  python scripts/manage.py install --dry-run
  if ($LASTEXITCODE -ne 0) { throw '技能安装预演失败' }
  python scripts/manage.py install
  if ($LASTEXITCODE -ne 0) { throw '技能安装失败，保留安装器回执' }
  python scripts/manage.py doctor
  if ($LASTEXITCODE -ne 0) { throw '技能检查失败' }
} finally { Pop-Location }
```

- 以上默认全部技能，安装器会按依赖安装；从预演和 doctor 实际结果确认数量及状态，以本次实际注册数量为准。安装器有事务备份；已有未托管技能仅在核对来源、备份和用户明确同意接管后使用 `--adopt-existing`。管理已有非默认目录时，以上各 `manage.py` 命令均加同一 `--target <已确认目录>`。
- 记录安装回执中的 `transaction` 和目标目录。更新出错时先读目标目录 `.omni-skills-backups/<transaction>/transaction.json`；必要时依仓库 `README` 的 `python scripts/manage.py rollback --transaction <事务ID>` 回退，并保留本地修改。
- 新建 Codex 对话或按客户端支持的方式重新加载，实际确认可以发现总统筹及电商等技能；未发现时单独排查，不能以 doctor 替代客户端加载验证。官方文档：[技能](https://learn.chatgpt.com/docs/build-skills)、[MCP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)。

## 4. B：已有系统的后续更新

1. **识别现有实例。** 找到原 Compose 项目名、源目录、当前 commit、运行环境文件、附加 override、数据库卷、素材卷、已安装技能及用户修改，记录正在使用的版本。确认没有进行中的生成或队列任务，不能只凭网页空闲判断；有执行器时检查对应任务状态、租约和进程身份。无可核实的停止/恢复路径则先停在更新前。
2. **保护并备份。** 停止或暂停对该实例的业务写入；记录本项目原服务、镜像 ID、启动参数、源码 commit、数据库与素材卷。用该实例自己的 PostgreSQL 执行一致性 `pg_dump -Fc`，核对退出状态和 `pg_restore --list`；在同一静止窗口内备份素材持久卷及受限的运行配置/解密密钥。备份放到源码和仓库外，做文件大小与哈希校验，并确认备份可读取、恢复命令与权限。不可复制运行中的 PostgreSQL 数据目录作为一致性备份。已有环境的 `LAB_INSTALL_TOKEN_SECRET` 与其他密钥必须保留；不要重新生成。停止仅限本实例的指定服务或执行器，不能影响别的项目。
3. **检查更新内容和数据库兼容性。** 先 `git fetch` 并比较本地/远端、变更文档、Compose、环境变量、Prisma schema 和初始化脚本；只在工作区干净且能 `git pull --ff-only` 时推进。当前 `db-init` 运行的是 `prisma db push`，并非成熟的可逆迁移系统：若 schema 变化无法证实不会丢数据，或备份/恢复未验证，不要运行更新后的初始化，先给出问题、影响和可回退方案。**仅回退镜像或 Git 提交无法回退已修改的数据库。**
4. **更新应用。** 确认备份与兼容性后，使用已有原运行配置、相同 Compose 项目和 override，在原源码仓按分支 `git pull --ff-only`；按当前仓库说明串行构建 server、web、ingress，按受控的项目启动顺序更新。记录旧/新 commit 和镜像 ID。服务失败时先保留日志与数据；只有确认数据库兼容时才恢复旧镜像。若 schema 已变化，先保护当前数据，再依据已验证的一致性备份恢复数据库、素材和密钥，不能只切旧镜像假装回滚成功。
5. **更新技能。** 在技能源码仓核工作区和分支，`git pull --ff-only`，按第 3 节先校验、dry-run、install、doctor；保留安装事务和旧版本。当前会话不一定自动重载，新建对话再确认。
6. **逐项验收。** 服务/数据库健康，网页登录与实际品牌资料读取，更新前后品牌和素材仍可读；技能本地状态及 Codex 新会话发现；此前有品牌 MCP 或宿主执行器时按第 5 节核对。发现不兼容或失败，给出哪一步失败、已做什么、备份位置与恢复点，不重放可能产生费用或副作用的业务任务。

## 5. 品牌 MCP、第三方连接及页面上的 Codex 按钮

- 由用户在新机中台创建或选择真实品牌，通过该品牌安装页面生成本机品牌 MCP 配置；默认本机地址 `http://127.0.0.1:23011/api/ai-control-center/mcp`。品牌 ID 和令牌必须来自**此机器此品牌**，按当前 Codex 官方支持方式增量配置；保留现有其他 MCP 服务。不要复制旧机 Token，不放进 Git、文档或聊天。按需重载后，真实验证身份、品牌资料、可用工具及一次只读调用。
- 有赞、3Chat、豆包/巨量、千问淘宝/天猫、RunningHub 等需用户在新机分别授权或配置；逐项做只读验证，缺失列为待配置。仅技能安装不会赋予第三方接口权限。
- 电商页面直接调用 Codex 的后台执行器运行在**宿主机**，不是技能文件，也不是 Docker Compose 服务。按当前中台仓 `integrations/commerce/executor/README.md`：检查宿主 Node、Codex CLI 登录、真实品牌 MCP、执行器可执行路径；为指定品牌使用本机安全的进程环境变量提供 Token，并以隐藏窗口启动该执行器、保存专属 PID。不要把 Token 放命令参数或输出日志。执行器目前不自动开机启动；需要用户明确要求才设置自启。检查心跳与一个用户授权、无额外费用的实际任务及版本回写；在线不等于图片/视频生成已验证。
- 若用户只需要中台页面和技能，可在缺第三方授权或宿主执行器时先完成可用部分，并列出按钮不能执行的具体原因。图片、视频及商业发布以实际连接、费用和用户指定的操作为准。

## 6. 如用户需要迁移旧电脑的历史数据

这与安装空系统不同：先确定源、目标、数据范围和停写窗口，保持旧系统不变；取得可验证的一致性数据库备份、对应时点的素材存储以及必须的旧加密密钥，按用户授权通过安全渠道迁移。目标环境另做备份，确认版本/schema、恢复顺序、权限和回退方案；在隔离目标上恢复并核对品牌、用户、连接器解密、素材及记录完整性。不能从旧机运行中的 PG 数据目录直接复制，不能拿随机新密钥读取旧加密数据，不能覆盖已有目标数据。资料或版本缺失就说明具体缺口，保留源和备份。

## 7. 完成回执（Codex 必须逐条报告）

1. 本轮是首次安装、更新还是迁移；机器与安装根目录；中台及技能仓实际分支和完整 SHA，是否为最新版。
2. Docker 项目名、数据卷及受限运行/备份位置，网页和 API 地址，服务、登录和历史数据核验结果。
3. 技能安装位置、安装事务、doctor 数量与状态、Codex 新会话是否实际发现；未发现项及原因。
4. 当前品牌 MCP 是否真实读取成功；第三方连接逐项状态；宿主 Codex 执行器是否在线及是否做过真实无费用任务。
5. 未完成事项、具体失败与恢复点；如为旧安装包，标清版本和未包含的更新。不得输出秘密。

这份文档是安装/更新工作指令，不代表已经在目标电脑实际测试。新电脑验收必须在目标机器重新执行。技能仓公开不包含旧版私人专家原文全集、品牌数据或账号授权。
