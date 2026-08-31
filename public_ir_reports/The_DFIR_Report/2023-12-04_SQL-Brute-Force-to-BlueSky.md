---
title: "SQL Brute Force Leads to BlueSky Ransomware - The DFIR Report"
source_url: "https://thedfirreport.com/2023/12/04/sql-brute-force-leads-to-bluesky-ransomware/"
published: "2023-12-04T01:55:56+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2023-12-04_SQL-Brute-Force-to-BlueSky.html"
---

# SQL Brute Force Leads to BlueSky Ransomware - The DFIR Report
In December 2022, we observed an intrusion on a public-facing MSSQL Server, which resulted in BlueSky ransomware. First discovered in June 2022 , BlueSky ransomware has code links to Conti and Babuk ransomware.

While other reports point to malware downloads as initial access, in this report the threat actors gained access via a MSSQL brute force attack. They then leveraged Cobalt Strike and Tor2Mine to perform post-exploitation activities. Within one hour of the threat actors accessing the network, they deployed BlueSky ransomware network wide.

## Case Summary

In the month of December 2022, we observed a cluster of activity targeting MSSQL servers. The activity started with brute force password attempts for the MS SQL “sa” (System Administrator) account on an internet facing server. Upon successfully discovering the password, the threat actors enabled “xp_cmdshell” on the SQL server. The “xp_cmdshell” allows users with sysadmin privilege to execute shell commands on the host.

Using “xp_cmdshell” the threat actors first executed a PowerShell command on the SQL server. The command contained base64 encoded content, which, upon execution, established a connection to a Cobalt Strike command and control server. This activity was immediately followed by injection into the legitimate process winlogon. The injected process then spawned PowerShell and cmd to perform SMB scans and discovery using SMBexec .

The PowerShell session was then seen making a connection to a Tor2Mine stager server. This was followed by execution of a PowerShell script which performed a variety of operations, such as checking privileges of the active user, disabling of AV solutions, and dropping of a miner payload named java.exe. Tor2Mine is a Monero-mining campaign that is based on XMRigCC. Depending upon the privileges of the user, the script also performs creation of scheduled tasks and Windows services to maintain persistence on the host.

Around 15 minutes after initial access, the threat actors then moved laterally toward domain controllers and file shares using remote service creation. These services were used to execute the same PowerShell commands, download and execute the Tor2Mine malware. Upon establishing access to one of the domain controllers the threat actors performed similar activity as observed on the beachhead.

After roughly 30 minutes after initial access, the BlueSky ransomware binary was dropped and executed on the beachhead. The execution worked as intended which resulted in the ransomware spreading to all devices in the network over SMB. The time to ransomware in this case was 32 minutes.

### Threat Actor Profile:

Cobalt Strike

The Cobalt Strike server observed in this intrusion was first observed on December 16th 2022 and remained active through January 17th 2023. We saw the server then return for a second time frame from April 6th 2023 though April 15th 2023. This data was provided via the Threat Intel tracking services of The DFIR Report.

Tor2Mine

The PowerShell scripts involved in this case as well as infrastructure for the Tor2Mine server were observed being reused in May 2023 with the PaperCut NG CVE-2023-27350 exploit as the initial access source. In that intrusion no ransomware was observed. The linked case data is available for All Intel subscribers in event 21132 ( c39d59d8-8bae-49f5-8b29-de5c13b61899 ).

## Services

We offer multiple services including a Threat Feed service which tracks Command and Control frameworks such as Cobalt Strike, Sliver, BianLian, Metasploit, Empire, Havoc, etc. More information on this service can be found here .

Our All Intel service includes private reports, exploit events, long term infrastructure tracking, clustering, C2 configs, and other curated intel.

We’ll be launching a private ruleset soon, if you’d like to get in at a discounted rate for the beta, please Contact Us .

If you are interested in hearing more about our services, or would like to talk about a free trial, please reach out using the Contact Us page. We look forward to hearing from you.

## Analysts

Analysis and reporting completed by @yatinwad

## Initial Access

The initial access occurred via a brute-force attack, where the threat actors mainly targeted the System Admin (“sa”) account.

During the intrusion, we observed over 10,000 failed attempts before successful login.

SQL Server event ID 18456 Failure Audit Events in the Windows application logs:

Successful Login:

## Execution

In the next attack stage, the threat actors established a command shell via Extended SQL Stored Procedure ( xp_cmdshell ). This process allows you to issue operating system commands directly to the Windows command shell. To do this they enabled the feature the MSSQL configuration:

The threat actor then executed a Cobalt Strike beacon and a PowerShell script that has previously been identified by Sophos as used in campaigns to deploy Tor2Mine malware.

The overall execution events are depicted in the below diagram:

The first PowerShell script executed a command to download a Cobalt Strike beacon.

This was followed by a second PowerShell execution for:

A connection was then established with the following Tor2Mine server and URIs:

Tor2Mine uses a PowerShell script checking.ps1 to perform variety of operations. The script first sets a variable named $priv and $osver to check whether the active user is an administrator and the operating system version respectively, in the first few lines.

It then attempts to pull down an additional script named kallen.ps1, a PowerShell version of mimikatz from the Tor2Mine server.

It also consists of a function named “StopAV”, where it tries to disable antivirus solutions – in this case, MalwareBytes, Sophos and Windows Defender.

Depending upon the result of the $priv variable, there are 2 routes for the script: Privileged ”PrivTrue()“ and Non-Privileged “PrivFalse()”.

If the user is a privileged user, it first checks for the OS architecture, then downloads appropriate version (in our case, x64) of the miner and installs it as java.exe, in the “C:\ProgramData\Oracle\Java” directory. It also installs a driver named WinRing0x64.sys.

The function also creates multiple scheduled tasks and services which have references to Tor2Mine miner java.exe, encoded PowerShell commands and .hta files hosted on Tor2Mine servers.

In the case of the non-privileged function “PrivFalse()”, it executes a batch script “PrivFalse.bat” as scheduled tasks and also sets up schtasks as seen in the “PrivTrue()” function.

In the last section, a script named del.ps1 is downloaded and executed on the host as a scheduled task. The del.ps1 script has been explored further in the Defense Evasion section.

Depending upon the output of the $priv variable, the execution flow is as follows:

As the mimi function is commented, we didn’t observe any artifacts related to kallen.ps1 script.

## Persistence

To establish persistence in the network, multiple scheduled tasks and Windows services were created on the beachhead and one of the domain controllers. They reference the files dropped on the compromised hosts and Tor2Mine servers.

## Privilege Escalation

The threat actor was seen injecting code into legitimate process winlogon.exe via CreateRemoteThread which can be detected using Sysmon event ID 8.

During the intrusion the threat actor deployed XMrig miner which loaded the driver WinRing0 . This driver is deployed to assist the miner in operations and has been in use since at least version 5.3.0 .

## Defense Evasion

The Windows Defender AV Real-Time Monitoring was disabled on the beachhead and one of the domain controllers using Set-MpPreference cmdlet.

The PowerShell script, checking.ps1, is explained in the Execution section which contained other ways to disable AV, including registry modifications and service disabling.

A PowerShell script named del.ps1 attempts to terminate system utilities such as Process Explorer, Task Manager, Process Monitor, and Daphne Task Manager.

In the script checking.ps1 the threat actor created 16 different tasks on the hosts where Tor2Mine was deployed. These tasks were named in a manner to try and blend in with various Windows tasks that on the hosts:
\Microsoft\Windows\MUI\LPupdate \Microsoft\Windows\RamDiagnostic\Error Diagnostic \Microsoft\Windows\.NET Framework\.NET Framework Cache Optimization Files-S-3-5-21-2236678156-433529325-2142214268-1138 \Microsoft\Windows\.NET Framework\.NET Framework Cache Optimization Files-S-3-5-21-2236678155-433529325-2142214968-1138 \Microsoft\Windows\.NET Framework\.NET Framework Cache Optimization" \Microsoft\Windows\Registry\RegBackup \Microsoft\Windows\DiskCleanup\SlientDefragDisks \Microsoft\Windows\.NET Framework\.NET Framework NGEN v4.0.50319 Critical \Microsoft\Windows\EDP\EDP App Update Cache \Microsoft\Windows\EDP\EDP App Lock Task \Microsoft\Windows\UPnP\UPnPClient Task \Microsoft\Windows\UPnP\UPnPHost \Microsoft\Windows\Shell\WinShell \Microsoft\Windows\Shell\WindowsShellUpdate \Microsoft\Windows\Bluetooth\UpdateDeviceTask \Microsoft\Windows\.NET Framework\.NET Framework Cache Optimization

## Credential Access

Tor2Mine was used to access the LSASS memory space and the access granted was 0x1010.

On the beachhead, we observed the execution of credential dumping utility Invoke-PowerDump.

## Discovery

During the course of the intrusion, we observed port discovery (port 445) activity from the beachhead. We attribute this to the invocation of the PowerShell command Invoke-SMBExec. This was likely executed as part of the Invoke-TheHash framework based on other PowerShell modules observed.

Looking at the traffic from a network perspective we observed the activity making DCE\RPC calls to the svcctl endpoint and the named pipe \pipe\ntsvcs using the OpenSCManagerW operation.

This appeared to be how they profiled the network layout and remote hosts.

The threat actor was observed running whoami from the Tor2Mine PowerShell process on the beachhead.
"C:\Windows\system32\whoami.exe" /user

## Lateral Movement

The threat actors moved laterally toward the domain controllers and file shares using Remote Service creation. The pattern “%COMSPEC% /C “cmd /c powershell.exe” is associated with the Cobalt Strike “psexec_psh” jump module.

Decoding the command we can see the same PowerShell download and execute as observed on the beachhead. The hexadecimal value 0x53611451 corresponds to the IP address 83.97.20[.]81 which was the command and control server for the Tor2Mine malware.

## Command and Control

Tor2Mine Server:
{ destination: { [-] address: 83.97.20.81 as: { [-] number: 9009 organization: { [-] name: M247 Europe SRL } } geo: { [-] city_name: Bucharest continent_name: Europe country_iso_code: RO country_name: Romania location: { [+] } region_iso_code: RO-B region_name: Bucuresti } ip: 83.97.20.81 port: 443 } network.direction: outbound tls: { [-] cipher: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 client: { [-] ja3: c12f54a3f91dc7bafd92cb59fe009a35 } curve: x25519 established: true resumed: false server: { [-] ja3s: ec74a5c51106f0419184d0dd08fb05bc } version: 1.2 version_protocol: tls }
Cobalt Strike C2:

IP Address: 5.188.86.237

Connection to the following URIs was observed:

Cobalt Strike Server Config:
{ "beacontype": [ "HTTPS" ], "sleeptime": 120000, "jitter": 12, "maxgetsize": 1398924, "spawnto": "AAAAAAAAAAAAAAAAAAAAAA==", "license_id": 1580103824, "cfg_caution": false, "kill_date": null, "server": { "hostname": "5.188.86.237", "port": 443, "publickey": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCnCZHWnYFqYB/6gJdkc4MPDTtBJ20nkEAd3tsY4tPKs8MV4yIjJb5CtlrbKHjzP1oD/1AQsj6EKlEMFIKtakLx5+VybrMYE+dDdkDteHmVX0AeFyw001FyQVlt1B+OSNPRscKI5sh1L/ZdwnrMy6S6nNbQ5N5hls6k2kgNO5nQ7QIDAQABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==" }, "host_header": "", "useragent_header": null, "http-get": { "uri": "/functionalStatus/2JYbAmfY5gYNj7UrgAte5p1jXx2V", "verb": "GET", "client": { "headers": null, "metadata": null }, "server": { "output": [ "print", "append 8 characters", "append 8 characters", "append 10 characters", "append 6 characters", "append 11 characters", "append 33 characters", "append 69 characters", "append 55 characters", "append 67 characters", "append 27 characters", "append 15 characters", "append 25 characters", "append 32 characters", "append 72 characters", "prepend 16 characters", "prepend 17 characters", "prepend 11 characters", "prepend 31 characters", "prepend 80 characters", "prepend 60 characters", "prepend 54 characters", "prepend 69 characters", "prepend 38 characters", "prepend 8 characters", "base64url" ] } }, "http-post": { "uri": "/rest/2/meetings2JYbAmfY5gYNj7UrgAte5p1jXx2V", "verb": "GET", "client": { "headers": null, "id": null, "output": null } }, "tcp_frame_header": "AAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "crypto_scheme": 0, "proxy": { "type": null, "username": null, "password": null, "behavior": "Use IE settings" }, "http_post_chunk": 96, "uses_cookies": false, "post-ex": { "spawnto_x86": "%windir%\\syswow64\\auditpol.exe", "spawnto_x64": "%windir%\\sysnative\\auditpol.exe" }, "process-inject": { "allocator": "NtMapViewOfSection", "execute": [ "CreateThread 'ntdll.dll!RtlUserThreadStart'", "NtQueueApcThread-s", "SetThreadContext", "CreateRemoteThread", "CreateThread 'kernel32.dll!LoadLibraryA'", "RtlCreateUserThread" ], "min_alloc": 40263, "startrwx": true, "stub": "IiuPJ9vfuo3dVZ7son6mSA==", "transform-x86": [ "prepend '\\x90\\x90\\x90\\x90\\x90\\x90\\x90\\x90\\x90'" ], "transform-x64": [ "prepend '\\x90\\x90\\x90\\x90\\x90\\x90\\x90\\x90\\x90'" ], "userwx": false }, "dns-beacon": { "dns_idle": null, "dns_sleep": null, "maxdns": null, "beacon": null, "get_A": null, "get_AAAA": null, "get_TXT": null, "put_metadata": null, "put_output": null }, "pipename": null, "smb_frame_header": "AAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", "stage": { "cleanup": true }, "ssh": { "hostname": null, "port": null, "username": null, "password": null, "privatekey": null } }

## Impact

The BlueSky ransomware binary named vmware.exe was dropped on the beachhead, which upon execution, resulted in network wide ransomware. This was accomplished using SMB with the ransomware connecting to host over port 445 to encrypt files.

The files were renamed with the file extension .bluesky and a ransom note file named # DECRYPT FILES BLUESKY #.txt was dropped on the host and opened to reveal the ransom note.

On the beachhead server, the time of encryption was visible as the MSSQL service stopped functioning after execution of vmware.exe :

The whole intrusion after initial access lasted only around 30 minutes with limited discovery and no exfiltration observed.

## Timeline

## Diamond Model

## Indicators

### Atomic
hxxp://0x53611451/win/clocal hxxp://qlqd5zqefmkcr34a[.]onion[.]sh/win/checking[.]hta hxxps://asq[.]d6shiiwz[.]pw/win/hssl/d6[.]hta hxxp://83[.]97[.]20[.]81/win/checking[.]hta hxxp://83[.]97[.]20[.]81/win/update[.]hta hxxps://asd[.]s7610rir[.]pw/win/checking[.]hta hxxps://asq[.]r77vh0[.]pw/win/hssl/r7[.]hta hxxp://asq[.]r77vh0[.]pw/win/checking[.]hta hxxp://5[.]188[.]86[.]237/vmware[.]exe

### Computed
java.exe md5: 9e88c287eb376f3c319a5cb13f980d36 sha1: 501af977080d56a55ff0aeba66b58e7f3d1404ea sha256: 74b6d14e35ff51fe47e169e76b4732b9f157cd7e537a2ca587c58dbdb15c624f vmware.exe md5: 7b68bc3dd393c2e5273f180e361f178a sha1: 07610f11d3b8ccb7b60cc8ad033dda6c7d3940c4 sha256: d4f4069b1c40a5b27ba0bc15c09dceb7035d054a022bb5d558850edfba0b9534 WinRing0x64.sys md5: 0c0195c48b6b8582fa6f6373032118da sha1: d25340ae8e92a6d29f599fef426a2bc1b5217299 sha256: 11bd2c9f9e2397c9a16e0990e4ed2cf0679498fe0fd418a3dfdac60b5c160ee5 del.ps1 md5: bfd36fd6a20ccd39f5c3bb64a5c5dd8b sha1: e938646862477e598fcda20d0b7551863f8b651c sha256: 35b95496b243541d5ad3667f4aabe2ed00066ba8b69b82f10dd1186872ce4be2 checking.ps1 md5: 08bdf000031bbad1a836381f73adace5 sha1: 3dff4ae3c421c9143978f8fc9499dca4aed0eac5 sha256: f955eeb3a464685eaac96744964134e49e849a03fc910454faaff2109c378b0b Invoke-PowerDump.ps1 md5: 42a80cc2333b612b63a859f17474c9af sha1: e7be97fb2200eb99805e39513304739a7a28b17e sha256: 3b463c94b52414cfaad61ecdac64ca84eaea1ab4be69f75834aaa7701ab5e7d0

## Detections

### Network
ET HUNTING SUSPICIOUS Dotted Quad Host MZ Response ET INFO Executable Download from dotted-quad Host ET INFO Executable Retrieved With Minimal HTTP Headers - Potential Second Stage Download ET INFO PowerShell Hidden Window Command Common In Powershell Stagers M2 ET MALWARE Successful Cobalt Strike Shellcode Download (x64) M2 ET POLICY PE EXE or DLL Windows file download HTTP ET HUNTING Generic Powershell DownloadFile Command ET HUNTING Generic Powershell DownloadString Command ET HUNTING Generic Powershell Launching Hidden Window ET HUNTING SUSPICIOUS Dotted Quad Host MZ Response ET INFO Executable Download from dotted-quad Host ET INFO Executable Retrieved With Minimal HTTP Headers - Potential Second Stage Download ET INFO PS1 Powershell File Request ET INFO PowerShell Base64 Encoded Content Command Common In Powershell Stagers M1 ET INFO PowerShell Base64 Encoded Content Command Common In Powershell Stagers M2 ET INFO PowerShell DownloadFile Command Common In Powershell Stagers ET INFO PowerShell DownloadString Command Common In Powershell Stagers ET INFO PowerShell Hidden Window Command Common In Powershell Stagers M2 ET INFO PowerShell NoProfile Command Received In Powershell Stagers ET INFO PowerShell NonInteractive Command Common In Powershell Stagers ET INFO Powershell Base64 Decode Command Inbound ET MALWARE JS/Nemucod requesting EXE payload 2016-02-01 ET MALWARE JS/Nemucod.M.gen downloading EXE payload ETPRO MALWARE Likely Evil Request for Invoke-Mimikatz ETPRO MALWARE PS/Deathhm Script Inbound via HTTP ET DNS Query to a *.pw domain - Likely Hostile ET SCAN Behavioral Unusual Port 445 traffic Potential Scan or Infection

### Sigma

Search rules on detection.fyi or sigmasearchengine.com

Sigma Repo:
Suspicious Scheduled Task Creation - 3a734d25-df5c-4b99-8034-af1ddb5883a4 PowerShell Scripts Installed as Services - a2e5019d-a658-4c6a-92bf-7197b54e2cae Potentially Suspicious AccessMask Requested From LSASS - 4a1b6da0-d94f-4fc3-98fc-2d9cb9e5ee76 Powershell Defender Disable Scan Feature - 1ec65a5f-9473-4f12-97da-622044d6df21 Windows Defender Exclusions Added - 1321dc4e-a1fe-481d-a016-52c45f0c8b4f CobaltStrike Service Installations System - 5a105d34-05fc-401e-8553-272b45c1522d CobaltStrike Service Installations in Registry - 61a7697c-cb79-42a8-a2ff-5f0cdfae0130 Suspicious Child Process Of SQL Server - 869b9ca7-9ea2-4a5a-8325-e80e62f75445 Whoami.EXE Execution Anomaly - 8de1cbe8-d6f5-496d-8237-5f44a721c7a0 Malicious PowerShell Commandlets PoshModule - 7d0d0329-0ef1-4e84-a9f5-49500f9d7c6c Malicious PowerShell Commandlets ScriptBlock - 89819aa4-bbd6-46bc-88ec-c7f7fe30efa6 PowerShell Base64 Encoded IEX Cmdlet - 88f680b8-070e-402c-ae11-d2914f2257f1 MSSQL Server Failed Logon - 218d2855-2bba-4f61-9c85-81d0ea63ac71 MSSQL XPCmdshell Suspicious Execution - 7f103213-a04e-4d59-8261-213dddf22314 MSSQL XPCmdshell Option Change - d08dd86f-681e-4a00-a92c-1db218754417 MSSQL Server Failed Logon From External Network - ebfe73c2-5bc9-4ed9-aaa8-8b54b2b4777d Vulnerable WinRing0 Driver Load - 1a42dfa6-6cb2-4df9-9b48-295be477e835

### Yara

https://github.com/The-DFIR-Report/Yara-Rules/blob/main/19208/19208.yar

## MITRE

Valid Accounts - T1078
Brute Force - T1110
Scheduled Task - T1053.005
Windows Command Shell - T1059.003
PowerShell - T1059.001
Disable or Modify Tools - T1562.001
Process Injection - T1055
LSASS Memory - T1003.001
System Owner/User Discovery - T1033
Network Share Discovery - T1135
Data Encrypted for Impact - T1486
SMB/Windows Admin Shares - T1021.002
Web Protocols - T1071.001
Service Execution - T1569.002
Modify Registry - T1112
Obfuscated Files or Information - T1027
Windows Service - T1543.003
Masquerade Task or Service - T1036.004
Internal case #19208

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
