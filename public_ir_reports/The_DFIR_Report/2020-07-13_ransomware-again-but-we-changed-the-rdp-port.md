---
title: "Ransomware Again...But We Changed the RDP Port!?!?! - The DFIR Report"
source_url: "https://thedfirreport.com/2020/07/13/ransomware-again-but-we-changed-the-rdp-port/"
published: "2020-07-13T01:00:29+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2020-07-13_ransomware-again-but-we-changed-the-rdp-port.html"
---

# Ransomware Again...But We Changed the RDP Port!?!?! - The DFIR Report
Here’s another example of threat actors brute forcing RDP to install ransomware, this time the brute forced system was not using the default RDP port. The threat actors installed ransomware on two machines including a Domain Controller in ~17 minutes.

We saw a Tweet the other day that said “just change RDP to another port and you’re safe”. We couldn’t disagree more…

### Timeline of Events (UTC)

7:00 RDP login from 212.102.45.98

7:01 Opens Task Manager (usually to see who else is logged in)

7:03 Drops/runs Network Scanner

7:08 RDPs into a Domain Controller (DC)

7:10 DC – Opens Task Manager

7:10 DC – Drops/runs Network Scanner

7:13 DC – Drops Harma ransomware on the desktop and then runs it

7:17 entry point – Drops Harma ransomware on the desktop and then runs it

### Harma

###

Harma is a variant of Dharma (CrySiS) which we wrote about here . There are many similarities between the two including a common pdb path.

###

###

The ransom notes also look similar.

###

###

###

### Summary

Changing the RDP port will not stop threat actors. We consistently get scanned for the RDP protocol on almost every port we open. If you must use RDP over the internet make sure default accounts are disabled and you are using MFA. With that said, we still recommend using VPN or a front end such as VMware View or Citrix Workspace with MFA.

Enjoy our report? Please consider donating $1 or more to the project using Patreon . Thank you for your support!

### IOCs

MISP Priv 69099/21ce5f26-43bb-4971-a02d-59b563c4e3ca

RDP login from 212.102.45.98
BPY6A7_payload.exe|56452e0839ef830c904182992aa11691 e94e21979565c2372fc2745f18eec3c64d9cc2da 23a3dfe1493dcda00a3d9a00210793553b629bd77f30c39974c8e1ab0ea51c6f 5-NS new.exe|597de376b1f80c06d501415dd973dcec
629c9649ced38fd815124221b80c9d9c59a85e74
f47e3555461472f23ab4766e4d5b6f6fd260e335a6abc31b860e569a720a5446
Persistence – C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\BPY6A7_payload.exe

MITRE ATT&CK
External Remote Services - T1133
Network Share Discovery - T1135
Data Encrypted for Impact - T1486
Valid Accounts - T1078

Internal case 1001

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
