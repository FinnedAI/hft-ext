class COLORS:
    BLUE = "\033[94m"
    END = "\033[0m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"


def main():
    try:
        public = str(input(f"{COLORS.BLUE}Enter your Alpaca API Key ID:{COLORS.END} "))
        private = str(input(f"{COLORS.BLUE}Enter your Alpaca API Secret Key:{COLORS.END} "))
        paper = str(input(f"{COLORS.BLUE}Are you using a paper account? (y/n):{COLORS.END} "))
    except ValueError:
        print("Invalid input, please try again.")

    with open("../config.py", "r") as f:
        lines = f.readlines()
    # Generate the dictionary and save it to the config file
    with open("../config.py", "w") as f:
        for line in lines:
            if line.startswith("ALPACA_PUBLIC_KEY"):
                f.write(f"ALPACA_PUBLIC_KEY = '{str(public)}'\n")
            elif line.startswith("ALPACA_SECRET_KEY"):
                f.write(f"ALPACA_SECRET_KEY = '{str(private)}'\n")
            elif line.startswith("PAPER"):
                boolean = paper.lower() == "y" or paper.lower() == "yes"
                f.write(f"PAPER = {boolean}\n")
            else:
                f.write(line)

    print(f"{COLORS.GREEN}Successfully updated config.py!{COLORS.END}")


if __name__ == "__main__":
    main()
