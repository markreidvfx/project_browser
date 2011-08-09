import os
import platform
import subprocess

import utilities
import timeout_process

def get_avaible_flipbooks():
    
    return ['Shake','RV']



def get_shake():
    
    shake = utilities.find_executable_path('shake')
    
    if shake:
        return shake
    
    if platform.system() == 'Darwin':
        path = '/Applications/Shake/shake.app/Contents/MacOS/shake'
        if os.path.exists(path):
            return path
        
    return None
    


def get_rv():
    rv_exe = ['RV64']
    if platform.machine() == 'i386':
        rv_exe.insert(0, 'RV')
    for exe in rv_exe:
        rv = utilities.find_executable_path(exe)
        if rv:
            return rv
    if platform.system() == 'Darwin':
        rv_paths = ['/Applications/RV64.app/Contents/MacOS/RV64']
        if platform.machine() == 'i386':
            rv_paths.insert(0,'/Applications/RV.app/Contents/MacOS/RV')
            
        for path in rv_paths:
            if os.path.exists(path):
                return path
            
    

def shake_flipbook(file_item,options):
    
    
    shake = get_shake()
    
    cmd = [shake,'-t',options['range'], file_item.content.shake_path()]
    
    
    proxy = options.get('proxy')
    
    if proxy == "P1":
        cmd.extend(['-zoom','.5'])
        
    elif proxy == "P2":
        cmd.extend(['-zoom','.25'])
        
    #print subprocess.list2cmdline(cmd)
    
    return timeout_process.launch_process(cmd)
    
    



def rv_flipbook(file_items,options):
    rv = get_rv()
    #print options
    
    cmd = [rv,'-c','-sRGB']
    
    mode = options.get('mode')
    
    if mode:
        cmd.append(mode)
    
    for item in file_items:
        
        cmd.extend(['[', item.content.shake_path(),']'])
        
    #print subprocess.list2cmdline(cmd) 
        
    return timeout_process.launch_process(cmd)
    