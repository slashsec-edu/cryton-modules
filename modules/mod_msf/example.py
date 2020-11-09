from mod import execute, validate

args = {
    "arguments": {
        "exploit": "auxiliary/scanner/ssh/ssh_login",
        "exploit_arguments":
            {
                "RHOSTS": "127.0.0.1",
                "USERNAME": "vagrant",
                "PASSWORD": "vagrant"
            }
    }
}

try:
    val_output = validate(args.get('arguments'))
    print("validate output: " + str(val_output))
except Exception as ex:
    print(ex)

try:
    ex_output = execute(args)
    print("execute output: " + str(ex_output))
except Exception as ex:
    print(ex)
