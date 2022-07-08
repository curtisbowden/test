#!/usr/bin/env python3

from .agent_based_api.v1 import *
from pprint import pprint
from random import randint

def parse_sentry4_temperature(string_table):

    parsed = {}

    for (scale, sensor_id, name, value, status) in string_table:

        if scale != '':
            print("Scale:" + scale)
        elif scale == '' and value != '' and int(value) == -410:
            # No sensor connected
            continue
        else:
            item = 'Temperature ' + sensor_id + ' ' + name
            parsed[item] = {}
            parsed[item]['Value'] = float(int(value)/10)
            parsed[item]['Status'] = int(status)

    return parsed

register.snmp_section(
    name='sentry4_temperature',
    detect=exists('.1.3.6.1.4.1.1718.4.1.1.1.1.0'),
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.1718.4.1.9', # Sentry4-MIB::st4TemperatureSensors
        oids=[
            '1.10', # Sentry4-MIB::st4TempSensorScale
            '2.1.2', # Sentry4-MIB::st4TempSensorID
            '2.1.3', # Sentry4-MIB::st4TempSensorName
            '3.1.1', # Sentry4-MIB::st4TempSensorValue
            '3.1.2', # Sentry4-MIB::st4TempSensorStatus
        ],
    ),
    parse_function=parse_sentry4_temperature,
)

def discover_sentry4_temperature(section):
    for service in section.keys():
        yield Service(item=service)

def check_sentry4_temperature(item, section):
    if item not in section:
        return

    if section[item]['Status'] == 0:
        summary = str(section[item]['Value']).replace('(',r'\(').replace(')',r'\)')+ ' °C'

        yield Metric('temp', section[item]['Value'])

        yield Result(state=State.OK, summary=summary)

    else:
        yield Result(state=State.CRIT, summary='Sensor Error')

register.check_plugin(
    name='sentry4_temperature',
    service_name='%s',
    discovery_function=discover_sentry4_temperature,
    check_function=check_sentry4_temperature,
)