import os

root_path = './annotations/'

splits = ['train', 'test']

for split in splits:
    task_folders = os.listdir(root_path + split)
    for task_folder in task_folders:
        folder_path = root_path + split + '/' + task_folder
        
        if not os.path.exists(folder_path + '/' + 'labels'):
                os.makedirs(folder_path + '/' + 'labels')

        for file in ['lh_aa.txt', 'rh_aa.txt']:
            original_file_path = folder_path + '/' + file
            
            target_file_path = folder_path + '/' + 'labels' + '/' + file

            mapping_file = open('./action_mapping.txt','r')
            mapping_labels = mapping_file.readlines()
            mapping_labels = [s.split(' ')[-1] for s in mapping_labels]

            original_file = open(original_file_path,'r')
            target_file = open(target_file_path, 'w')
            for line in original_file.readlines():
                label_number = str(mapping_labels.index(line))
                target_file.write(label_number+'\n')

        for file in ['lh_pt.txt', 'rh_pt.txt']:
            original_file_path = folder_path + '/' + file
            
            target_file_path = folder_path + '/' + 'labels' + '/' + file

            mapping_file = open('./task_mapping.txt','r')
            mapping_labels = mapping_file.readlines()
            mapping_labels = [s.split(' ')[-1] for s in mapping_labels]

            original_file = open(original_file_path,'r')
            target_file = open(target_file_path, 'w')
            for line in original_file.readlines():
                label_number = str(mapping_labels.index(line))
                target_file.write(label_number+'\n')
                


            



