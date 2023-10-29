# Sample participant submission for testing
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
        # print(vector_image)
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
        raster_images.append(raster_image.reshape(side, side))
    
    return raster_images

from flask import Flask, request, jsonify, make_response, send_file
from solution import Solution
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
sol = Solution()
global globalGuess
globalGuess = [None, True, False]
# BOILERPLATE
@app.route("/newcase", methods=["POST"])
def new_case():
    sol.new_case()
    return jsonify(success=True)

@app.route("/scored", methods=["GET"])
def scored():
    return {"scored": globalGuess[2], 'correct': globalGuess[0]}

@app.route("/disableScored", methods=["GET"])
def disableScored():
    globalGuess[2] = False
    return {}

@app.route("/guess", methods=["POST"])
def guess():
    data = request.get_json()
    data = json.loads(data)
    try:
        while globalGuess[2]:
            pass
        x, y = tuple(data["stroke"])
        listOfStrokes = sol.guess(x, y)
        img = vector_to_raster([scale(shift(rdp_simplify(listOfStrokes)))], side=256, line_diameter=16, padding=16)[0]
        #socketio.emit('message', img)
        # plt.imshow(img)
        # plt.show()
        # plt.close()

        # save img to file
        plt.imsave("pictionary\src\img.png", img)
        # check if img exists in directory
        import os
        globalGuess[1] = True
        while globalGuess[1]:
            pass
        import os
        os.unlink("pictionary\src\img.png")


        # send information to my react app
        

        guess = globalGuess[0]
        print("guess {}".format(guess))
    except:
        guess = "tool"
    ret_data = {"guess": guess}

    response = jsonify(ret_data)
    return response

@app.route("/score", methods=["POST"])
def score():
    globalGuess[2] = True
    data = request.get_json()
    data = json.loads(data)

    score = data["score"]
    print("score {}".format(score))
    sol.add_score(score)
    
    return jsonify(success=True)

@app.route("/getImage", methods=["GET"])
def getImage():
    import os
    if os.path.exists("pictionary\src\img.png"):
        with open("pictionary\src\img.png", "rb") as f:
            img = f.read()
        #print(img)
        from base64 import b64encode
        img = b64encode(img).decode("utf-8")
        return jsonify({"image": img})
    else:
        return jsonify({"image": None})

@app.route("/finalGuess", methods=["POST"])
def finalGuess():
    
    data = request.get_json()
    globalGuess[0] = data["guess"]
    globalGuess[1] = False

    return {}

@app.route("/imgExists", methods=["GET"])
def imgExists():
    import os
    if os.path.exists("pictionary\src\img.png"):
        return jsonify({"imgExists": True})
    else:
        return jsonify({"imgExists": False})
    
@app.route("/deleteImg", methods=["GET"])
def deleteImg():
    import os
    os.remove("pictionary\src\img.png")
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
