#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lindorm TSDB（gpsdb / sys_gps）连接、轨迹查询与测试数据插入 —— macOS 版

通过 Lindorm HTTP SQL API（POST /api/v2/sql，Basic Auth，body 为原始 SQL）访问，
无需 lindorm-cli.exe、PowerShell 或控制台窗口，仅依赖 Python 3 标准库。

子命令：
  connect   连通性检查（show databases / show tables from gpsdb）
  query     按时间区间 + 车牌查询车辆轨迹
  max-id    查询当前最大 gps_id（默认过滤时间见 state.json）
  insert    插入 20 点轨迹测试数据（区间包含首尾、中间均分）
  sql       执行任意 SQL
"""

import argparse
import base64
import csv
import io
import json
import math
import os
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timedelta

# ========== 连接配置 ==========
HOST = 'ld-8vb432g58h0em96sw-proxy-tsdb-vpc.lindorm.aliyuncs.com'
PORT = 8242
USERNAME = 'root'
PASSWORD = '__PASSWORD__'
DATABASE = 'gpsdb'
TABLE = 'sys_gps'
# =============================

URL = f'http://{HOST}:{PORT}/api/v2/sql'
QUALIFIED_TABLE = f'{DATABASE}.{TABLE}'
AUTH = 'Basic ' + base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode('utf-8')).decode('ascii')

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SKILL_DIR, 'state.json')
DEFAULT_STATE_TIME = '2026-09-24 19:27:41'
TIME_FMT = '%Y-%m-%d %H:%M:%S'

POINTS = 20
MILEAGE_BASE = 92346.3


# ---------- 通用 ----------
def run_sql(sql, timeout=120):
    """执行 SQL，返回 {columns, metadata, rows}；失败直接退出并打印服务端报错"""
    req = urllib.request.Request(URL, data=sql.encode('utf-8'), method='POST')
    req.add_header('Authorization', AUTH)
    req.add_header('Content-Type', 'text/plain; charset=utf-8')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        raise SystemExit(f'ERROR: HTTP {e.code}：{body}')
    except urllib.error.URLError as e:
        raise SystemExit(f'ERROR: 连接失败（{URL}）：{e.reason}')
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise SystemExit(f'ERROR: 返回内容无法解析：{body[:500]}')
    if data.get('code') not in (None, 0):
        msg = data.get('message', '')
        raise SystemExit(f"ERROR: SQL 执行失败 [{data['code']}] {msg}")
    return data


def parse_time(text):
    try:
        return datetime.strptime(text, TIME_FMT)
    except ValueError:
        raise SystemExit(f"ERROR: 无法解析时间 '{text}'，格式应为 {TIME_FMT}")


def load_state_time():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding='utf-8-sig') as f:
                return json.load(f).get('max_id_query_time') or DEFAULT_STATE_TIME
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_STATE_TIME


def save_state_time(value):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'max_id_query_time': value}, f, ensure_ascii=False, indent=4)
        f.write('\n')


def cell_text(column, value):
    """TIMESTAMP 字段返回毫秒时间戳，统一转成本地时间字符串"""
    if column.lower() == 'time' and isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000).strftime(TIME_FMT)
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return '' if value is None else str(value)


def display_width(text):
    """终端显示宽度：中文等全角字符按 2 列计算"""
    return sum(2 if unicodedata.east_asian_width(ch) in 'WF' else 1 for ch in text)


def pad(text, width):
    return text + ' ' * max(width - display_width(text), 0)


def print_result(data, fmt='table', pretty=False):
    # 过滤 Lindorm 返回的内部列（如 __taglist__）
    raw_columns = data.get('columns') or []
    keep = [i for i, c in enumerate(raw_columns) if not c.startswith('__')]
    columns = [raw_columns[i] for i in keep]
    rows = [[cell_text(c, row[i]) for c, i in zip(columns, keep)] for row in (data.get('rows') or [])]

    if fmt == 'json':
        payload = [dict(zip(columns, row)) for row in rows]
        print(json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None))
        return

    if not rows:
        print('（无数据）')
        return

    if fmt == 'csv':
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator='\n')
        writer.writerow(columns)
        writer.writerows(rows)
        print(buf.getvalue(), end='')
    elif fmt == 'vertical':
        for i, row in enumerate(rows):
            if i:
                print()
            for c, v in zip(columns, row):
                print(f'{c}: {v}')
    else:  # table
        widths = [max([display_width(c)] + [display_width(r[i]) for r in rows]) for i, c in enumerate(columns)]
        print('  '.join(pad(c, w) for c, w in zip(columns, widths)).rstrip())
        print('  '.join('-' * w for w in widths))
        for row in rows:
            print('  '.join(pad(v, w) for v, w in zip(row, widths)).rstrip())


# ---------- 子命令 ----------
def cmd_connect(args):
    dbs = run_sql('show databases;')
    names = [r[0] for r in (dbs.get('rows') or [])]
    print(f'OK: 已连接 {URL}（HTTP SQL API）')
    print(f'OK: databases: {", ".join(names)}')
    if DATABASE not in names:
        raise SystemExit(f'ERROR: 未找到数据库 {DATABASE}')
    tables = run_sql(f'show tables from {DATABASE};')
    tnames = [r[0] for r in (tables.get('rows') or [])]
    print(f'OK: {DATABASE} tables: {", ".join(tnames)}')


def build_query_sql(plate, start, end):
    return (f"SELECT x.* FROM {QUALIFIED_TABLE} x WHERE time >= '{start}' AND time <= '{end}' "
            f"AND license_plate_number = '{plate}';")


def cmd_query(args):
    if args.start or args.end:
        if not (args.start and args.end):
            raise SystemExit('ERROR: -Start 与 -End 需同时提供')
        start, end = parse_time(args.start), parse_time(args.end)
    else:
        end = datetime.now()
        start = end - timedelta(minutes=args.minutes)
    if start > end:
        raise SystemExit('ERROR: 开始时间不能晚于结束时间')
    sql = build_query_sql(args.plate, start.strftime(TIME_FMT), end.strftime(TIME_FMT))
    data = run_sql(sql)
    print_result(data, args.format, args.pretty)


def query_max_id(time_filter, timeout=120):
    sql = f'SELECT gps_id FROM {QUALIFIED_TABLE} WHERE time >= \'{time_filter}\' ORDER BY gps_id DESC LIMIT 1;'
    rows = run_sql(sql, timeout=timeout).get('rows') or []
    return int(rows[0][0]) if rows else None


def cmd_max_id(args):
    time_filter = args.time or load_state_time()
    max_id = query_max_id(time_filter)
    if max_id is None:
        print(f'（time >= {time_filter} 无数据；可用 -Time 指定更早时间）')
        return
    print(max_id)


def build_insert(args):
    """按 skill 规则生成 20 个时间点与插入 SQL，返回 (sql, values, times, start_id)"""
    end = parse_time(args.end) if args.end else datetime.now()
    start = parse_time(args.start) if args.start else end - timedelta(seconds=POINTS - 1)
    if start > end:
        raise SystemExit('ERROR: 开始时间不能晚于结束时间')

    total_sec = (end - start).total_seconds()
    if total_sec >= POINTS - 1:
        step = total_sec / (POINTS - 1)
        times = [(start + timedelta(seconds=step * i)).strftime(TIME_FMT) for i in range(POINTS)]
        times[-1] = end.strftime(TIME_FMT)  # 消除浮点误差，尾点精确等于 End
    else:
        count = max(int(math.floor(total_sec)) + 1, 1)
        print(f'WARN: 区间仅 {total_sec} 秒，按 1 秒间隔、包含首尾，本次插入 {count} 条（不足 20 条）。')
        times = [(start + timedelta(seconds=i)).strftime(TIME_FMT) for i in range(count)]

    if args.start_id is not None:
        start_id = args.start_id
    else:
        max_id = query_max_id(load_state_time())
        if max_id is None:
            print('  按时间未查到记录，回退查询全表最大 gps_id ...')
            max_id = query_max_id('1970-01-01 00:00:00', timeout=300)
        if max_id is None:
            raise SystemExit('ERROR: 未查到任何已有 gps_id，请用 -StartId 指定起始 ID')
        start_id = max_id + 1
        print(f'  当前最大 gps_id = {max_id}，本次从 {start_id} 开始追加')

    mid_lat = (args.lat_from + args.lat_to) / 2
    dx = (args.lng_to - args.lng_from) * math.cos(mid_lat * math.pi / 180)
    dy = args.lat_to - args.lat_from
    angle = int(round((math.atan2(dx, dy) * 180 / math.pi + 360) % 360))

    columns = 'gps_id, license_plate_number, time, longitude, latitude, mileage, speed, angle, altitude, dele_flag'
    denominator = max(len(times) - 1, 1)
    values = []
    for i, t in enumerate(times):
        ratio = i / denominator
        db_lng = int(round((args.lng_from + (args.lng_to - args.lng_from) * ratio) * 600000))
        db_lat = int(round((args.lat_from + (args.lat_to - args.lat_from) * ratio) * 600000))
        speed = int(round(45 + 10 * math.sin(i * 0.5)))
        altitude = 40 + i % 5
        mileage = round(MILEAGE_BASE + i * 0.1, 1)
        values.append(
            f"('{start_id + i}', '{args.plate}', '{t}', CAST('{db_lng}' AS BIGINT), "
            f"CAST('{db_lat}' AS BIGINT), CAST('{mileage}' AS DOUBLE), CAST('{speed}' AS INT), "
            f"CAST('{angle}' AS INT), CAST('{altitude}' AS INT), CAST('0' AS INT))"
        )
    sql = f'INSERT INTO {QUALIFIED_TABLE} ({columns}) VALUES ' + ', '.join(values) + ';'
    return sql, columns, values, times, start_id


def cmd_insert(args):
    sql, columns, values, times, start_id = build_insert(args)
    print(f'SQL（{len(values)} 行）:')
    print(sql)

    if args.dry_run:
        print('\nDRYRUN: 仅打印 SQL，未执行，state.json 未更新。')
        return

    print('\n插入中...')
    try:
        data = run_sql(sql, timeout=180)
        affected = (data.get('rows') or [[0]])[0][0]
        print(f'  批量插入完成，服务端返回 updated={affected}')
    except SystemExit as e:
        print(f'多行 VALUES 方式失败，回退逐条插入...\n{e}')
        for idx, value in enumerate(values):
            try:
                run_sql(f'INSERT INTO {QUALIFIED_TABLE} ({columns}) VALUES {value};')
            except SystemExit as one_err:
                raise SystemExit(f'ERROR: 逐条插入失败于第 {idx + 1} 条: {value}\n{one_err}')

    last_time = times[-1]
    save_state_time(last_time)
    print(f'\nOK: 已插入 {len(values)} 条（gps_id {start_id} ~ {start_id + len(values) - 1}），'
          f'时间 {times[0]} ~ {last_time}，车牌 {args.plate}。')
    print(f'state.json 默认查询时间已更新为 {last_time}')


def cmd_sql(args):
    print_result(run_sql(args.statement, timeout=args.timeout), args.format, args.pretty)


# ---------- 入口 ----------
def main():
    parser = argparse.ArgumentParser(
        prog='lindorm-cli.py',
        description='Lindorm TSDB（gpsdb.sys_gps）连接、轨迹查询与测试数据插入（macOS）',
    )
    sub = parser.add_subparsers(dest='command', required=True)

    sub.add_parser('connect', help='连通性检查（show databases / show tables）').set_defaults(func=cmd_connect)

    p_query = sub.add_parser('query', help='按时间区间 + 车牌查询车辆轨迹')
    p_query.add_argument('-Plate', '--plate', default='渝D94049', help='车牌号，默认 渝D94049')
    p_query.add_argument('-Start', '--start', default='', help='开始时间 yyyy-MM-dd HH:mm:ss')
    p_query.add_argument('-End', '--end', default='', help='结束时间 yyyy-MM-dd HH:mm:ss')
    p_query.add_argument('-Minutes', '--minutes', type=int, default=10, help='未给 -Start 时：最近 N 分钟，默认 10')
    p_query.add_argument('-Format', '--format', choices=['table', 'json', 'csv', 'vertical'], default='table')
    p_query.add_argument('-Pretty', '--pretty', action='store_true', help='json 美化输出')
    p_query.set_defaults(func=cmd_query)

    p_max = sub.add_parser('max-id', help='查询当前最大 gps_id')
    p_max.add_argument('-Time', '--time', default='', help=f'过滤时间，默认取 state.json（初始 {DEFAULT_STATE_TIME}）')
    p_max.set_defaults(func=cmd_max_id)

    p_ins = sub.add_parser('insert', help='插入 20 点轨迹测试数据')
    p_ins.add_argument('-Plate', '--plate', default='渝D94049', help='车牌号，默认 渝D94049')
    p_ins.add_argument('-Start', '--start', default='', help='开始时间 yyyy-MM-dd HH:mm:ss，默认最近 20 秒')
    p_ins.add_argument('-End', '--end', default='', help='结束时间 yyyy-MM-dd HH:mm:ss，默认当前时间')
    p_ins.add_argument('-LngFrom', '--lng-from', type=float, default=116.10, help='起点经度（真实值），默认 116.10')
    p_ins.add_argument('-LatFrom', '--lat-from', type=float, default=39.85, help='起点纬度（真实值），默认 39.85')
    p_ins.add_argument('-LngTo', '--lng-to', type=float, default=116.70, help='终点经度（真实值），默认 116.70')
    p_ins.add_argument('-LatTo', '--lat-to', type=float, default=40.05, help='终点纬度（真实值），默认 40.05')
    p_ins.add_argument('-StartId', '--start-id', type=int, default=None, help='手动指定起始 gps_id')
    p_ins.add_argument('-DryRun', '--dry-run', action='store_true', help='仅打印 SQL，不执行、不更新 state.json')
    p_ins.set_defaults(func=cmd_insert)

    p_sql = sub.add_parser('sql', help='执行任意 SQL')
    p_sql.add_argument('statement', help='SQL 语句，例如 "show tables from gpsdb"')
    p_sql.add_argument('-Format', '--format', choices=['table', 'json', 'csv', 'vertical'], default='table')
    p_sql.add_argument('-Pretty', '--pretty', action='store_true')
    p_sql.add_argument('-Timeout', '--timeout', type=int, default=120, help='超时秒数，默认 120')
    p_sql.set_defaults(func=cmd_sql)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    if sys.version_info < (3, 8):
        raise SystemExit('ERROR: 需要 Python 3.8+')
    main()
