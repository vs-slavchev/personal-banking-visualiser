import json
import os

VALID_CATEGORIES = [
    "groceries", "health", "entertainment", "restaurants",
    "home", "bills", "transportation", "clothes", "investment",
]

PROMPT_TEMPLATE = """You are a personal finance assistant. Categorize each bank transaction description below into exactly one of these categories:
groceries, health, entertainment, restaurants, home, bills, transportation, clothes, investment

Rules:
- Only assign a category if you are confident (>80% sure).
- If unsure, omit the transaction from the response entirely.
- Reply with a single JSON object mapping each transaction index (as a string) to a category name.
- No explanation, no markdown, just raw JSON.

Transactions:
{transactions}
"""


def categorize_with_openai(df):
    token = os.environ.get("OPENAI_API_KEY")
    if not token:
        print("OPENAI_API_KEY not set — skipping AI categorization")
        return df

    try:
        from openai import OpenAI
    except ImportError:
        print("openai package not installed — skipping AI categorization")
        return df

    uncategorized = df[df["category"] == "other"].copy()
    if uncategorized.empty:
        print("No uncategorized transactions — skipping AI categorization")
        return df

    print(f"Sending {len(uncategorized)} uncategorized transactions to OpenAI...")

    transactions_text = "\n".join(
        f'{idx}: {row["description"]}'
        for idx, row in uncategorized.iterrows()
    )
    prompt = PROMPT_TEMPLATE.format(transactions=transactions_text)

    client = OpenAI(api_key=token)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    suggestions = json.loads(raw)

    assigned = 0
    for idx_str, category in suggestions.items():
        if category in VALID_CATEGORIES:
            df.at[int(idx_str), "category"] = category
            assigned += 1

    print(f"OpenAI assigned categories to {assigned}/{len(uncategorized)} transactions")
    return df
