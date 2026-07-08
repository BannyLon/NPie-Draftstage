# 生图提示词模板

每张图单独生成。根据正文内容替换变量，不要把多张图拼在一起。

```text
Generate one standalone 16:9 horizontal Chinese article illustration.

Visual DNA:
Pure white background. Warm hand-drawn style with soft pencil/ink lines and colored-pencil or light watercolor fill. Slightly organic, handmade pen strokes. Lots of empty white space. Sparse red/orange/blue handwritten Chinese annotations. Clean, warm, charming product-sketch feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no cold technical diagram, no realistic UI.

Recurring IP character required:
嗯哌哌, a warm and charming hand-drawn character with long straight dark center-parted hair flowing naturally past her shoulders, a soft rounded face with gentle features, large expressive dark eyes with a warm gentle gaze and subtle smile lines at the corners, soft arched eyebrows, small natural nose, rosy full lips, fair smooth skin with a natural faint blush. She wears a signature loose white knit sweater. Her proportions are slightly rounded and cute (eyes slightly larger, face soft), rendered in visible soft pencil/ink lines with colored-pencil or light watercolor warmth. 嗯哌哌 must be the core visual and emotional anchor of the scene — using her pose, expression, and gesture to convey the key idea, not passively standing in the corner.

Theme:
{正文配图主题}

Structure type:
{结构类型：Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜}

Core idea:
{这张图要表达的核心意思}

Composition:
{具体画面：嗯哌哌在哪里、正在做什么姿势或表情、主要物件是什么、信息如何流动}

Suggested elements:
{元素1} / {元素2} / {元素3} / {元素4}

Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4} / {可选标注词5}

Color use:
Black/dark-gray for main line art and character outlines. Orange for main flow/path/arrows/guidance. Red only for key highlights/emphasis/results. Blue only for secondary notes or feedback/system state. Warm soft pink/peach tones for 嗯哌哌's skin and sweater warmth — use sparingly.

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten Chinese labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Do not copy prior examples unless explicitly requested; invent a fresh visual metaphor for this specific article. It should feel warm and charming but still clean and clear — not cold, not overly cute, not childish.
```

## 图像编辑提示

去掉左上角标题：

```text
Edit the provided image. Remove only the handwritten title "{要删除的文字}" and its underline from the top-left corner. Fill that area with the same clean white background, matching the surrounding blank paper. Preserve everything else exactly: characters, labels, paths, line style, composition, aspect ratio, and image quality. Do not add any new text or objects.
```

增强嗯哌哌的情感核心：

```text
Regenerate this illustration with the same core meaning and simple layout, but make 嗯哌哌 more central to the visual and emotional expression. 嗯哌哌 should use her pose, expression, and gesture to convey the key idea, not just stand beside the diagram. Keep it clean, warm, hand-drawn, and charming — not cold or overly cute.
```
