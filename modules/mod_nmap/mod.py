import json
from typing import Optional as OptionalType
import re
import nmap3
import datetime
import random
import string
from schema import Schema, Optional, And, Use
from copy import deepcopy


def validate(arguments: dict) -> int:
    """
    Validate input values for the execute function.

    :param arguments: Arguments for module execution
    :return: 0 If arguments are valid
    :raises: Schema Exception
    """
    conf_schema = Schema({
        'target': And(str),
        Optional("output_file"): And(bool),
        Optional("std_out"): And(bool),
        Optional('ports'): [Use(int)],
        Optional('port_parameters'): [
            {
                Optional("portid"): Use(str),
                Optional("host"): And(str),
                Optional("protocol"): And(str),
                Optional("state"): And(str),
                Optional("reason"): And(str),
                Optional("cpe"): And(str),
                Optional("service"):
                    {
                       Optional("name"): Use(str),
                       Optional("product"): Use(str),
                       Optional("version"): Use(str),
                       Optional("extrainfo"): Use(str),
                       Optional("ostype"): Use(str),
                       Optional("method"): Use(str),
                       Optional("conf"): Use(str),
                    }
            }
        ],

        Optional('options'): And(str),
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
    return "nmap_report" + time_stamp + file_tail + ".txt"


def execute_scan(target: str, options: OptionalType[str], ports: OptionalType[list]) -> dict:
    """
    Executes Nmap scan from predefined parameters.
    :param target: Target of nmap scan
    :param options: Additional Nmap parameters
    :param ports: Specific ports for scan
    :return: Parsed Nmap scan result
    """
    nm = nmap3.Nmap()
    arguments = ''
    if options is not None:
        arguments = options
    if ports is not None:
        ports_string = ' -p' + ','.join(list(map(str, ports)))
        arguments += ports_string
        return nm.nmap_version_detection(target=target, args=arguments)
    return nm.scan_top_ports(target=target, default=1000, args=arguments)


def filtering_ports(scan_result: dict, desired_port_parameters: list) -> dict:
    """
    Filtering ports that are open and meets desired_port_parameters if specified.

    :param scan_result: Ports with a specific parameters that you want to return
    :param desired_port_parameters: Output of scan_from_parameters function
    :return: Open ports that meets desired_port_parameters if not None
    """
    for key in scan_result.keys():
        if re.match("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", key):
            ports_result = deepcopy(scan_result[key]['ports'])
            for port in ports_result:
                for each_port in desired_port_parameters:
                    # check if host in port_parameters is in scan result if target is subnet
                    if check_desired_parameters(each_port, port) is False:
                        scan_result[key]['ports'].remove(port)
                        pass

    return scan_result


def check_desired_parameters(desired_port: dict, port_results: dict) -> bool:
    """
    Check if port meets given desired parameters and if then yes return True or else return False.

    :param desired_port: Desired parameters that port should meet
    :param port_results: Parameters of specific port found by scan
    :return: Bool value representing whether desired port parameters match any found port in scan result
    """
    for key, value in desired_port.items():
        if key in port_results.keys():
            if key == 'service':
                for service_key, service_value in desired_port[key].items():
                    if service_key in port_results[key].keys():
                        if service_value.lower() != port_results[key][service_key].lower():
                            return False
            else:
                if key == 'cpe':
                    cpes = []
                    for cpe in port_results['cpe']:
                        cpes.append(cpe['cpe'])
                    if value not in cpes:
                        return False
                else:
                    if value.lower() != port_results[key].lower():
                        return False
    return True


def parse_modout(nmap_result: dict):
    """
    Deletes unnecessary info from nmap scan result.

    @param nmap_result: raw nmap scan output
    @return: Nmap scan output without stats and runtime info
    """
    mod_out = deepcopy(nmap_result)
    del mod_out["stats"]
    del mod_out["runtime"]
    return mod_out


def execute(arguments: dict) -> dict:
    """
    Takes arguments in form of dictionary and runs Nmap based on them.

    :param arguments: Arguments from which is compiled and ran nmap command and parsed wanted output
    :return: Module output containing:
                return_code (0-success, 1-fail, 2-err),
                std_out (raw output),
                mod_out (parsed output that can be used in other modules),
                mod_err (error output)
    """
    ret_vals = dict(dict())
    ret_vals.update({'return_code': -1})
    ret_vals.update({'std_out': None})
    ret_vals.update({'mod_err': None})
    ret_vals.update({'mod_out': None})

    port_array = arguments.get('ports')
    port_parameters = arguments.get('port_parameters')
    options = arguments.get('options')
    target = arguments.get('target')
    output_file = arguments.get('output_file', False)
    std_out_flag = arguments.get('std_out', False)

    try:
        result = execute_scan(target, options, port_array)
    except Exception as err:
        ret_vals.update({'mod_err': str(err)})
        return ret_vals

    mod_out = parse_modout(result)
    if port_parameters is not None:
        mod_out = filtering_ports(result, port_parameters)

    if output_file is True:
        ret_vals.update({"file": {"file_name": create_output_file(),
                                  "file_content": json.dumps(result).encode('utf-8')}})
        ret_vals.update({"std_out": "Output file saved in evidence dir"})
    elif std_out_flag is True:
        ret_vals.update({'std_out': result})

    ret_vals.update({'mod_out': mod_out})
    ret_vals.update({'return_code': 0})

    return ret_vals
