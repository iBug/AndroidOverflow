import sys
import os
import datetime
import traceback

import requests
from termcolor import colored

import core


_LOG_CONFIG = {
    'debug': (0, 'grey'),
    'info': (1, 'cyan'),
    'warning': (2, 'yellow'),
    'error': (3, 'red'),
}


def log(log_level, *args):
    level, color = _LOG_CONFIG[log_level]
    if level < core.config.log_level:
        return

    time_s = datetime.datetime.now().isoformat()[11:23]
    s = "{} {}".format(colored("[{}]".format(time_s), color, attrs=['bold']),
                       "\n             ".join([str(x) for x in args]))
    print(s, file=sys.stderr)
    if level == 3:
        traceback.print_stack()

    log_file(log_level, *args)


def log_file(log_level, *args):
    level = _LOG_CONFIG[log_level][0]
    if level < core.config.file_log_level:
        return

    time_s = datetime.datetime.now().isoformat()[11:23]
    log_s = "\n             ".join([str(x) for x in args])
    with open(core.config.log_file) as f:
        print("[{}] {}".format(time_s, log_s), file=f)


def get_site_id(hostname):
    if not core.obj.site_list:
        core.obj.site_list = requests.get(
            "https://meta.stackexchange.com/topbar/site-switcher/all-pinnable-sites").json()

    for item in core.obj.site_list:
        if item['hostname'] == hostname:
            return item['siteid']
    return None
