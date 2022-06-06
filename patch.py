import glob, os
for avi_tmp in glob.glob(os.path.join(os.getcwd(), 'Result\*\*.avi.tmp')):
    os.system(f'del {avi_tmp}')
