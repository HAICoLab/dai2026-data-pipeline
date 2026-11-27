"""내 결과와 정답을 비교한다. 저장소 루트에서 실행한다.

    python part1/solution/compare.py s1            # S1 문서 준비 결과 비교
    python part1/solution/compare.py s2            # S2 줄 단위 정리 결과 비교
    python part1/solution/compare.py s3            # S3 문서 단위 필터 결과 비교
    python part1/solution/compare.py s2 --show inbox/12   # 메일 한 통을 내 결과와 정답으로 나란히 보기

정답과 숫자가 다르다고 틀린 것이 아니다. 어디가 왜 다른지 메일을 열어 보고 설명할 수 있으면 된다.
"""

import argparse
import csv
import difflib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(errors="replace")

SOLUTION = Path(__file__).resolve().parent / "out"
FIELDS = ["id", "folder", "date", "from", "to", "subject", "body"]
FILES = {"s1": "s1_parsed.jsonl", "s2": "s2_cleaned.jsonl", "s3": "emails.jsonl"}

# 잔재 확인용 (느슨한 탐지)
TAG = re.compile(r"</?(?:html|body|head|br|p|div|span|font|table|tr|td|b|i|u|a|img|center)\b[^<>]*>", re.I)
QP = re.compile(r"=20[ \t]*$|=09(?!\d)", re.M)   # 줄 끝의 = 는 ===== 구분선과 구별할 수 없어 세지 않는다


def load_jsonl(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"파일이 없습니다: {path}\n이 단계를 먼저 실행하세요.")
    records = {}
    with path.open(encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            if "id" not in record:
                sys.exit(f"{path} {number}번째 줄에 'id' 필드가 없습니다. CLAUDE.md의 파일 약속을 확인하세요.")
            records[record["id"]] = record
    return records


def squash(text) -> str:
    """공백 차이는 무시하고 비교하기 위해 공백을 하나로 줄인다."""
    return " ".join(str(text or "").split())


def n_lines(records: dict) -> int:
    return sum(len([l for l in str(r.get("body", "")).splitlines() if l.strip()]) for r in records.values())


def row(label: str, mine, answer) -> None:
    mark = "" if mine == answer else "   <- 다름"
    print(f"  {label:<28}{str(mine):>12}{str(answer):>12}{mark}")


def header(title: str) -> None:
    print(f"\n{title}")
    print(f"  {'':<28}{'내 결과':>9}{'정답':>10}")


def check_fields(mine: dict) -> None:
    sample = next(iter(mine.values()))
    missing = [f for f in FIELDS if f not in sample]
    if missing:
        print(f"\n  ! 내 결과에 없는 필드: {missing}  (CLAUDE.md의 파일 약속 참고)")


def body_diff(mine: dict, answer: dict, top: int) -> None:
    common = [i for i in mine if i in answer]
    same = [i for i in common if squash(mine[i].get("body")) == squash(answer[i].get("body"))]
    print(f"\n본문이 정답과 같은 메일: {len(same):,} / {len(common):,}통")
    different = [i for i in common if i not in set(same)]
    if not different:
        return
    # 글자 수 차이가 큰 순서로 보여준다.
    different.sort(key=lambda i: -abs(len(squash(mine[i].get("body"))) - len(squash(answer[i].get("body")))))
    print(f"차이가 큰 메일 {min(top, len(different))}통 (글자 수: 내 결과 / 정답)")
    for i in different[:top]:
        a, b = str(mine[i].get("body", "")), str(answer[i].get("body", ""))
        print(f"  {i:<40} {len(a):>7,} / {len(b):>7,}")
    print(f"자세히 보려면: python part1/solution/compare.py {ARGS.stage} --show {different[0]}")


def show_one(mine: dict, answer: dict, mail_id: str) -> None:
    if mail_id not in mine or mail_id not in answer:
        where = "내 결과" if mail_id not in mine else "정답"
        sys.exit(f"{where}에 id '{mail_id}'가 없습니다. (S3에서는 걸러진 메일일 수 있습니다)")
    a = str(mine[mail_id].get("body", "")).splitlines()
    b = str(answer[mail_id].get("body", "")).splitlines()
    print(f"메일 {mail_id}   제목: {answer[mail_id].get('subject', '')}")
    print("  '-' 로 시작하는 줄: 내 결과에만 있음 / '+' 로 시작하는 줄: 정답에만 있음\n")
    diff = list(difflib.unified_diff(a, b, lineterm="", n=1))[2:]
    if not diff:
        print("  (차이 없음)")
    for line in diff[:80]:
        print("  " + line[:160])
    if len(diff) > 80:
        print(f"  ... ({len(diff) - 80}줄 더 있음)")


def compare_s1(mine: dict, answer: dict) -> None:
    header("S1 문서 준비")
    row("메일 수", f"{len(mine):,}", f"{len(answer):,}")
    row("HTML 태그가 남은 메일", sum(bool(TAG.search(str(r.get("body", "")))) for r in mine.values()),
        sum(bool(TAG.search(str(r.get("body", "")))) for r in answer.values()))
    row("QP 잔재(=20 등)가 남은 메일", sum(bool(QP.search(str(r.get("body", "")))) for r in mine.values()),
        sum(bool(QP.search(str(r.get("body", "")))) for r in answer.values()))
    row("날짜가 비어 있는 메일", sum(not r.get("date") for r in mine.values()),
        sum(not r.get("date") for r in answer.values()))
    check_fields(mine)
    common = [i for i in mine if i in answer]
    print(f"\n정답과 같은 id: {len(common):,}통" + ("" if len(common) == len(answer) else "   <- id는 원본 값을 그대로 써야 합니다"))
    for field in ("date", "from", "to", "subject"):
        same = sum(squash(mine[i].get(field)) == squash(answer[i].get(field)) for i in common)
        print(f"  {field:<8} 정답과 같음: {same:,} / {len(common):,}")
    body_diff(mine, answer, ARGS.top)


def compare_s2(mine: dict, answer: dict) -> None:
    my_s1 = load_jsonl(ARGS.mine / FILES["s1"])
    answer_s1 = load_jsonl(SOLUTION / FILES["s1"])
    header("S2 줄 단위 정리")
    row("메일 수", f"{len(mine):,}", f"{len(answer):,}")
    row("정리 전 줄 수 (빈 줄 제외)", f"{n_lines(my_s1):,}", f"{n_lines(answer_s1):,}")
    row("정리 후 줄 수", f"{n_lines(mine):,}", f"{n_lines(answer):,}")
    row("제거한 줄 수", f"{n_lines(my_s1) - n_lines(mine):,}", f"{n_lines(answer_s1) - n_lines(answer):,}")
    row("본문이 비게 된 메일", sum(not squash(r.get("body")) for r in mine.values()),
        sum(not squash(r.get("body")) for r in answer.values()))
    check_fields(mine)
    body_diff(mine, answer, ARGS.top)


def load_keep(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"파일이 없습니다: {path}")
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows or "id" not in rows[0] or "keep" not in rows[0]:
        sys.exit(f"{path}에 'id'와 'keep' 열이 있어야 합니다.")
    return {r["id"]: (r["keep"].strip().lower() in ("true", "1", "yes"), r.get("reason", "")) for r in rows}


def compare_s3(mine: dict, answer: dict) -> None:
    my_keep = load_keep(ARGS.mine / "quality_signals.csv")
    answer_keep = load_keep(SOLUTION / "quality_signals.csv")
    answer_s2 = load_jsonl(SOLUTION / FILES["s2"])
    header("S3 문서 단위 필터")
    row("판정한 메일 수", f"{len(my_keep):,}", f"{len(answer_keep):,}")
    row("남긴 메일 (keep=True)", f"{sum(k for k, _ in my_keep.values()):,}", f"{sum(k for k, _ in answer_keep.values()):,}")
    row("버린 메일 (keep=False)", f"{sum(not k for k, _ in my_keep.values()):,}", f"{sum(not k for k, _ in answer_keep.values()):,}")
    row("emails.jsonl 메일 수", f"{len(mine):,}", f"{len(answer):,}")

    common = [i for i in my_keep if i in answer_keep]
    only_me = [i for i in common if my_keep[i][0] and not answer_keep[i][0]]
    only_answer = [i for i in common if not my_keep[i][0] and answer_keep[i][0]]
    for title, ids, reason_from in (
        ("나는 남겼는데 정답은 버린 메일", only_me, answer_keep),
        ("나는 버렸는데 정답은 남긴 메일", only_answer, my_keep),
    ):
        print(f"\n{title}: {len(ids):,}통" + ("  (S2 결과가 다르면 같은 기준이라도 판정이 달라진다)" if ids else ""))
        for i in ids[: ARGS.top]:
            body = squash(answer_s2.get(i, {}).get("body"))
            print(f"  {i:<36} 버린 이유: {reason_from[i][1] or '-':<16} | 정답 본문 {len(body.split())}단어 | {body[:60]}")


def main() -> None:
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["s1", "s2", "s3"])
    ap.add_argument("--mine", type=Path, default=Path("part1/out"), help="내 결과 폴더")
    ap.add_argument("--top", type=int, default=5, help="예시로 보여줄 메일 수")
    ap.add_argument("--show", metavar="ID", help="이 id의 메일 본문을 내 결과와 정답으로 비교")
    ARGS = ap.parse_args()

    mine = load_jsonl(ARGS.mine / FILES[ARGS.stage])
    answer = load_jsonl(SOLUTION / FILES[ARGS.stage])
    if ARGS.show:
        show_one(mine, answer, ARGS.show)
        return
    {"s1": compare_s1, "s2": compare_s2, "s3": compare_s3}[ARGS.stage](mine, answer)


if __name__ == "__main__":
    main()
