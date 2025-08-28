# 마일스톤 – 2단계 (데이터 및 토크나이저)

데이터
- 다운로더: `data/download_midis.py`
- 폴더 준비 완료: `data/midi_raw/{melody,drums}`, `data/midi_proc/{melody,drums}`

토큰화
- 멜로디: `models/tokenizer.py`, 데모 `data/melody_tokens_demo.py`, 일괄 처리 `data/melody_tokenize_all.py`
- 드럼: `models/tokenizer_drums.py`, 데모 `data/drum_smoke_test.py`, 일괄 처리 `data/drum_tokenize_all.py`

어휘집 및 패키징된 데이터셋
- `data/vocab.json` (토큰으로부터 구축됨)
- JSONL 데이터셋: `data/ds/{melody_train,melody_val,drums_train,drums_val}.jsonl`

프롬프트 → 제어 토큰
- `models/prompt_parser.py` (+ 데모 `data/prompt_parser_demo.py`)

참고 사항
- 생성된 아티팩트 (`data/midi_proc/**`, `data/ds/**`)는 로컬에만 있으며, 코드는 Git에 있습니다.
- 라이선스: MAESTRO (CC BY-NC-SA), Groove/E-GMD (CC BY). 연구/교육용으로만 사용됩니다.