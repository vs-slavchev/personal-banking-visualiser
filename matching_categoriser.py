import re
import pandas as pd


def categorize_string(description):
    categorised_keywords = {
        "groceries": ["lidl", "kaufland", "billa", "ebag", "cba ", "fantastico", "fantastiko", "market ", "avanti", "minimart"],
        "health": ["lilly", "apteka", "dm ", "pharm", "remedium", "cibalab", "med ", "bodimed", "ramus", "medical"],
        "entertainment": ["escape", "room", "film", "cinema", "steam", " sport", "ski", "aqua", "boat", "yoga", "hotel",
                          "museum", "spotify", "fitness", "gym ", "dance", "hotel", "climbing", "walltopia", "rowing",
                          "swimming", "stadium"],
        "restaurants": ["restaurant", "burger", "mehana", "bar", "dinner", "food", "brew", "tekila", "bbq", "slado",
                        "grill", "takeaway", "coffee", "cafe", "restorant", "diner", "beer", "kafe", "shahraiar", "chefs ",
                        "sushi", " pub ", "skara", "kitchen", "pastry", "breakfast", "brunch"],
        "home": ["наем", "rent", "jysk", "ikea", "praktiker", "momax", "aliexpress", "technopolis", "pepco", "jumbo", "zoo", "pets"],
        "bills": ["ком.усл.", "vivacom", " a1", "yettel"],
        "transportation": ["bdz", "bus", "taxi", "omv", "lukoil", "gas", "petrol", "eko", "transport", "wizz", "ryan",
                           "air ", "omio ", "ride share", "car rent", "rent a car"],
        "clothes": ["denim", "jeans", "fashion", "reserved", "remix", "h&m", "cropp", "lacoste", "puma", "pull&bear"],
        "finance": ["trading", "onderwijs"]
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
