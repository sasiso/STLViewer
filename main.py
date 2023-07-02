import vtk

# Create a reader and load the STL file
reader = vtk.vtkSTLReader()
reader.SetFileName('a.stl')
reader.Update()

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(reader.GetOutputPort())

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
interactor.Start()
