import shapefile

# Load the shapefile
shapefile_path = "/Users/pchristofi/Documents/CyBuses/data/static/routes/routes.shp"
sf = shapefile.Reader(shapefile_path)

#fields = sf.fields[1:]  # Skip the first record (deletion flag)
#print("Fields:")
#for field in fields:
#    print(f"Name: {field[0]}, Type: {field[1]}, Length: {field[2]}")

print(sf.records().head())
