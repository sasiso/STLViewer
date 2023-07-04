import vtk


class MeasureInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, renderer):
        self.AddObserver("KeyPressEvent", self.on_key_press)
        self.AddObserver("KeyReleaseEvent", self.on_key_release)
        self.AddObserver("LeftButtonPressEvent", self.on_left_button_press)
        self.AddObserver("LeftButtonReleaseEvent", self.on_left_button_release)
        self.renderer = renderer
        self.line_source = vtk.vtkLineSource()
        self.line_mapper = vtk.vtkPolyDataMapper()
        self.line_mapper.SetInputConnection(self.line_source.GetOutputPort())
        self.line_actor = vtk.vtkActor()
        self.line_actor.SetMapper(self.line_mapper)
        self.renderer.AddActor(self.line_actor)
        self.start_point = [0, 0, 0]
        self.end_point = [0, 0, 0]
        self.alt_pressed = False
        self.text_actor = vtk.vtkTextActor()
        self.text_actor.SetPosition(10, 10)
        self.text_actor.GetTextProperty().SetFontSize(18)
        self.renderer.AddActor2D(self.text_actor)

    def on_key_press(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        if key == "Alt_L":
            self.alt_pressed = True

    def on_key_release(self, obj, event):
        key = self.GetInteractor().GetKeySym()
        if key == "Alt_L":
            self.alt_pressed = False

    def on_left_button_press(self, obj, event):
        if self.alt_pressed:
            click_pos = self.GetInteractor().GetEventPosition()
            picker = vtk.vtkCellPicker()
            picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
            self.start_point = picker.GetPickPosition()

    def on_left_button_release(self, obj, event):
        if self.alt_pressed:
            click_pos = self.GetInteractor().GetEventPosition()
            picker = vtk.vtkCellPicker()
            picker.Pick(click_pos[0], click_pos[1], 0, self.renderer)
            self.end_point = picker.GetPickPosition()

            distance = vtk.vtkMath.Distance2BetweenPoints(self.start_point, self.end_point)
            self.text_actor.SetInput(f"Distance: {distance:.2f}")

            self.line_source.SetPoint1(self.start_point)
            self.line_source.SetPoint2(self.end_point)
            self.line_source.Update()

            self.GetInteractor().GetRenderWindow().Render()


def render_stl_file(file_path):
    # Create a reader and load the STL file
    reader = vtk.vtkSTLReader()
    reader.SetFileName(file_path)
    reader.Update()

    # Get the STL mesh
    stl_mesh = reader.GetOutput()

    # Create a mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(stl_mesh)

    # Create an actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create a renderer and add the actor
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)

    # Create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create an interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Set the custom interactor style
    measure_style = MeasureInteractorStyle(renderer)
    interactor.SetInteractorStyle(measure_style)

    # Initialize the interactor and start the rendering loop
    interactor.Initialize()
    render_window.Render()

    # Start the interactor loop
    interactor.Start()


if __name__ == "__main__":
    file_path = 'path_to_stl_file.stl'
    render_stl_file(file_path)
