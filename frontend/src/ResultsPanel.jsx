import React from 'react';
import { DnaButton } from './DnaButton';
import { BatchRepair } from './BatchRepair';
import { FindingCards } from './FindingCards';
import { Icon } from './Icon';

const elementLabels = {
  Module: 'Whole file',
  FunctionDef: 'Function definition',
  AsyncFunctionDef: 'Async function definition',
  ClassDef: 'Class definition',
  Import: 'Import',
  ImportFrom: 'Import from a module',
  Assign: 'Assignment',
  AnnAssign: 'Assignment with a type hint',
  AugAssign: 'Update a value',
  Expr: 'Standalone expression',
  Call: 'Function or method call',
  Return: 'Return a value',
  Attribute: 'Access a property or method',
  Name: 'Name used in code',
  Constant: 'Literal value',
  Load: 'Read a value',
  Store: 'Write a value',
  If: 'If statement',
  For: 'For loop',
  While: 'While loop',
  BinOp: 'Operation on two values',
  Compare: 'Comparison',
  ListComp: 'List comprehension',
  arguments: 'Function parameter list',
  arg: 'Function parameter',
  alias: 'Imported name',
  keyword: 'Named argument',
};

function elementLabel(kind) {
  return elementLabels[kind] ?? kind;
}

const views = [
  ['findings', 'Findings'],
  ['outline', 'Outline'],
  ['types', 'Code breakdown'],
];

export function ResultsPanel({ analysis, busy, stale, jumpToLine, applyPatch, view, setView }) {
  const { result, problem } = analysis ?? {};

  return (
    <section className="panel results-panel" aria-labelledby="result-heading" aria-busy={busy}>
      <div className="panel-header">
        <Icon name="shield" />
        <h2 id="result-heading" tabIndex={-1}>Analysis results</h2>
      </div>
      <div className="results-body" aria-live="polite">
        {busy && <p className="notice">Parsing Python and checking for weaknesses…</p>}
        {!busy && !analysis && <p className="notice">Run an analysis to see findings and the syntax tree.</p>}
        {!busy && stale && <p className="notice warning">Source changed. Run analysis to update these results.</p>}
        {!busy && problem && (
          <div className="diagnostic">
            <Icon name="alert" />
            <div>
              <strong>{problem.line ? 'Syntax error' : 'Analysis failed'}</strong>
              <p>{problem.message}</p>
              {problem.line && !stale && (
                <button className="line-link" onClick={() => jumpToLine(problem)}>Go to line {problem.line}</button>
              )}
            </div>
          </div>
        )}
        {!busy && result && (
          <>
            <div className="metrics">
              <div><strong>{result.findings.length.toLocaleString()}</strong><span>Potential issues</span></div>
              <div><strong>{result.node_count.toLocaleString()}</strong><span>Code elements</span></div>
              <div><strong>{Object.keys(result.node_types).length.toLocaleString()}</strong><span>Element types</span></div>
            </div>
            <BatchRepair key={analysis.id} {...{ analysis, stale, applyPatch }} />
            <details className="results-guide">
              <summary>What do these numbers mean?</summary>
              <p><strong>Potential issues</strong> are patterns to review. Open Findings to see the line, the reason it was flagged, and how to fix it.</p>
              <p>An <strong>abstract syntax tree (AST)</strong> is Python’s map of how your code is put together. A <strong>node</strong> is one element on that map. In <code>print("Hi")</code>, the function call and the text value are two examples of elements.</p>
              <p><strong>Element types</strong> counts distinct kinds, such as function calls, imports, and values. The Code breakdown tab shows the count for each kind.</p>
            </details>
            <div className="view-switch" role="group" aria-label="Analysis view">
              {views.map(([id, name]) => (
                <DnaButton key={id} aria-pressed={view === id} onClick={() => setView(id)}>{name}</DnaButton>
              ))}
            </div>
            {view === 'findings' && <FindingCards key={analysis.id} findings={result.findings} source={analysis.source} {...{ stale, jumpToLine, applyPatch }} />}
            {view === 'outline' && (
              <div className="result-list">
                {result.outline.length ? (
                  <ul aria-label="Top-level statements">
                    {result.outline.map(({ kind, name, line }, index) => (
                      <li key={index}>
                        <button className="outline-row" disabled={stale} onClick={() => jumpToLine({ line })}>
                          <Icon name="code" size={15} />
                          <span className="statement">
                            <strong>{name ?? elementLabel(kind)}</strong>
                            {name && <small>{elementLabel(kind)}</small>}
                          </span>
                          <span className="location">L{line}</span>
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : <p className="notice">No top-level statements.</p>}
              </div>
            )}
            {view === 'types' && (
              <div className="result-list">
                <dl className="structure-counts" aria-label="Code structure summary">
                  {Object.entries(result.structure).map(([kind, count]) => (
                    <div key={kind}><dt>{kind}</dt><dd>{count}</dd></div>
                  ))}
                </dl>
                <dl className="type-list">
                  {Object.entries(result.node_types).map(([kind, count]) => (
                    <div key={kind}><dt>{elementLabel(kind)}{elementLabel(kind) !== kind && <small>{kind}</small>}</dt><dd>{count}</dd></div>
                  ))}
                </dl>
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
}
