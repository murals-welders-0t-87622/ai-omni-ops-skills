# 数字人 + 卡片 · 横屏合成规范

> 适用场景：RunningHub LTX2.3 生成的**竖屏**数字人片段，接入 **1920×1080 横屏** Remotion 工程。
> 来源：2026-08-31「十万块 AI 知识库 / 800 块 NAS」41 镜项目实测。

---

## 1. 数字人素材实况（LTX2.3 默认输出）

| 项 | 值 | 备注 |
|---|---|---|
| 分辨率 | 704×1280 | 竖屏 9:16，比例 0.55 |
| 帧率 | 25 fps | **与 Composition 30fps 不同，必须换算** |
| 编码 | h264 + aac | **自带音轨** |
| 时长 | ≈ 源音频时长 ±0.2s | 与 TTS 片段基本等长 |

> ⚠️ 输入图建议 720×1280（原图过大不会报错，但会拖慢排队；3040×5404 实测可用但慢）。

---

## 2. 三种 hostMode 的区域与裁切

布局常量见 `template/theme.ts` 的 `host` 与 `SAFE`。

| hostMode | 宿主区 | 主信息区（卡片） | 裁切要点 |
|---|---|---|---|
| `EDGE` | x1330 y130 · 494×880（右侧竖条） | `SAFE.mainEdge` 1214×796 | 比例 0.561 vs 源 0.55，微裁 18px |
| `CHIP` | x1478 y614 · 346×346（右下小窗，圆角 28） | `SAFE.mainChip` 1344×752 | 正方形裁竖屏，只取人脸 |
| `HIDDEN` | 不渲染 | `SAFE.mainHidden` 1728×752 | — |

**统一裁切写法**：

```tsx
<OffthreadVideo
  src={staticFile(`assets/dh_PART${part}.mp4`)}
  startFrom={hostStartFrom}
  volume={0}                                  // ← 必须静音
  style={{
    width: '100%', height: '100%',
    objectFit: 'cover',
    objectPosition: isChip ? 'center 28%' : 'center 22%',  // 取上半部人脸
  }}
/>
```

- `objectPosition` 偏上（22%~28%）是命门：竖屏人物整体偏上，取中心会裁到胸口。
- `volume={0}` **不可省略** —— 数字人源带 aac 音轨，不静音会与全片音轨叠加成回声。
- 源片整体偏暗（YAVG≈24，人物中心区也只有 65），建议加
  `filter: 'brightness(1.10) contrast(1.06) saturate(0.96)'` 提亮，否则会糊进深墨蓝背景。
  注意：**偏暗是素材特性，不是渲染故障**——验证渲染是否正常应比对
  「容器内人物中心区亮度 vs 源片同区亮度」，而不是看绝对值高低。

---

## 2.5 容器质感（暗色数字人必须做）

只给个 `boxShadow` 是不够的。数字人偏暗 + 背景偏暗，不做边框处理会连成一片。
采用**内外分层**（外层不裁切负责扩散，内层裁切负责边框）：

```tsx
<div style={{ position:'absolute', left:zone.x, top:zone.y, width:zone.w, height:zone.h }}>
  {/* 外层：扩散投影 + 琥珀金环境光（不裁切，否则阴影被 overflow 掉） */}
  <div style={{ position:'absolute', inset:0, borderRadius:r, boxShadow: outer }} />

  {/* 内层：描边 + 内高光（裁切视频） */}
  <div style={{ position:'absolute', inset:0, borderRadius:r, overflow:'hidden',
                boxShadow: inner, backgroundColor:'rgba(255,255,255,.02)' }}>
    <OffthreadVideo ... />
    {/* 顶部高光：模拟顶光落在玻璃边缘 */}
    <div style={{ position:'absolute', left:0, right:0, top:0, height:'12%',
                  background:'linear-gradient(to bottom, rgba(255,255,255,.07), transparent)' }} />
    {/* 底部渐隐：让竖条下沿融进背景，不出现硬切 */}
    <div style={{ position:'absolute', left:0, right:0, bottom:0, height:'17%',
                  background:'linear-gradient(to top, rgba(10,14,26,.95), rgba(10,14,26,.55) 45%, transparent)' }} />
  </div>
</div>
```

阴影分层（CHIP 小窗用稍弱一组）：

```ts
// 外层：接触阴影 → 中层 → 远景扩散 → 琥珀金环境光
outer = '0 3px 6px rgba(0,0,0,.45), 0 14px 32px rgba(0,0,0,.50), '
      + '0 40px 96px rgba(0,0,0,.60), 0 0 72px rgba(245,166,35,.07)';

// 内层：1px 外描边 → 顶部内高光 → 金色内描边 → 底部内阴影
inner = '0 0 0 1px rgba(255,255,255,.12), '
      + 'inset 0 1px 0 rgba(255,255,255,.16), '
      + 'inset 0 0 0 1px rgba(245,166,35,.10), '
      + 'inset 0 -1px 0 rgba(0,0,0,.35)';
```

> **为什么要分层**：`overflow:hidden` 会裁掉容器外的扩散阴影，
> 所以扩散投影必须放在不裁切的外层，描边和内高光放裁切的内层。

---

## 3. 帧率换算（最容易错的一步）

`Sequence` 的 `from` / `durationInFrames` 是 **Composition 帧（30fps）**，
`OffthreadVideo` 的 `startFrom` 是 **源视频帧（25fps）**。两者单位不同。

```ts
const COMP_FPS = 30;
const HOST_FPS = 25;

// 段首（Composition 秒）
const PART_FIRST_SEC = /* 每段首镜的 REAL_SPAN.startSec */;

// 镜头在 Composition 上的帧区间
const shotFrom   = Math.round(span.startSec * COMP_FPS);
const shotFrames = Math.round(span.endSec   * COMP_FPS) - shotFrom;

// 数字人在源视频内的相对起点 ← 用源 fps 换算
const hostStartFrom = Math.round((span.startSec - PART_FIRST_SEC[shot.part]) * HOST_FPS);
```

**每镜一个 `<Sequence from durationInFrames>` 包裹 `startFrom={hostStartFrom}`**
—— `startFrom` 是常量，只 seek 一次，性能正常。
❌ 不要把 `startFrom` 做成随 `useCurrentFrame()` 变化的值，会导致每帧 seek，渲染慢数十倍。

---

## 4. 卡片层接入

卡片原生 **960×540**（16:9），`export default function Xxx({ hostSrc })`，
并导出 `meta = { width, height, fps, durationInFrames }`。

### 4.1 注册表自动生成

```bash
python scripts/gen_card_index.py     # 扫描 src/cards/*.tsx → src/cards/index.ts
```

产出 `CARDS: Record<string, { Comp, dur }>`，`dur` 取自 `meta.durationInFrames`。

### 4.2 缩放

```tsx
const scale = Math.min(zone.w / 960, zone.h / 540);   // contain
<div style={{ width: 960, height: 540, transform: `scale(${scale})`,
              transformOrigin: 'top left', /* 居中于 zone */ }} />
```

### 4.3 多卡片均分与定格

一镜常配 1~3 张卡片，按时长均分。卡片自身节奏（60~321 帧）与分配时长不等时：

```tsx
<Sequence from={from} durationInFrames={dur}>
  <Sequence durationInFrames={Math.min(dur, metaDur)}>
    <CardCanvas><Comp /></CardCanvas>
  </Sequence>
  {dur > metaDur && (
    <Sequence from={metaDur} durationInFrames={dur - metaDur}>
      <Freeze frame={metaDur - 1}><CardCanvas><Comp /></CardCanvas></Freeze>
    </Sequence>
  )}
</Sequence>
```

> 不加 `Freeze` 的后果：卡片播完后镜头剩余时间变成空白，观感断裂。

---

## 5. 图层顺序（自下而上）

```
L1 背景        深墨蓝 + 网格 + vignette + 冷光晕
L2 卡片动效层   contain 到主信息区
L3 数字人层     EDGE / CHIP / HIDDEN
L4 字幕层       底部素排，单行 ≤12 字，无动效
L5 全片音轨     <Audio src={staticFile('audio/_full.mp3')} />
```

---

## 6. 全片音轨拼接

段间留白 0.5s（与 `shotsReal.ts` 的段间 gap 一致）：

```bash
ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 0.5 -c:a libmp3lame -q:a 4 audio/_gap.mp3
# _concat.txt: PART01.mp3 / _gap.mp3 / PART02.mp3 / … / PART07.mp3
ffmpeg -f concat -safe 0 -i audio/_concat.txt -c copy audio/_full.mp3
```

拼接后的总时长通常比镜位总时长长 0.3~0.5s（mp3 每帧 padding 累积）。
以 **Composition durationInFrames 为准**截断即可，尾部是静音，不影响观感。

---

## 7. 自检清单

- [ ] 数字人 `volume={0}`（否则回声）
- [ ] `startFrom` 用源 fps（25）换算，`Sequence` 用 Composition fps（30）
- [ ] `objectPosition` 偏上取人脸
- [ ] 卡片超出 `metaDur` 的部分用 `Freeze` 定格
- [ ] 字幕时间轴与 `shotsReal.ts` 同源（见 `scripts/vad_align.py`）
- [ ] 全片零 CTA（红线 #47）
