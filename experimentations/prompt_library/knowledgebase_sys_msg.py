from datetime import datetime

qrc_knowledgebase_system_message = """
Table Name: [CustomerSupportGPT].[dbo].[QRCKnowledgeBase]
Description: This table stores detailed customer support tickets including type (query, request, or complaint), communication mode, sentiment, banking product involved, resolution status, and escalation details.

Columns:
- 'CreatedDate' : Timestamp indicating when the query, request, or complaint was received (column format : "yyyy-mm-dd").
- 'TicketNo' : A unique identifier assigned to each support case or ticket.
- 'Mode' : Channel used by the customer to contact support (AVAILABLE VALUES:- Mails,Call).
- 'NameOfCustomer' : Full name of the customer who raised the issue.
- 'MobileNo' : Customer's contact mobile number.
- 'Email' : Customer's email address.
- 'DetailOfQRC' : Detailed text describing the Query, Request, or Complaint.
- 'QueryRequestComplaint' : Type of the interaction: whether it's a query, a request, or a complaint(Request,Query,Complaint).
- 'Product' : Product or service related to the issue (e.g., CASA, Fixed Deposit, Loans).
- 'Category' : High-level classification of the issue (e.g., Mobile Banking, KYC).
- 'SubCategory' : Specific sub-classification within the main category (e.g., Login Issue).
- 'Vertical' : Business vertical involved (e.g., Consumer Banking, Digital Banking).
- 'LastResponseToCustomer' : Final response or resolution message sent to the customer.
- 'ClosureDate' : Date when the ticket was officially resolved or closed.
- 'Status' : Current ticket status (AVAILABLE VALUES:- Open, Closed).
- 'FintechPartner' : Third-party fintech partner associated with the issue, if any.
- 'Level' : Escalation level (e.g., Level 1, Level 2).
- 'CustomerQueryInShort' : A brief summary or title describing the customer's issue.
- 'Sentiment' : Emotion detected or expressed by the customer (Positive, Neutral, Negative).
- 'ReasonForNotSatisfied' : Explanation provided by the customer for dissatisfaction, if any.
- 'IssueCategory' : Broader issue classification (AVAILABLE VALUES:- Product,Customer,Technical,Process,Operations).
"""
# prompt  (CHANGE IN SYSTEM PROMPT)
current_date_prompt = f"""Today's date is {str(datetime.today().strftime("%y-%m-%d"))},
Use this date whenever there is a requirement current date in a query"""