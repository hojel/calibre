# -*- coding: utf-8 -*-

__license__ = 'GPL 3'
__copyright__ = '2009, John Schember <john@nachtimwald.com>'
__docformat__ = 'restructuredtext en'

from calibre.gui2.convert.pdf_input_ui import Ui_Form
from calibre.gui2.convert import Widget, QDoubleSpinBox

class PluginWidget(Widget, Ui_Form):

    TITLE = _('PDF Input')
    HELP = _('Options specific to')+' PDF '+_('input')
    COMMIT_NAME = 'pdf_input'
    ICON = I('mimetypes/pdf.png')

    def __init__(self, parent, get_option, get_help, db=None, book_id=None):
        Widget.__init__(self, parent,
            ['no_images', 'unwrap_factor'])
        self.db, self.book_id = db, book_id
        self.initialize_options(get_option, get_help, db, book_id)

    def set_value_handler(self, g, val):
        if val is None and isinstance(g, QDoubleSpinBox):
            g.setValue(0.0)
            return True
