class PQClientController(QObject, WithViewMixin):
    gui_name = "client"

    def __init__(self, model: PQClientModel):
        super().__init__()
        self.install_gui()
        self.set_styles()
        self.model = model
        self.view_handler(self.checkbox_clicked)
        self.view.set_active.clicked.connect(self.checkbox_clicked)
        self.redraw()

    @pyqtSlot(bool)
    def checkbox_clicked(self, state: bool):
        self.model.set_active = state

    def redraw(self):
        self.view.login.setText(self.model.login)
        self.view.updated.setText(
            self.model.timestamp.strftime("%d/%m/%Y %H:%M")
        )
        self.view.source.setText(self.model.source)
        self.view.set_active.setChecked(1 if self.model.set_active else 0)