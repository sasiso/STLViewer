import vtk
from PyQt5 import QtCore, QtGui, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create a VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)

        # Create a slider widget
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)
        self.slider.setTickInterval(10)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)

        # Create the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.vtk_widget)
        layout.addWidget(self.slider)

        # Create a frame and set the layout
        frame = QtWidgets.QFrame(self)
        frame.setLayout(layout)

        # Set the central widget
        self.setCentralWidget(frame)

        # Initialize VTK objects and rendering
        self.renderer = vtk.vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()

        # Load and render the STL file
        self.load_stl_file('path_to_stl_file.stl')

        # Connect the slider value change event
        self.slider.valueChanged.connect(self.on_slider_value_changed)

    def load_stl_file(self, file_path):
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

        # Add the actor to the renderer
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()

    def on_slider_value_changed(self, value):
        opacity = value / 100.0
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        actor = actors.GetNextItem()
        while actor:
            actor.GetProperty().SetOpacity(opacity)
            actor = actors.GetNextItem()
        self.vtk_widget.GetRenderWindow().Render()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(800, 600)
    sys.exit(app.exec_())
