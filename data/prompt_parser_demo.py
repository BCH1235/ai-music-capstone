import sys
from pathlib import Path

# 모델을 임포트하기 전에 프로젝트 루트를 임포트 가능하게 만듭니다.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 프롬프트 파서 모듈을 임포트합니다.
from models.prompt_parser import parse_prompt  # noqa: E402

# 테스트할 프롬프트 목록
tests = [
    "lofi chill study bpm 82 in A minor",
    "citypop bright 105bpm",
    "hip hop dark 92",
    "jazzy smooth romantic 120",
    "classical piano calm in C major",
]
# 각 프롬프트에 대해 파싱 결과를 출력합니다.
for t in tests:
    print(t, "->", parse_prompt(t))
