"""선정한 직원의 메일함을 JSONL 파일 하나로 묶는다.

교수자 PC에서 한 번만 실행한다. (학생은 실행할 필요 없음)

사용법:
    python prep/extract.py --maildir <maildir 경로> --user <직원 폴더명> --out data/raw/<직원>.jsonl

왜 파일 하나로 묶나:
    Enron 원본은 메일 1통이 파일 1개이고 파일명이 `1.`처럼 점으로 끝난다.
    Windows에서는 이런 이름의 파일을 만들 수 없어 git clone이 실패한다.
    그래서 메일 원문은 한 글자도 바꾸지 않고, 담는 그릇만 JSONL로 바꾼다.

출력 형식 (한 줄 = 메일 1통):
    {"id": "inbox/12", "folder": "inbox", "raw": "<헤더와 본문이 그대로 들어 있는 메일 원문>"}
"""

import argparse
import json
from pathlib import Path


def decode(data: bytes) -> str:
    """원본은 대부분 ASCII이고 가끔 Windows 문자(cp1252)가 섞여 있다."""
    for enc in ("utf-8", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1")


def sort_key(rel: Path) -> tuple:
    """폴더 이름순, 그 안에서는 파일 번호순."""
    stem = rel.name.rstrip(".")
    return (rel.parent.as_posix(), int(stem) if stem.isdigit() else 0, stem)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--maildir", required=True, type=Path)
    ap.add_argument("--user", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    user_dir = args.maildir / args.user
    rels = sorted((p.relative_to(user_dir) for p in user_dir.rglob("*") if p.is_file()), key=sort_key)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="\n") as f:
        for rel in rels:
            record = {
                "id": f"{rel.parent.as_posix()}/{rel.name.rstrip('.')}",
                "folder": rel.parent.as_posix(),
                "raw": decode((user_dir / rel).read_bytes()),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    size_mb = args.out.stat().st_size / 1e6
    print(f"{args.user}: {len(rels)}통 → {args.out} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
