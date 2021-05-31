

[TOC]

# Cryton modules

## Description

Attack modules is a collection of Python scripts with goal of orchestrating known offensive security tools (Nmap, Metasploit, THC Hydra etc.). Although this is their intended purpose, they are still Python scripts, and therefore any custom made script can be used in similar way.

Attack modules get executed inside Step objects using Cryton Worker. All provided arguments are given to the Attack module.

As mentioned above, Cryton Worker is used for validating and executing modules and in order for them to work you have to install their requirements. To do that you either install them manually inside Cryton Worker's environment or you use Cryton Worker's CLI: `cryton-worker start --install-requirements`. If this flag is specified each *requirements.txt* file inside the Worker's modules directory will be check and installed.

## Installation

```
cryton-worker start --install-requirements
```

# Creating modules

To be able to execute a module (Python script), you have to follow few rules:
- Each module must have its own directory with its name.
- Name your script (module) `mod.py`.
- Your module must contain an `execute` function which takes *dict* argument and returns *dict* argument. It's an entry point for executing it.
- Your module should contain a `validate` function which takes *dict* argument, validates it and returns 0 if it's okay, else raises an exception.

Path example:  
`/CRYTON_WORKER_MODULES_DIR/my-module-name/mod.py`

Where:  
- **CRYTON_WORKER_MODULES_DIR** has to be the same path as is defined in *CRYTON_WORKER_MODULES_DIR* environmental variable.
- **my-module-name** is the directory containing your module.
- **mod.py** is your main module file.

Module (`mod.py`) simple example:  
```python
def validate(arguments: dict) -> int:
    if arguments != {}:
        return 0  # If arguments are valid.
    raise Exception("No arguments")  # If arguments aren't valid.

def execute(arguments: dict) -> dict:
    # Do stuff.
    return {"return_code": 0, "mod_out": ["x", "y"]}

```

## Input parameters

Every module has its own input parameters specified. These input parameters are given as a dictionary to the 
module `execute` (when executing the module) or `validate` (when validating the module parameters) function. 

## Output parameters

Every attack module returns a dictionary with following keys:

| Parameter name | Parameter meaning                                            |
| -------------- | ------------------------------------------------------------ |
| `return_code`  | Numeric representation of result (0, -1, -2) <br />0 (OK) means the module finished successfully<br />-1 (FAIL) means the module finished unsuccessfully<br />-2 (EXCEPTION) means the module finished with an error |
| `mod_out`      | Parsed output of module. Eg. for bruteforce module, this might be a list of found usernames and passwords. |
| `mod_err`      | Error message with description of the problem. |
| `std_out`      | Standard output (```std_out```) of any executed command (but mostly None) |
| `std_err`      | Standard error (```std_err```) of any executed command (but mostly None) |
| `file`         | A module can also return a file. It has to be a Python dictionary with keys `file_name` and `file_content` (optionally `file_encoding`, which can contain only `"base64"` or `None`). The file will be stored on the machine running Cryton Core. |

## Prebuilt functionality
Worker provides prebuilt functionality (limited for now) to make building modules easier. Import it using:
```python
from cryton_worker.lib.util import module_util
```

It gives you access to:
- **Metasploit** class which is a wrapper for *MsfRpcClient* from *[pymetasploit3](https://pypi.org/project/pymetasploit3/)*.  
  Examples:
  ```python
  from cryton_worker.lib.util.module_util import Metasploit
  msf_obj = Metasploit().get_target_sessions("target_ip")
  ```
  ```python
  from cryton_worker.lib.util.module_util import Metasploit
  msf_obj = Metasploit().msf_client.add_perm_token()
  ```
- **get_file_binary** function to get file as binary.  
  Example:
  ```python
  from cryton_worker.lib.util.module_util import get_file_binary
  my_file_content = get_file_binary("/path/to/my/file")
  ```
- **File** class used with *[schema](https://pypi.org/project/schema/)* for validation if file exists.
  Example:
  ```python
  from schema import Schema
  from cryton_worker.lib.util.module_util import File
  schema = Schema(File(str))
  schema.validate("/path/to/file")
  ```
- **Dir** class used with *[schema](https://pypi.org/project/schema/)* for validation if directory exists.
  Example:
  
  ```python
  from schema import Schema
  from cryton_worker.lib.util.module_util import Dir
  schema = Schema(Dir(str))
  schema.validate("/path/to/directory")
  ```


## Module example
```python
from schema import Schema
from cryton_worker.lib.util.module_util import get_file_binary, File


def validate(arguments: dict) -> int:
    """
    Validate input arguments for the execute function.
    :param arguments: Arguments for module execution
    :raises: schema.SchemaError
    :return: 0 If arguments are valid
    """
    conf_schema = Schema({
        'path': File(str),
    })

    conf_schema.validate(arguments)
    return 0


def execute(arguments: dict) -> dict:
    """
    This attack module can read a local file.
    Detailed information should be in README.md.
    :param arguments: Arguments for module execution
    :return: Generally supported output parameters (for more information check Cryton Worker README.md)
    """
    # Set default return values.
    ret_vals = dict()
    ret_vals.update({'return_code': -1})
    ret_vals.update({'mod_out': None})
    ret_vals.update({'mod_err': None})

    # Parse arguments.
    path_to_file = arguments.get("path")

    try:  # Try to get file's content as binary.
        my_file = get_file_binary(path_to_file)
    except Exception as ex:  # In case of fatal error (expected) update mod_err.
        ret_vals.update({'mod_err': str(ex)})
        return ret_vals

    ret_vals.update({'return_code': 0})  # In case of success update return_code to '0' and send file to Cryton Core.
    ret_vals.update({'file': {"file_name": "my_file", "file_content": my_file}})
    return ret_vals

```

