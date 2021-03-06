import datetime, requests, json, ConfigParser, pickle, os, re
from requests_oauthlib import OAuth1Session

def splitMsg(s):
    s.strip('\r\n')
    prefix = ''
    trailing = []
    if not s:
       return
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()
    command = args.pop(0)
    return prefix, command, args
    
def sendMsg(self, c, m):
    print(self.tag + c + " :: " + m)
    maxsize = 512 - 14 - len(c)
    if len(m) > maxsize:
        count = int(math.ceil(len(m) / maxsize))
        print(self.tag + "Message is " + str(len(m)) + " bytes long, splitting into " + str(count) + " pieces.")
        msglist = []
        for x in range(0,count+1):
            if (x+1)*maxsize > len(m):
                msglist.append(m[x*maxsize:])
            else:
                msglist.append(m[x*maxsize:(x+1)*maxsize])
        for i in msglist:
            self.irc.send("PRIVMSG " + c + " :" + i + "\r\n")
    else:
        self.irc.send("PRIVMSG " + c + " :" + m + "\r\n")

def sendNtc(self, c, m):
    print(self.tag + c + " :: " + m)
    maxsize = 512 - 14 - len(c)
    if len(m) > maxsize:
        count = int(math.ceil(len(m) / maxsize))
        print(self.tag + "Message is " + str(len(m)) + " bytes long, splitting into " + str(count) + " pieces.")
        msglist = []
        for x in range(0,count+1):
            if (x+1)*maxsize > len(m):
                msglist.append(m[x*maxsize:])
            else:
                msglist.append(m[x*maxsize:(x+1)*maxsize])
        for i in msglist:
            self.irc.send("NOTICE " + c + " :" + i + "\r\n")
    else:
        self.irc.send("NOTICE " + c + " :" + m + "\r\n")

def joinChan(self, c):
    print(self.tag + "Joining " + c)
    self.irc.send("JOIN " + c + "\r\n")

def goAway(self, m):
    print(self.tag + "Quitting with message: " + m)
    self.irc.send("QUIT :" + m + "\r\n")
    self.isConnected = False
    
def getTimeStamp():
    now = datetime.datetime.now()
    return str(now.year) + '/' + str(now.month) + '/' + str(now.day) + '|' + str(now.hour) + ':' + str(now.minute) + ':' + str(now.second)
    
#These take the list object from splitMsg
def getPrefix(l):
    return l[0]

def getNick(l):
    if l[0].find('!') != -1:
        nick = l[0][:l[0].find('!')]
    else:
        nick = ''
    return nick
    
def getMask(l):
    if l[0].find('!') != -1:
        mask = l[0][l[0].find('!')+1:]
    elif not l[0].equals(''):
        mask = l[0]
    else:
        mask = ''
    return mask
    
def getCommand(l):
    return l[1]
    
def getChannel(self, l):
    if l[2][0].startswith('#'):
        chan = l[2][0]
    elif l[2][0] == self.nick:
        chan = getNick(l)
    else:
        chan = ''
    return chan
    
def getMessage(self, l):
    try:
        if getChannel(self, l):
            message = l[2][1]
        else:
            message = ''
    except:
        message = ''
    return message

def getIgnore(m):
    try:
        with open('ignore.dat', 'rb') as f:
            data = pickle.load(f)
        for n in data:
            if re.match(n, splitMsg(m)[0]):
                return True
        return False
    except:
        return False

def getTweet(self, m, url):
    config = ConfigParser.RawConfigParser()
    config.readfp(open('default.cfg'))

    access_token = config.get('twitter', 'access_token')
    access_token_secret = config.get('twitter', 'access_token_secret')
    consumer_key = config.get('twitter', 'consumer_key')
    consumer_secret = config.get('twitter', 'consumer_secret')
    twitter = OAuth1Session(consumer_key, consumer_secret, access_token, access_token_secret)

    id = url[url.find('/status/')+8:]
    r = twitter.get('http://api.twitter.com/1.1/statuses/show.json?id=' + id).json()
    try:
        sendMsg(self, getChannel(self, m), '@\00313' + r['user']['screen_name'] + '\003 :: ' + r['text'])
    except:
        sendMsg(self, getChannel(self, m), 'I couldn\'t get that tweet, sorry.')
        print r