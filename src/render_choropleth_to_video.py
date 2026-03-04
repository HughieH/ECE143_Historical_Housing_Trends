import os
import numpy as np
import pandas as pd
import subprocess
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---- Video & Plot settings ----
DATA_CSV = "../output/state_growth_rates.csv"
OUT_DIR  = "frames"
OUT_MP4  = "state_growth_rates_choropleth_animation.mp4"
FPS      = 12
SCALE    = 2          
WIDTH    = 1100
HEIGHT   = 600

os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_CSV)

FIXED_MIN, FIXED_MAX = -20, 20  # or compute from df, see below

fig = px.choropleth(
    df,
    locations="Abbreviation",
    locationmode="USA-states",
    color="Annual Change (%)",
    color_continuous_scale="RdYlGn",
    range_color=[FIXED_MIN, FIXED_MAX],   # fixed for all frames
    scope="usa",
    animation_frame="Year",
    title="Annual House Price Change by State",
)

fig.update_layout(coloraxis=dict(cmin=FIXED_MIN, cmax=FIXED_MAX))

# Optional: add state abbreviation labels if your df has Longitude/Latitude columns
label_trace = None
if {"Longitude", "Latitude"}.issubset(df.columns):
    coords = df.drop_duplicates(subset="Abbreviation")
    label_trace = go.Scattergeo(
        locationmode="USA-states",
        lon=coords["Longitude"],
        lat=coords["Latitude"],
        text=coords["Abbreviation"],
        mode="text",
        textfont=dict(size=8, color="white"),
        showlegend=False,
        hoverinfo="skip",
    )
    fig.add_trace(label_trace)
    for fr in fig.frames:
        fr.data = (*fr.data, label_trace)

fig.update_layout(margin=dict(r=0, t=60, l=0, b=0), width=WIDTH, height=HEIGHT)

# Sort frames by year (numeric if possible)
frame_names = [f.name for f in fig.frames]
try:
    order = np.argsort([float(x) for x in frame_names])
except Exception:
    order = np.argsort(frame_names)

# Remove animation UI (slider + play/stop buttons)
fig.update_layout(sliders=None, updatemenus=None)

if fig.layout.updatemenus:
    fig.update_layout(updatemenus=[dict(visible=False) for _ in fig.layout.updatemenus])

if fig.layout.sliders:
    fig.update_layout(sliders=[dict(visible=False) for _ in fig.layout.sliders])

# Render frames to PNG (requires: pip install -U kaleido)
for k, idx in enumerate(order):
    fr = fig.frames[int(idx)]
    fig.update(data=fr.data)
    fig.update_layout(title=f"Annual House Price Change by State (Year={fr.name})")
    fig.write_image(os.path.join(OUT_DIR, f"frame_{k:04d}.png"), scale=SCALE)
    print(f"frame_{k:04d}.png rendered")
    

print(f"Rendered {len(order)} frames into {OUT_DIR}/")

frames_dir = Path(OUT_DIR)
pattern = str(frames_dir / "frame_%04d.png")

cmd = [
    "ffmpeg",
    "-y",
    "-framerate", str(FPS),
    "-i", pattern,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-crf", "18",
    OUT_MP4,
]

try:
    subprocess.run(cmd, check=True)
    print("Wrote", OUT_MP4)
except FileNotFoundError:
    raise SystemExit("ffmpeg not found on PATH. Install it (e.g., brew install ffmpeg).")
except subprocess.CalledProcessError as e:
    raise SystemExit(f"ffmpeg failed (exit {e.returncode}).")
