import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import json
import time
from backend.models.industry import RegisterRequest, LoginRequest
from backend.services.otp_service import generate_and_send_otp, verify_otp_code, is_official_work_email
from backend.services.email_service import get_sent_emails
from backend.services.sheet_service import get_sheet_records, get_csv_export_path
from backend.services.auth_store import register_user, login_user, update_student_profile

def test_full_pipeline():
    print("==================================================")
    print("Starting Comprehensive E2E Verification...")
    print("==================================================")

    # 1. Official Email Validator Tests
    print("\n--- 1. Testing Official Email Validation ---")
    assert is_official_work_email("director@iitb.ac.in") == True
    assert is_official_work_email("recruiter@google.com") == True
    assert is_official_work_email("student@gmail.com") == False
    assert is_official_work_email("john.doe@gmail.com") == False
    assert is_official_work_email("admin@yahoo.com") == False
    print("  [OK] Official work & institutional email validation rules working properly!")

    # 2. OTP Generation & Verification Tests
    print("\n--- 2. Testing OTP Generation & Verification ---")
    ts = int(time.time())
    student_email = f"alex.coder_{ts}@gmail.com"
    student_username = f"alexchen_{ts}"
    msg, otp_code = generate_and_send_otp(student_email, "student", "Alex Chen")
    assert len(otp_code) == 6
    assert otp_code.isdigit()
    print(f"  [OK] Generated 6-digit OTP for {student_email}: {otp_code}")

    # Verify invalid OTP fails
    assert verify_otp_code(student_email, "000000") == False
    print("  [OK] Invalid OTP correctly rejected")

    # Verify valid OTP passes
    assert verify_otp_code(student_email, otp_code) == True
    print("  [OK] Valid OTP verified successfully")

    # 3. Student Registration & Profile Builder
    print("\n--- 3. Testing Student Registration with College & Target Companies ---")
    student_reg = RegisterRequest(
        name="Alex Chen",
        username=student_username,
        email=student_email,
        password="SecurePassword123!",
        role="student",
        college="IIT Bombay (Indian Institute of Technology)",
        degree="B.Tech Computer Science & Engineering",
        graduation_year="2026",
        target_companies="Google, Microsoft, Amazon, DeepMind",
        target_role="AI / ML Systems Engineer",
        preferred_work_mode="Remote / Hybrid",
        expected_stipend="Rs 45,000 / month",
        resume_url="/resumes/alex_chen_resume.pdf",
        resume_filename="alex_chen_resume.pdf",
        otp_code=otp_code,
    )
    reg_student_res = register_user(student_reg)
    registered_student = reg_student_res.user
    assert registered_student.id.startswith("usr-")
    assert registered_student.email == student_email
    print(f"  [OK] Student registered: {registered_student.name} ({registered_student.id})")

    # 4. Institute Registration with Official Email & OTP
    print("\n--- 4. Testing Institute Registration ---")
    inst_email = f"dean.placements_{ts}@iitb.ac.in"
    _, inst_otp = generate_and_send_otp(inst_email, "institute", "Dr. Ramesh Sharma")
    verify_otp_code(inst_email, inst_otp)
    inst_reg = RegisterRequest(
        name="Dr. Ramesh Sharma",
        username=f"iitb_placements_{ts}",
        email=inst_email,
        password="InstitutePass2026!",
        role="institute",
        institute_name="IIT Bombay (Indian Institute of Technology)",
        college="IIT Bombay (Indian Institute of Technology)",
        department="Department of Computer Science & Engineering",
        designation="Head of Training & Placement",
        location="Powai, Mumbai",
        otp_code=inst_otp,
    )
    reg_inst_res = register_user(inst_reg)
    registered_inst = reg_inst_res.user
    assert registered_inst.is_official_email == True
    print(f"  [OK] Institute registered with verified official domain: {registered_inst.institute_name}")

    # 5. Industry Registration with Official Work Domain & OTP
    print("\n--- 5. Testing Industry Partner Registration ---")
    ind_email = f"recruiter_{ts}@deepmind-labs.com"
    _, ind_otp = generate_and_send_otp(ind_email, "industry", "Sarah Connor")
    verify_otp_code(ind_email, ind_otp)
    ind_reg = RegisterRequest(
        name="Sarah Connor",
        username=f"deepmind_recruiter_{ts}",
        email=ind_email,
        password="IndustryPass2026!",
        role="industry",
        company_name="DeepMind Innovations",
        industry_sector="Artificial Intelligence & Cloud",
        designation="Senior Technical Talent Lead",
        location="Bengaluru / Global",
        otp_code=ind_otp,
    )
    reg_ind_res = register_user(ind_reg)
    registered_ind = reg_ind_res.user
    assert registered_ind.is_official_email == True
    print(f"  [OK] Industry registered with verified work domain: {registered_ind.company_name}")

    # 6. Login Authentication (Username or Email + Password)
    print("\n--- 6. Testing Login by Username & Email ---")
    # Login by Username
    login_user_res = login_user(LoginRequest(identifier=student_username, password="SecurePassword123!"))
    assert login_user_res.user.id == registered_student.id
    print(f"  [OK] Successfully logged in with Username '{student_username}'")

    # Login by Email
    login_email_res = login_user(LoginRequest(identifier=student_email, password="SecurePassword123!"))
    assert login_email_res.user.id == registered_student.id
    print(f"  [OK] Successfully logged in with Email '{student_email}'")

    # 7. Thank-You & Welcome Email Verification
    print("\n--- 7. Verifying Thank-You / Welcome Emails Dispatched ---")
    sent_emails = get_sent_emails()
    assert len(sent_emails) >= 3
    student_welcome = next((e for e in sent_emails if e.get("to") == student_email and e.get("type") == "WELCOME_THANK_YOU"), None)
    assert student_welcome is not None
    assert "Thank You" in student_welcome["subject"]
    print(f"  [OK] Thank-You Welcome email successfully sent and logged for {student_email}")
    print(f"    Subject: {student_welcome['subject']}")

    # 8. Google Sheet & CSV Sync Verification
    print("\n--- 8. Verifying Google Sheet & Excel Data Record Sync ---")
    sheet_records = get_sheet_records()
    assert len(sheet_records) >= 3
    csv_path = get_csv_export_path()
    assert os.path.exists(csv_path)

    # Inspect student record in sheet
    alex_record = next((r for r in sheet_records if r.get("email") == student_email), None)
    assert alex_record is not None
    assert "Google, Microsoft, Amazon, DeepMind" in alex_record["target_companies_and_roles"]
    assert "alex_chen_resume.pdf" in alex_record["resume"]
    print(f"  [OK] Student row verified in CSV & Google Sheet store with target companies and resume link!")
    print(f"    CSV Path: {csv_path}")
    print(f"    Target Companies and Role: {alex_record['target_companies_and_roles']}")
    print(f"    Resume Record: {alex_record['resume']}")
    print(f"    Total Registered Users in Sheet: {len(sheet_records)}")

    print("\n==================================================")
    print("ALL E2E VERIFICATIONS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_full_pipeline()
