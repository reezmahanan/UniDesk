import pytest

def test_student_ticket_isolation(client, student_auth_headers, student2_auth_headers):
    # Ticket 1 belongs to student 1 (Kasun)
    # Ticket 3 belongs to student 2 (Sanduni)
    
    # Kasun can view ticket 1
    res1 = client.get("/api/tickets/1", headers=student_auth_headers)
    assert res1.status_code == 200

    # Kasun cannot view Sanduni's ticket (ticket 3)
    res_forbidden = client.get("/api/tickets/3", headers=student_auth_headers)
    assert res_forbidden.status_code == 403

def test_internal_note_privacy(client, student_auth_headers, staff_auth_headers):
    # Ticket 2 has an internal note added during seed
    # 1. Staff requests ticket 2 detail -> internal note should be visible
    staff_res = client.get("/api/tickets/2", headers=staff_auth_headers)
    assert staff_res.status_code == 200
    staff_data = staff_res.json()
    assert len(staff_data["internal_notes"]) > 0

    # 2. Student (ticket owner) requests ticket 2 detail -> internal notes MUST BE EMPTY
    student_res = client.get("/api/tickets/2", headers=student_auth_headers)
    assert student_res.status_code == 200
    student_data = student_res.json()
    assert len(student_data["internal_notes"]) == 0

def test_student_cannot_add_internal_note(client, student_auth_headers):
    res = client.post("/api/tickets/1/internal-notes", json={"note": "Hacking internal notes"}, headers=student_auth_headers)
    assert res.status_code == 403

def test_ticket_creation_and_reply(client, student_auth_headers):
    create_payload = {
        "subject": "Inquiry regarding module registration add/drop window",
        "description": "Please confirm if late add/drop window carries any penalty fees.",
        "category": "academics",
        "priority": "MEDIUM",
        "transcript_excerpt": "Student: What is the late enrollment period?"
    }
    create_res = client.post("/api/tickets", json=create_payload, headers=student_auth_headers)
    assert create_res.status_code == 201
    ticket = create_res.json()
    assert ticket["ticket_number"].startswith("APX-")
    assert ticket["status"] == "OPEN"

    # Add reply from student
    reply_res = client.post(
        f"/api/tickets/{ticket['id']}/replies",
        json={"message": "Following up on this query."},
        headers=student_auth_headers
    )
    assert reply_res.status_code == 200
    reply_data = reply_res.json()
    assert reply_data["message"] == "Following up on this query."

def test_ticket_status_transition_rules(client, staff_auth_headers, student2_auth_headers, admin_auth_headers):
    # Ticket 3 is in LIBRARY department.
    # Student 2 (ticket owner) can reopen their resolved ticket (transition to IN_PROGRESS)
    reopen_res = client.patch(
        "/api/tickets/3/status",
        json={"status": "IN_PROGRESS", "comment": "Issue still unresolved"},
        headers=student2_auth_headers
    )
    assert reopen_res.status_code == 200
    assert reopen_res.json()["status"] == "IN_PROGRESS"

    # Admin (or assigned library staff) can transition IN_PROGRESS -> RESOLVED
    resolve_res = client.patch(
        "/api/tickets/3/status",
        json={"status": "RESOLVED", "comment": "Book renewal granted"},
        headers=admin_auth_headers
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"

    # Verify staff boundary isolation: IT staff CANNOT modify Library ticket
    cross_dept_res = client.patch(
        "/api/tickets/3/status",
        json={"status": "CLOSED"},
        headers=staff_auth_headers
    )
    assert cross_dept_res.status_code == 403  # Enforces department boundary!

    # Invalid transition check: RESOLVED cannot jump directly to WAITING_FOR_STUDENT
    invalid_res = client.patch(
        "/api/tickets/3/status",
        json={"status": "WAITING_FOR_STUDENT"},
        headers=admin_auth_headers
    )
    assert invalid_res.status_code == 400
