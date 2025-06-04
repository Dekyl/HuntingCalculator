def exchange_results(green: int, blue: int) -> tuple[int, int, int]:
    """
    Calculate the number of exchanges possible with given green and blue resources to obtain maximum profit.
        :param green: The initial amount of green resources.
        :param blue: The initial amount of blue resources.
        :return: A tuple containing the number of exchanges, the final amount of green resources, and the final amount of blue resources.
    """
    try:
        count = 0
        while True:
            actual = (green+60)/(blue-30)
            if actual >= 1.2 or actual < 0:
                break
            green += 60
            blue -= 30
            count += 1

        return (count*30, green, blue)
    except:
        return (0, green, blue)