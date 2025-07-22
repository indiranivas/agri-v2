import pandas as pd
import folium
import random
import requests
from IPython.display import display

# Step 1: Load dataset
df = pd.read_csv("data.csv")  # Your Tamil Nadu dataset
locations = df['location'].tolist()
coordinates = list(zip(df['latitude'], df['longitude']))  # (lat, lon)

# Initialize matrix
n = len(coordinates)
distance_matrix = [[0] * n for _ in range(n)]

# Step 2: OSRM API endpoint
def get_distance_osrm(start, end):
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coordinates_str = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    url = base_url + coordinates_str + "?overview=false"
    
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        return int(data['routes'][0]['distance'])  # Distance in meters
    except Exception as e:
        print(f"Error fetching route between {start} and {end}: {e}")
        return None

# Step 3: Fill distance matrix
for i in range(n):
    for j in range(n):
        if i != j:
            dist = get_distance_osrm(coordinates[i], coordinates[j])
            if dist is not None:
                distance_matrix[i][j] = dist
                


# Step 4: Print distance matrix row by row
print("Distance Matrix (in meters):")
for i, row in enumerate(distance_matrix):
    print(f"{locations[i]}: {row}")

# Step 5: Save to CSV
matrix_df = pd.DataFrame(distance_matrix, index=locations, columns=locations)
matrix_df.to_csv("distance_matrix_tn.csv", index=True)
print("\nDistance matrix saved to 'distance_matrix_tn.csv'")

# Step 6: Plot routes on a Folium map
m = folium.Map(location=[coordinates[0][0], coordinates[0][1]], zoom_start=8)

# Add location markers
for i in range(n):
    folium.Marker(
        location=[coordinates[i][0], coordinates[i][1]],
        popup=locations[i],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Add routes with different colors
for i in range(n):
    for j in range(i + 1, n):
        start, end = coordinates[i], coordinates[j]
        url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
        
        try:
            r = requests.get(url)
            r.raise_for_status()
            route = r.json()['routes'][0]['geometry']

            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            folium.GeoJson(
                route,
                name=f"{locations[i]} to {locations[j]}",
                style_function=lambda x, color=color: {
                    'color': color,
                    'weight': 3,
                    'opacity': 0.6
                }
            ).add_to(m)
        except Exception as e:
            print(f"Failed to draw route from {locations[i]} to {locations[j]}: {e}")

# Step 7: Show map
display(m)
