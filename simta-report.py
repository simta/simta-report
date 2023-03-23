#!/usr/bin/env python3

import sys

import requests


hosts = [
    'influxdb.us-east-2.a.mail.umich.edu',
    'influxdb.us-west-2.a.mail.umich.edu',
]

report_class = 'mx'
if len(sys.argv) > 1:
    report_class = sys.argv[1]


def metric_query(metric, base='simta'):
    if not metric.startswith('/'):
        metric = f'"{metric}"'

    params = {
        'db': 'sensu',
        'q': f'SELECT sum({metric}) FROM "{base}" WHERE time > now() - 7d GROUP BY time(1d), "class" fill(0)'
    }

    totals = {}

    for h in hosts:
        res = requests.get(
            f'http://{h}:8086/query',
            timeout=10,
            params=params,
        )

        for r in res.json()['results']:
            for s in r.get('series', {}):
                cls = s['tags']['class']
                if cls not in totals:
                    totals[cls] = {}
                for v in s['values']:
                    for i in range(1, len(v)):
                        col = s['columns'][i]
                        val = v[i]
                        if col not in totals[cls]:
                            totals[cls][col] = 0
                        totals[cls][col] += val

    return totals


def get_sum(metric):
    res = metric_query(metric)
    return res.get(report_class, {'sum': 0})['sum']


def print_col(name, val):
    print(f'{name:<22}{val}')


def f_perc(value, total):
    return f'{value:>11,} ({value / total * 100:.1f}%)'


conn_total = get_sum('receive.connection.attempted.value')
conn_accepted = get_sum('receive.connection.accepted.value')
print_col('Connections Accepted:', f'{conn_accepted:>11,} ({conn_accepted / conn_total * 100:.1f}%) of {conn_total:,} attempted')

msg_total = get_sum('receive.smtp_command.MAIL.count')
msg_accepted = get_sum('receive.message.accepted.value')

print_col('Messages Accepted:', f'{msg_accepted:>11,} ({msg_accepted / msg_total * 100:.1f}%) of {msg_total:,} attempted')

bounces = get_sum('bounce.messages.value')
if bounces > 0:
    print_col('Messages Bounced:', f'{bounces:>11,}')

conn_banner_write = get_sum('receive.connection.write_before_banner.value')
conn_3strikes = get_sum('receive.connection.max_failed_rcpt.value') + get_sum('receive.connection.max_failed_sender.value')
bad_auth = get_sum('receive.connection.honeypot_auth.value')
punished = conn_banner_write + conn_3strikes + bad_auth
if punished > 0:
    print()
    print('Punishment Detail:')
    print_col('Total', f'{punished:>11,}')
    if conn_banner_write > 0:
        print_col('write before banner:', f_perc(conn_banner_write, punished))
    if conn_3strikes > 0:
        print_col('three strikes:', f_perc(conn_3strikes, punished))
    if bad_auth > 0:
        print_col('fake auth:', f_perc(bad_auth, punished))


rdns_total = 0
rdns = metric_query('/receive\.rdns\..+\.value/').get(report_class, {})
for k, v in rdns.items():
    rdns_total += v
print()
print('Reverse DNS Detail:')
for k, v in rdns.items():
    print_col(k.split('.')[-2] + ':', f_perc(v, rdns_total))


raw_acls = metric_query('/acl\..+\.value/').get(report_class, {})
acls = {}
for k, v in raw_acls.items():
    action = k.split('.')[2]
    name = k.split('.')[1]
    if name.startswith('_'):
        name = name.replace('_', '/')
    else:
        name = name.replace('_', '.')
    if action not in acls:
        acls[action] = {'total': 0}
    acls[action][name] = v
    acls[action]['total'] += v

for k, v in acls.items():
    total = v.pop('total')
    if total == 0:
        continue
    print()
    print(f'ACL {k.title()} Detail:')
    print_col('Total:', f'{total:>11,}')
    for k, v in v.items():
        if v > 0:
            print_col(k + ':', f_perc(v, total))

scanned_total = get_sum('receive.content_filter.count')
raw_filters = metric_query('/.+\.value/', 'mscan').get(report_class, {})
filters = {}
for k, v in raw_filters.items():
    action = k.split('.')[0][4:]
    name = k.split('.')[1]
    if action not in filters:
        filters[action] = {'total': 0}
    filters[action][name] = v
    filters[action]['total'] += v

for k, v in filters.items():
    total = v.pop('total')
    if total == 0:
        continue
    print()
    print(f'Filter {k.title()} Detail:')
    print_col('Total', f'{total:>11,} ({total / scanned_total * 100:.1f}%) of {scanned_total:,} scanned')
    for fk, fv in v.items():
        if fv > 0:
            print_col(fk, f_perc(fv, total))
