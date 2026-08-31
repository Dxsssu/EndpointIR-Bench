---
title: "Lockbit Ransomware, Why You No Spread? - The DFIR Report"
source_url: "https://thedfirreport.com/2020/06/10/lockbit-ransomware-why-you-no-spread/"
published: "2020-06-10T14:22:25+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2020-06-10_lockbit-ransomware-why-you-no-spread.html"
---

# Lockbit Ransomware, Why You No Spread? - The DFIR Report
RDP brute forcing continues to be a favorite entry point for ransomware actors. In this past month we saw activity from the Lockbit ransomware family.

### Initial Access:

RDP login from 165.231.142.36. Threat actor logged in, then switched accounts to a DA 15 minutes later.

### Action on Objectives:

Unlike other actors we’ve seen in the lab or in other reports take meticulous inventory and thoroughly enumerate a victim environment this actor moved straight into final phase activity.

They used a tool to disable the security defenses of the host they had access to with a program masquerading in the user Appdata location.
%APPDATA%\svchost.exe
Which issued the following commands.

netsh firewall set opmode disable net stop security center net stop WinDefend

The malware then kept a communication stream open to an Ukrainian FTP server even after ransomware deployment.

svchost is seen sending key logs to the following FTP server using Hakops15 which occurred once per day after infection.

Then they moved straight into the ransom deployment. With 2 tools apparently selected, screensaver.exe and 9689A16B72D48DAB.exe deployed right on the desktop.

The screensaver executable doesn’t appear to have been used in attack and allows one to lock out access to the desktop.

Instead they ran the random number named executable which is of the Lockbit ransomware variety.

As expected we see the standard set of ransomware commands:

\"C:\\Windows\\System32\\cmd.exe\" /c vssadmin delete shadows /all /quiet &amp; wmic shadowcopy delete &; bcdedit /set {default} bootstatuspolicy ignoreallfailures &; bcdedit /set {default} recoveryenabled no &; wbadmin delete catalog -quiet vssadmin delete shadows /all /quiet wmic shadowcopy delete bcdedit /set {default} bootstatuspolicy ignoreallfailures bcdedit /set {default} recoveryenabled no wbadmin delete catalog -quiet
Afterwards we saw the executable ping the entire /16 and then make SMB connections to alive hosts, but no actual infection was spread. We don’t understand why the ransomware did not spread as authentication was successful and shares were enumerated.

At this point, the malware completed its ransom of the one system leaving the following note below.

Lockbit created the following reg keys:

### Lockbit Support Page:

This ransomware family uses a website and live chat functionality as opposed to previous families we investigated which have mostly relied on email contact.

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
