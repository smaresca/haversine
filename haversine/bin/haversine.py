# Copyright 2012-2015 - Steven Maresca
# steve@zentific.com
#
# Haversine: a Splunk command for computing great-circle distance between two points.

import os, splunk.Intersplunk, logging as logger
import math

logger.basicConfig(level=logger.WARN, format='%(asctime)s %(levelname)s %(message)s',
                   filename=os.path.join(os.environ['SPLUNK_HOME'],'var','log','splunk','haversine.log'),
                   filemode='a')

def haversine(origin, point):
    lat1, lon1 = origin
    lat2, lon2 = point
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d

def toPoint(pt):
    if pt and "," in pt:
        originpoint = pt.split(',')

        if len(originpoint) != 2:
            return None

        try:
            originpoint[0] = float(originpoint[0].strip())
            originpoint[1] = float(originpoint[1].strip())
        except ValueError:
            return None

        return originpoint

    return None

def run_command():
    try:
        messages = {}
        keywords, options = splunk.Intersplunk.getKeywordsAndOptions()
        results, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()

        outputField = options.get('outputField', 'distance')
        units = options.get('units', 'km')
        originField = options.get('originField', None)
        inputField = options.get('inputField', None)
        originValue = options.get('origin', None)

        inputFieldLat = options.get('inputFieldLat', None)
        inputFieldLon = options.get('inputFieldLon', None)

        # Pull input fields (if and only if inputField is not set):
        #   single interpreted as "lat,lon" in decimal degree format
        #   two interpreted as lat lon, respectively
        #   >2 ignored
        num_keywords = len(keywords)
        if num_keywords > 2:
            return splunk.Intersplunk.generateErrorResults("Calculation not performed; too many keywords, expected two at most (latitude and longitude).")

        if ( inputField or inputFieldLat or inputFieldLon ) and num_keywords > 0 and num_keywords < 3 :
            return splunk.Intersplunk.generateErrorResults("Calculation not performed; latitude and longitude field names are ambiguous. Specify one fieldname for decimal-degree format data or two fields for latitude and longitude, but not both.")

        if num_keywords == 1:
            inputField = keywords[0]
        elif num_keywords == 2:
            inputFieldLat = keywords[0]
            inputFieldLon = keywords[1]

        if (not inputFieldLat or not inputFieldLon) and not inputField:
            return splunk.Intersplunk.generateErrorResults("Calculation not performed; latitude and longitude field name(s) not provided to haversine.")

        if inputFieldLat and inputFieldLon and inputField:
            return splunk.Intersplunk.generateErrorResults("Calculation not performed; latitude and longitude field names are ambiguous. Specify one fieldname for decimal-degree format data or two fields for latitude and longitude, but not both.")

        if not originValue and not originField:
            return splunk.Intersplunk.generateErrorResults("Calculation not performed; required origin value/field name is missing.")

        if results:
            for result in results:
                origin = None

                # build origin coordinates from either a static value passed as a haversine param
                # or pulled out of the field specified by originField in the current event
                if originField:
                    if originField not in result:
                        continue

                    origin = result[originField]
                else:
                    origin = originValue

                originPoint = toPoint(origin)

                if not originPoint:
                    return splunk.Intersplunk.generateErrorResults("Origin value malformed. Received '%s' - expected origin='x,y' as a value represented using decimal degree notation, (e.g. '-41.22,80.22')." % origin)


                inputCoord = ""

                # build input coordinates from what we
                # have available (inputField with lat,lon tuple or two separate fields)
                if inputFieldLat and inputFieldLon:
                    if inputFieldLat not in result or inputFieldLon not in result:
                        continue

                    if not result[inputFieldLat] or not result[inputFieldLon]:
                        continue

                    inputCoord = result[inputFieldLat]+","+result[inputFieldLon]
                else:
                    if inputField not in result:
                        continue

                    if not result[inputField]:
                        continue

                    inputCoord = result[inputField]

                inputPoint = toPoint(inputCoord)

                # geoip outputs lat/lon that are empty if details unknown (or if invalid inputField used)
                # so in this case, handle it gracefully.
                #
                # >1 rather than >0 to simultaneously account for the case where
                #  inputCoord (from a single inputField) is == "" OR
                #  inputCoord="," when inputFieldLat+","+inputFieldLon=="," because they're blank
                #
                if not inputPoint and len(inputCoord) > 1:
                    return splunk.Intersplunk.generateErrorResults("Input coordinates malformed. Received '%s' - expected inputField='x,y' as a value represented using decimal degree notation, (e.g. '-41.22,80.22')." % inputCoord)
                elif not inputPoint:
                    #silently ignore lat,lon=""
                    continue

                distance = haversine(originPoint, inputPoint)

                if type(distance) == float and units=="mi":
                    result[outputField] = distance*0.621371192
                elif type(distance) == float:
                    result[outputField] = distance

            splunk.Intersplunk.outputResults(results)

    except Exception, e:
        import traceback
        stack =  traceback.format_exc()
        splunk.Intersplunk.generateErrorResults(str(e))
        logger.error(str(e) + ". Traceback: " + str(stack))

run_command()
