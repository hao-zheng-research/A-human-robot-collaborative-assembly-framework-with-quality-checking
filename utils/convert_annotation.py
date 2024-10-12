import json
import os



def get_middle_step_annotation(input, output,video_name):
    file = json.load(open(input,'r'))
    new_data = {}

    hand_counter = 0
    ball_seat_counter = 0
    cylinder_bracket_counter =0
    shaft_counter = 0
    nut_counter = 0
    spacer_large_counter = 0
    spacer_small_counter = 0
    screw_hex_counter = 0
    screw_pilips_counter = 0
    for item in file[0]['tracks']:
        key = 'label'
        if item[key] == 'Hand':
                item['object_id'] = f'Hand_{hand_counter}'
                hand_counter += 1
        elif item[key] == 'Ball Seat':
                item['object_id'] = f'Ball Seat_{ball_seat_counter}'
                ball_seat_counter += 1
        elif item[key] == 'Cylinder Bracket':
                item['object_id'] = f'Cylinder Bracket_{cylinder_bracket_counter}'
                cylinder_bracket_counter += 1
        elif item[key] == 'Shaft':
                item['object_id'] = f'Shaft_{shaft_counter}'
                shaft_counter += 1
        elif item[key] == 'Nut':
                item['object_id'] = f'Nut_{nut_counter}'
                nut_counter += 1
        elif item[key] == 'Spacer Large':
                item['object_id'] = f'Spacer Large_{spacer_large_counter}'
                spacer_large_counter += 1 
        elif item[key] == 'Spacer Small':
                item['object_id'] = f'Spacer Small_{spacer_small_counter}'
                spacer_small_counter += 1            
        elif item[key] == 'Screw (hex)':
                item['object_id'] = f'Screw (hex)_{screw_hex_counter}'
                screw_hex_counter += 1      
        elif item[key] == 'Screw (philips)':
                item['object_id'] = f'Screw (philips)_{screw_pilips_counter}'
                screw_pilips_counter += 1
        else:
                item['object_id'] = f'{item[key]}_0'                 

    new_data['video'] = video_name
    new_data['track'] = file[0]['tracks']
    with open(output,'w') as f:
        json.dump(new_data, f, indent=4)
    return

def get_frame_object_bbox(input, output,video_name):
    file = open(input,'r')
    print(input)
    new_data = {}
    new_data['video'] = video_name

    action_dic = {}
    for line in file.readlines():
        track_id = line.split(',')[1]
        category_id = line.split(',')[-2]
        action_dic[track_id] = category_id    
    [2, 6, 8, 18, 19, 20, 21, 41]
    value_2_counter = 0
    value_6_counter = 0
    value_8_counter = 0
    value_18_counter = 0
    value_19_counter = 0
    value_20_counter = 0
    value_21_counter = 0
    value_41_counter = 0
    action_new_dic = {}
    for key, value in action_dic.items():
        if int(value) == 1:
            action_new_dic[key] = value
        elif int(value) == 2:
             action_new_dic[key] = int(value) + value_2_counter
             value_2_counter += 1
        elif int(value) in [3, 4, 5]:
             action_new_dic[key] = int(value) + 1
        elif int(value) == 6:
             action_new_dic[key] = int(value) + 1 + value_6_counter
             value_6_counter += 1
        elif int(value) == 7:
             action_new_dic[key] = int(value) + 2
        elif int(value) == 8:
             action_new_dic[key] = int(value) + 2 + value_8_counter
             value_8_counter += 1
        elif int(value) in [9, 10, 11, 12, 13, 14, 15, 16, 17]:
             action_new_dic[key] = int(value) + 3
        elif int(value) == 18:
             action_new_dic[key] = int(value) + 3 + value_18_counter
             value_18_counter += 1
        elif int(value) == 19:
             action_new_dic[key] = int(value) + 4 + value_19_counter
             value_19_counter += 1 
        elif int(value) == 20:
             action_new_dic[key] = int(value) + 5 + value_20_counter
             value_20_counter += 1 
        elif int(value) == 21:
             action_new_dic[key] = int(value) + 6 + value_21_counter
             value_21_counter += 1
        elif int(value) in [22, 23, 24, 25, 26, 27, 28, 29, 30 ,31, 32, 33, 34, 35, 36, 37, 38, 39, 40]:
             action_new_dic[key] = int(value) + 9
        elif int(value) == 41:
             action_new_dic[key] = int(value) + 9 + value_41_counter
             value_41_counter += 1
        elif int(value) == 42:
             action_new_dic[key] = int(value) + 10
        else:
             print('no value found: ', value)

    frame_num = 0
    file1 = open(input,'r')
    for line in file1.readlines():
        frame_id = line.split(',')[0]
        if frame_num < int(frame_id):
            frame_num = int(frame_id)
    frames=[]
    for i in range(frame_num):
        frame_id = i + 1
        frame = {}
        frame['frame'] = frame_id
        frame['object_location'] =[None]*52
        frame['object_location'][49] = [0,0,0,0]
        frame['object_location'][50] = [0,0,0,0]
        file2 = open(input,'r')

        for line in file2.readlines():
            if line.split(',')[0] == str(frame_id):
                track_id = line.split(',')[1]
                object_id = action_new_dic[track_id]
                location = [float(line.split(',')[2]),float(line.split(',')[3]),float(line.split(',')[4]),float(line.split(',')[5])]
                frame['object_location'][int(object_id)-1] = location
        frames.append(frame)
    new_data['frames'] = frames
    with open(output,'w') as f:
        json.dump(new_data, f, indent=4)

    return

    
def find_object_in_frame(data,object,frame):
    location = []
    for item in data['track']:
        if item['object_id'] == object:
            for bbox in item['shapes']:
                if bbox['frame'] == frame:
                    location = bbox['points']
    return location

def get_annotation(input,output):
    data = json.load(open(input,'r'))
    new_data = {}
    new_data['video'] = data['video']
    video_length = 0
    for item in data['track']:
        frame_num = item['shapes'][-1]['frame']
        if frame_num > video_length:
             video_length = frame_num

    frames=[]
    for frame in range(video_length+1):
        new_frame = {}
        new_frame['frame'] = frame
        new_frame['object_location'] = []
        for object in object_list:
            location = find_object_in_frame(data,object,frame)
            if location:
                new_frame['object_location'].append(find_object_in_frame(data,object,frame))
            else:
                new_frame['object_location'].append(None)
        frames.append(new_frame)

    new_data['frames'] = frames
    with open(output,'w') as f:
        json.dump(new_data, f, indent=4)
    
    return

def get_video_name(split, task):
    task_index = int(task.split('_')[1])
    if split == 'test':
        file = open('./video_list_test.txt','r')
        lines = file.readlines()
        video_name = lines[task_index].split('.')[0]
    else:
        file = open('./video_list_train.txt','r')
        lines = file.readlines()
        video_name = lines[task_index].split('.')[0]

    return video_name       

if __name__ == "__main__":
    object_list = ["Ball_0", "Ball Seat_0", "Ball Seat_1", "Box_0", "Cylinder Base_0", "Cylinder Cap_0", "Cylinder Bracket_0", "Cylinder Bracket_1", "Cylinder Subassembly_0", "Shaft_0", "Shaft_1", "Gear Large_0", "Gear Small_0", "Worm Gear_0", "Hand-dial_0", "Quarter-turn Handle_0", "Hand-wheel_0", "Bar_0", "Rod_0", "Linear Bearing_0", "Nut_0", "Nut_1", "Spacer Large_0", "Spacer Large_1" "Spacer Small_0", "Spacer Small_1", "Screw (hex)_0", "Screw (hex)_1", "Screw (hex)_2", "Screw (hex)_3", "Screw (philips)_0", "USB Male_0", "Hole C1_0", "Hole C2_0", "Hole C3_0", "Hole C4_0", "Hole G1 (GL)_0", "Hole G2 (GS)_0", "Hole G3 (GW)_0", "Hole N1 (NR)_0", "Hole N2 (NB)_0", "Hole N3 (NL)_0", "Hole N4 (NS)_0", "Hole/Stud N5 (NN)_0", "Hole N6 (NU)_0", "Screwdriver (hex)_0", "Screwdriver (philips)_0", "Wrench (nut)_0", "Wrench (shaft)_0", "Hand_0", "Hand_1", "Bolt_0"]
    
    data_split = ['test','train']

    root_path = r"D:/HA-ViD/MOT/"
    output_folder = './annotations/'
    for split in data_split:
        input_folder = root_path + split
        for task in os.listdir(input_folder):
            task = 'task_' + str(i)
            if task == 'project.json':
                continue
            else:
                input_file = input_folder + '/'+ task +'/gt/gt.txt'
                video_name = get_video_name(split, task)
                
                annotation_path = output_folder +split+'/'+task
                if not os.path.exists(annotation_path):
                    os.makedirs(annotation_path)
                annotation_file = annotation_path + '/annoations.json'
                get_frame_object_bbox(input_file, annotation_file, video_name)
                
                #annotation_path = output_folder + split + '/' + task
                #if not os.path.exists(annotation_path):
                #    os.makedirs(annotation_path)
                #annotation_file = annotation_path + '/annotations.json'
                #get_annotation(annotation_middle_step,annotation_file)
