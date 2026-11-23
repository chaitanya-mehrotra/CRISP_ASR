import React, { useEffect, useRef, useState } from 'react';
import { parseError, previewRepair } from './api';
import { DnaButton } from './DnaButton';
import { Icon } from './Icon';

export function RepairPreview({ finding, source, stale, applyPatch }) {
  const active = useRef(null);
  const [pending, setPending] = useState(false);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => () => active.current?.abort(), []);

  async function request() {
    const controller = new AbortController();
    active.current = controller;
    setPending(true);
    setError('');
    setPreview(null);
    try {
      const patch = await previewRepair(source, finding, controller.signal);
      if (!controller.signal.aborted) {
        setPreview(patch);
      }
    } catch (problem) {
      if (!controller.signal.aborted) {
        setError(parseError(problem).message);
      }
    } finally {
      if (!controller.signal.aborted) {
        active.current = null;
        setPending(false);
      }
    }
  }

  return (
    <div className="repair-preview">
      {!preview && (
        <DnaButton className="button secondary" disabled={stale || pending} onClick={request}>
          <Icon name="helix" size={16} />{pending ? 'Checking candidate…' : 'Preview repair'}
        </DnaButton>
      )}
      {error && <p className="notice warning" role="alert">{error}</p>}
      {preview && (
        <>
          <h3>Proposed edit on line {preview.line}</h3>
          <p>{preview.explanation}</p>
          <figure className="patch-diff">
            <figcaption>Before and after</figcaption>
            <pre><code className="patch-before"><span>− </span>{preview.before}</code><code className="patch-after"><span>+ </span>{preview.after}</code></pre>
          </figure>
          <ul className="patch-checks" aria-label="Validation checks">
            {[
              ['syntax', 'Parsed as Python'],
              ['compilation', 'Compiled successfully'],
              ['rescan', 'Re-scan cleared the selected finding'],
            ].map(([id, name]) => preview.checks[id] && (
              <li key={id}><Icon name="check" size={15} />{name}</li>
            ))}
          </ul>
          <p>Findings before: {preview.before_findings}. {preview.new_findings} new findings. {preview.remaining_findings} other {preview.remaining_findings === 1 ? 'finding remains' : 'findings remain'} after the re-scan. Run your tests to check behavior.</p>
          <DnaButton className="button primary" disabled={stale} onClick={() => {
            if (!applyPatch(preview)) setError('The editor changed. Re-run analysis before applying the repair.');
          }}>
            <Icon name="check" size={16} />Apply and re-scan
          </DnaButton>
        </>
      )}
    </div>
  );
}
