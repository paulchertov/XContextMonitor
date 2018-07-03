"""
Module contains resources common to all or many
controllers 
classes:
    WithViewMixin - controller with view mixin unifies gui installation 
    process - pointing where to find .qss and .ui files
    TaskGroupController - controller for some process with progress bar
functions:
    clear_items - clears all items from target layout
"""

import os
from typing import Callable, List, ClassVar

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QFrame, QLayout, QProgressBar


class WithViewMixin:
    # styles text(will be saved in class variable for not reopening .qss file)
    qss_text: ClassVar[str] = ""

    # gui_name class variable should be defined in main class
    # gui_name.qss and gui_name.ui files from which styles and ui to be loaded
    gui_name: ClassVar[str] = ""

    def install_gui(self):
        """
        Load /gui/{self.view}.ui into self.view
        :return: None
        """
        gui_path = os.path.join(
            'gui', '{}.ui'.format(self.gui_name)
        )
        self.view = QFrame()
        self.view = loadUi(gui_path, self.view)

    def set_styles(self, reload: bool=False):
        """
        Loads /gui/{self.view}.qss file contents into self.style
        property 
        :param reload: reload styles from file or just set from class var
        :return: 
        """
        if not self.qss_text or reload:
            style_path = os.path.join(
                'gui', '{}.qss'.format(self.gui_name)
            )
            style_path = os.path.abspath(style_path)
            with open(style_path, 'r') as file:
                self.qss_text = file.read()
        self.view.setStyleSheet(self.qss_text)

    def view_handler(self, handler: Callable):
        """
        If controller is not QWidget all handlers could be added
        to its view to work as intended. This method does 
        self.view.method = self.method for provided method
        :param handler: handler method
        :return: None
        """
        setattr(self.view, handler.__name__, handler)

    def view_handlers(self, handlers: List[Callable]):
        """
        WithViewMixin.view_handler for list of handlers
        :param handlers: 
        :return: None
        """
        for handler in handlers:
            self.view_handler(handler)


def clear_items(layout: QLayout):
    """
    Clears all widgets from layout
    :param layout: layout to clear
    :return: None
    """
    while layout.count() > 0:
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            layout.removeWidget(widget)
            widget.deleteLater()
