from datetime import datetime

from googletrans import Translator



def get_academic_year():
    """Return current academic year in format '2026 - 2027'."""
    year = datetime.now().year
    return f"{year} - {year + 1}"


# utils.py
translator = Translator()

def translate_to_somali(text):
    """
    English text dynamically ugu beddel Af-Soomaali.
    Haddii text-ka uu already Somali yahay ama translation fails, text-ka as-is ayuu ahaanayaa.
    """
    if not text:
        return ""
    
    try:
        result = translator.translate(text, src='en', dest='so')
        return result.text
    except Exception as e:
        print("Translation error:", e)
        return text




def auto_charge_monthly_fees():
    # IMPORT-KA U GUURI HALKAN (LOCAL IMPORT)
    from app import db, app 
    from app.modal import Student, StudentFeeCollection, FeeInvoice

    with app.app_context():
        # 1. Hel taariikhda bisha hadda
        now = datetime.now()
        current_month = now.strftime('%B')
        current_year = now.strftime('%Y')
        
        # 2. Hel dhammaan ardayda firfircoon
        students = Student.query.filter_by(status=1).all()
        
        for student in students:
            # 3. Hubi haddii bishaan horay loogu dalacay
            already_charged = StudentFeeCollection.query.filter(
                StudentFeeCollection.student_id == student.id,
                StudentFeeCollection.description.contains(f"{current_month} {current_year}")
            ).first()
            
            if not already_charged:
                # 4. Hel BAAQIGII HORE (Balance-ka ugu dambeeya)
                last_fee = StudentFeeCollection.query.filter_by(student_id=student.id)\
                    .order_by(StudentFeeCollection.id.desc()).first()
                
                previous_balance = float(last_fee.remaining_balance) if last_fee else 0.0
                monthly_tuition = float(student.price or 0)
                new_balance = previous_balance + monthly_tuition
                
                # 5. Samaynta Record Cusub (Collection)
                new_collection = StudentFeeCollection(
                    student_id=student.id,
                    school_id=student.school_id,
                    branch_id=student.branch_id,
                    amount_due=monthly_tuition,
                    amount_paid=0,
                    remaining_balance=new_balance,
                    payment_status='Pending',
                    payment_date=now,
                    description=f"Monthly Fee - {current_month} {current_year}"
                )
                db.session.add(new_collection)
                db.session.flush() # Hel ID-ga
                
                # 6. Samaynta Invoice (Si ay ugu muuqato report-ka)
                new_invoice = FeeInvoice(
                    student_fee_id=new_collection.id,
                    school_id=student.school_id,
                    branch_id=student.branch_id,
                    invoice_number=f"INV-{new_collection.id}-{now.timestamp()}",
                    type='Tuition',
                    amount_due=monthly_tuition,
                    amount_paid=0,
                    balance=new_balance,
                    description=f"Monthly Tuition Fee for {current_month} {current_year}"
                )
                db.session.add(new_invoice)
        
        db.session.commit()
        print(f"✅ Automated Billing completed for {len(students)} students.")




