# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Aug  3 16:51:42 2019
#
# @author: Brénainn Woodsend
#
#
# QtFigure.py provides a figure that doubles as a QWidget.
# Copyright (C) 2019  Brénainn Woodsend
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================

from __future__ import print_function

import numpy as np
import sys
from vtkplotlib._get_vtk import vtk, QVTKRenderWindowInteractor

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from vtkplotlib.figures.BaseFigure import BaseFigure, VTKRenderer
from vtkplotlib import nuts_and_bolts
from vtkplotlib._vtk_errors import handler, silencer

if __name__ == "__main__":
    debug = print
else:
    debug = lambda *x: None


class QtFigure(BaseFigure, QWidget):
    """The VTK render window embedded into a PyQt5 QWidget. This can be
    embedded into a GUI the same way all other QWidgets are used.

    :param name: The window title of the figure, only applicable is parent is None, defaults to 'qt vtk figure'.
    :type name: str, optional

    :param parent: Parent window, defaults to None.
    :type parent: NoneType, optional


    .. note::

        If you are new to Qt then this is a rather poor place to start. Whilst
        many libraries in Python are intuitive enough to be able to just dive
        straight in, Qt is not one of them. Preferably familiarise yourself
        with some basic Qt before coming here.


    This class inherits both from QWidget and a vtkplotlib BaseFigure class.
    Therefore it can be used exactly the same as you would normally use either
    a `QWidget` or a `vpl.figure`.

    Care must be taken when using Qt to ensure you have **exactly one**
    QApplication. To make this class quicker to use the qapp is created
    automatically but is wrapped in a

    .. code-block:: python

        if QApplication.instance() is None:
            self.qapp = QApplication(sys.argv)
        else:
            self.qapp = QApplication.instance()

    This prevents multiple QApplication instances from being created (which
    causes an instant crash) whilst also preventing a QWidget from being
    created without a qapp (which also causes a crash).


    On ``self.show()``, ``self.qapp.exec_()`` is called automatically if
    ``self.parent() is None`` (unless specified otherwise). If the QFigure is part
    of a larger window then ``larger_window.show()`` must also show
    the figure. It won't begin interactive mode until ``qapp.exec_()`` is
    called.


    If the figure is not to be part of a larger window then it behaves exactly
    like a regular figure. You just need to explicitly create it first.

    .. code-block:: python

        import vtkplotlib as vpl

        # Create the figure. This automatically sets itself as the current
        # working figure. The qapp is created automatically if one doesn't
        # already exist.
        vpl.QtFigure("Exciting Window Title")

        # Everything from here on should be exactly the same as normal.

        vpl.quick_test_plot()

        # Automatically calls ``qapp.exec_()``. If you don't want it to then
        # use ``vpl.show(False)``.
        vpl.show()


    However this isn't particularly helpful. A more realistic example would
    require the figure be part of a larger window. In this case, treat the
    figure as you would any other QWidget. You must explicitly call
    ``figure.show()`` however. (Not sure why.)

    .. code-block:: python

        import vtkplotlib as vpl
        from PyQt5 import QtWidgets
        import numpy as np
        import sys

        # python 2 compatibility
        from builtins import super


        class FigureAndButton(QtWidgets.QWidget):
            def __init__(self):
                super().__init__()

                # Go for a vertical stack layout.
                vbox = QtWidgets.QVBoxLayout()
                self.setLayout(vbox)

                # Create the figure
                self.figure = vpl.QtFigure()

                # Create a button and attach a callback.
                self.button = QtWidgets.QPushButton("Make a Ball")
                self.button.released.connect(self.button_pressed_cb)

                # QtFigures are QWidgets and are added to layouts with `addWidget`
                vbox.addWidget(self.figure)
                vbox.addWidget(self.button)


            def button_pressed_cb(self):
                \"""Plot commands can be called in callbacks. The current working
                figure is still self.figure and will remain so until a new
                figure is created explicitly. So the ``fig=self.figure``
                arguments below aren't necessary but are recommended for
                larger, more complex scenarios.
                \"""

                # Randomly place a ball.
                vpl.scatter(np.random.uniform(-30, 30, 3),
                            color=np.random.rand(3),
                            fig=self.figure)

                # Reposition the camera to better fit to the balls.
                vpl.reset_camera(self.figure)

                # Without this the figure will not redraw unless you click on it.
                self.figure.update()


            def show(self):
                # The order of these two are interchangeable.
                super().show()
                self.figure.show()


            def closeEvent(self, event):
                \"""This isn't essential. VTK, OpenGL, Qt and Python's garbage
                collect all get in the way of each other so that VTK can't
                clean up properly which causes an annoying VTK error window to
                pop up. Explicitly calling QtFigure's `closeEvent()` ensures
                everything gets deleted in the right order.
                \"""
                self.figure.closeEvent(event)




        qapp = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

        window = FigureAndButton()
        window.show()
        qapp.exec_()


    .. seealso:: QtFigure2 is an extension of this to provide some standard GUI elements, ready-made.


    """

    def __init__(self, name="qt vtk figure", parent=None):

        self.qapp = QApplication.instance() or QApplication(sys.argv)
#        debug(self.qapp)
#        debug("qw init")
        QWidget.__init__(self, parent)

#        debug("name")
        self.window_name = name

        self.setWindowModified(False)

#        debug("layout")
        self.vl = QVBoxLayout()
#        debug("vtkwidget")
        self.vtkWidget# = QVTKRenderWindowInteractor(self)
#        debug("addWidget")
#        self.vl.addWidget(self.vtkWidget)
#        debug("renWin")
        self.renWin
        iren = self.iren

        # try to prevent error pop-up windows
        # They don't seem to achieve anything. Normally these spew errors on
        # cleanup, by which time the silencer has already been garbage collected.
        silencer.attach(self.vtkWidget)
        silencer.attach(self.iren)
        silencer.attach(self.renWin)


        self.data_holder = []
#        debug("basefig init")
        BaseFigure.__init__(self, name)
        self.iren_style = vtk.vtkInteractorStyleTrackballCamera()
        iren.SetInteractorStyle(self.iren_style)

        self.renWin.AddRenderer(self.renderer)

        self.setLayout(self.vl)


    def _re_init(self):
        debug("re init")
        renderer = self.renderer
        name = self.window_name
        parent = self.parent()
#        self.__init__(name, parent)
        QWidget.__init__(self, parent)
        self.window_name = name
        self.vtkWidget, self.renWin, self.iren.SetInteractorStyle(self.iren_style)
        self.renderer = renderer
        self.renWin.AddRenderer(self.renderer)
        self.renderer.SetActiveCamera(self.camera)
        if self.vl.indexOf(self.vtkWidget) == -1:
            self.vl.insertWidget(self._vtkwidget_replace_index, self.vtkWidget)
        self.setLayout(self.vl)


    def show(self, block=None):
        if self.renWin is not self.renderer.GetRenderWindow():
            self._re_init()
        QWidget.show(self)
        if block is None:
            block = self.parent() is None
        BaseFigure.show(self, block)
        self.setWindowTitle(self.window_name)

        if block:
            self.qapp.exec_()


    @nuts_and_bolts.init_when_called
    def vtkWidget(self):
        vtkWidget = QVTKRenderWindowInteractor(self)
        self.vl.addWidget(vtkWidget)
        return vtkWidget

    @nuts_and_bolts.init_when_called
    def renWin(self):
        renWin = self.vtkWidget.GetRenderWindow()
#        if not renWin.HasRenderer(self.renderer):
#            renWin.AddRenderer(self.renderer)
#            self.renderer.SetRenderWindow(renWin)
        return renWin

    @nuts_and_bolts.init_when_called
    def iren(self):
#        iren = vtk.vtkRenderWindowInteractor()
#        self.renWin.SetInteractor(iren)
#        assert iren is self.vtkWidget.GetRenderWindow().GetInteractor()
#        BaseFigure.__init__(self)
        return self.vtkWidget.GetRenderWindow().GetInteractor()

    def update(self):
        BaseFigure.update(self)
        QWidget.update(self)
#        self.repaint()
        self.qapp.processEvents()

    def close(self):
        BaseFigure.close(self)
        QWidget.close(self)
        self._clean_up()

    def finalise(self):
#        Very important that BaseFigure.finalise gets overwritten. This gets
#        called immediately after self.iren.Start(). The original performs resets
#        that stop the QtFigure from responding. These resets must go in closeEvent().
        pass

    def _clean_up(self):
        debug("cleaning up")
        self.renWin.MakeCurrent()
        self._vtkwidget_replace_index = self.vl.indexOf(self.vtkWidget)
        self.vl.removeWidget(self.vtkWidget)
#        self.renderer.RemoveAllViewProps()
        self.renWin.Finalize()
        self.renWin.RemoveRenderer(self.renderer)
        del self.vtkWidget, self.iren, self.renWin


    window_name = property(QWidget.windowTitle, QWidget.setWindowTitle)

    def closeEvent(self, event):
        self._clean_up()
#        debug("close")

    def __del__(self):
#        debug("delete")
        try:
            self.renderer.RemoveAllViewProps()
        except (AttributeError, TypeError):
            # In Python2, RemoveAllViewProps is already None 
            pass
#        BaseFigure.__del__(self)
#        self.renderer.FastDelete()
#        self.renWin.FastDelete()
#        self.vtkWidget.FastDelete()



from vtkplotlib.tests._figure_contents_check import checker
@checker()
def test():
    import vtkplotlib as vpl

    self = QtFigure("a Qt widget figure")

    assert self is vpl.gcf()

    direction = np.array([1, 0, 0])
    vpl.quiver(np.array([0, 0, 0]), direction)
    vpl.view(camera_direction=direction)
    vpl.reset_camera()

#    self.show()


#    vpl.show()
    # self.show()
#    self.__init__()
#    self.show()
#    self.vtkWidget.show()
#    self.update()
#    self.show(False)
#    self.update()
#    self.vtkWidget.show()
#    self.qapp.exec_()


    globals().update(locals())



if __name__ == "__main__":
    test()

