---
title: "BengalSEO Part 1: Anatomy of the Operation - The DFIR Report"
source_url: "https://thedfirreport.com/2026/08/24/bengalseo-part-1-anatomy-of-the-operation/"
published: "2026-08-24T14:28:41+00:00"
author: "editor"
archived_at: "2026-08-25"
source_html: "2026-08-24_bengalseo-part-1-anatomy-of-the-operation.html"
---

# BengalSEO Part 1: Anatomy of the Operation - The DFIR Report
## Key Takeaways

- In March 2026, a widespread SEO Poisoning campaign leading to malware deployment and tech support scams was identified by the DFIR Report.

- This campaign was attributed to a scam operation operating out of Rajasthan, India, which our team has dubbed BengalSEO

- Two IT Service Provider companies and their owners were identified as the main drivers for the BengalSEO operations.

- This group utilizes its extensive SEO and web development capabilities to create and promote lure pages with multiple Black Hat SEO techniques.

- These lure pages then tie into a sophisticated Traffic Distribution System to direct, track, and filter traffic to payloads and tech support scams.

- This includes deploying a custom malware strain our team has named MayaBot, used to further scam operations.

## The DFIR Report Offerings

Check out our Products here and our Services here . Want a demo, more information on our services, pricing or just want to chat? Get in Touch

Contact us today for pricing or a demo!

## Case Summary

In March 2026, our team identified an SEO poisoning campaign leading to malware deployment and tech support scams. Further research into this campaign revealed a sophisticated and widespread scam operation that has been operating since at least 2015. Our team attributes this operation, with high confidence, to a group of core individuals and IT service providers operating out of Rajasthan, India, which our team tracks collectively as BengalSEO.

Using indicators gathered from the identified SEO poisoning campaign, our team was able to correlate this activity with information posted on scam hunting forums. This discovery led our team to a company named WeConnect Solutions LLC (previously iConnect Soft Solutions LLC), which operates a tech support call center located in Kota, Rajasthan. Additional research into this company allowed our team to identify its core members, history, and links to supporting companies involved in the operation.

A second company named Garage2Global was identified, which had the same owners and operated out of the same office building. Garage2Global advertises itself as a legitimate SEO, Web & Mobile App Development, and Digital Marketing services provider; however, our research uncovered extensive evidence indicating Garage2Global develops malicious web infrastructure used in SEO poisoning campaigns as part of the BengalSEO scam operation.

Our team assesses these two companies and their owners to be the primary drivers of the current operation; however, our research implicates multiple companies and individuals that have contributed to or benefited from the operation and its fraudulent activities over its nearly decade-long history.

While on the surface this may appear to be a standard tech support scam operation, BengalSEO has developed custom malware that has been in use since 2022 to enable the group’s operations and objectives. Our team dubbed this malware MayaBot, based on the Indian philosophical term translating to ‘illusion’ or ‘magic’.

BengalSEO uses their extensive knowledge of black hat SEO techniques and web development to create and promote a network of malicious lure pages to deliver the MayaBot malware or trick victims into calling their scam call centers.

BengalSEO also integrates a sophisticated Traffic Distribution System (TDS) into their campaigns, which manages traffic flow, campaign performance, and cloaking. This TDS uses a rotating series of redirector domains to route victims to payload delivery domains, as well as a Matomo analytics instance to support victim tracking and fingerprinting.

Due to the size of this operation and extensive findings uncovered during research, this report will be delivered in several parts, get subscribed to learn when the next report comes out!

## Delivery Chain

BengalSEO uses a complex but practical delivery chain to enable both the delivery of MayaBot and their scam operations. This delivery chain relies upon a broad technology stack to host their infrastructure. This section details the delivery chain and the chosen technologies used by BengalSEO.

Figure 1: BengalSEO four-stage delivery chain flowchart

## Lure Pages

BengalSEO targets victims through a distributed network of malicious lure pages. Operators use SEO poisoning to promote these domains to the top of search engine results. The lure pages mimic legitimate technical support and service activation portals for popular consumer brands.

Campaigns observed between 2015 and 2020 focused on technical support scams. From 2020 through 2026, operators expanded across five categories:

- Tax software downloads and Tax support.

- Antivirus software downloads and support.

- Gaming software downloads and support.

- Activation and support for streaming services.

- Activation of credit, healthcare and gift cards.

Figure 2: Google SERP highlighting a readthedocs[.]io Bitdefender lure

Lure pages observed from 2024 onward follow a common theme of a support page with a large button as the central focus, designed to direct the visitor to the next stage of the lure.

Figure 3: Fake Bitdefender Central help page with Get Started button

## Traffic Distribution System

BengalSEO employs a custom Traffic Distribution System (TDS) using a rotating network of redirector domains to route victims from lure pages to final landing pages. This system can fingerprint potential victims appropriately to serve malicious sites and payloads.
Examples of observed redirector domains:
- ts.remdos[.]com

- tx.newredir[.]com

- to.ghredir[.]com

- tx.platdir[.]com

- ww0[.]us

- q82[.]net

- pre[.]im

- us6[.]my

- link72[.]com

- us00[.]net

- fm[.]ci

- url90[.]com

- 4jio[.]com

- flosyr[.]com

Using Validin, our team observed these redirectors embedded in multiple lure pages, for example we observed 73 in June 2026 for the link72[.]com redirector.

Figure 4: Validin results for lure pages embedding link72[.]com

Redirector URLs embedded in lure page buttons are generated from a base62 or base64 encoding of the URL of the page they are embedded on. This is used by the TDS as a tracking identifier for where the request has arrived from.

Figure 5: Lure page button URL pointing to a TDS redirector

Figure 6: CyberChef Base64 decode of redirector tracking parameter

Before being redirected to the final landing page, the redirector domains deploy a Cloudflare Turnstile or hCaptcha challenge to filter out automated crawlers, scanners, and bots. The redirector also fingerprints the browser at this stage.

Figure 7: Cloudflare Turnstile “Verify You’re Not a Robot”

Figure 8: hCaptcha image-grid bot check on a redirector

Matomo Analytics

The BengalSEO TDS integrates a Matomo analytics instance hosted at stats.us3.org to track and fingerprint visitors, monitor campaign performance, and help filter unwanted visitors.

Figure 9: Matomo sign-in page at stats.us3[.]org

Notably, our team observed the same Matomo instance used for analytics on legitimate websites run as part of BengalSEO business entities such as insurance.ug, which redirects to WeConnect Associates as seen in the example below:

Figure 10: urlscan.io requests showing matomo.js on WeConnect site

The Matomo tracking script is typically present on lure pages and landing pages.

Figure 11: Hulu lure page loading Matomo from stats.us3[.]org

Embedded JavaScript within these pages handles tracking and browser fingerprinting, loading matomo.js and triggering an HTTP POST request to stats.us3[.]org/matomo.php with the tracking information and browser fingerprint.

Figure 12: Embedded Matomo tracking script snippet

Figure 13: Above — Network POST to the matomo.php | Below — Example of data sumitted to matomo.php endpoint

# Telemetry Infrastructure Endpoint : https://stats.us3[.]org/matomo.php Site ID (idsite) : 35 # Target Page Artifacts (Impersonation / Lure) URL (url) : https://oculus-app[.]com/ Page Title : Oculus-App - VR Headsets, Specs, Prices & Honest Comparisons Referrer (urlref) : https://www.bing[.]com/ Referrer TS : 1784609591 (2026-07-21 04:53:11 UTC) # Tracking & Session Identifiers Visitor ID (_id) : 82fc7378bc9ef9d9 Pageview ID (pv_id): FAsJXL New Visitor (_idn): 1 (True) Client Local Time : 00:53:11 (h=0, m=53, s=11) # Client System Environment (uadata / res) OS / Platform : Windows 10.0.0 Form Factor : Desktop Browser Brand : Microsoft Edge 133.0.3065.92 / Chromium 133.0.6943.142 Screen Res (res) : 1360x768
Matomo was not the only analystics system ued by BengalSEO, lure pages on hosting platforms such as github.io and pages.dev instead typically use analytics services such as Google Tag Manager.

Figure 14: Plex lure page using Google Tag Manager instead of Matomo

Traffic Flow

A breakdown of an example traffic flow can be seen in the Any.Run sandbox analysis below:

Figure 15: Any.Run traffic flow from lure through captcha to payload

The steps taken by the TDS are as follows:

- Victim visits the initial lure page.
- Matomo or Google Tag Manager executes client-side fingerprinting and tracking at this stage if the analytics framework is present on the lure page.
- Victim clicks the lure link and connects to a redirector domain containing an appended Base62-encoded referrer URL as a campaign tracking parameter.
- The redirector landing page loads and presents an interactive Cloudflare Turnstile or hCaptcha challenge to the client browser.
- The browser transmits session data via HTTP POST to the hCaptcha API, providing metrics including IP addresses, HTTP headers, user agent strings, screen resolution, browser plugins, mouse movements, keystroke timings, puzzle responses, and tracking cookies to generate a cryptographically signed validation token.
- The browser forwards this validation token to the TDS redirector server inside an HTTP POST request.
- The TDS backend evaluates the token to establish a verdict.
- The redirector server issues an HTTP 302 redirect to the payload hosting domain, appending a live Base64-encoded timestamp to the URL.
- The payload domain evaluates the incoming timestamp and forwards the request to the final landing page.
- The infrastructure loads either the malicious landing page or a benign version of the landing page based on the established verdict.
- Matomo transmits an HTTP POST request containing tracking data and browser fingerprints to the Matomo server.

Figure 16: Any.Run HTTP log for redirector hCaptcha stage

Figure 17: Any.Run HTTP log for malicious landing page stage

When a visitor fails the TDS checks, they are served a benign version of the landing page. The overall traffic flow remains almost identical; however, clicking the “Click to continue” button instead sends the visitor to the legitimate service page.

Figure 18: Cloaked benign Bitdefender page with Click to continue

## Payload Delivery

BengalSEO is financially motivated, which means their target objectives are to either serve malware to further enable their scam operations or direct users to a number from which they will attempt to scam over the phone.

Examples of domains used for payload delivery landing pages:

- ustechnio[.]com

- tax.dll[.]lat

- u320[.]my

- reficon[.]pro

- ñ[.]link

- pltechoo[.]pro

Malicious landing pages typically contain a download link and instructions for fake software related to the lure page campaign. Upon clicking the download button, the victim begins downloading a ZIP archive before being redirected to the legitimate software page after 40 seconds.

The following screenshot shows a successful redirect to a malicious landing page:

Figure 19: Malicious Bitdefender landing page with user tracking script

Upon clicking the download button, the victim is prompted with instructions to open and execute the contents of the downloaded ZIP file.

Figure 20: Browser download of ZIP after landing-page click

Figure 21: ZIP contents showing small JavaScript file posing as EXE

Inside the ZIP file is a MayaBot JavaScript dropper masquerading as an exe file. Once executed, the JavaScript executes via wscript.exe and initiates the Mayabot infection.

Figure 22: Obfuscated MayaBot JavaScript dropper source

In some instances, no payload is served, and instead the victim is redirected to a contact page prompting them to call a BengalSEO scam number.

Figure 23: Tech-support scam page prompting call to 1855 number

## Infrastructure and Web Components

Page hosting platforms

BengalSEO utilizes page hosting platforms such as github.io , pages.dev. sites.google.com, and readthebooks.io . These pages appeared most frequently at the top of search engine results during analysis, likely because of the trusted status of these platforms in search engine rankings, alongside SEO poisoning efforts.
A list of hosting platforms observed during research can be seen below:
- beehiv.com

- gitbook.io

- github.io

- godaddysites.com

- groups.google.com

- helplook.com

- jimdosite.com

- mozellosite.com

- my.canva.site

- neocities.org

- nicepage.io

- notion.site

- onsitesupport.io

- pages.dev

- readthedocs.io

- sites.google.com

- slimfaq.com

- tawk.help

- usedocs.com

- webflow.io

- weebly.com

Example of a lure page hosted on sites.google.com

Figure 24: Paramount activation lure hosted on sites.google.com

## Github Infrastructure

BengalSEO uses GitHub for a large portion of their lure page infrastructure. This choice allowed us to take a closer look into their operations. During analysis, our team identified multiple BengalSEO-linked GitHub accounts used for developing and hosting lure pages.

These GitHub accounts were identified using GitHub and OSINT tools to hunt for the following:

- Commits containing known redirector domains & urls.

- github.io pages with embedded html links and redirects to known redirector domains & urls.

Using these identified accounts, our team was able to perform the following:

- Analyze codebases to gain a deeper understanding of how the lure page infrastructure operates.

- Create a timeline of activity on the accounts from account creation to commit history.

- Extract the email addresses used for the accounts, allowing us to link BengalSEO activity to the business entities Garage2Global and WeConnect.

The BengalSEO accounts typically contain multiple repos, each used for deploying web page content for a specific scam campaign via premade web page templates.

Figure 25: BengalSEO GitHub profile with multiple lure-page repos

Repos will typically either contain HTML used in github.io and pages.dev hosted pages, or Python used to deploy pages hosted on readthedocs.io.

Figure 26: GitHub index.html lure page with embedded redirector link

Figure 27: GitHub repo used to deploy readthedocs-style lure pages

These pages are regularly updated via commits to rotate redirector domains or temporarily replace them with legitimate URLs. This is done to avoid detection and replace domains that have been taken down.

Figure 28: GitHub commit diff rotating a redirector domain

Our research identified 84 active BengalSEO GitHub accounts between Jan 2024 and March 2026. Using the GitHub API, our team mapped each account’s creation time and commit history into the chart below, highlighting how frequently these repos were updated. A noticeable spike in account creation and commits was observed from Mid 2025, continuing through to early 2026.

Figure 29: Chart of 84 GitHub accounts’ creation and commit activity

By adding “.patch” to the end of GitHub commit URLs, our team was able to identify emails used in these commits where available. Our team discovered 17 accounts using naming conventions linked to the BengalSEO business Garage2Global, identified by g2g tags and wc.ci domains.

Figure 30: GitHub .patch header exposing Garage2Global-linked commit email

Garage2Global Associated Emails

Note: wc.ci has been attributed to BengalSEO. We assess G2g in the Gmail aliases is a clear link to GarageToGlobal

| Github Account | Email Address

| activate-uhc-com-ucard | [email protected]

| activate-uhc-helpbook | [email protected]

| amazonmytvguide | [email protected]

| capitalonecredit | [email protected]

| cornerguideservice | [email protected]

| guidecenter | [email protected]

| helpguideteam | [email protected]

| help-line-center | [email protected]

| kohlscreditcardhelpadvisor | [email protected]

| kohls-helpguide | [email protected]

| serviceguidecenter | [email protected]

| snehajaing2g | [email protected]

| sywaccountonlinecom | [email protected]

| syw-helpcenter | [email protected]

| tutorialcenter | [email protected]

| viziocomsetupentercode | [email protected]

| viziosetup | [email protected]

Figure 31: Table of GitHub accounts mapped to Garage2Global emails

Garage2Global advertises web development services and likely uses their workforce to develop malicious lure pages used in BengalSEO campaigns alongside legitimate web development projects, as seen on their webpage Garage2Global.org below.

Figure 32: Garage2Global marketing homepage promoting SEO and web services

wc.ci is another domain registered by BengalSEO and links to both WeConnect and Garage2Global by name and hosted content. Garage2Global also shares the same office building as WeConnect. A contact card for the BengalSEO alias Salman Khan can be seen hosted at sk.wc.ci

Figure 33: Salman Khan contact card for Garage2Global Ventures, Kota

## Domain & Certificate Registration

Between 2023 and 2026, our team identified hundreds of domains and SSL certificates tied to BengalSEO. Analyzing campaign patterns uncovered additional assets using these key indicators:

- Tracking the Matomo analytics script used across lure pages, malware download pages, and legitimate BengalSEO websites.

- Identifying consistent use of the Hostmaza hosting provider alongside the Spaceship domain registrar.

- Finding bulk subdomain certificate registrations linked to main BengalSEO domains.

- Running reverse WHOIS lookups for known BengalSEO email addresses and aliases.

- Pivoting on VirusTotal connections and DNS records.

To map the full setup, our team used targeted pivoting techniques and tools to identify additional Indicators of Compromise (IOCs).

VirusTotal

VirusTotal pivoting focused on three main areas:

- Analyzing file submissions and connections between known IOCs.

- Tracking historical DNS record changes across domain clusters.

- Pivoting on Name Server (NS) records to identify backend hosting infrastructure, exposing domains even when proxied behind Cloudflare.

Our team previously identified that BengalSEO frequently registers domains via Spaceship Inc. and hosts them on Hostmaza. These domains often resolve to the IP address 5.101.140[.]80 (AS42831 - UK Dedicated Servers Limited) . Further investigation revealed that Hostmaza leases infrastructure from UK Dedicated Servers and utilizes specific name servers, such as cp1.hostmaza.co.in . To hunt for domains matching this specific Spaceship and Hostmaza combination, our team used the following VirusTotal query:

entity:domain registrar:spaceship AND (a_record:5.101.140.80 OR ns_record:*hostmaza*)

This returned 206 results, yielding 21 unique domain pivots. This represented only a small subset of the infrastructure, as the majority of BengalSEO domains are proxied behind Cloudflare ( detailed in later sections ).

Figure 34: VirusTotal Spaceship and Hostmaza domain pivot query results

Following the NS record pivoting methodology detailed in Saksham Anand’s blog post , our team matched assigned Cloudflare nameserver pairs across VirusTotal to uncover additional domains operating under the threat actor’s Cloudflare account.

Figure 35: VirusTotal search results linking Cloudflare nameserver pairs to BengalSEO domains

Validin

Using Validin, our team identified 411 subdomains for wapp[.]live . Certificate registrations for these subdomains spanned from August 12, 2025, to February 28, 2026, coinciding with bulk domain registrations under .shop , .info , and .my TLDs in August 2025 ( covered in later sections ). These subdomains mapped to approximately 180 unique BengalSEO-registered domains, serving as a pivot point to uncover additional malicious infrastructure.

Figure 36: Validin wapp[.]live page showing 411 subdomains

The domain wapp.live shifted to a hostmaza.co.in name server on August 12th 2025, before the bulk subdomain certificate registrations, indicating BengalSEO gained control of the DNS for this domain at this time.

Figure 37: Validin NS records shifting wapp[.]live to Hostmaza

These wapp.live subdomains were observed in use as redirector domains, indicating this was likely used as a method to create redundancy for registered domains.

Figure 38: Lure page HTTP transactions with redirector request highlighted

Not long after February 28th 2026, the account owner for the wapp[.]live domain was suspended by Hostmaza, taking this domain and its subdomains offline.

Figure 39: Hostmaza account suspended interstitial

This method was also observed with the domains aol[.]cx and iconnectpc[.]com , revealing 80 and 43 unique BengalSEO domains respectively. Notably, the aol[.]cx subdomains were not observed to be in use.

Figure 40: Validin subdomain panels for aol[.]cx and iconnectpc[.]com

urlscan.io

Having identified that the Matomo analytics instance was reused across the wider BengalSEO campaign, our team used urlscan.io to hunt for associated infrastructure:

domain:stats.us3[.]org

This query returned 1,190 total results, revealing 146 unique domains and subdomains actively utilizing this Matomo instance.

Figure 41: urlscan.io Pro search results for domain:stats.us3[.]org

Figure 42: urlscan.io thumbnail gallery of BengalSEO lure and landing pages

## Timeline and Trend Analysis

Using domain and SSL/TLS certificate registration APIs, our team performed timeline analysis on a sample of identified BengalSEO domains active between March 2023 and March 2026. This provides insight into BengalSEO’s operational activity during this period, including registration volumes, preferred hosting providers and registrars, and the distribution of scam themes across registered domains.

Note : This dataset represents a sample to visualize trends, rather than an exhaustive list of BengalSEO infrastructure. The complete set of gathered IOCs can be viewed on GitHub .

The graph below shows a timeline of cumulative domain and certificate registrations over this period. Registrations increased steadily between early 2023 and July 2025, followed by a sharp uptick in August 2025 driven by a wave of bulk domain registrations. This heightened activity continued through late 2025 and early 2026 as BengalSEO scaled up their operations.

Figure 43: Cumulative BengalSEO domain and certificate registration timeline

As shown in more detail in the graph below, BengalSEO maintained a steady trend of domain registrations between early 2023 and the first half of 2025.

Registrations during this period primarily focused on setting up scam lure pages across distinct themes, including tax services, healthcare, streaming platforms, and tech support. This timeframe also includes several BengalSEO business domains, such as sasta[.]holiday , wc[.]ci , and garage2global[.]com.

Additionally, domains serving as MayaBot C2 servers, such as cus[.]cam , dll[.]lat , and us99[.]org , were registered during this timeframe, along with the Matomo tracking domain us3[.]org in early 2024.

Figure 44: Domain registration scatter plot for 2023 through mid-2025

Starting in Q3 2025, BengalSEO began registering bulk domains using numbered us, act, and pc naming conventions across .my , .shop , and .info TLDs. While primarily deployed as redirectors, several of these domains functioned as landing pages.

This activity continued into Q4 2025 with the addition of ustech and ustechno naming patterns. Our team speculates that the “us” and “act” naming conventions coincided with the passage of the US One Big Beautiful Bill Act (OBBBA) during this timeframe, which may have influenced healthcare-targeted themes and lures.

Figure 45: Domain registration scatter plot for 2025 Q3 bulk wave

Figure 46: Domain registration scatter plot for 2025 Q4

In Q1 2026, MayaBot SEO campaigns featured sequential ustechnio[.]com domains, ranging from ustechnio[.]com through ustechnio100[.]com .

Figure 47: Domain registration scatter plot for 2026 ustechnio series

The graph below provides a clearer breakdown of registered domain themes and clusters observed during this time period.

Figure 48: Registered domain theme distribution across 2023–2026

Between 2023 and 2026, BengalSEO primarily registered domains through Spaceship (47.6%) and Namecheap (28.6%). For hosting, the group heavily favored Cloudflare (81.1%) to proxy traffic, with Hostmaza serving as the origin host for 10.0% of domains.

Figure 49: Registrar distribution bar chart led by Spaceship and Namecheap

Figure 50: Hosting provider distribution bar chart led by Cloudflare and Hostmaza

## SEO Capabilities Analysis

Our team observed BengalSEO often priding themselves on their SEO skillset publicly. Search Engine Optimization (SEO) enables BengalSEO to promote their lure sites to the top of search engine results, increasing the chances that users visit their sites and move through their delivery chain. BengalSEO used backlinks, DOM injection, DOM shuffling, and keyword stuffing to enable their operation through Black Hat SEO techniques.

Backlink Generation

BengalSEO uses aggressive user-generated content (UGC) spam to generate backlinks at scale. Analysis identified multiple accounts spamming hyperlinks to lure pages in forums and blog comment sections.

Figure 51: Blog comment spam pushing a Vizio setup lure link

Figure 52: Forum profile spam posting activate[.]uhc[.]com links

Figure 53: Keyword-stuffed forum post with repeated lure hyperlinks

Using the underground community Demon Forums as an example, our team observed multiple accounts spamming various BengalSEO lure page links between September 2025 and June 2026.

Figure 54: Demon Forums spam post list from Sept 2025 to June 2026

These accounts were often flagged on StopForumSpam, where reports traced some of the activity to residential IPs in Jaipur, Rajasthan.

Figure 55: StopForumSpam table of flagged spam accounts

Figure 56: IP geolocation showing Airtel and Jio addresses in Jaipur

Using the Ahrefs service, our team noted that in one example, a lure page had 1900 generated backlinks. BengalSEO utilizes this high volume of backlinks to manipulate search engine ranking algorithms, artificially boosting the visibility of the lure pages.

Figure 57: Ahrefs backlink profile with about 1.9K backlinks to a lure

### DOM Injection

Lure pages contain embedded JavaScript for SEO poisoning. The script uses obfuscated ASCII character codes to construct a typosquatted domain ajax.googleapis.com[.]co mimicking the legitimate Google CDN.

The script attempts to fetch an HTML payload disguised as a standard stylesheet bootstrap-table.min.css . This payload serves as an invisible link farm, injecting hundreds of keyword-stuffed tags and links for targeted campaigns directly into the Document Object Model (DOM).

Figure 58: DOM injection script building typosquatted Googleapis CDN host

Figure 59: Invisible keyword-stuffed link farm injected into the DOM

During analysis, this retrieval often failed due to Cross-Origin Resource Sharing (CORS) restrictions enforced by the browser. Despite this, the underlying code remains an artifact in the BengalSEO lure page template.

Figure 60: DevTools showing CORS-blocked bootstrap-table.min.css fetch

Keyword stuffing & Webmaster tools

Many lure pages use HTML meta tags for keyword stuffing to manipulate search rankings and for site verification to gain access to Google Search Console and Bing Webmaster Tools. This access is likely used to submit sitemaps for faster indexing, track performance via search query metrics, and monitor security alerts to pivot infrastructure when pages are flagged as malicious.

Figure 61: Meta keywords and Google/Bing site-verification tags in source

DOM Shuffling

Payload hosting pages execute an embedded JavaScript function that dynamically reorders HTML elements. This script uses the current UTC month as a seed to randomize the Document Object Model (DOM) structure.

BengalSEO uses this technique to evade search engine duplicate content penalties. Randomizing the layout allows identical setup guides deployed across hundreds of domains to appear unique to web crawlers, bypassing automated spam filters to preserve high search rankings.
<!-- JavaScript: Monthly Shuffle (UTC-based) + Auto Refresh --> <script> document.addEventListener("DOMContentLoaded", () => { const wrapper = document.getElementById("sections-wrapper"); const sections = Array.from(wrapper.children); // Use UTC time for a fixed reference const now = new Date(); const currentMonthUTC = `${now.getUTCFullYear()}-${now.getUTCMonth() + 1}`; // stored data const lastShuffle = localStorage.getItem("lastShuffleMonthUTC"); const savedOrder = JSON.parse(localStorage.getItem("sectionOrderUTC")); // helper to shuffle array const shuffle = (arr) => { for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [arr[i], arr[j]] = [arr[j], arr[i]]; } return arr; }; // if month changed → shuffle new order if (lastShuffle !== currentMonthUTC) { const newOrder = shuffle(sections.map(sec => sec.id)); localStorage.setItem("sectionOrderUTC", JSON.stringify(newOrder)); localStorage.setItem("lastShuffleMonthUTC", currentMonthUTC); // auto refresh after shuffle (1 second delay) setTimeout(() => location.reload(), 1000); } // use stored order (if available) const orderToUse = JSON.parse(localStorage.getItem("sectionOrderUTC")) || sections.map(sec => sec.id); orderToUse.forEach(id => wrapper.appendChild(document.getElementById(id))); // optional: daily refresh safeguard (still UTC-based) const lastVisitUTC = localStorage.getItem("lastVisitDateUTC"); const todayUTC = now.toISOString().split("T")[0]; // e.g. "2025-10-08" if (lastVisitUTC !== todayUTC) { localStorage.setItem("lastVisitDateUTC", todayUTC); // optional: location.reload(); } }); </script>
Figure 62: JavaScript monthly DOM shuffle to evade duplicate-content filters

## Diamond Model

## Indicators

Note: Indicators cover campaigns from 2023 to 2026.

https://github.com/The-DFIR-Report/DFIR-Report-Indicators/blob/main/2026-08-24-bengalseo-part-1-anatomy-of-the-operation.md

## MITRE ATT&CK

This is part one of a multipart series, get subscribed to learn when the next report comes out!

##### Share this entry

- Share on Facebook

- Share on X

- Share on WhatsApp

- Share on Linkedin

- Share on Reddit

- Share by Mail
