# phyxexp

受约束的学生实验数据处理 Skill（可配置）。

## 一句话
不让大模型"自由写代码算数"，而是把它锁进一个**只能调用审查过工具链**的 Skill 编排层；
数值一律由工具产出，结论带不确定度、R²、残差图与可复现哈希（run_id + 输入哈希）。

## 为什么（痛点）
AI 做数据分析最大的问题：会编数字、结论不可复现、缺乏物理一致性检查。

## 怎么解（约束 = 可信度）
- **白名单工具链**：计算能力只能来自 `TOOL_REGISTRY`（公式可查、可复现）。
- **守卫**：拒绝白名单外的工具 / 任意代码执行 / 自行算数。
- **溯源**：每次运行产出 run_id + 输入哈希 + recipe，重放结果逐位一致。
- **一致性检查**：截距近零、R>0、R² 合理。
- **grounding**：结论模板的每个字段必须溯源到工具输出。

## 可配置（Skill 核心）
实验在 `config/experiments.json` 里声明（id / tool / inputs / checks / conclusion 模板）。
**新增实验 = 加一条 JSON +（可选）加一个工具，无需改其他代码。**

## 快速开始
```bash
pip install -r requirements.txt
python scripts/run.py --list                        # 列出可用实验
python scripts/run.py -e ohms_law --data '{"I":[0.1,0.2,0.3,0.4,0.5,0.6],"V":[1.0,1.97,2.95,3.94,4.93,5.92]}'
python demo/compare.py                              # 裸 LLM vs 受约束 Agent
```

## 目录
```
SKILL.md                  # 宿主大模型加载的 Skill 声明
config/experiments.json   # 可配置的实验声明（权威）
phyxexp/
  engine/                 # 不确定度、拟合、物理模型
  agent/                  # 白名单、守卫、执行器、编排（含多步管线）
  ingest.py               # 统一数据识别（文字/文档/图片）
  identify.py             # 实验自动识别
  viz.py / format.py      # 绘图 / 规范结果表示
  data/experiments.json   # 打包副本
scripts/run.py            # Skill 运行时入口
scripts/server.py         # HTTP 入口（ChatGPT Actions）
chatgpt/                  # Custom GPT 的 Actions 与指令
demo/                     # 裸LLM vs 受约束Agent 对比
tests/                    # 引擎单测
examples/                 # 可直接跑的示例
docs/                     # 录屏/优势论证/技术选型/部署/PPT
.github/workflows/ci.yml  # CI
```



## 多步管线（完整实验）

除单步实验外，支持把多个工具按序串成一条管线，一条命令完成整个实验：

- `youngs_modulus_raw`（杨氏模量原始数据全流程）：线性拟合 → 直径 A 类 → 派生 dn → 公式传播 → 误差预算。
- 管线声明在 `config/experiments.json` 的 `pipeline` 字段（工具 + 派生量 + 引用），无需写代码。

## 打包

`pip install .` 后，配置从包内 `phyxexp/data/experiments.json` 读取；源码运行时优先用根目录 `config/experiments.json`。可用环境变量 `PHYXEXP_CONFIG` 覆盖。

## 数据识别（可选安装）

phyxexp 核心计算只需 numpy + matplotlib（`requirements.txt`）。

从文档/图片里"识别数据"是可选能力，分两档：**轻量内置、重选装**。

### 默认轻量（覆盖 Excel/CSV/Word/PDF/文字/图片基础 OCR）
```bash
pip install -r requirements-ingest.txt
```

### 选装 · 高精度（体积大，有需求再自行安装）
针对扫描件表格、手写数字、公式，可选装更重的引擎（phyxexp 会自动检测并优先使用）：
```bash
# PaddleOCR + PP-Structure（表格结构 + 手写 + 公式，中文最强）
pip install paddleocr paddlepaddle

# Surya 2（多语言表格识别）
pip install surya-ocr
```

> 说明：重型引擎体积大、依赖多，不做硬性绑定；`phyxexp/ingest.py` 用「后端检测」自动选引擎：没装就走轻量 RapidOCR，装了 PaddleOCR 就自动用它的 PP-Structure。

## 不确定度依据
JJF 1059.1-2012（测量不确定度评定与表示）。

## 覆盖的实验（11 个，本科普通物理 力/电/光/热）
- 电学：伏安法测电阻、惠斯通电桥、霍尔效应载流子浓度
- 力学：弹簧振子、单摆测 g、落球法黏滞系数、杨氏模量（光杠杆法）
- 光学：牛顿环曲率半径、光栅衍射测波长
- 热学：金属线膨胀系数
- 通用：线性拟合

每个实验都输出：规范结果（值±不确定度，k=2）+ 误差预算（误差主要来自哪个量）。
加实验 = 在 config/experiments.json 加一条 +（可选）登记一个公式工具。

## License
MIT

第三方依赖与许可见 [THIRD_PARTY.md](THIRD_PARTY.md)。
