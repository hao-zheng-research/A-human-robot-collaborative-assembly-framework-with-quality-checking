import os

def get_file_name(file_path):
    file = file_path.split('/')[-1]
    if file.split('_')[2] == 'pa':
        task_level = 'aa'
    else:
        task_level = 'pt'
    file_name = file.split('_')[0] + '_' + file.split('_')[1] + '_' + task_level
    return file_name, file.split('_')[0], file.split('_')[1], task_level

def find_folder(file_name):
    test_video_file = open('./video_list_test.txt','r')
    train_video_file = open('./video_list_train.txt','r')
    test_videos = test_video_file.readlines()
    test_videos = [s.split('.')[0][:9] for s in test_videos]
    train_videos = train_video_file.readlines()
    train_videos = [s.split('.')[0][:9] for s in train_videos]
    folder_path = ''
    if file_name in test_videos:
        index = test_videos.index(file_name)
        folder_path = './annotations/test/task_'+str(index)
    elif file_name in train_videos:
        index = train_videos.index(file_name)
        folder_path = './annotations/train/task_'+str(index)
    else:
        folder_path = None
    return folder_path

def generate_files(original_file_path, target_file_path):
    original_file = open(original_file_path,'r')
    target_file = open(target_file_path,'w')
    original_labels = original_file.readlines()
    print(original_file_path)
    for line in original_labels:
        if line == '\n' or line == ' ' or line == ' \n':
            continue
        else:
            start = int(line.split(' ')[0])
            end = int(line.split(' ')[1])
            label = line.split(' ')[2]
            
            if '\n' in label:
                label = label
            else:
                label = label + '\n'
                
            for i in range(end-start+1):
                target_file.write(label)
    return


if __name__ == '__main__':
    root_path = r"D:/HA-ViD/action_recognition_labels"

    test_videos_file = open('./video_list_test.txt','r')
    train_videos_file = open('./video_list_train.txt','r')

    test_videos = test_videos_file.readlines()
    test_videos = [s.split('.')[0] for s in test_videos]
    train_videos = train_videos_file.readlines()
    train_videos = [s.split('.')[0] for s in train_videos]
    print(test_videos)

    label_files = os.listdir(root_path)

    index_test = 0
    for test_video in test_videos:
        test_video_short = test_video[:9]
        for label_file in label_files:
            if label_file.split('_')[0] == test_video_short:
                original_file = root_path + '/' + label_file
                if label_file.split('_')[2] == 'pa':
                    task_level = 'aa'
                else:
                    task_level = label_file.split('_')[2]
                target_file = './annotations/test/task_' + str(index_test) + '/' + label_file.split('_')[1] + '_' + task_level + '.txt'
                generate_files(original_file,target_file)
        index_test += 1

    index_train = 0
    for train_video in train_videos:
        train_video_short = train_video[:9]
        for label_file in label_files:
            if label_file.split('_')[0] == train_video_short:
                original_file = root_path + '/' + label_file
                if label_file.split('_')[2] == 'pa':
                    task_level = 'aa'
                else:
                    task_level = label_file.split('_')[2]
                target_file = './annotations/train/task_' + str(index_train) + '/' + label_file.split('_')[1] + '_' + task_level + '.txt'
                generate_files(original_file,target_file)
        index_train += 1


    





    # files = os.listdir(root_path)
    # for file in files:
    #     file_path = root_path + "/" + file
    #     file_name, video_head_name, hand, task_level = get_file_name(file_path)
    #     video_name = file_name.split('_')[0]
    #     print('video_name', video_head_name)
    #     folder_path = find_folder(video_name)
    #     print('folder_path', folder_path)
    #     if folder_path:
    #         target_file_path_M0 = folder_path + '/' + video_head_name + 'M0' + '_' + hand + '_' + task_level +'.txt'
    #         target_file_path_S1 = folder_path + '/' + video_head_name + 'S1' + '_' + hand + '_' + task_level +'.txt'
    #         target_file_path_S2 = folder_path + '/' + video_head_name + 'S2' + '_' + hand + '_' + task_level +'.txt'
    #         generate_files(file_path,target_file_path_M0)
    #         generate_files(file_path,target_file_path_S1)
    #         generate_files(file_path,target_file_path_S2)


