# Flask application written in Pythin 3.12 on March 2024, By Hire Intelligence International Limited.

# Developer : Mehdi Singer, Technician.


# importing necessary modules for flask app to run.
import datetime
from flask import Flask, render_template, redirect, url_for, flash, current_app, request, send_file, send_from_directory
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from forms import (RegisterForm, LoginForm, ScanForm, AssignForm, RenameUpdateForm, AddForm, SearchForm, ShowDB,
                   ReturnedForm, ExportForm)
import pandas as pd
import os

# path to the md.csv to populate the database with ipad information, asset id and serial number.
file_path = r"\\192.168.16.16\MAC\mdAssetList.csv"

# initiating the flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# user loader decorator for flask app
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


# creating database in instance folder in application man folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MD.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES to store all ipad information
class ModDem(db.Model):
    __tablename__ = "ModDem"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    serial_number: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    udid: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    asset_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    cover_tag: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    technician: Mapped[str] = mapped_column(String, nullable=True)
    time_scanned: Mapped[str] = mapped_column(String, nullable=True)
    owner: Mapped[str] = mapped_column(String, nullable=True)
    returned: Mapped[str] = mapped_column(String, nullable=True)


# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100), unique=True)


# creating all databases if not existing
with app.app_context():
    db.create_all()

asset_list = []
# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Check if user email is already present in the database.
            result = db.session.execute(db.select(User).where(User.name == form.name.data))
            user = result.scalar()
            if user:
                # User already exists
                flash("You've already signed up with that name, log in instead!", "success")
                return redirect(url_for('login'))

            # hashing the password for the user to store as a hash not plain text
            hash_and_salted_password = generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            # creating new user on database
            new_user = User(
                name=form.name.data.lower(),
                password=hash_and_salted_password,
            )
            db.session.add(new_user)
            db.session.commit()
            # This line will authenticate the user with Flask-Login
            login_user(new_user)
            return redirect(url_for("get_all_assets"))
        except:
            # Handle any IntegrityError exceptions (e.g., duplicate entry)
            db.session.rollback()
            flash("User already exists. Please try different name.", "error")
            return redirect(url_for('register'))
    return render_template("register.html", form=form, current_user=current_user)


# login route to allow user to login
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.name == form.name.data.lower()))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("That name does not exist, please try again.", "error")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', "error")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_assets'))

    return render_template("login.html", form=form, current_user=current_user)


# log out user when they are finished with the work
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_assets'))


# landing page / home page
@app.route('/', methods=["GET", "POST"])
def get_all_assets():
    global asset_list
    asset_list = []
    form = ShowDB()
    export_form = ExportForm()
    result = db.session.execute(db.select(ModDem))
    assets = result.scalars().all()
    if export_form.validate_on_submit() and export_form.form_type.data == "export":
        print("export")
        all_records = ModDem.query.all()

        # Convert the queried records into a pandas DataFrame
        data = {
            "Serial Number": [],
            "UDID": [],
            "Asset ID": [],
            "Cover Tag": [],
            "Location": [],
            "Technician": [],
            "Time Scanned": [],
            "Owner": [],
            "Returned": []
        }
        for record in all_records:
            data["Serial Number"].append(record.serial_number)
            data["UDID"].append(record.udid)
            data["Asset ID"].append(record.asset_id)
            data["Cover Tag"].append(record.cover_tag)
            data["Location"].append(record.location)
            data["Technician"].append(record.technician)
            data["Time Scanned"].append(record.time_scanned)
            data["Owner"].append(record.owner)
            data["Returned"].append(record.returned)

        df = pd.DataFrame(data)

        # Export the DataFrame to a CSV file
        csv_filename = "ModDem_records.csv"
        csv_path = os.path.join(os.path.dirname(__file__), csv_filename)
        df.to_csv(csv_path, index=False)
        return redirect(url_for("get_all_assets"))
    if form.validate_on_submit() and form.form_type.data == "db":
        print("form")
        print(form.form_type.data)
        return redirect(url_for("show_db"))

    return render_template("index.html", all_assets=assets, current_user=current_user, form=form,
                           export_form=export_form, form_type="export", db_form_type="db")


# scanning devices to add cover tag to database acording to asset ID
@app.route("/add_new_asset", methods=["GET", "POST"])
def add_new_asset():
    form = ScanForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(ModDem).where(ModDem.asset_id == form.asset_id.data))
        asset = result.scalar()

        if asset is not None:  # meaning asset exist and can be manipulated
            if asset.cover_tag is None:  # check to make sure cover tag is empty
                try:  # trying to assign cover tag to scanned tag
                    asset.cover_tag = form.cover_tag.data
                    asset.technician = current_user.name
                    asset.time_scanned = datetime.datetime.now()
                    db.session.commit()
                    flash("Asset updated successfully!")
                    return redirect(url_for("add_new_asset"))
                except Exception as e:  # if there was a problem adding the cover tag, it will flash a failed message
                    flash("There was a problem assigning the tag. Please contact the admin.", "error")
                    return redirect(url_for('add_new_asset'))
            else:  # if the asset already has a cover assigned to it , it will flash a message.
                flash("Asset already have a cover assigned to it. Please make sure it exists.", "error")
                return redirect(url_for('add_new_asset'))
        else:  # if the asset is not in the list, check spelling or add manually.
            flash("Asset ID not found. Please make sure it exists.", "error")
            return redirect(url_for('add_new_asset'))

    return render_template("add-asset.html", form=form, current_user=current_user)


# Route to assign the assets to location.
@app.route("/assign_asset", methods=["GET", "POST"])
def assign_asset():
    print(asset_list)
    form = AssignForm()
    cover_form = ReturnedForm()
    if request.method == "POST" and "custom_action" in request.form:
        print("yup")
    if cover_form.validate_on_submit():
        asset_list.append(cover_form.cover_tag.data)
        print(asset_list)
    else:
        if request.method == "POST" and "custom_action" in request.form:
            print("yup")
        if form.validate_on_submit():
            # an empty list for email and identifier to be converted to Miradore
            # template for upload to users list of devices.
            data = {
                "Email": [],
                "Identifier": []
            }
            # for all the device ranges , assign the cover number to a user
            # takes cover tag, with that info, takes serial number and created a csv file for that location

            for i in asset_list.copy():

                result = db.session.execute(db.select(ModDem).where(ModDem.cover_tag == i))
                asset = result.scalar()
                asset.location = form.location.data
                db.session.commit()
                serial_number = asset.serial_number
                data["Email"].append(form.location.data)
                data["Identifier"].append(serial_number)
                print(data)
                print(asset_list)
                asset_list.remove(i)
                print(asset_list)
            df = pd.DataFrame(data)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Specify the relative path to your files directory
            folder_path = os.path.join(base_dir, 'locations')
            # Access the form field correctly: form.location.data
            filename = f"{form.location.data}.csv"
            path = os.path.join(folder_path, filename)
            df.to_csv(path, index=False)
            return redirect(url_for("assign_asset"))

    if request.method == "POST" and "custom_action" in request.form:
        print("yup")

        # Get the current working directory of your Flask app
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Specify the relative path to your files directory
    folder_path = os.path.join(base_dir, 'locations')

    # Get a list of all files in the folder
    files = os.listdir(folder_path)

    return render_template("assign_asset.html", cover_form=cover_form, form=form,
                           current_user=current_user, files=files)


# to manually add a device to the database
@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        new_device = ModDem(
            asset_id=form.asset_id.data,
            serial_number=form.serial_number.data,
        )
        db.session.add(new_device)
        db.session.commit()
        flash("Device added successfully", "success")
        return redirect(url_for("add_new_asset"))
    return render_template("add.html", form=form)


# adds the md.csv file on nas/MAC folder to the database. make sure the database is empty before adding devices
# or make sure there is no duplication or it will fail.


@app.route("/populate")
def populate():
    csv_data = pd.read_csv(file_path)

    for index, row in csv_data.iterrows():
        # Extract serial number and asset tag from CSV
        sn = row["serial number"]
        asset_id = row["asset tag"]
        owner = row["owner"]

        # Check if asset_id already exists in the database
        existing_device = ModDem.query.filter_by(asset_id=asset_id).first()

        if existing_device:
            # Asset ID already exists, handle accordingly
            print(f"Asset ID {asset_id} already exists in the database.")
            # You can choose to skip, update, or handle the duplicate in another way
            continue

        # Asset ID doesn't exist, create a new device
        if len(sn) == 11:
            serial_number = sn[1:]
        else:
            serial_number = sn

        # Create and add new device to the database
        new_device = ModDem(serial_number=serial_number, asset_id=asset_id, owner=owner)

        # Add to the session and commit
        db.session.add(new_device)
        try:
            db.session.commit()
        except:
            # Handle any IntegrityError exceptions (e.g., if another process added the same asset_id concurrently)
            db.session.rollback()
            print(f"Error adding device with asset ID {asset_id}")

    return "Data population complete."


# deleted all data on the asset database, no warning.


@app.route("/delete_all")
def empty_database():
    entries_to_delete = db.session.query(ModDem).all()

    # Iterate over the query result and delete each entry
    for entry in entries_to_delete:
        db.session.delete(entry)

    # Commit the changes to persist the deletions
    db.session.commit()

    return redirect(url_for("get_all_assets"))


# takes a csv file containing udid and serial number and updates the database according to serial number with udid
@app.route("/rename_export", methods=["GET", "POST"])
def rename_export():
    form = RenameUpdateForm()
    if form.validate_on_submit():
        file = form.file.data  # Get the uploaded file
        if file:
            filename = secure_filename(file.filename)
            file_path2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            file.save(file_path2)
            flash('File uploaded successfully!', 'success')
            # Now you can process the file or perform any further actions

        else:
            flash('No file selected!', 'error')

        df = pd.read_csv(file_path2)
        print(df.head())
        for index, row in df.iterrows():
            result = db.session.execute(db.select(ModDem).where(ModDem.serial_number == row["Serial Number"]))
            asset = result.scalar()
            print(asset)
            if asset:
                asset.udid = row["UDID"]
                db.session.commit()
            else:
                flash(f'Asset with serial number {row["Serial Number"]} not found!', 'error')

    return render_template("rename.html", form=form)


# thgis allows the download of the csv files created with location name adn assets assigned to it.
@app.route('/download/<path:filename>')
def download_file(filename):
    folder_path = 'locations'  # Adjust the folder path as per your directory structure
    return send_from_directory(folder_path, filename, as_attachment=True)


# shows all the assets in the database regardless of their status in the process.
@app.route("/show_db")
def show_db():
    result = db.session.execute(db.select(ModDem))
    assets = result.scalars().all()

    table_headers = ['ID', 'Cover Tag', 'Asset Tag', 'Serial Number', 'Location', 'UDID', 'Technician', 'Time']
    return render_template("show_db.html", all_assets=assets, current_user=current_user, table_headers=table_headers)


@app.route("/returned", methods=["GET", "POST"])
def returned():
    form = ReturnedForm()
    if form.validate_on_submit():
        try:
            result = db.session.execute(db.select(ModDem).where(ModDem.cover_tag == form.cover_tag.data))
            asset = result.scalar()
            asset.returned = datetime.datetime.now()
            db.session.commit()
            flash("Saved Successfully")
            return redirect(url_for("returned"))
        except:
            flash("Asset not found!!!")
    return render_template("return.html", form=form)


@app.route("/edit/<int:asset_id>", methods=["GET", "POST"])
def edit(asset_id):
    asset = db.get_or_404(ModDem, asset_id)
    edit_form = ScanForm(
        asset_id=asset.asset_id,
        cover_tag=asset.cover_tag
    )
    if edit_form.validate_on_submit():
        asset.asset_id = edit_form.asset_id.data
        asset.cover_tag = edit_form.cover_tag.data
        db.session.commit()
        return redirect(url_for("get_all_assets", asset_id=asset.id))
    return render_template("edit.html", form=edit_form, is_edit=True, current_user=current_user)




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
