# mod_cmd

Module for running shell commands (depending on the shell used). When specifying "use_session" or "use_named_session", the command will be executed in the respective sessions context, eg. meterpreter.

## Requirements

System requirements (those not listed in requirements.txt for python).

### **For use with sessions only**

For this module to function properly, [Metasploit-framework](https://github.com/rapid7/metasploit-framework/wiki/Nightly-Installers) needs to be installed.

After a successful installation of Metasploit-framework, you need to load msgrpc plugin. Easiest way to do this to open your terminal and run `msfrpcd` with `-P toor` to use password and `-S` to turn off SSL (depending on configuration in Worker config file). 

**Optional:**

Another option is to run Metasploit using `msfconsole` and load msgrpc plugin using this command:

````bash
load msgrpc ServerHost=127.0.0.1 ServerPort=55553 User=msf Pass='toor' SSL=true
````

This is just default, feel free to change the parameters to suit your needs, but keep in mind that they must match your worker config file.

After successfully loading the msgrpc plugin, you are all set and ready to use this module.

## Input parameters

Description of input parameters for module.

| Parameter name   | Parameter description  |
| ---------------- | ---------------------- |
| `cmd` (required) | Command to be executed |
| `end_check` (optional) | String that is checked regularly to determine whether the command execution finished |
| `session_id` (optional) | Msf session in which command should be executed |
| `output_file`(optional)     | Flag whether you want to save the output to a file in Cryton evidence directory (eg. true, false(default)) |
| `std_out` (optional) | Flag whether you want to return `std_out`(raw output of command) (eg. true, false(default)) |

This module can use existing sessions with our [Cryton session management](https://cryton.gitlab-pages.ics.muni.cz/cryton-project/1.0/scenario/#session-management) feature.

#### Example yaml(s)

``` yaml
attack_module_args:
  cmd: cat /etc/passwd; echo end_check_string
  end_check: end_check_string
  session_id: 1
```

## Output

Description of module output.

| Parameter name | Parameter description                                        |
| -------------- | ------------------------------------------------------------ |
| `return_code`  | 0 - success<br />-1 - fail                    |
| `std_out`      | Raw result of command                             |
| `mod_err`      | Error while running module                        |
| `mod_out`      | Module output that can be used as input for some modules |

### Example

```
{
    'return_code': 0, 
 	'std_out': 'contents of passwd file on target'
 	'mod_err': '', 
 	'mod_out': same as std_out
}
```