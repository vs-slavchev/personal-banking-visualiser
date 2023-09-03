import re
import pandas as pd


def categorize_string(description):
    categorised_keywords = {
        "groceries": ["lidl", "kaufland", "billa", "ebag", "cba ", "fantastico", "market ", "avanti"],
        "health": ["lilly", "apteka", " dm ", "pharm", "remedium"],
        "entertainment": ["escape", "room", "film", "cinema", "steam", " sport", "ski", "aqua", "boat", "yoga", "hotel",
                          "museum"],
        "restaurants": ["restaurant", "burger", "mehana", "bar", "dinner", "food", "brew", "tekila", "bbq", "slado",
                        "grill", "takeaway", "coffee", "cafe", "restorant", "diner", "beer"],
        "home": ["jysk", "ikea", "praktiker", "momax", "aliexpress", "technopolis", "pepco"],
        "transportation": ["bdz", "bus", "taxi", "omv", "lukoil", "gas", "petrol", "eko", "transport", "wizz", "ryan",
                           "air "],
        "clothes": ["reserved"]
    }

    for expense_category, categorised_keywords in categorised_keywords.items():
        for keyword in categorised_keywords:
            if re.search(keyword, description.lower()):
                return expense_category

    return "other"


def add_category(input_file, output_file):
    data = pd.read_csv(input_file)
    data['category'] = data.apply(lambda x: categorize_string(x['description']), axis=1)
    data.to_csv(output_file, index=False)


if __name__ == "__main__":
    string = "I love playing basketball."
    category = categorize_string(string)
    print("The category of the string is:", category)
