import glob, os
for avi_tmp in glob.glob('Result.{2559a1f2-21d7-11d4-bdaf-00c04f60b9f0}\*\*.avi.tmp'):
    os.system(f'del {avi_tmp}')
