
# importing the necessary dependencies
from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__) # initializing a flask app

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("main.html")

@app.route('/predict',methods=['POST','GET']) # route to show the predictions in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:

            def lat_long_gen(location):
                #This function is responsible for converting the place inputted by user into latitude and longitude.
                try:
                    import geopy
                    from geopy.geocoders import Nominatim
                    locator = Nominatim(user_agent="myGeocoder")
                    locating = locator.geocode(location)
                    return locating.longitude, locating.latitude
                except Exception as e:
                    print('Exception error is:\n{}'.format(e))
                    return 'Location Error from server side. Kindly retry.'
                #  reading the inputs given by the user
            location =request.form['location']
            longitude,latitude = lat_long_gen(location)
            try:
###########################################################################################################
                bathrooms = int(request.form['bathrooms'].strip())
###########################################################################################################
                BHK = int(request.form['BHK'].strip())
###########################################################################################################
                no_of_parking = int(request.form['no_of_parking'].strip())
###########################################################################################################
                area = float(request.form['area'].strip())
###########################################################################################################
                flat_floor_no = float(request.form['flat_floor_no'])
###########################################################################################################
                total_floors = float(request.form['total_floors'])
###########################################################################################################
                p = request.form['Possession_Status_received']

                if p.lower() == 'yes':
                    Possession_Status_received = 1
                else:
                    Possession_Status_received = 0
###########################################################################################################
                n_or_r = request.form['new_or_resale']
                if n_or_r.lower() == 'new':
                    new_or_resale_Resale = 0
                else:
                    new_or_resale_Resale = 1
###########################################################################################################
                furnishing = request.form['furnishing']
                if furnishing.lower() == "unfurnished":
                    furnishing_Semi_Furnished, furnishing_Unfurnished = [0,1] #Unfurnished
                elif furnishing.lower() == 'semi-furnished':
                    furnishing_Semi_Furnished, furnishing_Unfurnished = [1, 0] #Semi-Furnished
                else:
                    furnishing_Semi_Furnished, furnishing_Unfurnished = [0, 0] #Furnished
###########################################################################################################
                overlooking = request.form['overlooking']
                if overlooking.lower() == 'main road':
                    overlooking_other = 0
                else:
                    overlooking_other = 1
###########################################################################################################
                config = request.form['config']
                if config.lower() == "apartment":
                    config_Studio, config_apartment, config_other = [0, 1, 0]
                elif config.lower() == "studio":
                    config_Studio, config_apartment, config_other = [1, 0, 0]
                elif config.lower() == "other":
                    config_Studio, config_apartment, config_other = [0, 0, 1]
                else:
                    config_Studio, config_apartment, config_other = [0, 0, 0]
###########################################################################################################
                parking_type = request.form['parking_type']
                if parking_type.lower() == "open parking":
                    parking_type_open, parking_type_both = [1, 0]
                elif parking_type.lower() == "covered parking":
                    parking_type_open, parking_type_both = [0, 0]
                else:
                    parking_type_open, parking_type_both = [0, 1]
            except Exception as e:
                return render_template('var_issue.html')
###########################################################################################################

            filename = 'Saved Models/xgbmodel.pickle'
            loaded_model = pickle.load(open(filename, 'rb')) # loading the model file from the storage
            # predictions using the loaded model file
            params = [bathrooms, BHK, no_of_parking, longitude, latitude,
                      np.log(area), np.log(flat_floor_no), np.log(total_floors),
                      Possession_Status_received, new_or_resale_Resale,
                      furnishing_Semi_Furnished, furnishing_Unfurnished,
                      overlooking_other, config_Studio, config_apartment,
                      config_other, parking_type_open, parking_type_both]

            col_names = ['bathrooms', 'BHK', 'no_of_parking', 'longitude', 'latitude',
                         'area_log', 'flat_floor_no_log', 'total_floors_log',
                         'Possession_Status_received', 'new_or_resale_Resale',
                         'furnishing_Semi-Furnished', 'furnishing_Unfurnished',
                         'overlooking_other', 'config_Studio', 'config_apartment',
                         'config_other', 'parking_type_Open', 'parking_type_both']

            data_to_predict = pd.DataFrame(params, index=col_names).T





            prediction=np.exp(loaded_model.predict(data_to_predict))
            print('prediction is', prediction)
            # showing the prediction results in a UI
            # greater than 72.6 and less than 73.2 (longitude) Conditions
            # greater than 18.80 and less than 19.6(latitude) Conditions


            if (prediction > 0) and (longitude>72.60 and longitude<73.2) and (latitude>18.80 and latitude<19.60):
                return render_template('results.html',
                                       prediction=round(prediction[0],2),
                                       location = location,
                                       bedrooms = BHK,
                                       area = area,
                                       bathrooms = bathrooms,
                                       no_of_parking = no_of_parking,
                                       flat_floor_no = flat_floor_no,
                                       total_floors = total_floors,
                                       p = p,
                                       n_or_r = n_or_r,
                                       furnishing = furnishing,
                                       overlooking = overlooking,
                                       config = config,
                                       parking_type = parking_type)
            else:
                return render_template('failed.html')
        except Exception as e:
            print('The Exception message is: ',e)
            return render_template('failed_program.html')
    # return render_template('results.html')
    else:
        return render_template('main.html')



if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True) # running the app
	#app.run(port=8000, debug=True) #for deployment