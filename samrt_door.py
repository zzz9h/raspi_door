import _thread
import threading
from aip import AipFace
from picamera import PiCamera
import urllib.request #32
import RPi.GPIO as GPIO
import base64
import time
import sys
import cv2
import os
import smtplib
from picamera.array import PiRGBArray
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
import socket
# 百度人识别API信息
APP_ID = '##################'
API_KEY = '###################'
SECRET_KEY = '##############'
client = AipFace(APP_ID, API_KEY, SECRET_KEY)  # 创建客户端访问百度云
# 图像编码方式base64
IMAGE_TYPE = 'BASE64'

# 用户组
GROUP = '01'
GPIO_OUT = 17  # 定义gpio输出口
BUTTON=18
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
BUTTON1=27
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON1,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
BUTTON2=22
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON2,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
def app_server():
        HOST_IP = "192.168.199.192"
        HOST_PORT = 9090
        rev=b'\xe8\xa7\xa3\xe9\x94\x81\xe6\x88\x90\xe5\x8a\x9f\n'
        print("Starting socket: TCP...")
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         
        print("TCP server listen @ %s:%d!" %(HOST_IP, HOST_PORT) )
        host_addr = (HOST_IP, HOST_PORT)
        socket_tcp.bind(host_addr)
        socket_tcp.listen(1)    
         
        while True:
                init_gpio()
                print ('waiting for connection...')
                socket_con, (client_ip, client_port) = socket_tcp.accept()
                print("Connection accepted from %s." %client_ip)
                while True:
                        data=socket_con.recv(1024)
                        if data:
                                print(data)
                                data1=data[1]
                                print(data1)
                        if data1 ==188:
                                print("解锁成功")
                                setGPIO_OUTAngle(17,100)
                                socket_con.send(rev)
                                time.sleep(5)
                        if data1 ==167:
                                print("解锁成功")
                                setGPIO_OUTAngle(17,100)
                                socket_con.send(rev)
                                time.sleep(5)
                        
                        
        socket_tcp.close()
def menu():    
    while True:
        init_gpio()
        value=GPIO.input(BUTTON) 
        if value ==1:
            print(123)
            video()
            time.sleep(0.1)
def video():
    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = (1920, 1080)
    camera.framerate = 60
    rawCapture = PiRGBArray(camera, size=(1920, 1080))

    # allow the camera to warmup
    time.sleep(0.1)
    
    # capture frames from the camera
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        rawCapture.truncate(0)
        image = frame.array

        # show the frame
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        value1=GPIO.input(BUTTON1)
        value2=GPIO.input(BUTTON2)
        if value1 ==1:
            print(321)
            setGPIO_OUTAngle(GPIO_OUT, 100)  # 调用舵机函数
            time.sleep(5)
            setGPIO_OUTAngle(GPIO_OUT, 10)  # 调用舵机函数
            rawCapture.truncate(0)
            frame.seek(0)
            frame.truncate()
            camera.close()
            cv2.destroyAllWindows()
            
            break
        if value2 ==1:
            print(231)
            setGPIO_OUTAngle(GPIO_OUT, 10)  # 调用舵机函数
            rawCapture.truncate(0)
            frame.seek(0)
            frame.truncate()
            camera.close()
            cv2.destroyAllWindows()
            
            menu()
            break   
# 为线程定义一个函数
#发送邮件函数
# 功能：发送解锁记录到邮箱
# 参数：log_info：用户名，时间
# 返回值：无
def smtp_email(log_info):
    # 1.连接邮箱服务器:
    con=smtplib.SMTP_SSL('smtp.qq.com' ,465)
    # 2.登陆邮箱
    #连接对象.login(id,passwd)
    #密码-写授权码
    con.login('2986627051@qq.com' , '################')
    # 3.准备数据
    msg=MIMEMultipart()
    #设置邮件的主题
    subject=Header('登录提醒','utf-8').encode()
    msg['Subject']=subject

    #设置邮件发送人
    msg['From']='2986627051@qq.com '
    #设置邮件的收件人
    msg['To']='1987698934@qq.com'
    #设置邮件内容
    
    #html文本创建
    content="""
    <h1>登陆记录</h1>
    <h3>人脸识别门禁系统</h3>
    <p>'{}'</p>
    <img src='cid:dsaf'>
    """
    content1=content.format(log_info)
    html =MIMEText(content1,'html','utf-8')

    #4.发送邮件
    #读取图片
    fp=open('faceimage.jpg','rb').read()
    image1=MIMEImage(fp)
    image1["Content-Disposition"]='attachment; filename="faceimage.jpg"'
    image1.add_header('Content-ID','<dsaf>')
    msg.attach(image1)
    msg.attach(html)
    con.sendmail('2986627051@qq.com','15004780816@163.com',msg.as_string())
    con.quit()



# 拍照函数
# 功能：使用opencv的级联分类器检测人脸，当检测到人脸保存图片
# 参数：无
# 返回值：无
def face_detection():
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)  # set video width
    cam.set(4, 480)  # set video height
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    print("\n [INFO] Initializing face capture. Look the camera and wait ...")
    # Initialize individual sampling face count
    count = 0
    while (True):
        ret, img = cam.read()
        img = cv2.flip(img, 1)  # flip video image vertically
        #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(img, 1.3, 5)
        falg = 0
        for (x, y, w, h) in faces:
            # cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)    
            # Save the captured image into the datasets folder
            time.sleep(1)
            cv2.imwrite('faceimage.jpg' , img)
            falg = 1
            time.sleep(1)
            cam.release()
            break
        if falg == 1:
            break


# 初始化舵机函数
# 功能：无
# 参数：无
# 返回值：无
def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(GPIO_OUT, GPIO.OUT)


# 计算pwm占空比函数
# 功能：计算角度用来控制舵机旋转
# 参数：GPIO_OUT：pwm波输出引脚
# angle：旋转角度
# 返回值：无
def setGPIO_OUTAngle(GPIO_OUT, angle):  # 参数1：输出GPIO口  参数2：角度
    pwm = GPIO.PWM(GPIO_OUT, 50)  # pwm波产生周期
    pwm.start(8)
    dutyCycle = float(angle) / 18 + 2.5  # pwm占空比计算
    pwm.ChangeDutyCycle(dutyCycle)
    time.sleep(0.3)
    pwm.stop()  # pwm波停止函数，不加会导致电机只能运行一次

# 图片格式转换函数
# 功能：转换图片格式为base64
# 参数：无
# 返回值：img转换好的图片
def transimage():
    f = open('faceimage.jpg', 'rb')
    img = base64.b64encode(f.read())
    return img

def face_verify(img):
    image=str(img,'UTF-8')
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceverify"
    params = "[{\"image\":\"" + image + "\",\"image_type\":\"BASE64\",\"face_field\":\"age,beauty,expression\"}]"
    #params = "['{}','BASE64']"
    #params.format(image)
    access_token = '[ 24.cd22c9eb048cfabbd84400714119732f.2592000.1597982423.282335-19374140]'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        print(response.json())
    return response.json()["result"]["face_liveness"]

# 上传到百度api函数
# 功能：上转到百度智能云进行人脸库搜索
# 参数：base64格式的图片
# 返回值：用户id，相似度，人脸名字
def go_api(image):
    result1=face_verify(image)
    if result1 >0.8:
        result = client.search(str(image, 'utf-8'), IMAGE_TYPE, GROUP);  # 在百度云人脸库中寻找是否存在匹配人脸
        if result['error_msg'] == 'SUCCESS':
            name = result['result']['user_list'][0]['user_id']  # 获取id
            score = result['result']['user_list'][0]['score']  # 获取相似度
            curren_time = time.asctime(time.localtime(time.time()))  # 获取当前时间
            print(result)
            print(score)
            if score > 80:  # 相似度>80
                print('欢迎%s!' % name)
                time.sleep(3)
            else:
                print('人脸信息不存在')
                name = '陌生人'
                log_info =name + "在" + str(curren_time) + "进行了解锁"
                smtp_email(log_info)
                f = open('log.txt', 'a')
                f.write("person:" + name + "   " + "time:" + str(curren_time) + '\n')
                f.close()
                return 0

            # 记录日志
            f = open('log.txt', 'a')
            f.write("person:" + name + "   " + "time:" + str(curren_time) + '\n')
            log_info = name + "在" + str(curren_time) + "进行了解锁"
            smtp_email(log_info)
            f.close()
            return 1

        if result['error_msg'] == 'pic not has face':
            print('未检测到人脸')
            time.sleep(2)
            return 0
        else:
            print(result['error_code'] + ' ' + result['error_code'])
            return 0
    else:
        print('请不要使用照片尝试解锁！！')
def thread_1():
    while True:
        init_gpio()  # 初始化舵机
        if True:
            face_detection()
            img= transimage()  # 转换照片格式
            res = go_api(img)  # 将转换好的照片上传到百度云
            if (res == 1):  # 比对成功，是人脸库中的人
                print("开门")
                setGPIO_OUTAngle(GPIO_OUT, 100)  # 调用舵机函数
                GPIO.cleanup()  # 释放脚本中的使
            print("g门")
            time.sleep(3)
            init_gpio()
            setGPIO_OUTAngle(GPIO_OUT, 10) 
def thread_2():
    menu()
def thread_3():
    app_server()

# 创建线程
try:
    threading.Thread(target=thread_1).start()
    threading.Thread(target=thread_2).start()
    threading.Thread(target=thread_3).start()
except:
   print ("Error: 无法启动线程")

while 1:
   pass
