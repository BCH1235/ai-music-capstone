import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # 현재 스크립트의 루트 디렉터리
# 토큰화된 JSON 파일이 있는 디렉터리 목록
PROC_DIRS = [ROOT / "data" / "midi_proc" / "melody", ROOT / "data" / "midi_proc" / "drums"]
OUT = ROOT / "data" / "vocab.json"  # 최종 어휘집 파일 경로

# 특별 토큰들을 맨 앞에 예약 (고정된 ID)
SPECIAL = [
    "PAD",
    "BOS",
    "EOS",
    "BAR",
    "TS:1",
    "UNK",
]  # PAD: 패딩, BOS: 시작, EOS: 끝, BAR: 마디, TS: 시간 이동, UNK: 알 수 없음


def gather_tokens():
    seen = set()  # 일반 토큰 (특별 토큰은 별도 처리)
    for d in PROC_DIRS:  # 각 처리 디렉터리 순회
        if not d.exists():  # 디렉터리가 존재하지 않으면 건너뜀
            continue
        for p in d.glob("*.json"):  # 해당 디렉터리 내 모든 JSON 파일 검색
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))  # JSON 파일 내용 읽어 파싱
                for t in obj.get("tokens", []):  # "tokens" 키의 값(토큰 목록) 순회
                    if t not in SPECIAL:  # 특별 토큰이 아닌 경우
                        seen.add(t)  # seen 집합에 추가
            except Exception as e:  # 파일 처리 중 예외 발생 시
                print(f"[WARN] Skip {p.name}: {e}")  # 경고 메시지 출력

    # 결정론적 순서: 특별 토큰 먼저, 그 다음 정렬된 일반 토큰
    ordered = SPECIAL + sorted(seen)
    tok2id = {t: i for i, t in enumerate(ordered)}  # 토큰 -> ID 매핑 생성
    id2tok = {i: t for t, i in tok2id.items()}  # ID -> 토큰 매핑 생성

    OUT.parent.mkdir(parents=True, exist_ok=True)  # 출력 디렉터리 생성
    OUT.write_text(  # 어휘집 파일을 JSON으로 저장
        json.dumps(
            {
                "token_to_id": tok2id,
                "id_to_token": id2tok,
                "size": len(ordered),
            },  # 토큰->ID, ID->토큰, 전체 크기 포함
            ensure_ascii=False,  # ASCII 아닌 문자도 그대로 저장
            indent=2,  # 들여쓰기 적용
        ),
        encoding="utf-8",  # UTF-8 인코딩 사용
    )
    print(f"Vocab size={len(ordered)} → {OUT}")  # 어휘집 크기 및 경로 출력


if __name__ == "__main__":
    gather_tokens()  # 메인 함수 실행
