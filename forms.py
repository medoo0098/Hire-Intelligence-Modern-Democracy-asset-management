from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, FileField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired


# Create a form to register new users
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


# Create a form to login existing users
class LoginForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


# Create a form for scanning existing items asset ID and assign cover to them
class ScanForm(FlaskForm):
    asset_id = StringField("Scan Asset ID", validators=[DataRequired()])
    cover_tag = StringField("Scan Cover TAG", validators=[DataRequired()])
    submit = SubmitField("Save Scan")


# Create a form that assigns iPads to locations
class AssignForm(FlaskForm):
    location = StringField("Enter Location Email", validators=[DataRequired()])
    # cover_tag = IntegerField("Scan cover Tag ", validators=[DataRequired()])
    # end_number = IntegerField("Enter last iPad Cover tag in the bunch ", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Creates a form to upload the CSV file to record UDID according to Serial Number
class RenameUpdateForm(FlaskForm):
    file = FileField(validators=[FileRequired(), FileAllowed(["csv"], "CSV file only")])
    submit = SubmitField("Upload")


# Creates a form to manually add an ipad to list of devices.
class AddForm(FlaskForm):
    asset_id = StringField("Scan Device Asset ID or enter Manually", validators=[DataRequired()])
    serial_number = StringField("Enter Serial Number", validators=[DataRequired()])
    submit = SubmitField("Add")


# Define a search form using Flask-WTF
class SearchForm(FlaskForm):
    search_query = StringField('Search Query')
    submit = SubmitField('Search')


class ShowDB(FlaskForm):
    submit = SubmitField("Show DB")


class ReturnedForm(FlaskForm):
    cover_tag = StringField("Scan Cover Tags",validators=[DataRequired()])
    submit = SubmitField("Save")



