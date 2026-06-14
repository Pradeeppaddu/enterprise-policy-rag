"""One-off script to (re)generate policies.json with a broad set of sample enterprise policies."""

import json
from pathlib import Path

# Each tuple: (title, product_area, sections)
# sections is a list of (heading, body) pairs.
POLICIES = [
    # ---- HR ----
    ("Leave and Time-Off Policy", "hr_leave", [
        ("Annual Leave", "Full-time employees accrue 18 days of paid annual leave per calendar year, credited monthly at 1.5 days/month. Unused leave up to 5 days may be carried over to the next year; any balance beyond that is forfeited on December 31."),
        ("Sick Leave", "Employees receive 10 days of paid sick leave per year. A medical certificate is required for absences longer than 2 consecutive days."),
        ("Parental Leave", "- Primary caregivers are entitled to 16 weeks of paid parental leave.\n- Secondary caregivers are entitled to 4 weeks of paid parental leave.\n- Leave must be taken within 12 months of the child's birth or adoption."),
        ("Public Holidays", "Employees receive all locally observed public holidays as paid days off, as published in the regional holiday calendar each January."),
        ("Requesting Leave", "All leave requests must be submitted through the HR portal at least 5 business days in advance, except for sick leave, which may be reported on the day of absence to the employee's manager."),
        ("Unpaid Leave", "Employees with more than 1 year of tenure may request up to 30 days of unpaid leave per year, subject to manager and HR approval."),
    ]),
    ("Remote and Hybrid Work Policy", "hr_remote_work", [
        ("Eligibility", "Employees whose roles do not require regular on-site presence may work remotely, subject to manager approval. New hires must complete their first 90 days on-site before transitioning to a hybrid or remote schedule."),
        ("Hybrid Schedule", "Standard hybrid employees are expected to be in the office at least 2 days per week (Tuesday and Thursday are core in-office days for most teams)."),
        ("Equipment", "The company provides a laptop, monitor, and standard peripherals for remote work. Employees may submit a one-time home office setup reimbursement of up to $300 through the expense system."),
        ("Working Hours", "Remote employees must be reachable during core hours (10:00 AM - 4:00 PM local time) and should keep their calendar status updated to reflect availability."),
        ("Working from Abroad", "Employees wishing to work from a country other than their employment country must request approval from HR at least 3 weeks in advance due to tax and legal compliance requirements. Such arrangements are limited to 20 working days per year."),
        ("Data Security While Remote", "Employees must use the company VPN when accessing internal systems remotely and must not work from unsecured public Wi-Fi without VPN protection."),
    ]),
    ("Code of Conduct", "hr_compliance", [
        ("Workplace Behavior", "All employees are expected to treat colleagues, clients, and partners with respect and professionalism. Harassment, discrimination, and retaliation of any kind are strictly prohibited and may result in disciplinary action up to and including termination."),
        ("Conflicts of Interest", "Employees must disclose any personal, financial, or familial relationships that could create a conflict of interest with their role, including outside employment, board positions, or significant investments in competitors or vendors."),
        ("Gifts and Entertainment", "Employees may accept gifts from vendors or clients valued under $100. Any gift over $100 must be declined or reported to the compliance team. Cash gifts of any amount are prohibited."),
        ("Confidentiality", "Employees must protect confidential company, client, and employee information both during and after employment, in accordance with their signed confidentiality agreement."),
        ("Anti-Bribery and Corruption", "Employees must not offer, give, request, or accept bribes or improper payments of any kind, whether dealing with private parties or government officials."),
        ("Reporting Violations", "Employees who become aware of a violation of this Code of Conduct should report it to their manager, HR, or via the anonymous ethics hotline. Retaliation against good-faith reporters is prohibited."),
    ]),
    ("Recruitment and Hiring Policy", "hr_recruitment", [
        ("Job Postings", "All open positions must be posted internally for at least 5 business days before external advertising begins, except for confidential executive searches approved by HR leadership."),
        ("Interview Process", "Candidates for roles above entry level must be interviewed by at least 3 panelists, including the hiring manager and one cross-functional partner, to reduce individual bias."),
        ("Background Checks", "Offers of employment are contingent on satisfactory completion of a background check, which may include employment verification, education verification, and (for finance and security roles) a credit and criminal history check."),
        ("Referral Bonuses", "Employees who refer a successful external hire receive a referral bonus of $1,500 for standard roles and $3,000 for hard-to-fill technical roles, paid after the new hire completes 90 days of employment."),
        ("Equal Opportunity", "Hiring decisions are based solely on qualifications, skills, and experience. The company does not discriminate based on race, gender, age, religion, disability, sexual orientation, or any other protected characteristic."),
    ]),
    ("Performance Review Policy", "hr_performance", [
        ("Review Cycle", "Formal performance reviews are conducted twice per year: a mid-year check-in in June and an annual review in December that informs compensation decisions."),
        ("Goal Setting", "Employees and managers set quarterly goals (OKRs) within the first two weeks of each quarter. Goals should be specific, measurable, and aligned with team objectives."),
        ("Rating Scale", "Performance is rated on a 5-point scale ranging from 'Does Not Meet Expectations' to 'Significantly Exceeds Expectations'. Ratings of 'Does Not Meet Expectations' trigger a Performance Improvement Plan (PIP)."),
        ("Performance Improvement Plans", "A PIP lasts 30-90 days and includes specific, measurable improvement goals, regular check-ins with the manager, and HR oversight. Failure to meet PIP goals may result in termination."),
        ("Calibration", "Manager ratings are calibrated across teams by HR and department leadership to ensure consistency before ratings are communicated to employees."),
    ]),
    ("Compensation and Benefits Policy", "hr_compensation", [
        ("Salary Reviews", "Base salaries are reviewed annually as part of the December performance review cycle. Off-cycle adjustments may be made for promotions, market corrections, or retention concerns with VP approval."),
        ("Bonus Program", "Eligible employees participate in an annual bonus program with a target payout of 10-20% of base salary, depending on level, based on company and individual performance."),
        ("Health Insurance", "The company covers 80% of the premium for medical, dental, and vision insurance for employees and 50% for dependents. Enrollment occurs during the annual open enrollment period in November."),
        ("Retirement Plan", "Employees are eligible to contribute to the company retirement plan from their first day of employment. The company matches 100% of contributions up to 4% of base salary, vesting immediately."),
        ("Equity Compensation", "Eligible employees receive equity grants (RSUs or stock options) that vest over 4 years with a 1-year cliff. Additional refresh grants are considered annually based on performance."),
    ]),
    ("Employee Onboarding Policy", "hr_onboarding", [
        ("Pre-Boarding", "HR sends new hires their offer letter, equipment shipping confirmation, and Day 1 schedule at least 5 business days before their start date."),
        ("Day One", "New hires complete IT setup, badge issuance, and mandatory compliance training (Code of Conduct, IT Security, and Anti-Harassment) on their first day."),
        ("30-60-90 Day Plan", "Managers must create a 30-60-90 day onboarding plan with the new hire outlining ramp-up goals, key stakeholders to meet, and initial deliverables."),
        ("Buddy Program", "Every new hire is assigned a peer 'buddy' from their team (not their manager) for their first 60 days to help with informal questions and cultural orientation."),
        ("Probationary Period", "New hires are subject to a 90-day probationary period during which either party may end employment with reduced notice, as outlined in the offer letter."),
    ]),
    ("Termination and Offboarding Policy", "hr_offboarding", [
        ("Voluntary Resignation", "Employees are asked to provide at least 2 weeks' written notice (4 weeks for management roles) to allow for knowledge transfer and transition planning."),
        ("Involuntary Termination", "Terminations for performance or conduct reasons must be approved by HR and the employee's department head, with documentation of prior warnings or PIP outcomes where applicable."),
        ("Final Pay", "Final paychecks, including accrued unused vacation, are issued in accordance with local wage payment laws, typically within 5 business days of the last day of employment."),
        ("Equipment Return", "Departing employees must return all company equipment (laptop, badge, phone, access cards) on or before their last day. Unreturned equipment may be deducted from final pay where legally permitted."),
        ("Access Revocation", "IT disables all system access, email, and badge access at 5:00 PM on the employee's last working day unless otherwise instructed by HR for transition purposes."),
    ]),
    ("Anti-Harassment and Discrimination Policy", "hr_compliance", [
        ("Prohibited Conduct", "Harassment based on race, color, religion, sex, national origin, age, disability, sexual orientation, gender identity, or any other protected characteristic is strictly prohibited, including verbal, physical, and visual conduct."),
        ("Sexual Harassment", "Sexual harassment includes unwelcome sexual advances, requests for sexual favors, and other verbal or physical conduct of a sexual nature that creates an intimidating or hostile work environment."),
        ("Reporting Process", "Employees may report harassment to their manager, HR, or via the anonymous ethics hotline. All reports are investigated promptly and confidentially to the extent possible."),
        ("Investigation", "HR will complete an investigation within 14 business days where feasible, including interviews with the complainant, respondent, and relevant witnesses, and document findings and outcomes."),
        ("Non-Retaliation", "Retaliation against anyone who reports harassment in good faith or participates in an investigation is strictly prohibited and is itself grounds for disciplinary action."),
    ]),
    ("Diversity, Equity and Inclusion Policy", "hr_dei", [
        ("Commitment", "The company is committed to building a diverse workforce and an inclusive culture where all employees feel valued, respected, and able to do their best work."),
        ("Hiring Practices", "Hiring panels for roles at the senior manager level and above must include at least one member from an underrepresented group where feasible, and job descriptions are reviewed for inclusive language."),
        ("Employee Resource Groups (ERGs)", "The company supports employee-led ERGs (e.g., Women in Tech, Pride Alliance, Multicultural Network) with an annual budget for events and a dedicated executive sponsor for each group."),
        ("Pay Equity", "The company conducts an annual pay equity audit across gender and ethnicity for comparable roles, and remediates identified gaps within the following compensation cycle."),
        ("Training", "All employees complete annual inclusive workplace training, and people managers complete additional training on inclusive hiring and reducing bias in performance reviews."),
    ]),
    ("Employee Training and Development Policy", "hr_training", [
        ("Learning Budget", "Each employee has an annual learning and development budget of $1,000 for courses, certifications, conferences, or books relevant to their role, approved by their manager."),
        ("Mandatory Compliance Training", "All employees must complete annual training on Code of Conduct, IT Security, Anti-Harassment, and Data Privacy. Completion is tracked in the HR system and overdue training is escalated to managers."),
        ("Internal Mobility", "Employees with at least 12 months in their current role may apply for internal job postings without requiring their current manager's pre-approval to apply, though a transition period is coordinated upon offer."),
        ("Mentorship Program", "Employees may opt into the company mentorship program, which pairs mentees with senior employees in a different department for a 6-month structured mentorship cycle."),
        ("Tuition Reimbursement", "The company reimburses up to $5,000 per year for job-related degree or certification programs at accredited institutions, subject to a grade requirement of B or better and a 1-year service commitment after completion."),
    ]),

    # ---- IT ----
    ("IT Security and Acceptable Use Policy", "it_security", [
        ("Passwords", "- Passwords must be at least 12 characters and include uppercase, lowercase, numbers, and symbols.\n- Passwords must be changed every 90 days and may not be reused for the previous 5 password cycles.\n- Multi-factor authentication (MFA) is mandatory for all company accounts."),
        ("Device Usage", "- Company laptops must have disk encryption and the endpoint security agent enabled at all times.\n- Personal devices accessing company email or documents must be enrolled in the Mobile Device Management (MDM) system."),
        ("Software Installation", "Employees may not install unauthorized software on company devices. Software requests must be submitted via the IT Service Desk and approved before installation."),
        ("Data Classification", "Company data is classified as Public, Internal, Confidential, or Restricted. Confidential and Restricted data must not be stored on personal devices, USB drives, or third-party cloud storage not approved by IT."),
        ("Incident Reporting", "Any suspected security incident (phishing email, lost device, unauthorized access) must be reported to security@company.com within 1 hour of discovery."),
        ("Email and Internet Use", "Company email and internet access are provided primarily for business purposes. Limited personal use is permitted as long as it does not interfere with work duties or violate the Code of Conduct."),
    ]),
    ("Password and Authentication Policy", "it_security", [
        ("Password Requirements", "Passwords must be a minimum of 12 characters and must not contain the employee's username, common dictionary words, or sequential characters (e.g., '12345')."),
        ("Multi-Factor Authentication", "MFA is required for all access to email, VPN, HR systems, and any system containing Confidential or Restricted data. Approved MFA methods include the company authenticator app and hardware security keys."),
        ("Single Sign-On (SSO)", "Employees must use the corporate SSO provider for all supported applications. Creating separate local accounts for SSO-enabled applications is prohibited without IT approval."),
        ("Shared Accounts", "Shared or generic accounts (e.g., 'admin', 'support') are prohibited except for service accounts approved by IT Security, which must use a managed password vault and be reviewed quarterly."),
        ("Password Resets", "Employees who suspect their password has been compromised must reset it immediately and notify the IT Service Desk so the account can be reviewed for suspicious activity."),
    ]),
    ("Data Backup and Recovery Policy", "it_operations", [
        ("Backup Schedule", "Production databases are backed up via automated incremental backups every 6 hours and a full backup nightly. File storage and email systems are backed up daily."),
        ("Retention", "Daily backups are retained for 30 days, weekly backups for 1 year, and monthly backups for 7 years to satisfy legal and financial record-keeping requirements."),
        ("Offsite and Redundancy", "Backups are replicated to a geographically separate cloud region to ensure recoverability in the event of a regional outage or disaster."),
        ("Recovery Testing", "IT performs a full disaster recovery test at least twice per year, including restoring a production system from backup to a test environment and validating data integrity."),
        ("Employee Responsibilities", "Employees must store business files in approved cloud storage (not local hard drives only) so that files are included in the automated backup process."),
    ]),
    ("Software Licensing Policy", "it_operations", [
        ("Approved Software", "Only software listed in the IT-approved catalog may be installed on company devices. New software requests are evaluated for security, licensing cost, and overlap with existing tools."),
        ("License Compliance", "IT maintains a software asset register to ensure the company does not exceed licensed seat counts. Employees must not share individually licensed software accounts with colleagues."),
        ("Open Source Software", "Use of open source software in company products must be reviewed by Legal and Engineering leadership to confirm license compatibility (e.g., MIT, Apache 2.0 are generally pre-approved; GPL requires review)."),
        ("Personal Software Purchases", "Employees may not purchase software using personal funds for reimbursement without prior IT approval, as unapproved tools may create security or compliance risks."),
        ("Annual Audit", "IT conducts an annual software license audit and removes unused licenses to control costs, notifying affected users at least 2 weeks in advance."),
    ]),
    ("Email and Communication Policy", "it_operations", [
        ("Business Use", "Company email and messaging tools (e.g., Slack, Teams) are intended primarily for business communication. Confidential information should not be sent to personal email accounts."),
        ("Professional Conduct", "All communications using company systems must comply with the Code of Conduct and Anti-Harassment Policy, including messages sent via internal chat tools."),
        ("External Communications", "Employees responding to media inquiries, regulatory requests, or public forums on behalf of the company must route the request through Corporate Communications or Legal."),
        ("Email Retention", "Emails are retained for 3 years by default. Legal hold notices may extend retention for specific mailboxes involved in litigation or investigations."),
        ("Distribution Lists", "Company-wide distribution lists (e.g., all-employees@) may only be used for announcements approved by HR, IT, or Executive Leadership."),
    ]),
    ("Bring Your Own Device (BYOD) Policy", "it_security", [
        ("Eligibility", "Employees may use personal smartphones and tablets to access company email and calendar, subject to enrollment in the Mobile Device Management (MDM) system."),
        ("Security Requirements", "BYOD devices must have a passcode or biometric lock, automatic screen lock after 5 minutes, and the latest operating system security updates installed."),
        ("Data Separation", "Company data on personal devices is stored in a managed, encrypted container that IT can remotely wipe without affecting personal apps or data."),
        ("Lost or Stolen Devices", "Employees must report lost or stolen BYOD devices to the IT Service Desk immediately so the company data container can be remotely wiped."),
        ("Reimbursement", "Employees using personal phones for business purposes may submit for a monthly stipend of $30 toward their phone bill via the expense system."),
    ]),
    ("Cloud Services Usage Policy", "it_operations", [
        ("Approved Providers", "The company's approved cloud providers are AWS, Azure, and Google Workspace. Use of other cloud storage or SaaS tools for company data requires IT Security review and approval."),
        ("Account Provisioning", "All cloud service accounts must be provisioned through corporate SSO. Personal cloud accounts (e.g., personal Dropbox, Gmail) must not be used to store or transmit company data."),
        ("Cost Management", "Engineering teams provisioning cloud infrastructure must tag resources by project and team for cost allocation, and review spend against budget monthly with Finance."),
        ("Data Residency", "Customer data subject to regional data residency requirements (e.g., EU customer data) must be stored in the corresponding regional cloud infrastructure."),
        ("Shadow IT", "Departments must not procure SaaS tools that handle company or customer data without IT Security and Procurement review, even for free-tier trials."),
    ]),
    ("IT Asset Management Policy", "it_operations", [
        ("Asset Inventory", "IT maintains an inventory of all company-owned hardware (laptops, monitors, phones, peripherals) tagged with an asset ID and assigned to an individual employee or location."),
        ("Issuance", "New employees are issued a standard laptop and accessory kit based on their role profile (e.g., Engineering, Sales, Design) selected from the approved hardware catalog."),
        ("Refresh Cycle", "Laptops are refreshed every 3 years, or sooner if hardware failure or performance issues are documented by the IT Service Desk."),
        ("Asset Disposal", "Decommissioned devices are wiped using IT-approved data destruction methods and recycled through a certified e-waste vendor; disposal records are retained for audit purposes."),
        ("Loss or Damage", "Lost or damaged company equipment must be reported to IT within 24 hours. Repeated losses due to negligence may result in the cost being charged back to the employee's department."),
    ]),
    ("Network Access Policy", "it_security", [
        ("VPN Access", "Remote access to internal systems requires connection via the corporate VPN with MFA. Split-tunneling configurations that bypass the VPN for internal traffic are prohibited."),
        ("Guest Wi-Fi", "Visitors and contractors are provided access to an isolated guest Wi-Fi network that has no connectivity to internal corporate systems."),
        ("Network Segmentation", "Production environments, corporate IT systems, and guest networks are segmented into separate VLANs with firewall rules restricting cross-segment traffic to required services only."),
        ("Access Reviews", "Network and VPN access lists are reviewed quarterly by IT Security, and access for terminated employees or expired contractors is removed within 24 hours."),
        ("Third-Party Access", "Vendors requiring network access for support purposes must use time-limited credentials and are logged and monitored for the duration of the access window."),
    ]),

    # ---- Finance ----
    ("Expense and Travel Reimbursement Policy", "finance_expenses", [
        ("General Principles", "All business expenses must be reasonable, necessary, and supported by an itemized receipt for amounts over $25. Expenses must be submitted within 30 days of being incurred."),
        ("Travel Booking", "All flights and hotels for business travel must be booked through the corporate travel portal. Economy class is standard for flights under 6 hours; Premium Economy is permitted for flights over 6 hours with manager approval."),
        ("Meals", "- Domestic travel: meal per diem of $60/day.\n- International travel: meal per diem of $80/day.\n- Client entertainment meals require pre-approval and must list attendees and business purpose."),
        ("Mileage", "Employees using personal vehicles for business travel are reimbursed at the current IRS standard mileage rate, submitted via the expense system with trip details."),
        ("Approval Process", "Expenses under $500 require manager approval. Expenses of $500 or more require both manager and finance department approval before reimbursement is processed."),
        ("Non-Reimbursable Items", "Alcohol (outside of approved client entertainment), personal entertainment, traffic fines, and upgrades to first class are not reimbursable."),
    ]),
    ("Procurement and Purchasing Policy", "finance_procurement", [
        ("Purchase Requests", "All purchases over $1,000 require a purchase order (PO) created in the procurement system prior to placing the order with a vendor. Retroactive POs require Finance Director approval."),
        ("Approval Thresholds", "- Up to $1,000: manager approval.\n- $1,000-$10,000: department head approval.\n- $10,000-$50,000: VP and Finance approval.\n- Over $50,000: CFO approval and competitive bidding (minimum 3 quotes)."),
        ("Preferred Vendors", "Employees should use vendors on the approved vendor list where available. New vendor onboarding requires a W-9 (or equivalent), security questionnaire, and contract review by Legal."),
        ("Conflicts of Interest", "Employees must not direct purchases to vendors in which they or a family member have a financial interest without disclosing the relationship to Finance and obtaining written approval."),
        ("Receiving and Payment", "Goods receipt must be confirmed in the procurement system before invoices are approved for payment, ensuring a three-way match between PO, receipt, and invoice."),
    ]),
    ("Invoice and Payment Policy", "finance_accounts_payable", [
        ("Invoice Submission", "Vendor invoices must be submitted to accountspayable@company.com referencing a valid purchase order number. Invoices without a PO will be routed to the requesting department for approval."),
        ("Payment Terms", "Standard payment terms are Net 30 from the invoice date. Early payment discounts offered by vendors (e.g., 2/10 Net 30) should be flagged to Finance to capture savings where cash flow allows."),
        ("Payment Methods", "Payments are made via ACH or wire transfer. Check payments are issued only for vendors who cannot accept electronic payment, with Finance Director approval."),
        ("Disputed Invoices", "Invoices disputed due to pricing or quantity discrepancies are placed on hold and the requesting department must resolve the discrepancy with the vendor within 10 business days."),
        ("Duplicate Payment Prevention", "The accounts payable system automatically flags potential duplicate invoices based on vendor, amount, and invoice number; flagged invoices require manual review before payment."),
    ]),
    ("Budget Approval Policy", "finance_budgeting", [
        ("Annual Budget Cycle", "Department budgets are proposed in Q4 for the following fiscal year, reviewed by Finance, and approved by the Executive Leadership Team and Board by December 15."),
        ("Budget Categories", "Budgets are tracked by category (Headcount, Travel, Software, Marketing Programs, Capital Expenditure) and department heads receive monthly variance reports."),
        ("Reallocation", "Reallocation of budget between categories within a department of up to 10% of the category total may be approved by the department head; larger reallocations require Finance approval."),
        ("Mid-Year Reviews", "A mid-year budget review is conducted in July to adjust forecasts based on actual performance and update full-year projections for the Board."),
        ("Capital Expenditure", "Capital expenditures over $25,000 (e.g., equipment, infrastructure build-out) require a business case with ROI analysis and CFO approval regardless of whether they fall within an approved budget."),
    ]),
    ("Corporate Credit Card Policy", "finance_expenses", [
        ("Eligibility", "Corporate credit cards are issued to employees who travel frequently or manage recurring vendor payments, subject to manager and Finance approval."),
        ("Permitted Use", "Corporate cards may only be used for legitimate business expenses such as travel, client meals, and approved software subscriptions. Personal purchases are strictly prohibited, even if reimbursed later."),
        ("Reconciliation", "Cardholders must reconcile transactions and attach receipts in the expense system within 7 days of each transaction. Unreconciled transactions older than 30 days may result in card suspension."),
        ("Credit Limits", "Default credit limits are $5,000 per month for individual contributors and $15,000 per month for managers and above. Temporary limit increases for large purchases require Finance approval."),
        ("Lost or Stolen Cards", "Cardholders must report lost or stolen corporate cards to the card issuer and to Finance immediately to prevent fraudulent charges."),
    ]),
    ("Financial Reporting Policy", "finance_reporting", [
        ("Reporting Calendar", "Monthly financial close occurs within 5 business days of month-end, with management reports distributed to department heads by the 7th business day."),
        ("Internal Controls", "All journal entries over $10,000 require review and approval by a second member of the Finance team (segregation of duties) before posting."),
        ("Revenue Recognition", "Revenue is recognized in accordance with ASC 606 / IFRS 15, with subscription revenue recognized ratably over the contract term and professional services recognized as delivered."),
        ("External Audit", "The company engages an independent external auditor annually. Department heads must provide requested documentation to the audit team within 5 business days of request."),
        ("Record Retention", "Financial records, including invoices, contracts, and journal entry support, are retained for a minimum of 7 years in accordance with tax and regulatory requirements."),
    ]),

    # ---- Legal / Compliance ----
    ("Anti-Bribery and Corruption Policy", "legal_compliance", [
        ("Scope", "This policy applies to all employees, contractors, and third parties acting on behalf of the company worldwide, and complies with the U.S. Foreign Corrupt Practices Act (FCPA) and the UK Bribery Act."),
        ("Prohibited Payments", "Employees must never offer, promise, give, or authorize anything of value to a government official or private party to obtain or retain business or secure an improper advantage."),
        ("Facilitation Payments", "Small 'facilitation payments' to expedite routine government actions (e.g., customs processing) are prohibited, even where locally common, unless required for the immediate safety of an employee."),
        ("Third-Party Due Diligence", "Agents, distributors, and consultants operating in high-risk jurisdictions must undergo anti-corruption due diligence and sign an anti-bribery compliance certification before engagement."),
        ("Books and Records", "All payments, gifts, and hospitality must be accurately recorded in the company's books. Off-the-books accounts or slush funds of any kind are strictly prohibited."),
    ]),
    ("Data Privacy Policy", "legal_privacy", [
        ("Scope", "This policy governs the collection, use, storage, and sharing of personal data of employees, customers, and other individuals in compliance with GDPR, CCPA, and other applicable privacy laws."),
        ("Data Minimization", "Personal data must be collected only for specified, legitimate business purposes and limited to what is necessary for that purpose. Unnecessary personal data must not be retained."),
        ("Data Subject Rights", "Individuals may request access to, correction of, or deletion of their personal data. Requests must be routed to privacy@company.com and fulfilled within the legally required timeframe (typically 30 days)."),
        ("Data Breach Response", "Suspected data breaches involving personal data must be reported to the Privacy Officer within 4 hours of discovery so that legally mandated notification timelines (e.g., 72 hours under GDPR) can be met."),
        ("Vendor Data Processing", "Third-party vendors that process personal data on the company's behalf must sign a Data Processing Agreement (DPA) and undergo a privacy and security assessment before onboarding."),
    ]),
    ("Intellectual Property Policy", "legal_ip", [
        ("Ownership of Work Product", "All inventions, designs, software, and other work product created by employees within the scope of their employment, or using company resources, are owned exclusively by the company."),
        ("Invention Disclosure", "Employees who develop a potentially patentable invention must submit an Invention Disclosure Form to the Legal team within 30 days of conception for evaluation."),
        ("Third-Party IP", "Employees must not incorporate third-party intellectual property (code, designs, content) into company products without confirming appropriate licensing through Legal review."),
        ("Trademarks and Branding", "Use of the company's trademarks, logos, and brand assets, whether internally or externally, must follow the Brand and Trademark Usage Policy and brand guidelines."),
        ("Open Source Contributions", "Employees wishing to contribute to open source projects on behalf of the company, or using company time/resources, must obtain approval from Engineering leadership and Legal."),
    ]),
    ("Whistleblower Policy", "legal_compliance", [
        ("Purpose", "This policy provides a confidential channel for employees to report suspected violations of law, regulation, or company policy, including financial reporting irregularities, fraud, and safety concerns."),
        ("Reporting Channels", "Reports may be made to a manager, HR, the Legal team, or the independent, anonymous Ethics Hotline (available 24/7 by phone and web form) operated by a third-party provider."),
        ("Confidentiality", "Reports are kept confidential to the extent possible and on a need-to-know basis during investigation. Anonymous reports are accepted, though anonymity may limit the ability to follow up."),
        ("Non-Retaliation", "The company prohibits retaliation against any employee who, in good faith, reports a concern or participates in an investigation. Retaliation claims are investigated and may result in disciplinary action."),
        ("Investigation and Outcomes", "All reports are reviewed by the Compliance team, which determines the appropriate investigation path and reports findings to the Audit Committee for matters involving financial reporting or executives."),
    ]),
    ("Records Retention Policy", "legal_compliance", [
        ("Purpose", "This policy establishes minimum retention periods for company records to meet legal, tax, and operational requirements while avoiding unnecessary accumulation of data."),
        ("Retention Schedule", "- Financial records and tax filings: 7 years.\n- Employee records: 7 years after termination.\n- Contracts: 7 years after expiration.\n- Email: 3 years.\n- Marketing materials: 2 years."),
        ("Legal Holds", "When litigation, audit, or investigation is reasonably anticipated, the Legal team issues a Legal Hold Notice suspending normal deletion schedules for relevant records until the hold is released."),
        ("Secure Disposal", "Records that have reached the end of their retention period and are not subject to a legal hold must be securely destroyed (e.g., shredding for paper, certified wipe for electronic media)."),
        ("Employee Responsibilities", "Employees must store business records in approved company systems (not personal drives) so retention and disposal schedules can be applied consistently by IT and Legal."),
    ]),
    ("Export Control and Trade Compliance Policy", "legal_trade", [
        ("Scope", "This policy applies to the export, re-export, or transfer of company products, software, and technical data across borders, including intangible transfers such as cloud access or email."),
        ("Restricted Parties Screening", "Before engaging a new customer or partner outside the home country, Sales must screen the party against denied persons and sanctioned entity lists using the approved screening tool."),
        ("Classification", "Engineering and Legal jointly classify products and software under applicable export control regimes (e.g., U.S. Export Administration Regulations) to determine licensing requirements."),
        ("Embargoed Countries", "The company does not sell, ship, or provide services to individuals or entities in countries subject to comprehensive trade embargoes, except as permitted under applicable general licenses."),
        ("Training and Reporting", "Employees in Sales, Shipping, and Engineering roles complete annual export compliance training, and any suspected violation must be reported to the Trade Compliance Officer immediately."),
    ]),

    # ---- Security / Safety ----
    ("Workplace Health and Safety Policy", "facilities_safety", [
        ("General Responsibilities", "The company is committed to providing a safe working environment in compliance with applicable occupational health and safety regulations (e.g., OSHA). All employees share responsibility for maintaining a safe workplace."),
        ("Incident Reporting", "Workplace injuries, near-misses, and unsafe conditions must be reported to Facilities and HR within 24 hours using the Incident Report Form, regardless of severity."),
        ("Ergonomics", "Employees may request an ergonomic assessment of their workstation (office or home) from Facilities, which provides adjustable chairs, monitor arms, and keyboard trays as needed."),
        ("Fire Safety", "Each office floor has designated fire wardens responsible for evacuation during drills and emergencies. Fire drills are conducted at least twice per year."),
        ("Workplace Violence", "Threats or acts of violence in the workplace are not tolerated. Employees who feel unsafe should contact Security or, in an emergency, local law enforcement immediately, then notify HR."),
    ]),
    ("Visitor Access Policy", "facilities_security", [
        ("Pre-Registration", "All visitors must be pre-registered by their host employee at least 24 hours in advance through the visitor management system, providing the visitor's name and company."),
        ("Check-In Process", "Visitors must check in at reception, present a government-issued photo ID, and wear a visitor badge visibly at all times while on company premises."),
        ("Escort Requirements", "Visitors must be escorted by their host employee at all times in non-public areas, including office floors, server rooms, and labs."),
        ("Restricted Areas", "Data centers, server rooms, and labs containing prototype hardware require additional approval from Facilities Security and are logged separately in the access control system."),
        ("Badge Return", "Visitor badges must be returned to reception upon departure. Visitors who do not return badges within the expected visit window trigger an automated alert to Facilities Security."),
    ]),
    ("Emergency Preparedness Policy", "facilities_safety", [
        ("Emergency Plans", "Each office maintains an Emergency Action Plan covering fire, earthquake, severe weather, and active threat scenarios, reviewed annually by Facilities and local emergency services where applicable."),
        ("Communication", "In the event of an emergency affecting an office, the company uses an automated mass notification system (text, email, and app push) to communicate status and instructions to affected employees."),
        ("Business Continuity", "Critical business functions have documented continuity plans identifying key personnel, backup locations, and recovery time objectives, tested annually through tabletop exercises."),
        ("Evacuation Procedures", "Evacuation routes and assembly points are posted on each floor. Employees with disabilities or temporary mobility limitations may register with Facilities for an assigned evacuation buddy."),
        ("Remote Employee Safety", "Remote employees are encouraged to maintain a basic emergency kit and should update their emergency contact information annually via the HR portal."),
    ]),
    ("Incident Response Policy", "it_security", [
        ("Incident Classification", "Security incidents are classified as Low, Medium, High, or Critical based on impact to confidentiality, integrity, or availability of systems and data."),
        ("Response Team", "The Security Incident Response Team (SIRT), composed of IT Security, Engineering, Legal, and Communications representatives, is activated for High and Critical incidents within 1 hour of detection."),
        ("Containment and Eradication", "Upon detection, the SIRT prioritizes containment (e.g., isolating affected systems, revoking compromised credentials) before root cause analysis and remediation."),
        ("Notification", "Legal determines whether an incident triggers regulatory notification obligations (e.g., to data protection authorities or affected customers) and ensures notifications are made within required timeframes."),
        ("Post-Incident Review", "Within 5 business days of resolution, the SIRT conducts a post-incident review documenting timeline, root cause, and corrective actions, tracked to completion by IT Security."),
    ]),
    ("Physical Security Policy", "facilities_security", [
        ("Access Badges", "All employees are issued a personal access badge that must be used to enter office facilities. Badges must not be shared, loaned, or used to allow 'tailgating' of unbadged individuals."),
        ("Access Levels", "Badge access is provisioned based on role and location, with sensitive areas (server rooms, finance offices) requiring additional access approval from the relevant department head."),
        ("CCTV Monitoring", "Common areas, entrances, and parking facilities are monitored by CCTV for security purposes. Footage is retained for 90 days and accessed only by Facilities Security and, when required, Legal or HR for investigations."),
        ("Lost Badges", "Lost or stolen badges must be reported to Facilities Security immediately so the badge can be deactivated. A replacement badge fee of $25 applies after the second lost badge in a 12-month period."),
        ("After-Hours Access", "Access to office facilities outside of standard hours (8 PM - 6 AM) is logged and reviewed weekly by Facilities Security for unusual patterns."),
    ]),
    ("Drug and Alcohol Policy", "hr_compliance", [
        ("Workplace Standard", "Employees must not be under the influence of illegal drugs or alcohol, or misuse prescription medication, in a manner that impairs their ability to safely and effectively perform their job duties."),
        ("Company Events", "Alcohol may be served at approved company events at the discretion of the event organizer, with non-alcoholic options always available. Employees are expected to drink responsibly and are never required to consume alcohol."),
        ("Safety-Sensitive Roles", "Employees in safety-sensitive roles (e.g., operating company vehicles or machinery) are subject to additional restrictions and may be required to undergo testing in accordance with applicable law."),
        ("Support Resources", "Employees struggling with substance use are encouraged to seek help through the Employee Assistance Program (EAP), which provides confidential counseling and treatment referrals at no cost."),
        ("Violations", "Reporting to work under the influence, or possession/distribution of illegal drugs on company premises, may result in disciplinary action up to and including termination."),
    ]),

    # ---- Marketing / Sales ----
    ("Social Media Policy", "marketing_communications", [
        ("Personal Use", "Employees may identify themselves as working for the company on personal social media but must make clear that views expressed are their own and not those of the company."),
        ("Confidential Information", "Employees must not share confidential company information, including unannounced products, financial results, or customer data, on any social media platform."),
        ("Official Accounts", "Only Marketing and Corporate Communications may create or post on official company social media accounts. Department-specific accounts require approval and ongoing oversight from Marketing."),
        ("Crisis Situations", "During a company crisis or major incident, all employees should refrain from posting about the situation on social media and direct inquiries to Corporate Communications."),
        ("Endorsements and Influencers", "Engagements with external influencers or content creators to promote company products must comply with FTC disclosure guidelines (e.g., #ad, #sponsored) and be coordinated through Marketing."),
    ]),
    ("Brand and Trademark Usage Policy", "marketing_brand", [
        ("Logo Usage", "The company logo must only be used in its approved forms (color, monochrome, reversed) as provided in the brand asset library, with minimum clear space and size requirements respected."),
        ("Co-Branding", "Co-branding with partners or customers (e.g., joint webinars, case studies) requires approval from Marketing and must follow the joint usage guidelines in the partner brand kit."),
        ("Trademark Notices", "Company trademarks must be marked with the appropriate ® or ™ symbol on first prominent use in external materials, as advised by the Legal team."),
        ("Third-Party Use", "External parties (customers, partners, press) wishing to use company trademarks or product names must request approval through Marketing, which maintains a trademark usage guideline document."),
        ("Internal Templates", "Employees creating external-facing materials (presentations, proposals) must use approved templates from the brand portal rather than recreating logos or layouts independently."),
    ]),
    ("Customer Data Handling Policy", "legal_privacy", [
        ("Access Controls", "Access to customer data is granted on a least-privilege, role-based basis. Support and Sales teams may access customer account data only as needed to perform their job functions."),
        ("Data Use Limitations", "Customer data may only be used for the purposes disclosed in the company's privacy policy and customer agreements (e.g., providing the service, support, and product improvement)."),
        ("Data Sharing", "Customer data must not be shared with third parties except as required to deliver the service (e.g., approved subprocessors) or as required by law, and only under an executed data processing agreement."),
        ("Support Tickets", "Support staff must not request or store full payment card numbers, passwords, or government ID numbers in support tickets; such data should be redirected to secure, PCI-compliant channels."),
        ("Data Subject Requests", "Customer requests to access, export, or delete their data must be routed to the Privacy team and fulfilled within the timeframe specified in the customer agreement or applicable law."),
    ]),
    ("Sales Commission Policy", "sales_compensation", [
        ("Commission Structure", "Account Executives earn a commission of 8% of new annual contract value (ACV) and 4% of renewal ACV, paid monthly on collected revenue."),
        ("Quota and Accelerators", "Quota attainment above 100% earns an accelerator of 1.5x the standard commission rate on the incremental revenue above quota, up to a maximum of 200% of quota."),
        ("Splits", "Deals involving multiple sales representatives (e.g., account executive and sales engineer) are split according to the standard split table published by Sales Operations, defaulting to 80/20 unless otherwise agreed in writing before close."),
        ("Clawbacks", "Commissions are subject to clawback if a customer cancels or fails to pay within 90 days of the deal closing, proportional to the unpaid amount."),
        ("Draw and Guarantees", "New Account Executives receive a guaranteed commission draw for their first 3 months of employment (ramp period) to account for pipeline-building time."),
    ]),

    # ---- Facilities ----
    ("Office Access and Badge Policy", "facilities_security", [
        ("Badge Issuance", "New employees receive their access badge during Day 1 onboarding, programmed for their assigned office location and standard access hours (7 AM - 8 PM, Monday-Friday)."),
        ("Multi-Site Access", "Employees who regularly travel between offices may request multi-site badge access from Facilities, approved by their manager, valid for up to 12 months before renewal."),
        ("Tailgating", "Employees must not hold doors open for individuals without a valid badge ('tailgating'), even if they appear to be employees, and should direct them to reception."),
        ("Contractor Badges", "Contractors and temporary staff receive time-limited badges that automatically expire at the end of their contract period as recorded in the vendor management system."),
        ("Badge Deactivation", "Badges are deactivated immediately upon termination of employment or contract, coordinated between HR/Procurement and Facilities Security."),
    ]),
    ("Workplace Dress Code Policy", "hr_workplace", [
        ("General Guidance", "The company maintains a casual dress code for most roles. Employees should use judgment to dress appropriately for their day's activities, including client meetings or site visits."),
        ("Client-Facing Roles", "Employees meeting with clients in person, or representing the company at conferences, should dress in business casual attire unless the client or event context calls for more formal dress."),
        ("Safety Requirements", "Employees visiting warehouses, labs, or manufacturing areas must wear the required personal protective equipment (PPE), including closed-toe shoes and safety glasses where posted."),
        ("Remote Video Calls", "While there is no strict dress code for video calls, employees should ensure attire is appropriate and professional for internal and external meetings."),
        ("Company Apparel", "Company-branded apparel provided at events or as swag may be worn at the employee's discretion and is encouraged at company-sponsored public events."),
    ]),
    ("Desk and Workspace Policy", "facilities_operations", [
        ("Desk Assignment", "Employees in hybrid roles are assigned to a desk neighborhood by team rather than a fixed individual desk, supporting flexible in-office attendance via desk booking."),
        ("Desk Booking", "Employees should reserve a desk through the workplace app before coming into the office on days when neighborhood capacity may be constrained, particularly on core in-office days."),
        ("Clean Desk Policy", "At the end of each day, employees using shared desks must clear personal items and any documents containing Confidential or Restricted information, storing them in a locker or secure drawer."),
        ("Personalization", "Personal items at shared desks should be limited to what fits in an assigned locker. Permanent desk decorations are reserved for employees with fixed desk assignments (e.g., specialized equipment needs)."),
        ("Meeting Room Etiquette", "Meeting rooms should be booked only for the duration needed and released promptly if a meeting ends early or is cancelled, to maximize availability for other teams."),
    ]),
    ("Sustainability and Environmental Policy", "facilities_sustainability", [
        ("Carbon Footprint Goals", "The company has committed to reducing its operational carbon footprint by 50% by 2030 (from a 2024 baseline) and achieving net-zero emissions by 2040."),
        ("Office Operations", "Offices prioritize energy-efficient lighting and HVAC systems, recycling and composting programs, and elimination of single-use plastics in break rooms and cafeterias."),
        ("Business Travel", "Employees are encouraged to use video conferencing in place of travel where practical. When travel is necessary, direct flights are preferred to reduce emissions from layovers."),
        ("Supplier Standards", "Significant suppliers (over $100,000 annual spend) are asked to complete an environmental practices questionnaire as part of the vendor onboarding and annual review process."),
        ("Employee Engagement", "The company supports employee-led Green Teams at each office location and provides an annual volunteer day employees can use for environmental community service."),
    ]),

    # ---- Misc ----
    ("Travel Safety Policy", "hr_travel", [
        ("Trip Registration", "All international business travel must be registered in the travel management system at least 5 business days in advance so the company can track employee locations for duty-of-care purposes."),
        ("High-Risk Destinations", "Travel to destinations classified as high-risk by the company's travel security provider requires additional approval from the employee's VP and a pre-travel safety briefing."),
        ("Emergency Assistance", "Employees traveling for business have access to a 24/7 travel assistance hotline providing medical, security, and evacuation support while abroad."),
        ("Health Precautions", "Employees traveling to regions requiring vaccinations or health precautions should consult the company's travel health resources and may seek reimbursement for required vaccinations."),
        ("Communication Check-Ins", "Employees traveling to high-risk destinations are asked to check in with their manager or the Travel Security team daily during their trip."),
    ]),
    ("Vendor Management Policy", "finance_procurement", [
        ("Vendor Onboarding", "New vendors must complete onboarding, including a W-9 (or local equivalent), banking details verification, and a security/privacy questionnaire for vendors handling company or customer data."),
        ("Contract Management", "All vendor contracts over $10,000 annually must be reviewed by Legal and stored in the central contract repository before signature, with renewal dates tracked to avoid auto-renewal surprises."),
        ("Vendor Risk Tiering", "Vendors are tiered (Low, Medium, High risk) based on data access and business criticality. High-risk vendors undergo annual security reassessments and require cyber insurance evidence."),
        ("Performance Reviews", "Business owners of strategic vendor relationships (over $250,000 annually) conduct quarterly business reviews covering performance, SLAs, and upcoming needs."),
        ("Vendor Offboarding", "When a vendor relationship ends, the business owner must ensure data is returned or destroyed per the contract, access is revoked, and final invoices are reconciled within 30 days."),
    ]),
    ("Conflict of Interest Policy", "hr_compliance", [
        ("Disclosure Requirement", "Employees must disclose any situation that could create, or appear to create, a conflict between their personal interests and the interests of the company by completing an annual Conflict of Interest declaration."),
        ("Outside Employment", "Employees must obtain written approval from their manager and HR before accepting outside employment, consulting work, or board positions, particularly with competitors, customers, or vendors."),
        ("Family and Personal Relationships", "Employees must disclose close personal relationships with colleagues in their reporting line (direct or indirect) so reporting structures can be adjusted to avoid conflicts in pay, promotion, or performance decisions."),
        ("Financial Interests", "Employees with a significant financial interest (generally over 5% ownership, or any ownership for employees involved in vendor selection) in a company supplier, customer, or competitor must disclose this to Legal."),
        ("Review and Resolution", "Disclosed conflicts are reviewed by HR and Legal, who may require recusal from related decisions, reassignment of responsibilities, or other mitigations."),
    ]),
    ("Gift and Hospitality Policy", "hr_compliance", [
        ("General Limits", "Employees may give or receive gifts, meals, and entertainment from business contacts only if they are reasonable in value (generally under $100), infrequent, and not intended to improperly influence a business decision."),
        ("Government Officials", "Gifts, meals, or entertainment provided to government officials are subject to stricter limits (often near-zero) under anti-bribery laws and require pre-approval from Legal regardless of value."),
        ("Approval and Reporting", "Gifts or hospitality valued over $100, or any cash/cash-equivalent gifts (which are always prohibited), must be reported to the employee's manager and logged in the gift register maintained by Compliance."),
        ("Procurement Contexts", "Employees involved in vendor selection or contract negotiations must decline gifts and hospitality from prospective vendors during the active procurement process to avoid the appearance of bias."),
        ("Holiday Gifts", "Modest holiday gifts from vendors (e.g., branded items, food baskets) intended for an entire team or office may be accepted and shared communally, but should still be logged if individually valued over $100."),
    ]),
    ("Mobile Phone and Communication Reimbursement Policy", "finance_expenses", [
        ("Eligibility", "Employees whose roles require regular use of a mobile phone for business purposes (e.g., client-facing, on-call, or frequently traveling roles) are eligible for a monthly communications stipend."),
        ("Stipend Amounts", "- Standard stipend: $30/month toward a personal mobile plan.\n- On-call/IT roles: $50/month.\n- International roles requiring frequent roaming: additional reimbursement for documented roaming charges with manager approval."),
        ("Company-Issued Phones", "Certain roles (e.g., Executive team, on-call Engineering leads) may instead be issued a company-owned phone and plan in lieu of a stipend, managed through IT Asset Management."),
        ("Submission Process", "Stipends are requested once via the expense system and continue automatically each month until the employee's role changes or employment ends; no monthly resubmission is required."),
        ("Acceptable Use", "Employees receiving a stipend or company phone must comply with the BYOD or IT Security policy as applicable, including enrollment in MDM if accessing company email or data."),
    ]),
]


DEPARTMENT_AREAS = {
    "hr": "Human Resources",
    "it": "Information Technology",
    "finance": "Finance",
    "legal": "Legal",
    "facilities": "Facilities",
    "marketing": "Marketing",
    "sales": "Sales",
}

# Policies that cover sensitive management decisions (compensation, hiring/firing,
# budget and procurement authority, sales pay structure) are restricted to managers.
# Everything else is general workplace guidance available to all employees (ICs).
MANAGER_ONLY_POLICIES = {
    "Performance Review Policy",
    "Compensation and Benefits Policy",
    "Recruitment and Hiring Policy",
    "Termination and Offboarding Policy",
    "Budget Approval Policy",
    "Financial Reporting Policy",
    "Procurement and Purchasing Policy",
    "Vendor Management Policy",
    "Sales Commission Policy",
}


def build_content(title: str, sections: list[tuple[str, str]]) -> str:
    parts = [title]
    for heading, body in sections:
        parts.append(f"{heading}:\n{body}")
    return "\n\n".join(parts)


def main():
    docs = []
    for title, policy_type, sections in POLICIES:
        department_area = DEPARTMENT_AREAS[policy_type.split("_")[0]]
        employee_level = "manager" if title in MANAGER_ONLY_POLICIES else "IC"
        docs.append(
            {
                "content": build_content(title, sections),
                "metadata": {
                    "department_area": department_area,
                    "policy_type": policy_type,
                    "employee_level": employee_level,
                    "status": "active",
                    "title": title,
                },
            }
        )

    out_path = Path(__file__).parent / "policies.json"
    out_path.write_text(json.dumps(docs, indent=2) + "\n")
    print(f"wrote {len(docs)} policies to {out_path}")


if __name__ == "__main__":
    main()
