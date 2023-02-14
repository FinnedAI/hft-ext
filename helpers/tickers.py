class COLORS:
    BLUE = "\033[94m"
    END = "\033[0m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"


def main():
    tickers = []

    while True:
        try:
            ticker = str(input(f"{COLORS.BLUE}Enter a ticker you would like to trade (or -1 to stop):{COLORS.END} "))
            if ticker == '-1': break
            tickers.append(ticker)
        except ValueError:
            print("Invalid input, please try again.")

    with open("../config.py", "r") as f:
        lines = f.readlines()
    with open("../config.py", "w") as f:
        for line in lines:
            if line.startswith("TRADE_TICKERS"):
                f.write(f"TRADE_TICKERS = {tickers}\n")
            else:
                f.write(line)

    print(f"{COLORS.GREEN}Successfully updated config.py!{COLORS.END}")


if __name__ == "__main__":
    main()
