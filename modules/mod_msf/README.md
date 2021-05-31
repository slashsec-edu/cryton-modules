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
| `std_out` (optional) | Flag whether you want to return `std_out`(raw metasploit output) (eg. true, false(default)) |
| `exploit_arguments` | Custom list of Metasploit specific arguments (eg. RHOSTS, RPORT) |

As a default value for RHOSTS, Stage "target" is used.

This module can create sessions using our [Cryton session management](https://cryton.gitlab-pages.ics.muni.cz/cryton-project/1.0/scenario/#session-management) feature.

### Example yaml(s)

```yaml
attack_module_args:
	exploit: auxiliary/scanner/ssh/ssh_login
	exploit_arguments:
		RHOSTS: 127.0.0.1
		USERPASS_FILE: /usr/share/metasploit-framework/data/wordlists/root_userpass.txt
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