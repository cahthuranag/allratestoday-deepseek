# AllRatesToday × DeepSeek

[English](./README.md) | 简体中文

> 通过函数调用，为 DeepSeek 聊天和 Agent 注入实时货币汇率、历史数据能力。

DeepSeek 的 Chat Completions API 与 OpenAI 兼容，因此同一套 function calling 机制即可接入。本包提供开箱即用的工具定义和一个精简的 Agent 封装，让 DeepSeek 可以直接回答类似问题：

- *"现在美元对欧元的汇率是多少？"*
- *"把 1000 英镑换成日元"*
- *"过去 30 天美元兑印度卢比的走势如何？"*

由 [AllRatesToday API](https://allratestoday.com) 提供数据支持 —— 160+ 种货币、来自 Reuters/Refinitiv 的中间价、两个公共接口无需 API 密钥。

## 安装

```bash
pip install allratestoday-deepseek
```

## 快速开始 —— 一问一答

```bash
export DEEPSEEK_API_KEY=sk-...      # 在 platform.deepseek.com/api_keys 获取
allratestoday-deepseek --ask "2500 美元现在等于多少欧元？"
```

## 快速开始 —— 交互式对话

```bash
allratestoday-deepseek
# 或者：
python examples/chat.py
```

## 作为库使用

```python
from allratestoday_deepseek import DeepSeekCurrencyAgent

with DeepSeekCurrencyAgent() as agent:
    print(agent.ask("500 瑞士法郎能换多少日元？"))
```

需要更精细的控制？直接配合 OpenAI SDK 使用工具定义，将 `base_url` 指向 DeepSeek 即可 —— 请参考 `examples/raw_tool_call.py`。

## 提供的工具

| 工具 | 需要密钥 | 说明 |
|---|---|---|
| `get_exchange_rate` | 否 | 两种货币间的实时中间价 |
| `convert_currency` | 否 | 按实时汇率换算金额 |
| `get_historical_rates` | 是 | `1d`、`7d`、`30d`、`1y` 历史数据 |
| `list_currencies` | 否 | 所有受支持货币的代码、名称和符号 |

公共工具（`get_exchange_rate`、`convert_currency`、`list_currencies`）无需 API 密钥即可使用。`get_historical_rates` 需要 `ALLRATES_API_KEY`。

## 环境变量

| 变量 | 是否必需 | 用途 |
|---|---|---|
| `DEEPSEEK_API_KEY` | 是 | DeepSeek 的 API 密钥 |
| `ALLRATES_API_KEY` | 否 | AllRatesToday 的 API 密钥（用于更高额度）。访问 [allratestoday.com/register](https://allratestoday.com/register) 免费注册 |
| `ALLRATES_BASE_URL` | 否 | 覆盖默认 API 地址（默认 `https://allratestoday.com/api`）|

## 工作原理

1. 你向 DeepSeek 发送一个问题。
2. Agent 调用 `chat.completions.create(..., tools=TOOLS)` —— DeepSeek 拿到全部工具 schema。
3. 如果 DeepSeek 判断需要调用工具（例如 `get_exchange_rate(source="USD", target="EUR")`），它会发出一次 `tool_call`。
4. Agent 执行该工具对 AllRatesToday API 的请求，把 JSON 结果回传给 DeepSeek。
5. DeepSeek 给出最终的自然语言回答，引用真实汇率。

永远不会凭空给出汇率 —— 没有调用工具之前 Agent 不会提供数字。

## 兼容性

- 支持 function calling 的 DeepSeek 模型（`deepseek-chat`、`deepseek-reasoner`）
- Python 3.9+
- Linux、macOS、Windows 均可运行

## 相关项目

- **MCP 服务器**: [`@allratestoday/mcp-server`](https://www.npmjs.com/package/@allratestoday/mcp-server) —— 适用于 Claude Code、Cursor、Claude Desktop
- **JavaScript SDK**: [`@allratestoday/sdk`](https://www.npmjs.com/package/@allratestoday/sdk) —— Node.js / 浏览器通用 SDK
- **文档**: [allratestoday.com/developers](https://allratestoday.com/developers)

## 开源协议

MIT 协议 —— 详见 [LICENSE](./LICENSE) 文件。
