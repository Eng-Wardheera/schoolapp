import csv
from decimal import Decimal
from email import parser
import io
import string
from pandas import read_csv 
import pandas as pd
from flask_mail import Message
from math import ceil
import os
import random
import re
from sqlite3 import IntegrityError
import uuid
import pycountry
import qrcode
from datetime import date, datetime, timedelta
import pytz
from flask import Blueprint, Response, current_app, flash, g, jsonify, render_template, request, redirect, send_file, session, url_for
from flask_login import login_user, login_required, current_user
import requests
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy import Integer, cast, extract, func
from app import UPLOAD_FOLDER, db, ALLOWED_EXTENSIONS
from app import mail
from app import google 
from app import github 
import phonenumbers
from phonenumbers import NumberParseException, PhoneMetadata, parse, is_valid_number, format_number, PhoneNumberFormat
from app.modal import (Branch, Class, ClassLevel, ClassSubject, Parent, Permission, Role, RolePermission, School, SchoolSiteSettings, Section, SettingsData, SomaliaLocation, Student, Subject, Teacher,User, UserLog, UserPermission, UserRole)
from app.view import BranchForm, ChangePasswordForm, ClassForm, ClassLevelForm, ClassSubjectForm, ForgotPasswordChangeForm, ForgotPasswordForm, LoginForm, ParentForm, RegisterForm, SchoolForm, SchoolSiteSettingsForm, SectionForm, SettingsDataForm, SomaliaLocationForm, StudentForm, SubjectForm, TeacherForm, UserForm, UserProfileForm, VerifyOTPForm 
 
zp = Blueprint('sub', __name__)










