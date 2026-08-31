---
chain_id: IRCHAIN-L2-COINMINER-SAFE-001
report_id: DFIR-2021-01-18-8404b22d
title: Coinminer 入侵的安全缩减攻击链
source: The DFIR Report
published: 2021-01-18
source_report: Public_IR_Reports/The_DFIR_Report/2021-01-18_all-that-for-a-coinminer.md
source_url: https://thedfirreport.com/2021/01/18/all-that-for-a-coinminer/
use_level: A
scenario_level: L2
platform: windows
atomic_repo_commit: 6132b92779873cb0d05bef07ba0a480d47eb1cc8
generated_at: 2026-08-25
atomic_tests:
  - order: 1
    technique: T1201
    guid: 4588d243-f24e-4549-b2e3-e627acc089f6
    name: Examine local password policy - Windows
    implementation: atomic
    source_confidence: observed
    mutates_state: false
    input_args: {}
    allow_elevation: false
    allow_dependencies: false
  - order: 2
    technique: T1018
    guid: 2d5a61f5-0447-4be4-944a-1f8530ed6574
    name: Remote System Discovery - arp
    implementation: atomic
    source_confidence: observed
    mutates_state: false
    input_args: {}
    allow_elevation: false
    allow_dependencies: false
  - order: 3
    technique: T1059.003
    guid: 127b4afe-2346-4192-815c-69042bec570e
    name: Writes text to a file and displays it.
    implementation: atomic
    source_confidence: observed
    mutates_state: true
    input_args:
      file_contents_path: 'C:\ProgramData\EndpointIRBench\coinminer-safe\svshost.exe'
      message: ENDPOINTIR_BENCH_COINMINER_CANARY
    allow_elevation: false
    allow_dependencies: false
  - order: 4
    technique: T1564.001
    implementation: custom_canary
    source_confidence: observed
    mutates_state: true
    input_args:
      file_to_modify: 'C:\ProgramData\EndpointIRBench\coinminer-safe\svshost.exe'
    custom_cleanup: Clear the hidden attribute and remove only the scenario-owned canary file.
  - order: 5
    technique: T1496
    implementation: not_simulated
    source_confidence: observed
    mutates_state: false
---

# 攻击链示例：Coinminer 入侵的安全缩减攻击链

> 本示例保留“侦察 → 投放 → 隐藏 → 资源劫持意图”的因果关系，但不暴力破解账户、不读取凭证、不横向移动、不运行矿工，也不连接矿池。

## 来源与场景范围

场景来源为 The DFIR Report 的 [本地归档报告](../Public_IR_Reports/The_DFIR_Report/2021-01-18_all-that-for-a-coinminer.md)及[原始网页](https://thedfirreport.com/2021/01/18/all-that-for-a-coinminer/)。原事件包含 RDP 暴力破解、Mimikatz、网络扫描、跨主机 RDP、XMRig 部署和文件隐藏；本示例只选择一台 Windows 主机上的低风险 L2 子链，并明确标记未模拟的高风险动作。

## 报告原始攻击链

| 顺序 | 报告行为 | 置信度 | 报告依据 | 是否保留 |
|---:|---|---|---|---|
| 1 | 攻击者暴力破解本地管理员并通过 RDP 登录 | observed | “Initial Access” | 不保留 |
| 2 | Mimikatz 导出登录密码和 Kerberos 票据 | observed | “Credential Access” | 不保留 |
| 3 | 执行 `net accounts` 并使用 Advanced IP Scanner 扫描环境 | observed | “Discovery” | 安全缩减保留 |
| 4 | 通过 RDP 进入多台主机 | observed | “Lateral Movement” | 不保留 |
| 5 | 在初始主机部署 XMRig 相关文件并运行 `HideAll.bat` 隐藏文件 | observed | “Execution”“Defense Evasion”“Impact” | canary 替代 |
| 6 | XMRig 使用 CPU 并尝试连接外部矿池 IP | observed | “Impact” | 标记为未模拟 |

## 可执行攻击语义链

```text
本地密码策略发现（T1201）
  → ARP 邻居发现（T1018，替代主动扫描）
  → 矿工命名的纯文本 canary 落盘（T1059.003）
  → 隐藏场景专属 canary（T1564.001，自定义安全步骤）
  → 资源劫持意图（T1496，仅记录，不执行）
```

## Atomic Red Team 映射

| # | 语义动作 | ATT&CK | Atomic 名称/GUID | 平台与执行器 | 参数调整 | 预期证据 | Cleanup |
|---:|---|---|---|---|---|---|---|
| 1 | 查询本地密码策略 | T1201 | `Examine local password policy - Windows` / `4588d243-f24e-4549-b2e3-e627acc089f6` | Windows / command_prompt | 无 | `cmd.exe → net.exe accounts` | 不修改状态 |
| 2 | 发现邻近系统 | T1018 | `Remote System Discovery - arp` / `2d5a61f5-0447-4be4-944a-1f8530ed6574` | Windows / command_prompt | 以读取 ARP 缓存替代主动 IP 扫描 | `cmd.exe → arp.exe -a` | 不修改状态 |
| 3 | 创建矿工载荷替身 | T1059.003 | `Writes text to a file and displays it.` / `127b4afe-2346-4192-815c-69042bec570e` | Windows / command_prompt | 输出到场景目录中的文本 `svshost.exe` | 文件创建、固定 canary 内容和 `cmd.exe` | Atomic 自带删除命令 |
| 4 | 隐藏 canary | T1564.001 | `custom_canary`，无 Atomic GUID | Windows / command_prompt | 只对上一步 canary 执行 `attrib.exe +h` | 文件 Hidden 属性和 `attrib.exe` 命令行 | `attrib.exe -h`，随后删除 canary |
| 5 | 表达资源劫持目标 | T1496 | `not_simulated`，无 Atomic GUID | 不执行 | 不启动矿工、不制造 CPU 压力、不连接矿池 | 无主机执行证据；仅存在场景元数据 | 无需 Cleanup |

## 安全与适配说明

- 暴力破解、真实账户登录、密码修改、Mimikatz、Kerberos 票据导出和跨主机 RDP 全部删除，不产生或访问任何真实凭证。
- Advanced IP Scanner 被只读的 `arp -a` 替代；该步骤不会主动扫描网段或访问其他主机。
- `svshost.exe` 只是包含 `ENDPOINTIR_BENCH_COINMINER_CANARY` 的文本文件，不能执行，也不包含 XMRig 或报告样本内容。
- 本地 Atomic 的 Windows 隐藏文件测试需要依赖准备和提权，因此本例不强行套用该 GUID，而使用边界更窄的 `attrib.exe +h` 自定义 canary 步骤。
- T1496 明确设置为 `not_simulated`；不得启动真实矿工、压力测试程序或外部网络连接，并且评分中不得声称观测到了 CPU 挖矿。

## Ground Truth

| ID | 必需性 | 实体与精确值 | 证据面 | 时间关系 | 独立验证方式 |
|---|---|---|---|---|---|
| F1 | 必需 | `net accounts` | Sysmon、4688 或 EDR | 链首 | 核验 `cmd.exe` 子进程与完整命令行 |
| F2 | 必需 | `arp.exe -a` | 进程创建遥测 | F1 之后、文件落盘之前 | 按进程时间戳和父子关系验证 |
| F3 | 必需 | `C:\ProgramData\EndpointIRBench\coinminer-safe\svshost.exe`，内容含 `ENDPOINTIR_BENCH_COINMINER_CANARY` | 文件系统 | F2 之后创建 | `Test-Path`、`Get-Content`，不依赖 Atomic 返回值 |
| F4 | 必需 | F3 文件具有 Hidden 属性 | 文件元数据 | F3 创建后 | `(Get-Item -Force <path>).Attributes` 包含 `Hidden` |
| F5 | 必需 | `attrib.exe +h` 仅作用于 F3 路径 | 进程创建遥测 | 紧随 F3 | 核验命令行目标和时间戳 |
| F6 | 反向约束 | 不存在矿工进程、矿池连接或跨主机 RDP | 进程、网络和登录日志 | 全场景 | 对进程名、外连目的地和登录事件做负向核验 |

## 调查任务

初始告警为：“`WIN-TARGET-03` 上的命令解释器在 ProgramData 创建了一个名称近似系统程序的隐藏文件。”调查 Agent 需要判断该文件能否执行、还原其创建与隐藏过程、识别此前的策略和邻居发现行为，并用证据说明该场景是否真的发生了凭证访问、横向移动或资源劫持。

## 执行与清理计划

只在启用进程创建遥测的可恢复 Windows 测试虚拟机运行，执行前创建干净快照。以下是审阅用规格；T1496 不对应任何执行命令：

```powershell
$ScenarioDir = 'C:\ProgramData\EndpointIRBench\coinminer-safe'
New-Item -ItemType Directory -Force -Path $ScenarioDir | Out-Null

Invoke-AtomicTest T1201 -TestGuids 4588d243-f24e-4549-b2e3-e627acc089f6
Invoke-AtomicTest T1018 -TestGuids 2d5a61f5-0447-4be4-944a-1f8530ed6574
Invoke-AtomicTest T1059.003 -TestGuids 127b4afe-2346-4192-815c-69042bec570e -InputArgs @{
  file_contents_path = "$ScenarioDir\svshost.exe"
  message = 'ENDPOINTIR_BENCH_COINMINER_CANARY'
}
attrib.exe +h "$ScenarioDir\svshost.exe"
```

调查和证据导出完成后，先移除 Hidden 属性，再运行 Atomic Cleanup，并只删除场景目录：

```powershell
attrib.exe -h "$ScenarioDir\svshost.exe"
Invoke-AtomicTest T1059.003 -TestGuids 127b4afe-2346-4192-815c-69042bec570e -Cleanup -InputArgs @{
  file_contents_path = "$ScenarioDir\svshost.exe"
  message = 'ENDPOINTIR_BENCH_COINMINER_CANARY'
}
Remove-Item -LiteralPath $ScenarioDir -Recurse -Force -ErrorAction SilentlyContinue
```

## 未覆盖与人工复核项

- 未模拟 RDP 初始访问、密码喷洒、账户创建或密码修改，因此不能用本例评价登录溯源或账户接管能力。
- 未模拟 Mimikatz 和票据导出，因此不应生成或评分任何真实凭证、LSASS 访问或 Kerberos 文件证据。
- ARP 缓存查询的保真度低于 Advanced IP Scanner；它只保留“执行前环境发现”的语义，不代表主动端口扫描。
- T1496 是报告事实但不是执行步骤；如果未来需要评价资源劫持调查，应另行设计经过性能和安全审查的有界工作负载，而不能把本例的 canary 当作挖矿证据。
