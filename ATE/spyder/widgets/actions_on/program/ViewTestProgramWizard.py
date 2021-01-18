from ATE.spyder.widgets.actions_on.program.TestProgramWizard import TestProgramWizard


class ViewTestProgramWizard(TestProgramWizard):
    def __init__(self, name, project_info, owner):
        super().__init__(project_info, owner, read_only=True, enable_edit=False)
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
        self.usertext.setEnabled(False)
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

    @staticmethod
    def setup_view(dialog, name):
        dialog._custom_parameter_handler.import_tests_parameters(dialog.project_info.get_program_test_configuration(name, dialog.owner))
        dialog._update_selected_test_list()
        dialog._populate_binning_tree()
        configuration = dialog.project_info.get_program_configuration_for_owner(dialog.owner, name)
        # TODO: can we edit any of the following property
        dialog.hardware.clear()
        dialog.base.clear()
        dialog.target.clear()
        dialog.hardware.setEnabled(False)
        dialog.base.setEnabled(False)
        dialog.target.setEnabled(False)
        dialog.sequencerType.setEnabled(False)

        dialog.hardware.addItem(configuration['hardware'])
        dialog.base.addItem(configuration['base'])
        dialog.target.addItem(configuration['target'])
        dialog.usertext.setText(configuration['usertext'])
        dialog.cacheType.setCurrentText(configuration['cache_type'])

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


def view_program_dialog(name, project_info, owner):
    testProgramWizard = ViewTestProgramWizard(name, project_info, owner)
    testProgramWizard.exec_()
    del(testProgramWizard)
