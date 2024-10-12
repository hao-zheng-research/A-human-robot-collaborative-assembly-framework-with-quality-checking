import torch

def compensate_node(tensor, node_idx):
    num_frames, num_nodes, node_dim = tensor.shape
    
    # Extract the coordinates of the specific node across all frames
    node_coords = tensor[:, node_idx, :]
        
    # Find the indices of frames where the node is missing ([0,0,0,0])
    missing_frames = (node_coords == torch.zeros(node_dim).to(node_coords.device)).all(dim=1)
    
    # Loop through each frame to compensate missing coordinates
    for i in range(num_frames):
        if missing_frames[i]:
            # Find the nearest previous frame where the node is not missing
            prev_frame = i - 1
            while prev_frame >= 0 and missing_frames[prev_frame]:
                prev_frame -= 1
            
            # Find the nearest next frame where the node is not missing
            next_frame = i + 1
            while next_frame < num_frames and missing_frames[next_frame]:
                next_frame += 1
            
            # If both previous and next frames are found, interpolate
            if prev_frame >= 0 and next_frame < num_frames:
                alpha = (i - prev_frame) / (next_frame - prev_frame)
                tensor[i, node_idx, :] = (1 - alpha) * node_coords[prev_frame, :] + alpha * node_coords[next_frame, :]
            
            # If only previous frame is found, use its coordinates
            elif prev_frame >= 0:
                tensor[i, node_idx, :] = node_coords[prev_frame, :]
            
            # If only next frame is found, use its coordinates
            elif next_frame < num_frames:
                tensor[i, node_idx, :] = node_coords[next_frame, :]
    return tensor

def compensate_node_batch(tensor, node_idx):
    batch_size, num_frames, num_nodes, node_dim = tensor.shape
    
    for b in range(batch_size):
        # Work on each batch individually
        for i in range(num_frames):
            # Extract the coordinates of the specific node across all frames for the current batch
            node_coords = tensor[b, :, node_idx, :]

            # Find the indices of frames where the node is missing ([0,0,0,0])
            missing_frames = (node_coords == torch.zeros(node_dim).to(node_coords.device)).all(dim=1)

            for i in range(num_frames):
                if missing_frames[i]:
                    # Find the nearest previous frame where the node is not missing
                    prev_frame = i - 1
                    while prev_frame >= 0 and missing_frames[prev_frame]:
                        prev_frame -= 1

                    # Find the nearest next frame where the node is not missing
                    next_frame = i + 1
                    while next_frame < num_frames and missing_frames[next_frame]:
                        next_frame += 1

                    # If both previous and next frames are found, interpolate
                    if prev_frame >= 0 and next_frame < num_frames:
                        alpha = (i - prev_frame) / (next_frame - prev_frame)
                        tensor[b, i, node_idx, :] = (1 - alpha) * tensor[b, prev_frame, node_idx, :] + alpha * tensor[b, next_frame, node_idx, :]

                    # If only previous frame is found, use its coordinates
                    elif prev_frame >= 0:
                        tensor[b, i, node_idx, :] = tensor[b, prev_frame, node_idx, :]

                    # If only next frame is found, use its coordinates
                    elif next_frame < num_frames:
                        tensor[b, i, node_idx, :] = tensor[b, next_frame, node_idx, :]
    return tensor

def compensate_all_nodes_efficiently(tensor):
    num_frames, num_nodes, node_dim = tensor.shape
    device = tensor.device
    
    # Identify missing coordinates (assuming [0,0,0,0] represents missing)
    missing_mask = (tensor == torch.zeros(node_dim, device=device)).all(dim=2)
    
    # Create a tensor to hold the compensated coordinates
    compensated_tensor = tensor.clone()
    
    for node_idx in range(num_nodes):
        node_missing_mask = missing_mask[:, node_idx]
        if not node_missing_mask.any():
            # Skip if there are no missing frames for this node
            continue

        valid_frames = torch.where(~node_missing_mask)[0]
        if len(valid_frames) == 0:
            # If all frames are missing, there's nothing to compensate
            continue

        for i, is_missing in enumerate(node_missing_mask):
            if is_missing:
                # Find the closest valid frames before and after the missing frame
                valid_before = valid_frames[valid_frames < i]
                valid_after = valid_frames[valid_frames > i]
                
                prev_frame = valid_before[-1] if len(valid_before) > 0 else None
                next_frame = valid_after[0] if len(valid_after) > 0 else None
                
                if prev_frame is not None and next_frame is not None:
                    # Linear interpolation
                    alpha = (i - prev_frame) / (next_frame - prev_frame)
                    compensated_tensor[i, node_idx, :] = (1 - alpha) * tensor[prev_frame, node_idx, :] + alpha * tensor[next_frame, node_idx, :]
                elif prev_frame is not None:
                    compensated_tensor[i, node_idx, :] = tensor[prev_frame, node_idx, :]
                elif next_frame is not None:
                    compensated_tensor[i, node_idx, :] = tensor[next_frame, node_idx, :]

    return compensated_tensor