import React from 'react';

export function FindingLesson({ finding }) {
  return (
    <details className="finding-lesson">
      <summary>Why this spot?</summary>
      <h3>How Python reads the expression</h3>
      <ol className="ast-chain" aria-label="Syntax tree path">
        {finding.ast_chain.map((kind, index) => <li key={index}><code>{kind}</code></li>)}
      </ol>
      <h3>Where the value comes from</h3>
      <p>{finding.origin}</p>
      <h3>What could go wrong</h3>
      <p>{finding.impact}</p>
      <details>
        <summary>Quick self-check</summary>
        <p>{finding.question}</p>
      </details>
    </details>
  );
}
