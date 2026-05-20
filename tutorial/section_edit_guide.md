# Site Section Edit Guide

这份文档讲如何编辑你站点里的这五块内容：

- `News`
- `Education`
- `Intern`
- `Publications`
- `Honors&Awards`

它们分别由下面这些文件控制：

| 板块 | 数据文件 | 展示模板 | 当前显示位置 |
| --- | --- | --- | --- |
| News | `/Users/syu/LiMing/lm.github.io/_data/news.yml` | `/Users/syu/LiMing/lm.github.io/_includes/sections/news.html` | 首页 `/` |
| Education | `/Users/syu/LiMing/lm.github.io/_data/education.yml` | `/Users/syu/LiMing/lm.github.io/_includes/sections/education.html` | 首页 `/` |
| Intern | `/Users/syu/LiMing/lm.github.io/_data/intern.yml` | `/Users/syu/LiMing/lm.github.io/_includes/sections/intern.html` | 首页 `/` |
| Publications | `/Users/syu/LiMing/lm.github.io/_publications/*.md` | `/Users/syu/LiMing/lm.github.io/_includes/sections/publications.html` | 首页 `/` 和 `/publications/` |
| Honors&Awards | `/Users/syu/LiMing/lm.github.io/_data/honors.yml` | `/Users/syu/LiMing/lm.github.io/_includes/sections/honors.html` | `/cv/` |

首页内容由下面这个文件串起来：

`/Users/syu/LiMing/lm.github.io/_pages/about.md`

## 1. 通用修改流程

1. 打开对应的数据文件。
2. 按已有格式新增、删除或修改条目。
3. 保存后提交并推送到 GitHub。
4. 等 GitHub Pages 自动部署。

如果你本地已经配好 Jekyll，也可以先预览：

```bash
cd /Users/syu/LiMing/lm.github.io
bundle exec jekyll serve
```

推送命令通常是：

```bash
cd /Users/syu/LiMing/lm.github.io
git add .
git commit -m "Update website sections"
git push origin main
```

## 2. 如何编辑 News

对应文件：

`/Users/syu/LiMing/lm.github.io/_data/news.yml`

当前格式是一个 YAML 列表，每一条 news 都有 3 个字段：

- `date`: 显示日期
- `icon`: 前面的 emoji 或符号
- `html`: 新闻正文，支持 HTML

示例：

```yaml
- date: "2026.4"
  icon: "🚀"
  html: 'Joined <a href="https://hyper3d.ai/">Rodin</a> as an <span class="news-highlight">Intern Researcher</span>.'
```

### 新增一条 News

建议直接加在文件最上面，因为 `news.html` 是按文件中的顺序从上到下显示的，不会自动排序。

例如：

```yaml
- date: "2026.5"
  icon: "🎉"
  html: 'Started a new project on <span class="news-highlight">interactive 3D editing</span>.'
```

### 注意事项

- `html` 字段支持超链接、加粗高亮等 HTML 标签。
- 如果文本里有冒号 `:`、引号或 HTML，建议像现在一样用引号包起来。
- 想调整显示顺序，直接在 `news.yml` 里上下移动条目即可。

## 3. 如何编辑 Education

对应文件：

`/Users/syu/LiMing/lm.github.io/_data/education.yml`

每条教育经历有 3 个字段：

- `title_html`: 学校名称，支持 HTML 链接
- `program`: 学位或项目名称
- `dates`: 时间范围

示例：

```yaml
- title_html: '<a href="https://www.hit.edu.cn/">Harbin Institute of Technology</a>'
  program: "B.Eng. in Computer Science and Technology"
  dates: "2021.9 - 2025.7"
```

### 新增一段 Education

直接追加一个新条目即可：

```yaml
- title_html: '<a href="https://www.example.edu/">Example University</a>'
  program: "M.S. in Computer Science"
  dates: "2026.9 - 2028.6"
```

### 注意事项

- `title_html` 支持多个学校一起写，也支持中间用 `-` 连接。
- 当前模板也是按文件顺序显示，不自动排序。
- 如果你想把最近的经历放前面，就把最新经历放在最上方。

## 4. 如何编辑 Intern

对应文件：

`/Users/syu/LiMing/lm.github.io/_data/intern.yml`

这部分和 `News` 不一样，它不是列表，而是单个对象。也就是说，当前模板默认只展示一段实习经历。

字段如下：

- `company_html`: 公司名，支持 HTML 链接
- `team_role`: 团队和职位
- `description`: 简介
- `logo`: 图片路径，路径是相对于 `/images/`
- `logo_alt`: 图片的替代文本

示例：

```yaml
company_html: '<a href="https://hyper3d.ai/">deemos</a>'
team_role: "Rodin team, Intern Researcher"
description: "Research on 3D generation and editing."
logo: "rodin_logo.jpg"
logo_alt: "deemos Rodin logo"
```

### 修改实习信息

直接改这 5 个字段即可。

### 修改 Logo

当前模板会把 `logo` 自动拼成：

`/images/你的文件名`

所以如果图片在：

`/Users/syu/LiMing/lm.github.io/images/rodin_logo.jpg`

那么写：

```yaml
logo: "rodin_logo.jpg"
```

如果图片放在子目录，例如：

`/Users/syu/LiMing/lm.github.io/images/company/example.png`

那么写：

```yaml
logo: "company/example.png"
```

### 注意事项

- 当前模板只能显示一段 internship。
- 如果你以后想展示多段实习，需要把 `/Users/syu/LiMing/lm.github.io/_data/intern.yml` 改成列表，并同步修改模板 `/Users/syu/LiMing/lm.github.io/_includes/sections/intern.html`。

## 5. 如何编辑 Publications

对应目录：

`/Users/syu/LiMing/lm.github.io/_publications/`

这里不是一个总表，而是“一篇论文一个 Markdown 文件”。

当前页面会自动读取：

`site.publications`

然后按 `date` 从新到旧排序。

### 新增一篇论文

在这个目录下新建一个文件，建议命名格式：

`YYYY-MM-DD-short-name.md`

例如：

`2026-02-20-reweaver.md`

最小模板如下：

```yaml
---
title: "Paper Title"
collection: publications
category: conferences
permalink: /publication/paper-slug
date: 2026-02-20
venue_display: "CVPR 2026"
authors_html: 'Author A, <span class="pub-self">Ming Li</span>, Author C'
teaser:
projecturl:
paperurl:
arxivurl:
codeurl:
dataseturl:
pressurl:
---
```

### 字段说明

- `title`: 论文标题
- `collection`: 固定写 `publications`
- `category`: 一般写 `conferences`，也可以按你的分类体系修改
- `permalink`: 论文详情页链接，建议唯一
- `date`: 用来排序，格式建议固定为 `YYYY-MM-DD`
- `venue_display`: 页面上显示的会议或期刊名称
- `authors_html`: 作者列表，支持 HTML，可用 `<span class="pub-self">Ming Li</span>` 高亮自己
- `teaser`: 预览图路径，路径相对于 `/images/`
- `projecturl` 到 `pressurl`: 这些字段非必填，填了才会显示对应按钮

### 预览图怎么放

当前模板会把 `teaser` 自动拼成：

`/images/你的路径`

例如，如果图片放在：

`/Users/syu/LiMing/lm.github.io/images/pub/ReWeaver.png`

那么条目里写：

```yaml
teaser: "pub/ReWeaver.png"
```

如果 `teaser` 留空，页面会显示一个占位框。

### 示例

你现在仓库里的一个真实例子是：

`/Users/syu/LiMing/lm.github.io/_publications/2026-02-20-reweaver.md`

### 注意事项

- Publications 的顺序不是文件顺序，而是 `date` 顺序。
- 想让一篇论文排到前面，改 `date` 即可。
- `permalink` 最好不要和其他论文重复。
- 如果你希望论文详情页有更多内容，可以在 YAML 头之后继续写正文，比如 abstract、project note、bibtex 等。

## 6. 如何编辑 Honors&Awards

对应文件：

`/Users/syu/LiMing/lm.github.io/_data/honors.yml`

每条奖励有两个字段：

- `year`: 年份或年份范围
- `text`: 奖项文字

示例：

```yaml
- year: "2021-2022"
  text: "Outstanding Student of the Year, Harbin Institute of Technology"
```

### 新增一条奖项

直接在文件里增加新条目：

```yaml
- year: "2026"
  text: "Example Fellowship"
```

### 注意事项

- 当前模板按文件顺序显示，不自动排序。
- 如果想按时间倒序展示，建议把最新奖项放在最上面。

## 7. 常见坑

### YAML 缩进

YAML 对缩进很敏感。列表项前面要用 `-`，同一级字段要对齐，例如：

```yaml
- year: "2024"
  text: "..."
```

不要写成：

```yaml
- year: "2024"
    text: "..."
```

### HTML 字段

下面这些字段支持 HTML：

- `news.yml` 里的 `html`
- `education.yml` 里的 `title_html`
- `intern.yml` 里的 `company_html`
- `_publications/*.md` 里的 `authors_html`

如果你想加链接或高亮，可以直接写 HTML。

### 图片路径

- `Intern` 的 `logo`
- `Publications` 的 `teaser`

都不要写完整绝对路径，也不要手动写 `/images/` 前缀。直接写相对于 `images/` 的路径即可。

正确示例：

```yaml
logo: "rodin_logo.jpg"
teaser: "pub/ReWeaver.png"
```

### 多段 Intern

当前站点的 `Intern` 是单条结构，不是列表。如果你直接照 `News` 那样写多个 `- item`，页面不会按你预期显示。

## 8. 一份最短操作清单

如果你只是想快速改内容，可以按下面记：

- 改 News：编辑 `/Users/syu/LiMing/lm.github.io/_data/news.yml`
- 改 Education：编辑 `/Users/syu/LiMing/lm.github.io/_data/education.yml`
- 改 Intern：编辑 `/Users/syu/LiMing/lm.github.io/_data/intern.yml`
- 改 Publications：编辑 `/Users/syu/LiMing/lm.github.io/_publications/*.md`
- 改 Honors&Awards：编辑 `/Users/syu/LiMing/lm.github.io/_data/honors.yml`

改完后：

```bash
cd /Users/syu/LiMing/lm.github.io
git add .
git commit -m "Update website content"
git push origin main
```
