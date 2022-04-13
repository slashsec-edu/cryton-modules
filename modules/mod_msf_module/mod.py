#!/usr/bin/python
import copy
import multiprocessing
import sys
import time
from ctypes import c_wchar_p

from cryton_worker.lib.util import logger
from cryton_worker.lib.util.module_util import Metasploit
from schema import Schema, Optional, And

from modules.mod_msf.mod import get_current_job_id


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function.

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema({
        'module_type': And(str),
        'module_name': And(str),
        Optional('module_options'): {
            Optional(str): And(str)
        },
        Optional("payload_name"): And(str),
        Optional("payload_options"): {
            Optional(str): And(str)
        },
        Optional('run_as_job'): And(bool),
        Optional("session_id"): And(int),
        Optional("create_named_session"): And(str),
        Optional("std_out"): And(bool),
        Optional("exploit_timeout_in_sec"): And(int),
        Optional("exploit_retries"): And(int),
        Optional("session_timeout_in_sec"): And(int),
    })

    conf_schema.validate(arguments)

    return 0


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
    msf_module_type: str = arguments.get('module_type')
    msf_module_name: str = arguments.get('module_name')
    msf_module_options: dict = arguments.get('module_options')

    msf_payload_name: str = arguments.get('payload_name')
    msf_payload_options: dict = arguments.get('payload_options')

    run_as_job: bool = arguments.get("run_as_job", False)

    session_id: int = arguments.get('session_id')
    create_named_session: str = arguments.get('create_named_session')

    exploit_timeout_in_sec: int = arguments.get("exploit_timeout_in_sec", 60)
    exploit_retries: int = arguments.get("exploit_retries", 1)

    session_timeout_in_sec: int = arguments.get("session_timeout_in_sec", 30)

    # Open MSF client session
    try:
        msf = Metasploit()
    except Exception as ex:
        ret_vals.update({'return_code': -1, 'mod_err': str(sys.exc_info()) + " " + str(ex)})
        return ret_vals

    module = msf.client.modules.use(msf_module_type, msf_module_name)
    if msf_module_options is not None:
        module.update(msf_module_options)

    if session_id is not None:
        print(type(session_id))
        module.update({"SESSION": int(session_id)})

    payload = None
    if msf_payload_name is not None:
        time.sleep(1)
        payload = msf.client.modules.use("payload", msf_payload_name)

        if msf_payload_options is not None:
            payload.update(msf_payload_options)

    # Execute without output
    # job = payload.execute(payload=payload)

    jobs_before = msf.client.jobs.list
    sessions_before = msf.get_sessions()

    # Execute with output
    try:

        logger.logger.debug("Executing ", module=module.modulename, run_as_job=run_as_job)

        exploit_runs = 0
        exploit_succeeded = False
        # response = multiprocessing.Value(unicode, "")

        response_queue = multiprocessing.Queue()
        while exploit_runs < exploit_retries and not exploit_succeeded:
            print("Executing exploit. Run:", exploit_runs)
            msf_console = msf.client.consoles.console()
            p = multiprocessing.Process(target=run_exploit, name=module.modulename,
                                        args=(msf_console, module, payload, run_as_job, response_queue))
            p.start()

            p.join(exploit_timeout_in_sec)

            if p.is_alive():
                print("Exploit did not return any data within defined timeout. Killing exploit thread now.")
                p.kill()
                p.join()
            else:
                exploit_succeeded = True
            msf_console.destroy()
            exploit_runs += 1

        if exploit_runs >= exploit_retries and not exploit_succeeded:
            ret_vals.update({'return_code': -1, 'mod_err': "Could not successfully execute exploit."})
            return ret_vals

            # response_data = msf_console.run_module_with_output(module, payload=payload, run_as_job=run_as_job)
        response_data = response_queue.get()
        logger.logger.debug("Response from module", response_data=response_data)
    except Exception as ex:
        ret_vals.update({'return_code': -1, 'mod_err': str(ex)})
        return ret_vals

    # Wait for new session
    if create_named_session is not None:
        jobs_after = msf.client.jobs.list

        new_job_id = get_current_job_id(jobs_after, jobs_before)

        # Wait until current job is finished
        timeout_counter = 0
        if new_job_id is not None:
            # Until job ends
            while new_job_id in jobs_after.keys() and timeout_counter < session_timeout_in_sec:
                time.sleep(1)
                timeout_counter += 1
                jobs_after = msf.client.jobs.list

        new_sessions = []
        timeout_counter = -5
        while len(new_sessions) == 0:
            sessions_after = msf.get_sessions()
            new_sessions = list(set(sessions_after) - set(sessions_before))

            if timeout_counter >= session_timeout_in_sec:
                ret_vals.update({'return_code': -1, 'mod_err': "Timeout reached. No new session opened."})
                return ret_vals

            if timeout_counter > 0 and run_as_job:
                msf_console = msf.client.consoles.console()
                p = multiprocessing.Process(target=run_exploit, name=module.modulename,
                                            args=(msf_console, module, payload, False, response_queue))
                p.start()

                p.join(exploit_timeout_in_sec)

                if p.is_alive():
                    print("Exploit did not return any data within defined timeout. Killing exploit thread now.")
                    p.kill()
                    p.join()
                msf_console.destroy()

            timeout_counter += 1
            time.sleep(1)

        newest_session_id = new_sessions[-1]
        session_type = msf.get_parameter_from_session(newest_session_id, "type")
        ret_vals.update({'session_id': newest_session_id})
        ret_vals.update({'session_type': 'MSF_' + session_type.upper()})

    ret_vals.update({'mod_out': str(response_data)})
    ret_vals.update({'return_code': 0})

    return ret_vals


def run_exploit(msf_console, module, payload, run_as_job, response_queue: multiprocessing.Queue):
    response_data = msf_console.run_module_with_output(module, payload=payload, run_as_job=run_as_job)
    response_queue.put(response_data)
