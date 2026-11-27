---
name: quality-signals
description: 정리된 메일(JSONL)마다 품질 신호(단어 수, 평균 단어 길이, 알파벳 단어 비율 등)를 pandas로 계산하고, 남길 메일과 버릴 메일을 정한다. "품질 필터", "쓸모없는 메일 걸러줘", "문서 단위 필터" 같은 요청에 사용한다.
---

# quality-signals: 문서 단위 품질 필터

## 언제 쓰나
- 본문 정리(S2)가 끝난 뒤, 통째로 버릴 메일을 골라야 할 때
- 기준을 바꾸면 몇 통이 달라지는지 숫자로 비교하고 싶을 때

## 입력과 출력
- 입력: `<out-dir>/s2_cleaned.jsonl`
- 출력: `<out-dir>/quality_signals.csv` (메일마다 한 줄: 신호, `keep`, `reason`), `<out-dir>/emails.jsonl` (`keep`이 True인 메일), `<out-dir>/audit_log.md`

## 단계
1. 실행한다.
   ```
   python ${CLAUDE_SKILL_DIR}/scripts/s3_quality.py --input <out-dir>/s2_cleaned.jsonl --out-dir <out-dir>
   python ${CLAUDE_SKILL_DIR}/scripts/make_report.py --out-dir <out-dir>
   ```
2. 버린 이유별 메일 수와, Gopher 기준을 그대로 썼을 때의 탈락 수를 함께 보고한다.
3. 이유마다 버린 메일 3~5통을 열어 사용자와 확인한다.

## 결정과 기준
웹 문서용 기준(Gopher)은 재기만 하고 적용하지 않는다. ward-k 메일함에서는 54%가 탈락하고 그 대부분이 "50단어 미만" 때문이다. 업무 메일은 원래 짧다.

메일용 기준 (위에서부터 확인해 처음 걸린 이유를 적는다)

| reason | 기준 | 버리는 이유 |
|---|---|---|
| `too_short` | 5단어 미만 | 내용이 없다 ("ok", "thanks") |
| `not_text` | 평균 단어 길이 10 초과 | 글이 아니다 (인코딩 덩어리, 긴 URL) |
| `mostly_numbers` | 알파벳 단어 60% 미만 또는 숫자 비율 30% 초과 | 숫자표 |
| `bulk_sender` | 보낸 주소에 광고·알림 단어 포함 | 광고, 뉴스 알림, 전사 공지 |

기준 숫자는 `scripts/s3_quality.py` 맨 위의 상수다. 바꾸면 반드시 전후 메일 수를 비교해 기록한다.

## 검증 방법
- `quality_signals.csv`의 줄 수 = 입력 메일 수
- `emails.jsonl`의 메일 수 = `keep`이 True인 줄 수
- 이유별 표본 확인. 특히 경계에 있는 메일(5~10단어, 알파벳 단어 60~70%)을 본다.

## 알려진 한계
- **무엇이 "쓸모없는지"는 목적에 따라 다르다.** 가격표 메일("Cal 02 $3.025 ...")은 `mostly_numbers`로 버려지지만, 질문에 답하는 챗봇에게는 정답일 수 있다.
- `bulk_sender`는 주소의 단어만 본다. 사람이 보낸 광고는 통과하고, 전사 공지 중 필요한 것(조직 개편 등)도 버려진다.
- 단어 수 기준은 본문 정리 결과에 달려 있다. S2에서 덜 지우면 짧은 메일이 길어 보인다.
- 영어 메일 기준이다. 불용어 목록과 알파벳 판정이 영어에 맞춰져 있다.
