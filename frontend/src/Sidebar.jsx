import React from 'react';
import { DnaButton } from './DnaButton';
import { examples } from './examples';
import { Icon } from './Icon';

const pages = [
  { id: 'workspace', title: 'Workspace', icon: 'workspace' },
  { id: 'history', title: 'Session history', icon: 'history' },
  { id: 'rules', title: 'Rule scope', icon: 'shield' },
  { id: 'guide', title: 'Student guide', icon: 'tree' },
];

const demos = [
  ['session_tokens.py', 'Weak randomness'],
  ['yaml_config.py', 'YAML loader'],
  ['fixed_command.py', 'Shell command'],
].map(([name, label]) => ({ example: examples.find((item) => item.name === name), label }));

export function Sidebar({ page, setPage, file, analysis, stale, busy, runDemo, showFindings }) {
  const findings = analysis?.result?.findings.length ?? 0;
  let status = 'Run an analysis';
  if (busy) status = 'Analysis in progress';
  else if (stale) status = 'Source changed since the last scan';
  else if (analysis?.problem) status = analysis.problem.line ? 'Syntax error found' : 'Analysis unavailable';
  else if (analysis?.result) status = `${findings} potential ${findings === 1 ? 'issue' : 'issues'}`;

  return (
    <aside className="sidebar">
      <div className="sidebar-content">
        <nav aria-label="Project">
          {pages.map(({ id, title, icon }) => (
            <DnaButton key={id} aria-current={page === id ? 'page' : undefined} onClick={() => setPage(id)}>
              <Icon name={icon} size={18} />{title}
            </DnaButton>
          ))}
        </nav>
        <section className="sidebar-section" aria-labelledby="demos-heading">
          <h2 id="demos-heading">Quick demos</h2>
          <ul className="sidebar-demos">
            {demos.map(({ example, label }) => (
              <li key={example.name}>
                <DnaButton disabled={busy} onClick={() => runDemo(example)} aria-label={`Run ${label} demo`}>
                  <Icon name="play" size={14} />{label}
                </DnaButton>
              </li>
            ))}
          </ul>
        </section>
        <section className="sidebar-section" aria-labelledby="scan-heading">
          <h2 id="scan-heading">Current scan</h2>
          <div className="sidebar-scan">
            <strong title={file}>{file}</strong>
            <span role="status">{status}</span>
            <DnaButton className="line-link" disabled={busy || !analysis} onClick={showFindings}>View results</DnaButton>
          </div>
        </section>
      </div>
      <div className="sidebar-footer"><Icon name="shield" size={17} /><span>Source is parsed without execution.</span></div>
    </aside>
  );
}
