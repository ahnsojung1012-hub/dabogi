# 다시보기 채점실 — 학생용 시험 페이지

학원 학생들이 휴대폰으로 여는 시험 페이지 모음입니다. 사이트 주소: https://ahnsojung1012-hub.github.io/dabogi/

## 새 시험 링크를 만드는 방법 (Claude가 하는 작업)
1. 선생님의 claude.ai 아티팩트 "다시보기 채점실"(선생님 화면)을 Artifact read로 읽고, `<script type="application/json" id="state">` 안의 JSON을 state.json으로 저장한다.
2. `node tools/make_student.js state.json --list` 로 시험 id를 확인한다.
3. `node tools/make_student.js state.json <시험id> <영문-파일이름>.html` 로 학생용 페이지를 만든다. 파일 이름은 짧은 영문/숫자(예: 2-3-linear-eq.html).
4. 커밋하고 main에 푸시하면 1~2분 뒤 `https://ahnsojung1012-hub.github.io/dabogi/<파일이름>.html` 에서 열린다.
5. 시험을 지울 때는 해당 html 파일을 삭제하고 푸시한다.

학생용 페이지에는 정답이 해시로, AI 오답 분석은 모든 정답으로만 풀리는 암호로 들어 있다. 시험지 이미지는 공개된다.
