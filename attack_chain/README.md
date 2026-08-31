# Atomic Red Team 攻击链示例集

本目录收录三个从公开溯源报告提取的 L2 单主机攻击链示例。每个文档都区分报告事实、ATT&CK 语义、Atomic 实现和可独立验证的 Ground Truth；其中涉及恶意载荷、外部 C2、凭证访问、横向移动或资源劫持的部分均被替代、缩减或明确标记为不模拟。

| # | 示例 | 报告来源 | 核心链路 | Atomic 步骤 | 安全处理重点 |
|---:|---|---|---|---:|---|
| 1 | [BazarLoader 网络侦察](01-BazarLoader网络侦察.md) | Unit 42 | canary 落盘 → Run Key → 主机/网络发现 → Mock C2 | 6 | 不执行宏、恶意 DLL 或公网 C2 |
| 2 | [Trickbot/PyXie 侦察](02-Trickbot-PyXie侦察.md) | The DFIR Report | 域组 → 进程 → 系统/网络 → 本机共享 → Mock C2 | 6 | 删除注入、凭证导出和 Sharphound，共享目标限于 localhost |
| 3 | [Coinminer 安全缩减](03-Coinminer入侵安全缩减.md) | The DFIR Report | 策略发现 → ARP → canary → 隐藏 → 资源劫持意图 | 3 Atomic + 1 custom | 不模拟凭证访问、跨主机 RDP、真实矿工或矿池连接 |

## 使用方式

这些文档是场景设计和批量生成格式的示例，不代表攻击已经执行。若用于 Benchmark，应先由安全专家复核，再在有快照、可恢复且与外部网络隔离的测试虚拟机上按照各文档的执行与清理计划操作。

统一静态校验命令：

```bash
python3 ir-report-to-atomic-chain/scripts/validate_chain_docs.py \
  --repo-root /Users/sssu/Project/EndpointIR-Bench \
  攻击链示例/01-BazarLoader网络侦察.md \
  攻击链示例/02-Trickbot-PyXie侦察.md \
  攻击链示例/03-Coinminer入侵安全缩减.md
```

校验覆盖本地报告路径、必需章节、Atomic 仓库提交、GUID、测试名称、平台、输入参数、依赖、提权要求、Cleanup 和外部网络目标。
