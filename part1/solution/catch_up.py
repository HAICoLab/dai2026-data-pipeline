"""따라잡기: 정답 결과를 내 결과 폴더(part1/out)로 복사해 다음 단계부터 합류한다.

    python part1/solution/catch_up.py s1     # S1까지의 정답 결과를 복사 → S2부터 시작
    python part1/solution/catch_up.py s2     # S2까지 복사 → S3부터 시작
    python part1/solution/catch_up.py s3     # 전부 복사

이미 있는 내 파일은 같은 이름이면 덮어쓴다.
"""

import shutil
import sys
from pathlib import Path

SOLUTION = Path(__file__).resolve().parent / "out"
MINE = Path("part1/out")
FILES = {
    "s1": ["s1_parsed.jsonl"],
    "s2": ["s1_parsed.jsonl", "s2_cleaned.jsonl"],
    "s3": ["s1_parsed.jsonl", "s2_cleaned.jsonl", "quality_signals.csv", "emails.jsonl"],
}

if len(sys.argv) != 2 or sys.argv[1] not in FILES:
    sys.exit("사용법: python part1/solution/catch_up.py s1|s2|s3")

MINE.mkdir(parents=True, exist_ok=True)
for name in FILES[sys.argv[1]]:
    shutil.copy(SOLUTION / name, MINE / name)
    print(f"복사: {SOLUTION / name} -> {MINE / name}")
print("완료. 다음 단계부터 이어서 하세요.")
