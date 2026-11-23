import React, { useEffect, useRef, useState } from 'react';
import { parseError, previewAllRepairs } from './api';
import { DnaButton } from './DnaButton';
import { Icon } from './Icon';

export function BatchRepair({ analysis, stale, applyPatch }) {
  const request = useRef(null);
  const [patch, setPatch] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const count = analysis.result.findings.filter((finding) => finding.repairable).length;

  useEffect(() => () => request.current?.abort(), []);

  async function preview() {
    const controller = new AbortController();
    request.current = controller;
    setBusy(true);
    setError('');
    try {
      setPatch(await previewAllRepairs(analysis.source, controller.signal));
    } catch (problem) {
      if (!controller.signal.aborted) setError(parseError(problem).message);
    } finally {
      if (!controller.signal.aborted) setBusy(false);
    }
  }

  if (!analysis.result.findings.length) return null;
  if (!count) return <p className="notice">These findings need manual review. Open each finding for suggested changes.</p>;

  return (
    <section className="batch-repair" aria-labelledby="batch-heading">
      <h3 id="batch-heading">Repair this file</h3>
      <p>{count} findings have a repair preview. Other findings include manual guidance.</p>
      {!patch && (
        <DnaButton className="button secondary" disabled={stale || busy} onClick={preview}>
          <Icon name="helix" size={16} />{busy ? 'Checking repairs…' : 'Preview available repairs'}
        </DnaButton>
      )}
      {error && <p className="notice warning" role="alert">{error}</p>}
      {patch && (
        <>
          <p role="status">{patch.before_findings} findings before, {patch.remaining_findings} after. Syntax, compilation, and re-scan passed.</p>
          <p>{patch.manual_findings} need manual review. {patch.deferred_count > 0 && `${patch.deferred_count} overlapping fixes can be reviewed separately after applying this batch.`}</p>
          <div className="batch-changes">
            {patch.changes.map(({ line, before, after, notes }) => (
              <details key={line} className="patch-diff">
                <summary>Review line {line}</summary>
                {notes.map((note, index) => <p key={index}>{note}</p>)}
                <pre><code className="patch-before">− {before}</code><code className="patch-after">+ {after}</code></pre>
              </details>
            ))}
          </div>
          <DnaButton className="button primary" disabled={stale} onClick={() => {
            if (!applyPatch(patch)) setError('The editor changed. Re-run analysis before applying repairs.');
          }}>
            Apply {patch.repair_count} {patch.repair_count === 1 ? 'repair' : 'repairs'} and re-scan
          </DnaButton>
        </>
      )}
    </section>
  );
}
