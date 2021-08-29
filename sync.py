# from genericpath import isfile
import os, shutil, sys
import time, datetime

### Phil 20210829 re.search site to requests.get API
import re, requests

### Phil 20210814 renaming
# SyncLog_csv = os.path.join(os.path.expanduser('~'), 'Desktop', 'SyncLog.csv')
upload_progress_ns = os.path.join(os.getcwd(), 'upload_progress.ns')

local_Result = os.path.join(os.getcwd(), "Result")
local_logs = os.path.join(os.getcwd(), "logs")
local_ReportSyncLog = os.path.join(os.getcwd(), "ReportSyncLog")

Ndrive = r"N:"
Ndrive_Result = r"N:Result"
Ndrive_logs = r'N:logs'
Ndrive_ReportSyncLog = r'N:ReportSyncLog'

# Ndrive_Result = r"C:\Users\b03501063\Desktop\AWS2"
# Ndrive_ReportSyncLog = r'C:\Users\b03501063\Desktop\AWS2\ReportSyncLog'
# Ndrive_logs = r'C:\Users\b03501063\Desktop\AWS2\logs'

# directory processing
def crawler(path: str, method: str):
    if method == 'd':
        dir_list = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        return dir_list
    elif method == 'f':
        file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        return file_list

def get_dir_size(dir: str):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
    return size

def compare_size(dir_name: str, src_path: str, des_path: str, method: str):
    dir_src_path = os.path.join(src_path, dir_name) 
    dir_des_path = os.path.join(des_path, dir_name)
    if method == "d":
        print(f"({dir_name}\t local: {get_dir_size(dir_src_path)}\t Ndrive : {get_dir_size(dir_des_path)})")
        return get_dir_size(dir_src_path) > get_dir_size(dir_des_path)
    if method == "f":
        print(f"({dir_name}\t local: {os.path.getsize(dir_src_path)}\t Ndrive: {os.path.getsize(dir_des_path)})")
        return os.path.getsize(dir_src_path) > os.path.getsize(dir_des_path)

def sync_dir(dir_name: str, ori_path: str, target_path: str):
    ori_dir_path = os.path.join(ori_path, dir_name)
    target_dir_path = os.path.join(target_path, dir_name)
    if os.path.exists(target_dir_path):
        shutil.rmtree(target_dir_path)
        #print(f"Deleted: {target_dir_path}")
        print(f'{target_dir_path} folder is deleted.')
 
    t = 0
    while os.path.exists(target_dir_path):
        print(f"{t}..")
        time.sleep(1)
        t += 1

    shutil.copytree(ori_dir_path, target_dir_path)
    #print(f"Moved: {dir_name}")

def sync_file(file_name: str, ori_path: str, target_path: str):
    ori_file_path = os.path.join(ori_path, file_name)
    target_file_path = os.path.join(target_path, file_name)
    if os.path.exists(target_file_path):
        os.remove(target_file_path)
        #print(f"Deleted: {target_file_path}")
        print(f'{target_file_path} file is deleted.')
 
    t = 0
    while os.path.exists(target_file_path):
        print(f"{t}..")
        time.sleep(1)
        t += 1

    shutil.copy2(ori_file_path, target_file_path)
    #print(f"Moved: {file_name}")

# comparison of list
def compare_two_list(src_list: list, des_list: list, method: str):
    if method == 'i':
        return sorted(list(set(src_list).intersection(des_list)))
    elif method == 'd':
        return sorted(list(set(src_list).difference(des_list)))

try:
    with open(upload_progress_ns, 'w') as upload_progress:
        upload_progress.write('...\n')

    dt = datetime.datetime.today()
    yyyymmdd, hhmmss = str(dt).split('.')[0].split()
    yyyymmdd, hhmmss = yyyymmdd.replace('-', ''), hhmmss.replace(':', '')
    log_file_name = f'{yyyymmdd}_{hhmmss}_site.txt'
    log_file_name = os.path.join(local_ReportSyncLog, log_file_name)
    original_stdout = sys.stdout

    # Syncing and Logging local_ReportSyncLog
    with open(log_file_name, 'w') as f:
        sys.stdout = f
        if os.path.exists(Ndrive):
            # Result
            if not os.path.exists(Ndrive_Result):
                os.mkdir(Ndrive_Result)
            # logs
            if not os.path.exists(Ndrive_logs):
                os.mkdir(Ndrive_logs)
            # ReportSyncLog
            if not os.path.exists(Ndrive_ReportSyncLog):
                os.mkdir(Ndrive_ReportSyncLog)

            # Result folders
            local_Result_folders = crawler(local_Result, "d")
            Ndrive_Result_folders = crawler(Ndrive_Result, "d")
            # logs files
            local_logs_files = crawler(local_logs, "f")
            Ndrive_logs_files = crawler(Ndrive_logs, "f")
            # ReportSyncLog files
            local_ReportSyncLog_files =crawler(local_ReportSyncLog, "f")
            Ndrive_ReportSyncLog_files = crawler(Ndrive_ReportSyncLog, "f")

            ### Phil 20210829
            site = re.search('H\d\d', str(local_Result_folders)).group(0)

            print("=== Result folders to sync ===")
            Result_folders_inter = compare_two_list(local_Result_folders, Ndrive_Result_folders, "i")
            #print("=== Compare Same Dir Size (..\Result) ===")
            Result_folders_inter = [d for d in Result_folders_inter if compare_size(d, local_Result, Ndrive_Result, "d")]
            Result_folders_diff = compare_two_list(local_Result_folders, Ndrive_Result_folders, "d")
            Result_folders_sync = sorted(Result_folders_inter + Result_folders_diff)
            print('\n'.join(Result_folders_sync))
            print()

            ### Phil 20210829
            payload = {'site': site, 'case': Result_folders_sync}
            requests.get('https://deqg3un8ha.execute-api.eu-central-1.amazonaws.com/start', params=payload)

            print('=== logs files to sync ===')
            logs_files_inter = compare_two_list(local_logs_files, Ndrive_logs_files, "i")
            #print("=== Compare Same Log Files Size (..\logs) ===")
            logs_files_inter = [f for f in logs_files_inter if compare_size(f, local_logs, Ndrive_logs, "f")]
            logs_files_diff = compare_two_list(local_logs_files, Ndrive_logs_files, "d")
            logs_files_sync = sorted(logs_files_inter + logs_files_diff)
            print('\n'.join(logs_files_sync))
            print()

            print('=== ReportSyncLog files to sync ===')
            ReportSyncLog_files_diff = compare_two_list(local_ReportSyncLog_files, Ndrive_ReportSyncLog_files, "d")
            ReportSyncLog_files_sync = sorted(ReportSyncLog_files_diff)
            #print("\n=== File Sync List ===")
            print('\n'.join(ReportSyncLog_files_sync))
            print()

            if not os.path.exists('SyncLog.csv'):
                with open('SyncLog.csv', 'a') as synclog:
                    synclog.write('Date,Time,Synced folder,Synced files\n')
            with open('SyncLog.csv', 'a') as synclog:
                print("Syncing patient folders in Result...")
                uploading = uploaded = 0
                for idx, dir in enumerate(Result_folders_sync):
                    uploading += len(os.listdir(os.path.join(local_Result, dir)))
                with open(upload_progress_ns, 'a') as upload_progress:
                    upload_progress.write('0\n')
                for idx, dir in enumerate(Result_folders_sync):
                    #print(f"({idx+1}/{len(Result_folders_sync)}) Syncing {dir}")
                    sync_dir(dir, local_Result, Ndrive_Result)
                    #print(f"({idx+1}/{len(Result_folders_sync)}) Synced {dir}\n")
                    print(f'{dir} folder is synced. ({idx+1}/{len(Result_folders_sync)})')
                    uploaded += len(os.listdir(os.path.join(local_Result, dir)))
                    with open(upload_progress_ns, 'a') as upload_progress:
                        upload_progress.write(f'{100 * uploaded // uploading}\n')

                    synclog.write(f'{dt.date()},{dt.hour:2d}:{dt.minute:2d}:{dt.second:2d},{dir},')
                    synclog.write(','.join(os.listdir(os.path.join(local_Result, dir))))
                    synclog.write('\n')

                if Result_folders_sync:
                    print(f"Synced {len(Result_folders_sync)} patient folder(s) successfully.\n")
                else:
                    print("Nothing to sync.\n")

            ### Phil 20210829 SyncLog.csv on Desktop
            try:
                os.system(f"copy SyncLog.csv {os.path.join(os.path.expanduser('~'), 'Desktop')}")
                print('Succeed to copy SyncLog.csv to Desktop')
            except:
                os.system(f"copy SyncLog.csv {os.path.join(os.path.expanduser('~'), 'Desktop', 'During_syncing_you_have_to_close_SyncLog.csv')}")
                print('Fail to copy SyncLog.csv to Desktop')
            
            print("Syncing files in logs...")
            for idx, dir in enumerate(logs_files_sync):
                #print(f"({idx+1}/{len(logs_files_sync)}) Syncing {dir}")
                sync_file(dir, local_logs, Ndrive_logs)
                #print(f"({idx+1}/{len(logs_files_sync)}) Synced {dir}\n")
                print(f'{dir} is synced. ({idx+1}/{len(logs_files_sync)})')
            if logs_files_sync:
                print(f"Synced {len(logs_files_sync)} log file(s) successfully.\n")
            else:
                print("Nothing to sync.\n")
        else:
            print("Failed to connect to Ndrive!")
            raise Exception

    sys.stdout = original_stdout
    print("ReportSyncLog finished.")

    ### Phil 20210829 ReportSyncLog rename on Windows
    os.system(f"move {log_file_name} {log_file_name.replace('site', site)}")

    if os.path.exists(Ndrive):
        print("Syncing ReportSyncLog...")
        for idx, dir in enumerate(ReportSyncLog_files_sync):
            #print(f"({idx+1}/{len(ReportSyncLog_files_sync)}) Syncing {dir}")
            sync_file(dir, local_ReportSyncLog, Ndrive_ReportSyncLog)
            #print(f"({idx+1}/{len(ReportSyncLog_files_sync)}) Synced {dir}\n")
            print(f"{dir} is synced. ({idx+1}/{len(ReportSyncLog_files_sync)})")
        if ReportSyncLog_files_sync:
            print(f"Synced {len(ReportSyncLog_files_sync)} ReportSyncLog file(s) successfully.\n")
        else:
            print("Nothing to sync.\n")
    else:
        print("Failed to connect to Ndrive!")
        raise Exception

### Phil 20210830
except:
    with open(upload_progress_ns, 'a') as upload_progress:
        upload_progress.write('Fail!')
else:
    with open(upload_progress_ns, 'a') as upload_progress:
        upload_progress.write('Finish!')