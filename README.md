# AI API 配置格式化工具

一个基于 PyQt6 的现代化桌面应用，旨在为您快速解析并格式化 AI API 配置。

## ✨ 核心特性
- 🤖 **智能解析**：自动从杂乱文本中识别 Base URL 和 API Key。
- 🔍 **双模 OCR**：支持 macOS 系统 Vision 引擎及 AI 模型（GPT-4V）识别图片中的模型列表。
- 📄 **多格式导出**：一键生成 `.env`、JSON、YAML 或 TOML 格式。
- 📚 **历史记录**：自动保存配置，支持搜索与复用。
- 🎨 **优质体验**：响应式深色界面，支持主流 AI 厂商识别。

## 🚀 快速开始

### 前置要求
- Python 3.10+
- [uv](https://astral.sh/uv/) (推荐)

### 运行应用
```bash
# 克隆并进入目录
cd formatApi

# 一键安装依赖并启动
uv run python main.py
```

> [!TIP]
> **macOS 系统 OCR**：若需使用系统原生 OCR，请运行 `uv sync --extra macos-ocr`。

## 📖 使用技巧
1. **输入**：直接粘贴包含 API 信息的文本或上传模型列表截图。
2. **格式**：在下拉框中选择目标文件格式。
3. **完成**：点击开始，即可复制或保存生成的配置。

<details>
<summary>📂 查看详细配置路径与结构</summary>

- **配置文件**: `~/.formatapi/config.json`
- **历史记录**: `~/.formatapi/history.json`

项目核心结构：
- `main.py`: 应用入口
- `ui/`: 界面组件
- `services/`: 解析与格式化核心逻辑
- `utils/`: 验证与厂商识别
</details>

<details>
<summary>📝 查看输出示例</summary>

### .env 格式
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
HOST=0.0.0.0
CAPABILITIES=["vision","function_calling","stream"]
MODELS=["gpt-4-turbo","gpt-3.5-turbo"]
```

### JSON 格式
```json
{
  "api_key": "sk-xxxxxxxxxxxxx",
  "base_url": "https://api.openai.com/v1",
  "host": "0.0.0.0",
  "capabilities": ["vision", "function_calling", "stream"],
  "models": ["gpt-4-turbo", "gpt-3.5-turbo"]
}
```
</details>

<details>
<summary>🛠️ 故障排除</summary>

### 系统 OCR 不可用
若提示需要 Vision 框架，请确保在 macOS 环境并运行：
```bash
uv sync --extra macos-ocr
```

### AI OCR 失败
1. 在设置中检查 API Key 是否正确配置。
2. 确认网络可以访问 AI 服务端点。
3. 验证模型名称（如 `gpt-4-vision-preview`）是否正确。
</details>

---

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
