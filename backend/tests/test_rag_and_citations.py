import pytest

def test_rag_grounded_answer_with_citations(client, student_auth_headers):
    # Ask question about Mahapola scholarship
    payload = {"content": "How and where do I collect my monthly Mahapola scholarship voucher?"}
    res = client.post("/api/chat/message", json=payload, headers=student_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "citations" in data
    assert len(data["citations"]) > 0

    # Validate citation structure and metadata
    citation = data["citations"][0]
    assert "document_title" in citation
    assert "Mahapola" in citation["document_title"]
    assert citation["page_number"] is not None
    assert citation["section_heading"] is not None

def test_rag_insufficient_information_fallback(client, student_auth_headers):
    # Ask totally unrelated query not in any knowledge documents
    payload = {"content": "Can I land a helicopter on the university cricket ground?"}
    res = client.post("/api/chat/message", json=payload, headers=student_auth_headers)
    assert res.status_code == 200
    data = res.json()
    # Response should clearly indicate lack of information and offer ticket creation
    assert "not find sufficient information" in data["content"] or "ticket" in data["content"]

def test_archived_documents_excluded_from_retrieval(client, admin_auth_headers, student_auth_headers):
    # 1. Archive document 1 (Mahapola policy)
    archive_res = client.patch("/api/documents/1/status?new_status=ARCHIVED", headers=admin_auth_headers)
    assert archive_res.status_code == 200
    assert archive_res.json()["status"] == "ARCHIVED"

    # 2. Search again for Mahapola voucher
    search_res = client.get("/api/knowledge/search?q=Mahapola voucher 5000 BOC", headers=student_auth_headers)
    assert search_res.status_code == 200
    results = search_res.json()
    # Document 1 chunks should be excluded
    for r in results:
        assert r["document_id"] != 1

    # 3. Restore document 1 to PUBLISHED
    restore_res = client.patch("/api/documents/1/status?new_status=PUBLISHED", headers=admin_auth_headers)
    assert restore_res.status_code == 200

def test_chat_to_ticket_handoff_draft(client, student_auth_headers):
    # 1. Send inquiry in a session
    msg_res = client.post("/api/chat/message", json={"content": "LMS portal login password failed 3 times"}, headers=student_auth_headers)
    assert msg_res.status_code == 200
    session_id = msg_res.json()["session_id"]

    # 2. Request handoff draft
    draft_res = client.post("/api/chat/hand-off-draft", json={"session_id": session_id}, headers=student_auth_headers)
    assert draft_res.status_code == 200
    draft = draft_res.json()
    assert "suggested_subject" in draft
    assert "suggested_description" in draft
    assert "transcript_excerpt" in draft
    assert draft["suggested_department_id"] is not None

def test_staff_ai_assistance_endpoints(client, staff_auth_headers):
    # Test ticket 2 AI summary
    sum_res = client.get("/api/tickets/2/ai-summary", headers=staff_auth_headers)
    assert sum_res.status_code == 200
    summary_data = sum_res.json()
    assert "summary" in summary_data
    assert len(summary_data["key_facts"]) > 0

    # Test ticket 2 AI draft reply
    draft_res = client.get("/api/tickets/2/ai-draft-reply", headers=staff_auth_headers)
    assert draft_res.status_code == 200
    draft_data = draft_res.json()
    assert "suggested_reply" in draft_data
    assert "Kasun" in draft_data["suggested_reply"]
