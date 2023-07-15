import vtk


class AnnotationInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, vtk_widget, window):
        self.window = window
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        self.vtk_widget = vtk_widget
        self.annotation_text = ""
        self.annotation_actors = []
        self.line_actors = []
        self.bounding_box_actors = []

    def left_button_press_event(self, obj, event):
        if not self.window.annotation_button.isChecked():
            super().OnLeftButtonDown()
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
            self.add_annotation(picked_position, mouse_position)

        self.vtk_widget.GetRenderWindow().Render()
    def add_annotation(self, position, click_position):
        annotation_text = self.window.annotation_text_edit.toPlainText()

        if annotation_text:
            self.annotation_text = annotation_text

            annotation_actor = vtk.vtkBillboardTextActor3D()
            annotation_actor.SetInput(self.annotation_text)
            annotation_actor.GetTextProperty().SetColor(1.0, 1.0, 0)
            annotation_actor.GetTextProperty().SetFontSize(40)
            annotation_actor.SetVisibility(True)

            # Get the model's bounding box
            mapper = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().GetActors().GetLastActor().GetMapper()
            mapper.Update()
            bounds = mapper.GetBounds()

            # Calculate the distance from the clicked position to the left and right sides of the bounding box
            distance_left = abs(click_position[0] - bounds[0])
            distance_right = abs(click_position[0] - bounds[1])

            # Set the position of the annotation based on the calculated distances
            if distance_left < distance_right:
                annotation_position = (position[0] - 5, position[1], position[2])
            else:
                annotation_position = (position[0] + 5, position[1], position[2])

            annotation_actor.SetPosition(annotation_position)

            self.annotation_actors.append(annotation_actor)
            self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(
                annotation_actor
            )

            # Create a line between the text and the picked position
            line_source = vtk.vtkLineSource()
            line_source.SetPoint1(position)
            line_source.SetPoint2(annotation_position)

            line_mapper = vtk.vtkPolyDataMapper()
            line_mapper.SetInputConnection(line_source.GetOutputPort())

            line_actor = vtk.vtkActor()
            line_actor.SetMapper(line_mapper)
            line_actor.GetProperty().SetColor(1.0, 0, 0)  # Red line
            line_actor.GetProperty().SetLineWidth(4.0)    # Set the line width to 4 pixels

            self.line_actors.append(line_actor)
            self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(
                line_actor
            )

            self.window.annotation_text_edit.clear()

    def update_annotations_position(self):
        # Update the position of the annotations based on the current position of the model
        renderer = self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer()

        for annotation_actor, line_actor, bounding_box_actor in zip(
            self.annotation_actors, self.line_actors, self.bounding_box_actors
        ):
            annotation_actor.SetCamera(renderer.GetActiveCamera())
            line_source = line_actor.GetMapper().GetInputConnection(0, 0).GetProducer()
            line_source.SetPoint1(annotation_actor.GetPosition())
            line_source.SetPoint2(annotation_actor.GetPosition())

            # Update the position of the bounding box around the annotation text
            if bounding_box_actor.GetVisibility():
                bounding_box_source = bounding_box_actor.GetMapper().GetInputConnection(0, 0).GetProducer()
                bounding_box_source.SetInputData(annotation_actor.GetMapper().GetInput())
                bounding_box_actor.SetPosition(annotation_actor.GetPosition())

    def OnMouseMove(self):
        if not self.window.annotation_button.isChecked():
            super().OnMouseMove()
        else:
            self.update_annotations_position()

    def OnLeftButtonUp(self):
        if not self.window.annotation_button.isChecked():
            super().OnLeftButtonUp()
        else:
            self.update_annotations_position()

    def OnRightButtonDown(self):
        if not self.window.annotation_button.isChecked():
            super().OnRightButtonDown()
        else:
            self.update_annotations_position()

    def on_annotation_button_clicked(self):
        if self.window.annotation_button.isChecked():
            for bounding_box_actor in self.bounding_box_actors:
                bounding_box_actor.SetVisibility(True)
        else:
            for bounding_box_actor in self.bounding_box_actors:
                bounding_box_actor.SetVisibility(False)
