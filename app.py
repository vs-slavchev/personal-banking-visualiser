import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from fibank_importer import transform_folder
from matching_categoriser import add_category
from pie_visualiser import visualize_as_monthly_pies
from bar_visualiser import visualize_as_bars
from multiline_chart_visualiser import visualize_as_multiline_chart
from prepare_output_folder import prepare_output_folder
from report_pages import add_title_page, add_stats_page

prepare_output_folder()

input_folder = 'input'
ready_to_import = transform_folder(input_folder)

categorised_expenses = "output/categorised_expenses.csv"
add_category(ready_to_import, categorised_expenses)

df = pd.read_csv(categorised_expenses)
with PdfPages('output/report.pdf') as pdf:
    add_title_page(pdf, df)
    add_stats_page(pdf, df)
    visualize_as_multiline_chart(categorised_expenses, pdf)
    visualize_as_monthly_pies(categorised_expenses, pdf)
    visualize_as_bars(categorised_expenses, pdf)
