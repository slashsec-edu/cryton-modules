from mod import execute, validate

args = {
    "cmd": "cat /etc/passwd",
    "session_id": '1'  # needs active session
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
