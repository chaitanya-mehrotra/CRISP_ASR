import React, { useState } from 'react';
import { DnaButton } from './DnaButton';
import { Icon } from './Icon';
import { FindingLesson } from './FindingLesson';
import { RepairPreview } from './RepairPreview';

export function Severity({ value }) {
  return <span className={`severity severity-${value}`}>{value}</span>;
}

export function FixExample({ example }) {
  const [status, setStatus] = useState('');
  async function copy() {
    try {
      await navigator.clipboard.writeText(example);
      setStatus('Copied');
    } catch {
      setStatus('Select the code to copy it');
    }
  }

  return (
    <div className="fix-example">
      <div><span>Safer pattern</span><DnaButton className="copy-button" onClick={copy}>Copy code</DnaButton></div>
      <pre><code>{example}</code></pre>
      {status && <p className="copy-status" role="status">{status}</p>}
    </div>
  );
}

function FindingCard({ finding, stale, jumpToLine, source, applyPatch }) {
  return (
    <details className="finding-card">
      <summary>
        <span className="finding-label"><strong>{finding.title}</strong><small>{finding.id} · Line {finding.line}, column {finding.column}</small></span>
        <Severity value={finding.severity} />
        <Icon name="chevron" size={15} />
      </summary>
      <div className="finding-detail">
        <div className="finding-call">
          <code>{finding.call}</code>
          <DnaButton className="line-link" disabled={stale} onClick={() => jumpToLine(finding)}>
            Highlight source
          </DnaButton>
        </div>
        <h3>Why it matters</h3>
        <p>{finding.risk}</p>
        <FindingLesson finding={finding} />
        <h3>How to fix it</h3>
        <p>{finding.fix}</p>
        {finding.repairable
          ? <>
            {finding.repair_mode === 'guided' && <p className="manual-review">Guided preview · review behavior before applying</p>}
            <RepairPreview {...{ finding, source, stale, applyPatch }} />
          </>
          : <p className="manual-review">Manual review</p>}
        <FixExample example={finding.example} />
      </div>
    </details>
  );
}

export function FindingCards({ findings, stale, jumpToLine, source, applyPatch }) {
  const [filter, setFilter] = useState('all');
  const visible = findings.filter((finding) => filter === 'all' || finding.severity === filter);

  if (!findings.length) return (
    <div className="findings-empty">
      <Icon name="check" />
      <div><strong>No patterns flagged</strong><p>The scanner found no matching patterns in this source. Other weaknesses may still be present.</p></div>
    </div>
  );

  return (
    <div className="findings">
      <div className="filter-bar">
        <span>{visible.length} of {findings.length} shown</span>
        <label className="example-select">
          <select aria-label="Filter by severity" value={filter} onChange={(event) => setFilter(event.target.value)}>
            <option value="all">All severities</option>
            <option value="high">High severity</option>
            <option value="medium">Medium severity</option>
          </select>
          <Icon name="chevron" size={15} />
        </label>
      </div>
      {visible.map((finding) => (
        <FindingCard key={`${finding.id}-${finding.line}-${finding.column}`} {...{ finding, stale, jumpToLine, source, applyPatch }} />
      ))}
      {!visible.length && <p className="notice">No findings at this severity.</p>}
    </div>
  );
}
