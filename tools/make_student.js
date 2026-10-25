// Usage: node make_student.js <state.json> <examId|--list> <out.html>
// Builds a student-only page for one exam from the teacher artifact's embedded state.
const fs = require('fs');
const [stateFile, examId, out] = process.argv.slice(2);
const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
if (examId === '--list') {
  state.exams.forEach(e => console.log(e.id, '|', e.title, '|', e.hashes.length + '문항', '| 사진 ' + e.images.length, e.lock ? '| AI분석' : ''));
  process.exit(0);
}
const ex = state.exams.find(e => e.id === examId);
if (!ex) { console.error('exam not found'); process.exit(1); }
let tpl = fs.readFileSync(__dirname + '/template.html', 'utf8');
const json = JSON.stringify({ exams: [ex], studentOnly: true }).replace(/</g, '\\u003c');
tpl = tpl.replace('<title>다시보기 채점실</title>', `<title>${ex.title.replace(/[<&]/g, '')} · 다시보기 채점실</title>`);
tpl = tpl.replace('__STATE__', () => json);
const page = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + tpl + '</body></html>';
fs.writeFileSync(out, page);
console.log('wrote', out, (page.length / 1048576).toFixed(2) + 'MB');
