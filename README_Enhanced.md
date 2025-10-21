🚀 FLUX AI 增强版 - 多模型AI图像生成器

这是Flux-AI-Pro项目的增强版本，大幅扩展了AI模型支持，包括Stable Diffusion系列、DALL-E、Midjourney等多种主流AI图像生成模型。

![AI Image Generator](https://github.com/kinai2028-dot/Flux-AI-Pro/blob/main/螢幕擷取畫面%202025-09-25%20041942.png)

## 🆕 增强版新特性

### 🤖 多模型支持

**FLUX 系列**
- 🏆 Flux 1.1 Pro - 最新旗舰模型
- 🧠 Flux.1 Kontext Pro/Max - 上下文理解增强
- 🛠️ Flux Dev - 开发者版本
- ⚡ Flux Schnell - 快速生成
- 📷 Flux Realism - 写实风格

**Stable Diffusion 系列**
- 🎯 SD 3.5 Large/Medium - 最新版本
- 💎 SDXL 1.0 - 高分辨率标准
- 🚀 SDXL Turbo - 快速生成版本
- 🔄 SD 2.1 - 稳定版本
- 🔰 SD 1.5 - 经典版本

**专业级模型**
- 🎭 Midjourney - 艺术创作专家
- 🤖 DALL-E 3/2 - OpenAI官方模型
- 🎪 Playground v2.5 - 商业级模型

**社区特化模型**
- 💫 DreamShaper - 梦境风格
- 👁️ Realistic Vision - 超现实主义
- 🎨 Deliberate - 精细控制
- 🌟 Anything v5 - 通用型
- 👩‍🎨 Waifu Diffusion - 动漫风格
- 🗺️ OpenJourney - 开放式创作

**风格特化模型**
- 📸 Analog Film - 胶片风格
- 🌆 Synthwave - 合成波风格
- 🤖 Cyberpunk Anime - 赛博朋克动漫
- 🎮 Pixel Art XL - 像素艺术

### 🎨 增强风格系统

**摄影风格**
- 人像摄影 - 专业头像拍摄
- 街头摄影 - 纪实风格
- 风景摄影 - 自然景观
- 微距摄影 - 极致细节

**艺术流派**
- 抽象表现主义 - Jackson Pollock风格
- 立体主义 - Pablo Picasso风格
- 新艺术运动 - Alphonse Mucha风格
- 包豪斯 - 极简功能设计
- 复古海报 - 50年代美学

### 🔧 API供应商扩展

**新增支持**
- 🤗 **Hugging Face Inference** - 开源模型平台
  - 直接访问HF模型库
  - 支持自定义推理参数
  - 兼容所有HF托管模型

**现有供应商增强**
- 🌸 **Pollinations.ai** - 扩展模型库支持
- ⚓ **NavyAI** - 商业级API服务
- 🤖 **OpenAI Compatible** - 标准兼容接口

## 📊 增强功能对比

| 功能 | 原版 | 增强版 |
|------|------|--------|
| 支持模型数量 | 5个 | 25+个 |
| API供应商 | 3个 | 4个 |
| 风格预设 | 21种 | 30+种 |
| 图像尺寸预设 | 6种 | 13种 |
| 模型分类显示 | 无 | 6大类别 |
| 历史记录 | 15条 | 20条 |
| 收藏限制 | 30张 | 40张 |

## 🛠️ 技术增强

### 智能模型发现
- **自动分类**: 根据模型名称智能归类
- **图标系统**: 每个模型都有专属图标
- **优先级排序**: 热门模型优先显示

### 用户界面升级
- **分类展示**: 按模型类别组织界面
- **网格布局**: 更直观的模型选择
- **状态指示**: 清晰的选中状态显示

### API兼容性
- **多协议支持**: OpenAI、HF Inference、自定义API
- **参数适配**: 针对不同API自动调整参数
- **错误处理**: 更完善的异常处理机制

## 📋 部署要求

### 基础依赖
```
streamlit>=1.28.0
openai>=1.0.0
requests>=2.31.0
Pillow>=10.0.0
```

### 环境变量配置
```toml
# .streamlit/secrets.toml 示例
[api_profiles."Pollinations Pro"]
provider = "Pollinations.ai"
api_key = ""
base_url = "https://image.pollinations.ai"
validated = true
pollinations_auth_mode = "令牌"
pollinations_token = "your-token-here"

[api_profiles."HuggingFace"]
provider = "Hugging Face"
api_key = "hf_your-token-here"
base_url = "https://api-inference.huggingface.co"
validated = true

[api_profiles."NavyAI Pro"]
provider = "NavyAI"
api_key = "sk-your-navy-key"
base_url = "https://api.navy/v1"
validated = true
```

## 🚀 快速部署

### 1. Koyeb 部署
[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?name=flux-ai-enhanced&type=git&repository=kinai2028-dot%2FFlux-AI-Pro&branch=main&run_command=streamlit+run+app_enhanced.py+--server.port%3D%24PORT+--server.address%3D0.0.0.0+--server.headless%3Dtrue&instance_type=free)

### 2. Docker部署
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app_enhanced.py .
EXPOSE 8501

CMD ["streamlit", "run", "app_enhanced.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 3. 本地运行
```bash
git clone https://github.com/kinai2028-dot/Flux-AI-Pro.git
cd Flux-AI-Pro
pip install -r requirements.txt
streamlit run app_enhanced.py
```

## 🔐 API密钥配置

### Pollinations.ai
- **免费模式**: 无需密钥，但有使用限制
- **令牌模式**: 获取API令牌以解除限制
- **域名模式**: 通过域名验证访问

### Hugging Face
1. 访问 [HuggingFace](https://huggingface.co/settings/tokens)
2. 创建新的访问令牌
3. 在应用中配置为API密钥

### NavyAI
1. 注册 [NavyAI](https://api.navy) 账户
2. 获取API密钥
3. 在应用中配置

### OpenAI Compatible
- 支持任何OpenAI兼容的API服务
- 包括Azure OpenAI、本地部署等

## 📱 使用指南

### 模型选择
1. 在侧边栏配置API供应商
2. 点击"发现模型"自动加载可用模型
3. 在主界面按类别浏览和选择模型

### 图像生成
1. 选择目标模型
2. 输入提示词和负向提示词
3. 选择风格预设和图像尺寸
4. 设置生成数量和高级选项
5. 点击生成按钮

### 历史管理
- 自动保存生成历史
- 一键收藏优质图像
- 基于历史生成变体

## 🎯 最佳实践

### 提示词优化
- **具体描述**: 使用具体而非抽象的描述
- **风格关键词**: 结合风格预设使用特定关键词
- **质量提升**: 添加"high quality", "detailed", "4k"等质量关键词

### 模型选择建议
- **写实照片**: Stable Diffusion 3.5, Realistic Vision
- **艺术创作**: Midjourney, DALL-E 3
- **动漫风格**: Anything v5, Waifu Diffusion
- **快速生成**: Flux Schnell, SDXL Turbo
- **高质量**: Flux 1.1 Pro, SD 3.5 Large

## 🐛 故障排除

### 常见问题
1. **模型发现失败**: 检查API密钥和网络连接
2. **生成失败**: 确认模型支持当前参数设置
3. **API限制**: 注意各供应商的使用限制和配额

### 性能优化
- 使用较小的批次大小避免超时
- 选择合适的图像尺寸平衡质量和速度
- 定期清理历史记录释放内存

## 📈 未来规划

### 即将新增
- 🔄 图像到图像生成支持
- 🎛️ 更多高级参数控制
- 📊 生成统计和分析
- 🔀 批量风格转换
- 💾 云端配置同步

### 模型扩展
- Leonardo.ai 集成
- Ideogram 支持
- 更多开源模型
- 自定义模型上传

## 🤝 贡献指南

欢迎提交问题和功能请求！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Streamlit](https://streamlit.io/) - 优秀的Python Web应用框架
- [Pollinations.ai](https://pollinations.ai/) - 免费AI图像生成服务
- [Hugging Face](https://huggingface.co/) - 开放的AI模型平台
- [OpenAI](https://openai.com/) - DALL-E系列模型
- 所有开源AI模型的创作者们

---

<div align="center">
  <strong>🎨 让AI艺术创作更简单，让想象力无限延伸 🎨</strong>
</div>
