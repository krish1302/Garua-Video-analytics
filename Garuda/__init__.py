from flask import Flask
from flask_cors import CORS

app = Flask(__name__,static_url_path='',static_folder='./static',template_folder='./templates')
cors = CORS(app, resources={r"/static/*": {"origins": "*"}})

import Garuda.model
import Garuda.views
import Garuda.carTracking
import Garuda.Loitering
import Garuda.LineCrossing
import Garuda.AbandonedObject
import Garuda.Detections

