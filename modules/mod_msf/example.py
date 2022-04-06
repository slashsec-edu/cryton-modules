from mod import execute, validate

args = {
    "exploit": "auxiliary/scanner/ssh/ssh_login",
    "exploit_arguments":
        {
            "RHOSTS": "192.168.62.98",
            "USERNAME": "vagrant",
            "PASSWORD": "vagrant"
        }
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
