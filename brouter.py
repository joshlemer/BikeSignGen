from select import select
from typing import Any, Mapping
import requests

home = (49.264026, -122.981245)
metrotown = (49.227382, -122.998239)

host  = 'https://brouter.de'

def get_trip_info(start, end):
    # return {'distance': '10.1km','elevationGain':'100m','travelTime':'12min'}
    url = f'{host}/brouter?lonlats={start[1]},{start[0]}|{end[1]},{end[0]}&profile=trekking&alternativeidx=0&format=geojson'
    res = requests.get(url)
    body = res.json()
    properties: Mapping[str, Any] = body['features'][0]['properties']

    def format_num(s, decimal_places):
        suffix = f'.{decimal_places}' if decimal_places > 0 else ''
        return f'%d{suffix}' % float(s)
    return {
        'distance': format_num(float(properties["track-length"])/1000, 1) + 'km',
        'elevationGain': format_num(properties['filtered ascend'],0) + 'm',
        'travelTime': format_num(float(properties['total-time'])/60,0) + 'min',
    }

def get_brouter_traveltime(lonlat_start, lonlat_end):
    url = f'{host}/brouter?lonlats={lonlat_start[0]},{lonlat_start[1]}|{lonlat_end[0]},{lonlat_end[1]}&profile=trekking&alternativeidx=0&format=geojson'
    res = requests.get(url)
    print(str(res.content))
    body = res.json()
    print(body)
    return float(body['features'][0]['properties']['total-time'])





# print(get_trip_info(home, metrotown))

# '%d' % float('2000000000000000000000000000000000.123')

# print(1)

# home[0]
# f'{host}/brouter?lonlats={home[0]},{home[1]}|{metrotown[0]},{metrotown[1]}&profile=trekking&alternativeidx=0&format=geojson'

# get_trip_info(home, metrotown)

# get_brouter_traveltime((49.8793525027847,-97.1906580951554,), (49.8806391992424,-97.1813606755899))