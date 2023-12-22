import vtk
from PyQt5 import QtCore, QtWidgets
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class LiveMeasurements(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, vtk_widget, window):
        self.parent = window
        self.vtk_widget = vtk_widget
        self.AddObserver("LeftButtonPressEvent", self.on_left_button_press) 

        # Initialize line source and mapper
        self.line_source = vtk.vtkLineSource()
        self.line_mapper = vtk.vtkPolyDataMapper()
        self.line_actor = vtk.vtkActor()

        # Initialize text actor for line length
        self.text_actor = vtk.vtkTextActor()

        # Initialize variables for tracking the clicked positions
        self.start_click_position = None
        self.end_click_position = None

        # Initialize line length display
        self.line_length_displayed = False

        # Initialize picking flag
        self.picking = False

    def on_left_button_press(self, obj, event):
        # Remove previous actors from the renderer
        self.parent.renderer.RemoveActor(self.line_actor)
        self.parent.renderer.RemoveActor(self.text_actor)

        click_position = self.GetInteractor().GetEventPosition()

        # Convert the click position to world coordinates
        picker = vtk.vtkPointPicker()
        picker.Pick(click_position[0], click_position[1], 0, self.parent.renderer)

        if picker.GetActor():
            # User clicked on the model, perform ray casting along X-axis
            self.ray_casting(picker.GetPickPosition(), [1, 0, 0])
        else:
            # User clicked in free space, perform ray casting along X-axis
            self.ray_casting(self.get_world_coordinates(click_position), [1, 0, 0])
    
    def set_mapper(self, mapper):
        self.mapper = mapper
    def ray_casting(self, start_point, direction):
        # Initialize ray casting mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        actor = vtk.vtkActor()

        # Initialize a line source for ray casting
        ray_source = vtk.vtkLineSource()
        ray_source.SetPoint1(start_point)
        ray_source.SetPoint2(start_point[0] + direction[0] * 1000, start_point[1] + direction[1] * 1000, start_point[2] + direction[2] * 1000)
        ray_source.Update()

        # Perform ray casting
        mapper.SetInputConnection(ray_source.GetOutputPort())
        actor.SetMapper(mapper)

        # Create an intersect filter
        intersect_filter = vtk.vtkIntersectionPolyDataFilter()
        intersect_filter.SetInputConnection(0, ray_source.GetOutputPort())
        intersect_filter.SetInputData(1,  self.mapper.GetInput())

        # Set the tolerance for intersection (adjust as needed)
        intersect_filter.SetTolerance(0.01)

        # Update the intersection filter
        intersect_filter.Update()

        # Get the intersection points
        intersections = vtk.vtkPoints()
        intersections.SetData(intersect_filter.GetOutput().GetPoints())

        if intersections.GetNumberOfPoints() > 0:
            # Model was hit, draw a line along the X-axis on the model
            self.start_click_position = start_point
            self.end_click_position = intersections.GetPoint(0)

            # Update the line source
            self.line_source.SetPoint1(self.start_click_position)
            self.line_source.SetPoint2(self.end_click_position)
            self.line_source.Update()

            # Set the mapper and actor for the line
            self.line_mapper.SetInputConnection(self.line_source.GetOutputPort())
            self.line_actor.SetMapper(self.line_mapper)

            # Add the line actor to the renderer
            self.parent.renderer.AddActor(self.line_actor)

            # Calculate the length of the line
            line_length = vtk.vtkMath.Distance2BetweenPoints(
                self.start_click_position, self.end_click_position
            )

            # Set the position of the text actor
            text_position = (
                (self.start_click_position[0] + self.end_click_position[0]) / 2,
                (self.start_click_position[1] + self.end_click_position[1]) / 2,
                (self.start_click_position[2] + self.end_click_position[2]) / 2
            )

            # Set the text for the text actor
            self.text_actor.SetTextScaleModeToNone()
            self.text_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
            self.text_actor.SetPosition(0.1, 0.9)  # Adjust the position as needed
            self.text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)  # White color
            self.text_actor.GetTextProperty().SetFontSize(20)
            self.text_actor.SetInput("Length: {:.2f} mm".format(line_length))

            # Add the text actor to the renderer
            self.parent.renderer.AddActor(self.text_actor)

            # Update the renderer
            self.parent.renderer.Modified()
            self.parent.vtk_widget.GetRenderWindow().Render()

            # Reset click positions for the next ray casting
            self.start_click_position = None
            self.end_click_position = None
        else:
            # Free space was hit, draw a line between two points on the X-axis
            end_point = start_point[0] + direction[0] * 1000, start_point[1] + direction[1] * 1000, start_point[2] + direction[2] * 1000

            # Update the line source
            self.line_source.SetPoint1(start_point)
            self.line_source.SetPoint2(end_point)
            self.line_source.Update()

            # Set the mapper and actor for the line
            self.line_mapper.SetInputConnection(self.line_source.GetOutputPort())
            self.line_actor.SetMapper(self.line_mapper)

            # Add the line actor to the renderer
            self.parent.renderer.AddActor(self.line_actor)

            # Calculate the length of the line
            line_length = vtk.vtkMath.Distance2BetweenPoints(start_point, end_point)

            # Set the position of the text actor
            text_position = (
                (start_point[0] + end_point[0]) / 2,
                (start_point[1] + end_point[1]) / 2,
                (start_point[2] + end_point[2]) / 2
            )

            # Set the text for the text actor
            self.text_actor.SetTextScaleModeToNone()
            self.text_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
            self.text_actor.SetPosition(0.1, 0.9)  # Adjust the position as needed
            self.text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)  # White color
            self.text_actor.GetTextProperty().SetFontSize(20)
            self.text_actor.SetInput("Length: {:.2f} mm".format(line_length))

            # Add the text actor to the renderer
            self.parent.renderer.AddActor(self.text_actor)

            # Update the renderer
            self.parent.renderer.Modified()
            self.parent.vtk_widget.GetRenderWindow().Render()
