from typing import List
from collections import namedtuple

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from xlsxwriter import Workbook

from controllers.common import WithViewMixin, clear_items
from model.gui.links import ParsedLink


# xslsx styles
xlsx_column_header_style = {
'bold': 1,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
}


xlsx_warning_header_style = {
    'bold': 1,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': 'yellow'
}


xlsx_warning_cell_style = {'fg_color': 'yellow'}


xlsx_error_header_style = {
    'bold': 1,
    'border': 1,
    'align': 'center',
    'valign': 'vcenter',
    'fg_color': 'red'
}


xlsx_error_cell_style = {
    'fg_color': 'red'
}


class PQResultController(QObject, WithViewMixin):
    gui_name = "result"

    def __init__(self):
        super().__init__()
        self.install_gui()
        self.set_styles()
        self.__model: list = []
        self.view_handler(self.download)
        self.view.download_button.clicked.connect(self.view.download)

    @property
    def model(self)->List[ParsedLink]:
        return self.__model

    @model.setter
    def model(self, val: List[ParsedLink]):
        self.__model = val
        self.redraw()

    @property
    def errors(self)->List[ParsedLink]:
        return [error for error in self.__model if error.kind == "Error"]

    @property
    def warnings(self) -> List[ParsedLink]:
        return [warning for warning in self.__model if warning.kind == "Warning"]

    def redraw(self):
        self.view.wrong_elements.setText(
            "Элементов с ошибками: {}".format(len(self.errors))
        )
        self.view.warnings_elements.setText(
            "Элементов с предупреждениями: {}".format(len(self.warnings))
        )

    def download(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setDefaultSuffix(".xlsx")
        dlg.setNameFilter("*.xlsx")
        if dlg.exec_():
            path = dlg.selectedFiles()[0].__repr__().strip("'")
            workbook = Workbook(path, {'strings_to_urls': False})
            worksheet = workbook.add_worksheet()
            row = 0
            col_headers = [
                "Код ответа или текст ошибки",
                "URL",
                "login",
                "Кампания",
                "Группа",
                "Объявление",
                "Комментарий",
				"Статус"
            ]
            col_header_style = workbook.add_format(
                xlsx_column_header_style
            )
            for col, field in enumerate(col_headers):
                worksheet.write(row, col, field, col_header_style)
            row += 1

            if self.errors:
                header_style = workbook.add_format(
                    xlsx_error_header_style
                )
                cell_style = workbook.add_format(
                    xlsx_error_cell_style
                )
                worksheet.merge_range(
                    first_row=row, first_col=0, last_row=row+1, last_col=6,
                    data="ОШИБКИ",
                    cell_format=header_style
                )
                row += 1
                for error in self.errors:
                    for col, field in enumerate(error):
                        worksheet.write(row, col, field, cell_style)
                    row += 1

            if self.warnings:
                header_style = workbook.add_format(
                    xlsx_warning_header_style
                )
                cell_style = workbook.add_format(
                    xlsx_warning_cell_style
                )
                worksheet.merge_range(
                    first_row=row, first_col=0, last_row=row + 1, last_col=6,
                    data="ПРЕДУПРЕЖДЕНИЯ",
                    cell_format=header_style
                )
                row += 1
                for warning in self.warnings:
                    for col, field in enumerate(warning):
                        worksheet.write(row, col, field, cell_style)
                    row += 1

            workbook.close()