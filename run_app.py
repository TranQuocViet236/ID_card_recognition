from flask import Flask, json, render_template, jsonify, request
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os 
from datetime import datetime
import json
from model.model import Model
from api_doc.api import DocsAPI
import cv2
app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'static/img'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_IMAGES = ["png", "jpg", "jpeg"]

model = Model()
model.load_model()

DOCS_API = DocsAPI("backend/api_doc/credentials_file.json")


def validation_img(filename):
   if "." in filename and filename.split(".")[-1].lower() in ALLOWED_IMAGES:
      return 1
   return 0


def predict():
   data = {"id": "031007", "name": "ĐỊNH DUY TƯỜNG", "birth": "15-08-1977", "home": "Nam Định", "add": "666/14/17 Đường 3/2 P.14, Q.10, TP. Hồ Chí Minh", "date": "04/04/2003", "place": "TP HCM"}
   return data

@app.route("/download", methods=["POST"])
def download():
   # Parse string data to json data
   form_data = json.loads(request.form["data"])

   # Id of form
   idx = int(request.form["id"])

   # Parse string table to json data
   table = json.loads(request.form["table"])

   idx_of_table = [2, 1, 3]

   requests_api = []
   if idx in idx_of_table:
      requests_api = DOCS_API.delete_fixed_row(idx)
      requests_api += DOCS_API.insert_row(idx, table["rowNumber"])
      requests_api += DOCS_API.insert_text_into_table(idx, table)
      requests_api += DOCS_API.replace_text(form_data)
   else:
      requests_api = DOCS_API.replace_text(form_data)
   
   link_doc = DOCS_API.run(idx, form_data["name"], requests_api)

   return {"Link": link_doc}


@app.route("/testTable")
def test_table():
   idx = 3
   requests_api = []
   requests_api = DOCS_API.delete_fixed_row(idx)
   requests_api += DOCS_API.insert_row(idx, 5)
   link_doc = DOCS_API.run(idx, "123", requests_api)
   return {"Link": link_doc}


@app.route("/test")
def test():
   result = DOCS_API.get_json()
   with open("table.json", "w") as f:
      json.dump(result, f)
   return result


@app.route("/suggests")
def suggestion():
   with open('backend/suggest.json', "rb") as json_file:
      data = json.load(json_file)
      return data[int(request.args.get("id"))]


@app.route("/upload", methods=["POST"])
def upload_img():
   if 'files[]' not in request.files:
      response = jsonify({"Message": "No file in request"})
      response.status_code = 400
      return response
   
   files = request.files.getlist("files[]")

   rotation_list = request.form["rotations"].split(",")
   err = {}
   success = False 
   list_info = {}
   image_name_list = []
   IMAGE_SOURCE = "frontend/static/img/"
   for file in files:
      if file and validation_img(file.filename):
         file_name = secure_filename( str(datetime.now()) + (file.filename))
         file.save(os.path.join(app.config['UPLOAD_FOLDER'] + '/' + filename))
         image_name_list.append(IMAGE_SOURCE + file_name)
         success = 1
      else:
         err[file.filename] = "File type is not supported"
         
   for index_rotation_list in range(len(rotation_list)-1):
      src = cv2.imread(image_name_list[index_rotation_list])
      if rotation_list[index_rotation_list]=='90':
         img = cv2.rotate(src, cv2.ROTATE_90_CLOCKWISE)
         cv2.imwrite(IMAGE_SOURCE+str(index_rotation_list)+'.jpg', img)
         list_info = model.predict(IMAGE_SOURCE+str(index_rotation_list)+'.jpg')
      elif rotation_list[index_rotation_list]=='180' or rotation_list[index_rotation_list]=='-180':
         img = cv2.rotate(src, cv2.ROTATE_180)
         cv2.imwrite(IMAGE_SOURCE+str(index_rotation_list)+'.jpg', img)
         list_info = model.predict(IMAGE_SOURCE+str(index_rotation_list)+'.jpg')
      elif rotation_list[index_rotation_list]=='270' or rotation_list[index_rotation_list]=='-90':
         img = cv2.rotate(src, cv2.ROTATE_90_COUNTERCLOCKWISE)
         cv2.imwrite(IMAGE_SOURCE+str(index_rotation_list)+'.jpg', img)
         list_info = model.predict(IMAGE_SOURCE+str(index_rotation_list)+'.jpg')
   print(list_info)     
   if success:
      err["Message"] = "Success"
      err["data"] = json.loads(list_info)
      response = jsonify(err)
      response.status_code = 201
      return response
   
   else:
      response = jsonify(err)
      response.status_code = 400
      return response

@app.route("/extract_infor")
def extract_info():
   print(model.predict("test.png"))
   return jsonify(model.predict("test.png"))


if __name__=="__main__":
   app.run(host="0.0.0.0",debug=True, port="8080")

