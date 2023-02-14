import customtkinter as ctk
from alpaca.trading.client import TradingClient
from utils.utils import Storage
import config as CONFIG
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import os
import webbrowser

ctk.set_default_color_theme("scripts/finned-theme.json")
app = ctk.CTk()
matplotlib.use("TkAgg")
app.title("Finned-tech: High Frequency Trader GUI")
app.geometry("1180x600")
api = TradingClient(
    CONFIG.ALPACA_PUBLIC_KEY, CONFIG.ALPACA_SECRET_KEY, paper=CONFIG.PAPER
)
storage = Storage()
storage.create_table()


class Themeing:
    bg_main = "#18191A"
    bg_secondary = "#242526"
    primary = "#E4E6EB"
    secondary = "#b0b3b8"
    gray_complement = "#3A3B3C"
    blue = "#1f6feb"
    green = "#198754"
    red = "#dc3545"
    yellow = "#ffc107"


leftcol = ctk.CTkFrame(app, width=240, height=600)
top_bar_left = ctk.CTkFrame(leftcol, height=50, fg_color=Themeing.bg_secondary)
actions = ctk.CTkScrollableFrame(leftcol, width=240, height=550)
rightcol = ctk.CTkFrame(app, width=560, height=600)
top_bar_right = ctk.CTkFrame(rightcol, height=60, fg_color=Themeing.bg_secondary)
liveview = ctk.CTkScrollableFrame(rightcol, width=560, height=300)
portfolio = ctk.CTkScrollableFrame(rightcol, width=560, height=250)
top_bar = [top_bar_left, top_bar_right]


def _get_ticker_day(ticker):
    pricelist = storage.retrieve_data(ticker)
    day_pricelist = pricelist[-450:] if len(pricelist) >= 450 else pricelist
    day_pricelist = [item[0] for item in day_pricelist]
    return day_pricelist


class Updater:
    def update_actions(self, _actions):
        # make scrolling list of items in actions
        # using tkinter
        for item in _actions:
            background_color = (
                Themeing.green
                if "buy " in item.lower()
                else Themeing.red
                if "sell " in item.lower()
                else Themeing.yellow
                if "error" in item.lower()
                else Themeing.blue
            )
            msg = ctk.CTkLabel(
                actions,
                text=item,
                width=560,
                bg_color=background_color,
                anchor=ctk.W,
            )
            msg.pack(expand=True, fill="both", pady=1, padx=1)

    # show liveview with specified ticker
    def update_liveview(self, ticker, pricelist):
        for widget in liveview.winfo_children():
            try:
                widget.destroy()
            except:
                pass

        # make a line chart of pricelist using matplotlib
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(pricelist)
        ax.set_title(f"Liveview of {ticker}")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")

        ax.tick_params(axis="x", colors=Themeing.gray_complement)
        ax.tick_params(axis="y", colors=Themeing.gray_complement)
        ax.title.set_color(Themeing.primary)
        ax.xaxis.label.set_color(Themeing.gray_complement)
        ax.yaxis.label.set_color(Themeing.gray_complement)
        ax.lines[0].set_color(Themeing.blue)

        canvas = FigureCanvasTkAgg(fig, liveview)
        canvas.draw()
        canvas.get_tk_widget().configure(background=Themeing.bg_main)
        canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(canvas, liveview)
        toolbar.update()
        canvas._tkcanvas.pack(side="bottom", fill="both", expand=True)

    def update_portfolio(self, _portfolio):
        # clear portfolio
        try:
            for widget in portfolio.winfo_children():
                widget.destroy()
        except:
            pass

        est_value = 0
        for ticker in _portfolio:
            est_value += float(_portfolio[ticker]["qty"]) * float(
                _portfolio[ticker]["price"]
            )

        # add header with large bolded text
        ctk.CTkLabel(
            portfolio,
            text=f"My Portfolio (${round(est_value, 2)}): ",
            width=240,
            fg_color=Themeing.gray_complement,
            font=("Helvetica", 20, "bold"),
        ).pack(expand=True, fill="both", pady=1, padx=1)

        for ticker in _portfolio:
            # make bordered element and insert to portfolio
            ctk.CTkLabel(
                portfolio,
                text=f"({_portfolio[ticker]['qty']}x{ticker}) @ ${_portfolio[ticker]['price']}",
                width=240,
                fg_color=Themeing.gray_complement,
            ).pack(expand=True, fill="both", pady=1, padx=1)

    def update_buttons(self):
        toggle_state = ctk.CTkButton(
            top_bar[0],
            text="Exit",
            command=lambda: os._exit(1),
        )
        homepage = ctk.CTkButton(
            top_bar[0],
            text="Homepage",
            command=lambda: webbrowser.open("https://finned.tech"),
        )
        github = ctk.CTkButton(
            top_bar[0],
            text="Github",
            command=lambda: webbrowser.open(
                "https://github.com/finned-digital-solutions"
            ),
        )
        dropdown = ctk.CTkOptionMenu(
            top_bar[1],
            values=CONFIG.TRADE_TICKERS,
            command=lambda x: self.update_liveview(x, _get_ticker_day(x)),
            fg_color=Themeing.primary,
        )

        for button in [toggle_state, homepage, github, dropdown]:
            # pack to left with space to the right
            button.pack(side=ctk.LEFT, padx=2, pady=4)


# default functions for intializing
class Defaults:
    # pack all frames
    leftcol.pack(side=ctk.LEFT, fill="both", expand=True)
    rightcol.pack(side=ctk.RIGHT, fill="both", expand=True)
    top_bar_left.pack(side=ctk.TOP, fill="both", expand=True)
    top_bar_right.pack(side=ctk.TOP, fill="both", expand=True)
    portfolio.pack(side=ctk.BOTTOM, fill="both", expand=True)
    liveview.pack(side=ctk.TOP, fill="both", expand=True)
    actions.pack(side=ctk.TOP, fill="both", expand=True)

    def liveview(self):
        return _get_ticker_day(CONFIG.TRADE_TICKERS[0])

    def actions(self):
        account = api.get_account()
        return [
            " -> Connected to Alpaca",
            f" -> Account ID: {account.id}",
            f" -> Buying Power: {account.buying_power}",
            f" -> Change since last run: {float(account.equity) - float(account.last_equity)}\n",
        ]


def start_gui():
    defaults = Defaults()
    updater = Updater()
    updater.update_buttons()
    updater.update_liveview(CONFIG.TRADE_TICKERS[0], defaults.liveview())
    updater.update_actions(defaults.actions())
    # portfolio is updated by the trading algorithm
    # once it is initialized

    app.protocol("WM_DELETE_WINDOW", lambda: os._exit(1))
    app.mainloop()
