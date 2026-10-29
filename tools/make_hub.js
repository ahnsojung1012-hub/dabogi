// Usage: node make_hub.js <state.json>  → writes index.html: one link for all students, each sees only their grade's exams.
const fs = require('fs');
const state = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const pages = JSON.parse(fs.readFileSync(__dirname + '/pages.json', 'utf8'));
let cfg = {}; try { cfg = JSON.parse(fs.readFileSync(__dirname + '/config.json', 'utf8')); } catch (e) {}
let roster = []; try { roster = JSON.parse(fs.readFileSync(__dirname + '/roster.json', 'utf8')); } catch (e) {}
const v = Date.now().toString(36);
const exams = Object.entries(pages).map(([file, p]) => {
  const meta = typeof p === 'string' ? { id: p } : p;
  const ex = state.exams.find(e => e.id === meta.id);
  if (!ex || ex.sample || meta.hidden) return null;
  return { id: ex.id, title: ex.title, grade: meta.grade || ex.grade || null, n: ex.hashes.length, np: ex.images.length, link: file + '?v=' + v };
}).filter(Boolean);
let tpl = fs.readFileSync(__dirname + '/template.html', 'utf8');
const json = JSON.stringify({ exams, studentOnly: true, hub: true, v, endpoint: cfg.endpoint || '', roster }).replace(/</g, '\\u003c');
tpl = tpl.replace('<title>블라인드 테스트</title>', '<title>시험 대비 · 페르마 수학학원</title>').replace('__STATE__', () => json);
const page = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex"><style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + tpl + '</body></html>';
fs.writeFileSync('index.html', page);
console.log('wrote index.html with', exams.length, 'exams');
