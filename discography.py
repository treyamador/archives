# band discog
from pprint import PrettyPrinter
import json


class Discography:


    pp = PrettyPrinter()


    def __init__(self,id,artist,genre,location):
        self.discog = {
            'id':id,
            'artist': artist,
            'genre': {
                str(i): genre[i] for i in range(len(genre))
            },
            'location': location,
            'discography': {}
        }


    def add(self,name,type,year,*review):
        self.discog['discography'][name] = {
            'type': type,
            'year': year,
            'rating': review[1],
            'reviews': review[0]
        }


    def retrieve(self):
        return self.discog


    def json(self):
        print(json.dumps(self.discog))



