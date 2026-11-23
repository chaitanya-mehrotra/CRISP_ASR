import React, { useEffect, useState } from 'react';
import { fetchRules } from './api';
import { FixExample, Severity } from './FindingCards';
import { Icon } from './Icon';

const clock = new Intl.DateTimeFormat(undefined, { dateStyle: 'short', timeStyle: 'short' });

export function History({ entries }) {
  return (
    <>
      <div className="page-heading"><div><h1>Session history</h1><p>Review analyses run since this page was opened.</p></div></div>
      <section className="panel history-panel" aria-label="Analysis attempts">
        {entries.length ? (
          <table>
            <thead><tr><th>Source file</th><th>Result</th><th>Findings</th><th>AST nodes</th><th>Analyzed</th></tr></thead>
            <tbody>
              {entries.map(({ id, file, time, count, findings, status }) => (
                <tr key={id}><td>{file}</td><td>{status}</td><td>{findings ?? '—'}</td><td>{count ?? '—'}</td><td>{clock.format(time)}</td></tr>
              ))}
            </tbody>
          </table>
        ) : <p className="notice">Your analysis attempts will appear here.</p>}
      </section>
    </>
  );
}

export function RuleScope() {
  const [rules, setRules] = useState(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetchRules(controller.signal).then(setRules).catch(() => {
      if (!controller.signal.aborted) setFailed(true);
    });
    return () => controller.abort();
  }, []);

  return (
    <>
      <div className="page-heading"><div><h1>Rule scope</h1><p>See what each AST check looks for and how to address a finding.</p></div></div>
      {!rules && <p className="notice" role="status">{failed ? 'The rule catalog could not be loaded. Check that the API is running.' : 'Loading checks…'}</p>}
      <div className="rules-grid">
        {rules?.map((rule) => (
          <article className="panel rule-card" key={rule.id}>
            <div><span className="tag">{rule.id}</span><Severity value={rule.severity} /></div>
            <h2><Icon name="shield" />{rule.title}</h2><p>{rule.risk}</p>
            <details className="rule-guidance">
              <summary>How to fix it</summary>
              <p>{rule.fix}</p>
              <FixExample example={rule.example} />
            </details>
          </article>
        ))}
      </div>
    </>
  );
}
