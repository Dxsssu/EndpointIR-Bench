---
title: "Apache ActiveMQ Exploit Leads to LockBit Ransomware - The DFIR Report"
source_url: "https://thedfirreport.com/2026/02/23/apache-activemq-exploit-leads-to-lockbit-ransomware/"
published: "2026-02-23T14:09:43+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2026-02-23_Apache-ActiveMQ-to-LockBit.html"
---

# Apache ActiveMQ Exploit Leads to LockBit Ransomware - The DFIR Report
## Key Takeaways

- A threat actor exploited CVE-2023-46604 on an internet-facing Apache ActiveMQ server. Despite being evicted after the initial intrusion, they successfully breached the same server on a second occasion 18 days later.

- After compromising the server, the threat actor used Metasploit, possibly along with Meterpreter, to perform post-exploitation activities. These activities included escalating privileges, accessing LSASS process memory, and moving laterally across the network.

- After regaining access following their eviction, the threat actor swiftly transitioned to deploying ransomware. They leveraged credentials extracted during their previous breach to deploy LockBit ransomware via RDP.

- Although the ransomware binary aligns with LockBit signatures, we believe it was crafted using the leaked LockBit builder because the ransom note had been modified, and communication methods relied exclusively on the Session messaging service.

An audio version of this report can be found on Spotify , Apple , YouTube , Audible , & Amazon .

## Case Summary

This intrusion began in mid-February 2024 after a threat actor exploited a vulnerability (CVE-2023-46604) on an exposed Apache ActiveMQ server. The threat actor was able to perform remote code execution (RCE) by using a Java Spring class and a custom Java Spring bean configuration XML file. The malicious XML contained a command that downloaded a payload from a remote server using the Windows CertUtil utility.

The payload was successfully downloaded and executed on the beachhead host. This payload turned out to be a Metasploit stager. Around 40 minutes after the initial exploit, we observed the threat actor’s next actions. The first evidence of the GetSystem command was observed, resulting in the achievement of SYSTEM level permissions. After that, LSASS process memory was accessed on the beachhead by the Metasploit process.

Around 20 minutes after that, we observed a spike in SMB traffic from the beachhead host to systems across the network, likely attributable to network scanning by the threat actor. While the scanning occurred, we noted lateral movement activity, with the threat actor using a domain administrator account to run remote services and execute Metasploit payloads on several remote hosts. Several of these hosts then also had LSASS process memory accessed by the malicious processes created by the remote services. One of these hosts had a privileged service account configured to run an application, which would be used later in the intrusion. While the threat actor gained extensive access throughout the environment, some targeted hosts were running active antivirus that detected and prevented lateral Metasploit activity.

On the second day of the intrusion, the threat actor returned to the beachhead host and ran some more standard discovery commands using various Windows utilities. Many of the commands contained syntax errors, and the threat actor also tried to add the account they used the prior day to the domain admin group; however, that account was already a member of the group. Shortly after this, the threat actor lost access to the environment.

18 days after their first exploitation of CVE-2023-46604, the threat actor returned. They used the same access path, exploiting the same unpatched Apache ActiveMQ server, and regained access to the environment. After this, they repeated the same GetSystem and LSASS access as previously observed on the beachhead during the first round of the intrusion.

Shortly after gaining access, they performed a quick check of the domain admin group and then, 20 minutes later, proceeded to move laterally to several servers, including domain controllers. This lateral movement involved the same remote service execution of a Metasploit payload and used the same C2 server as 18 days prior. The account used for this activity was the privileged service account that we assess was dumped from LSASS on one of the hosts during the first round of the intrusion.

They then began using RDP to log into other servers, including a backup server and a file server, while continuing their remote service executions. They dropped a batch file and AnyDesk installer on the beachhead host. A series of commands were then executed to ensure RDP was enabled and the required ports opened, after which AnyDesk was installed.

After that, several more executables were dropped via the Metasploit process on the beachhead. These included a renamed Advanced IP Scanner binary and two LockBit ransomware files. Advanced IP Scanner was then run, and the threat actor began another round of RDP connections. This time, when they accessed the backup and file servers via RDP, they dropped and executed one of the LockBit ransomware binaries with specific path and password flags.

They continued RDP connections to hosts across the network using the other LockBit ransomware file. This included dropping it into the user’s Downloads folder and executing it via a simple double-click. This activity continued for approximately four hours until the threat actor was satisfied with their deployment and ceased activity. The Time to Ransomware (TTR) for this intrusion was 419 hours — approximately 19 calendar days from initial access to ransomware deployment. However, if the organization failed to detect the first half of the intrusion and only became aware of activity when the threat actor re-engaged, they would have had less than 90 minutes before ransomware execution.

If you would like to get an email when we publish a new report, please subscribe here .

## The DFIR Report Offerings

A Threat Brief version of this report was published to customers in May of 2024.

Check out our Products here and our Services here . Want a demo, more information on our services, pricing or just want to chat? Get in Touch

## Analysts

Analysis and reporting completed by @malforsec , @lapadrino , and @PeteO .

## Initial Access

This intrusion began in February of 2024 with an exposed Windows server hosting a vulnerable Apache ActiveMQ instance that was compromised through a Remote Code Execution(RCE) vulnerability, CVE-2023-46604 .

The threat actor exploited the server twice, as they lost access a day after the first intrusion. However, the unpatched system allowed them to easily return later. Unfortunately, some network logs from the exploitation activity during the first compromise are missing. From the logs available, it appears the threat actor utilized the exact same technique and procedure, changing only the names of the files that were downloaded after successful exploitation.

The exploit activity triggered the following network intrusion detection rules from Emerging Threats:
ET INFO Apache ActiveMQ Instance - Vulnerable to CVE-2023-46604 - Local Instance ET EXPLOIT Apache ActiveMQ Remote Code Execution Attempt (CVE-2023-46604) ET EXPLOIT Successful Apache ActiveMQ Remote Code Execution (CVE-2023-46604)
The first step in the exploitation was to send a maliciously crafted OpenWire command to the ActiveMQ server ( shown with this POC code ):

RCE was accomplished by sending the Java Spring org.springframework.context.support.ClassPathXmlApplicationContext class, along with a URL to a maliciously crafted Java Spring bean configuration XML file, in an OpenWire Exception Response command within a Throwable type field. This technique is well documented by Fidelissecurity . The XML config file contained the commands the threat actor intended to execute on the exploited system.

On the second day of the intrusion, the threat actor started began more traditional discovery activity by running various Windows utilities.

From network traffic recorded during the second round of exploitation, we saw the ActiveMQ Server process downloading the malicious XML file containing the commands to be run in the command-line interface:

## Execution

After successfully exploiting the internet-facing ActiveMQ server, the XML file provided the commands to run on the server. Sysmon event ID 1 showed the execution, with Java – the ActiveMQ server process – listed as the parent process.

Meterpreter

During the first successful intrusion, after exploiting the vulnerable ActiveMQ server, the threat actor downloaded and executed a Metasploit stager named uFSyLszKsuR.exe using CertUtil as the download tool. Adding %TEMP% to the file location resulted in the file being saved in the C:\Users\<USERNAME>\AppData\Local\Temp> directory.

Sysmon event ID 11 showed that certutil created the file:

Reviewing the network traffic, we also saw the download of an executable file with the typical MZ header and the “ This program cannot be run in DOS mode ” string:

After download, the executable file was started. Sysmon event ID 1 (process execution) showed execution of the file:

uFSyLszKsuR.exe was a Metasploit executable configured to communicate back to the same server from which it was delivered. Using YARA and speakeasy allowed us to confirm it as a Metasploit executable that communicated with 166.62.100[.]52.

YARA hit with signature from Elastic :

## Persistence

During the intrusion, the AnyDesk remote access tool was also dropped on the beachhead host and subsequently installed. When installed, the AnyDesk application created a service and configured it to AutoStart, which was observed in the System Event Log (event ID 7045).

## Privilege Escalation

After the execution of the Meterpreter stager delivered through exploitation on the beachhead host, we observed the creation of a new service named kesknq.

This service then executed the following command:
cmd.exe /c echo kesknq > \\.\pipe\kesknq
This pattern of activity is commonly associated with running the getsystem command in a Meterpreter shell to elevate privileges.

We can see in the logs that this command provided access to System-level privileges on the host.

## Defense Evasion

One of the tools and scripts observed being introduced into the compromised environment on the beachhead host was a batch file named rdp.bat, which was created by the injected Winlogon process.

After the creation of the rdp.bat file, several commands were executed via a CMD process to modify the host configuration, specifically to permit RDP through the firewall and set the RDP port number to 3389. We assess that these commands were included in the batch file.

The rdp.bat file was then removed by the threat actor approximately six minutes after the RDP configuration commands were executed.

The threat actor was observed clearing out both System and Application event logs on the beachhead host, as indicated by event ID 104, as well as clearing the Security event logs, as indicated by event ID 1102.

Event ID 104:

Event ID 1102:

On the Exchange email server, the threat actor used a legitimate Windows executable, SystemSettingsAdminFlows.exe, which allows users to customize or configure the system settings to user’s preference . This LOLBIN was used to disable Windows Defender settings on the server.

## Credential Access

Credentials were accessed on several hosts by dumping them from LSASS process memory. This activity occurred during both round one and round two of the intrusion. CallTrace UNKNOWN is indicative of injected code, and GrantedAccess 0x1010 grants read to process memory (0x00000010 = VMRead).

Round One:

Round Two:

Four hosts showed signs of LSASS dumping during the first round of the intrusion. One of these hosts was a server with a privileged service account configured to run an installed application. This service account was later observed in the second round of the intrusion to facilitate lateral movement activity.

## Discovery

Round One

After the initial exploitation of the beachhead host, no immediate process activity related to discovery was observed. However, around an hour after the first exploit, SMB traffic from the beachhead to remote hosts across the network was observed. This activity was likely network scanning performed by the threat actor.

On the second day of the intrusion, the threat actor began more traditional discovery activity by running various Windows utilities.

Some commands executed by the threat actor contained syntax errors, including a mistyped / and reversing the domain administrator group. Additionally, the threat actor attempted to add an account that was already a domain administrator to the domain administrator group. The threat actor also ran the command netstat -t , which displays active connections; however, -t is not a documented option for netstat on Windows .

Round Two

During the second round of the intrusion, the threat actor correctly queried the domain administrator group.

They then pivoted to using external utilities. They dropped a file designed to appear as SoftPerfect Network Scanner , which was actually Advanced IP Scanner .

After executing the installer, the threat actor launched the scanner to enumerate the local network. The following were the top ports were scanned using the tool:

## Lateral Movement

Remote Services

The threat actor used Metasploit to execute remote services across several hosts in the environment, both on the first day of the intrusion and when they returned on the 18th day.

Example Obfuscated PowerShell command:

To deobfuscate the command, the following steps were required:

- Remove all occurrences of + , which were used solely to concatenate strings

- Replace {0} with =

- Replace {1} with n

- Base64-decode the resulting string

- Gunzip the final output

Cyberchef recipe to perform the deobfuscation

This code performs the following actions:

- Converts a Base64-encoded string to a byte array named $dSU.

- Allocates memory for the byte array using VirtualAlloc , where the 0x04 parameter corresponds to the PAGE_EXECUTE_READWRITE protection attribute, allowing the allocated memory to be read, written, and executed.

- Copies the byte array to the allocated memory.

- Changes the memory protection to executable using VirtualProtect , where the 0x10 parameter specifies the new protection attributes for the memory region and corresponds to PAGE_EXECUTE.

- Creates a new thread to execute the code in the allocated memory using CreateThread.

- Waits for the thread to completed using WaitForSingleObject.

This behavior is typical when code is dynamically written to memory and executed.

The Base64 string $dsU contained the shellcode. We decoded it and used SpeakEasy to simulate an environment in which it would run. The simulation showed network activity toward a specific IP address, port, URI, and User-Agent used for C2 communication. These matched the same server used to launch the exploit and were consistent across both rounds of exploitation and C2 communications.

On some hosts, Microsoft Defender antivirus was active. On these systems, Defender detected and blocked execution of the service creation and Powershell execution in several instances. This activity is shown in the Defender logs below:

RDP

On the 18th day of the intrusion, the threat actor also used RDP for lateral movement. They began by logging into a backup server. The credentials used belonged to a privileged service account that was active on one of the servers from which credentials were dumped on the first day of access.

RDP sessions were then observed across multiple hosts in a short period of time, with the threat actor spending between 1 and 10 minutes per host before moving to the next system. This RDP activity was used execute ransomware and is covered in further detail in the #Impact section.

## Command and Control

Metasploit

Threat actor dropped a Metasploit stager upon successful exploitation of CVE-2023-46604 on the exposed Apache ActiveMQ server. A Speakeasy emulation run showed C2 communication to 166.62.100[.]62 on port 2460, as was also observed in the network connection data from Sysmon event ID 3 during the intrusion:

AnyDesk

On the 18th day of the intrusion, the threat actor installed AnyDesk on the beachhead host. Shortly after installation, we observed the threat actor log in to the application. This activity was identified using the ad_svc.trace logs from the beachhead host. These logs revealed the login location to be the same IP address used to launch the exploit and host the Metasploit command and control, linking activity across the multiple exploits to final actions.
info 2024-XX-XX 23:11:03.933 gsvc 11580 11960 24 anynet.any_socket - Client-ID: 1312001388 (FPR: 62cf8d944a69). info 2024-XX-XX 23:11:03.933 gsvc 11580 11960 24 anynet.any_socket - Logged in from 166.62.100.52:6761 on relay 1ec46041

## Impact

On the 18th day of the intrusion, during the second round of threat actor activity, the threat actor moved to final objectives involving the deployment of ransomware across the environment. Using their injected Winlogon process they dropped two files: LB3_pass.exe and LB3.exe.

These files were LockBit ransomware executables. Based on the ransom note dropped after execution, we assess that the ransomware was created using the leaked LockBit Black builder. This builder generates the encryption and decryption keys and produces the required PE files. INCIBE has published an excellent analysis of LockBit and provides additional details on the builder.

After introducing the ransomware into the environment, the threat actor copied the files across systems via RDP sessions. Both the C:\Intel staging folder and the %USERPROFILE%\Downloads directory of the user account used for RDP connections were leveraged.

All ransomware was executed interactively via those RDP sessions; however, several different execution flags were observed. On the file server and backup server, the LB3_pass.exe file was executed with specific path and password flags.

On other hosts, the LB3.exe file was executed via the Explorer.exe process and spawned a subprocess with the -psex option, which was likely intended to trigger the ransomware’s ability to spread via a PsExec-style SMB spreader configurable within the builder .

Upon execution, ransom notes were written to directories across affected hosts as the systems were encrypted.

The ransom note did not follow the normal LockBit format directing victims to a Tor leak site or TOX/Jabber communications; instead, it instructed them to download and use the Session private messaging application. This modified note and lack of linkage to official LockBit infrastructure led us to assess that this activity was conducted by an independent threat actor using the leaked builder to operate their own ransomware campaign.

In addition to the ransom note, the ransomware also changed desktop backgrounds to ensure users were aware of the ransom.

## Timeline

## Diamond Model

## Indicators

### Atomic
166.62.100[.]52 - C2 and AnyDesk (Login)
1148037084 - AnyDesk Client ID

### Computed
lb3_pass.exe
sha256: C8646CFB574FF2C6F183C3C3951BF6B2C6CF16FF8A5E949A118BE27F15962FAE
lb3.exe
sha256: 8CEEE89550C521BA43F59D24BA53A22A3B69EAD0FCE118508D0A87A383D6A7B6
netscan.exe
SHA256=87BFB05057F215659CC801750118900145F8A22FA93AC4C6E1BFD81AA98B0A55
advanced_ip_scanner.exe
SHA256=722FFF8F38197D1449DF500AE31A95BB34A6DDABA56834B13EAAFF2B0F9F1C8B
rdp.bat
SHA256=D9C888BDE81F19F3DC4F050D184FFA6470F1A93A2B3B10B3CC2D246574F56841

## Detections

### Network
2034225 : ET MALWARE [CISA AA21-291A] Possible BlackMatter Ransomware Lateral Movement 2851484 : ETPRO INFO SMB/DCERPC Bind_ack with Endian Flipped 2049009 : ET INFO Apache ActiveMQ Instance - Vulnerable to CVE-2023-46604 - Local Instance 2025701 : ET POLICY SMB2 NT Create AndX Request For an Executable File 2033713 : ET MALWARE Cobalt Strike Beacon Observed 2810654 : ETPRO HUNTING Possibly Suspicious example.com SSL Cert 2049045 : ET EXPLOIT Apache ActiveMQ Remote Code Execution Attempt (CVE-2023-46604) 2049046 : ET INFO Remote Spring Application XML Configuration Containing ProcessBuilder Downloaded 2049385 : ET EXPLOIT Successful Apache ActiveMQ Remote Code Execution (CVE-2023-46604) 2028867 : ET POLICY Vulnerable Java Version 11.0.x Detected 2025703 : ET POLICY SMB2 NT Create AndX Request For an Executable File In a Temp Directory 2021076 : ET HUNTING SUSPICIOUS Dotted Quad Host MZ Response 2018959 : ET POLICY PE EXE or DLL Windows file download HTTP 2851878 : ETPRO MALWARE Cobalt Strike Stager Payload 2001569 : ET SCAN Behavioral Unusual Port 445 traffic Potential Scan or Infection 2009897 : ET MALWARE Possible Windows executable sent when remote host claims to send html content 2025699 : ET POLICY SMB Executable File Transfer 2842116 : ETPRO USER_AGENTS Observed Suspicious UA (Mozilla/5.0) 2018358 : ET HUNTING GENERIC SUSPICIOUS POST to Dotted Quad with Fake Browser 1 2025644 : ET MALWARE Possible Metasploit Payload Common Construct Bind_API (from server) 2844488 : ETPRO HUNTING Suspicious Offset PE EXE or DLL Download on Non-Standard Ports 2035480 : ET HUNTING PE EXE Download over raw TCP 2014819 : ET INFO Packed Executable Download 2043337 : ET INFO Request for EXE via Powershell 2033355 : ET INFO Windows Powershell User-Agent Usage 2019714 : ET MALWARE Terse alphanumeric executable downloader high likelihood of being hostile 2016141 : ET INFO Executable Download from dotted-quad Host 2027761 : ET POLICY SSL/TLS Certificate Observed (AnyDesk Remote Desktop Software) 2015744 : ET INFO EXE IsDebuggerPresent (Used in Malware Anti-Debugging) 2829988 : ETPRO POLICY Observed MS Certutil User-Agent in HTTP Request

### Sigma

Search rules on detection.fyi or sigmasearchengine.com

DFIR Rules:
03be05e6-4977-44cd-8ee4-a79400a5ceb0 : Detection of Cobalt Strike Execution a09079c2-e4af-4963-84d2-d65c2fb332f5 : Detection of CertUtil Misuse for Malicious File Download 47a69e6a-7829-4014-817b-148846e51f55 : Detection of Antivirus Disabling via SystemSettingsAdminFlows a526e0c3-d53b-4d61-82a1-76d3d1358a30 : Silent Installation of AnyDesk RMM b526e0c3-d53b-4d61-82a1-76d3d1358a31 : AnyDesk RMM Password Setup via Command Line b26feb0b-8891-4e66-b2e7-ec91dc045d58 : AnyDesk Network
Sigma Repo:
61a7697c-cb79-42a8-a2ff-5f0cdfae0130 : Potential CobaltStrike Service Installations - Registry
178e615d-e666-498b-9630-9ed363038101 : Elevated System Shell Spawned
2617e7ed-adb7-40ba-b0f3-8f9945fe6c09 : Suspicious SYSTEM User Process Creation
d522eca2-2973-4391-a3e0-ef0374321dae : Abused Debug Privilege by Arbitrary Parent Processes
d75d6b6b-adb9-48f7-824b-ac2e786efe1f : Suspicious FromBase64String Usage On Gzip Archive - Process Creation
98767d61-b2e8-4d71-b661-e36783ee24c1 : Gzip Archive Decode Via PowerShell
30edb182-aa75-42c0-b0a9-e998bb29067c : Potential AMSI Bypass Via .NET Reflection
d7bcd677-645d-4691-a8d4-7a5602b780d1 : Potential PowerShell Command Line Obfuscation
954f0af7-62dd-418f-b3df-a84bc2c7a774 : New Remote Desktop Connection Initiated Via Mstsc.EXE
ed74fe75-7594-4b4b-ae38-e38e3fd2eb23 : Outbound RDP Connections Over Non-Standard Tools
bef37fa2-f205-4a7b-b484-0759bfd5f86f : PUA - Advanced IP Scanner Execution
b52e84a3-029e-4529-b09b-71d19dd27e94 : Remote Access Tool - AnyDesk Execution
4d07b1f4-cb00-4470-b9f8-b0191d48ff52 : DNS Query To Remote Access Software Domain From Non-Browser App
cde0a575-7d3d-4a49-9817-b8004a7bf105 : Uncommon New Firewall Rule Added In Windows Firewall Exception List
2aa0a6b4-a865-495b-ab51-c28249537b75 : Startup Folder File Write
530a6faa-ff3d-4022-b315-50828e77eef5 : Anydesk Remote Access Software Service Installation
114e7f1c-f137-48c8-8f54-3088c24ce4b9 : Remote Access Tool - AnyDesk Silent Installation
0d5675be-bc88-4172-86d3-1e96a4476536 : Potential Tampering With RDP Related Registry Keys Via Reg.EXE
178e615d-e666-498b-9630-9ed363038101 : Elevated System Shell Spawned
d95de845-b83c-4a9a-8a6a-4fc802ebf6c0 : Suspicious Group And Account Reconnaissance Activity Using Net.EXE
15619216-e993-4721-b590-4c520615a67d : Potential Meterpreter/CobaltStrike Activity
9bd04a79-dabe-4f1f-a5ff-92430265c96b : Privilege Escalation via Named Pipe Impersonation
8e0bb260-d4b2-4fff-bb8d-3f82118e6892 : CMD Shell Output Redirect
19b08b1c-861d-4e75-a1ef-ea0c1baf202b : Suspicious Download Via Certutil.EXE
13e6fe51-d478-4c7e-b0f2-6da9b400a829 : Suspicious File Downloaded From Direct IP Via Certutil.EXE
dff1e1cc-d3fd-47c8-bfc2-aeb878a754c0 : Shell Process Spawned by Java.EXE

### Yara

Elastic Protection Artifacts:
7bc0f998-7014-4883-8a56-d5ee00c15aed : Windows_Trojan_Metasploit_7bc0f998 91bc5d7d-31e3-4c02-82b3-a685194981f3 : Windows_Trojan_Metasploit_91bc5d7d

## MITRE ATT&CK

Internal case #TB27524 #PR39767

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
