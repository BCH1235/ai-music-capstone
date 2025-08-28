import os

import numpy as np
import pretty_midi
import soundfile as sf

# 출력 디렉터리 설정 및 생성
OUT_DIR = os.path.join("render", "out")
os.makedirs(OUT_DIR, exist_ok=True)

# ---- (A) 간단한 MIDI 작성: C 장음계, 120 BPM, 음표당 0.5초
pm = pretty_midi.PrettyMIDI()  # 템포는 연기 테스트에 적합한 기본값 사용
piano = pretty_midi.Instrument(program=0)  # 어쿠스틱 그랜드 피아노
pitches = [60, 62, 64, 65, 67, 69, 71, 72]  # C D E F G A B C 음높이
t = 0.0  # 시작 시간
dur = 0.5  # 음표 길이
for p in pitches:
    # 각 음에 대한 pretty_midi.Note 객체 생성 및 추가
    piano.notes.append(pretty_midi.Note(velocity=80, pitch=p, start=t, end=t + dur))
    t += dur  # 다음 음의 시작 시간 업데이트
pm.instruments.append(piano)
midi_path = os.path.join(OUT_DIR, "test.mid")
pm.write(midi_path)  # MIDI 파일로 저장

# ---- (B) 빠른 WAV 생성 (간단한 사인파 톤; 외부 신디사이저 불필요)
sr = 22050  # 샘플링 레이트
audio = []
for p in pitches:
    freq = 440.0 * (2 ** ((p - 69) / 12))  # MIDI 음높이를 Hz로 변환
    n = int(sr * dur)  # 음표 길이(초) * 샘플링 레이트 = 샘플 수
    x = np.linspace(0, dur, n, endpoint=False)  # 0부터 dur까지 n개의 샘플 포인트 생성
    # 클릭음을 피하기 위한 아주 작은 페이드인/페이드아웃 적용
    env = np.minimum(x / 0.02, 1.0) * np.minimum((dur - x) / 0.02, 1.0)
    tone = 0.2 * np.sin(2 * np.pi * freq * x) * env  # 사인파 생성 및 엔벨로프 적용
    audio.append(tone.astype(np.float32))  # 32비트 부동소수점 형식으로 변환하여 리스트에 추가
audio = np.concatenate(audio, axis=0)  # 모든 오디오 세그먼트를 하나로 합침
wav_path = os.path.join(OUT_DIR, "test.wav")
sf.write(wav_path, audio, sr)  # WAV 파일로 저장

print("Wrote:", midi_path)
print("Wrote:", wav_path)
