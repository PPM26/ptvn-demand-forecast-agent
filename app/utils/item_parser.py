def fix_item_format(item: str) -> str:
    """
    Normalizes the item string by converting to lowercase and removing all spaces.
    """
    if not item:
        return item
    return item.lower().replace(" ", "")
