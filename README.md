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

默认只做离线预览：复用模型视图、低成本草稿和最终贴图渲染，不启动战雷、不进行游戏内镜头或截图操作。仅在用户明确要求本次订单进入游戏时例外；取消后立即停止。未进行游戏验证会如实标注，不阻塞离线交付。保存输出后关闭本任务启动的渲染工具。

### 默认节省 token 的验收方式

- AI 负责开发与客观检查；人类负责最终视觉验收。预览图保存并提供链接，默认不逐张送回模型。
- 先测量真实网格/UV 边界和投射方向，再批量修改；需要时生成一次低成本预览，完成后集中烘焙。
- 明确的视觉缺陷才触发局部看图：每批修正默认一次、最多两张裁剪/缩小图；用户明确要求全面 AI 审阅时例外。
- 保留格式、引用、法线通道等必要检查；未实现的几何检查、未做的视觉或游戏验收如实标注，不伪称通过。
- 使用正常完成等待，避免秒级轮询、重复读长日志和历史。阶段结束保存简短订单检查点，续作优先读检查点。
- 完成要求后停止美化迭代；用户要求停止或提醒额度不足时立即停止新增迭代，保存状态并交接。
- 这是工作流约束，不是 API 硬预算或计费限额；不会保证固定比例的节省。

Su-30MKK 守岸人 V3 是用户确认游戏生效的历史案例。泛化脚本验证单独记录，不能代替新增机型的游戏检查。外部 library 的 case.json / verification 保留证据。

tests/test_pipeline.py 用临时目录验证通道、格式、路径、安装防覆盖，不触碰真实游戏。Blender 集成验证放在 library/verification。已有安装涂装不变。

维护：修改源插件，运行测试和 Skill/插件校验，再按 Plugin Creator 的 cachebuster + CLI 重装流程更新。用配置和证据传承，避免依赖聊天记录。
