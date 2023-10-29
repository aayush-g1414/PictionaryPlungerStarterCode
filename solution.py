# IMPORTANT
# unless you're willing to change the run.py script, keep the new_case, guess, and add_score methods.
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

    return [[[x / max_value * 255 for x in stroke[0]], [y / max_value * 255 for y in stroke[1]]] for stroke in drawing]

def rdp_simplify(drawing):
    return [points_to_stroke(simplify_coords(stroke_to_points(stroke), 2.0)) for stroke in drawing]

def vector_to_raster(vector_images, side=28, line_diameter=16, padding=16, bg_color=(0,0,0), fg_color=(1,1,1)):
    """
    padding and line_diameter are relative to the original 256x256 image.
    """
    
    original_side = 256.0
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, side, side)
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(line_diameter)

    # scale to match the new size
    # add padding at the edges for the line_diameter
    # and add additional padding to account for antialiasing
    total_padding = padding * 2. + line_diameter
    new_scale = float(side) / float(original_side + total_padding)
    ctx.scale(new_scale, new_scale)
    ctx.translate(total_padding / 2., total_padding / 2.)

    raster_images = []
    for vector_image in vector_images:
        # clear background
        ctx.set_source_rgb(*bg_color)
        ctx.paint()
        
        bbox = np.hstack(vector_image).max(axis=1)
        offset = ((original_side, original_side) - bbox) / 2.
        offset = offset.reshape(-1,1)
        centered = [stroke + offset for stroke in vector_image]

        # draw strokes, this is the most cpu-intensive part
        ctx.set_source_rgb(*fg_color)        
        for xv, yv in centered:
            ctx.move_to(xv[0], yv[0])
            for x, y in zip(xv, yv):
                ctx.line_to(x, y)
            ctx.stroke()

        data = surface.get_data()
        raster_image = np.copy(np.asarray(data)[::4])
        raster_images.append(raster_image)
    
    return raster_images

class Solution:
    def __init__(self):
        pass

    # this is a signal that a new drawing is about to be sent
    def new_case(self):
        # datapoint: {category: str, strokes: list[list[int], list[int]]}

        
        pass

    # given a stroke, return a string of your guess
    def guess(self, x: list[int], y: list[int]) -> str:
        img = vector_to_raster(scale(shift(rdp_simplify([x, y]))), side=256, line_diameter=16, padding=16).reshape(256, 256)
        plt.imshow(img)
        plt.show()
        myGuess = input("Guess: ")
        return myGuess
        pass

    # this function is called when you get
    def add_score(self, score: int):
        print(score)
        pass
