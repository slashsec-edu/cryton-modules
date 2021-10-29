#!/usr/bin/python
import traceback
import subprocess
import json
import string
import datetime
import random
from schema import Schema, Optional, And

from cryton_worker.lib.util.module_util import Metasploit


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema({
        'cmd': And(str),
        Optional('end_check'): str,
        Optional('target'): And(str),
        Optional('timeout'): And(int),
        Optional('output_file'): And(bool),
        Optional('std_out'): And(bool),
        Optional('session_id'): And(str),
    })

    conf_schema.validate(arguments)

    return 0


def create_output_file() -> str:
    """
    Creates output file name which will be send to Cryton.

    :return: Output file name
    """
    time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f"))
    file_tail = "".join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=5))
    return "cmd_report" + time_stamp + file_tail + ".txt"


def execute(arguments: dict) -> dict:
    """
    Takes arguments in form of dictionary and runs command based on them.

    :param arguments: Arguments from which is compiled and ran command
    :return: Module output containing:
                return_code (0-success, 1-fail),
                std_out (raw output),
                mod_out (output that can be used in other modules),
                mod_err (error output)

    """
    ret_vals = dict(dict())
    ret_vals.update({'return_code': -1})
    ret_vals.update({'std_out': None})
    ret_vals.update({'mod_out': None})
    ret_vals.update({'mod_err': None})

    session_id = arguments.get('session_id', False)
    cmd = list(arguments.get('cmd').split(' '))
    end_check = arguments.get('end_check')
    output_file = arguments.get('output_file', False)
    std_out_flag = arguments.get('std_out', False)
    timeout = arguments.get('timeout', None)

    if session_id is not False:
        if int(session_id) != 0:
            cmd = " ".join(cmd)
            try:
                msf = Metasploit()
                output = msf.execute_in_session(cmd, session_id, end_check)
            except Exception as ex:
                ret_vals.update({'return_code': -1, 'mod_err': 'couldn\'t execute command in msf - is msfrpcd running? '
                                                               'Original exception: {}'.format(ex)})
                return ret_vals

        else:
            ret_vals.update({'return_code': -1, 'mod_err': 'session did not run'})
            return ret_vals

    else:
        try:
            process = subprocess.run(cmd, timeout, capture_output=True)
            process.check_returncode()
            output = process.stdout
            error = process.stderr

        except subprocess.TimeoutExpired:
            ret_vals.update({'std_out': 'Timeout expired'})
            ret_vals.update({'return_code': -1})
            return ret_vals
        except subprocess.CalledProcessError as err:  # exited with return code other than 0
            ret_vals.update({'mod_err': err.stderr.decode('utf-8')})
            ret_vals.update({'return_code': -1})
            return ret_vals
        except Exception as ex:
            tb = traceback.format_exc()
            mod_err = str(ex) + tb
            ret_vals.update({'return_code': -1, 'mod_err': json.dumps(mod_err)})
            return ret_vals
        else:
            ret_vals.update({'return_code': 0})
            ret_vals.update({'mod_err': error.decode("utf-8")})

    ret_vals.update({'mod_out': output})
    ret_vals.update({'return_code': 0})
    if output_file is True:
        ret_vals.update({'std_out': 'Output file saved in evidence dir'})
        ret_vals.update({'file': {'file_name': create_output_file(), 'file_content': output}})
    elif std_out_flag is True:
        ret_vals.update({'std_out': output})

    return ret_vals
