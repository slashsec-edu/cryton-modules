#!/usr/bin/python
import time
import copy
import sys
from schema import Schema, Optional, And

from cryton_worker.lib.util.module_util import Metasploit


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function.

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema({
        'exploit': And(str),
        Optional("std_out"): And(bool),
        Optional('exploit_arguments'): {
            Optional(str): And(str)
        }
    })

    conf_schema.validate(arguments)

    return 0


def read_output(client, console_id: int) -> str:
    """
    Reads output from msfrpcd exploit execution.

    :param client: msfrpcd client
    :param console_id: created console id
    :return: exploit output
    """
    output = client.call('console.read', [console_id])
    data = output.get('data')
    while output.get('busy'):
        time.sleep(1)
        output = client.call('console.read', [console_id])
        data += "\n===MORE DATA===\n"
        data += output.get('data')
    return data


def get_current_job_id(jobs_after: dict, jobs_before: dict) -> int:
    """
    Get new job created in this exploit execution.

    :param jobs_after: Jobs created before this run
    :param jobs_before: Jobs after exploit execution started
    :return: Current job id
    """
    new_jobs = set(jobs_after.keys()) - set(jobs_before.keys())
    try:
        new_job_id = new_jobs.pop()
    except KeyError:
        new_job_id = None
    return new_job_id


def execute(args: dict) -> dict:
    """
    Takes arguments in form of dictionary and runs Msf based on them.

    :param args: Arguments from which is compiled and ran medusa command
    :return: Module output containing:
                return_code (0-success, -1-fail),
                std_out (raw output),
                mod_out (parsed output that can be used in other modules),
                mod_err (error output)

    """
    ret_vals = dict(dict())
    ret_vals.update({'return_code': -1})
    ret_vals.update({'std_out': None})
    ret_vals.update({'mod_err': None})
    ret_vals.update({'mod_out': None})

    # Copy arguments to not change them by mistake
    arguments = copy.deepcopy(args)

    # Parse exploit
    exploit = arguments.get('exploit')
    std_out_flag = arguments.get("std_out", False)
    exploit_arguments = arguments.get('exploit_arguments')

    # Open client
    try:
        msf = Metasploit()
    except Exception:
        ret_vals.update({'return_code': -1, 'mod_err': str(sys.exc_info())})
        return ret_vals

    # Set parameters
    s = "use %s\n" % exploit
    for key, val in exploit_arguments.items():
        s += "set %s %s\n" % (key, val)
    s += "exploit -j;\n"

    # Create console
    console_id = msf.client.consoles.console().cid

    # Clear console
    msf.client.call('console.read', [console_id])

    # Get sessions before
    target = exploit_arguments.get('RHOSTS')
    before_sessions = msf.get_sessions(target_host=target, tunnel_peer=target)
    jobs_before = msf.client.jobs.list

    # Run exploit
    msf.client.call('console.write', [console_id, s])
    time.sleep(1)

    jobs_after = msf.client.jobs.list
    new_job_id = get_current_job_id(jobs_after, jobs_before)

    # Wait until current job is finished
    if new_job_id is not None:
        # Until job ends
        while new_job_id in jobs_after.keys():
            time.sleep(5)
            jobs_after = msf.client.jobs.list

    # Read output of job
    data = read_output(msf.client, console_id)

    # Return std_out
    if std_out_flag is True:
        ret_vals.update({'std_out': str(data)})

    # Check for Error or Success
    if 'OptionValidateError' in data:
        ret_vals.update({'return_code': -1, 'mod_err': str(data)})
        return ret_vals

    if 'Success' in data or ('[+]' in data and '[-]' not in data):
        ret_vals.update({'return_code': 0, 'mod_out': str(data)})
    else:
        ret_vals.update({'return_code': -1, 'mod_err': str(data)})
        return ret_vals

    # get sessions after
    after_sessions = msf.get_sessions(target_host=target, tunnel_peer=target)

    # Get new session
    new_sessions_to_same_host = list(set(after_sessions) - set(before_sessions))

    if len(new_sessions_to_same_host) > 0:
        sessions = msf.get_sessions(target_host=target, tunnel_peer=target, via_exploit=exploit)
        if sessions is not None:
            ret_vals.update({'session_id': sessions[-1]})
            ret_vals.update({'return_code': 0})

    return ret_vals
