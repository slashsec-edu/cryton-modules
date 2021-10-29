from mod import execute, validate

args = {
    "file": "/tmp/test.py",
    "executable": "python3",
    "timeout": 30,
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
