import React, { useState } from 'react';
import { DnaButton } from './DnaButton';
import { examples } from './examples';
import { Icon } from './Icon';

const sections = [
  ['Workspace', 'workspace', 'workspace', 'Upload or paste Python, run a scan, inspect findings, and preview supported fixes.'],
  ['Session history', 'history', 'history', 'Review which files you analyzed since you opened this page, when, and how many issues each scan found. Reloading clears the list.'],
  ['Rule scope', 'rules', 'shield', 'See the kinds of weakness the scanner looks for. Each rule explains its risk and shows a safer code example.'],
  ['Student guide', 'guide', 'tree', 'Follow a practice scan, learn what the results mean, and check your understanding.'],
];

const steps = [
  ['Start with a sample', 'Choose Run weak randomness demo. It loads and scans a Python function that makes a session token. For your own file, use Open Python file, then Run analysis.'],
  ['Find the line', 'Look under Findings for Weak randomness. Expand it, then choose Highlight source to see the exact function call. Why this spot? explains what the scanner recognized.'],
  ['Review the proposed fix', 'Choose Preview repair to compare the original and suggested code. The site checks that Python can parse and compile the edit, then scans it again.'],
  ['Apply and check again', 'Choose Apply and re-scan and look for the issue count to drop. Save your work with Download .py, or use Security report to export the scan results.'],
];

const terms = [
  ['AST and node', 'An abstract syntax tree (AST) is Python’s map of how a file is put together. A node is one piece of that map. In print("Hi"), the call and the text value are two pieces.'],
  ['Code elements and element types', 'Code elements counts all pieces on the map. Element types counts the different kinds, such as imports, calls, and values.'],
  ['Finding and CWE', 'A finding is a pattern the scanner flagged for review. A CWE code identifies its weakness category. For example, CWE-330 identifies weak randomness.'],
  ['Manual review and validation', 'Manual review means you need to decide how to change the code. Validation checks the structure and scanner results for a proposed edit without running the program.'],
];

function PracticeQuestion() {
  const [answer, setAnswer] = useState(null);

  return (
    <div className="guide-practice">
      <h3>Quick self-check</h3>
      <p>If the scan shows zero potential issues, what can you conclude?</p>
      <div role="group" aria-label="Choose an answer">
        <DnaButton className="button secondary" aria-pressed={answer === 'secure'} onClick={() => setAnswer('secure')}>
          The program is secure
        </DnaButton>
        <DnaButton className="button secondary" aria-pressed={answer === 'patterns'} onClick={() => setAnswer('patterns')}>
          No supported patterns were found
        </DnaButton>
      </div>
      {answer && (
        <p className="guide-feedback" role="status">
          {answer === 'patterns'
            ? 'Correct. The scanner checks a fixed set of patterns. Other weaknesses may still be present.'
            : 'Try again. Think about how many weakness categories the scanner checks.'}
        </p>
      )}
    </div>
  );
}

export function StudentGuide({ runDemo, busy, setPage }) {
  return (
    <>
      <div className="page-heading guide-heading">
        <div><h1>Student guide</h1><p>Learn to read a Python security scan and try your first repair.</p></div>
        <DnaButton className="button primary" disabled={busy} onClick={() => runDemo(examples[0])}>
          <Icon name="play" size={16} /> Run weak randomness demo
        </DnaButton>
      </div>
      <section aria-labelledby="guide-nav-heading">
        <h2 id="guide-nav-heading" className="guide-section-title">What’s in the sidebar?</h2>
        <div className="guide-nav">
          {sections.map(([title, page, icon, detail]) => (
            <article className="panel" key={page}>
              <h3><Icon name={icon} size={17} />{title}</h3>
              <p>{detail}</p>
              {page !== 'guide' && <DnaButton className="line-link" onClick={() => setPage(page)}>Open {title.toLowerCase()}</DnaButton>}
            </article>
          ))}
        </div>
      </section>
      <div className="guide-layout">
        <section className="panel guide-panel" aria-labelledby="walkthrough-heading">
          <h2 id="walkthrough-heading">Your first scan</h2>
          <ol className="guide-steps">
            {steps.map(([title, detail], index) => (
              <li key={title}>
                <span aria-hidden="true">{index + 1}</span>
                <div><h3>{title}</h3><p>{detail}</p></div>
              </li>
            ))}
          </ol>
          <p className="guide-note"><strong>Seeing a syntax error?</strong> Use Go to line, correct the Python syntax, then run analysis again.</p>
        </section>
        <section className="panel guide-panel" aria-labelledby="terms-heading">
          <h2 id="terms-heading">Terms you’ll see</h2>
          <div className="guide-terms">
            {terms.map(([term, explanation]) => (
              <details key={term}><summary>{term}</summary><p>{explanation}</p></details>
            ))}
          </div>
          <PracticeQuestion />
        </section>
      </div>
    </>
  );
}
