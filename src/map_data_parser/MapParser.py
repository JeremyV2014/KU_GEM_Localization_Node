import csv

with open('FILEPATH\\MRC_Cut_Middle.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0

    lat_lng = []

    for row in csv_reader:
        if line_count == 0:
            # print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            # print(f'\t{row[0]} is the latitude {row[1]} is the longitude.')
            line_count += 1

            lat_lng.append(row);


# write a function that takes longitude and latitide and finds closest pair within array
    latlonglist = []
def calculateLatLongPair(latitude, longtitude, latlonglist):
    for row in latlonglist:
        if lat_lng[row] == [latitude, longtitude]:
            return lat_lng[row]
    # print(f'Processed {line_count} lines.')
    returnedPair = calculateLatLongPair(43.012045,-83.708319, lat_lng)
    #print(returnedPair)

print(lat_lng)
print(lat_lng[0])