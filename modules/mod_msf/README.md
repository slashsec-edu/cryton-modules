# mod_msf

Module for orchestrating Metasploit Framework.

## Requirements

System requirements (those not listed in requirements.txt for python).

For this module to function properly, [Metasploit-framework](https://github.com/rapid7/metasploit-framework/wiki/Nightly-Installers) needs to be installed.

After a successful installation of Metasploit-framework, you need to load msgrpc plugin. Easiest way to do this to open your terminal and run `msfrpcd` with `-P toor` to use password and `-S` to turn off SSL (depending on configuration in Worker config file). 

**Optional:**

Another option is to run Metasploit using `msfconsole` and load msgrpc plugin using this command:

````bash
load msgrpc ServerHost=127.0.0.1 ServerPort=55553 User=msf Pass='toor' SSL=true
````

This is just default, feel free to change the parameters to suit your needs, but keep in mind that they must match your worker config file.

After successfully loading the msgrpc plugin, you are all set and ready to use this module.

## Input parameters

Description of input parameters for module.

| Parameter name      | Parameter description                                        |
| ------------------- | ------------------------------------------------------------ |
| `exploit`           | Exploit present in Metasploit library to be used             |
| `exploit_arguments` | Custom list of Metasploit specific arguments (eg. RHOSTS, RPORT) |

As a default value for RHOSTS, Stage "target" is used.

This module can create sessions using our [Cryton session management](https://cryton.gitlab-pages.ics.muni.cz/cryton-project/1.0/scenario/#session-management) feature.

#### Example yaml(s)

```yaml
attack_module_args:
	exploit: auxiliary/scanner/ssh/ssh_login
	exploit_arguments:
		RHOSTS: 127.0.0.1
		USERPASS_FILE: /usr/share/metasploit-framework/data/wordlists/root_userpass.txt
```

## Output