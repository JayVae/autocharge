# coding=utf-8
from imp import reload
from io import StringIO

import requests
import re
import time
import vcodeprocess_final
from PIL import Image
from numpadimgbreak_final import NumPadBreak
import sys
import traceback
from myemail import myemail


vcode_url = 'http://card.xjtu.edu.cn/Account/GetCheckCodeImg/Flag=' + str(int(time.time() * 100))
transform_account_url = 'http://card.xjtu.edu.cn/CardManage/CardInfo/TransferAccount'
num_pad_image_url = 'http://card.xjtu.edu.cn/Account/GetNumKeyPadImg'
login_url = 'https://cas.xjtu.edu.cn/login?service=http://card.xjtu.edu.cn:8050/Account/CASSignIn'
default_log_file = 'charge.log'
headers = {
    'Host': 'cas.xjtu.edu.cn',
    'Origin': 'https://cas.xjtu.edu.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': '0',
    'Referer': 'https://cas.xjtu.edu.cn/login?service=http://card.xjtu.edu.cn:8050/Account/CASSignIn',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    # 'Content-Length': '150',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Upgrade-Insecure-Requests': '1'
}


def convert_password(password, result):
    try:
        result_string = ''
        for p in password:
            result_string += str(result.index(p))
        return result_string
    except Exception as e:
        print(e)
        return None


def save_to_default_file(r):
    with open(default_log_file, 'a') as f:
        f.write('\n'+r)
    pass


def my_print(string):
    r =str(time.asctime()) + '  ' + str(string)
    save_to_default_file(r)
    print(r)


if __name__ == '__main__':
    try:
        reload(sys)
        sys.setdefaultencoding('utf-8')
        my_print('init...')
        session = requests.session()
        It = ''
        execution = ''
        submit = '登录'
        iPlanetDirectoryPro = ''
        params = {
            'username': 'yejiawei',
            'password': 'Yejiawei19921121',
            'code': '',
            'lt': It,
            'execution': execution,
            '_eventId': 'submit',
            'submit': submit
        }

        my_print('login begin ...')
        login_response = session.get(login_url, headers=headers)
        text = login_response.text
        p = re.compile("<input type=\"hidden\" name=\"lt\" value=\"(.+?)\"")
        It = p.findall(text)[0]
        p = re.compile("<input type=\"hidden\" name=\"execution\" value=\"(.+?)\"")
        execution = p.findall(text)[0]
        params['lt'] = It
        params['execution'] = execution
        for i in range(5):
            time.sleep(2)
            login_response = session.post(login_url, data=params, headers=headers)
            iPlanetDirectoryPro = login_response.cookies.get('iPlanetDirectoryPro')
            if iPlanetDirectoryPro is not None and iPlanetDirectoryPro != '' and len(iPlanetDirectoryPro) == 48:
                break
            text = login_response.text
            print(text)
            p = re.compile("<input type=\"hidden\" name=\"lt\" value=\"(.+?)\"")
            It = p.findall(text)[0]
            p = re.compile("<input type=\"hidden\" name=\"execution\" value=\"(.+?)\"")
            execution = p.findall(text)[0]
            params['lt'] = It
            params['execution'] = execution
        # except Excep
        my_print('login success ...')
        # amt = input(str(time.asctime())+": input num:")
        basic_info_url = 'http://card.xjtu.edu.cn/CardManage/CardInfo/BasicInfo?' + str(int(time.time() * 100))
        basic_info_response = session.get(basic_info_url)
        p = re.compile("<em>(\d+\.*\d*)</em>")
        text = basic_info_response.text
        find_result = p.findall(text)
        balance = float(find_result[1])
        balance_remain = float(find_result[2])
        my_print('balance: '+str(balance))
        my_print('balance_remain: '+str(balance_remain))
        balance_sum = balance + balance_remain
        my_print('balance_sum: '+ str(balance_sum))

        amt = 0
        if balance_sum < 30.0:
            my_print(200.0 - balance_sum)
            amt = 70
        data = {
            'amt': amt,
            'bankno': '',
            'bankpwd': '',
            'checkCode': '',
            'fcard': 'bcard',
            'password': '',
            'tocard': 'card'
        }
        if amt == 0:
            my_print('amount is enough')
            exit()

        my_print('charge amount: ' + str(amt))
        try:
            response = session.get(vcode_url, headers=headers)
            image = Image.open(StringIO(response.content))
            image.save('image/vcode.gif')
            vcode_Break = vcodeprocess_final.VcodeBreak()
            data['checkCode'] = vcode_Break.vcode_break(image)
            for i in range(10):
                num_response = session.get(num_pad_image_url, headers=headers)
                num_pad_image = Image.open(StringIO(num_response.content))
                num_pad_image.save('image/num_pad_image.jpg')
                num_pad_break = NumPadBreak()
                result = num_pad_break.break_numpadimage(num_pad_image)
                password = [4, 9, 0, 9, 5, 1]
                result_string = convert_password(password, result)
                data['password'] = result_string
                if result_string is not None:
                    break
            response = session.post(transform_account_url, data=data, headers=headers)
            my_print(response.text)
        except Exception as e:
            my_print(traceback.format_exc(e))
            msg = u'卡上余额不足，充值失败！！'
            myemail().sendmessage(msg.encode('utf-8'))
    except Exception as e:
        my_print(traceback.format_exc(e))
    finally:
       my_print("===================================")
