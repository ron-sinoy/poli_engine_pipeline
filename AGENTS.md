# Agent Instructions

## Restricted Files
- Never read, print, log, or modify `.env` or any file containing secrets/keys.

## Scope
These instructions apply to the entire `/home/ronsinoy/playground/gb/pipeline` workspace unless a more specific `AGENTS.md` exists in a subdirectory.

Before changing files, check this file and any nearer `AGENTS.md` files that apply to the files being edited.

## Working Rules
- always assume data shape is perfect.
- Keep edits scoped to the requested task.
- Ask for clarification when project-specific requirements are ambiguous or conflict.

## Overall techstack
- Work with python
- If you got any suggestions on adding any framework or library ask me
- follow naming conventions followed in bronze

## How to do task
Log everything into AGENT_LOG.md file, by following rules stated in that file

## Backend url
  https://poli-engine-backend-production.up.railway.app

## What to do
1. make sure to add source into each before removing source parents
2. create a specific_modules/enrich_data
	Fetch the itemsdetailurl
	then clean the following format according if else source name
	for mathrubhumi following is the data format remove everything other than element type 0/1 
	then merge all data
	use before used inbuilt funtions
data model
{
  "contentType": 0,
  "itemTitle": "'നീറ്റ് പുനഃപരീക്ഷ നടപടികളിൽ പ്രധാനമന്ത്രി നേരിട്ട് മേൽനോട്ടംവഹിക്കുന്നു'; കേന്ദ്രം സുപ്രീം കോടതിയിൽ",
  "publishedTime": "May 29, 2026, 17:21",
  "contentID": "i2o8l9u6",
  "commentID": "1rftbffboq5q314n5fo",
  "itemAuthor": "ബി. ബാലഗോപാല്‍/മാതൃഭൂമി ന്യൂസ്",
  "itemAuthorImage": "",
  "itemColumnName": "",
  "itemColumnURL": "",
  "contentItemLabel": "",
  "itemImageURL": "/view/acePublic/alias/contentid/1rftaq0nmd1iffnrwke/0/narendra-modi-jpg.webp?f=3:2&w=735&q=0.75",
  "itemImageCaption": "നരേന്ദ്ര മോദി | Photo: AFP",
  "itemTitleLead": "",
  "commentsURL": "OPEN",
  "videoBaseURL": "https://content.jwplatform.com/",
  "sectionTitle": "News",
  "sectionTitleURL": "/263/news",
  "subSectionTitle": "India",
  "seeAllURL": "/263/news/india",
  "itemDetailURL": "/263/news/india/neet-re-exam-supreme-court-pm-modi-monitoring-i2o8l9u6",
  "shareURL": "https://www.mathrubhumi.com/news/india/neet-re-exam-supreme-court-pm-modi-monitoring-i2o8l9u6",
  "englishURL": "",
  "malayalamURL": "",
  "contentItemIcon": 0,
  "contentItemIconLabel": "",
  "readTime": "2 Min Read",
  "contentLength": "short",
  "subHeadings": [],
  "detail_elements": [
    {
      "elementType": 0,
      "elementContent": "ന്യൂഡൽഹി: ജൂൺ 21-ന് നടക്കുന്ന നീറ്റ് പുനഃപരീക്ഷ നടപടികളിൽ പ്രധാനമന്ത്രി നരേന്ദ്ര മോദി നേരിട്ട് മേൽനോട്ടം വഹിക്കുന്നതായി കേന്ദ്രം സുപ്രീം കോടതിയെ അറിയിച്ചു. അതിനാൽ ഒരു പിഴവും ഇത്തവണ ഉണ്ടാകില്ലെന്ന് സോളിസിറ്റർ ജനറൽ തുഷാർ മേത്ത സുപ്രീം കോടതിയെ അറിയിച്ചു. പുനഃപരീക്ഷയ്ക്കായി ചില പുതിയ ക്രമീകരണങ്ങൾ ഏർപ്പെടുത്തിയിട്ടുണ്ടെന്നും കേന്ദ്ര സർക്കാരും എൻടിഎയും കോടതിയെ അറിയിച്ചു.",
      "elementImageURL": ""
    },
    {
      "elementType": 8,
      "elementContent": "/1120978/300X250_MbPortal_Mapp",
      "elementImageURL": ""
    },
    {
      "elementType": 0,
      "elementContent": "പുനഃപരീക്ഷയ്ക്ക് എത്രത്തോളം മേൽനോട്ടം ഉണ്ടെന്ന കോടതിയുടെ ചോദ്യത്തിനാണ് പ്രധാനമന്ത്രി തന്നെ മേൽനോട്ടം വഹിക്കുന്നുവെന്ന മറുപടി സോളിസിസ്റ്റർ ജനറൽ നൽകിയത്. ചോദ്യ പേപ്പർ ചോർച്ച പോലെയുള്ളവ ഉണ്ടാകുന്നത് മനസികാഘാതം ഉണ്ടാക്കുന്ന കാര്യമാണെന്ന് സുപ്രീം കോടതി നിരീക്ഷിച്ചു. വിദ്യാർഥികൾക്ക് മാത്രമല്ല അവരുടെ കുടുംബങ്ങൾക്കും ഇത് കടുത്ത മാനസിക സംഘർഷം ഉണ്ടാക്കുന്ന കാര്യമാണെന്നും യുവാക്കളെ നിരാശരാക്കരുതെന്നും കോടതി അഭിപ്രായപ്പെട്ടു.",
      "elementImageURL": ""
    },
    {
      "elementType": 11,
      "elementContent": "",
      "elementImageURL": ""
    },
    {
      "elementType": 0,
      "elementContent": "നീറ്റ് ചോദ്യപേപ്പർ ചോർച്ചയുടെ പശ്ചാത്തലത്തിൽ പുനഃപരീക്ഷയിലെ ചോദ്യ പേപ്പർ ചോരാതിരിക്കാൻ എല്ലാ നടപടികളും സ്വീകരിച്ചിട്ടുണ്ടെന്ന് എൻടിഎ സുപ്രീം കോടതിയെ അറിയിച്ചു. പരീക്ഷയുടെ പരിശുദ്ധി കാത്തുസൂക്ഷിക്കുന്നതിൽ പ്രതിജ്ഞാബദ്ധം ആണ്. അതിനായി പുതിയ ക്രമീകരണങ്ങൾ ഏർപ്പെടുത്തിയിട്ടുണ്ടെന്നും എൻടിഎ സത്യവാങ്മൂലത്തിലൂടെ കോടതിയെ അറിയിച്ചു.",
      "elementImageURL": ""
    },
    {
      "elementType": 8,
      "elementContent": "/1120978/300X250_MbPortal_Mapp_2",
      "elementImageURL": ""
    },
    {
      "elementType": 0,
      "elementContent": "ചോദ്യപ്പേപ്പർ ചോർച്ചയുമായി ബന്ധപ്പെട്ട അന്വേഷണം എങ്ങനെയാണ് പൂർത്തിയാക്കുക എന്നത് സംബന്ധിച്ച വിശദമായ സത്യവാങ്മൂലം സമർപ്പിക്കാൻ കോടതി സർക്കാരിനോട് ആവശ്യപ്പെട്ടിട്ടുണ്ട്. പരീക്ഷാ നടത്തിപ്പിലെ പാളിച്ചകളെക്കുറിച്ച് ചോദ്യങ്ങൾ ഉന്നയിച്ച കോടതി, ഉയർന്ന സമിതികൾ ഉണ്ടായിട്ടും ഇത്തരം സംഭവങ്ങൾ ഉണ്ടാകുന്നത് സംവിധാനത്തിലെ പോരായ്മയാണോ എന്ന് പരിശോധിക്കണമെന്നും ആവശ്യപ്പെട്ടു.",
      "elementImageURL": ""
    },
    {
      "elementType": 0,
      "elementContent": "സിബിഐ ആണ് നിലവിൽ കേസ് അന്വേഷിക്കുന്നത്. മേയ് മൂന്നിന് നടന്ന പരീക്ഷയിൽ ക്രമക്കേട് ആരോപിക്കപ്പെട്ടതിനെത്തുടർന്ന് മെയ് 12-നാണ് പരീക്ഷ റദ്ദാക്കിയത്.",
      "elementImageURL": ""
    },
    {
      "elementType": 12,
      "elementContent": "",
      "elementImageURL": ""
    }
  ],
  "relatedArticles": [
    {
      "relatedImageURL": "/view/acePublic/alias/contentid/1rfpn98vpd996v8ssou/0/vinesh-phogat.webp?f=1:1&w=172&q=0.75",
      "relatedTitle": "വിനേഷ് ഫോഗട്ട് രാജ്യത്തിന്റെ അഭിമാനം-സുപ്രീം കോടതി; ട്രയൽസിൽ പങ്കെടുക്കാം,WFIക്ക് കനത്ത തിരിച്ചടി",
      "relatedLead": "ഗുസ്തിയിലേക്കുള്ള വിനേഷ് ഫോഗട്ടിന്റെ തിരിച്ചുവരവ് തടയാൻ ശ്രമിച്ച ഇന്ത്യൻ ഗുസ്തി ഫെഡറേഷന്റെ നടപടിയെ നേരത്തേ ഡൽഹി ഹൈക്കോടതി രൂക്ഷമായി വിമർശിച്ചിരുന്നു.",
      "relatedURL": "/263/sports/other-sports/vinesh-phogat-asian-games-trials-supreme-court-verdict-rift45qz",
      "relatedSectionTitle": "Related Stories",
      "relatedContentType": 0,
      "relatedContentID": "rift45qz"
    },
    {
      "relatedImageURL": "/view/acePublic/alias/contentid/1rfnky5lr4vpwf0o62f/0/supreme-court-of-india.webp?f=1:1&w=172&q=0.75",
      "relatedTitle": "'വാദം കേൾക്കൽ പൂർത്തിയായാൽ 3 മാസത്തിനുള്ളിൽ വിധി പറയണം'; ഹൈക്കോടതികൾക്ക് സുപ്രീംകോടതി നിർദേശം",
      "relatedLead": "കേസുകളുടെ വിധി പ്രസ്താവിക്കുന്നതിന് ഹൈക്കോടതികള്‍ക്ക് സുപ്രധാന നിര്‍ദേശവുമായി സുപ്രീംകോടതി.",
      "relatedURL": "/263/news/india/supreme-court-verdict-timeline-guidelines-f2epzhi3",
      "relatedSectionTitle": "Related Stories",
      "relatedContentType": 0,
      "relatedContentID": "f2epzhi3"
    },
    {
      "relatedImageURL": "/view/acePublic/alias/contentid/1rfmtklt9vie0rtp5hf/0/teacher-jpg.webp?f=1:1&w=172&q=0.75",
      "relatedTitle": "കെ-ടെറ്റ്; പുനഃപരിശോധനാ ഹർജികൾ തള്ളി; പരീക്ഷ പാസാകാനുള്ള സമയപരിധി ഒരു വർഷം നീട്ടി",
      "relatedLead": "കെ-ടെറ്റ് യോഗ്യത നേടാത്ത അധ്യാപകരെ പുറത്താക്കണമെന്ന വിധിക്ക് എതിരായ പുനഃപരിശോധന ഹര്‍ജികള്‍ സുപ്രീംകോടതി തള്ളി.",
      "relatedURL": "/263/news/india/k-tet-exam-deadline-extension-supreme-court-ruling-xh7ak18v",
      "relatedSectionTitle": "Related Stories",
      "relatedContentType": 0,
      "relatedContentID": "xh7ak18v"
    },
    {
      "relatedImageURL": "/view/acePublic/alias/contentid/1reke77mn42i6tn4194/0/supreme-court-jobs-jpg.webp?f=1:1&w=172&q=0.75",
      "relatedTitle": "ട്രാൻസ്ജെൻഡർ ഭേദഗതി നിയമം: ഹർജികൾ സുപ്രീംകോടതിയിലേക്ക് മാറ്റണമെന്ന് കേന്ദ്രം",
      "relatedLead": "ഡൽഹി, കേരളം അടക്കമുള്ള ഹൈക്കോടതികളിൽനിന്ന് കേസ് മാറ്റണമെന്നാണ് കേന്ദ്രത്തിന്റെ ആവശ്യം.",
      "relatedURL": "/263/social/news/centre-seeks-transfer-transgender-protection-act-pleas-supreme-court-ebmbalc0",
      "relatedSectionTitle": "Related Stories",
      "relatedContentType": 0,
      "relatedContentID": "ebmbalc0"
    },
    {
      "relatedImageURL": "/view/acePublic/alias/contentid/1red7fqi3klrhwp66pp/0/wetland-1-jpg.webp?f=1:1&w=172&q=0.75",
      "relatedTitle": "സംരക്ഷണം ഇല്ലാതാകുന്നു; ‘തണ്ണീർത്തടം’ എന്ന വാക്കിന്റെ നിർവചനം പരിശോധിക്കാൻ സുപ്രീം കോടതി",
      "relatedLead": "",
      "relatedURL": "/263/environment/news/supreme-court-review-wetlands-definition-2017-rules-iahtsvy6",
      "relatedSectionTitle": "Related Stories",
      "relatedContentType": 0,
      "relatedContentID": "iahtsvy6"
    },
    {
      "relatedImageURL": "/view/acePublic/alias/contentid/1re2fdyl26eh2t32zw9/0/icds-supervisor-supreme-court-ask-uphold-highcourt-verdict.webp?f=1:1&w=172&q=0.75",
      "relatedTitle": "എസ്.ഐ.ആർ ശരിവെച്ച് സുപ്രീംകോടതി; വോട്ടർ പട്ടികയിൽ നിന്ന് പേര് നീക്കിയാൽ പൗരത്വം നഷ്ടമാകില്ല",
      "relatedLead": "എസ്‌ഐആര്‍ എന്നത് പിന്‍വാതിലിലൂടെയുള്ള പൗരത്വ പരിശോധനയാണെന്ന് ആരോപിച്ച് ഹര്‍ജിക്കാരും പ്രതിപക്ഷവും ഉയര്‍ത്തിയ തടസ്സവാദങ്ങള്‍ കോടതി തള്ളി.",
      "relatedURL": "/263/news/india/supreme-court-upholds-election-commission-voter-list-revision-sir-gjmwuei2",
      "relatedSectionTitle": "Related Stories",
      "relatedContentType": 0,
      "relatedContentID": "gjmwuei2"
    },
    {
      "relatedImageURL": "/view/acePublic/alias/contentid/1rdefckdr84fh2t4lcs/1/suresh-gopi-jpg.webp?f=1:1&w=172&q=0.75",
      "relatedTitle": "ലോക്സഭാംഗത്വം റദ്ദാക്കണമെന്ന ആവശ്യത്തിനെതിരെ സുരേഷ് ഗോപിയുടെ ഹർജിയിൽ സുപ്രീം കോടതി നോട്ടീസ്",
      "relatedLead": "സുരേഷ് ഗോപി ഫയൽ ചെയ്ത ഹർജിയിൽ ജസ്റ്റിസ് പി.എസ്. നരസിംഹ അധ്യക്ഷനായ ബെഞ്ചാണ് നോട്ടീസ് അയച്ചത്.",
      "relatedURL": "/263/news/kerala/suresh-gopi-thrissur-lok-sabha-election-petition-supreme-court-mi7s9n36",
      "relatedSectionTitle": "Related Stories",
      "relatedContentType": 0,
      "relatedContentID": "mi7s9n36"
    }
  ],
  "tagList": [
    {
      "tagTitle": "NEET",
      "tagURL": "/263/topics/tag/neet"
    },
    {
      "tagTitle": "CBSE NEET",
      "tagURL": "/263/topics/tag/cbse_neet"
    },
    {
      "tagTitle": "Supreme Court Of India",
      "tagURL": "/263/topics/tag/supreme_court_of_india"
    },
    {
      "tagTitle": "NEET UG 2026",
      "tagURL": "/263/topics/tag/neet_ug_2026"
    },
    {
      "tagTitle": "Narendra Modi",
      "tagURL": "/263/topics/person/narendra_modi"
    }
  ],
  "nextStory": {
    "contentType": "",
    "contentID": "",
    "itemDetailURL": ""
  }
}