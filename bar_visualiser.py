import pandas as pd
import matplotlib.pyplot as plt
from visualiser_colors import category_to_color_dict


def visualize_as_bars(csv_file):
    """
  Visualizes the transaction data in the given CSV file. This code first reads the data from the CSV file into a Pandas DataFrame. Then, it groups the data by month and category and counts the number of transactions for each category. Finally, it creates a bar chart for each month showing the number of transactions per category. 
  
  Bard prompt: Code up in Python3 a program that takes in a csv file containing transactions data with the following columns: date, amount, description, category. Then visualises the data by making a separate bar chart for each month. Each bar chart shows the number of transactions per category.

  Args:
    csv_file: The path to the CSV file containing the transaction data.
  """

    # Read the data from the CSV file.
    data = pd.read_csv(csv_file, parse_dates=['date'])
    data['date_month'] = data['date'].dt.strftime('%Y-%m')

    # Group the data by month and category.
    grouped_data = data.groupby(['date_month', 'category'])['amount_bgn'].count()

    # Create a bar chart for each month.
    for month, group_data in grouped_data.groupby('date_month'):
        # Get the categories.
        categories = group_data.index.to_numpy()
        categories = [tup[1] for tup in categories]

        # Get the number of transactions for each category.
        counts = group_data.to_numpy()

        # Create a bar chart of the number of transactions per category.
        plt.figure()
        bar_container = plt.bar(categories, counts)
        for i, patch in enumerate(bar_container.patches):
            patch.set_facecolor(category_to_color_dict[categories[i]])
        plt.xlabel('Category')
        plt.ylabel('Number of Transactions')
        plt.title('Number of Transactions per Category in Month ' + str(month))
        plt.savefig("output/bar-chart-" + str(month) + ".png", format="png")
        plt.show()
        plt.close()


if __name__ == '__main__':
    # Get the path to the CSV file.
    csv_file = input('Enter the path to the CSV file: ')

    # Visualize the transaction data.
    visualize_as_bars(csv_file)
