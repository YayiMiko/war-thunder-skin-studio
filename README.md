# 战雷涂装工作室

本地 Skill + CLI 插件。先用真实载具与主立绘制作整体概念方案，选定后投射、烘焙、验证和交付。当前不包含 MCP 服务。

公开仓库包含通用代码、Skill、模板和技术经验；模型、角色立绘、游戏贴图、订单、截图及本机配置不随仓库发布。这是非官方工具，与游戏发行方无隶属关系。

## 本地开始

需要 Python 3.10+，以及可用的 Blender。当前集成验证环境为 Windows、Python 3.12、Blender 5.2.2；其他组合尚未验证。

```powershell
git clone https://github.com/YayiMiko/war-thunder-skin-studio.git
cd war-thunder-skin-studio
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/studio.py --help
```

用自己的实际路径配置外部工作库、游戏目录和 Blender：

```powershell
.\.venv\Scripts\python.exe scripts/studio.py configure --library "E:/SkinLibrary" --game "E:/Games/War Thunder" --blender "E:/Tools/Blender/blender.exe"
.\.venv\Scripts\python.exe scripts/studio.py doctor
```

资源提取还需要单独配置 Dagor Asset Explorer 源码及其 Python 环境，详见 [提取说明](skills/war-thunder-skins/references/extraction.md)。仓库不附带该工具或其 DLL。

Codex 工作流入口为 [SKILL.md](skills/war-thunder-skins/SKILL.md)，配置格式与命令见 [schema.md](skills/war-thunder-skins/references/schema.md)。CLI 可以独立使用；概念图生成仍依赖调用环境提供的图像生成能力。

运行不依赖游戏或 Blender 的测试：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## 工作流程

入口 skills/war-thunder-skins/SKILL.md；命令 scripts/studio.py --help。依赖 Python 3、Pillow、numpy、Blender；提取可选外部 Dagor Asset Explorer。概念图使用会话已有 ImageGen，不在脚本中嵌入密钥。

新任务说：**使用战雷涂装工作室，为这架飞机和这张立绘做两个整体概念方案，先不生产。**

环境：~/.config/war-thunder-skin-studio/environment.json。大型模型、立绘、订单在配置的 library。分享插件不包含游戏素材或外部工具。换电脑时迁移 library，再 configure 工具路径。

顺序：doctor → list → register（新载具）→ new-order → baseline（无缓存时）→ concept-brief → 概念图 → choose → preview → bake → validate → install。按用户要求停在规划/概念阶段。

Su-30MKK 守岸人 V3 是用户确认游戏生效的历史案例。泛化脚本验证单独记录，不能代替新增机型的游戏检查。外部 library 的 case.json / verification 保留证据。

tests/test_pipeline.py 用临时目录验证通道、格式、路径、安装防覆盖，不触碰真实游戏。Blender 集成验证放在 library/verification。已有安装涂装不变。

维护：修改源插件，运行测试和 Skill/插件校验，再按 Plugin Creator 的 cachebuster + CLI 重装流程更新。用配置和证据传承，避免依赖聊天记录。
