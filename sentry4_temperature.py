#!/usr/bin/env python3

from curses import termattrs
from re import I
from .agent_based_api.v1 import *
from pprint import pprint
from random import randint

def parse_sentry4_temperature(string_table):

    parsed = {}

    for (scale, \
         sensor_id, \
         name, \
         value, \
         status, \
         low_alarm, \
         low_warn, \
         high_warn, \
         high_alarm) in string_table:

        if scale != '':
            continue
        if int(value) == -410:
            # No sensor connected
            continue
        else:
            item = 'Temperature ' + sensor_id + ' ' + name
            parsed[item] = {}
            parsed[item]['Value'] = float(int(value)/10)
            parsed[item]['Status'] = int(status)
            parsed[item]['LowAlarm'] = int(low_alarm)
            parsed[item]['LowWarning'] = int(low_warn)
            parsed[item]['HighWarning'] = int(high_warn)
            parsed[item]['HighAlarm'] = int(high_alarm)

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
            '4.1.2', # Sentry4-MIB::st4TempSensorLowAlarm
            '4.1.3', # Sentry4-MIB::st4TempSensorLowWarning
            '4.1.4', # Sentry4-MIB::st4TempSensorHighWarning
            '4.1.5', # Sentry4-MIB::st4TempSensorHighAlarm
        ],
    ),
    parse_function=parse_sentry4_temperature,
)

def discover_sentry4_temperature(section):
    for service in section.keys():
        yield Service(item=service)

def check_sentry4_temperature(item, params, section):
    if item not in section:
        return

    low_alarm = 0.0
    low_warning = 0.0
    high_warning = 0.0
    high_alarm = 0.0

    if params == {}:
        low_alarm = float(section[item]['LowAlarm'])
        low_warning = float(section[item]['LowWarning'])
        high_warning = float(section[item]['HighWarning'])
        high_alarm = float(section[item]['HighWarning'])
    else:
        low_alarm = params['levels_lower'][1]
        low_warning = params['levels_lower'][0]
        high_warning = params['levels'][0]
        high_alarm = params['levels'][1]

    if section[item]['Status'] == 0:
        temperature = section[item]['Value']
        summary = str(temperature) + ' °C'

        yield Metric('temp', temperature)

        if temperature <= low_warning:
            yield Result(state=State.WARN, summary='Temperature below warning threshold {low_warning}')


        yield Result(state=State.OK, summary='{temperature} ... °C')

    else:
        yield Result(state=State.CRIT, summary='Sensor Error')

register.check_plugin(
    name='sentry4_temperature',
    service_name='%s',
    discovery_function=discover_sentry4_temperature,
    check_function=check_sentry4_temperature,
    check_default_parameters={},
    check_ruleset_name='temperature',
)