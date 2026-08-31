---
title: "Dharma Ransomware - The DFIR Report"
source_url: "https://thedfirreport.com/2020/04/14/dharma-ransomware/"
published: "2020-04-14T00:08:55+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2020-04-14_dharma-ransomware.html"
---

# Dharma Ransomware - The DFIR Report
An attacker logged into the honeypot via RDP from 178.239.173[.]172. Within 10 minutes the attacker went from local admin, to domain admin to installing ransomware on multiple machines. The attacker used Defender Control to turn off Defender and then used Mimikatz to dump credentials. From there the attacker used Network Scanner to scan the local subnet. The attacker then used RDP to log into each machine to manually run the ransomware payload.

Here is a screenshot of Network Scanner which was renamed by the actors to NSold.exe

Logs showing the extraction and use of DefenderControl to disable Windows Defender during the attack:

Here is a screenshot of the ransom which pops up at login.

This FILES ENCRYPTED file can be found in the root of C as well as on the desktop. This file appears to be written to every folder where encryption occured.

We’ve seen the below command a few times in ransomware intrusions and it might be worth writing a rule to detect findstr.exe + /c:system$ and/or /c:sistem$ in the command line arguments.

We submitted information to ID Ransomware which provided the below information.

We’ve seen the same pdb path below used for Dharma in the past so this pdb path stays consistent and would be a good detection.

More information about Dharma/Crysis can be found here .

## Summary

This attacker was able to deploy ransomware to 5+ machines in under 10 minutes which was quite impressive. The attacker used Defender Control which we’ve seen in the past to disable Defender and Mimikatz to dump credentials. There are multiple detection rules that can be written from this intrusion which should help improve detection times moving forward. With that said when the attackers move this fast you must respond to incidents in a timely matter to catch the attacker before they accomplish their mission.

Enjoy our report? Please consider donating $1 or more to the project using Patreon . Thank you for your support!

## IOCs

The ransomware payload can be found at Any.Run

RDP login from 178.239.173[.]172

The ransomware payload created a few run keys

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
