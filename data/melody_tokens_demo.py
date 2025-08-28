import sys
from pathlib import Path

# 모델을 임포트하기 전에 프로젝트 루트를 임포트 가능하게 만듭니다.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 이제 models.tokenizer에서 임포트가 가능합니다.
from models.tokenizer import midi_to_melody_tokens, save_tokens  # noqa: E402

# 멜로디 MIDI 파일이 있는 디렉터리 경로 설정
MELODY_DIR = ROOT / "data" / "midi_raw" / "melody" / "maestro"
# 토큰화된 결과를 저장할 디렉터리 경로 설정
OUT_DIR = ROOT / "data" / "midi_proc" / "melody"


def find_midis(dir_path: Path):
    # .mid / .midi에 대한 대소문자 구분 없는 재귀적 검색
    return [
        p
        for p in dir_path.rglob("*")  # 모든 파일 및 디렉터리 순회
        if p.is_file()
        and p.suffix.lower()
        in {".mid", ".midi"}  # 파일이고 확장자가 .mid 또는 .midi (소문자 변환 후)인 경우
    ]


if __name__ == "__main__":
    # 지정된 디렉터리에서 MIDI 파일 검색
    midi_files = sorted(find_midis(MELODY_DIR))
    if not midi_files:  # MIDI 파일이 없으면 오류 메시지 출력 후 종료
        raise SystemExit(f"No MIDI files found under {MELODY_DIR}")

    print(
        f"Found {len(midi_files)} MIDI files. Using first one."
    )  # 찾은 MIDI 파일 개수와 사용할 파일 정보 출력
    midi_path = midi_files[0]  # 데모를 위해 첫 번째 파일만 사용
    OUT_DIR.mkdir(parents=True, exist_ok=True)  # 출력 디렉터리 생성 (이미 있어도 오류 없음)

    # MIDI 파일을 토큰으로 변환
    tokens = midi_to_melody_tokens(midi_path, key_hint="C_major")
    # 결과 JSON 파일 경로 설정
    out_path = OUT_DIR / (midi_path.stem + ".json")
    # 토큰을 JSON 파일로 저장
    save_tokens(tokens, out_path)

    print("MIDI:", midi_path.name)  # 처리된 MIDI 파일 이름 출력
    print("Tokens saved to:", out_path)  # 저장된 토큰 파일 경로 출력
    print("Preview:", tokens[:32])  # 처음 32개 토큰 미리보기 출력
