#!/usr/bin/env python3

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
         low_warning, \
         high_warning, \
         high_alarm) in string_table:

        unit = 'c'

        if scale == '1':
            unit = 'f'
        else:
            if value !='' and int(value) != -410:
                item = 'Temperature ' + sensor_id + ' ' + name
                parsed[item] = {}
                parsed[item]['unit'] = unit
                parsed[item]['value'] = float(int(value)/10)
                parsed[item]['status'] = int(status)
                parsed[item]['low_alarm'] = int(low_alarm)
                parsed[item]['low_warning'] = int(low_warning)
                parsed[item]['high_warning'] = int(high_warning)
                parsed[item]['high_alarm'] = int(high_alarm)

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

    pprint(section[item])

    low_alarm = 0.0
    low_warning = 0.0
    high_warning = 0.0
    high_alarm = 0.0

    if 'levels_lower' in params:
        low_alarm = params['levels_lower'][1]
        low_warning = params['levels_lower'][0]
    else:
        low_alarm = float(section[item]['low_alarm'])
        low_warning = float(section[item]['low_warning'])

    if 'levels' in params:
        high_warning = params['levels'][0]
        high_alarm = params['levels'][1]
    else:
        high_warning = float(section[item]['high_warning'])
        high_alarm = float(section[item]['high_alarm'])


    if section[item]['status'] == 0:
        temperature = section[item]['value']

        yield Metric('temp', temperature, levels=(high_warning, high_alarm))

        if temperature <= low_alarm:
            yield Result(state=State.CRIT, summary=str(temperature) + ' °C is below critical threshold')

        elif temperature >= high_alarm:
            yield Result(state=State.CRIT, summary=str(temperature) + ' °C is above critical threshold')

        elif temperature >= high_warning:
            yield Result(state=State.WARN, summary=str(temperature) + ' °C is above warning threshold')

        elif temperature <= low_warning:
            yield Result(state=State.WARN, summary=str(temperature) + ' °C is below warning threshold')

        else:
            yield Result(state=State.OK, summary=str(temperature) + ' °C')

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