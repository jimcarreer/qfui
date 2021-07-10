from typing import Optional, Set

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QDialog, QHBoxLayout, QPushButton, QGroupBox

from qfui.models.enums import SectionModes


class ModeSelection(QWidget):

    selection_changed = Signal(set)

    def __init__(self, parent: Optional[QWidget] = None, selected: Set[SectionModes] = None):
        super().__init__(parent)
        self._selected = selected or set()
        self._layout = QVBoxLayout(parent=self)
        self.setLayout(self._layout)
        self._checkboxes = {}
        for mode in SectionModes:
            self._checkboxes[mode] = QCheckBox(mode.value.title(), parent=self)
            self._layout.addWidget(self._checkboxes[mode])
            self._checkboxes[mode].setChecked(mode in self._selected)
            self._checkboxes[mode].stateChanged.connect(self._box_check)

    @property
    def selected(self) -> Set[SectionModes]:
        return self._selected

    @selected.setter
    def selected(self, selected: Set[SectionModes] = None):
        self._selected = selected or set()

    def _box_check(self):
        self._selected = [m for m, v in self._checkboxes.items() if v.isChecked()]
        self.selection_changed.emit(self._selected)


class ModeSelectionDialog(QDialog):

    ok_clicked = Signal(set)
    cancel_clicked = Signal(set)

    def __init__(self, title: str = "Modes", parent: Optional[QWidget] = None, selected: Set[SectionModes] = None):
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        self._layout = QVBoxLayout(parent=self)
        self.setLayout(self._layout)
        self._group = QGroupBox(self.tr("Section Modes"))
        self._group_layout = QVBoxLayout()
        self._group.setLayout(self._group_layout)
        self._layout.addWidget(self._group)
        self._mode_select = ModeSelection(self, selected)
        self._mode_select.selection_changed.connect(self.selection_change)
        self._group_layout.addWidget(self._mode_select)
        self._button_layout = QHBoxLayout()
        self._layout.addLayout(self._button_layout, stretch=True)
        self._ok_button = QPushButton(self.tr("OK"))
        self._ok_button.clicked.connect(self.ok_click)
        self._cancel_button = QPushButton(self.tr("Cancel"))
        self._cancel_button.clicked.connect(self.cancel_click)
        self._button_layout.addWidget(self._ok_button)
        self._button_layout.addWidget(self._cancel_button)
        self.selection_change()

    @property
    def selected(self) -> Set[SectionModes]:
        return self._mode_select.selected

    @selected.setter
    def selected(self, selected: Set[SectionModes] = None):
        self._mode_select.selected = selected

    def selection_change(self):
        self._ok_button.setDisabled(len(self._mode_select.selected) == 0)

    def ok_click(self):
        self.close()
        self.ok_clicked.emit(self._mode_select.selected)

    def cancel_click(self):
        self.close()
        self.cancel_clicked.emit(self._mode_select.selected)
