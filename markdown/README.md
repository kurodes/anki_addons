# Anki Markdown

通过 Anki 卡片模板实现客户端 Markdown 渲染。

## 核心流程

```
卡片字段内容 (Markdown文本)
        ↓
   HTML模板加载
        ↓
   动态加载 JS/CSS 库
        ↓
   Showdown.js 转换 Markdown → HTML
        ↓
   highlight.js 代码高亮
        ↓
   显示渲染后的内容
```

## 依赖安装

使用 [Showdown](https://github.com/showdownjs/showdown) 作为 Markdown 转换器，[highlight.js](https://highlightjs.org/) 实现代码高亮。

1. 下载依赖文件：
   - https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.5/styles/default.min.css
   - https://cdnjs.cloudflare.com/ajax/libs/showdown/1.9.0/showdown.min.js
   - https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.5/highlight.min.js

2. 重命名文件（以 `_` 开头，绕过 Anki 对未引用文件的垃圾回收）：
   - `_highlight.default.min.css`
   - `_showdown.min.js`
   - `_highlight.min.js`

3. 移动到 collection.media 目录：
   - macOS: `~/Library/Application Support/Anki2/User 1/collection.media/`

## 代码逻辑

### 模板结构

```html
<div class="section">
    <div class="question md-content">{{Question}}</div>
</div>
```

- `{{Question}}` 是 Anki 字段占位符，包含原始 Markdown 文本
- `md-content` 类标记需要被渲染的 div

### 依赖加载 (front_template.html:34-38)

按顺序动态加载三个文件：
1. `_highlight.default.min.css` - 代码高亮样式
2. `_showdown.min.js` - Markdown 转换器
3. `_highlight.min.js` - 代码语法高亮

### 渲染处理 (front_template.html:39-57)

```javascript
document.querySelectorAll('div.md-content').forEach((div) => {
    replaceImage(div);                                  // 预处理图片
    var text = replaceAllWhitespaceWithSpace(rawText);  // 规范化空白字符
    var html = showdownConverter.makeHtml(text);        // Markdown → HTML
    // 创建新 div 显示渲染结果，隐藏原始 div
    div.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);                     // 代码高亮
    });
});
```

### 背面模板 (back_template.html)

```html
{{FrontSide}}
<hr id=answer>
<div class="section">
    <div id="back" class="Description md-content">{{Answer}}</div>
</div>
```

复用正面的 JS 代码（通过 `{{FrontSide}}`），同样用 `md-content` 类标记答案字段。

## 使用方式

1. 按上述步骤安装依赖文件
2. 在 Anki 中创建笔记类型，将 `front_template.html`、`back_template.html`、`styling.css` 的内容分别粘贴到对应位置
3. 在卡片字段中直接写 Markdown 语法即可
