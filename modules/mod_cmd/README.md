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
| `output_file` (optional) | Where should be output file of module be stored, if not defined, output will be in the report file |

This module can use existing sessions with our [Cryton session management](https://cryton.gitlab-pages.ics.muni.cz/cryton-project/1.0/scenario/#session-management) feature.

#### Example yaml(s)

``` yaml
attack_module_args:
  cmd: cat /etc/passwd
  output_file: /tmp/
```

## Output

Description of output.

| Parameter name  | Parameter description                                   |
| --------------- | ------------------------------------------------------- |
| `file_contents` | File that contains output of command in `cmd` parameter |

#### Example

**With `output_file` parameter:**

```json
{"mod_out": {"file_contents": "path/to/file"}}
```

**Without `output_file` parameter:**

```json
{"mod_out": {"cmd_out": "command output"}}
```

