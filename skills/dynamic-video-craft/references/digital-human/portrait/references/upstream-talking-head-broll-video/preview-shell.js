/* ============================================================
   _shell.js · 动态预览外壳（缩放 + 循环播放 + 辅助线）
   动效本体写在各 preview 页里，本文件只负责"重放/循环"这套壳。
   ============================================================ */
(function () {
  const FPS = 30;
  window.f2ms = f => Math.round(f * 1000 / FPS);   /* 帧 → 毫秒 */

  function fit() {
    const vp = document.querySelector('.viewport');
    const sc = document.querySelector('.scaler');
    if (!vp || !sc) return;
    const k = Math.min(vp.clientWidth / 1920, vp.clientHeight / 1080) * 0.94;
    sc.style.setProperty('--k', k.toFixed(4));
  }
  window.addEventListener('resize', fit);

  /* 供各页调用：注册一条时间线
     opts = { total: 总时长毫秒, onRun: 每轮开始时执行 }            */
  window.initPreview = function (opts) {
    const stage = document.querySelector('.stage');
    const total = opts.total || 4000;
    let timer = null, looping = true;

    function run() {
      stage.classList.remove('run');
      void stage.offsetWidth;              /* 强制重排，重置 CSS 动画 */
      if (opts.onReset) opts.onReset(stage);
      stage.classList.add('run');
      if (opts.onRun) opts.onRun(stage);
    }
    function schedule() {
      clearTimeout(timer);
      if (!looping) return;
      timer = setTimeout(() => { run(); schedule(); }, total + 900);
    }

    document.getElementById('btn-replay')
      .addEventListener('click', () => { run(); schedule(); });

    const loopBox = document.getElementById('chk-loop');
    loopBox.addEventListener('change', e => {
      looping = e.target.checked;
      if (looping) schedule(); else clearTimeout(timer);
    });

    document.getElementById('chk-guide')
      .addEventListener('change', e =>
        stage.classList.toggle('show-guide', e.target.checked));

    fit();
    run();
    schedule();
  };

  /* 打字机：每字 stepFrames 帧 */
  window.typewriter = function (el, text, stepFrames, delayMs) {
    el.textContent = '';
    const step = f2ms(stepFrames);
    let i = 0;
    setTimeout(function tick() {
      if (i > text.length) return;
      el.textContent = text.slice(0, i);
      i++;
      if (i <= text.length) setTimeout(tick, step);
    }, delayMs || 0);
  };

  /* 数字滚动：spring 观感（过冲一次后停稳，不来回弹） */
  window.rollNumber = function (el, from, to, frames, delayMs, fmt) {
    const dur = f2ms(frames);
    const t0 = performance.now() + (delayMs || 0);
    function ease(p) {                     /* 近似 spring damping:120 */
      return 1 - Math.pow(1 - p, 3);
    }
    function frame(now) {
      const p = Math.max(0, Math.min(1, (now - t0) / dur));
      const v = from + (to - from) * ease(p);
      el.textContent = fmt ? fmt(v) : Math.round(v);
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  };
})();
