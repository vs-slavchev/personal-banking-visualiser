import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

HEADER_COLOR = '#2c3e50'
HEADER_TEXT  = 'white'
ROW_EVEN     = '#f2f4f5'
ROW_ODD      = 'white'
ACCENT       = '#2980b9'


def _style_table(table, n_data_rows, n_cols, col_widths=None):
    """Apply consistent styling to a matplotlib Table object."""
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)

    for (row, col), cell in table.get_celld().items():
        cell.set_linewidth(0)
        if row == 0:
            cell.set_facecolor(HEADER_COLOR)
            cell.set_text_props(color=HEADER_TEXT, fontweight='bold')
        else:
            cell.set_facecolor(ROW_EVEN if row % 2 == 0 else ROW_ODD)
        if col_widths:
            cell.set_width(col_widths[col] if col >= 0 else col_widths[0])


def add_title_page(pdf, df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])

    start       = df['date'].min().strftime('%B %Y')
    end         = df['date'].max().strftime('%B %Y')
    n_months    = df['date'].dt.to_period('M').nunique()
    n_tx        = len(df)
    total_eur   = df['amount_eur'].sum()

    fig = plt.figure(figsize=(8.27, 11.69))
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # accent bar at top
    ax.add_patch(mpatches.FancyBboxPatch((0, 0.88), 1, 0.12,
                 boxstyle='square,pad=0', facecolor=HEADER_COLOR, zorder=2))

    ax.text(0.5, 0.935, 'Personal Banking Report',
            ha='center', va='center', fontsize=26, fontweight='bold',
            color='white', zorder=3)

    # period & coverage
    ax.text(0.5, 0.76, f'{start}  –  {end}',
            ha='center', va='center', fontsize=18, color='#2c3e50')
    ax.text(0.5, 0.69, f'{n_months} months  ·  {n_tx:,} transactions',
            ha='center', va='center', fontsize=12, color='#7f8c8d')

    # divider
    ax.axhline(0.63, xmin=0.2, xmax=0.8, color='#bdc3c7', linewidth=1)

    # total
    ax.text(0.5, 0.565, 'Total spent',
            ha='center', va='center', fontsize=11, color='#7f8c8d')
    ax.text(0.5, 0.505, f'€{total_eur:,.2f}',
            ha='center', va='center', fontsize=30, fontweight='bold', color=ACCENT)

    pdf.savefig(fig)
    plt.close()


def add_stats_page(pdf, df):
    df = df.copy()
    df['date']  = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m')

    monthly_totals     = df.groupby('month')['amount_eur'].sum()
    monthly_totals_noi = df[df['category'] != 'investment'].groupby('month')['amount_eur'].sum()
    cat_monthly        = df.groupby(['month', 'category'])['amount_eur'].sum().unstack(fill_value=0)

    fig = plt.figure(figsize=(8.27, 11.69))
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # page title bar
    ax.add_patch(mpatches.FancyBboxPatch((0, 0.93), 1, 0.07,
                 boxstyle='square,pad=0', facecolor=HEADER_COLOR))
    ax.text(0.5, 0.965, 'Summary Statistics',
            ha='center', va='center', fontsize=16, fontweight='bold', color='white')

    # ── Monthly spend ──────────────────────────────────────────────
    ax.text(0.06, 0.895, 'Monthly spend', fontsize=12, fontweight='bold', color='#2c3e50')

    def _fmt(series, idx_fn):
        val = idx_fn(series)
        month = series.idxmin() if idx_fn == min else series.idxmax()
        return f'€{val:,.2f}  ({month})'

    monthly_rows = [
        ['Average',
         f'€{monthly_totals.mean():,.2f}',
         f'€{monthly_totals_noi.mean():,.2f}'],
        ['Median',
         f'€{monthly_totals.median():,.2f}',
         f'€{monthly_totals_noi.median():,.2f}'],
        ['Min',
         f'€{monthly_totals.min():,.2f}  ({monthly_totals.idxmin()})',
         f'€{monthly_totals_noi.min():,.2f}  ({monthly_totals_noi.idxmin()})'],
        ['Max',
         f'€{monthly_totals.max():,.2f}  ({monthly_totals.idxmax()})',
         f'€{monthly_totals_noi.max():,.2f}  ({monthly_totals_noi.idxmax()})'],
    ]

    ax_m = fig.add_axes([0.06, 0.70, 0.88, 0.185])
    ax_m.axis('off')
    t_m = ax_m.table(
        cellText=monthly_rows,
        colLabels=['Metric', 'All categories', 'Excl. investment'],
        loc='upper left',
        cellLoc='left',
    )
    t_m.scale(1, 1.6)
    _style_table(t_m, len(monthly_rows), 3, col_widths={0: 0.20, 1: 0.40, 2: 0.40})

    # ── Per-category spend ─────────────────────────────────────────
    ax.text(0.06, 0.675, 'Spend by category  (EUR per month)', fontsize=12, fontweight='bold', color='#2c3e50')

    order = cat_monthly.mean().sort_values(ascending=False).index
    cat_rows = []
    for cat in order:
        col = cat_monthly[cat]
        cat_rows.append([
            cat,
            f'€{col.mean():,.2f}',
            f'€{col.median():,.2f}',
            f'€{col.min():,.2f}',
            f'€{col.max():,.2f}',
        ])

    ax_c = fig.add_axes([0.06, 0.27, 0.88, 0.395])
    ax_c.axis('off')
    t_c = ax_c.table(
        cellText=cat_rows,
        colLabels=['Category', 'Average', 'Median', 'Min', 'Max'],
        loc='upper left',
        cellLoc='center',
    )
    t_c.scale(1, 1.6)
    # make category column left-aligned
    for (row, col), cell in t_c.get_celld().items():
        if col == 0 and row > 0:
            cell.set_text_props(ha='left')
    _style_table(t_c, len(cat_rows), 5,
                 col_widths={0: 0.28, 1: 0.18, 2: 0.18, 3: 0.18, 4: 0.18})

    pdf.savefig(fig)
    plt.close()


_UNCATEGORISED_ROWS_PER_PAGE = 25


def add_uncategorised_pages(pdf, df):
    """Append pages listing all 'other' transactions sorted by amount descending.
    Returns the number of pages added."""
    other = (df[df['category'] == 'other']
             .sort_values('amount_eur', ascending=False)
             .copy())

    if other.empty:
        return 0

    other['date']        = pd.to_datetime(other['date']).dt.strftime('%Y-%m-%d')
    other['amount_eur']  = other['amount_eur'].map('€{:.2f}'.format)
    other['description'] = other['description'].str.slice(0, 65)

    rows    = other[['date', 'amount_eur', 'description']].values.tolist()
    n_pages = math.ceil(len(rows) / _UNCATEGORISED_ROWS_PER_PAGE)

    for page_idx in range(n_pages):
        chunk = rows[page_idx * _UNCATEGORISED_ROWS_PER_PAGE:
                     (page_idx + 1) * _UNCATEGORISED_ROWS_PER_PAGE]

        fig = plt.figure(figsize=(8.27, 11.69))
        ax  = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # Header bar
        ax.add_patch(mpatches.FancyBboxPatch((0, 0.93), 1, 0.07,
                     boxstyle='square,pad=0', facecolor=HEADER_COLOR))
        title = 'Uncategorised Transactions'
        if n_pages > 1:
            title += f'  ({page_idx + 1} / {n_pages})'
        ax.text(0.5, 0.965, title,
                ha='center', va='center', fontsize=16, fontweight='bold', color='white')

        ax_t = fig.add_axes([0.02, 0.01, 0.96, 0.90])
        ax_t.axis('off')
        t = ax_t.table(
            cellText=chunk,
            colLabels=['Date', 'Amount', 'Description'],
            loc='upper left',
            cellLoc='left',
        )
        t.auto_set_font_size(False)
        t.set_fontsize(8.5)
        t.scale(1, 1.4)

        for (row, col), cell in t.get_celld().items():
            cell.set_linewidth(0)
            if row == 0:
                cell.set_facecolor(HEADER_COLOR)
                cell.set_text_props(color=HEADER_TEXT, fontweight='bold')
            else:
                cell.set_facecolor(ROW_EVEN if row % 2 == 0 else ROW_ODD)
            if col == 0:
                cell.set_width(0.13)
            elif col == 1:
                cell.set_width(0.13)
            else:
                cell.set_width(0.74)

        pdf.savefig(fig)
        plt.close()

    return n_pages


# Y-centres of the four TOC entry rows in axes coords (0=bottom, 1=top).
# Exported so app.py can compute link annotation rectangles precisely.
TOC_ENTRY_Y_CENTERS = [0.77, 0.62, 0.47, 0.32]
TOC_ENTRY_HALF_H    = 0.055   # half-height of each clickable row


def add_toc_page(pdf, sections):
    """Draw the table of contents page.

    sections: list of (label, display_page_1indexed) – one entry per section,
              in the same order as TOC_ENTRY_Y_CENTERS.
    """
    fig = plt.figure(figsize=(8.27, 11.69))
    ax  = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Header bar
    ax.add_patch(mpatches.FancyBboxPatch((0, 0.93), 1, 0.07,
                 boxstyle='square,pad=0', facecolor=HEADER_COLOR))
    ax.text(0.5, 0.965, 'Table of Contents',
            ha='center', va='center', fontsize=16, fontweight='bold', color='white')

    for i, (label, page_num) in enumerate(sections):
        yc = TOC_ENTRY_Y_CENTERS[i]
        h  = TOC_ENTRY_HALF_H

        # Entry background
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.05, yc - h), 0.90, 2 * h,
            boxstyle='round,pad=0.008',
            facecolor=ROW_EVEN, edgecolor='#d0d5d8', linewidth=0.5,
        ))

        # Numbered circle
        ax.add_patch(plt.Circle((0.115, yc), 0.028, color=ACCENT, zorder=2))
        ax.text(0.115, yc, str(i + 1),
                ha='center', va='center', fontsize=10,
                color='white', fontweight='bold', zorder=3)

        # Section label
        ax.text(0.175, yc, label,
                ha='left', va='center', fontsize=13, color='#2c3e50')

        # Dotted connector
        ax.plot([0.58, 0.83], [yc, yc], ':', color='#bdc3c7', linewidth=1.2)

        # Page number
        ax.text(0.865, yc, f'p. {page_num}',
                ha='left', va='center', fontsize=13,
                color=ACCENT, fontweight='bold')

    pdf.savefig(fig)
    plt.close()
