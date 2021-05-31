from mod import execute, validate

args = {
    "target": "127.0.0.1",
    "credentials": {
        "username": "vagrant",
        "password": "vagrant",
    }
}

args2 = {
    "command": "medusa -t 4 -u vagrant -p vagrant -h 127.0.0.1 -M ssh"
}

try:
    val_output = validate(args)
    print("validate output: "+str(val_output))
except Exception as ex:
    print(ex)

try:
    ex_output = execute(args)
    print("execute output: "+str(ex_output))
except Exception as ex:
    print(ex)
