def infer_category(name: str):
    name = name.lower()
    if "sofa bed" in name:
        return "sofa bed"
    if "sofa" in name:
        return "sofa"
    if "loveseat" in name:
        return "loveseat"
    if "ottoman" in name:
        return "ottoman"
    if "armchair" in name or "chair" in name:
        return "chair"
    return "other"
