# Halo PixelBar Monitor

把 **花再 Halo PixelBar 2026 升级款**的像素屏用作 Windows 电脑性能监视器。

使用 USB HID 在本地显示 CPU / GPU 温度与占用率、内存占用率和时间。无账户、无遥测、无服务端，也不需要 MCP。项目为独立社区工具，与 EDIFIER 无隶属或官方支持关系。

```text
 C42/ 8  | G45/12  | M67 | 15:30
```

上图为人工构造的示例，不包含真实设备记录。

## 适用版本

**目前实际验证的机器版本：Halo PixelBar 2026 升级款。**

| 项目 | 已验证值 |
| --- | --- |
| 系统 | Windows 11，64 位 |
| 连接 | 支持数据传输的 USB 连接 |
| USB VID / PID | `0x2D99` / `0xA160` |
| HID interface | `4` |
| HID usage page / usage | `0xFF14` / `1` |
| 文字容量 | **32 个 ASCII 字符，可完整静态显示，已目视确认** |
| 可用功能 | 文字、对齐、主题颜色、状态查询与文字回读 |

`A160` 是 USB 产品标识 PID，不是商品型号、固件版本或显示屏分辨率。
这里“2026 升级款”描述实际测试的设备版本，不代表同名商品的所有批次都已验证。

其他 PixelBar 版本（包括 PID `A106`）、AI 型号、其他 EDIFIER 音箱尚未验证，本程序会拒绝不匹配的设备。**不要为了让设备被识别而直接放宽 HID 过滤条件。** Windows 10、AMD CPU、NVIDIA / Intel GPU 等组合也需要独立验证；代码中的通用传感器选择不代表已完成全部硬件兼容测试。

## 功能与布局

- CPU 温度和占用率、GPU 核心温度和占用率、内存占用率、24 小时时间。
- 单页固定 **32 字符**，默认居中，`|` 分隔各部分。
- 普通数值至少两位，个位数左侧补空格；三位数会占用本段留白，分隔线位置保持不变。
- 不截断 100%，不把 100 显示成 99。缺失、无效或过期读数用 `--` 表示。
- 每秒采样，默认每两秒更新显示；USB 断开后重试连接。
- 退出时尽力恢复启动前的文字、场景和颜色。
- 下载 / 上传速度已移除，也不采集网络流量。

| 字段 | 含义 |
| --- | --- |
| `C42/ 8` | CPU 温度 42 摄氏度，占用率 8% |
| `G45/12` | GPU 核心温度 45 摄氏度，占用率 12% |
| `M67` | 内存占用率 67% |
| `15:30` | 时间，默认 UTC+8，北京时间 |

测试机器的字库无法显示 `°` 或独立字符 `℃`，因此屏幕使用 ASCII 缩写表达单位。
USB 回读验证只能证明文本被设备接收，不能证明任意 Unicode 字形都能显示。

## 安装

### 1. 准备环境

- Windows 10 / 11，建议 Windows 11 64 位。
- [Python 3.11 或更新版本](https://www.python.org/downloads/windows/)，安装时启用 Python 命令或 Python Launcher。
- 可读取硬件传感器的管理员权限；.NET Framework 4.7.2 或更新版本。
- 将音箱用 USB 数据线连接电脑，开机并切换至 USB 声卡输入。仅蓝牙连接或仅供电连接不能使用本工具。

从本仓库下载 ZIP 后解压，或使用 Git 克隆；后续命令都在**项目根目录**运行。

### 2. 安装依赖

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Setup.ps1
```

脚本会在项目目录内：

1. 创建 `.venv`，安装固定版本 `hidapi==0.15.0`。
2. 下载 LibreHardwareMonitor **0.9.6 的 .NET Framework 发布包**。
3. 下载固定上游提交中的 PawnIO 安装程序。
4. 校验 SHA-256；对 PawnIO 另外校验有效数字签名与发布者。
5. 从 `config.example.json` 创建本地 `config.json`，保留已有设置。

下载地址和校验值在 [`scripts/dependencies.json`](scripts/dependencies.json)。不从第三方镜像获取驱动。
`Setup.ps1` 只准备文件，不自动安装驱动；首次启动监视器时，若尚未安装 PawnIO，会在管理员权限下安装已经验证的签名版本。

若 Python 不在 PATH，可显式指定你自己机器上的 Python：

```powershell
.\Setup.ps1 -PythonExecutable (Get-Command python).Source
```

这两个命令只为当前进程选择执行策略，不永久修改系统策略。

### 3. 启动

双击 **`Start-Monitor.cmd`**，在 Windows 管理员提示中确认运行。

也可以在终端执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Start-Monitor.ps1
```

程序在后台运行，同一登录会话只允许一个实例。请关闭其他持续改写音箱屏幕的工具，例如 TempoHub 歌词或场景同步，否则它们可能互相覆盖。

无需安装 TempoHub 即可运行本监视器；它仍可用于官方设置和故障诊断。本项目不会登录 EDIFIER 账户。

### 4. 停止

双击 **`Stop-Monitor.cmd`**，等待约 5 秒。程序停止采样，并尽力恢复启动前的显示。

如果 USB 已拔掉、程序被强制结束或电脑突然断电，屏幕恢复可能无法完成。不会恢复整个音箱的所有设置，只恢复本工具保存的屏幕文字、场景/排版和颜色。

## 配置

编辑本地 `config.json`。该文件已被 Git 忽略。

```json
{
  "alignment": "center",
  "refresh_seconds": 2.0,
  "timezone_offset_hours": 8,
  "hot_cpu_c": 85,
  "hot_gpu_c": 80,
  "gpu_index": 0,
  "restore_on_exit": true
}
```

| 设置 | 说明 |
| --- | --- |
| `alignment` | `left`、`center`、`right`、`stretch`；默认居中 |
| `refresh_seconds` | 显示更新间隔，1–60 秒；传感器仍每秒采样 |
| `timezone_offset_hours` | 固定 UTC 偏移，默认 8；不自动处理夏令时 |
| `hot_cpu_c` / `hot_gpu_c` | 达到该温度时文字变橙色，仅为显示阈值，不是厂商温度上限或报警系统 |
| `gpu_index` | LibreHardwareMonitor 枚举的第几张显卡，从 0 开始；更改后重启监视器 |
| `restore_on_exit` | 退出时是否尝试恢复原显示 |

除显卡选择外，显示设置在下一次刷新时读取。配置无效时保留最近一次有效设置。
配置不会改变字体大小、绘制任意像素或开启多行模式。

## 数据来源与限制

传感器由 [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) 提供。
CPU 优先读取 `CPU Package`；不存在时尝试已知的核心温度传感器。GPU 优先读取所选显卡的 `GPU Core` 温度与负载。
传感器缺失时显示 `--`，不会用主板温度、默认常数或其他无关数值冒充 CPU 温度。

CPU 温度可能需要 [PawnIO](https://pawnio.eu/) 与管理员权限。`Start-Monitor.ps1 -NoElevation` 可以用于排查，但此时 CPU 温度可能无法读取。

**本项目只实现单行文字显示。** 新版软件中的画布接口在测试设备上查询无响应；这不能证明硬件绝对不支持自绘像素，但当前没有经过验证的实时像素绘图、多行显示或任意小字体功能。不会通过反复上传未知图像文件来冒充实时绘图。

## 隐私与文件

发布仓库只包含通用源代码、人工构造的示例、配置模板和文档。
不包含开发机器的硬件型号、用户名、路径、设备序列号、实时读数、账户凭据、OAuth 数据或反编译结果。

运行后生成的数据在 `runtime/` 下，**不要把这个目录上传到 issue 或另一个仓库**：

| 文件 | 内容 |
| --- | --- |
| `sensors.json` | 仅有白名单数字传感器读数与采样时间 |
| `display-status.json` | 最近的显示文字及回读验证状态 |
| `previous-screen.json` | 启动前的显示备份，可能包含你自己的自定义文字 |
| `running.json` | 本地工作进程编号 |
| `display.log` / `sensor-error.log` | 简化错误类型，不记录原始设备路径 |

`.gitignore` 排除整个 `runtime/`、`lib/`、`.venv/`、本地配置和二进制文件。
本项目不创建开机启动项、Windows 服务或防火墙规则，不更改音量、风扇设置或固件。
更多说明见 [SECURITY.md](SECURITY.md)。

## 常见问题

**没有显示或屏幕仍被歌词覆盖**

确认是 2026 升级款且 VID/PID 匹配，使用 USB 数据连接，停止其他屏幕控制程序。检查 `runtime/display-status.json` 中的 `verified`。只有一个受支持设备时才会写入；多个匹配设备会被拒绝，避免写错音箱。

**CPU 温度为 `--`，但其他数据正常**

检查管理员权限和 PawnIO 是否已安装。先在官方 LibreHardwareMonitor 中确认该硬件能提供所需传感器。不要关闭系统安全功能，也不要替换为来源不明的旧驱动。

**运行一段时间后停止显示**

检查 `runtime/sensor-error.log` 和 `runtime/display.log`。0.1.1 修复了 Windows 读取数据文件时替换失败导致监控退出的问题：现在采用原子替换、短暂重试，文件持续占用时跳过本次采样并继续运行。短暂读取失败保留最近的有效读数，超过 10 秒则显示 `--`。旧版本请停止后更新代码，再重新启动。

**显卡数据不对应独显**

存在多张显卡时，调整 `gpu_index` 并重启。不同系统枚举顺序可能不同。选择超出范围时显示 `--`。

**三位数会不会被截断**

不会。100% 或三位温度占用本段留白，整行仍固定 32 字符，`|` 在第 10、20、26 个字符位置；后续段落不移动。

**重新插入 USB 后没有恢复**

等待几次刷新；如果仍失败，确认其他工具没有占用通道，再停止并重新启动。停止时设备不在线，原屏幕可能无法恢复。

**依赖下载哈希不匹配**

安装会停止。检查下载是否完整或上游是否改变了发布资产；不要跳过校验运行未知文件。

**停止后立即启动没有反应**

等约 5 秒，给屏幕恢复和传感器释放留出时间，再启动。也要确认没有另一个目录中的监视器实例占用同一个实例锁。

## 开发与检查

不连接硬件也可以运行测试和合成预览：

```powershell
python -m unittest discover -s tests -v
powershell -NoProfile -ExecutionPolicy Bypass -File tests/test_sensor_snapshot.ps1
python -m halo_pixelbar_monitor --preview
```

提交前检查暂存/跟踪文件：

```powershell
python scripts/check_public_files.py
```

测试覆盖固定列宽、9→10 / 99→100 的边界、缺失数值、损坏回包、写入回读不一致、屏幕备份/恢复、无效配置及文件占用后的恢复。PowerShell 测试使用实际 Windows 文件锁，Python 单元测试使用假设备，不等于硬件兼容性测试。
GitHub Actions 运行相同检查，并解析 PowerShell 文件。

目录结构：

```text
halo_pixelbar_monitor/    显示格式、配置、HID 通讯和显示工作进程
scripts/                 传感器工作进程、依赖清单、发布文件检查
tests/                   无硬件单元测试
docs/                    协议说明与第三方许可证
Setup.ps1                可复现安装入口
Start-Monitor.cmd        启动
Stop-Monitor.cmd         停止
config.example.json      无私人信息的配置模板
```

## 参考资料与许可

- [官方 Halo PixelBar 支持页面](https://www.edifier.com/cn/product/support-840.html)
- [官方中文用户说明书](https://cn-oss.edifier.com/Uploads/images/2025/06/17/2025061713502517501394251794.pdf)
- [官方 TempoHub 下载入口](https://www.edifier.com/PC.html)
- [halo-pixelbar-mcp](https://github.com/Seraph310/halo-pixelbar-mcp)
- [HaloPixelToolBox](https://github.com/XFEstudio/HaloPixelToolBox)

官方用户说明书不是开发协议文档；社区协议观察也不是官方 SDK。
本项目代码采用 [MIT License](LICENSE)。第三方程序保留各自许可，详见 [THIRD_PARTY.md](THIRD_PARTY.md)。
