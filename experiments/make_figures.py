"""
Generate thesis figures from the saved experiment result files.

Usage:
    python experiments/make_figures.py

Figures are written to results/figures/ as PNG (300 dpi) and PDF.
All numbers are computed from the JSON result files, nothing is typed in.
"""

import glob
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

project_dir = Path(__file__).resolve().parent.parent
results_dir = project_dir / "results"
figures_dir = results_dir / "figures"
figures_dir.mkdir(exist_ok=True)

# Validated palette (light): blue / orange, plus a neutral for "no answer".
BLUE, ORANGE, NEUTRAL = "#2a78d6", "#eb6834", "#c9c8c1"
TEXT, TEXT_2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.edgecolor": MUTED, "axes.labelcolor": TEXT_2, "axes.titlecolor": TEXT,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "xtick.color": TEXT_2, "ytick.color": TEXT_2,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def load(pattern):
    files = [f for f in sorted(glob.glob(str(results_dir / pattern)))
             if json.load(open(f))["summary"]["reps"] == 3]
    if not files:
        raise FileNotFoundError(pattern)
    return json.load(open(files[-1]))["records"]


def outcome(records):
    n = len(records)
    correct = sum(r["correct_lenient"] for r in records)
    answered = sum(r["executed"] for r in records)
    return {
        "n": n,
        "correct": correct / n,
        "wrong": (answered - correct) / n,
        "abstain": (n - answered) / n,
        "latency": sum(r["latency_seconds"] for r in records) / n,
    }


def save(fig, name):
    fig.savefig(figures_dir / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(figures_dir / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


def gridlines(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


# --------------------------------------------------
# Data
# --------------------------------------------------

HOLDOUT = [
    ("A (7B)", "experiment_holdout_definitions_system_A_2*.json"),
    ("C v2 (7B)", "experiment_holdout_definitions_system_C_2*.json"),
    ("C v3 (7B)", "experiment_holdout_definitions_system_C3_2*.json"),
    ("C v3 (7B + 14B reviewer)", "experiment_holdout_definitions_system_C3_review-qwen2.5-14b_*.json"),
    ("A (14B)", "experiment_holdout_definitions_system_A_gen-qwen2.5-14b_*.json"),
    ("C v3 (14B)", "experiment_holdout_definitions_system_C3_gen-qwen2.5-14b_2*.json"),
]
holdout = [(label, outcome(load(p))) for label, p in HOLDOUT]


# --------------------------------------------------
# Figure 1: Experiment 1 vs 2 (development set, 7B)
# --------------------------------------------------

exp = {
    "Exp 1: schema only": [outcome(load(f"experiment_system_{s}_2*.json"))["correct"] for s in "ABC"],
    "Exp 2: + business definitions": [outcome(load(f"experiment_definitions_system_{s}_2*.json"))["correct"] for s in "ABC"],
}
fig, ax = plt.subplots(figsize=(7, 3.6))
systems = ["System A", "System B", "System C (v2)"]
width = 0.36
x = range(len(systems))
for k, (label, values) in enumerate(exp.items()):
    color = NEUTRAL if k == 0 else BLUE
    pos = [i + (k - 0.5) * (width + 0.02) for i in x]
    bars = ax.bar(pos, [v * 100 for v in values], width, color=color, label=label)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v * 100 + 1.5, f"{v:.1%}",
                ha="center", va="bottom", fontsize=9, color=TEXT)
ax.set_xticks(list(x), systems)
ax.set_ylabel("Correct answers (%)")
ax.set_ylim(0, 100)
ax.set_title("Business definitions roughly double accuracy (development set, qwen2.5:7b)")
ax.legend(frameon=False, loc="upper left")
gridlines(ax, "y")
save(fig, "fig1_definitions_effect")


# --------------------------------------------------
# Figure 2: Hold-out outcomes per configuration (stacked 100%)
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 4.2))
labels = [h[0] for h in holdout][::-1]
data = [h[1] for h in holdout][::-1]
y = range(len(labels))
left = [0] * len(labels)
for key, color, name in [("correct", BLUE, "Correct"),
                         ("wrong", ORANGE, "Wrong, returned without warning"),
                         ("abstain", NEUTRAL, "No answer (query failed or system abstained)")]:
    values = [d[key] * 100 for d in data]
    ax.barh(list(y), values, left=left, color=color, label=name,
            edgecolor=SURFACE, linewidth=2, height=0.62)
    for i, v in enumerate(values):
        if v >= 7:
            ax.text(left[i] + v / 2, i, f"{v:.0f}%", ha="center", va="center",
                    fontsize=9, color="white" if color != NEUTRAL else TEXT)
    left = [l + v for l, v in zip(left, values)]
ax.set_yticks(list(y), labels)
ax.set_xlim(0, 100)
ax.set_xlabel("Share of 60 hold-out evaluations (%)")
ax.set_title("Hold-out results: model size matters most; recovery helps a capable model")
ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.45, -0.16))
save(fig, "fig2_holdout_outcomes")


# --------------------------------------------------
# Figure 3: Accuracy vs latency (cost of reliability)
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(7, 4.2))
for label, d in holdout:
    ax.scatter(d["latency"], d["correct"] * 100, s=60, color=BLUE,
               edgecolor=SURFACE, linewidth=2, zorder=3)
    if "reviewer" in label:
        offset, ha = (-8, -4), "right"
    else:
        offset, ha = (6, 4), "left"
    ax.annotate(label, (d["latency"], d["correct"] * 100), textcoords="offset points",
                xytext=offset, ha=ha, fontsize=9, color=TEXT_2)
ax.set_xlabel("Average latency per question (seconds)")
ax.set_ylabel("Correct answers (%)")
ax.set_ylim(30, 100)
ax.set_xlim(0, 36)
ax.set_title("Accuracy versus latency on the hold-out set")
gridlines(ax, "both")
save(fig, "fig3_accuracy_vs_latency")


# --------------------------------------------------
# Figure 4: Fixed vs broken answers relative to the matching baseline
# --------------------------------------------------

def fixed_lost(system_pattern, baseline_pattern):
    sys_r, base_r = load(system_pattern), load(baseline_pattern)
    base = {(r["rep"], r["id"]): r["correct_lenient"] for r in base_r}
    fixed = sum(r["correct_lenient"] and not base[(r["rep"], r["id"])] for r in sys_r)
    lost = sum(not r["correct_lenient"] and base[(r["rep"], r["id"])] for r in sys_r)
    return fixed, lost

pairs = [
    ("C v2 (7B) vs A (7B)", HOLDOUT[1][1], HOLDOUT[0][1]),
    ("C v3 (7B) vs A (7B)", HOLDOUT[2][1], HOLDOUT[0][1]),
    ("C v3 (7B + 14B reviewer) vs A (7B)", HOLDOUT[3][1], HOLDOUT[0][1]),
    ("C v3 (14B) vs A (14B)", HOLDOUT[5][1], HOLDOUT[4][1]),
]
fig, ax = plt.subplots(figsize=(8, 3.6))
names = [p[0] for p in pairs][::-1]
counts = [fixed_lost(p[1], p[2]) for p in pairs][::-1]
y = range(len(names))
ax.barh(list(y), [c[0] for c in counts], color=BLUE, height=0.55, label="Wrong answers fixed")
ax.barh(list(y), [-c[1] for c in counts], color=ORANGE, height=0.55, label="Correct answers broken")
for i, (f, l) in enumerate(counts):
    ax.text(f + 0.3, i, str(f), va="center", fontsize=9, color=TEXT)
    ax.text(-l - 0.3, i, str(l), va="center", ha="right", fontsize=9, color=TEXT)
ax.axvline(0, color=MUTED, linewidth=1)
ax.set_yticks(list(y), names)
ax.set_xlim(-8, 12)
ticks = list(range(-8, 13, 2))
ax.set_xticks(ticks, [str(abs(t)) for t in ticks])
ax.set_xlabel("Number of evaluations (hold-out, 60 per system)")
ax.set_title("What recovery changed compared with its baseline")
ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.4, -0.2))
gridlines(ax, "x")
save(fig, "fig4_fixed_vs_broken")


# --------------------------------------------------
# Table: hold-out summary (CSV, for the thesis table)
# --------------------------------------------------

with open(figures_dir / "holdout_summary.csv", "w") as f:
    f.write("configuration,correct_pct,wrong_without_warning_pct,abstained_pct,avg_latency_s\n")
    for label, d in holdout:
        f.write(f"{label},{d['correct']*100:.1f},{d['wrong']*100:.1f},{d['abstain']*100:.1f},{d['latency']:.1f}\n")
print("saved holdout_summary.csv")
