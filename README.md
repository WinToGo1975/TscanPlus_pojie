# TscanPlus 一键破解

永久 VIP 破解工具，适配 TscanPlus 3.5.x 各版本更新。

## 使用方法

```bash
python TscanPlus_Full.py TscanPlus_Win_Amd64.exe
```

完成。运行 exe 即永久 VIP。

## 要求

- Python 3.x（无需第三方库）
- `upx.exe` 放在同目录（用于自动脱壳/压缩）
- 原版 TscanPlus exe

## 版本

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-09-22 | 支持 3.5.1，双 patch（VIP + License 检查绕过） |

## 原理

通过 Go pclntab 符号表自动定位两个函数：

| 函数 | Patch | 效果 |
|------|-------|------|
| `UpInY2UYR` | `MOV AL,1; RET` | VIP 等级检查始终通过 |
| `IoxJab0E6` | `MOV AL,1; RET` | License 完整性检查跳过 |

**自动适配新版本**：只要函数名不变，脚本自动定位 patch 点，无需关心偏移量。

## 文件说明

| 文件 | 说明 |
|------|------|
| `TscanPlus_Full.py` | 一键破解脚本（唯一需要的文件） |
| `upx.exe` | UPX 脱壳/压缩工具 |

## 免责声明

仅供学习和研究使用，请于 24 小时内删除。商用请购买正版。
