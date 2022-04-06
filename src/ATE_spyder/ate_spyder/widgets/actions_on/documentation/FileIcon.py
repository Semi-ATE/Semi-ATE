from ate_spyder.widgets.actions_on.documentation.Constants import FileIconTypes
import qtawesome as qta


FileIcons = {FileIconTypes.PDF.name: qta.icon('mdi.file-pdf-outline', color='orange'),
             FileIconTypes.DOC.name: qta.icon('mdi.file-word-outline', color='orange'),
             FileIconTypes.XLS.name: qta.icon('mdi.file-excel-outline', color='orange'),
             FileIconTypes.PPT.name: qta.icon('mdi.file-powerpoint-outline', color='orange'),
             FileIconTypes.TEX.name: qta.icon('mdi.file-outline', 'mdi.alpha-x', color='orange'),
             FileIconTypes.ODF.name: qta.icon('mdi.file-outline', 'mdi.exponent', color='orange'),
             FileIconTypes.ODG.name: qta.icon('mdi.file-outline', 'mdi.draw', color='orange'),
             FileIconTypes.HTML.name: qta.icon('mdi.file-link-outline', color='orange'),
             FileIconTypes.PNG.name: qta.icon('mdi.file-image-outline', color='orange'),
             FileIconTypes.AVI.name: qta.icon('mdi.file-video-outline', color='orange'),
             FileIconTypes.FLAC.name: qta.icon('mdi.file-music-outline', color='orange'),
             FileIconTypes.TXT.name: qta.icon('mdi.note-text-outline', color='orange'),
             FileIconTypes.MD.name: qta.icon('mdi.file-outline', 'mdi.markdown', color='orange'),
             FileIconTypes.ZIP.name: qta.icon('mdi.folder-zip-outline', color='orange'),
             FileIconTypes.PY.name: qta.icon('mdi.language-python', color='orange'),
             FileIconTypes.FOLDER.name: qta.icon('mdi.folder-open', color='orange'),
             FileIconTypes.VIRTUAL.name: qta.icon('mdi.standard-definition', color='orange')}
