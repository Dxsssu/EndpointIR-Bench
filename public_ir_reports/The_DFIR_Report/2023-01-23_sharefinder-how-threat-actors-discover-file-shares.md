---
title: "ShareFinder: How Threat Actors Discover File Shares - The DFIR Report"
source_url: "https://thedfirreport.com/2023/01/23/sharefinder-how-threat-actors-discover-file-shares/"
published: "2023-01-23T01:11:17+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2023-01-23_sharefinder-how-threat-actors-discover-file-shares.html"
---

# ShareFinder: How Threat Actors Discover File Shares - The DFIR Report
Many of our reports focus on adversarial Tactics, Techniques, and Procedures (TTPs) along with the tools associated with them. After gaining a foothold in an environment, one challenge for all threat actors is discovery. One common target for discovery is the enumeration of network shares. Network shares are common targets of an intrusion to facilitate later actions on objectives such as data exfiltration or targets for ransomware encryption.

For this reason, it is important for defenders to be able to detect and proactively hunt for signs of any unauthorized network share discovery in order to mitigate the impacts of data exfiltration and anything that may follow it, such as ransomware. In this report, we’ll be profiling a commonly used tool for discovering shares in a network, the PowerShell script Invoke-ShareFinder, which we will call ShareFinder throughout the report. This publication will delve into the specific characteristics of the underlying mechanism Invoke-ShareFinder uses to enumerate network shares. This is vital for defenders to understand to detect Invoke-ShareFinder and similar tools in their environments.

## The DFIR Report Services

- Private Threat Briefs : Over 20 private reports annually, such as this one but more concise and quickly published post-intrusion.

- Threat Feed : Focuses on tracking Command and Control frameworks like Cobalt Strike, Metasploit, Sliver, etc.

- All Intel : Includes everything from Private Threat Briefs and Threat Feed, plus private events, long-term tracking, data clustering, and other curated intel.

- Private Sigma Ruleset : Features 100+ Sigma rules derived from 40+ cases, mapped to ATT&CK with test examples.

- DFIR Labs : Offers cloud-based, hands-on learning experiences, using real data, from real intrusions. Interactive labs are available with different difficulty levels and can be accessed on-demand, accommodating various learning speeds.

Contact us today for a demo!

## Analysts

Report by @iiamaleks

Reviewed by @samaritan_o

## What is Invoke-ShareFinder?

ShareFinder has been a common theme in our reports and has generally been paired with both enumeration of network resources and exfiltration of data. In the past year, we have reported on it being used in around 40% of our reported intrusion cases .

ShareFinder was originally part of the PowerView module of the PowerSploit framework . However, now it has been included in various other projects and is in wide use across both red teams and many threat actors. Throughout 2022, we had multiple cases that featured ShareFinder, including:

- https://thedfirreport.com/2022/11/28/emotet-strikes-again-lnk-file-leads-to-domain-wide-ransomware/

- https://thedfirreport.com/2022/11/14/bumblebee-zeros-in-on-meterpreter/

- https://thedfirreport.com/2022/09/26/bumblebee-round-two/

- https://thedfirreport.com/2022/08/08/bumblebee-roasts-its-way-to-domain-admin/

- https://thedfirreport.com/2022/04/04/stolen-images-campaign-ends-in-conti-ransomware/

In these cases, ShareFinder had been observed being directly executed on an endpoint using Powershell. The example below demonstrates this behavior, in which the threat actor has taken steps to save the result of the “ Invoke-ShareFinder -CheckShareAccess ” command to a txt file named shares:

Invoke-ShareFinder -CheckShareAccess -Verbose | Out-File -Encoding ascii C:\ProgramData\shares.txt"

We can see from the Conti leaks , that the Conti threat actors use this method, but slightly change the output name .

We also see similar information on ShareFinder as part of the “ Fast Guide ” in the Conti leaks .

Another method of execution is making use of the Cobalt Strike built-in proxy functionality to load the script and invoke it.

IEX (New-Object Net.Webclient).DownloadString('http://127.0.0.1:10966/'); Invoke-ShareFinder -CheckShareAccess

The standard ShareFinder script supports the following optional parameters:

| Parameter | Description

| HostList | List of hostnames/IPs to search.

| ExcludeStandard | Exclude standard shares from display (C$, IPC$, print$ etc.)

| ExcludePrint | Exclude the print$ share

| ExcludeIPC | Exclude the IPC$ share

| CheckShareAccess | Only display found shares that the local user has access to.

| CheckAdmin | Only display ADMIN$ shares the local user has access to.

| Ping | Ping each host to ensure it’s up before enumerating.

| NoPing | Ping each host to ensure it’s up before enumerating.

| Delay | Delay between enumerating hosts, defaults to 0

| Jitter | Jitter for the host delay, defaults to +/- 0.3

| Domain | Domain to query for machines.

Please note, this article will focus on the core characteristics produced by ShareFinder. Detection through the above command lines and parameters is possible, however, these parameters are easily changed by anyone with the motivation to do so.

## Network Detection

### SMB Traffic

Detecting ShareFinder, or any SMB related activity, over the network is subject to a lot of false positives if normal SMB activity in the environment is not well understood. It is recommended to have a baseline of the network to be able to differentiate the normal from abnormal in the network.

From a high-level, the traffic produced from the default settings of ShareFinder is rather unique when multiple different attributes are combined. The following table illustrates network activity produced from ShareFinder when executed in an environment:

There are multiple characteristics that can be extracted from this in order to be able to detect the presence of this network share scanning activity:

- Each host is consistently queried for three shares, the IPC$, C$, and ADMIN$ shares.

- User and system created file shares are queried, including a Domain Controllers SYSVOL share and a share named ‘Files’ from a fileserver.

- These network shares are queried during a very short period, in this case, all within two seconds of each other (latency may vary depending on the environment and network topology).

- Lastly, all the network share scanning is originating from a single host, and targeting multiple different other hosts (one to many relationship).

These characteristics, when combined, can be a good indicator that there is software attempting to discover file shares on computers in the network.

Sigma Rule:

https://github.com/The-DFIR-Report/Sigma-Rules/blob/main/rules/network/zeek/zeek_smb_mapping_invoke-sharefinder_discovery.yml

In a worst case, ShareFinder may be executed with parameters such as ExcludeStandard to prevent the querying of the default IPC$, C$, and ADMIN$ shares. Delay and Jitter may be used to slow down the enumeration process so it appears as regular SMB activity. While these options are present, we have seen that many threat actors stick with the default settings.

In a case where most of these default characteristics are disabled, the core TCP connection to port 445 can be relied on. In addition to discovering file shares, SMB/445, is used by threat actors to discover systems and to check if they are online.

The following demonstrates a simple example of a one-to-many relationship between a single host and all the others in the network.

If relying purely on TCP connections, correlation with other indicators that can suggest network share enumeration becomes much more important as TCP connections to 445 alone may also indicate other activity, such as a port scan.

When conducting such an analysis, this may become an exercise to understand if the activity is normal for the host, or if one host connection to many other SMB hosts is not normal for the specific endpoint. One example of likely false positives for this kind of hunt or detection would likely include authorized vulnerability scanner hosts or other network share auditing platforms.

### ICMP Traffic

ShareFinder supports -Ping , which ensures that a host is checked for connectivity via ICMP before connecting to it. The screenshot below demonstrates the one to many relationship of ICMP echo requests from a single host, just as with the SMB traffic in the previous section.

ICMP echo requests alone cannot be used as an indicator of file share discovery, this can also be a characteristic of network discovery software being used for legitimate or illegitimate purposes on the network. However, when paired with the characteristics above, this can further support the conclusion that a system on the network was performing discovery activities.

### LDAP Host Discovery

ShareFinder supports the option of using a host file to scan only specific hosts on the network; however, if this option is not used, it will attempt to get a list of computers from the network via LDAP.

This is done by running a query in the CN of the domain for objects of class Computer . In this case, the various attributes such as dnshostanme , operatingsystem , and servicePrincipalName are queried with a wildcard in order to retrieve all the computer objects from the domain.

(&(&(&(objectClass=Computer)(dnshostname=*))(operatingsystem=*))(servicePrincipalName=*))

Once again, such a broad LDAP query is not an indication by itself that network share discovery is occurring, but only that something on the network is attempting to find a list of computers. An event such as this should be correlated with other activity discussed above in order to conclusively determine if it is the result of network share discovery.

## Event Log Detection

### PowerShell Logging

In the five cases we reported usage of ShareFinder over the past year, each time the usage was initiated by a Cobalt Strike beacon. While on rare occasions you might spy a command line invocation of the script, a better detection location is in PowerShell Module and Script Block logging . Below we have an example of a threat actor’s invocation captured in a Windows Event ID 4103 (Module logging) event from the Microsoft-Windows-PowerShell/Operational event channel.

A potential detection point would be to detect the loading of the ShareFinder module in the 4103 events as demonstrated in the following sigma rule.

https://github.com/The-DFIR-Report/Sigma-Rules/blob/main/rules/windows/powershell/powershell_module/posh_pm_invoke-sharefinder_discovery.yml

This data can also be observed in the 4104 (script block logging) events.

Using these logs we can then include a additional point of detection with the following rule, which could be helpful if a threat actor were to rename the functions in order to try to evade detection:

https://github.com/The-DFIR-Report/Sigma-Rules/blob/main/rules/windows/powershell/powershell_script/posh_ps_invoke_sharefinder_discovery.yml

These methods using the PowerShell event logs will likely be better suited to detection as the specificity precludes the likelihood of false positives, compared to many of the other methods in this report.

### Computer Account Enumeration via LDAP

Just as with the network detection, the specific LDAP query used to get a list of all computer accounts in the Domain can be logged via Event ID 1644 in the Directory Service event source.

Event ID 1644 has the capability to log an entry for each LDAP search made against the Domain Controller, however, this can also produce a lot of noise and result in many unrelated logs. By default Event ID 1644 is not logged and will need to be enabled by an administrator.

Once enabled, the same LDAP query will be found in Event ID 1644 as was seen through the network. In addition, the source host can be seen, along with all the hosts that were provided as a response to the query.

It is important to mention, LDAP queries can be changed and will depend on the implementation of the script or software performing the query. For example, in this case we observe objectClass=computer as the means of filtering for computer accounts. However, this can easily be changed to samAccountType=805306369 to filter for samAccountType that matches the identifier for a computer account.

( & (objectClass=computer) (dNSHostName=*) (operatingSystem=*) (servicePrincipalName=*))

### Object Access Logs

Just as with the network detection, network share access anomalies can also be found via network share auditing logs on the host. Event ID 5145 from the Security event source has the capability to log object access to file shares along with the source.

These logs will need to be aggregated from each endpoint to conduct analysis for any anomalies. In this case, we observe many similar traits as from the network detection:

- Each host is consistently queried for three shares, the IPC$, C$, and ADMIN$ shares.

- User and system created file shares are queried, including a Domain Controllers SYSVOL share and a fileservers Files share.

- These network shares are queried during a very short period, in this case all within two seconds of each other.

- Lastly, all the network share scanning is originating from a single host, and targeting multiple different other hosts (one to many relationship).

The same principle used in the network detection can also be applied to Windows event logs, such as the network share object access Event ID 5145. From the ‘Source Address’ field in Event ID 5145 an investigator can determine the one-to-many relationship; however, once again, further analysis may be required to understand if the detected activity is normal for the environment and host.

An example of a detection using that logic can be found in the following sigma rule:

https://github.com/The-DFIR-Report/Sigma-Rules/blob/main/rules/windows/builtin/win_security_invoke_sharefinder_discovery.yml

## Detection of Other Tools

There are many tools that may overlap with the detection’s discussed in this article, for example, the Find-LocalAdmin script from PowerView has the capability to enumerate endpoints for local administrative privileges and has a similar one-to-many ICMP characteristic as described above.

While we have focused on the most common implementation of ShareFinder, there are various other tools that implement the same features nearly one-for-one. Some of them include:

Python Implementation: https://github.com/p0dalirius/FindUncommonShares

.NET PowerView port: https://github.com/tevora-threat/SharpView/

These can still be detected based on similar activity at the network or object access level; moreover, evidence of execution from the command line or Powershell logs may not be reliable if a threat actor attempts to obfuscate the script or program being used. In general, these detections may also overlap with legitimate software responsible for inventorying assets or performing scans on the network.

## Future of ShareFinder

The ShareFinder PowerShell script will likely continue to be a favorite in the toolbox of threat actors. With the integration of this tool in various frameworks and guides widely distributed among underground forums this tool provides an easy and accessible option for threat actors.

In general, the ability to discover network share resources and quickly move to exfiltrate data from the network is critical to the operation of many threat actors. This core fact will ensure that this technique, whether executed in the form of ShareFinder or another implementation, will continue to be popular.

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
