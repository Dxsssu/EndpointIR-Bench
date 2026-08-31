---
title: "Tricky Pyxie - The DFIR Report"
source_url: "https://thedfirreport.com/2020/04/30/tricky-pyxie/"
published: "2020-04-30T11:22:27+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2020-04-30_tricky-pyxie.html"
---

# Tricky Pyxie - The DFIR Report
Trickbot has been seen often as a payload dropped by other malware like Emotet, and has been seen dropping many payloads, most notably ransomware. But while Emotet sleeps it may be that this botnet is passing out access to other groups a la Emotet style. In the past month we witnessed a Trickbot infection lie dormant for several days before being scoped by Cobalt Strike and then left with just a Pyxie infection.

## Initial infection

A Trickbot sample was run in the lab:
dmndfkle.exe|81ee8c62fff641b99f3e5ac83c575526 81ee8c62fff641b99f3e5ac83c575526 cdde976a0d485e91c9e304eeac91eab5b19126c1 4dc82acf2a736e9cbaa39b5decfa943177417ad88d995ebe7fba79d9d0579849
Upon execution the sample moved itself to:
C:\Users\user\AppData\Roaming\CmdValidate\ேதததததகககஏஏேஏேேஓோோபகபகபபபஊஊூலலலல.exe
We’ve seen the Trickbot actors use various unicode characters for some time now, we believe that the intention here is to evade security tools as many have difficulty parsing these characters and can fail to detect or even simply break while trying to parse these characters.

After an hour or so we witnessed the common Trickbot internal reconnaissance using Microsoft utilities.

During the time Trickbot was active network traffic indicated gtag man6

Locally on the system the Trickbot config file showed the following configuration.

From the infected host we saw two different processes get injected for running Trickbot and communications with the C2 infrastructure.
C:\Windows\System32\svchost.exe C:\Windows\System32\wermgr.exe
These legitimate windows executables allow Trickbot to run unhindered and undetected on the system. After the initial checkins and setting up on the host, Trickbot proceeded to do nothing but beacon for 3 days. Then out of the blue things moved on to the next phase.

## Group 2 Arrives

Trickbot delivered a Cobalt Strike payload using PowerShell to inject into memory.

This Cobalt Strike payload was using the malleable c2 amazon profile.

Cobalt Strike ran a flurry of windows recon commands and this interesting AV enumeration script:

Commands ran by the attacker during Cobalt Strike session:
C:\Windows\system32\cmd.exe /C whoami /groups C:\Windows\system32\cmd.exe /C tasklist /v C:\Windows\system32\cmd.exe /C netstat -na | findstr "EST" C:\Windows\system32\cmd.exe /C systeminfo C:\Windows\system32\cmd.exe /C ipconfig /displaydns C:\Windows\system32\cmd.exe /C wmic /Namespace:\\root\SecurityCenter2 Path AntiVirusProduct Get displayName,pathtoSignedProductExe wmic /Namespace:\\root\SecurityCenter2 Path AntiVirusProduct Get displayName,pathtoSignedProductExe netstat -an net user net use net view /all netstat -an net user net use net view /all net view /all /domain cmd.exe /c "reg.exe save hklm\security c:\windows\temp\xqjxxkmbrx" reg.exe save hklm\security c:\windows\temp\xqjxxkmbrx cmd.exe /c "reg.exe save hklm\system c:\windows\temp\kjmohmuk" reg.exe save hklm\system c:\windows\temp\kjmohmuk cmd.exe /c "reg.exe save hklm\sam c:\windows\temp\emmbnafzjtwq" reg.exe save hklm\sam c:\windows\temp\emmbnafzjtwq net share C:\Windows\system32\net1 share net config workstation C:\Windows\system32\net1 config workstation net group "Domain Admins" C:\Windows\system32\net1 group "Domain Admins" route print net localgroup C:\Windows\system32\net1 localgroup ipconfig /all tasklist /V net share C:\Windows\system32\net1 share net config workstation C:\Windows\system32\net1 config workstation net group "Domain Admins" C:\Windows\system32\net1 group "Domain Admins" route print net localgroup C:\Windows\system32\net1 localgroup ipconfig /all tasklist /V net config workstation C:\Windows\system32\net1 config workstation nslookup -type=any %%userdnsdomain%% net config workstation C:\Windows\system32\net1 config workstation nslookup -type=any %%userdnsdomain%%

## PyXie

At the same time that Cobalt activity began an additional entry point began using a combination of PyXie RAT and a Logmein signed binary used to load the RAT. For an in depth breakdown of Pyxie check out this write-up by Ryan Tracey of Cylance.

### C2

PyXie C2 uses TLS to encrypt its communication so it was very helpful to have ssl interception here. Multiple ET-PRO signatures (2029084, 2029086) fired for this communication based on the certificate. C2 ip is 162.[]248[.]245[.]71 and the domain is benreat.com.

Here’s a keep alive from PyXie. Notice the referer being google.com; that wouldn’t normally arise suspicion. The user-agent string does appear to be unique as we weren’t able to validate the string. Looking at the content we see some interesting information being passed such as uptime, system name, admin or not, domain name, if in memory or on disk, godmode (system?), av check, os version, etc.

### Sharphound

Sharphound was downloaded and run via PyXie.

After the initial flurry of activity Cobalt Strike fell off, PyXie continued with little beacon activity and once a day returning to dump creds via the registry.

###

## Conclusion

We did not see a final action on objectives, based on TTP’s ransomware could have been a likely choice.

Trickbot seem to be continuing strong even in Emotet’s absence and seeing usage of PyXie is certainly new ground for infections we’ve seen. Still being able to detect default behavior can help you quickly identify and remediate malicious behavior. Trickbot C2 infrastructure is quite well known and you should treat any Trickbot infection as a potential full domain compromise.

Being able to detect Cobalt Strike and Bloodhound/Sharphound activity may just save your digital domain.

Enjoy our report? Please consider donating $1 or more to the project using Patreon . Thank you for your support!

## IOCs

Pyxie Intezer

Trickbot Any.Run
dmndfkle.exe|81ee8c62fff641b99f3e5ac83c575526 81ee8c62fff641b99f3e5ac83c575526 cdde976a0d485e91c9e304eeac91eab5b19126c1 4dc82acf2a736e9cbaa39b5decfa943177417ad88d995ebe7fba79d9d0579849 192.169.6.180 ConsoleHost_history.txt|444b446dd246829db1b7b343a7d4d9ce 444b446dd246829db1b7b343a7d4d9ce 97a481c07f8ca2346f5167ae2ae0d992a8fdebf4 199969c142a625ac50364623ba43898f3db4e4ff3441f93911717ce5cd68bb0f LMIGuardianDll.dll|82df61349a9391a6cf236047c7471572 82df61349a9391a6cf236047c7471572 b8ec908cc4a0e8e406ce5d100a8f34a10fe3d064 80bd15267756343f028cbe77afe810068b0e6a36ce32f52be63f620ef5b5ed89 LMIGuardianDll.dll.dat|a82672168756becefe2dac9234ee61f6 a82672168756becefe2dac9234ee61f6 5bfc42ed380e5b9701ccaec2d2f312069ef4af11 39646dd3bf20ff74415b806cea08daa8277ccc1bb7da5df4c5bd4313ae5cd697 cmdline.txt|6d0b192efb3909556cc6452ee5336b93 6d0b192efb3909556cc6452ee5336b93 a4789b71f8382f23b39c656f797fe1c2f22e3cc8 4beed76d5848fda5c41a9705ebef9bd81278e085ed57ffacc97b188ed8979b50 51.89.115.112|443 185.141.27.225|443 151.80.212.114|443 5.182.210.178|443 188.119.113.60|443 91.235.129.199|443 185.234.72.193|443 194.5.250.200|443 185.14.29.141|443 185.99.2.197|443 185.234.72.50|443 194.5.250.201|443 108.170.61.186|443 217.12.209.159|443 185.99.2.44|443 51.89.115.108|443 164.68.120.58|443 164.132.255.19|443 148.251.185.164|443 94.250.250.69|443 94.250.249.170|443 195.123.237.105|443 190.214.13.2|449 181.129.104.139|449 181.112.157.42|449 181.129.134.18|449 131.161.253.190|449 121.100.19.18|449 202.29.215.114|449 171.100.142.238|449 190.136.178.52|449 45.6.16.68|449 110.232.76.39|449 122.50.6.122|449 103.12.161.194|449 36.91.45.10|449 103.227.147.82|449 96.9.77.56|449 103.5.231.188|449 110.93.15.98|449 200.171.101.169|449 162.248.245.71 185.206.144.40 216.189.145.132 teamchuan.com benreat.com tedxns.com 148.251.185.186|443 170.238.117.187|8082 176.119.159.147|443 178.156.202.251|443 185.99.2.152|447 203.176.135.102|8082 217.12.209.176|447 217.12.209.244|443 51.254.164.243|443 5.182.210.30|447 51.89.115.121|443 5.196.247.14|443 93.189.42.81|443 96.9.77.142|80 Mozilla/4.0 (compatible; MSIE 2.1; Windows NT 5.0; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
