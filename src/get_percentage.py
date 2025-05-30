def get_percentage_item(actual_label, gains_item, total_gains):
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