from scripts.gui import Updater


class Notifier:
    def __init__(self):
        self.notify = Updater()

    def new_action(self, text):
        self.notify.update_actions([text])

    def new_portfolio(self, portfolio):
        self.notify.update_portfolio(portfolio)
