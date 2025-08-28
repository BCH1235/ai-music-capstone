import argparse
import sys  # 명령줄 인자 처리를 위한 argparse 추가
from pathlib import Path

from tqdm import tqdm  # 진행률 표시줄을 위한 tqdm

# 모델 임포트를 위해 프로젝트 루트 경로를 sys.path에 추가
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 토크나이저 모듈 임포트
from models.tokenizer import midi_to_melody_tokens, save_tokens  # noqa: E402

# 멜로디 MIDI 파일이 있는 루트 디렉터리
MELODY_ROOT = ROOT / "data" / "midi_raw" / "melody"
# 토큰화된 JSON 파일이 저장될 디렉터리
OUT_DIR = ROOT / "data" / "midi_proc" / "melody"


def find_midis(root: Path):
    """주어진 디렉터리 내에서 모든 .mid 또는 .midi 파일을 대소문자 구분 없이 검색합니다."""
    return [
        p
        for p in root.rglob("*")  # 재귀적으로 모든 파일/디렉터리 검색
        if p.is_file()
        and p.suffix.lower() in {".mid", ".midi"}  # 파일이고 확장자가 .mid 또는 .midi인 경우
    ]


def main(limit: int | None = None, overwrite: bool = False):
    """멜로디 MIDI 파일을 일괄 토큰화하는 메인 함수"""
    files = find_midis(MELODY_ROOT)  # 모든 MIDI 파일 목록 가져오기
    if not files:  # 파일이 없으면 오류 메시지 출력 후 종료
        raise SystemExit(f"No MIDI files under {MELODY_ROOT}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)  # 출력 디렉터리 생성
    total = saved = skipped = errors = 0  # 처리 통계 초기화

    # 각 MIDI 파일을 순회하며 토큰화 (진행률 표시)
    for p in tqdm(files, desc="Tokenizing melody MIDIs"):
        if limit is not None and total >= limit:  # limit 설정 시 N개 파일만 처리
            break
        total += 1

        out = OUT_DIR / (p.stem + ".json")  # 출력 JSON 파일 경로 설정
        if out.exists() and not overwrite:  # 이미 JSON 파일이 있고 overwrite 옵션이 없으면 건너뜀
            skipped += 1
            continue

        try:
            tokens = midi_to_melody_tokens(p, key_hint="C_major")  # MIDI 파일 토큰화
            save_tokens(tokens, out)  # 토큰을 JSON 파일로 저장
            saved += 1
        except Exception as e:  # 오류 발생 시
            errors += 1
            print(f"[ERR] {p.name}: {e}")  # 오류 메시지 출력

    # 최종 통계 출력
    print(f"Done. total={total} saved={saved} skipped={skipped} errors={errors} out_dir={OUT_DIR}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()  # 명령줄 인자 파서 생성
    ap.add_argument(
        "--limit", type=int, default=None, help="Process only N files for a quick test"
    )  # N개 파일만 처리하는 옵션
    ap.add_argument(
        "--overwrite", action="store_true", help="Regenerate even if JSON exists"
    )  # 기존 JSON 파일 덮어쓰기 옵션
    args = ap.parse_args()  # 인자 파싱
    main(limit=args.limit, overwrite=args.overwrite)  # main 함수 호출
