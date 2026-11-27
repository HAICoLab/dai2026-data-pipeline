"""정규식 테스트. 데이터에 적용하기 전에 먼저 통과시킨다.

    python part1/tests/test_regex.py                                       # 내 패턴 (part1/src/patterns.py)
    python part1/tests/test_regex.py --patterns part1/solution/src/patterns.py   # 정답 패턴

patterns.py에는 PATTERNS라는 딕셔너리가 있어야 한다.
    PATTERNS = {"html_tag": re.compile(r"..."), "email": re.compile(r"..."), ...}

테스트 사례는 regex_cases.json에 있다. 사례 하나는 이렇게 생겼다.
    rule    어떤 패턴을 시험하는지 (PATTERNS의 키)
    input   시험할 문자열
    expect  input에서 잡혀야 하는 부분들. 빈 목록이면 아무것도 잡히면 안 된다.
    note    왜 이 사례가 있는지
    known_limit  true이면 정규식만으로는 풀기 어려운 사례. 틀려도 실패로 세지 않는다.

PATTERNS에 아직 없는 규칙은 건너뛴다. (email, phone은 개인정보 가리기를 할 때만 필요하다)
"""

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(errors="replace")
HERE = Path(__file__).resolve().parent


def load_patterns(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"패턴 파일이 없습니다: {path}\nPATTERNS 딕셔너리가 들어 있는 patterns.py를 먼저 만드세요.")
    spec = importlib.util.spec_from_file_location("patterns", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "PATTERNS"):
        sys.exit(f"{path} 안에 PATTERNS 딕셔너리가 없습니다.")
    return {name: re.compile(p) if isinstance(p, str) else p for name, p in module.PATTERNS.items()}


def show(text: str) -> str:
    """줄바꿈과 탭이 눈에 보이도록 바꾼다."""
    return text.replace("\n", "\\n").replace("\t", "\\t")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", type=Path, default=Path("part1/src/patterns.py"))
    ap.add_argument("--cases", type=Path, default=HERE / "regex_cases.json")
    ap.add_argument("--rule", help="이 규칙만 시험한다")
    args = ap.parse_args()

    patterns = load_patterns(args.patterns)
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if args.rule:
        cases = [c for c in cases if c["rule"] == args.rule]

    passed = failed = limits = 0
    missing = {}
    for case in cases:
        rule = case["rule"]
        if rule not in patterns:
            missing[rule] = missing.get(rule, 0) + 1   # 아직 만들지 않은 패턴은 건너뛴다
            continue
        # 앞뒤 공백 차이는 무시하고 비교한다.
        found = [m.group(0).strip() for m in patterns[rule].finditer(case["input"])]
        found = [f for f in found if f]
        expect = [e.strip() for e in case["expect"]]
        ok = found == expect
        if ok:
            passed += 1
            continue
        if case.get("known_limit"):
            limits += 1
            label = "한계"
        else:
            failed += 1
            label = "실패"
        print(f"[{label}] {rule}: {case['note']}")
        print(f"       입력   {show(case['input'])}")
        print(f"       기대   {[show(e) for e in expect]}")
        print(f"       실제   {[show(f) for f in found]}")

    for rule, count in missing.items():
        print(f"[건너뜀] {rule}: PATTERNS에 '{rule}' 키가 없어 {count}건을 시험하지 못했습니다.")
    print(f"\n통과 {passed} / 실패 {failed} / 알려진 한계 {limits} / 건너뜀 {sum(missing.values())}  (총 {len(cases)}건)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
