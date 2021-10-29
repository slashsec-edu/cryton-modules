# mod_wpscan

This module runs WPScan on given target and returns a file with found vulnerabilities.

**TODO**: update output

## System requirements

System requirements (those not listed in requirements.txt for python).

For this module to function properly, [WPScan](https://gitlab.com/kalilinux/packages/wpscan) needs to be installed.

## Input parameters

Description of input parameters for module.

| Parameter name       | Parameter description                                        |
| -------------------- | ------------------------------------------------------------ |
| `target`             | Scan target (must be set when not using command)             |
| `prefix` (optional)  | What prefix you want to add to your target (example: 'http://') |
| `tail` (optional)    | What tail you want to add to your target (examples: ':8000'; ':8000/index.php') |
| `command` (optional) | WPScan command arguments with syntax as in command line (if not defined default command is used) |
| `report_type`        | How will the output look like. (json - machine readable / standard - human readable and default option) |
| `report_path`        | Absolute path to the generated file(s) (default is Cryton's evidence directory) |

#### Default command

It scans the target and returns a file with found vulnerabilities in defined report type.

```bash
--url [target] -o [report_file] -f [report_type]
```

#### Example yaml(s)

```yaml
attack_module_args:
  command: --url http://127.0.0.1
```

## Output

Description of output.

| Parameter name | Parameter description         |
| -------------- | ----------------------------- |
| `report`_file  | File containing module output |

#### Example

```json
{'report_file': 'path/to/file'}
```
