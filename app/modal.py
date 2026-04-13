from decimal import Decimal
import enum
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.dialects.mysql import ENUM  # Make sure this is the MySQL ENUM
import pytz
from sqlalchemy import DECIMAL, UniqueConstraint, event
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, now_eat



# user role 
class UserRole(enum.Enum):
    superadmin = "superadmin"
    school_admin = "school_admin"
    branch_admin = "branch_admin"
    teacher = "teacher"
    student = "student"
    parent = "parent"


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    # Relationships
    role_permissions = db.relationship('RolePermission', back_populates='role', cascade='all, delete-orphan')

    users = db.relationship('User', back_populates='role_id_fk')

    # Property to directly get Permission objects
    @property
    def permissions(self):
        return [rp.permission for rp in self.role_permissions]

    def __repr__(self):
        return f"<Role {self.name}>"


# -------------------------------
# ------ School Model ------------
# -------------------------------
class School(db.Model):
    __tablename__ = 'schools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(255), nullable=True)  # Optional title
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', 'suspended'), default='active')
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    branches = db.relationship('Branch', backref='school', lazy=True, cascade="all, delete-orphan")
    users = db.relationship('User', backref='school', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<School {self.name}>"


# -------------------------------
# ------ Branch Model ------------
# -------------------------------
class Branch(db.Model):
    __tablename__ = 'branches'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(255), nullable=True)  # Optional title
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', 'suspended'), default='active')
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    users = db.relationship('User', backref='branch', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Branch {self.name}>"


# -------------------------------
# ------ User Model --------------
# -------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys to school and branch
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='SET NULL'), nullable=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)

    # Role
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.student)
    # ✅ Add ForeignKey with a custom name
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id', name='fk_user_role')  # ← HERE
    )

    # Relationship to role
    role_id_fk = db.relationship('Role', back_populates='users')



    # Basic info
    username = db.Column(db.String(150), unique=True, nullable=False)
    fullname = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(20))
    country = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    address = db.Column(db.String(255))
    bio = db.Column(db.Text)
    photo = db.Column(db.String(255))
    gender = db.Column(db.String(10))
    photo_visibility = db.Column(db.String(20), default='everyone')
    status = db.Column(db.Boolean, default=True)
    # Device info
    device = db.Column(db.String(100))          # Desktop / Mobile
    browser = db.Column(db.String(100))         # Chrome / Firefox
    platform = db.Column(db.String(100))        # Windows / Android
    device_name = db.Column(db.String(150))     # NEW (hostname / PC name)
    interface_name = db.Column(db.String(100))  # NEW (Wi-Fi / Ethernet)

    # Extra
    extra_info = db.Column(db.String(255))

    # Security & authentication
    is_verified = db.Column(db.Boolean, default=False)
    auth_status = db.Column(db.String(10), nullable=False, default='logout')
    session_token = db.Column(db.String(64), nullable=True)
    login_time = db.Column(db.DateTime, nullable=True)
    last_seen = db.Column(db.DateTime, default=now_eat)
    phone_verified = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_code = db.Column(db.String(10), nullable=True)
    two_factor_expires_at = db.Column(db.DateTime, nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    remember_token = db.Column(db.String(255), nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    auth_provider = db.Column(db.String(50), default='local')
    last_active = db.Column(db.DateTime, nullable=True)

    # Socials
    facebook = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    google = db.Column(db.String(255))
    whatsapp = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    github = db.Column(db.String(255))
    github_id = db.Column(db.String(100), unique=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    user_logs = db.relationship('UserLog', backref='user', cascade="all, delete-orphan", lazy=True)
    sessions = db.relationship('UserSession', back_populates='user', cascade="all, delete-orphan", lazy=True)
    user_permissions = db.relationship('UserPermission', back_populates='user', cascade='all, delete-orphan')

    # Gudaha class User:
    @property
    def is_active(self):
        
        return self.status == True

    @property
    def permissions(self):
        return [up.permission for up in self.user_permissions]
    
    def __repr__(self):
        return f"<User {self.username}>"


# -------------------------------
#---------  3. Permission -------
# -------------------------------
class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(100), nullable=False, unique=True)  # e.g. 'manage_users'
    group_name = db.Column(db.String(100), nullable=True)  # e.g. 'User Management'

    # Relationships
    role_permissions = db.relationship('RolePermission', back_populates='permission', cascade='all, delete-orphan')
    user_permissions = db.relationship('UserPermission', back_populates='permission', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Permission {self.code}>"

# -------------------------------
#------- 4. Role Permission -----
# -------------------------------
class RolePermission(db.Model):
    __tablename__ = 'role_permissions'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)

    # Relationships
    role = db.relationship('Role', back_populates='role_permissions')
    permission = db.relationship('Permission', back_populates='role_permissions')

# -------------------------------
#- 5. User Permission -----------
# -------------------------------
class UserPermission(db.Model):
    __tablename__ = 'user_permissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)

    # Relationships
    permission = db.relationship('Permission', back_populates='user_permissions')
    user = db.relationship('User', back_populates='user_permissions')  # Add this to User model


# -------------------------------
# --- 2. User Log Model ---------
# -------------------------------
class UserLog(db.Model):
    __tablename__ = 'user_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    action = db.Column(db.Text)
    status = db.Column(db.String(10), default='login')

    # Time
    login_time = db.Column(db.DateTime, default=now_eat)
    timestamp = db.Column(db.DateTime, default=now_eat)

    # Network info
    ip_address = db.Column(db.String(45))
    subnet_mask = db.Column(db.String(45))      # NEW
    gateway = db.Column(db.String(45))          # NEW
    mac_address = db.Column(db.String(50))      # NEW

    # Device info
    device = db.Column(db.String(100))          # Desktop / Mobile
    browser = db.Column(db.String(100))         # Chrome / Firefox
    platform = db.Column(db.String(100))        # Windows / Android
    device_name = db.Column(db.String(150))     # NEW (hostname / PC name)
    interface_name = db.Column(db.String(100))  # NEW (Wi-Fi / Ethernet)

    # Extra
    extra_info = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)


class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_token = db.Column(db.String(255), nullable=False)

    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    device = db.Column(db.String(100))
    browser = db.Column(db.String(100))
    platform = db.Column(db.String(100))
    payload = db.Column(db.Text, nullable=True)
    last_activity = db.Column(db.DateTime, default=now_eat)
    is_active = db.Column(db.Boolean, default=True)
    user = db.relationship('User', back_populates='sessions')

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)


    def __repr__(self):
        return f"<UserSession {self.id} - User {self.user_id}>"




# ------------------------------------
#   Somalia Location Table ---------
# ------------------------------------
class SomaliaLocation(db.Model):
    __tablename__ = 'somalia_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    def __repr__(self):
        return f"<{self.region} - {self.district}>"


class Parent(db.Model):
    __tablename__ = 'parents'

    id = db.Column(db.Integer, primary_key=True)

    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='SET NULL'), nullable=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)

    full_name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255), nullable=True)

    roll_no = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.Enum('male', 'female', 'other', name='gender_enum'), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    occupation = db.Column(db.String(150), nullable=True)
    emergency_contact = db.Column(db.String(30), nullable=True)

    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


    address = db.Column(db.Text, nullable=True)
    national_id = db.Column(db.String(100), nullable=True)

    relationship = db.Column(db.Enum('father', 'mother', 'guardian', 'other', name='relationship_enum'), nullable=True)

    status = db.Column(db.Enum('active', 'inactive', 'blocked', name='status_enum'), default='active')

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships (optional)
    user = db.relationship("User", backref="parents")  # ✅ LINKED VIA FOREIGNKEY
    school = db.relationship('School', backref=db.backref('parents', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('parents', lazy=True))

    # Password helper methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Parent {self.full_name} ({self.status})>"



# Teachers
class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)

    # روابط (FK)
    school_id = db.Column(
        db.Integer,
        db.ForeignKey('schools.id', ondelete='CASCADE'),
        nullable=False
    )
    branch_id = db.Column(
        db.Integer,
        db.ForeignKey('branches.id', ondelete='SET NULL'),
        nullable=True
    )

    # Basic Info
    full_name = db.Column(db.String(150), nullable=False)
    specialization = db.Column(db.String(150), nullable=False)
    designation = db.Column(db.String(100), nullable=True)

    # Contact
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    emergency = db.Column(db.String(30), nullable=True)

    # Personal
    gender = db.Column(db.Enum('male', 'female', 'other', name='teacher_gender_enum'), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    # Auth
    password_hash = db.Column(db.String(255), nullable=False)

    # Extra
    roll_no = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Status
    status = db.Column(db.Enum('active', 'inactive', 'blocked', name='teacher_status_enum'), default='active')

    # Timestamps
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    school = db.relationship('School', backref=db.backref('teachers', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('teachers', lazy=True))
    user = db.relationship("User", backref="teacher")

    # -------------------------
    # Password helpers
    # -------------------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Teacher {self.full_name} ({self.specialization})>"

# Teacher Assignment
class TeacherAssignment(db.Model):
    __tablename__ = 'teacher_assignments'

    id = db.Column(db.Integer, primary_key=True)

    teacher_id = db.Column(
        db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False
    )
    class_id = db.Column(
        db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False
    )
    section_id = db.Column(
        db.Integer, db.ForeignKey('sections.id', ondelete='SET NULL'), nullable=True
    )
    # For multiple subjects, store as JSON array of IDs
    subject_ids = db.Column(db.JSON, nullable=False)
    subjects = db.Column(db.JSON, nullable=False)

    school_id = db.Column(
        db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False
    )
    branch_id = db.Column(
        db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True
    )

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    __table_args__ = (
        db.UniqueConstraint(
            'teacher_id', 'class_id', 'section_id', 'school_id', 'branch_id',
            name='uq_teacher_class_section'
        ),
    )

    # ================= RELATIONSHIPS =================
    teacher = db.relationship('Teacher', backref=db.backref('assignments', cascade='all, delete-orphan'))
    class_obj = db.relationship('Class', backref=db.backref('teacher_assignments', cascade='all, delete-orphan'))
    section = db.relationship('Section', backref=db.backref('teacher_assignments', cascade='all, delete-orphan'))
    school = db.relationship('School', backref=db.backref('teacher_assignments', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('teacher_assignments', passive_deletes=True))

    def __repr__(self):
        return f"<TeacherAssignment Teacher:{self.teacher_id} Class:{self.class_id} Section:{self.section_id}>"

class ClassLevel(db.Model):
    __tablename__ = 'class_levels'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    # Kuwani 'backref' ayay isticmaali karaan maadaama aysan isku magac ahayn
    school = db.relationship('School', backref=db.backref('school_levels', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('branch_levels'))
    
    # Midka hoose waxaan u isticmaalaynaa back_populates si uu ula hadlo Class.level
    classes = db.relationship('Class', back_populates='level', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<ClassLevel {self.name} - {self.price}>"

class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('class_levels.id', ondelete='CASCADE'), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, default=0)
    shift = db.Column(db.Enum('morning', 'afternoon', name='class_shift_enum'), nullable=False)
    status = db.Column(db.Enum('active', 'inactive', name='class_status_enum'), default='active')

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ================= Relationships =================
    # Waxaan ka saarnay backref-yadii isku magaca ahaa
    school = db.relationship('School', backref=db.backref('school_classes', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('branch_classes'))
    
    # MUHIIM: Waxaan u beddelnay back_populates si uu ula xiriiro ClassLevel.classes
    level = db.relationship('ClassLevel', back_populates='classes')

    def __repr__(self):
        return f"<Class {self.name} - Level {self.level_id}>"



class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    school_id = db.Column(
        db.Integer,
        db.ForeignKey('schools.id', ondelete='CASCADE'),
        nullable=False
    )

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey('branches.id', ondelete='SET NULL'),
        nullable=True
    )

    class_id = db.Column(
        db.Integer,
        db.ForeignKey('classes.id', ondelete='CASCADE'),
        nullable=False
    )

    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, default=0)
    shift = db.Column(
        db.Enum('morning', 'afternoon', name='section_shift_enum'),
        nullable=False
    )

    status = db.Column(
        db.Enum('active', 'inactive', name='section_status_enum'),
        default='active'
    )

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ================= Relationships =================
    school = db.relationship('School', backref=db.backref('sections', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('sections'))
    klass  = db.relationship('Class', backref=db.backref('sections', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Section {self.name} - Class {self.class_id}>" 


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # School foreign key with cascade delete
    school_id = db.Column(
        db.Integer,
        db.ForeignKey('schools.id', ondelete='CASCADE'),
        nullable=False
    )

    # Branch foreign key (nullable, set to NULL if branch deleted)
    branch_id = db.Column(
        db.Integer,
        db.ForeignKey('branches.id', ondelete='SET NULL'),
        nullable=True
    )

    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    school = db.relationship('School', backref=db.backref('subjects', passive_deletes=True))
    branch = db.relationship('Branch', backref=db.backref('subjects'))

    def __repr__(self):
        return f"<Subject {self.name}>"

class ClassSubject(db.Model):
    __tablename__ = 'class_subjects'

    id = db.Column(db.Integer, primary_key=True)

    class_id = db.Column(
        db.Integer,
        db.ForeignKey('classes.id', ondelete='CASCADE'),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey('subjects.id', ondelete='CASCADE'),
        nullable=False
    )

    school_id = db.Column(
        db.Integer,
        db.ForeignKey('schools.id', ondelete='CASCADE'),
        nullable=False
    )

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey('branches.id', ondelete='SET NULL'),
        nullable=True
    )

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ✅ prevent duplicates
    __table_args__ = (
        db.UniqueConstraint('class_id', 'subject_id', 'branch_id', name='uq_class_subject'),
    )

    # ================= RELATIONSHIPS =================
    class_obj = db.relationship(
        'Class',
        backref=db.backref(
            'class_subjects',
            cascade='all, delete-orphan',
            passive_deletes=True
        )
    )

    subject = db.relationship(
        'Subject',
        backref=db.backref(
            'class_subjects',
            cascade='all, delete-orphan',
            passive_deletes=True
        )
    )

    school = db.relationship(
        'School',
        backref=db.backref(
            'class_subjects',
            cascade='all, delete-orphan',
            passive_deletes=True
        )
    )

    branch = db.relationship(
        'Branch',
        backref=db.backref(
            'class_subjects',
            passive_deletes=True
        )
    )

    def __repr__(self):
        return f"<ClassSubject Class:{self.class_id} Subject:{self.subject_id}>"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(150), nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'other'), nullable=True)

    # Foreign Keys
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id', ondelete='SET NULL'), nullable=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='SET NULL'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('class_levels.id', ondelete='CASCADE'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id', ondelete='SET NULL'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Academic Year Logic
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id', ondelete='SET NULL'), nullable=True)
    academic_year = db.Column(db.String(20), nullable=True) # Kani waa column-ka String-ka ah ee database-ka ku jira

    shift = db.Column(db.Enum('morning', 'afternoon', name='student_shift_enum'), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    place_of_birth = db.Column(db.String(150), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    roll_no = db.Column(db.String(50), nullable=True)

    price = db.Column(db.Numeric(10, 2), default=0)
    registration_fee = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.Enum('active', 'inactive', 'graduated', 'suspended'), default='active')

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # --- Relationships ---
    # Waxaan u bixinay backref magacyo unique ah si looga baxo "Mapper" error
    student_class = db.relationship('Class', backref='students')
    user = db.relationship("User", backref="student_record")
    parent = db.relationship('Parent', backref=db.backref('children_students', passive_deletes=True))
    school = db.relationship('School', backref=db.backref('all_students', passive_deletes=True))
    branch = db.relationship('Branch', backref=db.backref('branch_student_list', passive_deletes=True))
    class_obj = db.relationship('Class', backref=db.backref('class_student_list', passive_deletes=True))
    level = db.relationship('ClassLevel', backref=db.backref('level_student_list', passive_deletes=True))
    section_rel = db.relationship('Section', backref=db.backref('section_student_list', passive_deletes=True))
    
    # Relationship-ka sanadka (loo bixiyay _rel si uusan ugu dhicin column-ka sare)
    academic_year_rel = db.relationship('AcademicYear', backref=db.backref('year_students', passive_deletes=True))

    # Xiriirka Natiijooyinka (results) - Kani waa kan routes.py looga baahan yahay
    results = db.relationship('StudentExamResult', back_populates='student', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<Student {self.full_name}>"
    

@event.listens_for(Student, 'before_insert')
def set_total_insert(mapper, connection, target):
    target.total = float(target.price or 0) + float(target.registration_fee or 0)

@event.listens_for(Student, 'before_update')
def set_total_update(mapper, connection, target):
    target.total = float(target.price or 0) + float(target.registration_fee or 0)    




# Student Fee Collection
class StudentFeeCollection(db.Model):
    __tablename__ = 'student_fee_collections'

    id = db.Column(db.Integer, primary_key=True)
    
    student_id = db.Column(
        db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False
    )
    class_id = db.Column(
        db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False
    )
    section_id = db.Column(
        db.Integer, db.ForeignKey('sections.id', ondelete='SET NULL'), nullable=True
    )
    school_id = db.Column(
        db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False
    )
    branch_id = db.Column(
        db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True
    )

    # Fee details
    amount_due = db.Column(db.Float, nullable=False, default=0.0)
    amount_paid = db.Column(db.Float, default=0.0, nullable=False)
    remaining_balance = db.Column(db.Float, nullable=False, default=0.0)  # stored column

    payment_status = db.Column(
        db.Enum('Pending', 'Partial', 'Paid', name='payment_status_enum'), default='Pending'
    )
    payment_date = db.Column(db.DateTime, nullable=True)
    remarks = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    student = db.relationship(
        'Student', backref=db.backref('fee_collections', cascade='all, delete-orphan')
    )
    class_obj = db.relationship(
        'Class', backref=db.backref('fee_collections', cascade='all, delete-orphan')
    )
    section = db.relationship(
        'Section', backref=db.backref('fee_collections', cascade='all, delete-orphan')
    )
    school = db.relationship(
        'School', backref=db.backref('fee_collections', cascade='all, delete-orphan')
    )
    branch = db.relationship(
        'Branch', backref=db.backref('fee_collections', passive_deletes=True)
    )

    __table_args__ = (
        db.UniqueConstraint(
            'student_id', 'class_id', 'section_id', 'school_id', 'branch_id',
            name='uq_student_fee'
        ),
    )
    def recalculate(self):
        """Single source of truth"""
        self.remaining_balance = max(0.0, self.amount_due - self.amount_paid)

        if self.amount_paid == 0:
            self.payment_status = 'Pending'
        elif self.amount_paid < self.amount_due:
            self.payment_status = 'Partial'
        else:
            self.payment_status = 'Paid'

     # ---------------- METHODS ----------------
    def update_status(self):
        """Update remaining_balance and payment_status"""
        self.remaining_balance = max(0.0, self.amount_due - self.amount_paid)
        if self.amount_paid == 0:
            self.payment_status = 'Pending'
        elif self.amount_paid < self.amount_due:
            self.payment_status = 'Partial'
        else:
            self.payment_status = 'Paid'

    def __repr__(self):
        return f"<FeeCollection Student:{self.student_id} Due:{self.amount_due} Paid:{self.amount_paid} Remaining:{self.remaining_balance}>"

# ------------------ AUTO CALCULATE AMOUNT DUE ------------------

def calculate_smart_fee(target):
    if target.student_id:
        # Soo qaado ardayga
        student = Student.query.get(target.student_id)
        if student:
            # ✅ HUBI: Ardaygu ma leeyahay biilal hore oo laga dhex helay dugsigan?
            # Haddii uu leeyahay, waxay ka dhigan tahay inuu hore u iska dhiibay Registration.
            previous_fee_exists = StudentFeeCollection.query.filter(
                StudentFeeCollection.student_id == student.id,
                StudentFeeCollection.school_id == target.school_id,
                StudentFeeCollection.id != target.id  # Ha xisaabin biilka hadda la abuurayo
            ).first()

            tuition_fee = float(student.price or 0)
            reg_fee = float(student.registration_fee or 0)

            if previous_fee_exists:
                # ❗ Maadaama uu hore u jiray biil, qaado kaliya Tuition
                target.amount_due = tuition_fee
            else:
                # ❗ Kani waa biilkii u horreeyay, isku dar Tuition + Registration
                target.amount_due = tuition_fee + reg_fee
        else:
            target.amount_due = 0.0
    else:
        target.amount_due = 0.0

    # Xisaabi Payment Status-ka
    update_payment_status(target)


def update_payment_status(target):
    amount_paid = float(target.amount_paid or 0)
    amount_due = float(target.amount_due or 0)

    if amount_paid >= amount_due and amount_due > 0:
        target.payment_status = 'Paid'
    elif 0 < amount_paid < amount_due:
        target.payment_status = 'Partial'
    else:
        target.payment_status = 'Pending'


# ================= EVENT LISTENERS =================

@event.listens_for(StudentFeeCollection, 'before_insert')
def set_amount_due_insert(mapper, connection, target):
    calculate_smart_fee(target)


@event.listens_for(StudentFeeCollection, 'before_update')
def set_amount_due_update(mapper, connection, target):
    # Marka la update-gareynayo, haddii qofku hadda gacanta ku bedelo amount_due
    # ama haddii xogta ardayga isbedeshay, dib u xisaabi status-ka.
    update_payment_status(target)

# Fee Invoice
# ============================
# Fee Invoice Model
# ============================
class FeeInvoice(db.Model):
    __tablename__ = "fee_invoices"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign key to StudentFeeCollection
    student_fee_id = db.Column(
        db.Integer,
        db.ForeignKey('student_fee_collections.id', ondelete='CASCADE'),
        nullable=False
    )

    school_id = db.Column(
        db.Integer,
        db.ForeignKey('schools.id', ondelete='CASCADE'),
        nullable=False
    )

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey('branches.id', ondelete='SET NULL'),
        nullable=True
    )

    invoice_number = db.Column(db.String(50), nullable=False, unique=True)

    type = db.Column(
        db.Enum('Registration', 'Tuition', 'Credit Memo', name='invoice_type_enum'),
        nullable=False
    )

    date_issued = db.Column(db.DateTime, default=now_eat)

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    amount_due = db.Column(db.Float, nullable=False, default=0.0)
    amount_paid = db.Column(db.Float, nullable=False, default=0.0)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    remaining_balance = db.Column(db.Float, nullable=False, default=0.0)
    balance = db.Column(db.Float, nullable=False, default=0.0)

    receipt_url = db.Column(db.String(255), nullable=True)
    receipt_amount = db.Column(db.Numeric(10, 2), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    extra_info = db.Column(db.String(255), nullable=True)

    # ---------------- RELATIONSHIPS ----------------

    fee_collection = db.relationship(
        'StudentFeeCollection',
        backref=db.backref('invoices', cascade='all, delete-orphan')
    )

    school = db.relationship(
        'School',
        backref=db.backref('fee_invoices', cascade='all, delete-orphan')
    )

    branch = db.relationship(
        'Branch',
        backref=db.backref('fee_invoices', passive_deletes=True)
    )

    # ---------------- METHODS ----------------

    def update_remaining_balance(self):
        self.remaining_balance = max(0.0, self.total_amount - self.amount_paid)
        self.balance = self.remaining_balance

    def calculate(self):
        self.update_remaining_balance()

    def __repr__(self):
        return f"<FeeInvoice #{self.invoice_number} Type:{self.type} Paid:{self.amount_paid} Remaining:{self.remaining_balance}>"



# Student Attendance
class StudentAttendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    student_id = db.Column(
        db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False
    )
    school_id = db.Column(
        db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False
    )
    branch_id = db.Column(
        db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True
    )
    class_id = db.Column(
        db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False
    )
    section_id = db.Column(
        db.Integer, db.ForeignKey('sections.id', ondelete='SET NULL'), nullable=True
    )
    teacher_id = db.Column(
        db.Integer, db.ForeignKey('teachers.id', ondelete='SET NULL'), nullable=True
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False
    )

    date = db.Column(db.Date, nullable=False)
    status = db.Column(
        ENUM('present', 'absent', 'late', 'excused'), nullable=False
    )

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ================= RELATIONSHIPS =================
    student = db.relationship('Student', backref=db.backref('attendances', cascade='all, delete-orphan'))
    school = db.relationship('School', backref=db.backref('attendances', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('attendances', passive_deletes=True))
    class_obj = db.relationship('Class', backref=db.backref('attendances', cascade='all, delete-orphan'))
    section = db.relationship('Section', backref=db.backref('attendances', cascade='all, delete-orphan'))
    teacher = db.relationship('Teacher', backref=db.backref('attendances', cascade='all, delete-orphan'))
    subject = db.relationship('Subject', backref=db.backref('attendances', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint(
            'student_id', 'date', 'subject_id', 'school_id', 'branch_id', 'class_id', 'section_id',
            name='uq_student_date_subject'
        ),
    )

    def __repr__(self):
        return f"<Attendance Student:{self.student_id} Date:{self.date} Status:{self.status}>"


# ================= AcademicYear Model =================
class AcademicYear(db.Model):
    __tablename__ = 'academic_years'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    year_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=now_eat)
    updated_at = db.Column(db.TIMESTAMP, default=now_eat, onupdate=now_eat)

    # ================= Relationships =================
    school = db.relationship('School', backref=db.backref('academic_years', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('academic_years', passive_deletes=True))

    # ================= Unique Constraint =================
    __table_args__ = (
        UniqueConstraint('school_id', 'branch_id', 'year_name', name='uq_school_branch_year'),
    )

    def __repr__(self):
        return f"<AcademicYear {self.year_name} School:{self.school_id} Branch:{self.branch_id}>"


# Term
class Term(db.Model):
    __tablename__ = 'terms'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ----------------- Foreign Keys -----------------
    school_id = db.Column(
        db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False
    )
    branch_id = db.Column(
        db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True
    )
    academic_year_id = db.Column(
        db.Integer, db.ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False
    )

    # ----------------- Term Info -----------------
    term_name = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=False)

    # ----------------- Timestamps -----------------
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ----------------- Relationships -----------------
    school = db.relationship('School', backref=db.backref('terms', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('terms', passive_deletes=True))
    academic_year = db.relationship('AcademicYear', backref=db.backref('terms', cascade='all, delete-orphan'))

    # ----------------- Unique Constraint -----------------
    __table_args__ = (
        db.UniqueConstraint(
            'school_id', 'branch_id', 'academic_year_id', 'term_name',
            name='uq_school_branch_academicyear_term'
        ),
    )

    def __repr__(self):
        return f"<Term {self.term_name} Year:{self.academic_year_id} School:{self.school_id} Branch:{self.branch_id}>"


# Exam
class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ----------------- Foreign Keys -----------------
    school_id = db.Column(
        db.Integer,
        db.ForeignKey('schools.id', ondelete='CASCADE'),
        nullable=False
    )

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey('branches.id', ondelete='SET NULL'),
        nullable=True
    )

    academic_year_id = db.Column(
        db.Integer,
        db.ForeignKey('academic_years.id', ondelete='CASCADE'),
        nullable=False
    )

    term_id = db.Column(
        db.Integer,
        db.ForeignKey('terms.id', ondelete='CASCADE'),
        nullable=False
    )

    # ----------------- Exam Info -----------------
    exam_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    status = db.Column(
        db.Enum('draft', 'published', 'closed', name='exam_status'),
        default='draft',
        nullable=False
    )

    # ----------------- Timestamps -----------------
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ----------------- Relationships (FIXED) -----------------

    school = db.relationship(
        'School',
        backref=db.backref('exams', passive_deletes=True)
    )

    branch = db.relationship(
        'Branch',
        backref=db.backref('exams', passive_deletes=True)
    )

    academic_year = db.relationship(
        'AcademicYear',
        backref=db.backref('exams', passive_deletes=True)
    )

    term = db.relationship(
        'Term',
        backref=db.backref('exams', passive_deletes=True)
    )

    # ----------------- Unique Constraint -----------------
    __table_args__ = (
        db.UniqueConstraint(
            'school_id',
            'branch_id',
            'academic_year_id',
            'term_id',
            'exam_name',
            name='uq_school_branch_year_term_exam'
        ),
    )

    def __repr__(self):
        return (
            f"<Exam {self.exam_name} "
            f"Term:{self.term_id} Year:{self.academic_year_id} "
            f"School:{self.school_id} Branch:{self.branch_id}>"
        )

# Exam Timetable
class ExamTimetable(db.Model):
    """
    Exam timetable for each class level.
    One timetable per level, school, branch, exam, and subject.
    """
    __tablename__ = 'exam_timetables'

    id = db.Column(db.Integer, primary_key=True)
    
    school_id = db.Column(
        db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False
    )
    branch_id = db.Column(
        db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey('exams.id', ondelete='CASCADE'),
        nullable=False
    )
    
    level_id = db.Column(
        db.Integer,
        db.ForeignKey('class_levels.id', ondelete='CASCADE'),
        nullable=False
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey('subjects.id', ondelete='CASCADE'),
        nullable=False
    )

    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Prevent duplicate timetable for same exam + level + subject + date
    __table_args__ = (
        db.UniqueConstraint('exam_id', 'level_id', 'subject_id', 'date', name='uq_exam_level_subject_date'),
    )

    school = db.relationship('School', backref=db.backref('timetables', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('timetables', passive_deletes=True))

    # ================= RELATIONSHIPS =================
    exam = db.relationship(
        'Exam',
        backref=db.backref('timetables', cascade='all, delete-orphan')
    )

    level = db.relationship(
        'ClassLevel',
        backref=db.backref('timetables', cascade='all, delete-orphan')
    )

    subject = db.relationship(
        'Subject',
        backref=db.backref('timetables', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return f"<ExamTimetable Exam:{self.exam_id} Level:{self.level_id} Subject:{self.subject_id} Date:{self.date}>"


# Exam Hall
class ExamHall(db.Model):
    __tablename__ = 'exam_halls'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    
    name = db.Column(db.String(100), nullable=False)  # Magaca hall-ka
    capacity = db.Column(db.Integer, nullable=False)  # Tirada ardayda qaadi karta

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    school = db.relationship('School', backref=db.backref('exam_halls', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('exam_halls', passive_deletes=True))

    def __repr__(self):
        return f"<ExamHall {self.name} Capacity:{self.capacity}>"



class ExamHallAssignment(db.Model):
    __tablename__ = 'exam_hall_assignments'

    id = db.Column(db.Integer, primary_key=True)

    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)

   

    hall_id = db.Column(
        db.Integer,
        db.ForeignKey('exam_halls.id', ondelete='CASCADE'),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('students.id', ondelete='CASCADE'),
        nullable=False
    )

    class_id = db.Column(
        db.Integer,
        db.ForeignKey('classes.id', ondelete='CASCADE'),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    school = db.relationship('School', backref=db.backref('hall_assignments', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('hall_assignments', passive_deletes=True))

    student = db.relationship('Student', backref=db.backref('hall_assignments', cascade='all, delete-orphan'))
    class_obj = db.relationship('Class', backref=db.backref('hall_assignments', cascade='all, delete-orphan'))

    hall = db.relationship('ExamHall', backref=db.backref('hall_assignments', cascade='all, delete-orphan'))

    # ✅ Prevent duplicate student assignment in same exam
    

    def __repr__(self):
        return f"<Assignment Student:{self.student_id} Hall:{self.hall_id}>"


class ExamTicket(db.Model):
    __tablename__ = 'exam_tickets'

    id = db.Column(db.Integer, primary_key=True)

    # ----------------- Foreign Keys -----------------
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'))

    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id', ondelete='CASCADE'), nullable=False)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)

    hall_id = db.Column(db.Integer, db.ForeignKey('exam_halls.id', ondelete='SET NULL'))
    # ----------------- Ticket Info -----------------
    ticket_number = db.Column(db.String(100), unique=True, nullable=False)

    # ----------------- Status -----------------
    status = db.Column(db.Enum('active', 'used', 'cancelled', name='ticket_status'), default='active')

    # ----------------- Timestamps -----------------
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ----------------- Constraints -----------------
    __table_args__ = (
        db.UniqueConstraint('exam_id', 'student_id', name='uq_ticket_student_exam'),
    )

    # ----------------- Relationships -----------------
    school = db.relationship('School', backref=db.backref('exam_tickets', cascade='all, delete-orphan'))
    branch = db.relationship('Branch', backref=db.backref('exam_tickets', passive_deletes=True))

    exam = db.relationship('Exam', backref=db.backref('exam_tickets', cascade='all, delete-orphan'))

    student = db.relationship('Student', backref=db.backref('exam_tickets', cascade='all, delete-orphan'))
    class_obj = db.relationship('Class', backref=db.backref('exam_tickets', cascade='all, delete-orphan'))

    hall = db.relationship('ExamHall', backref=db.backref('exam_tickets', passive_deletes=True))

    # ----------------- Representation -----------------
    def __repr__(self):
        return f"<ExamTicket ID:{self.id} Student:{self.student_id}>"

#------ ExamSubject
#------ ExamSubject
class ExamSubject(db.Model):
    __tablename__ = 'exam_subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    
    # MUHIIM: Waxaan ku darnay class_id si loogu xiro fasalka saxda ah
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)

    total_marks = db.Column(db.Numeric(10, 2), nullable=False)
    pass_marks = db.Column(db.Numeric(10, 2), nullable=False)

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    school = db.relationship('School', backref=db.backref('exam_subjects_list', cascade='all, delete-orphan', passive_deletes=True))
    exam = db.relationship('Exam', backref=db.backref('exam_subjects', cascade='all, delete-orphan', passive_deletes=True))
    subject = db.relationship('Subject', backref=db.backref('exam_subjects', cascade='all, delete-orphan', passive_deletes=True))
    # Relationship-ka fasalka
    class_name = db.relationship('Class', backref=db.backref('exam_subjects', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('exam_id', 'subject_id', 'class_id', 'academic_year_id', 'branch_id', name='uq_exam_subject_full_logic'),
    )





# =========================
# Student Exam Marks
# =========================
class StudentExamMark(db.Model):
    __tablename__ = 'student_exam_marks'

    id = db.Column(db.Integer, primary_key=True)

    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)

    academic_year_id = db.Column(
        db.Integer,
        db.ForeignKey('academic_years.id', ondelete='CASCADE'),
        nullable=False
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey('exams.id', ondelete='CASCADE'),
        nullable=False
    )

    exam_subject_id = db.Column(
        db.Integer,
        db.ForeignKey('exam_subjects.id', ondelete='CASCADE'),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('students.id', ondelete='CASCADE'),
        nullable=False
    )

    marks_obtained = db.Column(db.Numeric(10, 2), nullable=False)

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ---------------- RELATIONSHIPS ----------------

    school = db.relationship('School', backref='student_exam_marks')

    branch = db.relationship('Branch', backref='student_exam_marks')

    academic_year = db.relationship(
        'AcademicYear',
        backref=db.backref('student_exam_marks', passive_deletes=True)
    )

    exam = db.relationship(
        'Exam',
        backref=db.backref('student_exam_marks', passive_deletes=True)
    )

    exam_subject = db.relationship(
        'ExamSubject',
        backref='student_exam_marks'
    )

    student = db.relationship(
        'Student',
        backref='exam_marks'
    )

# =========================
# Student Exam Results
# =========================

class StudentExamResult(db.Model):
    __tablename__ = 'student_exam_results'

    id = db.Column(db.Integer, primary_key=True)

    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)

    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)

    academic_year_id = db.Column(
        db.Integer,
        db.ForeignKey('academic_years.id', ondelete='CASCADE'),
        nullable=False
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey('exams.id', ondelete='CASCADE'),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('students.id', ondelete='CASCADE'),
        nullable=False
    )

    class_id = db.Column(
        db.Integer,
        db.ForeignKey('classes.id', ondelete='CASCADE'),
        nullable=False
    )

    section_id = db.Column(
        db.Integer,
        db.ForeignKey('sections.id', ondelete='SET NULL'),
        nullable=True
    )

    total_marks = db.Column(db.Numeric(10, 2), nullable=False)
    average = db.Column(db.Numeric(10, 2), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    decision = db.Column(db.String(20), nullable=False)
    published = db.Column(db.String(20), default='pending')

    class_position = db.Column(db.Integer)
    section_position = db.Column(db.Integer)
    school_position = db.Column(db.Integer)
    count_subjects = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ---------------- RELATIONSHIPS ----------------

    school = db.relationship('School', backref='exam_results')

    branch = db.relationship('Branch', backref='exam_results')

    academic_year = db.relationship(
        'AcademicYear',
        backref=db.backref('exam_results', passive_deletes=True)
    )

    exam = db.relationship(
        'Exam',
        backref=db.backref('exam_results', passive_deletes=True)
    )

    student = db.relationship(
        'Student',
        backref='exam_results'
    )

    class_rel = db.relationship('Class', backref='exam_results')

    section = db.relationship('Section', backref='exam_results')

# ==========================================
# Student Promotion Model (History & Tracking)
# ==========================================
class StudentPromotion(db.Model):
    __tablename__ = 'student_promotions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)

    # FROM STATE
    from_class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    from_section_id = db.Column(db.Integer, db.ForeignKey('sections.id', ondelete='SET NULL'), nullable=True)
    from_academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False)

    # TO STATE
    to_class_id = db.Column(db.Integer, db.ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    to_section_id = db.Column(db.Integer, db.ForeignKey('sections.id', ondelete='SET NULL'), nullable=True)
    to_academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False)

    # Promotion Details
    promotion_type = db.Column(
        db.Enum('regular', 'double', 'repeat', 'trial', name='promo_type_enum'),
        default='regular'
    )

    decision_by_exam_id = db.Column(
        db.Integer,
        db.ForeignKey('exams.id', ondelete='SET NULL'),
        nullable=True
    )

    remarks = db.Column(db.Text, nullable=True)

    promoted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    promotion_date = db.Column(db.DateTime, default=now_eat)

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ----------------- RELATIONSHIPS -----------------

    school = db.relationship(
        'School',
        backref=db.backref('promotions', cascade='all, delete-orphan')
    )

    student = db.relationship(
        'Student',
        backref=db.backref('promotions', cascade='all, delete-orphan')
    )

    # Class relationships
    from_class = db.relationship('Class', foreign_keys=[from_class_id])
    to_class = db.relationship('Class', foreign_keys=[to_class_id])

    # Section relationships
    from_section = db.relationship('Section', foreign_keys=[from_section_id])
    to_section = db.relationship('Section', foreign_keys=[to_section_id])

    # 🔥 IMPORTANT FIX (THIS WAS YOUR ERROR SOURCE)

    from_year = db.relationship(
        'AcademicYear',
        foreign_keys=[from_academic_year_id],
        backref=db.backref('promotions_from', passive_deletes=True)
    )

    to_year = db.relationship(
        'AcademicYear',
        foreign_keys=[to_academic_year_id],
        backref=db.backref('promotions_to', passive_deletes=True)
    )

    def __repr__(self):
        return f"<Promotion Student:{self.student_id} From:{self.from_class_id} To:{self.to_class_id}>"


class ExamPaper(db.Model):
    __tablename__ = 'exam_papers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)
    exam_subject_id = db.Column(db.Integer, db.ForeignKey('exam_subjects.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    
    duration_minutes = db.Column(db.Integer, nullable=False, default=60)
    instructions = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum('draft', 'published', 'closed', name='paper_status_enum'), default='draft')
    
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # ✅ Relationships
    # Ku dar kani si uu u xaliyo 'UndefinedError: paper object has no attribute teacher'
    teacher = db.relationship(
        'Teacher', 
        backref=db.backref('exam_papers', cascade='all, delete-orphan')
    )

    exam_subject = db.relationship(
        'ExamSubject',
        backref=db.backref('papers', cascade='all, delete-orphan')
    )

    questions = db.relationship(
        'ExamQuestion',
        back_populates='paper',
        cascade='all, delete-orphan'
    )

    @property
    def paper_total_marks(self):
        return self.exam_subject.total_marks if self.exam_subject else 0

    @property
    def current_questions_marks(self):
        return sum(q.marks for q in self.questions)

    def __repr__(self):
        return f"<ExamPaper ID:{self.id} Status:{self.status}>"


class ExamQuestion(db.Model):
    __tablename__ = 'exam_questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('exam_papers.id', ondelete='CASCADE'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)

    # 1. Question Details
    question_type = db.Column(db.Enum('mcq', 'true_false', 'direct', name='question_type_enum'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_image = db.Column(db.String(255), nullable=True)
    marks = db.Column(db.Numeric(5, 2), nullable=False, default=1.0)
    
    # 2. Options & Answers
    options = db.Column(db.JSON, nullable=True) # MCQ Options
    correct_answer = db.Column(db.Text, nullable=False)
    
    # --- WAXA KA DHIMAN EE SOCRATIVE-KA AH ---
    
    # 3. Explanation (Feedback): Markuu ardaygu jawaabo, maxaa loo sheegayaa?
    explanation = db.Column(db.Text, nullable=True)

    # 4. Question Order: Si loo ogaado su'aashu inay tahay 1aad, 2aad, iwm.
    sort_order = db.Column(db.Integer, default=0)

    # 5. Time Limit: Haddii su'aashan la rabo in muddo gaar ah la dhex fadhiyo (ilbiriqsiyo)
    time_limit = db.Column(db.Integer, nullable=True) 

    # 6. Randomize Options: Ma la rabaa in 'A, B, C' la kala beddelo arday kasta?
    shuffle_options = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships (Sidayadii)
    paper = db.relationship('ExamPaper', back_populates='questions')
    school = db.relationship('School', backref=db.backref('all_questions', passive_deletes=True))
    branch = db.relationship('Branch', backref=db.backref('branch_questions'))

    def __repr__(self):
        return f"<Question {self.id} | Type: {self.question_type}>"




class StudentResponse(db.Model):
    __tablename__ = 'student_responses'
    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('exam_papers.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('exam_questions.id'))
    
    selected_option = db.Column(db.Text) # Jawaabta uu doortay
    is_correct = db.Column(db.Boolean)   # Inuu saxay iyo in kale
    time_taken = db.Column(db.Integer)   # Immisa ilbiriqsi ayay ku qaadatay?








# -------------------------------------
# 4. Settings Data Model Table --------
# ------------------------------------- 
class SettingsData(db.Model):
    __tablename__ = 'settings_data'

    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(255), nullable=False)
    system_name = db.Column(db.String(255), nullable=True)  # New column
    address = db.Column(db.String(255), nullable=False)
    short_desc = db.Column(db.Text, nullable=True)
    long_desc = db.Column(db.Text, nullable=True)
    head_image = db.Column(db.String(255), nullable=True)
    image_success = db.Column(db.String(255), nullable=True)
    about_image = db.Column(db.String(255), nullable=True)
    success_desc = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    phone1 = db.Column(db.String(15), nullable=False)
    phone2 = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    facebook = db.Column(db.String(255), nullable=True)
    twitter = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(255), nullable=True)
    dribbble = db.Column(db.String(255), nullable=True)
    logo = db.Column(db.String(255), nullable=True)
    logo2 = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    def __repr__(self):
        return f"<SettingsData {self.id}>"



# -------------------------------
# ------ School Site Settings Model ------------
# -------------------------------
class SchoolSiteSettings(db.Model):
    __tablename__ = 'school_site_settings'
    
    id = db.Column(db.Integer, primary_key=True)

    # Link to School
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id', ondelete='CASCADE'), nullable=False)
    
    # Optional link to Branch
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id', ondelete='SET NULL'), nullable=True)

    # Site settings fields
    main_logo = db.Column(db.String(255), nullable=True)   # Main logo
    sub_logo = db.Column(db.String(255), nullable=True)    # Secondary logo
    sign_logo = db.Column(db.String(255), nullable=True)    # Secondary logo
    site_title = db.Column(db.String(255), nullable=True)  # Optional site title
    short_desc = db.Column(db.Text, nullable=True)
    long_desc = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    facebook = db.Column(db.String(255), nullable=True)
    twitter = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=now_eat)
    updated_at = db.Column(db.DateTime, default=now_eat, onupdate=now_eat)

    # Relationships
    school = db.relationship('School', backref=db.backref('site_settings', lazy=True, uselist=False))
    branch = db.relationship('Branch', backref=db.backref('site_settings', lazy=True, uselist=False))

    def __repr__(self):
        return f"<SchoolSiteSettings school_id={self.school_id} branch_id={self.branch_id}>"

 


