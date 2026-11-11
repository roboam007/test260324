---
name: lindorm-cli-connect
description: "macOS：通过 Lindorm TSDB HTTP SQL API 连接 gpsdb，按时间/车牌查询车辆 GPS 轨迹、查询最大 gps_id、插入 20 点轨迹测试数据。Invoke for Lindorm connect/query/insert tasks."
---

# Lindorm 连接、轨迹查询与测试数据插入（macOS）

本技能目录下包含：

| 文件 | 作用 |
|---|---|
| `lindorm-cli.py` | **macOS 使用**；统一 CLI，子命令 `connect` / `query` / `max-id` / `insert` / `sql` |
| `state.json` | 保存"最大 gps_id 查询"的默认过滤时间；插入成功后自动更新 |
| `connect.ps1` / `query-gps.ps1` / `get-max-gps-id.ps1` / `insert-gps.ps1` | Windows 旧版脚本（依赖 `lindorm-cli.exe` 与 PowerShell），macOS 下不使用，保留备用 |

运行环境：macOS 自带 `python3`（仅用标准库，无第三方依赖），**不需要** `lindorm-cli.exe`、PowerShell 或控制台窗口。

访问方式：Lindorm TSDB 的 HTTP SQL API —— `POST http://<host>:8242/api/v2/sql`，Basic Auth，请求体为**原始 SQL 文本**，返回 JSON `{columns, metadata, rows}`。HTTP 接口无会话状态，因此 SQL 中统一使用全限定表名 `gpsdb.sys_gps`（等价于旧版脚本的 `use gpsdb`）。

示例统一约定：

```bash
SKILL="$HOME/work/skills/lindorm-cli-connect"
```

## 一、连接检查（connect）

```bash
python3 "$SKILL/lindorm-cli.py" connect
```

行为：执行 `show databases;` 与 `show tables from gpsdb;`，输出：

```
OK: 已连接 http://...:8242/api/v2/sql（HTTP SQL API）
OK: databases: ...
OK: gpsdb tables: ...
```

## 二、查询车辆轨迹（query）

SQL 模板（时间区间与车牌号为动态参数）：

```sql
SELECT x.* FROM gpsdb.sys_gps x WHERE time >= '<开始时间>' and time <= '<结束时间>' and license_plate_number = '<车牌号>';
```

调用示例：

```bash
# 默认参数：最近 10 分钟 + 渝D94049
python3 "$SKILL/lindorm-cli.py" query

# 指定时间区间与车牌
python3 "$SKILL/lindorm-cli.py" query -Plate '甘J86573' -Start '2026-10-30 16:00:56' -End '2026-10-30 16:09:26'

# 最近 30 分钟，json 美化输出
python3 "$SKILL/lindorm-cli.py" query -Minutes 30 -Format json -Pretty
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `-Plate` | 渝D94049 | 车牌号 |
| `-Start` / `-End` | 最近 10 分钟 | 时间区间，格式 `yyyy-MM-dd HH:mm:ss`，需同时提供 |
| `-Minutes` | 10 | 未给 `-Start` 时可用：最近 N 分钟 |
| `-Format` | table | 结果格式：table / json / csv / vertical |
| `-Pretty` | 关闭 | json 格式美化输出 |

说明：库中 `time` 以毫秒时间戳返回，脚本会按**本机时区**格式化为 `yyyy-MM-dd HH:mm:ss`；返回的内部列（如 `__taglist__`）会自动过滤。结果直接打印到控制台，agent 读取后转述给用户。

## 三、查询当前最大 gps_id（max-id）

```bash
# 默认：使用 state.json 中的默认过滤时间（初始 '2026-09-24 19:27:41'，插入数据后自动更新）
python3 "$SKILL/lindorm-cli.py" max-id

# 指定过滤时间
python3 "$SKILL/lindorm-cli.py" max-id -Time '2026-05-26 00:00:00'
```

执行的 SQL：

```sql
SELECT gps_id FROM gpsdb.sys_gps WHERE time >= '<默认时间>' ORDER BY gps_id DESC LIMIT 1;
```

默认时间规则：初始 `'2026-09-24 19:27:41'`；**每当 insert 插入数据成功，自动更新为本次最新插入的时间**（存于 state.json 的 `max_id_query_time` 字段）。该时间过滤可避免全表扫描（全表 `ORDER BY gps_id DESC` 很慢，可能超时）。

## 四、插入车辆轨迹测试数据（insert）

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
INSERT INTO gpsdb.sys_gps (gps_id, license_plate_number, time, longitude, latitude, mileage, speed, angle, altitude, dele_flag)
VALUES ('***', '渝D94049', '2026-09-24 19:27:41', CAST('69660000' AS BIGINT), CAST('23910000' AS BIGINT), CAST('92346.3' AS DOUBLE), CAST('45' AS INT), CAST('66' AS INT), CAST('40' AS INT), CAST('0' AS INT)), ...;
```

调用示例：

```bash
# 默认：最近20秒区间（1秒×20点）、渝D94049、北京坐标，自动续接最大 gps_id
python3 "$SKILL/lindorm-cli.py" insert

# 指定区间与车牌
python3 "$SKILL/lindorm-cli.py" insert -Plate '甘J86573' -Start '2026-10-30 16:00:56' -End '2026-10-30 16:09:26'

# 仅打印 SQL 不执行（不插数据、不更新 state.json）
python3 "$SKILL/lindorm-cli.py" insert -DryRun

# 手动指定起始 gps_id 与起终点经纬度
python3 "$SKILL/lindorm-cli.py" insert -StartId 1000001 -LngFrom 116.3 -LatFrom 39.9 -LngTo 116.5 -LatTo 40.0
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

## 五、执行任意 SQL（sql）

```bash
python3 "$SKILL/lindorm-cli.py" sql "show tables from gpsdb"
python3 "$SKILL/lindorm-cli.py" sql "SELECT * FROM gpsdb.sys_gps WHERE license_plate_number = '甘J86573' AND time >= '2026-10-30 16:00:56' AND time <= '2026-10-30 16:09:26';" -Format json -Pretty
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `statement` | 必填 | 要执行的 SQL（无需结尾分号） |
| `-Format` | table | table / json / csv / vertical |
| `-Timeout` | 120 | 请求超时秒数 |

表结构速查（`describe gpsdb.sys_gps`）：`gps_id` BIGINT、`license_plate_number` VARCHAR(TAG)、`time` TIMESTAMP、`longitude/latitude/mileage/speed/angle/altitude/dele_flag` DOUBLE。

## 连接信息与维护

| 项 | 值 |
|---|---|
| URL | `http://ld-8vb432g58h0em96sw-proxy-tsdb-vpc.lindorm.aliyuncs.com:8242/api/v2/sql` |
| 用户名 / 密码 | root / 明文保存在 `lindorm-cli.py` 顶部配置区（勿将本目录提交到公开仓库） |
| 库 / 表 | gpsdb / sys_gps |
| state.json | `max_id_query_time`：最大 gps_id 查询的默认过滤时间（插入成功后自动更新） |
| 依赖 | macOS 自带 python3（3.8+），仅标准库 |

修改连接信息：编辑 `lindorm-cli.py` 顶部的 `HOST / PORT / USERNAME / PASSWORD / DATABASE / TABLE`。

## 验证与排错

| 现象 | 处理 |
|---|---|
| `ERROR: 连接失败` | 网络不通或端点变更（VPC 地址需内网/VPN）；确认 `nc -z <host> 8242` 可通 |
| `ERROR: SQL 执行失败 [...]` | 看 message：语法/字段类型/表名问题（HTTP API 无会话，须写全限定表名 `gpsdb.sys_gps`） |
| `zsh: command not found: python3` | 安装命令行工具：`xcode-select --install` |
| 查最大 gps_id 返回「无数据」 | 该时间后无数据；用 `-Time` 指定更早时间，或插入时用 `-StartId` |
| 插入失败 | 脚本自动回退逐条插入；仍失败则检查报错中的 SQL 片段与字段类型 |
| 查询/插入返回空或行数不对 | 确认时间区间、车牌号；刚插入的数据可用 query 按插入时输出的 T1~T2 复查 |
| 时间显示与预期相差 8 小时 | 库内时间按东八区解释，输出按本机时区格式化；跨时区机器需注意 |
| agent 沙盒内报网络错误 | 该技能需要访问 Lindorm 端点，可将命令改为非沙盒（dangerouslyDisableSandbox: true）执行 |
