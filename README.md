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
SKILL.md                  # 宿主大模型（Claude Code 等）加载的 Skill 声明
config/experiments.json   # 可配置的实验声明
scripts/run.py            # Skill 运行时入口（大模型唯一计算入口）
phyxexp/                  # 引擎 + 约束层（白名单/守卫/溯源）
  engine/                 # 不确定度、拟合、物理模型
  agent/                  # 注册表、守卫、执行器、编排
  viz.py                  # 绘图工具
demo/                     # 对比演示
docs/                     # 录屏演示脚本等
```

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
