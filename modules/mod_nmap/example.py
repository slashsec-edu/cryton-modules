from mod import execute, validate

args = {
    "arguments": {
        "target": "127.0.0.1"
    }
}

try:
    val_output = validate(args.get('arguments'))
    print("validate output: "+str(val_output))
except Exception as ex:
    print(ex)

try:
    ex_output = execute(args)
    print("execute output: "+str(ex_output))
except Exception as ex:
    print(ex)
