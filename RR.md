# AI API 配置格式化工具

一个基于 PyQt6 的桌面应用，用于快速格式化 AI API 配置信息。

## ✨ 功能特性

- 🤖 **智能文本解析**: 自动识别文本中的 URL 和 API Key
- 🔍 **双模式 OCR**: 支持系统 OCR（免费）和 AI 模型（GPT-4V）识别图片中的模型列表
- 📄 **多格式输出**: 支持 `.env`、`JSON`、`YAML`、`TOML` 格式
- 📚 **历史记录**: 自动保存配置历史，支持搜索和复用
- 🎨 **深色主题**: 现代化深色界面设计
- 🔐 **厂商识别**: 自动识别主流 AI 服务商（OpenAI、Anthropic、Google 等）

## 📦 安装

### 前置要求

- Python 3.10 或更高版本
- uv 包管理器（推荐）

如果还没有安装 uv：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 安装步骤

#### 方式一：使用 uv（推荐）

```bash
# 1. 进入项目目录
cd /Users/meng/tools/formatApi

# 2. 使用 uv 同步依赖（自动创建虚拟环境）
uv sync

# 3. 如果需要 macOS 系统 OCR 支持（可选）
uv sync --extra macos-ocr
```

#### 方式二：使用 pip

```bash
# 安装依赖
pip install -r requirements.txt

# macOS 系统 OCR（可选）
pip install pyobjc-framework-Vision pyobjc-framework-Quartz
```

**注意**: 
- 系统 OCR 仅支持 macOS，需要额外安装 Vision 框架
- AI OCR 模式需要配置 OpenAI API Key（在应用设置中配置）

## 🚀 使用方法

### 启动应用

**使用 uv（推荐）：**
```bash
uv run python main.py
```

**或者激活虚拟环境后运行：**
```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行应用
python main.py
```

**直接使用 Python：**
```bash
python main.py
```

### 基本使用流程

1. **输入 API 信息**
   - 在文本框中粘贴包含 URL 和 API Key 的文本
   - 格式不限，工具会自动识别

2. **上传模型列表图片**（可选）
   - 点击"选择图片"上传包含模型名称的截图
   - 选择识别方式（系统OCR/AI模型）

3. **选择输出格式**
   - 从下拉菜单选择：`.env`、`JSON`、`YAML`、`TOML`

4. **生成配置**
   - 点击"开始解析并格式化"
   - 查看生成的配置文件

5. **保存或复制**
   - 复制到剪贴板
   - 保存为文件

### AI OCR 配置

如需使用 AI 模型识别图片：

1. 点击菜单栏"⚙️ 设置" → "AI OCR 配置"
2. 填写：
   - **API Key**: `sk-xxxxxxxxxxxxx`
   - **Base URL**: `https://api.openai.com/v1`
   - **模型**: `gpt-4-vision-preview`
3. 点击保存

## 📁 项目结构

```
formatApi/
├── main.py                      # 应用入口
├── config.py                    # 配置管理
├── requirements.txt             # 依赖列表
├── ui/
│   ├── main_window.py          # 主窗口
│   ├── candidate_dialog.py     # 候选选择对话框
│   ├── settings_dialog.py      # 设置对话框
│   └── styles.qss              # 样式表
├── services/
│   ├── text_parser.py          # 文本解析
│   ├── ocr_service.py          # OCR 服务
│   ├── formatter_service.py    # 格式化服务
│   └── history_service.py      # 历史记录服务
└── utils/
    ├── validators.py           # 验证工具
    └── vendor_detector.py      # 厂商识别
```

## 🔧 配置文件

应用配置和历史记录保存在：
```
~/.formatapi/
├── config.json      # 用户配置
└── history.json     # 历史记录
```

## 🎯 支持的厂商

- OpenAI
- Anthropic (Claude)
- Google (Gemini)
- DeepSeek
- 智谱 (ChatGLM)
- Moonshot (Kimi)
- 自定义厂商

## 📝 输出示例

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

## ⚠️ 注意事项

1. **API Key 安全**: 历史记录以明文存储在本地，请注意保护
2. **系统 OCR**: macOS 专用，其他系统请使用 AI 模式
3. **AI OCR 费用**: 使用 GPT-4V 会产生 API 调用费用

## 🐛 故障排除

### 系统 OCR 不可用

如果提示"系统OCR需要安装..."：
```bash
pip install pyobjc-framework-Vision pyobjc-framework-Quartz
```

### AI OCR 失败

1. 检查 API Key 是否正确配置
2. 确认网络连接正常
3. 验证模型名称是否正确（需支持 Vision）

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
