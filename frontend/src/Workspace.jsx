import React, { useRef, useState } from 'react';
import { DnaButton } from './DnaButton';
import { Editor } from './Editor';
import { examples } from './examples';
import { Icon } from './Icon';
import { Helix } from './Helix';
import { ResultsPanel } from './ResultsPanel';

const maxSourceLength = 100_000;

export function Workspace({ source, setSource, file, setFile, analyze, analysis, busy, resultView, setResultView }) {
  const editorRef = useRef(null);
  const fileInput = useRef(null);
  const [pulse, setPulse] = useState(0);
  const [reading, setReading] = useState(false);
  const [fileError, setFileError] = useState('');
  const stale = analysis && (source !== analysis.source || file !== analysis.file);

  function chooseExample(event) {
    const example = examples.find(({ name }) => name === event.target.value);
    if (!example) return;
    setFileError('');
    setFile(example.name);
    setSource(example.source);
  }

  async function readFile(event) {
    const upload = event.target.files[0];
    event.target.value = '';
    if (!upload) return;
    setFileError('');
    setReading(true);
    try {
      if (!upload.name.toLowerCase().endsWith('.py')) throw new Error('Choose a .py file.');
      if (upload.size > 4 * maxSourceLength) throw new Error('Choose a file with 100,000 characters or fewer.');
      const text = new TextDecoder('utf-8', { fatal: true }).decode(await upload.arrayBuffer());
      if (Array.from(text).length > maxSourceLength) throw new Error('Choose a file with 100,000 characters or fewer.');
      setSource(text.replace(/\r\n?/g, '\n'));
      setFile(upload.name);
    } catch (error) {
      setFileError(error instanceof TypeError ? 'Choose a Python file encoded as UTF-8.' : error.message);
    } finally {
      setReading(false);
    }
  }

  function jumpToLine({ line, column = 1, end_line, end_column }) {
    const instance = editorRef.current;
    if (end_line) {
      instance.setSelection({
        startLineNumber: line,
        startColumn: column,
        endLineNumber: end_line,
        endColumn: end_column,
      });
    } else {
      instance.setPosition({ lineNumber: line, column });
    }
    instance.revealLineInCenterIfOutsideViewport(line);
    instance.focus();
  }

  function applyPatch(patch) {
    const instance = editorRef.current;
    const model = instance.getModel();
    if (stale || busy || instance.getValue() !== analysis.source) return false;
    const changes = patch.changes ?? [patch];
    if (changes.some(({ line, before }) => model.getLineContent(line) !== before)) return false;
    const edits = changes.map(({ line, after }) => ({
      range: {
        startLineNumber: line,
        startColumn: 1,
        endLineNumber: line,
        endColumn: model.getLineMaxColumn(line),
      },
      text: after,
    }));
    instance.pushUndoStop();
    if (!instance.executeEdits('crispr-asr-repair', edits)) return false;
    instance.pushUndoStop();
    jumpToLine({ line: changes[0].line });
    setPulse((previous) => previous + 1);
    const { checks, before_findings, remaining_findings, target_resolved, new_findings } = patch;
    analyze(instance.getValue(), file, {
      checks, before_findings, remaining_findings, target_resolved, new_findings,
      changed_lines: changes.map(({ line }) => line),
      repair_count: patch.repair_count ?? 1,
    });
    return true;
  }

  function download(content, name, type) {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const link = document.createElement('a');
    link.href = url;
    link.download = name;
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function downloadReport() {
    const { result, repair } = analysis;
    const report = {
      file,
      finding_count: result.findings.length,
      findings: result.findings.map(({ id, title, line, column, severity, repair_mode }) => (
        { id, title, line, column, severity, repair_mode }
      )),
      verification: repair ?? { status: 'No repair verified for this analysis' },
    };
    download(JSON.stringify(report, null, 2), file.replace(/\.py$/i, '') + '-security-report.json', 'application/json');
  }

  return (
    <>
      <section className="workspace-hero" aria-labelledby="workspace-title">
        <div className="hero-content">
          <p className="project-label"><Icon name="helix" size={15} /> Bioinspired EL</p>
          <h1 id="workspace-title">Analysis workspace</h1>
          <p className="hero-description">Inspired by CRISPR’s precise targeting, scan Python for security weaknesses, pinpoint the source, and see how to fix each finding.</p>
          <div className="action-bar">
            <input type="file" accept=".py,text/x-python" ref={fileInput} onChange={readFile} hidden />
            <DnaButton className="button secondary" disabled={reading} onClick={() => fileInput.current.click()}>
              <Icon name="upload" size={17} />{reading ? 'Opening…' : 'Open Python file'}
            </DnaButton>
            <DnaButton className="button primary" disabled={busy || reading || !source.length}
              onClick={() => {
                setPulse((previous) => previous + 1);
                analyze(source, file);
              }}>
              <Icon name="play" size={16} />{busy ? 'Analyzing…' : 'Run analysis'}
            </DnaButton>
          </div>
        </div>
        <Helix pulse={pulse} />
      </section>
      {fileError && <p className="notice warning" role="alert">{fileError}</p>}
      <div className="workspace-grid">
        <section className="panel source-panel" aria-labelledby="source-heading">
          <div className="panel-header">
            <Icon name="code" />
            <h2 id="source-heading">Python source</h2>
            <label className="example-select">
              <select aria-label="Load example" value="" onChange={chooseExample} disabled={reading}>
                <option value="" disabled>Load example</option>
                {examples.map(({ name, label }) => <option key={name} value={name}>{label}</option>)}
              </select>
              <Icon name="chevron" size={15} />
            </label>
          </div>
          <div className="file-bar"><Icon name="file" size={16} /><span title={file}>{file}</span></div>
          <Editor editorRef={editorRef} value={source} onChange={setSource} />
          <footer className="editor-footer"><span>Python · {source.split('\n').length.toLocaleString()} lines</span>
            <DnaButton className="line-link" disabled={!source.length} onClick={() => download(source, file, "text/x-python;charset=utf-8")}>Download .py</DnaButton>
            <DnaButton className="line-link" disabled={stale || busy || !analysis?.result} onClick={downloadReport}>Security report</DnaButton>
          </footer>
        </section>
        <ResultsPanel analysis={analysis} busy={busy} stale={stale} jumpToLine={jumpToLine} applyPatch={applyPatch} view={resultView} setView={setResultView} />
      </div>
    </>
  );
}
