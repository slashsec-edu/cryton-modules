#!/usr/bin/python
from pymetasploit3.msfrpc import MsfRpcClient as ms

from cryton_worker.etc import config

import time
import copy
import sys
from schema import Schema, Optional, And


def validate(step_args):
    """
    Validate input values for the execute function

    :param dict step_args: execute function args.get('arguments')
    :return: 0
    :raises: Schema Exception
    """
    conf_schema = Schema({
        'exploit': And(str),
        Optional('payload'): And(str),
        Optional(str): And(str)
    })

    conf_schema.validate(step_args)

    return 0


"""
Configuration variables
"""
MSFRPCD_PASS = config.MSFRPCD_PASS
MSFRPCD_USERNAME = config.MSFRPCD_USERNAME
MSFRPCD_PORT = config.MSFRPCD_PORT
MSFRPCD_SSL = config.MSFRPCD_SSL


def get_session_ids(target_ip):
    """
    Get a list of session IDs

    :param str target_ip: IP address of the desired target
    :return: list of session IDs
    """
    sess_list = list()

    client = ms(MSFRPCD_PASS, username=MSFRPCD_USERNAME,
                port=MSFRPCD_PORT, ssl=MSFRPCD_SSL)

    for session_key, session_value in client.sessions.list.items():
        if session_value['target_host'] == target_ip or session_value['tunnel_peer'].split(':')[0] == target_ip:
            sess_list.append(session_key)
    return sess_list


def execute(args):
    """
    This attack module can run Metasploit scripts in virtual Metasploit console connected to
    msfrpcd daemon.

    Available arguments are:

    * exploit: exploit/auxilliary/... or any other family of Metasploit console scripts

    * exploit_arguments: custom dict of Metasploit module specific arguments (eg. RHOSTS, RPORT)

    example:
        args = {"arguments": {"exploit": "auxiliary/scanner/ssh/ssh_login",
                              "exploit_arguments": {
                                  "USERPASS_FILE": "/home/nutar/temp/userpass.txt",
                                  "RHOSTS": "192.168.56.101"
                                }
                              }
                }
    :param dict args: dictionary of mandatory subdictionary 'arguments' and other optional elements
    :return: ret_vals: dictionary with following values:

        * ret: 0 in success, other number in failure,

        * value: return value, usually stdout,

        * std_err: error message, if any
    """
    ret_vals = dict(dict())
    ret_vals.update({'return_code': -1})
    ret_vals.update({'std_out': None})
    ret_vals.update({'std_err': None})
    ret_vals.update({'mod_out': None})
    ret_vals.update({'mod_err': None})

    # Copy arguments to not change them by mistake
    args = copy.deepcopy(args)

    # Get arguments
    arguments = args.get('arguments')

    # Parse exploit
    exploit = arguments.get('exploit')
    exploit_arguments = arguments.get('exploit_arguments')

    # Open client
    try:
        client = ms(MSFRPCD_PASS, username=MSFRPCD_USERNAME,
                    port=MSFRPCD_PORT, ssl=MSFRPCD_SSL)
    except Exception:
        ret_vals.update({'return_code': -2, 'std_err': str(sys.exc_info())})
        return ret_vals

    # Set parameters
    s = "use %s\n" % exploit
    for key, val in exploit_arguments.items():
        s += "set %s %s\n" % (key, val)
    s += "exploit -j;\n"

    # Create console
    console_id = client.consoles.console().cid

    # Clear console
    client.call('console.read', [console_id])

    # Get sessions before
    target = exploit_arguments.get('RHOSTS')
    before_sessions = get_session_ids(target)
    jobs_before = client.jobs.list

    # Run exploit
    client.call('console.write', [console_id, s])
    time.sleep(1)

    # Check created job
    jobs_after = client.jobs.list
    new_jobs = set(jobs_after.keys()) - set(jobs_before.keys())
    try:
        new_job_id = new_jobs.pop()
    except KeyError:
        new_job_id = None

    # Wait until job finishes
    if new_job_id is not None:
        # Until job ends
        while new_job_id in jobs_after.keys():
            time.sleep(5)
            jobs_after = client.jobs.list

    # Read output of job
    output = client.call('console.read', [console_id])
    data = output.get('data')
    while output.get('busy'):
        time.sleep(1)
        output = client.call('console.read', [console_id])
        data += "\n===MORE DATA===\n"
        data += output.get('data')

    # Store data to std_out
    ret_vals.update({'std_out': data})

    # Check for Error or Success
    if 'OptionValidateError' in data:
        ret_vals.update({'return_code': -1, 'std_err': str(data)})
        return ret_vals

    if 'Success' in data or ('[+]' in data and '[-]' not in data):
        ret_vals.update({'return_code': 0, 'std_out': str(data)})

    # get sessions after
    after_sessions = get_session_ids(target)

    # Get new session
    new_sessions_to_same_host = list(set(after_sessions) - set(before_sessions))

    if len(new_sessions_to_same_host) > 0:
        for session_key, session_value in client.sessions.list.items():
            if (session_value['target_host'] == target or session_value['tunnel_peer'].split(':')[0] == target) \
                    and session_value['via_exploit'] == exploit:
                ret_vals.update({'session_id': session_key})
                ret_vals.update({'return_code': 0})

    return ret_vals
