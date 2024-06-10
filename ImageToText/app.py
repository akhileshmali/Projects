from flask import Flask, request, Response, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from db import db_init, db
from models import Img
from transformers import pipeline
import os
from flask import Flask, request, Response, render_template, redirect, flash, url_for

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'pic' not in request.files:
            return 'No pic uploaded!', 400

        pic = request.files['pic']

        if pic.filename == '':
            return 'No selected file!', 400

        if not allowed_file(pic.filename):
            return 'Invalid image format! Allowed formats are png, jpg, jpeg, gif', 400

        # Save the uploaded image temporarily
        upload_folder = './uploads/'
        os.makedirs(upload_folder, exist_ok=True)
        filename = secure_filename(pic.filename)
        pic_path = os.path.join(upload_folder, filename)
        pic.save(pic_path)

        # Check if the image already exists based on its file path
        img = Img.query.filter_by(name=filename).first()
        if img:
            return redirect(url_for('display_images', message='Image already exists!'))

        # Generate caption for the uploaded image
        caption = pipeline('image-to-text')
        description = caption(pic_path)[0]['generated_text']  # Extracting the text from the dictionary

        # Save the image and description to the database
        with open(pic_path, 'rb') as f:
            img_data = f.read()

        img = Img(img=img_data, name=filename, mimetype=pic.mimetype, description=description)
        db.session.add(img)
        db.session.commit()

        return redirect(url_for('display_images', message='Img Uploaded!'))
    except Exception as e:
        return f"Error uploading image: {str(e)}", 500

@app.route('/images')
def display_images():
    try:
        message = request.args.get('message', None)
        images = Img.query.all()
        return render_template('images.html', images=images, message=message)
    except Exception as e:
        return f"Error displaying images: {str(e)}", 500

@app.route('/<int:id>')
def get_img(id):
    try:
        img = Img.query.filter_by(id=id).first()
        if not img:
            return 'Img Not Found!', 404
        return Response(img.img, mimetype=img.mimetype)
    except Exception as e:
        return f"Error retrieving image: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)

#UPLOAD ONLY
# from flask import Flask, request, Response,render_template
# from werkzeug.utils import secure_filename

# from db import db_init, db
# from models import Img

# app = Flask(__name__)
# # SQLAlchemy config. Read more: https://flask-sqlalchemy.palletsprojects.com/en/2.x/
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db_init(app)


# @app.route('/')
# def hello_world():

#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     pic = request.files['pic']
#     if not pic:
#         return 'No pic uploaded!', 400

#     filename = secure_filename(pic.filename)
#     mimetype = pic.mimetype
#     if not filename or not mimetype:
#         return 'Bad upload!', 400

#     img = Img(img=pic.read(), name=filename, mimetype=mimetype)
#     db.session.add(img)
#     db.session.commit()

#     return 'Img Uploaded!', 200


# @app.route('/<int:id>')
# def get_img(id):
#     img = Img.query.filter_by(id=id).first()
#     if not img:
#         return 'Img Not Found!', 404

#     return Response(img.img, mimetype=img.mimetype)


# @app.route('/images')
# def display_images():
#     images = Img.query.all()
#     return render_template('images.html', images=images)

# import warnings,logging
# warnings.simplefilter('ignore')
# logging.disable(logging.WARNING)

# from transformers import pipeline

# caption = pipeline('image-to-text')

# print(caption('./uploads/sample.jpg'))



# import os
# import hashlib

# from flask import Flask, render_template_string, request, Response, render_template, url_for
# from werkzeug.utils import secure_filename
# from db import db_init, db
# from models import Img
# from transformers import pipeline

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db_init(app)

# @app.route('/')
# def hello_world():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload():
#     pic = request.files['pic']
#     if not pic:
#         return 'No pic uploaded!', 400

#     filename = secure_filename(pic.filename)
#     if not filename:
#         return 'Bad upload!', 400

#     # Check if the image already exists based on its file path or content hash
#     img = Img.query.filter_by(name=filename).first()
#     if img:
#         return render_template_string('<img src="{{ img_src }}"><p>{{ description }}</p>', img_src=url_for('get_img', id=img.id), description=img.description)

#     # Save the uploaded image temporarily
#     upload_folder = './uploads/'
#     os.makedirs(upload_folder, exist_ok=True)
#     pic_path = os.path.join(upload_folder, filename)
#     pic.save(pic_path)

#     # Generate content hash for the image
#     content_hash = hashlib.md5(pic.read()).hexdigest()

#     # Check if an image with the same content hash exists
#     img = Img.query.filter_by(content_hash=content_hash).first()
#     if img:
#         return render_template_string('<img src="{{ img_src }}"><p>{{ description }}</p>', img_src=url_for('get_img', id=img.id), description=img.description)

#     # Generate caption for the uploaded image
#     caption = pipeline('image-to-text')
#     description = caption(pic_path)[0]['generated_text']  # Extracting the text from the dictionary

#     # Save the image and description to the database
#     img = Img(img=pic.read(), name=filename, mimetype=pic.mimetype, description=description, content_hash=content_hash)
#     db.session.add(img)
#     db.session.commit()

#     return render_template_string('<img src="{{ img_src }}"><p>{{ description }}</p>', img_src=url_for('get_img', id=img.id), description=description)


# @app.route('/images')
# def display_images():
#     images = Img.query.all()
#     return render_template('images.html', images=images)

# @app.route('/<int:id>')
# def get_img(id):
#     img = Img.query.filter_by(id=id).first()
#     if not img:
#         return 'Img Not Found!', 404
#     return Response(img.img, mimetype=img.mimetype)

#Working without image loading