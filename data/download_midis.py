import urllib.request
import zipfile
from pathlib import Path

from tqdm import tqdm

# 프로젝트 루트 경로 설정
ROOT = Path(__file__).resolve().parents[1]
# 다운로드 및 임시 파일 경로 설정
DL = ROOT / "data" / "downloads"
TMP = ROOT / "data" / "tmp"
# MIDI 파일이 저장될 최종 경로 설정
DEST_MELODY = ROOT / "data" / "midi_raw" / "melody" / "maestro"
DEST_DRUMS_GMD = ROOT / "data" / "midi_raw" / "drums" / "gmd"
DEST_DRUMS_EGMD = ROOT / "data" / "midi_raw" / "drums" / "egmd"

# 다운로드할 데이터셋 URL 목록
URLS = {
    "maestro_v3_midi": "https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0-midi.zip",
    "gmd_midionly": "https://storage.googleapis.com/magentadata/datasets/groove/groove-v1.0.0-midionly.zip",
    # 선택 사항:
    "e_gmd_midionly": "https://storage.googleapis.com/magentadata/datasets/e-gmd/e-gmd-v1.0.0-midi.zip",
}


# 파일 다운로드 함수 (진행률 표시 포함)
def download(url: str, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)  # 대상 폴더가 없으면 생성

    class TqdmUpTo(tqdm):  # tqdm을 상속받아 파일 크기 기반 진행률 표시
        def update_to(self, b=1, bsize=1, tsize=None):
            if tsize is not None:
                self.total = tsize
            self.update(b * bsize - self.n)

    # urlretrieve를 사용하여 파일을 다운로드하고 reporthook으로 진행률 업데이트
    with TqdmUpTo(unit="B", unit_scale=True, unit_divisor=1024, miniters=1, desc=out.name) as t:
        urllib.request.urlretrieve(url, out, reporthook=t.update_to)


# MIDI 파일 압축 해제 함수
def extract_midis(zip_path: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)  # 대상 폴더가 없으면 생성
    TMP.mkdir(parents=True, exist_ok=True)  # 임시 폴더 생성
    with zipfile.ZipFile(zip_path) as z:  # zip 파일 열기
        for info in z.infolist():  # zip 파일 내 모든 파일 정보 순회
            name = info.filename.lower()
            if name.endswith(".mid") or name.endswith(".midi"):  # MIDI 파일인 경우
                # 각 MIDI 파일을 dest 폴더에 저장 (디렉터리 구조 평탄화)
                raw = z.read(info)
                out = dest / Path(info.filename).name
                with open(out, "wb") as f:
                    f.write(raw)


if __name__ == "__main__":
    # 1) GMD (드럼) 다운로드 및 압축 해제
    gmd_zip = DL / "groove-v1.0.0-midionly.zip"
    if not gmd_zip.exists():  # 파일이 없으면 다운로드
        download(URLS["gmd_midionly"], gmd_zip)
    extract_midis(gmd_zip, DEST_DRUMS_GMD)  # MIDI 압축 해제

    # 2) MAESTRO v3 MIDI-only (멜로디/화성) 다운로드 및 압축 해제
    maestro_zip = DL / "maestro-v3.0.0-midi.zip"
    if not maestro_zip.exists():  # 파일이 없으면 다운로드
        download(URLS["maestro_v3_midi"], maestro_zip)
    extract_midis(maestro_zip, DEST_MELODY)  # MIDI 압축 해제

    # 3) (선택 사항) E-GMD 드럼 다운로드 및 압축 해제
    egmd_zip = DL / "e-gmd-v1.0.0-midi.zip"
    # 활성화하려면 주석 해제:
    # if not egmd_zip.exists():
    #     download(URLS["e_gmd_midionly"], egmd_zip)
    # extract_midis(egmd_zip, DEST_DRUMS_EGMD)

    print("Done. MIDIs in:", DEST_DRUMS_GMD, DEST_MELODY)  # 완료 메시지 및 MIDI 파일 경로 출력
