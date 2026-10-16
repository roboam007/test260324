---
name: lindorm-cli-connect
description: "Starts lindorm-cli & connects Lindorm TSDB (gpsdb); queries vehicle GPS trajectory by time/plate; queries max gps_id; inserts 20-point test trajectories. Invoke for Lindorm connect/query/insert tasks."
---

# Lindorm CLI 连接、轨迹查询与测试数据插入

本技能目录下包含以下脚本/文件：

| 脚本/文件 | 作用 |
|---|---|
| `connect.ps1` | 启动 lindorm-cli 新窗口、自动连接，随后自动执行 `show databases; use gpsdb; show tables;` |
| `query-gps.ps1` | 非交互查询车辆轨迹（时间区间/车牌动态参数） |
| `get-max-gps-id.ps1` | 查询当前最大 gps_id（默认时间过滤，见 state.json） |
| `insert-gps.ps1` | 向 sys_gps 插入 20 条轨迹测试数据（区间均分 20 个时间点） |
| `state.json` | 保存"最大 gps_id 查询"的默认过滤时间；插入成功后自动更新为最新插入时间 |

所有脚本运行时**必须设置 `dangerouslyDisableSandbox: true`**：需要执行 D:\soft 下的 exe、在用户桌面创建控制台窗口、访问网络连接阿里云 Lindorm 端点。**所有 ps1 必须保持 UTF-8 with BOM 编码**（Windows PowerShell 5.1 中文兼容），重新生成文件后需补 BOM。

## 一、启动 CLI 并连接（connect.ps1）

```powershell
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\connect.ps1"
```

行为：
1. 用 lindorm-cli 原生参数直连（`-url -username -password -database gpsdb`），窗口打开即为已连接的交互会话；
2. 自动向窗口输入并依次执行：`show databases;` → `use gpsdb;` → `show tables;`
3. 脚本输出 `OK: ...` 即成功；`ERROR: ...` 按下方排错表处理。

兜底模式（仅当主方式异常时使用：先开空窗口，再模拟键盘输入 connect 命令，之后同样执行三条命令）：

```powershell
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\connect.ps1" -Fallback
```

已知限制：若用户默认终端是 Windows Terminal，窗口按键自动发送可能失败（脚本会提示手动执行）。

## 二、查询车辆轨迹（query-gps.ps1）

SQL 模板（时间区间与车牌号为动态参数）：

```sql
SELECT x.* FROM sys_gps x WHERE time >= '<开始时间>' and time <= '<结束时间>' and license_plate_number = '<车牌号>';
```

调用示例：

```powershell
# 默认参数：最近 10 分钟 + 渝D94049
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\query-gps.ps1"

# 指定时间区间与车牌
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\query-gps.ps1" -Plate '渝D94049' -Start '2026-05-26 19:21:03' -End '2026-05-26 19:22:05'

# 最近 30 分钟，json 美化输出
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\query-gps.ps1" -Minutes 30 -Format json -Pretty
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-Plate` | 渝D94049 | 车牌号 |
| `-Start` / `-End` | 最近 10 分钟 | 时间区间，格式 `yyyy-MM-dd HH:mm:ss` |
| `-Minutes` | 10 | 未给 `-Start` 时可用：最近 N 分钟 |
| `-Format` | table | 结果格式：json / csv / table / column / vertical / horizontal |
| `-Pretty` | 关闭 | json 格式美化输出 |

结果直接打印到控制台，agent 读取后转述给用户。

## 三、查询当前最大 gps_id（get-max-gps-id.ps1）

```powershell
# 默认：使用 state.json 中的默认过滤时间（初始 '2026-09-24 19:27:41'，插入数据后自动更新）
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\get-max-gps-id.ps1"

# 指定过滤时间
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\get-max-gps-id.ps1" -Time '2026-05-26 00:00:00'
```

执行的 SQL：

```sql
SELECT gps_id FROM sys_gps WHERE time >= '<默认时间>' ORDER BY gps_id DESC LIMIT 1;
```

默认时间规则：初始 `'2026-09-24 19:27:41'`；**每当 insert-gps.ps1 插入数据成功，自动更新为本次最新插入的时间**（存于 state.json 的 `max_id_query_time` 字段）。

## 四、插入车辆轨迹测试数据（insert-gps.ps1）

生成规则：

| 项 | 规则 |
|---|---|
| time | `-Start/-End` 给区间，**区间包含首尾**（第1点=Start、第20点=End），中间**均分 18 个时间点**，共 20 点插入 20 条；默认区间 = 最近 20 秒；**区间不足 19 秒时**按 1 秒间隔、包含首尾，**有几秒就插入几条**（条数 = 整秒数 + 1，可能少于 20 条） |
| gps_id | 自动取"当前最大 gps_id + 1"起追加（查询用 state.json 默认时间过滤；可用 `-StartId` 手动指定） |
| license_plate_number | 默认 `渝D94049`，`-Plate` 动态指定 |
| 坐标 | 默认北京范围 (116.10, 39.85) → (116.70, 40.05) 线性插值；**数据库存值 = 真实经纬度 × 600000**（即 真实值 = 库值 ÷ 600000）；可传 `-LngFrom/-LatFrom/-LngTo/-LatTo` |
| 其他字段 | mileage 从 92346.3 起每条 +0.1；speed 35~55 波动；angle 为行进方向角；altitude 40~44；dele_flag 0 |
| state.json | 插入成功后默认过滤时间自动更新为本次最新插入时间（下次查最大 id / 插入即基于新时间） |

SQL 与用户示例同构（多行 VALUES 一次插入；失败自动回退逐条插入）：

```sql
INSERT INTO sys_gps (gps_id, license_plate_number, time, longitude, latitude, mileage, speed, angle, altitude, dele_flag)
VALUES ('5056182257686298815', '渝D94049', '2026-09-24 19:27:41', CAST('69660000' AS BIGINT), CAST('23910000' AS BIGINT), CAST('92346.3' AS DOUBLE), CAST('45' AS INT), CAST('66' AS INT), CAST('40' AS INT), CAST('0' AS INT)), ...;
```

调用示例：

```powershell
# 默认：最近20秒区间（1秒×20点）、渝D94049、北京坐标，自动续接最大 gps_id
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\insert-gps.ps1"

# 指定区间与车牌
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\insert-gps.ps1" -Plate '京A12345' -Start '2026-09-24 14:00:00' -End '2026-09-24 14:10:00'

# 仅打印 SQL 不执行（不插数据、不更新 state.json）
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\insert-gps.ps1" -DryRun

# 手动指定起始 gps_id 与起终点经纬度
powershell -ExecutionPolicy Bypass -File "<本技能所在目录>\insert-gps.ps1" -StartId 5056182257686298813 -LngFrom 116.3 -LatFrom 39.9 -LngTo 116.5 -LatTo 40.0
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-Plate` | 渝D94049 | 车牌号 |
| `-Start` / `-End` | 最近 20 秒 | 时间区间，格式 `yyyy-MM-dd HH:mm:ss`；区间过短（<19 秒）自动按 1 秒间隔 |
| `-LngFrom/-LatFrom` | 116.10 / 39.85 | 起点真实经纬度（北京范围） |
| `-LngTo/-LatTo` | 116.70 / 40.05 | 终点真实经纬度 |
| `-StartId` | 自动 | 不自动查最大 id，直接指定起始 gps_id |
| `-DryRun` | 关闭 | 仅打印 SQL，不执行 |

成功输出 `OK: 已插入 20 条（gps_id A ~ B），时间 T1 ~ T2 ...`，并同步更新 state.json。

## 五、自定义任意 SQL（非交互，不开窗口）

```powershell
& 'D:\soft\lindorm-cli.exe' -url '<同下URL>' -username root -password '<见脚本顶部>' -database gpsdb -execute '<SQL>'
```

支持 `-format json|csv|table`、`-pretty`、`-output <文件>` 导出，完整参数见 `lindorm-cli --help`。表结构速查（describe sys_gps）：gps_id BIGINT、license_plate_number VARCHAR(TAG)、time TIMESTAMP、longitude/latitude/mileage/speed/angle/altitude/dele_flag DOUBLE。

## 连接信息与维护

| 项 | 值 |
|---|---|
| URL | jdbc:lindorm:tsdb:url=http://ld-8vb432g58h0em96sw-proxy-tsdb-vpc.lindorm.aliyuncs.com:8242 |
| 用户名 / 密码 | root / 明文保存在各 ps1 顶部配置区（勿将本目录提交到公开仓库） |
| 库 / 表 | gpsdb / sys_gps |
| state.json | `max_id_query_time`：最大 gps_id 查询的默认过滤时间（插入成功后自动更新） |

修改连接信息：编辑各脚本顶部的配置变量。

## 验证与排错

| 现象 | 处理 |
|---|---|
| `ERROR: 找不到 ...lindorm-cli.exe` | exe 路径已变动，修改脚本顶部 `$CliPath` |
| `ERROR: 进程已退出` / 连接报错 | URL/账号/密码错误或网络不通（VPC 地址需内网环境），检查脚本顶部配置 |
| 后续命令按键未生效（connect.ps1） | Windows Terminal 承载时已知限制，手动在窗口输入；或调大脚本内 `Start-Sleep` 重试 |
| 脚本中文乱码或解析报错 | 文件缺 UTF-8 BOM，补 BOM 后重试 |
| 查最大 gps_id 返回空 | 该时间后无数据；用 `-Time` 指定更早时间，或插入时用 `-StartId` |
| 插入失败 | 脚本自动回退逐条插入；仍失败则检查 SQL 输出中的报错（字段类型见上文表结构） |
| 查询/插入返回空或行数不对 | 确认时间区间、车牌号；刚插入的数据可用 query-gps.ps1 按插入时输出的 T1~T2 复查 |
