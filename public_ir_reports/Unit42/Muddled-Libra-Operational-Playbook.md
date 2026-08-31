---
title: "A Peek Into Muddled Libra’s Operational Playbook"
source_url: "https://unit42.paloaltonetworks.com/muddled-libra-ops-playbook/"
published: "2026-02-10T23:00:41+00:00"
author: "Justin De Luna, Noah Rincon, Cuong Dinh"
archived_at: "2026-08-25"
source_html: "Muddled-Libra-Operational-Playbook.html"
---

# A Peek Into Muddled Libra’s Operational Playbook
## Executive Summary

During a September 2025 incident response investigation, Unit 42 discovered a rogue virtual machine (VM) which we believe with high confidence to be used by the cybercrime group Muddled Libra (aka Scattered Spider, UNC3944). The contents of this rogue VM and activity from the attack provide valuable insight into the operational playbook of this threat actor.

Muddled Libra created the VM after the group successfully gained unauthorized access to the target's VMware vSphere environment. Activities during the attack include:

- Performing reconnaissance

- Downloading tools

- Establishing persistence via a command and control (C2) channel

- Using stolen certificates

- Copying files from the rogue VM to the target's domain controller (DC)

- Interacting with the target’s Snowflake infrastructure

Based on the characteristics of the attack, we assess with high confidence that Muddled Libra conducted it. This article provides a detailed analysis of our observations to shed further light on the threat actor’s tactics, techniques and procedures (TTPs).

Palo Alto Networks are better protected from the threats discussed in this article through the following products and services:

- Advanced WildFire

- Cortex Cloud

- Cortex XDR and XSIAM

If you think you might have been compromised or have an urgent matter, contact the Unit 42 Incident Response team .

| Related Unit 42 Topics | Muddled Libra , Cybercrime

## Who Is Muddled Libra?

As previously documented, threat actors affiliated with Muddled Libra use various social engineering tactics (e.g., smishing, vishing) to gain initial access to targeted organizations. Activities can include targeting call centers operated by potential victims, as well as those outsourced to third-party firms. These third-party firms include business process outsourcing (BPOs) and managed service providers (MSPs). This expands the group’s range of potential targets.

Threat actors affiliated with Muddled Libra are highly proficient at exploiting human psychology by impersonating employees to attempt password and multi-factor authentication (MFA) resets. Figure 1 illustrates the composition of Muddled Libra in terms of their demographics, tradecraft, victim targeting and actions on objectives.

Figure 1. Muddled Libra threat profile.

While their tradecraft has evolved, threat actors affiliated with Muddled Libra continue to minimize their use of malware throughout the attack chain. Whenever possible, they prefer to use their targets' own assets against them.

Threat actors often abuse, take advantage of or subvert legitimate products for malicious purposes. This does not imply that the legitimate product is flawed or malicious.

## Background on the Attack Chain

We assisted a client with an incident response engagement in September 2025. Throughout our investigation, we identified and recovered a VM created and leveraged by the threat actor to conduct the early stages of its attack. Attackers were unable to delete this VM before their access was cut off. We often observe threat actors creating VMs within targeted environments to avoid detection from endpoint tools like endpoint detection and response (EDR) or extended detection and response (XDR).

By examining this VM, we discovered the tools the attackers leveraged and the basic troubleshooting they conducted during their unauthorized access. This provided insights into their operational methods.

Using forensic artifacts and logs, we uncovered a large amount of activity conducted from this VM, including lateral movement and tools used. Figure 2 further illustrates our observations during the investigation. Note that the analysis below is of a single system and does not cover the entire incident observed by Unit 42.

Figure 2. High-level chain of events in the attack investigated by Unit 42.

## A Peek Into Muddled Libra Tactics

Approximately two hours after gaining initial access to the target’s environment, we observed the attackers accessing the target’s vSphere portal and creating a new VM named “New Virtual Machine.” The attackers then leveraged this VM for the early stages of the incident as a beachhead host using the local Administrator account.

Shortly after logging into the newly created VM, attackers downloaded stolen certificates from the targeted environment. They leveraged these certificates to forge tickets throughout their attack chain.

Within three minutes, attackers established additional persistence in the target’s environment using an SSH tunnel through the Chisel tool. This tool was contained in a ZIP archive named goon.zip that was hosted on an AWS S3 bucket under the attackers' control.

Nearly one minute after they downloaded the ZIP archive containing Chisel, we observed malicious network connections to an attacker-controlled IP address over TCP port 443 (HTTPS). We observed this connection for a total of 15 hours. Figures 3-5 illustrate these observations.

Figure 3. URL hosting archive containing the Chisel tool.

Figure 4. The downloaded tool, goon.zip .

Figure 5. The SSH tunneling tool, chisel.exe , extracted from goon.zip .

A minute later, we observed them logging in interactively with a new local user account named gooner .

Approximately 15 minutes after creating the VM, the attackers began using vSphere to power down two of the target's virtualized DCs. They then mounted the virtual machine disks (VMDKs) of the powered-down DCs. This allowed them to copy the NTDS.dit and SYSTEM registry hive files from these two DCs and place them on the desktop of the Administrator account on their newly created VM.

Approximately two minutes later, they wrote two files, result and result.kerb , to the local Administrator account’s desktop. We retrieved these files and determined that these were decrypted versions of the target’s NTDS.dit Active Directory database, which contained hashes of all users. Figures 6 and 7 illustrate these observations.

Figure 6. VMware logs of the shutdown activities of the DC.

Figure 7. List of files discovered for credential dump, NTML hash and Kerberos hash.

At nearly 30 minutes of access to this newly created VM, the attackers began executing the Active Directory enumeration tool ADRecon . We observed and retrieved dozens of files associated with ADRecon, including a PowerShell script and output files.

These files contained information such as:

- Domain details

- Forest

- Trusts

- Sites

- Subnets

- Schema

- Password policy

- DCs

- Service Principal Names (SPNs)

- Users

- Group Policy Objects (GPOs)

The output of the ADRecon tool would then be placed in a ZIP archive named <VICTIM ORGANIZATION>.zip (where <victim organization> represents the name of the victim, redacted for this report). We also observed the attackers downloading the tool ADExplorer64.exe directly from the Microsoft SysInternals domain. Figure 8 illustrates these observations.

Figure 8. List of ADRecon output files discovered during our investigation.

Within the ADRecon output, the threat actors only opened the CSV file ComputerSPNs.csv . This file contained all available service principal names (SPNs) associated with hosts in the environment. Attackers gather this information to help identify critical services running that they are interested in targeting. These critical services include:

- Veeam

- Terminal services

- Hyper-V

- MSSQL

- Exchange

- Other similar systems as shown in Figure 9

Figure 9. List of targeted services discovered during our investigation.

One hour later, attackers began searching the web for various acronyms associated with the targeted organization, likely to determine what data could be sensitive and interesting for exfiltration. This included searches such as “what is NAIC code” and “NAICS code lookup,” as shown in Figure 10.

A North American Industry Classification System (NAICS) code is a six-digit number that classifies businesses by their primary economic activity. By looking up this code, attackers might have been trying to understand the business category of the target organization.

Figure 10. Example of web searches.

Thirty minutes after their web searches, attackers began interacting with significant data from the target’s Snowflake database, which they also downloaded to their VM. For the next few hours, attackers began interacting with the data and attempting to identify ways to send the data from their VM to a file-sharing site. However, we observed them having difficulties finding a file-sharing site that the targeted organization had not already blocked.

After trying several common file-sharing sites, they began using Bing to search on the phrases “upload files” and “upload files no registration” to identify a file-sharing site that was not blocked. We observed attempts at accessing sites such as:

- LimeWire

- upload[.]ee

- uploadnow[.]io

- filetransfer[.]io

- filebin[.]io

- Dropbox

Figures 11-13 illustrate these observations.

Figure 11. List of Snowflake web browsing activities documented from our investigation.

Figure 12. Web searches for cloud storage services discovered during our investigation.

Figure 13. Web browsing activities to cloud storage services discovered during our investigation.

Shortly after interacting with the data, the attackers began lateral movement using multiple then-compromised accounts with their SSH tunnel, RDP and PsExec. They downloaded the PsExec tool directly from the Microsoft SysInternals domain.

Approximately four hours after the creation of their VM, the attackers began looking for additional sensitive data. At that time, we observed them having compromised a handful of accounts, one of which they used to access the mailboxes of other accounts to download a Personal Storage Table (PST) file. However, based on Bing search history, they had difficulty accessing the mailbox via Office.

The attackers then searched the web for “ office[.]com old setup download” and “is there a place to download an older version of Outlook?” Attackers also reviewed various Reddit posts related to this query. Shortly after, they downloaded and ran OfficeSetup.exe from Microsoft.

They then began troubleshooting items such as “Outlook slow downloading emails” and performed several internet speed checks using the site fast[.]com . Figures 14-17 illustrate these observations.

Figure 14. Online Outlook login activities discovered during our investigation.

Figure 15. Web searches for Outlook agents discovered during our investigation.

Figure 16. Web searches for older Outlook versions discovered during our investigation.

Figure 17. Web searches to troubleshoot slow email download issues and perform a speed test.

In addition to troubleshooting their download speeds, attackers used Bing to identify the location of the Outlook ODT file. Figure 18 illustrates this observation.

Figure 18. Web search for the Outlook ODT file location discovered during our investigation.

Additionally, we observed Microsoft Defender, presumably installed on the VM by default, taking action on multiple malicious files on this VM. This included ADRecon, Chisel and GoSecretsDump. Figure 19 lists these detections.

Figure 19. Microsoft Defender detections on tools discovered during our investigation.

After some time, the attackers then began attempting to exfiltrate the Outlook PST file. They first searched for the S3 Browser tool. Once they downloaded the tool from the S3 Browser website, attackers then attempted to exfiltrate the PST file by uploading it to their S3 bucket. Figures 20 and 21 illustrate these observations.

Figure 20. Downloaded S3 browser executable discovered during our investigation.

Figure 21. S3 Browser logs of PST file upload.

After approximately 15 hours of access to their VM, attackers began browsing various VMware ESXi hosts. They continued to pivot through the network, leveraging access to multiple compromised accounts before their access was terminated by the targeted organization’s security team. Figure 22 illustrates this observation.

Figure 22. Browsing activities to the target’s VMware ESXi hosts discovered during our investigation.

## Conclusion

Intrusion operations Muddled Libra conducts have affected the business operations of many organizations across the globe. This is not because they use advanced malware or novel exploits, but because they exploit the weakest link: humans.

While focusing on identity compromise and social engineering, this threat actor leverages legitimate tools and existing infrastructure to blend in. They operate quietly and maintain persistence.

This incident offers a rare window into an operational playbook used by Muddled Libra, revealing how a single rogue VM can serve as a powerful foothold for lateral movement and data theft. The threat actor's methods underscore the importance of:

- Strengthening identity security

- Enforcing strict access controls

- Continuously monitoring for anomalous use of administrative tools and cloud environments

Organizations should adopt a defense-in-depth strategy centered on:

- Protecting identity

- Maintaining least-privileged access

- Detecting living-off-the-land behaviors

While Muddled Libra’s tactics may appear simple, their effectiveness reminds us that cybersecurity resilience begins not with complexity, but with vigilance, visibility and disciplined access management.

Palo Alto Networks customers are better protected from the threats discussed above through the following products:

The Advanced WildFire machine-learning models and analysis techniques have been reviewed and updated in light of the indicators shared in this research.

Cortex Cloud customers can better protect their cloud infrastructure from the topics discussed within this article through the proper placement of Cortex Cloud XDR endpoint agent and serverless agents within their cloud environment. Designed to protect a cloud’s posture and runtime operations against these threats, Cortex Cloud helps detect and prevent the malicious operations or configuration alterations or exploitations discussed within this article.

Cortex XDR and XSIAM help to prevent the threats described in this blog, by employing the Malware Prevention Engine . This approach combines several layers of protection, including WildFire , Behavioral Threat Protection and the Local Analysis module, designed to prevent both known and unknown malware from causing harm to endpoints.

If you think you may have been compromised or have an urgent matter, get in touch with the Unit 42 Incident Response team or call:

- North America: Toll Free: +1 (866) 486-4842 (866.4.UNIT42)

- UK: +44.20.3743.3660

- Europe and Middle East: +31.20.299.3130

- Asia: +65.6983.8730

- Japan: +81.50.1790.0200

- Australia: +61.2.4062.7950

- India: 000 800 050 45107

- South Korea: +82.080.467.8774

Palo Alto Networks has shared these findings with our fellow Cyber Threat Alliance (CTA) members. CTA members use this intelligence to rapidly deploy protections to their customers and to systematically disrupt malicious cyber actors. Learn more about the Cyber Threat Alliance .

## Indicators of Compromise

### Host Based

Important note: The following files are not malicious, but they are indicators because they were used during the attack.

SHA256 hash:

- 078163d5c16f64caa5a14784323fd51451b8c831c73396b967b4e35e6879937b

- Filename: psexec.exe

- File description: Sysinternals PsExec — remote execution / lateral movement tool (observed downloaded from Sysinternals).

SHA256 hash:

- 996e68f2fe1c8bb091f34e9bf39fd34d95c3e21508def1f54098a1874bfb825e

- Filename: chisel.exe

- File description: Chisel — SSH/HTTPS tunneling tool (persistence via SSH tunnel observed).

SHA256 hash:

- 6784e652f304bf8e43b42c29ad8dd146dd384fa9536b9c6640dfbc370c3e78de

- Filename: s3browser-12-6-1.exe

- File description: S3 Browser client — used to upload files to S3 (used for exfiltration attempts).

SHA256 hash:

- e451287843b3927c6046eaabd3e22b929bc1f445eec23a73b1398b115d02e4fb

- Filename: ADExplorer64.exe

- File description: ADExplorer (Sysinternals) — Active Directory data browsing tool.

SHA256 hash:

- 088f2aced9ed60c2ce853b065f57691403459e1e0d167891d6849e1b58228173

- Filename: goon.zip

- File description: Archive containing attacker tools (observed in S3 bucket).

SHA256 hash:

- 6e2c39d0c00a6a8eef33f9670f941a88c957d3c1e9496392beedc98af14269a2

- Filename: OfficeSetup.exe

- File description: Microsoft Office installer/setup executable (observed use by the attackers while attempting to access mailboxes/PSTs).

### Network Based

| IP Address or Domain | Description

| 162.125.3[.]18 | Associated with Dropbox — destination IP address observed in firewall logs from the attackers' VM

| 104.16.100[.]29 | Associated with Dropbox — destination IP address observed in firewall logs from the attackers' VM

| upload[.]ee | Online cloud storage

| uploadnow[.]io | Online cloud storage

| limewire[.]com | Online cloud storage

| we[.]tl | Online cloud storage

| s3browser[.]com | S3 browser, used for exfiltration

| sean-referrals-commissions-electricity.trycloudflare[.]com | Online cloud storage

| fast[.]com | Used by attackers to check the internet speed

| filetransfer[.]io | Online cloud storage

| filebin[.]io | Online cloud storage

## Additional Resources

- Muddled Libra Threat Assessment: Further-Reaching, Faster, More Impactful – Unit 42, Palo Alto Networks
