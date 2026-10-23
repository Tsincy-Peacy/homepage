# Yi Zhang 的学术主页

面向国际学术交流的个人主页，默认提供英文内容，并设有中文简介。当前身份为中国科学技术大学人工智能与数据科学学院研究生一年级，研究方向为类脑神经网络。

## 项目结构

项目继续使用 MkDocs 将 Markdown 构建为静态网站，以独立的 `theme/` 模板替换原有文档门户式外观。无需 Node.js、前端打包工具或数据库。

| 路径 | 用途 |
| --- | --- |
| `docs/index.md` | 英文主页：个人简介、研究方向、荣誉与联系 |
| `docs/zh/index.md` | 中文简介 |
| `docs/about.md` | 教育背景和完整奖项 |
| `docs/certificates/` | 已有奖项证书 |
| `theme/` | 页面结构、导航及 404 模板 |
| `docs/stylesheets/academic.css` | 排版、响应式布局与打印样式 |
| `mkdocs.yml` | 网站地址、导航、扩展和联系方式 |
| `requirements.txt` | 固定版本的 Python 构建依赖 |
| `scripts/check_site.py` | 构建产物的链接、锚点、语言与内容清理检查 |

## 本地开发

推荐 Python 3.12；CI 使用相同版本。

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m mkdocs serve
```

macOS / Linux：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m mkdocs serve
```

浏览器打开终端输出的本地地址（默认 `http://127.0.0.1:8000/`）。修改 Markdown、模板和样式后自动重新构建。

提交前运行以下命令。请将 `python` 替换为所用虚拟环境的解释器路径，或先激活虚拟环境：

```sh
python -m mkdocs build --strict
python scripts/check_site.py
```

输出位于 `site/`，已加入 `.gitignore`。网站包含英文主页、学术背景、中文简介及 404 页面，共四个 HTML 页面。检查脚本只使用 Python 标准库，验证站内链接、资源、跨页面锚点、页面语言及已删除内容的发布情况，并检查笔名的语言范围和分隔符样式。页面布局另需在浏览器中检查。

## 内容维护

- 中英文主页分别维护在 `docs/index.md` 与 `docs/zh/index.md`，身份、研究方向和重要奖项应同步更新。
- 笔名及其相关描述仅出现在中文简介中。英文页面使用 Yi Zhang，中文姓名为张义。
- 文案使用完整、自然的句子；必要的标签与元信息分别排版，省略无实际作用的装饰性短语和中点分隔符。
- 首页左侧身份信息位于 `theme/main.html`；教育背景同时更新 `docs/about.md`。
- 邮箱与 GitHub 地址在 `mkdocs.yml` 的 `extra` 中配置；正文中直接写入的联系链接也需同步修改。
- 修改姓名、身份或研究方向时，同时更新 `mkdocs.yml` 的网站描述及各页面的 `description` 元信息。
- 获得正式论文信息后再增加 Publications 栏目，使用真实作者、标题、会议或期刊、年份和 DOI / 论文链接。
- 添加 Markdown 页面后更新 `mkdocs.yml` 的 `nav` 和相关入口；页面间优先使用 Markdown 源文件链接，让 MkDocs 生成正确的相对路径。

## GitHub Pages

当前 `site_url` 为 `https://tsincy-peacy.github.io/Homepage/`。仓库路径前缀用于规范链接、站点地图及 404 页面；更换仓库名称、账户或自定义域名时必须同步修改 `mkdocs.yml`，然后重新构建并检查。

工作流对 Pull Request 只执行构建与检查。推送至 `main` 且验证通过后，使用 `mkdocs gh-deploy --strict` 发布到 `gh-pages` 分支。GitHub 仓库的 **Settings → Pages** 应选择 **Deploy from a branch → gh-pages → /(root)**。
