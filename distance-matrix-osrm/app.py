import pandas as pd
import requests
import time


df = pd.read_csv("data.csv")  
locations = df['location'].tolist()
coordinates = list(zip(df['latitude'], df['longitude']))  


n = len(coordinates)
distance_matrix = [[0] * n for _ in range(n)]


def get_distance_osrm(start, end):
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coordinates_str = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    url = base_url + coordinates_str + "?overview=false"

    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        return int(data['routes'][0]['distance'])  
    except Exception as e:
        print(f"Error from {start} to {end}: {e}")
        return -1  


print("Distance Matrix (in meters):")
for i in range(n):
    for j in range(n):
        if i != j:
            dist = get_distance_osrm(coordinates[i], coordinates[j])
            distance_matrix[i][j] = dist
            time.sleep(1)  
    print(f"{locations[i]}: {distance_matrix[i]}") 


matrix_df = pd.DataFrame(distance_matrix, index=locations, columns=locations)
matrix_df.to_csv("distance_matrix_tn.csv", index=True)

print("\n✅ Distance matrix saved to 'distance_matrix_tn.csv'")
