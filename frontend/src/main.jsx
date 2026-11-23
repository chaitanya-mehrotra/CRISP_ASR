import React, { useCallback, useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { fetchParserHealth, parseError, parseSource } from './api';
import { History, RuleScope } from './ProjectViews';
import { Icon } from './Icon';
import { AccountPanel } from './AccountPanel';
import { Workspace } from './Workspace';
import { Sidebar } from './Sidebar';
import { StudentGuide } from './StudentGuide';
import './styles.css';

function App() {
  const [page, setPage] = useState('workspace');
  const [resultView, setResultView] = useState('findings');
  const [jumpPending, setJumpPending] = useState(false);
  const [source, setSource] = useState('');
  const [file, setFile] = useState('untitled.py');
  const [api, setApi] = useState('Checking parser');
  const [analysis, setAnalysis] = useState(null);
  const [entries, setEntries] = useState([]);
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const sequence = useRef(0);

  const analyze = useCallback(async (source, file, repair = null) => {
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    const attempt = { id: ++sequence.current, time: new Date(), file };
    try {
      const result = await parseSource(source);
      setApi('Parser online');
      setAnalysis((previous) => ({
        id: attempt.id, source, file, result,
        repair: repair ?? (previous?.source === source && previous?.file === file ? previous.repair : null),
      }));
      setEntries((previous) => [{ ...attempt, count: result.node_count, findings: result.findings.length, status: 'Analyzed' }, ...previous]);
    } catch (error) {
      const problem = parseError(error);
      setApi(error.response && error.response.status < 500 ? 'Parser online' : 'Parser unavailable');
      setAnalysis({ source, file, problem });
      setEntries((previous) => [{ ...attempt, status: problem.line ? 'Syntax error' : 'Failed' }, ...previous]);
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    function updateStatus(status) {
      if (!controller.signal.aborted && sequence.current === 0) setApi(status);
    }
    fetchParserHealth(controller.signal)
      .then((ready) => updateStatus(ready ? 'Parser online' : 'Parser unavailable'))
      .catch(() => updateStatus('Parser unavailable'));
    return () => controller.abort();
  }, []);

  function runDemo(example) {
    setPage('workspace');
    setResultView('findings');
    setFile(example.name);
    setSource(example.source);
    analyze(example.source, example.name);
  }

  function showFindings() {
    setPage('workspace');
    setResultView('findings');
    setJumpPending(true);
  }

  useEffect(() => {
    if (!jumpPending || page !== 'workspace') return;
    const heading = document.getElementById('result-heading');
    heading?.focus({ preventScroll: true });
    heading?.scrollIntoView({ block: 'start' });
    setJumpPending(false);
  }, [jumpPending, page]);

  const stale = analysis && (analysis.source !== source || analysis.file !== file);

  return (
    <>
      <header className="app-header">
        <div className="brand">
          <span className="brand-icon"><Icon name="helix" size={22} /></span>
          <div><strong>CRISPR-ASR</strong><span>HelixForge</span></div>
        </div>
        <div className="header-actions">
          <span className="api-status" data-online={api === 'Parser online'} role="status">
            <span aria-hidden="true" />{api}
          </span>
          <AccountPanel />
        </div>
      </header>
      <div className="app-grid">
        <Sidebar {...{ page, setPage, file, analysis, stale, busy, runDemo, showFindings }} />
        <main>
          {page === 'workspace' && (
            <Workspace {...{ source, setSource, file, setFile, analyze, analysis, busy, resultView, setResultView }} />
          )}
          {page === 'history' && <History entries={entries} />}
          {page === 'rules' && <RuleScope />}
          {page === 'guide' && <StudentGuide {...{ runDemo, busy, setPage }} />}
        </main>
      </div>
    </>
  );
}

createRoot(document.getElementById('root')).render(<App />);
