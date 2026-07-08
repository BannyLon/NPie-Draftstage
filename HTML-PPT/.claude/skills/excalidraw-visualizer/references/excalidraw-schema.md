# Excalidraw 元素格式参考

## .excalidraw 文件顶层结构

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "excalidraw-visualizer-skill",
  "elements": [...],
  "appState": {
    "viewBackgroundColor": "#ffffff"
  }
}
```

## 元素类型

| type | 说明 | 特有属性 |
|------|------|----------|
| `rectangle` | 矩形 / 圆角矩形 | `roundness` |
| `diamond` | 菱形 | - |
| `ellipse` | 椭圆/圆形 | - |
| `arrow` | 箭头连线 | `points`, `startBinding`, `endBinding`, `endArrowhead` |
| `text` | 文本标签 | `text`, `fontSize`, `fontFamily`, `containerId` |
| `line` | 直线 | `points` |

## 所有元素共享的属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识符 |
| `type` | string | 元素类型 |
| `x` | number | 画布 X 坐标 |
| `y` | number | 画布 Y 坐标 |
| `width` | number | 元素宽度 |
| `height` | number | 元素高度 |
| `angle` | number | 旋转角度 (弧度) |
| `strokeColor` | string | 描边颜色 (hex) |
| `backgroundColor` | string | 填充颜色 (hex) |
| `fillStyle` | string | `solid` / `hachure` / `cross-hatch` |
| `strokeWidth` | number | 描边宽度 (1-4) |
| `roughness` | number | 手绘程度: 0=完美, 1=轻微, 2=强烈 |
| `opacity` | number | 透明度 (0-100) |
| `seed` | number | 随机种子，不同值产生不同手绘抖动 |
| `version` | number | 版本号 (非降级可用) |
| `isDeleted` | boolean | 是否已删除 |
| `groupIds` | array | 所属组 ID 列表 |
| `boundElements` | array | 绑定的子元素引用 `[{type, id}]` |
| `updated` | number | 更新时间戳 |
| `link` | string? | 超链接 |
| `locked` | boolean | 是否锁定 |

## 形状特有属性

### roundness
```json
// 直角
{ "type": null }

// 小圆角
{ "type": 2 }

// 全圆角 (pill)
{ "type": 3 }
```

### arrow 特有
```json
{
  "points": [[0,0], [dx, dy]],
  "startBinding": { "elementId": "src-id", "focus": 0, "gap": 0 },
  "endBinding": { "elementId": "tgt-id", "focus": 0, "gap": 0 },
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

### text 特有
```json
{
  "text": "显示的文本内容",
  "fontSize": 16,
  "fontFamily": 1,
  "textAlign": "left | center | right",
  "verticalAlign": "top | middle | bottom",
  "containerId": "所属形状的ID" // 嵌套在形状内时使用
}
```

## 字体

| fontFamily | 名称 | 风格 |
|-----------|------|------|
| 1 | Virgil | 手写体 (默认，配合手绘风格) |
| 2 | Normal | 无衬线体 |
| 3 | Code | 等宽代码字体 |

## 元素绑定关系

形状和文本的绑定:
```
形状.boundElements = [{ "type": "text", "id": "text-id" }]
文本.containerId = "形状-id"
```

箭头和形状的绑定:
```
箭头.startBinding = { "elementId": "形状-id", "focus": 0, "gap": 5 }
箭头.endBinding = { "elementId": "形状-id", "focus": 0, "gap": 5 }
```
