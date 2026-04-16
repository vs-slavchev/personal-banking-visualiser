import pandas as pd
import matplotlib.pyplot as plt
from visualiser_colors import category_to_color_dict


def visualize_as_multiline_chart(csv_file_name):
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
    grouped_data = df.groupby(['date_month', 'category'])["amount_bgn"].sum().unstack()

    plt.figure(figsize=(10, 6))
    for category in grouped_data.columns:
        plt.plot(grouped_data.index, grouped_data[category], label=category)

    # Add labels and title
    plt.xlabel('Month')
    plt.ylabel('Amount BGN')
    plt.title('Monthly Transactions by Category')
    plt.legend(title='Category')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show the plot
    plt.show()


if __name__ == "__main__":
    # Get the path to the CSV file.
    csv_file = input("Enter the path to the CSV file: ")

    # Visualize the transactions data.
    visualize_as_multiline_chart(csv_file)
