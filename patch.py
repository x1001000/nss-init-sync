import glob, os
for avi_tmp in glob.glob(os.path.join(os.getcwd(), 'Result\*\*.avi.tmp')):
    os.system(f'del {avi_tmp}')
with open('sync.py', 'r') as f:
    lines = f.readlines()
with open('sync.py', 'w') as f:
    lines[36] = "        size += sum([os.path.getsize(os.path.join(root, name)) for name in files if 'avi' not in name])\n"
    lines[63] = "    shutil.copytree(ori_dir_path, target_dir_path, ignore=shutil.ignore_patterns('*avi*'))\n"
    f.writelines(lines)