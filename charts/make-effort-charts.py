#!/usr/bin/env python3
"""Article figures for the Opus 5 effort sweep. Values come from results.jsonl
filtered on model==claude-opus-5 and finishedAt > effort-sweep-cutoff.txt."""

import json
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = pathlib.Path(__file__).parent

# 1 CSS px = 0.72 pt, so a figure inch is 100 CSS px and mark specs stay honest at 2x.
PX = 0.72

SURFACE = "#ffffff"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

# Entity-stable across every figure: hidden is always blue, available always orange.
HIDDEN = "#0080FF"
AVAILABLE = "#eb6834"

LEVELS = ["low", "medium", "high", "xhigh", "max"]
X = range(len(LEVELS))

SOLVED_HIDDEN = [0, 0, 1, 3, 8]
N_HIDDEN = 13
SOLVED_AVAILABLE = [18, 18, 18, 18, 18]
N_AVAILABLE = 18

COST_AVAILABLE = [0.1270, 0.1464, 0.1524, 0.2013, 0.2416]
COST_HIDDEN = [0.0748, 0.0818, 0.1113, 0.2038, 0.3865]
SECS_AVAILABLE = [21.6, 27.9, 26.5, 34.4, 50.1]
SECS_HIDDEN = [24.6, 23.3, 37.1, 53.2, 130.7]

MAX_TOKENS = json.loads((OUT.parent / "results/max-blind-tokens.json").read_text())

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Avenir Next", "DejaVu Sans"],
    "font.size": 13 * PX,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS,
    "axes.linewidth": 1 * PX,
    "text.color": INK,
    "axes.labelcolor": INK_2,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "xtick.major.size": 0,
    "ytick.major.size": 0,
    "legend.frameon": False,
})


def chrome(ax, ygrid=True):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    if ygrid:
        ax.grid(axis="y", color=GRID, linewidth=1 * PX, linestyle="-")
        ax.set_axisbelow(True)


def series(ax, ys, color, label):
    ax.plot(
        list(X), ys,
        color=color, linewidth=2 * PX, solid_capstyle="round", solid_joinstyle="round",
        marker="o", markersize=8 * PX, markerfacecolor=color,
        markeredgecolor=SURFACE, markeredgewidth=2 * PX,
        label=label, clip_on=False, zorder=3,
    )


def levels_axis(ax, headroom=0.72, xlabel="reasoning effort"):
    ax.set_xticks(list(X))
    ax.set_xticklabels(LEVELS)
    ax.set_xlim(-0.28, len(LEVELS) - headroom)
    if xlabel:
        ax.set_xlabel(xlabel, labelpad=8 * PX)


def titles(fig, title, note):
    fig.text(0.012, 0.965, title, color=INK, fontsize=15 * PX,
             fontweight="bold", va="top")
    fig.text(0.012, 0.018, note, color=MUTED, fontsize=11 * PX, va="bottom")


# Figure 1 — solve rate by effort, both information regimes.
fig, ax = plt.subplots(figsize=(7.4, 4.3))
chrome(ax)

rate_hidden = [100 * s / N_HIDDEN for s in SOLVED_HIDDEN]
rate_available = [100 * s / N_AVAILABLE for s in SOLVED_AVAILABLE]

series(ax, rate_available, AVAILABLE, "Tests available")
series(ax, rate_hidden, HIDDEN, "Tests hidden")

ax.set_ylim(-4, 108)
ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_ylabel("solve rate", labelpad=10 * PX)
levels_axis(ax)

ax.annotate(
    "18 of 18 at every level", xy=(2, 100), xytext=(2, 92),
    ha="center", color=INK_2, fontsize=12 * PX,
)
ax.annotate(
    "0 of 13", xy=(0, 0), xytext=(0.06, 7),
    ha="left", color=INK_2, fontsize=12 * PX,
)
ax.annotate(
    "8 of 13", xy=(4, rate_hidden[-1]), xytext=(3.92, rate_hidden[-1] + 7),
    ha="right", color=INK, fontsize=12 * PX, fontweight="bold",
)

ax.legend(loc="center left", bbox_to_anchor=(0.015, 0.62), fontsize=12 * PX,
          labelcolor=INK_2, handlelength=1.6, handletextpad=0.6)
titles(fig,
       "Reasoning effort changes nothing until the agent cannot test its own work",
       "Claude Opus 5, one bug family. Tests available: 6 tasks x 3 trials per level. "
       "Tests hidden: 13 trials per level.")
fig.tight_layout(rect=(0, 0.045, 1, 0.9))
fig.savefig(OUT / "effort-01-solve-rate.png", dpi=200)
plt.close(fig)


# Figure 2 — what the dial costs, in dollars and in seconds.
fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.9))

for ax, (ya, yh, ylab, fmt, ticks, labels) in zip(axes, [
    (COST_AVAILABLE, COST_HIDDEN, "cost per run",
     lambda v, _: f"${v:.2f}", [0, 0.1, 0.2, 0.3, 0.4], ("$0.24", "$0.39")),
    (SECS_AVAILABLE, SECS_HIDDEN, "median runtime",
     lambda v, _: f"{v:.0f}s", [0, 30, 60, 90, 120, 150], ("50s", "131s")),
]):
    chrome(ax)
    series(ax, ya, AVAILABLE, "Tests available")
    series(ax, yh, HIDDEN, "Tests hidden")
    ax.set_yticks(ticks)
    ax.set_ylim(0, ticks[-1] * 1.06)
    ax.yaxis.set_major_formatter(FuncFormatter(fmt))
    ax.set_ylabel(ylab, labelpad=10 * PX)
    levels_axis(ax, headroom=0.42, xlabel=None)
    for value, text, color in ((ya[-1], labels[0], AVAILABLE),
                               (yh[-1], labels[1], HIDDEN)):
        ax.annotate(text, xy=(4.12, value), va="center", ha="left",
                    color=INK_2, fontsize=11 * PX)

axes[0].legend(loc="upper left", bbox_to_anchor=(-0.02, 1.04), fontsize=11 * PX,
               labelcolor=INK_2, handlelength=1.6, handletextpad=0.6)
fig.supxlabel("reasoning effort", color=INK_2, fontsize=13 * PX, y=0.135)
titles(fig,
       "Turning the dial up always costs more, whether or not it buys anything",
       "Cost per run is per-trace billing. From low to max: 1.9x the price with tests "
       "available for an identical 18 of 18, 5.2x without them.")
fig.tight_layout(rect=(0, 0.10, 1, 0.88))
fig.savefig(OUT / "effort-02-cost-and-latency.png", dpi=200)
plt.close(fig)


# Figure 3 — inside max effort, the blind runs that failed spent more.
fig, ax = plt.subplots(figsize=(7.4, 2.9))
chrome(ax, ygrid=False)
ax.grid(axis="x", color=GRID, linewidth=1 * PX)
ax.set_axisbelow(True)
ax.spines["bottom"].set_visible(False)

rows = [("Failed", MAX_TOKENS["failed"], 0), ("Solved", MAX_TOKENS["solved"], 1)]
for label, vals, y in rows:
    ax.plot(vals, [y] * len(vals), linestyle="none",
            marker="o", markersize=9 * PX, markerfacecolor=HIDDEN,
            markeredgecolor=SURFACE, markeredgewidth=2 * PX, clip_on=False, zorder=3)
    med = sorted(vals)[len(vals) // 2] if len(vals) % 2 else \
        (sorted(vals)[len(vals) // 2 - 1] + sorted(vals)[len(vals) // 2]) / 2
    ax.plot([med, med], [y - 0.26, y + 0.26], color=INK, linewidth=2 * PX, zorder=4)
    ax.annotate(f"median {med:,.0f}", xy=(med, y + 0.32), ha="center",
                color=INK_2, fontsize=11 * PX)

ax.set_yticks([0, 1])
ax.set_yticklabels([f"Failed ({len(MAX_TOKENS['failed'])} runs)",
                    f"Solved ({len(MAX_TOKENS['solved'])} runs)"])
ax.set_ylim(-0.6, 1.75)
ax.set_xlim(3000, 22500)
ax.set_xticks([5000, 10000, 15000, 20000])
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_xlabel("output tokens per run", labelpad=8 * PX)
titles(fig,
       "Within max effort, the blind runs that failed spent the most",
       "13 blind trials at max effort, one dot per run. The distributions overlap, "
       "so read this as suggestive rather than established.")
fig.tight_layout(rect=(0, 0.10, 1, 0.87))
fig.savefig(OUT / "effort-03-tokens-by-outcome.png", dpi=200)
plt.close(fig)

# Hero — the solve-rate chart at the blog's 2280x1096 card ratio.
fig, ax = plt.subplots(figsize=(11.4, 5.48))
chrome(ax)
series(ax, rate_available, AVAILABLE, "Tests available")
series(ax, rate_hidden, HIDDEN, "Tests hidden")
ax.set_ylim(-4, 108)
ax.set_yticks([0, 25, 50, 75, 100])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_ylabel("solve rate", labelpad=10 * PX)
levels_axis(ax)
ax.annotate("18 of 18 at every level", xy=(2, 100), xytext=(2, 92),
            ha="center", color=INK_2, fontsize=13 * PX)
ax.annotate("0 of 13", xy=(0, 0), xytext=(0.06, 7),
            ha="left", color=INK_2, fontsize=13 * PX)
ax.annotate("8 of 13", xy=(4, rate_hidden[-1]), xytext=(3.94, rate_hidden[-1] + 6),
            ha="right", color=INK, fontsize=13 * PX, fontweight="bold")
ax.legend(loc="center left", bbox_to_anchor=(0.015, 0.60), fontsize=13 * PX,
          labelcolor=INK_2, handlelength=1.6, handletextpad=0.6)
fig.text(0.012, 0.955, "Effort substitutes for verification", color=INK,
         fontsize=19 * PX, fontweight="bold", va="top")
fig.text(0.012, 0.885,
         "Claude Opus 5 across all five reasoning-effort levels, 155 runs",
         color=INK_2, fontsize=13 * PX, va="top")
fig.tight_layout(rect=(0, 0.01, 1, 0.85))
fig.savefig(OUT / "effort-00-hero.png", dpi=200)
plt.close(fig)

print("wrote:")
for p in sorted(OUT.glob("effort-0*.png")):
    print(" ", p.name)
