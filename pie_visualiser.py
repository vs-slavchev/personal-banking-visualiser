import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
from visualiser_colors import category_to_color_dict


def _shorten(text, max_len=22):
    text = str(text).strip()
    return text[:max_len] + "…" if len(text) > max_len else text


def _lighter(color, factor):
    """Blend a color toward white by factor (0 = original, 1 = white)."""
    rgb = mcolors.to_rgb(color)
    return tuple(c + (1 - c) * factor for c in rgb)


def visualize_as_monthly_pies(csv_file_name, pdf=None):
    df = pd.read_csv(csv_file_name, parse_dates=['date'])
    df['date_month'] = df['date'].dt.strftime('%Y-%m')

    for month, month_df in df.groupby('date_month'):
        labels, values, colors = [], [], []
        legend_handles, legend_labels = [], []

        for category, cat_df in month_df.groupby('category'):
            base_color = category_to_color_dict.get(category, 'lightgrey')
            by_desc = (
                cat_df.groupby('description')['amount_eur']
                .sum()
                .sort_values(ascending=False)
            )

            top3 = by_desc.head(3)
            rest_sum = by_desc.iloc[3:].sum()

            shade_factors = [0.0, 0.3, 0.55, 0.72]
            slice_wedges = []
            slice_labels = []
            for i, (desc, amt) in enumerate(top3.items()):
                labels.append(_shorten(desc))
                values.append(amt)
                colors.append(_lighter(base_color, shade_factors[i]))
                slice_wedges.append(None)
                slice_labels.append((_shorten(desc), amt))

            if rest_sum > 0:
                labels.append(f"{category} (rest)")
                values.append(rest_sum)
                colors.append(_lighter(base_color, shade_factors[len(top3)]))
                slice_wedges.append(None)
                slice_labels.append(("rest", rest_sum))

            # category header (blank patch) + sub-items stored for later
            legend_handles.append(('header', category, base_color, slice_labels))

        total = sum(values)
        fig, ax = plt.subplots(figsize=(14, 9))
        wedges, texts, pcts = ax.pie(
            values,
            colors=colors,
            autopct=lambda p: f'{p * total / 100:.0f}' if p > 2 else '',
            pctdistance=0.75,
            startangle=140,
        )
        for t in texts:
            t.set_text('')

        # Build legend: category header + its sub-slices
        wedge_idx = 0
        final_handles, final_labels = [], []
        for item in legend_handles:
            _, category, base_color, sub_items = item
            # Header: bold category name, colored patch
            final_handles.append(mpatches.Patch(color=base_color))
            final_labels.append(f"── {category.upper()} ──")
            for sub_label, amt in sub_items:
                final_handles.append(wedges[wedge_idx])
                final_labels.append(f"   {sub_label}  ({amt:.0f}€)")
                wedge_idx += 1

        ax.legend(
            final_handles,
            final_labels,
            loc='center left',
            bbox_to_anchor=(1.0, 0.5),
            fontsize=7.5,
            frameon=False,
        )
        ax.set_title(f"EUR spent by category in month {month}", pad=16)
        plt.tight_layout()

        if pdf:
            pdf.savefig()
            plt.close()
        else:
            plt.savefig(f"output/pie-chart-{month}.png", format="png")
            plt.show()
            plt.close()


if __name__ == "__main__":
    csv_file = input("Enter the path to the CSV file: ")
    visualize_as_monthly_pies(csv_file)
