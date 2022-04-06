from ate_spyder.widgets.actions_on.utils.FileObserver import FileObserver


class FileItemHandler:
    def __init__(self, project_info, base_path):
        self.file_items = []
        self.project_info = project_info
        self.base_path = base_path
        self.observer = FileObserver(self.base_path)
        self.observer.start_observer()
        self._append_items()

    def _append_items(self):
        self._append_pattern_item()
        self._append_wave_item()

    def _append_pattern_item(self):
        from ate_spyder.widgets.actions_on.patterns.PatternItem import PatternItem
        self.pattern_section = PatternItem('pattern', self.base_path, self.project_info)
        self.file_items.append(self.pattern_section)
        self.observer.append_section(self.pattern_section)

    def _append_wave_item(self):
        from ate_spyder.widgets.actions_on.waves.WaveItem import WaveItem
        self.wave_section = WaveItem('waves', self.base_path, self.project_info)
        self.file_items.append(self.wave_section)
        self.observer.append_section(self.wave_section)

    def items(self):
        return self.file_items

    def clean_up(self):
        self.observer.stop_observer()
