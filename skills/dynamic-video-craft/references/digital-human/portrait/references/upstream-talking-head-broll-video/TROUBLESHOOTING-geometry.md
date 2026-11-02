# 排障：图表压扁 / 元素塌陷 / AI 素材通道

本文件记录已被浏览器实测验证过的根因与解法。
**铁律：判断「修好了没有」只认探针数据，不认抽帧截图。**
截图经过缩放后畸变更难判断，多次误判都源于此。

---

## 一、图表压扁（最高频问题）

### 真正的根因
**svg 的 viewBox 宽高比必须贴合它实际落进的容器宽高比。**
不匹配时 `preserveAspectRatio="none"` 会强行拉伸 → 视觉上就是「压扁」。

畸变量 = 实际渲染 AR / viewBox AR。超过 1.35 就肉眼可见。

### 三个反面案例（都实测过）

| 坑 | 做法 | 结果 |
|---|---|---|
| 1 | 方形 viewBox 620×360（AR 1.72）塞进 solo-band 容器 1540×250（AR 6.16） | 畸变 3.44 倍，就是用户投诉的「图表压扁」 |
| 2 | 改 `preserveAspectRatio="xMidYMid meet"` | 只是把变形换成留白：内容缩成 447×260，左右各空 546px，图表成中间一小条 |
| 3 | 加 `min-height: 260px` 想保底 | min-height 从「保底闸」退化成「天花板」：父容器有 324px 可用，svg 被钉死 260px |

### 正确解法（按顺序排查）

1. **先让 viewBox 比例贴合容器**
   - 宽扁容器（solo-band，AR≈6）→ 宽幅坐标系 `1550×330`（AR 4.70）
   - 方形容器（full / solo-wide 单组件，AR≈1.72）→ `620×360`
   - 比例吻合后 `none` 才是最优解（既铺满又不变形），不要盲目换 `meet`

2. **svg 必须能被 flex 拉伸**
   ```css
   .chart svg { flex: 1 1 0; width: 100%; height: 0; min-height: 180px; }
   ```
   `height: 0` 是关键。svg 是替换元素有「固有尺寸」，
   `flex-basis: auto` 会拿固有尺寸当起点，flex 就不再往上拉伸，
   最后只剩 min-height 在撑 → 表现为「svg 死守 180px 不长」。

3. **双组件镜要处理空间竞争**
   - `flex: 1 1 auto` 会按内容高度分配，内容天生高的组件（大数字）会赢。
     实测 S07：big-number 拿 494px，area-chart 只剩 220px。
   - 改 `flex-basis: 0` 才是真均分；图表要看清趋势，建议倾斜给 `3 : 2`。
   - **主副组件必须同时改**，单边改无效。

4. **副组件图表要给固定开销瘦身**
   窄带场景下 `padding(56) + cap(30) + margin(16) = 112px` 是奢侈品。
   实测 S54：.chart 只有 214px，扣完只剩 102px 给曲线。
   ```css
   .c-area-chart.is-second .chart { padding: 16px 22px 14px; }
   .c-area-chart.is-second .chart svg { margin-top: 8px; min-height: 150px; }
   ```

5. **版式选择必须考虑组件数量**
   `SOLO_OF` 只按主组件选版式，会让双组件镜落进最矮的框。
   反面案例 S54：`big-type` → solo-wide（frame-b 仅 660px，全版式最矮），
   两块内容挤进去后图表只有 160px，怎么调都是压扁。
   ```python
   if len(cs) > 1 and lay in ('solo-wide', 'solo-band'):
       lay = 'solo-tall'   # 890px，多出的 230px 正好让图表过闸
   ```

### 副组件降级：按类型分流，不要一刀切
- **大数字 / 大字**类副组件 → 角标化，绝对定位到右下角，彻底脱离 flex 流
  （留在 flex 流里，它占的每一像素都是从图表身上扣的）
- **图表**类副组件 → 它是「第二块画面」不是角标，必须留高度参与 flex
  （曾把 area-chart 一起角标化，S07/S54 直接从 1660×964 塌成 310×180）

绝对定位需要父元素有定位上下文，记得给 `.b-pad` 加 `position: relative`，
否则角标会挂到 `.frame-b` 上，随各版式 padding 差异漂移。

---

## 二、探针脚本（确定性核验）

### `_chart_probe.py` — 图表几何闸
两条判据：高度闸（`clientHeight >= 240`）+ 畸变闸（`实际AR / viewBox AR <= 1.35`）。

**选择器必须收窄为 `.chart > svg`**：
`bn__spark` / `rule-strip` 这类装饰性迷你走势条本就是细长条
（AR 8+ 是设计意图，不是畸变），混进门禁会把判据带偏，
真问题被噪声淹没（首版探测 11 个 svg 里 8 个 FAIL，全是噪声）。

**不要把 `par != 'xMidYMid meet'` 写成判据** —— 比例吻合时 `none` 才对。
门禁判据要衡量「畸变量」，而不是「用了哪个属性」。

### `_box_probe.py` — 盒模型链
递归打印容器的 tag/class/宽高/display/flex/min-height。
排查「空间被谁吃掉了」时用它，一眼就能看出：
父容器有多少、子元素各拿多少、哪个 min-height 在硬撑。

---

## 三、AI 图 / AI 视频素材通道

> **已迁出到 `AI-ASSET-CHANNEL.md`**，避免两处维护导致结论打架。
>
> ⛔ **默认不走 AI 通道**（用户明确指令：不需要 AI 生成图片和视频）。
> B-roll 一律用本地零成本形式实现。仅当用户当次明确要求时才查阅那份文档。
>
> 那里记录了：工具通道硬约束、RunningHub 四步流程、
> **通道可用性实测表**（`ltx23` 可用 / `minimax-h3` 文生故障 / 图生视频形态不支持）、
> `localFilePath` 在 HTTP MCP 下失效的真根因、并发=1 纪律、
> 提示词要点、AI 视频镜的合成侧处理（contrast/brightness 配平、纸幕达成率）。

---

## 四、通用工程注意

- **日志落盘时机**：脚本若重定向 `sys.stdout` 到文件，运行期间日志是 0 字节，
  进程完全退出后才一次性 flush。所以直接跑看不到输出，必须读 `.log`。
- **Windows `timeout` 冲突**：Git Bash 下 `timeout 900 python ...` 会触发
  Windows 内建 TIMEOUT 报「无效语法」，但脚本实际仍完整执行。别用。
- **抽帧时间点**：取镜头中段（`start + dur * 0.6~0.7`），
  取起点会截到入场动画未完成的半透明中间态。
- **片段命名**：是 `scene-44.mp4` 不是 `S44.mp4`。
- **`python -c` 内嵌反斜杠替换**在 Bash 转义后易变成未闭合字符串，
  写独立脚本文件更稳。具体地，Python 字符串里的 `\s` 会被吞掉，
  内联 JS 正则 `replace(/\s/g,'')` 会触发 `SyntaxWarning`
  并让 JS 报 `Invalid or unexpected token`。
- **`lstrip('0')` 陷阱**：HTML 文件名是零填充的 `scene-08.html`，
  取镜号必须用 `.zfill(2)`，用 `lstrip('0')` 会把 `08` 变成 `8`
  导致 `ERR_FILE_NOT_FOUND`，而探针会把加载失败静默 parse 成 `nan%`。
- **numpy / Pillow 只装在系统 Python 3.11 里**，托管的 3.13.12 没有。
  用到像素统计的脚本（`_shot_health.py` 等）必须显式用系统解释器跑。
  注意裸 `python x.py` 失败时，若 stderr 走了管道，外层仍可能显示
  `exit=0`，很容易误判成「跑过了」——务必看 stdout 有没有实际表格。

---

## 五、验收方法论（本轮血泪总结，最容易重复踩坑）

### ★ 目视验收不可信，必须用像素统计做机器判据

用 `Read` 直接看大 PNG 时图会被缩放，肉眼判断极不可靠。实测矛盾案例：
`fix_s07.png` 被读成「大面积噪点」，而 `_chart_probe.py` 独立测得
S07 图表宽 1496 / 畸变 1.07 完全正常 —— 两个结论互相打架。

既然目视通道不可信，就用 `_shot_health.py` 的三条判据一起看
（缺一条都会误判）：

| 指标 | 正常区间 | 异常含义 |
|---|---|---|
| `mean` 整体亮度 | 150~250（纸艺底色 ~247） | `>252` 且 std 极小 = 页面没渲染出来 |
| `std` 明暗跨度 | `>= 6` | `<6` = 画面几乎没内容（空白页） |
| `dark%` (L<110) | 1%~25% | `0%` = 一个字没画上；`>60%` = 整片黑 |

实测 10 个 `layout-full` 镜次：`mean 189~212 / std 46~55 / dark% 4~7%`，
全部落在正常区间。

### ★ 探针报警必须用「单镜双模对照」复核，不能直接照批量结果改全局

批量探针报 S28「文字 LOW 1→2（新增 1）」，看似视频透穿导致新增问题。
但单独跑双模对照，**含视频与基线都是 1 处 LOW，增量实际为 0** ——
批量跑与单跑的抓帧时刻不同会造成偶发差异。

**判据永远是「含视频 LOW 数 − 基线 LOW 数」的增量**，
基线本身就不合格的元素属于设计问题，不该记在视频头上（但仍要修）。

### ★ 文字对比度报警的三态归因法（勿跳步直接调颜色）

报 LOW 后先量 ROI 的 `min/max`，再分流：

1. `min=0` 且 max 很低 → **被遮挡**，查 `elementsFromPoint` 图层栈
2. `min` 很高（如 156）、无暗像素 → **溢出画框**，量的是画框外页面底色
3. min/max 跨度正常但 Δ 不足 → 才是**真的配色问题**

反面案例：S31「7 : 3」Δ=15，按配色问题加了 `text-stroke: 6px`
+ `paint-order: stroke` + 双层 `text-shadow`，**复测依然 Δ=15 毫无变化**。
量像素才发现 `min=0 max=15` 整块纯黑 = 被数字人小窗盖住。

### ★ 「淡而不透」修法

配角元素不该靠半透明表达，而应靠**墨色抬实 + 字重降低 + 字号略收**表达。
半透明会让暗视频直接透穿。

- S09 `.vs__t/.vs__s`：`.46/.42` → `.62/.60`，Δ 83/77 → 达标
- S28 `.an__eq`：`rgba(60,44,24,.34)/900/54px` → `.74/700/48px`，Δ 70 → 122

### ★ 遮挡的正确修法是「挪走」而非「加底衬」

底衬盖不住 `z-index:3` 的数字人小窗。`layout-full` 的 `.frame-a` 是
`right:72 / bottom:180 / 246×328` 的右下角画中画，实测占据
`x 1602~1848、y 572~900`（10 个镜次逐一验证，几何值完全一致）。

- `.rule-strip b` → `order:-1` 挪到刻度尺左端（x 起点 ~92，余量 1500px，永久安全）
- SVG 轴标签 → 不能用 order 挪，也**不能给 svg 加 padding**
  （svg 是替换元素，padding 会压缩绘图区导致曲线变形 = 图表压扁老坑），
  正解是给外层 `.chart` 容器加 `padding-right`，svg 随容器等比缩窄

这类问题**在截图里根本看不出来**（那块就是数字人画面），
必须用 `_occlude_check.py` 做 DOM 几何关系机器检测。

### ★ `.b-pad` 绝不能加 `overflow: hidden`

AI 镜的文字补底大量依赖 `box-shadow: 0 0 0 Npx` 做外扩底衬，
`hidden` 会把贴边元素的底衬整圈裁掉。
溢出问题要从源头解决 —— 收起装饰层：
`.b-pad > .is-second ~ .note-strip ~ .rule-strip { display: none; }`

### ★ 门禁脚本的输出落点不统一，读之前先 grep

`_rich_check.py` / `_comp_check.py` / `_chart_probe.py` / `_ai_batch_probe.py`
都把 `sys.stdout` 重定向到 `.log`，前台跑**终端零输出且 exit=0**，
极易误判成脚本没执行。而 `_text_probe.py` 只重设编码，可前台直接看。

固化读法：

```bash
python _x.py; echo "exit=$?"; tail -30 _x.log
```

### ★ 通用截图脚本的关键参数

`_shot_any.py`（按镜号截图，目视/统计验收专用）：

- `viewport 1920×1080` + `device_scale_factor=1` —— 必须与 `_render60.py`
  渲染尺寸一致，量出的几何才能和 `.frame-a` 那套坐标对得上
- 等待 **2600ms** —— 场景最长动画 delay+duration 约 2.2s，
  等满才拍到**终态**；等太短会拍到动画中途，误判成元素缺失

### ★ 探针指标本身可能有数学缺陷，反常数值先质疑指标

`tex_keep`（纹理保留）在线性合成 `out = a×247 + (1-a)×src` 下满足
`std(out) = (1-a)×std(src)`，即 **`keep ≡ (1 - alpha)` 恒等于 45%**,
与素材、滤镜全都无关 —— 这个指标压根测不出它声称要测的东西。
用 numpy 网格搜索反推确认后，改用「达成率 = 实测/理论上限」判据，闸值 80%。

### ★ 成片输出名不要硬编码

`_assemble65.py` 原先写死 `final_v6.mp4`，每次重新合成都**原地覆盖上一版**，
新版有问题就没有对照物可退回。改为 `python _assemble65.py v7` 传版本号，
且中间产物 `_v65_<ver>.mp4` / `_a65_<ver>.m4a` / `_concat65_<ver>.txt`
和日志 `_assemble65_<ver>.log` 一并带版本号，避免多版并行互相踩。

### ★ 重渲染用 `--force`，不要试图删文件

`_render60.py` 见输出已存在会 `SKIP 已存在`。它自带 `--force` 开关。
沙箱禁止删除文件（`rm` 拒相对路径、`os.remove` 被 `sitecustomize.py`
的 `_safe_remove` 拦截），实在要避让就用 `shutil.move` 改名。

