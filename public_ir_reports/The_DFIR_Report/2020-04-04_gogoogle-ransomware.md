---
title: "GoGoogle Ransomware - The DFIR Report"
source_url: "https://thedfirreport.com/2020/04/04/gogoogle-ransomware/"
published: "2020-04-04T19:18:33+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2020-04-04_gogoogle-ransomware.html"
---

# GoGoogle Ransomware - The DFIR Report
An attacker logged into the honeypot from 93.174.95[.]73, disabled security tools, dropped their toolkit and started recon. Recon was quickly followed by an onslaught of password dumping tools such as Mimikatz, Lazagne, rdpv, and more. After the attacker dumped credentials they moved laterally to multiple machines using Network Port Scanner. Minutes later the attacker focused in a Domain Controller and started deploying ransomware.

## Interesting Artifacts

There were a bunch of artifacts dropped during this compromise. Most of these are password dumping tools with the exception of !start.cmd and Advanced IP Scanner.

The !start.cmd script appears to use the above artifacts to dump credentials from the machine. The script is written to handle 64 and 32 bit systems as it checks the processor architecture before running each of the password dumping tools. The first half of the script runs Mimikatz , Lazagne , BulletsPassView, netpass, PasswordFox, SniffPass, and WirelessKeyView.

The second half of the script runs ChromePass, Dialupass, iepv, mailpv, mspass, OperaPassView, pspv, PstPassword, rdpv, RouterPassView, VNCPassView, and WebBrowserPassView before deleting the mimikatz files. The artifact can be downloaded here .

One thing to notice here is the folder named passrecpk. After doing some further research we believe this folder most likely correlates to the free NirSoft toolpack named passrecenc.zip . Most of the NirSoft tools above are in passrecenc.zip.

The next artifact is a Mimikatz parser. The goal of this script is to parse out the Mimikatz output so its easier for the actor to use passwords/NTLM. We saw the actors open up the Passwords.txt file which included username:password for logged in users. The artifact can be downloaded here .

Another interesting artifact is Remote Desktop PassView (rpv.exe) created by NirSoft which reveals passwords stored in .rdp files. This is a great example of why you shouldnt store passwords in rdp files.

Example of the PowerShell scripts and other recon elements executed:

We were not able to acquire these files but here are our thoughts:

- lubrute.ps1 – We believe this script was used to brute force local accounts.

- adbrute.ps1 – We believe this script was used to brute force AD accounts.

- Find-Pass.ps1 – We believe this script was used to run mimikatz and the other password dumping tools.

- NetADPC.ps1 – We believe this script launched Network Port Scanner and helped with RDP connections.

The ransomware was deployed in a manual fashion requiring the actor to RDP to each machine that Network Port Scanner found.

The specific executable looks to be new, currently identified as GoGoogle by id-ransomware .

bild.exe|9330544a69b499f9b2ea79fd5a57bccc
9330544a69b499f9b2ea79fd5a57bccc
17cf9b71e0f8cf3068977c670499ed816e1b65ab
8805ce23c95a5049ca6d9678f419848b3ace3f1a0cdd36d3867d7d827ab5f4e8

Looking at the binary itself we can see that much of the code is written using Go and the compiler/creator used the name demon777.

Before encrypting files the ransomware uses many windows utilities such as WMI, taskkill, WEVTUTIL, and net.exe to kill processes and remove logs from the system.

Example of Logs being cleared:

Example of processes being killed:

Here is a long list of services killed before the ransomware encryption process starts:

AcronisActiveProtectionService,AcronisAgent,AcronisMonitoringService,AcronisZmqGw,AcrSch2Svc,AdobeActiveFileMonitor10.0,AdobeARMservice,AdobeFlashPlayerUpdateSvc,AdobeUpdateService,ADWS,AGMService,AGSService,AmazonSSMAgent,AMPPALR3,AMS,AnyDesk,Apple,ARSM,ASM,aspnet_state,Atenet.Service,Backupper,BASupportExpressSrvcUpdater_LOGICnow,BASupportExpressSrvcUpdater_N_Central,BASupportExpressStandaloneService_LOGICnow,BASupportExpressStandaloneService_N_Central,BayanService,bkserv,BTHSSecurityMgr,btwdins,CcmExec,Check_MK_Agent,CIMnotify,Cissesrv,ClickToRunSvc,CodeMeter.exe,CpqNicMgmt,CpqRcmc3,cpqvcagent,CqMgHost,CqMgServ,CqMgStor,cramsrv,crserv,crsyslog,dbex,DESIGO,discagt,disvc,dlhm,DPMClientService,DpmCPWrapperService,DPMRA,DriveLock,dwmrcs,Dyn,Ec2Config,EcuRemote,EFI,ekrn,ekrnEpfw,EpsonBidirectionalService,EpsonScanSvc,FileOpenManagerSvc,firebirdguardiandefaultinstance,FirebirdGuardiansgsSFBServer,FirebirdServersgsSFBServer,FlowExport,FontCache3.0.0.0,fvstermiser,HealthService,hist32,hMailServer,HostControllerService,HPSIService,HPWMISTOR,IAStorDataMgrSvc,ibmiasrw,IISADMIN,iPod,jhi_service,LavasoftTcpService,LicSvrM,MacriumService,Microsoft.Crm.VssWriterService.exe,MMAExtensionHeartbeatService,MMS,MSComplianceAudit,MSCRMAsyncService,MSCRMAsyncService$maintenance,MSCRMMonitoringService,MSCRMSandboxService,MSCRMUnzipService,MSDTC,MsDtsServer100,MSExchangeAB,MSExchangeADTopology,MSExchangeAntispamUpdate,MSExchangeCompliance,MSExchangeDagMgmt,MSExchangeDelivery,MSExchangeDiagnostics,MSExchangeEdgeSync,MSExchangeFastSearch,MSExchangeFBA,MSExchangeFDS,MSExchangeFrontEndTransport,MSExchangeHM,MSExchangeHMRecovery,MSExchangeImap4,MSExchangeIMAP4BE,MSExchangeIS,MSExchangeMailboxAssistants,MSExchangeMailboxReplication,MSExchangeMailSubmission,MSExchangeMonitoring,MSExchangeNotificationsBroker,MSExchangePop3,MSExchangePOP3BE,MSExchangeProtectedServiceHost,MSExchangeRepl,MSExchangeRPC,MSExchangeSA,MSExchangeSearch,MSExchangeServiceHost,MSExchangeSubmission,MSExchangeThrottling,MSExchangeTransport,MSExchangeTransportLogSearch,MSExchangeUM,MSExchangeUMCR,msftesql,Exchange,MSMQ,MSOLAP$SQL,MSSQL$CRMVIEW,MSSQL$CRMVIEW2,MSSQL$ISARS,MSSQL$MSFW,MSSQLFDLauncher,MSSQLLaunchpad$SQLEXPRESS,MSSQLSERVER,MSSQLServerADHelper100,MSSQLServerOLAPService,MySQL,MySQL55,NetPipeActivator,NetTcpActivator,NetTcpPortSharing,NGCLIENT,ntfsvc,nvsvc,NVWMI,OpenVPNAccessClient,OracleMTSRecoveryService,OracleOraDb11g_home1ClrAgent,OracleOraDb11g_home1TNSListener,OracleServiceINFAORCL,ose,osppsvc,PCoIPAgent,PCoIPArbiterService,PCoIPPrintingSvc,PolicyAgent,ProLiantMonitor,QBCFMonitorService,QBFCService,QBPOSDBServiceV12,QBVSS,QuickBooksDB1,QuickBooksDB10,QuickBooksDB11,QuickBooksDB12,QuickBooksDB13,QuickBooksDB14,QuickBooksDB15,QuickBooksDB16,QuickBooksDB17,QuickBooksDB18,QuickBooksDB19,QuickBooksDB2,QuickBooksDB20,QuickBooksDB21,QuickBooksDB22,QuickBooksDB23,QuickBooksDB24,QuickBooksDB25,QuickBooksDB3,QuickBooksDB4,QuickBooksDB5,QuickBooksDB6,QuickBooksDB7,QuickBooksDB8,QuickBooksDB9,RdAgent,Realtek11nCU,ReportServer,ReportServer$ISARS,ReportServer$SQL,RtkAudioService,SageEvolutionEcommService,SDRSVC,SearchExchangeTracing,SentinelKeysServer,SentinelProtectionServer,SentinelSecurityRuntime,Service,ShadowProtectSvc,ShutdownMon,SkyLightWorkspaceConfigService,SNMPTRAP,SoftwareProxyJavaChecker,SolarWindsAgent64,SPAdminV4,Spooler,sppsvc,SPSearch4,SPTimerV4,SPTraceV4,SPUserCodeV4,SPWriterV4,SQLAgent$ISARS,SQLAgent$MSFW,SQLBrowser,SQLSERVERAGENT,SQLServerReportingServices,SQLTELEMETRY$SQLEXPRESS,SQLWriter,sshd,Stxhd.HostAgents.HAService,swprv,sysdown,SysMgmtHp,TdmService,TeamViewer,TeamViewer1,TeamViewer10,TeamViewer11,TeamViewer12,TeamViewer2,TeamViewer3,TeamViewer4,TeamViewer5,TeamViewer6,TeamViewer7,TeamViewer8,TeamViewer9,Tomcat8Testing,Tomcat9,tvnserver,UltraViewService,UNS,uvnc_service,vcsFPService,VeeamCatalogSvc,VeeamCloudSvc,VeeamDeploySvc,VeeamMountSvc,VeeamNFSSvc,VeeamTransportSvc,VGAuthService,VisualSVNServer,VMAuthdService,vmicheartbeat,vmickvpexchange,vmicrdv,vmicshutdown,vmictimesync,vmicvss,VMnetDHCP,VMTools,VMUSBArbService,VMware,VMwareHostd,VSS,wbengine,WindowsAzureGuestAgent,WindowsAzureNetAgentSvc,WindowsAzureTelemetryService,wlidsvc,WMPNetworkSvc,Wrmserv,wsbexchange,WSearch

The ransom note left behind left an ID and used an email address as outreach to the attackers using the qq.com service.

Contact was made with the ransomer and they asked for 2 BTC (13,400 USD at time of writing). It is possible that this was per ransomed device, but the lab was reset with only a single ransom note collected before indicators were removed.

While leaving the ransom note, it appears the actors were planting the capability to potentially return in the future should the systems not receive a full wipe using a Utilman.exe backdoor to allow system cmd access at the login screen.

## Summary

These attackers moved fairly fast as they were able to go from zero to installing ransomware on 5+ machines in just over an hour. There were a ton of artifacts dropped by this attacker which were mostly NirSoft tools but the attackers did have a few of their own scripts. The attackers ran a few commands that may be easy to detect such as enabling network discovery, replacing Utilman with cmd, clearing logs and killing a bunch of services such as TeamViewer1. We found some interesting strings in the bild binary which could make for a good Yara rule. If you have any further questions please feel free to reach out to us via the Contact Us page.

Enjoy our report? Please consider donating $1 or more to the project using Patreon . Thank you for your support!

## IOCs

In the future IOCs will be posted to MISP but right now you can find them on pastebin .

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
