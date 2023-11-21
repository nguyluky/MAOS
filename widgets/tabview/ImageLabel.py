from PIL import Image
from customtkinter import *

from widgets.ImageHandel import cropping_image_in_a_rounded_rectangle, async_load_img_from_url, load_img

TEST_URL = "https://media.valorant-api.com/bundles/d958b181-4e7b-dc60-7c3c-e3a3a376a8d2/displayicon.png"
TEST_SKIN = "https://media.valorant-api.com/weaponskinlevels/578e9077-4f88-260c-e54c-b988425c60e4/displayicon.png"

FILL_X = "fillX"
FILL_Y = "fillY"
FILL_AUTO = "fillAuto"


class ImageLabel(CTkFrame):
    def __init__(self, master, path=None, url=None, size=None, corner_radius=20, fill_type=FILL_Y,
                 *args, **kw) -> None:
        super().__init__(master, fg_color="transparent", *args, **kw)

        self.label = CTkLabel(self, text='')
        self.label.place(x=0, y=0, relheight=1, relwidth=1)
        self.img_size = None
        self.img = None

        self._fill_type = fill_type
        self._corner_radius = corner_radius
        self.set_img(path, url)

        if fill_type is not None:
            self.bind('<Configure>', self.update_size_img)

    def update_size_img(self, event=None):
        if self.img is None:
            return

        if event is not None:
            self.label.configure(image=self.crop(event.height, event.width))
        else:
            self.label.configure(image=self.crop(self.winfo_height(), self.winfo_width()))

    def _crop_fill_y(self, height, width):
        new_height = height
        new_width = int(height / self.img_size[1] * self.img_size[0])
        img = self.img.resize((new_width, new_height))

        if width < new_width:
            denta_width = new_width - width
            img = img.crop((denta_width // 2, 0, denta_width // 2 + width, height))

        return CTkImage(cropping_image_in_a_rounded_rectangle(img, self._corner_radius), size=(width, height))

    def _crop_fill_x(self, height, width):
        new_width = width
        new_height = int(width / self.img_size[0] * self.img_size[1])
        img = self.img.resize((new_width, new_height))

        if width < new_width:
            denta_width = new_width - width
            img = img.crop((denta_width // 2, 0, denta_width // 2 + width, height))

        return CTkImage(cropping_image_in_a_rounded_rectangle(img, self._corner_radius),
                        size=(new_width, new_height))

    def crop(self, height, width):
        if self._fill_type == FILL_Y:
            return self._crop_fill_y(height, width)

        elif self._fill_type == FILL_X:
            return self._crop_fill_x(height, width)

        elif self._fill_type == FILL_AUTO:
            new_height = height - 1
            new_width = int(height / self.img_size[1] * self.img_size[0])
            if new_width > width:
                new_width = width
                new_height = int(width / self.img_size[0] * self.img_size[1])

            img = self.img.resize((new_width, new_height))

            return CTkImage(cropping_image_in_a_rounded_rectangle(img, self._corner_radius),
                            size=(new_width, new_height))

    def set_img(self, path=None, url=None):
        self.winfo_toplevel().loop.create_task(self.async_set_img(path, url))

    async def async_set_img(self, path=None, url=None):
        if url is not None:
            img = await async_load_img_from_url(url)
        elif path is not None:
            img = load_img(path)
        else:
            return FileExistsError

        self.img = img
        self.img_size = self.img.size

        self.update_size_img()
