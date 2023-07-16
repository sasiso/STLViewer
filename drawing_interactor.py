# drawing_interactor.py
import vtk

class DrawingInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, vtk_widget, window):
        self.window = window
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        self.AddObserver("LeftButtonReleaseEvent", self.left_button_release_event)
        self.AddObserver("MouseMoveEvent", self.mouse_move_event)
        self.vtk_widget = vtk_widget
        self.drawing = False
        self.line_points = []
        self.drawing_actors = []

    def left_button_press_event(self, obj, event):
        if not self.window.drawing_button.isChecked():
            super().OnLeftButtonDown()
            return

        interactor = self.GetInteractor()
        self.line_points.clear()
        self.drawing = True

    def left_button_release_event(self, obj, event):
        if not self.window.drawing_button.isChecked() or not self.drawing:
            super().OnLeftButtonUp()
            return

        self.drawing = False
        self.draw_line()
        self.line_points.clear()

    def mouse_move_event(self, obj, event):
        if not self.window.drawing_button.isChecked() or not self.drawing:
            super().OnMouseMove()
            return

        interactor = self.GetInteractor()
        mouse_position = interactor.GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.001)
        picker.Pick(
            mouse_position[0],
            mouse_position[1],
            0,
            self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer(),
        )

        if picker.GetCellId() >= 0:
            picked_position = picker.GetPickPosition()
            self.line_points.append(picked_position)
            self.draw_line()

    def draw_line(self):
        if len(self.line_points) < 2:
            return

        # Create a line between the points
        line_source = vtk.vtkLineSource()
        line_source.SetPoint1(self.line_points[-2])
        line_source.SetPoint2(self.line_points[-1])
        line_source.Update()

        # Create a mapper and actor for the line
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(line_source.GetOutput())

        line_actor = vtk.vtkActor()
        line_actor.SetMapper(mapper)
        line_actor.GetProperty().SetColor(0.0, 0.0, 1.0)  # Blue color
        line_actor.GetProperty().SetLineWidth(2)  # Adjust line width as needed

        # Add the line actor to the renderer
        self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(line_actor)
        self.drawing_actors.append(line_actor)
        self.vtk_widget.GetRenderWindow().Render()

    def clear_drawings(self):
        # Remove all drawing actors from the renderer
        for actor in self.drawing_actors:
            self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(actor)
        self.drawing_actors.clear()
        self.vtk_widget.GetRenderWindow().Render()
