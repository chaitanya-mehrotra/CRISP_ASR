import React, { useRef } from 'react';

export function DnaButton({ children, className = '', onClick, ...props }) {
  const effect = useRef(null);

  function activate(event) {
    const button = event.currentTarget;
    const wave = effect.current;
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && wave?.animate) {
      const { left, top, width, height } = button.getBoundingClientRect();
      wave.style.left = `${event.detail ? event.clientX - left : width / 2}px`;
      wave.style.top = `${event.detail ? event.clientY - top : height / 2}px`;
      wave.getAnimations().forEach((animation) => animation.cancel());
      wave.animate([
        { transform: 'translate(-50%, -50%) scale(.25) rotate(-38deg)', opacity: .94 },
        { transform: 'translate(-50%, -50%) scale(1.2) rotate(8deg)', opacity: .78, offset: .42 },
        { transform: 'translate(-50%, -50%) scale(2.55) rotate(43deg)', opacity: 0 },
      ], { duration: 520, easing: 'cubic-bezier(.15,.65,.32,1)' });
    }
    onClick?.(event);
  }

  return (
    <button type="button" className={`dna-button ${className}`} onClick={activate} {...props}>
      <span className="dna-press" ref={effect} aria-hidden="true">
        <i /><i /><i />
      </span>
      {children}
    </button>
  );
}
