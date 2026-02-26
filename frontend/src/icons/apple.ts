export type AppleIconName =
  | 'document'
  | 'chat'
  | 'trend'
  | 'settings'
  | 'arrow-right'
  | 'arrow-left'
  | 'arrow-down'
  | 'plus'
  | 'user'
  | 'refresh'
  | 'loading'
  | 'reading'
  | 'star'
  | 'view'
  | 'book'
  | 'shield'
  | 'bolt'
  | 'graph'
  | 'chevron-down'
  | 'folder'
  | 'more'
  | 'upload'
  | 'trash'
  | 'chat-bubble'
  | 'cpu'
  | 'clock'
  | 'message'
  | 'info'
  | 'warning'
  | 'stop'
  | 'full-screen';

interface IconPath {
  d: string;
  fill?: string;
}

interface AppleIconDefinition {
  viewBox: string;
  paths: IconPath[];
}

export const appleIcons: Record<AppleIconName, AppleIconDefinition> = {
  document: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M7 3h7l4 4v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z' },
      { d: 'M14 3v5h5' },
      { d: 'M9 12h6' },
      { d: 'M9 16h4' }
    ]
  },
  plus: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 5v14' },
      { d: 'M5 12h14' }
    ]
  },
  'arrow-left': {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M19 12H5' },
      { d: 'M11 18l-6-6 6-6' }
    ]
  },
  chat: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-5l-4 4v-4H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z' }
    ]
  },
  trend: {
    viewBox: '0 0 24 24',
    paths: [{ d: 'M4 16l5-6 4 3 7-9' }]
  },
  settings: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z' },
      { d: 'M12 3v3' },
      { d: 'M12 18v3' },
      { d: 'M4.7 6.3l2.1 2.1' },
      { d: 'M17.2 17.7l2.1 2.1' },
      { d: 'M3 12h3' },
      { d: 'M18 12h3' },
      { d: 'M4.7 17.7l2.1-2.1' },
      { d: 'M17.2 6.3l2.1-2.1' }
    ]
  },
  'arrow-right': {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M5 12h14' },
      { d: 'M13 6l6 6-6 6' }
    ]
  },
  'arrow-down': {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 5v14' },
      { d: 'M6 13l6 6 6-6' }
    ]
  },
  'chevron-down': {
    viewBox: '0 0 24 24',
    paths: [{ d: 'M6 9l6 6 6-6' }]
  },
  user: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8z' },
      { d: 'M5 20a7 7 0 0 1 14 0' }
    ]
  },
  refresh: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M5 11a7 7 0 0 1 12-4l2 2V5' },
      { d: 'M19 13a7 7 0 0 1-12 4l-2-2v4' }
    ]
  },
  loading: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 4a8 8 0 1 1-5.657 2.343', fill: 'none' }
    ]
  },
  reading: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M4 5h6a3 3 0 0 1 3 3v13c-1.5-1.5-3.5-2.5-6-2.5H4z' },
      { d: 'M20 5h-6a3 3 0 0 0-3 3v13c1.5-1.5 3.5-2.5 6-2.5h3z' }
    ]
  },
  star: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 3.5l2.6 4.9 5.4.8-4 3.9.95 5.4L12 15.8l-4.95 2.9.95-5.4-4-3.9 5.4-.8z' }
    ]
  },
  view: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M2 12s4-6 10-6 10 6 10 6-4 6-10 6-10-6-10-6z' },
      { d: 'M12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z' }
    ]
  },
  book: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M5 4h6a3 3 0 0 1 3 3v13c-1.5-1.5-3.5-2.5-6-2.5H5z' },
      { d: 'M19 4h-6a3 3 0 0 0-3 3v13c1.5-1.5 3.5-2.5 6-2.5h3z' }
    ]
  },
  shield: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 3l8 3v6c0 4.5-3 8.2-8 9-5-0.8-8-4.5-8-9V6z' }
    ]
  },
  bolt: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M11 2L5 14h6l-2 8 8-12h-6z' }
    ]
  },
  graph: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M4 20V10' },
      { d: 'M10 20V4' },
      { d: 'M16 20V7' },
      { d: 'M22 20V12' }
    ]
  },
  folder: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M3 6h6l2 2h10v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z' }
    ]
  },
  more: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M6 12h.01' },
      { d: 'M12 12h.01' },
      { d: 'M18 12h.01' }
    ]
  },
  upload: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M4 17v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3' },
      { d: 'M7 9l5-5 5 5' },
      { d: 'M12 4v12' }
    ]
  },
  trash: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M4 7h16' },
      { d: 'M10 11v6' },
      { d: 'M14 11v6' },
      { d: 'M6 7l1 13a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-13' },
      { d: 'M9 7V4h6v3' }
    ]
  },
  'chat-bubble': {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-5l-4 4v-4H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z' }
    ]
  },
  cpu: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M6 9v6' },
      { d: 'M9 6h6' },
      { d: 'M15 18V6' },
      { d: 'M6 15h12' },
      { d: 'M9 9h6v6H9z' },
      { d: 'M4 10v4' },
      { d: 'M20 10v4' },
      { d: 'M10 4h4' },
      { d: 'M10 20h4' }
    ]
  },
  clock: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 6v6l4 2' },
      { d: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z' }
    ]
  },
  message: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M5 5h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H9l-4 4v-4H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z' }
    ]
  },
  info: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 17v-5' },
      { d: 'M12 8h.01' },
      { d: 'M4 12a8 8 0 1 1 16 0 8 8 0 0 1-16 0z' }
    ]
  },
  warning: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M12 9v5' },
      { d: 'M12 17h.01' },
      { d: 'M10.29 3.86L2.82 18a1.7 1.7 0 0 0 1.47 2.5h15.42a1.7 1.7 0 0 0 1.47-2.5L13.71 3.86a1.7 1.7 0 0 0-2.94 0z' }
    ]
  },
  stop: {
    viewBox: '0 0 24 24',
    paths: [
      { d: 'M6 6h12v12H6z' }
    ]
  }
}

