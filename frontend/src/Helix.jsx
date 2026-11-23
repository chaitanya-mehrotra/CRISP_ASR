import React, { useEffect, useRef } from 'react';

const stepCount = 160;
const pairs = 24;
const palette = ['#87f4c9', '#bea3ff'];

function drawHelix(canvas, phase, scan = null) {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  if (!width || !height) return;

  const density = Math.min(window.devicePixelRatio || 1, 2);
  const pixelWidth = Math.round(width * density);
  const pixelHeight = Math.round(height * density);
  if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
    canvas.width = pixelWidth;
    canvas.height = pixelHeight;
  }

  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  ctx.setTransform(density, 0, 0, density, 0, 0);
  ctx.clearRect(0, 0, width, height);
  const radius = Math.min(height * .33, width * .22);

  function point(t, offset) {
    const angle = t * Math.PI * 5.6 + phase + offset;
    const depth = (Math.cos(angle) + 1) / 2;
    return {
      x: width * (.11 + t * .77) + Math.cos(angle) * radius * .11,
      y: height * (.62 - t * .24) + Math.sin(angle) * radius,
      depth,
    };
  }

  function line(from, to, color, opacity, thickness) {
    ctx.globalAlpha = opacity;
    ctx.strokeStyle = color;
    ctx.lineWidth = thickness;
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
  }

  ctx.lineCap = 'round';
  const segments = [];
  for (const [strand, color] of palette.entries()) {
    for (let step = 0; step < stepCount; step += 1) {
      const from = point(step / stepCount, strand * Math.PI);
      const to = point((step + 1) / stepCount, strand * Math.PI);
      segments.push({ from, to, color, near: (from.depth + to.depth) / 2 });
    }
  }

  const rungs = Array.from({ length: pairs }, (_, index) => {
    const t = (index + .5) / pairs;
    return { t, points: [point(t, 0), point(t, Math.PI)] };
  });

  function rail({ from, to, color, near }) {
    line(from, to, color, .12, 5 + near * 3);
    line(from, to, color, .5 + near * .48, 1.35 + near * 1.6);
  }

  segments.filter(({ near }) => near < .5).forEach(rail);
  for (const { t, points: [left, right] } of rungs) {
    const hot = scan === null ? 0 : Math.max(0, 1 - Math.abs(t - scan) / .12);
    const center = { x: (left.x + right.x) / 2, y: (left.y + right.y) / 2 };
    line(left, center, palette[0], .42 + .55 * hot, 1.25 + 2.2 * hot);
    line(center, right, palette[1], .42 + .55 * hot, 1.25 + 2.2 * hot);
  }
  segments.filter(({ near }) => near >= .5).forEach(rail);

  for (const { t, points } of rungs) {
    const hot = scan === null ? 0 : Math.max(0, 1 - Math.abs(t - scan) / .12);
    points.forEach(({ x, y, depth }, strand) => {
      const dot = 1.2 + depth * 1.55 + hot * 1.8;
      ctx.fillStyle = palette[strand];
      ctx.globalAlpha = .09 + hot * .14;
      ctx.beginPath();
      ctx.arc(x, y, dot * 2.9, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = .6 + depth * .39;
      ctx.beginPath();
      ctx.arc(x, y, dot, 0, Math.PI * 2);
      ctx.fill();
    });
  }
  ctx.globalAlpha = 1;
}

export function Helix({ pulse }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let frame = 0;
    let phase = .5;
    let scan = null;
    const paint = () => drawHelix(canvas, phase, scan);
    const observer = new ResizeObserver(paint);
    observer.observe(canvas);
    paint();

    if (pulse && !reducedMotion.matches) {
      const start = performance.now();
      const tick = (time) => {
        const progress = Math.max(0, Math.min(1, (time - start) / 760));
        // Complete one turn so the helix returns to its resting position.
        phase = .5 + 2 * Math.PI * progress;
        scan = progress < 1 ? progress : null;
        paint();
        if (progress < 1) frame = requestAnimationFrame(tick);
      };
      frame = requestAnimationFrame(tick);
    }

    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
    };
  }, [pulse]);

  return (
    <div className="helix-field" aria-hidden="true">
      <canvas ref={canvasRef} className="helix" />
    </div>
  );
}
