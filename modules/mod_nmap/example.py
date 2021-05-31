from mod import execute, validate

args = {
    "target": "127.0.0.1",
    "ports": [22, 80],
    "options": "-T4",
    "port_parameters": [
        {"portid": "22", "state": "open", "service": {"ostype": "Linux", "product": "OpenSSH"}}
    ]
}

try:
    val_output = validate(args)
    print("validate output: " + str(val_output))
except Exception as ex:
    print(ex)

try:
    ex_output = execute(args)
    print("execute output: " + str(ex_output))
except Exception as ex:
    print(ex)
