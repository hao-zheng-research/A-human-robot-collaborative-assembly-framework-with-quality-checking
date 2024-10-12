import torch
import torch.nn.functional as F

def bounding_box_to_center(input_tensor):
    """
    Convert bounding box coordinates to center point positions.
    
    Args:
    - input_tensor (torch.Tensor): Tensor of shape (num_frame, num_node, 4)
      where each 4-vector represents the bounding box [x_min, y_min, x_max, y_max]
    
    Returns:
    - center_points (torch.Tensor): Tensor of shape (num_frame, num_node, 2)
      where each 2-vector represents the center point [x_center, y_center]
    """
    # Extract bounding box coordinates
    x_min = input_tensor[:, :, 0]
    y_min = input_tensor[:, :, 1]
    x_width = input_tensor[:, :, 2]
    y_height = input_tensor[:, :, 3]
    
    # Compute center point positions
    x_center = x_min + x_width / 2
    y_center = y_min + y_height / 2
    
    # Combine x_center and y_center into a single tensor
    center_points = torch.stack([x_center, y_center], dim=-1)
    
    return center_points

def calculate_attention_scores(input_tensor, num_prev_frames=5):
    """
    Calculate the attention scores based on directional cosine similarity.

    Parameters:
    - input_tensor: numpy array of shape (num_frame, num_node, node_feature)
      where node_feature is the bounding box coordinates of the object.

    Returns:
    - attention_map: numpy array of shape (num_frame, num_node, num_node)
    """
    # Initialize variables
    num_frame, num_node, _ = input_tensor.shape
    # attention_map = torch.zeros((num_frame, num_node, num_node)).to(input_tensor.device)
    attention_map_left_hand = torch.zeros((num_frame,num_node)).to(input_tensor.device)
    attention_map_right_hand = torch.zeros((num_frame,num_node)).to(input_tensor.device)

    center_points = bounding_box_to_center(input_tensor)
    
    for t in range(num_prev_frames, num_frame):  # Starting from 1 because we need t-1
        # Calculate velocity for left_hand and right_hand at frame t
        velocity_left_hand = center_points[t, 49, :] - torch.mean(center_points[t-num_prev_frames:t, 49, :], dim=0)
        velocity_right_hand = center_points[t, 50, :] - torch.mean(center_points[t-num_prev_frames:t, 50, :], dim=0)
        norm_left_hand = torch.linalg.norm(velocity_left_hand)
        norm_right_hand = torch.linalg.norm(velocity_right_hand)
        for j in range(num_node):
            # Calculate velocity for node j at frame t
            velocity_j = center_points[t, j, :] - torch.mean(center_points[t-num_prev_frames:t, j, :], dim=0)
            norm_j = torch.linalg.norm(velocity_j)
        
            if norm_left_hand == 0 or norm_j == 0:
                cosine_similarity_left_hand = 0
            else:
          # Calculate cosine similarity
                cosine_similarity_left_hand = torch.dot(velocity_left_hand, velocity_j) / (norm_left_hand * norm_j)
          
            if norm_right_hand == 0 or norm_j == 0:
                cosine_similarity_right_hand = 0
            else:
              # Calculate cosine similarity
                cosine_similarity_right_hand = torch.dot(velocity_right_hand, velocity_j) / (norm_right_hand * norm_j)
          
            attention_map_left_hand[t, j] = cosine_similarity_left_hand
            attention_map_right_hand[t, j] = cosine_similarity_right_hand
            
    # Get rid of the self-connected attention score   
    # attention_map_left_hand = torch.cat((attention_map_left_hand[:, :49], attention_map_left_hand[:, 50:]), dim=1)
    # attention_map_right_hand = torch.cat((attention_map_right_hand[:, :50], attention_map_right_hand[:, 51:]), dim=1)
    attention_map_left_hand[:, 49] = 0
    attention_map_right_hand[:, 50] = 0
                       
    # Apply softmax to the attention scores for each node at frame t
    attention_map_left_hand[:, :] = torch.softmax(attention_map_left_hand[:, :], axis=-1)
    attention_map_right_hand[:, :] = torch.softmax(attention_map_right_hand[:, :], axis=-1)
    return attention_map_left_hand, attention_map_right_hand