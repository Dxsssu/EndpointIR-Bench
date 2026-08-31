# 公开溯源与事件响应报告集

本目录收录用于 EndpointIR-Bench 场景设计的公开材料，共 **120 份报告**，覆盖 2020-2026 年的真实入侵、联合调查通告和事件响应总结。网页报告同时保留原始 HTML，并生成便于检索和 LLM 结构化抽取的 Markdown 文本。

| 来源 | 报告数 | 主要用途 |
|---|---:|---|
| CISA/FBI/NSA 等机构 | 15 | 官方调查结论、攻击者 TTP、IOC 和检测/响应建议 |
| The DFIR Report | 97 | 官网 Reports 目录的完整公开条目；高颗粒度攻击时间线、终端证据、命令和跨主机行为 |
| Unit 42 | 8 | 事件响应案例、身份攻击、云环境、虚拟化和攻击者画像 |
| **合计** | **120** | 93 份 A 类场景种子，27 份 B 类覆盖参考 |

## 使用原则

- 报告仅作为场景语义、真实攻击行为和证据线索的来源，不直接作为完整攻击链或 Ground Truth。
- A 类材料包含相对完整的事件时间线和技术细节，优先用于场景种子；B 类材料主要用于补充攻击者行为分布和能力覆盖。
- The DFIR Report 的 97 条官网目录记录全部保留，但其中的年度总结、检测指南、演讲材料、占位页及不足 800 词的短文统一降为 B 类，不直接等同于 97 条可执行攻击场景。
- 从报告抽取的步骤应记录出处与置信度；缺失步骤只能通过审核后的动作库补全，并在受控环境中执行和独立验证。
- CISA 材料均来自其公开下载地址，多数标记为 TLP:CLEAR；红队评估 PDF 仍保留发布流程中的 TLP:AMBER+STRICT/TLP:CLEAR 标记，应在使用前单独复核。其他材料仍归原发布方版权所有，仅应按其网站条款用于研究、引用和内部分析。

## 目录结构

```text
Public_IR_Reports/
├── CISA/                 # 原始 PDF
├── The_DFIR_Report/      # 97 条原始 HTML + 提取后的 Markdown + 官网目录快照
├── Unit42/               # 原始 HTML + 提取后的 Markdown
├── manifest.csv          # 来源、标签、哈希和本地路径
└── README.md
```

The DFIR Report 全量目录可使用同步脚本更新；网页文本和清单也可以独立重建：

```bash
python3 scripts/sync_dfir_reports.py
python3 scripts/extract_public_report.py Public_IR_Reports/Unit42/*.html
python3 scripts/rebuild_report_manifest.py
```

## 覆盖范围

当前集合覆盖以下主要场景，完整的逐条索引、来源 URL、平台、标签和 SHA-256 见 [manifest.csv](manifest.csv)。

- **初始访问**：Office/LNK/ISO/OneNote/HTML Smuggling、假冒 Zoom、SEO 投毒、邮件交互、RDP 密码喷洒和有效账号。
- **暴露服务利用**：Exchange ProxyShell、Follina、Confluence、ActiveMQ、WordPress、MOVEit、Ivanti CSA 和 MSSQL。
- **执行与持久化**：PowerShell、BITS、计划任务、注册表 Run Key、服务、WebShell、RMM、Cobalt Strike 和 Sliver。
- **权限与凭据**：LSASS、Mimikatz、Kerberoasting、Zerologon、AD CS、域账号创建和证书滥用。
- **横向移动与发现**：RDP、PsExec、远程服务、AdFind、BloodHound、网络扫描、代理和恶意虚拟机。
- **目标行动**：Rclone/WinSCP/S3 数据外传、云存储访问、文件删除、域级勒索、ESXi 加密和破坏性擦除。
- **调查环境**：Windows 单机、Active Directory、Linux 服务、VMware/vSphere、AWS、Snowflake 和边界设备。

## 建议优先使用的场景种子

如需先做一批原型，建议从下面几类开始，它们的时间线和终端证据相对完整：

- [BazarCall 到 Conti](The_DFIR_Report/2021-08-01_BazarCall-to-Conti.md)：用户执行、恶意加载器、Cobalt Strike、凭据访问和域级勒索。
- [Follina 到域失陷](The_DFIR_Report/2022-10-31_Follina-to-Domain-Compromise.md)：文档漏洞、PowerShell、C2 和横向移动。
- [HTML Smuggling 到域级勒索](The_DFIR_Report/2023-08-28_HTML-Smuggling-to-Ransomware.md)：浏览器下载、用户执行、持久化和多主机攻击链。
- [GootLoader 到域控制](The_DFIR_Report/2024-02-26_GootLoader-to-Domain-Control.md)：SEO 投毒、脚本执行、发现和域权限提升。
- [Cobalt Strike/SOCKS 到 LockBit](The_DFIR_Report/2025-01-27_Cobalt-Strike-SOCKS-to-LockBit.md)：计划任务、代理、RDP、Defender 修改和数据外传。
- [Volt Typhoon](CISA/2024-02-07_AA24-038A_Volt-Typhoon-Critical-Infrastructure.pdf)：LOTL、长期潜伏和多源调查证据。
- [CISA Red Team Assessment](CISA/2024-11-21_AA24-326A_CISA-Red-Team-Assessment.pdf)：检测缺口、调查响应和组织防御失败模式。
- [Muddled Libra 行动手册](Unit42/Muddled-Libra-Operational-Playbook.md)：恶意 VM、vSphere、AD、证书与 Snowflake 活动。

## 完整性说明

所有 PDF 均通过文件类型和页数检查；新增 PDF 还会进行抽样首页渲染。网页报告均成功下载，并生成了非空 Markdown 正文。`The_DFIR_Report/catalog.json` 保存同步时的 97 条官网目录快照，`manifest.csv` 保存原始报告文件的 SHA-256，后续重新抓取时可用于检测上游内容变化。

The DFIR Report 的 WordPress/Godzilla 案例网页只包含简介，因此目录中额外保存了页面嵌入的完整 PDF；清洗后的 Markdown 仅作为该 PDF 的入口摘要，不应单独用于场景生成。

Dridex 旧报告的普通网页模板未返回正文，但官网 WordPress REST 接口仍提供完整文章；目录同时保留原网页 HTML、REST JSON 和恢复后的 Markdown。`default-post` 是官网目录中的占位内容，已完整归档并标为 B 类，不应作为场景种子。
