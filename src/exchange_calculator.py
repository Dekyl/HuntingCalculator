def exchange_results(green, blue):
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
        return 0