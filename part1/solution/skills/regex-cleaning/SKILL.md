---
name: regex-cleaning
description: 메일함 JSONL을 파싱하고(S1) 본문에서 인용, 전달 머리말, 면책 문구 같은 줄을 정규식으로 걷어낸다(S2). "메일 파싱", "본문 정리", "인용 제거", "정규식으로 정리" 같은 요청에 사용한다. 정규식은 반드시 테스트를 통과시킨 뒤 적용한다.
---

# regex-cleaning: 문서 준비와 줄 단위 정리

## 언제 쓰나
- 메일 원문(JSONL)을 날짜·보낸 사람·제목·본문으로 나누어야 할 때
- 본문에서 메일을 쓴 사람이 쓰지 않은 줄을 걷어내야 할 때

## 입력과 출력
- 입력: 메일함 JSONL (`id`, `folder`, `raw`)
- 출력: `<out-dir>/s1_parsed.jsonl`, `<out-dir>/s2_cleaned.jsonl` (`id`, `folder`, `date`, `from`, `to`, `subject`, `body`), `<out-dir>/audit_log.md`
- 두 단계 모두 메일을 버리지 않는다. 입력과 출력의 메일 수가 같아야 한다.

## 단계
1. 정규식을 먼저 테스트한다. 실패가 0건이어야 다음으로 간다.
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/test_regex.py --patterns ${CLAUDE_SKILL_DIR}/scripts/patterns.py
   ```
2. S1 문서 준비를 실행한다.
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/s1_parse.py --input data/raw/<메일함>.jsonl --out-dir <out-dir>
   ```
3. S2 줄 단위 정리를 실행한다.
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/s2_clean.py --input <out-dir>/s1_parsed.jsonl --out-dir <out-dir>
   ```
4. `audit_log.md`의 숫자를 사용자에게 요약하고, 본문이 비게 된 메일 3통을 열어 정말 비어야 하는지 확인한다.

## 결정과 기준
- **인코딩 잔재(`=20`, `=09`, 줄 끝의 `=`)는 정규식으로 지우지 않는다.** 메일 머리말의 `Content-Transfer-Encoding`이 quoted-printable인 메일만 표준 디코더로 되돌린다. 정규식은 `=====` 구분선과 `hspace=20`까지 망가뜨린다(ward-k 메일함에서 38통 209군데).
- **HTML 태그는 알려진 태그 이름만 지운다.** `<.*?>`는 `<kim.ward@enron.com>`과 `a < b and c > d`도 지운다.
- **답장 인용은 지운다.** `-----Original Message-----` 이후, 그리고 Lotus 방식 머리말(`이름 / 날짜 / To: / cc: / Subject:`) 이후를 잘라낸다.
- **전달 내용은 남긴다.** `---- Forwarded by ... ----` 구분선과 그 아래 머리말만 지운다.
- **구분선 앞에 쓴 글이 3단어 미만이면 전달로 본다.** 바로 아래 메일 한 통은 남기고 그다음부터 자른다.
- Lotus 주소는 이름만 남긴다(`Kim Ward/HOU/ECT@ECT` → `Kim Ward`).
- **C4의 종결부호 규칙은 쓰지 않는다.** ward-k 메일함에서 남은 줄의 74%가 지워지고 메일 13%가 통째로 빈다.

## 검증 방법
- 정규식 테스트: 실패 0건. 사례를 추가하려면 `scripts/regex_cases.json`에 넣는다.
- 메일 수: 입력 = S1 출력 = S2 출력
- S2 결과에 `Original Message`, `Forwarded by`가 남은 메일 수를 세어 본다. 0에 가까워야 한다.
- 정리 전후의 글자 수 차이가 가장 큰 메일 5통을 열어 지나치게 지우지 않았는지 본다.

## 알려진 한계
- Lotus 방식 답장은 구분선이 없어 `To:` 줄을 단서로 찾는다. 본문이 우연히 `To:`와 `Subject:`로 시작하면 머리말로 오해한다.
- 전달 메일 안에 다시 전달이 들어 있으면 안쪽 머리말(`Subject:` 줄 등)이 남는다.
- Lotus 주소 정규식은 이름 앞의 대문자 단어까지 잡는다(`Please Call Kim Ward/HOU/ECT@ECT`).
- 서명(이름, 전화번호)은 지우지 않는다.
- `don?t`처럼 원본에서 이미 깨진 문자는 복구할 수 없다.
- Outlook과 Lotus Notes 형식의 영어 메일 기준이다.
