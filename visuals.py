import json
import numpy as np
import cairocffi as cairo
import matplotlib.pyplot as plt
from simplification.cutil import simplify_coords

def stroke_to_points(stroke):
    return [[x, y] for x, y in zip(stroke[0], stroke[1])]

def points_to_stroke(points):
    return [[x for x, y in points], [y for x, y in points]]

def min_drawing(drawing):
    min_x = min([min(stroke[0]) for stroke in drawing])
    min_y = min([min(stroke[1]) for stroke in drawing])
    
    return min_x, min_y

def max_drawing(drawing):
    max_x = max([max(stroke[0]) for stroke in drawing])
    max_y = max([max(stroke[1]) for stroke in drawing])
    
    return max_x, max_y

def shift(drawing):
    min_x, min_y = min_drawing(drawing)

    return [[[x - min_x for x in stroke[0]], [y - min_y for y in stroke[1]]] for stroke in drawing]

def scale(drawing):
    max_value = max(max_drawing(drawing))
    if max_value == 0:
        return drawing
    return [[[x / max_value * 255 for x in stroke[0]], [y / max_value * 255 for y in stroke[1]]] for stroke in drawing]

def rdp_simplify(drawing):
    return [points_to_stroke(simplify_coords(stroke_to_points(stroke), 2.0)) for stroke in drawing]

def vector_to_raster(vector_images, side=28, line_diameter=16, padding=16, bg_color=(0,0,0), fg_color=(1,1,1)):
    original_side = 256.0
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(line_diameter)
    
    raster_images = []
    for vector_image in vector_images:
        ctx.set_source_rgb(*bg_color)
        ctx.paint()
        
        bbox = np.hstack(vector_image).max(axis=1)
        offset = ((original_side, original_side) - bbox) / 2.
        offset = offset.reshape(-1,1)
        centered = [stroke + offset for stroke in vector_image]
        
        ctx.set_source_rgb(*fg_color)
        for xv, yv in centered:
            ctx.move_to(xv[0], yv[0])
            for x, y in zip(xv, yv):
                ctx.line_to(x, y)
            ctx.stroke()
        
        data = surface.get_data()
        raster_image = np.copy(np.asarray(data)[::4])
        raster_images.append(raster_image.reshape(side, side))
    
    return raster_images

with open('./cases/writing_utensil.ndjson') as f:
    data = f.readlines()

strokes = []
for line in data:
    stroke = json.loads(line)
    strokes.append(stroke['strokes'])

# Parameters for subplot layout
# num_frames = len(strokes[0])
# num_rows = 10   # Number of rows in the subplot grid
# num_cols = 10   # Number of columns in the subplot grid
# fig, axes = plt.subplots(num_rows, num_cols, figsize=(10, 10))
print(len(strokes))
iterations =  len(strokes) // 100
connected = []

for x in range(5):
    # print(x)
    # print(connected)
    counter = 0
    num_frames = len(strokes[0])
    num_rows = 10   # Number of rows in the subplot grid
    num_cols = 10   # Number of columns in the subplot grid
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(10, 10))
  
    for i in range(0, len(strokes), iterations): # len(strokes)
        counter += 1
        # frame_strokes = []
        # for stroke in strokes:
        #     try:
        #         frame_strokes.append(stroke[i])
        #     except:
        #         pass
        
        #for j, frame in enumerate(strokes[i]):
        try:
            frame = strokes[i][x]
            if x == 0:
                connected.append([frame])
                # print(len(connected[0]))
            else:
                connected[counter] += [frame]
                # print(len(connected[0]))
            # Modify this line to view each image frame by frame
            image = vector_to_raster([scale(shift(rdp_simplify(connected[counter])))], side=256, line_diameter=8, padding=8)[0]
        
            row = counter // num_cols
            col = counter % num_cols
            axes[row, col].imshow(image)
            axes[row, col].axis('off')
        except:
            pass

    plt.show()
        # import time
        # time.sleep(10)