#!/usr/bin/env python3

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import (
    metric_info,
    graph_info,
)

metric_info['test'] = {
    'title': _('test'),
    'unit': 'count',
    'color': '16/a',
}


graph_info['test'] = {
    'metrics': [
        ('test', "line"),
    ],
}