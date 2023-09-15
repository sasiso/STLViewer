import numpy as np
from stl import mesh

# Load the STL file
stl_file = mesh.Mesh.from_file('1351.stl')

# Calculate the volume, center of mass, and inertia tensor
volume, _, _ = stl_file.get_mass_properties()
volume_grams = volume / 1000.0  # Convert milligrams to grams
print(f"Volume of STL file: {volume_grams} grams")

# Densities of gold for different karats (g/cm³)
density_9k = 11.0
density_14k = 13.0
density_18k = 15.6
density_21k = 17.0
density_22k = 17.5

# Calculate the weight of gold for different karats
weight_9k = volume_grams * density_9k
weight_14k = volume_grams * density_14k
weight_18k = volume_grams * density_18k
weight_21k = volume_grams * density_21k
weight_22k = volume_grams * density_22k

print(f"Weight of 9 karat gold: {weight_9k} grams")
print(f"Weight of 14 karat gold: {weight_14k} grams")
print(f"Weight of 18 karat gold: {weight_18k} grams")
print(f"Weight of 21 karat gold: {weight_21k} grams")
print(f"Weight of 22 karat gold: {weight_22k} grams")
