"""Reusable APA-style bar-chart layout for the thesis figures.

Saved layout (as established on the gender chart):
  * light grey bars (#D3D3D3) with black outlines, width 0.62
  * top & right spines removed
  * "Frequency" y-axis label, no x-axis title
  * n + % data labels above each bar
  * Liberation Sans (Arial-metric), exported as PNG/PDF/SVG at 300 dpi

Usage:
    import apa_barchart as apa
    fig, ax = apa.bar_chart(categories, counts, N)   # ylabel defaults to "Frequency"
    apa.save(fig, "/path/to/figXX_name")             # writes .png/.pdf/.svg
"""
import math
import matplotlib as mpl
import matplotlib.pyplot as plt

BAR_COLOR = '#D3D3D3'
EDGE_COLOR = 'black'
FONT_STACK = ['Liberation Sans', 'Arial', 'DejaVu Sans']


def apply_apa_style():
    """Set the global rcParams for the APA look."""
    mpl.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': FONT_STACK,
        'font.size': 11,
        'axes.edgecolor': 'black',
        'axes.linewidth': 0.8,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
    })


def bar_chart(categories, counts, N, ylabel='Frequency', ytick_step=20,
              figsize=(6.5, 4.5), bar_color=BAR_COLOR, show_pct=True):
    """Build a styled bar chart and return (fig, ax).

    categories : x tick labels
    counts     : bar heights (frequencies)
    N          : total sample size, used for the % data labels
    ylabel     : y-axis title (None to omit); x-axis stays unlabeled
    ytick_step : spacing of y ticks; y range auto-scales with headroom for labels
    show_pct   : if True, label bars as "n\\n(p.p%)"; else just "n"
    """
    apply_apa_style()
    fig, ax = plt.subplots(figsize=figsize)
    x = range(len(categories))
    bars = ax.bar(x, counts, width=0.62, color=bar_color,
                  edgecolor=EDGE_COLOR, linewidth=0.8, zorder=3)

    if ylabel:
        ax.set_ylabel(ylabel, labelpad=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(categories)

    top_tick = math.ceil(max(counts) / ytick_step) * ytick_step
    ax.set_ylim(0, top_tick * 1.10)
    ax.set_yticks(range(0, top_tick + 1, ytick_step))
    ax.tick_params(axis='both', length=4)

    offset = max(counts) * 0.015
    for rect, n_ in zip(bars, counts):
        label = f'{n_}\n({n_ / N * 100:.1f}%)' if show_pct else f'{n_}'
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + offset,
                label, ha='center', va='bottom', fontsize=9.5)

    fig.tight_layout()
    return fig, ax


GREYS = ['#D3D3D3', '#808080', '#4D4D4D', '#BFBFBF']


def grouped_bar_chart(group_labels, series, ylabel='Mean', errors=None,
                      figsize=(6.5, 4.5), colors=None, value_fmt='{:.2f}'):
    """Grouped bar chart in the same APA style.

    group_labels : x-axis categories (e.g., conditions)
    series       : list of (name, values) tuples, one per legend group
    errors       : optional list of error arrays (same shape as series values)
    Returns (fig, ax).
    """
    import numpy as np
    apply_apa_style()
    fig, ax = plt.subplots(figsize=figsize)
    ng, n = len(series), len(group_labels)
    x = np.arange(n)
    bw = 0.7 / ng
    cols = colors or GREYS[:ng]
    ymax = 0
    for j, (name, vals) in enumerate(series):
        off = (j - (ng - 1) / 2) * bw
        err = errors[j] if errors else None
        bars = ax.bar(x + off, vals, bw * 0.95, label=name, color=cols[j],
                      edgecolor=EDGE_COLOR, linewidth=0.8, zorder=3,
                      yerr=err, capsize=3, error_kw=dict(lw=0.8))
        for rect, v, i in zip(bars, vals, range(n)):
            e = (err[i] if err is not None else 0)
            ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + e,
                    value_fmt.format(v), ha='center', va='bottom', fontsize=8.5)
            ymax = max(ymax, rect.get_height() + e)
    ax.set_ylabel(ylabel, labelpad=8)
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels)
    ax.set_ylim(0, ymax * 1.18)
    ax.tick_params(axis='both', length=4)
    ax.legend(frameon=False, fontsize=9.5, loc='upper right')
    fig.tight_layout()
    return fig, ax


def save(fig, path_stem):
    """Save a figure as PNG, PDF and SVG (300 dpi) at the given path stem."""
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(f'{path_stem}.{ext}', dpi=300, bbox_inches='tight')
