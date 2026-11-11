<#
.SYNOPSIS
  查询车辆轨迹：按时间区间 + 车牌号查询 Lindorm TSDB gpsdb 库的 sys_gps 表
.DESCRIPTION
  非交互模式执行，结果直接输出到当前控制台（agent 可直接读取）。
  动态参数：
    - 时间区间：-Start/-End（格式 'yyyy-MM-dd HH:mm:ss'），或 -Minutes 指定最近 N 分钟；默认最近 10 分钟
    - 车牌号：-Plate，默认 渝D94049
.EXAMPLE
  # 默认参数：最近 10 分钟 + 渝D94049
  powershell -ExecutionPolicy Bypass -File query-gps.ps1
  # 指定时间区间和车牌
  powershell -ExecutionPolicy Bypass -File query-gps.ps1 -Plate '渝D94049' -Start '2026-05-26 19:21:03' -End '2026-05-26 19:22:05'
  # 最近 30 分钟，json 美化输出
  powershell -ExecutionPolicy Bypass -File query-gps.ps1 -Minutes 30 -Format json -Pretty
.NOTES
  需在非沙盒环境运行：执行 D:\soft 下的 exe、访问网络连接 Lindorm 端点。
#>
param(
    [string]$Plate  = '渝D94049',
    [string]$Start  = '',
    [string]$End    = '',
    [int]$Minutes   = 0,
    [string]$Format = 'table',
    [switch]$Pretty
)

# ========== 连接配置（与 connect.ps1 保持一致）==========
$CliPath  = 'D:\soft\lindorm-cli.exe'
$Url      = 'jdbc:lindorm:tsdb:url=http://ld-8vb432g58h0em96sw-proxy-tsdb-vpc.lindorm.aliyuncs.com:8242'
$Username = 'root'
$Password = 'ieEwstUiAKec'
$Database = 'gpsdb'
$Table    = 'sys_gps'
# ====================================================

try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
# 上一行解决中文（车牌/数据）在输出捕获时乱码

if (-not (Test-Path $CliPath)) { Write-Host "ERROR: 找不到 $CliPath"; exit 1 }

# 计算时间区间：优先显式 Start/End；否则 -Minutes；默认最近 10 分钟
$now = Get-Date
if (-not $End) { $End = $now.ToString('yyyy-MM-dd HH:mm:ss') }
if (-not $Start) {
    $spanMin = if ($Minutes -gt 0) { $Minutes } else { 10 }
    $Start = $now.AddMinutes(-$spanMin).ToString('yyyy-MM-dd HH:mm:ss')
}

$sql = "SELECT x.* FROM $Table x WHERE time >= '$Start' and time <= '$End' and license_plate_number = '$Plate';"
Write-Host "SQL: $sql"

$cliArgs = @('-url', $Url, '-username', $Username, '-password', $Password, '-database', $Database, '-format', $Format)
if ($Pretty) { $cliArgs += '-pretty' }
$cliArgs += @('-execute', $sql)

& $CliPath @cliArgs
exit $LASTEXITCODE
