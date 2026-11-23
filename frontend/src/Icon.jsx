import React from 'react';

const paths = {
  helix: 'M5 2c0 7 14 13 14 20M19 2c0 7-14 13-14 20M6 5h12M9 8h6M9 16h6M6 19h12',
  code: 'm8 6-6 6 6 6m8-12 6 6-6 6m-2-15-4 18',
  workspace: 'M3 4h18v16H3zM3 9h18m-12 0v11',
  history: 'M3 12a9 9 0 1 1 2.7 6.4M3 12V6m0 6h6m3-5v5l3 2',
  shield: 'M12 22s7-3 7-10V5l-7-3-7 3v7c0 7 7 10 7 10Z',
  upload: 'M12 16V4m-5 5 5-5 5 5M4 16v4h16v-4',
  play: 'm8 5 12 7-12 7V5Z',
  file: 'M6 3h8l4 4v14H6zM14 3v5h4',
  tree: 'M5 5h4v4H5zm10 10h4v4h-4zM7 9v8h8m0-10h4m-2-2v4',
  check: 'm5 12 4 4L19 6',
  alert: 'M12 3 2 20h20L12 3Zm0 6v4m0 3v1',
  chevron: 'm6 9 6 6 6-6',
};

export function Icon({ name, size = 18 }) {
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round">
      <path d={paths[name]} />
    </svg>
  );
}
