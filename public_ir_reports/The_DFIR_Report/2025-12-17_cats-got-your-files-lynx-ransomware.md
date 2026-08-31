---
title: "Cat’s Got Your Files: Lynx Ransomware - The DFIR Report"
source_url: "https://thedfirreport.com/2025/12/17/cats-got-your-files-lynx-ransomware/"
published: "2025-12-17T19:07:07+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2025-12-17_cats-got-your-files-lynx-ransomware.html"
---

# Cat’s Got Your Files: Lynx Ransomware - The DFIR Report
## Key Takeaways

- The intrusion began with a successful RDP login using already-compromised credentials, likely obtained via an infostealer, data breach reuse, or an initial access broker.

- Within minutes, the threat actor moved laterally to a domain controller using a separate compromised domain admin account, created multiple impersonation-style accounts, and added them to privileged groups.

- The threat actor mapped out virtualization infrastructure and file shares, conducted additional enumeration, and created one more look-alike account before pausing activity.

- Sensitive files from multiple network shares were collected, compressed using 7-Zip, and exfiltrated via temporary file-sharing service temp.sh .

- The threat actor connected to backup servers, deleted backup jobs, and deployed Lynx ransomware across multiple backup and file servers via RDP. The overall Time to Ransomware (TTR) was ~178 hours across nine days.

## The DFIR Report Services

- Private Threat Briefs: 20+ private DFIR reports annually.

- Threat Feed: Focuses on tracking Command and Control frameworks like Cobalt Strike, Metasploit, Sliver, etc.

- All Intel : Includes everything from Private Threat Briefs and Threat Feed, plus private events, Threat Actor Insights reports, long-term tracking, data clustering, and other curated intel.

- Private Sigma Ruleset : Features 170+ Sigma rules derived from 50+ cases, mapped to ATT&CK with test examples.

- https://thedfirreport.com/products/dfir-labs/ DFIR Labs: Offers cloud-based, hands-on learning experiences, using real data, from real intrusions. Interactive labs are available with different difficulty levels and can be accessed on-demand, accommodating various learning speeds.

Contact us today for pricing or a demo!

## Case Summary

The intrusion began in early March 2025 with a single successful Remote Desktop Protocol (RDP) logon to an internet-exposed system. Notably, there was no evidence of credential stuffing, brute forcing, or other failed authentication attempts from the source IP, indicating the threat actor likely possessed valid credentials before the activity occurred. Although the original source of the credentials could not be determined, they are commonly acquired through credential-stealing malware, reused passwords from prior data breaches, or purchased through initial access brokers.

Immediately after logging in, the threat actor began reconnaissance using the command prompt and standard Windows utilities. They then expanded their activity to network-wide enumeration by deploying SoftPerfect Network Scanner (netscan).

Just ten minutes after the initial logon, the threat actor identified a domain controller and moved laterally to it via RDP. For this activity, they authenticated using a different account with domain administrator privileges. In the absence of any evidence of on-host privilege escalation or credential dumping, we assess that these domain admin credentials were also compromised prior to the intrusion. The threat actor’s possession of multiple valid accounts, spanning both standard and privileged access, further supports the likelihood that an initial access broker was the source of their entry into the environment.

Once on the domain controller, the threat actor used Active Directory Users and Computers (dsa.msc) to create two new accounts: one named “administratr” and another designed to mimic an existing domain account, altered by a single character to blend in. Both accounts were promptly added to privileged security groups, including Domain Administrators. To establish persistence, the threat actor installed the AnyDesk remote access client on the domain controller. Although, this AnyDesk access was never used during the remainder of the intrusion.

The threat actor then searched the environment for signs of virtualization infrastructure and browsed several network file shares. Afterward, they created one additional look-alike account and concluded their first round of hands-on activity.

Six days after the initial access, the threat actor returned via RDP from the same source IP address and using the same hostname. They resumed reconnaissance by running netscan, then downloaded NetExec through a web browser and conducted a password spray attack over port 445. Afterward, they again browsed multiple file shares. These shares were then targeted for collection; the actor compressed the contents into archives and exfiltrated them to the temporary file-sharing service temp[.]sh. This activity marked the end of their operations for the day.

Around nine hours after the exfiltration activity, the threat actor returned via RDP from a new source IP address but using the same hostname observed earlier in the intrusion. Notably, both IP addresses involved were associated with Railnet LLC, a company previously identified as a front for Virtualine, which is known to operate infrastructure tied to IP ranges reportedly leveraged by criminal networks. Further details on this attribution are available in the Intrinsec blog. [link]

During this period, the threat actor connected to several additional domain controllers and hypervisor systems via RDP. On these hosts, they executed various discovery commands and interacted with the Microsoft Management Console (MMC), specifically the Local Users and Groups snap-in, to enumerate and review user accounts and permissions. Leveraging their earlier netscan results, they also identified additional network infrastructure and attempted to access these systems by launching browser sessions directly from within netscan.

Approximately 24 hours later, on the ninth day of the intrusion, the threat actor returned for the final time. They initiated one last round of network scanning with netscan on the beachhead host before connecting via RDP to a backup server, where they proceeded to delete existing backup jobs. Following this, they deployed and executed Lynx ransomware on the backup server. The threat actor then repeated this ransomware deployment across multiple additional backup and file servers accessed via RDP.

The Time to Ransomware (TTR) for this intrusion was just under 178 hours, spanning nine calendar days.

If you would like to get an email when we publish a new report, please subscribe here .

## Analysts

Analysis and reporting completed by Friff and Daniel Casenove , reviewed by MittenSec .

## Initial Access

The first instance of unauthorized access by the threat actor was a successful RDP logon to the beachhead host, a publicly exposed RDP server. The logon was performed using valid credentials, and there was no indication of brute force or password spraying occurring, indicating these credentials were obtained prior to the intrusion.

The threat actor was also observed using credentials for a second account with domain administrator privileges to pivot from the beachhead host without performing any credential access activities, indicating these credentials were also obtained prior to initial access.

The logon originated from IP address 195.211.190[.]189 and can be observed in Windows Security Log Event ID 4624 logon type 3 followed by logon type 10 indicating a successful RDP logon.

The initial access logon was observed using an elevated token, indicating the session was elevated and had administrator privileges – Event 4624 Microsoft Learn

## Execution

Due to the primary method of access being Remote Desktop Protocol (RDP), the threat actor conducted most post-compromise activity through RDP sessions. This was evidenced by processes consistently spawning under explorer.exe , indicating interactive use aligned with RDP behavior.

Throughout the intrusion, the threat actor used Windows Command Shell ( cmd.exe ) and PowerShell to execute commands on compromised hosts during hands-on-keyboard activity. These tools were primarily used to run Living Off The Land Binaries (LOLBins), largely for discovery purposes.

SoftPerfect NetScan was used extensively during the intrusion. While the configuration deployed by the threat actor is detailed in the Discovery section, it’s clear the tool played a role in automating portions of their activity. Notably, evidence from Security Event ID 4688 logs showed mstsc.exe /v:<IP address> being launched by netscan.exe , confirming the use of NetScan’s Remote Desktop functionality.

## Persistence

In the first hour of the compromise, the threat actor leveraged already-known high-privileged account credentials to connect to a domain controller via RDP.

On the domain controller, they used the “Active Directory Users and Computers” snap-in (dsa.msc) to create three users for persistence. All of the newly created accounts have usernames that mimic legitimate accounts already present in the environment. For the rest of the report we will refer to these accounts as: “administratr”, “Lookalike 1”, and “Lookalike 2”.

To ensure persistence, the threat actor set the accounts’ passwords to never expire with the USER_DONT_EXPIRE_PASSWORD attribute.

Furthermore, as detailed in the Privilege Escalation section, the threat actor assigned high privileges to the newly created accounts.

First, they added two of the accounts, namely “administratr” and “Lookalike 1”, to the Domain Admins group. The “administratr” account was also added to the Group Policy Creator Owners, giving it capabilities to create, for example, new GPOs. Afterward, the threat actor added “Lookalike 2” to a high-privilege group specific to the domain in question.

## Privilege Escalation

After having created the three domain accounts, the threat actor added them to several high-privilege domain groups.

First, they added two of the accounts, namely “administratr” and “Lookalike 1”, to the Domain Admins group. The “administratr” account was also added to the Group Policy Creator Owners, giving it capabilities to create, for example, new GPOs. Afterward, the threat actor added “Lookalike 2” to a high-privilege group specific to the domain in question.

Lastly, the threat actor connected to multiple hypervisor servers using these newly created accounts with high privileges. We assess this was likely to test whether the modifications made to the accounts were successful, as no further actions were performed on these hosts.

## Defense Evasion

Other than creating new accounts to blend in to the environment, the threat actor did not take other actions to really obscure their activity.

## Credential Access

The attacker was able to get into the environment through a successful Remote Desktop Protocol (RDP) connection. What’s interesting is that there were no signs of brute force or password spraying, so this wasn’t a case of someone hammering away at login attempts until they got in. Instead, it looks like the credentials were already valid, which points to a few likely scenarios:

- Third-Party Access Broker: These are threat actors who specialize in selling access to compromised systems. They don’t always do the hacking themselves, instead, they collect or buy credentials and then resell them to others who want to get into networks without doing the initial legwork.

- Info Stealer Malware: This type of malware is designed to quietly grab saved credentials, browser cookies, and other sensitive data from infected machines. Once stolen, that data often ends up for sale or trade on dark web marketplaces, where attackers can use it to log in.

- Credential Dump Leaks: These are large sets of usernames and passwords that get exposed during breaches of unrelated services. If users reuse passwords across platforms (which is still pretty common), attackers can test those credentials elsewhere and find systems where they still work.

Given the clean nature of the logins seen throughout this incident, it’s reasonable to assume the threat actor used credentials obtained through one of these indirect methods rather than trying to force their way in.

Within this incident, there were no signs of additional reconnaissance or attempts to escalate access by harvesting more credentials. This suggests the attacker may have had a specific goal or was operating with limited scope.

## Discovery

Immediately after gaining initial access to the beachhead host, the threat actor spawned cmd.exe and performed hands-on-keyboard network and system discovery commands.
"C:\Windows\System32\cmd.exe"
ipconfig
route print
Systeminfo
ping \REDACTED
ping REDACTED

### Netscan

After these first commands, the threat actor created a folder named “000” on the initial access account’s desktop and dropped SoftPerfect Network Scanner v7.2.7 along with the netscan config and license file onto the beachhead host via File Explorer over RDP.

Analysis of the netscan.xml config file revealed multiple custom configurations made by the threat actor to achieve their objectives on the network:

- Use domain administrator credentials obtained by the threat actor prior to the intrusion.

- Scan a predefined set of ports.

- Scan the full IP range of the victim environment.

- Enabled share scanning with checks for security info, share writing and diskspace.

- Enabled workstation scanning, with accounts, disk drives, LAN group, logged users, OS version, and uptime enabled.

Netscan also had default hotkeys enabled for Remote Desktop and Computer Management, mapped to CTRL + R and CTRL + M.

The Netscan license file ( netscan.lic ) shows that Netscan was used with a paid license, removing the heavy restrictions from the trial version. A blog from ReliaQuest notes that between 2023 and 2024, they observed threat actors attempting to buy SoftPerfect Network Scanner and freely sharing cracked versions and keygens on various criminal forums. It is unclear if the threat actor had purchased this license legitimately or obtained it through illicit means.
<?xml version="1.0"?>
<network-scanner-license>
<license>CJaUZHmoljWtb9JAkiZNWSiPIWCB0uxXApH2FwzyKSBXp2wTNyj8F1oVJsq/1TTRDgh0+pjWXvho96bMj2M6NmH0PTYqYOJqmaQep1AY/rLeBAWtjyV1ZSdXCHxbfgBFchM8IU5iXvS4waD1jFCXx2qeX+snG
5FazL6UZPyhMkf/0xgrEr9Pv3VseLhPB07jHgnyP7wY5NWXvw1GzWO31ozsYAoVwBWmb/BpoI7briDlvRQXTC40LMzq+kq0smWLKbDnyQCRuRyQSrKVnN1lq8YXlobygCOF5/lzpEPEyruPyXOX1RQAyM5rLVxRmiCZmrqtg
pn0ovRJ+3Az/s6cpqHWG41voP2bzk9lT+usc+rxO1QZrp5hPE0Q+IcE6CdY464AMtjt/aN2FcAcCpe6kWw3ZyLBdz8C9PwAoJEJoE5OiplvjaIejkasJlYQIF2yNe1uasJIq4MJ+OaNVX5K9R7kFg/97mltbyKW4Ofmy8Pdb
9lsHgnx7LAGbeagdD22</license>
<upgrade>0</upgrade>
<language>English</language>
<nmap></nmap>
<autoupdate>
<prompt>false</prompt>
<enabled>false</enabled>
<lastcheck>0</lastcheck>
</autoupdate>

Soon after dropping Netscan on the beachhead host, the threat actor executed Netscan to perform network discovery.

After execution, port scanning was observed in Sysmon EID 3 network connections events over the preconfigured IP and port ranges.

During the scan, multiple remote hosts showed file creation events for delete[.]me, as seen in Sysmon Event ID 11. This is a known behavior of NetScan when it’s set to check for write access on network shares.

In this case, Netscan was run with domain administrator privileges, so all discovered shares were writable. As a result, NetScan was able to create and delete the delete[.]me file on each discovered share.

These actions also generated Windows Security Event ID 5145 object access entries referencing the delete[.]me file.

Soon after Netscan finished running, a file named “ss.xml” was dropped on the user’s desktop by netscan. While this file could not be recovered, it was likely an XML export of the Netscan results.

Next, the threat actor performed two more discovery commands before moving laterally to the previously pinged domain controller via RDP using domain admin credentials.
ipconfig
net user
Once connected to the domain controller, the actor ran:
C:\Windows\System32\ServerManager.exe
"C:\Windows\system32\mmc.exe" "C:\Windows\system32\dsa.msc"
This launched the Microsoft Management Console with the Active Directory Users & Computers snap‑in (dsa.msc), allowing them to browse and manipulate AD objects.

After establishing persistence on the domain controller (detailed in the persistence section), the threat actor performed additional discovery commands and queried the registry to identify hostnames of the Hypervisor servers. This concluded discovery activities for day one.
reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Virtual Machine\Guest\Parameters
systeminfo
C:\Windows\regedit.exe
Discovery activities resumed on day six of the intrusion when the threat actor returned to the beachhead host via RDP. First, they ran Task Manager to view running processes and system information.
"C:\Windows\system32\taskmgr.exe" /4
This was followed by the threat actor running SoftPerfect Network Scanner again to perform network discovery, along with additional network discovery commands.
"C:\Users\REDACTED\Documents\000\netscan.exe"
ROUTE PRINT
Netexec

The threat actor then downloaded the network service exploitation tool Netexec via Microsoft Edge.

NetExec was then executed with the following command:
nxc.exe smb REDACTED/24 -u REDACTED -p REDACTED
This command is designed to enumerate a list of live hosts over smb (port 445) using the specified IP range, in this case the same IP range was used from netscan scanning.

An example output can be seen below:
SMB 192.168.1.101 445 DC2012A [*] Windows Server 2012 R2 Standard 9600 x64 (name:DC2012A) (domain:OCEAN) (signing:True) (SMBv1:True)
SMB 192.168.1.102 445 DC2012B [*] Windows Server 2012 R2 Standard 9600 x64 (name:DC2012B) (domain:EARTH) (signing:True) (SMBv1:True)
SMB 192.168.1.110 445 DC2016A [*] Windows Server 2016 Standard Evaluation 14393 x64 (name:DC2016A) (domain:OCEAN) (signing:True) (SMBv1:True)
SMB 192.168.1.117 445 WIN10DESK1 [*] WIN10DESK1 x64 (name:WIN10DESK1) (domain:OCEAN) (signing:False) (SMBv1:True)
Once executed, nxc.exe was observed making connections over SMB port 445 to multiple hosts on the network over roughly a 2-minute period.

Following extraction and execution, NTFS records show that multiple files and directories were created in the user’s profile under the .nxc directory. Of note were the nxc.conf configuration file and the databases used to store results for each protocol.

This configuration file matched the default configuration on the NetExec GitHub repository .

[nxc]
workspace = default
last_used_db = smb
pwn3d_label = Pwn3d!
audit_mode =
reveal_chars_of_pwd = 0
log_mode = False
ignore_opsec = True
host_info_colors = ["green", "red", "yellow", "cyan"]
[BloodHound]
bh_enabled = False
bh_uri = 127.0.0.1
bh_port = 7687
bh_user = neo4j
bh_pass = bloodhoundcommunityedition
[Empire]
api_host = 127.0.0.1
api_port = 1337
username = empireadmin
password = password123
[Metasploit]
rpc_host = 127.0.0.1
rpc_port = 55552
password = abc123
Artifacts of this SMB enumeration were left behind in the smb.db database stored by NetExec in C:\Users\%UserProfile%\nxc\workspaces\smb.db. This database confirms that a number of domains and hosts were successfully enumerated using the domain admin credentials during scanning.

After each execution of Netexec, multiple scripts were dropped into the temp directory, which can be used as part of the module functionality built into Netexec. However, no modules were used by the threat actor during the intrusion.

Soon after NetExec had finished running, the threat actor was observed manually creating a text file, renaming it to nxc.txt, and opening it in Notepad, likely to review the NetExec output.

After collecting and exfiltrating data from the network shares, the threat actor ran one last ipconfig command before disconnecting the RDP session, ending discovery activity for day six.

On day eight of the intrusion, the threat actor returned to the beachhead host via RDP from a second IP address 77.90.153[.]30 and immediately executed Netscan, as well as the following discovery commands:
ipconfig
"C:\Windows\system32\mmc.exe" "C:\Windows\system32\lusrmgr.msc"
"C:\Windows\system32\SecEdit.exe" /export /cfg C:\secpol.cfg"
notepad.exe C:\secpol.cfg
lusrmgr.msc is the Microsoft Management Console Local Users and Groups snap-in and is used for advanced management of local users and groups.

The next command run launched secedit.exe, a native windows binary used to analyze and make changes to system security policies. In this case, the threat actor exported all local security policies to a file named secpol.cfg and reviewed the export using Notepad.

Following this, the threat actor connected to a domain controller via RDP and launched dsa.msc, the Active Directory Users and Computers console. They reviewed this for some time before disconnecting their session and moving to a second domain controller via RDP and launching “ C:\Windows\system32\ServerManager.exe” .

Next, the threat actor pivoted to mapping out the Hyper-V infrastructure, as we observed RDP connections from the beachhead host to three hypervisors. On all three servers, the threat actor launched virtmgmt.msc (the Hyper-V management console) and also ran systeminfo and regedit . The threat actor was also observed issuing ping commands to a third domain controller during the RDP session on one of the hypervisors.

During this time, the threat actor was again observed querying the registry on the beachhead host to identify Hyper-V hostnames.
reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Virtual Machine\Guest\Parameters
The threat actor also made multiple attempts to enumerate another domain on the network using discovery commands from the beachhead host and DC B, including:
regedit
nslookup REDACTED
nbtstat -a REDACTED
C:\Windows\system32\PING.EXE REDACTED -4
On day eight, the threat actor was observed utilizing netscan to browse multiple network appliances such as Firewalls and VPNs. These actions can be observed in browser history events, as well as in process events for Microsoft Edge, with netscan.exe as the parent process.

The threat actor used the open ‘As Web (HTTP)’ shortcut within the Netscan GUI to view the appliances’ web portals in the browser.

Finally, on day nine of the intrusion, the threat actor reconnected to the beachhead host from IP address 77.90.153[.]30 and ran systeminfo , followed by launching SoftPerfect Network Scanner, before moving on to their final objective of deploying ransomware.

## Lateral Movement

Throughout the intrusion, the threat actor used the beachhead host as a central point to access and move laterally across the network via RDP. The threat actor relied heavily on SoftPerfect Network Scanner to identify and enumerate targets for lateral movement, running scans each time they accessed the network.

On day one of the intrusion, after running initial discovery commands and netscan.exe, the threat actor was observed connecting to a domain controller via RDP using Domain Admin credentials. A logon type 7 (Unlock) was seen in Security Event ID 4624 logs, indicating an existing RDP session was unlocked.

On day two of the intrusion, the threat actor was observed logging into several hypervisors using the “Lookalike 1” domain administrator account and the “administratr” account created the previous day. Following this, the threat actor created “Lookalike 2” and added it to a domain-specific high-privileged group. They then also tested this account by authenticating to the hypervisors.

These logins were observed in Security Event ID 4624 Logon Type 3 (Network) events. No activity was observed during these logons, and as detailed in the privilege escalation section, this was likely to test the permissions of the newly created accounts.

On day six of the intrusion, the threat actor was observed launching mstsc.exe via explorer.exe and initiating connections to several hypervisors. However, no successful logons were observed on this day. This can be observed in Sysmon Event ID 1 (process creation) and Event ID 3 (network connections) events.

On day eight of the intrusion the threat actor was observed connecting to multiple domain controllers and hypervisor servers via RDP using the Domain Admin account to perform further discovery activities.

On day nine of the intrusion the threat actor was observed connecting to multiple backup servers and file servers via RDP using the domain admin account to achieve their final objective of deploying ransomware.

## Collection

On the sixth day of the compromise, the threat actor accessed several network shares and their contents from the beachhead host. This activity culminated with the collection of several folders from multiple file servers. From the beachhead, the threat actor leveraged 7-Zip to create zip archives of the contents of the two file servers.

The combination of the 7zG.exe archiving command lines and explorer.exe as their parent process suggests that the threat actor navigated to each target folder via the file manager, right-clicked on them to open the Context Menu and selected 7-Zip’s “Add to Archive” functionality to create the zip files.

The threat actor saved the resulting archives in the Desktop folder of the compromised user.

## Command and Control

As detailed in the persistence section, AnyDesk was installed as a service on the domain controller; however, no further AnyDesk traffic or activity was observed during the intrusion, and all activity was performed via RDP sessions.

During initial access the threat actor connected from the IP 195.211.190[.]189. During this connection the threat actor’s hostname DESKTOP-BUL6K1U, was observed in the Workstation name field in the logon type 3 event

The IP address 195.211.190[.]189 was hosted on infrastructure from Railnet LLC which is used as a legal front for the Russia based bulletproof hosting provider Virtualine as reported by Intrinsec . Bulletproof hosting providers are frequently used by threat actors, as they knowingly provide services that enable cybercrime, such as allowing anonymous use of their infrastructure and actively ignoring law enforcement requests, government inquiries, and abuse complaints. Furthermore, their infrastructure is typically hosted in countries with a high tolerance for malicious cyber activities.

Later in the intrusion, the threat actor switched to a second IP address (also hosted on Railnet LLC infrastructure) to access the network. The same hostname DESKTOP-BUL6K1U was used.

Virtualine has been observed advertising its bulletproof hosting services on the Russian-speaking forums Exploit and XSS since at least August 2024.

## Exfiltration

Soon after the collection activities performed on the beachhead host on day six of the intrusion, the threat actor browsed to the temporary file sharing site temp.sh . This site is commonly used by threat actors to exfiltrate data or host malicious payloads.

The threat actor used the upload feature to exfiltrate the previously archived files. Evidence of this can be seen in the browsing history, with references to the “/upload” URI.

Further evidence can be seen in network traffic to the associated temp.sh IP address.

The number of visits to the “/upload” URI and the number of large outgoing network traffic events both correlate with the number of archives created by the threat actor, confirming that the multiple archives were exfiltrated individually.

## Impact

Ransomware deployment

On the ninth day of the intrusion, the threat actor moved laterally to several backup servers and file servers via RDP from the beachhead.

On these servers, they dropped the Lynx ransomware payload “w.exe” on the Desktop folder of the compromised Domain Administrator account.

On one occasion “w.exe” was also dropped on the root folder of an E drive, likely by mistake.

The threat actor then executed “w.exe” on each server using cmd, as shown below.

It is interesting to note that in almost all the command lines the order of the passed parameters differs. In one case, the threat actor also mistyped the command by forgetting to specify a flag.

In general, the ransomware was executed with the following arguments:
w.exe --dir E:\ --mode fast --verbose --noprint
As detailed in a blog post from Group-IB , the arguments passed can be summed up as follows:

- –dir E:\ specifies the folder to encrypt, in this case the E drive.

- –mode fast specifies the percentage of file to encrypt, in this case 5%.

- –verbose enables output verbosity.

- –noprint disables printing out the ransom note on connected printers.

After execution, the ransomware dropped the following ransom note.

Inhibit system recovery

While connected via RDP to the backup servers to deploy the ransomware payload, the threat actor also interacted with the backup software application present on these hosts.

In particular, the RDP bitmap cache of the beachhead host shows the threat actor opening the Veeam Backup & Replication console.

Using the console, they browsed the currently deployed backup jobs, the Veeam tape infrastructure, and the Veeam storage infrastructure.

Moreover, the threat actor removed backups from the configuration database, as shown in the partially reconstructed RDP bitmap cache below.

The following Veeam log for Job Deletion was also observed around the time of activity.

## Timeline

## Diamond Model

## Indicators

Atomic
RDP Initial Access:
195.211.190.189

RDP Follow Up Activity:
77.90.153.30

## Computed

File: netscan.exe
3073af95dfc18361caebccd69d0021a2
efe8b9ff7ff93780c9162959a4c1e5ecf6e840a4
517288e12c05a92e483e6d80b9136c19bc58c46851720680bb6d1b7016034c37

File: nxc.exe
7532ff90145b8c59dc9440bf43dc87a5
2b4b11d3ecffd82ed44db652cdd65733224f8e34
6285d32a9491a0084da85a384a11e15e203badf67b1deed54155f02b7338b108

File: w.exe
e2179046b86deca297ebf7398b95e438
3e01df0155a539fe6d802ee9e9226d8c77fd96c9
07b36c1660deb223749a8ac151676d8924bc13aa59e6712a3c14a2df5237264a

## Detections

Network
ET DROP Spamhaus DROP Listed Traffic Inbound group 7
ET DROP Spamhaus DROP Listed Traffic Inbound group 37
ET SCAN Behavioral Unusual Port 135 traffic Potential Scan or Infection
ET SCAN Behavioral Unusual Port 1433 traffic Potential Scan or Infection
Sigma

Search rules on detection.fyi or sigmasearchengine.com

DFIR Rules:
8a0d153f-b4e4-4ea7-9335-892dfbe17221 : NetScan Share Enumeration Write Access Check
53ad7638-3862-49a2-9ddd-af7132f9e598 : Using Netscan for Post-Scanning Lateral Movement
b26feb0b-8891-4e66-b2e7-ec91dc045d58 : AnyDesk Network
d7838d77-3a28-45cd-bc0e-7b941b687a39 : HyperVisor Discovery Activity
Sigma Repo:
c43c26be-2e87-46c7-8661-284588c5a53e : A Member Was Added to a Security-Enabled Global Group
f9d091f6-f1c7-4873-a24f-050b4a02b4dd : Command Executed Via Run Dialog Box – Registry
573df571-a223-43bc-846e-3f98da481eca : Creation Of a Suspicious ADS File Outside a Browser Download
8fbf3271-1ef6-4e94-8210-03c2317947f6 : Cred Dump Tools Dropped Files
259a9cdf-c4dd-4fa2-b243-2269e5ab18a2 : External Remote RDP Logon from Public IP
78d5cab4-557e-454f-9fb9-a222bd0d5edc : External Remote SMB Logon from Public IP
ac7102b4-9e1e-4802-9b4f-17c5524c015c : New PowerShell Instance Created
954f0af7-62dd-418f-b3df-a84bc2c7a774 : New Remote Desktop Connection Initiated Via Mstsc.EXE
ed74fe75-7594-4b4b-ae38-e38e3fd2eb23 : Outbound RDP Connections Over Non-Standard Tools
8eef149c-bd26-49f2-9e5a-9b00e3af499b : Pass the Hash Activity 2
d36f7c12-14a3-4d48-b6b8-774b9c66f44d : Potential Python DLL SideLoading
c2c76b77-32be-4d1f-82c9-7e544bdfe0eb : Potential Suspicious Activity Using SeCEdit
ca387a8e-1c84-4da3-9993-028b45342d30 : PUA - SoftPerfect Netscan Execution
cbb56d62-4060-40f7-9466-d8aaf3123f83 : Python Image Load By Non-Python Process
dae8171c-5ec6-4396-b210-8466585b53e9 : SCM Database Privileged Operation
b210394c-ba12-4f89-9117-44a2464b9511 : SMB Create Remote File Admin Share
91c945bc-2ad1-4799-a591-4d00198a1215 : Suspicious Access to Sensitive File Extensions
7be5fb68-f9ef-476d-8b51-0256ebece19e : Suspicious Execution of Hostname
0ef56343-059e-4cb6-adc1-4c3c967c5e46 : Suspicious Execution of Systeminfo
3037d961-21e9-4732-b27a-637bcc7bf539 : Suspicious High IntegrityLevel Conhost Legacy Option
910ab938-668b-401b-b08c-b596e80fdca5 : Transferring Files with Credential Data via Network Shares
e54979bd-c5f9-4d6c-967b-a04b19ac4c74 : Uncommon Outbound Kerberos Connection
a24e5861-c6ca-4fde-a93c-ba9256feddf0 : Uncommon Process Access Rights For Target Image
c265cf08-3f99-46c1-8d59-328247057d57 : User Added to Local Administrator Group
94309181-d345-4cbf-b5fe-061769bdf9cb : User with Privileges Logon
671bb7e3-a020-4824-a00e-2ee5b55f385e : WMI Module Loaded By Uncommon Process
Yara
MAL_RANSOM_INC_Aug24
Rule from Nextron-Systems’s analysis of Lynx Ransomware.

## MITRE ATT&CK

Additional Local or Domain Groups - T1098.007
Archive via Utility - T1560.001
Data Encrypted for Impact - T1486
Domain Account - T1136.002
Exfiltration Over Web Service - T1567
External Remote Services - T1133
Inhibit System Recovery - T1490
Local Account - T1087.001
Network Service Discovery - T1046
Network Share Discovery - T1135
PowerShell - T1059.001
Query Registry - T1012
Remote Access Software - T1219
Remote Desktop Protocol - T1021.001
Remote System Discovery - T1018
System Information Discovery - T1082
System Network Configuration Discovery - T1016
Valid Accounts - T1078
Windows Command Shell - T1059.003
Windows Service - T1543.003
Internal Case #TB34936 #PR38220

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
