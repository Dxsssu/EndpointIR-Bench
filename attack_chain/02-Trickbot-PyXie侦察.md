---
chain_id: IRCHAIN-L2-TRICKY-PYXIE-RECON-001
report_id: DFIR-2020-04-30-52b6b755
title: Trickbot/PyXie 风格主机与网络侦察
source: The DFIR Report
published: 2020-04-30
source_report: Public_IR_Reports/The_DFIR_Report/2020-04-30_tricky-pyxie.md
source_url: https://thedfirreport.com/2020/04/30/tricky-pyxie/
use_level: A
scenario_level: L2
platform: windows
atomic_repo_commit: 6132b92779873cb0d05bef07ba0a480d47eb1cc8
generated_at: 2026-08-25
atomic_tests:
  - order: 1
    technique: T1069.002
    guid: dd66d77d-8998-48c0-8024-df263dc2ce5d
    name: Basic Permission Groups Discovery Windows (Domain)
    implementation: atomic
    source_confidence: observed
    mutates_state: false
    input_args: {}
    allow_elevation: false
    allow_dependencies: false
  - order: 2
    technique: T1057
    guid: c5806a4f-62b8-4900-980b-c7ec004e9908
    name: Process Discovery - tasklist
    implementation: atomic
    source_confidence: observed
    mutates_state: false
    input_args: {}
    allow_elevation: false
    allow_dependencies: false
  - order: 3
    technique: T1082
    guid: 66703791-c902-4560-8770-42b8a91f7667
    name: System Information Discovery
    implementation: atomic
    source_confidence: observed
    mutates_state: false
    input_args: {}
    allow_elevation: false
    allow_dependencies: false
  - order: 4
    technique: T1016
    guid: 970ab6a1-0157-4f3f-9a73-ec4166754b23
    name: System Network Configuration Discovery on Windows
    implementation: atomic
    source_confidence: observed
    mutates_state: false
    input_args: {}
    allow_elevation: false
    allow_dependencies: false
  - order: 5
    technique: T1135
    guid: 20f1097d-81c1-405c-8380-32174d493bbb
    name: Network Share Discovery command prompt
    implementation: atomic
    source_confidence: observed
    mutates_state: false
    input_args:
      computer_name: localhost
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
      domain: http://127.0.0.1:18089/beacon
    allow_elevation: false
    allow_dependencies: false
---

# 攻击链示例：Trickbot/PyXie 风格主机与网络侦察

> 本文档是从公开报告抽取的安全模拟规格。它不加载 Trickbot、Cobalt Strike、PyXie 或 Sharphound，也不会连接报告中的任何公网基础设施。

## 来源与场景范围

场景来源为 The DFIR Report 的 [本地归档报告](../Public_IR_Reports/The_DFIR_Report/2020-04-30_tricky-pyxie.md)及[原始网页](https://thedfirreport.com/2020/04/30/tricky-pyxie/)。报告明确列出了 Cobalt Strike 会话中的 Windows 侦察命令和 PyXie C2 行为；本例只保留一台 Windows/AD 测试主机上的只读侦察与回环 C2，构成 L2 单主机链。

## 报告原始攻击链

| 顺序 | 报告行为 | 置信度 | 报告依据 | 是否保留 |
|---:|---|---|---|---|
| 1 | Trickbot 在实验环境执行、迁移自身，并注入系统进程后持续 beacon | observed | “Initial infection” | 不保留恶意实现 |
| 2 | Trickbot 通过 PowerShell 投递内存中的 Cobalt Strike | observed | “Group 2 Arrives” | 不保留投递与注入 |
| 3 | Cobalt Strike 运行 `whoami /groups`、`tasklist`、`systeminfo`、`ipconfig`、`net view` 等侦察命令 | observed | 报告给出的完整命令清单 | 缩减保留 |
| 4 | 攻击者保存 SAM、SYSTEM、SECURITY 注册表配置单元并运行 Sharphound | observed | “Group 2 Arrives”“Sharphound” | 不保留 |
| 5 | PyXie 使用 TLS C2，并携带主机、域、权限和 AV 信息 | observed | “PyXie / C2” | 仅保留回环通信语义 |
| 6 | 报告推测最终目标可能是勒索软件 | inferred | “Conclusion” | 不保留 |

## 可执行攻击语义链

```text
域组发现（T1069.002）
  → 进程发现（T1057）
  → 系统信息发现（T1082）
  → 网络配置发现（T1016）
  → 本机共享发现（T1135）
  → 回环 Mock HTTP C2（T1071.001）
```

## Atomic Red Team 映射

| # | 语义动作 | ATT&CK | Atomic 名称/GUID | 平台与执行器 | 参数调整 | 预期证据 | Cleanup |
|---:|---|---|---|---|---|---|---|
| 1 | 查询本地组和域高权限组 | T1069.002 | `Basic Permission Groups Discovery Windows (Domain)` / `dd66d77d-8998-48c0-8024-df263dc2ce5d` | Windows / command_prompt | 无；要求测试机已加入隔离域 | `net.exe`/`net1.exe` 的组查询命令行 | 不修改状态 |
| 2 | 枚举进程 | T1057 | `Process Discovery - tasklist` / `c5806a4f-62b8-4900-980b-c7ec004e9908` | Windows / command_prompt | 无 | `cmd.exe` 启动 `tasklist.exe` | 不修改状态 |
| 3 | 查询系统信息 | T1082 | `System Information Discovery` / `66703791-c902-4560-8770-42b8a91f7667` | Windows / command_prompt | 无 | `systeminfo.exe` 和 `reg.exe query` | 不修改状态 |
| 4 | 查询网络配置 | T1016 | `System Network Configuration Discovery on Windows` / `970ab6a1-0157-4f3f-9a73-ec4166754b23` | Windows / command_prompt | 无 | `ipconfig.exe`、`netsh.exe`、`arp.exe`、`nbtstat.exe` | 不修改状态 |
| 5 | 查询共享 | T1135 | `Network Share Discovery command prompt` / `20f1097d-81c1-405c-8380-32174d493bbb` | Windows / command_prompt | 将目标限定为 `localhost` | `net.exe view \\localhost` | 不修改状态 |
| 6 | 模拟 beacon | T1071.001 | `Malicious User Agents - Powershell` / `81c13829-f6c9-45b8-85a6-053366d55297` | Windows / PowerShell | 将域名替换为 `127.0.0.1:18089/beacon` | 四次回环 HTTP 请求和不同 User-Agent | 不修改状态；停止 Mock 服务 |

## 安全与适配说明

- 不执行恶意样本、PowerShell 下载、进程注入、注册表配置单元导出、Sharphound 或任何凭证访问。
- 报告中的域名和 IP 不作为模拟目标；全部应用层通信只进入 `127.0.0.1:18089`。
- 报告中的域级 `net view /all /domain` 被缩减为 `net view \\localhost`，避免访问其他主机；因此只保留“共享发现”语义，不声称完成域共享枚举。
- 域组发现只允许在专用、隔离的测试 AD 中运行；如果测试机未加入该域，执行器应跳过该步骤并记录环境不满足，而不是改查生产域。
- 六个测试均无外部下载依赖、无需提权且不产生持久化修改。

## Ground Truth

| ID | 必需性 | 实体与精确值 | 证据面 | 时间关系 | 独立验证方式 |
|---|---|---|---|---|---|
| F1 | 必需 | `net localgroup`、`net group /domain`、`net group "enterprise admins" /domain`、`net group "domain admins" /domain` | Sysmon、4688 或 EDR | 链首，早于其他侦察 | 终端进程创建遥测中的完整命令行 |
| F2 | 必需 | `tasklist.exe`、`systeminfo.exe`、`reg.exe`、`ipconfig.exe`、`netsh.exe`、`arp.exe`、`nbtstat.exe` | 进程创建遥测 | 按步骤 2–4 顺序出现 | 按 PID、父进程和时间戳独立重建 |
| F3 | 必需 | `net view \\localhost` | 进程创建遥测 | 网络配置发现之后 | 终端命令行与目标参数核验 |
| F4 | 必需 | `127.0.0.1:18089/beacon` 上四次请求及四个 Atomic User-Agent | Mock 服务日志 | 所有侦察动作之后 | 独立 Mock 服务记录时间、路径、来源与 User-Agent |
| F5 | 可选 | 域组查询的返回对象 | 命令标准输出或 EDR 捕获 | F1 同时 | 仅在隔离域预置对象可重复时评分 |

## 调查任务

初始告警为：“`WIN-TARGET-02` 在短时间内连续启动多个系统枚举工具，并随后出现本机 HTTP 请求。”调查 Agent 需要识别被枚举的主机、进程、域组和共享，判断通信是否离开本机，重建六个行为的顺序，并说明为何现有证据不足以断言发生了凭证访问、横向移动或勒索。

## 执行与清理计划

只在启用进程创建审计的可恢复 Windows 测试虚拟机中运行；如保留域组步骤，虚拟机必须加入专用测试域。执行前创建快照，并在 `127.0.0.1:18089` 启动记录请求的 Mock HTTP 服务。以下命令仅作为审阅后的执行规格：

```powershell
Invoke-AtomicTest T1069.002 -TestGuids dd66d77d-8998-48c0-8024-df263dc2ce5d
Invoke-AtomicTest T1057 -TestGuids c5806a4f-62b8-4900-980b-c7ec004e9908
Invoke-AtomicTest T1082 -TestGuids 66703791-c902-4560-8770-42b8a91f7667
Invoke-AtomicTest T1016 -TestGuids 970ab6a1-0157-4f3f-9a73-ec4166754b23
Invoke-AtomicTest T1135 -TestGuids 20f1097d-81c1-405c-8380-32174d493bbb -InputArgs @{
  computer_name = 'localhost'
}
Invoke-AtomicTest T1071.001 -TestGuids 81c13829-f6c9-45b8-85a6-053366d55297 -InputArgs @{
  domain = 'http://127.0.0.1:18089/beacon'
}
```

这些步骤不写入持久化主机状态，因此调查证据导出后只需停止 Mock 服务并恢复快照；若运行框架生成了控制端日志，应与终端 Ground Truth 分开保存。

## 未覆盖与人工复核项

- 进程注入、Cobalt Strike、PyXie TLS 指纹、注册表配置单元导出和 Sharphound 均未复现，也不得据此评分。
- 本机共享查询的保真度低于报告中的域级共享发现；需要域级证据的 Benchmark 应单独设计经授权的多主机场景。
- 本链主要产生进程和网络日志，执行前必须确认 Sysmon、4688 审计或 EDR 以及 Mock 服务日志稳定可用；否则所需证据会随进程退出而丢失。
- 报告中的勒索目标属于推测，不得补写为实际发生的攻击步骤。
