# mod_medusa

This module implements attacking capabilities of Medusa bruteforce tool.

## Requirements

System requirements (those not listed in requirements.txt for python).

For this module to function properly, [Medusa](https://github.com/jmk-foofus/medusa) need to be installed.

## Input parameters

Description of input parameters for module.

| Parameter name           | Parameter description                                        |
| ------------------------ | ------------------------------------------------------------ |
| `target`                 | Bruteforce target (must be set when not using command)       |
| `mod` (optional)         | Specified mod(service) you want to use to attack (default ssh) |
| `output_file` (optional) | Flag whether you want to save the output to a file in Cryton evidence directory (eg. true, false(default)) |
| `std_out` (optional) | Flag whether you want to return `std_out`(raw medusa output) (eg. true, false(default)) |
| `credentials` (optional) | Parameters that can be used under this key are in table below (default are wordlists in module folder) |
| `tasks` (optional)       | Total number of login pairs to be tested concurrently (default is 4) |

Parameters that can be used under `credentials`.

| Parameter name  | Parameter description                                        |
| --------------- | ------------------------------------------------------------ |
| `username`      | Username to use for bruteforce                               |
| `password`      | Password to use for bruteforce                               |
| `username_list` | Absolute path to file with usernames (default is username wordlist in mod folder) |
| `password_list` | Absolute path to file with passwords (default is password wordlist in mod folder) |
| `combo_list`    | Absolute path to file with login pairs - user:password (official format can be found in http://foofus.net/goons/jmk/medusa/medusa.html). **Cannot be combined with other input parameters under `credentials`!** |

Parameters for custom command usage

| Parameter name           | Parameter description                                        |
| ------------------------ | ------------------------------------------------------------ |
| `command`                | Medusa command with syntax as in command line. If you specify '-o' parameter `output_file` will be True. **Cannot be combined with other input parameters!** |
| `output_file` (optional) | Flag whether you want to save the output to a file in Cryton evidence directory (eg. true, false(default)) |

#### Example yaml(s)

```yaml
attack_module_args:
  target: 127.0.0.1
  credentials:
    username: admin
    password: pass
  tasks: 4
```

```yaml
attack_module_args:
  target: 127.0.0.1
  credentials:
    combo_list: absolute/path/to/file
  tasks: 4
```

```yaml
attack_module_args:
  command: medusa -t 4 -u vagrant -p vagrant -O cryton_default -h 127.0.0.1 -M ssh
```

## Output

Description of module output.

| Parameter name | Parameter description                                        |
| -------------- | ------------------------------------------------------------ |
| `return_code`  | 0 - success<br />-1 - fail                   |
| `std_out`      | Raw output of hydra bruteforce                               |
| `mod_err`      | Error while running hydra bruteforce                         |
| `mod_out`      | Parsed module output with useful data that can be used as input for some modules |

### Mod_out

Description of `mod_out` output parameter

| Parameter name | Parameter description                                        |
| -------------- | ------------------------------------------------------------ |
| `username`     | Username found during bruteforce                             |
| `password`     | Password found during bruteforce                             |
| `credentials`  | If there are more than one login credentials found, they are returned in form of user:password pairs |

### Example

```
{
    'return_code': 0, 
    'std_out': 'Medusa v2.2 [http://www.foofus.net] (C) JoMo-Kun / Foofus Networks <jmk@foofus.net>\n\nACCOUNT CHECK: [ssh] Host: 127.0.0.1 (1 of 1, 0 complete) User: admin (1 of 1, 0 complete) Password: pass (1 of 1 complete)\nACCOUNT FOUND: [ssh] Host: 127.0.0.1 User: vagrant Password: vagrant [SUCCESS]\n', 
    'mod_err': '', 
    'mod_out': {'username': 'admin', 'password': 'pass'}
}
```