class COLORS:
    BLUE = "\033[94m"
    END = "\033[0m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"


def main():
    shares_by_price = {}

    # Ask the user to enter their preferred stock prices and corresponding shares to buy
    while True:
        try:
            price = int(
                # print blue text
                input(
                    f"""{COLORS.BLUE}Enter a stock price for a new rule (or -1 to stop).
For example, entering 1000 will allow you to set the amount of shares to
buy when the stock price is $1000 or less:{COLORS.END} """
                )
            )
            if price == -1:
                break
            shares = int(input(f"{COLORS.YELLOW}Enter the number of shares to buy for this rule:{COLORS.END} "))
            shares_by_price[price] = shares
        except ValueError:
            print("Invalid input, please try again.")

    with open('../config.py', 'r') as f:
        lines = f.readlines()
    with open("../config.py", "w") as f:
        for line in lines:
            if line.startswith("SHARES_BY_PRICE"):
                f.write(f"SHARES_BY_PRICE = {shares_by_price}\n")
            else:
                f.write(line)

    print(f"{COLORS.GREEN}Successfully updated config.py!{COLORS.END}")


if __name__ == "__main__":
    main()
