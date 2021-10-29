#!/usr/bin/python
# import importlib
import datetime
import os
import random
import string
import subprocess
from schema import Schema, And, Optional, Or

from cryton_worker.lib.util.module_util import Dir, File


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema({
        'file': File(str),
        'executable': And(Or(str)),
        Optional('args'): And(str),
        Optional('output_file'): Dir(str),
        Optional('timeout'): And(Or(str, int))
    })

    conf_schema.validate(arguments)

    return 0


def execute(arguments: dict) -> dict:
    """
    This attack module is supposed to run python scripts

    Available arguments are:

    !!! target for this module has to be specified in 'args' !!!

    * file - full path to the script

    * args - optional args for script

    * output_file (optional) - where should be output file of module be stored, if not defined,
    output will be in the report file

    * timeout - for how long - in seconds - the script should run, if not defined in args;
                if timeout is not set, module waits until its finished

    * executable - which type of script you want to run (python, shell , ruby)

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

    file_exec = arguments.get('file')
    special_args = arguments.get('args')
    output_file = arguments.get('output_file')
    timeout = arguments.get('timeout')
    executable = arguments.get('executable')

    if file_exec is None or file_exec == '' or (not os.path.exists(file_exec)):
        ret_vals.update({'mod_err': 'please check your file_location input'})
        ret_vals.update({'return_code': -1})
        return ret_vals

    if timeout != '' and timeout is not None:
        try:
            timeout = int(timeout)
        except ValueError:
            ret_vals.update({'mod_err': 'please check your timeout input'})
            ret_vals.update({'return_code': -1})
            return ret_vals
    else:
        timeout = None

    cmd = [executable, file_exec]

    special_args = str(special_args).split(' ')
    for each in special_args:
        cmd.append(str(each))

    try:
        process = subprocess.run(cmd, timeout=timeout, capture_output=True)
        process.check_returncode()
    except subprocess.TimeoutExpired:
        ret_vals.update({'std_out': "Timeout expired"})
        ret_vals.update({'return_code': 0})
        return ret_vals
    except subprocess.CalledProcessError as err:  # process exited with return code other than 0
        ret_vals.update({'mod_err': err.stderr.decode('utf-8')})
        ret_vals.update({'return_code': -1})
        return ret_vals
    except Exception as err:
        ret_vals.update({'mod_err': str(err)})
        ret_vals.update({'return_code': -1})
        return ret_vals
    else:
        ret_vals.update({'return_code': 0})

    try:
        if output_file is not None:
            if os.path.isdir(output_file):
                time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f"))
                file_tail = ''.join(random.choices(string.ascii_uppercase + string.digits
                                                   + string.ascii_lowercase, k=5))
                report_file = output_file + 'log_script_' + str(file_exec).split('/')[-1] + time_stamp + file_tail
                with open(report_file, 'w') as file:
                    file.write(
                        "RETURN CODE: 0" + "\n" * 2 +
                        "STDOUT: " + process.stdout.decode('utf-8') + "\n"
                        "STDERR: " + process.stderr.decode('utf-8') + "\n"
                    )
                ret_vals.update({'std_out': report_file})

            else:
                ret_vals.update({'mod_err': output_file + 'isn\'t directory.'})
                ret_vals.update({'return_code': -1})
                return ret_vals

        else:
            ret_vals.update({'mod_err': process.stderr.decode('utf-8')})
            ret_vals.update({'mod_out': {'script_output': process.stdout.decode('utf-8')}})
            ret_vals.update({'return_code': 0})
    except OSError:
        ret_vals.update({'mod_err': 'Cannot create files in report_path.'})
        return ret_vals
    except Exception as err:
        ret_vals.update({'return_code': -1})
        ret_vals.update({'mod_err': str(err)})
        return ret_vals

    return ret_vals
