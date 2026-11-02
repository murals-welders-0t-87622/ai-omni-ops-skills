# STORYBOARD.md

## 文件信息

- Skill：`douyin-dh-landscape-remotion-video`
- 版本：`v1`
- 时长：`70s`
- 画幅：`1920x1080`

## 一、统一版式规则

1. 每段先判断 A/B 主次
2. 数字人只能以三种模式出现：
   - 贴边主持
   - 缩位让台
   - 暂时隐藏
3. B-roll 必须是高动态镜头，不得做静态 PPT 页面

## 二、镜头结构

### Scene 1 · Hook 开场（0s-8s）

- 主导：A-roll 主导
- 数字人：贴边主持
- B-roll：标题卡 + 轻视差背景 + `camera.tsx` 慢推 + 金句停留
- 目的：快速抛出结论和问题

### Scene 2 · 证据抛出（8s-20s）

- 主导：B-roll 主导
- 数字人：缩位让台
- B-roll：`host-shrink-to-chip` + `focus-dim-spotlight` + 截图标注 + 手绘箭头
- 目的：把第一组证据讲清

### Scene 3 · 界面巡游（20s-34s）

- 主导：B-roll 主导
- 数字人：暂时隐藏
- B-roll：`evidence-scroll-tour` + 缓推特写 + 画中画放大
- 目的：让观众专注界面和功能证据

### Scene 4 · 结论拆解（34s-50s）

- 主导：双主导
- 数字人：右下角缩位
- B-roll：三卡片堆入 + 图表生长 + 数字弹出 + `life.tsx` idle/retire
- 目的：讲清 3 个核心结论

### Scene 5 · 行动建议（50s-64s）

- 主导：A-roll 主导
- 数字人：贴边主持
- B-roll：左右摇移 + 重点词强调
- 目的：回到主持人总结建议

### Scene 6 · CTA 结尾（64s-70s）

- 主导：A-roll 主导
- 数字人：贴边主持
- B-roll：关注 CTA / 结尾标识 + `push-through` 或 `overexpose-flip` 收束
- 目的：收尾与行动召唤

## 三、门禁说明

1. `demo.html` 必须至少模拟 Scene 1、2、4 的关系
2. 没有用户确认，不进入正式制作
3. 正式制作时，A-roll 和 B-roll 的时间关系必须与这里保持一致
