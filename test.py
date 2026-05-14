import os
from google import genai

# Note: Hardcoding keys makes them visible to anyone who has the file.
client = genai.Client(api_key="AIzaSyBb8vXh2Sk_HH7nRPG_rwpPcfXWeZKU9Jk")

input_string = "ന്യൂഡൽഹി: മുതിർന്ന നേതാക്കളുമായുള്ള അവസാനഘട്ട ചർച്ചകൾ പൂർത്തിയാക്കിയ കോൺഗ്രസ് ഹൈക്കമാൻഡ് കേരളത്തിന്റെ മുഖ്യമന്ത്രിയെ ബുധനാഴ്ച പ്രഖ്യാപിച്ചേക്കും.\n\nപ്രതിപക്ഷ നേതാവ് രാഹുൽ ഗാന്ധി ചൊവ്വാഴ്ച നടത്തിയ കൂടിക്കാഴ്ചയിൽ നേതാക്കളെല്ലാം തീരുമാനം വൈകരുതെന്ന് ഒറ്റസ്വരത്തിൽ ആവശ്യപ്പെട്ടു.\n\nകർണാടകത്തിലുള്ള കോൺഗ്രസ് അധ്യക്ഷൻ മല്ലികാർജുൻ ഖാർഗെയോട് ഡൽഹിയിലെത്താൻ സോണിയാ ഗാന്ധി നിർദേശിക്കുകയും ചെയ്തു. നേതാക്കളുടെ അഭിപ്രായത്തിന്റെ രത്‌നച്ചുരുക്കം ഖാർഗെയുമായി സോണിയാ ഗാന്ധിയും പ്രിയങ്കാ ഗാന്ധിയും ബുധനാഴ്ച ചർച്ചചെയ്ത ശേഷമാവും അന്തിമതീരുമാനം പ്രഖ്യാപിക്കുക.\n\nഘടകകക്ഷികളെ വിവരം ഔദ്യോഗികമായി അറിയിച്ച് പിന്തുണയും തേടും.\n\nകെ.പി.സി.സി. മുൻ അധ്യക്ഷരായ വി.എം. സുധീരൻ, എം.എം. ഹസൻ, കെ. മുരളീധരൻ, കെ. സുധാകരൻ എന്നിവരുമായും അച്ചടക്ക സമിതി ചെയർമാൻ തിരുവഞ്ചൂർ രാധാകൃഷ്ണൻ, വർക്കിങ് പ്രസിഡന്റുമാരായ എ.പി. അനിൽകുമാർ, പി.സി. വിഷ്ണുനാഥ്, ഷാഫി പറമ്പിൽ എന്നിവരുമായാണ് ചർച്ച നടന്നത്.\n\nമുരളീധരനും സുധീരനുമൊഴികെ മറ്റെല്ലാവരും കെ.സി. വേണുഗോപാൽ മുഖ്യമന്ത്രിയാവുന്നതിനോട് യോജിച്ചതായാണറിയുന്നത്. വി.ഡി. സതീശന് അനുകൂലമായി ജനവികാരമുണ്ടെന്ന് പറഞ്ഞ മുരളീധരൻ, ഹൈക്കമാൻഡ് എന്തു തീരുമാനമെടുത്താലും വൈകരുതെന്ന് നിർദേശിച്ചു."

# Renamed 'dir' to 'script_dir' to avoid shadowing the built-in dir() function
script_dir = os.path.dirname(os.path.abspath(__file__))

try:
    with open(os.path.join(script_dir, "prompt.txt"), "r", encoding="utf-8") as f:
        prompt = f.read()
except FileNotFoundError:
    print("Error: prompt.txt not found in the script directory.")
    prompt = ""

full_prompt = f"{prompt}\n\n{input_string}"

# Change the model name here
response = client.models.generate_content(
    model="gemini-3.1-flash-lite", 
    contents=full_prompt
)

print(response.text)