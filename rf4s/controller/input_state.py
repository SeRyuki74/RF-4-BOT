import pyautogui as pag


class InputStateManager:
    def __init__(self, logger=None):
        self.logger = logger

        self.mouse_held = False
        self.shift_held = False
        self.ctrl_held = False
        self.alt_held = False

    def log(self, msg):
        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)

    # =========================
    # Mouse
    # =========================

    def hold_mouse(self, button="left"):
        if not self.mouse_held:
            pag.mouseDown(button=button)
            self.mouse_held = True
            self.log("[INPUT] Mouse hold")

    def release_mouse(self, button="left"):
        try:
            pag.mouseUp(button=button)
        except Exception:
            pass

        self.mouse_held = False
        self.log("[INPUT] Mouse release")

    # =========================
    # Shift
    # =========================

    def hold_shift(self):
        pag.keyDown("shift")
        self.shift_held = True
        self.log("[INPUT] Shift hold")

    def release_shift(self):
        try:
            pag.keyUp("shift")
        except Exception:
            pass

        self.shift_held = False
        self.log("[INPUT] Shift release")

    # =========================
    # Reset All
    # =========================

    def reset_all(self):
        try:
            pag.mouseUp(button="left")
            pag.mouseUp(button="right")
        except Exception:
            pass

        for key in ["shift", "ctrl", "alt"]:
            try:
                pag.keyUp(key)
            except Exception:
                pass

        self.mouse_held = False
        self.shift_held = False
        self.ctrl_held = False
        self.alt_held = False

        self.log("[SAFE RESET] Done")