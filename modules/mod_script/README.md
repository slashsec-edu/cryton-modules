# mod_script

Module for running custom scripts.

## System requirements

System requirements (those not listed in requirements.txt for python).

None.

## Input parameters

Description of input parameters for module.

| Parameter name | Parameter description                                        |
| -------------- | ------------------------------------------------------------ |
| `file`         | Full path to the script                                      |
| `args`         | Optional args for script                                     |
| `output_file` (optional)  | Where should be output file of module be stored, if not defined, output will be in the report file |
| `timeout`      | For how long - in seconds - the script should run (overrides args), if not set, module waits until the script finishes |
| `version`      | Which python version should run the script, default is python 3 |

#### Example yaml(s)

```yaml
attack_module_args:
  file: /root/example.py
  args: -t 10.10.10.5
  output_file: /tmp/
  timeout: 30
  version: 3
```

## Output

Description of output.

| Parameter name | Parameter description                |
| -------------- | ------------------------------------ |
| `report_file`  | File that containts output of module |

#### Example

```json
{"mod_out": "path/to/file"}
```