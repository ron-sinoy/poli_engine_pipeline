### Tech Stack
- use python
- use any frameworks or libraries, if required, ask for permission and run.

### Note
- All files should be modular, that is callable from main.py
- Don't change location of the files
### Flow 
Loop → item→feed to llm →isPolitical → thread → fetchThreadContents → feed to llm → checkDuplication →paraphrase → inserttodb

#### backend url : 
https://poli-engine-backend-production.up.railway.app/threadsList

### Task
1. use gold_final_resulats.json -> final_response to be used for call POST/ incidents and post each one of them
2. eg of gold_final_resulats.json -> final_response
	1. {

"thread_id": 2,

"body": "തിരഞ്ഞെടുപ്പ് കാലത്ത് അനുവദിച്ച കെ.എസ്.ആർ.ടി.സി ബസ് ഫലപ്രഖ്യാപനത്തിന് പിന്നാലെ സർവീസ് നിർത്തി. മുഖ്യമന്ത്രിയുടെ മണ്ഡലമായ ധർമ്മടത്തെ യാത്രക്കാരാണ് പരാതിയുമായി രംഗത്തെത്തിയത്.",

"source_url": "/263/news/kerala/ksrtc-bus-service-dharmadam-suspended-election-dbiliqfy",

"persons_involved": [

1

]

},

### Format of post incidents body
{
"thread_id": 1,
"body": "മന്ത്രി പത്രസമ്മേളനത്തിൽ വിവാദ പ്രസ്താവന നടത്തി", 
"source_url": "https://example.com/news/incident1",
"persons_involved": [1,2]
}