import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw

class RobotFace:
    def __init__(self, i2c=None, width=128, height=64, address=0x3C):
        self.width = width
        self.height = height

        if i2c is None:
            self.i2c = busio.I2C(board.SCL, board.SDA)
        else:
            self.i2c = i2c

        self.display = adafruit_ssd1306.SSD1306_I2C(self.width, self.height, self.i2c, addr=address)
        self.display.fill(0)
        self.display.show()

        self.faces = {
            "normal": self._draw_normal(),
            "grin": self._draw_teethy_grin(),
            "scared": self._draw_scared(),
            "laughing": self._draw_laughing()
        }
        self.current_mood = None

    def _create_canvas(self):
        """Creates a blank 1-bit canvas with an outer decorative border."""
        img = Image.new("1", (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, self.width - 1, self.height - 1], outline=1)
        return img, draw

    def _draw_normal(self):
        """Neutral, slightly stern monster gaze."""
        img, draw = self._create_canvas()
        # Slanted brows / eyes
        draw.polygon([(26, 18), (56, 26), (26, 32)], fill=1)
        draw.polygon([(102, 18), (72, 26), (102, 32)], fill=1)
        # Small centered mouth slit
        draw.line([(48, 48), (80, 48)], fill=1, width=2)
        return img

    def _draw_teethy_grin(self):
        """Mischievous, sharp-toothed monster."""
        img, draw = self._create_canvas()
        # Angled eyes with small cutouts
        draw.polygon([(24, 16), (56, 25), (24, 30)], fill=1)
        draw.polygon([(104, 16), (72, 25), (104, 30)], fill=1)
        
        # Wide upper and lower toothy jaw
        upper_teeth = [(28, 42), (38, 50), (48, 42), (58, 50), (68, 42), (78, 50), (88, 42), (98, 50), (100, 42)]
        lower_teeth = [(28, 42), (38, 38), (48, 42), (58, 38), (68, 42), (78, 38), (88, 42), (98, 38), (100, 42)]
        draw.line(upper_teeth, fill=1, width=2)
        draw.line(lower_teeth, fill=1, width=1)
        return img

    def _draw_scared(self):
        """Wide open eyes with small pupils and an open screaming mouth."""
        img, draw = self._create_canvas()
        # Large white sclera
        draw.ellipse([22, 10, 52, 38], fill=1)
        draw.ellipse([76, 10, 106, 38], fill=1)
        # Tiny shifted pupils
        draw.ellipse([34, 22, 40, 28], fill=0)
        draw.ellipse([88, 22, 94, 28], fill=0)
        # Trembling O-mouth
        draw.ellipse([52, 42, 76, 60], outline=1, width=2)
        return img

    def _draw_laughing(self):
        """Squinting happy inverted arches with a wide curved tongue."""
        img, draw = self._create_canvas()
        # Upward curved squinting eyes (happy ^_^)
        draw.arc([24, 18, 54, 36], start=180, end=0, fill=1, width=2)
        draw.arc([74, 18, 104, 36], start=180, end=0, fill=1, width=2)
        # Big open crescent grin
        draw.chord([36, 32, 92, 58], start=0, end=180, fill=1)
        # Internal black separator
        draw.line([(36, 45), (92, 45)], fill=0, width=2)
        return img

    def set_mood(self, mood):
        """Renders the selected mood. Avoids redrawing if already active."""
        if mood not in self.faces or mood == self.current_mood:
            return
        self.display.image(self.faces[mood])
        self.display.show()
        self.current_mood = mood

    def clear(self):
        self.display.fill(0)
        self.display.show()
        self.current_mood = None