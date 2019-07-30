# -*-coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from flask import Flask,jsonify
from flask import request,render_template
import os

import click
app = Flask(__name__,template_folder=sys.path[0])

CMD = {
    'status': 'ps -ef |grep -v grep  |  grep dnsmasq &>/dev/null  && echo  -n $? || echo -n  $?' ,
    'pid': " ps -ef |grep -v grep  |  grep dnsmasq   | awk '{print $2}'",
    'restart': 'service dnsmasq restart &>/dev/null && echo -n $? || echo -n $?',
    'check': 'dnsmasq   --conf-file=/tmp/dnsmasq.conf   --test &>/tmp/state  && echo  -n $? || echo -n  $?',
}



def getDnsInfo():
    dnsinfo = {}
    if  os.popen(CMD['status']).read() == '0':
        dnsinfo['status'] = 'running'
        dnsinfo['pid'] = os.popen(CMD['pid']).read()
    else:
        dnsinfo['status'] = 'stoped'
    return  dnsinfo

@app.route('/', methods=['GET'])
def home():
    dnsinfo = getDnsInfo()
    with open(serverInfo['conffile'],'r') as f:
        dnscontent = f.read()

    with open(serverInfo['hostfile'],'r') as f:
        hostcontent = f.read()


    return render_template(
        'home.html',
         dnscontent   = dnscontent,
         hostcontent  = hostcontent,
         host         = serverInfo['host'] + ':' + str(serverInfo['port']),
         dnsinfo      = dnsinfo
         )

@app.route('/postdns', methods=['POST'])
def post_form():
    data = request.get_json(force=True)
    print(data)
    dnscontent  =   data['dnscontent']
    hostcontent =  data['hostcontent']
    ops =  data['ops']
    print(ops,dnscontent)
    if ops == 'post' or ops == 'check':
        with open(serverInfo['hostfile'], 'w') as f:
            f.write(hostcontent)

        result = checkCfg(dnscontent)
        if result == True:
            status = {'status': '检查配置成功！'}
            if ops == 'post':
                with open(serverInfo['conffile'], 'w') as f:
                    f.write(dnscontent)
                status = {'status': '提交配置成功！'}
        else:
            status = {'status': result}

    elif ops == 'restart':
        if os.popen(CMD['restart']).read() == '0':
            dnsinfo = getDnsInfo()
            status = {'status': '重启成功！','dnsinfo': dnsinfo}
        else:
            status = {'status': '重启失败！','dnsinfo': dnsinfo}
    else:
        status = {'status': '请求错误！'}

    return jsonify(status)

def checkCfg(dnscontent):
    with open('/tmp/dnsmasq.conf','w') as f:
        f.write(dnscontent)

    result = os.popen(CMD['check']).read()
    if result  == '0':
        return True
    else:
        with open('/tmp/state','r') as f:
            result = f.read().replace('of /tmp/dnsmasq.conf','')
        return  result

@click.command()
@click.option('--host',         default='0.0.0.0',          help='请指定服务绑定的ip(默认0.0.0.0)')
@click.option('--port',         default=8008,               help='请指定服务运行的端口(默认8008)')
@click.option('--username',     default='admin',            help='请指定服务账号(默认admin)')
@click.option('--password',     default='admin',            help='请指定服务密码(默认admin)')
@click.option('--conffile',     default='/etc/dnsmasq.conf',    help='请指定dnsmasq配置文件路径(默认/etc/dnsmasq.conf)')
@click.option('--hostfile',     default='/etc/hosts',           help='请指定hosts配置文件路径(默认/etc/hosts)')


def run(host, port,username,password,conffile,hostfile):
    """Simple program that greets NAME for a total of COUNT times."""
    # app.run()
    global  serverInfo
    serverInfo = {}
    serverInfo['host'] = host
    serverInfo['port'] = port
    serverInfo['username'] = username
    serverInfo['password'] = password
    serverInfo['conffile'] = conffile
    serverInfo['hostfile'] = hostfile

    app.run(host=host, port=port)

if __name__ == '__main__':
    # base_path = os.path.dirname(os.path.abspath(__file__))
    # sys.path.insert(0, base_path)
    # print(base_path)

    run()