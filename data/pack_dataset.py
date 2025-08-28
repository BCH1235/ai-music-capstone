import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # 현재 스크립트의 루트 디렉터리
VOCAB_PATH = ROOT / "data" / "vocab.json"  # 어휘집 파일 경로

# 처리된 토큰 파일이 있는 디렉터리들
PROC_DIRS = {
    "melody": ROOT / "data" / "midi_proc" / "melody",
    "drums": ROOT / "data" / "midi_proc" / "drums",
}

OUT_DIR = ROOT / "data" / "ds"  # 최종 데이터셋 파일이 저장될 디렉터리

# 특별 토큰 목록 (항상 처음에 오도록 보장)
SPECIAL = ["PAD", "BOS", "EOS", "BAR", "TS:1", "UNK"]


def load_vocab():
    """어휘집 파일 (vocab.json)을 로드하고, 필요한 경우 특별 토큰을 포함하여 재구성합니다."""
    obj = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    tok2id = obj["token_to_id"]
    # 만약 SPECIAL 토큰이 없으면 (발생하면 안 됨), 결정론적으로 앞에 추가합니다.
    changed = False
    for sp in SPECIAL:
        if sp not in tok2id:
            changed = True
    if changed:
        # 특별 토큰을 앞에 두고 다시 구성합니다.
        all_tokens = sorted([t for t in tok2id.keys() if t not in SPECIAL])  # 일반 토큰만 정렬
        ordered = SPECIAL + all_tokens  # 특별 토큰 + 정렬된 일반 토큰
        tok2id = {t: i for i, t in enumerate(ordered)}  # 새로운 토큰->ID 맵핑 생성
        VOCAB_PATH.write_text(  # 업데이트된 어휘집을 파일에 씁니다.
            json.dumps(
                {
                    "token_to_id": tok2id,
                    "id_to_token": {i: t for t, i in tok2id.items()},  # ID->토큰 맵핑도 포함
                    "size": len(ordered),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return tok2id


def list_token_files(kind: str):
    """지정된 종류(멜로디 또는 드럼)의 토큰 파일 목록을 반환합니다."""
    d = PROC_DIRS[kind]
    return sorted([p for p in d.glob("*.json")])  # .json 파일만 검색하고 정렬


def to_ids(tokens, tok2id, max_len: int):
    """토큰 리스트를 ID 리스트로 변환하고, 최대 길이를 초과하면 잘라냅니다."""
    # 토큰을 ID로 매핑. 알 수 없는 토큰은 UNK ID로 변환
    ids = [tok2id.get(t, tok2id["UNK"]) for t in tokens]
    # 간단한 길이 제한 적용
    return ids[:max_len]


def pack(kind: str, val_ratio: float, max_len: int, min_len: int, seed: int = 42):
    """
    지정된 종류의 토큰 파일들을 학습/검증 데이터셋으로 패킹합니다.
    kind: "melody" 또는 "drums"
    val_ratio: 검증 데이터셋 비율
    max_len: 최대 토큰 길이
    min_len: 최소 토큰 길이 (이보다 짧으면 건너뜀)
    seed: 데이터 셔플링을 위한 시드 값
    """
    tok2id = load_vocab()  # 어휘집 로드
    files = list_token_files(kind)  # 토큰 파일 목록 가져오기
    if not files:  # 파일이 없으면 오류 메시지 출력 후 종료
        raise SystemExit(f"No token files for {kind} in {PROC_DIRS[kind]}")

    random.Random(seed).shuffle(files)  # 파일 목록을 시드 기반으로 셔플링
    n_val = max(1, int(len(files) * val_ratio))  # 검증 파일 개수 계산 (최소 1개)
    val_files = files[:n_val]  # 검증 파일 목록
    train_files = files[n_val:]  # 학습 파일 목록

    OUT_DIR.mkdir(parents=True, exist_ok=True)  # 출력 디렉터리 생성
    out_train = OUT_DIR / f"{kind}_train.jsonl"  # 학습 파일 경로
    out_val = OUT_DIR / f"{kind}_val.jsonl"  # 검증 파일 경로

    kept_train = kept_val = 0  # 최종 저장된 파일 수 카운터
    # 학습 및 검증 파일을 쓰기 모드로 열기
    with out_train.open("w", encoding="utf-8") as ftr, out_val.open("w", encoding="utf-8") as fva:
        for split, flist, fout in [
            ("train", train_files, ftr),
            ("val", val_files, fva),
        ]:  # 학습, 검증 분할 처리
            for p in flist:  # 각 파일에 대해 반복
                obj = json.loads(p.read_text(encoding="utf-8"))  # JSON 파일 읽어 파싱
                tokens = obj.get("tokens", [])  # 토큰 목록 가져오기
                if len(tokens) < min_len:  # 최소 길이보다 짧으면 건너뜀
                    continue
                ids = to_ids(tokens, tok2id, max_len)  # 토큰을 ID로 변환
                rec = {
                    "ids": ids,
                    "src": p.name,
                    "kind": kind,
                }  # 학습 레코드 생성 (ID, 원본 파일명, 종류)
                fout.write(
                    json.dumps(rec, ensure_ascii=False) + "\n"
                )  # JSON 레코드를 파일에 쓰고 줄바꿈
                if split == "train":
                    kept_train += 1  # 학습 파일 카운트 증가
                else:
                    kept_val += 1  # 검증 파일 카운트 증가

    print(f"{kind}: train={kept_train}  val={kept_val}  -> {OUT_DIR}")  # 최종 결과 출력


if __name__ == "__main__":
    ap = argparse.ArgumentParser()  # 명령줄 인자 파서 설정
    ap.add_argument(
        "--kind", choices=["melody", "drums"], required=True, help="Dataset kind to pack"
    )  # 'melody' 또는 'drums' 선택
    ap.add_argument(
        "--val_ratio", type=float, default=0.05, help="Ratio of validation files"
    )  # 검증 파일 비율 (기본 0.05)
    ap.add_argument(
        "--max_len", type=int, default=1024, help="Maximum sequence length in tokens"
    )  # 최대 토큰 길이 (기본 1024)
    ap.add_argument(
        "--min_len", type=int, default=32, help="Minimum sequence length in tokens"
    )  # 최소 토큰 길이 (기본 32)
    args = ap.parse_args()
    pack(args.kind, args.val_ratio, args.max_len, args.min_len)  # 설정값으로 pack 함수 호출
