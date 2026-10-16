<#
.SYNOPSIS
  查询 sys_gps 当前最大 gps_id（按默认时间过滤，时间取自 state.json）
.DESCRIPTION
  SQL: SELECT gps_id FROM sys_gps WHERE time >= '<默认时间>' ORDER BY gps_id DESC LIMIT 1;
  默认时间初始为 '2026-09-24 19:27:41'，保存在本目录 state.json；
  每当 insert-gps.ps1 插入数据成功后，会自动把该默认时间更新为最新插入的时间。
  可用 -Time 覆盖默认时间。
.NOTES
  需在非沙盒环境运行：执行 D:\soft 下的 exe、访问网络连接 Lindorm 端点。
#>
param(
    [string]$Time = ''
)

# ========== 连接配置（与 connect.ps1 保持一致）==========
$CliPath  = 'D:\soft\lindorm-cli.exe'
$Url      = 'jdbc:lindorm:tsdb:url=http://ld-8vb432g58h0em96sw-proxy-tsdb-vpc.lindorm.aliyuncs.com:8242'
$Username = 'root'
$Password = 'ieEwstUiAKec'
$Database = 'gpsdb'
$Table    = 'sys_gps'
# ====================================================

$StateFile  = Join-Path $PSScriptRoot 'state.json'
$DefaultTime = '2026-09-24 19:27:41'

try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

if (-not (Test-Path $CliPath)) { Write-Host "ERROR: 找不到 $CliPath"; exit 1 }

if (-not $Time) {
    if (Test-Path $StateFile) {
        try { $Time = (Get-Content $StateFile -Raw | ConvertFrom-Json).max_id_query_time } catch {}
    }
    if (-not $Time) {
        # 首次运行：初始化 state.json 为默认时间
        $Time = $DefaultTime
        @{ max_id_query_time = $Time } | ConvertTo-Json | Set-Content -Path $StateFile -Encoding UTF8
    }
    Write-Host "使用默认过滤时间: $Time"
}

$sql = "SELECT gps_id FROM $Table WHERE time >= '$Time' ORDER BY gps_id DESC LIMIT 1;"
Write-Host "SQL: $sql"
& $CliPath '-url' $Url '-username' $Username '-password' $Password '-database' $Database '-format' 'table' '-execute' $sql
exit $LASTEXITCODE
