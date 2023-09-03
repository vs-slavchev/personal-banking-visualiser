import pandas as pd
import matplotlib.pyplot as plt
from visualiser_colors import category_to_color_dict


def visualize_as_monthly_pies(csv_file_name):
    """
  Visualizes transactions data by month and category. This code first reads the CSV file into a Pandas DataFrame. Then, it gets the month and category columns from the DataFrame. Next, it groups the data by month and category and sums the amount column for each group. Finally, it creates a pie chart for each month and shows the pie chart.

To use this code, you need to first install the following Python packages:

pandas
matplotlib
Once you have installed the packages, you can run the code by saving it as a Python file and then running the following command in the terminal:

python visualize_transactions_data.py
This will prompt you to enter the path to the CSV file. Enter the path to the CSV file and the code will visualize the transactions data for you.

Bard prompt: Code up in Python3 a program that takes in a csv file containing transactions data with the following columns: date, amount, description, category. Then visualises the data by making a separate pie chart for each month. Each pie chart shows transactions per category.

  Args:
    csv_file_name: The path to the CSV file containing the transactions' data.
  """

    # Read the CSV file into a Pandas DataFrame.
    df = pd.read_csv(csv_file_name, parse_dates=['date'])
    df['date_month'] = df['date'].dt.strftime('%Y-%m')

    # Group the data by month and category.
    grouped_data = df.groupby(['date_month', 'category'])["amount_bgn"].sum()

    # Create a pie chart for each month.
    for month, group_data in grouped_data.groupby('date_month'):
        # Get the pie chart slice labels.
        pie_chart_slice_labels = group_data.index.to_numpy()
        pie_chart_slice_labels = [tup[1] for tup in pie_chart_slice_labels]

        # Remove slice labels beyond the top 15 to avoid labels overlapping.
        pie_chart_slice_labels[15:] = ""

        # Get the pie chart slice values.
        pie_chart_slice_values = group_data.to_numpy()

        # Create the pie chart.
        patches, texts, pcts = plt.pie(pie_chart_slice_values, labels=pie_chart_slice_labels,
                                       autopct=lambda p: '{:.0f}'.format(p * sum(pie_chart_slice_values) / 100))
        for i, patch in enumerate(patches):
            patch.set_facecolor(category_to_color_dict[texts[i].get_text()])
        plt.title(f"BGN spent by category in month {month}")
        plt.savefig("output/pie-chart-" + str(month) + ".png", format="png")
        plt.show()
        plt.close()


if __name__ == "__main__":
    # Get the path to the CSV file.
    csv_file = input("Enter the path to the CSV file: ")

    # Visualize the transactions data.
    visualize_as_monthly_pies(csv_file)
