from Uniqapi import app, request
import os, uuid

UPLOAD_FOLDER = 'Api'
SUBFOLDER = 'uploads'
UPLOAD_PATH = os.path.join(UPLOAD_FOLDER, SUBFOLDER)
app.config['UPLOAD_PATH'] = UPLOAD_PATH

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return app._jsonify(error= "No file part")
    
    file = request.files['file']
    
    if file.filename == '':
        return app._jsonify(error= "No selected file")
    
    if file:
        # Generate a unique filename to prevent duplicates
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        return app._jsonify(success=True, message= "File successfully uploaded", filename=filename)
    else:
        return app._jsonify(error="Upload failed")