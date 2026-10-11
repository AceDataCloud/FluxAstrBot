# AstrBot Flux 图片插件

通过您自己的 Ace Data Cloud 账号，在 AstrBot 对话中生成或编辑一张 Flux 图片。`flux_generate_image` 提交一次任务，`flux_get_task` 用同一个任务 ID 查询最终结果。

[English guide](../README.md) · [Flux 图片接口](https://platform.acedata.cloud/documents/flux-images) · [Flux 任务接口](https://platform.acedata.cloud/documents/flux-tasks) · [当前价格](https://platform.acedata.cloud/services/flux)

## 查找与安装

在 AstrBot WebUI 中打开 **扩展 → 插件 → AstrBot 插件市场**，搜索 **Flux**。核对卡片名称 **Flux by Ace Data Cloud**、作者 **acedatacloud** 和[当前 Flux 服务图标](https://cdn.acedata.cloud/ogm2oa.png)，安装后在**已安装**页检查加载状态。

官方 AstrBot Cloud 上架仍待完成。源码合并后，可通过**已安装 → 安装 (+) → 从 URL 安装**并填写 `https://github.com/AceDataCloud/FluxAstrBot` 预览。通过 URL 安装不代表已在官方市场上架。

## 配置密钥

在 [Ace Data Cloud 应用管理](https://platform.acedata.cloud/console/applications)复制生成 API Key，或创建同时允许 `/flux/images` 与 `/flux/tasks` 的 Key。提交前查看当前模型价格和余额。将 Key 填入插件的 **Ace Data Cloud generation API key with Flux access** 配置项，不要添加 `Bearer `，也不要使用 `platform-...` 管理令牌。AstrBot WebUI 会遮蔽显示此字段，但原值保存在数据目录中，请保护该目录。

选择支持工具调用的对话模型，并在当前对话的 profile 与 persona 中允许两个 Flux 工具。

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
