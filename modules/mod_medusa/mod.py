import pathlib
import random
import string
import subprocess
import datetime
import os
from typing import Optional as OptionalType
from schema import Schema, Optional, And, Or

from cryton_worker.lib.util.module_util import File


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema(Or(
        {
            "command": And(str),
            Optional("output_file"): And(bool),
        },
        {
            "target": And(str),
            Optional("mod"): str,
            Optional("output_file"): And(bool),
            Optional("std_out"): And(bool),
            Optional("tasks"): Or(str, int),
            Optional("credentials"): Or(
                {
                    "combo_file": And(str)
                },
                {
                    Optional("username_file"): File(str),
                    Optional("password_file"): File(str),
                    Optional("username"): And(str),
                    Optional("password"): And(str)
                }
            )
        }
    ))

    conf_schema.validate(arguments)

    return 0


def create_output_file() -> str:
    """
    Creates output file name which will be send to Cryton.

    :return: Output file name
    """
    time_stamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f"))
    file_tail = "".join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=5))
    return "medusa_report" + time_stamp + file_tail + ".txt"


def parse_custom_command(command: str) -> list:
    """
    Convert custom medusa command from string to list to be usable in subprocess.

    :param command: Custom medusa command
    :return: Parameters for medusa command
    """

    command_split = command.split(" ")
    command_list = []
    for parameter in command_split:
        command_list.append(parameter)
    return command_list


def parse_mod(mod: OptionalType[str]) -> list:
    """
    Parse service mod parameter.

    @param mod: Medusa service mod for bruteforce
    @return: Medusa mod parameter
    """
    if mod is None:
        mod = "ssh"
    return ["-M", mod]


def parse_username(username: OptionalType[str], username_list: OptionalType[str]) -> list:
    """
    Parse either username or path to file with usernames into medusa command parameter.

    :param username: Username for bruteforce
    :param username_list: Path to file with usernames
    :return: Username parameter for medusa command
    """
    if username is None and username_list is None:
        default_usr_path = str(pathlib.Path(__file__).parent.absolute()) + '/default_usernames.txt'
        return ["-U", default_usr_path]
    else:
        if username is not None:
            return ["-u", username]
        if username_list is not None:
            if os.path.isfile(username_list):
                return ["-U", username_list]
            else:
                raise FileNotFoundError("Username_list file doesn\"t exist.")


def parse_password(password: OptionalType[str], password_list: OptionalType[str]) -> list:
    """
    Parse either password or path to file with passwords into medusa command parameter.

    :param password: Password for bruteforce
    :param password_list: Path to file with passwords
    :return: Password parameter for medusa command
    """
    if password is None and password_list is None:
        default_pass_path = str(pathlib.Path(__file__).parent.absolute()) + '/default_passwords.txt'
        return ["-P", default_pass_path]
    else:
        if password is not None:
            return ["-p", password]
        if password_list is not None:
            if os.path.isfile(password_list):
                return ["-P", password_list]
            else:
                raise FileNotFoundError("Password_list file not found.")


def parse_combo_list(combo_list: str) -> list:
    """
    Parsing file path of username:password like credentials into medusa parameter.

    :param combo_list: Path to combo_list file
    :return: Parameters for medusa command
    """
    if os.path.isfile(combo_list):
        return ["-C", combo_list]
    else:
        raise FileNotFoundError("Combo_list file not found.")


def check_found_credentials(medusa_stdout: str) -> bool:
    """
    Check medusa output if bruteforce ran successfully and found valid credentials.

    :param medusa_stdout: Stdout of medusa bruteforce
    :return: Value representing if medusa was successful in finding valid credentials
    """
    if "ACCOUNT FOUND:" in medusa_stdout and "[SUCCESS]" in medusa_stdout:
        return True
    return False


def parse_credentials(medusa_output: str) -> dict:
    """
    Parse found credentials from medusa output.

    :param medusa_output: Stdout of medusa bruteforce
    :return: Found username and password credentials
    """
    json_credentials = {}
    medusa_output_lines = medusa_output.split("\n")
    for row in medusa_output_lines:
        if "ACCOUNT FOUND:" in row:
            found_username = ""
            found_password = ""
            row_split = row.split(" ")
            for word in row_split:
                if word == "User:":
                    found_username = (row_split[row_split.index(word) + 1]).strip()
                if word == "Password:":
                    found_password = (row_split[row_split.index(word) + 1]).strip()
            json_credentials.update({str(found_username): str(found_password)})

    if len(json_credentials) > 1:
        json_credentials = {"credentials": json_credentials}
    elif len(json_credentials) == 1:
        json_credentials = {"username": list(json_credentials.keys())[0],
                            "password": list(json_credentials.values())[0]}
    return json_credentials


def execute(arguments: dict) -> dict:
    """
    Takes arguments in form of dictionary and runs Medusa based on them.

    :param arguments: Arguments from which is compiled and ran medusa command
    :return: Module output containing:
                return_code (0-success, 1-fail, 2-err),
                std_out (raw output),
                mod_out (parsed output that can be used in other modules),
                mod_err (error output)
    """

    # setting default return values
    ret_vals = dict(dict())
    ret_vals.update({"return_code": -1})
    ret_vals.update({"std_out": None})
    ret_vals.update({"mod_err": None})
    ret_vals.update({"mod_out": None})

    # parsing input arguments
    output_file = arguments.get("output_file", False)
    std_out_flag = arguments.get("std_out", False)

    # assembling medusa command
    if "command" in arguments:
        command_input = arguments.get("command")
        command = parse_custom_command(command_input)
        for parameter in command:
            if parameter == '-o':
                output_file = True
    else:
        target = arguments.get("target")
        mod = arguments.get("mod", "ssh")
        tasks = arguments.get("tasks", 4)

        credentials = arguments.get("credentials")
        username = credentials.get("username")
        username_list = credentials.get("username_list")
        password = credentials.get("password")
        password_list = credentials.get("password_list")
        combo_list = credentials.get("combo_list")

        if target is None:
            ret_vals.update({"mod_err": "Target parameter is missing"})
            return ret_vals
        command = ["medusa", "-h", target, "-t", str(tasks)]

        try:
            command += parse_mod(mod)
            if combo_list is None:
                command += parse_username(username, username_list) + parse_password(password, password_list)
            else:
                command += parse_combo_list(combo_list)
        except FileNotFoundError as file_error:
            ret_vals.update({"mod_err": str(file_error)})
            return ret_vals

    # executing medusa bruteforce
    try:
        medusa_process = subprocess.run(command, capture_output=True)
    except FileNotFoundError:
        ret_vals.update({"mod_err": "Check if your command starts with \"medusa\" and is installed."})
        return ret_vals
    except subprocess.SubprocessError:
        ret_vals.update({"mod_err": "Medusa couldn\"t start."})
        return ret_vals

    # reporting results
    medusa_stdout = medusa_process.stdout.decode("utf-8")
    medusa_stderr = medusa_process.stderr.decode("utf-8")
    mod_out = None
    if check_found_credentials(medusa_stdout) is True:
        ret_vals.update({"return_code": 0})
        mod_out = parse_credentials(medusa_stdout)
    if output_file is True:
        ret_vals.update({"file": {"file_name": create_output_file(),
                                  "file_content": medusa_process.stdout}})
        ret_vals.update({"std_out": "Output file saved in evidence dir"})
    elif std_out_flag is True:
        ret_vals.update({"std_out": medusa_stdout})
    ret_vals.update({"mod_out": mod_out})
    ret_vals.update({"mod_err": medusa_stderr})

    return ret_vals
