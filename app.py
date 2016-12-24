from __future__ import absolute_import, unicode_literals
import os
import sys
from PIL import Image
import random
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
######################################## Embeding of Text and Image ###########################################


DIST = 8


def normalize_pixel(r, g, b):
    """
    pixel color normalize
    :param r: int
    :param g: int
    :param b: int
    :return: (int, int, int)
    """
    if is_modify_pixel(r, g, b):
        seed = random.randint(1, 3)
        if seed == 1:
            r = _normalize(r)
        if seed == 2:
            g = _normalize(g)
        if seed == 3:
            b = _normalize(b)
    return r, g, b


def modify_pixel(r, g, b):
    """
    pixel color modify
    :param r: int
    :param g: int
    :param b: int
    :return: (int, int, int)
    """
    return map(_modify, [r, g, b])


def is_modify_pixel(r, g, b):
    """
    :param r: int
    :param g: int
    :param b: int
    :return: bool
    """
    return r % DIST == g % DIST == b % DIST == 1


def _modify(i):
    if i >= 128:
        for x in xrange(DIST + 1):
            if i % DIST == 1:
                return i
            i -= 1
    else:
        for x in xrange(DIST + 1):
            if i % DIST == 1:
                return i
            i += 1
    raise ValueError


def _normalize(i):
    if i >= 128:
        i -= 1
    else:
        i += 1
    return i


def normalize(path):

    img = Image.open(path)
    img = img.convert('RGB')
    size = img.size
    new_img = Image.new('RGB', size)

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b = img.getpixel((x, y))
            _r, _g, _b = normalize_pixel(r, g, b)
            new_img.putpixel((x, y), (_r, _g, _b))
    new_img.save(path, "PNG", optimize=True)


def hide_text(path, text):
    
    text = str(text)

    # convert text to hex for write
    write_param = []
    _base = 0
    for _ in to_hex(text):
        write_param.append(int(_, 16) + _base)
        _base += 16

    # hide hex-text to image
    img = Image.open(path)
    counter = 0
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if counter in write_param:
                r, g, b = img.getpixel((x, y))
                r, g, b = modify_pixel(r, g, b)
                img.putpixel((x, y), (r, g, b))
            counter += 1

    # save
    img.save(path, "PNG", optimize=True)


def to_hex(s):
    return s.encode("hex")


def to_str(s):
    return s.decode("hex")
###############################################################################################################

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')


# Route that will process the file upload
@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    # Get the name of the uploaded file
    if request.method == 'POST':
      file = request.files['upl']
    #file = request.files['input_image']
    #img=request.form['input_image']
      text=request.form['alt_text'] 
    # Check if the file is one of the allowed types/extensions
    # Make the filename safe, remove unsupported chars
      filename = secure_filename(file.filename)
      #result={'image':filename,'text':text}   # Dictionary to store image name and text
      #result = request.form
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ################################# Encrypt here ####################
        img=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        normalize(img)
        hide_text(img, text)
        ###################################################################
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        #return redirect(url_for('uploaded_file',filename=filename))
        #return "Image Uploaded and Embeded"
        #return redirect(url_for('uploaded_file',result=result))
        return render_template("results.html",result = filename)
    # Move the file form the temporal folder to
    # the upload folder we setup
    #filename.save(filename)
    #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # f.save(secure_filename(f.filename))
    
    
# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return render_template("results.html",result = filename)
    #return filename
    #return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
    #send_from_directory(app.config['UPLOAD_FOLDER'],filename)

if __name__ == '__main__':
    app.run(debug=True)
