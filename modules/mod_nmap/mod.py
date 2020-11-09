import nmap
import csv
import json
from schema import Schema, Optional, And, Use


def validate(step_args):
    """
    Validate input values for the execute function

    :param dict step_args: execute function args.get('arguments')
    :return: 0
    :raises: Schema Exception
    """
    conf_schema = Schema({
        'target': And(str),
        Optional('ports'): [Use(int)],
        Optional('port_parameters'): [{"port": Use(str),
                                       Optional("version"): And(str),
                                       Optional("host"): And(str),
                                       Optional("hostname"): And(str),
                                       Optional("hostname_type"): And(str),
                                       Optional("protocol"): And(str),
                                       Optional("name"): And(str),
                                       Optional("state"): And(str),
                                       Optional("product"): And(str),
                                       Optional("extrainfo"): And(str),
                                       Optional("reason"): And(str),
                                       Optional("conf"): And(str),
                                       Optional("cpe"): And(str)
                                       }],
        Optional('command'): And(str)
    })

    conf_schema.validate(step_args)

    return 0


def execute(args):
    """
    This module runs an nmap scan against target host/subnet.
    The target must be in this format: 1.2.3.4 (target). (may even be 'scanme.nmap.org' or '198.116.0-255.1-127'
    or '216.163.128.20/20')

    Available arguments are:
    * target: scan target

    * ports: a list of ports to scan (optional, default scans most common ports)
        example: "ports": [80, 443]

    *port_parameters: check if the port matches your desired parameters (optional, only works if
                                                                         you add the port in ports)
        options with examples:  "host": "192.168.56.111",
                                "hostname": "example",
                                "hostname_type": "",
                                "protocol": "tcp",
                                "port": "22",
                                "name": "ssh",
                                "state": "open",
                                "product": "OpenSSH",
                                "extrainfo": "Ubuntu Linux; protocol 2.0",
                                "reason": "syn-ack",
                                "version": "5.9p1 Debian 5ubuntu1.10",
                                "conf": "10",
                                "cpe": "cpe:/o:linux:linux_kernel"

        example: "port_parameters": [
                        {"port": 80, "version": "2.2.22"}, {"port": 22, "name": "ssh", "product": "OpenSSH"}
                            ]

    * command: input your own command like in nmap cli
        example: "command": "-p 22 -sV -T4"

    :param dict args: dictionary of mandatory subdictionary 'arguments' and other optional elements
    :return: ret_vals: dictionary with following values:

        * return_code: 0 in success, other number in failure,

        * std_out: return std_out, usually stdout,

        * std_err: error message, if any
    """
    ret_vals = dict(dict())
    ret_vals.update({'return_code': -1})
    ret_vals.update({'std_out': None})
    ret_vals.update({'std_err': None})
    ret_vals.update({'mod_out': None})
    port_array = args.get('arguments').get('ports')
    params_array = args.get('arguments').get('port_parameters')
    command = args.get('arguments').get('command')
    target = args.get('arguments').get('target')

    if command is not None and command != '':
        # parsing command
        ports = ''
        params = ''
        command = command.split(' ')
        save_ports = False
        for arg in command:
            if save_ports is False:
                if arg == '-p':
                    save_ports = True
                elif arg.startswith('-'):
                    params += arg + ' '
            else:
                save_ports = False
                ports = ports.join(arg)

        # starting, running scanner
        nm = nmap.PortScanner()
        try:
            nm.scan(hosts=target, ports=ports, arguments=params, sudo=False)
        except Exception as e:
            ret_vals.update({'return_code': -2})
            ret_vals.update({'std_err': str(e)})
            return ret_vals

        # reading scan results
        out_csv = nm.csv()
        scan_dict = list(csv.DictReader(out_csv.splitlines(), delimiter=';'))

        # evaluating results
        value = list()
        for row in scan_dict:
            if row['state'] == 'open':
                value.append(row)

        # returning result
        ret_vals.update({'return_code': 0})
        ret_vals.update({'mod_out': json.dumps(value)})
        ret_vals.update({'std_out': json.dumps(value)})

    else:
        # parsing input args
        if port_array is not None:
            ports_string = ','.join(list(map(str, port_array)))
        else:
            ports_string = ''

        specific_params_ports = list()
        if params_array is not None:
            for each in params_array:
                specific_params_ports.append(each['port'])

        # starting, running scanner
        nm = nmap.PortScanner()
        if port_array:
            try:
                nm.scan(hosts=target, ports=ports_string, sudo=False)
            except Exception as e:
                ret_vals.update({'return_code': -2})
                ret_vals.update({'std_err': str(e)})
                return ret_vals
        else:
            try:
                nm.scan(hosts=target, sudo=False)
            except Exception as e:
                ret_vals.update({'return_code': -2})
                ret_vals.update({'std_err': str(e)})
                return ret_vals

        # reading scan results
        out_csv = nm.csv()
        scan_dict = list(csv.DictReader(out_csv.splitlines(), delimiter=';'))

        # evaluating results
        result = list()
        mod_out = {'open_ports': dict()}
        ports_output = list()
        for row in scan_dict:
            if row['port'] in specific_params_ports:
                for unique_port in params_array:
                    if unique_port['port'] == row['port']:

                        # checking if requirements are satisfied
                        requirements_satisfied = True
                        for key, value in unique_port.items():
                            if value != row[key]:
                                requirements_satisfied = False
                                break
                        if requirements_satisfied is True:
                            ports_output.append(int(row['port']))
                            break

            else:
                if row['state'] == 'open':
                    ports_output.append(int(row['port']))
                    mod_out['open_ports'] = {**mod_out['open_ports'], **{row['name']: row['port']}}

            result.append(row)
            ret_vals.update({'mod_out': mod_out})
            ret_vals.update({'std_out': json.dumps(result)})

        if port_array is not None:
            if all(x in ports_output for x in port_array):
                return_code = 0
            else:
                return_code = -1
        else:
            if ports_output:  # some open port found
                return_code = 0
            else:
                return_code = -1
        ret_vals.update({'return_code': return_code})

    return ret_vals
