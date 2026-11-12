import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.department import Department, StaffDepartmentAssignment
from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketReply, TicketInternalNote, TicketEvent
from app.models.knowledge import FAQ, ServiceLink, KnowledgeDocument, DocumentChunk, ContentStatus
from app.models.notice import Notice
from app.services.embedding_service import embedding_service
from app.config import settings

def init_db_data():
    db: Session = SessionLocal()
    try:
        if db.query(Department).first():
            db.close()
            return  # Already seeded

        print("Seeding initial university data...")

        # 1. Seed Departments
        depts_data = [
            {"code": "IT", "name": "IT & LMS Support Division", "description": "Student email, campus WiFi, portal access and LMS maintenance.", "email": "helpdesk@apex.edu.lk"},
            {"code": "ADMISSIONS", "name": "Admissions & UGC Registration", "description": "UGC student intake, degree registration, and minimum entry requirements.", "email": "admissions@apex.edu.lk"},
            {"code": "ACADEMICS", "name": "Examinations & Academic Affairs", "description": "Course registration, grading disputes, semester calendars, and deferments.", "email": "academics@apex.edu.lk"},
            {"code": "WELFARE", "name": "Student Welfare & Mahapola Division", "description": "Mahapola scholarship vouchers, bursaries, student loans, and accommodation.", "email": "welfare@apex.edu.lk"},
            {"code": "LIBRARY", "name": "Main Campus Library Services", "description": "Book reservations, catalog inquiries, study cubicles, and fine clearances.", "email": "library@apex.edu.lk"},
            {"code": "GENERAL", "name": "General Student Affairs", "description": "Campus facilities, student identification cards, and general inquiries.", "email": "info@apex.edu.lk"},
        ]
        dept_map = {}
        for d in depts_data:
            dept = Department(**d)
            db.add(dept)
            db.commit()
            db.refresh(dept)
            dept_map[d["code"]] = dept

        # 2. Seed Users
        # Admin
        admin = User(
            email="admin@apex.edu.lk",
            hashed_password=get_password_hash("admin123"),
            full_name="University Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)

        # Staff
        staff = User(
            email="staff@apex.edu.lk",
            hashed_password=get_password_hash("staff123"),
            full_name="Dr. Priyantha Alwis",
            role=UserRole.STAFF,
            department_id=dept_map["IT"].id,
            is_active=True,
        )
        db.add(staff)

        # Students
        student1 = User(
            email="student@apex.edu.lk",
            hashed_password=get_password_hash("student123"),
            full_name="Kasun Jayasundara",
            role=UserRole.STUDENT,
            student_index="2026/SE/048",
            faculty="Faculty of Computing",
            is_active=True,
        )
        db.add(student1)

        student2 = User(
            email="sanduni@apex.edu.lk",
            hashed_password=get_password_hash("student123"),
            full_name="Sanduni Perera",
            role=UserRole.STUDENT,
            student_index="2026/BM/102",
            faculty="Faculty of Business",
            is_active=True,
        )
        db.add(student2)
        db.commit()
        db.refresh(admin)
        db.refresh(staff)
        db.refresh(student1)
        db.refresh(student2)

        # 3. Seed Staff Assignment
        db.add(StaffDepartmentAssignment(
            staff_id=staff.id,
            department_id=dept_map["IT"].id,
            role_title="Senior IT Support Engineer",
            is_primary=True,
        ))

        # 4. Seed Support Tickets
        t1 = Ticket(
            ticket_number="APX-2026-0001",
            student_id=student1.id,
            department_id=dept_map["WELFARE"].id,
            subject="Mahapola Scholarship voucher collection schedule for June",
            description="I was unable to collect the June Mahapola voucher during the primary distribution window. Can I know the alternate collection dates at the Welfare division?",
            category="mahapola",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
        )
        db.add(t1)

        t2 = Ticket(
            ticket_number="APX-2026-0002",
            student_id=student1.id,
            department_id=dept_map["IT"].id,
            assigned_staff_id=staff.id,
            subject="LMS account locked after multiple failed password attempts",
            description="My Student LMS account displays 'Account Locked: Error 401' when attempting to submit the software engineering assignment. Please unlock my credentials.",
            category="it_support",
            priority=TicketPriority.HIGH,
            status=TicketStatus.IN_PROGRESS,
        )
        db.add(t2)

        t3 = Ticket(
            ticket_number="APX-2026-0003",
            student_id=student2.id,
            department_id=dept_map["LIBRARY"].id,
            subject="Request to extend book return deadline during study leave",
            description="I have borrowed two reference books for the upcoming marketing exam. Requesting a 7-day renewal without fine penalty.",
            category="library",
            priority=TicketPriority.LOW,
            status=TicketStatus.RESOLVED,
            resolved_at=datetime.utcnow() - timedelta(days=2),
        )
        db.add(t3)
        db.commit()
        db.refresh(t1)
        db.refresh(t2)
        db.refresh(t3)

        # Add replies & internal notes to ticket 2
        reply = TicketReply(
            ticket_id=t2.id,
            user_id=staff.id,
            message="Hello Kasun, your account lock has been reviewed. We have sent a temporary one-time password to your official student email.",
            is_solution=False,
        )
        db.add(reply)

        note = TicketInternalNote(
            ticket_id=t2.id,
            staff_id=staff.id,
            note="Verified student identity via Student Index 2026/SE/048 in Active Directory. Password reset link dispatched.",
        )
        db.add(note)

        # 5. Seed Knowledge Documents & Chunks (Sri Lankan Higher Education Context)
        os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
        doc1_path = os.path.join(settings.DOCUMENTS_DIR, "mahapola_policy_2026.txt")
        doc1_text = (
            "APEX UNIVERSITY - MAHAPOLA HIGHER EDUCATION SCHOLARSHIP AND BURSARY POLICY (YEAR 2026)\n\n"
            "1. Eligibility Criteria:\n"
            "The Mahapola Higher Education Scholarship is awarded annually based on the University Grants Commission (UGC) merit and parental income criteria. "
            "Students with parental annual income below LKR 500,000 are eligible for Ordinary Bursaries, while top Z-Score holders in each district receive Merit Scholarships.\n\n"
            "2. Payout and Disbursement:\n"
            "Disbursements are made monthly at the rate of LKR 5,000 per installment. Payment vouchers are issued at the Student Welfare Division starting from the 10th of every month. "
            "Students must physically present their valid Student Record Book and National Identity Card (NIC). "
            "Vouchers can be cashed at the Bank of Ceylon (BOC) Campus Branch or credited directly to linked student accounts.\n\n"
            "3. Attendance Requirements:\n"
            "Students must maintain a minimum of 80% attendance in lectures and practical sessions. Any suspension or academic disciplinary action will temporarily freeze stipend installments."
        )
        with open(doc1_path, "w", encoding="utf-8") as f:
            f.write(doc1_text)

        kdoc1 = KnowledgeDocument(
            title="Mahapola Scholarship and Bursary Regulations (2026)",
            original_filename="mahapola_policy_2026.txt",
            stored_filename="mahapola_policy_2026.txt",
            file_path=doc1_path,
            file_size=len(doc1_text.encode('utf-8')),
            mime_type="text/plain",
            version="1.0",
            department_id=dept_map["WELFARE"].id,
            status=ContentStatus.PUBLISHED,
            uploaded_by=admin.id,
        )
        db.add(kdoc1)
        db.commit()
        db.refresh(kdoc1)

        # Chunks for doc1
        chunk1 = DocumentChunk(
            document_id=kdoc1.id,
            chunk_index=0,
            content="Mahapola Scholarship Eligibility: Awarded based on UGC merit and parental income. Annual parental income below LKR 500,000 qualifies for Ordinary Bursary, while district top Z-Scores receive Merit Scholarships.",
            page_number=1,
            section_heading="Section 1: Eligibility",
            token_count=35,
            embedding=embedding_service.generate_embedding("Mahapola scholarship eligibility income Z-score criteria 500000"),
        )
        chunk2 = DocumentChunk(
            document_id=kdoc1.id,
            chunk_index=1,
            content="Mahapola Payout Schedule: Monthly disbursement of LKR 5,000 per installment. Payment vouchers are issued at the Student Welfare Division starting the 10th of each month. Students must show Student Record Book and National Identity Card (NIC). Vouchers can be cashed at Bank of Ceylon (BOC) campus branch.",
            page_number=1,
            section_heading="Section 2: Disbursement and BOC Payout",
            token_count=48,
            embedding=embedding_service.generate_embedding("Mahapola monthly payment voucher 5000 BOC Bank of Ceylon collection Welfare Division 10th"),
        )
        db.add(chunk1)
        db.add(chunk2)

        # Document 2: IT and Campus Services
        doc2_path = os.path.join(settings.DOCUMENTS_DIR, "it_lms_campus_guide.txt")
        doc2_text = (
            "APEX UNIVERSITY - CAMPUS IT SERVICES AND STUDENT LMS GUIDE\n\n"
            "1. Campus WiFi Setup:\n"
            "Connect to the 'UniDesk-Secure' wireless network on campus. Authenticate using your student email (indexNumber@student.apex.edu.lk) and your portal password. "
            "For guest access, connect to 'UniDesk-Guest' and complete SMS OTP verification.\n\n"
            "2. Student LMS and Webmail:\n"
            "Student email is hosted on Microsoft 365. LMS accounts provide lecture slides, assignment submissions, and exam results. "
            "If your LMS account is locked due to 3 consecutive failed login attempts, submit an IT support ticket or visit Admin Block Room 204 with your Student ID.\n\n"
            "3. Main Campus Library Hours:\n"
            "The library operates Monday to Friday from 8:00 AM to 8:00 PM, and Saturdays from 8:30 AM to 5:00 PM. Closed on Sundays and Poya Days."
        )
        with open(doc2_path, "w", encoding="utf-8") as f:
            f.write(doc2_text)

        kdoc2 = KnowledgeDocument(
            title="Campus IT, LMS and Library Student Handbook",
            original_filename="it_lms_campus_guide.txt",
            stored_filename="it_lms_campus_guide.txt",
            file_path=doc2_path,
            file_size=len(doc2_text.encode('utf-8')),
            mime_type="text/plain",
            version="1.0",
            department_id=dept_map["IT"].id,
            status=ContentStatus.PUBLISHED,
            uploaded_by=admin.id,
        )
        db.add(kdoc2)
        db.commit()
        db.refresh(kdoc2)

        chunk3 = DocumentChunk(
            document_id=kdoc2.id,
            chunk_index=0,
            content="Campus WiFi Configuration: Connect to 'UniDesk-Secure' using student email credentials (indexNumber@student.apex.edu.lk) and portal password. Guests can connect to 'UniDesk-Guest' using OTP verification.",
            page_number=1,
            section_heading="Campus WiFi",
            token_count=30,
            embedding=embedding_service.generate_embedding("wifi setup connect apex-secure credentials student email guest otp"),
        )
        chunk4 = DocumentChunk(
            document_id=kdoc2.id,
            chunk_index=1,
            content="Student LMS Account Lock: If your LMS account is locked after 3 failed login attempts, submit an IT support ticket or visit Admin Block Room 204 with your Student ID to reset credentials.",
            page_number=1,
            section_heading="LMS Account Locked",
            token_count=32,
            embedding=embedding_service.generate_embedding("lms login account locked password reset it support ticket admin block"),
        )
        chunk5 = DocumentChunk(
            document_id=kdoc2.id,
            chunk_index=2,
            content="Main Campus Library Operating Hours: Open Monday to Friday 8:00 AM to 8:00 PM, and Saturdays 8:30 AM to 5:00 PM. Closed on Sundays, public holidays, and Poya Days.",
            page_number=2,
            section_heading="Library Hours",
            token_count=28,
            embedding=embedding_service.generate_embedding("library hours opening weekdays saturdays poya days closed"),
        )
        db.add(chunk3)
        db.add(chunk4)
        db.add(chunk5)

        # 6. Seed FAQs
        faqs_data = [
            {
                "category": "admissions",
                "question": "What are the GCE A/L requirements for Faculty of Computing degrees?",
                "answer": "Candidates must obtain a minimum of three 'S' passes in the Physical Science stream (Combined Mathematics, Physics, Chemistry, or ICT) in a single sitting of the GCE Advanced Level examination, matching UGC guidelines.",
                "department_id": dept_map["ADMISSIONS"].id,
                "source_reference": "UGC Handbook 2025/2026",
            },
            {
                "category": "mahapola",
                "question": "How do I collect my monthly Mahapola Scholarship stipend voucher?",
                "answer": "Mahapola scholarship stipends are disbursed as vouchers at the Student Welfare Division starting the 10th of each month. Present your Student Record Book and National Identity Card (NIC). Vouchers can be cashed at Bank of Ceylon (BOC) campus branch.",
                "department_id": dept_map["WELFARE"].id,
                "source_reference": "Welfare Circular 2026/02",
            },
            {
                "category": "it_support",
                "question": "How do I connect to the secure campus WiFi network?",
                "answer": "Connect to 'UniDesk-Secure' on your device. Enter your student email address (indexNumber@student.apex.edu.lk) and your portal password.",
                "department_id": dept_map["IT"].id,
                "source_reference": "IT Center Network Guide",
            },
            {
                "category": "library",
                "question": "What are the main campus library opening hours?",
                "answer": "The Main Library is open on weekdays from 8:00 AM to 8:00 PM, and on Saturdays from 8:30 AM to 5:00 PM. Closed on Sundays and Poya Days.",
                "department_id": dept_map["LIBRARY"].id,
                "source_reference": "Library Regulation 2026",
            },
        ]
        for f in faqs_data:
            db.add(FAQ(**f, status=ContentStatus.PUBLISHED, language="en"))

        # 7. Seed Notices
        notices_data = [
            {
                "title": "Semester Module Enrollment - Year 2026 Semester 1",
                "content": "Course registration for Year 2026 Semester 1 will open for all faculties on August 1st via the Student Portal. Please clear any outstanding hostel fees or library fines beforehand to avoid automated registration locks.",
                "tag": "Urgent",
                "audience": "STUDENTS",
                "is_published": True,
            },
            {
                "title": "Mahapola Bursary Installments for June Released",
                "content": "Mahapola stipend payouts for the month of June have been disbursed. Eligible students can collect their payment vouchers at the Student Welfare Division starting today. Bring your student record book.",
                "tag": "Scholarships",
                "audience": "STUDENTS",
                "is_published": True,
            },
            {
                "title": "New Batch Orientation Ceremony & Faculty Welcome",
                "content": "The official welcome ceremony for the incoming student batch will take place in the Main Auditorium on August 26 from 9:00 AM onwards.",
                "tag": "General",
                "audience": "ALL",
                "is_published": True,
            },
        ]
        for n in notices_data:
            db.add(Notice(**n))

        # 8. Seed Service Links
        services_data = [
            {"title": "Student LMS Portal", "description": "Access modules, download lecture notes, check semester grades, and pay fees.", "url": "https://lms.apex.edu.lk", "icon_name": "book-open", "badge_color": "purple", "display_order": 1},
            {"title": "Student Email (Office 365)", "description": "Official institutional mailbox (indexNumber@student.apex.edu.lk).", "url": "https://outlook.office.com", "icon_name": "mail", "badge_color": "blue", "display_order": 2},
            {"title": "Library OPAC Catalog", "description": "Search textbooks, academic papers, and reserve study cubicles.", "url": "https://library.apex.edu.lk", "icon_name": "search", "badge_color": "emerald", "display_order": 3},
            {"title": "Campus Interactive Map", "description": "Faculties, lecture halls, canteens, and sports grounds in Malabe.", "url": "https://maps.apex.edu.lk", "icon_name": "map-pin", "badge_color": "indigo", "display_order": 4},
        ]
        for s in services_data:
            db.add(ServiceLink(**s))

        db.commit()
        print("Database seeded successfully with demo university content!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()
