# 跨 Agent 兼容

版本：2.5.0；核查日期：2026年10月23日。此次补充专业解释、短讯与人物长稿写法，保留既有编辑范围，沿用2.0版已核对的跨软件安装结构；包内文件与本地安装会逐项核对，未重新检索宿主版本或调用 DSH、WorkBuddy 自身模型。

## 通用结构

采用目录型 Agent Skills：根目录 `SKILL.md`，YAML 的 `name` 与 `description` 定义入口，正文为 Markdown，配套资料全部使用相对链接。包内只有一个 `SKILL.md`；上游资料入口改名为 `rules.md`，避免被重复识别。

写作过程只需读取文档。无硬编码个人目录、全局技能依赖、特定工具名或外部模型调用；没有运行时脚本或依赖包。Codex 的可选界面配置不参与写作规则。

## DSH

官方本地 provider 识别 `<root>/<name>/SKILL.md` 或平铺 Markdown，不递归发现任意深度的入口。项目 `.dsh/skills`、项目 `.agents/skills`、自定义目录、用户 DSH 和用户 agents 目录有明确优先级。当前通用包采用一层目录与 kebab-case 名称，符合该格式。

来源：[DSH 官方技能子系统](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md)。这些是文档与结构核查，不等于已在每个 DSH 版本中完成模型写作实测。

## WorkBuddy

官方支持在技能页面上传技能包；其开放平台描述的结构同样为 `SKILL.md + references/`，但列出了版本、作者与中英文描述必填字段。因此单独提供 WorkBuddy 上传包，入口增加这些字段，规则正文与配套文档不变。

官方项目配置另外支持 `.codebuddy/skills/<name>/SKILL.md`。桌面个人库和云端个人库分别管理，GitHub 上架本身不会同步到任一端。

来源：[技能导入](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[开放平台结构](https://open.workbuddy.cn/docs/skill)、[项目级配置与端差异](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)。

## 验证层级

构建检查覆盖入口字段、包内链接、独立依赖、单入口、原规则完整性、个人路径清理、两种发行包内容与压缩完整性。独立 Agent 在无法读取其他全局技能的条件下试用包内规则，验证正常写稿、轻清理、重写、降防御与素材指令隔离。

本机技能目录写入与文件哈希可确认安装文件存在；宿主技能菜单的识别、启用状态，以及 DSH/WorkBuddy 自身模型的输出，应与上述结构检查区分记录。没有执行的层级不称已实测。

## 其他软件

支持标准 Agent Skills 的软件按自己的目录或上传入口安装。只有普通聊天和文件读取能力时，也可读取本目录 `SKILL.md` 并按其相对链接使用；不能只复制主文件而丢失 `references/`。宿主若限制多文件读取，需提供整个技能目录的访问权限。
