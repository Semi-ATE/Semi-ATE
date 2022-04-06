import qtawesome as qta

from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes


ACTIONS = {MenuActionTypes.Edit(): (qta.icon('mdi.lead-pencil', color='orange'), "Edit"),
           MenuActionTypes.Add(): (qta.icon('mdi.plus', color='orange'), "New"),
           MenuActionTypes.AddFile(): (qta.icon('mdi.file-plus', color='orange'), "File"),
           MenuActionTypes.AddFolder(): (qta.icon('mdi.folder-plus', color='orange'), "Folder"),
           MenuActionTypes.View(): (qta.icon('mdi.eye-outline', color='orange'), "View"),
           MenuActionTypes.Delete(): (qta.icon('mdi.minus', color='orange'), "Delete"),
           MenuActionTypes.Import(): (qta.icon('mdi.application-import', color='orange'), "Import"),
           MenuActionTypes.ImportFile(): (qta.icon('mdi.file-import', color='orange'), "File"),
           MenuActionTypes.ImportFolder(): (qta.icon('mdi.folder-download', color='orange'), "Folder"),
           MenuActionTypes.Activate(): (qta.icon('mdi.check', color='orange'), "Select Hardware"),
           MenuActionTypes.CloneTo(): (qta.icon('mdi.application-export', color='orange'), "Clone to ..."),
           MenuActionTypes.CloneFrom(): (qta.icon('mdi.application-import', color='orange'), "Clone from ..."),
           MenuActionTypes.Trace(): (qta.icon('mdi.share-variant', color='orange'), "Trace usage"),
           MenuActionTypes.AddStandardTest(): (qta.icon('mdi.plus-box-outline', color='orange'), "Add Standard Test"),
           MenuActionTypes.Rename(): (qta.icon('mdi.file-edit', color='orange'), "Rename"),
           MenuActionTypes.Move(): (qta.icon('mdi.file-move', color='orange'), "Move"),
           MenuActionTypes.DeleteFile(): (qta.icon('mdi.file-remove', color='orange'), "Remove"),
           MenuActionTypes.Obsolete(): (qta.icon('mdi.block-helper', color='orange'), "Obsolete"),
           MenuActionTypes.Enable(): (qta.icon('mdi.check', color='orange'), "Activate"),
           MenuActionTypes.MoveUp(): (qta.icon('mdi.arrow-up-bold-box', color='orange'), "Move Up"),
           MenuActionTypes.MoveDown(): (qta.icon('mdi.arrow-down-bold-box', color='orange'), "Move Down"),
           MenuActionTypes.OpenFile(): (qta.icon('mdi.book-open', color='orange'), "Open"),
           MenuActionTypes.AddTestprogram(): (qta.icon('mdi.plus', color='orange'), "New Testprogram"),
           MenuActionTypes.UseCustomImplementation(): (qta.icon('mdi.file-move', color='orange'), "Use Custom Implementation"),
           MenuActionTypes.UseDefaultImplementation(): (qta.icon('mdi.file-replace', color='orange'), "Use Default Implementation"),
           MenuActionTypes.Select(): (qta.icon('mdi.check', color='orange'), "Select Target"),
           MenuActionTypes.CopyPath(): (qta.icon('mdi.content-copy', color='orange'), "Copy Absolute Path"),
           MenuActionTypes.AddGroup(): (qta.icon('mdi.folder-plus', color='orange'), "Add New Group"),
           MenuActionTypes.Export(): (qta.icon('mdi.application-export', color='orange'), "Export")}
