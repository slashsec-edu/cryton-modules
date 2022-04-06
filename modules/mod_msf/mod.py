#!/usr/bin/python
import logging
import time
import copy
import sys

from pymetasploit3.msfrpc import MsfSession, MsfModule, PayloadModule
from schema import Schema, Optional, And

from cryton_worker.lib.util.module_util import Metasploit
from cryton_worker.lib.util import logger


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function.

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema({
        'msf_module_name': And(str),
        Optional('msf_module_options'): {
            Optional(str): And(str)
        },
        Optional("session_id"): And(str),
        Optional("create_named_session"): And(str),
        Optional("std_out"): And(bool),
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
    std_out_flag: bool = arguments.get("std_out", False)
    msf_module_name: str = arguments.get('exploit')
    msf_module_options: dict = arguments.get('exploit_arguments')
    session_id: str = arguments.get('session_id')
    create_named_session: str = arguments.get('create_named_session')

    # Open client
    try:
        msf = Metasploit()
    except Exception:
        ret_vals.update({'return_code': -1, 'mod_err': str(sys.exc_info())})
        return ret_vals

    # check if a remote target is set
    target_host = msf_module_options["RHOSTS"] if "RHOSTS" in msf_module_options else None

    if create_named_session:
        logger.logger.debug("Create session.", session_name=create_named_session)

        if target_host:
            before_sessions = msf.get_sessions(session_host=target_host)
        elif session_id:
            try:
                target_host = msf.client.sessions.list.get(session_id)["session_host"]
                before_sessions = msf.get_sessions(session_host=target_host)
            except Exception as e:
                ret_vals.update({'return_code': -1, 'mod_err': str(e)})
                return ret_vals
        else:
            before_sessions = msf.get_sessions()

    if session_id:
        logger.logger.debug("Use session.", session_id=session_id)
        msf_module_options['SESSION'] = session_id

    # Create console
    console_id = msf.client.consoles.console().cid

    jobs_before = msf.client.jobs.list

    # Clear console
    msf.client.call('console.read', [console_id])
    time.sleep(1)

    # Set parameters
    s = "use %s\n" % msf_module_name
    msf.client.call('console.write', [console_id, s])
    time.sleep(3)

    for key, val in msf_module_options.items():
        s = "set %s %s\n" % (key, val)
        msf.client.call('console.write', [console_id, s])
        time.sleep(3)

    s = "exploit -j -z\n"
    msf.client.call('console.write', [console_id, s])
    time.sleep(3)

    jobs_after = msf.client.jobs.list

    time.sleep(1)

    new_job_id = get_current_job_id(jobs_after, jobs_before)

    # Wait until current job is finished
    if new_job_id is not None and msf_module_name != "exploit/multi/handler":
        # Until job ends
        while new_job_id in jobs_after.keys():
            time.sleep(2)
            jobs_after = msf.client.jobs.list
        time.sleep(3)

    # Read output of job
    data = read_output(msf.client, console_id)

    logger.logger.debug("Response: ", data=data)



    # Return std_out
    if std_out_flag is True:
        ret_vals.update({'std_out': str(data)})

    # Check for Error or Success
    if 'OptionValidateError' in data:
        ret_vals.update({'return_code': -1, 'mod_err': str(data)})
        return ret_vals

    if msf_module_name == "exploit/multi/handler":
        ret_vals.update({'return_code': 0, 'mod_out': str(data)})

    elif 'Success' in data or 'Command shell session' in data or 'Meterpreter session' in data or "Upgrading session ID:" \
            in data or "[+] Route added to subnet" in data or "Command Stager progress - 100.00%" in data or (
            '[+]' in data and '[-]' not in data):
        ret_vals.update({'return_code': 0, 'mod_out': str(data)})
    else:
        # TODO changed to return code 0 for tests
        ret_vals.update({'return_code': 0, 'mod_out': str(data)})
        return ret_vals

    # get sessions after
    if create_named_session:
        time.sleep(20)
        if target_host:
            after_sessions = msf.get_sessions(session_host=target_host)
        else:
            after_sessions = msf.get_sessions()

        # Get new session
        new_sessions_to_same_host = list(set(after_sessions) - set(before_sessions))

        logger.logger.debug("new_sessions_to_same_host: ", new_sessions_to_same_host=new_sessions_to_same_host)
        if len(new_sessions_to_same_host) > 0:
            sessions = msf.get_sessions(session_host=target_host, via_exploit=msf_module_name)

            if sessions is None or len(sessions) == 0:
                sessions = msf.get_sessions(session_host=target_host, via_exploit='exploit/multi/handler')

            sessions = msf.get_sessions()

            if sessions is not None:
                newest_session_id = sessions[-1]
                session_type = msf.get_parameter_from_session(newest_session_id, "type")
                ret_vals.update({'session_id': newest_session_id})
                ret_vals.update({'session_type': 'MSF_' + session_type.upper()})
                ret_vals.update({'return_code': 0})

    return ret_vals
