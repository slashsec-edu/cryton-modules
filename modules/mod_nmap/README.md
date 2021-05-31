# mod_nmap

This module implemets scanning capabilities of Nmap.

It is scanning target's ports. By default it scans the most common ports and returns a list with all ports and their parameters.

## Requirements

List of system requirements (those not listed in requirements.txt for python).

For this module to function properly, [Nmap](https://github.com/nmap/nmap) need to be installed.

## Input parameters

Description of input parameters for module.

| Parameter name               | Parameter description                                        |
| ---------------------------- | ------------------------------------------------------------ |
| `target`                     | Scan target (eg. 127.0.0.1)                                  |
| `ports` (optional)           | List of ports to be scanned (default scans most common ports) (eg. [80, 443]) |
| `port_parameters` (optional) | Check if found ports match your desired parameters. The desired port must be added into 'ports'). Options with examples:  {`"portid": 22, "host": "127.0.0.1", "protocol": "tcp", "state": "open", "reason":"syn-ack", "service": {"name": "ssh", "product": "OpenSSH", "version": "8.4p1 Debian 3", "extrainfo": "protocol 2.0", "ostype": "Linux", "method": "probed", "conf": "10"}, "cpe": "cpe:/o:linux:linux_kernel"`}. |
| `options` (optional)         | Additional Nmap parameters (parameter -sV already included) (eg. -T4) |
| `output_file` (optional) | Flag whether you want to save the output to a file in Cryton evidence directory (eg. true, false(default)) |
| `std_out` (optional) | Flag whether you want to return `std_out`(raw nmap output) (eg. true, false(default)) |

### Example yaml(s)

```yaml
attack_module_args:
  target: 127.0.0.1
  ports:
    - 22
    - 21
  port_parameters:
    - portid: 22
      state: open
      service:
        product: OpenSSH
        ostype: Linux
  options: -T4
```

## Output

Description of module output.

| Parameter name | Parameter description                                        |
| -------------- | ------------------------------------------------------------ |
| `return_code`  | 0 - success<br />-1 - fail                 |
| `std_out`      | Raw output of Nmap scan                                      |
| `mod_err`      | Error while running Nmap scan                                |
| `mod_out`      | Parsed module output with useful data that can be used as input for some modules, for example filtered ports with `port_parameters` input parameter |

### Example

```
{
    'return_code': 0, 
    'std_out': {'127.0.0.1': {'osmatch': {}, 'ports': [{'protocol': 'tcp', 'portid': '22', 'state': 'open', 'reason': 'syn-ack', 'reason_ttl': '0', 'service': {'name': 'ssh', 'product': 'OpenSSH', 'version': '8.1p1 Debian 1', 'extrainfo': 'protocol 2.0', 'ostype': 'Linux', 'method': 'probed', 'conf': '10'}, 'cpe': [{'cpe': 'cpe:/o:linux:linux_kernel'}], 'scripts': []}, {'protocol': 'tcp', 'portid': '80', 'state': 'closed', 'reason': 'conn-refused', 'reason_ttl': '0', 'service': {'name': 'http', 'method': 'table', 'conf': '3'}, 'scripts': []}], 'hostname': [{'name': 'localhost', 'type': 'PTR'}], 'macaddress': None, 'state': {'state': 'up', 'reason': 'conn-refused', 'reason_ttl': '0'}}, 'stats': {'scanner': 'nmap', 'args': '/usr/bin/nmap -oX - -sV -T4 -p22,80 127.0.0.1', 'start': '1614274118', 'startstr': 'Thu Feb 25 18:28:38 2021', 'version': '7.80', 'xmloutputversion': '1.04'}, 'runtime': {'time': '1614274119', 'timestr': 'Thu Feb 25 18:28:39 2021', 'elapsed': '0.26', 'summary': 'Nmap done at Thu Feb 25 18:28:39 2021; 1 IP address (1 host up) scanned in 0.26 seconds', 'exit': 'success'}}, 
    'mod_err': None, 
    'mod_out': {'127.0.0.1': {'osmatch': {}, 'ports': [{'protocol': 'tcp', 'portid': '22', 'state': 'open', 'reason': 'syn-ack', 'reason_ttl': '0', 'service': {'name': 'ssh', 'product': 'OpenSSH', 'version': '8.4p1 Debian 3', 'extrainfo': 'protocol 2.0', 'ostype': 'Linux', 'method': 'probed', 'conf': '10'}, 'cpe': [{'cpe': 'cpe:/o:linux:linux_kernel'}], 'scripts': []}], 'hostname': [{'name': 'localhost', 'type': 'PTR'}], 'macaddress': None, 'state': {'state': 'up', 'reason': 'conn-refused', 'reason_ttl': '0'}}}
}
```