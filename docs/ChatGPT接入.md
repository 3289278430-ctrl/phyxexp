# ChatGPT 接入说明（Custom GPT + Actions）

phyxexp 同时支持两类宿主：
- **Claude Code**：加载根目录 `SKILL.md`。
- **ChatGPT**：创建 Custom GPT，用「Actions」挂载 `chatgpt/openapi.json`，指令用 `chatgpt/instructions.md`。

> 为什么用 Actions 而不是 Code Interpreter？Code Interpreter 会让模型自由写代码算数（= 回到"会编数"的老问题）；
> Actions 是 ChatGPT 的**受约束工具调用**接口——它只能按我们声明的端点传 JSON，拿回结构化结果，恰好就是我们要的"约束"。

## 三步接入
1. **起服务**（本地）：
   \`\`\`bash
   python scripts/server.py --port 8000
   \`\`\`
   验证：浏览器/curl 访问 `http://127.0.0.1:8000/list`。
2. **暴露公网**（ChatGPT Actions 要求 HTTPS）：
   \`\`\`bash
   ngrok http 8000
   \`\`\`
   拿到形如 `https://xxxx.ngrok.io` 的地址，把 `chatgpt/openapi.json` 里 `servers[0].url` 改成它。
3. **建 Custom GPT**：
   - Instructions：粘贴 `chatgpt/instructions.md` 全文。
   - Actions → Import from URL / 粘贴 `chatgpt/openapi.json`，确认服务器地址为 ngrok 地址。
   - 测试：问一句"伏安法测电阻，I 从 0.1 到 0.6 A，V 是 1.0/1.97/2.95/3.94/4.93/5.92 V，求电阻"。

## 本地无 ChatGPT 时怎么演示（录屏/PPT 素材）
直接用 curl 打本服务，效果与 ChatGPT 调用完全一致：
\`\`\`bash
curl http://127.0.0.1:8000/run -H "Content-Type: application/json" \
  -d '{"experiment":"ohms_law","data":{"I":[0.1,0.2,0.3,0.4,0.5,0.6],"V":[1.0,1.97,2.95,3.94,4.93,5.92]}}'
\`\`\`
返回：
\`\`\`json
{ "run_id": "...", "input_hash": "...",
  "conclusion": "电阻 R = 9.8486 ± 0.0197 Ω（扩展 k=2：9.849 ± 0.039 Ω）...",
  "checks": ["通过 · R > 0", "通过 · intercept_ok"], "grounded": true, "replay_match": true }
\`\`\`
