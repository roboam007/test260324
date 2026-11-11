<#
.SYNOPSIS
  Lindorm CLI 自动连接：启动 lindorm-cli.exe 并自动连接 Lindorm TSDB
.DESCRIPTION
  主方式（默认）：用 lindorm-cli 原生连接参数启动（含 -database gpsdb），窗口打开即为已连接的交互式会话；
  随后自动输入并执行：show databases; use gpsdb; show tables;
  兜底方式（-Fallback）：先启动空 CLI 窗口，模拟键盘输入 connect 命令并回车执行，再执行上述三条命令。
.NOTES
  需在非沙盒环境运行：启动 D:\soft 下的 exe、在用户桌面创建控制台窗口、访问网络连接 Lindorm 端点。
#>
param(
    [switch]$Fallback
)

# ========== 连接配置（按需修改）==========
$CliPath  = 'D:\soft\lindorm-cli.exe'
$Url      = 'jdbc:lindorm:tsdb:url=http://ld-8vb432g58h0em96sw-proxy-tsdb-vpc.lindorm.aliyuncs.com:8242'
$Username = 'root'
$Password = 'ieEwstUiAKec'
$Database = 'gpsdb'
# ========================================

# 兜底方式要输入的命令
$ConnectCmd = "connect $Url $Username $Password;"

# 连接成功后自动在窗口执行的命令
$PostConnectCommands = @(
    'show databases;'
    "use $Database;"
    'show tables;'
)

# 向已激活的 CLI 窗口逐条发送命令并回车执行；返回是否成功激活并发送
function Send-CliCommands {
    param([object]$WsShell, [int]$TargetPid, [string[]]$Commands)
    if (-not $WsShell.AppActivate($TargetPid)) { return $false }
    Start-Sleep -Milliseconds 300
    foreach ($cmd in $Commands) {
        $WsShell.SendKeys($cmd)
        Start-Sleep -Milliseconds 150
        $WsShell.SendKeys('{ENTER}')
        Start-Sleep -Milliseconds 800   # 等上一条命令结果输出完
    }
    return $true
}

if (-not (Test-Path $CliPath)) {
    Write-Host "ERROR: 找不到 $CliPath"
    exit 1
}

$WorkDir = Split-Path $CliPath

if ($Fallback) {
    # ---------- 兜底方式：启动后模拟键盘输入 connect 命令 ----------
    $proc = Start-Process -FilePath $CliPath -WorkingDirectory $WorkDir -PassThru
    $ws = New-Object -ComObject WScript.Shell
    $target = $null
    $deadline = (Get-Date).AddSeconds(20)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 500
        # 优先用启动进程的 PID 激活窗口；若 exe 拉起了子进程则按窗口标题匹配
        if (-not $proc.HasExited -and $ws.AppActivate($proc.Id)) { $target = $proc.Id; break }
        $w = Get-Process | Where-Object { $_.MainWindowTitle -like '*lindorm*' } | Select-Object -First 1
        if ($w -and $ws.AppActivate($w.Id)) { $target = $w.Id; break }
    }
    if (-not $target) {
        Write-Host "ERROR: 未能激活 lindorm-cli 窗口，未发送按键。请手动输入：$ConnectCmd"
        exit 1
    }
    Start-Sleep -Seconds 3   # 等 CLI 提示符就绪，若按键丢失可调大此值
    $null = $ws.AppActivate($target)
    Start-Sleep -Milliseconds 300
    $ws.SendKeys($ConnectCmd)
    Start-Sleep -Milliseconds 150
    $ws.SendKeys('{ENTER}')
    Start-Sleep -Seconds 8   # 等待 connect 完成
    $null = Send-CliCommands -WsShell $ws -TargetPid $target -Commands $PostConnectCommands
    Write-Host "OK: 已发送连接命令及后续命令（$($PostConnectCommands -join ' ')），请在窗口确认结果。"
}
else {
    # ---------- 主方式：原生参数直连，启动即连接 ----------
    $cliArgs = @('-url', $Url, '-username', $Username, '-password', $Password, '-database', $Database)
    $proc = Start-Process -FilePath $CliPath -WorkingDirectory $WorkDir -ArgumentList $cliArgs -PassThru
    Start-Sleep -Seconds 8   # 等待连接建立
    if ($proc.HasExited) {
        Write-Host "ERROR: lindorm-cli 进程已退出，连接可能失败。请检查 URL/账号/密码（本文件顶部变量）或网络是否可达。"
        exit 1
    }
    # 连接成功，自动执行 show databases; use gpsdb; show tables;
    $ws = New-Object -ComObject WScript.Shell
    if (Send-CliCommands -WsShell $ws -TargetPid $proc.Id -Commands $PostConnectCommands) {
        Write-Host "OK: lindorm-cli 已启动并连接（PID $($proc.Id)），已自动执行: $($PostConnectCommands -join ' ')"
    } else {
        Write-Host "OK: lindorm-cli 已启动并连接（PID $($proc.Id)），但窗口激活失败，请手动执行: $($PostConnectCommands -join ' ')"
    }
}
