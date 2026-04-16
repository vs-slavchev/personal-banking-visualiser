import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from fibank_importer import transform_folder
from matching_categoriser import add_category
from openai_categoriser import categorize_with_openai
from pie_visualiser import visualize_as_monthly_pies
from bar_visualiser import visualize_as_bars
from multiline_chart_visualiser import visualize_as_multiline_chart
from prepare_output_folder import prepare_output_folder
from report_pages import (add_title_page, add_stats_page, add_toc_page,
                           add_uncategorised_pages,
                           TOC_ENTRY_Y_CENTERS, TOC_ENTRY_HALF_H)

prepare_output_folder()

print("=== Step 1: Importing transactions ===")
input_folder = 'input'
ready_to_import = transform_folder(input_folder)

print("\n=== Step 2: Categorizing transactions ===")
categorised_expenses = "output/categorised_expenses.csv"
df = add_category(ready_to_import, categorised_expenses)

print("\n=== Step 3: AI categorization ===")
df = categorize_with_openai(df)
df.to_csv(categorised_expenses, index=False)

df['date'] = pd.to_datetime(df['date'])
months = sorted(df['date'].dt.strftime('%Y-%m').unique())
n_months = len(months)

# Page indices (0-based) for each section
TITLE_PAGE           = 0
STATS_PAGE           = 1
TOC_PAGE             = 2
OVERVIEW_PAGE        = 3
PIES_START           = 4
BARS_START           = 4 + n_months
UNCATEGORISED_START  = 4 + 2 * n_months

# Pre-compute uncategorised page count so the TOC can show the right page number
n_uncategorised = len(df[df['category'] == 'other'])
n_uncategorised_pages = max(1, -(-n_uncategorised // 25))  # ceiling division

PDF_PATH = 'output/report.pdf'

print("\n=== Step 4: Generating PDF report ===")
with PdfPages(PDF_PATH) as pdf:
    print("  Adding title and stats pages...")
    add_title_page(pdf, df)
    add_stats_page(pdf, df)
    add_toc_page(pdf, [
        ('Overview',                    OVERVIEW_PAGE       + 1),
        ('Monthly Pie Charts',          PIES_START          + 1),
        ('Monthly Bar Charts',          BARS_START          + 1),
        ('Uncategorised Transactions',  UNCATEGORISED_START + 1),
    ])
    print("  Rendering charts...")
    visualize_as_multiline_chart(categorised_expenses, pdf)
    visualize_as_monthly_pies(categorised_expenses, pdf)
    visualize_as_bars(categorised_expenses, pdf)
    print("  Adding uncategorised transactions table...")
    add_uncategorised_pages(pdf, df)

print("\n=== Step 5: Adding bookmarks and links ===")
# ── Post-process: add PDF outline (bookmarks) and TOC link annotations ──
reader = PdfReader(PDF_PATH)
writer = PdfWriter()
for page in reader.pages:
    writer.add_page(page)

# Bookmarks – nested outline entries
overview_item      = writer.add_outline_item('Overview',                   OVERVIEW_PAGE)
pies_item          = writer.add_outline_item('Monthly Pie Charts',         PIES_START)
bars_item          = writer.add_outline_item('Monthly Bar Charts',         BARS_START)
uncategorised_item = writer.add_outline_item('Uncategorised Transactions', UNCATEGORISED_START)
for i, month in enumerate(months):
    writer.add_outline_item(month, PIES_START + i, parent=pies_item)
for i, month in enumerate(months):
    writer.add_outline_item(month, BARS_START + i, parent=bars_item)

# Link annotations on the TOC page – derive rect from actual page dimensions
toc_page  = reader.pages[TOC_PAGE]
page_w_pt = float(toc_page.mediabox.width)
page_h_pt = float(toc_page.mediabox.height)

section_targets = [OVERVIEW_PAGE, PIES_START, BARS_START, UNCATEGORISED_START]
for target, yc in zip(section_targets, TOC_ENTRY_Y_CENTERS):
    rect = (
        0.05 * page_w_pt,
        (yc - TOC_ENTRY_HALF_H) * page_h_pt,
        0.95 * page_w_pt,
        (yc + TOC_ENTRY_HALF_H) * page_h_pt,
    )
    writer.add_annotation(TOC_PAGE, Link(rect=rect, target_page_index=target))

with open(PDF_PATH, 'wb') as f:
    writer.write(f)

print(f"\nDone! Report saved to {PDF_PATH}")
