# 工程与时间轴

## 工具与依赖

`assets/remotion-starter/` 是原创最小工程。初始化脚本按所选画幅复制它，拒绝覆盖非空目录，不执行安装或联网。Node/npm、FFmpeg 不随技能分发。

工程使用固定版本的 Remotion、React 与 TypeScript；`npm install` 安装依赖，之后保留 lockfile 并用 `npm ci` 重建。所有 `@remotion/*` 与 `remotion` 保持同版本；新增 Three.js、字体或额外动画库只在镜头需要时安装。

首次 Remotion 渲染可能需要下载 Chrome Headless Shell。离线或下载失败时检查现有可用浏览器，按当前 Remotion CLI 支持的 `--browser-executable` 参数提供路径，不声称渲染已完成。

## 文件分工

| 文件 | 用途 |
|---|---|
| `src/video.json` | 画幅、帧率、镜头、事件、字幕、声轨的唯一配置 |
| `src/Video.tsx` | 场景、连续相机、转场、音画层组合 |
| `src/types.ts` | 配置类型 |
| `src/Root.tsx` | Composition 注册与整片长度 |
| `public/` | 最终渲染使用的本地素材 |
| `SHOTBOOK.md` | 初始化时生成的镜头工作表，后续随真实内容改写 |
| `out/` | 视频、关键帧与验收结果 |

编辑 `video.json` 后重跑检查。复杂成片可以拆成独立场景组件，但保留统一时间源。

## 数据契约

全部输入时间为绝对秒。渲染边界统一 `Math.round(seconds * fps)`；Python 检查用等效的非负数四舍五入，避免 Python `round()` 的银行家舍入差异。

- `duration`：整片秒数；`fps/width/height`：输出配置。
- `scenes`：相邻半开区间 `[start,end)`，连续覆盖整片。包括 `id/type/headline`，可选 `subline/eyebrow/labels/metric/unit/image/revealEvent/camera`。
- `type`：`title`、`metric`、`steps`、`evidence`。evidence 需真实 `image` 路径；这些场景是起点，不能覆盖全部镜头库。
- `camera`：可选 `from/to`，每端含 `x/y/scale/rotate`；单位为该工程输出像素、倍数与度。路径是场景局部的平滑变化，字幕不在相机层。
- `transition`：写在后一镜，`wipe` 或 `cut`。wipe 在边界前后各约 0.23 秒，用覆盖全幅的色块隐藏切点；若有其他语法自行扩展。
- `events`：`{id,sceneId,at,label,anchorId?,sfx?,volume?}`。`revealEvent` 对应信息组开始揭示的事件；有 `anchorId` 的 `at` 与锚点起时一致。
- `anchors`：`{id,text,start,end,source}`，由真实对齐结果归一化而来。没有配音的演示可为空。
- `captions`：`{text,start,end}`，模板同一时刻显示一句；支持导出 SRT。
- `audio`：可选 `voiceover/music`，各为 `{src,volume}`。音量为线性倍数，不是 dB。
- `palette`：全片共用的 `background/surface/text/muted/accent`。

`image/audio.src/events.sfx` 均是相对 `public/` 的路径，不能填远程 URL、绝对路径或 `..`。字体用已安装字体或项目内本地字体，避免逐帧联网取字。

模板允许静音示例。实际解说成片运行 `check_timeline.py ... --require-voiceover`；这会要求旁白和有词锚的视觉事件，避免把预演误交付为配音成片。

当前原创骨架的类型、画面组件和检查器没有实现数字人 `host` 字段，也没有 `--require-host` 选项；未知字段不会证明被渲染或验证。需要人物时须先实现并测试人物媒体层及其时间范围、路径和缺失处理，或选用具备该能力的工程；然后播放实际输出核验要求出镜的各段。其他旧工程的命令和素材字段必须以其自身版本为准，不能直接套用在本骨架上。

## 确定性

帧、配置和固定种子决定画面。React 渲染中不用实时计时器、CSS 自动播放、`Math.random()` 或依赖上一帧累加的状态。新库的动画必须能按任意帧 seek；提前隐藏尚未到时的内容。字幕、音效使用绝对帧或统一换算的局部帧，不能混用。

分段运镜的连接处同时检查位置和速度，先写清每段缓动是位置函数还是速度函数，再计算导数与行程；不要把匀加速的距离公式套在任意缓动上。例如位置缓动 `f(u)=1−cos(πu/2)`、时长 `T`、末速 `v` 时，行程是 `2vT/π`，不是 `vT/2`。实现中还要检查所用引擎实际缓动定义、变换顺序和帧离散结果，并通过连续播放验证。

浏览器逐帧渲染时，先按时间轴核对预期页面和实际渲染队列，不因缺失页面被过滤而把零镜或部分镜头视为成功。等待字体、图片及视频实际就绪；每帧视频定位须检查成功与目标时间，超时、解码失败或动画定位异常应记录失败并重试或停止，不能只等固定时间。旁白对应的口型素材不足时不能自动循环掩盖缺口；其他素材是否循环由镜头设计决定。复用已渲染片段前核对时间轴、素材、参数、版本和可解码性，不能只靠文件存在或大小。输出帧率变高不代表实际采样帧率或动作细节随之增加。

## 常用命令

```text
python "<SKILL_DIR>/scripts/check_timeline.py" src/video.json --srt out/captions.srt
npm run typecheck
npm run still -- out/scene.png --frame=65
npm run render
npx remotion render src/index.ts DynamicVideo out/video-no-music.mp4 --props=no-music.json --codec=h264
```

`no-music.json` 内容为 `{"music":false}`，旁白与音效仍保留。成品片名默认 `out/video.mp4`；另存版本可直接 `npx remotion render src/index.ts DynamicVideo out/video-v2.mp4`。

先用 `--scale=0.5 --frames=0-89` 验证一个短段，最终再输出完整分辨率。不要在渲染时生成配音、搜索素材或改变时间轴。长片需要分段时让视频段精确按帧拼接，整条音轨单独混入，避免多段 AAC 编码前导引起偏移。

分段合成前列明预期镜头、顺序、音轨及版本，逐段检查存在、可解码、编码参数和实际时长；比较每段及累计偏差，超出项目容差就定位处理，不能只打印警告后继续当作通过。合成后的文件重新检查视频、音频、字幕及首尾内容；采用 `-shortest` 时尤其核对是否截掉语音尾部或画面，不以一次合流命令成功替代成片验收。旧脚本可能在报错后正常退出或覆盖既有版本，须检查日志、退出码和输出文件，修复时保留旧产物及对应记录。
