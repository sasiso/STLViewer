from collections import defaultdict

import vtk


class AnnotationInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, vtk_widget, window):
        self.window = window
        self.AddObserver("LeftButtonPressEvent", self.left_button_press_event)
        self.vtk_widget = vtk_widget
        self.annotation_text = ""
        self.annotation_actors = defaultdict(list)

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
            self.add_annotation(picked_position)

        self.vtk_widget.GetRenderWindow().Render()

    def add_annotation(self, position):
        annotation_text = self.window.annotation_text_edit.toPlainText()

        if annotation_text:
            self.annotation_text = annotation_text

            annotation_actor = vtk.vtkBillboardTextActor3D()
            annotation_actor.SetInput(self.annotation_text)
            annotation_actor.SetPosition(position)
            annotation_actor.GetTextProperty().SetColor(1.0, 1.0, 0)
            annotation_actor.GetTextProperty().SetFontSize(40)
            annotation_actor.SetVisibility(True)

            self.annotation_actors[position].append(annotation_actor)

            self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(
                annotation_actor
            )

            self.window.annotation_text_edit.clear()

            annotation_text = self.window.annotation_text_edit.toPlainText()

            if annotation_text:
                self.annotation_text = annotation_text

                annotation_actor = vtk.vtkBillboardTextActor3D()
                annotation_actor.SetInput(self.annotation_text)
                annotation_actor.SetPosition(position)
                annotation_actor.SetVisibility(True)

                self.annotation_actors[position].append(annotation_actor)

                self.vtk_widget.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(
                    annotation_actor
                )

                self.window.annotation_text_edit.clear()

    def OnMouseMove(self):
        if not self.window.annotation_button.isChecked():
            super().OnMouseMove()

    def OnLeftButtonUp(self):
        if not self.window.annotation_button.isChecked():
            super().OnLeftButtonUp()

    def OnRightButtonDown(self):
        if not self.window.annotation_button.isChecked():
            super().OnRightButtonDown()
