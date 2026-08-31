---
title: "Threat Assessment: Ignoble Scorpius, Distributors of BlackSuit Ransomware"
source_url: "https://unit42.paloaltonetworks.com/threat-assessment-blacksuit-ransomware-ignoble-scorpius/"
published: "2024-11-20T11:00:53+00:00"
author: "Unit 42"
archived_at: "2026-08-25"
source_html: "Ignoble-Scorpius-BlackSuit.html"
---

# Threat Assessment: Ignoble Scorpius, Distributors of BlackSuit Ransomware
## Executive Summary

Unit 42 researchers have observed an increase in BlackSuit ransomware activity beginning in March 2024 that suggests a ramp up of operations. This threat emerged as a rebrand of Royal ransomware, which occurred in May 2023. Unit 42 tracks the group behind this threat as Ignoble Scorpius. Since the rebrand, Unit 42 has observed at least 93 victims globally, a quarter of which were in the construction and manufacturing industries.

The group describes themselves as an “extortioner named BlackSuit” and claims to reverse file encryption for “quite a small compensation essentially.” Although the group states the compensation is small, Unit 42 has observed that, on average, the initial ransom demand is about equal to 1.6% of the victim organization’s annual revenue. As of the date of this report, the median victim revenue across all industries is roughly $19.5 million , making the ransom payout quite significant for all organizations.

This threat assessment includes details identified during routine threat research activities, incident response cases and collaboration with the Unit 42 Managed Threat Hunting team.

This report maps the group’s activity to the MITRE ATT&CK® framework in that section , which organizations can use to assess their coverage of threats posed by Ignoble Scorpius, pre- and post-compromise.

Palo Alto Networks customers are better protected from the threats discussed above through the following products:

- The Unit 42 Managed Threat Hunting and Managed Detection and Response teams conduct proactive hunts for pre- and post-incident activity.

- Cortex XDR and XSIAM block and alert on known techniques and files associated with Ignoble Scorpius. We provide XQL queries in the MITRE ATT&CK TTPs section of this report.

- Palo Alto Networks Next-Generation Firewalls with cloud-delivered security services , including Advanced WildFire , detect known malicious files associated with Ignoble Scorpius.

- Organizations can engage the Unit 42 Incident Response team to help with a compromise or to provide a proactive assessment to lower your risk.

| Related Unit 42 Topics | BlackSuit Ransomware , Royal Ransomware , Ignoble Scorpius

| Related Unit 42 Themes | Cybercrime , Ransomware

## BlackSuit Ransomware Overview

BlackSuit ransomware emerged in May 2023 as a rebrand of the Royal ransomware . Unit 42 Threat Intelligence assesses that the group behind this threat is a direct evolution of Royal , and as such we track the group under the same moniker, Ignoble Scorpius.

Much like the operations as Royal ransomware, BlackSuit operates a dark web leak site where they publish their victims’ names and stolen data to extort them into paying a ransom. Figure 1 shows an excerpt of this site.

Figure 1. Screenshot of BlackSuit leak site.

Since the rebrand, Unit 42 has observed at least 93 victims globally and an upward trend in the number of successful compromises shared on their leak site. This suggests an overall ramping up of operations. Figure 2 below details the monthly total leak site posts from Ignoble Scorpius as BlackSuit.

Figure 2. Activity from Ignoble Scorpius under the BlackSuit name, May 2023 through October 2024.

The number of organizations truly impacted by the group is likely higher, as organizations can pay their ransom before ransomware operators post details on their leak sites to avoid reputational damage.

The median revenue of these victims was $19.5 million, which highlights the average size of organizations that the group has successfully targeted. Based on ransom negotiations observed by Unit 42, we can also estimate that the group’s initial ransom demand is equal to about 1.6% of the victim organization’s annual revenue.

Breaking down the 93 victims by sector indicates a preference for the education, construction and manufacturing sectors, as shown in Figure 3 below.

Figure 3. Pie chart breakdown of Ignoble Scorpius victimology.

Finally, as with many ransomware groups, Ignoble Scorpius’ victims are overwhelmingly based in the United States, as shown below in Figure 4.

Figure 4. Ignoble Scorpius’ geographical impact.

## Attack Lifecycle

The following sections highlight tactics, techniques and procedures (TTPs) observed from Ignoble Scorpius during BlackSuit incident response investigations Unit 42 conducted. Similar findings have also been shared by researchers at ReliaQuest and The DFIR Report .

### Initial Access

Initial access for Ignoble Scorpius, and ransomware groups in general, can be highly varied due to the prevalence of initial access brokers (IABs) who sell stolen credentials or other forms of access to organizations. While some threat actors obtain initial access on their own, others require the expertise of IABs to gain entry into a compromised network.

During an incident response investigation, delineating between the TTPs of a suspected IAB or the ransomware group is not always possible. Within Ignoble Scorpius’ ransomware cases, Unit 42 has observed many different initial access methods, including:

- Phishing campaigns with malicious email attachments ( T1566.001 );

- SEO poisoning with GootLoader ( T1608.006 );

- Using legitimate VPN credentials ( T1078 ), potentially obtained via social engineering and voice-based phishing (aka vishing) of executives ( T1566.004 )

- A software supply chain attack ( T1195.002 ).

### Credential Access and Privilege Escalation

Unit 42 has observed Ignoble Scorpius using common credential theft tools, such as Mimikatz and NanoDump , which is “a flexible tool that creates a minidump of the LSASS process.” Techniques observed include:

- Dumping LSASS via Taskmgr ( T1003.001 )

- Performing a DCSync attack ( T1003.006 )

- Using Impacket to conduct an adversary-in-the-middle (AiTM) attack ( T1557 )

- Requesting Kerberos service tickets ( T1558.002 )

Once they have obtained sufficiently privileged accounts (i.e., domain administrator on Windows systems) Ignoble Scorpius has been observed dumping the NTDS.dit file via ntdsutil , ( T1003.003 ) to compromise the domain controller.

### Lateral Movement

Unit 42 has observed Ignoble Scorpius making use of RDP ( T1021.001 ), SMB ( T1021.002 ) and PsExec ( T1570 ) to move laterally across systems.

### Defense Evasion

Unit 42 has observed Ignoble Scorpius and other ransomware groups making use of a vulnerable driver and loader, which are called STONESTOP and POORTRY by Mandiant . They use these tools to disable and evade antivirus and EDR solutions ( T1562.001 ).

### Exfiltration

Ignoble Scorpius has used various commonly available software and services to exfiltrate victim data. We observed WinRAR and 7-Zip being used to compress and stage files prior to exfiltration, after which attackers used WinSCP over FTP and Rclone to exfiltrate files. In at least one instance, attackers renamed Rclone to svchost.exe prior to execution ( T1048 ).

Unit 42 has also observed Ignoble Scorpius using a third-party project management application named Bublup to exfiltrate files ( T1567 , T1567.002 ). Threat actors often abuse, take advantage of or subvert legitimate products for malicious purposes. This does not imply that the legitimate product is flawed or malicious.

### Execution and Impact

As Ignoble Scorpius' goal is to encrypt and ransom a victim’s files, the primary payload of their campaigns is the BlackSuit ransomware. During incident response investigations involving BlackSuit, Unit 42 has also observed attackers using other tools for persistent access and the execution of arbitrary commands.

These additional tools include Cobalt Strike and SystemBC . In these cases it was not possible to identify whether Ignoble Scorpius or an IAB deployed the tools.

The final ransomware payload has Windows and Linux operating system variants with specific functionality to target VMware ESXi servers in some Linux variants.

#### Windows Variant

Unit 42’s analysis of the Windows variant found that the execution of the malware required the command-line argument -id followed by a 32-character value. The ID identifies the victim and grants access to a private chat room on Ignoble Scorpius' dark website to negotiate the ransom. They provide the ID to the victim via the ransom note. An example ransom note is shown below:

Good whatever time of day it is! Your safety service did a really poor job of protecting your files against our professionals. Extortioner named BlackSuit has attacked your system. As a result all your essential files were encrypted and saved at a secure server for further use and publishing on the Web into the public realm. Now we have all your files like: financial reports, intellectual property, accounting, law actions and complaints, personal files and so on and so forth. We are able to solve this problem in one touch. We (BlackSuit) are ready to give you an opportunity to get all the things back if you agree to make a deal with us. You have a chance to get rid of all possible financial, legal, insurance and many others risks and problems for a quite small compensation. You can have a safety review of your systems. All your files will be decrypted, your data will be reset, your systems will stay in safe. Contact us through TOR browser using the link: hxxp[://]weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd[.]onion/?id=[ID]

|

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

|

Good whatever time of day it is !

Your safety service did a really poor job of protecting your files against our professionals .

Extortioner named BlackSuit has attacked your system .

As a result all your essential files were encrypted and saved at a secure server for further use and publishing on the Web into the public realm .

Now we have all your files like : financial reports , intellectual property , accounting , law actions and complaints , personal files and so on and so forth .

We are able to solve this problem in one touch .

We ( BlackSuit ) are ready to give you an opportunity to get all the things back if you agree to make a deal with us .

You have a chance to get rid of all possible financial , legal , insurance and many others risks and problems for a quite small compensation .

You can have a safety review of your systems .

All your files will be decrypted , your data will be reset , your systems will stay in safe .

Contact us through TOR browser using the link :

hxxp [ : //]weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd[.]onion/?id=[ID]

Other command-line arguments for the Windows variant of BlackSuit malware are shown below in Table 1.

| Argument | Functionality

| -path | Specifies a target directory to encrypt

| -id | Victim ID

| -ep | Percentage of a file that should be encrypted

| -localonly | Encrypts only the local system

| -networkonly | Encrypts file shares connected to the system

Table 1. BlackSuit Windows variant command-line arguments.

Analysis of BlackSuit ransomware from TrendMicro and SentinelOne in 2023 identified more command-line flags than recent samples. This could be due to the ransomware group creating variants that target ESXi servers specifically, which we detail below , or a consolidation of functionality.

After the initial execution, the malware creates a mutual exclusion flag (aka mutex) with the value Global\WLm87eV1oNRx6P3E4Cy9 to prevent machines from being infected multiple times. As a result, the mutex chosen by Ignoble Scorpius needs to be a unique value that is not frequently changed. Unit 42 has observed attackers using this mutex as recently as June 2024, with open source highlighting its use as early as October 2023 .

To ensure the encryption of as many files as possible, the ransomware enumerates and terminates a list of known processes and services ( T1057 ). The ransomware also uses Windows Restart Manager ( rstrtmgr.dll ) to identify processes using files that would prevent encryption, terminating anything that isn't a critical process or the Windows File Explorer ( explorer.exe ). This is a technique commonly used by ransomware payloads .

The malware uses the following command to delete shadow backups ( T1490 ):

To execute the ransomware payload, researchers at ReliaQuest observed Ignoble Scorpius downloading VirtualBox and creating a virtual machine (VM) ( T1564.006 ). They copied the ransomware payload from the VM using PsExec ( T1570 ) to “hundreds of hosts via SMB” ( T1021.002 ). They then used Windows Management Instrumentation Command-line (WMIC) to load the ransomware as a library to execute it. This is a technique that Unit 42 has also observed from the group ( T1047 , T1218.010 ).

They then enumerate available files ( T1083 ) and encrypt them using OpenSSL AES, adding the extension .blacksuit to the encrypted file’s name ( T1486 ).

#### ESXi Variant

The ESXi variant, a Linux-based executable, targets virtual machines and introduces two more command-line flags:

- -vmkill (shuts down virtual machines before encryption if set)

- -crypt_all

If the -crypt_all flag is not set, the following files relating to VMware are encrypted:

- *.vmsd

- *.vmx

- *.vmxf

- *.vmdk

- *.vmem

- *.vmsn

- *.nvram

- *.vmx~

- *.vswp

- *.vmtx

- *.vmss

## Conclusion

Our analysis indicates that BlackSuit is a direct continuation of the activity under Royal, and as such we have opted to continue tracking the group under the same identifier as Royal – Ignoble Scorpius. The true effectiveness of rebranding is difficult to quantify. However, it can offer ransomware groups a respite from the scrutiny of researchers, law enforcement and the media.

A more subtle effect of rebranding is the perception it can have on defenders. For example, BlackSuit’s predecessor Royal and their predecessor Conti were some of the most reported and sophisticated ransomware groups while active.

As a result, organizations who were looking to assess their exposure to ransomware at the time could have looked toward the most prolific ransomware groups and attempted to cater their defensive solutions toward them. Rebranding resets this perception, and if it is accompanied with a shift in the group’s TTPs, it can place defenders on their back foot.

This is one of the primary reasons we chose to highlight Ignoble Scorpius’ BlackSuit ransomware in this report. Although the group as BlackSuit might not yet reach the top 10 list of ransomware groups by number of compromises, this group has the following qualities:

- They conduct complex supply chain attacks

- They exhibit a high level of sophistication compromising at least 93 organizations without a public-facing RaaS program

- Their membership likely includes members from Conti and Royal ransomware

This report maps the group’s activity to the MITRE ATT&CK framework in the that section below. Organizations can use this information to assess their coverage of threats posed by Ignoble Scorpius, pre- and post-compromise.

## Protections and Mitigations

Palo Alto Networks customers are better protected from the threats discussed above through the following products:

- The Unit 42 Managed Threat Hunting and Managed Detection and Response teams conduct proactive hunts for pre- and post-incident activity.

- Cortex XDR and XSIAM block and alert on known techniques and files associated with Ignoble Scorpius. We provide XQL queries in the MITRE ATT&CK TTPs section of this report.

- Palo Alto Networks Next-Generation Firewalls with Cloud-Delivered Security Services , including Advanced WildFire , detect known malicious files associated with Ignoble Scorpius.

If you think you may have been compromised or have an urgent matter, get in touch with the Unit 42 Incident Response team or call:

- North America Toll-Free: 866.486.4842 (866.4.UNIT42)

- EMEA: +31.20.299.3130

- APAC: +65.6983.8730

- Japan: +81.50.1790.0200

Palo Alto Networks has shared these findings with our fellow Cyber Threat Alliance (CTA) members. CTA members use this intelligence to rapidly deploy protections to their customers and to systematically disrupt malicious cyber actors. Learn more about the Cyber Threat Alliance .

## Additional Resources

- BlackSuit Attack Analysis – ReliaQuest Threat Research Team

- BlackSuit Ransomware – The DFIR Report

- Threat Actor Spotlight: BlackSuit Ransomware – Arete Incident Response

- #StopRansomware: Blacksuit (Royal) Ransomware – Cybersecurity and Infrastructure Security Agency (CISA)

## MITRE ATT&CK TTPs

Table 2 below depicts the MITRE ATT&CK TTPs mapping for techniques referenced in this report.

| ID | Tactic | Technique Name | Procedure

| T1570 | Lateral Movement | Lateral Tool Transfer | Uses PsExec for lateral movement and tool transfer

| T1567.002 | Exfiltration | Exfiltration Over Web Service: Exfiltration to Cloud Storage | Uses RClone and Bublup for data exfiltration

| T1566.004 | Initial Access | Phishing: Spearphishing Voice | Uses vishing with executives

| T1566.001 | Initial Access | Phishing: Spearphishing Attachment | Sends phishing emails using malicious attachments

| T1564.006 | Defense Evasion | Hide Artifacts: Run Virtual Instance | Uses VirtualBox to create virtual machines

| T1562.001 | Defense Evasion | Impair Defenses: Disable or Modify Tools | Vulnerable drivers/loaders used to disable and evade antivirus and EDR solutions

| T1558.004 | Credential Access | Steal or Forge Kerberos Tickets: AS-REP Roasting | Uses toolkits such as Rubeus to compromise accounts using AS-REP roasting

| T1558.003 | Credential Access | Steal or Forge Kerberos Tickets: Kerberoasting | Uses toolkits such as Rubeus to compromise accounts using Kerberoasting

| T1558.002 | Credential Access | Steal or Forge Kerberos Tickets: Silver Ticket | Requests Kerberos service tickets

| T1557 | Collection, Credential Access | Adversary-in-the-Middle | Uses Impacket to conduct AitM attacks

| T1490 | Impact | Inhibit System Recovery | Deletes shadow copies using a specific vssadmin.exe command

| T1486 | Impact | Data Encrypted for Impact | Files are encrypted with the .blacksuit file extension

| T1218.010 | Defense Evasion | System Binary Proxy Execution: Regsvr32 | WMIC used to load the ransomware as a library, executing it through regsvr32.exe

| T1195.002 | Initial Access | Supply Chain Compromise: Compromise Software Supply Chain | Uses supply chain compromise for initial access

| T1189 | Initial Access | Drive-by Compromise | Search engine optimization (SEO) poisoning with GootLoader

| T1140 | Defense Evasion | Deobfuscate/Decode Files or Information | Uses stack strings to obfuscate data

| T1110 | Credential Access | Brute Force | Conducted brute-force attacks against virtual private network (VPN) gateways not configured with multi-factor authentication (MFA)

| T1083 | Discovery | File and Directory Discovery | Enumerates files and encrypts all found

| T1078 | Defense Evasion, Initial Access, Persistence, Privilege Escalation | Valid Accounts | Uses legitimate VPN credentials or password dumps

| T1071 | Command and Control | Application Layer Protocol | Uses multiple protocols alongside the Cobalt Strike post-exploitation framework

| T1059.007 | Execution | Command and Scripting Interpreter: JavaScript | Wscript makes an external connection upon executing a JavaScript file

| T1059.001 | Execution | Command and Scripting Interpreter: PowerShell | Uses the default PowerShell string for command execution on a remote host

| T1057 | Discovery | Process Discovery | The Windows Restart Manager ( rstrtmgr.dll ) is used to identify processes using files that would prevent encryption, terminating anything that isn't a critical process

| T1048 | Exfiltration | Exfiltration Over Alternative Protocol | Rclone is sometimes renamed to svchost.exe prior to execution and exfiltration over alternative protocols

| T1047 | Execution | Windows Management Instrumentation | Impacket framework execution relating to wmiexec ; uses WMIC to load the ransomware as a library

| T1036 | Defense Evasion | Masquerading | Renaming PE files (e.g., Rclone.exe to 1.exe )

| T1027.007 | Defense Evasion | Obfuscated Files or Information: Dynamic API Resolution | Uses dynamic API resolution to conceal functionality

| T1021.002 | Lateral Movement | Remote Services: SMB/Windows Admin Shares | Copies the ransomware payload from VMs using PSExec to numerous hosts using SMB

| T1021.001 | Lateral Movement | Remote Services: Remote Desktop Protocol | Uses remote desktop protocol (RDP) for lateral movement

| T1003.006 | Credential Access | OS Credential Dumping: DCSync | Conducts a DCSync attack for credential access

| T1003.003 | Credential Access | OS Credential Dumping: NTDS | Uses ntdsutil.exe to dump Active Directory database

| T1003.001 | Credential Access | OS Credential Dumping: LSASS Memory | LSASS dumped via the Task Manager

Table 2. MITRE ATT&CK techniques.

## XDR Query Language (XQL) Queries

This section documents relevant TTPs used by Ignoble Scorpius and maps them directly to Palo Alto Networks Cortex XQL queries. These queries detect renamed tools with Cortex XDR.

Like many ransomware actors, Ignoble Scorpius likes to rename their Portable Executable (PEs) files. For example, rather than execute a tool such as Rclone as rclone.exe , the actor might rename it to something else, such as svchost.exe .

In the case mentioned above, a query for action_process_image_name = “rclone.exe” in Cortex XDR’s Query Language (XQL) will fail. However, Cortex XDR can identify these files even if they’ve been renamed.

When a PE is compiled, it often includes a resource called VERSIONINFO . This resource can contain the original file name, the company that produced the software, and more. Though ransomware actors can rename executables, they rarely alter the VERSIONINFO resource.

We can extract the VERSIONINFO from PEs that run on a host using Cortex XDR with the action_process_file_info field in the ENUM.PROCESS filter set, shown in the following XQL query snippet.

config case_sensitive = false | dataset = xdr_data | filter event_type = ENUM.PROCESS and event_sub_type = ENUM.PROCESS_START | alter action_process_original_name = action_process_file_info -> original_name, action_process_company_name = action_process_file_info -> company, action_process_description = action_process_file_info -> description, action_process_internal_name = action_process_file_info -> internal_name, action_process_legal_copyright = action_process_file_info -> legal_copyright

|

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

|

config case_sensitive = false

| dataset = xdr_data

| filter event_type = ENUM . PROCESS and event_sub_type = ENUM . PROCESS_START

| alter

action_process_original_name = action_process_file_info - > original_name ,

action_process_company_name = action_process_file_info - > company ,

action_process_description = action_process_file_info - > description ,

action_process_internal_name = action_process_file_info - > internal_name ,

action_process_legal_copyright = action_process_file_info - > legal_copyright

Table 3 below highlights data from the VERSIONINFO resource, which is extracted for running processes by the above query.

| VERSIONINFO Data | Description

| original_name | The original name of a PE upon compilation

| company | The company that released the software

| description | A description of the compiled software

| internal_name | The internal name of the PE. This is often equal to or very similar to the original_name .

| legal_copyright | A copyright notification from the releasing company

Table 3. Ignoble Scorpius data extraction.

Once the VERSIONINFO data has been extracted, XQL can then be used to filter on known version info values from executables. The following is an example filter set that will identify renamed versions of Rclone’s default executable, rclone.exe .

| filter (action_process_image_name = "rclone.exe" or action_process_original_name ~= "rclone" or action_process_company_name ~= "https\:\/\/rclone\.org" or action_process_description ~= "rclone" or action_process_internal_name ~= "rclone" or action_process_legal_copyright = "The Rclone Authors")

|

1

2

3

4

5

6

7

8

9

10

11

12

13

|

| filter

( action_process_image_name = "rclone.exe" or

action_process_original_name ~ = "rclone" or

action_process_company_name ~ = "https\:\/\/rclone\.org" or

action_process_description ~ = "rclone" or

action_process_internal_name ~ = "rclone" or

action_process_legal_copyright = "The Rclone Authors" )

Some of the Cortex XDR queries we’ve included in this report use the above method for identifying renamed executables.

### 1. GootLoader: Wscript Making External Connection

Technique description: The query looks for wscript.exe making external connections upon executing a JavaScript ( .js ) file, which could be indicative of GootLoader activity. The query restricts results to user-based Downloads or Temp folders, as these are the directories most commonly associated with GootLoader infections.

#### MITRE ATT&CK TTP ID

- T1059.007 Execution - Command and Scripting Interpreter: JavaScript

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.STORY and agent_os_type = ENUM.AGENT_OS_WINDOWS | filter actor_process_image_name = "wscript.exe" and actor_process_command_line contains ".js" | filter actor_process_command_line contains "\Users\*\Downloads" or actor_process_command_line contains "\Users\*\Temp" | filter dst_is_internal_ip = False | fields _time, agent_hostname, actor_effective_username,actor_process_image_name, actor_process_command_line, action_remote_ip, dst_action_external_hostname | sort desc _time

|

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . STORY and agent_os_type = ENUM . AGENT_OS_WINDOWS

| filter actor_process_image_name = "wscript.exe" and actor_process_command_line contains ".js"

| filter actor_process_command_line contains "\Users\*\Downloads" or actor_process_command_line contains "\Users\*\Temp"

| filter dst_is_internal_ip = False

| fields _time , agent_hostname , actor_effective_username , actor_process_image_name , actor_process_command_line , action_remote_ip , dst_action_external_hostname

| sort desc _time

### 2. Dumping LSASS via Task Manager

Technique description: The query looks for LSASS being dumped via the Task Manager. To identify this activity, we focus on lsass.DMP files being created via the Taskmgr.exe process.

#### MITRE ATT&CK TTP ID

- T1003.001 Credential Access - OS Credential Dumping: LSASS Memory

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.FILE and event_sub_type = ENUM.FILE_CREATE_NEW and agent_os_type = ENUM.AGENT_OS_WINDOWS | filter action_file_name = "lsass.DMP" and actor_process_image_name = "Taskmgr.exe" | fields agent_hostname, event_type, event_sub_type, action_file_name, action_file_path, action_file_sha256, action_file_md5, actor_process_image_name, actor_process_image_path, actor_process_image_command_line | sort desc _time

|

1

2

3

4

5

6

7

8

9

10

11

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . FILE and event_sub_type = ENUM . FILE_CREATE_NEW and agent_os_type = ENUM . AGENT_OS_WINDOWS

| filter action_file_name = "lsass.DMP" and actor_process_image_name = "Taskmgr.exe"

| fields agent_hostname , event_type , event_sub_type , action_file_name , action_file_path , action_file_sha256 , action_file_md5 , actor_process_image_name , actor_process_image_path , actor_process_image_command_line

| sort desc _time

### 3. Impacket Process Execution

Technique description: The query looks for signs of Impacket framework execution, especially relating to smbexec and wmiexec . It focuses on the default PowerShell string used for command execution on the remote host.

#### MITRE ATT&CK TTP IDs

- T1059.001 Execution - Command and Scripting Interpreter: PowerShell

- T1047 Execution - Windows Management Instrumentation

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.PROCESS and agent_os_type = ENUM.AGENT_OS_WINDOWS | filter (causality_actor_process_image_name = "wmiprvse.exe" or causality_actor_process_image_name = "services.exe") and actor_process_image_name = "powershell.exe" | filter actor_process_command_line ~= "-NoP -NoL -sta -NonI -W Hidden -Exec Bypass -Enc" | sort desc _time

|

1

2

3

4

5

6

7

8

9

10

11

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . PROCESS and agent_os_type = ENUM . AGENT_OS_WINDOWS

| filter ( causality_actor_process_image_name = "wmiprvse.exe" or causality_actor_process_image_name = "services.exe" ) and actor_process_image_name = "powershell.exe"

| filter actor_process_command_line ~ = "-NoP -NoL -sta -NonI -W Hidden -Exec Bypass -Enc"

| sort desc _time

### 4. Mimikatz and Rubeus Execution

Technique description: The query looks for signs of Mimiktaz or Rubeus executing within the environment. It takes into account renamed process image files by using PE metadata to identify VERSIONINFO data of executing processes.

#### MITRE ATT&CK TTP ID

- T1003.001 Credential Access - OS Credential Dumping: LSASS Memory

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.PROCESS and event_sub_type = ENUM.PROCESS_START and agent_os_type = ENUM.AGENT_OS_WINDOWS | alter action_process_original_name = action_process_file_info -> original_name, action_process_company_name = action_process_file_info -> company, action_process_description = action_process_file_info -> description, action_process_internal_name = action_process_file_info -> internal_name, action_process_legal_copyright = action_process_file_info -> legal_copyright | filter (action_process_image_name ~= "(mimikatz|rubeus)\.exe" or action_process_original_name ~= "(mimikatz|rubeus)" or action_process_description ~= "(mimikatz|rubeus)" or action_process_internal_name ~= "(mimikatz|rubeus)") | fields _time, agent_hostname, agent_ip_addresses, actor_effective_username, action_process_image_name, action_process_image_path, action_process_image_command_line, action_process_image_sha256, actor_process_image_name, actor_process_image_path, actor_process_command_line, actor_process_image_sha256, os_actor_process_command_line, action_process_original_name, action_process_company_name, action_process_description, action_process_internal_name, action_process_legal_copyright, action_process_file_info | sort desc _time

|

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . PROCESS and event_sub_type = ENUM . PROCESS_START and agent_os_type = ENUM . AGENT_OS_WINDOWS

| alter

action_process_original_name = action_process_file_info - > original_name ,

action_process_company_name = action_process_file_info - > company ,

action_process_description = action_process_file_info - > description ,

action_process_internal_name = action_process_file_info - > internal_name ,

action_process_legal_copyright = action_process_file_info - > legal_copyright

| filter ( action_process_image_name ~ = "(mimikatz|rubeus)\.exe" or action_process_original_name ~ = "(mimikatz|rubeus)" or action_process_description ~ = "(mimikatz|rubeus)" or action_process_internal_name ~ = "(mimikatz|rubeus)" )

| fields _time , agent_hostname , agent_ip_addresses , actor_effective_username , action_process_image_name , action_process_image_path , action_process_image_command_line , action_process_image_sha256 , actor_process_image_name , actor_process_image_path , actor_process_command_line , actor_process_image_sha256 , os_actor_process_command_line , action_process_original_name , action_process_company_name , action_process_description , action_process_internal_name , action_process_legal_copyright , action_process_file_info

| sort desc _time

### 5. Active Directory Dumping via NTDSUTIL

Technique description: The query looks for the use of ntdsutil.exe to dump the Active Directory database ( NTDS.dit ).

#### MITRE ATT&CK TTP ID

- Credential Access - T1003.003 OS Credential Dumping: NTDS

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.PROCESS and event_sub_type = ENUM.PROCESS_START and agent_os_type = ENUM.AGENT_OS_WINDOWS | filter action_process_image_name = "ntdsutil.exe" and (action_process_image_command_line contains "ac i ntds" or action_process_image_command_line contains "activate instance ntds") and action_process_image_command_line contains "create full" | fields _time, agent_hostname, agent_ip_addresses, actor_effective_username, action_process_image_name, action_process_image_path, action_process_image_command_line, action_process_image_sha256, actor_process_image_name, actor_process_image_path, actor_process_command_line, actor_process_image_sha256, os_actor_process_command_line, action_process_file_info | sort desc _time

|

1

2

3

4

5

6

7

8

9

10

11

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . PROCESS and event_sub_type = ENUM . PROCESS_START and agent_os_type = ENUM . AGENT_OS_WINDOWS

| filter action_process_image_name = "ntdsutil.exe" and ( action_process_image_command_line contains "ac i ntds" or action_process_image_command_line contains "activate instance ntds" ) and action_process_image_command_line contains "create full"

| fields _time , agent_hostname , agent_ip_addresses , actor_effective_username , action_process_image_name , action_process_image_path , action_process_image_command_line , action_process_image_sha256 , actor_process_image_name , actor_process_image_path , actor_process_command_line , actor_process_image_sha256 , os_actor_process_command_line , action_process_file_info

| sort desc _time

### 6. Cobalt Strike Combined Query

Technique description: The query looks for a combination of identifiers related to the Cobalt Strike post-exploitation framework. Though the tool is used legitimately by pentesting, red teaming and emulation teams alike, threat actors such as BlackSuit also like to use the tool.

#### MITRE ATT&CK TTP ID

- T1071 Command and Control - Application Layer Protocol

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter (event_type = ENUM.PROCESS AND event_sub_type = ENUM.PROCESS_START and actor_process_image_name = "services.exe" and action_process_image_command_line ~= ".+\\admin\$\\[a-z0-9]{7}\.exe") or (event_type = ENUM.PROCESS AND event_sub_type = ENUM.PROCESS_START and (action_process_image_command_line = "c:\windows\system32\rundll32.exe" or action_process_image_command_line = "c:\windows\syswow64\rundll32.exe" and actor_process_image_name != "setup.exe" and actor_process_command_line not contains "chrome" and actor_process_command_line not contains "edge")) or (event_type = ENUM.FILE and action_file_path ~= "\\device\\namedpipe\\msse-\d+-server" or action_file_path ~= "\\device\\namedpipe\\postex_[a-z0-9]{4}" or action_file_path ~= "\\device\\namedpipe\\status_[a-z0-9]{4}" or action_file_path ~= "\\device\\namedpipe\\msagent_[a-z0-9]{4}") or (event_type = ENUM.PROCESS AND event_sub_type = ENUM.PROCESS_START and (action_process_image_name contains "powershell.exe" OR actor_process_image_name contains "cmd.exe") AND ((action_process_image_command_line contains "-enc jabzad0" OR action_process_image_command_line contains "-encodedcommand jabzad0"))) or (event_type = ENUM.STORY and dst_action_external_hostname contains "aaa.stage") or (event_type = ENUM.EVENT_LOG and (action_evtlog_message ~= "\$s=New-Object IO.MemoryStream" OR action_evtlog_message ~= "\$var_code")) | fields agent_hostname, agent_id, agent_ip_addresses , agent_version, actor_effective_username, actor_process_image_name, actor_process_image_path, actor_process_command_line, action_process_image_command_line, action_file_path, action_evtlog_username, action_evtlog_message, actor_process_signature_vendor | filter not ((actor_process_image_path contains "Microsoft\EdgeWebView\Application" or actor_process_image_path contains "Microsoft\EdgeUpdate\Install" or actor_process_image_path contains "Microsoft\Edge\Application" or actor_process_image_path contains "Chromium" or actor_process_image_path contains "Installer\setup.exe") and (actor_process_signature_vendor = "Microsoft Corporation" or actor_process_image_name = "setup.exe")) | sort desc _time

|

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter ( event_type = ENUM . PROCESS AND event_sub_type = ENUM . PROCESS_START and actor_process_image_name = "services.exe" and action_process_image_command_line ~ = ".+\\admin\$\\[a-z0-9]{7}\.exe" )

or ( event_type = ENUM . PROCESS AND event_sub_type = ENUM . PROCESS_START and ( action_process_image_command_line = "c:\windows\system32\rundll32.exe" or action_process_image_command_line = "c:\windows\syswow64\rundll32.exe" and actor_process_image_name ! = "setup.exe" and actor_process_command_line not contains "chrome" and actor_process_command_line not contains "edge" ) )

or ( event_type = ENUM . FILE and action_file_path ~ = "\\device\\namedpipe\\msse-\d+-server" or action_file_path ~ = "\\device\\namedpipe\\postex_[a-z0-9]{4}" or action_file_path ~ = "\\device\\namedpipe\\status_[a-z0-9]{4}" or action_file_path ~ = "\\device\\namedpipe\\msagent_[a-z0-9]{4}" )

or ( event_type = ENUM . PROCESS AND event_sub_type = ENUM . PROCESS_START and ( action_process_image_name contains "powershell.exe" OR actor_process_image_name contains "cmd.exe" ) AND ( ( action_process_image_command_line contains "-enc jabzad0" OR action_process_image_command_line contains "-encodedcommand jabzad0" ) ) )

or ( event_type = ENUM . STORY and dst_action_external_hostname contains "aaa.stage" )

or ( event_type = ENUM . EVENT_LOG and ( action_evtlog_message ~ = "\$s=New-Object IO.MemoryStream" OR action_evtlog_message ~ = "\$var_code" ) )

| fields agent_hostname , agent_id , agent_ip_addresses , agent_version , actor_effective_username , actor_process_image_name , actor_process_image_path , actor_process_command_line , action_process_image_command_line , action_file_path , action_evtlog_username , action_evtlog_message , actor_process_signature_vendor

| filter not ( ( actor_process_image_path contains "Microsoft\EdgeWebView\Application" or actor_process_image_path contains "Microsoft\EdgeUpdate\Install" or actor_process_image_path contains "Microsoft\Edge\Application" or actor_process_image_path contains "Chromium" or actor_process_image_path contains "Installer\setup.exe" ) and ( actor_process_signature_vendor = "Microsoft Corporation" or actor_process_image_name = "setup.exe" ) )

| sort desc _time

### 7. Rclone Exfiltration

Technique description: The query looks for data exfiltration via Rclone, a tool used by BlackSuit to exfiltrate data from victim environments. It takes into account renamed process image files by using PE metadata to identify VERSIONINFO data of executing processes.

#### MITRE ATT&CK TTP IDs

- T1567 Exfiltration - Exfiltration Over Web Service

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.PROCESS and event_sub_type = ENUM.PROCESS_START and agent_os_type = ENUM.AGENT_OS_WINDOWS | alter action_process_original_name = action_process_file_info -> original_name, action_process_company_name = action_process_file_info -> company, action_process_description = action_process_file_info -> description, action_process_internal_name = action_process_file_info -> internal_name, action_process_legal_copyright = action_process_file_info -> legal_copyright | filter (action_process_image_name = "rclone.exe" or action_process_original_name ~= "rclone" or action_process_company_name ~= "https\:\/\/rclone\.org" or action_process_description ~= "rclone" or action_process_internal_name ~= "rclone" or action_process_legal_copyright = "The Rclone Authors") and action_process_image_command_line in ("*lsd*", "*remote:*", "*mega*", "*--config*", "*--auto-confirm*", "*or --multi-thread-streams and copy*", "*config*", "*create*", "*user*", "*pass*", "*progress*", "*no-check-certificate*", "*ignore-existing*", "*auto-confirm*", "*multi-thread-streams*", "*transfers*", "*ftp:*") | fields _time, agent_hostname, agent_ip_addresses, actor_effective_username, action_process_image_name, action_process_image_path, action_process_image_command_line, action_process_image_sha256, actor_process_image_name, actor_process_image_path, actor_process_command_line, actor_process_image_sha256, os_actor_process_command_line | sort desc _time

|

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . PROCESS and event_sub_type = ENUM . PROCESS_START and agent_os_type = ENUM . AGENT_OS_WINDOWS

| alter

action_process_original_name = action_process_file_info - > original_name ,

action_process_company_name = action_process_file_info - > company ,

action_process_description = action_process_file_info - > description ,

action_process_internal_name = action_process_file_info - > internal_name ,

action_process_legal_copyright = action_process_file_info - > legal_copyright

| filter

( action_process_image_name = "rclone.exe" or

action_process_original_name ~ = "rclone" or

action_process_company_name ~ = "https\:\/\/rclone\.org" or

action_process_description ~ = "rclone" or

action_process_internal_name ~ = "rclone" or

action_process_legal_copyright = "The Rclone Authors" ) and

action_process_image_command_line in ( "*lsd*" , "*remote:*" , "*mega*" , "*--config*" , "*--auto-confirm*" , "*or --multi-thread-streams and copy*" , "*config*" , "*create*" , "*user*" , "*pass*" , "*progress*" , "*no-check-certificate*" , "*ignore-existing*" , "*auto-confirm*" , "*multi-thread-streams*" , "*transfers*" , "*ftp:*" )

| fields _time , agent_hostname , agent_ip_addresses , actor_effective_username , action_process_image_name , action_process_image_path , action_process_image_command_line , action_process_image_sha256 , actor_process_image_name , actor_process_image_path , actor_process_command_line , actor_process_image_sha256 , os_actor_process_command_line

| sort desc _time

### 8. Shadow Copy Deletion via VSSADMIN

Technique description: The query looks for deletion of shadow copies using a specific vssadmin.exe command associated with the BlackSuit encryptor.

#### MITRE ATT&CK TTP IDs

- T1490 Impact - Inhibit System Recovery

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.PROCESS and event_sub_type = ENUM.PROCESS_START and agent_os_type = ENUM.AGENT_OS_WINDOWS | filter action_process_image_command_line ~= "cmd.exe\s+\/c\svssadmin\sdelete\sshadows\s\/all\s\/quiet" or actor_process_image_command_line ~= "cmd.exe\s+\/c\svssadmin\sdelete\sshadows\s\/all\s\/quiet" | fields _time, agent_hostname, agent_ip_addresses, actor_effective_username, action_process_image_name, action_process_image_path, action_process_image_command_line, action_process_image_sha256, actor_process_image_name, actor_process_image_path, actor_process_command_line, actor_process_image_sha256, os_actor_process_command_line, action_process_file_info | sort desc _time

|

1

2

3

4

5

6

7

8

9

10

11

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . PROCESS and event_sub_type = ENUM . PROCESS_START and agent_os_type = ENUM . AGENT_OS_WINDOWS

| filter action_process_image_command_line ~ = "cmd.exe\s+\/c\svssadmin\sdelete\sshadows\s\/all\s\/quiet" or actor_process_image_command_line ~ = "cmd.exe\s+\/c\svssadmin\sdelete\sshadows\s\/all\s\/quiet"

| fields _time , agent_hostname , agent_ip_addresses , actor_effective_username , action_process_image_name , action_process_image_path , action_process_image_command_line , action_process_image_sha256 , actor_process_image_name , actor_process_image_path , actor_process_command_line , actor_process_image_sha256 , os_actor_process_command_line , action_process_file_info

| sort desc _time

### 9. BlackSuit Mutex

Technique description: The query looks for the mutex created by the BlackSuit encryptor. This mutex is created and checked upon execution to ensure no more than a single encryptor runs at one time.

#### MITRE ATT&CK TTP ID

- T1027 Execution - Obfuscated Files or Information

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.SYSTEM_CALL and event_sub_type = ENUM.SYSTEM_CALL_NT_CREATE_MUTANT and agent_os_type = ENUM.AGENT_OS_WINDOWS | fields agent_hostname, action_syscall_string_params | alter syscall_mutant_name = json_extract(action_syscall_string_params, "$.1") | alter syscall_mutant_name = trim(to_string(syscall_mutant_name),"\"") | filter syscall_mutant_name ~= "WLm87eV1oNRx6P3E4Cy9" | sort desc _time

|

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . SYSTEM_CALL and event_sub_type = ENUM . SYSTEM_CALL_NT_CREATE_MUTANT and agent_os_type = ENUM . AGENT_OS_WINDOWS

| fields agent_hostname , action_syscall_string_params

| alter syscall_mutant_name = json_extract ( action_syscall_string_params , "$.1" )

| alter syscall_mutant_name = trim ( to_string ( syscall_mutant_name ) , "\"" )

| filter syscall_mutant_name ~ = "WLm87eV1oNRx6P3E4Cy9"

| sort desc _time

### 10. BlackSuit Encrypted Files

Technique description: The query looks for files encrypted with the .blacksuit file suffix, which indicates the BlackSuit encryptor has encrypted the file.

#### MITRE ATT&CK TTP ID

- T1486 Impact - Data Encrypted for Impact

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.FILE and action_file_extension ~= "blacksuit" | fields agent_hostname, event_type, event_sub_type, action_file_name, action_file_path, action_file_sha256, action_file_md5, actor_process_image_name, actor_process_image_path, actor_process_image_command_line

|

1

2

3

4

5

6

7

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . FILE and action_file_extension ~ = "blacksuit"

| fields agent_hostname , event_type , event_sub_type , action_file_name , action_file_path , action_file_sha256 , action_file_md5 , actor_process_image_name , actor_process_image_path , actor_process_image_command_line

### 11. BlackSuit Ransom Note

Technique description: The query looks for known names of the BlackSuit encryptor’s ransomware notes.

#### MITRE ATT&CK TTP ID

- T1486 Impact - Data Encrypted for Impact

#### XQL Query

config case_sensitive = false timeframe = 30d | dataset = xdr_data | filter event_type = ENUM.FILE and event_sub_type = ENUM.FILE_CREATE_NEW and action_file_name ~= "README.BlackSuit.txt" | fields agent_hostname, event_type, event_sub_type, action_file_name, action_file_path, action_file_sha256, action_file_md5, actor_process_image_name, actor_process_image_path, actor_process_image_command_line

|

1

2

3

4

5

6

7

|

config case_sensitive = false timeframe = 30d

| dataset = xdr_data

| filter event_type = ENUM . FILE and event_sub_type = ENUM . FILE_CREATE_NEW and action_file_name ~ = "README.BlackSuit.txt"

| fields agent_hostname , event_type , event_sub_type , action_file_name , action_file_path , action_file_sha256 , action_file_md5 , actor_process_image_name , actor_process_image_path , actor_process_image_command_line
