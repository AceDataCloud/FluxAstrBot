# Flux images for AstrBot

Generate or edit one Flux image in an AstrBot conversation through your own Ace Data Cloud account. `flux_generate_image` submits a job, and `flux_get_task` retrieves that same task until its final image is ready.

[简体中文指南](readme/README_zh_Hans.md) · [Flux Images API](https://platform.acedata.cloud/documents/flux-images?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fluxastrbot_readme_documents_flux_images) · [Flux Tasks API](https://platform.acedata.cloud/documents/flux-tasks?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fluxastrbot_readme_documents_flux_tasks) · [Current prices](https://platform.acedata.cloud/services/flux?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fluxastrbot_readme_services_flux)

## Find and install

In AstrBot WebUI, open **Extensions → Plugins → AstrBot Plugin Market** and search **Flux**. Confirm the card says **Flux by Ace Data Cloud**, the author is **acedatacloud**, and the logo matches the [current Flux service icon](https://cdn.acedata.cloud/ogm2oa.png). Install it, then check **Installed** for load errors.

The official AstrBot Cloud listing is pending. After the source release is merged, **Installed → Install (+) → Install from URL** with `https://github.com/AceDataCloud/FluxAstrBot` can preview it. A URL installation does not prove market publication.

## Configure your key

New account? Register and sign in first. If the Applications page has no General application yet, choose **Initialize General Application**, then continue with the key steps below.

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=fluxastrbot_readme_api_key), copy a generation API key from your General application or create a key that permits both `/flux/images` and `/flux/tasks`. Check the current price and balance before submitting. Paste the key into the plugin's **Ace Data Cloud generation API key with Flux access** setting. Do not add `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

Select a chat model that supports tool calling. Allow both Flux tools in the conversation's profile and persona.

## Generate once, then query

Ask the bot:

> Use `flux_generate_image` once to create a yellow paper boat on a plain blue background. Use `flux-dev`, size `1024x1024`, and show me the task ID.

The tool sends one asynchronous `POST /flux/images` request with `count: 1` and returns `status: submitted` with a task ID. Keep the ID and ask:

> Use `flux_get_task` with the exact task ID `<task_id>`. Tell me its status and final image URL. Do not generate another image.

If pending, query the same ID later. Only `status: succeeded`, `success: true`, and a final HTTPS image URL indicate completion. The plugin never retries a paid submission automatically.

This first version supports generation with `flux-dev`, `flux-pro`, `flux-2-klein`, `flux-2-flex`, `flux-2-pro`, and `flux-2-max`. To edit an image you own or may process, include its public HTTPS URL as `image_url` and choose `flux-kontext-pro` or `flux-kontext-max`. For `flux-dev` and `flux-pro`, use pixel sizes `1024x1024`, `1024x1792`, or `1792x1024`; this plugin limits `flux-2-klein` to `1024x1024`. The other models use aspect ratios, such as `1:1` or `16:9`; omitting `size` selects a model-compatible default. This version submits one output image. Flux video, batch output, and advanced image controls are outside its scope.

## Verify and troubleshoot

In Ace Data Cloud usage, match a returned trace ID when available. A finished task may return public `cost` amounts in Credits; confirm the live usage row before treating an estimate as a charge. Task lookup reads an existing job and does not submit another generation.

| Symptom | Check |
| --- | --- |
| Plugin fails to load | AstrBot version, **Failed to Load Plugins**, and **Data & Logs → Logs**. |
| Tools are missing | Plugin enabled, both tools allowed in the active profile and persona, chat model supports tool calling. |
| HTTP 401/403 | Key type, both allowed API paths, and account access. |
| Network error after submission | Inspect request history before generating again; a timeout may already have created a paid task. |
| Pending task | Query the same task ID later. |
| Failed task | Use the task or trace ID to inspect request history. |

The key goes only to `https://api.acedata.cloud`; redirects are rejected. The plugin exposes final image URLs and public cost fields to the model, without raw internal data. It uses Python's standard library and needs no runtime package installation.

## Validation and brand asset

On official AstrBot `v4.28.2`, an isolated editable installation registered both tools. ChatUI submitted one `flux-dev` image at `1024x1024` and queried the same task ID once through `flux_get_task`, without another generation. The final PNG responded HTTP 200, `image/png`, and decoded at 1024×1024. The exact generation trace matched one successful `/flux/images` usage row with 0.216 Credits deducted; the completed task returned 0.24 Credits as its list amount. See the [sanitized evidence](tests/e2e-results.json). Editing and other models were validated structurally but not generated. This is a local editable installation; official Cloud review, market installation, and a first call from a market installation remain open.

`logo.png` is the unmodified 364×364 [current Flux service icon](https://cdn.acedata.cloud/ogm2oa.png), SHA-256 `e1c93722db66db1f3721d4b1e02f1e63f130a6a41151476856e51fca914e7c94`.
