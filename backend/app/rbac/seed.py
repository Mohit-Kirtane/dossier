import uuid

from langchain_core.documents import Document as LcDocument
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.policy_models import PolicyDocument
from app.ingestion.loaders import chunk_documents
from app.rbac.personas import ROLES
from app.rbac.vectorstore import add_policy_documents

_ALL_ROLES = list(ROLES)

_POLICIES = [
    {
        "filename": "Employee Handbook - Remote Work & PTO Policy.txt",
        "allowed_roles": _ALL_ROLES,
        "content": """
Employee Handbook: Remote Work & PTO Policy

Remote Work Eligibility: All full-time employees are eligible to work remotely up
to 3 days per week, subject to manager approval. Fully remote arrangements require
VP-level sign-off and are reviewed annually. Core collaboration hours are 10am-3pm
in the employee's local time zone, regardless of work location.

Paid Time Off: Full-time employees accrue 18 days of paid time off per year,
credited monthly at 1.5 days per month. Unused PTO can be carried over up to a
maximum of 10 days into the next calendar year; any balance above that is forfeited
on December 31st. PTO requests should be submitted at least 5 business days in
advance through the HR portal.

Home Office Stipend: Remote employees receive a one-time $500 home office setup
stipend during their first 90 days, plus an annual $150 equipment refresh
allowance.
""",
    },
    {
        "filename": "Manager Playbook - Performance Review & PIP Process.txt",
        "allowed_roles": ["manager", "hr", "executive"],
        "content": """
Manager Playbook: Performance Review & Performance Improvement Plan (PIP) Process

Review Cadence: Formal performance reviews occur twice a year, in June and
December. Managers must complete written evaluations for every direct report
using the 5-point rating scale (1 = Unsatisfactory, 5 = Exceptional) at least 5
business days before the calendar review window closes.

Performance Improvement Plans: An employee rated 2 or below on two consecutive
review cycles must be placed on a Performance Improvement Plan (PIP). A PIP runs
for 60 days, with documented weekly check-ins between the manager and the
employee. HR Business Partners must review and approve every PIP before it is
issued to the employee, and must be copied on all weekly check-in notes.

Manager Responsibilities: Managers are responsible for calibrating ratings within
their department before submission, to reduce rating inflation. Any rating of 5
requires a written justification of at least 100 words.
""",
    },
    {
        "filename": "HR Policy - Compensation Bands & Pay Equity Guidelines.txt",
        "allowed_roles": ["hr", "executive"],
        "content": """
HR Policy: Compensation Bands & Pay Equity Guidelines

Leveling System: All roles are mapped to levels L1 through L6. Base salary bands
by level (US, annualized): L1 $70,000-$90,000; L2 $90,000-$115,000; L3
$115,000-$145,000; L4 $145,000-$180,000; L5 $180,000-$225,000; L6 $225,000+.
Bands are reviewed annually by the Compensation Committee and adjusted for
regional cost-of-living multipliers outside the US.

Equity Refreshers: Employees become eligible for an equity refresh grant at their
2-year anniversary, and every 2 years thereafter, subject to a performance rating
of 3 or higher on their most recent review.

Pay Equity Audits: HR runs a pay equity audit twice per year (Q1 and Q3) across
all departments, controlling for level, tenure, and location. Any unexplained pay
gap greater than 3% between comparable roles must be remediated within the
following pay cycle and reported to the Executive team.
""",
    },
    {
        "filename": "Executive Policy - M&A Disclosure & Trading Blackout Windows.txt",
        "allowed_roles": ["executive"],
        "content": """
Executive Policy: M&A Disclosure & Trading Blackout Windows

Trading Blackout Windows: All executives and board members are subject to a
trading blackout window beginning 14 calendar days before the end of each fiscal
quarter and ending 2 full trading days after quarterly earnings are publicly
released. No executive may trade company securities, exercise options for resale,
or amend a 10b5-1 plan during a blackout window without written pre-clearance
from the General Counsel.

M&A Confidentiality Tiers: Potential acquisition or divestiture discussions are
classified as Tier 1 (deal team + CEO only), Tier 2 (adds CFO, General Counsel,
and named VPs), or Tier 3 (full executive team) based on deal size and
diligence stage. Tier 1 and Tier 2 discussions must not be referenced in any
written communication outside of the deal room without General Counsel approval.

Board Disclosure: Any acquisition exceeding $10M in enterprise value requires
board notification within 48 hours of signing a letter of intent.
""",
    },
    {
        "filename": "IT Security Policy - Data Classification & Access Control.txt",
        "allowed_roles": _ALL_ROLES,
        "content": """
IT Security Policy: Data Classification & Access Control Standards

Data Classification Levels: All company data must be classified as Public,
Internal, Confidential, or Restricted. Restricted data (e.g. customer payment
details, employee compensation records, unreleased financials) requires
multi-factor authentication and is logged on every access.

Access Control: Access to any system is granted on a least-privilege basis and
must be tied to a specific business justification. Access to Confidential or
Restricted systems is reviewed quarterly by the system owner, and automatically
revoked 24 hours after an employee's termination date.

Incident Reporting: Any suspected data exposure, lost device, or phishing
compromise must be reported to the Security team within 1 hour of discovery
via the #security-incidents channel or the security@ mailbox. Security aims to
issue an initial impact assessment within 4 business hours of a report.
""",
    },
]


def seed_policy_documents(session: Session) -> None:
    if session.scalar(select(PolicyDocument.id).limit(1)) is not None:
        return

    for policy in _POLICIES:
        document_id = str(uuid.uuid4())
        raw_doc = LcDocument(page_content=policy["content"].strip())
        chunks = chunk_documents([raw_doc], document_id=document_id, filename=policy["filename"])
        for chunk in chunks:
            chunk.metadata["allowed_roles"] = policy["allowed_roles"]

        add_policy_documents(chunks)

        session.add(
            PolicyDocument(
                id=document_id,
                filename=policy["filename"],
                allowed_roles=policy["allowed_roles"],
                chunk_count=len(chunks),
            )
        )

    session.commit()
