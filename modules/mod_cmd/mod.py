#!/usr/bin/python

import time
import traceback
import subprocess
import json
import os
import string
import datetime
import random
from pymetasploit3.msfrpc import MsfRpcClient as ms
from schema import Schema, Optional, And, Use
from cryton_worker.lib.util import Dir, File, get_file_content
from cryton_worker.etc import config

# Config variables
MSFRPCD_PASS = config.MSFRPCD_PASS
MSFRPCD_USERNAME = config.MSFRPCD_USERNAME
MSFRPCD_PORT = config.MSFRPCD_PORT
MSFRPCD_SSL = config.MSFRPCD_SSL


def validate(step_args):
    """
    Validate input values for the execute function

    :param dict step_args: execute function args.get('arguments')
    :return: 0
    :raises: Schema Exception
    """
    conf_schema = Schema({
        'cmd': And(str),
        Optional('target'): And(str),
        Optional('timeout'): And(int),
        Optional('output_file'): Dir(str),
        Optional('session_id'): And(int),
        Optional('create_session'): And(bool)
    })

    conf_schema.validate(step_args)

    return 0


def execute_in_msf_session(cmd, msf_session_id):
    """
    Execute command in session

    :param cmd: command
    :param msf_session_id: Metasploit session ID
    :return: output of command execution, return code {'code', 'output'}
    """
    client = ms(MSFRPCD_PASS, username=MSFRPCD_USERNAME,
                port=MSFRPCD_PORT, ssl=MSFRPCD_SSL)
    console = client.sessions.session(msf_session_id)
    # Execute command
    new_out = "START"
    output = ""
    console.write(cmd)
    while new_out:
        new_out = console.read()
        output += new_out
        time.sleep(1)

    code = 0
    output = dict({'code': code, 'output': output})

    return output


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
    This attack module can run bash commands either locally or in session, if specified
    in argument 'session_id'.

    Available arguments are:
    * target: target

    * cmd: command to be run

    * session_id (optional): Metasploit session ID, in which the command should be run

    * create_session (optional): True/False - is it desired to create a new session?

    * timeout (optional): Time in seconds after which the command execution should be terminated

    * output_file (optional) - where should be output file of module be stored, if not defined, 
    output will be in the report file

    :param dict args: dictionary of mandatory subdictionary 'arguments' and other optional elements
    :return: ret_vals: dictionary with following values:

        * ret: 0 in success, other number in failure,

        * value: location of output file (return code, stdout, stderr)

        * std_err: error message, if any

    """
    ret_vals = dict(dict())
    ret_vals.update({'return_code': -1})
    ret_vals.update({'std_out': None})
    ret_vals.update({'mod_out': None})
    ret_vals.update({'std_err': None})

    arguments = args.get('arguments')
    session_id = arguments.get('session_id', False)
    cmd = list(arguments.get('cmd').split(' '))
    output_file = arguments.get('output_file')
    create_session = arguments.get('create_session', False)
    timeout = arguments.get('timeout', None)
    target = arguments.get('target')

    check_output = False
    report_file = None
    if output_file is not None:
        if os.path.isdir(output_file):
            time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f"))
            file_tail = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=5))
            report_file = output_file + 'medusa_report' + time_stamp + file_tail + '.txt'
            check_output = True
        else:
            ret_vals.update({'std_err': output_file + 'isn\'t directory.'})
            return ret_vals

    file_contents = ""
    if session_id is not False:
        if int(session_id) != 0:
            cmd = " ".join(cmd)
            try:
                output_dict = execute_in_msf_session(cmd, session_id)
                output = output_dict.get('output')
                code = output_dict.get('code')
            except Exception as ex:
                ret_vals.update({'return_code': -2, 'std_err': 'couldn\'t execute command in msf - is msfrpcd running? '
                                                               'Original exception: {}'.format(ex)})
                return ret_vals

            if check_output is True:
                file_contents += "RETURN CODE: " + str(code) + "\n" * 2
                file_contents += "STDOUT/STDERR: " + output
                ret_vals.update({'return_code': 0})

            else:
                ret_vals.update({'std_out': output})
                ret_vals.update({'mod_out': {'cmd_out': output}})
                ret_vals.update({'return_code': int(code)})

        else:
            ret_vals.update({'return_code': -1, 'std_err': 'session did not run'})
            return ret_vals

    else:
        # Get sessions before
        if create_session:
            try:  # can we connect to msfrpc?
                before_sessions = get_session_ids(target)
            except:
                ret_vals.update({'return_code': -2, 'std_err': 'couldn\'t get current sessions - is msfrpcd running?'})
                return ret_vals

        try:
            process = subprocess.run(cmd, timeout, capture_output=True)
            process.check_returncode()

            if check_output is True:
                file_contents += "RETURN CODE: 0" + "\n" * 2
                file_contents += "STDOUT: " + process.stdout.decode('utf-8') + "\n"
                file_contents += "STDERR: " + process.stderr.decode('utf-8') + "\n"

                ret_vals.update({'return_code': 0})

            else:
                ret_vals.update({'std_out': process.stdout.decode('utf-8')})
                ret_vals.update({'mod_out': {'cmd_out': process.stdout.decode('utf-8')}})
                ret_vals.update({'std_err': process.stderr.decode('utf-8')})
                ret_vals.update({'return_code': 0})
        except subprocess.TimeoutExpired:
            ret_vals.update({'std_out': 'Timeout expired'})
            ret_vals.update({'return_code': 0})
            return ret_vals
        except subprocess.CalledProcessError as err:  # exited with return code other than 0
            ret_vals.update({'std_err': err.stderr.decode('utf-8')})
            ret_vals.update({'return_code': -1})
            return ret_vals
        except Exception as ex:
            tb = traceback.format_exc()
            std_err = str(ex) + tb
            ret_vals.update({'return_code': -2, 'std_err': json.dumps(std_err)})
            return ret_vals
        else:
            ret_vals.update({'return_code': 0})

        # get sessions after
        if create_session:
            try:  # can we connect to msfrpc?
                after_sessions = get_session_ids(target)
                new_sessions_to_same_host = list(set(after_sessions) - set(before_sessions))
                if len(new_sessions_to_same_host) > 0:
                    ret_vals.update({'session_id': new_sessions_to_same_host[-1]})
                    ret_vals.update({'return_code': 0})
            except Exception:
                ret_vals.update({'return_code': -2, 'std_err': 'couldn\'t get current sessions - is msfrpcd running?'})

    if check_output is True:
        with open(report_file, 'w') as f:
            f.write(file_contents)
        parsed_file_name = os.path.basename(report_file)
        ret_vals.update({'std_out': report_file})
        ret_vals.update({'mod_out': {'file_contents': report_file}})
        ret_vals.update({'file': {'file_name': parsed_file_name, 'file_contents': file_contents}})

    return ret_vals
