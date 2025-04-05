from flask_wtf import FlaskForm
from DBManager import DBManager
from wtforms.fields import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.widgets import TextArea

#Make a form with flask WTF
class Forms():
    def __init__(self, dbmanager):
        self.dbmanager = dbmanager

    def buildLoginForm(self):
        class Login(FlaskForm):
            password = PasswordField('Password', default="")
            submit = SubmitField('Login')
        return Login()

    def buildAnnouncementForm(self):
        class Login(FlaskForm):
            title = StringField('Title', default="")
            content = TextAreaField('Content', default="")
            submit = SubmitField('Post Announcement')
        return Login()

    def buildClipEdit(self, clipid):
        class ClipEdit(FlaskForm):
            clipinfo = self.dbmanager.getclip(clipid)
            name = StringField('Clip name', default=clipinfo[1])
            streamname = StringField('Stream name', default=clipinfo[2])
            submit = SubmitField('Edit')
        return ClipEdit()