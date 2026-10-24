# 第三方依赖与许可（THIRD PARTY）

phyxexp 本体（`phyxexp/`、`scripts/`、`config/`、`tests/`、`examples/`）为**原创代码**，采用 **MIT** 许可。

以下为运行时依赖：**未修改源码、未内嵌**，仅通过 `import` 调用，各自遵循其原许可。

| 依赖 | 用途 | 许可 |
|---|---|---|
| numpy | 数值计算 / 最小二乘 | BSD-3-Clause |
| matplotlib | 绘图 | PSF-based |
| RapidOCR（rapidocr-onnxruntime） | 图片/扫描件 OCR（轻量默认） | Apache-2.0 |
| PaddleOCR（选装） | 表格结构 / 手写 / 公式 | Apache-2.0 |
| pypdf | PDF 文本与图片抽取 | BSD-3-Clause |
| xlrd | 旧版 .xls 读取 | BSD-3-Clause |
| openpyxl | .xlsx 读取 | MIT |
| python-docx | Word 表格读取 | MIT |
| Pillow | 图像（matplotlib 依赖） | HPND |

## 关于公式与方法
- 不确定度评定依据 **JJF 1059.1-2012**（国家计量技术规范）；最小二乘、杨氏模量、单摆、光栅等为**公开标准 / 教科书方法**，非任何单一开源项目的专有代码。
- 项目起点参考了作者提供的 `labudata`（Streamlit 单文件示例，MIT）中的物理公式；phyxexp 对其**重新实现**（数值偏导传播替代符号推导），未复制其代码。
