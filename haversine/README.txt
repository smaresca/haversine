Calculates the distance between two points represented via latitude and longitude. Augments each relevant event with the resultant distance, stored in a field named 'distance' or another field as specified. Latitude and longitude for input must be represented in decimal degree format, though separate input fields may be specified for each. Units are in kilometers by default, but optionally represented in miles.

This is helpful when operating upon geo-spacial data obtained from IP-to-location tools/databases.  

For example, if one wishes to determine the average distance of a user from a location associated with a specific website, one would build a search like the following:  
    sourcetype="apache" GET somepage.php | iplocation src_ip | haversine origin="-47.31,80.33" lat lon

The output includes the original event data, with an added field 'distance' -- after which one might perform further analysis. For example:
    sourcetype="apache" GET somepage.php | iplocation src_ip | haversine origin="-47.31,80.33" lat lon | stats avg(distance) as "Avg. Distance" by userid

Other examples (flexible syntax - positional or k=v params, separate or combined fields for lat and lon) :
    sourcetype="apache" GET somepage.php | iplocation src_ip | haversine origin="-47.31,80.33" units=mi lat lon 
    sourcetype="apache" GET somepage.php | iplocation src_ip | haversine origin="-47.31,80.33" outputField=d lat lon 
    sourcetype="apache" GET somepage.php | geoip src_ip | haversine origin="-47.31,80.33" inputFieldLat=src_ip_latitude inputFieldLon=src_ip_longitude
    sourcetype="raw_coords" some filter | eval latlon_in_decimal_degree_format="fieldA,fieldB" | haversine origin="-47.31,80.33" units=mi latlon_in_decimal_degree_format

Copyright 2012 - Steven Maresca - steve.maresca@gmail.com
