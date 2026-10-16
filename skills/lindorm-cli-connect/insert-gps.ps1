<#
.SYNOPSIS
  插入车辆轨迹测试数据：给定时间区间均分 20 个时间点，批量插入 20 条 sys_gps 记录
.DESCRIPTION
  - time：-Start/-End 给区间，区间包含首尾（第1点=Start、第20点=End），中间均分出 18 个时间点，共 20 点（默认区间 = 最近 20 秒）；
    区间不足 19 秒时按 1 秒间隔、包含首尾，有几秒就插入几条（条数 = 整秒数 + 1，可能少于 20 条）
  - gps_id：从"当前最大 gps_id + 1"开始追加（查询过滤条件 time >= state.json 默认时间，初始 '2026-09-24 19:27:41'；可用 -StartId 手动指定）
  - 车牌：默认 渝D94049，可用 -Plate 指定
  - 坐标：默认北京范围 (116.10,39.85) -> (116.70,40.05) 线性插值；数据库存值 = 真实经纬度 * 600000（即 真实值 = 库值 / 600000）
  - 插入成功后，state.json 的默认查询时间自动更新为本次最新插入的时间
  - -DryRun：仅打印 SQL，不执行、不更新 state.json
.EXAMPLE
  # 默认：时间区间=最近20秒(间隔1秒)、渝D94049、北京坐标
  powershell -ExecutionPolicy Bypass -File insert-gps.ps1
  # 指定区间与车牌
  powershell -ExecutionPolicy Bypass -File insert-gps.ps1 -Plate '京A12345' -Start '2026-09-24 14:00:00' -End '2026-09-24 14:10:00'
.NOTES
  需在非沙盒环境运行：执行 D:\soft 下的 exe、访问网络连接 Lindorm 端点。
#>
param(
    [string]$Plate   = '渝D94049',
    [string]$Start    = '',
    [string]$End      = '',
    [double]$LngFrom  = 116.10,   # 起点经度（北京范围）
    [double]$LatFrom  = 39.85,    # 起点纬度
    [double]$LngTo    = 116.70,   # 终点经度
    [double]$LatTo    = 40.05,    # 终点纬度
    [long]$StartId    = -1,       # 默认自动查询"当前最大 gps_id + 1"；也可手动指定起始 ID
    [switch]$DryRun
)

# ========== 连接配置（与 connect.ps1 保持一致）==========
$CliPath  = 'D:\soft\lindorm-cli.exe'
$Url      = 'jdbc:lindorm:tsdb:url=http://ld-8vb432g58h0em96sw-proxy-tsdb-vpc.lindorm.aliyuncs.com:8242'
$Username = 'root'
$Password = 'ieEwstUiAKec'
$Database = 'gpsdb'
$Table    = 'sys_gps'
# ====================================================

$Points      = 20          # 每次插入条数：区间内均分 20 个时间点
$MileageBase = 92346.3     # 初始里程（可按需修改）
$StateFile   = Join-Path $PSScriptRoot 'state.json'
$DefaultStateTime = '2026-09-24 19:27:41'
$Fmt = 'yyyy-MM-dd HH:mm:ss'
$Inv = [System.Globalization.CultureInfo]::InvariantCulture

try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

if (-not (Test-Path $CliPath)) { Write-Host "ERROR: 找不到 $CliPath"; exit 1 }

function Invoke-Lindorm {
    param([string]$Sql)
    & $CliPath '-url' $Url '-username' $Username '-password' $Password '-database' $Database '-format' 'csv' '-execute' $Sql 2>&1
}

function Parse-MaxIdFromOutput {
    param([object]$Out)
    $text = $Out | Out-String
    foreach ($line in ($text -split "`r?`n")) {
        $t = $line.Trim().Trim('"')
        if ($t -match '^[0-9]{5,}$') { return [long]$t }
    }
    return $null
}

# ---------- 1. 时间区间 -> 20 个时间点 ----------
function Parse-TimeParam([string]$s) {
    try { return [datetime]::ParseExact($s, $Fmt, $Inv) }
    catch {
        try { return [datetime]::Parse($s, $Inv) }
        catch { Write-Host "ERROR: 无法解析时间 '$s'，格式应为 $Fmt"; exit 1 }
    }
}
$endDt   = if ($End)   { Parse-TimeParam $End }   else { Get-Date }
$startDt = if ($Start) { Parse-TimeParam $Start } else { $endDt.AddSeconds(-($Points - 1)) }
if ($startDt -gt $endDt) { Write-Host "ERROR: 开始时间不能晚于结束时间"; exit 1 }

# 时间点规则：区间包含首尾（第1点=Start、第20点=End），中间均分 18 个点，共 20 点
$totalSec = ($endDt - $startDt).TotalSeconds
if ($totalSec -ge ($Points - 1)) {
    $stepSec = $totalSec / ($Points - 1)   # 精确均分（可为小数秒），保证首=Start、尾=End
    $times = @()
    for ($i = 0; $i -lt $Points; $i++) { $times += $startDt.AddSeconds($stepSec * $i).ToString($Fmt, $Inv) }
    $times[$Points - 1] = $endDt.ToString($Fmt, $Inv)   # 消除浮点/舍入误差，强制尾点精确等于 End
} else {
    # 区间不足：按 1 秒间隔、包含首尾，有几秒就插入几条（条数 = 整秒数 + 1）
    $n = [int][math]::Floor($totalSec) + 1
    if ($n -lt 1) { $n = 1 }
    Write-Host "WARN: 区间仅 $totalSec 秒，按 1 秒间隔、包含首尾，本次插入 $n 条（不足 20 条）。"
    $times = @()
    for ($i = 0; $i -lt $n; $i++) { $times += $startDt.AddSeconds($i).ToString($Fmt, $Inv) }
}
$Points = $times.Count   # 后续逻辑（gps_id 数量/行数/提示）统一按实际条数

# ---------- 2. 起始 gps_id = 当前最大 gps_id + 1 ----------
if ($StartId -lt 0) {
    $qTime = $DefaultStateTime
    if (Test-Path $StateFile) {
        try { $qTime = (Get-Content $StateFile -Raw | ConvertFrom-Json).max_id_query_time } catch {}
    }
    Write-Host "查询当前最大 gps_id（time >= '$qTime'）..."
    $maxId = Parse-MaxIdFromOutput (Invoke-Lindorm "SELECT gps_id FROM $Table WHERE time >= '$qTime' ORDER BY gps_id DESC LIMIT 1;")
    if (-not $maxId) {
        Write-Host "  按时间未查到记录，回退查询全表最大 gps_id ..."
        $maxId = Parse-MaxIdFromOutput (Invoke-Lindorm "SELECT gps_id FROM $Table ORDER BY gps_id DESC LIMIT 1;")
    }
    if (-not $maxId) { Write-Host "ERROR: 未查到任何已有 gps_id，请用 -StartId 指定起始 ID"; exit 1 }
    $StartId = $maxId + 1
    Write-Host "  当前最大 gps_id = $maxId，本次从 $StartId 开始追加"
}

# ---------- 3. 生成 20 行数据（北京坐标线性插值，库值 = 真实经纬度 * 600000） ----------
$midLat = ($LatFrom + $LatTo) / 2
$dx = ($LngTo - $LngFrom) * [math]::Cos($midLat * [math]::PI / 180)
$dy = $LatTo - $LatFrom
$angle = [int][math]::Round(([math]::Atan2($dx, $dy) * 180 / [math]::PI + 360) % 360)   # 行进方向角

$cols = 'gps_id, license_plate_number, time, longitude, latitude, mileage, speed, angle, altitude, dele_flag'
$rDenom = [math]::Max($Points - 1, 1)   # 防止单条时除零
$values = @()
for ($i = 0; $i -lt $Points; $i++) {
    $r = $i / $rDenom
    $dbLng = [long][math]::Round(($LngFrom + ($LngTo - $LngFrom) * $r) * 600000)
    $dbLat = [long][math]::Round(($LatFrom + ($LatTo - $LatFrom) * $r) * 600000)
    $speed    = [int][math]::Round(45 + 10 * [math]::Sin($i * 0.5))   # 35~55 波动
    $altitude = 40 + ($i % 5)
    $mileage  = [math]::Round($MileageBase + $i * 0.1, 1)
    $id = $StartId + $i
    $values += "('$id', '$Plate', '$($times[$i])', CAST('$dbLng' AS BIGINT), CAST('$dbLat' AS BIGINT), CAST('$($mileage.ToString($Inv))' AS DOUBLE), CAST('$speed' AS INT), CAST('$angle' AS INT), CAST('$altitude' AS INT), CAST('0' AS INT))"
}
$sql = "INSERT INTO $Table ($cols) VALUES " + ($values -join ', ') + ';'
Write-Host ""
Write-Host "SQL（$Points 行）:"
Write-Host $sql

if ($DryRun) { Write-Host ""; Write-Host "DRYRUN: 仅打印 SQL，未执行，state.json 未更新。"; exit 0 }

# ---------- 4. 执行插入（失败自动回退逐条插入） ----------
Write-Host ""
Write-Host "插入中..."
$out = Invoke-Lindorm $sql
$ok = ($LASTEXITCODE -eq 0) -and ((($out | Out-String) -notmatch '(?i)error|exception|failed'))
if (-not $ok) {
    Write-Host "多行 VALUES 方式失败，回退逐条插入..."
    Write-Host ($out | Out-String)
    $done = 0
    foreach ($v in $values) {
        $one = "INSERT INTO $Table ($cols) VALUES $v;"
        $o = Invoke-Lindorm $one
        if ($LASTEXITCODE -ne 0 -or (($o | Out-String) -match '(?i)error|exception|failed')) {
            Write-Host "ERROR: 逐条插入失败于第 $($done + 1) 条: $one"
            Write-Host ($o | Out-String)
            exit 1
        }
        $done++
    }
}

# ---------- 5. 插入成功：state.json 默认时间更新为本次最新插入时间 ----------
$lastTime = $times[$Points - 1]
@{ max_id_query_time = $lastTime } | ConvertTo-Json | Set-Content -Path $StateFile -Encoding UTF8
Write-Host ""
Write-Host "OK: 已插入 $Points 条（gps_id $StartId ~ $($StartId + $Points - 1)），时间 $($times[0]) ~ $lastTime，车牌 $Plate。"
Write-Host "state.json 默认查询时间已更新为 $lastTime"
exit 0
