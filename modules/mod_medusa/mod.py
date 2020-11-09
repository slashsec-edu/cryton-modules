import json
import random
import string
import subprocess
import time
import datetime
import os
from schema import Schema, Optional, And, Or
from cryton_worker.lib.util import Dir, File, get_file_content


def validate(step_args):
    """
    Validate input values for the execute function

    :param dict step_args: execute function args.get('arguments')
    :return: 0
    :raises: Schema Exception
    """
    conf_schema = Schema({
        Optional('target'): And(str),
        Optional('mod'): And(str),
        Optional('command'): And(str),
        Optional('report_path'): Dir(str),
        Optional('username'): And(str),
        Optional('username_list'): File(str),
        Optional('password'): And(str),
        Optional('password_list'): File(str),
        Optional('combo_list'): File(str),
        Optional('open_ports'): And(str),
        Optional('tasks'): Or(str, int),
    })

    conf_schema.validate(step_args)

    return 0


def execute(args):
    """
    This module uses medusa.
    The target must be in this format: 1.2.3.4 (target).

    Available arguments are:
    * target: bruteforce target (must be set when not using command)

    * mod: specified mod you want to use to attack (default ssh)

    * command: Medusa args with syntax as in command line. Cannot be combined with other module arguments!

    * report_path: absolute path where you want to save login pairs - default is Cryton reports folder

    * username: username to test

    * username_list: absolute path to file with usernames

    * password: password to test

    * password_list: absolute path to file with passwords

    * combo_list: absolute path to file with login pairs (official format can be found in medusa doc - user:pass)

    * tasks: Total number of login pairs to be tested concurrently, default is 16

    :param dict args: dictionary of mandatory subdictionary 'arguments' and other optional elements
    :return: ret_vals: dictionary with following values:

        * ret: 0 in success, other number in failure,

        * value: return value, usually stdout,

        * std_err: error message, if any
    """
    # setting default return values
    ret_vals = dict(dict())
    ret_vals.update({'return_code': -1})
    ret_vals.update({'std_out': None})
    ret_vals.update({'std_err': None})
    ret_vals.update({'mod_out': None})

    # parsing input arguments
    arguments = args.get('arguments')
    target = arguments.get('target')

    report_path = arguments.get('report_path')
    username = arguments.get('username')
    username_list = arguments.get('username_list')
    password = arguments.get('password')
    password_list = arguments.get('password_list')
    combo_list = arguments.get('combo_list')
    command_input = arguments.get('command')
    open_ports = arguments.get('open_ports')
    mod = arguments.get('mod')
    tasks = arguments.get('tasks')

    # setting default working values
    time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f"))
    file_tail = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=5))
    check_file = '/tmp/' + 'medusa_check' + time_stamp + file_tail + '.txt'
    log_file = '/tmp/' + 'medusa_log' + time_stamp + file_tail + '.txt'
    report_file = '/tmp/' + 'medusa_report' + time_stamp + file_tail + '.txt'
    create_check_file = True

    # setting command for module
    command = ["medusa"]

    # setting command from user custom command
    if command_input is not None and command_input != '':
        split = command_input.split(' ')

        set_report_file = False
        for each in split:
            if set_report_file:
                set_report_file = False
                create_check_file = False
                check_file = each

            elif each == '-O':
                set_report_file = True

            command.append(each)

        if create_check_file:
            command.append('-O')
            command.append(check_file)

    # setting command from user input
    else:
        # if combo_list is set, choose it by default
        if combo_list is not None and combo_list != '':
            if os.path.isfile(combo_list):
                command.append("-C")
                command.append(combo_list)
        else:
            # set user
            set_default_user = True
            if username is not None and username != "":
                command.append("-u")
                command.append(username)
                set_default_user = False
            else:
                if username_list is not None and username != "":
                    if os.path.isfile(username_list):
                        command.append("-U")
                        command.append(username_list)
                        set_default_user = False

            if set_default_user:
                command.append("-u")
                command.append("admin")

            # set password
            set_default_password = True
            if password is not None and password != "":
                command.append("-p")
                command.append(password)
                set_default_password = False
            else:
                if password_list is not None and password_list != "":
                    if os.path.isfile(password_list):
                        command.append("-P")
                        command.append(password_list)
                        set_default_password = False

            if set_default_password:
                passwd = '/usr/share/wordlists/rockyou.txt'
                if os.path.isfile(passwd):
                    command.append("-P")
                    command.append(passwd)
                else:
                    ret_vals.update({'std_err': 'Default passwd file doesn\'t exist.'})
                    return ret_vals

        # set report and check file file
        if report_path is None or report_path == '':
            report_path = '/tmp/'

        if os.path.isdir(report_path):
            report_file = report_path + 'medusa_report' + time_stamp + file_tail + '.txt'
            check_file = report_path + 'medusa_check' + time_stamp + file_tail + '.txt'
        else:
            ret_vals.update({'std_err': report_path + 'isn\'t directory.'})
            return ret_vals

        command.append("-O")
        command.append(check_file)

        # set tasks
        if tasks is None or tasks == '':
            tasks = '16'
        elif isinstance(tasks, int):
            tasks = str(tasks)

        command.append('-t')
        command.append(tasks)

        if target is None or target == '':
            ret_vals.update({'mod_err': '\'target\' parameter is missing.'})
            return ret_vals

        command.append('-h')
        command.append(target)

        # set mod
        if mod is None or mod == '':
            mod = 'ssh'

        # look if mod is in open_ports
        if open_ports is not None:
            if mod in open_ports.keys():
                command.append('-M')
                command.append(mod)
            else:
                ret_vals.update({'mod_err': 'Cannot connect to the port of this service'})
                os.remove(log_file)
                return ret_vals
        else:
            command.append('-M')
            command.append(mod)

    # setting files
    try:
        log = open(log_file, 'w')

    except OSError:
        ret_vals.update({'std_err': 'Cannot create file ' + log_file + '.'})
        return ret_vals

    # starting
    try:
        t = subprocess.Popen(command, stderr=log, stdout=log)
    except FileNotFoundError:
        ret_vals.update({'std_err': 'Check if your command starts with \'medusa\' and is installed.'})
        os.remove(log_file)
        return ret_vals

    except subprocess.SubprocessError:
        ret_vals.update({'std_err': 'Medusa couldn\'t start.'})
        os.remove(log_file)
        return ret_vals

    time.sleep(2)
    with open(log_file, 'r') as f:
        err = f.read()
        if "Syntax" in err and "ALERT:" in err or 'invokeModule failed' in err:
            file_content = get_file_content(log_file)
            parsed_file_name = os.path.basename(log_file)
            ret_vals.update({'file': {'file_name': parsed_file_name, 'file_contents': file_content}})
            ret_vals.update({'std_err': 'Something went wrong, check in results EVIDENCE_DIR/' +
                                        parsed_file_name + ' for details.'})
            t.kill()
            return ret_vals

    # main loop
    while True:
        time.sleep(1)
        finished = False
        success = False
        err = 'Something went wrong'
        with open(check_file, 'r') as f:
            file = f.read()
        with open(log_file, 'r') as lf:
            l_file = lf.read()

        if "Medusa has finished" in file:
            if "[SUCCESS]" not in file:
                ret_vals.update({'return_code': -1})
                if 'ERROR:' in file or 'ERROR' in l_file:
                    if 'NOTICE:' in l_file:
                        for row in l_file.splitlines(True):
                            if 'NOTICE:' in row:
                                err = row
                                break

                        file_content = get_file_content(log_file)
                        parsed_file_name = os.path.basename(log_file)
                        ret_vals.update({'file': {'file_name': parsed_file_name, 'file_contents': file_content}})
                        ret_vals.update({'std_err': '{}, check in results EVIDENCE_DIR/{} for more details.'
                                        .format(str(err), parsed_file_name)})
                    elif 'NOTICE:' in file:
                        for row in file.splitlines(True):
                            if 'NOTICE:' in row:
                                err = row
                                break

                        file_content = get_file_content(check_file)
                        parsed_file_name = os.path.basename(check_file)
                        ret_vals.update({'file': {'file_name': parsed_file_name, 'file_contents': file_content}})
                        ret_vals.update({'std_err': '{}, check in results EVIDENCE_DIR/{} for more details.'
                                        .format(str(err), parsed_file_name)})
                    else:
                        ret_vals.update({'std_err': '{}, check in results {} or {} on your executor/slave for details.'
                                        .format(str(err), check_file, log_file)})
                else:
                    ret_vals.update({'std_out': 'No password found.'})
                success = False

            else:
                success = True
            finished = True

        if finished:
            try:
                t.kill()
            except Exception as e:
                with open(check_file, 'a+') as f:
                    f.write('An error occurred while killing the program: ' + str(e))
            break

    # reporting results
    if success:
        json_credentials = {}
        with open(check_file, 'r') as f:
            for row in f:
                if '[SUCCESS]' in row:
                    found_username = row.split('User: ')[1].split(' Password:')[0]
                    found_password = row.split('Password: ')[1].split(' [SUCCESS]')[0]
                    json_credentials.update({str(found_username): str(found_password)})

            if len(json_credentials) > 1:
                json_credentials = {"credentials": json_credentials}
            else:
                json_credentials = {"username": list(json_credentials.keys())[0],
                                    "password": list(json_credentials.values())[0]}

        with open(report_file, 'w') as f:
            json.dump(json_credentials, f)

        # reporting results
        file_content = get_file_content(report_file)
        parsed_file_name = os.path.basename(report_file)
        ret_vals.update({'file': {'file_name': parsed_file_name, 'file_contents': file_content}})

        ret_vals.update({'return_code': 0})
        ret_vals.update({'std_out': json_credentials})
        ret_vals.update({'mod_out': json_credentials})

        if create_check_file:
            os.remove(check_file)
        os.remove(log_file)

    return ret_vals
