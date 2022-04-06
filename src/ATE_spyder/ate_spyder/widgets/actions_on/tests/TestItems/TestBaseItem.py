from ate_spyder.widgets.actions_on.utils.StateItem import StateItem


class TestBaseItem(StateItem):
    def __init__(self, project_info, name, parent):
        super().__init__(project_info, name, parent)

    def _set_icon(self, is_virtual):
        from ate_spyder.widgets.actions_on.documentation.FileIcon import FileIcons
        from ate_spyder.widgets.actions_on.documentation.Constants import FileIconTypes

        if not is_virtual:
            icon = FileIcons[FileIconTypes.PY.name]
        else:
            icon = FileIcons[FileIconTypes.VIRTUAL.name]

        if icon is None:
            return

        self.setIcon(icon)
