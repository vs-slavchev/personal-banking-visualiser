from fibank_importer import transform_csv
from matching_categoriser import add_category
from pie_visualiser import visualize_as_monthly_pies
from bar_visualiser import visualize_as_bars
from prepare_output_folder import prepare_output_folder

prepare_output_folder()

xls_file = '01-Jan-2023-02-Sept-2023_credit_card.xls'
ready_to_import = transform_csv(xls_file)

categorised_expenses = "output/categorised_expenses.csv"
add_category(ready_to_import, categorised_expenses)

visualize_as_monthly_pies(categorised_expenses)
visualize_as_bars(categorised_expenses)
