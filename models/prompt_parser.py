from __future__ import annotations

import re  # 정규 표현식 모듈
from typing import List, Optional

# --- Lexicons ---------------------------------------------------------------
# 다양한 장르에 대한 매핑. 사용자 입력에서 일반적인 표현을 표준화합니다.
GENRE_MAP = {
    "lofi": "lofi",
    "lo-fi": "lofi",
    "chillhop": "lofi",
    "hiphop": "hiphop",
    "hip-hop": "hiphop",
    "boom bap": "hiphop",
    "trap": "hiphop",
    "jazz": "jazz",
    "swing": "jazz",
    "bossa": "jazz",
    "citypop": "citypop",
    "city pop": "citypop",
    "city-pop": "citypop",
    "classical": "classical",
    "orchestral": "classical",
    "piano": "classical",
    "electronic": "electronic",
    "edm": "electronic",
    "synth": "electronic",
}

# 다양한 분위기에 대한 매핑. 사용자 입력에서 일반적인 표현을 표준화합니다.
MOOD_MAP = {
    "calm": "calm",
    "chill": "calm",
    "relaxed": "calm",
    "soft": "calm",
    "cozy": "calm",
    "happy": "happy",
    "bright": "happy",
    "uplifting": "happy",
    "sad": "sad",
    "melancholy": "sad",
    "moody": "sad",
    "dark": "dark",
    "tense": "dark",
    "energetic": "energetic",
    "fast": "energetic",
    "driving": "energetic",
    "romantic": "romantic",
    "dreamy": "romantic",
    "smooth": "romantic",
    "groovy": "groovy",
    "funky": "groovy",
}

# 다양한 밀도에 대한 매핑. 사용자 입력에서 일반적인 표현을 표준화합니다.
DENSITY_MAP = {
    "sparse": "low",
    "minimal": "low",
    "simple": "low",
    "light": "low",
    "medium": "mid",
    "balanced": "mid",
    "full": "high",
    "busy": "high",
    "dense": "high",
    "thick": "high",
}

# 장르별 기본 BPM (폴백 값)
DEFAULT_BPM = {
    "lofi": 85,
    "hiphop": 90,
    "jazz": 120,
    "citypop": 105,
    "classical": 100,
    "electronic": 120,
}
# 모든 항목에 대한 기본값
DEFAULTS = {"genre": "lofi", "mood": "calm", "density": "mid", "key": "C_major", "bpm": 90}


# --- Helpers ----------------------------------------------------------------
def _find_bpm(text: str) -> Optional[int]:
    """프롬프트에서 BPM 값을 찾습니다. '85 bpm' 또는 '92'와 같은 패턴을 찾습니다."""
    m = re.search(r"(\d{2,3})\s*bpm", text, flags=re.I)  # '숫자 bpm' 패턴 찾기
    if not m:
        m = re.search(r"\b(\d{2,3})\b", text)  # 독립적인 숫자 패턴 찾기
    if m:
        bpm = int(m.group(1))
        if 40 <= bpm <= 220:  # BPM 유효 범위 확인
            return bpm
    return None


def _find_key(text: str) -> Optional[str]:
    """프롬프트에서 키(예: C minor, G# major)를 찾습니다."""
    # '음표(A-G)[#b]? (major|minor|maj|min)?' 패턴 찾기
    m = re.search(r"\b([A-Ga-g])([#b]?)(?:\s|-)?(major|minor|maj|min)?\b", text)
    if not m:
        return None
    note = m.group(1).upper() + m.group(2)  # 음표와 #/b 조합
    qual = m.group(3) or "major"  # major/minor 정보, 없으면 major 기본값
    qual = {"maj": "major", "min": "minor"}.get(
        qual.lower(), qual.lower()
    )  # 축약형을 전체명으로 변환
    return f"{note}_{qual}"  # 'C_major' 형식으로 반환


def _first_match(text: str, table: dict) -> Optional[str]:
    """주어진 텍스트에서 테이블의 첫 번째 키 매치를 찾아 해당 값을 반환합니다."""
    for k, v in table.items():
        if k in text:  # 텍스트에 키가 포함되어 있으면
            return v  # 해당 값 반환
    return None


# --- Public -----------------------------------------------------------------
def parse_prompt(prompt: str) -> List[str]:
    """
    주어진 텍스트 프롬프트를 제어 토큰 리스트로 파싱합니다.
    예: ['GENRE:lofi','MOOD:calm','BPM:85','KEY:C_major','DENSITY:low']
    """
    t = prompt.lower()  # 입력 프롬프트를 소문자로 변환

    # 각 요소에 대해 매핑 테이블에서 첫 번째 일치하는 항목을 찾거나 기본값을 사용합니다.
    genre = _first_match(t, GENRE_MAP) or DEFAULTS["genre"]
    mood = _first_match(t, MOOD_MAP) or DEFAULTS["mood"]
    density = _first_match(t, DENSITY_MAP) or DEFAULTS["density"]
    bpm = _find_bpm(t) or DEFAULT_BPM.get(
        genre, DEFAULTS["bpm"]
    )  # BPM 찾기, 없으면 장르별 기본값, 없으면 전체 기본값
    key = _find_key(t) or DEFAULTS["key"]  # 키 찾기, 없으면 기본값

    # 최종 토큰 리스트 생성
    return [f"GENRE:{genre}", f"MOOD:{mood}", f"BPM:{int(bpm)}", f"KEY:{key}", f"DENSITY:{density}"]


if __name__ == "__main__":
    # 테스트 프롬프트 목록
    tests = [
        "lofi chill study bpm 82 in A minor",
        "citypop bright 105bpm",
        "jazz swing medium density",
        "hip-hop dark 92",
        "classical romantic C major",
    ]
    # 각 테스트 프롬프트에 대해 파싱 결과를 출력합니다.
    for p in tests:
        print(p, "->", parse_prompt(p))
