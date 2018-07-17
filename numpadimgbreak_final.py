# encoding = utf8
from PIL import Image
import requests
from StringIO import StringIO
from vcodeprocess_final import VcodeBreak


class NumPadBreak(object):

    def convert_to_whtie_black(self, image):
        width = image.size[0]
        height = image.size[1]
        new_image = Image.new('RGB', (width, height), 'black')
        pix = new_image.load()
        for x in range(width):
            for y in range(height):
                pix[x, y] = (255, 255, 255)
                pix_value = image.getpixel((x, y))
                pix_sum = pix_value[0] + pix_value[1] + pix_value[2]
                # print pix_sum
                if pix_sum > 450:
                    pix[x, y] = (0, 0, 0)
        return new_image

    def break_numpadimage(self, image):
        image = self.convert_to_whtie_black(image)
        num_width = 5
        begin_y_mim = 10
        begin_y_max = 19
        image = image.crop((0, 0, image.size[0], 25))
        pix = image.load()
        width = image.size[0]
        height = image.size[1]
        y_values = []
        for x in range(width):
            sum_rgb = 0
            for y in range(height):
                pix_value = pix[x, y]
                sum_rgb += pix_value[0] + pix_value[1] + pix_value[2]
            y_values.append(sum_rgb)

        count = 0
        index = -1
        sub_images = []
        for y_value in y_values:
            index += 1
            if count > 0:
                count -= 1
                continue
            if y_value != 0:
                box = (index, begin_y_mim, index + num_width, begin_y_max)
                if y_values[index] < y_values[index + 5]:
                    box = (index + 1, begin_y_mim, index + 1 + num_width, begin_y_max)
                count = 10
                sub_image = image.crop(box)
                sub_images.append(sub_image)

        vcode_break = VcodeBreak()
        font_path = 'image/numkeypad/font/'
        result = []
        for sub_image in sub_images:
            max_like_count = 0
            like_font = None
            for i in range(10):
                image_font = Image.open(font_path + str(i) + '.png')
                like_count = vcode_break.pic_xor(image_font, sub_image)
                if like_count > max_like_count:
                    max_like_count = like_count
                    like_font = i
            result.append(like_font)
        return result
