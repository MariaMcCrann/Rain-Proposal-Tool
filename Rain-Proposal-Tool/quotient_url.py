"""
Builds a "create new quote" URL for Quotient, pre-filled with whatever fields
their generated-link feature actually supports.

STATUS: param names below are PLACEHOLDERS. Quotient documents this feature
("create a quote using a URL") in their CRM integration help pages (Capsule,
Insightly) but the actual query-string parameter names aren't published
anywhere public. Before relying on this:

  1. Check Quotient -> Account Settings -> Connected Apps for any
     "Generated Link" / "create quote URL" option, OR
  2. Email Quotient support and ask for the parameter spec directly.

Once you have the real names, only QUOTIENT_PARAM_MAP and QUOTIENT_BASE_URL
need to change - nothing else in this file or in extract_rfq.py.

Also worth setting expectations: this kind of URL-prefill almost certainly
only covers simple fields (quote title, contact name/email/company) - it is
very unlikely to support pre-filling a full line-item table. The fee detail
still gets entered inside Quotient by whoever builds the quote.
"""

from urllib.parse import urlencode

QUOTIENT_BASE_URL = "https://www.quotientapp.com/quotes/new"  # CONFIRM - placeholder

QUOTIENT_PARAM_MAP = {
    "quote_title": "title",  # CONFIRM
    "contact_name": "name",  # CONFIRM
    "contact_email": "email",  # CONFIRM
    "contact_company": "company",  # CONFIRM
    "contact_phone": "phone",  # CONFIRM
}


def build_quotient_prefill_url(extracted: dict, base_url: str = QUOTIENT_BASE_URL) -> str:
    """
    extracted: the dict returned by extract_rfq.extract_rfq()
    Returns a URL string. Does not call Quotient, does not send anything -
    just builds a link a human can click during the review step.
    """
    contact = extracted.get("contact", {})
    fields = {
        "quote_title": extracted.get("project_title", ""),
        "contact_name": contact.get("name", ""),
        "contact_email": contact.get("email", ""),
        "contact_company": contact.get("company", ""),
        "contact_phone": contact.get("phone", ""),
    }
    params = {QUOTIENT_PARAM_MAP[key]: value for key, value in fields.items() if value}
    if not params:
        return base_url
    return f"{base_url}?{urlencode(params)}"


if __name__ == "__main__":
    sample = {
        "project_title": "Elizabeth Street Flood Mitigation Concept Design",
        "contact": {
            "name": "Jordan Smith",
            "email": "jordan.smith@cityofexample.vic.gov.au",
            "company": "City of Example",
            "phone": "",
        },
    }
    print(build_quotient_prefill_url(sample))
