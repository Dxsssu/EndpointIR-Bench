# 背景
在安全运营场景中，高危告警触发后，真正决定处置效果的关键环节往往不是告警产生本身，而是后续对受害主机的溯源响应。运营人员需要围绕告警线索登录目标主机，综合威胁情报、异常进程、网络连接、浏览器下载记录、系统日志、文件痕迹及持久化项等多源证据，判断攻击是否真实发生、木马样本位于何处、是否存在外联 C2 以及攻击入口可能来自哪里。

现有工作几乎都建立在"取证数据已经存在"的假设上——日志已采集好(ExCyTIn/Cyber Defense Benchmark)、流量已抓包(CyberSleuth/CFA-Bench)、镜像已落盘(DFIR-Metric)。真正要求 agent**主动登录活体终端、通过交互式命令实时采集**(进程树、netstat 连接、浏览器历史/下载记录、文件时间线、注册表/计划任务等持久化项)并**动态决定下一步取证动作**的 benchmark,目前公开文献里基本是空白,仅有 AutoGen 那篇早期架构性工作触及但未形成量化评测体系。

| 类别               | 代表工作                                  | 证据形态                   |
| ---------------- | ------------------------------------- | ---------------------- |
| 静态日志问答           | ExCyTIn-Bench、Cyber Defense Benchmark | Sentinel/EDR 日志已抓取     |
| 静态取证镜像           | DFIR-Metric、CFA-Bench                 | 磁盘/内存镜像已落盘             |
| 网络流量取证           | CyberSleuth                           | PCAP 已抓包               |
| **活体主机交互溯源（空白）** | AutoGen-DF（架构性，非 benchmark）           | Agent 主动登录主机、执行命令、动态取证 |
# 攻击模拟调研
**攻击链和场景的"剧本"来源**
（1）真实世界的溯源叙事
从 Mandiant、MSTIC、Kaspersky、CrowdStrike、奇安信、安天及 [The DFIR Report](https://thedfirreport.com/) 等公开事件响应报告中抽取攻击时间线，包括初始访问、执行、持久化、C2 和横向移动等阶段，再据此设计调查任务。
[企业真实溯源报告](D:\Research\溯源响应智能体\溯源相关\yingji)
各大厂商的 APT/事件响应报告(Mandiant M-Trends、微软 MSTIC、360/奇安信/安天的年度或专题报告、Kaspersky/CrowdStrike 的分析)。这些报告通常会给出完整的攻击时间线:初始 access→执行→持久化→C2→(可能的)横向移动。
DFIR 安全事件调查报告
https://thedfirreport.com/
一个示例：从 Bing 搜索到勒索软件：Bumblebee 和 AdaptixC2 部署了 Akira 工具
https://thedfirreport.com/2026/06/29/from-bing-search-to-ransomware-bumblebee-and-adaptixc2-deliver-akira-3/
![[终端溯源Agent Benchmark-2026-07-27-03-50-24.png]]
SIR-Bench 的做法: 从 129 个脱敏的真实事件响应记录中提炼出攻击模式,再在受控云环境中重放,自动关联生成的证据来标注预期发现,最后由安全工程师复核、补充需要推理才能得出的发现(比如"看到 IAM 用户创建后紧跟 access key 生成"要推断出"攻击者建立了持久化")。
- **Ground truth 天然可信**:攻击链条、TTP、恶意样本哈希、C2 域名等都经过专业分析师验证,可直接作为评分基准。
- **无可交互环境**:报告是静态文本 + 少量截图/日志片段,Agent 无法"登录"到那台受害主机上执行 `ps`、查注册表、查浏览器历史。你只能把报告本身当成"阅读理解材料"来测(这退化成了 CyberTeam、DFIR-Metric 这类 QA/文本分析型 benchmark,而不是"终端自主取证"型 benchmark)。
（2）可复现、免版权风险的攻击链模拟工具
在隔离的 Windows/Linux 虚拟机中，使用 [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team)、[CALDERA](https://github.com/apache/caldera) 或自定义安全脚本执行攻击技术，并让 Agent 登录终端调查执行后留下的痕迹。
**Atomic Red Team**:覆盖261个ATT&CK技术、包含1225个独立的"原子测试",每个测试针对一个具体技术(比如注册表Run键持久化、计划任务创建),可以单独跑也可以串联成完整攻击链。
**MITRE Caldera**:自动化对抗模拟平台,默认配置自带527种ATT&CK技术的执行流程,支持自动化编排完整的攻击序列并自带C2通信。
https://github.com/apache/caldera
![[终端溯源Agent Benchmark-2026-07-27-08-47-33.png]]
- **完全可控、可交互**:Agent 可以真的登录到这台被模拟攻击过的主机上,跑 `tasklist`、看 `HKCU\...\Run`、翻计划任务、看下载目录
- **缺少专家验证的 ground truth 叙事**:Atomic Red Team 的每个测试用例只是"执行了 T1547.001(注册表 Run 键)",它本身不构成一个有因果逻辑、有攻击动机、有攻击者画像的"故事"。

# 论文 outline
## 真实事件引导的可执行终端调查 Benchmark
`事件报告/开放攻击计划 → 攻击语义图 → 可执行场景 → 终端证据验证 → VM 快照 → Agent 调查 → 自动评分`
**（1）筛选真实事件与开放攻击计划**
从 Mandiant、MSTIC、Kaspersky、CrowdStrike、The DFIR Report 以及国内安全厂商的公开事件响应报告中筛选具有代表性的终端攻击案例，同时补充 MITRE ATT&CK、CTID Adversary Emulation Library 等开放攻击计划。场景应优先覆盖浏览器或邮件投递、脚本执行、恶意服务、计划任务、注册表启动项和 C2 外联等典型终端行为。然后提取其中公开披露的攻击步骤、实体关系和调查目标，并记录来源与授权信息，形成经过筛选的事件种子集合。
除厂商报告外，可优先使用具有开放属性的 [MITRE ATT&CK](https://attack.mitre.org/)、[CTID Adversary Emulation Library](https://ctid.mitre.org/resources/adversary-emulation-library) 和 [Attack Flow](https://ctid.mitre.org/projects/attack-flow)。厂商报告主要用于验证场景是否符合真实事件。
**（2）抽象标准化攻击语义图**
将事件报告中的自然语言叙事转化为统一的攻击语义图或 Scenario Blueprint。图中的节点表示用户、浏览器、进程、文件、服务、计划任务、注册表项、域名和 IP 等实体，边表示下载、创建、执行、连接和持久化等行为关系。例如，“用户通过浏览器下载文件，文件被 PowerShell 执行，随后创建计划任务并连接 C2”可以被表示为一条结构化因果链。该步骤需要同时定义初始告警、核心调查问题、预期关键发现和可能涉及的终端证据面，从而将真实事件叙事转化为可执行、可扩展和可评分的场景规格。
例如：
```
浏览器下载
    → 用户执行脚本
    → 释放可执行文件
    → 创建计划任务
    → 周期性连接 C2
```
**（3）将攻击图编译为可执行场景**
根据场景规格，将每个攻击步骤映射到具体的执行组件。
通用攻击技术可由 Atomic Red Team 或 CALDERA 执行，浏览器下载、邮件收取、附件打开等应用层行为则由自定义用户模拟器完成，C2 通信通过隔离网络中的 Mock C2 服务产生。
所有恶意载荷均替换为无害的 canary 程序，只保留文件创建、进程执行、持久化和网络通信等可调查行为。场景中的文件名、路径、用户名、任务名、域名和时间等参数均由配置文件控制，使同一攻击语义能够生成多个表面不同的实例。
**（4）构建具有正常背景活动的终端环境**
环境中预装浏览器、邮件客户端、办公软件和常见应用，创建具有浏览历史、下载记录和用户文件的正常账号，并运行软件更新、系统维护、合法服务和正常网络访问等背景行为。
**（5）受控执行攻击并记录执行事实**
场景准备完成后，由独立的控制端按照攻击语义图执行完整攻击链，并记录每一步的真实执行结果，包括执行时间、用户身份、进程标识、文件路径、文件哈希、服务或任务名称、注册表位置以及网络目标。
攻击执行后，提取并生成 ground truth，即终端上存在的证据，例如文件、浏览器下载记录、Zone.Identifier、计划任务、服务、注册表项、网络连接、DNS 缓存、Prefetch 和本机事件记录等。Benchmark 只要求 Agent 发现经过验证且实际可观测的证据。
**（6）生成难度变体与正常对照案例**
在一个基础场景上，通过参数随机化、背景噪声注入和证据删减生成多个不同难度的实例。简单案例可以保留活动进程、现存连接和明显文件；困难案例可以让进程退出、删除原始下载文件、清除部分浏览记录，要求 Agent 通过持久化项和文件系统痕迹间接还原攻击链。此外，每个恶意案例应构造一个表面相似的 benign twin，例如用合法软件更新任务对应恶意计划任务、用合法遥测流量对应周期性 C2。
**（7）封装为可重复运行的 Benchmark Episode**
每个最终案例被封装为一个独立评测单元，包括稀疏初始告警、虚拟机快照、允许使用的调查工具、调用预算、结构化回答格式等。
**（8）Benchmark 质量控制**
所有案例在进入正式 Benchmark 前都应经过自动检查和专家复核。自动检查用于验证攻击动作是否成功、核心证据是否存在、场景能否从快照稳定恢复，以及 ground truth 是否与终端状态一致；安全专家则抽查攻击链合理性、证据充分性和 benign twin 的真实性。
## Benchmark 形式

将 Benchmark 组织成一组可重复运行的 Episode：每个 Episode 指定攻击机镜像、一个或多个靶机快照、版本化攻击场景、Ground Truth 和执行参数。运行时由统一 Runner 恢复环境、启动 CALDERA、等待靶机 Agent 上线、执行攻击链、验证证据并冻结现场，最后交给调查智能体分析和评分。

- **攻击机镜像（通常为 Kali）**：预装固定版本的 CALDERA、Benchmark 自定义插件、Mock C2、场景 Runner 和相关依赖。建议同时配置管理网络和模拟攻击网络，避免 CALDERA/Sandcat 的控制流量被误认为场景中的 C2 证据。
- **多个靶机环境**：准备 Windows、Linux 等不同操作系统和软件组合，每个环境具有可恢复的干净快照、正常用户数据和背景活动。场景通过镜像 ID、快照 ID、主机角色和 CALDERA Agent Group 选择目标，可支持 L1 单主机、L2 单主机攻击链和 L3 跨主机场景。
- **Scenario-as-Code**：将场景的攻击动作、执行顺序、输入参数、环境依赖和清理逻辑全部纳入 Git。CALDERA 原生提供组件级 YAML，但没有一份能够同时定义 VM、Agent、Operation 和 Ground Truth 的完整 `scenario.yml`。
- **Ground Truth**：通过靶机检查脚本、Mock C2 日志和文件哈希独立验证的可观测证据。Ground Truth 应描述实体、因果关系、时间窗口、必需/可选证据和验证方法，不能仅凭 CALDERA 命令返回成功来判断证据存在。
- **自动攻击执行器（CALDERA）**：Runner 等待指定 Agent Group 上线后，通过 `POST /api/v2/operations` 创建 Operation，传入 Adversary、Planner、Source、Group、Jitter 和审批模式；随后轮询执行状态，并导出 Operation Report、Event Logs 和单步输出。CALDERA 负责攻击动作下发与攻击链编排，不负责 VM 恢复、Ground Truth 验证和最终评分。

## 任务分级

| 等级  | 推荐名称     | 攻击图特征               | Agent 核心能力      |
| --- | -------- | ------------------- | --------------- |
| L1  | 单主机原子调查  | 1 台受害主机，1 个语义攻击步骤   | 发现单个攻击行为及其证据    |
| L2  | 单主机攻击链调查 | 1 台受害主机，多个因果关联步骤    | 在主机内部还原完整攻击链    |
| L3  | 跨主机攻击链调查 | 至少 2 台受害主机，存在跨主机因果边 | 关联多台主机证据并还原横向移动 |

（1）单主机单步攻击
一个具有独立安全语义的 ATT&CK 技术或 Atomic Test
```
Attacker1 ──[Scheduled Task Persistence]──> Target1
```
（2）单主机多步攻击
```
Attacker1 
──[Initial Access]──> Target1 
──[Execution]──────> Target1 
──[Persistence]────> Target1 
──[C2]─────────────> Target1
```
（3）多主机攻击
```
Attacker1 ──[Initial Compromise]──> Target1
Target1   ──[Lateral Movement]────> Target2
```

# 模拟攻击平台
## Atomic Red Team
https://github.com/redcanaryco/atomic-red-team
![[终端溯源Agent Benchmark-2026-08-04-01-31-50.png]]
Atomic Red Team™ 是一个测试库，其中的测试映射到 MITRE ATT&CK® 框架。安全团队可以使用 Atomic Red Team 快速、可移植且可重复地测试其环境。

为了便于管理，项目将测试分类到不同的目录中，这些目录的名称来源于 MITRE ATT&CK®中的技术分类。例如，项目将过程注入测试文件存放在 `atomic-red-team/atomics/T1055/` 目录下。
每个技术目录包含以下内容：
- 一个 YAML 格式的测试文件；
- 一个适合人类阅读的 Markdown 测试文件；
- 可选的 `src` 目录，用于存放源文件的相关信息；
- 可选的 `bin` 目录，用于存放二进制依赖文件；

以 T1614 为例：
`T1614 - System Location Discovery`，中文可译为“系统位置发现”，属于 MITRE ATT&CK 的 Discovery（发现）战术。
攻击者可能收集以下信息来推断受害主机所在的国家或地区：
- 系统语言和区域设置；
- 键盘布局；
- 时区；
- IP 地址及在线地理位置查询结果；
- 云主机的区域或可用区元数据。
攻击者获得位置线索后，可能据此决定是否继续感染、是否执行后续行为，或者针对特定地区调整攻击内容。有些恶意软件也会避开特定语言或司法辖区，以降低被调查和追踪的风险。
ATT&CK 页面：<https://attack.mitre.org/techniques/T1614/>
`T1614.001 - System Language Discovery` 是 T1614 的子技术，重点是通过系统语言推断主机位置。
Windows 上常见的实现方式包括：
- 查询 `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Nls\Language`；
- 执行 `chcp`、`dism.exe /online /Get-Intl` 或 `wmic`；
- 使用 PowerShell 查询区域、语言和时区；
- 调用 `GetKeyboardLayout`、`GetUserDefaultUILanguage` 等 Windows API。
Linux 和 macOS 上则常通过 `locale`、`localectl` 或 `$LANG` 环境变量获取语言信息。
ATT&CK 子技术页面：<https://attack.mitre.org/techniques/T1614/001/>

目录结构：
```text
T1614.001\
|-- T1614.001.yaml
|-- T1614.001.md
|-- src\
|   |-- LanguageKeyboardLayout.cs
|-- bin\
    |-- LanguageKeyboardLayout.exe
```
***T1614.001.yaml***
供执行框架读取的机器可读测试定义，包含：
- ATT&CK 技术编号和名称；
- Atomic 测试名称与稳定 GUID；
- 支持的平台；
- 输入参数及默认值；
- prerequisite 检查和依赖获取命令；
- executor、实际执行命令和提权要求；
- cleanup 命令（如果测试需要清理）。
![[终端溯源Agent Benchmark-2026-08-04-02-52-01.png]]
***T1614.001.md***
面向人工阅读的 Markdown 版本。它包含 ATT&CK 原始说明、测试目录、命令、输入参数、依赖和 cleanup，适合在执行前审核测试行为。
![[终端溯源Agent Benchmark-2026-08-04-02-53-18.png]]
***src 目录***
测试程序的 C# 源码。
源码调用以下 6 个只读 Windows API：

| DLL            | API                          | 作用             |
| -------------- | ---------------------------- | -------------- |
| `user32.dll`   | `GetKeyboardLayout`          | 获取当前线程键盘布局     |
| `user32.dll`   | `GetKeyboardLayoutList`      | 获取系统中的键盘布局列表   |
| `kernel32.dll` | `GetUserDefaultUILanguage`   | 获取当前用户默认 UI 语言 |
| `kernel32.dll` | `GetSystemDefaultUILanguage` | 获取系统默认 UI 语言   |
| `kernel32.dll` | `GetUserDefaultLangID`       | 获取当前用户默认语言 ID  |
| `kernel32.dll` | `GetCurrentThreadId`         | 获取当前线程 ID      |
***bin 目录***
上述 C# 源码的已编译 .NET 程序。

**Atomic Red Team 单步执行**
```powershell
Invoke-AtomicTest T1614.001 `
  -TestGuids e39b99e9-ce7f-4b24-9c88-0fbad069e6c6 `
  -PathToAtomicsFolder 'D:\Project\atomic-red-team\atomics' `
  -NoExecutionLog `
  -TimeoutSeconds 30 `
  -Confirm:$false
```
实际输出：
```powershell
Invoke-AtomicTest T1614.001 `
  -TestGuids e39b99e9-ce7f-4b24-9c88-0fbad069e6c6 `
  -PathToAtomicsFolder $atomics `
  -NoExecutionLog `
  -TimeoutSeconds 30 `
  -Confirm:$false
```
上述程序只将查询结果输出到控制台，没有文件写入、注册表修改、网络连接、持久化或提权逻辑。

另外一个修改注册表的示例：
T1222
```powershell
Invoke-AtomicTest T1112 `
  -TestGuids 15f44ea9-4571-4837-be9e-802431a7bfae `
  -PathToAtomicsFolder $atomics `
  -NoExecutionLog `
  -TimeoutSeconds 30 `
  -Confirm:$false
```
![[终端溯源Agent Benchmark-2026-08-04-03-02-17.png]]

**多步模拟：**
![[终端溯源Agent Benchmark-2026-08-04-03-36-34.png]]

假设员工收到一个“季度奖金审核”附件。附件实际上只是无害批处理文件，执行后开始进行主机侦察、寻找预置的假凭据、收集假文档，并将结果发送到 `127.0.0.1` 上的本地接收器。
- **模拟投递**：在桌面演示目录中放置名为“季度奖金审核”的无害批处理文件。
- **命令执行**：通过 `T1059.003` 执行批处理并释放无害的落地点标记和假业务文件。
- **持久化**：展示 `T1053.005` 创建计划任务的官方定义，但不实际注册任务。
- **环境发现**：通过 `T1614.001` 查询系统语言和键盘布局，识别出简体中文环境。
- **数据收集**：通过 `T1005` 收集演示目录中的两份假文本并生成 ZIP 文件。
- **数据归档**：通过 `T1560.001` 使用 `makecab.exe` 将收集结果压缩成 CAB 文件。
- **C2 通信**：通过 `T1071.001` 向本机回环地址发送四次模拟 HTTP 心跳。
- **数据外传**：通过 `T1041` 将假数据归档发送到本机回环接收端，数据未离开计算机。
- **时间戳伪装**：通过 `T1070.006` 将 CAB 文件的最后修改时间改为 1970 年。
- **痕迹删除**：通过 `T1070.004` 删除最初的无害诱饵批处理文件。
**事件日志证据**
1. PowerShell Operational 中存在 `4100/4103/4104`，可以关联数据收集、CAB 归档和回环 HTTP 行为。
2. 数据收集相关匹配 4 条，主要为 `4103/4104`。
3. 归档相关匹配 3 条，事件 ID 为 `4100/4103/4104`。
4. 回环 C2 心跳匹配 4 条 `4100`。
5. 回环外传匹配 1 条 `4100`。
6. Windows PowerShell 日志存在 `400/403/600/800`，能够反映 PowerShell 启停、提供程序和管道执行情况。
7. 日志中的匹配数量不等于攻击动作数量，因为一次 Atomic 测试可能启动多个 PowerShell 进程并产生多条生命周期事件。
**网络证据**
8. 执行时本机接收器实际观察到 4 个发往 `/beacon` 的 GET 请求。
9. User-Agent 分别包括 `HttpBrowser/1.0`、`Wget/1.9`、`Opera/8.81` 和 `*<|>*`。
10. 接收器观察到 1 个发往 `/upload` 的 POST，请求长度为 219。
11. 目标全部是 `127.0.0.1:18088`，没有外部网络通信。
12. 接收器只保存在内存中并已关闭，因此这些网络请求当前没有单独的落盘记录。

## CALDERA
[Apache CALDERA](https://github.com/apache/caldera) 是一个基于 MITRE ATT&CK 的自动化对手模拟平台，可用于自动化攻击演练、人工红队行动和自动化事件响应。与 Atomic Red Team 主要提供“单个技术的可执行测试”不同，CALDERA 同时提供异步 C2 服务、REST API、Web 界面、终端 Agent、攻击能力库和多步编排机制，能够把多个 ATT&CK 技术组织成一条由控制端自动执行的攻击链。
CALDERA 由两部分构成：
- **核心系统**：包含异步 C2 服务、REST API、Web 界面、任务调度、运行状态管理和结果记录。
- **插件系统**：提供终端 Agent、TTP/攻击计划、报告、背景行为模拟和事件响应等扩展能力。
官方资源：
- [项目仓库](https://github.com/apache/caldera)
- [官方文档](https://caldera.readthedocs.io/en/latest/)
- [Operation Results 文档](https://caldera.readthedocs.io/en/latest/Operation-Results.html)
**与 Atomic Red Team 的关系**

| 维度               | Atomic Red Team             | CALDERA                                          |
| ---------------- | --------------------------- | ------------------------------------------------ |
| 基本执行单元           | Atomic Test                 | Ability                                          |
| 多步攻击链            | 需要外部脚本自行串联                  | 使用 Adversary Profile 和 Planner 编排                |
| 终端执行方式           | 本地调用 Invoke-AtomicTest 等执行器 | 控制端通过 Sandcat 等 Agent 下发任务                       |
| 动态决策             | 较弱，通常按预设脚本顺序执行              | Planner 可根据 Facts、Requirements 和 Rules 决定后续步骤    |
| 跨主机执行            | 需要额外编排                      | Operation 可面向一组 Agent，并支持横向移动场景                  |
| 执行记录             | Atomic 执行日志或外部采集            | Operation Report、Event Logs、stdout/stderr 和执行元数据 |
| 适合的 Benchmark 层级 | L1 单主机原子调查；也可作为 L2 的技术组件    | L2 单主机攻击链和 L3 跨主机攻击链                             |
CALDERA 自带的 `atomic` 插件可以导入 Atomic Red Team 的 TTP；`emu` 插件提供 CTID Adversary Emulation Library 中的攻击计划。因此，两者不是互斥关系：Atomic Red Team 可以作为底层技术测试库，CALDERA 则作为攻击链编排与控制平面。
```text
CALDERA Server
    → 向 Agent Group 中的 Sandcat Agent 下发 Ability
    → Agent 在目标终端使用 PowerShell、cmd 或 sh 等 Executor 执行命令
    → Agent 返回状态、stdout 和 stderr
    → Parser 从结果中提取 Facts
    → Planner 根据 Facts、Requirements、Rules 和 Adversary Profile 选择下一步
    → 形成完整 Operation Chain，并导出结构化运行记录
```
默认 Planner 中：
- `atomic` 按 Adversary Profile 的 `atomic_ordering` 顺序执行；
- `batch` 同时调度所有可运行的 Ability；
- `buckets` 按 ATT&CK tactic 对 Ability 分组执行。
这里的 `atomic` 是“按照原子顺序执行”的 Planner 名称，不等同于 CALDERA 的 Atomic Red Team 插件。

CALDERA 服务端应部署在隔离的 Linux/macOS 控制机上，目标 Windows 虚拟机只运行终端 Agent。
```bash
git clone https://github.com/apache/caldera.git --recursive --tag x.x.x
cd caldera
python3 -m venv .calderavenv
source .calderavenv/bin/activate
pip3 install -r requirements.txt
python3 server.py --insecure --build
```

**Ability 的定义**
Ability 是 CALDERA 最小的攻击动作。下面给出一个只创建可观测标记文件的无害示例，用于模拟 `T1059.001 - PowerShell` 执行。该示例不会连接外部网络，也不会获得持久化或提升权限。
![[终端溯源Agent Benchmark-2026-08-11-03-19-19.png]]
```yaml
- id: 3c3ea6fb-67d3-4b56-9b36-b1f2b389ae52
  name: Create benchmark execution marker
  description: Create a harmless marker for terminal investigation
  tactic: execution
  technique:
    attack_id: T1059.001
    name: "Command and Scripting Interpreter: PowerShell"
  platforms:
    windows:
      psh:
        command: |
          $dir = Join-Path $env:ProgramData 'TerminalTraceBenchmark';
          New-Item -ItemType Directory -Path $dir -Force | Out-Null;
          Set-Content -Path (Join-Path $dir 'caldera_marker.txt') -Value "CALDERA_BENCHMARK_#{paw}";
        cleanup: |
          Remove-Item -Path (Join-Path $env:ProgramData 'TerminalTraceBenchmark\caldera_marker.txt') -Force -ErrorAction SilentlyContinue;
        timeout: 30
```

主要字段：
- `id`：Ability 的稳定 UUID，也是 Adversary Profile 引用该动作的标识。
- `tactic` 和 `technique`：对应 ATT&CK 战术、技术编号和名称。
- `platforms`：支持的操作系统和 Executor，例如 Windows/`psh`、Windows/`cmd`、Linux/`sh`。
- `command`：实际执行命令，可使用 `#{paw}`、`#{server}` 或 Fact 变量。
- `payloads`：执行前需要下载到终端的文件。
- `parsers`：从输出中解析新的 Fact。
- `requirements`：运行该 Ability 前必须满足的 Fact 关系。
- `cleanup`：用于恢复环境的逆向操作。
- `timeout`：命令执行超时时间。

**单步模拟**
CALDERA 没有与 `Invoke-AtomicTest Txxxx` 完全等价的单条命令接口。实现单步测试的方式是创建一个仅包含一个 Ability 的 Adversary Profile，然后启动一次 Operation：
```yaml
id: 87b09f04-fd75-48b4-a9ef-92f243d62f74
name: L1 PowerShell marker
description: Single-step benign execution scenario
atomic_ordering:
  - 3c3ea6fb-67d3-4b56-9b36-b1f2b389ae52
```
在 Operation 中选择：
- `Group`：目标 Sandcat Agent 所在的主机组；
- `Adversary`：`L1 PowerShell marker`；
- `Planner`：`atomic`；
- `Autonomous`：调试阶段关闭，由操作者逐条批准；正式复现实验时开启；
- `Run immediately`：立即开始或先以暂停状态创建。
这种方式适合构造 L1 案例，但 CALDERA 的主要优势仍然是多步和跨主机编排。

**多步模拟**
以“季度奖金审核”场景为例，可以将每个攻击语义步骤定义为一个无害 Ability，再使用 Adversary Profile 固定因果顺序：
```text
用户模拟器放置诱饵文件
    → T1059.001 PowerShell 执行
    → T1082 System Information Discovery
    → T1005 Data from Local System
    → T1560.001 Archive via Utility
    → T1053.005 Scheduled Task（仅注册无害 canary）
    → T1071.001 Web Protocols（仅访问隔离 Mock C2）
    → T1041 Exfiltration Over C2 Channel（仅上传假数据）
    → T1070.006 Timestomp
    → T1070.004 File Deletion
```

```yaml
id: 3dca1e26-3970-49f4-bf45-0aa44973bb93
name: Quarterly bonus investigation scenario
description: Harmless multi-step endpoint attack emulation
atomic_ordering:
  - 3c3ea6fb-67d3-4b56-9b36-b1f2b389ae52  # PowerShell execution
  - 7b2805f1-cf67-47f4-8e8b-4d3f6f5ae901  # System discovery
  - f0766f8d-b6bb-4bca-9f1c-9b4ca925e4e2  # Local collection
  - 64fd6884-1f20-424c-b496-7bf2acb05ed6  # Archive
  - e605cc21-0f5b-4fe0-99f1-30d8bcaa52c9  # Harmless scheduled task
  - e9123eb7-40a3-4cf2-8c41-971cf7bd0c66  # Mock C2 heartbeat
  - 8f013f49-fd51-4a65-a6f4-78923fa7ec4d  # Fake-data upload
  - c9ec7360-c783-4d3d-a00d-1df1d56f2a10  # Timestomp
  - 246280a6-bbd1-4e46-a256-3f3f12ce66f0  # Delete lure
```

其中每个 UUID 都应对应一个经过安全审核、可独立验证且具有 Cleanup 的自定义 Ability。运行时选择 `atomic` Planner 可保持预定的因果顺序；如果需要让步骤依赖前序发现，则可在命令中使用 Fact 变量，并使用 Parser 和 Requirement 约束后续 Ability。

多主机场景可以把 Target1 和 Target2 的 Sandcat 放入同一 Operation 管理，通过 Agent Group、`paw` 和主机来源约束区分证据，并在横向移动 Ability 成功后让新 Agent 回连。这样可以表达：
```text
Attacker → Target1 上的初始 Agent
         → Target1 执行发现和凭据模拟
         → 在 Target2 启动新的 Agent
         → Target2 执行、持久化和 C2 模拟
```

需要注意，Sandcat 自己的回连流量是“场景控制流量”，而模拟攻击产生的 C2 是“待调查证据”。Benchmark 应使用不同的网段、端口和服务标识区分两者，并且不应把 Sandcat 的固定通信特征泄露给被评测 Agent。

**CALDERA 的执行记录**
CALDERA 在 Operation 运行过程中记录命令状态和 `stdout`/`stderr`。Operation 完成后可以导出 Operation Report 或 Operation Event Logs；官方文档说明还可从 Operations 界面导出 JSON/CSV，并通过 Debrief 插件查看执行图和生成报告。

可用于构建控制端执行事实的字段包括：
1. Operation 名称、开始时间、Adversary Profile 和目标 Agent Group；
2. Agent 的 `paw`、主机名、用户名、权限、Agent PID、父 PID 和通信方式；
3. Ability ID、名称、ATT&CK tactic、technique ID 和 technique name；
4. 下发、领取和完成时间；
5. 实际命令、平台、Executor 和命令进程 PID；
6. 退出状态、`stdout` 和 `stderr`；
7. Parser 提取的 Facts 和 Operation Chain 中生成的 Links。

这些记录适合作为 ground truth 的“控制端执行账本”，但不能单独证明终端证据真实存在。例如，PowerShell 返回成功不一定意味着计划任务在快照时仍然存在；HTTP 命令执行成功也不一定意味着 Mock C2 实际收到了请求。因此仍需独立验证终端状态和 Mock 服务记录。

中文实操参考：[ATT&CK—Caldera 实操](https://www.freebuf.com/sectool/348940.html)

# 实验

采用三台虚拟机测试。
- 192.168.203.133 作为 Caldera 部署机。
- 192.168.203.134 作为 Kali 靶机。
- 192.168.203.135 作为 Windows 靶机。


![[终端溯源Agent Benchmark-2026-08-18-19-55-43.png]]

| #   | 分类（战术）               | 技术种类数   | 能力总数     | Windows能力数 | 说明    |
| --- | -------------------- | ------- | -------- | ---------- | ----- |
| 1   | stealth              | 23      | 334      | 249        | 隐蔽/规避 |
| 2   | defense-impairment   | 12      | 303      | 195        | 防御削弱  |
| 3   | discovery            | 29      | 294      | 206        | 发现    |
| 4   | credential-access    | 12      | 193      | 128        | 凭据获取  |
| 5   | execution            | 13      | 140      | 93         | 执行    |
| 6   | persistence          | 9       | 127      | 82         | 持久化   |
| 7   | privilege-escalation | 3       | 102      | 67         | 提权    |
| 8   | command-and-control  | 12      | 89       | 66         | C2    |
| 9   | collection           | 13      | 67       | 32         | 收集    |
| 10  | impact               | 8       | 66       | 36         | 影响    |
| 11  | exfiltration         | 5       | 27       | 16         | 数据外渗  |
| 12  | lateral-movement     | 5       | 24       | 23         | 横向移动  |
| 13  | initial-access       | 3       | 7        | 5          | 初始访问  |
| 14  | reconnaissance       | 2       | 2        | 2          | 侦察    |
|     | **合计**               | **149** | **1775** | **1200**   |       

**L1 分级任务**
L1 需要"单主机 + 单一语义步骤 + 稳定可验证痕迹"。从已导入的 1775 个 Atomic ability 中筛选，统一满足以下 4 条硬性标准：
1. **单一安全语义**：一个 Atomic Test 只对应一个 ATT&CK 技术（或其子技术），不含混合语义；
2. **稳定、可验证的终端痕迹**：执行后在终端留下可独立观测、快照后可恢复的证据（注册表项、计划任务、文件、进程、网络连接），而非仅依赖内存态或控制端日志；
3. **无外部依赖**：优先选择纯本地命令（`reg`、`schtasks`、`powershell`），不依赖外部下载、域环境或不可控网络（C2 类场景需将目标改为隔离网络中的 Mock C2）；
4. **可逆/可清理**：Ability 自带 cleanup，执行后可恢复终端状态，便于多实例复用。

[ATT&CK筛选v1.0.xlsx](file:///D:/Tencent/WeChat/xwechat_files/wxid_5vcfi8u0c15k22_651d/msg/file/2026-08/1.0.xlsx)


| 场景 ID     | 名称                           | ATT&CK    | 单一语义                    | 稳定终端痕迹                                                                                                      | 依赖                                       |
| --------- | ---------------------------- | --------- | ----------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **L1-S1** | Reg Key Run                  | T1547.001 | 注册表 Run 键持久化            | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 下新增 "Atomic Red Team" 值，指向 `C:\Path\AtomicRedTeam.exe` | 无（纯 `REG ADD`）                           |
| **L1-S2** | Qakbot Base64 计划任务           | T1053.005 | 计划任务持久化（Qakbot 风格）      | 计划任务 `ATOMIC-T1053.005` + 注册表 `HKCU\SOFTWARE\ATOMIC-T1053.005` 存 Base64 命令                                  | 无（纯 `cmd`）                               |
| **L1-S3** | PowerShell Command Execution | T1059.001 | PowerShell 混淆脚本执行       | PowerShell Event 4103/4104、`powershell.exe` 进程链（父进程为调用方）                                                    | 无（纯本地）                                   |
| **L1-S4** | Malicious User Agents - CMD  | T1071.001 | Web 协议 C2 beacon（恶意 UA） | 4 次 `curl.exe` 进程 + 到 Mock C2 的回环连接、不同 User-Agent 字符串                                                       | 需将目标 `www.google.com` 替换为隔离网络 Mock C2 地址 |

每个 L1 场景封装为一份运行策略。字段如下：
```yaml
scenario_id: L1-S1
title: 注册表 Run 键持久化调查
attack_semantics:             # 单一语义的因果陈述
  technique: T1547.001
  ability_id: 5503b4931592d3d01840133599b87893
  narrative: "攻击者在受害主机 HKCU Run 键写入指向恶意程序的启动项，实现开机自启动持久化。"
initial_alert:                # 稀疏初始告警
  severity: medium
  text: "检测到可疑注册表 Run 键写入，主机 WIN-TARGET-01"
expected_findings:            # 预期关键发现
  - type: registry_run_key
    hive: HKCU
    path: Software\Microsoft\Windows\CurrentVersion\Run
    value_name: Atomic Red Team
    value_data: C:\Path\AtomicRedTeam.exe
    verdict: malicious
evidence_surfaces:            # 涉及终端证据面
  - registry               # 注册表 Run 键
  - file                   # 目标 exe
```

### A. 持久化类（注册表 / 计划任务 / 启动目录）

| 名称                                                                | ATT&CK    | ability_id                         | 核心证据                                                                | 备注                      |
| ----------------------------------------------------------------- | --------- | ---------------------------------- | ------------------------------------------------------------------- | ----------------------- |
| Reg Key Run                                                       | T1547.001 | `5503b4931592d3d01840133599b87893` | HKCU Run 键新增值 `Atomic Red Team` → exe 路径                            | 纯 `REG ADD`，无网络         |
| Reg Key RunOnce                                                   | T1547.001 | `534ee0652aca292fc05421f6f429918b` | HKLM RunOnceEx 新增值 `AtomicRedTeam.dll`                              | 同族，更隐蔽（RunOnce 执行后自动删除） |
| Scheduled Task Executing Base64 Commands From Registry（Qakbot 风格） | T1053.005 | `469f554b1c5e8613d3ec3662e9d9e3e1` | 计划任务 `ATOMIC-T1053.005` + `HKCU\SOFTWARE\ATOMIC-T1053.005` 存 Base64 | 纯 `cmd`；任务解码执行注册表命令     |
| HKLM - Policy Settings Explorer Run Key                           | T1547.001 | `0a3220a423ed7c7804af6e3587ad8811` | HKLM `Policies\Explorer\Run` 新增值                                    | 纯 PowerShell 本地，无网络     |
| HKCU - Policy Settings Explorer Run Key                           | T1547.001 | `25128a85550b87725325e05571803aa3` | HKCU `Policies\Explorer\Run` 新增值                                    | 纯 PowerShell 本地，无网络     |
| Add Executable Shortcut Link to User Startup Folder               | T1547.001 | `1f15ab22c39a9b6bb2bb0d77276dfcb3` | 用户启动目录新增 `calc_exe.lnk` 快捷方式                                        | 痕迹为文件系统，指向 calc.exe     |
### B. 脚本执行类（进程 / 事件日志痕迹）

| 名称                           | ATT&CK    | ability_id                         | 核心证据                                                           | 备注       |
| ---------------------------- | --------- | ---------------------------------- | -------------------------------------------------------------- | -------- |
| PowerShell Command Execution | T1059.001 | `2f5e819a0fdae54834fa85a0b797d302` | `powershell.exe -e <b64>` 进程 + PowerShell Event 4103/4104 记录命令 | 纯本地，混淆命令 |
### C. 网络通信类（进程 + 连接痕迹）

| 名称                          | ATT&CK    | ability_id                         | 核心证据                                   | 备注                                    |
| --------------------------- | --------- | ---------------------------------- | -------------------------------------- | ------------------------------------- |
| Malicious User Agents - CMD | T1071.001 | `36ee81903cf3f729dfa31344b85b94c7` | 4 次 `curl.exe` 进程；到 Mock C2 回环连接；恶意 UA | 需将默认 `www.google.com` 改为隔离 Mock C2 地址 |
### D. 文件 / 下载痕迹类（需构造 canary 文件）


 T1027.004：Compile After Delivery ： MITRE ATT&CK 中 T1027“混淆文件或信息”的子技术。
 攻击者先投递源代码、中间语言或脚本化模块，再利用受害主机上的编译工具将其生成可执行文件。
![[终端溯源Agent Benchmark-2026-08-18-20-36-16.png]]

![[终端溯源Agent Benchmark-2026-08-18-20-38-25.png]]

![[终端溯源Agent Benchmark-2026-08-18-20-40-00.png]]



**L2 分级任务**

```Python
T1547.001  Registry Run Keys / Startup Folder（写入注册表 Run Key，让 payload 在用户登录后自动启动 | 这是典型持久化手法，保证 C2 implant 重启后还能回连）
T1033      System Owner/User Discovery（查看当前用户、权限、组信息 | 攻击者判断权限级别，决定后续能否提权、横向移动或读取敏感目录）
T1082      System Information Discovery(查看系统版本、补丁、主机信息 | 攻击者判断目标环境，选择后续攻击或规避策略)
T1057      Process Discovery(枚举当前进程 | 攻击者寻找杀软、EDR、浏览器、办公软件或高价值进程)
T1016      System Network Configuration Discovery(查看 IP、网卡、DNS、网关 | 攻击者理解目标在内网中的位置)
T1049      System Network Connections Discovery(查看网络连接和 PID | 攻击者确认通信状态，也帮助蓝队把 C2 连接关联到进程）
T1083      File and Directory Discovery（查看目录结构 | 攻击者寻找用户目录、数据位置和后续落点）
```
![[终端溯源Agent Benchmark-2026-08-18-20-09-22.png]]

![[终端溯源Agent Benchmark-2026-08-18-20-07-06.png]]

![[终端溯源Agent Benchmark-2026-08-18-20-07-50.png]]

![[终端溯源Agent Benchmark-2026-08-18-20-10-11.png]]

![[终端溯源Agent Benchmark-2026-08-18-20-11-01.png]]