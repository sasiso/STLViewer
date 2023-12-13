def get_weight_text(file_name):

    import numpy as np
    from stl import mesh
    import sys
    # Load the STL file
    stl_file = mesh.Mesh.from_file(file_name)

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
    rv = {}
    rv['9k'] =  weight_9k
    rv['14k'] = weight_14k
    rv['18k'] = weight_18k
    rv['21k'] = weight_21k
    rv['22K'] =  weight_22k
    return rv   
