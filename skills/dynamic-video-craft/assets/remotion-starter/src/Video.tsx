import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import raw from './video.json';
import type {CameraState, SceneSpec, Timeline} from './types';

const data = raw as Timeline;
const clamp = (value: number) => Math.min(1, Math.max(0, value));
const mix = (a: number, b: number, t: number) => a + (b - a) * t;
const ease = (t: number) => 1 - (1 - clamp(t)) ** 3;
const palette = data.palette;

// All animation is derived from the requested frame; no wall-clock state.
const Scene: React.FC<{scene: SceneSpec}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const portrait = height > width;
  const size = Math.min(width / 1920, height / 1080);
  const typeSize = portrait ? width / 1080 : size;
  const span = Math.round(scene.end * fps) - Math.round(scene.start * fps);
  const progress = clamp(frame / Math.max(1, span - 1));
  const event = data.events.find((item) => item.id === scene.revealEvent);
  const revealFrame = Math.round((event?.at ?? scene.start) * fps) - Math.round(scene.start * fps);
  const elapsed = frame - revealFrame;
  const reveal = ease(elapsed / (fps * 0.65));
  const visible = elapsed >= 0;
  const from: CameraState = {x: 0, y: 0, scale: 1, rotate: 0, ...scene.camera?.from};
  const to: CameraState = {x: 10 * size, y: -8 * size, scale: 1.04, rotate: 0, ...scene.camera?.to};
  const cameraT = Easing.inOut(Easing.sin)(progress);
  const camera = `translate(${mix(from.x, to.x, cameraT)}px, ${mix(from.y, to.y, cameraT)}px) scale(${mix(from.scale, to.scale, cameraT)}) rotate(${mix(from.rotate, to.rotate, cameraT)}deg)`;
  const headlineSize = portrait ? 76 * typeSize : 98 * typeSize;
  const stageWidth = portrait ? width * 0.81 : width * 0.79;
  const labelSize = 28 * typeSize;
  const mainStyle: React.CSSProperties = {
    opacity: visible ? reveal : 0,
    transform: `translateY(${(1 - reveal) * 45 * typeSize}px)`,
    width: stageWidth,
    position: 'relative',
  };
  const heading = <h1 style={{fontSize: headlineSize, fontWeight: 700, lineHeight: 1.18, letterSpacing: '-0.04em', margin: 0, textWrap: 'balance'}}>{scene.headline}</h1>;
  return <AbsoluteFill style={{background: palette.background, color: palette.text, overflow: 'hidden'}}>
    <AbsoluteFill style={{background: `radial-gradient(ellipse at ${60 + progress * 12}% 30%, ${palette.surface} 0%, transparent 66%)`}} />
    <div style={{position: 'absolute', width: width * 0.82, height: width * 0.82, borderRadius: '50%', border: `1px solid ${palette.muted}`, opacity: 0.12, right: -width * 0.38 + progress * 35 * typeSize, top: height * 0.04}} />
    <AbsoluteFill style={{transform: camera, alignItems: 'center', justifyContent: 'center', paddingBottom: portrait ? height * 0.09 : 0}}>
      <div style={{width: stageWidth, position: 'absolute', top: height * 0.13, color: palette.accent, fontSize: labelSize, letterSpacing: '0.16em'}}>{scene.eyebrow ?? scene.id.toUpperCase()}</div>
      <div style={mainStyle}>
        {scene.type === 'title' && <>
          <div style={{width: 62 * typeSize, height: 7 * typeSize, marginBottom: 40 * typeSize, background: palette.accent, transformOrigin: 'left', transform: `scaleX(${reveal})`}} />
          {heading}
        </>}
        {scene.type === 'metric' && <>
          <div style={{fontSize: 42 * typeSize, marginBottom: 16 * typeSize, color: palette.muted}}>{scene.headline}</div>
          <div style={{display: 'flex', alignItems: 'baseline', gap: 25 * typeSize}}>
            <span style={{fontSize: (portrait ? 245 : 280) * typeSize, fontWeight: 750, lineHeight: 1.06, color: palette.accent, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.07em'}}>{Math.round((scene.metric ?? 0) * ease(elapsed / (fps * 1.0)))}</span>
            <span style={{fontSize: 46 * typeSize}}>{scene.unit}</span>
          </div>
        </>}
        {scene.type === 'steps' && <>
          {heading}
          <div style={{display: 'flex', flexDirection: portrait ? 'column' : 'row', gap: 22 * typeSize, marginTop: 62 * typeSize}}>
            {(scene.labels ?? []).map((label, index) => {
              const phase = ease((elapsed - index * fps * 0.23) / (fps * 0.5));
              return <div key={index} style={{flex: 1, display: 'flex', alignItems: 'center', gap: 24 * typeSize, padding: 30 * typeSize, background: palette.surface, borderRadius: 20 * typeSize, opacity: phase, transform: `translateY(${(1 - phase) * 55 * typeSize}px)`}}>
                <span style={{fontSize: 26 * typeSize, color: palette.accent}}>0{index + 1}</span>
                <span style={{fontSize: 34 * typeSize, lineHeight: 1.35}}>{label}</span>
              </div>;
            })}
          </div>
        </>}
        {scene.type === 'evidence' && <>
          {heading}
          {scene.image && <div style={{marginTop: 38 * typeSize, height: height * (portrait ? 0.28 : 0.45), background: palette.surface, borderRadius: 18 * typeSize, padding: 14 * typeSize, overflow: 'hidden'}}>
            <Img src={staticFile(scene.image)} style={{width: '100%', height: '100%', objectFit: 'contain'}} />
          </div>}
        </>}
        {scene.subline && <div style={{marginTop: 44 * typeSize, color: palette.muted, fontSize: 30 * typeSize, lineHeight: 1.6, maxWidth: portrait ? '100%' : '80%'}}>{scene.subline}</div>}
      </div>
    </AbsoluteFill>
    <div style={{position: 'absolute', bottom: height * 0.075, left: width * 0.105, right: width * 0.105, height: 2, background: palette.surface}}>
      <div style={{height: '100%', width: `${progress * 100}%`, background: palette.accent, opacity: 0.55}} />
    </div>
  </AbsoluteFill>;
};

const Wipes: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const half = Math.max(1, Math.round(0.23 * fps));
  return <>{data.scenes.slice(1).filter((scene) => scene.transition === 'wipe').map((scene) => {
    const delta = frame - Math.round(scene.start * fps);
    if (delta < -half || delta > half) return null;
    const p = clamp((delta + half) / (half * 2));
    const left = p < 0.5 ? 0 : ease((p - 0.5) * 2) * 100;
    const right = p < 0.5 ? (1 - ease(p * 2)) * 100 : 0;
    return <AbsoluteFill key={scene.id} style={{background: palette.accent, clipPath: `inset(0 ${right}% 0 ${left}%)`}} />;
  })}</>;
};

export const Video: React.FC<{music: boolean}> = ({music = true}) => {
  const frame = useCurrentFrame();
  const {fps, height, width, durationInFrames} = useVideoConfig();
  const caption = data.captions.find((item) => frame >= Math.round(item.start * fps) && frame < Math.round(item.end * fps));
  const musicEnvelope = (f: number) => interpolate(f, [0, Math.min(fps, durationInFrames / 3), Math.max(durationInFrames - fps, durationInFrames * 2 / 3), durationInFrames], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{fontFamily: '"Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif', background: palette.background}}>
    {data.scenes.map((scene) => <Sequence key={scene.id} from={Math.round(scene.start * fps)} durationInFrames={Math.round(scene.end * fps) - Math.round(scene.start * fps)} name={scene.id}>
      <Scene scene={scene} />
    </Sequence>)}
    <Wipes />
    {caption && <div style={{position: 'absolute', bottom: height > width ? height * 0.19 : height * 0.085, left: '10%', right: '10%', textAlign: 'center'}}>
      <span style={{display: 'inline-block', color: '#fff', background: 'rgba(0,0,0,0.76)', padding: '10px 22px', borderRadius: 12, fontSize: (height > width ? 44 : 42) * width / (height > width ? 1080 : 1920), lineHeight: 1.5, whiteSpace: 'pre-line'}}>{caption.text}</span>
    </div>}
    {data.audio.voiceover && <Audio src={staticFile(data.audio.voiceover.src)} volume={data.audio.voiceover.volume} />}
    {music && data.audio.music && <Audio src={staticFile(data.audio.music.src)} loop volume={(f) => data.audio.music!.volume * musicEnvelope(f)} />}
    {data.events.filter((event) => event.sfx).map((event) => <Sequence key={event.id} from={Math.round(event.at * fps)}>
      <Audio src={staticFile(event.sfx!)} volume={event.volume ?? 0.5} />
    </Sequence>)}
  </AbsoluteFill>;
};
