import glob, os
for avi_tmp in glob.glob('Result\*\*.avi.tmp'):
    os.system(f'del {avi_tmp}')
