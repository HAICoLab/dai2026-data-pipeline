"""실습 환경 점검. 저장소 루트에서 실행한다.

    python check_env.py

모든 줄이 [OK]로 나오면 준비 완료.
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
problems = 0


def report(ok: bool, name: str, detail: str = "", fix: str = "") -> None:
    global problems
    print(f"[{'OK' if ok else '문제'}] {name}" + (f" - {detail}" if detail else ""))
    if not ok:
        problems += 1
        if fix:
            print(f"       해결: {fix}")


# 1. 파이썬 버전
version = sys.version_info
report(version >= (3, 9), "Python 버전", f"{version.major}.{version.minor}.{version.micro}",
       "Python 3.9 이상을 설치하세요.")

# 2. 패키지
for package in ("pandas", "matplotlib"):
    try:
        module = __import__(package)
        report(True, f"{package} 설치", module.__version__)
    except ImportError:
        report(False, f"{package} 설치", "없음", "pip install -r requirements.txt")

# 3. 실행 위치
report(Path.cwd().resolve() == ROOT, "실행 위치", str(Path.cwd()),
       f"저장소 루트로 이동한 뒤 다시 실행하세요: cd {ROOT}")

# 4. 데이터
data_files = sorted((ROOT / "data" / "raw").glob("*.jsonl"))
report(bool(data_files), "데이터 파일", ", ".join(p.name for p in data_files) or "없음",
       "git pull 로 최신 저장소를 받으세요.")
for path in data_files:
    try:
        with path.open(encoding="utf-8") as f:
            records = [json.loads(line) for line in f]
        fields_ok = all({"id", "folder", "raw"} <= set(r) for r in records)
        report(fields_ok, f"{path.name} 읽기", f"메일 {len(records):,}통")
    except Exception as error:  # 파일이 깨졌거나 인코딩 문제가 있는 경우
        report(False, f"{path.name} 읽기", str(error), "저장소를 다시 clone 하세요.")

# 5. 도구
report(shutil.which("git") is not None, "git", fix="git을 설치하세요.")
report(shutil.which("claude") is not None, "Claude Code", fix="Claude Code를 설치하고 로그인하세요.")

# 6. 결과 폴더에 쓸 수 있는지
try:
    out_dir = ROOT / "part1" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    test_file = out_dir / ".write_test"
    test_file.write_text("가나다", encoding="utf-8")
    test_file.unlink()
    report(True, "결과 폴더 쓰기", "part1/out")
except OSError as error:
    report(False, "결과 폴더 쓰기", str(error))

print()
print("준비 완료!" if problems == 0 else f"문제 {problems}건을 해결한 뒤 다시 실행하세요.")
sys.exit(0 if problems == 0 else 1)
