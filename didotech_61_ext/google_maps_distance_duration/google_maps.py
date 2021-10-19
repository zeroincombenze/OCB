# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 Didotech Srl <http://www.didotech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

import urllib
import urllib2
try:
    import json
except ImportError:
    import simplejson as json


def fetch_json(query_url, params={}, headers={}):
    """Retrieve a JSON object from a (parameterized) URL.
    
    :param query_url: The base URL to query
    :type query_url: string
    :param params: Dictionary mapping (string) query parameters to values
    :type params: dict
    :param headers: Dictionary giving (string) HTTP headers and values
    :type headers: dict 
    :return: A `(url, json_obj)` tuple, where `url` is the final,
        parametrized, encoded URL fetched, and `json_obj` is the data
        fetched from that URL as a JSON-format object.
    :rtype: (string, dict or array)
    
    """
    encoded_params = urllib.urlencode(params)    
    url = query_url + encoded_params
    request = urllib2.Request(url, headers=headers)
    try:
        response = urllib2.urlopen(request)
        # The same, but without headers
        # response = urllib.urlopen(url)
    except urllib2.URLError:
        return url, {'status': 'Internet connection unavailable'}
    return url, json.load(response)


class GoogleMapsDirections(object):
    """
    https://developers.google.com/maps/documentation/directions/
    """
    _DIRECTIONS_QUERY_URL = 'https://maps.googleapis.com/maps/api/directions/json?'

    def __init__(self, key, referrer_url=''):
        self.referrer_url = referrer_url
        self.key = key

    def directions(self, origin, destination, mode='driving', **kwargs):
        """
        Get directions from `origin` to `destination`.
        """

        params = {
            'origin': origin,
            'destination': destination,
            'key': self.key,
            'mode': mode,
        }

        params.update(kwargs)
        if mode == 'transit':
            if not params.get('departure_time') and not params.get('arrival_time'):
                params['mode'] = 'driving'
        url, response = fetch_json(self._DIRECTIONS_QUERY_URL, params=params)
        if response['status'] != 'OK':
            return {'error': response['status']}
        return response
    
    def duration(self, origin, destination, mode='driving', **kwargs):
        response = self.directions(origin, destination, mode, **kwargs)
        duration = 0
        routes = response.get('routes')
        if routes:
            legs = routes[0].get('legs')
            if legs:
                duration = legs[0].get('duration', {}).get('value', 0)
        return duration
    
    def distance(self, origin, destination, mode='driving', **kwargs):
        response = self.directions(origin, destination, mode, **kwargs)

        distance = 0
        routes = response.get('routes')
        if routes:
            legs = routes[0].get('legs')
            if legs:
                distance = legs[0].get('distance', {}).get('value', 0)
        return distance


class GoogleMapsDistance(object):
    """
    https://developers.google.com/maps/documentation/distancematrix/
    """
    _DISTANCE_QUERY_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

    def __init__(self, key, referrer_url=''):
        self.referrer_url = referrer_url
        self.key = key

    def directions(self, origin, destination, mode='driving', **kwargs):
        """
        Get directions from `origin` to `destination`.

        Optional parameters:
        key — Your application's API key. This key identifies your application for purposes of quota management. Learn how to get a key from the Google APIs Console.
        mode (defaults to driving) — Specifies the mode of transport to use when calculating distance. Valid values and other request details are specified in the Travel Modes section of this document.
        language — The language in which to return results. See the list of supported domain languages. Note that we often update supported languages so this list may not be exhaustive.
        avoid — Introduces restrictions to the route. Valid values are specified in the Restrictions section of this document. Only one restriction can be specified.
        units — Specifies the unit system to use when expressing distance as text. See the Unit Systems section of this document for more information.
        departure_time — The desired time of departure. You can specify the time as an integer in seconds since midnight, January 1, 1970 UTC. Alternatively, you can specify a value of now, which sets the departure time to the current time (correct to the nearest second). The departure time may be specified in two cases:
            For requests where the travel mode is transit: You can optionally specify one of departure_time or arrival_time. If neither time is specified, the departure_time defaults to now (that is, the departure time defaults to the current time).
            For requests where the travel mode is driving: Google Maps API for Work customers can specify the departure_time to receive trip duration considering current traffic conditions. The departure_time must be set to within a few minutes of the current time.
        arrival_time — Specifies the desired time of arrival for transit requests, in seconds since midnight, January 1, 1970 UTC. You can specify either departure_time or arrival_time, but not both. Note that arrival_time must be specified as an integer.
        transit_mode — Specifies one or more preferred modes of transit. This parameter may only be specified for requests where the mode is transit. The parameter supports the following arguments:
            bus indicates that the calculated route should prefer travel by bus.
            subway indicates that the calculated route should prefer travel by subway.
            train indicates that the calculated route should prefer travel by train.
            tram indicates that the calculated route should prefer travel by tram and light rail.
            rail indicates that the calculated route should prefer travel by train, tram, light rail, and subway. This is equivalent to transit_mode=train|tram|subway.
        transit_routing_preference — Specifies preferences for transit requests. Using this parameter, you can bias the options returned, rather than accepting the default best route chosen by the API. This parameter may only be specified for requests where the mode is transit. The parameter supports the following arguments:
            less_walking indicates that the calculated route should prefer limited amounts of walking.
            fewer_transfers indicates that the calculated route should prefer a limited number of transfers.

        """
        params = {
            'origins': origin,
            'destinations': destination,
            'key': self.key,
            'mode': mode,
        }

        params.update(kwargs)
        if mode == 'transit':
            if not params.get('departure_time') and not params.get('arrival_time'):
                params['mode'] = 'driving'

        url, response = fetch_json(self._DISTANCE_QUERY_URL, params=params)

        if response['status'] != 'OK':
            return {'error': response['status']}
        return response

    def duration(self, origin, destination, mode='driving', **kwargs):
        response = self.directions(origin, destination, mode, **kwargs)
        duration = 0
        routes = response.get('routes')
        if routes:
            legs = routes[0].get('legs')
            if legs:
                duration = legs[0].get('duration', {}).get('value', 0)
        return duration

    def distance(self, origin, destination, mode='driving', **kwargs):
        response = self.directions(origin, destination, mode, **kwargs)

        if response.get('error'):
            return response
        else:
            return response['rows'][0]['elements'][0]


if __name__ == '__main__':
    key = ''

    maps = GoogleMapsDistance(key)
    print maps.distance('Piove di Sacco Padova', 'Venezia Padova')

    # {u'status': u'NOT_FOUND'}
    # print maps.distance('Piove di Sacco Padova', 'akjdsfahdf')

    # maps = GoogleMapsDirections(key)
    # print maps.distance('Piove di Sacco Padova', 'Venezia')
