import cv2
import numpy as np
import pyautogui as pag
import time

class RodDetection:

    def __init__(self):

        self.threshold = 0.78

        # SESUAIKAN NANTI
        self.rod_areas = {
            1: (250, 250, 500, 700),
            2: (720, 320, 900, 520),
            3: (1050, 250, 1350, 700),
        }

        self.left_template = cv2.imread(
            "rf4s/templates/bottom/rod_left.png",
            0,
        )

        self.right_template = cv2.imread(
            "rf4s/templates/bottom/rod_right.png",
            0,
        )
        self.left_template = cv2.resize(
            self.left_template,
            (60, 140)
        )

        self.right_template = cv2.resize(
            self.right_template,
            (60, 140)
        )

    def screenshot_area(self, area):

        x1, y1, x2, y2 = area

        img = pag.screenshot(
            region=(x1, y1, x2 - x1, y2 - y1)
        )

        return cv2.cvtColor(
            np.array(img),
            cv2.COLOR_RGB2GRAY
        )

    def is_bent(self, img):

        left = cv2.matchTemplate(
            img,
            self.left_template,
            cv2.TM_CCOEFF_NORMED,
        )

        right = cv2.matchTemplate(
            img,
            self.right_template,
            cv2.TM_CCOEFF_NORMED,
        )

        left_score = np.max(left)
        right_score = np.max(right)

        return max(left_score, right_score)

    def get_bent_rod(self):

        best_rod = None
        best_score = 0

        for rod, area in self.rod_areas.items():

            img = self.screenshot_area(area)

            score = self.is_bent(img)

            if score > self.threshold:

                if score > best_score:

                    best_score = score
                    best_rod = rod

        return best_rod

if __name__ == "__main__":

    detector = RodDetection()

    while True:

        rod = detector.get_bent_rod()

        print("Detected:", rod)
        time.sleep(1)
