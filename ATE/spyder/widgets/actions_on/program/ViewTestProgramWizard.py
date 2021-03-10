import os
from ATE.spyder.widgets.navigation import ProjectNavigation
from ATE.spyder.widgets.actions_on.program.TestProgramWizard import TestProgramWizard


class ViewTestProgramWizard(TestProgramWizard):
    def __init__(self, name: str, project_info: ProjectNavigation, owner: str, parent: str):
        super().__init__(project_info, owner, parent=parent, read_only=True, enable_edit=False)
        self._setup_view()
        ViewTestProgramWizard.setup_view(self, name)

    def _setup_view(self):
        self.hardware.clear()
        self.base.clear()
        self.target.clear()
        self.sequencerType.clear()
        self.hardware.setEnabled(False)
        self.base.setEnabled(False)
        self.target.setEnabled(False)
        self.sequencerType.setEnabled(False)
        self.temperature.setEnabled(False)
        self.sample.setEnabled(False)
        self.parametersInput.setEnabled(False)
        self.parametersOutput.setEnabled(False)
        self.availableTests.clear()
        self.availableTests.setEnabled(False)
        self.moveTestUp.setEnabled(False)
        self.moveTestDown.setEnabled(False)
        self.testAdd.setEnabled(False)
        self.testRemove.setEnabled(False)
        self.binning_tree.setEnabled(False)
        self.user_name.setEnabled(False)

    @staticmethod
    def setup_view(dialog: TestProgramWizard, name: str):
        configuration = dialog.project_info.get_program_configuration_for_owner(dialog.owner, name)
        dialog._custom_parameter_handler.set_test_num_ranges(configuration['test_ranges'])
        # TODO: can we edit any of the following property
        dialog.hardware.clear()
        dialog.base.clear()
        dialog.target.clear()
        dialog.hardware.setEnabled(False)
        dialog.base.setEnabled(False)
        dialog.target.setEnabled(False)
        dialog.user_name.setEnabled(False)
        dialog.sequencerType.setEnabled(False)

        dialog.hardware.addItem(configuration['hardware'])
        dialog.base.addItem(configuration['base'])
        dialog.target.addItem(configuration['target'])
        dialog.cacheType.setCurrentText(configuration['cache_type'])
        dialog.user_name.setText(configuration['usertext'])

        dialog._custom_parameter_handler.import_tests_parameters(dialog.project_info.get_program_test_configuration(name, dialog.owner))
        dialog._update_selected_test_list()
        dialog._load_bin_table(os.path.join(dialog.project_info.project_directory,
                                            'src',
                                            dialog.hardware.currentText(),
                                            dialog.base.currentText(),
                                            f'{name}_binning.json'))
        dialog._populate_binning_tree()
        caching_policy = configuration['caching_policy']
        # cacheDisable is checked by default, we just check
        # the others, if they apply.
        if caching_policy == "store":
            dialog.cacheStore.setChecked(True)
        elif caching_policy == "drop":
            dialog.cacheDrop.setChecked(True)

        dialog.sequencerType.blockSignals(True)
        dialog.sequencerType.clear()
        dialog.sequencerType.addItem(configuration['sequencer_type'])
        dialog.sequencerType.blockSignals(False)

        dialog.temperature.setText(configuration['temperature'])

        dialog._verify()

    def _save_configuration(self):
        self.accept()


def view_program_dialog(name, project_info, owner, parent):
    testProgramWizard = ViewTestProgramWizard(name, project_info, owner, parent)
    testProgramWizard.exec_()
    del(testProgramWizard)
