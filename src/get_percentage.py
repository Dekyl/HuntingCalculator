def get_percentage_item(actual_label: str, gains_item: int, total_gains: int) -> str:
    """
    Returns the percentage of gains for a specific item formatted as a string.
        :param actual_label: The label of the item, which may include a name and a percentage.
        :param gains_item: The gains for the specific item.
        :param total_gains: The total gains from all items.
        :return: A string containing the item name and its percentage of total gains.
    """
    new_text = actual_label[0:actual_label.rfind(" ")]

    if total_gains == 0:
        new_text += " (" + f"{0:.2f}" + "%)"
        return new_text
    
    actual_percent = gains_item / total_gains * 100

    if actual_percent < 0:
        actual_percent = 0

    actual_percent = f"{actual_percent:.2f}"

    new_text += " (" + actual_percent + "%)"

    return new_text