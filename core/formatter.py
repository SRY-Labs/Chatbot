def format_response(items):
    if not items:
        return "I couldn’t find any matching products right now."

    lines = ["Here are some options:\n"]

    for idx, p in enumerate(items[:3], start=1):
        lines.append(
            f"{idx}. {p['product_name']}\n"
            f"   Price: ${int(p['price_usd'])}\n"
            f"   Link: {p['product_url']}"
        )

    return "\n\n".join(lines)
