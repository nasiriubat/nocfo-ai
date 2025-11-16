from datetime import datetime
from typing import Any

Attachment = dict[str, Any]
Transaction = dict[str, Any]

COMPANY_NAME = "Example Company Oy"

# herw we normalize the reference number by removing whitespace and leading zeros
def normalize_reference(ref: str | None) -> str | None:
    if ref is None:
        return None
    normalized = "".join(ref.split())
    normalized = normalized.lstrip("0")
    return normalized if normalized else None

# here we extract the counterparty from the attachment by checkinf the appropriate field
def get_counterparty_from_attachment(attachment: Attachment) -> str | None:
    data = attachment.get("data", {})
    attachment_type = attachment.get("type", "")
    
    if attachment_type == "receipt":
        supplier = data.get("supplier")
        if supplier and supplier != COMPANY_NAME:
            return supplier

    issuer = data.get("issuer")
    recipient = data.get("recipient")
    
    if issuer and issuer != COMPANY_NAME:
        return issuer
    
    if recipient and recipient != COMPANY_NAME:
        return recipient
    
    supplier = data.get("supplier")
    if supplier and supplier != COMPANY_NAME:
        return supplier
    
    return None

def company_name_match(name1: str | None, name2: str | None) -> bool:
    if name1 is None or name2 is None:
        return False
    
    n1 = " ".join(name1.lower().split())
    n2 = " ".join(name2.lower().split())
    
    if n1 == n2:
        return True
    
    shorter = n1 if len(n1) < len(n2) else n2
    longer = n2 if len(n1) < len(n2) else n1
    
    if longer.startswith(shorter):
        if len(longer) == len(shorter) or longer[len(shorter)] == " ":
            return True
    
    words1 = n1.split()
    words2 = n2.split()
    
    if len(words1) > 0 and len(words2) > 0:
        if words1[-1] == words2[-1]:
            shorter_words = set(words1) if len(words1) <= len(words2) else set(words2)
            longer_words = set(words2) if len(words1) <= len(words2) else set(words1)
            if shorter_words.issubset(longer_words):
                return True
    
    return False


def date_within_range(date1: str | None, date2: str | None, days: int = 30) -> bool:
    if date1 is None or date2 is None:
        return False
    
    try:
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        diff = abs((d1 - d2).days)
        return diff <= days
    except (ValueError, TypeError):
        return False


def amount_matches(amount1: float | None, amount2: float | None) -> bool:
    if amount1 is None or amount2 is None:
        return False
    
    return abs(abs(amount1) - abs(amount2)) < 0.01  # Allow small floating point differences


def get_attachment_date(attachment: Attachment) -> str | None:
    data = attachment.get("data", {})
    attachment_type = attachment.get("type", "")
    
    if attachment_type == "receipt":
        return data.get("receiving_date")
    
    return data.get("due_date") or data.get("invoicing_date")


def find_attachment(
    transaction: Transaction,
    attachments: list[Attachment],
) -> Attachment | None:
    """Find the best matching attachment for a given transaction."""
    # TODO: Implement me
    
    if not attachments:
        return None
    
    tx_reference = normalize_reference(transaction.get("reference"))
    tx_amount = transaction.get("amount")
    tx_date = transaction.get("date")
    tx_contact = transaction.get("contact")
    
    if tx_reference:
        for attachment in attachments:
            att_data = attachment.get("data", {})
            att_reference = normalize_reference(att_data.get("reference"))
            if att_reference and tx_reference == att_reference:
                return attachment
    
    best_match = None
    best_score = 0
    
    for attachment in attachments:
        att_data = attachment.get("data", {})
        att_amount = att_data.get("total_amount")
        att_date = get_attachment_date(attachment)
        att_counterparty = get_counterparty_from_attachment(attachment)
        
        score = 0
        matches = 0
        
        amount_match = amount_matches(tx_amount, att_amount)
        if amount_match:
            score += 1
            matches += 1
        
        date_match = date_within_range(tx_date, att_date)
        if date_match:
            score += 1
            matches += 1
        
        counterparty_match = company_name_match(tx_contact, att_counterparty)
        if counterparty_match:
            score += 1
            matches += 1

        has_counterparty_info = tx_contact is not None and att_counterparty is not None
        if has_counterparty_info and not counterparty_match:
            continue
        
        if matches >= 2 and score > best_score:
            best_score = score
            best_match = attachment
    
    return best_match if best_score >= 2 else None


def find_transaction(
    attachment: Attachment,
    transactions: list[Transaction],
) -> Transaction | None:
    """Find the best matching transaction for a given attachment."""
    # TODO: Implement me
    if not transactions:
        return None
    
    att_data = attachment.get("data", {})
    att_reference = normalize_reference(att_data.get("reference"))
    att_amount = att_data.get("total_amount")
    att_date = get_attachment_date(attachment)
    att_counterparty = get_counterparty_from_attachment(attachment)
    
    if att_reference:
        for transaction in transactions:
            tx_reference = normalize_reference(transaction.get("reference"))
            if tx_reference and tx_reference == att_reference:
                return transaction
    
    best_match = None
    best_score = 0
    
    for transaction in transactions:
        tx_amount = transaction.get("amount")
        tx_date = transaction.get("date")
        tx_contact = transaction.get("contact")
        
        score = 0
        matches = 0
        
        amount_match = amount_matches(tx_amount, att_amount)
        if amount_match:
            score += 1
            matches += 1
        
        date_match = date_within_range(tx_date, att_date)
        if date_match:
            score += 1
            matches += 1
        
        counterparty_match = company_name_match(tx_contact, att_counterparty)
        if counterparty_match:
            score += 1
            matches += 1
        
        has_counterparty_info = tx_contact is not None and att_counterparty is not None
        if has_counterparty_info and not counterparty_match:
            continue
        
        if matches >= 2 and score > best_score:
            best_score = score
            best_match = transaction
    
    return best_match if best_score >= 2 else None
