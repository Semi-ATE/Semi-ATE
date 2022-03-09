from enum import Enum


class MenuActionTypes(Enum):
    Add = "new_item"
    Edit = "edit_item"
    View = "display_item"
    Delete = "delete_item"
    Import = "import_item"
    Activate = "activate_item"
    Enable = "enable_item"
    CloneTo = "clone_to_item"
    CloneFrom = "clone_from_item"
    Trace = "trace_item"
    AddStandardTest = "add_standard_test_item"
    Rename = "rename_item"
    Move = "move_item"
    AddFile = "add_file__item"
    AddFolder = "add_folder_item"
    DeleteFile = "delete_item"
    ImportFile = "import_file_item"
    ImportFolder = "import_dir_item"
    Obsolete = "disable_item"
    MoveUp = "move_up_item"
    MoveDown = "move_down_item"
    OpenFile = "open_file_item"
    AddTestprogram = "add_testprogram"
    UseCustomImplementation = "use_custom_implementation"
    UseDefaultImplementation = "use_default_implementation"
    Select = "select_target_item"
    CopyPath = "copy_absolute_path"
    AddGroup = "add_test_group"
    Export = "export_item"

    def __call__(self):
        return self.value
