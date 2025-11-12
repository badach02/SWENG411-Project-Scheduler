const rowsEl = document.getElementById('rows');
const searchEl = document.getElementById('search');
const countEl = document.getElementById('count');
const emptyEl = document.getElementById('empty');

let items = [
  "Alpha Centauri",
  "Beta Release Notes",
  "Gamma Ray Burst Archive",
  "Delta Project Plan",
  "Epsilon - UX Spec",
  "Omega Final Draft",
  "Search Engine Optimization Guide",
  "Relevance Ranking Paper",
  "Quick Brown Fox",
  "Lazy Dog Case Study",
  "Example: User Feedback",
  "Another Example Item",
  "Fuzzy Matching Demo",
  "Prefix Matches First",
  "Contains in the Middle"
];

let idCounter = 0;
let originalOrder = items.map((t, i) => ({ id: ++idCounter, text: t, index: i }));

function levenshtein(a, b) {
  if (a === b) return 0;
  if (!a.length) return b.length;
  if (!b.length) return a.length;
  const matrix = [];
  for (let i = 0; i <= b.length; i++) matrix[i] = [i];
  for (let j = 0; j <= a.length; j++) matrix[0][j] = j;
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      const cost = a[j - 1] === b[i - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }
  return matrix[b.length][a.length];
}

function scoreItem(text, query) {
  if (!query) return 0;
  const s = text.toLowerCase();
  const q = query.toLowerCase().trim();
  if (!q) return 0;

  if (s === q) return 1000;
  if (s.startsWith(q)) return 800 - s.length / 100;
  const idx = s.indexOf(q);
  if (idx >= 0) return 600 + Math.max(0, 100 - idx);

  const d = levenshtein(q, s);
  const maxLen = Math.max(q.length, s.length);
  const similarity = (maxLen - d) / maxLen;
  return Math.round(similarity * 100);
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[m]));
}

function highlight(text, query) {
  if (!query) return escapeHtml(text);
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx === -1) return escapeHtml(text);
  return (
    escapeHtml(text.slice(0, idx)) +
    `<mark class="match">${escapeHtml(text.slice(idx, idx + query.length))}</mark>` +
    escapeHtml(text.slice(idx + query.length))
  );
}

function render(query = '') {
  const q = query.trim();
  const scored = originalOrder.map(obj => ({
    id: obj.id,
    text: obj.text,
    index: obj.index,
    score: scoreItem(obj.text, q)
  }));

  const visible = q ? scored.filter(s => s.score >= 10) : scored;
  visible.sort((a, b) => b.score - a.score || a.index - b.index);

  countEl.textContent = visible.length;
  rowsEl.innerHTML = '';
  emptyEl.style.display = visible.length ? 'none' : 'block';

  for (const v of visible) {
    const row = document.createElement('div');
    row.className = 'row' + (v.score >= 600 ? ' high' : (v.score > 0 ? ' relevant' : ''));
    row.tabIndex = 0;
    row.innerHTML = `
      <div class="title">${highlight(v.text, q)}</div>
      <div class="meta">Relevance: ${v.score}</div>
    `;
    row.addEventListener('click', () => alert('Selected: ' + v.text));
    rowsEl.appendChild(row);
  }
}

searchEl.addEventListener('input', e => render(e.target.value));

document.getElementById('reset').addEventListener('click', () => {
  searchEl.value = '';
  render('');
  searchEl.focus();
});

document.getElementById('example').addEventListener('click', () => {
  const extras = [
    "Apple iPhone 15 Pro",
    "Samsung Galaxy S25",
    "USB-C Cable",
    "TypeScript Guide",
    "Python Cookbook",
    "Fluent UI Patterns",
    "Accessibility Checklist",
    "Design System Tokens",
    "User Research Notes",
    "Component Roadmap"
  ];
  extras.forEach(t => {
    if (!originalOrder.some(o => o.text === t)) {
      originalOrder.push({ id: ++idCounter, text: t, index: originalOrder.length });
    }
  });
  render(searchEl.value);
});

render('');
