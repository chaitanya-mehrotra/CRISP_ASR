import React, { useEffect, useRef } from 'react';
import { editor } from 'monaco-editor/esm/vs/editor/editor.api';
import 'monaco-editor/esm/vs/basic-languages/python/python.contribution';
import EditorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';

self.MonacoEnvironment = { getWorker: () => new EditorWorker() };

editor.defineTheme('helix-dark', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'keyword', foreground: 'BDABFF' },
    { token: 'string', foreground: 'A7DBA6' },
    { token: 'number', foreground: 'F1AB7D' },
  ],
  colors: {
    'editor.background': '#0F1724',
    'editor.foreground': '#DCE3F5',
    'editorLineNumber.foreground': '#6C7895',
    'editorLineNumber.activeForeground': '#CDD6EA',
    'editor.lineHighlightBackground': '#17283A',
    'editor.selectionBackground': '#39456B',
    'editorIndentGuide.background1': '#273149',
  },
});

export function Editor({ editorRef, value, onChange }) {
  const container = useRef(null);

  useEffect(() => {
    const instance = editor.create(container.current, {
      language: 'python',
      theme: 'helix-dark',
      automaticLayout: true,
      ariaLabel: 'Python source code',
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 14,
      lineHeight: 24,
      padding: { top: 16, bottom: 16 },
      renderLineHighlight: 'line',
      wordWrap: 'on',
      glyphMargin: false,
      tabSize: 4,
    });
    const model = instance.getModel();
    const listener = instance.onDidChangeModelContent(() => onChange(instance.getValue()));
    editorRef.current = instance;
    return () => {
      listener.dispose();
      instance.dispose();
      model.dispose();
      editorRef.current = null;
    };
  }, [editorRef, onChange]);

  useEffect(() => {
    const instance = editorRef.current;
    if (instance.getValue() !== value) instance.setValue(value);
  }, [editorRef, value]);

  return <div ref={container} className="editor" />;
}
