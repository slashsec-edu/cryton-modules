import json
import random
import string
import subprocess
import time
import datetime
import os
from schema import Schema, And, Optional

from cryton_worker.lib.util.module_util import Dir


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema({
        Optional('target'): And(str),
        Optional('prefix'): And(str),
        Optional('tail'): And(str),
        Optional('report_path'): Dir(str),
        Optional('command'): And(str),
        Optional('report_type'): And(str),
    })

    conf_schema.validate(arguments)

    return 0


def execute(arguments: dict) -> dict:
    """
    This module uses WPScan.
    The target must be in this format: http://127.0.0.1 (prefix&target).

    Available arguments are:
    * target: scan target (define when not using command parameter)
    example: 1.1.1.1

    * prefix: what prefix you want to add to your target (optional)
    example: http://

    * tail: what tail you want to add to your target (optional)
    example: :8000

    * command: WPScan command arguments with syntax as in command line (when command is not set
    default command is used)

    * report_path: absolute path with the generated file(s)

    * report_type: if you want to use the basic command; options - json / standard

    :param dict arguments: dictionary of mandatory subdictionary 'arguments' and other optional elements
    :return: ret_vals: dictionary with following values:

        * ret: 0 in success, other number in failure,

        * value: return value, usually stdout,

        * mod_err: error message, if any
    """
    ret_vals = dict(dict())
    ret_vals.update({'return_code': -1})
    ret_vals.update({'std_out': None})
    ret_vals.update({'mod_out': None})
    ret_vals.update({'mod_err': None})

    report_type = arguments.get('report_type')
    target = arguments.get('target')

    report_path = arguments.get('report_path')
    command_input = arguments.get('command')
    prefix = arguments.get('prefix')
    tail = arguments.get('tail')

    if prefix:
        target = prefix + target
    if tail:
        target += tail

    command = ["wpscan"]

    time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f"))
    file_tail = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=5))

    if report_path is None or report_path == '':
        report_path = '/tmp/'

    if os.path.isdir(report_path):
        report_file = report_path + 'report_wpscan' + time_stamp + file_tail + '.txt'
    else:
        ret_vals.update({'mod_err': report_path + 'isn\'t directory.'})
        return ret_vals

    if report_type is None or report_type == "" or report_type == "json":
        report_type = "json"

    elif report_type == "standard":
        report_type = "cli-no-color"

    if command_input is not None and command_input != '':
        split = command_input.split(' ')
        for each in split:
            command.append(each)

    else:
        if target is None or target == '':
            ret_vals.update({'mod_err': '\'target\' parameter is missing.'})
            return ret_vals

        def_commands = ["--url", target, "-o", report_file, "-f", report_type]
        for each in def_commands:
            command.append(each)

    # setting files
    try:
        fnull = open(os.devnull, 'w')

    except OSError:
        ret_vals.update({'mod_err': 'Cannot open dumpster - fnull.'})
        return ret_vals

    # starting
    try:
        t = subprocess.Popen(command, stderr=fnull, stdout=fnull)
    except OSError:
        ret_vals.update({'mod_err': 'Check if your command starts with \'wpscan\''})
        return ret_vals

    except subprocess.SubprocessError:
        ret_vals.update({'mod_err': 'WPScan couldn\'t start.'})
        return ret_vals

    # main loop
    while True:
        time.sleep(5)
        with open(report_file, 'r') as f:
            file = f.read()
            if "unrecognized option" in file or "option requires an argument" in file or "seems to be down" in file \
                    or "but does not seem to be running WordPress." in file or "has not been found" in file \
                    or "Scan Aborted" in file:
                ret_vals.update({'mod_err': 'Something went wrong, check in results ' + report_file + ' for details.'})
                t.kill()
                return ret_vals

            if "Finished:" in file or '"stop_time":' in file or '"not_fully_configured":' in file:
                time.sleep(1)
                t.kill()
                break

    # reporting results
    report_name = str(report_file).split('/')[-1]
    final_json = {}

    try:
        with open(report_file, 'rb') as bin_file:
            file_content = bin_file.read()
    except Exception as e:
        raise e

    if report_type == "json":
        with open(report_file, 'r') as f:
            final_json = json.load(f)

    elif report_type == "cli-no-color":
        with open(report_file, 'r') as f:
            final_json = f.read()


    ret_vals.update({'return_code': 0})
    ret_vals.update({'std_out': report_file})
    ret_vals.update({'mod_out': final_json})
    ret_vals.update({'file': {'file_name': report_name, 'file_content': file_content}})

    return ret_vals
