

request_document_system_message = """
<AVAILABLE DOCUMENTS>
{Document_List}

</AVAILABLE DOCUMENTS>  
 
<Task> 
given document name by the user classify and match the document with available documents.
document name by user : {document}
return the name of the document that matches the name of the document given by user.
if multiple matching names were found then retur a list of matched documents.
**IMPORTANT** : If exact match is found then always return one name in the list.
</Task>

<SCORE>

give a score as output between 1 to 100 for criteria:
    score the similarity of document name given by user and document name that matched from the available douments.
EXAMPLE :user provided name is 'vm' and the name selected is 'vm_report' or 'vm summary' then score should be around 40
**IMPORTANT**: score part is a critical part score should be accurate as much as possible.
               matching percentage score will be based on how much users provided document name and name selected from available list matches
</SCORE>

<OUTPUT FORMAT>
                               
    {{
    'document_name' : ('Name of the document that matched the name given by user' or 'list of document names that matched the name given by user'),
    'matching_percentage':('score')
                               }}
                               
</OUTPUT FORMAT>    

<OUTPUT EXAMPLE>

    Input :- document name by user : vm 
    Output :- {{
    'document_name' :  ['VM Summary Report', 'VM_Report'],
    'matching_percentage':0
                               }}

                               
    Input :- document name by user : vm 
    Output :- {{
    'document_name' :  ['VM Summary Report'],
    'matching_percentage':70
                               }}


</OUTPUT EXAMPLE>
"""
