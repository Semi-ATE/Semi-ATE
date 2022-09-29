from typing import List

from ate_spyder.widgets.actions_on.documentation.BaseFolderStructureItem import BaseFolderStructureItem
from ate_spyder.widgets.navigation import ProjectNavigation


class DocumentationItem(BaseFolderStructureItem):
    '''
    DocumentationItem is the presentation of a folder
    '''
    def __init__(self, name: str, path: str, project_info: ProjectNavigation, parent: object=None, is_editable: bool=True, is_parent_node: bool=True):
        super().__init__(name, path, project_info, parent, is_editable, is_parent_node)

    def _do_not_edit_list(self) -> List[str]:
        return ['audits', 'exports']
