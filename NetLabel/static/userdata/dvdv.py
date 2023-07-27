import os
import numpy as np
print(os.listdir(f'jim'))
folders = os.listdir(f'jim')
# print(np.sort(os.listdir(f'jim')))

# os.listdir(f'jim').sort(key=lambda x: len(x.split('.')) > 1)

for i in os.listdir(f'jim'):
    print(int(i.split('-')[0].split('_')[0]+i.split('-')[0].split('_')[1]))

def extract_datetime(folder_name):
    # 設定資料夾名稱的格式為 'YYYYMMDD_HHMMSS'
    # 例如 '20230723_150202'
    date_str, time_str = folder_name.split('-')[0].split('_')
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    hour = int(time_str[:2])
    minute = int(time_str[2:4])
    second = int(time_str[4:6])
    return (year, month, day, hour, minute, second)

sorted_folders = sorted(folders, key=extract_datetime, reverse=True)

print(sorted_folders)
