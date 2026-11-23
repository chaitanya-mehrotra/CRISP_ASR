import axios from 'axios';

export async function parseSource(source) {
  const response = await axios.post('/api/parse', { source }, { timeout: 10000 });
  return response.data;
}

export function parseError(error) {
  const { detail } = error.response?.data ?? {};
  if (detail?.line) return { message: detail.message, line: detail.line };
  if (typeof detail === 'string') return { message: detail };
  if (Array.isArray(detail)) return { message: detail[0]?.msg ?? 'The request was rejected.' };
  return { message: 'Could not reach the parser. Check that FastAPI is running on port 8000.' };
}

export async function fetchRules(signal) {
  const response = await axios.get('/api/rules', { signal, timeout: 10000 });
  return response.data;
}

export async function previewRepair(source, finding, signal) {
  const response = await axios.post('/api/repair-preview', {
    source,
    rule_id: finding.id,
    line: finding.line,
    column: finding.column,
  }, { signal, timeout: 10000 });
  return response.data;
}

export async function accountRequest(action, credentials, signal) {
  const options = { timeout: 10000, signal };
  const response = action === 'session'
    ? await axios.get('/api/auth/session', options)
    : await axios.post(`/api/auth/${action}`, credentials, options);
  return response.data;
}

export async function fetchParserHealth(signal) {
  const response = await axios.get('/api/health', { signal, timeout: 3000 });
  return response.data.status === 'ok';
}

export async function previewAllRepairs(source, signal) {
  const response = await axios.post('/api/repair-preview/all', { source }, { signal, timeout: 10000 });
  return response.data;
}
