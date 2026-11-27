"""Enron maildir 전체에서 직원별 통계를 내어 실습용 메일함을 고르기 위한 스크립트.

교수자 PC에서 한 번만 실행한다. (학생은 실행할 필요 없음)

사용법:
    python prep/select_user.py --maildir <압축 푼 maildir 경로> --out <통계.csv>

직원별로 다음을 계산한다.
    - 메일 수, 폴더 수, 가장 큰 폴더 3개
    - 본문이 완전히 같은 메일의 비율 (폴더 사본 → Part 2 중복 제거용)
    - 노이즈 유형별로 '그 노이즈가 들어 있는 메일'의 비율
    - 본문 단어 수 중앙값, 50단어 미만 메일 비율
"""

import argparse
import csv
import hashlib
import re
import statistics
from collections import Counter
from pathlib import Path

# 노이즈 유형별 탐지 패턴 (선정용 대략 통계이므로 느슨하게 잡는다)
NOISE = {
    "orig_msg": re.compile(r"-{3,}\s*Original Message\s*-{3,}"),
    "forwarded": re.compile(r"-{3,}\s*Forwarded by "),
    "qp_residue": re.compile(r"=20\s*$|=09|=\n", re.M),
    "lotus_addr": re.compile(r"/[A-Za-z]{2,}/[A-Za-z_]{2,}@[A-Za-z_]{2,}|/[A-Z]{2,}@[A-Za-z]{2,}"),
    "html_tag": re.compile(r"</?(?:html|body|br|p|div|font|table|tr|td|b|a)\b[^>]*>", re.I),
    "disclaimer": re.compile(r"property of Enron Corp|intended (?:only|solely) for|confidential and", re.I),
    "gt_quote": re.compile(r"^>", re.M),
}


def read_mail(path: Path) -> tuple[str, str]:
    """파일을 읽어 (헤더, 본문)으로 나눈다. 첫 빈 줄이 경계."""
    text = path.read_bytes().decode("latin-1")
    head, _, body = text.partition("\n\n")
    return head, body


def user_stats(user_dir: Path) -> dict:
    files = [p for p in user_dir.rglob("*") if p.is_file()]
    folders = Counter()
    hashes = Counter()
    noise = Counter()
    word_counts = []
    for p in files:
        _, body = read_mail(p)
        folders[p.parent.relative_to(user_dir).as_posix()] += 1
        hashes[hashlib.md5(" ".join(body.split()).encode("latin-1")).hexdigest()] += 1
        for name, rx in NOISE.items():
            if rx.search(body):
                noise[name] += 1
        word_counts.append(len(body.split()))
    n = len(files)
    row = {
        "user": user_dir.name,
        "n_mails": n,
        "n_folders": len(folders),
        "top_folders": "; ".join(f"{k}={v}" for k, v in folders.most_common(3)),
        "exact_dup_rate": round(1 - len(hashes) / n, 3) if n else 0,
        "median_words": int(statistics.median(word_counts)) if n else 0,
        "under_50_words": round(sum(w < 50 for w in word_counts) / n, 3) if n else 0,
    }
    for name in NOISE:
        row[name] = round(noise[name] / n, 3) if n else 0
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maildir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    rows = []
    for user_dir in sorted(d for d in args.maildir.iterdir() if d.is_dir()):
        rows.append(user_stats(user_dir))
        print(f"{rows[-1]['user']:<20} {rows[-1]['n_mails']:>6}", flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)}명 통계 저장: {args.out}")


if __name__ == "__main__":
    main()
