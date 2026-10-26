// Pure helpers for time-driven custom scenes; independent of the chosen video engine.
const finite = (v, name) => { if (!Number.isFinite(v)) throw new TypeError(`${name} must be finite`); return v; };
const frameInt = (v, name) => { finite(v, name); if (!Number.isInteger(v)) throw new TypeError(`${name} must be an integer`); return v; };
const positive = (v, name) => { finite(v, name); if (v <= 0) throw new RangeError(`${name} must be positive`); return v; };

export function sceneClock(absoluteFrame, fps, fromFrame = 0) {
  frameInt(absoluteFrame, 'absoluteFrame'); frameInt(fromFrame, 'fromFrame'); positive(fps, 'fps');
  return {absoluteFrame, localFrame: absoluteFrame - fromFrame, absoluteSeconds: absoluteFrame / fps, localSeconds: (absoluteFrame - fromFrame) / fps};
}
export function frameAtSeconds(seconds, fps) {
  finite(seconds, 'seconds'); positive(fps, 'fps'); return Math.round(seconds * fps);
}
export function progressAt(frame, startFrame, durationFrames) {
  frameInt(frame, 'frame'); frameInt(startFrame, 'startFrame'); positive(durationFrames, 'durationFrames');
  return Math.max(0, Math.min(1, (frame - startFrame) / durationFrames));
}
export function motionTime(frame, fps, animationFps) {
  const t = sceneClock(frame, fps).absoluteSeconds;
  positive(animationFps, 'animationFps'); return Math.floor(t * animationFps) / animationFps;
}
export function randomFor(seed, objectId) {
  // Stateless FNV-1a hash. Stable layout, not cryptography or a random source for security.
  const text = JSON.stringify([String(seed), String(objectId)]); let h = 2166136261;
  for (let i = 0; i < text.length; i++) h = Math.imul(h ^ text.charCodeAt(i), 16777619) >>> 0;
  return h / 4294967296;
}
export function project2D(point, camera, viewport) {
  for (const [k,v] of Object.entries({x:point.x,y:point.y,cx:camera.x,cy:camera.y,angle:camera.angle ?? 0,width:viewport.width,height:viewport.height})) finite(v,k);
  positive(camera.scale,'scale');positive(viewport.width,'width');positive(viewport.height,'height');
  const a = camera.angle ?? 0, x = point.x - camera.x, y = point.y - camera.y;
  return {x: viewport.width / 2 + camera.scale * (x * Math.cos(a) - y * Math.sin(a)), y: viewport.height / 2 + camera.scale * (x * Math.sin(a) + y * Math.cos(a))};
}
