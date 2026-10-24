# 示例（可直接运行）

每个示例是一份**原始输入数据**（JSON），用一条命令即可得到带不确定度、溯源的结果。

| 文件 | 实验 | 命令 |
|---|---|---|
| `ohms_law.json` | 伏安法测电阻 | `python scripts/run.py -e ohms_law --data-file examples/ohms_law.json` |
| `spring_oscillator.json` | 弹簧振子 | `python scripts/run.py -e spring_constant --data-file examples/spring_oscillator.json` |
| `youngs_modulus_raw.json` | 杨氏模量（多步管线） | `python scripts/run.py -e youngs_modulus_raw --data-file examples/youngs_modulus_raw.json` |

## 一键跑全部
```bash
python examples/run_examples.py
```

## 预期结果（约值）
- 伏安法：`电阻 R = 9.85 ± 0.04 Ω（k=2），r = 0.99999`
- 弹簧振子：`劲度系数 k = 8.0 ± 1.8 N/m（k=2），r = 0.9816`
- 杨氏模量：`杨氏模量 E = (1.23 ± 0.20)×10^11 Pa（k=2），误差主要来自光杠杆前后脚 b`
