import sys
from pathlib import Path

# 프로젝트 루트를 임포트 가능하게 만듭니다.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 드럼 토크나이저 모듈을 임포트합니다.
from models.tokenizer_drums import midi_to_drum_tokens, save_tokens  # noqa: E402

# GMD 드럼 MIDI 파일이 있는 디렉터리 경로
IN_DIR = ROOT / "data" / "midi_raw" / "drums" / "gmd"
# 토큰화된 결과를 저장할 디렉터리 경로
OUT_DIR = ROOT / "data" / "midi_proc" / "drums"


def find_midis(d: Path):
    """주어진 디렉터리에서 .mid 또는 .midi 파일을 대소문자 구분 없이 검색합니다."""
    return [p for p in d.rglob("*") if p.is_file() and p.suffix.lower() in {".mid", ".midi"}]


if __name__ == "__main__":
    files = find_midis(IN_DIR)  # MIDI 파일 목록 검색
    if not files:
        raise SystemExit(f"No MIDI files in {IN_DIR}")  # 파일 없으면 오류 발생
    p = files[0]  # 데모를 위해 첫 번째 파일만 사용
    OUT_DIR.mkdir(parents=True, exist_ok=True)  # 출력 디렉터리 생성
    tokens = midi_to_drum_tokens(p)  # 드럼 MIDI 토큰화
    out = OUT_DIR / (p.stem + ".json")  # 출력 JSON 파일 경로 설정
    save_tokens(tokens, out)  # 토큰 저장
    print("Saved:", out)  # 저장된 파일 경로 출력
    print("Preview:", tokens[:32])  # 처음 32개 토큰 미리보기 출력
