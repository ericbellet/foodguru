import requests
import pandas as pd 

from flask import Flask, Response, request
from flask_restplus import Api, Resource


app = Flask(__name__)
api = Api(app, 
		  version = "1.0", 
		  title = "Food Guru API", 
		  description = "Obtain all the restaurants amd their pictures.")


@api.route('/bcn/restaurants')
class Restaurants(Resource):

    @api.doc(responses={ 200: 'OK', 500: 'Internal Problem'})
    def get(self):    
        try:
            data = pd.read_csv("C:/Users/EricBellet/Desktop/FG/FG/testFG/first_data.csv")     
            data.dropna(inplace = True)     
            data_dict = data.T.to_dict()   
            return str(data_dict)
  
        except Exception as e:
            api.abort(500, e.__doc__, status = "Internal Problem", statusCode = "500")


@api.route('/bcn/restaurants/photos')
class Photos(Resource):

    @api.doc(responses={ 200: 'OK', 500: 'Internal Error' }, params={ '?photoreference': 'Specify the photoreference associated with the restaurant' })
    def get(self):   
        try: 
            self.key = ""
            self.url = "https://maps.googleapis.com/maps/api/place/photo?"
            self.maxwidth = 400
            photoreference = request.args.get('photoreference')
            response = requests.get("{0}photoreference={1}&key={2}&maxwidth={3}".format(self.url, photoreference, self.key, self.maxwidth))
            return Response(response=response._content, status=200, mimetype="image/png")
        except Exception as e:
            api.abort(500, e.__doc__, status = "Internal Problem", statusCode = "500")


if __name__ == '__main__':
    #http://172.16.20.126:5000/
    app.run(host='0.0.0.0')