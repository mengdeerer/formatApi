# FormatAPI

一个基于 Tauri + React + TypeScript 打造的高性能 API 响应格式化工具。旨在为开发者提供极速、优雅的 API 响应处理体验。

## ✨ 核心特性

- 🚀 **极致性能**：基于 Rust (Tauri) 后端，处理大数据量响应依然流畅。
- 🎨 **现代 UI**：采用 Tailwind CSS 和 Lucide 图标库，简洁直观。
- 🛠️ **开发者友好**：支持多种格式化选项，集成代码高亮和搜索。
- 📦 **轻量级**：比原生 Electron 应用更小的体积，更低的资源占用。

## 🛠️ 技术栈

- **前端**: [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/)
- **后端**: [Rust](https://www.rust-lang.org/) (Tauri 2.0)
- **样式**: [Tailwind CSS](https://tailwindcss.com/)
- **图标**: [Lucide React](https://lucide.dev/)

## 🚀 快速开始

### 环境依赖

- [Node.js](https://nodejs.org/) (建议最新 LTS)
- [Rust](https://www.rust-lang.org/tools/install)
- [Tauri CLI](https://tauri.app/v1/guides/getting-started/prerequisites)

### 本地开发

1. **克隆仓库**
   ```bash
   git clone https://github.com/mengdeerer/formatApi.git
   cd formatApi
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **运行开发服务器**
   ```bash
   npm run tauri dev
   ```

### 构建打包

```bash
npm run tauri build
```

## 🤝 贡献指南

欢迎提交 Pull Request 或 Issue 来帮助我们改进 FormatAPI！

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 开源协议

本项目采用 MIT 协议。
