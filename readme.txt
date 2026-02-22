To run:
Replace the excel read path then you could run all the code
"aaa": all counties in CA from 1975 to 2014
"bbb": all counties in CA on year 2014
"ccc": all counties in CA from 1975 to 1979

Problems I found:
1. Animation generation costs huge on both time and space. It took me aournd 15s to generate the
    map with "ccc", which only contains data of counties in one state within 5 years. The ipynb file after
    generation occupied 160MB which is huge. I have not tried running "aaa" because I directly interupted
    the process after waiting for 30s. 

2. Generation with zip code could be hard if we can't find a geojson file containing the latitude, longitude,
    and zip codes for all counties in the US. This means we'd have to manually (impossible) or use a script 
    to add the zip code to each county in our current JSON file, which only contains location information. I've
    tried to find such json file with zip, but I could only find within some cities, not even within a state, let 
    alone the whole US.