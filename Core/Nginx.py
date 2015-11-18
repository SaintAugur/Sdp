#!/usr/bin/env python
#-*- coding=utf8 -*-
__author__ = 'saintic'
__date__ = '2015-11-12'
__doc__ = 'If type = WEBS, next nginx and code manager(ftp,svn)'
__version__ = 'sdp1.1'

import os,Public,Redis,subprocess,commands

class CodeManager():
  def __init__(self, index):
    self.rc = Redis.RedisObject()
    if self.rc.ping():
      self.user = self.rc.hashget(index)
      self.name = self.user['name']
      self.passwd = self.user['passwd']
      self.userhome = self.user['userhome']
      self.ip = self.user['ip']
      self.port = self.user['port']
      self.dn = self.user.get('dn', None)
    else:
      return 1

  def ftp(self):
    if Public.FTP_TYPE == 'virtual':
      ftp_user_list = r'''%s
%s
''' %(self.name, self.passwd)

      ftp_content_conf = r'''write_enable=YES
anon_world_readable_only=NO
anon_upload_enable=YES
anon_mkdir_write_enable=YES
anon_other_write_enable=YES
local_root=%s''' % self.userhome

      with open(Public.FTP_VFTPUSERFILE, 'a+') as f:
        f.write(ftp_user_list)

      with open(os.path.join(Public.FTP_VFTPUSERDIR, self.name), 'w') as f:
        f.write(ftp_content_conf)

      subprocess.call(['db_load -T -t hash -f ' + Public.FTP_VFTPUSERFILE + ' ' + Public.FTP_VFTPUSERDBFILE], shell=True)
      subprocess.call(['/etc/init.d/vsftpd restart'], shell=True)
      subprocess.call(['chown -R ' + Public.FTP_VFTPUSER + ':' + Public.FTP_VFTPUSER + ' ' + self.userhome], shell=True)
      subprocess.call(['chmod -R a+t ' + self.userhome], shell=True)

  def Proxy(self):
    ngx_user_conf = os.path.join(Public.PROXY_DIR, self.name) + '.conf'
    ngx_conf_content = r'''server {
    listen %s:80;
    server_name %s;
    index index.htm index.html index.php index.jsp;
    location / {
       proxy_pass http://%s:%s/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
''' %('0.0.0.0', self.dn, self.ip, int(self.port))
    
    with open(ngx_user_conf, 'w') as f:
      f.write(ngx_conf_content)
    status,output = commands.getstatusoutput(Public.NGINX_EXEC + ' -s reload')
    if status == 0:
      if os.environ['LANG'].split('.')[0] == 'zh_CN':
        print '\033[0;32;40mSuccess:Reload Nginx\033[0m' + ' ' * 39 +'[' + '\033[0;32;40m确定\033[0m' + ']'
      else:
        print '\033[0;32;40mSuccess:Reload Nginx\033[0m' + ' ' * 39 +'[ ' + '\033[0;32;40m OK \033[0m' + ' ]'
    else:
      print "\033[0;31;40mRelod Nginx Error:\033[0m", output
