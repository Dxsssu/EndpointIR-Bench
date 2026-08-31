# L2-BAZAR-RECON-001

这是从 Unit 42 的 *From BazarLoader to Network Reconnaissance* 提炼出的单主机 L2 场景。它保留“执行 → 注册表持久化 → 主机/网络发现 → HTTP C2”的因果骨架，但不执行 Office 宏、不加载 BazarLoader/Cobalt Strike，也不访问外部网络。

## 简化攻击链

```text
无害 DLL 命名文件落盘（T1059.003）
    → HKCU Run Key 持久化（T1547.001）
    → 系统信息发现（T1082）
    → 网络配置发现（T1016）
    → ARP 邻居发现（T1018）
    → 回环 Mock C2（T1071.001）
```

报告中的恶意 XLSB、宏、Regsvr32 DLL、BazarLoader 和 Cobalt Strike 均未复现。场景会创建一个纯文本的 `Documents new.xlsb` 诱饵和一个纯文本的 `tru.dll` canary，因此文件扩展名不代表真实 Office 文档或 DLL。

## 安全边界

- 仅在可恢复的 Windows 测试虚拟机运行。
- 所有网络请求只发送到 `127.0.0.1:18088`。
- 六个 Atomic 测试均不需要管理员权限或外部依赖。
- 唯一持久化修改是当前用户的 `HKCU Run` 值，并提供显式 Cleanup。
- 不包含漏洞利用、凭据读取、横向移动、数据外传或加密。

## 运行

前提是目标 Windows VM 已安装并导入 `Invoke-AtomicRedTeam`，且本仓库的 `atomic-red-team/atomics` 对该 VM 可见。

先查看不会修改系统的执行计划：

```powershell
.\run.ps1 -Mode Plan
```

在一次性快照中执行：

```powershell
.\run.ps1 `
  -Mode Execute `
  -ConfirmExecution `
  -PathToAtomicsFolder 'D:\EndpointIR-Bench\atomic-red-team\atomics'
```

执行结束后，`verify.ps1` 会自动验证 canary 文件、注册表持久化、执行记录和四次 Mock C2 请求，并把结果保存到：

```text
C:\ProgramData\EndpointIRBench\bazarloader-recon\verification.json
```

应先保留现场供调查 Agent 使用；调查完成后再清理：

```powershell
.\run.ps1 `
  -Mode Cleanup `
  -PathToAtomicsFolder 'D:\EndpointIR-Bench\atomic-red-team\atomics'
```

## 本地静态校验

在非 Windows 控制机上可以确认场景引用的 Atomic GUID、平台、依赖和网络目标：

```bash
python3 scenarios/l2-bazarloader-recon/validate_scenario.py
```
