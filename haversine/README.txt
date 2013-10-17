Calculates the distance between two points represented via latitude and longitude. Augments each relevant event with the resultant distance, stored in a field named 'distance' or another field as specified. Latitude and longitude for input must be represented in decimal degree format, though separate input fields may be specified for each. Units are in kilometers by default, but optionally represented in miles.

This is helpful when operating upon geo-spacial data obtained from IP-to-location tools/databases.  

For example, if one wishes to determine the average distance of a user from a location associated with a specific website, one would build a search like the following:  
    sourcetype="apache" GET somepage.php | table src_ip | geoip src_ip | haversine origin="-47.31,80.33" inputFieldLat=src_ip_latitude inputFieldLon=src_ip_longitude

The output includes the original event data, with an added field 'distance' -- after which one might perform further analysis. For example:
    sourcetype="apache" GET somepage.php | table src_ip | geoip src_ip | strcat src_ip_latitude "," src_ip_longitude latlon | haversine origin="-47.31,80.33" latlon | stats avg(distance) as "Avg. Distance" by userid

Copyright 2012 - Steven Maresca - steve.maresca@gmail.com
