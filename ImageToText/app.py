# Import necessary modules and packages
from flask import Flask, request, Response, render_template, redirect, flash, url_for
from werkzeug.utils import secure_filename
from db import db_init, db
from models import Img
from transformers import pipeline
import os

# Initialize Flask application
app = Flask(__name__)

# Configure SQLite database URI and disable track modifications
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db_init(app)

# Function to check if the file extension is allowed
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the homepage
@app.route('/')
def hello_world():
    return render_template('index.html')

# Route for handling file upload
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Check if file is present in the request
        if 'pic' not in request.files:
            return 'No pic uploaded!', 400

        pic = request.files['pic']

        # Check if no file was selected
        if pic.filename == '':
            return 'No selected file!', 400

        # Check if the file format is allowed
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

# Route for displaying uploaded images
@app.route('/images')
def display_images():
    try:
        message = request.args.get('message', None)
        images = Img.query.all()
        return render_template('images.html', images=images, message=message)
    except Exception as e:
        return f"Error displaying images: {str(e)}", 500

# Route for retrieving a specific image by ID
@app.route('/<int:id>')
def get_img(id):
    try:
        img = Img.query.filter_by(id=id).first()
        if not img:
            return 'Img Not Found!', 404
        return Response(img.img, mimetype=img.mimetype)
    except Exception as e:
        return f"Error retrieving image: {str(e)}", 500

# Run the application if executed directly
if __name__ == "__main__":
    app.run(debug=True)
