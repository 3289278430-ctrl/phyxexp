---
name: phyxexp
description: 受约束的学生实验数据处理技能。当用户提供物理实验数据并要求计算（线性拟合、伏安法测电阻、弹簧振子求劲度系数、杨氏模量、不确定度、残差分析）时使用。禁止自行计算或编造数据，必须调用 scripts/run.py 的审查过工具链。
---

# phyxexp —— 受约束的实验数据处理 Skill

大模型只允许「选实验 + 传数据」，数值一律来自受约束工具链，结论带溯源。

## 硬约束（违反即停止）
1. **禁止**心算、写代码算数、编造/估算任何数值。
2. 所有数值只能来自 `scripts/run.py` 的输出（带 run_id 与输入哈希）。
3. 最终答案必须原样引用 run.py 输出的 `conclusion` 字段，不得改写其中的数字。

## 使用步骤
1. 列出可用实验：
   ```bash
   python scripts/run.py --list
   ```
2. 把用户数据整理成 JSON（字段名见 --list 中各实验的 inputs）。
3. 调用（实验 id 按需替换）：
   ```bash
   python scripts/run.py --experiment ohms_law --data '{"I":[0.1,0.2,0.3,0.4,0.5,0.6],"V":[1.0,1.97,2.95,3.94,4.93,5.92]}'
   ```
4. 只转述输出的 `conclusion`，并附 `run_id` 与 `input_hash`。

## 可配置
新增实验只需在 `config/experiments.json` 里加一条（id / tool / inputs / checks / conclusion 模板），**无需改代码**。白名单工具见 `phyxexp/agent/registry.py`。

## 可用实验（11 个，力/电/光/热）
| id | 名称 | 工具 |
|----|------|------|
| ohms_law | 伏安法测电阻 | ohms_law_resistance |
| wheatstone_bridge | 惠斯通电桥 | wheatstone_bridge |
| hall_carrier_density | 霍尔效应载流子浓度 | hall_carrier_density |
| spring_constant | 弹簧振子 | spring_constant |
| simple_pendulum | 单摆测 g | simple_pendulum |
| falling_ball_viscosity | 落球法黏滞系数 | falling_ball_viscosity |
| youngs_modulus | 杨氏模量（光杠杆法） | youngs_modulus |
| newton_rings | 牛顿环曲率半径 | newton_rings |
| grating_wavelength | 光栅衍射测波长 | grating_wavelength |
| linear_expansion | 金属线膨胀系数 | linear_expansion |
| linear_fit | 通用线性拟合 | linear_fit |
