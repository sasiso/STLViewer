import vtk
from PyQt5 import QtCore, QtGui, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Create a VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)

        # Create a tool pane widget
        self.tool_pane = QtWidgets.QWidget(self)
        self.tool_pane.setMaximumWidth(int(0.2 * self.width()))  # Set maximum width to 20% of window width

        # Create a slider widget
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.tool_pane)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(100)
        self.slider.setTickInterval(10)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setStyleSheet("QSlider::handle:horizontal {"
                                   "background-color: #2196F3;"
                                   "border: 1px solid #2196F3;"
                                   "width: 10px;"
                                   "margin: -5px 0;"
                                   "border-radius: 5px;"
                                   "}")

        # Create a wireframe switch button
        self.switch_button = QtWidgets.QPushButton('Wireframe', self.tool_pane)
        self.switch_button.setCheckable(True)
        self.switch_button.setStyleSheet("QPushButton {"
                                          "background-color: #4CAF50;"
                                          "border: none;"
                                          "padding: 5px 10px;"
                                          "border-radius: 5px;"
                                          "color: white;"
                                          "}"
                                          "QPushButton:checked {"
                                          "background-color: #F44336;"
                                          "}")

        # Create the layout for the tool pane
        tool_layout = QtWidgets.QVBoxLayout(self.tool_pane)
        tool_layout.addWidget(self.slider)
        tool_layout.addWidget(self.switch_button)
        tool_layout.addStretch()

        # Create the main layout
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.vtk_widget)
        main_layout.addWidget(self.tool_pane)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create a frame and set the main layout
        frame = QtWidgets.QFrame(self)
        frame.setLayout(main_layout)

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

        # Connect the switch button clicked event
        self.switch_button.clicked.connect(self.on_switch_button_clicked)

        # Create a timer to delay the update
        self.update_timer = QtCore.QTimer()
        self.update_timer.setInterval(500)  # Adjust the delay as needed
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_model)

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
        # Restart the update timer
        self.update_timer.start()

    def on_switch_button_clicked(self):
        # Restart the update timer
        self.update_timer.start()

    def update_model(self):
        opacity = self.slider.value() / 100.0
        is_wireframe = self.switch_button.isChecked()
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        actor = actors.GetNextItem()
        while actor:
            actor.GetProperty().SetOpacity(opacity)
            if is_wireframe:
                actor.GetProperty().SetRepresentationToWireframe()
            else:
                actor.GetProperty().SetRepresentationToSurface()
            actor = actors.GetNextItem()
        self.vtk_widget.GetRenderWindow().Render()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')  # Set the application style to Fusion (dark theme)

    # Set the dark theme palette
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    window.resize(800, 600)
    sys.exit(app.exec_())
