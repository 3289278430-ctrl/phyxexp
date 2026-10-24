---
name: phyxexp
description: 受约束的学生实验数据处理技能。当用户提供物理实验数据并要求计算、拟合、求不确定度时使用。禁止自行计算或编造数据，必须调用 scripts/run.py 的审查过工具链。本技能会自动识别用户数据对应的实验，并配合对话上下文推断单位与列含义。
---

# phyxexp —— 受约束的实验数据处理 Skill

大模型只允许「识别实验 + 传数据」，数值一律来自受约束工具链，结论带溯源。

## 硬约束（违反即停止）
1. **禁止**心算、写代码算数、编造/估算任何数值。
2. 所有数值只能来自 `scripts/run.py` 的输出（带 run_id 与输入哈希）。
3. 最终答案必须原样引用 run.py 的 `conclusion`，不得改写数字。

## 第 0 步：识别实验（配合上下文，别急着问用户）
1. **先用对话上下文**：用户说过的话、上传的文件名、历史记录，往往已透露实验类型。
   - 例：用户说「这是杨氏模量的数据」→ 实验就是 `youngs_modulus`。
2. 不确定时用 `python scripts/run.py --list` 看实验目录（每个输入的标签+单位都写清）。
3. 再用 `--identify` 按「数据形状 + 提示词」辅助确认：
   ```bash
   python scripts/run.py --identify --data '{"c1":[...],"c2":[...]}' --hint '杨氏模量'
   ```
4. **单位与列含义优先从目录推断**，不要反复问用户单位；只有真正歧义时才问一次。

## 使用步骤
1. 识别实验（见第 0 步）。
2. 把用户数据映射到该实验的输入（数据列按顺序对应数据型输入；单位按目录）。
3. 调用：
   ```bash
   python scripts/run.py --auto --data '<json>' --hint '<实验提示>'
   # 或指定实验：
   python scripts/run.py -e <id> --data '<json>'
   ```
4. 原样转述 `conclusion`，附 `run_id` / `input_hash`。

## 可配置
新增实验只需在 `config/experiments.json` 加一条（id / tool / inputs / checks / conclusion / keywords），无需改代码。

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
| youngs_modulus_raw | 杨氏模量原始数据全流程（多步管线） | youngs_modulus |
