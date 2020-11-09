# mod_medusa

This module implemets attacking capabilities of Medusa bruteforce tool.

## Requirements

System requirements (those not listed in requirements.txt for python).

For this module to function properly, [Medusa](https://github.com/jmk-foofus/medusa) need to be installed.

## Input parameters

Description of input parameters for module.

| Parameter name  | Parameter description                                        |
| --------------- | ------------------------------------------------------------ |
| `target`        | Bruteforce target (must be set when not using command)       |
| `open_ports`    | Parameter for output of module mod_nmap (see [plan example](https://cryton.gitlab-pages.ics.muni.cz/cryton-project/1.0/plan/)) |
| `mod`           | Specified mod(service) you want to use to attack (default ssh) |
| `report_path`   | Absolute path where you want to save login pairs - default is Cryton evidence folder |
| `username`      | Username to use for bruteforce                               |
| `password`      | Password to use for bruteforce                               |
| `username_list` | Absolute path to file with usernames                         |
| `password_list` | Absolute path to file with passwords                         |
| `combo_list`    | Absolute path to file with login pairs - user:password (official format can be found in http://foofus.net/goons/jmk/medusa/medusa.html) |
| `tasks`         | Total number of login pairs to be tested concurrently, default is 16 |
| `command`       | Medusa arguments with syntax as in command line. Do not write 'medusa' into the command. If you specify '-O' parameter with 'cryton_default' it will save file with passwrods to Cryton's default directory **(if you choose other location, do not specify file name)** and if you specify target parameter (-h) with 'cryton_default' Cryton's stage target will be used (optional). **Cannot be combined with other input parameters!** |

#### Default command

```bash
-u admin -P /usr/share/wordlists/rockyou.txt -O [cryton_evidence_directory] -t 16 -h target -M ssh
```

What does it do? It tries to login with credentials [admin - passwords from file] onto ssh on target with 16 login pair tries concurrently and saves found login pairs into cryton evidence directory (which is automatically generated).

The default command works only on Kali (because of the password list). So if you want to use different password list, or only one password, you can use parameter: 'password' / 'password_list'. It works the same way for any other default parameter.

#### Example yaml(s)

```yaml
attack_module_args:
  target: 1.2.3.4
  username: admin
  password: pass
  tasks: 64
```

```yaml
attack_module_args:
  command: -t 16 -u vagrant -p vagrant -O cryton_default -h 127.0.0.1 -M ssh
```

## Output

Description of output.

| Parameter name | Parameter description                                        |
| -------------- | ------------------------------------------------------------ |
| `username`     | Username found during bruteforce                             |
| `password`     | Password found during bruteforce                             |
| `credentials`  | If there are more than one login credentials found, they are returned in form of user:password pairs |

#### Example

```json
{"mod_out": {"credentials": {"admin": "admin", "root": "toor"}}}
```

```json
{"mod_out": {"username": "admin", "password": "admin"}}
```