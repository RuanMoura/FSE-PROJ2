import curses

class MENU_CLASS():
    def __init__(self) -> None:
        self.tr: float = 0.0
        self.ti: float = 0.0
        self.ta: float = 0.0
        self.control_signal: int = 0
        self.on_off: int = 0
        self.operating: int = 0
        self.curve: int = 0

        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_WHITE)
        self.stdscr.clear()
        self.stdscr.refresh()
        self.panel = curses.newwin(9, 31, 1, 2)
        self.selected_option = 1

    def set_constant(self, tr, ti, ta, control_signal, on_off, operating, curve):
        self.tr = tr
        self.ti = ti
        self.ta = ta
        self.control_signal = control_signal
        self.on_off = on_off
        self.operating = operating
        self.curve = curve
        self.refresh_panel()

    def refresh_panel(self):
        self.panel.clear()
        self.panel.addstr(1, 1, "Ligado/Desligado:")
        self.addstr_on_off(self.panel, self.on_off, 1)
        self.panel.addstr(2, 1, "Funcionamento:")
        self.addstr_on_off(self.panel, self.operating, 2)
        self.panel.addstr(3, 1, "Curva:")
        self.addstr_on_off(self.panel, self.curve, 3)
        self.panel.addstr(4, 1, "Temperatura Referencia:")
        self.panel.addstr(4, 25, "%.1f" % self.tr,
            curses.A_REVERSE if self.selected_option == 4 else curses.A_NORMAL)
        self.panel.addstr(5, 1, "Temperatura Interna:")
        self.panel.addstr(5, 25, "%.1f" % self.ti)
        self.panel.addstr(6, 1, "Temperatura Ambiente:")
        self.panel.addstr(6, 25, "%.1f" % self.ta)
        self.panel.addstr(7, 1, "Sinal Controle:")
        self.panel.addstr(7, 25, f"{self.control_signal}%")
        self.panel.border()
        self.panel.refresh()

    def addstr_on_off(self, window, condition, row):
        if condition:
            window.addstr(row, 25, f"ON", curses.color_pair(
                2 if self.selected_option == row else 1))
        else:
            window.addstr(row, 25, f"OFF", curses.color_pair(
                4 if self.selected_option == row else 3))

    def interact(self):
        key = self.stdscr.getkey()
        rows = ["on_off", "operating", "curve", "tr"]
        res = None
        if key == "KEY_UP":
            self.selected_option = max(self.selected_option - 1, 1)
        elif key == "KEY_DOWN":
            self.selected_option = min(self.selected_option + 1, 4)
        elif key == "KEY_LEFT":
            res = (rows[self.selected_option-1], 'l')
        elif key == "KEY_RIGHT":
            res = (rows[self.selected_option-1], 'r')
        self.refresh_panel()
        return res

    def close(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
