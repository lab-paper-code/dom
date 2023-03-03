import os
from datetime import datetime

path = '/home/palisade2/dom/share/data/log'

fileList = os.listdir(path)

beforeStatus = ''
beforeTime = ''
loss = 0
total = 0
totalSize = 0
totalTime = 0

for file in fileList:
    total = 0
    beforeTime = ''
    beforeStatus = ''
    loss = 0
    totalSize = 0
    totalTime = 0
    totalTime_one_file = 0
    entire_filesize = 0
    current_filesize = 0
    loss_size = 0
    total_loss_size = 0
    count_loss_size = 0
    
    first_start_time = 0
    last_end_time = 0
    
    cpu_max = 0
    cpu_min = 100
    cpu_sum = 0
    cpu_avg = 0
    total_cpu_avg = 0

    if file.endswith('.log'):
        print(file)
        with open(file) as f:
            lines = f.readlines()
        
        for index, l in enumerate(lines):            
            
            line = l.split()
            
            time = line[0] + ' '+ line[1]
            time = time[1:len(time)-1]
            try:
                datetime = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
            except:
                if cpu_max < float(line[0]):
                    cpu_max = float(line[0])
                if cpu_min > float(line[1]):
                    cpu_min = float(line[1])
                #cpu_sum = line[2]
                cpu_avg = float(line[3])
                total_cpu_avg += cpu_avg
            
            if index == 0:
                first_start_time = datetime
                
            send_ip = line[2]
            
            fileName = line[5]
            
            fileSize = line[6]
            fileSize = float(fileSize[:len(fileSize)-3])
            
            status = line[8]
            if status == 'start':
                total += 1
                beforeTime = datetime
                entire_filesize = fileSize
            elif status == 'end':
                last_end_time = datetime
                
            if beforeStatus == 'start':
                current_filesize = fileSize
                loss_size = entire_filesize - current_filesize
                if loss_size != 0:
                    count_loss_size += 1
                total_loss_size += loss_size
                if status != 'end':
                    loss += 1
                    continue
                duration = datetime - beforeTime
                duration = duration.total_seconds()
                
                totalSize += float(fileSize)
                totalTime_one_file += duration             
                
            beforeStatus = status
        totalTime = (last_end_time - first_start_time).total_seconds()
        print('totalSize: {}MB, latency: {}s'.format(totalSize, totalTime))
        print('throughput: %f(MB/s)' % (float(totalSize) / totalTime))
        print('throughput2onefile: %f(MB/s)' % (float(totalSize) / totalTime_one_file))
        print('loss rate: {}%'.format(float(loss) / float(total) * 100))
        print('file size loss rate: {}%'.format(float(total_loss_size) / float(total) * 100))
        print('file size loss count rate: {}%'.format(float(count_loss_size) / float(total) * 100))
        print('CPU usage: max: {}, min: {}, avg: {}'.format(cpu_max, cpu_min, total_cpu_avg / float(total)))
        print()
        print()
