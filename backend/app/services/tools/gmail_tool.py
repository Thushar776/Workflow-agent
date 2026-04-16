def send_email(to: str, subject: str, message: str) -> str:
    """
    Sends an email using the Gmail integration.
    
    Args:
        to: The recipient's email address.
        subject: The subject of the email.
        message: The body of the email.
    
    Returns:
        Status message about the email dispatch.
    """
    # Mock implementation
    print(f"MOCK GMAIL: Sending email to {to} | Subject: {subject}")
    print(f"MOCK GMAIL: Body: {message}")
    
    return f"Success: Email sent to {to} with subject '{subject}'."

def read_emails(query: str = "", limit: int = 5) -> str:
    """
    Reads recent emails from the Gmail inbox.
    
    Args:
        query: Optional search query to filter emails.
        limit: Maximum number of emails to return.
        
    Returns:
        A string representation of the fetched emails.
    """
    # Mock implementation
    mock_inbox = [
        {"from": "boss@company.com", "subject": "Urgent: Q3 Report", "date": "2026-04-15"},
        {"from": "newsletter@tech.com", "subject": "AI News Daily", "date": "2026-04-14"}
    ]
    
    return f"Found {len(mock_inbox)} emails. Latest 2: {mock_inbox}"
