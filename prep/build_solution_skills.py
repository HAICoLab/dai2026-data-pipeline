"""정답 Skill 예시 폴더에 스크립트를 복사해 넣는다. (교수자용)

    python prep/build_solution_skills.py

Skill은 혼자서도 동작해야 하므로 필요한 스크립트를 scripts/ 안에 함께 둔다.
part1/solution/src/ 의 스크립트를 고쳤다면 이 스크립트를 다시 실행한다.
"""

import shutil
from pathlib import Path

SRC = Path("part1/solution/src")
TESTS = Path("part1/tests")
SKILLS = Path("part1/solution/skills")

CONTENTS = {
    "data-profiling": [SRC / "common.py", SRC / "s0_profile.py", SRC / "make_report.py"],
    "regex-cleaning": [SRC / "common.py", SRC / "patterns.py", SRC / "s1_parse.py", SRC / "s2_clean.py",
                       TESTS / "test_regex.py", TESTS / "regex_cases.json"],
    "quality-signals": [SRC / "common.py", SRC / "s3_quality.py", SRC / "make_report.py"],
}

for skill, files in CONTENTS.items():
    target = SKILLS / skill / "scripts"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for path in files:
        shutil.copy(path, target / path.name)
    print(f"{skill}: {', '.join(p.name for p in files)}")
