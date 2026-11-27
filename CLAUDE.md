# DAI 2026 데이터 파이프라인 실습

서강대 "AI를 위한 데이터분석" 실습 저장소다. 사용자는 비전공 학부생이다.
설명은 한국어로 쉽게 하고, 코드에는 짧은 한국어 주석을 단다. 무엇을 왜 했는지와 결과 숫자를 함께 알려준다.

## 규칙

1. `data/raw/`는 절대 수정하지 않는다.
2. 메일 데이터를 직접 통째로 읽지 않는다. 스크립트로 처리하고, 눈으로 확인할 때는 한 번에 5통 이하만 출력한다.
3. 단계가 끝날 때마다 `part1/out/audit_log.md`에 입력 건수, 출력 건수, 제거 건수와 사유를 덧붙인다.
4. 파일은 항상 `encoding="utf-8"`을 명시해서 열고 쓴다.
5. 정규식은 `part1/src/patterns.py`에 모으고, `python part1/tests/test_regex.py`를 통과시킨 뒤에 데이터에 적용한다.
6. 표 계산은 pandas로 한다.
7. 결과 확인용 표와 그래프는 `part1/out/report.html` 하나에 모은다. 인터넷 없이 열리도록 그림은 파일 안에 넣는다.
8. `part1/solution/`은 사용자가 정답을 보자고 하기 전에는 읽거나 베끼지 않는다. `compare.py` 실행은 언제든 해도 된다.
9. `CLAUDE.md`, `README.md`, `part*/README.md`, `part*/tests/`, `part*/solution/`은 수정하지 않는다. git commit과 push는 하지 않는다.
10. `requirements.txt`에 없는 패키지가 필요하면 설치하기 전에 사용자에게 묻는다.

## 파일 약속 (Part 1)

스크립트는 `part1/src/`에 단계마다 하나씩 만든다. 입력·출력 경로는 인자로 받고 기본값은 아래와 같다.
다른 메일함에도 그대로 쓸 수 있어야 하므로 직원 이름이나 경로를 코드 안에 고정하지 않는다.

| 단계 | 스크립트 | 입력 | 출력 |
|---|---|---|---|
| S1 문서 준비 | `s1_parse.py` | `data/raw/ward-k.jsonl` | `part1/out/s1_parsed.jsonl` |
| S2 줄 단위 정리 | `s2_clean.py` | `s1_parsed.jsonl` | `part1/out/s2_cleaned.jsonl` |
| S3 문서 단위 필터 | `s3_quality.py` | `s2_cleaned.jsonl` | `part1/out/quality_signals.csv`, `part1/out/emails.jsonl` |

필드 이름은 정확히 지킨다. 정답 비교와 다음 수업이 이 이름에 의존한다.

- 원본 `data/raw/*.jsonl`: `id`, `folder`, `raw` (메일 원문 전체)
- `s1_parsed.jsonl`, `s2_cleaned.jsonl`, `emails.jsonl`: `id`, `folder`, `date`, `from`, `to`, `subject`, `body`
  - `id`는 원본의 값을 그대로 쓴다. `date`는 ISO 8601 문자열, 없으면 빈 문자열.
  - S1은 메일을 버리지 않는다. 입력과 출력의 메일 수가 같아야 한다.
  - S2는 `body`만 바꾼다. 메일 수는 그대로다.
- `quality_signals.csv`: 메일마다 한 줄. `id`, 신호 열들, `keep`(True/False), `reason`(버린 이유)
- `emails.jsonl`: `keep`이 True인 메일만.

## 정답과 비교

```
python part1/solution/compare.py s1
python part1/solution/compare.py s2
python part1/solution/compare.py s3
```
