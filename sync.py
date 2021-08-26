#from genericpath import isfile
import os, shutil, sys
import time, datetime

### Phil 20210814 ###
sync_log_csv = os.path.join(os.path.expanduser('~'), 'Desktop', 'sync_log.csv')
upload_progress_ns = os.path.join(os.getcwd(), 'upload_progress.ns')

local_Result = os.path.join(os.getcwd(), "Result")
local_logs = os.path.join(os.getcwd(), "logs")
local_ReportSyncLog = os.path.join(os.getcwd(), "ReportSyncLog")

netdrive = r"N:"
netdrive_Result = r"N:Result"
netdrive_logs = r'N:logs'
netdrive_ReportSyncLog = r'N:ReportSyncLog'
###

# netdrive_Result = r"C:\Users\b03501063\Desktop\AWS2"
# netdrive_ReportSyncLog = r'C:\Users\b03501063\Desktop\AWS2\ReportSyncLog'
# netdrive_logs = r'C:\Users\b03501063\Desktop\AWS2\logs'

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
        print(f"({dir_name}\t local: {get_dir_size(dir_src_path)}\t netdrive : {get_dir_size(dir_des_path)})")
        return get_dir_size(dir_src_path) > get_dir_size(dir_des_path)
    if method == "f":
        print(f"({dir_name}\t local: {os.path.getsize(dir_src_path)}\t netdrive: {os.path.getsize(dir_des_path)})")
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

if __name__ == '__main__':
    with open(upload_progress_ns, 'w') as upload_progress:
        upload_progress.write('...\n')

    dt = datetime.datetime.today()
    log_file_name = f"log_{dt.date()}_{dt.hour}-{dt.minute}-{dt.second}.txt"
    log_file_name = os.path.join(local_ReportSyncLog, log_file_name)
    original_stdout = sys.stdout

    # Syncing and Logging local_ReportSyncLog
    with open(log_file_name, 'w') as f:
        sys.stdout = f
        if os.path.exists(netdrive):
            # Result
            if not os.path.exists(netdrive_Result):
                os.mkdir(netdrive_Result)
            # logs
            if not os.path.exists(netdrive_logs):
                os.mkdir(netdrive_logs)
            # ReportSyncLog
            if not os.path.exists(netdrive_ReportSyncLog):
                os.mkdir(netdrive_ReportSyncLog)

            # Result folders
            local_Result_folders = crawler(local_Result, "d")
            netdrive_Result_folders = crawler(netdrive_Result, "d")
            # logs files
            local_logs_files = crawler(local_logs, "f")
            netdrive_logs_files = crawler(netdrive_logs, "f")
            # ReportSyncLog files
            local_ReportSyncLog_files =crawler(local_ReportSyncLog, "f")
            netdrive_ReportSyncLog_files = crawler(netdrive_ReportSyncLog, "f")

            print("=== Result folders to sync ===")
            intersection_dir_list = compare_two_list(local_Result_folders, netdrive_Result_folders, "i")
            #print("=== Compare Same Dir Size (..\Result) ===")
            intersection_dir_list = [d for d in intersection_dir_list if compare_size(d, local_Result, netdrive_Result, "d")]
            difference_dir_list = compare_two_list(local_Result_folders, netdrive_Result_folders, "d")
            sync_dir_list = sorted(intersection_dir_list + difference_dir_list)
            print('\n'.join(sync_dir_list))
            print()

            print('=== logs files to sync ===')
            intersection_report_file_list = compare_two_list(local_logs_files, netdrive_logs_files, "i")
            #print("=== Compare Same Log Files Size (..\logs) ===")
            intersection_report_file_list = [f for f in intersection_report_file_list if compare_size(f, local_logs, netdrive_logs, "f")]
            difference_report_file_list = compare_two_list(local_logs_files, netdrive_logs_files, "d")
            sync_report_file_list = sorted(intersection_report_file_list + difference_report_file_list)
            print('\n'.join(sync_report_file_list))
            print()

            print('=== ReportSyncLog files to sync ===')
            difference_sync_file_list = compare_two_list(local_ReportSyncLog_files, netdrive_ReportSyncLog_files, "d")
            sync_sync_file_list = sorted(difference_sync_file_list)
            #print("\n=== File Sync List ===")
            print('\n'.join(sync_sync_file_list))
            print()

            if not os.path.exists(sync_log_csv):
                with open(sync_log_csv, 'a') as sync_log:
                    sync_log.write('Date,Time,Synced folder,Synced files\n')
            with open(sync_log_csv, 'a') as sync_log:
                print("Syncing patient folders in Result...")
                uploading = uploaded = 0
                for idx, dir in enumerate(sync_dir_list):
                    uploading += len(os.listdir(os.path.join(local_Result, dir)))
                with open(upload_progress_ns, 'a') as upload_progress:
                    upload_progress.write('0\n')
                for idx, dir in enumerate(sync_dir_list):
                    #print(f"({idx+1}/{len(sync_dir_list)}) Syncing {dir}")
                    sync_dir(dir, local_Result, netdrive_Result)
                    #print(f"({idx+1}/{len(sync_dir_list)}) Synced {dir}\n")
                    print(f'{dir} folder is synced. ({idx+1}/{len(sync_dir_list)})')
                    uploaded += len(os.listdir(os.path.join(local_Result, dir)))
                    with open(upload_progress_ns, 'a') as upload_progress:
                        upload_progress.write(f'{100 * uploaded // uploading}\n')

                    sync_log.write(f'{dt.date()},{dt.hour:2d}:{dt.minute:2d}:{dt.second:2d},{dir},')
                    sync_log.write(','.join(os.listdir(os.path.join(local_Result, dir))))
                    sync_log.write('\n')

                if sync_dir_list:
                    print(f"Synced {len(sync_dir_list)} patient folder(s) successfully.\n")
                else:
                    print("Nothing to sync.\n")

            print("Syncing files in logs...")
            for idx, dir in enumerate(sync_report_file_list):
                #print(f"({idx+1}/{len(sync_report_file_list)}) Syncing {dir}")
                sync_file(dir, local_logs, netdrive_logs)
                #print(f"({idx+1}/{len(sync_report_file_list)}) Synced {dir}\n")
                print(f'{dir} is synced. ({idx+1}/{len(sync_report_file_list)})')
            if sync_report_file_list:
                print(f"Synced {len(sync_report_file_list)} log file(s) successfully.\n")
            else:
                print("Nothing to sync.\n")
        else:
            print("Failed to connect to netdrive!")

    sys.stdout = original_stdout
    print("ReportSyncLog finished.")

    if os.path.exists(netdrive):
        print("Syncing ReportSyncLog...")
        for idx, dir in enumerate(sync_sync_file_list):
            #print(f"({idx+1}/{len(sync_sync_file_list)}) Syncing {dir}")
            sync_file(dir, local_ReportSyncLog, netdrive_ReportSyncLog)
            #print(f"({idx+1}/{len(sync_sync_file_list)}) Synced {dir}\n")
            print(f"{dir} is synced. ({idx+1}/{len(sync_sync_file_list)})")
        if sync_sync_file_list:
            print(f"Synced {len(sync_sync_file_list)} ReportSyncLog file(s) successfully.\n")
        else:
            print("Nothing to sync.\n")
    else:
        print("Failed to connect to netdrive!")

### Phil 20210814 ###
    if os.path.exists(netdrive):
        with open(upload_progress_ns, 'a') as upload_progress:
            upload_progress.write('Finish!')
