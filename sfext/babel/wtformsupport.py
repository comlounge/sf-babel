"""

Support file for providing i18n to wtforms.

In theory this is already present but we need to make it aware of our 
retrieval of language data.

"""

from wtforms import Form

class I18nForm(Form):
    """base class for forms supporting sf-babel based i18n"""

    def __init__(self, formdata=None, obj=None, prefix='', handler = None, *args, **kwargs):                                
        """initialize the form with the handler which we use to check for the
        correct language"""

        self.handler = handler
        super(I18nForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
