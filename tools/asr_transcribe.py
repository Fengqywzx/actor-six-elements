#!/usr/bin/env python3
"""ASR transcription via faster-whisper -> timestamped text + paragraph text"""
import sys, os, glob
from faster_whisper import WhisperModel

audio = sys.argv[1]
out_prefix = sys.argv[2]
model_size = sys.argv[3] if len(sys.argv) > 3 else "small"
local_dir = sys.argv[4] if len(sys.argv) > 4 else "C:/Users/18612/.workbuddy/models/faster-whisper-small"

import os
print(f"[ASR] loading model {model_size} from {local_dir} ...", flush=True)
model = WhisperModel(local_dir, device="cpu", compute_type="int8")

print(f"[ASR] transcribing {audio} ...", flush=True)
segments, info = model.transcribe(audio, language="zh", vad_filter=True, beam_size=5)
print(f"[ASR] detected language: {info.language} prob={info.language_probability:.2f} dur={info.duration:.0f}s", flush=True)

seg_list = []
with open(out_prefix + "_timestamped.txt", "w", encoding="utf-8") as f:
    for seg in segments:
        ts = f"[{int(seg.start//60):02d}:{int(seg.start%60):02d}]"
        line = f"{ts} {seg.text.strip()}"
        f.write(line + "\n")
        seg_list.append((seg.start, seg.text.strip()))
        print(line, flush=True)

# merge into paragraphs every ~90s
with open(out_prefix + "_full.txt", "w", encoding="utf-8") as f:
    buf, t0 = [], None
    for start, text in seg_list:
        if t0 is None:
            t0 = start
        buf.append(text)
        if start - t0 > 90:
            f.write("".join(buf) + "\n\n")
            buf, t0 = [], None
    if buf:
        f.write("".join(buf) + "\n\n")
print(f"[ASR] done -> {out_prefix}_timestamped.txt / {out_prefix}_full.txt", flush=True)
