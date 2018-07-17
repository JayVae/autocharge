import os
import uuid
from filecmp import cmp
from io import StringIO

import requests
import time

from PIL import Image


class VcodeBreak(object):
    def __init__(self):
        # file path
        self.font_path = "image/vcode/font/"

        # background color
        self.background_color = [
            (0, 85, 153), (0, 85, 204), (0, 128, 153), (0, 128, 204),
            (51, 85, 153), (51, 85, 204), (51, 128, 153), (51, 128, 204)
        ]
        # interference line
        self.interference_line = [
            (153, 128, 102), (102, 128, 102), (153, 128, 153), (102, 128, 153)
        ]
        # request url
        self.url = "http://card.xjtu.edu.cn/Account/GetCheckCodeImg"

    def getrgbsum(self, rgb):
        return rgb[0] + rgb[1] + rgb[2]

    def get_y_values(self, img):
        width = img.size[0]
        heigth = img.size[1]
        y_values = []
        for y in range(heigth):
            tmp = 0
            for x in range(width):
                rgb = img.getpixel((x, y))
                tmp += self.getrgbsum(rgb)
            y_values.append(tmp)
        return y_values

    def get_char_box(self, y_values):

        size = 20
        i_max = 0
        begin = 0
        for index in range(size - 11):
            sum = 0
            for i in range(11):
                sum += y_values[i + index]
            if sum > i_max:
                i_max = sum
                begin = index
        return (1, begin, 9, begin + 11)

    # change image to white and black
    def convert_to_white_black(self, img):
        img = img.convert("RGB")
        width, height = img.size

        # print str(width) + ":" + str(height)
        new_img = Image.new("RGB", (width, height), 'black')
        pix = new_img.load()
        for x in range(width):
            for y in range(height):
                value = img.getpixel((x, y))
                sum_value = value[0] + value[1] + value[2]
                if sum_value > 60:
                    pix[x, y] = (255, 255, 255)
                else:
                    pix[x, y] = (0, 0, 0)
        return new_img

    # advance remove noise pixel
    def remove_noise(self, new_image):
        width = new_image.size[0]
        height = new_image.size[1]
        pix = new_image.load()
        for x in range(width):
            for y in range(height):
                values = pix[x, y]
                if values[0] > 20 and values[1] > 20 and values[2] > 20:
                    l, r, u, d = (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)
                    around = []
                    if x != 0 and x != width - 1 and y != 0 and y != height - 1:
                        l = new_image.getpixel((x - 1, y))
                        r = new_image.getpixel((x + 1, y))
                        u = new_image.getpixel((x, y - 1))
                        d = new_image.getpixel((x, y + 1))
                        around = [l, r, u, d]
                    count = 0
                    for ard in around:
                        count += 1
                        if ard[0] > 200 and ard[1] > 200 and ard[2] > 200:
                            break
                    if count == 4:
                        pix[x, y] = (0, 0, 0)
        return new_image

    def crop_image(self, image):

        sub_images = []
        sub_images.append(image.crop((2, 0, 11, 20)))
        sub_images.append(image.crop((15, 0, 24, 20)))
        sub_images.append(image.crop((28, 0, 37, 20)))
        sub_images.append(image.crop((41, 0, 50, 20)))
        font_sub_images = []
        for sub_image in sub_images:
            y_values = self.get_y_values(sub_image)
            box = self.get_char_box(y_values)
            sub_image = sub_image.crop(box)
            font_sub_images.append(sub_image)
            # sub_image.save("d:/vcode/" +  str(uuid.uuid1()) +'.jpg')

        return font_sub_images

    # process image to four images and make the images colour to black or white
    def process(self, im):
        im1 = im.convert('RGB')
        width, height = im1.size
        new_image = Image.new("RGB", (width, height), 'blue')
        pix = new_image.load()
        for x in range(width):
            for y in range(height):
                values = im1.getpixel((x, y))
                pix[x, y] = values
                for bgc in self.background_color:
                    if cmp(bgc, values) == 0:
                        pix[x, y] = (0, 0, 0)
                        continue
                for ifl in self.interference_line:
                    if cmp(ifl, values) == 0:
                        l, r, u, d = (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)
                        around = []
                        if x != 0 and x != width - 1 and y != 0 and y != height - 1:
                            l = im1.getpixel((x - 1, y))
                            r = im1.getpixel((x + 1, y))
                            u = im1.getpixel((x, y - 1))
                            d = im1.getpixel((x, y + 1))
                            around = [l, r, u, d]
                        pix[x, y] = (0, 0, 0)
                        for ard in around:
                            if ard[0] > 200 and ard[1] > 200 and ard[2] > 200:
                                pix[x, y] = (255, 255, 255)
                                break
        # new_image.save("d:/vcode/" + str(uuid.uuid1()) + '.jpg')
        # new_image = remove_noise(new_image)
        new_image = self.convert_to_white_black(new_image)
        return self.remove_noise(new_image)

    def pic_xor(self, img_ori, img):
        width = img.size[0]
        height = img.size[1]
        img_ori_tmp = img_ori.convert("1")
        img_tmp = img.convert("1")
        like_count = 0
        for x in range(width):
            for y in range(height):
                value_ori = img_ori_tmp.getpixel((x, y))
                value = img_tmp.getpixel((x, y))
                if value_ori == value:
                    like_count += 1
        return like_count

    def match(self, image):
        result = {}
        font_images = []
        for i in range(9):
            font_image = Image.open(self.font_path + str(i + 1) + ".jpg")
            font_images.append(font_image)
        max_like_count = 0
        like_font = None
        for font_image_num in range(len(font_images)):
            like_count = self.pic_xor(font_images[font_image_num], image)
            if like_count > max_like_count:
                max_like_count = like_count
                like_font = font_image_num
        if max_like_count != 0 and like_font is not None:
            result['num'] = like_font + 1
            result['percent'] = str(int(max_like_count * 100.0 / 88)) + '%'
        return result

    def get_image_from_url(self, url):
        r = requests.get(url)
        return Image.open(StringIO(r.content))

    def get_match_results(self, image):
        results = []
        sub_images = self.crop_image(image)
        for sub_image in sub_images:
            result = self.match(sub_image)
            results.append(result)
        return results

    def result_tostring(self, results):

        result_string = ''
        for result in results:
            result_map = result
            result_string += str(result_map['num'])
        return result_string

    def vcode_break(self, image):
        # image = self.get_image_from_url(self.url)
        # process image
        image = self.process(image)
        results = self.get_match_results(image)
        result_string = self.result_tostring(results)
        print('matched result: ' + result_string)
       # image.save("d:/vcode/" + result_string + '.gif')
        return result_string
