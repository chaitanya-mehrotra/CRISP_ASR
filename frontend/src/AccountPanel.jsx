import React, { useEffect, useRef, useState } from 'react';
import { accountRequest, parseError } from './api';
import { DnaButton } from './DnaButton';
import { Icon } from './Icon';

export function AccountPanel() {
  const dialog = useRef(null);
  const [account, setAccount] = useState(undefined);
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    accountRequest('session', undefined, controller.signal)
      .then(setAccount)
      .catch(() => { if (!controller.signal.aborted) setAccount(null); });
    return () => controller.abort();
  }, []);

  function switchMode(nextMode) {
    setMode(nextMode);
    setError('');
    setPassword('');
  }

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      const result = await accountRequest(account ? 'logout' : mode, account ? undefined : { username, password });
      setAccount(result || null);
      dialog.current.close();
    } catch (problem) {
      setError(parseError(problem).message);
    } finally {
      setPassword('');
      setBusy(false);
    }
  }

  const creating = mode === 'register';

  return (
    <>
      <DnaButton className="button secondary account-trigger" disabled={account === undefined} onClick={() => {
        switchMode('login');
        dialog.current.showModal();
      }}>
        <Icon name="shield" size={16} />{account?.username ?? 'Sign in'}
      </DnaButton>
      <dialog ref={dialog} className="account-dialog" aria-labelledby="account-heading"
        onCancel={(event) => { if (busy) event.preventDefault(); }}
        onClose={() => setPassword('')}>
        <div className="account-heading">
          <span className="brand-icon"><Icon name="helix" size={22} /></span>
          <DnaButton className="line-link" disabled={busy} onClick={() => dialog.current.close()}>Close</DnaButton>
        </div>
        <h2 id="account-heading">{account ? 'Your account' : creating ? 'Create a local account' : 'Sign in to CRISPR-ASR'}</h2>
        <p>{account ? `Signed in as ${account.username}.` : 'Your account is stored on this computer. You can also use the scanner as a guest.'}</p>
        <form className="account-form" onSubmit={submit}>
          {!account && (
            <>
              <label htmlFor="auth-name">Username</label>
              <input id="auth-name" value={username} onChange={(event) => setUsername(event.target.value)}
                autoComplete="username" required maxLength={32} disabled={busy} />
              <label htmlFor="auth-password">Password</label>
              <input id="auth-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)}
                autoComplete={creating ? 'new-password' : 'current-password'} required minLength={12} maxLength={128}
                aria-describedby={creating ? 'auth-password-help' : undefined} disabled={busy} />
              {creating && <small id="auth-password-help">Choose at least 12 characters.</small>}
            </>
          )}
          {error && <p className="account-error" role="alert">{error}</p>}
          <button type="submit" className="button primary" disabled={busy}>
            {busy ? 'Please wait…' : account ? 'Sign out' : creating ? 'Create account' : 'Sign in'}
          </button>
        </form>
        {!account && (
          <div className="account-options">
            <DnaButton className="line-link" disabled={busy} onClick={() => switchMode(creating ? 'login' : 'register')}>
              {creating ? 'Back to sign in' : 'Create an account'}
            </DnaButton>
            <DnaButton className="line-link" disabled={busy} onClick={() => dialog.current.close()}>Continue as guest</DnaButton>
          </div>
        )}
      </dialog>
    </>
  );
}
