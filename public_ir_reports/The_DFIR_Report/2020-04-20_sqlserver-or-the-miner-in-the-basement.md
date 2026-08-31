---
title: "Sqlserver, or the Miner in the Basement - The DFIR Report"
source_url: "https://thedfirreport.com/2020/04/20/sqlserver-or-the-miner-in-the-basement/"
published: "2020-04-20T22:45:11+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2020-04-20_sqlserver-or-the-miner-in-the-basement.html"
---

# Sqlserver, or the Miner in the Basement - The DFIR Report
A threat actor logged into the honeypot via RDP and installed XMRig with multiple persistence mechanisms. The actor used icacls and attrib to lock down directories and files to make detection and eradication difficult.

While bitcoin was at $20K, actors dropping mining software was all the rage, but with Bitcoin and most currencies less than half their peak value you’d be forgiven thinking the malicious cryptominer has gone away. These days the news points to big game ransomware as the hottest threat actor trend. And while that may be the case don’t forget about the cryptominers.

## Intial Access

Initial entry was completed by two different IP addresses via RDP.
95.156.252.94
185.155.96.83

## Artifacts

### sqlsupdater.exe

##

### conhost.exe

Ever heard of the Non-Sucking Service Manager (NSSM)?

nssm is a service helper which doesn’t suck. srvany and other service helper programs suck because they don’t handle failure of the application running as a service. If you use such a program you may see a service listed as started when in fact the application has died. nssm monitors the running service and will restart it if it dies. With nssm you know that if a service says it’s running, it really is.

We think NSSM is used to manage the sqlserver.exe process which includes the miner. Read more about NSSM here .

### install.bat

The install script does as is named and is used to deploy the actors payload. Some notable actions in the script include hiding the files in the C:\Windows\Fonts\ location and then using DACLs via icacls scripting to remove access to the miner. Additionally as with many late stage miners, they look to kill competition that may be running on the box they’ve infected. (There are multiple misspellings in these scripts but they do accomplish their overall goal.)

### sqlserver.exe

This is the Monero coin miner binary known as XMRig. Here are a few strings from the binary.

You can see from the below strings that this is most likely XMRig version 5.1.0.

This binary is attempting to mimic sqlserver 2.7.8.2 which is not a real sql version.

For more information on XMRig see a write up on securityintelligence.com and XMRigs GitHub page.

## sqlsupdater.sfx.exe

##

sqlsupdater.sfx.exe contained the two files above and appears to include Neshta which is usually used for persistence. Here are a couple interesting strings from the binary.

Neshta installs itself into the registry for persistence using the following:

Registry key: HKLM\SOFTWARE\Classes\exefile\shell\open\command
Value: %SystemRoot%\svchost.com “%1” %*

Read more about Neshta at Cylance .

## update.bat

update.bat is used to run an update (go figure). It deletes scheduled tasks if they exist, deletes old binaries, creates directories, sets permissions on the new files and then starts sqlsupdater.exe

Other pools that are used in crypto-currency mining are added to the hosts file and directed to local host. This may be to help protect the infected machine from competing crypto-mining malware campaigns.

The next sequence creates multiple scheduled tasks and then cleans up after itself.

## Mining

The miner is finally invoked via command-line arguments that include the mining pools in use for the payout as well as the key used.

Thus far this particular wallet has received little payout. With 1.32 XMR or about $70 USD at time of publication. It is possible that they are using multiple keys across the campaign to avoid tracking or having funds locked by a pool for abuse reports.

Summary

Cryptomining is still alive and well! The attackers use of icacls and attrib were quite interesting and provide a few examples for easy detection writing. We also found it interesting that there were multiple persistent mechanisms from Neshta to NSSM to scheduled tasks and services.

If you get stuck in a position where you can’t see or access files, the easiest thing to do is to become system by using psexec or something similar. This allows you to access all files, folders, scheduled tasks, etc. We were fairly impressed by the completeness of this attack. It appears that these actors have been in the business for awhile or they are buying their tools.

Although the actors haven’t earned very much according to this wallet, if you do this at scale and/or without costs, the benefits are there, especially for operators in developing countries.

Enjoy our report? Please consider donating $1 or more to the project using Patreon . Thank you for your support!

## IOCs

Source IPs of RDP login
95.156.252.94
185.155.96.83
Exe File hashes
sqlsupdater.sfx.exe|77600facbd18746636921bab1a3918e0 77600facbd18746636921bab1a3918e0 bcb89eade054991169ebf1df6499011610198a5a cf3509a100b6110da866af3f7c1a514c6c27ca82b1105d0e45a2469f8e87426d sqlserver.exe|12959e0e561670229c98b4978d7b4738 12959e0e561670229c98b4978d7b4738 5b70d3e0182b553593cd8ca3c907d68018fd7f1f 1acb9ba8ddf74e1b4a8da54390605f33b31c7976a49fa135b5ab0613b277196f
Mining pool domains:
domain004.gleeze.com test1000.ooguy.com test1003.accesscam.org gamepanel2.theworkpc.com xmr-eu1.nanopool.org
sqlsupdater.exe

sqlsupdater.sfx.exe

### Persistence Mechanisms

Registry key: HKLM\SOFTWARE\Classes\exefile\shell\open\command
Value: %SystemRoot%\svchost.com “%1” %*

sqlbrowsers service name, multiple service names in the .bat files above in artifacts.

Multiple scheduled tasks were created, see the .bat files above in artifacts.

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
