# Part 1. 데이터 전처리: 사람이 쓴 글만 남기기

> 3일 전체 흐름은 [저장소 첫 페이지](../README.md#3일-동안-무엇을-하나)를 먼저 읽어 주세요. 오늘은 그 첫 단계입니다.

## 오늘 할 일, 한 문장으로

**전임자의 메일 2,611통에서 사람이 쓴 글만 남긴 깨끗한 파일을 만듭니다.**

말로는 감이 잘 오지 않으니 메일 한 통으로 먼저 보겠습니다.

## 메일 한 통으로 보기

2001년 11월, 고객사 Citizens Utilities의 Sean Breen이 Kim에게 보낸 답장입니다.
Griffith 발전소로 가는 가스 공급이 끊긴 일에 대해 Kim이 대책을 보내자, Sean이 답한 메일입니다.

### 처리 전: 원본

원본 파일 `data/raw/ward-k.jsonl`은 한 줄이 메일 한 통입니다. 이 메일은 이렇게 저장되어 있습니다.

```
{"id": "inbox/340", "folder": "inbox", "raw": "Message-ID: <26205361.1075861818646.JavaMail.evans@thyme>\r\nDate: Mon, 26 Nov 2001 ...
```

`raw` 안에 메일 원문이 통째로 들어 있습니다. 펼쳐 보면 아래와 같습니다.
**초록색(+) 줄은 남고, 빨간색(-) 줄은 지워집니다.** 너무 긴 줄은 `…`로 줄였습니다.

```diff
@@ 메일 머리말 → 날짜·보낸 사람·받는 사람·제목 4가지만 꺼내고 나머지는 버린다 (S1) @@
-Message-ID: <26205361.1075861818646.JavaMail.evans@thyme>
+Date: Mon, 26 Nov 2001 15:46:26 -0800 (PST)
+From: sbreen@czn.com
+To: houston <.ward@enron.com>, sean.breen@enron.com, e-mail <.john@enron.com>
+Subject: RE: Griffith flows
-Cc: barry.tycholiz@enron.com, mike.grigsby@enron.com, l..gay@enron.com, 
-    patti.sullivan@enron.com, shannon.groenewold@enron.com, 
-    m..tholt@enron.com, h..foster@enron.com
-Mime-Version: 1.0
-Content-Type: text/plain; charset=us-ascii
-Content-Transfer-Encoding: 7bit
-Bcc: barry.tycholiz@enron.com, mike.grigsby@enron.com, l..gay@enron.com, 
-    patti.sullivan@enron.com, shannon.groenewold@enron.com, 
-    m..tholt@enron.com, h..foster@enron.com
-X-From: "Breen, Sean" <SBreen@czn.com>@ENRON
-X-To: Ward, Kim S (Houston) </O=ENRON/OU=NA/CN=RECIPIENTS/CN=KWARD>, Breen, Sean <SBreen@czn.com …
-X-cc: Tycholiz, Barry </O=ENRON/OU=NA/CN=RECIPIENTS/CN=BTYCHOL>, Grigsby, Mike </O=ENRON/OU=NA/C …
-X-bcc: 
-X-Folder: \KWARD (Non-Privileged)\Ward, Kim S (Houston)\Inbox
-X-Origin: Ward-K
-X-FileName: KWARD (Non-Privileged).pst
@@ 본문: Sean이 직접 쓴 글 → 남긴다 @@
+Kim,
+Thank you for your attention to this matter.  Citizens is encouraged to see
+that steps are being taken and will continue to monitor the situation. Kindly
+inform me personally at the earliest possible time should cuts of any nature
+occur in the future on this contract. Thanks.
@@ 답장에 딸려 온 이전 메일 (Kim이 11/21에 보낸 메일) → 지운다 (S2) @@
------Original Message-----
-From: Ward, Kim S (Houston) [mailto:Kim.Ward@enron.com ]
-Sent: Wednesday, November 21, 2001 12:22 PM
-To: Sean Breen (E-mail); John Cogan (E-mail)
-Cc: Tycholiz, Barry; Grigsby, Mike; Gay, Randall L.; Sullivan, Patti;
-Groenewold, Shannon; Tholt, Jane M.; Foster, Chris H.
-Subject: Griffith flows
-Sean,
-Attached is our response to your request for a description of the steps
-Enron is taking to improve flows to the Griffith power plant.  Please
-let me know if you have any questions.
-Thanks,
-Kim
- <<cuts response.doc>>
@@ 면책 문구: Enron 메일마다 자동으로 붙는 법적 고지 → 지운다 (S2) @@
-**********************************************************************
-This e-mail is the property of Enron Corp. and/or its relevant affiliate and may contain confide …
-**********************************************************************
```

### 처리 후: 결과

오늘의 결과 파일 `part1/out/emails.jsonl`에서 이 메일은 이렇게 바뀝니다.

```json
{
  "id": "inbox/340",
  "folder": "inbox",
  "date": "2001-11-26T15:46:26-08:00",
  "from": "sbreen@czn.com",
  "to": "houston <.ward@enron.com>, sean.breen@enron.com, e-mail <.john@enron.com>",
  "subject": "RE: Griffith flows",
  "body": "Kim,\nThank you for your attention to this matter.  Citizens is encouraged to see that steps are being taken and will continue to monitor the situation. Kindly inform me personally at the earliest possible time should cuts of any nature occur in the future on this contract. Thanks."
}
```

42줄, 365단어였던 메일이 날짜·보낸 사람·받는 사람·제목, 그리고 48단어짜리 본문으로 바뀌었습니다.

### 무엇이 왜 사라졌나

| 사라진 부분 | 왜 지우나 | 단계 |
|---|---|---|
| 메일 머리말 대부분 (Message-ID, Cc, X-Folder …) | 메일 시스템이 붙인 관리용 정보입니다. 필요한 4가지만 칸을 나눠 꺼내 둡니다 | S1 |
| 이전 메일 (`-----Original Message-----` 아래) | Kim이 11/21에 보낸 원래 메일은 메일함에 따로 있습니다(`sent_items/771`). 남겨 두면 같은 글이 두 번 들어갑니다 | S2 |
| 첨부 파일 표시 `<<cuts response.doc>>` | 첨부 파일은 데이터에 없습니다. 이름만 남은 흔적입니다 | S2 |
| 면책 문구 | 이 메일함에서만 100통 넘게 똑같이 붙어 있는 법적 고지입니다. 내용과 상관없습니다 | S2 |

### 통째로 버리는 메일도 있다

글을 다듬는 것과 별개로, 남겨 둘 가치가 없는 메일은 통째로 버립니다(S3).

| 메일 | 본문 | 버리는 이유 |
|---|---|---|
| `deleted_items/311` | ARE YOU TIRED OF SLOW INTERNET CONNECTIONS? … CLICK HERE NOW! | 광고 |
| `sent_items/516` | hello | 내용이 없다 |

### 메일함 전체로 보면

| | 처리 전 | 처리 후 |
|---|---|---|
| 메일 수 | 2,611통 | 2,265통 |
| 본문 줄 수 (빈 줄 제외) | 65,995줄 | 27,815줄 |

본문의 절반 넘게가 사람이 쓴 글이 아니었습니다.
위 숫자는 교수자 정답 기준입니다. 여러분의 결과는 조금 다를 수 있고, **어디가 왜 다른지가 오늘의 토론거리**입니다.

## 이 일을 세 단계로 나눈다

위 예시에서 본 일을 세 단계로 나누어 합니다. 각 단계는 LLM 학습 데이터를 만들 때 웹 문서에 하는 일과 짝이 맞습니다.

| 단계 | 메일함에서 하는 일 | 위 예시에서는 | 웹 문서에서는 |
|---|---|---|---|
| S1 문서 준비 | 머리말과 본문 나누기, 깨진 인코딩 복원, HTML 메일 정리 | 머리말에서 4가지만 꺼냄 | HTML에서 글만 꺼내기 |
| S2 줄 단위 정리 | 이전 메일 인용, 전달 머리말, 면책 문구 지우기 | 이전 메일과 면책 문구 삭제 | 메뉴·버튼 같은 줄 지우기 (C4) |
| S3 문서 단위 필터 | 내용 없는 메일, 숫자표, 광고 버리기 | (이 메일은 남김) | 품질 낮은 문서 버리기 (Gopher) |

그 전에 **S0 진단**이 있습니다. 처음 보는 데이터에서 무엇을 지워야 하는지는 미리 알 수 없습니다. 2,611통을 숫자로 훑어보고 찾아냅니다.

## 오늘 배우는 것

1. 처음 보는 데이터에 어떤 전처리가 필요한지 **진단**하는 방법
2. 웹 문서를 정제하는 표준 절차를 메일에 적용하는 방법
3. 남이 만든 규칙을 그대로 쓰면 안 되는 이유를 **숫자로 확인**하는 방법
4. 오늘의 결정을 **Skill**로 저장해 다음 수업에서 다시 쓰는 방법

## 진행 방식

단계마다 **시연 → 따라 하기 → 정답과 비교**를 반복합니다. 평가는 없습니다.

1. 교수자가 문제를 보여 주고 **무엇을 할지(결정)** 말합니다.
2. 여러분이 **빈칸 틀을 내 말로 채워** Claude Code에 시킵니다.
3. Claude가 만든 코드를 **설명해 달라고 해서 읽고**, 결과를 숫자와 메일로 확인합니다.
4. `compare.py`로 내 결과와 정답을 비교합니다.

3분 넘게 막히면 각 단계의 "막히면 펼쳐 보기"에 있는 완성된 요청 문구를 써도 됩니다.

### 좋은 지시의 6가지 습관

| 습관 | 이렇게 쓴다 |
|---|---|
| 1. 목적을 먼저 말한다 | "목적은 ~야" |
| 2. 데이터를 가리킨다 | "`part1/out/s1_parsed.jsonl`의 실제 메일에서 찾아서 id와 함께" |
| 3. 바로 하지 말고 먼저 보여 달라고 한다 | "데이터에는 아직 적용하지 마", "먼저 ~를 보여줘" |
| 4. 숫자로 보고하게 한다 | "몇 통, 몇 줄이 바뀌었는지 숫자로" |
| 5. 표본으로 확인한다 | "바뀐 메일 3통을 전후로 보여줘" |
| 6. 설명을 요구한다 | "이 정규식을 조각마다 설명해줘", "이 pandas 코드를 한 줄씩 설명해줘" |

"알아서 다 해줘"라고 하면 Claude가 결정을 대신 내립니다. 그 결정이 맞는지 여러분은 알 수 없습니다.

정답과 숫자가 다르다고 틀린 것이 아닙니다. Claude Code는 사람마다 다른 코드를 씁니다.
**어디가 왜 다른지 메일을 열어 보고 설명할 수 있으면** 오늘의 목표는 달성입니다.

## 시작하기

```
git pull
python check_env.py
claude
```

| 시간 | 내용 |
|---|---|
| 0–5분 | 상황 설명 |
| 5–12분 | S0 진단 (교수자 시연) |
| 12–18분 | S1 문서 준비 (가볍게) |
| 18–33분 | S2 줄 단위 정리 (정규식) |
| 33–46분 | S3 문서 단위 필터 (pandas) |
| 46–55분 | Skill 저장 |
| 55–60분 | 정리 |

뒤처졌다면 기다리지 말고 **따라잡기** 명령으로 정답 결과를 받아 다음 단계부터 합류하세요.

---

## S0. 진단 (교수자 시연)

어떤 전처리가 필요한지는 데이터를 봐야 알 수 있습니다. 2,611통을 눈으로 읽는 대신 세 가지를 뽑아 봅니다.

- **여러 메일에 반복되는 줄**: 사람이 매번 새로 쓴 글이라면 같은 줄이 수백 통에 나올 수 없습니다.
- **특수 문자열의 빈도**: `-----Original Message-----`, `=20`, `<TABLE>` 같은 것이 몇 통에 있는지.
- **길이가 극단적인 메일**: 가장 짧은 메일과 가장 긴 메일.

교수자의 진단 결과는 `part1/solution/out/report.html`을 브라우저로 열면 볼 수 있습니다.

<details>
<summary>직접 해 보고 싶다면: 요청 문구</summary>

```
data/raw/ward-k.jsonl 은 전임자의 메일함이야. 아직 아무것도 고치지 말고 진단만 해줘.
part1/src/s0_profile.py 를 만들어서 다음을 뽑아줘.
1) 여러 메일에 반복되는 줄 상위 30개 (그 줄이 들어 있는 메일 수 기준)
2) 답장 인용, 전달, 인코딩 잔재, HTML 같은 특수 문자열이 들어 있는 메일 수
3) 본문 단어 수 분포, 가장 긴 메일과 가장 짧은 메일 5통씩
결과를 part1/out/report.html 에 표와 그래프로 정리하고, 어떤 전처리가 필요해 보이는지 표로 제안해줘.
```
</details>

### 진단에서 찾은 것

| 발견 | 근거 | 처리 |
|---|---|---|
| 줄바꿈이 두 가지로 섞여 있음 (`\r\n`과 `\n`) | 2,611통 전부 | S1 |
| 인코딩 잔재 `=20`, `=09`, 줄 끝의 `=` | 약 100통 | S1 |
| HTML 메일 | 26통, 태그 약 3,000개 | S1 |
| 답장에 딸려 온 이전 메일 | `-----Original Message-----` 837통 | S2 |
| 전달 머리말 | `Forwarded by` 267통 | S2 |
| 구분선 없이 딸려 온 이전 메일 (Lotus 방식) | 본문 안의 `To:` 줄 | S2 |
| 면책 문구 | 103통 | S2 |
| Lotus 주소 `Kim Ward/HOU/ECT@ECT` | 203통 | S2 |
| 내용이 거의 없는 메일 | 10단어 미만 151통 | S3 |
| 광고·뉴스 알림 | CNN, 여행사, 전사 공지 | S3 |
| 같은 메일이 여러 폴더에 | 2,611통 중 본문이 다른 것은 2,003통 | Part 2 |

### 하지 않는 것

텍스트 전처리라고 하면 흔히 나오는 **소문자로 바꾸기, 불용어 제거, 어간 추출**은 하지 않습니다.
단어 수를 세는 옛 방식(BoW, TF-IDF)에는 도움이 되지만, 사람과 LLM이 읽을 글에서는 정보만 잃습니다.
Claude Code가 제안하더라도 "왜 필요한가"를 되물어 보세요.

---

## S1. 문서 준비

메일 원문을 날짜·보낸 사람·받는 사람·제목·본문으로 나눕니다. 기술적인 단계라 **아래 요청 문구를 그대로 써도 됩니다.**

**요청 문구**

```
S1 문서 준비를 해줘. CLAUDE.md의 파일 약속대로 part1/src/s1_parse.py 를 만들고 실행해.
- 메일 원문(raw)에서 날짜, 보낸 사람, 받는 사람, 제목, 본문을 꺼낸다.
- 줄바꿈을 \n 으로 통일한다.
- quoted-printable 잔재(=20, =09, 줄 끝의 =)를 되돌린다. 정규식으로 지우는 방법과, 메일 머리말을 보고 표준 디코더를 쓰는 방법 중 어느 쪽이 안전한지 숫자로 비교해서 정해줘.
- HTML 메일은 태그를 지우고 글만 남긴다. 태그 정규식은 part1/src/patterns.py 의 PATTERNS["html_tag"] 로 만들고, python part1/tests/test_regex.py 를 먼저 통과시킨 뒤 적용해.
끝나면 audit_log.md 에 기록하고 report.html 에 S1 구역을 넣어줘.
```

**정답과 비교**

```
python part1/solution/compare.py s1
```

| 확인할 것 | 정답 |
|---|---|
| 메일 수 | 2,611 → 2,611 (한 통도 버리지 않음) |
| quoted-printable을 되돌린 메일 | 99통 |
| HTML 태그를 지운 메일 | 26통 |

**생각해 볼 것**

- `<.*?>`로 태그를 지우면 `<kim.ward@enron.com>`은 어떻게 될까요? `test_regex.py`가 잡아 줍니다.
- `=20$|=\n|=09`로 잔재를 지우면 `=====` 구분선은 어떻게 될까요? 정답에서는 38통 209군데가 잘못 지워집니다.
- 날짜가 1979년이나 1980년인 메일이 있습니다. 어떻게 생긴 걸까요?

**따라잡기**: `python part1/solution/catch_up.py s1`

---

## S2. 줄 단위 정리

웹 문서 정제(C4)에서는 "마침표로 끝나지 않는 줄"을 지웁니다. 메뉴나 버튼 글자를 걸러 내는 규칙입니다.
메일에서는 무엇이 "쓸모없는 줄"일까요? 그리고 C4의 규칙을 메일에 그대로 쓰면 어떻게 될까요?

**교수자가 정한 것**: 답장할 때 딸려 온 이전 메일은 지운다. 전달받은 메일은 구분선과 머리말만 지우고 내용은 남긴다. 면책 문구는 지운다. Lotus 주소는 이름만 남긴다.

**① 사례 보기: 빈칸을 채워 시키세요**

```
S2를 하려고 해. 목적은 ______________________________.
지울 것: ______________________ / 남길 것: ______________________
part1/out/s1_parsed.jsonl 의 실제 메일에서 해당하는 부분을 찾아 메일 id와 함께 3통만 보여줘.
그다음 정규식을 part1/src/patterns.py 에 만들고 python part1/tests/test_regex.py 결과를 보여줘.
데이터에는 아직 적용하지 마.
```

3번째 줄을 빼면 Claude가 우리 데이터를 보지 않고 Gmail 같은 다른 메일 형식으로 예시를 지어냅니다.

**② 예측해 보기**: `<.*?>`라는 정규식은 아래 문자열에서 무엇을 잡을까요? 먼저 손으로 적고, Claude에게 확인시켜 보세요.

| 문자열 | 내 예측 |
|---|---|
| `<b>hi</b>` | |
| `<kim.ward@enron.com>` | |
| `a < b and c > d` | |
| `<<budget.xls>>` | |

**③ 읽기**: Claude가 만든 정규식을 설명해 달라고 하세요.

```
patterns.py 의 quote_separator 정규식을 조각마다 한국어로 설명해줘.
```

| 기호 | 뜻 | 예 |
|---|---|---|
| `^`, `$` | 줄의 시작, 줄의 끝 | `^>` = `>`로 시작하는 줄 |
| `-{3,}` | 앞 글자가 3번 이상 | `-----` |
| `.*?` | 아무 글자나, 가능한 짧게 | `<.*?>` |
| `[ \t>]*` | 괄호 안 글자 중 아무거나 0번 이상 | 앞의 공백이나 `>` |
| `(?:A\|B)` | A 또는 B | `(?:html\|body)` |

**④ 적용하기**

```
이제 part1/src/s2_clean.py 를 만들어서 적용해줘. 규칙별로 지운 줄 수를 숫자로 보여주고, 전후가 가장 많이 달라진 메일 3통을 보여줘.
그리고 적용은 하지 말고 재기만 해줘: C4의 '마침표·물음표·느낌표·따옴표로 끝나지 않는 줄 삭제' 규칙을 썼다면 몇 % 줄이 지워지고 메일 몇 통이 통째로 비는지.
```

Claude가 "이것도 지울까요?"라고 물으면, 그 판단은 여러분 몫입니다.

<details>
<summary>막히면 펼쳐 보기: 완성된 요청 문구</summary>

```
S2 줄 단위 정리를 해줘. part1/src/s2_clean.py 를 만들어.
part1/out/s1_parsed.jsonl 의 실제 메일에서 지울 부분과 남길 부분의 예를 먼저 3통 보여줘.
그다음 part1/src/patterns.py 에 quote_separator, forward_header, disclaimer, lotus_address 패턴을 넣고
python part1/tests/test_regex.py 에서 실패가 0건이 되게 한 다음에 데이터에 적용해.
- 답장에 딸려 온 이전 메일(-----Original Message----- 이후)은 지운다.
- 전달 메일(---- Forwarded by ... ----)은 구분선과 그 아래 머리말(To, cc, Subject 줄)만 지우고, 전달된 내용은 남긴다.
- 구분선 앞에 직접 쓴 글이 3단어 미만이면 전달로 보고, 바로 아래 메일 한 통은 남긴다.
- 면책 문구 블록과 > 로 시작하는 인용 줄을 지운다.
- Lotus 주소는 이름만 남긴다. (Kim Ward/HOU/ECT@ECT → Kim Ward)
그리고 적용하지는 말고 재기만 해줘: C4의 '마침표·물음표·느낌표·따옴표로 끝나지 않는 줄 삭제' 규칙을 썼다면 남은 줄의 몇 %가 지워지고 메일 몇 통이 통째로 비는지.
규칙별로 지운 줄 수를 audit_log.md 와 report.html 에 넣어줘.
```
</details>

**정답과 비교**

```
python part1/solution/compare.py s2
python part1/solution/compare.py s2 --show all_documents/111
```

| 확인할 것 | 정답 |
|---|---|
| 줄 수 (빈 줄 제외) | 65,995 → 27,815 (58% 제거) |
| 전달만 한 메일로 판단한 것 | 145통 |
| 정리 후 본문이 빈 메일 | 28통 |
| C4 종결부호 규칙을 썼다면 | 남은 줄의 74%가 지워지고, 메일 13%가 통째로 빔 |

**생각해 볼 것**

- 답장 인용은 지우고 전달 내용은 남겼습니다. 왜 다르게 다룰까요?
- `_sent_mail/11`에는 `-----Original Message-----`가 없는데도 이전 메일이 딸려 있습니다. 내 결과는 이것을 지웠나요?
- 종결부호 규칙은 메일의 어떤 줄을 지울까요? ("Thanks,", "Kim", 짧은 답장 …)

**따라잡기**: `python part1/solution/catch_up.py s2`

---

## S3. 문서 단위 필터

이번에는 줄이 아니라 메일을 통째로 남길지 버릴지 정합니다.
웹 문서 정제(Gopher)의 기준은 "50단어 이상, 평균 단어 길이 3~10, 알파벳이 들어간 단어 80% 이상, 흔한 영어 단어 2개 이상"입니다.

**교수자가 정한 것**: Gopher 웹 기준은 재기만 한다. 메일용 기준으로 버린다. 5단어 미만, 평균 단어 길이 10 초과, 알파벳 단어 60% 미만 또는 숫자 30% 초과, 광고·알림 주소.

**① 분포부터 보기**

```
S3를 하려고 해. part1/out/s2_cleaned.jsonl 에서 메일마다 단어 수를 세서 pandas 표로 만들고, 단어 수 분포를 보여줘. 아직 아무것도 버리지 마.
```
```
0~5단어 메일 5통과 1000단어 넘는 메일 3통을 보여줘.
```

**② 재고, 정하기: 빈칸을 채워 시키세요**

```
part1/src/s3_quality.py 를 pandas로 만들어서 품질 신호를 part1/out/quality_signals.csv 로 저장해줘: n_words, mean_word_len, alpha_word_ratio, digit_ratio, n_stopwords.
먼저 Gopher 웹 기준(50단어 이상, 평균 단어 길이 3~10, 알파벳 단어 80% 이상, 불용어 2개 이상)으로는 몇 통이 탈락하는지 재기만 해줘.
그다음 메일용 기준으로 keep 과 reason 을 정하고 남긴 메일을 part1/out/emails.jsonl 로 저장해줘. 기준: ______________________________
```

**③ 읽기**: Claude가 만든 pandas 코드를 설명해 달라고 하세요.

```
keep 을 정하는 pandas 코드만 보여주고 한 줄씩 설명해줘.
```

| 코드 | 뜻 |
|---|---|
| `df["n_words"].describe()` | 분포 요약 |
| `(df["n_words"] < 5).sum()` | 조건에 맞는 개수 |
| `df[df["n_words"] < 5]` | 조건에 맞는 행만 |
| `df["reason"].value_counts()` | 종류별 개수 |
| `df.groupby("reason")["n_words"].median()` | 그룹별 요약 |

**④ 기준 바꿔 보기**

```
too_short 기준을 5단어에서 10단어로 바꾸면 몇 통이 더 빠져? 그 메일 5통을 보여줘.
```

<details>
<summary>막히면 펼쳐 보기: 완성된 요청 문구</summary>

```
S3 문서 단위 필터를 해줘. part1/src/s3_quality.py 를 pandas로 만들어.
1) 메일마다 품질 신호를 계산해: n_words, mean_word_len, symbol_ratio(단어 수 대비 #과 말줄임표 수), alpha_word_ratio(알파벳이 들어간 단어의 비율), n_stopwords(the, be, to, of, and, that, have, with 중 몇 가지가 나오는지), digit_ratio(공백을 뺀 글자 중 숫자의 비율)
2) 적용하지는 말고 재기만 해: Gopher의 웹 문서 기준(50~100,000단어, 평균 단어 길이 3~10, symbol_ratio 0.1 이하, alpha_word_ratio 0.8 이상, 불용어 2가지 이상)을 그대로 쓰면 규칙별로 몇 통이 탈락하는지.
3) 메일용 기준으로 keep 을 정해. 위에서부터 확인해서 처음 걸린 이유를 reason 에 적어.
   - too_short: 5단어 미만
   - not_text: 평균 단어 길이 10 초과
   - mostly_numbers: alpha_word_ratio 0.6 미만 또는 digit_ratio 0.3 초과
   - bulk_sender: 보낸 주소에 announcement, no.address, noreply, no-reply, administrator, deals, news, lists., reply, offer, promo, alert, weather, travelocity, milespree, update, customer, member, unsubscribe, vacations 중 하나가 들어 있음
quality_signals.csv 와 emails.jsonl 을 만들고, 단어 수 분포 그래프에 두 기준(50단어, 5단어)을 선으로 그려서 report.html 에 넣어줘.
```
</details>

**정답과 비교**

```
python part1/solution/compare.py s3
```

| 확인할 것 | 정답 |
|---|---|
| Gopher 기준을 그대로 썼다면 | 1,405통(54%) 탈락. 그중 1,367통이 "50단어 미만" |
| 메일용 기준으로 남긴 메일 | 2,265통 |
| 버린 메일 | 346통 (too_short 167, bulk_sender 156, mostly_numbers 13, not_text 10) |

**생각해 볼 것**

- "Dan Hyvl - we sent them a draft two/three weeks ago." 는 11단어입니다. 버려도 될까요?
- `sent_items/329`는 가격표라서 `mostly_numbers`로 버려졌습니다. 후임자가 "2002년 가격 제안이 얼마였지?"라고 묻는다면요?
- 웹 문서용 기준은 **LLM을 학습시킬 글**을 고르려고 만든 것입니다. 우리는 **질문에 답할 자료**를 고르고 있습니다. 무엇이 달라져야 할까요?

**따라잡기**: `python part1/solution/catch_up.py s3`

---

## Skill 저장

오늘 내린 결정은 다음 수업에서 다른 메일함에 그대로 다시 씁니다. 코드만 남기면 "왜 그렇게 했는지"가 사라집니다.
Skill은 **절차 + 결정과 기준 + 검증 방법 + 알려진 한계**를 Claude Code가 다시 읽을 수 있게 적어 둔 문서입니다.

S2와 S3에서 내린 결정을 내 말로 한 줄씩 적어 넣으세요. 예시를 베끼면 의미가 없습니다.

```
오늘 만든 것을 Skill 2개로 저장해줘: regex-cleaning, quality-signals.
part1/solution/skills/ 의 SKILL.md 예시와 같은 형식으로 .claude/skills/<이름>/SKILL.md 를 쓰고 내 part1/src 스크립트를 scripts/ 로 복사해. 다른 메일함에도 쓸 수 있게 입력 파일과 출력 폴더는 인자로 받아야 해.
'결정과 기준' 칸에는 아래 내 결정을 넣어줘:
- ______________________________
- ______________________________
'알려진 한계' 칸에는 정답과 달랐던 점을 넣어줘: ______________________________
```

저장한 뒤 `.claude/skills/regex-cleaning/SKILL.md`를 열어 두 칸을 직접 읽어 보세요.

- **결정과 기준**: 내가 설명할 수 있는 내용인가요?
- **알려진 한계**: 오늘 정답과 달랐던 지점이 적혀 있나요?

---

## 정리

- 전처리는 정해진 레시피가 아니라 **목적과 데이터를 보고 내리는 결정**입니다.
- 남이 만든 규칙은 그대로 쓰기 전에 **내 데이터에서 무엇을 지우는지 재 봅니다**. 오늘 두 번 쟀습니다(종결부호 규칙 74%, 50단어 규칙 54%).
- 코드는 Claude Code가 썼지만, **기준을 정하고 결과를 확인한 것은 여러분**입니다.

오늘의 결과물 `part1/out/emails.jsonl`은 Part 2의 입력입니다. 같은 메일이 여러 폴더에 들어 있는 문제는 Part 2에서 다룹니다.

## 더 해 보기 (선택)

- **개인정보 가리기**: `patterns.py`에 `email`, `phone` 패턴을 넣어 테스트를 통과시키고, 본문의 이메일 주소와 전화번호를 `[EMAIL]`, `[PHONE]`으로 바꿔 보세요. 몇 건이 바뀌나요? 놓친 것은 무엇인가요?
- **진단 Skill 만들기**: S0 진단을 직접 해 보고 `data-profiling` Skill로 저장해 보세요.
