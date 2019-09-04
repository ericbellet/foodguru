import requests
import json
import time
import pygeohash as Geohash
import gmplot
import pandas as pd
#https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=41.4081811,2.1871765&radius=500&type=restaurant&key=AIzaSyCTqU5GzJz2d2nf8yJgvakQp9gFLbTHkFA

class BaseException(Exception):
    def __init__(self, message):
        self.message = message

class GeoFigures():
    class HashPrecision:
        HashPrecision_6 = 6

    class RadiusMeters:
        RadiusMeters_550 = 550

    def __init__(self, latitude=None, longitude=None, geohash=None):
        self.precisionGeohash = GeoFigures.HashPrecision.HashPrecision_6   
        self.radiusMeters = GeoFigures.RadiusMeters.RadiusMeters_550
        self.latitude = latitude
        self.longitude = longitude
        self.geohash = geohash

class GeohashFigure(GeoFigures):

    def __init__(self, latitude=None, longitude=None, geohash=None):
        super().__init__(latitude, longitude, geohash)
        self.base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
        self.geohashes = []

    def encode(self):
        return Geohash.encode(self.latitude, self.longitude, precision=self.precisionGeohash)

    def decode(self):
        try:
            return Geohash.decode_exactly(self.geohash)
        except:
            pass

    def ifexists(self, geohash):
        try:
            Geohash.decode(geohash)
            return geohash
        except:
          print(geohash)
          pass

    def obtainAll(self):
        cont = 0
        comb = []
        while len(self.geohash) + cont < GeoFigures().HashPrecision.HashPrecision_6:
            auxGeohash = self.geohash
            if len(comb) != 0:
                for i, c in enumerate(comb):
                    comb[i] = [c + self.base32[i] for i in range(0, len(self.base32))]
            else:
                comb = [auxGeohash + self.base32[i] for i in range(0, len(self.base32))]
            cont += 1

        if cont > 1:
             self.geohashes = [self.ifexists(item) for sublist in comb for item in sublist]   
        else:
            self.geohashes = comb
        print(len(self.geohashes))
        return self.geohashes


class ApiKeys:
    apikey_eric = "key=AIzaSyCTqU5GzJz2d2nf8yJgvakQp9gFLbTHkFA"

class Endpoints:
    textsearch = "textsearch"
    nearbysearch = "nearbysearch"

class FormatResult:
    json = "json"
    xml = "xml"

class Filters:
    location = "location={latitude},{longitude}"
    typeRestaurant = "type=restaurant"
    radius = "radius={radius}"

class ApiPlaces():
     
    def __init__(self):
        self.typePlace = "restaurant"
        self.urlGoogleMaps = "https://maps.googleapis.com/maps/api/place/"
        self.df = pd.DataFrame(columns = ['id', 'name', 'latitude', 'longitude', 'photo_reference', 'place_id', 'price_level', 'rating', 'category']) 

    def addEndpoint(self, endpoint):
        self.urlGoogleMaps += endpoint + "/"

    def addFilter(self, filter):
        self.urlGoogleMaps += "&" + filter

    def addKey(self, key):
        self.urlGoogleMaps += "&" + key

    def addFormat(self, format):
        self.urlGoogleMaps += format + "?"

    def findPlaces(self, loc, radius, pagetoken = None):
       print(loc)
       latitude = loc[0]
       longitude = loc[1]
       url = self.urlGoogleMaps.format(**locals())
       response = requests.get(url)
       res = json.loads(response.text)
       print("Number of results ---->>> ", len(res["results"]))
       
       for restaurant in res["results"]:
          info = ";".join(map(str,[restaurant["name"]]))
          print(info)
          self.df = self.df.append(pd.DataFrame({'id':[restaurant['id']], 'name':[restaurant['name']], 'latitude':[restaurant['geometry']['location']['lat']], 'longitude':[restaurant['geometry']['location']['lng']], 
                                'photo_reference':[photoReference(restaurant.get('photos', 'Missing: key_name'))], 'place_id':[restaurant['place_id']], 
                                'price_level':[restaurant.get('price_level', 'Missing: key_name')], 'rating':[restaurant.get('rating', 'Missing: key_name')], 'category':['Otro']}))

       pagetoken = res.get("next_page_token", None)
       return pagetoken

def photoReference(photo):
    if photo == "Missing: key_name":
        return "Missing: key_name"
    else:
        return photo[0].get('photo_reference', 'Missing: key_name')

getObject = ApiPlaces()
getObject.addEndpoint(Endpoints.nearbysearch)
getObject.addFormat(FormatResult.json)
getObject.addFilter(Filters.location)   
getObject.addFilter(Filters.radius)   
getObject.addFilter(Filters.typeRestaurant)
getObject.addKey(ApiKeys.apikey_eric)

pagetoken = None
radius = GeoFigures().RadiusMeters.RadiusMeters_550
barcelona = ["sp37r", "sp37x", "sp3eb", "sp3ec", "sp3ef", "sp3eg", "sp3e8", "sp3e9", "sp3ed", "sp3e2", "sp3e3", "sp3e6", "sp3e0", "sp3e1"]
geohashes = []

for geohash in barcelona:
    geohashes.extend(GeohashFigure(geohash=geohash).obtainAll())

print("Total of areas: {0}".format(len(geohashes)))   
gmap = gmplot.GoogleMapPlotter(41.405483, 2.1914859, 16)

for geohash in geohashes:
    loc = GeohashFigure(geohash=geohash).decode()    
    if loc != None:        
        gmap.scatter([loc[0]],[loc[1]], '#ffa500', size=550, marker=False)
        getObject.findPlaces(loc=loc, radius=radius, pagetoken=pagetoken)

        while True:
            pagetoken = getObject.findPlaces(loc=[loc[0], loc[1]],
                            radius=GeoFigures().RadiusMeters.RadiusMeters_550,
                            pagetoken=pagetoken)
            time.sleep(5)

            if not pagetoken:
                break

#print(pagetoken)

#ToDo save uniques
getObject.df.to_csv("df.csv", index=False, header=True)
gmap.draw("mymap.html")



'''
  self.df = self.df.append(pd.DataFrame({'id':[restaurant['id']], 'name':[restaurant['name']], 'latitude':[restaurant['geomery']['location']['lat']], 'longitude':[restaurant['geomery']['location']['lng']], 
                                'photo_reference':[photoReference(restaurant.get('photos', 'Missing: key_name'))], 'place_id':[restaurant['place_id']], 
                                'price_level':[restaurant.get('price_level', 'Missing: key_name')], 'rating':[restaurant['rating']], 'category':['Otro']}))

with open('jsonResult.json', 'r') as f:
    jsonRestaurants = json.load(f)

for restaurant in jsonRestaurants["results"]:
    print(restaurant['name'])
    df = df.append(pd.DataFrame({'id':[restaurant['id']], 'name':[restaurant['name']], 'photo_reference':[photoReference(restaurant.get('photos', 'Missing: key_name'))], 
                                'place_id':[restaurant['place_id']], 'price_level':[restaurant.get('price_level', 'Missing: key_name')], 'rating':[restaurant['rating']], 'category':['Otro']}))
df.to_csv("df.csv", index=False, header=True)
'''



