import vtk

def render_stl_file(file_path):
    # Create a reader and load the STL file
    reader = vtk.vtkSTLReader()
    reader.SetFileName(file_path)
    reader.Update()

    # Get the STL mesh
    stl_mesh = reader.GetOutput()

    # Calculate width (thickness) for each point of the mesh
    width_array = vtk.vtkDoubleArray()
    width_array.SetNumberOfComponents(1)
    width_array.SetName("Width")

    for i in range(stl_mesh.GetNumberOfPoints()):
        point = stl_mesh.GetPoint(i)
        width = point[2]  # Assuming the width is the Z-coordinate of each point
        width_array.InsertNextValue(width)

    stl_mesh.GetPointData().SetScalars(width_array)

    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(stl_mesh)

    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create a renderer and add the actor
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)

    # Create a render window and set the renderer
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create an interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Initialize the interactor and start the rendering loop
    interactor.Initialize()

    # Create a color transfer function for the heatmap
    color_transfer_function = vtk.vtkColorTransferFunction()
    color_transfer_function.AddRGBPoint(0.0, 0.0, 0.0, 1.0)  # Blue color for minimum width
    color_transfer_function.AddRGBPoint(0.7, 1.0, 0.0, 0.0)  # Red color for maximum width

    # Set scalar visibility
    mapper.SetScalarVisibility(True)
    mapper.SetScalarModeToUsePointData()
    mapper.SetColorModeToMapScalars()
    mapper.ScalarVisibilityOn()

    # Set the color transfer function as the lookup table for the mapper
    mapper.SetLookupTable(color_transfer_function)

    # Start the rendering loop
    render_window.Render()
    interactor.Start()

if __name__ == "__main__":
    file_path = 'a.stl'
    render_stl_file(file_path)
