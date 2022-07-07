#!/usr/bin/env python3

from .agent_based_api.v1 import *
from pprint import pprint
from random import randint

def parse_sentry4_pdu_outlet(string_table):
    parsed = {'Outlet':'Outlet'}
    pprint(string_table)
    return parsed

register.snmp_section(
    name='sentry4_pdu_outlet',
    detect=exists('.1.3.6.1.4.1.1718.4.1.1.1.1.0'),
    fetch=SNMPTree(
        base='.1.3.6.1.4.1.1718.4.1.8', # Sentry4-MIB::st4OutletConfigTable
        oids=[
            '2.1.3', # Sentry4-MIB::st4OutletName
            '3.1.2', # Sentry4-MIB::st4OutletStatus
        ],
    ),
    parse_function=parse_sentry4_pdu_outlet,
)

def discover_sentry4_pdu_outlet(section):
    for service in section.keys():
        yield Service(item=service)

def check_sentry4_pdu_outlet(item, section):
    if item not in section:
        return

    yield Metric('test', randint(1, 100))

    summary = 'Outlet Summary'
    yield Result(state=State.OK, summary=summary)


register.check_plugin(
    name='sentry4_pdu_outlet',
    service_name='%s',
    discovery_function=discover_sentry4_pdu_outlet,
    check_function=check_sentry4_pdu_outlet,
)