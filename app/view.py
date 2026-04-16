from datetime import datetime

from flask import json, request
from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy.orm import joinedload
from wtforms import DateField, DecimalField, FileField, FloatField, HiddenField, IntegerField, SelectField, SelectMultipleField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, TimeField, ValidationError
from wtforms.validators import URL, DataRequired, Email, EqualTo, InputRequired, Length, NumberRange, Optional, Regexp
from app.modal import AcademicYear, Branch, Class, ClassLevel, Exam, ExamSubject, ExamTimetable, Parent, School, Section, Student, StudentFeeCollection, Subject, Teacher, TeacherAssignment, Term, TimeSlot, UserRole
from flask_wtf.file import FileField, FileAllowed

from app.utils import get_academic_year


class RegisterForm(FlaskForm):
    fullname = StringField("Full Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    receiveMail = BooleanField("Receive Emails", validators=[DataRequired()])
    termsCondition = BooleanField("Terms & Conditions", validators=[DataRequired()])
    submit = SubmitField("Create Account")

# 
class LoginForm(FlaskForm):
    login_id = StringField('Login ID', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[DataRequired(message="Email is required."), Email(message="Invalid email address.")]
    )
    submit = SubmitField("Send OTP")

class VerifyOTPForm(FlaskForm):
    otp_code = StringField(
        'OTP Code',
        validators=[
            DataRequired(message="Please enter the OTP."),
            Length(min=6, max=6, message="OTP must be 6 digits.")
        ]
    )
    submit = SubmitField("Validate")

class ForgotPasswordChangeForm(FlaskForm):
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message="New password is required."),
            Length(min=8, message="Password must be at least 8 characters long.")
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo('new_password', message='Passwords must match.')
        ]
    )
    submit = SubmitField('Save Changes')


#schpool
class SchoolForm(FlaskForm):
    name = StringField("School Name", validators=[DataRequired(), Length(max=150)])
    title = StringField("School Title", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=30)])
    status = SelectField("Status", choices=[('active','Active'),('inactive','Inactive'),('suspended','Suspended')], default='active')
    submit = SubmitField("Submit")

# branches
class BranchForm(FlaskForm):
    school_id = SelectField("School", coerce=int, validators=[DataRequired()])
    name = StringField("Branch Name", validators=[DataRequired(), Length(max=150)])
    title = StringField("Branch Title", validators=[DataRequired(), Length(max=150)])
    address = TextAreaField("Address", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=30)])
    status = SelectField("Status", choices=[('active','Active'),('inactive','Inactive'),('suspended','Suspended')], default='active')
    submit = SubmitField("Submit")



# Users
class UserForm(FlaskForm):
    # Required fields
    fullname = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    username = StringField("Username", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo('password', message="Passwords must match")]
    )

    # Optional info
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    country = SelectField("Country", choices=[], coerce=str)  # populate dynamically
    state = StringField("State", validators=[Optional(), Length(max=255)])
    city = StringField("City", validators=[Optional(), Length(max=255)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=255)])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
    gender = SelectField(
        "Gender",
        choices=[('', 'Select Gender'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        validators=[Optional()]
    )
    photo_visibility = SelectField(
        "Photo Visibility",
        choices=[('everyone', 'Everyone'), ('private', 'Private')],
        default='everyone'
    )

    # School & Branch
    school_id = SelectField("School", coerce=int, choices=[], validators=[Optional()])  # populate dynamically
    branch_id = SelectField("Branch", coerce=int, choices=[], validators=[Optional()])  # populate dynamically

    # Role & Status
    role = SelectField(
        "Role",
        choices=[(role.value, role.name.replace("_", " ").title()) for role in UserRole],
        validators=[DataRequired()]
    )
    status = SelectField(
        "Status",
        choices=[('1', 'Active'), ('0', 'Inactive')],
        default='1',
        validators=[DataRequired()]
    )

    # Security & verification
    is_verified = BooleanField("Verified")
    two_factor_enabled = BooleanField("Enable Two-Factor Authentication")
    phone_verified = BooleanField("Phone Verified")

    # Social links
    facebook = StringField("Facebook", validators=[Optional(), Length(max=255)])
    twitter = StringField("Twitter", validators=[Optional(), Length(max=255)])
    google = StringField("Google", validators=[Optional(), Length(max=255)])
    whatsapp = StringField("Whatsapp", validators=[Optional(), Length(max=255)])
    instagram = StringField("Instagram", validators=[Optional(), Length(max=255)])
    github = StringField("Github", validators=[Optional(), Length(max=255)])
    github_id = StringField("Github ID", validators=[Optional(), Length(max=100)])

    submit = SubmitField("Create User")

# Manage User Profile Form
class UserProfileForm(FlaskForm):
    # Basic Info
    fullname = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    username = StringField("Username", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField("Password", validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[Optional(), EqualTo('password', message="Passwords must match")]
    )

    # Optional info
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    country = SelectField("Country", choices=[], coerce=str)  # populate dynamically
    state = StringField("State", validators=[Optional(), Length(max=255)])
    city = StringField("City", validators=[Optional(), Length(max=255)])
    address = TextAreaField("Address", validators=[Optional(), Length(max=255)])
    bio = TextAreaField("Bio", validators=[Optional(), Length(max=500)])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])

    dob = DateField("Date of Birth", format='%Y-%m-%d', validators=[Optional()])
    pob = StringField("Place of Birth", validators=[Optional(), Length(max=255)])
    photo_visibility = SelectField(
        "Photo Visibility",
        choices=[('everyone', 'Visible to Everyone'), ('only_me', 'Visible Only to Me')],
        default='everyone'
    )


    # School & Branch (optional)
    school_id = SelectField("School", coerce=int, choices=[], validators=[Optional()])
    branch_id = SelectField("Branch", coerce=int, choices=[], validators=[Optional()])

    # Role & Status (for admins only)
    role = SelectField(
        "Role",
        choices=[],  # populate dynamically with UserRole
        validators=[Optional()]
    )
    status = SelectField(
        "Status",
        choices=[('1', 'Active'), ('0', 'Inactive')],
        default='1',
        validators=[Optional()]
    )

    # Security & verification
    is_verified = BooleanField("Verified")
    two_factor_enabled = BooleanField("Enable Two-Factor Authentication")
    phone_verified = BooleanField("Phone Verified")

    # Social links
    facebook = StringField("Facebook", validators=[Optional(), Length(max=255)])
    twitter = StringField("Twitter", validators=[Optional(), Length(max=255)])
    google = StringField("Google", validators=[Optional(), Length(max=255)])
    whatsapp = StringField("Whatsapp", validators=[Optional(), Length(max=255)])
    instagram = StringField("Instagram", validators=[Optional(), Length(max=255)])
    linkedin = StringField("LinkedIn", validators=[Optional(), Length(max=255)])
    skype = StringField("Skype", validators=[Optional(), Length(max=255)])
    github = StringField("Github", validators=[Optional(), Length(max=255)])
    github_id = StringField("Github ID", validators=[Optional(), Length(max=100)])

    # Profile photo
    profile_photo = FileField("Profile Photo", validators=[Optional()])

    submit = SubmitField("Update Profile")

# Manage Change Password Form
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired(message="Current password is required.")]
    )
    
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(message="New password is required."),
            Length(min=8, message="Password must be at least 8 characters long."),
            Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
                message="Password must include uppercase, lowercase, number, and special character."
            )
        ]
    )
    
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(message="Please confirm your new password."),
            EqualTo('new_password', message="Passwords must match.")
        ]
    )
    
    submit = SubmitField("Change Password")

# Two Factor Form
class TwoFactorForm(FlaskForm):
    two_factor_enabled = BooleanField("Enable Two-Factor Authentication")
    two_factor_code = StringField(
        "Two-Factor Code",
        validators=[
            DataRequired(message="OTP code is required."),
            Length(min=6, max=256),
            Regexp(r'^\d{6}$', message="OTP must be 6 digits.")
        ]
    )
    submit = SubmitField("Save 2FA Settings")

# somali locations
class SomaliaLocationForm(FlaskForm):
    region = StringField(
        "Region",
        validators=[DataRequired(), Length(max=100)]
    )
    district = StringField(
        "District",
        validators=[DataRequired(), Length(max=100)]
    )
    submit = SubmitField("Submit")

# School Site Settings      
class SchoolSiteSettingsForm(FlaskForm):
    # School selection
    school_id = SelectField(
        "School",
        coerce=int,
        validators=[DataRequired(message="Please select a school.")]
    )

    # Branch selection (optional)
    branch_id = SelectField(
        "Branch",
        coerce=int,
        validators=[Optional()]
    )

    # Site logos
    main_logo = FileField("Main Logo", validators=[Optional()])
    sub_logo = FileField("Sub Logo", validators=[Optional()])
    sign_logo = FileField("Sign Logo", validators=[Optional()])

    # Site info
    site_title = StringField(
        "Site Title",
        validators=[Optional(), Length(max=255)]
    )
    short_desc = TextAreaField("Short Description", validators=[Optional(), Length(max=500)])
    long_desc = TextAreaField("Long Description", validators=[Optional()])

    # Contact info
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    email = StringField("Email", validators=[Optional(), Length(max=100)])

    # Social links
    facebook = StringField("Facebook", validators=[Optional(), Length(max=255)])
    twitter = StringField("Twitter", validators=[Optional(), Length(max=255)])
    instagram = StringField("Instagram", validators=[Optional(), Length(max=255)])

    submit = SubmitField("Save Settings")

    # Populate school and branch dropdowns dynamically
    def set_choices(self):
        # Populate school dropdown
        self.school_id.choices = [(s.id, s.name) for s in School.query.order_by(School.name).all()]

        # Populate branch dropdown (all branches with default placeholder)
        branches = Branch.query.order_by(Branch.name).all()
        self.branch_id.choices = [(0, "Select Branch")] + [(b.id, b.name) for b in branches]

class SettingsDataForm(FlaskForm):

    # Basic info
    group_name = StringField(
        "Group Name",
        validators=[DataRequired(), Length(max=255)]
    )

    system_name = StringField(
        "System Name",
        validators=[Optional(), Length(max=255)]
    )

    address = StringField(
        "Address",
        validators=[DataRequired(), Length(max=255)]
    )

    # Descriptions
    short_desc = TextAreaField("Short Description", validators=[Optional()])
    long_desc = TextAreaField("Long Description", validators=[Optional()])
    success_desc = TextAreaField("Success Description", validators=[Optional()])

    # Images
    head_image = FileField("Header Image", validators=[Optional()])
    image_success = FileField("Success Image", validators=[Optional()])
    about_image = FileField("About Image", validators=[Optional()])

    # Video URL
    video_url = StringField(
        "Video URL",
        validators=[Optional(), URL()]
    )

    # Contact
    phone1 = StringField("Phone 1", validators=[DataRequired(), Length(max=15)])
    phone2 = StringField("Phone 2", validators=[Optional(), Length(max=15)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=100)])

    # Social media
    facebook = StringField("Facebook", validators=[Optional(), Length(max=255)])
    twitter = StringField("Twitter", validators=[Optional(), Length(max=255)])
    instagram = StringField("Instagram", validators=[Optional(), Length(max=255)])
    dribbble = StringField("Dribbble", validators=[Optional(), Length(max=255)])

    # Logos
    logo = FileField("Main Logo", validators=[Optional()])
    logo2 = FileField("Secondary Logo", validators=[Optional()])

    submit = SubmitField("Save Settings")

#---- class levels
class ClassLevelForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
    branch_id = SelectField('Branch', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # =========================
        # School admin
        # =========================
        if current_user.role.value == 'school_admin':
            self.school_id.choices = [(current_user.school_id, current_user.school.name)]
            self.school_id.data = current_user.school_id

            # Branch optional: all branches of school
            branches = Branch.query.filter_by(school_id=current_user.school_id).all()
            self.branch_id.choices = [('', '--- No Branch ---')] + [(b.id, b.name) for b in branches]
            self.branch_id.data = None  # branch-less by default

        # =========================
        # Branch admin
        # =========================
        elif current_user.role.value == 'branch_admin':
            self.school_id.choices = [(current_user.school_id, current_user.school.name)]
            self.school_id.data = current_user.school_id

            # Only their own branch
            self.branch_id.choices = [(current_user.branch_id, current_user.branch.name)]
            self.branch_id.data = current_user.branch_id


# Class
class ClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[Optional(), NumberRange(min=0)])
    
    school_id = SelectField('School', coerce=int)
    branch_id = SelectField(
        'Branch',
        coerce=lambda x: int(x) if x else None,
        validators=[Optional()]
    )
    level_id = SelectField('Class Level', coerce=int, validators=[DataRequired()])
    # ✅ NEW
    shift = SelectField(
        'Shift',
        choices=[('morning', 'Morning'), ('afternoon', 'Afternoon')],
        validators=[DataRequired()]
    )
    status = SelectField('Status', choices=[('active','Active'), ('inactive','Inactive')], default='active')
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ====================== SCHOOL ADMIN ======================
        if current_user.role.value == 'school_admin':
            # School fixed
            self.school_id.choices = [(current_user.school_id, current_user.school.name)]
            self.school_id.data = current_user.school_id

            # Branch optional
            branches = Branch.query.filter_by(school_id=current_user.school_id).all()
            self.branch_id.choices = [('', '--- No Branch ---')] + [(b.id, b.name) for b in branches]
            self.branch_id.data = None  # empty by default

            # Levels branch-less only
            levels = ClassLevel.query.filter_by(school_id=current_user.school_id, branch_id=None).order_by(ClassLevel.name).all()
            self.level_id.choices = [(l.id, l.name) for l in levels]

        # ====================== BRANCH ADMIN ======================
        elif current_user.role.value == 'branch_admin':
            # School fixed
            self.school_id.choices = [(current_user.school_id, current_user.school.name)]
            self.school_id.data = current_user.school_id

            # Branch fixed
            self.branch_id.choices = [(current_user.branch_id, current_user.branch.name)]
            self.branch_id.data = current_user.branch_id

            # Levels for this branch only
            levels = ClassLevel.query.filter_by(school_id=current_user.school_id, branch_id=current_user.branch_id).order_by(ClassLevel.name).all()
            self.level_id.choices = [(l.id, l.name) for l in levels]


# Sections
class SectionForm(FlaskForm):
    name = StringField('Section Name', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[Optional(), NumberRange(min=0)])

    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
    branch_id = SelectField('Branch', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])
    # ✅ NEW
     # Shift: will be auto-filled from class, readonly in template
    shift = StringField('Shift', render_kw={'readonly': True})
    status = SelectField(
        'Status',
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='active'
    )
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ====================== SCHOOL ADMIN ======================
        if current_user.is_authenticated and current_user.role.value == 'school_admin':
            # School fixed
            self.school_id.choices = [(current_user.school_id, current_user.school.name)]
            self.school_id.data = current_user.school_id

            # Branch optional
            branches = Branch.query.filter_by(school_id=current_user.school_id).all()
            self.branch_id.choices = [('', '--- No Branch ---')] + [(b.id, b.name) for b in branches]
            self.branch_id.data = None

            # Classes: only branch-less classes
            classes = Class.query.filter_by(school_id=current_user.school_id, branch_id=None, status='active').all()
            self.class_id.choices = [(c.id, c.name) for c in classes]

        # ====================== BRANCH ADMIN ======================
        elif current_user.is_authenticated and current_user.role.value == 'branch_admin':
            # School fixed
            self.school_id.choices = [(current_user.school_id, current_user.school.name)]
            self.school_id.data = current_user.school_id

            # Branch fixed
            self.branch_id.choices = [(current_user.branch_id, current_user.branch.name)]
            self.branch_id.data = current_user.branch_id

            # Classes: only branch classes
            classes = Class.query.filter_by(school_id=current_user.school_id, branch_id=current_user.branch_id, status='active').all()
            self.class_id.choices = [(c.id, c.name) for c in classes]

        else:
            # For super-admin or other roles: all schools, no branch filter
            schools = School.query.all()
            self.school_id.choices = [(s.id, s.name) for s in schools]
            self.school_id.data = None

            self.branch_id.choices = [('', '--- No Branch ---')]
            self.class_id.choices = []


# Subject Form
class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired()])
    code = StringField('Subject Code', validators=[DataRequired()])  # auto-generated

    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
    branch_id = SelectField('Branch', coerce=lambda x: int(x) if x else None, validators=[Optional()])

    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ====================== SCHOOL ADMIN ======================
        if current_user.role.value == 'school_admin':
            self.school_id.choices = [(current_user.school_id, current_user.school.name)]
            self.school_id.data = current_user.school_id

            branches = Branch.query.filter_by(school_id=current_user.school_id).all()
            self.branch_id.choices = [('', '--- No Branch ---')] + [(b.id, b.name) for b in branches]
            self.branch_id.data = None

        # ====================== BRANCH ADMIN ======================
        elif current_user.role.value == 'branch_admin':
            self.school_id.choices = [(current_user.school_id, current_user.school.name)]
            self.school_id.data = current_user.school_id

            self.branch_id.choices = [(current_user.branch_id, current_user.branch.name)]
            self.branch_id.data = current_user.branch_id

        # ====================== SUPERADMIN OR OTHERS ======================
        else:
            schools = School.query.all()
            self.school_id.choices = [(s.id, s.name) for s in schools]
            self.school_id.data = None

            self.branch_id.choices = [('', '--- No Branch ---')]
            self.branch_id.data = None


def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Schools
    self.school_id.choices = [(s.id, s.name) for s in School.query.all()]
    self.school_id.data = None

    # Branches empty initially
    self.branch_id.choices = [('', '--- No Branch ---')]
    self.branch_id.data = None

    # Classes empty initially
    self.class_id.choices = [('', '--- Select Class ---')]
    self.class_id.data = None

    # Levels
    self.level_id.choices = [(l.id, l.name) for l in ClassLevel.query.all()]

    # Sections empty initially
    self.section_id.choices = [('', '--- No Section ---')]
    self.section_id.data = None

    # Parents
    self.parent_id.choices = [('', '--- No Parent ---')] + [(p.id, p.full_name) for p in Parent.query.all()]

# Class Subject Form
class ClassSubjectForm(FlaskForm):
    class_ids = SelectMultipleField("Classes", coerce=int, validators=[DataRequired()])
    subject_ids = SelectMultipleField("Subjects", coerce=int, validators=[DataRequired()])
    school_id = HiddenField()
    branch_id = HiddenField()
    submit = SubmitField("Save Assignments")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if current_user.role.value == 'school_admin':
            # Classes branch-less only (school-level)
            classes = Class.query.filter_by(
                school_id=current_user.school_id,
                branch_id=None
            ).order_by(Class.name).all()
            self.class_ids.choices = [(c.id, c.name) for c in classes]

            # Subjects branch-less only (school-level)
            subjects = Subject.query.filter_by(
                school_id=current_user.school_id,
                branch_id=None
            ).order_by(Subject.name).all()
            self.subject_ids.choices = [(s.id, s.name) for s in subjects]

            self.school_id.data = current_user.school_id
            self.branch_id.data = None

        elif current_user.role.value == 'branch_admin':
            # Only branch classes
            classes = Class.query.filter_by(
                school_id=current_user.school_id,
                branch_id=current_user.branch_id
            ).order_by(Class.name).all()
            self.class_ids.choices = [(c.id, c.name) for c in classes]

            # Only branch subjects
            subjects = Subject.query.filter_by(
                school_id=current_user.school_id,
                branch_id=current_user.branch_id
            ).order_by(Subject.name).all()
            self.subject_ids.choices = [(s.id, s.name) for s in subjects]

            self.school_id.data = current_user.school_id
            self.branch_id.data = current_user.branch_id


# Parents
class ParentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=150)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=150)])
    phone = StringField('Phone', validators=[Optional(), Length(max=30)])

    password = PasswordField('Password', validators=[Optional(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[Optional(), EqualTo('password', message='Passwords must match')]
    )

    roll_no = StringField('Roll No', validators=[Optional(), Length(max=50)], render_kw={"readonly": True})
    gender = SelectField(
        'Gender',
        choices=[('', '--- Select Gender ---'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        validators=[Optional()]
    )
     # Profile photo
    profile_photo = FileField("Profile Photo", validators=[Optional()])

    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    occupation = StringField('Occupation', validators=[Optional(), Length(max=150)])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=30)])
    address = TextAreaField('Address', validators=[Optional()])
    national_id = StringField('National ID', validators=[Optional(), Length(max=100)])
    relationship = SelectField(
        'Relationship',
        choices=[('', '--- Select Relationship ---'), ('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian'), ('other', 'Other')],
        validators=[Optional()]
    )
    status = SelectField(
        'Status',
        choices=[('active', 'Active'), ('inactive', 'Inactive'), ('blocked', 'Blocked')],
        default='active'
    )

    # School and branch
    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
    branch_id = SelectField(
        'Branch',
        coerce=lambda x: int(x) if x else None,  # '' -> None
        validators=[Optional()]
    )

    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamic choices based on current user
        if current_user.is_authenticated:
            from app.modal import School, Branch  # adjust your import

            if current_user.role.value == 'school_admin':
                self.school_id.choices = [(current_user.school_id, current_user.school.name)]
                self.school_id.data = current_user.school_id

                branches = Branch.query.filter_by(school_id=current_user.school_id).all()
                self.branch_id.choices = [('', '--- No Branch ---')] + [(b.id, b.name) for b in branches]
                self.branch_id.data = None

            elif current_user.role.value == 'branch_admin':
                self.school_id.choices = [(current_user.school_id, current_user.school.name)]
                self.school_id.data = current_user.school_id

                self.branch_id.choices = [(current_user.branch_id, current_user.branch.name)]
                self.branch_id.data = current_user.branch_id

            else:
                schools = School.query.all()
                self.school_id.choices = [(s.id, s.name) for s in schools]
                self.school_id.data = None
                self.branch_id.choices = [('', '--- No Branch ---')]


# Students Form
class StudentForm(FlaskForm):
    # Basic Info
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=150)])
    gender = SelectField(
        'Gender',
        choices=[('', '--- Select Gender ---'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        validators=[Optional()]
    )
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    place_of_birth = StringField('Place of Birth', validators=[Optional(), Length(max=150)])
    photo = StringField('Photo', validators=[Optional(), Length(max=255)])

    # Academic
    academic_year = StringField('Academic Year', validators=[Optional(), Length(max=20)])
    roll_no = StringField('Roll No', validators=[Optional(), Length(max=50)])

    # Fees
    price = DecimalField('Tuition Fee', validators=[Optional()], places=2)
    registration_fee = DecimalField('Registration Fee', validators=[Optional()], places=2)

    # Status
    status = SelectField(
        'Status',
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('graduated', 'Graduated'),
            ('suspended', 'Suspended')
        ],
        default='active'
    )
     # ✅ NEW
    shift = SelectField(
        'Shift',
        choices=[('morning', 'Morning'), ('afternoon', 'Afternoon')],
        validators=[DataRequired()]
    )

    # Password
    password = PasswordField('Password', validators=[Optional(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[Optional(), EqualTo('password', message='Passwords must match')]
    )

    # Relationships
    parent_id = SelectField('Parent', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    school_id = SelectField('School', coerce=int, validators=[DataRequired()])
    branch_id = SelectField('Branch', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    class_id = SelectField('Class', coerce=lambda x: int(x) if x else None, validators=[Optional()])
    level_id = SelectField('Level', coerce=int, validators=[DataRequired()])
    section_id = SelectField('Section', coerce=lambda x: int(x) if x else None, validators=[Optional()])

    submit = SubmitField('Save')

    # -------------------------
    # Dynamic loading in __init__
    # -------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # -------------------------
        # Parents
        # -------------------------
        if current_user.is_authenticated:
            if current_user.role.value == 'school_admin':
                # Parents of the school with branch_id = NULL only
                parents = Parent.query.filter_by(school_id=current_user.school_id, branch_id=None).all()
                self.parent_id.choices = [('', '--- No Parent ---')] + [(p.id, p.full_name) for p in parents]

                # School fixed
                self.school_id.choices = [(current_user.school_id, current_user.school.name)]
                self.school_id.data = current_user.school_id

                # Branch optional (all branches)
                branches = Branch.query.filter_by(school_id=current_user.school_id).all()
                self.branch_id.choices = [('', '--- No Branch ---')] + [(b.id, b.name) for b in branches]
                self.branch_id.data = None

            elif current_user.role.value == 'branch_admin':
                # Parents only from this branch
                parents = Parent.query.filter_by(
                    school_id=current_user.school_id,
                    branch_id=current_user.branch_id
                ).all()
                self.parent_id.choices = [('', '--- No Parent ---')] + [(p.id, p.full_name) for p in parents]

                # School fixed
                self.school_id.choices = [(current_user.school_id, current_user.school.name)]
                self.school_id.data = current_user.school_id

                # Branch fixed
                self.branch_id.choices = [(current_user.branch_id, current_user.branch.name)]
                self.branch_id.data = current_user.branch_id

            else:
                # Other roles → all parents
                parents = Parent.query.all()
                self.parent_id.choices = [('', '--- No Parent ---')] + [(p.id, p.full_name) for p in parents]

                # All schools
                schools = School.query.all()
                self.school_id.choices = [(s.id, s.name) for s in schools]
                self.school_id.data = None
                self.branch_id.choices = [('', '--- No Branch ---')]

        # -------------------------
        # Levels (branch-aware)
        # -------------------------
        levels_query = ClassLevel.query.filter_by(school_id=current_user.school_id)
        if current_user.role.value == 'school_admin':
            # only branch-less levels
            levels_query = levels_query.filter_by(branch_id=None)
        elif current_user.role.value == 'branch_admin':
            # only levels for this branch
            levels_query = levels_query.filter_by(branch_id=current_user.branch_id)

        levels = levels_query.order_by(ClassLevel.name).all()
        self.level_id.choices = [(l.id, l.name) for l in levels]

        # -------------------------
        # Classes (branch-aware)
        # -------------------------
        classes_query = Class.query.filter_by(school_id=current_user.school_id, status='active')
        if current_user.role.value == 'school_admin':
            classes_query = classes_query.filter_by(branch_id=None)
        elif current_user.role.value == 'branch_admin':
            classes_query = classes_query.filter_by(branch_id=current_user.branch_id)

        classes = classes_query.order_by(Class.name).all()
        self.class_id.choices = [('', '--- No Class ---')] + [(c.id, c.name) for c in classes]

        # -------------------------
        # Sections (branch-aware)
        # -------------------------
        sections_query = Section.query.filter_by(school_id=current_user.school_id)
        if current_user.role.value == 'school_admin':
            sections_query = sections_query.filter_by(branch_id=None)
        elif current_user.role.value == 'branch_admin':
            sections_query = sections_query.filter_by(branch_id=current_user.branch_id)

        sections = sections_query.order_by(Section.name).all()
        self.section_id.choices = [('', '--- No Section ---')] + [(s.id, s.name) for s in sections]


# Teacher Form
class TeacherForm(FlaskForm):
    # -------------------------
    # Basic Info
    # -------------------------
    full_name = StringField(
        'Full Name',
        validators=[DataRequired(), Length(max=150)]
    )

    specialization = StringField(
        'Specialization',
        validators=[DataRequired(), Length(max=150)]
    )

    # -------------------------
    # Contact
    # -------------------------
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=150)]
    )

    phone = StringField(
        'Phone',
        validators=[Optional(), Length(max=30)]
    )

    emergency = StringField(
        'Emergency Contact',
        validators=[Optional(), Length(max=30)]
    )

    # -------------------------
    # Auth
    # -------------------------
    password = PasswordField(
        'Password',
        validators=[Optional(), Length(min=6, max=128)]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[Optional(), EqualTo('password', message='Passwords must match')]
    )

    # -------------------------
    # Extra Info
    # -------------------------
    roll_no = StringField(
        'Roll No',
        validators=[Optional(), Length(max=50)],
        render_kw={"readonly": True}
    )

    gender = SelectField(
        'Gender',
        choices=[
            ('', '--- Select Gender ---'),
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other')
        ],
        validators=[Optional()]
    )

    profile_photo = FileField(
        "Profile Photo",
        validators=[Optional()]
    )

    date_of_birth = DateField(
        'Date of Birth',
        format='%Y-%m-%d',
        validators=[Optional()]
    )

    address = TextAreaField(
        'Address',
        validators=[Optional()]
    )
    designation = StringField('Designation', validators=[Optional(), Length(max=100)])


    # -------------------------
    # Status
    # -------------------------
    status = SelectField(
        'Status',
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('blocked', 'Blocked')
        ],
        default='active'
    )

    # -------------------------
    # School & Branch
    # -------------------------
    school_id = SelectField(
        'School',
        coerce=int,
        validators=[DataRequired()]
    )

    branch_id = SelectField(
        'Branch',
        coerce=lambda x: int(x) if x else None,
        validators=[Optional()]
    )

    submit = SubmitField('Save')

    # -------------------------
    # Dynamic init (same logic)
    # -------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if current_user.is_authenticated:
            from app.modal import School, Branch  # adjust path

            if current_user.role.value == 'school_admin':
                self.school_id.choices = [
                    (current_user.school_id, current_user.school.name)
                ]
                self.school_id.data = current_user.school_id

                branches = Branch.query.filter_by(
                    school_id=current_user.school_id
                ).all()

                self.branch_id.choices = (
                    [('', '--- No Branch ---')] +
                    [(b.id, b.name) for b in branches]
                )
                self.branch_id.data = None

            elif current_user.role.value == 'branch_admin':
                self.school_id.choices = [
                    (current_user.school_id, current_user.school.name)
                ]
                self.school_id.data = current_user.school_id

                self.branch_id.choices = [
                    (current_user.branch_id, current_user.branch.name)
                ]
                self.branch_id.data = current_user.branch_id

            else:
                schools = School.query.all()
                self.school_id.choices = [(s.id, s.name) for s in schools]
                self.school_id.data = None
                self.branch_id.choices = [('', '--- No Branch ---')]

# Teacher Assignment Form
class TeacherAssignmentForm(FlaskForm):
    teacher_id = SelectField("Teacher", coerce=int, validators=[DataRequired()])
    school_id = HiddenField()
    branch_id = HiddenField()
    submit = SubmitField("Save Assignment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        teachers = []
        if getattr(current_user, "role", None):
            if current_user.role.value == "school_admin":
                teachers = Teacher.query.filter_by(school_id=current_user.school_id, branch_id=None).order_by(Teacher.full_name).all()
                self.school_id.data = current_user.school_id
                self.branch_id.data = None
            elif current_user.role.value == "branch_admin":
                teachers = Teacher.query.filter_by(school_id=current_user.school_id, branch_id=current_user.branch_id).order_by(Teacher.full_name).all()
                self.school_id.data = current_user.school_id
                self.branch_id.data = current_user.branch_id

        self.teacher_id.choices = [(t.id, t.full_name) for t in teachers] or []
        self.teacher_id.data = self.teacher_id.data or (teachers[0].id if teachers else None)


# Student Fee CollectionForm
# Student Fee CollectionForm
class StudentFeeCollectionForm(FlaskForm):
    student_id = SelectField(
        "Student",
        coerce=int,
        validators=[DataRequired(message="Please select a student")],
        choices=[]
    )
 
    amount_paid = FloatField(
        "Amount Paid",
        default=0.0,
        validators=[InputRequired(message="Amount is required"), NumberRange(min=0)]
    )
    payment_date = DateField(
        "Payment Date", 
        format="%Y-%m-%d", 
        validators=[DataRequired(message="Please select a date")]
    )
    remarks = TextAreaField("Remarks", validators=[Optional()])

    school_id = HiddenField()
    branch_id = HiddenField()
    submit = SubmitField("Save Fee Collection")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---------------- SCHOOL ADMIN ----------------
        if current_user.role.value == "school_admin":
            students = Student.query.filter_by(
                school_id=current_user.school_id, branch_id=None
            ).order_by(Student.full_name).all()
            self.school_id.data = current_user.school_id
            self.branch_id.data = None

        # ---------------- BRANCH ADMIN ----------------
        elif current_user.role.value == "branch_admin":
            students = Student.query.filter_by(
                school_id=current_user.school_id, branch_id=current_user.branch_id
            ).order_by(Student.full_name).all()
            self.school_id.data = current_user.school_id
            self.branch_id.data = current_user.branch_id

        else:
            students = []

        # ---------------- SET CHOICES ----------------
        self.student_id.choices = [(-1, "Select Student")] + [(s.id, s.full_name) for s in students]

        # ---------------- EDIT MODE LOGIC ----------------
        # Haddii 'obj' uu ku jiro kwargs, waxay ka dhigan tahay inaan Edit ku jirno
        if 'obj' in kwargs and kwargs['obj']:
            # Haddii obj uu yahay StudentFeeCollection (Edit Mode)
            if hasattr(kwargs['obj'], 'student_id'):
                self.student_id.data = kwargs['obj'].student_id
                # Waxaan ka dhigaynaa readonly dhanka HTML-ka si aanan loo beddelin ardayga
                self.student_id.render_kw = {'disabled': 'disabled'}
            # Haddii obj uu yahay Student (Add Mode from student profile)
            else:
                self.student_id.data = kwargs['obj'].id
                

# Fee Invoice Form
class FeeInvoiceForm(FlaskForm):
    student_fee_id = SelectField(
        "Fee Collection",
        coerce=int,
        validators=[
            DataRequired(message="Please select a fee collection"),
            NumberRange(min=1, message="Please select a valid fee collection")
        ],
        choices=[]
    )

    invoice_number = StringField(
        "Invoice Number",
        validators=[DataRequired()]
    )

    date_issued = DateField(
        "Date Issued",
        format="%Y-%m-%d",
        validators=[Optional()]
    )

    total_amount = FloatField(
        "Total Amount",
        validators=[DataRequired(), NumberRange(min=0)]
    )

    receipt_url = StringField(validators=[Optional()])
    description = TextAreaField(validators=[Optional()])

    submit = SubmitField("Create Invoice")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔒 SAFETY CHECK
        if not current_user.is_authenticated:
            fee_collections = []

        elif current_user.role.value == "school_admin":
            fee_collections = StudentFeeCollection.query.options(
                joinedload(StudentFeeCollection.student),
                joinedload(StudentFeeCollection.class_obj)
            ).filter_by(
                school_id=current_user.school_id,
                branch_id=None
            ).order_by(StudentFeeCollection.payment_date.desc()).all()

        elif current_user.role.value == "branch_admin":
            fee_collections = StudentFeeCollection.query.options(
                joinedload(StudentFeeCollection.student),
                joinedload(StudentFeeCollection.class_obj)
            ).filter_by(
                school_id=current_user.school_id,
                branch_id=current_user.branch_id
            ).order_by(StudentFeeCollection.payment_date.desc()).all()

        else:
            fee_collections = []

        # ✅ FIXED choices
        self.student_fee_id.choices = [(0, "Select Fee Collection")] + [
            (f.id, f"{f.student.full_name} - {f.class_obj.name} - {f.payment_status}")
            for f in fee_collections
        ]


# Attendance Form
class AttendanceForm(FlaskForm):
    class_id = SelectField("Class", coerce=int, validators=[DataRequired()])
    section_id = SelectField("Section", coerce=int)
    subject_id = SelectField("Subject", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save Attendance")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if not teacher:
            self.class_id.choices = []
            self.section_id.choices = []
            self.subject_id.choices = []
            return

        assignments = TeacherAssignment.query.filter_by(teacher_id=teacher.id).all()
        if not assignments:
            self.class_id.choices = []
            self.section_id.choices = []
            self.subject_id.choices = []
            return

        # -------------------
        # Classes assigned
        # -------------------
        class_map = {a.class_id: a.class_obj.name for a in assignments}
        class_choices = list(class_map.items())
        self.class_id.choices = class_choices
        selected_class = self.class_id.data or (class_choices[0][0] if class_choices else None)
        self.class_id.data = selected_class

        # -------------------
        # Sections assigned for selected class
        # -------------------
        sections = [(a.section_id, a.section.name) for a in assignments if a.class_id == selected_class and a.section_id]
        self.section_id.choices = sections
        selected_section = self.section_id.data or (sections[0][0] if sections else None)
        self.section_id.data = selected_section

        # -------------------
        # Subjects assigned for selected class + section
        # -------------------
        subject_ids = set()
        for a in assignments:
            if a.class_id == selected_class and (selected_section is None or a.section_id == selected_section):
                subject_ids.update(a.subject_ids)

        if subject_ids:
            subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
            self.subject_id.choices = [(s.id, s.name) for s in subjects]
            if subjects:
                self.subject_id.data = subjects[0].id
        else:
            self.subject_id.choices = []

# Academic Year Form
class AcademicYearForm(FlaskForm):
    year_name = StringField(
        "Academic Year",
        validators=[DataRequired()],
        default=get_academic_year  # ✅ pass the function, not call it
    )
    is_active = BooleanField("Is Active", default=True)
    school_id = HiddenField()
    branch_id = HiddenField()
    submit = SubmitField("Save Academic Year")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Automatically set school and branch IDs based on current user
        if getattr(current_user, "role", None):
            if current_user.role.value == "school_admin":
                self.school_id.data = current_user.school_id
                self.branch_id.data = None
            elif current_user.role.value == "branch_admin":
                self.school_id.data = current_user.school_id
                self.branch_id.data = current_user.branch_id

        # Optional: populate a SelectField with existing academic years for this school/branch
        # Only if you want the user to select existing year instead of typing
        # Uncomment below if needed:
        """
        years = AcademicYear.query.filter_by(
            school_id=self.school_id.data,
            branch_id=self.branch_id.data
        ).order_by(AcademicYear.year_name).all()
        self.year_id.choices = [(y.id, y.year_name) for y in years] or []
        """

# Term Form
class TermForm(FlaskForm):
    term_name = StringField("Term Name", validators=[DataRequired()])
    start_date = DateField("Start Date", validators=[DataRequired()], format="%Y-%m-%d")
    end_date = DateField("End Date", validators=[DataRequired()], format="%Y-%m-%d")
    is_active = BooleanField("Is Active", default=False)

    school_id = HiddenField()
    branch_id = HiddenField()
    academic_year_id = SelectField("Academic Year", coerce=int, validators=[DataRequired()])
    
    submit = SubmitField("Save Term")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Automatically set school and branch IDs based on current user
        if getattr(current_user, "role", None):
            if current_user.role.value == "school_admin":
                self.school_id.data = current_user.school_id
                self.branch_id.data = None
                years = AcademicYear.query.filter_by(
                    school_id=current_user.school_id,
                    branch_id=None
                ).order_by(AcademicYear.year_name.desc()).all()
            elif current_user.role.value == "branch_admin":
                self.school_id.data = current_user.school_id
                self.branch_id.data = current_user.branch_id
                years = AcademicYear.query.filter_by(
                    school_id=current_user.school_id,
                    branch_id=current_user.branch_id
                ).order_by(AcademicYear.year_name.desc()).all()
            else:
                years = []
        else:
            years = []

        # Populate academic year choices
        self.academic_year_id.choices = [(y.id, y.year_name) for y in years] or []

    def validate_end_date(self, field):
        """Ensure end_date is after start_date"""
        if self.start_date.data and field.data:
            if field.data < self.start_date.data:
                raise ValidationError("End date must be after start date.")



# ----------------- Exam Form -----------------
class ExamForm(FlaskForm):
    exam_name = StringField("Exam Name", validators=[DataRequired()])
    academic_year_id = SelectField("Academic Year", coerce=int, validators=[DataRequired()])
    term_id = SelectField("Term", coerce=int, validators=[DataRequired()])
    start_date = DateField("Start Date", format="%Y-%m-%d", validators=[DataRequired()])
    end_date = DateField("End Date", format="%Y-%m-%d", validators=[DataRequired()])
    status = SelectField(
        "Status",
        choices=[("draft", "Draft"), ("published", "Published"), ("closed", "Closed")],
        default="draft",
        validators=[DataRequired()]
    )

    school_id = HiddenField()
    branch_id = HiddenField()
    submit = SubmitField("Save Exam")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ---------------- Set school/branch ----------------
        if getattr(current_user, "role", None):
            self.school_id.data = current_user.school_id
            self.branch_id.data = current_user.branch_id if current_user.role.value == "branch_admin" else None

            # Academic years for this school/branch
            years = AcademicYear.query.filter_by(
                school_id=self.school_id.data,
                branch_id=self.branch_id.data
            ).order_by(AcademicYear.year_name.desc()).all()
        else:
            years = []

        self.academic_year_id.choices = [(y.id, y.year_name) for y in years] or []

        # ---------------- Populate only ACTIVE terms ----------------
        if self.academic_year_id.data:
            terms = Term.query.filter_by(
                school_id=self.school_id.data,
                branch_id=self.branch_id.data,
                academic_year_id=self.academic_year_id.data,
                is_active=True  # ONLY ACTIVE TERMS
            ).order_by(Term.term_name).all()
        else:
            terms = Term.query.filter_by(
                school_id=self.school_id.data,
                branch_id=self.branch_id.data,
                is_active=True  # ONLY ACTIVE TERMS
            ).order_by(Term.term_name).all()

        self.term_id.choices = [(t.id, t.term_name) for t in terms] or []

        # ---------------- Set start/end date if term already selected ----------------
        if "term_id" in self.data and self.data["term_id"]:
            term = Term.query.get(self.data["term_id"])
            if term:
                # Auto-fill start/end date from term
                self.start_date.data = term.start_date
                self.end_date.data = term.end_date
                self.start_date.render_kw = {"readonly": True}
                self.end_date.render_kw = {"readonly": True}

    def validate_end_date(self, field):
        """Ensure end_date is after start_date"""
        if self.start_date.data and field.data:
            if field.data < self.start_date.data:
                raise ValidationError("End date must be after start date.")



# Exam Time Table Form
class ExamTimetableForm(FlaskForm):
    exam_id = SelectField('Exam', choices=[], coerce=int, validators=[DataRequired()])
    level_id = SelectField('Class Level', choices=[], coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject', choices=[], coerce=int, validators=[DataRequired()])
    
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', validators=[DataRequired()], format='%H:%M')
    
    school_id = HiddenField(validators=[DataRequired()])
    branch_id = HiddenField()
    
    submit = SubmitField('Save Timetable')


class ExamHallForm(FlaskForm):
    name = StringField(
        'Hall Name',
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    capacity = IntegerField(
        'Capacity',
        validators=[
            DataRequired(),
            NumberRange(min=1, message="Capacity must be at least 1")
        ]
    )

    school_id = HiddenField(validators=[DataRequired()])
    branch_id = HiddenField()

    submit = SubmitField('Save Hall')


class ExamHallAssignmentForm(FlaskForm):
    # Select which timetable (exam + level + subject)
    exam_timetable_id = SelectField(
        'Exam Timetable',
        choices=[],  # populate dynamically in view
        coerce=int,
        validators=[DataRequired()]
    )

    # Select hall
    hall_id = SelectField(
        'Exam Hall',
        choices=[],  # populate dynamically in view
        coerce=int,
        validators=[DataRequired()]
    )

    # Select student
    student_id = SelectField(
        'Student',
        choices=[],  # populate dynamically in view
        coerce=int,
        validators=[DataRequired()]
    )

    # Select class (optional if student already has class info)
    class_id = SelectField(
        'Class',
        choices=[],  # populate dynamically in view
        coerce=int,
        validators=[DataRequired()]
    )

    # Hidden fields for school/branch
    school_id = HiddenField(validators=[DataRequired()])
    branch_id = HiddenField()

    submit = SubmitField('Assign Student')


class ExamTicketForm(FlaskForm):
    # Select Exam
    exam_id = SelectField(
        'Exam',
        choices=[],
        coerce=int,
        validators=[DataRequired()]
    )

    # Select Student
    student_id = SelectField(
        'Student',
        choices=[],
        coerce=int,
        validators=[DataRequired()]
    )

    # Select Class
    class_id = SelectField(
        'Class',
        choices=[],
        coerce=int,
        validators=[DataRequired()]
    )

    # Select Hall
    hall_id = SelectField(
        'Exam Hall',
        choices=[],
        coerce=int,
        validators=[DataRequired()]
    )

    # ✅ NEW FIELD
    ticket_number = StringField(
        'Ticket Number',
        validators=[DataRequired(), Length(max=100)]
    )

    # Hidden fields
    school_id = HiddenField(validators=[DataRequired()])
    branch_id = HiddenField()

    # Submit
    submit = SubmitField('Create Exam Ticket')



# Exam Subjects Form         
class ExamSubjectForm(FlaskForm):
    school_id = HiddenField()
    branch_id = HiddenField()
    academic_year_id = SelectField("Academic Year", coerce=int, validators=[DataRequired()])
    
    # 1. Waxaan u beddelnay SelectMultipleField si dhowr fasal loo doorto
    class_ids = SelectMultipleField("Fasallada", coerce=int, validators=[DataRequired()])
    
    exam_id = SelectField("Exam", coerce=int, validators=[DataRequired()])
    subject_ids = SelectMultipleField("Subjects", coerce=int, validators=[DataRequired()])
    total_marks = DecimalField("Total Marks", validators=[DataRequired(), NumberRange(min=0)])
    pass_marks = DecimalField("Pass Marks", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Save Exam Subjects")

    def __init__(self, *args, **kwargs):
        obj = kwargs.get('obj', None)
        super().__init__(*args, **kwargs)

        if getattr(current_user, "role", None):
            self.school_id.data = current_user.school_id
            if current_user.role.value == "branch_admin":
                self.branch_id.data = current_user.branch_id
        
        if obj and not self.school_id.data:
            self.school_id.data = obj.school_id
            self.branch_id.data = obj.branch_id

        s_id = self.school_id.data
        b_id = self.branch_id.data

        if s_id:
            # Sannadaha
            years = AcademicYear.query.filter_by(school_id=s_id).order_by(AcademicYear.created_at.desc()).all()
            self.academic_year_id.choices = [(y.id, y.year_name) for y in years]

            # Fasallada (Choices-ka)
            classes = Class.query.filter_by(school_id=s_id).all()
            self.class_ids.choices = [(c.id, c.name) for c in classes]

            # Imtixaannada
            selected_year = self.academic_year_id.data or (years[0].id if years else None)
            exams_q = Exam.query.filter_by(school_id=s_id)
            if b_id: exams_q = exams_q.filter_by(branch_id=b_id)
            if selected_year: exams_q = exams_q.filter_by(academic_year_id=selected_year)
            self.exam_id.choices = [(e.id, e.exam_name) for e in exams_q.all()]

            # Maaddooyinka
            subjects_q = Subject.query.filter_by(school_id=s_id)
            if b_id: subjects_q = subjects_q.filter_by(branch_id=b_id)
            self.subject_ids.choices = [(s.id, s.name) for s in subjects_q.all()]

        # Pre-fill data (Edit mode)
        if obj and request.method == 'GET':
            self.academic_year_id.data = getattr(obj, 'academic_year_id', None)
            self.exam_id.data = getattr(obj, 'exam_id', None)
            # Haddii uu jiro class_id (hal mid ah), u beddel liis ahaan
            if hasattr(obj, 'class_id'):
                self.class_ids.data = [obj.class_id]
            if hasattr(obj, 'subject_id'):
                self.subject_ids.data = [obj.subject_id]

    def validate_pass_marks(self, field):
        if self.total_marks.data is not None and field.data is not None:
            if field.data > self.total_marks.data:
                raise ValidationError("Pass marks cannot exceed total marks.")



class StudentExamMarkForm(FlaskForm):
    school_id = HiddenField()
    branch_id = HiddenField()
    
    exam_id = SelectField("Imtixaanka", coerce=int, validators=[DataRequired()])
    class_id = SelectField("Fasalka", coerce=int, validators=[DataRequired()])
    section_id = SelectField("Qaybta (Section)", coerce=int, default=0)
    exam_subject_id = SelectField("Maaddada", coerce=int, validators=[DataRequired()])
    
    submit = SubmitField("Keydi Dhibcaha")

    def __init__(self, *args, **kwargs):
        super(StudentExamMarkForm, self).__init__(*args, **kwargs)
        
        # 1. Deji xogta aqoonsiga
        self.school_id.data = getattr(current_user, 'school_id', None)
        self.branch_id.data = getattr(current_user, 'branch_id', None)

        teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        active_year = AcademicYear.query.filter_by(
            school_id=current_user.school_id, 
            is_active=True
        ).first()
        
        if not teacher or not active_year:
            self.exam_id.choices = [(0, 'Profile/Sanad lama helin')]
            self.class_id.choices = [(0, 'N/A')]
            return

        # 2. HEL FASALLADA
        assignments = TeacherAssignment.query.filter_by(teacher_id=teacher.id).all()
        assigned_class_ids = list(set([a.class_id for a in assignments if a.class_id]))
        
        if assigned_class_ids:
            classes = Class.query.filter(Class.id.in_(assigned_class_ids)).all()
            self.class_id.choices = [(0, '--- Dooro Fasal ---')] + [(c.id, c.name) for c in classes]
        else:
            self.class_id.choices = [(0, 'Ma jiro fasal laguu xilsaaray')]

        # 3. HEL IMTIXAANNADA
        exams = Exam.query.filter_by(
            school_id=current_user.school_id, 
            status='draft',
            academic_year_id=active_year.id
        ).all()
        
        self.exam_id.choices = [(0, '--- Dooro Imtixaan ---')] + [(e.id, e.exam_name) for e in exams] if exams else [(0, 'Ma jiro imtixaan qabyo ah')]

        # AJAX Defaults
        self.section_id.choices = [(0, '--- Dhammaan Qaybaha ---')]
        self.exam_subject_id.choices = [(0, '--- Dooro Maaddada ---')]




class StudentExamResultForm(FlaskForm):
    school_id = HiddenField()
    branch_id = HiddenField()
    academic_year_id = HiddenField()

    # SelectFields (Aqoonsiga)
    exam_id = SelectField("Imtixaanka", coerce=int, validators=[DataRequired()])
    class_id = SelectField("Fasalka", coerce=int, validators=[DataRequired()])
    section_id = SelectField("Qaybta", coerce=int, validators=[DataRequired()])
    student_id = SelectField("Ardayga", coerce=int, validators=[DataRequired()])

    # Xogta Natiijada
    total_marks = DecimalField("Wadarta Dhibcaha", places=2, validators=[DataRequired(), NumberRange(min=0)])
    average = DecimalField("Celceliska (%)", places=2, validators=[DataRequired(), NumberRange(min=0, max=100)])
    
    grade = SelectField("Darajada (Grade)", choices=[
        ('A+', 'A+'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('F', 'F')
    ], validators=[DataRequired()])
    
    decision = SelectField("Go'aanka", choices=[
        ('Pass', 'Gudbay (Pass)'), ('Fail', 'Haray (Fail)')
    ], validators=[DataRequired()])
    
    published = SelectField("Xaaladda Natiijada", choices=[
        ('pending', 'Sugitaan (Pending)'), 
        ('published', 'La Daabacay (Published)'), 
        ('closed', 'Lagu Xiray (Closed)')
    ], default='pending')

    # Boosaska (Positions) - IntegerField ayaa ku habboon maaddaama ay yihiin tiro dhan (1, 2, 3...)
    class_position = IntegerField("Kaalinta Fasalka", validators=[Optional(), NumberRange(min=1)])
    section_position = IntegerField("Kaalinta Qaybta", validators=[Optional(), NumberRange(min=1)])
    school_position = IntegerField("Kaalinta Iskuulka", validators=[Optional(), NumberRange(min=1)])

    submit = SubmitField("Keydi Natiijada Guud")

    def __init__(self, *args, **kwargs):
        super(StudentExamResultForm, self).__init__(*args, **kwargs)

        # 1. Deji aqoonsiga dugsiga iyo sanadka
        s_id = getattr(current_user, 'school_id', None)
        active_year = AcademicYear.query.filter_by(school_id=s_id, is_active=True).first()

        if s_id:
            self.school_id.data = s_id
            self.branch_id.data = getattr(current_user, 'branch_id', None)
            
            if active_year:
                self.academic_year_id.data = active_year.id

            # 2. Populate Dropdowns (Kaliya soo saar xogta dugsigaas khuseysa)
            # Imtixaannada sanadka firfircoon
            self.exam_id.choices = [(e.id, e.exam_name) for e in Exam.query.filter_by(
                school_id=s_id, 
                academic_year_id=active_year.id if active_year else 0
            ).all()] or [(0, 'Imtixaan lama helin')]

            # Fasallada
            self.class_id.choices = [(c.id, c.name) for c in Class.query.filter_by(school_id=s_id).all()] or [(0, 'Fasal lama helin')]

            # Qaybaha (Sections)
            self.section_id.choices = [(s.id, s.section_name) for s in Section.query.filter_by(school_id=s_id).all()] or [(0, 'Qayb lama helin')]

            # Ardayda Firfircoon (Limit 100 si looga fogaado gaabiska bogga haddii ardaydu badanyihiin)
            self.student_id.choices = [(s.id, f"{s.first_name} {s.last_name}") for s in Student.query.filter_by(
                school_id=s_id, 
                status='active'
            ).limit(100).all()] or [(0, 'Arday lama helin')]

    # 3. Validation gaar ah
    def validate_average(self, field):
        if field.data and (field.data > 100 or field.data < 0):
            raise ValidationError("Celcelisku waa inuu u dhexeeyaa 0 ilaa 100%.")
        
    
class StudentPromotionForm(FlaskForm):
    school_id = HiddenField()
    branch_id = HiddenField()
    # Waxaan ku darnay validators halkan si loo hubiyo in student_ids la soo diray
    student_ids = HiddenField("Selected Students", validators=[DataRequired(message="Dooro ardayda")]) 

    current_class_id = SelectField("Current Class", coerce=int, validators=[Optional()])
    current_academic_year_id = SelectField("Current Academic Year", coerce=int, validators=[Optional()])

    to_class_id = SelectField("Promote To Class", coerce=int, validators=[Optional()])
    to_section_id = SelectField("Target Section", coerce=int, validators=[Optional()])
    # Academic Year waa khasab si loo ogaado sanadka loo dallacayo
    to_academic_year_id = SelectField("Target Academic Year", coerce=int, validators=[DataRequired(message="Dooro sanadka cusub")])

    promotion_type = SelectField("Promotion Type", choices=[
        ('regular', 'Regular Promotion (Gudbi)'),
        ('repeat', 'Repeat Year (Ku celi)'),
        ('double', 'Double Promotion (Labo fasal gudbi)'),
        ('trial', 'Trial Promotion (Tijaabo)')
    ], default='regular')

    remarks = TextAreaField("Remarks/Notes")
    submit = SubmitField("Promote Selected Students")

    def __init__(self, *args, **kwargs):
        super(StudentPromotionForm, self).__init__(*args, **kwargs)
        
        # Hubi in current_user uu jiro
        school_id = getattr(current_user, 'school_id', None)
        self.school_id.data = school_id
        self.branch_id.data = getattr(current_user, 'branch_id', None)

        if school_id:
            # 1. Classes
            classes = Class.query.filter_by(school_id=school_id, status='active').order_by(Class.name).all()
            class_choices = [(0, '--- Select Class ---')] + [(c.id, c.name) for c in classes]
            self.current_class_id.choices = class_choices
            self.to_class_id.choices = class_choices

            # 2. Sections
            sections = Section.query.filter_by(school_id=school_id).all()
            self.to_section_id.choices = [(0, '--- Select Section ---')] + [(s.id, s.name) for s in sections]

            # 3. Years
            years = AcademicYear.query.filter_by(school_id=school_id).order_by(AcademicYear.year_name.desc()).all()
            # Waxaan ka saarnay (0, ...) to_academic_year_id maadaama uu yahay DataRequired
            year_choices = [(y.id, y.year_name) for y in years]
            
            # Haddii aysan jirin sanado, looma baahna in dropdown-ku eber noqdo
            self.current_academic_year_id.choices = [(0, '--- Select Year ---')] + year_choices
            self.to_academic_year_id.choices = year_choices # Tan waa khasab (DataRequired)


class ExamMultiPublishForm(FlaskForm):
    exam_id = SelectField('Select Exam Session', coerce=int, validators=[DataRequired()])
    
    # User-ka ayaa dooranaya waqtiyadan midkood
    duration_minutes = SelectField('Duration', coerce=int, choices=[
        (30, '30 Minutes'),
        (60, '1 Hour'),
        (90, '1.5 Hours'),
        (120, '2 Hours'),
        (180, '3 Hours')
    ], default=60)

    teacher_ids_hidden = HiddenField('Teacher IDs', validators=[DataRequired()])
    school_id = HiddenField()
    branch_id = HiddenField()
    submit = SubmitField('Publish Exam')




class ExamQuestionForm(FlaskForm):
    # 1. Hidden Fields for Context
    paper_id = HiddenField()
    school_id = HiddenField()
    branch_id = HiddenField()

    # 2. Basic Question Info
    question_type = SelectField(
        "Nooca Su'aasha",
        choices=[
            ('mcq', 'Multiple Choice (Xulasho)'),
            ('true_false', 'True / False (Run/Been)'),
            ('direct', 'Short Answer (Toos)')
        ],
        validators=[DataRequired()]
    )

    question_text = TextAreaField(
        "Su'aasha", 
        validators=[DataRequired(), Length(min=5)],
        render_kw={"placeholder": "Ku qor halkan qoraalka su'aasha..."}
    )

    # question_image waxaan u deynay String madaama aad u isticmaalayso file path
    question_image = StringField("Sawirka Su'aasha (Optional)", validators=[Optional()])

    marks = DecimalField(
        "Dhibcaha", 
        default=1.0, 
        validators=[DataRequired(), NumberRange(min=0.1)]
    )

    # 3. Correct Answer
    # MCQ iyo True/False ahaan halkan ayaa lagu keydinayaa jawaabta saxda ah (e.g. "A" ama "True")
    correct_answer = TextAreaField(
        "Jawaabta Saxda ah", 
        validators=[DataRequired()],
        render_kw={"placeholder": "Ku qor jawaabta saxda ah..."}
    )

    # 4. Socrative Features (Waxa aad ku dartay Model-ka)
    explanation = TextAreaField(
        "Sharaxaadda (Feedback)", 
        validators=[Optional()],
        render_kw={"placeholder": "Sharax sababta jawaabtani u saxantahay (Ardayga ayaa arki doona)..."}
    )

    sort_order = IntegerField(
        "Xiriirka (Order)", 
        default=0, 
        validators=[Optional()]
    )

    time_limit = IntegerField(
        "Waqtiga (Seconds)", 
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Tusaale: 60"}
    )

    shuffle_options = BooleanField("Kala beddel xulashooyinka (Shuffle)")

    submit = SubmitField("Save Question")

    def __init__(self, *args, **kwargs):
        super(ExamQuestionForm, self).__init__(*args, **kwargs)
        # Sidaadii hore, halkan waxaad ku fill-gareyn kartaa school_id iyo branch_id
        if getattr(current_user, "role", None):
            if not self.school_id.data:
                self.school_id.data = current_user.school_id
            if current_user.role.value == "branch_admin" and not self.branch_id.data:
                self.branch_id.data = current_user.branch_id


class TimeSlotForm(FlaskForm):
    label = StringField("Slot Label (e.g. Xiisadda 1aad)", validators=[DataRequired()])
    start_time = TimeField("Start Time", validators=[DataRequired()])
    end_time = TimeField("End Time", validators=[DataRequired()])
    
    shift = SelectField("Shift", choices=[
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon')
    ], validators=[DataRequired()])
    
    is_break = BooleanField("Is this a Break/Recess?")
    
    school_id = HiddenField()
    branch_id = HiddenField()
    submit = SubmitField("Save Time Slot")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hannaanka Sharciga (Permissions)
        if current_user.role.value == 'school_admin':
            self.school_id.data = current_user.school_id
            self.branch_id.data = None  # School-level slots

        elif current_user.role.value == 'branch_admin':
            self.school_id.data = current_user.school_id
            self.branch_id.data = current_user.branch_id

# Time table Form

class TimetableForm(FlaskForm):
    # Hidden fields si amniga loo sugo
    school_id = HiddenField()
    branch_id = HiddenField()

    day_of_week = SelectField("Maalinta (Day)", choices=[
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday')
    ], validators=[DataRequired()])

    class_id = SelectField("Fasalka (Class)", coerce=int, validators=[DataRequired()])
    section_id = SelectField("Qaybta (Section)", coerce=int) # Waxaan ka saarnay (Optional) label-ka si uu u nadiif sanaado
    subject_id = SelectField("Maaddada (Subject)", coerce=int, validators=[DataRequired()])
    teacher_id = SelectField("Macallinka (Teacher)", coerce=int, validators=[DataRequired()])
    time_slot_id = SelectField("Waqtiga (Time Slot)", coerce=int, validators=[DataRequired()])

    submit = SubmitField("Save Timetable")

    def __init__(self, *args, **kwargs):
        super(TimetableForm, self).__init__(*args, **kwargs)
        
        # 1. Deji aqoonsiga (Ownership) markaba
        self.school_id.data = current_user.school_id
        
        if current_user.role.value == 'branch_admin':
            self.branch_id.data = current_user.branch_id
        else:
            self.branch_id.data = None # School-level

        # 2. Xogta hadba Role-ka (Filtering Logic)
        s_id = current_user.school_id
        b_id = current_user.branch_id

        # --- FILTARAYNTA FASALLADA ---
        class_query = Class.query.filter_by(school_id=s_id)
        if current_user.role.value == 'branch_admin':
            class_query = class_query.filter_by(branch_id=b_id)
        else:
            class_query = class_query.filter_by(branch_id=None)
        self.class_id.choices = [(c.id, c.name) for c in class_query.order_by(Class.name).all()]

        # --- FILTARAYNTA SECTIONS ---
        section_query = Section.query.filter_by(school_id=s_id)
        if current_user.role.value == 'branch_admin':
            section_query = section_query.filter_by(branch_id=b_id)
        # Halkan waxaan ku daray 0 ama None si aysan qasab u noqon
        self.section_id.choices = [(0, "-- No Section --")] + [(s.id, s.name) for s in section_query.all()]

        # --- FILTARAYNTA MAADDOOYINKA ---
        sub_query = Subject.query.filter_by(school_id=s_id)
        if current_user.role.value == 'branch_admin':
            sub_query = sub_query.filter_by(branch_id=b_id)
        else:
            sub_query = sub_query.filter_by(branch_id=None)
        self.subject_id.choices = [(s.id, s.name) for s in sub_query.all()]

        # --- FILTARAYNTA MACALLIMIINTA ---
        teach_query = Teacher.query.filter_by(school_id=s_id)
        if current_user.role.value == 'branch_admin':
            teach_query = teach_query.filter_by(branch_id=b_id)
        self.teacher_id.choices = [(t.id, t.full_name) for t in teach_query.all()]

        # --- FILTARAYNTA WAQTIGA (SLOTS) ---
        # Kaliya kuwa aan 'Break' ahayn ayaan u baahanahay jadwalka
        slot_query = TimeSlot.query.filter_by(school_id=s_id, is_break=False)
        if current_user.role.value == 'branch_admin':
            slot_query = slot_query.filter_by(branch_id=b_id)
        else:
            slot_query = slot_query.filter_by(branch_id=None)
        
        self.time_slot_id.choices = [
            (ts.id, f"{ts.label} ({ts.start_time.strftime('%I:%M %p')} - {ts.shift.capitalize()})") 
            for ts in slot_query.order_by(TimeSlot.shift, TimeSlot.start_time).all()
        ]

























