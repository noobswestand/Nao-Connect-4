from naoqi import ALProxy

ip="10.255.3.76"
port=9559

mp=ALProxy("ALMotion", ip, port)
pp=ALProxy("ALRobotPosture", ip, port)

pp.goToPosture("Sit",1.0)
mp.rest()