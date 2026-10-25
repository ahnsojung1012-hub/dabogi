/**
 * 다시보기 채점실 — 학습 기록 저장용 Google Apps Script
 *
 * 이 스프레드시트에 시트 3개를 씁니다 (처음 실행할 때 자동으로 만들어져요).
 *   명단 : A열 반, B열 이름 (2행부터). 학생은 여기 있는 이름으로만 들어올 수 있어요.
 *   기록 : 학생 화면이 보낸 기록이 한 줄씩 쌓여요. 직접 고치지 마세요.
 *   설정 : B1 칸에 선생님 페이지 비밀번호를 적어요.
 */

var SHEET_LOG = '기록', SHEET_ROSTER = '명단', SHEET_SET = '설정';
var LOG_HEADER = ['받은 시각', '종류', '반', '이름', '시험 ID', '시험 이름', '회차', '틀린 문항', '틀린 개수', '문항 수',
  '기기 시각', '푼 시간(초)', '세션', '기기', '추가 정보'];

function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var log = ss.getSheetByName(SHEET_LOG) || ss.insertSheet(SHEET_LOG);
  if (log.getLastRow() === 0) { log.appendRow(LOG_HEADER); log.setFrozenRows(1); }
  var ro = ss.getSheetByName(SHEET_ROSTER) || ss.insertSheet(SHEET_ROSTER);
  if (ro.getLastRow() === 0) { ro.appendRow(['반', '이름']); ro.appendRow(['2-1', '홍길동(예시, 지우고 쓰세요)']); ro.setFrozenRows(1); }
  var st = ss.getSheetByName(SHEET_SET) || ss.insertSheet(SHEET_SET);
  if (st.getLastRow() === 0) { st.getRange('A1:B1').setValues([['선생님 페이지 비밀번호', '여기에 비밀번호를 적으세요']]); }
}

function clean_(s) { return String(s == null ? '' : s).replace(/\s+/g, '').normalize('NFKC'); }
function json_(obj) { return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON); }

function roster_() {
  var ro = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_ROSTER);
  if (!ro || ro.getLastRow() < 2) return [];
  return ro.getRange(2, 1, ro.getLastRow() - 1, 2).getValues()
    .filter(function (r) { return String(r[1]).trim(); })
    .map(function (r) { return { cls: String(r[0]).trim(), name: String(r[1]).trim() }; });
}
function findStudent_(cls, name) {
  var c = clean_(cls), n = clean_(name);
  var list = roster_();
  for (var i = 0; i < list.length; i++) {
    if (clean_(list[i].name) === n && (!c || clean_(list[i].cls) === c)) return list[i];
  }
  return null;
}

function appendLog_(d) {
  var who = findStudent_(d.cls, d.name);
  if (!who) return { ok: false, error: 'not_in_roster' };
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_LOG);
    if (!sh) { setup(); sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_LOG); }
    var cut = function (v, n) { return String(v == null ? '' : v).slice(0, n || 200); };
    sh.appendRow([new Date(), cut(d.ev, 20), who.cls, who.name, cut(d.examId, 40), cut(d.examTitle, 120),
      Number(d.attempt) || '', cut(d.wrong, 200), d.wrongCount === undefined ? '' : Number(d.wrongCount), Number(d.total) || '',
      d.at ? new Date(Number(d.at)) : '', Number(d.activeSec) || 0, cut(d.session, 40), cut(d.device, 40), cut(d.extra, 2000)]);
  } finally { lock.releaseLock(); }
  return { ok: true };
}

function doGet(e) {
  var p = (e && e.parameter) || {};
  try {
    if (p.action === 'check') {
      var who = findStudent_(p.cls, p.name);
      return json_(who ? { ok: true, cls: who.cls, name: who.name } : { ok: false, error: roster_().length ? 'not_in_roster' : 'empty_roster' });
    }
    if (p.action === 'log') {
      var batch = JSON.parse(p.d || '[]');
      if (!Array.isArray(batch)) batch = [batch];
      var res = batch.slice(0, 20).map(appendLog_);
      return json_({ ok: res.every(function (r) { return r.ok; }), results: res });
    }
    if (p.action === 'data') {
      var set = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_SET);
      var pw = set ? String(set.getRange('B1').getValue()) : '';
      if (!pw || pw === '여기에 비밀번호를 적으세요' || String(p.key) !== pw) return json_({ ok: false, error: 'bad_key' });
      var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_LOG);
      var rows = sh && sh.getLastRow() > 1 ? sh.getRange(2, 1, sh.getLastRow() - 1, LOG_HEADER.length).getValues() : [];
      rows = rows.map(function (r) {
        return { recv: +r[0], ev: r[1], cls: r[2], name: r[3], examId: r[4], examTitle: r[5], attempt: r[6], wrong: r[7],
          wrongCount: r[8], total: r[9], at: r[10] ? +r[10] : +r[0], activeSec: r[11], session: r[12], device: r[13], extra: r[14] };
      });
      return json_({ ok: true, roster: roster_(), rows: rows });
    }
    return json_({ ok: true, service: 'dabogi' });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  }
}

/* navigator.sendBeacon(학생이 화면을 닫을 때)용 */
function doPost(e) {
  try {
    var d = JSON.parse(e.postData.contents);
    var batch = Array.isArray(d) ? d : [d];
    batch.slice(0, 20).forEach(appendLog_);
    return json_({ ok: true });
  } catch (err) { return json_({ ok: false, error: String(err) }); }
}
