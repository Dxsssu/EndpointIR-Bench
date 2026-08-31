---
title: "Inside AD CS Escalation: Unpacking Advanced Misuse Techniques and Tools"
source_url: "https://origin-unit42.paloaltonetworks.com/active-directory-certificate-services-exploitation/"
published: "2026-05-11T22:00:43+00:00"
author: "Stav Setty, Tom Fakterman, Shachar Roitman"
archived_at: "2026-08-25"
source_html: "AD-CS-Escalation.html"
---

# Inside AD CS Escalation: Unpacking Advanced Misuse Techniques and Tools
## Executive Summary

Active Directory Certificate Services (AD CS) is a foundational component of Windows enterprise infrastructure, responsible for managing public key infrastructure (PKI) and issuing certificates that enable authentication and encryption across networks. Despite its critical role in the enterprise identity infrastructure, AD CS is often undermined by insecure default configurations and design complexities, resulting in exploitable attack surfaces. Due to misconfigured templates and overly permissive enrollment rights, AD CS has emerged as a high-impact, under-monitored vector for privilege escalation and unauthorized identity impersonation in modern environments.

Unlike traditional vulnerability exploitation, AD CS attacks rarely rely on zero-day vulnerabilities or malware. Instead, adversaries misuse native certificate issuance to impersonate privileged accounts, escalate privileges and establish persistence. Unit 42 observations and industry reporting show that these weaknesses are actively exploited by both financially motivated ransomware groups and state-sponsored actors .

We provide a technical deep-dive into advanced AD CS exploitation, including certificate template misconfigurations and shadow credential misuse. Our findings present a comprehensive breakdown of the attacker’s toolkit and their evolving operational behaviors.

By studying behavioral analytics, event log correlation and linking offensive techniques to actionable telemetry, it is possible to create dynamic and comprehensive detection strategies. Our detection methods reveal patterns and methods that extend beyond traditional signature-based approaches. We aim to provide defenders with unique ways to uncover stealthy AD CS abuse and address a persistent gap in enterprise security.

Cortex XDR and XSIAM customers are protected from this activity with Cortex User Entity Behavior Analytics (UEBA ) and Cortex Cloud Identity Security .

If you think you might have been compromised or have an urgent matter, contact the Unit 42 Incident Response team .

| Related Unit 42 Topics | Active Directory , Fighting Ursa, Microsoft

## Introduction: The Critical Role (and Risk) of AD CS

AD CS is the backbone of enterprise public key infrastructure ( PKI ). At its core is the certificate authority ( CA ), the service responsible for issuing and managing digital certificates . These certificates are cryptographic identity cards that prove that a user, device or service is what it claims to be. Organizations rely on AD CS for:

- User authentication : Certificates enable single sign-on and client authentication across services

- Service authentication : Internal services and domain controllers validate identity using PKI

- Encryption : Certificates underpin secure communications within and outside the enterprise

The same capabilities that make AD CS indispensable also create risk. To manage certificate issuance, AD CS uses certificate templates , which define who can request certificates, what they can be used for, and the permissions required. When misconfigured, these templates may grant long-lived authentication or privileged access, effectively providing complete control over a network.

Certificate issuance is an expected administrative function that often appears as normal network activity. This makes AD CS a powerful adversarial tool, because exploitation frequently evades detection.

In the AD CS issuance workflow, the CA issues certificates according to the policies defined in certificate templates, and users and services use the resulting certificates for authentication and encryption. Figure 1 illustrates this flow.

Figure 1. PKI architecture showing CA → Templates → Certificates → Users and Services.

For additional background on AD CS fundamentals, see Detecting AD CS Abuse .

## Ongoing Exploitation and Blind Spots

Despite years of research highlighting AD CS risks, certificate services remain a significant attack surface. Key contributing factors include:

- Widespread misconfigurations : Organizations often deploy AD CS with default or overly permissive settings.

- Complexity breeding mistakes : Consistently securing each configuration surface is a daunting task when combined with the need to manage dozens of certificate templates, enrollment policies and delegated permissions. Because certificate services support critical authentication workflows, security teams can be hesitant to modify legacy templates or tighten permissions, for fear of disrupting production systems.

- Limited monitoring : Few tools natively detect certificate misuse.

Recent incident response investigations show attackers leveraging AD CS to escalate from low-privileged accounts to full domain dominance. Exploiting certificate services is no longer rare; it has become a standard step in sophisticated intrusions.

In August 2024, Rapid7 described a social engineering campaign in which attackers attempted to escalate privileges by exploiting CVE-2022-26923 . This vulnerability allows a lower-privileged user to elevate their privileges by acquiring a certificate from the AD CS. The attackers tried to exploit it by dropping and executing a file named update6.exe .

Figure 2 shows a Cortex XDR alert that is triggered when update6.exe attempts to exploit CVE-2022-26923. The alert highlights a mismatch between the requesting machine and the issued certificate’s identity — a behavioral signal that is consistent with certificate-based privilege escalation. These inconsistencies can reveal AD CS abuse even when no malware signatures are present.

Figure 2. An alert on the detection and prevention of CVE-2022-26923, as seen in Cortex XDR.

## Phase Breakdown: How AD CS Attacks Work

The AD CS exploitation lifecycle typically encompasses five phases:

- Initial access : Compromising low-privileged accounts via phishing, credential theft or other vectors

- Discovery : Enumerating CA servers, certificate templates, enrollment permissions and account keys

- Exploitation : Misusing misconfigured templates to request certificates or register cryptographic keys for privileged accounts

- Privilege escalation and lateral movement : Using certificates or keys with public key cryptography for initial authentication ( PKINIT ) to request Kerberos tickets and impersonate privileged users

- Persistence : Maintaining access through shadow credentials , key trust misuse and certificate renewal

Figure 3 illustrates this sequence of operations, demonstrating how AD CS acts as a force multiplier that turns a single compromised account into long-term access across an enterprise.

Figure 3: AD CS attack lifecycle diagram.

## Deep Dive: Key AD CS Attack Techniques​​

The key adversarial tactics, techniques and procedures (TTPs) that target AD CS include certificate template misconfigurations and shadow credential abuse.

### Certificate Template Misuse and Misconfigurations

Certificate templates define how AD CS issues certificates, including who can request them and what privileges the certificates grant. Exploiting misconfigurations in certificate templates is one of the most common ways that attackers escalate privileges.

Common misconfigurations include:

- Low-privileged users allowed to enroll in high-privileged templates: This effectively lets attackers mint authentication certificates for accounts that they should not control

- Dangerous template flags enabled: For example, the “Supply in the request” option ( ENROLLEE_SUPPLIES_SUBJECT ) lets the requester define the certificate subject in the certificate signing request (CSR), enabling impersonation

- Broad group enrollment rights: Assigning rights to groups like Domain Users or Authenticated Users allows any authenticated user to abuse certificate enrollment

Figure 4 highlights a dangerous template configuration that allows the requester to supply the subject, enabling account impersonation.

Figure 4. Template setting with the “Supply in the request” ( ENROLLEE_SUPPLIES_SUBJECT ) specification enabled.

#### ESC1 Walkthrough

In their 2021 Certified Pre-Owned: Abusing Active Directory Certificate Services [PDF] whitepaper, SpecterOps researchers Will Schroeder and Lee Christensen identified and categorized eight primary AD CS escalation techniques, designated ESC1 through ESC8. Since then, several additional ESC techniques have been discovered.

ESC1 stands out as the most consistently observed and widely utilized escalation method. This technique exploits template vulnerabilities, enabling low-privileged users to request certificates as high-privileged accounts.

An ESC1 attack can be conducted when a certificate template is configured with the following settings:

- Low-privileged users have enrollment rights

- Requesters can specify a subject alternative name (SAN) ( ENROLLEE_SUPPLIES_SUBJECT )

- Manager approval is disabled

- No authorized signatures are required

- The enhanced key usage ( EKU ) allows authentication — for example, Client Authentication

A typical ESC1 attack begins with an adversary enumerating available certificate templates using tools such as Certify or Certipy to identify misconfigurations. Once a vulnerable template is discovered, the attacker submits a certificate request impersonating a high-privileged account. The issued certificate can then be used to authenticate to services or obtain Kerberos tickets as the target account, resulting in privilege escalation.

Figure 5 shows output from Certipy, a Python tool used to enumerate certificate templates and exploit misconfigurations, highlighting flags that enable the ESC1 attack path.

Figure 5. Example of Certipy output highlighting ESC1 flags such as ENROLLEE_SUPPLIES_SUBJECT , Client Authentication and Manager Approval.

### Shadow Credentials and Key Trust Exploitation

Attackers often turn to shadow credentials to gain stealthy, persistent access, authenticating as a target user without ever needing their password. Unlike traditional credential theft, shadow credentials leverage cryptographic keys that are linked directly to user accounts. This method enables long-term access that is resistant to common defenses like password resets or account lockouts.

A central enabler of this attack is Key Trust , a modern authentication mechanism used by Windows Hello for Business and smartcards. Key Trust leverages PKINIT in Kerberos to allow users to authenticate to Active Directory using public key certificates instead of passwords.

The msDS-KeyCredentialLink attribute stores public keys associated with a user account and is intended to support legitimate, key-based authentication. However, attackers can misuse this attribute to register their own key credentials as high-privileged accounts, effectively creating a shadow credential.

#### How Shadow Credentials Work

- Key registration : The attacker adds key credentials to the target account’s msDS-KeyCredentialLink attribute, usually through AD manipulation or elevated access

- PKINIT authentication : Using the key, the attacker requests Kerberos tickets without needing to provide the account password

Even if the account password is changed or previously issued certificates are revoked, the attacker can continue authenticating as the target account.

#### Integration With Other AD CS Exploits

Shadow credentials are particularly powerful when combined with certificate template misuse, such as ESC1. For example, an attacker might:

- Exploit a misconfigured template to request a certificate for a privileged account

- Use the certificate to elevate privileges and gain domain admin access

- Register a key in msDS-KeyCredentialLink for persistent, passwordless access

- Continue lateral movement or maintain stealthy persistence without creating new accounts or relying on stolen passwords

This combination of template exploitation and shadow credential misuse represents one of the most persistent and hard-to-detect attack paths in modern Windows environments.

## The Attacker Toolkit for AD CS Exploitation

A growing set of open-source tools makes AD CS misuse more accessible. Table 1 lists commonly-used tools for AD CS exploitation and their primary use cases.

| Tool | Primary Use Case | Notes

| Certify | Enumerates and exploits AD CS templates | C# tool, supports multiple ESC-style attack paths

| Certipy | Certificate template exploitation and AD enumeration | Python-based, covers ESC1-ESC16 attack paths

| PKINIT tools | Misuse PKINIT for Kerberos Ticket Granting Ticket (TGT) requests | Supports certificate-based Kerberos authentication

| Whisker | Shadow credentials and Key Trust misuse | C# tool, manipulates the msDS-KeyCredentialLink attribute

| pyWhisker | Shadow credentials and Key Trust misuse | Python equivalent of the Whisker tool

Table 1. Common AD CS attack tools.

Each of the tools listed plays a distinct role in the AD CS attack chain. Certify and Certipy are the primary utilities for enumerating and exploiting AD CS objects such as vulnerable certificate templates and CAs. For example, a common first step in AD CS attacks is the use of Certify to enumerate CAs in an Active Directory environment, as Figure 6 shows.

Figure 6. Using Certify to enumerate CAs in the Active Directory environment.

The operational use of Certipy has been observed in ransomware activity. The DFIR Report identified an exposed toolkit associated with the Fog ransomware group, highlighting the role of AD CS abuse in modern ransomware operations. Figure 7 shows a Cortex XDR alert detecting Certipy LDAP queries against certificate templates and other AD CS objects, illustrating reconnaissance activity during an AD CS attack.

Figure 7. Detection and prevention of Certipy, as seen in Cortext XDR.

PKINITtools extends misuse into Kerberos by leveraging certificate-based authentication to request TGTs. For persistence, Whisker and pyWhisker specialize in shadow credential and Key Trust attacks, enabling stealthy long-term access by manipulating the msDS-KeyCredentialLink attribute. Figure 8 demonstrates the use of pyWhisker to add malicious key credentials to a user account for persistence.

Figure 8. Using pyWhisker to add key credentials to a user account.

The availability of these open-source tools lowers the barrier of entry to complex AD CS exploitation. What once required deep expertise can now be executed by moderately skilled attackers, a shift that has accelerated adoption of these techniques across the threat landscape.

## Conclusion

As organizations harden traditional attack surfaces, adversaries increasingly turn to AD CS as a stealthy and under-monitored path to privilege escalation and persistence. Neglecting certificate services leaves a critical security gap, allowing serious exploitation methods to remain effectively unguarded.

To combat the evolution of AD CS compromise techniques and the expansion of attack toolkits, defenders must maintain secure certificate template configurations, monitor unusual certificate and key activity and maintain visibility across authentication paths. Strong configuration hygiene, combined with behavioral detection, enables organizations to identify and respond to stealthy AD CS exploitation before it results in privilege escalation or persistent access.

Palo Alto Networks customers are better protected from the threats discussed above through the following products:

### Cortex XDR and XSIAM

Cortex XDR and XSIAM are designed to prevent the execution of known malicious malware and prevent the execution of unknown malware using Behavioral Threat Protection and machine learning based on the Local Analysis module.

### Cortex User Entity Behavior Analytics (UEBA)

Cortex User Entity Behavior Analytics (UEBA ) helps to detect authentication and credential-based threats by analyzing user activity from multiple data sources including endpoints, network firewalls, Active Directory, identity and access management solutions, and cloud workloads. Cortex builds behavioral profiles of user activity over time with machine learning.

By comparing new activity to past activity, peer activity and the expected behavior of the entity, Cortex detects anomalous activity that may be indicative of credential-based attacks.

### Cortex Cloud Identity Security

Cortex Cloud Identity Security encompasses Cloud Infrastructure Entitlement Management (CIEM), Identity Security Posture Management (ISPM), Data Access Governance (DAG) as well as Identity Threat Detection and Response (ITDR) and provides clients with the necessary capabilities to improve their identity-related security requirements.

By providing visibility into identities and their permissions within cloud environments, Cortex Cloud Identity Security helps to accurately detect misconfigurations and unwanted access to sensitive data, and provides real-time analysis of usage and access patterns.

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

## Additional Resources

- Threat Actor Insights: Navigating Through The Fog – The DFIR Report

- Certipy - AD CS Attack & Enumeration Toolkit – GitHub

- Certify: Active Directory certificate abuse – GitHub

- Certifried: Active Directory Domain Privilege Escalation (CVE-2022–26923) – Oliver Lyak, Institut For Cyber Risk

- Fog Malware Family – Malpedia

- What is Active Directory Certificate Services? – Microsoft Learn

- Detecting Active Directory Certificate Services Abuse with Cortex XDR™ – Blog, Palo Alto Networks

- Certified Pre-Owned: Abusing Active Directory Certificate Services [PDF] – Will Schroeder and Lee Christensen, SpecterOps

- Shadow Credentials: Abusing Key Trust Account Mapping for Account Takeover – SpecterOps

- Fighting Ursa Archives – Unit 42, Palo Alto Networks

- Fluttering Scorpius – Unit 42, Palo Alto Networks

## Appendix A: Detection Strategies: Beyond Signatures

Attackers exploit native PKI and Active Directory features in ways that can blend into normal operations. Detecting AD CS misuse requires more than just monitoring individual events; effective detection involves:

- Correlating multiple event types

- Tracking unusual patterns

- Applying a baseline for user activity

Table 2 lists the specific Windows Event IDs essential for detecting AD CS-related anomalies and providing the necessary telemetry for threat hunting operations.

### Key Event IDs

| Log | Event ID | Description

| Security | 4886 | Certificate services received a certificate request

| Security | 4887 | Certificate services approved a certificate request and issued a certificate

| Security | 4898 | Certificate services loaded a template

| Security | 5136 | A directory service object was modified

| Security | 4768/4769 | Kerberos TGT and service ticket requests

| Microsoft-Windows-LDAP-Client | 30 | LDAP client search

| Microsoft-Windows-ActiveDirectory_DomainService | 1644 | LDAP server search

Table 2. Key Event IDs for AD CS monitoring.

Note: To maximize detection capabilities, all relevant audit policies must be enabled and configured correctly, using resources such as the Cortex XDR AD CS Event Setup documentation.

### LDAP Activity Monitoring

Lightweight Directory Access Protocol ( LDAP ) queries are a critical indicator of reconnaissance and exploitation in AD CS attacks. Attackers often enumerate certificate templates, group memberships, and msDS-KeyCredentialLink attributes via LDAP before attempting privilege escalation. High volumes of queries, repeated requests for sensitive objects, or unusual patterns from accounts that don’t usually perform administrative lookups should be treated as suspicious.

Correlating LDAP activity with certificate issuance events or directory modifications can help detect adversarial activity early, including ESC-style template misuse and shadow credential registration.

Monitoring the following LDAP queries is instrumental in identifying adversarial reconnaissance and the initial stages of AD CS infrastructure enumeration:

- objectClass=pKICertificateTemplate

- objectCategory=CN=PKI-Enrollment-Service

- msDS-KeyCredentialLink attributes

Tools like Certify and Certipy perform broad and repeated LDAP queries across users, groups and certificate templates, making this activity a strong early warning signal.

Figure 9 highlights an LDAP event where an attacker queried for sensitive AD CS attributes such as msDS-KeyCredentialLink .

Figure 9. Windows Event 1644 showing an LDAP query targeting the msDS-KeyCredentialLink attribute.

An example from recent years of an attacker using this technique in the wild is described in a 2025 advisory from the U.S. Cybersecurity and Infrastructure Security Agency (CISA) which describes a cyberespionage campaign attributed to Fighting Ursa (also known as APT28, Fancy Bear, Forest Blizzard). In this campaign, the threat actor used tools such as ADExplorer and Certipy to collect certificate services and Active Directory data from target environments prior to further exploitation.

Figure 10 shows an alert detecting ADExplorer enumerating AD CS objects. This type of behavior, including mass queries of certificate templates and AD objects, can indicate early-stage reconnaissance and warrants investigation.

Figure 10. Screenshot from a Cortex XDR alert on the detection and prevention of ADExplorer.exe .

### Template Misuse – ESC Attacks

Monitoring template usage helps detect attacks across the ESC1–ESCn spectrum, where overly permissive templates are exploited. Event ID 4898 indicates that a certificate template was loaded. Signs of misuse include:

- msPKI-RA-Signature = 0: No authorized signatures required

- CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT : Requester can specify the SAN in the CSR

- msPKI-Enrollment-Flag = 0x0 (0): Manager approval is disabled

Together, these conditions point to misconfigurations that attackers turn into privilege escalation paths.

#### Monitoring Certificate Service Activity

The following Event IDs can reveal unusual request patterns:

- 4886: Received certificate request

- 4887: Certificate issued

For example, a low-privileged account requesting certificates from high-privileged templates may be an indication of ESC-style template misuse. To differentiate legitimate activity from attacks, track enrollment rights, SAN usage and EKU flags.

#### Directory Modifications and Shadow Credentials

To detect shadow credential attacks, focus on unexpected modifications to the msDS-KeyCredentialLink attribute. Given that attackers use this attribute to silently add their own credentials to privileged accounts, even small changes should be investigated. Event ID 5136 records changes to directory objects.

Figure 11 shows a directory modification event indicating a potential shadow credential attack.​

Figure 11. Event 5136 detecting a change in the msDS-KeyCredentialLink attribute.

#### Kerberos Ticket Requests and Lateral Movement

Monitoring Kerberos TGT and service ticket events can help detect potential privilege escalation and lateral movement attempts – Event IDs 4768 and 4769. When correlated with suspicious certificate issuance or key registration activity, PKINIT authentication requests can reveal attackers leveraging stolen or shadow credentials to impersonate users without triggering password alerts.

## Appendix B: Cortex XDR/XSIAM Alerts on AD CS Activity

Table 3 outlines the Cortex XDR/XSIAM alerts that detect AD CS-related malicious behaviors across multiple attack stages.

| Alert Name | Alert Source | MITRE ATT&CK Technique

| Vulnerable certificate template loaded | XDR Analytics BIOC, Identity Analytics | Steal or Forge Authentication Certificates (T1649)

| Suspicious certificate template modification | XDR Analytics BIOC, Identity Analytics | Steal or Forge Authentication Certificates (T1649)

| Key credential attribute modification | XDR Analytics BIOC, Identity Analytics | Modify Authentication Process (T1556)

| PKINIT TGT authentication request | XDR Analytics BIOC, Identity Analytics | Use Alternate Authentication Material (T1550)

| LDAP AD CS Enumeration via Attack Tool | XDR Analytics BIOC, Identity Analytics | Account Discovery (T1087)

| Discovery of misconfigured certificate templates using LDAP | XDR Analytics BIOC | File and Directory Discovery (T1083)

| A user queried AD CS objects via LDAP | XDR Analytics BIOC, Identity Analytics | Steal or Forge Authentication Certificates (T1649)

| A suspicious process queried AD CS objects via LDAP | XDR Analytics BIOC, Identity Analytics | Steal or Forge Authentication Certificates (T1649)

| A user certificate was issued with a mismatch | XDR Analytics BIOC, Identity Analytics | Steal or Forge Authentication Certificates (T1649)

| A machine certificate was issued with a mismatch | XDR Analytics BIOC, Identity Analytics | Valid Accounts: Domain Accounts (T1078.002)

| Unusual CertLog Remote File Write | XDR Analytics BIOC, Identity Analytics | Steal or Forge Authentication Certificates (T1649)

| Privileged certificate request via certificate template | XDR Analytics BIOC, Identity Analytics | Valid Accounts: Domain Accounts (T1078.002)

| PowerShell pfx certificate extraction | XDR Analytics BIOC | Unsecured Credentials: Credentials In Files (T1552.001)

| Deletion of AD CS certificate database entries | XDR Analytics BIOC, Identity Analytics | Indicator Removal (T1070)

| Suspicious Certutil AD CS contact | XDR Analytics BIOC | Steal or Forge Authentication Certificates (T1649)

| Certutil pfx parsing | XDR Analytics BIOC | Data from Local System (T1005)

| The CA policy EditFlags was queried | XDR Analytics BIOC | Valid Accounts (T1078)

| A suspicious process enrolled for a certificate | XDR Analytics BIOC | Steal or Forge Authentication Certificates (T1649)

| A user created a pfx file for the first time | XDR Analytics BIOC, Identity Analytics | Unsecured Credentials: Credentials In Files (T1552.001)

| A user modified the CA audit policy | XDR Analytics BIOC, Identity Analytics | Impair Defenses: Disable Windows Event Logging (T1562.002)

| User set insecure CA registry setting for global SANs | XDR Analytics BIOC, Identity Analytics | Impair Defenses: Disable or Modify Tools (T1562.001)

| A user logged on to multiple workstations via Schannel | XDR Analytics, Identity Analytics | Steal or Forge Authentication Certificates (T1649)

Table 3. Cortex XDR/XSIAM alerts on AD CS activity.
