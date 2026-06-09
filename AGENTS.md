# AGENTS.md

本文件是本仓库的协作规范，适用于工作台根目录及其所有子目录。除非某个子目录另有更具体的 `AGENTS.md`，否则后续代理都按本文件执行。

## 工作背景

- 站点所有者：Xu Lian（连序）。
- 当前身份：东南大学自动化学院大一学生。
- 站点定位：个人学术主页，用于逐步展示个人简介、研究兴趣、学习经历、项目、论文、博客和联系方式。
- 研究兴趣：robotic grasping、VLA models、world action models、robotic learning、autonomous driving。
- 当前仓库状态：本项目从他人的 Academic Pages/Jekyll 个人主页 fork 而来，仍可能包含原作者姓名、学校、导师、论文、实习、奖项、图片和博客内容。
- 工作目标：逐步把继承内容替换为符合 Xu Lian 本人情况的真实文案和结构；不编造尚未提供的信息。

## 内容原则

- 面向网页访客的学术文案默认使用英文；只有用户明确要求中文页面或中文说明时，才在网页正文中使用中文。
- 个人简介的基础事实以这段为准：
  `I am Xu Lian (连序), a freshman in the School of Automation at Southeast University. My research interests include robotic grasping, VLA models, world action models, robotic learning, and autonomous driving.`
- 标题、导航、页面元信息中使用 `Xu Lian`；在 About 页正文或完整简介中可使用 `Xu Lian (连序)`。
- 不添加未经用户确认的导师、实验室、论文、项目成果、获奖、实习、GPA、排名、基金、专利、录用状态或媒体链接。
- 当某个板块暂无真实内容时，优先隐藏该板块；若页面结构需要保留，使用 `To be updated.` 作为临时占位，并在回复中说明需要后续确认。
- 可见标题统一使用清晰英文：`Honors & Awards`、`Internships`、`Publications`、`Education`、`News`。

## 目录结构

- `_config.yml`：全站配置，包括站点标题、作者信息、头像、邮箱、社交链接、主题、URL 和仓库名。
- `_pages/`：顶层页面，包括首页/About、Publications、CV、归档、Talks、Teaching、Portfolio、Sitemap 等。
- `_data/`：结构化内容，包括 `news.yml`、`education.yml`、`intern.yml`、`honors.yml`、`navigation.yml`、`authors.yml`、`cv.json`。
- `_includes/sections/`：首页和页面中复用的板块组件，如 news、education、intern、honors、publications。
- `_publications/`：论文条目。只有用户提供真实论文信息或明确要求删除占位内容时，才替换或删除继承条目。
- `_posts/`：博客、笔记和文章。
- `_talks/`、`_teaching/`、`_portfolio/`：演讲、教学、项目集合；当前内容可能是原作者占位，修改前必须核对。
- `images/`：头像、图标、论文图、主题图和其他视觉资源。
- `files/`：公开下载文件，如 PDF、slides、BibTeX。
- `assets/`：CSS、JavaScript、字体和主题资源。
- `markdown_generator/`、`scripts/`、`talkmap/`、`tutorial/`：生成脚本、地图和教程；除非任务涉及这些功能，否则不改。
- `_site/`、`.sass-cache/`：构建产物和缓存；不得手动编辑，也不要把它们当作源文件。

## 编辑规则

- 修改前先查看相关源文件，并检查当前工作区状态，避免覆盖用户已有改动。
- 只改完成当前请求所必需的文件；不做顺手重构、不改无关样式、不批量清理无关内容。
- 修改 Jekyll 页面时保留原有 front matter 字段，除非字段本身导致页面行为错误。
- 优先修改 Markdown、YAML、Liquid include 和 Sass/JS 源文件；不直接修改 `_site/` 中的生成 HTML。
- YAML 保持原文件缩进风格；包含括号、URL、非 ASCII 字符或特殊符号的值使用引号。
- Markdown 页面标题要短；能复用 `_includes/sections/` 的地方不要重复写一份结构。
- 发现原作者信息时，只处理本次任务范围内的内容；不要在没有要求时整站删除。
- 需要删除继承内容时，确认该内容在当前页面或导航中确实会展示，或用户明确要求删除。
- 图片替换时，先确认引用路径；不要删除仍被页面引用的图片。
- 不提交、不推送、不创建 PR，除非用户明确要求。

## 验证规则

- 纯 Markdown/YAML 文案改动：至少检查 diff，并运行 `git diff --check`。
- 修改 `_config.yml`、布局、include、Sass 或 JavaScript 后：依赖可用时运行 `bundle exec jekyll build`。
- 修改 JavaScript 源文件后：依赖可用时运行 `npm run build:js`。
- 如果构建或命令因为依赖缺失失败，在回复中说明失败命令和原因，不要假装验证通过。
- 不用 `_site/` 的生成结果判断源文件是否正确；以源文件和本地构建结果为准。

## 协作规则

- 与用户沟通默认使用中文。
- 用户提供的新个人事实优先于仓库中继承的旧内容。
- 信息不足但可以用中性占位继续推进时，先推进并标注待确认；信息不足会导致事实错误时，向用户询问最小必要信息。
- 处理用户已有未提交改动时，只在相关上下文中合并修改；不得回滚用户改动。
- 每次完成修改后，说明改了哪些文件、影响哪些网页区域、做了哪些验证。
- 对代码或内容做 review 时，先列问题和文件位置，再给摘要。

## 输出格式

完成仓库修改后的最终回复按以下顺序写：

1. 一句话概括本次完成的事。
2. 列出修改文件和每个文件的作用。
3. 写明已执行的验证；如未能执行，说明原因。
4. 只在确实影响下一步时，列出需要用户补充的信息。

如果只是回答问题、不改文件，直接给结论和必要依据；不要套用修改汇报格式。
