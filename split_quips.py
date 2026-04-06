import subprocess, re, os

FFMPEG  = r"C:\Users\nasha\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
FFPROBE = r"C:\Users\nasha\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffprobe.exe"
DOWNLOADS = r"C:\Users\nasha\Downloads"
OUT_DIR   = r"C:\Users\nasha\OneDrive\Desktop\My Projects\chessmate\static\audio\quips"

FILES = [
    "Review_blunder", "Review_mistake", "Review_best", "Review_book",
    "Review_good", "Review_load", "Opp_blunder", "Opp_mistake",
    "Opp_best", "Opp_book", "Opp_good", "Sacrifice_queen", "Sacrifice_rook"
]

for name in FILES:
    src = os.path.join(DOWNLOADS, name + ".m4a")
    base = name.lower()

    # Get duration
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", src],
                       capture_output=True, text=True)
    duration = float(r.stdout.strip())

    # Detect silences >= 0.8s
    r2 = subprocess.run([FFMPEG, "-i", src, "-af",
                         "silencedetect=noise=-35dB:d=0.8", "-f", "null", "-"],
                        capture_output=True, text=True)
    output = r2.stderr

    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", output)]
    ends   = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", output)]
    silences = list(zip(starts, ends))

    if len(silences) < 2:
        print(f"WARNING: {name} - not enough silences detected ({len(silences)}), skipping")
        continue

    mids = [(s + e) / 2 for s, e in silences]

    t1_target = duration / 3
    t2_target = 2 * duration / 3

    split1 = min(mids, key=lambda m: abs(m - t1_target))
    remaining = [m for m in mids if m > split1 + 2]
    if not remaining:
        print(f"WARNING: {name} - couldn't find 2nd split point")
        continue
    split2 = min(remaining, key=lambda m: abs(m - t2_target))

    print(f"{name}: dur={duration:.1f}s  split1={split1:.2f}s  split2={split2:.2f}s")

    for i, (start, end) in enumerate([(0, split1), (split1, split2), (split2, duration)], 1):
        out = os.path.join(OUT_DIR, f"{base}_{i}.m4a")
        subprocess.run([FFMPEG, "-y", "-i", src,
                        "-ss", str(start), "-to", str(end),
                        "-c", "copy", out],
                       capture_output=True)
        print(f"  -> {base}_{i}.m4a  ({start:.2f}s - {end:.2f}s)")

print("Done.")