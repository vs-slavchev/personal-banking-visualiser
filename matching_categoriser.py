import re
import pandas as pd


def categorize_string(description):
    categorised_keywords = {
        "groceries": ["lidl", "kaufland", "billa", "ebag", "cba ", "fantastico", "fantastiko",
                      "market ", "avanti", "minimart", "coop", "migros", "conad", "aldi",
                      "carrefour", "kolichka", "mesarnic", "supermarket",
                      "mesarniza"],
        "health": ["lilly", "apteka", "dm ", "pharm", "remedium", "cibalab", "med ", "bodimed",
                   "ramus", "medical", "dental", "termal", "gymbeam",
                   "notino", "titanium", "flays", "cut eood sofia", "eva stil"],
        "entertainment": ["escape", "room", "film", "cinema", "steam", " sport", "ski", "aqua",
                          "boat", "yoga", "hotel", "proparti", "museum",
                          "villa", "borosport",
                          "spotify", "fitness", "gym ", "dance", "za igra"
                          "climbing", "walltopia", "rowing", "swimming", "stadium",
                          "airbnb", "booking.com", "casino", "kazino", "iventim", "billiard",
                          "festiv", "adventurebase", "borovets", "nikayla",
                          "funky monkeys"],
        "restaurants": ["restaurant", "burger", "mehana", "bar", "dinner", "food", "brew", "tekila",
                        "bbq", "slado", "grill", "takeaway", "coffee", "cafe", "restorant", "diner",
                        "beer", "kafe", "shahraiar", "chefs ", "sushi", " pub ", "skara", "kitchen",
                        "pastry", "breakfast", "brunch", "halbite", "macchiato",
                        "kebab", "duner", "doner", "shaurma", "gyros", "bistro", "taverna",
                        "pastaria", "poke", "brauhaus", "wirtshaus", "pizza", "dostavka",
                        "happy.bg", "fantazia", "stara sofia", "soleno",
                        "punto roso"],
        "home": ["наем", "rent", "jysk", "ikea", "praktiker", "momax", "aliexpress", "technopolis",
                 "pepco", "jumbo", "zoo", "pets",
                 "bauhaus", "baumax", "homemax", "amazon", "amzn", "emag", "ozone.bg",
                 "tuk-tam", "econt", "speedy"],
        "bills": ["ком.усл.", "vivacom", " a1", "yettel", "nek ", "e-governance"],
        "transportation": ["bdz", "bus", "taxi", "omv", "lukoil", "gas", "petrol", "eko",
                           "transport", "wizz", "ryan", "air ", "omio ", "ride share",
                           "car rent", "rent a car",
                           "sncf", "s-bahn", "vinetki", "shell", "самолетн", "parking",
                           "via trakia", "citygate"],
        "clothes": ["denim", "jeans", "fashion", "reserved", "remix", "h&m", "cropp", "lacoste",
                    "puma", "pull&bear", "dekatlon"],
        "investment": ["trading", "onderwijs", "revolut", "такса", "захранване"],
    }

    for expense_category, categorised_keywords in categorised_keywords.items():
        for keyword in categorised_keywords:
            if re.search(keyword, description.lower()):
                return expense_category

    return "other"


def add_category(input_file, output_file):
    print("Categorizing transactions with keyword matching...")
    data = pd.read_csv(input_file)
    data['category'] = data.apply(lambda x: categorize_string(x['description']), axis=1)
    counts = data['category'].value_counts()
    other_count = counts.get('other', 0)
    print(f"Categorized {len(data)} transactions — {other_count} uncategorized ('other')")
    data.to_csv(output_file, index=False)
    return data


if __name__ == "__main__":
    string = "I love playing basketball."
    category = categorize_string(string)
    print("The category of the string is:", category)
