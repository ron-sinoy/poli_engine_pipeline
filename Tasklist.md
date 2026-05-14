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
1. As of now if llm finds the thread dont align with any threads its thread id is given as 1
2. instead create a new thread, with new thread id and call get threadslist again and use that new thread id
3. already post /threads is available
	1. body of post is given as this
	2. {

"title": "ടെസ്റ്റ് തൃെഡ്",

"summary": "ഇത് ഒരു ടെസ്റ്റ് സംഗ്രഹമാണ്"

}
ask gemini to create a title and summary

