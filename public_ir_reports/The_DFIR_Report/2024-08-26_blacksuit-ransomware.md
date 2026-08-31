---
title: "BlackSuit Ransomware - The DFIR Report"
source_url: "https://thedfirreport.com/2024/08/26/blacksuit-ransomware/"
published: "2024-08-26T00:30:32+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2024-08-26_blacksuit-ransomware.html"
---

# BlackSuit Ransomware - The DFIR Report
## Key Takeaways

- In December 2023, we observed an intrusion that started with the execution of a Cobalt Strike beacon and ended in the deployment of BlackSuit ransomware.

- The threat actor leveraged various tools, including Sharphound, Rubeus, SystemBC, Get-DataInfo.ps1, Cobalt Strike, and ADFind, along with built-in system tools.

- Command and control traffic was proxied through CloudFlare to conceal their Cobalt Strike server.

- Fifteen days after initial access, BlackSuit ransomware was deployed by copying files over SMB to admin shares and executing them through RDP sessions.

- Three rules were added to our private ruleset related to this case.

An audio version of this report can be found on Spotify , Apple , YouTube , Audible , & Amazon .

## The DFIR Report Services

- Private Threat Briefs : Over 20 private DFIR reports annually.

- Threat Feed : Focuses on tracking Command and Control frameworks like Cobalt Strike, Metasploit, Sliver, etc.

- All Intel : Includes everything from Private Threat Briefs and Threat Feed, plus private events, opendir reports, long-term tracking, data clustering, and other curated intel.

- Private Sigma Ruleset : Features 100+ Sigma rules derived from 40+ cases, mapped to ATT&CK with test examples.

- DFIR Labs : Offers cloud-based, hands-on learning experiences, using real data, from real intrusions. Interactive labs are available with different difficulty levels and can be accessed on-demand, accommodating various learning speeds.

Contact us today for pricing or a demo!

#### Table of Contents:

- Case Summary

- Services

- Analysts

- Initial Access

- Execution

- Persistence

- Privilege Escalation

- Defense Evasion

- Credential Access

- Discovery

- Lateral Movement

- Collection

- Command and Control

- Exfiltration

- Impact

- Timeline

- Diamond Model

- Indicators

- Detections

- MITRE ATT&CK

## Case Summary

The intrusion began in December 2023, with the initial sign being the execution of an unusually large-sized Cobalt Strike beacon. After the beacon’s execution, there was no immediate follow-up activity. The initial access delivery method for the intrusion remains unclear, as there was no evidence available. The Cobalt Strike C2 traffic beaconed to IP addresses managed by CloudFlare, which acted as proxy server between the victim network and their team server.

Approximately six hours after the initial execution, the threat actor used Windows utilities, such as systeminfo and nltest to perform enumeration on the system and environment. After, they conducted AS-REP Roasting and Kerberoasting attacks against two of the domain controllers, utilizing Rubeus, which was executed in memory via Cobalt Strike. Following this, the threat actor ran Sharphound in memory through the Cobalt Strike beacon, and saved the output to disk.

Around ten minutes after the initial discovery, the threat actor carried out their first lateral movement. They transferred a Cobalt Strike beacon via SMB and executed it through a service to compromise another workstation. On that workstation, they accessed LSASS to obtain credentials from memory. Throughout the second day of the intrusion, the threat actor deployed multiple Cobalt Strike beacons on workstations and servers and also used RDP for further lateral movement.

The threat actor deployed multiple SystemBC executables on one of the file servers. The second executable, established persistence through a registry run key and opened a new command and control channel. After a busy second day of activity, the intrusion went silent. On the seventh day, the Cobalt Strike command and control domain stopped using CloudFlare and switched to an Amazon AWS IP address, for the remainder of the intrusion.

On the eighth day, the threat actors deployed a new PowerShell Cobalt Strike beacon on a domain controller, this time pointing to a separate command and control server. After two days of inactivity, the intrusion resumed with more Cobalt Strike beacons being distributed, along with several RDP logins. More discovery activity was noticed when Sharphound was executed again. The threat actor attempted multiple times to run ADFind but failed in each instance.

Five days later, the threat actor returned to finalize their objectives. This time, ADFind was executed successfully, followed by the execution of the PowerShell script Get-DataInfo.ps1. The final step was the deployment of the BlackSuit ransomware binary, qwe.exe, which was distributed via SMB to remote systems through the C$ share. The attacker then manually connected to these systems using RDP to execute the ransomware. Upon execution, the ransomware used vssadmin to delete shadow copies before encrypting the hosts. The Time to Ransomware (TTR) was just under 328 hours, spanning 15 calendar days, with files being encrypted and the BlackSuit ransom note left on desktops and folders across the systems.

If you would like to get an email when we publish a new report, please subscribe here . Follow us on LinkedIn for additional insights and notifications!

## Analysts

Analysis and reporting completed by @MetallicHack , @yatinwad , and @malforsec .

## Initial Access

The earliest sign of the threat actor’s presence was the execution of a Cobalt Strike beacon, identified as RtWin64.exe. Despite thorough investigation, the initial access point for the beacon’s deployment could not be determined.

## Execution

### Cobalt Strike PsExec

Cobalt Strike served as the primary tool utilized by the threat actor, with a particular focus on its capabilities that mimic Sysinternals PsExec. These features, including psexec and psexec_psh, enable remote process execution across systems. The psexec module functions by uploading a binary to the target system, then creating and launching a Windows service to execute the file.

The eventID 7045 in Windows System logs shows the services created on the system:

The psexec command spawned a rundll32.exe process.

The psexec_psh module doesn’t copy a binary to the target, but instead executes a PowerShell one-liner. The pattern it uses is %COMSPEC% /b /c start /b /min powershell -nop -w hidden -encodedcommand …

## Persistence

### Registry Run Key

To ensure persistent access to the environment, the threat actor created a run key named “socks5” within the Current User registry hive. The registry key’s configuration indicated that PowerShell would be used to launch a SystemBC backdoor named socks32.exe.

Sysmon eventID 13 ( Registry value set ) shows changes to a registry key value:

One interesting thing to mention is that the registry value name socks5 created under the Run key is hard coded.

The data is a string (type REG_SZ ) which starts with powershell.exe windowstyle -hidden Command concatenated with the current executable name, which is obtained using GetModuleFileNameA with a null hModule first parameter.

### Scheduled Task

SystemBC possesses the ability to create scheduled tasks using COM, as demonstrated in the following example. While other reports have noted SystemBC utilizing this feature, it likely wasn’t employed in our case, as no evidence of scheduled task creation was observed during our investigation.

It first uses the function CoCreateInstance to create an instance of an ITaskScheduler object and then call the method NewWorkItem to create a scheduled task.

## Privilege Escalation

On a workstation that the threat actor moved laterally to, we observed use of named pipes.

Usually, when observing this behavior from Cobalt Strike, this tends to be usage of the getsystem command to elevate privileges; however, in this case we observed the parent process to not be services.exe and the threat actor was already running as SYSTEM. This activity was seen in correlation to pass-the-hash behavior listed in Lateral Movement . The threat actor changed to the context of a domain administrator and then was observed moving laterally again using Cobalt Strike, so we attribute this activity to pass-the-hash command execution activity rather than getsystem.

## Defense Evasion

### Modify Registry

The threat actor employed an encoded PowerShell command to modify the registry, enabling Remote Desktop Protocol (RDP) access to a file server.

Setting the registry key “HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server” DenyTSConnections to 0 will allow terminal server connections to the host.

### Process Injection

Given the threat actor’s extensive use of Cobalt Strike beacons, we anticipated the use of process injection as a method of evading detection by hiding within legitimate processes.

Upon analyzing process injections and access patterns from Cobalt Strike-generated processes, we successfully identified the suspicious activity we were searching for.

These injections can then be confirmed using things like YARA memory scanning:

## Credential Access

The threat actor undertook multiple actions to obtain valid credentials, primarily leveraging Rubeus as the key tool. During our investigation, we discovered that Rubeus had been loaded into mstsc.exe—a process previously injected by Cobalt Strike—functioning as a CLR module .

### AS-REP roasting

AS-REP roasting was the first credential access activity performed by the threat actor. This was done with Rubeus on the beachhead host targeting a domain controller.

Rubeus writing the result of AS-REP roasting output to a file:

Indications of AS-REP roasting can be found by looking for windows eventID 4768 on the target domain controller. The request is for Authentication tickets(TGT) with “Pre-Authentication Type” set to 0, meaning no password is required.

A lot of Kerberos Authentication Tickets were requested during AS-REP Roasting:

### Kerberoasting

The threat actor used Rubeus to conduct a Kerberoasting attack. During this period of time, we observed numerous Kerberos ticket requests, specifically using encryption type 0x17, which corresponds to RC4 encryption. These RC4 encryption requests coincided with the execution of Rubeus and targeted multiple accounts across the domain

Rubeus executed in memory by Cobalt Strike creating kerberoast output:

EventID 4769 on a domain controller showing request for tickets with weak encryption:

### LSASS memory access

The threat actor accessed LSASS memory on a workstation with a specific access request of 0x1010, where 0x0010 is necessary to read memory using ReadProcessMemory. This request originated from a process that had been injected with Cobalt Strike.

Sysmon eventID 10 shows mstsc.exe accessing lsass with the access mask 0x1010

## Discovery

Discovery plays a critical role for the threat actor in assessing the environment they have infiltrated. Throughout the intrusion, the attacker conducted discovery activities across multiple systems, gathering valuable intelligence on the network and its assets.

### Hands On Keyboard

Discovery began on the beachhead host approximately six hours after initial access. The first command executed was “systeminfo,” aimed at gathering details about the local system. Shortly after, the command “nltest /dclist” was issued to identify the domain controllers within the environment.

Sysmon eventID 1 shows evidence of running the commands:

### Sharphound

Once the threat actor identified the domain controllers, they wasted no time and promptly loaded Sharphound into memory via Cobalt Strike. This allowed them to conduct further discovery activities within the environment, expanding their reconnaissance efforts.

We have some proof showing mstsc.exe loading Sharphound as a CLR(Common Language Runtime) module. mstsc.exe is the child process of Cobalt Strike beacon RtWin64.exe. The below screenshot taken from the EDR telemetry depicts that:

Output from Sharphound was stored in “C:\Windows\Temp\Dogi\”. The recurring use of this directory aligns with behaviors documented in a different report, BazarCall to Conti Ransomware chain . This suggests a potential operational signature or TTP (Tactics, Techniques, and Procedures) common to this threat actor group or its operators. Based on the output files created, `it looks like it was run in default mode as described below.

Sysmon eventID 11 showing the files created:

Sharphound appeared to be running in its default mode, which involves enumerating local group memberships by querying the Windows Security Accounts Manager (SAM) database remotely through the samr pipe on the target host. This pipe is exposed via the IPC$ share, and corresponding activity can be detected by monitoring Windows security events with event ID 5145. A similar approach is used to discover logged-on users; however, in this case, Sharphound communicates with the srvsvc pipe, utilizing the Server Service Remote Protocol.

Windows eventlog eventID 5145 showing Sharphound enumeration activity:

When Sharphound enumerates the Active Directory through LDAP searches, it performs an excess amount of queries.

Example of Sharphound LDAP searches:
"(|(samaccounttype=268435456)(samaccounttype=268435457)(samaccounttype=536870912)(samaccounttype=536870913))", "(BuildString("(primarygroupid=*)"
Sharphound executed in memory by Cobalt Strike, performing LDAP queries:

Sharphound was initially executed on the beachhead host. Later in the intrusion, the threat actor ran Sharphound two more times, this time on a domain controller. The output from the first run was saved to “C:\Windows\System32\”, while the second run’s results were directed to “C:\Perflogs\”.

Again Sysmon eventID 11 caught the files created by Sharphound:

Windows Security eventID 4799 shows Sharphound performing discovery on local security-enabled groups:

More information on how Sharphound functions can be found here:

https://blog.compass-security.com/2022/05/bloodhound-inner-workings-part-1

https://blog.compass-security.com/2022/05/bloodhound-inner-workings-part-2

More ways to detect LDAP queries generally in this great article here:

https://falconforce.nl/falconfriday-detecting-active-directory-data-collection-0xff21

### ADFind

ADFind, a tool frequently used by threat actors, was also employed in this intrusion to conduct enumeration and discovery. After gaining access to the second domain controller, the threat actor created “ADFind.exe” and “adf.bat” in an attempt to gather further Active Directory information.

Sysmon eventID 11 showing creation of ADFind.exe and adf.bat by Cobalt Strike:

A few seconds after creation of the files, the threat actor was eager to collect the desired information and executed adf.bat via cmd.exe :

No additional commands were observed after each batch file execution. This indicates the operator may have encountered difficulties, as the batch file was executed twice within just over a minute of the initial attempt, suggesting potential issues or missteps during execution.

Sysmon eventID 11 shows the creation of the files with the output of ADFind:

It’s possible that the files ended up being empty, causing the threat actor to reconsider their approach. About 15 minutes later, the operator tried running ADFind.exe directly from the command line, likely to verify whether the tool would execute properly.

After failing to determine the cause of the issue, the threat actor stayed quiet until the next day. The operator likely made an error by trying to run “ adf.bat ” from “ C:\Windows\System32\ ” when both “adf.bat” and “ADFind.exe” were actually located in “ C:\Perflogs\adf\" . Because of this, “ ADFind.exe ” probably couldn’t be found as an executable in the wrong directory, leading to the error.

After several days, the threat actor decided to give ADFind another try. This time, on the file server the operator was successful in running adf.bat correctly to find ADFind.exe and perform the desired discovery activity:

Sysmon eventID 1 showing threat actor running adf.bat:

Resulting in several adfind.exe process events:

### Get-DataInfo.ps1

The threat actor also used a PowerShell script to enumerate local systems. Together with a batch script called “ start.bat ” the threat actor ran Get-DataInfo.ps1 on both a domain controller and a different servers in the environment. We have seen this PowerShell script used several times before . Interestingly, PowerShell was initiated using the start.bat file. However, the start.bat file did not work as intended and passed the “method” parameter to the Get-DataInfo.ps1 script, which is not recognized as a valid parameter. As a result, it ran in default mode. This behavior may have confused the operator at the keyboard, as well as the batch script that was run several times in a row on both servers.

Sysmon EventID 1 shows start.bat executes Get-DataInfo.ps1 with parameter method:

The start.bat script tries to set a variable called method to the discovery method chosen by the user if the method is not typed on the command line:

The issue with the script arises from the fact that the variable “method” does not receive the user-chosen value until after the IF condition is complete. Additionally, the variable must be referenced as %method% to capture the user input correctly. This oversight explains why the PowerShell command initiating Get-DataInfo.ps1 includes “ method ” as a parameter on the command line:

The below will end up running the Get-DataInfo.ps1 script in default mode:

The default mode will run the Test-LHost , Get-DiskInfo and Get-Software functions in the script before calling the last function, Compress-Result :

Sysmon eventID 1 showing the execution:

Sysmon eventID 1 process create showing several runs of start.bat:

### Windows Utilities

The threat actor performed several discovery commands using various Windows utilities at various times during the intrusion.
C:\Windows\system32\\cmd.exe /C systeminfo C:\Windows\system32\cmd.exe /C net group "domain admins" /domain C:\Windows\system32\cmd.exe /C nltest /dclist <domainname redacted> nltest /domain_trusts /all_trusts C:\Windows\system32\cmd.exe /C net group "enterprise admins" /domain C:\Windows\system32\cmd.exe /C ping <hostname redacted> C:\Windows\system32\taskmgr.exe /4 C:\Windows\system32\cmd.exe /C All windows Import-Module ActiveDirectory Get-ADComputer -Filter {enabled -eq $true} -properties *|select Name, DNSHostName, OperatingSystem, LastLogonDate, IPv4Address | Export-CSV C:\Users\AllWindows.csv -NoTypeInformation -Encoding UTF8 C:\Windows\system32\cmd.exe /C route print C:\Windows\system32\cmd.exe /C ping http://<IP redacted>/

### Administrator Consoles

On the final day of the intrusion, the threat actor accessed the administrative consoles for both DNS and Group Policy. Shortly after, they proceeded to deploy ransomware across the environment.
C:\Windows\system32\mmc.exe C:\Windows\system32\dsa.msc C:\Windows\system32\mmc.exe C:\Windows\System32\gpedit.msc

## Lateral Movement

### Pass the hash

An examination of logon activity within the environment revealed evidence pointing to pass-the-hash attacks. Specifically, Windows Security logs with event ID 4624, showing logon type 9 and the Logon Process listed as “seclogo,” serve as solid indicators of the pass-the-hash technique employed by the threat actor.

The threat actor used three main methods for lateral movement. First, Cobalt Strike utilized SMB ADMIN$ shares to move beacons laterally, along with distributing both SMB and HTTPS beacons. Secondly, they used Remote Desktop Protocol to access a file server and a backup server, where they performed discovery activity. Lastly, the threat actor used the hidden SMB share C$ to distribute the ransomware executable to strategic endpoints within the infrastructure.

A domain controller was used as the main pivot point by the threat actor.

Overview of lateral movement involving SMB ADMIN$ shares and RDP:

To investigate access to the SMB ADMIN$ share, the Windows event log proves invaluable. By examining System event ID 5145, which indicates “A network share object was checked…,” We can track the movement of beacons by the threat actor across the network, gaining essential insight into their lateral movements and activities.

The RDP Activity can be identified with windows security eventID 4624 where the logon type equals 10 RemoteInteractive – “A user logged on to this computer remotely using Terminal Services or Remote Desktop.”

Windows security event ID 5145 was used to demonstrate lateral movement once again, showing SMB C$ share usage.

Cobalt Strike SMB beacons, used for lateral movement, were distributed on the beachhead and on a domain controller:

The configuration of the SMB beacons:
xorkey b'.' 2e 0x0001 payload type 0x0001 0x0002 2 windows-beacon_smb-bind_pipz 0x0002 port 0x0001 0x0002 4444 0x0003 sleeptime 0x0002 0x0004 10000 0x0004 maxgetsize 0x0002 0x0004 2048576 0x0005 jitter 0x0001 0x0002 0 0x0006 maxdns 0x0001 0x0002 0 0x0007 publickey 0x0003 0x0100 30819f300d06092a864886f70d010101050003818d0030818902818100b8783383addbd675fb86964aae676bcaf31237e8cb4edf428d39816f41810d852974f73e9ae1e7fd525c02221b9761a8f157db0728039c1103f31bb8adae4b4fed45f670943616de985e5dfc034982f3eb8ff643db4433fb59f2a45058eeed09af9881931dd32d999279172b79739f60628e57c311f4234fe65ea8eab3b7d19b020301000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 0x0008 server,get-uri 0x0003 0x0100 (NULL ...) 0x0009 useragent 0x0003 0x0080 (NULL ...) 0x000a post-uri 0x0003 0x0040 (NULL ...) 0x000b Malleable_C2_Instructions 0x0003 0x0100 Transform Input: [7:Input] 0x000c http_get_header 0x0003 0x0100 0x000d http_post_header 0x0003 0x0100 0x000e SpawnTo 0x0003 0x0010 (NULL ...) 0x001d spawnto_x86 0x0003 0x0040 '%windir%\\syswow64\\SyncHost.exe' 0x001e spawnto_x64 0x0003 0x0040 '%windir%\\sysnative\\mstsc.exe' 0x000f pipename 0x0003 0x0080 '\\\\.\\pipe\\WkSvcPipeMgr_JORW2e' 0x001f CryptoScheme 0x0001 0x0002 0 0x0037 EXIT_FUNK 0x0001 0x0002 0 0x0028 killdate 0x0002 0x0004 0 0x0025 license-id 0x0002 0x0004 674054486 Stats uniques -> ips/hostnames: 60 publickeys: 47 0x0024 deprecated 0x0003 0x0020 'bfnETSwzb1Xsa2g6gr+auA==' 0x0026 bStageCleanup 0x0001 0x0002 1 0x0027 bCFGCaution 0x0001 0x0002 0 0x0029 textSectionEnd 0x0002 0x0004 1 0x002a ObfuscateSectionsInfo 0x0003 0x0028 '\x00\x10\x00\x00\x95`\x02\x00\x00p\x02\x00À\n\x03\x00\x00\x10\x03\x00\x00Í\x03\x00\x00Ð\x03\x00lî\x03' 0x003a TCP_FRAME_HEADER 0x0003 0x0080 '\x00\x0fk\x1d^ôá±\x81Bª\x1da' 0x0039 SMB_FRAME_HEADER 0x0003 0x0080 '\x00\x1ek\x01oÿ>ñëb±\x1b ×\x85\x8e¥X\x1eOQË©¶¦\x13ø1' 0x002b process-inject-start-rwx 0x0001 0x0002 4 PAGE_READWRITE 0x002c process-inject-use-rwx 0x0001 0x0002 32 PAGE_EXECUTE_READ 0x002d process-inject-min_alloc 0x0002 0x0004 13891 0x002e process-inject-transform-x86 0x0003 0x0100 '\x00\x00\x00U\x0f\x1f\x84\x00\x00\x00\x00\x00\x0f\x1f@\x00\x0f\x1f\x80\x00\x00\x00\x00PX\x0f\x1fD\x00\x00f\x90f\x90\x90\x90f\x0f\x1fD\x00\x00f\x0f\x1f\x84\x00\x00\x00\x00\x00\x0f\x1f\x84\x00\x00\x00\x00\x00\x0f\x1f\x84\x00\x00\x00\x00\x00\x0f\x1f@\x00\x0f\x1fD\x00\x00PXf\x0f\x1fD\x00\x00\x0f\x1fD\x00\x00\x00\x00\x00KPX\x0f\x1fD\x00\x00f\x0f\x1fD\x00\x00PX\x0f\x1fD\x00\x00f\x0f\x1fD\x00\x00f\x90\x90\x0f\x1fD\x00\x00\x0f\x1f\x80\x00\x00\x00\x00f\x90\x90\x90PXPX\x0f\x1fD\x00\x00f\x90\x0f\x1fD\x00\x00\x90\x0f\x1f\x00\x0f\x1fD\x00\x00\x0f\x1fD' 0x002f process-inject-transform-x64 0x0003 0x0100 '\x00\x00\x00\x16f\x90f\x0f\x1fD\x00\x00f\x90\x0f\x1f\x00f\x0f\x1f\x84\x00\x00\x00\x00\x00\x00\x00\x00Zf\x0f\x1f\x84\x00\x00\x00\x00\x00\x0f\x1f\x80\x00\x00\x00\x00\x0f\x1f\x84\x00\x00\x00\x00\x00PX\x0f\x1fD\x00\x00\x0f\x1f\x00f\x0f\x1f\x84\x00\x00\x00\x00\x00\x0f\x1f\x84\x00\x00\x00\x00\x00f\x0f\x1fD\x00\x00\x90f\x0f\x1f\x84\x00\x00\x00\x00\x00\x0f\x1fD\x00\x00\x0f\x1f\x80\x00\x00\x00\x00f\x0f\x1fD\x00\x00\x90\x0f\x1f@' 0x0035 process-inject-stub 0x0003 0x0010 'ÅNí/½Ée\\\x0c\x13U\x0f\x04Ç,(' 0x0033 process-inject-execute 0x0003 0x0080 '\x06\x04\x07\x00\x00\x00\x06ntdll\x00\x00\x00\x00\x13RtlUserThreadStart\x00\x01\x08\x03\x04' 0x0034 process-inject-allocation-method 0x0001 0x0002 0 0x0030 DEPRECATED_PROCINJ_ALLOWED 0x0001 0x0002 1 0x0010 killdate_year 0x0001 0x0002 0 0x004a 0x0003 0x0020 'ÌÑ¶\x8f½ÉeDc~buq®FJô\x16\x9ccß\x82+\td\x7ff_J°\x11\x15' 0x0000 Guessing Cobalt Strike version: 4.4 (max 0x004a)
The threat actor’s use of RDP and tunnels via SystemBC left behind crucial artifacts that helped identify their activities. Notably, we detected two hostnames, “DESKTOP-0MEMSEA” and “DESKTOP-BIFFSC7”, which were used during the intrusion. These artifacts appeared in various logs, including Sysmon event ID 24 (clipboard change), Windows Security event ID 4624 (logon), event ID 4778 (terminal session reconnect), and event ID 4779 (terminal server disconnect), providing multiple points of evidence linking the threat actor’s presence across the environment.

Here is an overview of the RDP sessions where the threat actor used these two hosts:

## Collection

### Archiving

The threat actor used 7z to archive data output from running the Get-DataInfo.ps1 PowerShell script.

Sysmon eventID 1 showing execution of 7z.exe archiving data:

### Looking for interesting files

In their pursuit of valuable data, the threat actor browsed through file systems, selectively opening files they deemed interesting. Documents containing passwords, financial information, and other sensitive data were specifically targeted, as these types of files typically hold high value for the intruders.

Sysmon eventID 1 showing Notepad and Wordpad used to open and look at files:

## Command and Control

For command and control, the threat actor used two main tools, Cobalt Strike and SystemBC.

### Cobalt Strike

Overview of Cobalt Strike traffic beaconing pattern over intrusion:

The initial Cobalt Strike beacon, delivered via RtWin64.exe on the beachhead host, maintained a continuous command and control domain at svchorst[.]com throughout the entire infection. The IP address associated with the domain changed over time, and the communication process also shifted as queries were injected into different processes by RtWin64.exe.

To further obfuscate its presence, the threat actor initially routed the Cobalt Strike command and control traffic through CloudFlare’s CDN service, effectively attempting to hide in plain sight by blending into legitimate web traffic.

The 104[.]21.76.140 and 172[.]67.196.25 addresses belonged to Cloudflare.

Later in the intrusion, the command and control (C2) server moved away from CloudFlare, and subsequently, the domain resolved to an AWS IP address.

DNS queries performed for svchorst[.]com:

Network connections to svchorst[.]com:

Using Didier Steven’s great tool 1768.py , we successfully extracted the configuration of the Cobalt Strike beacon, which validated the host artifacts discovered on the beachhead host.
xorkey b'.' 2e 0x0001 payload type 0x0001 0x0002 8 windows-beacon_https-reverse_https 0x0002 port 0x0001 0x0002 443 0x0003 sleeptime 0x0002 0x0004 50408 0x0004 maxgetsize 0x0002 0x0004 4103260 0x0005 jitter 0x0001 0x0002 30 0x0007 publickey 0x0003 0x0100 30819f300d06092a864886f70d010101050003818d0030818902818100b8783383addbd675fb86964aae676bcaf31237e8cb4edf 428d39816f41810d852974f73e9ae1e7fd525c02221b9761a8f157db0728039c1103f31bb8adae4b4fed45f670943616de985e5dfc034982f3eb8ff643db4433fb59f2a45058eeed09af9881931dd3 2d999279172b79739f60628e57c311f4234fe65ea8eab3b7d19b0203010001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 0x0008 server,get-uri 0x0003 0x0100 'svchorst.com,/shiatzu/v2.41' 0x0043 DNS_STRATEGY 0x0001 0x0002 0 0x0044 DNS_STRATEGY_ROTATE_SECONDS 0x0002 0x0004 -1 0x0045 DNS_STRATEGY_FAIL_X 0x0002 0x0004 -1 0x0046 DNS_STRATEGY_FAIL_SECONDS 0x0002 0x0004 -1 0x000e SpawnTo 0x0003 0x0010 (NULL ...) 0x001d spawnto_x86 0x0003 0x0040 '%windir%\\syswow64\\SyncHost.exe' 0x001e spawnto_x64 0x0003 0x0040 '%windir%\\sysnative\\mstsc.exe' 0x001f CryptoScheme 0x0001 0x0002 0 0x001a get-verb 0x0003 0x0010 'GET' 0x001b post-verb 0x0003 0x0010 'POST' 0x001c HttpPostChunk 0x0002 0x0004 0 0x0025 license-id 0x0002 0x0004 674054486 0x0024 deprecated 0x0003 0x0020 'bfnETSwzb1Xsa2g6gr+auA==' 0x0026 bStageCleanup 0x0001 0x0002 1 0x0027 bCFGCaution 0x0001 0x0002 0 0x0047 MAX_RETRY_STRATEGY_ATTEMPTS 0x0002 0x0004 0 0x0048 MAX_RETRY_STRATEGY_INCREASE 0x0002 0x0004 0 0x0049 MAX_RETRY_STRATEGY_DURATION 0x0002 0x0004 0 0x0009 useragent 0x0003 0x0100 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Sa fari/537.36' 0x000a post-uri 0x0003 0x0040 '/unobservedly/v10.78'
In the rest of the infrastructure, two distinct types of Cobalt Strike beacons were deployed: HTTPS beacons and SMB beacons. The HTTPS beacons appeared to communicate with three different domains—wq[.]regsvcast[.]com, as[.]regsvcast[.]com, and zx[.]regsvcast[.]com—though, in reality, only wq[.]regsvcast[.]com was actively used, resolving to IP address 147.78.47[.]178. This Cobalt Strike server was tracked as active by the DFIR Threat Feeds from December 21st through Jan 6th, 2024.

Sysmon event ID 22 helped document the DNS queries related to the *regsvcast[.]com domains, providing further insight into the network activity tied to the Cobalt Strike infrastructure.

Sysmon event ID 3 logs every network connection made, provided it’s not disabled in the Sysmon configuration. This can be particularly useful, as some EDR solutions apply rate limits to this type of artifact.

Since Cobalt Strike beacons can generate significant traffic, the volume of network connections for each beacon can be observed in the final column of these logs, highlighting the frequency and noisiness of the communication between beacons and command and control infrastructure.

Below is the configuration of the beacon from DC Y which communicated encrypted over https on port 443:
File: b7bcee8.exe payloadType: 0x00002810 payloadSize: 0x00040405 intxorkey: 0xe43ebc19 id2: 0x00000000 MZ header found position 9 Config found: xorkey b'.' 0x0003ac30 0x000403fc 0x0001 payload type 0x0001 0x0002 8 windows-beacon_https-reverse_https 0x0002 port 0x0001 0x0002 443 0x0003 sleeptime 0x0002 0x0004 63612 0x0004 maxgetsize 0x0002 0x0004 2796542 0x0005 jitter 0x0001 0x0002 39 0x0007 publickey 0x0003 0x0100 30819f300d06092a864886f70d010101050003818d0030818902818100a208a5996fa9e52ff4f19fb148b97176ab0a7e2cfc1d59fcc661e4d1afad0c6636fc952b6cab7b88bc62e7c5ad34441750e74eab69ab68acc39f005cfd315edda934ad438245830fd29688df4a4f2b89154cb81ea126d04804015e2660f55136d1cce8fb14126d1677ac0b38746b7a5543753c53dae05552e142d8ba74c34569020301000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 0x0008 server,get-uri 0x0003 0x0100 'qw.regsvcast.com,/hr,as.regsvcast.com,/hr,zx.regsvcast.com,/hr' 0x0043 DNS_STRATEGY 0x0001 0x0002 0 0x0044 DNS_STRATEGY_ROTATE_SECONDS 0x0002 0x0004 -1 0x0045 DNS_STRATEGY_FAIL_X 0x0002 0x0004 -1 0x0046 DNS_STRATEGY_FAIL_SECONDS 0x0002 0x0004 -1 0x000e SpawnTo 0x0003 0x0010 (NULL ...) 0x001d spawnto_x86 0x0003 0x0040 '%windir%\\syswow64\\runonce.exe' 0x001e spawnto_x64 0x0003 0x0040 '%windir%\\sysnative\\runonce.exe' 0x001f CryptoScheme 0x0001 0x0002 0 0x001a get-verb 0x0003 0x0010 'GET' 0x001b post-verb 0x0003 0x0010 'POST' 0x001c HttpPostChunk 0x0002 0x0004 0 0x0025 license-id 0x0002 0x0004 1580103824 Stats uniques -> ips/hostnames: 316 publickeys: 148 0x0026 bStageCleanup 0x0001 0x0002 1 0x0027 bCFGCaution 0x0001 0x0002 0 0x0009 useragent 0x0003 0x0100 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246' 0x000a post-uri 0x0003 0x0040 '/rw' 0x000b Malleable_C2_Instructions 0x0003 0x0100 Transform Input: [7:Input,4,2:338,3,11] Print Remove 338 bytes from begin BASE64 NETBIOS uppercase 0x000c http_get_header 0x0003 0x0200 Const_header Connection: close Const_header Accept-Encoding: br Build Metadata: [7:Metadata,13,3,2:wordpress_logged_in=,6:Cookie] BASE64 URL BASE64 Prepend wordpress_logged_in= Header Cookie 0x000d http_post_header 0x0003 0x0200 Const_header Connection: close Const_header Accept-Language: en-US Const_header Content-Type: text/plain Build Output: [7:Output,3,3,4] BASE64 BASE64 Print Build SessionId: [7:SessionId,3,2:__session__id=,6:Cookie] BASE64 Prepend __session__id= Header Cookie 0x0036 HostHeader 0x0003 0x0080 (NULL ...) 0x0032 UsesCookies 0x0001 0x0002 1 0x0023 proxy_type 0x0001 0x0002 2 IE settings 0x003a TCP_FRAME_HEADER 0x0003 0x0080 '\x00\x04' 0x0039 SMB_FRAME_HEADER 0x0003 0x0080 '\x00\x04' 0x0037 EXIT_FUNK 0x0001 0x0002 0 0x0028 killdate 0x0002 0x0004 0 0x0029 textSectionEnd 0x0002 0x0004 179426 0x002a ObfuscateSectionsInfo 0x0003 0x0028 '\x00À\x02\x00â¸\x03\x00\x00À\x03\x00H\x92\x04\x00\x00\xa0\x04\x00dÀ\x04\x00\x00Ð\x04\x00hß\x04' 0x002b process-inject-start-rwx 0x0001 0x0002 4 PAGE_READWRITE 0x002c process-inject-use-rwx 0x0001 0x0002 32 PAGE_EXECUTE_READ 0x002d process-inject-min_alloc 0x0002 0x0004 18046 0x002e process-inject-transform-x86 0x0003 0x0100 '\x00\x00\x00\x05\x90\x90\x90\x90\x90' 0x002f process-inject-transform-x64 0x0003 0x0100 '\x00\x00\x00\x05\x90\x90\x90\x90\x90' 0x0035 process-inject-stub 0x0003 0x0010 '"+\x8f\'Ûßº\x8dÝU\x9eì¢~¦H' 0x0033 process-inject-execute 0x0003 0x0080 '\x01\x04\x03' 0x0034 process-inject-allocation-method 0x0001 0x0002 0 0x0000 Guessing Cobalt Strike version: 4.3 (max 0x0046) Sanity check Cobalt Strike config: OK Public key config entry found: 0x0003ac65 (xorKey 0x2e) (LSFIF: b'././.,.&.,./.,/') Public key header found: 0x0003ac6b (xorKey 0x2e) (LSFIF: b'././.,.&.,./.,/')
One C2 connection from the Cobalt Strike beacons stands out from the rest: it originates from PowerShell but communicates over HTTP to port 80.

Communicating in clear text gives us the opportunity to look at what is going on. The threat actor used PowerShell to perform the download:

Using Wireshark to view the exact HTTP query to the C2 server:

A PowerShell script was downloaded that decodes a Base64-encoded blob using `FromBase64String`. At the end of the script, the decoded data is decompressed, which can easily be done using tools like `gunzip`. This behavior is highly indicative of a Cobalt Strike PowerShell stager. Upon decoding the Base64 blob, we uncovered another embedded PowerShell script.

This PowerShell script decodes another base64 blob, but as we can see it also performs XOR operations on the bytes. XOR with decimal 35(0x23) is a well known key for Cobalt Strike PowerShell stagers.

After decoding the final base64 blob we get the Cobalt Strike beacon and can get the configuration (as the configuration is the same on all HTTP beacons the config is extracted with csce ):

{ "beacontype": [ "HTTPS" ], "sleeptime": 63612, "jitter": 39, "maxgetsize": 2796542, "spawnto": "AAAAAAAAAAAAAAAAAAAAAA==", "license_id": 1580103824, "cfg_caution": false, "kill_date": null, "server": { "hostname": "qw.regsvcast.com", "port": 443, "publickey": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCiCKWZb6nlL/Txn7FIuXF2qwp+LPwdWfzGYeTRr60MZjb8lStsq3uIvGLnxa00RBdQ506raatorMOfAFz9MV7dqTStQ4JFgw/SlojfSk8riRVMuB6hJtBIBAFeJmD1UTbRzOj7FBJtFnesCzh0a3pVQ3U8U9rgVVLhQti6dMNFaQIDAQABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==" }, "host_header": "", "useragent_header": null, "http-get": { "uri": "/hr", "verb": "GET", "client": { "headers": null, "metadata": null }, "server": { "output": [ "print", "prepend 338 characters", "base64", "netbiosu" ] } }, "http-post": { "uri": "/ch", "verb": "POST", "client": { "headers": null, "id": null, "output": null } }, "tcp_frame_header": "AAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "crypto_scheme": 0, "proxy": { "type": null, "username": null, "password": null, "behavior": "Use IE settings" }, "http_post_chunk": 0, "uses_cookies": true, "post-ex": { "spawnto_x86": "%windir%\\syswow64\\runonce.exe", "spawnto_x64": "%windir%\\sysnative\\runonce.exe" }, "process-inject": { "allocator": "VirtualAllocEx", "execute": [ "CreateThread", "RtlCreateUserThread", "CreateRemoteThread" ], "min_alloc": 18046, "startrwx": false, "stub": "IiuPJ9vfuo3dVZ7son6mSA==", "transform-x86": [ "prepend '\\x90\\x90\\x90\\x90\\x90'" ], "transform-x64": [ "prepend '\\x90\\x90\\x90\\x90\\x90'" ], "userwx": false }, "dns-beacon": { "dns_idle": null, "dns_sleep": null, "maxdns": null, "beacon": null, "get_A": null, "get_AAAA": null, "get_TXT": null, "put_metadata": null, "put_output": null }, "pipename": null, "smb_frame_header": "AAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "stage": { "cleanup": true }, "ssh": { "hostname": null, "port": null, "username": null, "password": null, "privatekey": null } }

### SytemBC

Another command and control channel utilized by the threat actor in this intrusion was SystemBC, a tool frequently favored by ransomware groups. One of its most commonly used features is its proxy functionality. This allowed the threat actor to leverage their own external computers and, through the SystemBC malware deployed on the file server, establish proxy connections to access the local network, facilitating further actions within the compromised environment.

The threat actor first brought in SystemBC as a file named SC.exe. This was executed manually by the threat actor after logging into the file server from DC X.

Security EventID 4624 showing RDP logon and Logon ID:

The threat actor manually started SystemBC with name SC.exe:

Notice that the original name is different and that the LogonID is the same as from the RDP login above.

Shortly after the threat actor brought another SystemBC file, with the name socks32.exe. That was moved to the file server from DC X.

socks32.exe moved over SMB C$ share:

Once again execution is done manually after logging in through RDP.

RDP logon:

Manual execution:

If the SystemBC sample is compiled without modifications, it should be feasible to extract the configuration from the implant by examining the exe file, as all information is presented in plain text.

Port and host configuration for SystemBC in the socks32.exe implant:

## Impact

The threat actor’s primary objective in this case was financial gain through ransom. They introduced an executable named qwe.exe, which we later identified as BlackSuit ransomware.

This ransomware was strategically distributed across key endpoints within the infrastructure and executed, initiating the ransom demands.

Windows security eventID 5145 shows the distribution of the BlackSuit ransom executable via SMB C$ shares:

To avoid any errors during the final stage of their operation, the threat actor refrained from manually typing the command to execute the ransomware with the necessary command line arguments. Instead, to ensure accuracy and eliminate the risk of typos, they also moved a file named 123.txt along with qwe.exe, likely using it as a script or reference to guarantee the correct execution of the ransomware.

Windows security eventID 5145 shows distribution of 123.exe to the c:\users directory:

Movement of the 123.txt file seen from the network side. Including the content. The id is redacted.

After staging the ransomware executable qwe.exe and the helper file 123.txt, the threat actor used RDP from DC X to log onto various systems. Once logged in, they opened 123.txt in Notepad, copied the command from the file, and executed the ransomware. This method ensured the correct command line arguments were used, reducing the risk of mistakes during the final execution phase.

Sysmon eventID 1 showing notepad.exe opening 123.txt:

Sysmon eventID 1 showing execution of qwe.exe

Once the ransomware was executed a lot of ransom notes where created:

readme.blacksuit.txt looked like:

## Timeline

## Diamond Model

## Indicators

### Atomic
SystemBC C2 137.220.61[.]94 Cobalt Strike C2 svchorst[.]com - 15.197.130[.]221 as.regsvcast[.]com - 147.78.47[.]178 zx.regsvcast[.]com - 147.78.47[.]178 qw.regsvcast[.]com - 147.78.47[.]178

### Computed
RtWin64.exe - Cobalt Strike Beacon md5:b5266cd35d1b3770b05 ad6870c0c4bde sha1:2bb6c8b6461edc49e22f3d0c7dc45904b2ed8a2b sha256:55cde638e9bcc335c79c605a564419819abf5d569c128b95b005b2f48ccc43c1 imphash:6015e6e85d0d93e60041fa68c6a89776 7f02ab2.exe - Cobalt Strike Beacon md5:3bf1142b3294c23852852053135ec0df sha1:a3b617eb4248aba34c28c48886116ac97e55e932 sha256:6c884e4a9962441155af0ac8e7eea4ac84b1a8e71faee0beafc4dd95c4e4753f imphash:1b2b0fc8f126084d18c48b4f458c798b 7341ac3.exe - Cobalt Strike Beacon md5:519dc779533b4ff0fc67727fecadba82 sha1:586ea19ea4776300962e20cfc9e7017a50888ecb sha256:a39dc30bd672b66dc400f4633dfa4bdd289b5e79909c2e25e9c08b44d99b8953 imphash:1b2b0fc8f126084d18c48b4f458c798b 61185c1.exe - Cobalt Strike Beacon md5:820cfde780306e759bb434da509f7a91 sha1:4e38b98965a4d4756e6f4a8259df62cbca7de559 sha256:e92912153cf82e70d52203a1a5c996e68b7753818c831ac7415aedbe6f3f007d imphash:1b2b0fc8f126084d18c48b4f458c798b b7bcee8.exe - Cobalt Strike Beacon md5:b54240c98ca23202e58a1580135ad14c sha1:cd55256904f1964b90b51089b46f1a933fec3e8e sha256:27e300fa67828d8ffd72d0325c6957ff54d2dc6a060bbf6fc7aa5965513468e0 imphash:bed5688a4a2b5ea6984115b458755e90 e225857.exe - Cobalt Strike Beacon md5:3900ebc7766f3894fb1eb300460376ad sha1:e63732fb38d2e823348529a264b4c4718e0c0b4a sha256:f474241a5d082500be84a62f013bc2ac5cde7f18b50bf9bb127e52bf282fffbf imphash:bed5688a4a2b5ea6984115b458755e90 7341ac3.exe - Cobalt Strike Beacon md5:519dc779533b4ff0fc67727fecadba82 sha1:586ea19ea4776300962e20cfc9e7017a50888ecb sha256:a39dc30bd672b66dc400f4633dfa4bdd289b5e79909c2e25e9c08b44d99b8953 imphash:1b2b0fc8f126084d18c48b4f458c798b AdFind.exe md5:9b02dd2a1a15e94922be3f85129083ac sha1:2cb6ff75b38a3f24f3b60a2742b6f4d6027f0f2a sha256:b1102ed4bca6dae6f2f498ade2f73f76af527fa803f0e0b46e100d4cf5150682 imphash:4fbf3f084fbbb2470b80b2013134df35 SharpHound.exe md5:76a2363d509cc7174c4abee9a7d7ae68 sha1:286588a50b9b128d07aa0f8851f2d7ee91dfa372 sha256:3b873bc8c7ee12fe879ab175d439b5968c8803fbb92e414de39176e2371896b2 imphash:f34d5f2d4577ed6d9ceec516c1f5a744 socks32.exe md5:ed44877077716103973cbbebd531f38e sha1:ceb8c699a57193aa3be2a1766b03050cde3c738a sha256:9493b512d7d15510ebee5b300c55b67f9f2ff1dda64bddc99ba8ba5024113300 imphash:d66000edfed0a9938162b2b453ffa516 qwe.exe md5:0bb61c0cff022e73b7c29dd6f1ccf0e2 sha1:8dde03600a18a819b080a41effc24f42fa960a3e sha256:60dcbfb30802e7f4c37c9cdfc04ddb411060918d19e5b309a5be6b4a73c8b18a imphash:ecc488e51fbb2e01a7aac2b35d5f10bd

## Detections

### Network
ET CURRENT_EVENTS [Fireeye] HackTool.TCP.Rubeus.[nonce] ET CURRENT_EVENTS [Fireeye] HackTool.TCP.Rubeus.[nonce 2] ET Threatview.io High Confidence Cobalt Strike C2 IP group 3 ET Threatview.io High Confidence Cobalt Strike C2 IP group 2 ET POLICY SMB Executable File Transfer ET RPC DCERPC SVCCTL - Remote Service Control Manager Access ET POLICY SMB2 NT Create AndX Request For a .bat File ET POLICY SMB2 NT Create AndX Request For an Executable File In a Temp Directory ET POLICY Powershell Command With Hidden Window Argument Over SMB - Likely Lateral Movement ET POLICY PE EXE or DLL Windows file download HTTP

### Sigma

Search rules on detection.fyi or sigmasearchengine.com

DFIR Public Rules Repo:
50046619-1037-49d7-91aa-54fc92923604 : AdFind Discovery
DFIR Private Rules:
03be05e6-4977-44cd-8ee4-a79400a5ceb0 : Detection of Cobalt Strike Execution
ded07dbe-bcd4-4d15-a27b-1669445d3215 : Enabling RDP service via reg.exe command execution
feee5785-1381-4119-95d0-ca0c3fffe2f2 : Potential Kerberoasting Attack Detected
f8fd3970-d558-40c8-86e2-a989cd53daea : RDP Session from Host with Default Hostname
194e0132-ddee-433c-ac98-3e544c5a2a3a : Suspicious Powershell Execution in Run Key
Sigma Repo:
903076ff-f442-475a-b667-4f246bcc203b : Nltest.EXE Execution 5cc90652-4cbd-4241-aa3b-4b462fa5a248 : Potential Recon Activity Via Nltest.EXE 9a132afa-654e-11eb-ae93-0242ac130002 : PUA - AdFind Suspicious Execution d5601f8c-b26f-4ab0-9035-69e11a8d4ad2 : CobaltStrike Named Pipe 496a0e47-0a33-4dca-b009-9e6ca3591f39 : Suspicious Kerberos RC4 Ticket Encryption 8eef149c-bd26-49f2-9e5a-9b00e3af499b : Pass the Hash Activity 2 f376c8a7-a2d0-4ddc-aa0c-16c17236d962 : HackTool - Bloodhound/Sharphound Execution 02773bed-83bf-469f-b7ff-e676e7d78bab : BloodHound Collection Files 0d894093-71bc-43c3-8c4d-ecfc28dcf5d9 : Mimikatz Detection LSASS Access a18dd26b-6450-46de-8c91-9659150cf088 : Potentially Suspicious GrantedAccess Flags On LSASS 098d7118-55bc-4912-a836-dc6483a8d150 : Access To ADMIN$ Network Share 61a7697c-cb79-42a8-a2ff-5f0cdfae0130 : Potential CobaltStrike Service Installations - Registry 1d61f71d-59d2-479e-9562-4ff5f4ead16b : Suspicious Service Installation 4aafb0fa-bff5-4b9d-b99e-8093e659c65f : Writing Local Admin Share ca2092a1-c273-4878-9b4b-0d60115bf5ea : Suspicious Encoded PowerShell Command Line 0ef56343-059e-4cb6-adc1-4c3c967c5e46 : Suspicious Execution of Systeminfo bbb7e38c-0b41-4a11-b306-d2a457b7ac2b : Suspicious File Created In PerfLogs 3dfd06d2-eaf4-4532-9555-68aca59f57c4 : Process Execution From A Potentially Suspicious Folder 0d5675be-bc88-4172-86d3-1e96a4476536 : Potential Tampering With RDP Related Registry Keys Via Reg.EXE

### Yara

File Scan Results:

DFIR Report:

https://github.com/The-DFIR-Report/Yara-Rules/compare/26364

https://github.com/search?q=repo%3AThe-DFIR-Report%2FYara-Rules+get-data&type=code

https://github.com/search?q=repo%3AThe-DFIR-Report%2FYara-Rules%20netscan&type=code

YARA Forge :
DITEKSHEN_MALWARE_Win_EXEPWSH_Dlagent ELASTIC_Windows_Trojan_Cobaltstrike_1787Eef5 ELASTIC_Windows_Trojan_Cobaltstrike_7F8Da98A EMBEERESEARCH_Win_Cobaltstrike_Pipe_Strings_Nov_2023 GCTI_Cobaltstrike_Resources_Artifact64_V3_14_To_V4_X
Memory Scan Results:
HKTL_CobaltStrike_SleepMask_Jul22 CobaltStrike_Sleep_Decoder_Indicator Windows_Trojan_CobaltStrike_b54b94ac HKTL_CobaltStrike_Beacon_4_2_Decrypt CobaltStrike_Sleeve_Beacon_x64_v4_4_v_4_5_and_v4_6 Windows_Trojan_CobaltStrike_663fc95d Windows_Trojan_CobaltStrike_3dc22d14 HKTL_CobaltStrike_Beacon_Strings HKTL_Win_CobaltStrike SUSP_PS1_JAB_Pattern_Jun22_1 WiltedTulip_WindowsTask CobaltStrike_Resources_Command_Ps1_v2_5_to_v3_7_and_Resources_Compress_Ps1_v3_8_to_v4_x Cobaltbaltstrike_Payload_Encoded Msfpayloads_msf_ref CobaltStrike_Resources_Template_x64_Ps1_v3_0_to_v4_x_excluding_3_12_3_13 Windows_Shellcode_Generic_8c487e57 Cobaltbaltstrike_RAW_Payload_smb_stager_x86 Windows_Trojan_Metasploit_38b8ceec CobaltStrike_Resources_Smbstager_Bin_v2_5_through_v4_x Windows_Trojan_CobaltStrike_f0b627fc CobaltStrike_Sleeve_BeaconLoader_HA_x64_o_v4_3_v4_4_v4_5_and_v4_6 CobaltStrike_C2_Encoded_XOR_Config_Indicator SUSP_XORed_Mozilla SUSP_PowerShell_IEX_Download_Combo CobaltStrike_Sleeve_Beacon_Dll_v4_3_v4_4_v4_5_and_v4_6 Windows_Trojan_Metasploit_7bc0f998 Windows_Trojan_Metasploit_c9773203
Rule authors:

[email protected]

Elastic Security

[email protected]

[email protected]

Florian Roth (Nextron Systems)

Avast Threat Intel Team

## MITRE ATT&CK

Abuse Elevation Control Mechanism - T1548 Archive Collected Data - T1560 AS-REP Roasting - T1558.004 Data Encrypted for Impact - T1486 Domain Groups - T1069.002 Domain Trust Discovery - T1482 Inhibit System Recovery - T1490 Kerberoasting - T1558.003 LSASS Memory - T1003.001 Malicious File - T1204.002 Modify Registry - T1112 PowerShell - T1059.001 Process Injection - T1055 Proxy - T1090 Registry Run Keys / Startup Folder - T1547.001 Remote Desktop Protocol - T1021.001 Remote System Discovery - T1018 Security Software Discovery - T1518.001 Service Execution - T1569.002 SMB/Windows Admin Shares - T1021.002 Software Discovery - T1518 System Information Discovery - T1082 Web Protocols - T1071.001 Windows Command Shell - T1059.003 Pass the Hash - T1550.002
Internal case #TB29364 #PR31354

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
