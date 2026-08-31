---
title: "Inside the Open Directory of the “You Dun” Threat Group - The DFIR Report"
source_url: "https://thedfirreport.com/2024/10/28/inside-the-open-directory-of-the-you-dun-threat-group/"
published: "2024-10-28T01:05:30+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2024-10-28_inside-the-open-directory-of-the-you-dun-threat-group.html"
---

# Inside the Open Directory of the “You Dun” Threat Group - The DFIR Report
## Key Takeaways

- Analysis of an open directory found a Chinese speaking threat actor’s toolkit and history of activity.

- The threat actor displayed extensive scanning and exploitation using WebLogicScan, Vulmap, and Xray, targeting organizations in South Korea, China, Thailand, Taiwan, and Iran.

- The Viper C2 framework was present as well as a Cobalt Strike kit which included TaoWu and Ladon extensions.

- The Leaked LockBit 3 builder was used to create a LockBit payload with a custom ransom note that included reference to a Telegram group which we investigated further in the report.

An audio version of this report can be found on Spotify , Apple , YouTube , Audible , & Amazon .

## The DFIR Report Services

Reports such as this one are part of our All Intel service and are categorized as Threat Actor Insights.

- Private Threat Briefs : Over 20 private DFIR reports annually.

- Threat Feed : Focuses on tracking Command and Control frameworks like Cobalt Strike, Metasploit, Sliver, etc.

- All Intel : Includes everything from Private Threat Briefs and Threat Feed, plus private events, Threat Actor Insights reports, long-term tracking, data clustering, and other curated intel.

- Private Sigma Ruleset : Features 100+ Sigma rules derived from 40+ cases, mapped to ATT&CK with test examples.

- DFIR Labs : Offers cloud-based, hands-on learning experiences, using real data, from real intrusions. Interactive labs are available with different difficulty levels and can be accessed on-demand, accommodating various learning speeds.

#### Table of Contents:

- Case Summary

- Services

- Analysts

- Capability

- Victims

- Infrastructure

- Adversary

- Diamond Model

- Indicators

- MITRE ATT&CK

## Case Summary

The DFIR Report’s Threat Intel Team detected an open directory in January 2024 and analyzed it for trade craft and threat actor activity. Once reviewed, we identified it was related to the Chinese speaking hacking group that call themselves “You Dun”.

The threat actor conducted various activities using the host we investigated which included reconnaissance and web exploitation activities. Using tools such as WebLogicScan, Vulmap, and Xray, they were able to identify numerous vulnerable servers. They exploited several websites running Zhiyuan OA software and used SQLmap to conduct SQL injection.

We found evidence of several successful exploitation attempts. After gaining access we found use of further tools to try and use various exploits to elevate privileges on the compromised hosts, including the use of traitor for Linux privilege escalation exploits and CDK for docker and kubernetes privilege escalation.

Both Cobalt Strike and Viper framework files were visible in the open directory. A zip archive that contained the files for a Cobalt Strike team server, included the plugins TaoWu and Ladon which extend the capabilities of the framework greatly. The DFIR Report Threat Intel Team tracked the server as hosting active command and control from January 18th through Feburary 10th of 2024. Using data from the leaked server we identified a cluster of eight IP address’s all being used to proxy the command and control for the same threat actor and active for the same time frame.

The threat actor also utilized the leaked LockBit 3 ransomware builder to create a custom binary LB3.exe. The ransom note the LockBit binary produced provided the contact details as a Telegram group “You_Dun” administrated by “EVA”. The group responsible also use the name “Dark Cloud Shield Technical Team”. This group appears to be involved in selling “penetration testing” according to their channels, but also engaged in illicit data sales, DDOS, and based on the LockBit binary, also use ransomware to earn a payday.

If you would like to get an email when we publish a new report, please subscribe here .

## Analysts

Analysis and reporting completed by @pcsc0ut and @svch0st .

## Capability

### Reconnaissance

WebLogicScan

The threat actor use WebLogicScan , a python script that scans for vulnerabilities in WebLogic.

Based on bash history, they ran the tool by supplying various text files to the script.

Vulmap

The threat actor used vulmap.py to also scan for WebLogic vulnerabilities by providing several lists of their targets.

Bash history excerpts:

Below is the help options detailing the “-a” switch that defines what application is being targeted.

Xray

The threat actor scanned for vulnerabilities more broadly with the tool Xray for vulnerabilities against two Chinese websites.

Bash history excerpts:

dirsearch

The threat actor used dirsearch to attempt to scan for URL paths against their targets. A log of one of their scans still remained:

### Initial Access

Sqlmap

The threat actor used sqlmap to compromise various websites:

Below is one of the many commands the threat actor ran to dump tables from a Pharmaceutical organization in South Korea:

Seeyon_exp

The script seeyon_exp was used to upload JSPX web sells to several sites by exploiting a component in the software Zhiyuan OA .

The results that were left behind by the threat actor provided evidence of the web shells from the successful exploitation:

Translated we can see the confirmation of what was successful with each target.

Weaver

Another tool weaver was also used to scan for vulnerabilities and exploit Zhiyuan OA instances.

### Command and Control

Cobalt Strike (S0154)

The bash history included a nohup command to run a Cobalt Strike server with the following password and account details:

The IP 116.212.120.32 exposed the following beacon configuration, most notably a cracked watermark of 987654321:

Cobalt Strike Beacon: x86: beacon_type: HTTP dns-beacon.strategy_fail_seconds: -1 dns-beacon.strategy_fail_x: -1 dns-beacon.strategy_rotate_seconds: -1 http-get.client: Cookie http-get.uri: 116.212.120.32,/IE9CompatViewList.xml http-get.verb: GET http-post.client: Content-Type: application/octet-stream id http-post.uri: /submit.php http-post.verb: POST maxgetsize: 1048576 port: 80 post-ex.spawnto_x64: %windir%\sysnative\rundll32.exe post-ex.spawnto_x86: %windir%\syswow64\rundll32.exe process-inject.execute: CreateThread SetThreadContext CreateRemoteThread RtlCreateUserThread process-inject.startrwx: 64 process-inject.stub: e43a1b63f09794f74d90a9889f7acb77 process-inject.userwx: 64 proxy.behavior: 2 (Use IE settings) server.publickey_md5: a490a5e2db1fcc496e6b793a8ea02a19 sleeptime: 60000 useragent_header: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; BOIE9;ENUS) uses_cookies: 1 watermark: 987654321 x64: beacon_type: HTTP dns-beacon.strategy_fail_seconds: -1 dns-beacon.strategy_fail_x: -1 dns-beacon.strategy_rotate_seconds: -1 http-get.client: Cookie http-get.uri: 116.212.120.32,/visit.js http-get.verb: GET http-post.client: Content-Type: application/octet-stream id http-post.uri: /submit.php http-post.verb: POST maxgetsize: 1048576 port: 80 post-ex.spawnto_x64: %windir%\sysnative\rundll32.exe post-ex.spawnto_x86: %windir%\syswow64\rundll32.exe process-inject.execute: CreateThread SetThreadContext CreateRemoteThread RtlCreateUserThread process-inject.startrwx: 64 process-inject.stub: e43a1b63f09794f74d90a9889f7acb77 process-inject.userwx: 64 proxy.behavior: 2 (Use IE settings) server.publickey_md5: a490a5e2db1fcc496e6b793a8ea02a19 sleeptime: 60000 useragent_header: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0) uses_cookies: 1 watermark: 987654321

The threat actor left behind the file 红队版.zip in the root of the open directory.

The zip contained a Cobalt Strike kit which was also the same that was extracted to the root of the open directory.

The aggressor script CrossC2-GithubBot-2023-03-27.cna was sourced from this repo .

The other major modules as part of this Cobalt Strike kit are TaoWu and Landon which extends Cobalt Strike’s capabilities.

TaoWu

The TaoWu aggressor script includes tooling and scripts that adds to Cobalt Strike actions.

It includes a huge number of precompiled binaries in the path taowu-cobalt-strike-master\script :

./0803.exe ./360bowser.exe ./add-admin.exe ./ATPMiniDump.exe ./blocketw.exe ./blue.exe ./BrowserGhost.exe ./BypassAddUser.exe ./certexp.exe ./chfs.exe ./ClearnEventRecordID.ps1 ./ClearnIpAddress.ps1 ./ClearnTempLog.ps1 ./crack.exe ./CredPhisher.exe ./cve-2014-4113.x64.dll ./cve-2014-4113.x86.dll ./cve-2015-1701.x64.dll ./cve-2015-1701.x86.dll ./cve-2016-0051.x86.dll ./CVE-2020-0796.x64.dll ./CVE-2021-1675.x64.dll ./dazzleUP_Reflective_DLL.x64.dll ./DecryptAutoLogon.exe ./DecryptTeamViewer.exe ./dis_defender.exe ./EfsPotato.exe ./encode ./encode.exe ./EncryptedZIP.exe ./FakeLogonScreen.exe ./FullPowers.dll ./Gopher.exe ./GPSCoordinates.exe ./hack-browser-data.exe ./InternalMonologue.exe ./Invoke-EternalBlue.ps1 ./Invoke-MS16032.ps1 ./Invoke-MS16135.ps1 ./iox.exe ./JuicyPotato.x64.dll ./JuicyPotato.x86.dll ./KillEvenlogService.ps1 ./Ladon.exe ./Ladon1.exe ./lazagne.exe ./ListAllUsers.ps1 ./ListLogged-inUsers.ps1 ./ListRDPConnections.exe ./LocalSessionManager.ps1 ./LPE_Reflect_Elevate.x64.dll ./MaceTrap.exe ./MiniDump.exe ./napwd.exe ./navicatpwd.exe ./Net-GPPPassword.exe ./NoAmci.exe ./noNetApiAdd.exe ./NoPowerShell.exe ./RdpThief_x64.tmp ./Recon-AD-AllLocalGroups.dll ./Recon-AD-Computers.dll ./Recon-AD-Domain.dll ./Recon-AD-Groups.dll ./Recon-AD-LocalGroups.dll ./Recon-AD-SPNs.dll ./Recon-AD-Users.dll ./ReflectiveDll.x64.dll ./RegRdpPort.ps1 ./rpcscan.dll ./SafetyKatz.exe ./scout.exe ./scrying.exe ./Seatbelt.exe ./SessionGopher.ps1 ./SessionSearcher.exe ./Sharp3389.exe ./SharpAVKB.exe ./SharpBypassUAC.exe ./SharpChassisType.exe ./SharpCheckInfo.exe ./SharpChromium.exe ./SharpClipHistory.exe ./SharpCloud.exe ./SharpCrashEventLog.exe ./SharpDecryptPwd.exe ./SharpDecryptPwd2.exe ./SharpDir.exe ./SharpDirLister.exe ./SharpDomainSpray.exe ./SharpDoor.exe ./SharpDPAPI.exe ./SharpDump.exe ./SharpEDRChecker.exe ./SharPersist.exe ./SharpEventLog.exe ./SharpExcelibur.exe ./SharpExec.exe ./SharpGetTitle.exe ./SharpGPOAbuse.exe ./SharpHide.exe ./SharpHound.exe ./SharpLocker.exe ./SharpMiniDump.exe ./SharpNetCheck.exe ./SharpOXID-Find.exe ./SharpSCshell.exe ./SharpShares.exe ./SharpSpray.exe ./SharpSpray1.exe ./SharpSQLDump.exe ./SharpSQLTools.exe ./SharpStay.exe ./SharpTask.exe ./SharpWeb.exe ./SharpWebScan.exe ./SharpWifiGrabber.exe ./sharpwmi.exe ./SharpXDecrypt.exe ./SharpZeroLogon.exe ./SharpZip.exe ./Shhmon.exe ./SolarFlare.exe ./SPNSearcher.exe ./SpoolTrigger.x64.dll ./SpoolTrigger.x86.dll ./Stealer.exe ./StickyNotesExtract.exe ./SweetPotato.exe ./Telemetry.exe ./Telemetry3.5.exe ./temp.exe ./user.exe ./Watson.exe ./WeblogicRCE.exe ./WireTap.exe ./WMIHACKER.vbs ./x64 ./x64/bypass.exe ./x64/frpc.exe ./x64/fscan.exe ./x64/index.html ./x64/nc.exe ./x64/npc.exe ./x64/PrintSpoofer.dll ./x64/PrintSpoofer.exe ./x86 ./x86/bypass.exe ./x86/frpc.exe ./x86/fscan.exe ./x86/index.html ./x86/npc.exe ./x86/PrintSpoofer.dll ./x86/PrintSpoofer.exe

Ladon

The Ladon plugin for Cobalt Strike is a framework that allows for lots of automation of intrusion activity.

The documentation ( https://mp.weixin.qq.com/s/GQBXCX1fiSLi6gKY3M-JcA ) includes screenshots such as:

Viper

Viper is a command and control tool used for post exploitation activity. It is one of the C2 frameworks tracked by the DFIR Report Threat Intelligence group . According to the GitHub profile:

It was installed through the execution of the f8x script, which installs docker dependencies and a mostly pre-configured docker image:

The threat actor was asked to provide a password upon initial install, and reused the password that was configured for the Cobalt Strike team server:

The Viper C2 management panel was observed listening on the default tcp port 60000, and using the default SSL certificates provided with the docker image. A pivot on the default SSL certificate in Censys shows a much broader network of this VIPER docker image publicly exposed on the Internet.

Censys Search:

services.tls.certificates.leaf_data.fingerprint: 4de3278507c89d2242a12c20b74878e3f84970c463a924771f156a3da7d7b5a1 or services.tls.certificates.chain.fingerprint: 4de3278507c89d2242a12c20b74878e3f84970c463a924771f156a3da7d7b5a1

The threat actor was observed using the Viper C2 for post exploitation on a AWS host running a Bitnami WordPress app. After initial access was gained, the vipermsf (Metasploit) backend was utilized to run a one-line command to upload and execute a file:

The ONE-LINE-CMD pattern matches the format utilized in the Viper MSF Web Delivery API found in Github :

Information gathered from the Redis RDB dump file using ( https://github.com/sripathikrishnan/redis-rdb-tools ) shows that the execution was successful, and the threat actor was able to achieve execution of the payload (recovered from the host info module):

Due to the location of the payload being written to disk matching POC exploit code ( https://github.com/projectdiscovery/nuclei-templates/blob/main/http/cves/2021/CVE-2021-25003.yaml ) , we assess with high confidence that initial access was gained through a WordPress plugin WPCargo exploit, specifically, the Remote Code execution vulnerability CVE-2021-25003.

### Privilege Escalation

The reverse shell created by the payload appeared to be used to run a docker container exploit using a tool called CDK .

The mount-cgroup is a module that utilizes a docker container escape exploit documented by @_fel1x:

Additional follow-on activity showed the threat actor uploading an additional file using a VIPER agent used for privilege escalation:

traitor-amd64 upload completed

Traitor is a tool that includes several privilege escalation exploits for Linux:

### Impact

The threat actor had a copy of LockBit ransomware in the directory .local\LB3.exe and in the bash history of the host there were two RAR files they had deleted:

While the archives no longer existed for us to analyze, we assess with moderate confidence that these were copies of the previously leaked LockBit Black ransomware builder.

Triage Sandbox run screenshot of .local\LB3.exe:

Ransom note presented after executing the LB3.exe binary:

When analyzing the left behind LB3.exe binary, the following ransomware note is created upon execution:

The telegram channel mentioned is hXXps://t.me/You_Dun. Further analysis of this group is discussed in the Adversary section.

## Victims

Countries

- South Korea

- China

- Thailand

- Taiwan

- Iran

As part of reconnaissance activities, the threat actor left their target URL lists they used for several tools which were separated by country:

- ./vulmap/kk.txt – Korean IPs and Domains

- ./vulmap/kr.txt – Korean IPs and Domains

- ./vulmap/hh.txt – Various Countries IPs and Domains

- ./vulmap/wb.txt – Iranian IPs and Domains

- ./vulmap/ww.txt – Iranian IPs and Domains

- ./weaver_exp/uu.txt – Chinese IPs and Domains

- ./WebLogicScan/target.txt – Iranian IPs and Domains

- ./WebLogicScan/kk.txt – South Korean IPs and Domains

- ./tt.txt – Saved HTTP request to a Thai police website

Of the targeted countries China, South Korea, and Iran were most frequently observed.

Industries

While we note the following industries below, we assess the threat actor was not specifically targeting by industry in this case.

- Government

- Education

- Health

- Logistics

## Infrastructure

The open directory we initially investigated had the following attributes:

8000/opendir Server: SimpleHTTP/0.6 Python/3.8.10 28888/mitmproxy SSL Cert Issuer: CN=mitmproxy, O=mitmproxy SSL Cert Subject: CN=163.53.216.157 JA3S: 15af977ce25de452b96affa2addb1036 55918/SSH Fingerprint SHA256: 1192d660e36e9b6f671a22a1ed1adb50f752ca986885ecfffdbbf3967e8ff9c1 SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.11 60000/Viper SSL Cert Issuer: C=CN, ST=0d72da0c, L=0d72da0c, O=0d72da0c, OU=0d72da0c, CN=0d72da0c SSL Cert Subject: C=CN, ST=d1d38ec9, L=d1d38ec9, O=d1d38ec9, OU=d1d38ec9, CN=d1d38ec9 JA3S: 475c9302dc42b2751db9edcac3b74891

The opendir had the following in the root directory:

When searching in Censys for further hosts with the same SSH Fingerprint, there were eight results all with similar open services.

services.ssh.server_host_key.fingerprint_sha256: 1192d660e36e9b6f671a22a1ed1adb50f752ca986885ecfffdbbf3967e8ff9c1

Based on the fingerprints of these servers and shared opendir content, we assess the following IP’s were used to proxy the threat actor’s back end infrastructure at various points in time:

43.228.89.245 43.228.89.246 43.228.89.247 43.228.89.248 103.228.108.247 115.126.107.244 116.212.120.32 163.53.216.157

All of the IP addresses were associated with the same ISP, Forewin Telecom Group Limited. While we did not have access to the entire system, we did find ‘.viminfo’ register artifacts which suggest these IP’s were specifically added through VIM to a file on the device:

When reviewing the Viper access logs, the initial service was listening on the domain fgfg.bcfnwg.cc:60000 . This domain was registered with NameSilo on 2023-02-07T16:16:06Z:

Based on the access and usage of Viper in the access.log of the server, we identified 101.36.124.183 as the IP address the threat actor was using at the time.

When pivoting on that IP, it appears to be a proxy.

f8x

f8x is a setup script that the The DFIRReport has observed on various threat actor controlled infrastructure. It is used to automate the setup of infrastructure by installing security tooling and dependencies.

In this case the threat actor simply curl-ed the script from f8x.io and executed it with the -all and -viper switch

curl -o f8x https://f8x.io/ chmod +X f8x bash f8x -all bash f8x -viper

According to the GitHub documentation, there are several other options that can be supplied such as:

## Adversary

Based on the tooling and evidence available, the threat actor is Chinese speaking.

The telegram channel mentioned in the modified ransom note is hXXps://t.me/You_Dun which was created on 09 January 2024 (since been deleted):

Just as many other threat actors claim to be innocent “pentesters”, this group is no different:

Reviewing their telegram channel, they post their various escapades such as defacements and data leaks.

The administrator of this group as seen above goes by “EVA” and the telegram tag @YD099 (ID: 6392878812)

Further analysis of the telegram group mentioned 2 more related groups related hxxps://t.me/You_Dun:

- hxxps://t.me/You_Dun888

- hxxps://t.me/juxingchuhai

You_Dun888 is a group channel that claims to provide various services including penetration testing, selling data, DDOS and more.

Proofs of defacements and compromises also are present in the You_Dun888 group going by the name “Dark Cloud Shield”.

The Telegram channel @xuanshang posted advertisement to their chat which included similar wording as the other channel’s bios and a link to You_Dun777 (since been deleted).

## Diamond Model

## Indicators

### Atomic

43.228.89.245 43.228.89.246 43.228.89.247 43.228.89.248 103.228.108.247 115.126.107.244 163.53.216.157 116.212.120.32

### Computed

SSH Fingerprint for OpenDir SHA256: 1192d660e36e9b6f671a22a1ed1adb50f752ca986885ecfffdbbf3967e8ff9c1 红队版.zip (Cobalt Strike Kit) SHA256: b94d9412764529f264433c39b6043d43b96e824d016f40a5a38e26771374171f SHA1: 56bd833178c08baedb0a6f51c957a0cc8e6f9298 MD5: 8c4d6f6c6db273d79a7c46b623e515e3 xray_linux_amd64 SHA256: 6e3c5f8444040e5982da9990cbb9d0ce66b7272a3e6804139e7cbe3083459035 SHA1: 89b12a33628d5939bcedb53c908df9dbb24fe910 MD5: 77915c856012baa7cd554041e7315317 YeNoenXSQB.exe SHA265: fa301a12655598b9266a8315ac7f48da4f79ed4ea39273e57ac08b8c66b6fced SHA1: b7b0a37aee514c735913bfa8826faa4bbfc14556 MD5: 2cc31da03228b31dae0a05065e9e1506 f8x (ffffffff0x) SHA265: 206ac51c01604267c04f0966cdc685fd9ade42dd8d0698df639b06a0ed19377f SHA1: 2787930ac016783837e7d11903cd84c055356e4c MD5: 0658d07948a053da265ef693a64e9626 LB3.exe (LockBit) SHA265: 07104f9be906e62be7539e4f81d980dddb480d64dce204c199a2afe5a0bc3367 SHA1: f8ccc2503052eceebd5311a8b74dc197a4e9f68a MD5: c8033ec30b55a46ce7daf9d7d9b6b596 TaoWu Cobalt Strike Kit - MD5 f87afacff9c44b94db109e3e956a4b33 taowu-cobalt-strike-master/script/0803.exe 98d006fbea457ec76243cab8f7f6631a taowu-cobalt-strike-master/script/360bowser.exe 8cda17f33d42754721ef2a87f3b5a984 taowu-cobalt-strike-master/script/ATPMiniDump.exe bfd92dedefe429205a635a38096429a2 taowu-cobalt-strike-master/script/BrowserGhost.exe 201ebb467e02e63242ab4e0a21576f52 taowu-cobalt-strike-master/script/BypassAddUser.exe 67a604d24c2478b19d80032dbc5a3d41 taowu-cobalt-strike-master/script/CVE-2020-0796.x64.dll 13b2df26ffb467142106040cfa98e8dd taowu-cobalt-strike-master/script/CVE-2021-1675.x64.dll 251fe0878c16d68aa88405994c74a8d8 taowu-cobalt-strike-master/script/ClearnEventRecordID.ps1 ee28414ff1bcbb3a6efd9a08f7baaf51 taowu-cobalt-strike-master/script/ClearnIpAddress.ps1 1d0d8fb9803967c5b23c2e519e4c2cfe taowu-cobalt-strike-master/script/ClearnTempLog.ps1 5562f8aa216f87142dccc080506e2ad2 taowu-cobalt-strike-master/script/CredPhisher.exe f481acde58892cc1af01a009e73c3ae5 taowu-cobalt-strike-master/script/DecryptAutoLogon.exe fed5394f1b2a425d760e5ac9ee90d851 taowu-cobalt-strike-master/script/DecryptTeamViewer.exe f41eed0c700eb6961310b19449595af3 taowu-cobalt-strike-master/script/EfsPotato.exe f3ac9fb21d91fd283d6762a09fee8776 taowu-cobalt-strike-master/script/EncryptedZIP.exe a65b02f7ee85fec8580d69361df16350 taowu-cobalt-strike-master/script/FakeLogonScreen.exe bf1bbfd14c7cf3e72458a173c8e7f5a4 taowu-cobalt-strike-master/script/FullPowers.dll 282b368bc42f506b58b83ae16e200544 taowu-cobalt-strike-master/script/GPSCoordinates.exe 4f887be6011ea3e3d1b6afc41da2227d taowu-cobalt-strike-master/script/Gopher.exe 9cd740d0de919819ad00f73665c40500 taowu-cobalt-strike-master/script/InternalMonologue.exe 38d1bf58e34b68a8836b352af978d6a1 taowu-cobalt-strike-master/script/Invoke-EternalBlue.ps1 a63c52d46cb33e57f1f17beaa733ea65 taowu-cobalt-strike-master/script/Invoke-MS16032.ps1 1dc27c44d74bf619aaf496963dfd67d6 taowu-cobalt-strike-master/script/Invoke-MS16135.ps1 894aba8dfa538ba99c1453066824cc63 taowu-cobalt-strike-master/script/JuicyPotato.x64.dll 28e874a7107b7e08e79e6efc63602609 taowu-cobalt-strike-master/script/JuicyPotato.x86.dll 34fb77cd8902076f55071b218c494f77 taowu-cobalt-strike-master/script/KillEvenlogService.ps1 2c2ddfb749aeeca32a9fd5fc20324b47 taowu-cobalt-strike-master/script/LPE_Reflect_Elevate.x64.dll 3aa57bf8e7ea973cc793745de79033fa taowu-cobalt-strike-master/script/Ladon.exe 6b7bba769db3701e13214cb70ca5a54d taowu-cobalt-strike-master/script/Ladon1.exe d0929362057fbcb2a9971222ef6db973 taowu-cobalt-strike-master/script/ListAllUsers.ps1 fd18c734fa25bbacf0b7a6331d404126 taowu-cobalt-strike-master/script/ListLogged-inUsers.ps1 e8a59e21ab61a7d615a7f8a407d72712 taowu-cobalt-strike-master/script/ListRDPConnections.exe 13508e34428cf9611c8d7904b532e1b2 taowu-cobalt-strike-master/script/LocalSessionManager.ps1 50c0e5c847f4a66fbcdda53e6555267f taowu-cobalt-strike-master/script/MaceTrap.exe 80926c91b6d82c4ad7f915bafa70e8d3 taowu-cobalt-strike-master/script/MiniDump.exe b8016d2f778b9c4c7d7a6347608fb18c taowu-cobalt-strike-master/script/Net-GPPPassword.exe da296f6861a17738358b043ecc823bdc taowu-cobalt-strike-master/script/NoAmci.exe b175bb17e17ba2f6a8826c9c90cb9c7e taowu-cobalt-strike-master/script/NoPowerShell.exe 4332225f7e3672c16f705a779dc360f5 taowu-cobalt-strike-master/script/RdpThief_x64.tmp 976df0f9c9319c50a5ac20f4643dec4c taowu-cobalt-strike-master/script/Recon-AD-AllLocalGroups.dll 7e65a509b90b6e9fa0963803020280d9 taowu-cobalt-strike-master/script/Recon-AD-Computers.dll 3f6b6935f5820196c69616e6bd8aa684 taowu-cobalt-strike-master/script/Recon-AD-Domain.dll 7349fa84c7e2fced4885fea0ef0fec63 taowu-cobalt-strike-master/script/Recon-AD-Groups.dll 66a7733af713c5beff9c76d0b6adbe6d taowu-cobalt-strike-master/script/Recon-AD-LocalGroups.dll c69e7c0bac6b1846fcad05ee7fdd5023 taowu-cobalt-strike-master/script/Recon-AD-SPNs.dll bbee3a7a828af2a936e3e9a2931f2022 taowu-cobalt-strike-master/script/Recon-AD-Users.dll fb5fbc7c6b56a7a491532581faef5ee1 taowu-cobalt-strike-master/script/ReflectiveDll.x64.dll 5ed0803ea91968c87994280f6432d43c taowu-cobalt-strike-master/script/RegRdpPort.ps1 cdaa0eda10dce813a0def8be3a669825 taowu-cobalt-strike-master/script/SPNSearcher.exe 29321457a14c9722d76c9134781cf328 taowu-cobalt-strike-master/script/SafetyKatz.exe 42de98c28dae64d104dcccc1d72e7834 taowu-cobalt-strike-master/script/Seatbelt.exe 8885ae88e244f6bcf3089eba94e2cc87 taowu-cobalt-strike-master/script/SessionGopher.ps1 d4969c3a7d88ad38f885a061bba26752 taowu-cobalt-strike-master/script/SessionSearcher.exe e06b24113cab27ff5a1173fa3f9e1615 taowu-cobalt-strike-master/script/SharPersist.exe 755fa47d4527e9c93433e1887bd871ab taowu-cobalt-strike-master/script/Sharp3389.exe 74f79b71ba72dd55ca261ef789d243d6 taowu-cobalt-strike-master/script/SharpAVKB.exe 205621408b7f84a5f451df233b0b87b1 taowu-cobalt-strike-master/script/SharpBypassUAC.exe 7b5da1d6648103353216a0391638cee8 taowu-cobalt-strike-master/script/SharpChassisType.exe da478e7f17353b01d9ffa53aab0f0528 taowu-cobalt-strike-master/script/SharpCheckInfo.exe 470acd82ade29f1ef29f198027771517 taowu-cobalt-strike-master/script/SharpChromium.exe f04164b15b9530d4b7ada28c1b9042b3 taowu-cobalt-strike-master/script/SharpClipHistory.exe 44bac97f297c86a66b2af33eee7e4d8e taowu-cobalt-strike-master/script/SharpCloud.exe df37fedde5fa9dc9d7a7ea7a87b71e10 taowu-cobalt-strike-master/script/SharpCrashEventLog.exe 6f5764932e177157f307b33649968b5b taowu-cobalt-strike-master/script/SharpDPAPI.exe 6214cc7a0b9491b38a592be4d3032dd1 taowu-cobalt-strike-master/script/SharpDecryptPwd.exe 3cf370a9f29a6b7ea83abac4a3141f26 taowu-cobalt-strike-master/script/SharpDecryptPwd2.exe 34f645d8bf012f8f4965c1cd8857921f taowu-cobalt-strike-master/script/SharpDir.exe 98bacbfcc39e0dee46a0092699a56832 taowu-cobalt-strike-master/script/SharpDirLister.exe 51cf67846561fe279e6e1c4bda712dbe taowu-cobalt-strike-master/script/SharpDomainSpray.exe 3a273a07749d17b50a4ec6387a54e2cc taowu-cobalt-strike-master/script/SharpDoor.exe 95fec2925ea9fa4a5181d491ea07f5e5 taowu-cobalt-strike-master/script/SharpDump.exe 1ef929169b3309a01e850c6ff4e0064f taowu-cobalt-strike-master/script/SharpEDRChecker.exe 122413ef9a5f642703b1e8385c5dbad1 taowu-cobalt-strike-master/script/SharpEventLog.exe 5b1c1007de5a2864d24276e3b1d293da taowu-cobalt-strike-master/script/SharpExcelibur.exe 03ee7c0c3822822b5e2373c4f532545a taowu-cobalt-strike-master/script/SharpExec.exe a4f9bfa588427735f80e749ee341e819 taowu-cobalt-strike-master/script/SharpGPOAbuse.exe fe4f202c9595f6242903fbad0611eebb taowu-cobalt-strike-master/script/SharpGetTitle.exe f6c2d2cc1e2016fddb7654822411ab2b taowu-cobalt-strike-master/script/SharpHide.exe 71eaf81214239027d5385a61e3917ab2 taowu-cobalt-strike-master/script/SharpHound.exe 56892df95d1b9d78261587d5080630d1 taowu-cobalt-strike-master/script/SharpLocker.exe ea381b3247b6c2ed4d39973eca62669f taowu-cobalt-strike-master/script/SharpMiniDump.exe bddf6c8e9a8229ed7667e3e1bb33aac9 taowu-cobalt-strike-master/script/SharpNetCheck.exe 6181e5196eaeb14ec9ff798b43300ceb taowu-cobalt-strike-master/script/SharpOXID-Find.exe 56c33b2a06e3d68fe4e8b9421b36e902 taowu-cobalt-strike-master/script/SharpSCshell.exe 09e471f71d1d66f5c8b407dfadce8ce5 taowu-cobalt-strike-master/script/SharpSQLDump.exe e390dbe577164988694d7aab5235e1af taowu-cobalt-strike-master/script/SharpSQLTools.exe ccf2d0a5bbe52e80775900a2e18fe70f taowu-cobalt-strike-master/script/SharpShares.exe d06c2c02133b810eb0111c6b4e34e940 taowu-cobalt-strike-master/script/SharpSpray.exe 1d1478fddbf9b4128a4ecb85238c87b7 taowu-cobalt-strike-master/script/SharpSpray1.exe aca267b9a1ab0c97b8f88773d356220c taowu-cobalt-strike-master/script/SharpStay.exe 3f1abaf273e3ce16265a3f639945ff3e taowu-cobalt-strike-master/script/SharpTask.exe dc443ffed5b96bee78ca2309d0f8fdca taowu-cobalt-strike-master/script/SharpWeb.exe fc98ec23880eea7f0f701c5d66fa6892 taowu-cobalt-strike-master/script/SharpWebScan.exe 1ca3ca7750b0ce2095a2f99d5b33177a taowu-cobalt-strike-master/script/SharpWifiGrabber.exe e23e588319f82d826d3bf2c9fa4d1cba taowu-cobalt-strike-master/script/SharpXDecrypt.exe bf2144fcf764bc3e5337fa3d2253232b taowu-cobalt-strike-master/script/SharpZeroLogon.exe e73ca08a6937b95d8d5a90a33fcbc5c1 taowu-cobalt-strike-master/script/SharpZip.exe 2ac4edf1110124560aeec330de7f8328 taowu-cobalt-strike-master/script/Shhmon.exe 1de240d44557e7497ad1a1e144077805 taowu-cobalt-strike-master/script/SolarFlare.exe 76fca31c99b232be1ec92d6b5762d97b taowu-cobalt-strike-master/script/SpoolTrigger.x64.dll ad9382b2e7214d350f622f360f300ccf taowu-cobalt-strike-master/script/SpoolTrigger.x86.dll a145f3345a4a2fd23b49dd299d0c3a83 taowu-cobalt-strike-master/script/Stealer.exe 99d639417aa2a0ed7d188c85ea9ece23 taowu-cobalt-strike-master/script/StickyNotesExtract.exe 624007937ba4931486c9bba5bb695688 taowu-cobalt-strike-master/script/SweetPotato.exe 2d9777a0e299315b23d08955389154ed taowu-cobalt-strike-master/script/Telemetry.exe 817ddd444915bda25a5e81c1faa8978e taowu-cobalt-strike-master/script/Telemetry3.5.exe ceb337687402e19efdf57264b2682d08 taowu-cobalt-strike-master/script/WMIHACKER.vbs 9c444a9c1d75cbd07798110eeca1c3ce taowu-cobalt-strike-master/script/Watson.exe 2a449b2b65686a72525c98622e5bade7 taowu-cobalt-strike-master/script/WeblogicRCE.exe 98d8bbeac624e77323f45256f6c87369 taowu-cobalt-strike-master/script/WireTap.exe 1c96ec806a6e0a54cd7e0e78bb75eeb7 taowu-cobalt-strike-master/script/add-admin.exe 3febcc80ab5ea418ef3e2103fe92d2e0 taowu-cobalt-strike-master/script/blocketw.exe 4b1fdcf5cfa616fcaf411f3bff9acd75 taowu-cobalt-strike-master/script/blue.exe b3ec75c3a7454a096c65a99a0eb3073c taowu-cobalt-strike-master/script/certexp.exe d7b669038c4860f1e3be02d389ed52d7 taowu-cobalt-strike-master/script/chfs.exe 827cdfb4c1f1169c21ba84a194a70a0f taowu-cobalt-strike-master/script/crack.exe c8c886ca25a381b22343a397f80a35c1 taowu-cobalt-strike-master/script/cve-2014-4113.x64.dll 159801144740381f30e0ae4dfbfd62e6 taowu-cobalt-strike-master/script/cve-2014-4113.x86.dll e0e467f5597828a1d3c8abdbde8b6f17 taowu-cobalt-strike-master/script/cve-2015-1701.x64.dll dafc44bc1e488e1108449e39bcb147e1 taowu-cobalt-strike-master/script/cve-2015-1701.x86.dll e79195ab1fda13edac7a000cf8742802 taowu-cobalt-strike-master/script/cve-2016-0051.x86.dll 600c41b3a161c5d2019767c87a7889ce taowu-cobalt-strike-master/script/dazzleUP_Reflective_DLL.x64.dll 5e4319826d24eacce3ca0738885722f3 taowu-cobalt-strike-master/script/dis_defender.exe d035f1c73e746553323924e3b61b3fb2 taowu-cobalt-strike-master/script/encode b5fac96201ab68d8a0c29eb8df6596e7 taowu-cobalt-strike-master/script/encode.exe 58bbb92c36ee75183d2257b2ae64a0c2 taowu-cobalt-strike-master/script/hack-browser-data.exe 0e51c36a7c45a2dea751fcb692102a6b taowu-cobalt-strike-master/script/iox.exe 73255c8357afd671c2256360d0be69cd taowu-cobalt-strike-master/script/lazagne.exe 5bd9a0f8a2f63622eb0d8bba2fb70fbb taowu-cobalt-strike-master/script/napwd.exe 5bd9a0f8a2f63622eb0d8bba2fb70fbb taowu-cobalt-strike-master/script/navicatpwd.exe bb15b1dbc80dae1b9ac51455c72b44b4 taowu-cobalt-strike-master/script/noNetApiAdd.exe deca5d20a7fb145e288f39d4e4bd5042 taowu-cobalt-strike-master/script/rpcscan.dll dbff25033593278d05d2eee6cb9f44a6 taowu-cobalt-strike-master/script/scout.exe 7c42df21e22b9c6cc87b2eebf219c01d taowu-cobalt-strike-master/script/scrying.exe 34daed0b12685ee391660f658b5980b5 taowu-cobalt-strike-master/script/sharpwmi.exe 7728fc3821a7ff9c994258a36812e250 taowu-cobalt-strike-master/script/temp.exe dc6606879efe07595dfd968f8edf82f7 taowu-cobalt-strike-master/script/user.exe 575b5020c27e3d7b14fee8b2b33c44e3 taowu-cobalt-strike-master/script/x64/PrintSpoofer.dll 108da75de148145b8f056ec0827f1665 taowu-cobalt-strike-master/script/x64/PrintSpoofer.exe bd0f451c578f5a0b6c55e39e124db2fa taowu-cobalt-strike-master/script/x64/bypass.exe d0139fda662f3ca949dd335c30573fa2 taowu-cobalt-strike-master/script/x64/frpc.exe 9b0e4652a0317e6e4da66f29a74b5ad7 taowu-cobalt-strike-master/script/x64/fscan.exe a5a74d73fbf4a6f0b75f074de316277e taowu-cobalt-strike-master/script/x64/nc.exe 07edf20febc120edf731c4dc0d4d3b0b taowu-cobalt-strike-master/script/x64/npc.exe 5047fc7502bc9520fd2b9c26e8cbbd82 taowu-cobalt-strike-master/script/x86/PrintSpoofer.dll 2a74db17b50025d13a63d947d8a8f828 taowu-cobalt-strike-master/script/x86/PrintSpoofer.exe 11c1ffdff16dd42e33c8014f2b5360cd taowu-cobalt-strike-master/script/x86/bypass.exe 03f45692db10fe291de65f15ca9761af taowu-cobalt-strike-master/script/x86/frpc.exe 3505308cf3fd01398f1e4d1974b2438e taowu-cobalt-strike-master/script/x86/fscan.exe 8fa2d7a60d5bc36ead30c61d7b3608e7 taowu-cobalt-strike-master/script/x86/index.html f860286242afc5151d9ff68f0c7b8a56 taowu-cobalt-strike-master/script/x86/npc.exe Landon Cobalt Strike Kit - MD5 1f040434a5bbaa855822ab4bed5fde2b Ladon911/ChatLadon.exe 9055f7437681be39b865326fad31cfd4 Ladon911/Ladon-cn.cna 689aa7368a41586690d84a1a9d1b158a Ladon911/Ladon.ps1 59a5445907ea5f4e6db1cc4d47a0417e Ladon911/Ladon911.exe 31aa0419b32bf3b3228157f91c1a21fd Ladon911/LadonExp.exe 2242303952f6fb570b2484974b7771ba Ladon911/LadonGUI.exe 813fb29abbe42068283efaf665bea1c7 Ladon911/LadonShell.exe 6153ce694983cf7e1c12e875d944e7e7 Ladon911/LadonStudy.exe 486015a44a273c6c554a27b3d498365c Ladon911/Newtonsoft.Json.dll

## MITRE ATT&CK

Application Layer Protocol - T1071 Data Encrypted for Impact - T1486 Exploitation for Privilege Escalation - T1068 Exploit Public-Facing Application - T1190 Ingress Tool Transfer - T1105 Vulnerability Scanning - T1595.002 Web Protocols - T1071.001 Wordlist Scanning - T1595.003

Internal case #27241

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
