from mod import execute, validate

args = {
    "module_type": "auxiliary",
    "module_name": "scanner/ssh/ssh_login",
    "module_options":
        {
            "RHOSTS": "172.28.128.99",
            "USERNAME": "vagrant",
            "PASSWORD": "vagrant",
        },
    "run_as_job": False,
    # "session_id": "1",
    "create_named_session": "some_name",
    "exploit_timeout_in_sec": 30,  # default 60
    "exploit_retries": 3,          # default 1
    "session_timeout_in_sec": 10,  # default 60
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
