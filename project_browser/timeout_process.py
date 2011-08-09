#Copyright (C) 2011 Mark Reid <mindmark@gmail.com>

#This file is part of Project Browser.

#Project Browser is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#Project Browser is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Project Browser.  If not, see <http://www.gnu.org/licenses/>.

import time
import subprocess

import traceback

import threading
import platform

CREATE_NO_WINDOW = 134217728


class ProccessTimeOut(Exception):
    def __init__(self,value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

def communicate(p,output,stdin):
    
    
    output.extend(p.communicate(stdin))
    
    
def launch_process(cmd,env=None,cwd=None,stdout=None,stderr=None,stdin=None):
    print subprocess.list2cmdline(cmd)
    
    kwargs = {'stdin':stdin,
              'stdout':stdout,
              'stderr':stderr,
              'env':env,
              'cwd':cwd}
    
    if platform.system() == 'Windows':
        kwargs['creationflags'] = CREATE_NO_WINDOW
    
    p = subprocess.Popen(cmd,**kwargs)
    
    return p

def timeout_process(cmd,stdin=None,env=None,cwd=None,timeout=12,raise_exception=True):

    p = launch_process(cmd,env,cwd,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       stdin=subprocess.PIPE)
    
    
    output = []
    
    communicate_thread = threading.Thread(target=communicate,
                                          args=(p, output,stdin))
    
    
    communicate_thread.start()
    
    start_time = time.time()
    pid = p.pid
    while True:
        if p.returncode is None:
            pass
        else:
            break
        
        dur = time.time() -start_time
        
        if dur > timeout:
            #print 'process timed out'
            p.kill()
            if raise_exception:
                raise ProccessTimeOut('pid %i timed out, over %s seconds' % (pid,str(timeout)))
            else:
                break
            
        time.sleep(.05)
    
    
    communicate_thread.join()
    
    
    
    stdout = None
    stderr = None
    if output:
        stdout = output[0]
    if len(output) > 1:
        stderr = output[1]
        
    if p.returncode != 0:
        raise Exception("pid %i exited with errors\n" % pid + stderr)
    
    return stdout,stderr

    
    


if __name__ == '__main__':
    print timeout_process(['ls','/'])[0]
    cmd = ['find','/']
    
    
    timeout_process(cmd,raise_exception=False)
    
    timeout_process(cmd)
    
    
    
  
    
    
    