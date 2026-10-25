# 다시보기 채점실 — 학생용 시험 페이지

학원 학생들이 휴대폰으로 여는 시험 페이지 모음입니다. 사이트 주소: https://ahnsojung1012-hub.github.io/dabogi/

## 새 시험 링크를 만드는 방법 (Claude가 하는 작업)
1. 선생님의 claude.ai 아티팩트 "다시보기 채점실"(선생님 화면)을 Artifact read로 읽고, `<script type="application/json" id="state">` 안의 JSON을 state.json으로 저장한다.
2. `node tools/make_student.js state.json --list` 로 시험 id를 확인한다.
3. `node tools/make_student.js state.json <시험id> <영문-파일이름>.html` 로 학생용 페이지를 만든다. 파일 이름은 짧은 영문/숫자(예: 2-3-linear-eq.html).
4. 커밋하고 main에 푸시하면 1~2분 뒤 `https://ahnsojung1012-hub.github.io/dabogi/<파일이름>.html` 에서 열린다.
5. `tools/pages.json`에 `"파일이름.html": "시험id"`를 추가한다. 시험을 지울 때는 html 파일과 pages.json 항목을 지우고 푸시한다.
6. 템플릿이 바뀌면 `sh tools/build_all.sh state.json`으로 모든 학생 페이지와 teacher.html을 다시 만든다. 링크 끝에 ?v=숫자를 붙여 캐시를 건너뛰게 안내한다.

## 학습 기록 (Google 스프레드시트)
- `apps-script/Code.gs`를 선생님 스프레드시트의 Apps Script에 붙여 넣고 웹 앱(실행: 나, 액세스: 모든 사용자)으로 배포한다.
- 배포 주소(…/exec)를 `tools/config.json`의 `endpoint`에 넣고 build_all.sh를 실행하면 학생 페이지가 기록을 보내고, teacher.html(선생님 기록 페이지)이 비밀번호(설정 시트 B1)로 기록을 불러온다.
- 학생은 명단 시트(A열 반, B열 이름)에 있는 이름으로만 기록할 수 있다. 학생 화면의 반·이름 선택 목록은 `tools/roster.json`에서 오므로, 명단이 바뀌면 시트와 roster.json을 둘 다 고치고 build_all.sh를 다시 실행한다.

학생용 페이지에는 정답이 해시로, AI 오답 분석은 모든 정답으로만 풀리는 암호로 들어 있다. 시험지 이미지는 공개된다.

## 학년별 시험 목록 (index.html)
- 학생에게는 사이트 첫 주소(https://ahnsojung1012-hub.github.io/dabogi/) 하나만 보낸다. 반·이름을 고르면 그 학년 시험만 보인다.
- 학년은 반 이름 앞 숫자(7=중1, 8=중2, 9=중3). 시험 학년은 `tools/pages.json`의 `grade`(또는 선생님 화면에서 고른 학년)로 정한다.
- 다른 학년 시험 링크를 직접 열면 첫 주소로 돌려보낸다. build_all.sh가 index.html도 다시 만든다.
