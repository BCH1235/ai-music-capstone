from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List

import pretty_midi

STEPS_PER_BAR = 16  # 4/4 그리드 기준

# GM 드럼 → 압축된 클래스 매핑
_PITCH2CLS: Dict[int, str] = {
    35: "KICK",
    36: "KICK",  # 베이스 드럼
    38: "SNARE",
    40: "SNARE",
    37: "SNARE",  # 스네어 드럼
    42: "HHC",
    44: "HHC",  # 클로즈드/페달 하이햇
    46: "HHO",  # 오픈 하이햇
    48: "TOM",
    45: "TOM",
    47: "TOM",
    50: "TOM",
    41: "TOM",
    43: "TOM",  # 탐탐
    49: "CRASH",
    57: "CRASH",
    55: "CRASH",  # 크래시 심벌
    51: "RIDE",
    59: "RIDE",
    52: "RIDE",  # 라이드 심벌
    39: "CLAP",  # 클랩
}
# 사용될 클래스 목록 (순서 중요)
_CLASSES = [
    "KICK",
    "SNARE",
    "HHC",
    "HHO",
    "TOM",
    "RIDE",
    "CRASH",
    "CLAP",
    "PERC",
]  # PERC는 그 외 퍼커션


def _cls_for_pitch(p: int) -> str:
    """주어진 피치에 해당하는 드럼 클래스를 반환합니다. 매핑되지 않으면 'PERC' 반환."""
    return _PITCH2CLS.get(p, "PERC")


def _estimate_bpm(pm: pretty_midi.PrettyMIDI) -> float:
    """BPM 추정 함수 (이상값 발생 시 90으로 대체)"""
    try:
        bpm = float(pm.estimate_tempo())
        if not math.isfinite(bpm) or bpm <= 0:
            return 90.0  # 유효하지 않거나 0 이하 BPM은 90으로 대체
        return max(40.0, min(220.0, bpm))  # BPM 범위를 40~220으로 제한
    except Exception:
        return 90.0  # BPM 추정 중 오류 발생 시 90 반환


def midi_to_drum_tokens(midi_path: Path) -> List[str]:
    """
    드럼 토큰화 함수:
    토큰: BOS, BPM:<int>, TS:1 (시간 이동), BAR (마디 구분), DRUM:<CLASS> (드럼 클래스), …, EOS
    """
    pm = pretty_midi.PrettyMIDI(str(midi_path))  # MIDI 파일 로드
    bpm = _estimate_bpm(pm)  # BPM 추정
    step_sec = (60.0 / bpm) / 4.0  # 16분 음표당 초 (4/4 기준)

    hits = {}  # 각 스텝(시간)에 어떤 드럼 클래스가 있는지 저장: {step: set(classes)}
    min_step, max_step = None, 0  # 최소/최대 스텝 기록
    for inst in pm.instruments:
        if not inst.is_drum:
            continue  # 드럼 악기가 아닌 경우 건너뜀
        for n in inst.notes:
            s = int(round(n.start / step_sec))  # 노트 시작 시간을 스텝 단위로 변환
            hits.setdefault(s, set()).add(_cls_for_pitch(n.pitch))  # 해당 스텝에 드럼 클래스 추가
            if min_step is None or s < min_step:
                min_step = s  # 최소 스텝 업데이트
            if s > max_step:
                max_step = s  # 최대 스텝 업데이트
    if min_step is None:  # 처리할 노트가 없으면 기본 토큰 반환
        return ["BOS", f"BPM:{int(round(bpm))}", "EOS"]

    # 시작 스텝을 0으로 맞추기 위한 쉬프트 계산
    shift = min_step or 0
    if shift:
        # 모든 스텝을 shift만큼 빼서 시작 스텝을 0으로 만듦
        hits = {s - shift: v for s, v in hits.items()}
        max_step -= shift

    tokens = ["BOS", f"BPM:{int(round(bpm))}"]  # 시작, BPM 토큰 추가
    bar_step = 0  # 현재 마디 내 스텝 카운트
    for step in range(max_step + 1):  # 최대 스텝까지 반복
        tokens.append("TS:1")  # 시간 이동 토큰 추가
        bar_step += 1
        if bar_step >= STEPS_PER_BAR:  # STEPS_PER_BAR (16) 도달 시 마디 구분 토큰 추가
            tokens.append("BAR")
            bar_step = 0
        if step in hits:  # 현재 스텝에 드럼 히트가 있는 경우
            for cls in _CLASSES:  # 정의된 클래스 순서대로 확인
                if cls in hits[step]:  # 해당 클래스가 히트된 경우
                    tokens.append(f"DRUM:{cls}")  # DRUM:<CLASS> 토큰 추가
    tokens.append("EOS")  # 끝 토큰 추가
    return tokens


def save_tokens(tokens: List[str], out_json: Path) -> None:
    """토큰 리스트를 JSON 파일로 저장하는 함수"""
    out_json.parent.mkdir(parents=True, exist_ok=True)  # 출력 디렉터리 생성
    # UTF-8 인코딩으로 JSON 파일에 저장
    out_json.write_text(
        json.dumps({"tokens": tokens}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
