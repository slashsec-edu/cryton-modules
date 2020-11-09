# mod_nmap

This module implemets scanning capabilities of Nmap.

It is scanning target's ports. By default it scans the most common ports, returns OK and a list with all ports and their parameters.

With set 'ports' the module is scanning target's ports from the 'ports' list.  If those ports match their parameters in port_parameters (default parameter is "state": "open") the module returns OK and a list with all ports and their parameters.

## Requirements

List of system requirements (those not listed in requirements.txt for python).

For this module to function properly, [Nmap](https://github.com/nmap/nmap) need to be installed.

## Input parameters

Description of input parameters for module.

| Parameter name               | Parameter description                                        |
| ---------------------------- | ------------------------------------------------------------ |
| `target`                     | Scan target                                                  |
| `ports`                      | List of ports to be scanned (default scans most common ports) |
| `port_parameters` (optional) | Check if found ports match your desired parameters. The desired port must be added into 'ports'). Options with examples:  {```"host": "1.1.1.1", "hostname": "host", "hostname_type": "", "protocol": "tcp", "port": 22, "name": "ssh", "state": "open", "product": "OpenSSH", "extrainfo": "Ubuntu Linux; protocol 2.0", "reason": "syn-ack", "version": "5.9p1 Debian 5ubuntu1.10", "conf": "10", "cpe": "cpe:/o:linux:linux_kernel"```}. |
| `command`                    | Input your own command like in Nmap cli. Do not add 'nmap' into the command. Also do not specify target, Cryton's stage target will be used by default. |

#### Example yaml(s)

```yaml
attack_module_args:
  target: 127.0.0.1
  ports:
    - 22
```

```yaml
attack_module_args:
  target: 127.0.0.1
  ports:
    - 22
  port_parameters: [{"port": 22, "name": "ssh", "product": "OpenSSH"}]
```

```yaml
attack_module_args:
  command: -p 22 -sV -T4
```

## Output

Description of output.

| Parameter name   | Parameter description                            |
| ---------------- | ------------------------------------------------ |
| ```open_ports``` | Key:value pairs of open services and their ports |

#### Example

```json
{"mod_out": {"open_ports": {"ssh": "22", "ftp": "21"}}}
```