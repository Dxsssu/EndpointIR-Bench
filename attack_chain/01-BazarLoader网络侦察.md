---
chain_id: IRCHAIN-L2-BAZAR-RECON-001
report_id: UNIT42-2021-10-18-o-Network-Reconnaissance
title: BazarLoader 风格单主机持久化与网络侦察
source: Unit 42
published: 2021-10-18
source_report: Public_IR_Reports/Unit42/BazarLoader-to-Network-Reconnaissance.md
source_url: https://unit42.paloaltonetworks.com/bazarloader-network-reconnaissance/
use_level: A
scenario_level: L2
platform: windows
atomic_repo_commit: 6132b92779873cb0d05bef07ba0a480d47eb1cc8
generated_at: 2026-08-25
atomic_tests:
  - order: 1
    technique: T1059.003
    guid: 127b4afe-2346-4192-815c-69042bec570e
    name: Writes text to a file and displays it.
    implementation: atomic
    source_confidence: observed
    mutates_state: true
    input_args:
      file_contents_path: 'C:\ProgramData\EndpointIRBench\bazarloader-recon\tru.dll'
      message: ENDPOINTIR_BENCH_BAZAR_CANARY
    allow_elevation: false
    allow_dependencies: false
  - order: 2
    technique: T1547.001
    guid: e55be3fd-3521-4610-9d1a-e210e42dcf05
    name: Reg Key Run
    implementation: atomic
    source_confidence: observed
    mutates_state: true
    input_args:
      command_to_execute: 'cmd.exe /c type C:\ProgramData\EndpointIRBench\bazarloader-recon\tru.dll > C:\ProgramData\EndpointIRBench\bazarloader-recon\beacon-started.txt'
    allow_elevation: false
    allow_dependencies: false
  - order: 3
    technique: T1082
    guid: 66703791-c902-4560-8770-42b8a91f7667
    name: System Information Discovery
    implementation: atomic
    source_confidence: reported
    mutates_state: false
    input_args: {}
    allow_elevation: false
    allow_dependencies: false
  - order: 4
    technique: T1016
    guid: 970ab6a1-0157-4f3f-9a73-ec4166754b23
    name: System Network Configuration Discovery on Windows
    implementation: atomic
    source_confidence: reported
    mutates_state: false
    input_args: {}
    allow_elevation: false
    allow_dependencies: false
  - order: 5
    technique: T1018
    guid: 2d5a61f5-0447-4be4-944a-1f8530ed6574
    name: Remote System Discovery - arp
    implementation: atomic
    source_confidence: observed
    mutates_state: false
    input_args: {}
    allow_elevation: false
    allow_dependencies: false
  - order: 6
    technique: T1071.001
    guid: 81c13829-f6c9-45b8-85a6-053366d55297
    name: Malicious User Agents - Powershell
    implementation: atomic
    source_confidence: observed
    mutates_state: false
    input_args:
      domain: http://127.0.0.1:18088/beacon
    allow_elevation: false
    allow_dependencies: false
---

# 攻击链示例：BazarLoader 风格单主机持久化与网络侦察

> 本文档是攻击链生成 Skill 的完整输出示例，也是现有 `scenarios/l2-bazarloader-recon/` 场景的文档化版本。它只描述面向隔离测试虚拟机的无害模拟方案，不代表已经执行。

## 来源与场景范围

场景来源为 Unit 42 的 [本地归档报告](../Public_IR_Reports/Unit42/BazarLoader-to-Network-Reconnaissance.md)及[原始网页](https://unit42.paloaltonetworks.com/bazarloader-network-reconnaissance/)。报告记录了恶意 Excel 宏投递 BazarLoader、注册表持久化、Cobalt Strike 通信和 AD 环境侦察；本示例将其缩减为一台 Windows 主机上的 L2 因果链，不复现真实恶意代码、外部 C2、凭据访问、横向移动或勒索行为。

## 报告原始攻击链

| 顺序 | 报告行为 | 置信度 | 报告依据 | 是否保留 |
|---:|---|---|---|---|
| 1 | 用户启用恶意 XLSB 宏，宏下载 `tru.dll` 并通过 `regsvr32.exe` 启动 | observed | “Malicious Excel Spreadsheet”“BazarLoader Binary” | 语义替代 |
| 2 | BazarLoader DLL 被复制并通过 Windows 注册表建立持久化 | observed | “BazarLoader Binary” | 保留 |
| 3 | 主机与 Bazar/Cobalt Strike 基础设施进行 HTTPS C2 通信 | observed | “Bazar C2 Traffic”“Cobalt Strike Activity” | 端点替代 |
| 4 | `AdFind.exe` 和 `adf.bat` 枚举用户、计算机、共享、OU、组和信任关系 | observed | “Reconnaissance Activity”及 `adf.bat` 命令清单 | 缩减保留 |
| 5 | 高价值目标可能发生横向移动或勒索 | inferred | “Executive Summary”“Conclusion”；该案例实际未发生 | 不保留 |

## 可执行攻击语义链

```text
无害 DLL 命名 canary 落盘（T1059.003）
  → HKCU Run Key 持久化（T1547.001）
  → 系统信息发现（T1082）
  → 网络配置发现（T1016）
  → ARP 邻居发现（T1018）
  → 回环 Mock HTTP C2（T1071.001）
```

## Atomic Red Team 映射

| # | 语义动作 | ATT&CK | Atomic 名称/GUID | 平台与执行器 | 参数调整 | 预期证据 | Cleanup |
|---:|---|---|---|---|---|---|---|
| 1 | 生成无害载荷替身 | T1059.003 | `Writes text to a file and displays it.` / `127b4afe-2346-4192-815c-69042bec570e` | Windows / command_prompt | 将输出改为场景目录中的纯文本 `tru.dll` | `cmd.exe`、文件创建及固定 canary 内容 | Atomic 自带删除命令 |
| 2 | 建立当前用户自启动项 | T1547.001 | `Reg Key Run` / `e55be3fd-3521-4610-9d1a-e210e42dcf05` | Windows / command_prompt | Run 值只指向读取 canary 的无害命令 | `HKCU\...\Run` 下的 `Atomic Red Team` 值 | Atomic 自带注册表删除命令 |
| 3 | 查询主机信息 | T1082 | `System Information Discovery` / `66703791-c902-4560-8770-42b8a91f7667` | Windows / command_prompt | 无 | `systeminfo.exe` 和注册表查询活动 | 不修改状态 |
| 4 | 查询网络配置 | T1016 | `System Network Configuration Discovery on Windows` / `970ab6a1-0157-4f3f-9a73-ec4166754b23` | Windows / command_prompt | 无 | `ipconfig.exe`、`netsh.exe`、`arp.exe`、`nbtstat.exe` | 不修改状态 |
| 5 | 查询 ARP 邻居 | T1018 | `Remote System Discovery - arp` / `2d5a61f5-0447-4be4-944a-1f8530ed6574` | Windows / command_prompt | 用本地 ARP 缓存替代完整 AD 枚举 | `cmd.exe` 启动 `arp.exe -a` | 不修改状态 |
| 6 | 模拟应用层 C2 | T1071.001 | `Malicious User Agents - Powershell` / `81c13829-f6c9-45b8-85a6-053366d55297` | Windows / PowerShell | 将默认公网域名改为 `127.0.0.1:18088/beacon` | 四次回环 HTTP 请求及不同 User-Agent | 不修改状态；停止 Mock 服务 |

## 安全与适配说明

- 恶意 XLSB、宏、BazarLoader DLL 和 Cobalt Strike DLL均未执行；`tru.dll` 只是带 DLL 扩展名的纯文本 canary。
- 报告中的公网 IP、域名和下载地址均不使用，C2 语义仅由 `127.0.0.1:18088` 上的隔离 Mock HTTP 服务表达。
- 完整 AdFind/Active Directory 枚举被缩减为只读的主机信息、网络配置和 ARP 缓存查询，不触碰其他主机。
- 所选测试不需要管理员权限或外部依赖。唯一的持久化修改位于当前用户 HKCU Run Key，并具有精确 Cleanup。
- 所有文件限定在 `C:\ProgramData\EndpointIRBench\bazarloader-recon`；不得在生产终端或含真实用户数据的主机执行。

## Ground Truth

| ID | 必需性 | 实体与精确值 | 证据面 | 时间关系 | 独立验证方式 |
|---|---|---|---|---|---|
| F1 | 必需 | `C:\ProgramData\EndpointIRBench\bazarloader-recon\tru.dll`，内容含 `ENDPOINTIR_BENCH_BAZAR_CANARY` | 文件系统 | 首个动作产生，早于持久化与侦察 | `Test-Path` 与 `Get-Content`，不读取 Atomic 控制端输出 |
| F2 | 必需 | `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` 的 `Atomic Red Team` 值，数据为 frontmatter 中的无害命令 | 注册表 | F1 之后、侦察之前 | `Get-ItemProperty` 直接读取注册表 |
| F3 | 必需 | 到 `127.0.0.1:18088/beacon` 的四次请求，User-Agent 分别匹配 Atomic 测试中的四个值 | Mock 服务访问日志 | 侦察动作之后 | 由独立 Mock 服务记录请求时间、路径和 User-Agent |
| F4 | 必需 | `cmd.exe → systeminfo.exe/reg.exe/ipconfig.exe/netsh.exe/arp.exe/nbtstat.exe` 以及 `powershell.exe` 活动 | Sysmon、Windows 进程创建审计或 EDR | 顺序与语义链一致 | 从终端遥测按进程 ID、父进程和时间戳重建，不使用 Runner 成功状态 |
| F5 | 可选 | `beacon-started.txt` | 文件系统 | Run Key 在登录触发后产生 | `Test-Path` 和文件时间戳；未触发重新登录时允许缺失 |

## 调查任务

初始告警仅提供：“`WIN-TARGET-01` 上出现可疑命令解释器，并在 ProgramData 下创建了一个 DLL 命名文件。”调查 Agent 需要确认入口文件是否为真实可执行载荷、识别持久化位置、还原侦察命令与先后关系、确认网络目标是否离开主机，并判断证据是否支持横向移动或勒索已经发生。

## 执行与清理计划

前提：仅使用可恢复的 Windows 测试虚拟机；先创建干净快照，配置进程创建遥测，并在本机 `127.0.0.1:18088` 启动能够记录请求的 Mock HTTP 服务。下列命令是审阅用执行规格，不在生成本文档时运行；项目中已有带确认门槛的编排器 [`scenarios/l2-bazarloader-recon/run.ps1`](../scenarios/l2-bazarloader-recon/run.ps1)。

```powershell
$ScenarioDir = 'C:\ProgramData\EndpointIRBench\bazarloader-recon'
New-Item -ItemType Directory -Force -Path $ScenarioDir | Out-Null

Invoke-AtomicTest T1059.003 -TestGuids 127b4afe-2346-4192-815c-69042bec570e -InputArgs @{
  file_contents_path = "$ScenarioDir\tru.dll"
  message = 'ENDPOINTIR_BENCH_BAZAR_CANARY'
}
Invoke-AtomicTest T1547.001 -TestGuids e55be3fd-3521-4610-9d1a-e210e42dcf05 -InputArgs @{
  command_to_execute = "cmd.exe /c type $ScenarioDir\tru.dll > $ScenarioDir\beacon-started.txt"
}
Invoke-AtomicTest T1082 -TestGuids 66703791-c902-4560-8770-42b8a91f7667
Invoke-AtomicTest T1016 -TestGuids 970ab6a1-0157-4f3f-9a73-ec4166754b23
Invoke-AtomicTest T1018 -TestGuids 2d5a61f5-0447-4be4-944a-1f8530ed6574
Invoke-AtomicTest T1071.001 -TestGuids 81c13829-f6c9-45b8-85a6-053366d55297 -InputArgs @{
  domain = 'http://127.0.0.1:18088/beacon'
}
```

调查完成并导出现场证据后，先执行 Atomic 的精确 Cleanup，再删除场景专属目录并停止 Mock 服务：

```powershell
Invoke-AtomicTest T1547.001 -TestGuids e55be3fd-3521-4610-9d1a-e210e42dcf05 -Cleanup -InputArgs @{
  command_to_execute = "cmd.exe /c type $ScenarioDir\tru.dll > $ScenarioDir\beacon-started.txt"
}
Invoke-AtomicTest T1059.003 -TestGuids 127b4afe-2346-4192-815c-69042bec570e -Cleanup -InputArgs @{
  file_contents_path = "$ScenarioDir\tru.dll"
  message = 'ENDPOINTIR_BENCH_BAZAR_CANARY'
}
Remove-Item -LiteralPath $ScenarioDir -Recurse -Force -ErrorAction SilentlyContinue
```

## 未覆盖与人工复核项

- 未复现 Office 宏、`regsvr32.exe` 加载恶意 DLL、BazarLoader/Cobalt Strike 内存行为及真实 C2 TLS 特征。
- ARP 和本机网络配置查询只能保留“环境侦察”语义，不能等价于报告中的 AdFind 域枚举；评分时不得把 AD 用户、组、共享或信任关系列为必需发现。
- F4 依赖测试镜像已启用可靠的进程创建遥测；若镜像未配置 Sysmon、4688 审计或 EDR，应在发布 Benchmark 前补齐，而不是降低 Ground Truth 要求。
- 示例不包含横向移动或勒索，因为源报告明确指出该案例未发生后续勒索，相关内容不得作为事实补入攻击链。
