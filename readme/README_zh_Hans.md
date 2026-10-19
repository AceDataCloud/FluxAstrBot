# AstrBot Flux 图片插件

通过您自己的 Ace Data Cloud 账号，在 AstrBot 对话中生成或编辑一张 Flux 图片。`flux_generate_image` 提交一次任务，`flux_get_task` 用同一个任务 ID 查询最终结果。

这是 **Ace Data Cloud 提供的 Flux 独立集成**，不是 Flux 厂商或 AstrBot 团队的官方插件。请使用自己的 Ace API Key。

[English guide](../README.md) · [Flux 图片接口](https://platform.acedata.cloud/documents/flux-images?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fluxastrbot_readme_documents_flux_images) · [Flux 任务接口](https://platform.acedata.cloud/documents/flux-tasks?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fluxastrbot_readme_documents_flux_tasks) · [当前价格](https://platform.acedata.cloud/services/flux?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fluxastrbot_readme_services_flux)

## 1. 查找与安装

当前上游菜单为 **插件 → 顶部插件 → 插件市场 / 已安装**；旧英文版本可能仍写 Extensions。在插件市场搜索 **Flux**，核对 **Flux by Ace Data Cloud**、作者 **acedatacloud** 与对应服务图标。

**2026-10-19 发布状态：尚未在官方市场公开上架。** 上面的搜索/安装是正式上架后的路径；当前不要等待不存在的卡片，请用下一段的仓库地址手动安装。

仓库安装：**插件 → 插件 → 已安装 → 安装插件（+）→ 从链接安装**，输入 `https://github.com/AceDataCloud/FluxAstrBot`。源码已经存在；安装后核启用和加载状态。仓库/文件安装与官方市场安装分别记账。

## 配置密钥

首次使用请先注册并登录；如果应用页还没有通用应用，点击 **初始化通用应用（Initialize General Application）**，再按下面步骤管理密钥。

在 [Ace Data Cloud 应用管理](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fluxastrbot_readme_api_key)复制生成 API Key，或创建同时允许 `/flux/images` 与 `/flux/tasks` 的 Key。提交前查看当前模型价格和余额。将 Key 填入插件的 **Ace Data Cloud generation API key with Flux access** 配置项，不要添加 `Bearer `，也不要使用 `platform-...` 管理令牌。AstrBot WebUI 会遮蔽显示此字段，但原值保存在数据目录中，请保护该目录。

选择支持工具调用的对话模型，并在当前对话的 profile 与 persona 中允许两个 Flux 工具。

### Token 图文：复制或创建专用 Key

先[注册或登录 Ace](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fluxastrbot_readme_signup)，打开 **Applications → General application**；没有通用应用时先初始化。图中 **1** 复制现有 Key，**2 Manage Keys → Create** 创建专用 Key。API 限制开启时应包含 `/flux/images`、`/flux/tasks`，并检查账户当前权限、余额与价格。

![Ace 应用页复制 Key 或管理 Key（已脱敏）](../_assets/tutorial/get-api-key-en.png)

专用 Key 可命名为 `AstrBot Flux`；到期和限额按需设置。下图中的 `Dify tutorial` 是旧示例名称，不需要照抄。

![创建专用 API Key（共享 Ace 页面，非 AstrBot）](../_assets/tutorial/create-api-key-en.png)

两张图于 **2026-10-19** 复用核验，原拍摄日期未知，凭据/App ID/余额均已脱敏；这是共享 Ace Applications 页面，不是 AstrBot 安装或真实调用证明。[原图来源与限制](../_assets/tutorial/sources.json)。

### 在 AstrBot 填写哪里

打开 **插件 → 插件 → 已安装**，点击 **Flux by Ace Data Cloud** 卡片齿轮（插件配置），在 **Ace Data Cloud generation API key with Flux access**（字段 `api_key`）粘贴 Key 并保存。只填 Key 本身，不加 `Bearer `；不填到模型提供商或聊天消息。界面遮罩不加密磁盘配置，请保护 AstrBot 数据目录。此处提供准确文字路径；不以假界面代替本插件最新设置截图。

## 生成一次，然后查询

可以对机器人说：

> 用 `flux_generate_image` 生成一张纯蓝背景上的黄色纸船，模型 `flux-dev`，尺寸 `1024x1024`。只提交一次并告诉我任务 ID。

工具会异步提交一次 `POST /flux/images` 请求，固定生成一张，返回 `status: submitted` 和任务 ID。这时还不能认为图片已完成。保存 ID，随后说：

> 用 `flux_get_task` 查询刚才的准确任务 ID `<task_id>`，告诉我状态与最终图片链接，不要重新生成。

如果仍是 pending，稍后继续查询同一个 ID。只有 `status: succeeded`、`success: true` 和最终 HTTPS 图片链接同时出现才算完成。插件不会自动重试付费提交。

首版生成支持 `flux-dev`、`flux-pro`、`flux-2-klein`、`flux-2-flex`、`flux-2-pro` 和 `flux-2-max`。编辑您有权处理的图片时，传入公开的 HTTPS `image_url`，选择 `flux-kontext-pro` 或 `flux-kontext-max`。`flux-dev` 和 `flux-pro` 使用 `1024x1024`、`1024x1792` 或 `1792x1024` 像素尺寸；本插件将 `flux-2-klein` 限定为 `1024x1024`；其余模型使用 `1:1`、`16:9` 等图片比例。省略 `size` 时插件会选对应模型的默认值。首版只提交一张图片；Flux 视频、批量生成和高级控制尚未覆盖。

## 核验与排查

在 Ace Data Cloud 用量记录中优先按返回的 trace ID 核对。任务结果可能包含以 Credits 计的公开 `cost` 字段；以实时用量记录为扣费依据。任务查询只读取已有任务，不会再次生成。

| 现象 | 检查 |
| --- | --- |
| 插件加载失败 | AstrBot 版本、**加载失败的插件**和**数据与日志 → 日志**。 |
| 看不到工具 | 插件启用、当前 profile 与 persona 允许两个工具、对话模型支持工具调用。 |
| HTTP 401/403 | Key 类型、两个 API 路径的权限和账号访问权限。 |
| 提交后网络报错 | 再次生成前先看请求历史；超时也可能已创建付费任务。 |
| 任务仍在进行 | 稍后查询同一个任务 ID。 |
| 任务失败 | 用任务 ID 或 trace ID 查请求历史。 |

Key 只会发送到 `https://api.acedata.cloud`，重定向会被拒绝。插件只把最终图片链接和公开的费用字段交给对话模型，不返回内部原始数据。运行时仅用 Python 标准库。

## 验收与品牌图标

在官方 AstrBot `v4.28.2` 的隔离实例中，editable 安装成功注册两个工具。ChatUI 用 `flux-dev` 和 `1024x1024` 提交了一次图片任务，并通过 `flux_get_task` 查询同一个任务 ID 一次，没有重复生成。最终 PNG 返回 HTTP 200、`image/png`，尺寸为 1024×1024。生成任务的准确 trace ID 对应一条成功的 `/flux/images` 用量记录，实扣 0.216 Credits；任务返回的原价为 0.24 Credits。见[脱敏实测证据](../tests/e2e-results.json)。编辑和其他模型仅做结构校验，未实际生成。这只是本地 editable 安装；Cloud 审核、市场安装以及市场包的首次调用仍待完成。

`logo.png` 是[当前 Flux 服务图标](https://cdn.acedata.cloud/ogm2oa.png)的原文件，364×364，SHA-256 为 `e1c93722db66db1f3721d4b1e02f1e63f130a6a41151476856e51fca914e7c94`。
