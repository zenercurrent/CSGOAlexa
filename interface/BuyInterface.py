import pydirectinput
from pyautogui import screenshot
from time import sleep
import csv
import random
import cv2
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r'speech\Tesseract-OCR\tesseract.exe'


def press(key):
    pydirectinput.keyDown(key, _pause=False)
    sleep(0.01)
    pydirectinput.keyUp(key, _pause=False)
    sleep(0.01)


class BuyInterface:

    def __init__(self, side):
        self.SIDE = side
        assert self.SIDE == "CT" or self.SIDE == "T"

        self.BUY = "b"
        self.DROP = "g"
        self.data = {}

        self.balance = 0

        self.isP2000 = True
        self.isCZ = False
        self.isR8 = True
        self.isMP5 = True
        self.isM4A4 = False

        self.alwaysArmour = False
        self.alwaysKit = False
        self.autoBuyOptions = True

        self.load_info()

    def load_info(self):
        with open("interface/csgo.csv") as file:
            data = list(csv.reader(file))
            key = data.pop(0)
            for row in data:
                d = {row[0]: {}}
                if row[4] != "B" and row[4] != self.SIDE:
                    continue
                for k in range(len(key)):
                    if k == 0:
                        continue
                    d[row[0]][key[k]] = row[k]
                self.data.update(d)

            # Loadouts
            if self.SIDE == "CT":
                if self.isP2000:
                    del self.data["USP-S"]
                else:
                    del self.data["P2000"]
                if self.isM4A4:
                    del self.data["M4A1-S"]
                else:
                    del self.data["M4A4"]

            if self.isCZ:
                self.data.pop("Five-Seven", None)
                self.data.pop("Tec-9", None)
            else:
                del self.data["CZ75-Auto"]
            if self.isR8:
                del self.data["Desert Eagle"]
            else:
                del self.data["R8 Revolver"]
            if self.isMP5:
                del self.data["MP7"]
            else:
                del self.data["MP5-SD"]

    def switch_sides(self):
        self.SIDE = "T" if self.SIDE == "CT" else "CT"
        self.data = {}
        self.load_info()

    def buy(self, __item):
        item = self.data[__item]
        print(__item)
        print("Cost: $" + item["cost"] + "\n")

        press(self.BUY)
        press(item["section"])
        press(item["index"])
        press(self.BUY)
        if item["section"] in ["5", "6"]:
            print("TRUE!")
            press(self.BUY)

    def drop(self, slot):
        assert 0 < int(slot) < 6
        press(str(slot))
        press(self.DROP)

    def random_buy(self):
        items = list(self.data.keys())
        guns = items[0:21]
        pistols = items[0:5]
        main = items[5:21]
        zeus = items[23]
        grenades = items[25:]
        self.get_balance()

        # Buy Armour
        if self.alwaysArmour:
            if self.balance > 1000:
                self.buy("Full Armour")
                self.balance -= 1000

        # Buy Defuse Kit
        if self.alwaysKit:
            if self.balance > 400 and self.SIDE == "CT":
                self.buy("Defuse Kit")
                self.balance -= 400

        # Random Main Weapon
        if self.autoBuyOptions:
            guns += ["Auto Buy", "Re-buy Previous", "ECO"]
        m = random.randint(0, len(guns))
        # cost checking
        if self.balance < 300:
            print("Not enough balance for purchase")
        else:
            if m != len(main):
                if self.autoBuyOptions:
                    if guns[m] == "Auto Buy":
                        print("AUTO BUY")
                        press("f3")
                    elif guns[m] == "Re-buy Previous":
                        print("RE-BUY PREVIOUS")
                        press("f4")
                    elif guns[m] == "ECO":
                        print("ECO")
                        self.drop(2)
                cost = int(self.data[guns[m]]["cost"])
                while cost > self.balance:
                    m = random.randint(0, len(guns) - 1 - (3 if self.autoBuyOptions else 0))
                    cost = int(self.data[guns[m]]["cost"])
                self.buy(guns[m])
                self.balance -= cost
            else:
                print("No buy")

        # Grenades
        grenades.append("Flashbang")
        g_count = random.randint(0, 4)
        nades = random.sample(grenades, g_count)
        for n in nades:
            cost = int(self.data[n]["cost"])
            if cost > self.balance:
                break
            self.buy(n)
            self.balance -= cost

        # Zeus
        if random.randint(0, 2) == 0 and self.balance > 200:
            self.buy(zeus)
            self.balance -= int(self.data[zeus]["cost"])

        # Pistols
        if 4 < m < 22:
            p = random.randint(0, len(pistols))
            if p != len(pistols):
                cost = int(self.data[pistols[p]]["cost"])
                if cost < self.balance:
                    self.buy(pistols[p])
                    self.balance -= cost

        print("The balance should be:", self.balance)
        self.buy("", end=True)

    def get_balance(self):
        press(self.BUY)
        sleep(0.5)
        screenshot("interface/balance.png", region=(0, 350, 150, 50))
        press(self.BUY)
        im = cv2.imread("interface/balance.png")
        im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(im_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        info = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, lang="eng")

        for text in info["text"]:
            if text.startswith("$"):
                self.balance = int(text.strip().replace("$", "", 1))
                break

        # show thresholding
        # for s in range(len(info["text"])):
        #     (x, y, w, h) = (info["left"][s], info["top"][s], info["width"][s], info["height"][s])
        #     im = cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #
        # cv2.imshow("Original Image", im)
        # # cv2.imshow("Threshold Image", thresh)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
