# i18n review notes

Status: **every Hindi and Marathi string needs native review** (the table below lists all of them).
The English source is the reference text. Keys are the contract keys in `docs/CONTRACTS.md`.

## Terms I was unsure about

- **Protector of Emigrants**: kept in English with the Hindi/Marathi name in brackets. Check the official Marathi/Hindi term.
- **MEA, eMigrate, RC number, PBBY, AI**: kept in Latin script. PBBY is expanded once in `rule.R9_PBBY_MISSING.hit`.
- **Tripartite contract**: written as "three-party contract" in English; Hindi "तीन पक्षों वाला अनुबंध", Marathi "तीन पक्षांचा करार".
- **Simulated / demo**: "सिमुलेटेड" and "सिम्युलेटेड" are used with "(डेमो)". Confirm the everyday word.
- **Check-in, alert, plan**: kept as loanwords (चेक-इन, अलर्ट) because young users use them.
- **Employer / agent**: नियोक्ता / एजेंट (Hindi), नियोक्ता / एजंट (Marathi).
- **Visa names**: टूरिस्ट, विज़िट (Hindi); टुरिस्ट, व्हिजिट (Marathi).

## Product-rule decisions

- The word "safety" and its equivalents are not used in any value. The check-in feature is called "Check-in plan" (चेक-इन योजना / चेक-इन योजना). The key names keep `safety.*`.
- `check.demo_scam` is a key name only; the English value reads "Bangkok data-entry offer (synthetic)". The key name contains "scam" because the contract fixes it. Rename the key only through the lead.
- Heuristic rules H1-H3 say "warning sign, not a legal rule".
- R9 is information only.

## Open points for the lead

- **R4 fee cap**: `backend/rules.py` says the Rs 30,000 + 18% GST figure must be verified before release. The copy says "the limit in MEA advice" and does not state the amount. Adding the amount needs a `{cap}` placeholder in all three languages.
- **R2 date**: `rule.R2_RA_NOT_LISTED.hit` contains `{date}`. The backend must pass the list date when this rule is `hit`. The clear and unknown texts have no placeholder.
- **Verdict body length**: `verdict.STOP.body` and `verdict.VERIFY_FIRST.body` are one or two sentences each, as the spec requires.
- **Helplines**: the copy does not list helpline numbers. `limits.verify_contacts` says to check them on official sites.
- **Synthetic labels**: all demo offers are labelled synthetic in `check.demo_*`, `app.synthetic_badge`, `map.synthetic_badge`, and `limits.what_it_does`.

## Strings in the reference table

| Key | English source | Hindi (needs native review) | Marathi (needs native review) |
|---|---|---|---|
| `app.name` | Saavdhan | Saavdhan | Saavdhan |
| `app.tagline` | Check a job offer before you pay an agent or travel. | विदेश में नौकरी के ऑफ़र की जाँच करें, उसके बाद ही एजेंट को पैसे दें या यात्रा करें। | परदेशातील नोकरीचा ऑफर आधी तपासा, मगच एजंटला पैसे द्या किंवा प्रवास करा. |
| `app.synthetic_badge` | Synthetic demo data | काल्पनिक डेमो डेटा | काल्पनिक डेमो डेटा |
| `lang.en` | English | English | English |
| `lang.hi` | हिंदी | हिंदी | हिंदी |
| `lang.mr` | मराठी | मराठी | मराठी |
| `nav.check` | Check offer | ऑफ़र जाँचें | ऑफर तपासा |
| `nav.verdict` | Result | नतीजा | निकाल |
| `nav.safety` | Check-in plan | चेक-इन योजना | चेक-इन योजना |
| `nav.family` | Family | परिवार | कुटुंब |
| `nav.map` | Map | नक्शा | नकाशा |
| `nav.limits` | Limits | सीमाएँ | मर्यादा |
| `check.title` | Check your job offer | अपने नौकरी के ऑफ़र की जाँच करें | तुमच्या नोकरीच्या ऑफरची तपासणी करा |
| `check.intro` | Paste the offer or upload a file. Saavdhan checks what the offer says against public MEA guidance. | ऑफ़र का टेक्स्ट चिपकाएँ या फ़ाइल अपलोड करें। Saavdhan ऑफ़र में जो लिखा है, उसे MEA की सार्वजनिक सलाह से मिलाकर देखता है। | ऑफरचा मजकूर पेस्ट करा किंवा फाइल अपलोड करा. Saavdhan ऑफरमध्ये जे लिहिले आहे ते MEA च्या सार्वजनिक मार्गदर्शनाशी जुळवून पाहते. |
| `check.paste_label` | Paste offer text | ऑफ़र का टेक्स्ट चिपकाएँ | ऑफरचा मजकूर इथे पेस्ट करा |
| `check.paste_placeholder` | For example: Job: data entry. Salary 40,000 a month. Agent fee 2.5 lakh. Visa: visit. | उदाहरण: नौकरी: डेटा एंट्री। वेतन 40,000 महीना। एजेंट फ़ीस 2.5 लाख। वीज़ा: विज़िट। | उदाहरण: नोकरी: डेटा एंट्री. पगार 40,000 महिना. एजंट फी 2.5 लाख. व्हिसा: व्हिजिट. |
| `check.upload_label` | Or upload screenshots or a PDF (up to 10 files) | या स्क्रीनशॉट या PDF अपलोड करें (ज़्यादा से ज़्यादा 10 फ़ाइलें) | किंवा स्क्रीनशॉट किंवा PDF अपलोड करा (जास्तीत जास्त 10 फाइली) |
| `check.submit` | Check offer | ऑफ़र जाँचें | ऑफर तपासा |
| `check.demo_title` | Try a demo offer | डेमो ऑफ़र आज़माएँ | डेमो ऑफर वापरून पहा |
| `check.demo_scam` | Bangkok data-entry offer (synthetic) | बैंकॉक डेटा एंट्री ऑफ़र (काल्पनिक डेमो) | बँकॉक डेटा एंट्री ऑफर (काल्पनिक डेमो) |
| `check.demo_near_miss` | Dubai offer with gaps (synthetic) | दुबई ऑफ़र, जिसमें कुछ बातें अधूरी हैं (काल्पनिक डेमो) | दुबई ऑफर, ज्यात काही गोष्टी अपूर्ण आहेत (काल्पनिक डेमो) |
| `check.privacy_note` | Remove names, phone numbers and passport numbers before you paste. Saavdhan does not send this to any authority. | चिपकाने से पहले नाम, फ़ोन नंबर और पासपोर्ट नंबर हटा दें। Saavdhan इसे किसी सरकारी विभाग को अपने-आप नहीं भेजता। | पेस्ट करण्यापूर्वी नावे, फोन नंबर आणि पासपोर्ट नंबर काढून टाका. Saavdhan हे कोणत्याही सरकारी विभागाला आपोआप पाठवत नाही. |
| `check.analyzing` | Checking the offer... | ऑफ़र जाँचा जा रहा है... | ऑफर तपासत आहे... |
| `verdict.title` | Result | नतीजा | निकाल |
| `verdict.STOP.title` | Stop. Do not pay or travel yet. | रुकिए। अभी पैसे न दें और न जाएँ। | थांबा. आत्ता पैसे देऊ नका आणि प्रवास करू नका. |
| `verdict.STOP.body` | One or more serious points in this offer go against MEA advice. Do not pay any fee until you have checked each point with the Protector of Emigrants. | इस ऑफ़र में कुछ गंभीर बातें MEA की सलाह के खिलाफ़ हैं। प्रवासी संरक्षक (Protector of Emigrants) से हर बात की जाँच करवाने तक कोई फ़ीस न दें। | या ऑफरमध्ये काही गंभीर मुद्दे MEA च्या सल्ल्याच्या विरुद्ध आहेत. प्रवासी संरक्षक (Protector of Emigrants) कडून प्रत्येक मुद्द्याची तपासणी होईपर्यंत कोणतेही शुल्क देऊ नका. |
| `verdict.VERIFY_FIRST.title` | Check these points before you pay. | पैसे देने से पहले इन बातों की जाँच करें। | पैसे देण्यापूर्वी हे मुद्दे तपासा. |
| `verdict.VERIFY_FIRST.body` | Some points are missing or unclear. Get written answers before you pay any agent or travel. | कुछ बातें नहीं लिखी हैं या साफ़ नहीं हैं। किसी एजेंट को पैसे देने या जाने से पहले लिखित जवाब लें। | काही मुद्दे लिहिलेले नाहीत किंवा स्पष्ट नाहीत. कोणत्याही एजंटला पैसे देण्यापूर्वी किंवा प्रवास करण्यापूर्वी लेखी उत्तरे घ्या. |
| `verdict.NO_RED_FLAGS_FOUND.title` | Nothing flagged in this check | इस जाँच में कुछ नहीं मिला | या तपासणीत काहीही आढळले नाही |
| `verdict.NO_RED_FLAGS_FOUND.body` | No red flags found. Confirm with the Protector of Emigrants before paying anything. | कोई बड़ी चेतावनी नहीं मिली। कोई भी फ़ीस देने से पहले प्रवासी संरक्षक (Protector of Emigrants) से पुष्टि कर लें। | कोणताही मोठा इशारा सापडला नाही. कोणतेही शुल्क देण्यापूर्वी प्रवासी संरक्षक (Protector of Emigrants) कडून खात्री करून घ्या. |
| `verdict.ra_list_date` | Agent list checked: MEA active recruiting agent list dated {date}. | जाँची गई सूची: MEA की सक्रिय भर्ती एजेंट सूची, तिथि {date}। | तपासलेली यादी: MEA ची सक्रिय भरती एजंट यादी, तारीख {date}. |
| `verdict.quote_label` | From the offer | ऑफ़र में लिखा है | ऑफरमध्ये लिहिले आहे |
| `verdict.source_label` | Source | स्रोत | स्रोत |
| `verdict.rule_source` | Rule source | नियम का स्रोत | नियमाचा स्रोत |
| `verdict.heuristic_badge` | Warning sign, not a rule | चेतावनी का संकेत, नियम नहीं | इशाऱ्याचे चिन्ह, नियम नाही |
| `verdict.status.hit` | Point to check | जाँचने वाली बात | तपासण्यासारखा मुद्दा |
| `verdict.status.clear` | Nothing found | कुछ नहीं मिला | काही आढळले नाही |
| `verdict.status.unknown` | Not stated | नहीं लिखा है | लिहिलेले नाही |
| `verdict.method.llm` | Read by AI reader | AI से पढ़ा गया | AI ने वाचले |
| `verdict.method.fallback` | Read by simple text rules | सामान्य टेक्स्ट नियमों से पढ़ा गया | साध्या मजकूर नियमांनी वाचले |
| `verdict.download_packet` | Download report packet | रिपोर्ट पैकेट डाउनलोड करें | अहवाल पॅकेट डाउनलोड करा |
| `verdict.make_safety_plan` | Make a check-in plan | चेक-इन योजना बनाएँ | चेक-इन योजना तयार करा |
| `verdict.facts_title` | Facts from the offer | ऑफ़र की बातें | ऑफरमधील तथ्ये |
| `verdict.not_found` | Not found in the offer. | ऑफ़र में नहीं मिला। | ऑफरमध्ये सापडले नाही. |
| `severity.critical` | Critical | बहुत गंभीर | अत्यंत गंभीर |
| `severity.high` | High | गंभीर | गंभीर |
| `severity.medium` | Medium | मध्यम | मध्यम |
| `severity.low` | Low | कम | कमी |
| `severity.info` | Information | जानकारी | माहिती |
| `rule.R1_TOURIST_VISA.title` | Tourist visa is not for jobs | टूरिस्ट वीज़ा पर नौकरी नहीं | टुरिस्ट व्हिसावर नोकरी नाही |
| `rule.R1_TOURIST_VISA.hit` | The offer uses a tourist or visit visa. MEA advice says a tourist visa cannot be used for work. | ऑफ़र में टूरिस्ट या विज़िट वीज़ा लिखा है। MEA की सलाह के मुताबिक़ टूरिस्ट वीज़ा पर काम नहीं किया जा सकता। | ऑफरमध्ये टुरिस्ट किंवा व्हिजिट व्हिसा लिहिला आहे. MEA च्या सल्ल्यानुसार टुरिस्ट व्हिसावर काम करता येत नाही. |
| `rule.R1_TOURIST_VISA.clear` | The offer says the visa is for work. | ऑफ़र में लिखा है कि वीज़ा काम के लिए है। | ऑफरमध्ये लिहिले आहे की व्हिसा कामासाठी आहे. |
| `rule.R1_TOURIST_VISA.unknown` | The offer does not say what visa you will get. Ask the employer for the visa type in writing. | ऑफ़र में नहीं लिखा कि आपको कौन-सा वीज़ा मिलेगा। नियोक्ता से लिखित में वीज़ा का प्रकार माँगें। | ऑफरमध्ये कोणता व्हिसा मिळेल ते लिहिलेले नाही. नियोक्त्याकडून व्हिसाचा प्रकार लेखी मागा. |
| `rule.R2_RA_NOT_LISTED.title` | Agent not on MEA list | एजेंट MEA की सूची में नहीं | एजंट MEA यादीत नाही |
| `rule.R2_RA_NOT_LISTED.hit` | This agent was not found on MEA's active recruiting agent list dated {date}. Ask for the agent's RC number and check it on eMigrate before you pay. | यह एजेंट MEA की सक्रिय भर्ती एजेंट सूची में नहीं मिला, जो {date} की है। पैसे देने से पहले एजेंट का RC नंबर माँगें और eMigrate पर जाँचें। | हा एजंट MEA च्या सक्रिय भरती एजंट यादीत सापडला नाही, जी {date} रोजीची आहे. पैसे देण्यापूर्वी एजंटचा RC नंबर मागा आणि eMigrate वर तपासा. |
| `rule.R2_RA_NOT_LISTED.clear` | This agent is on MEA's active recruiting agent list. | यह एजेंट MEA की सक्रिय भर्ती एजेंट सूची में है। | हा एजंट MEA च्या सक्रिय भरती एजंट यादीत आहे. |
| `rule.R2_RA_NOT_LISTED.unknown` | The agent was not checked. Give the agent's name or RC number, then check the MEA list. | एजेंट की जाँच नहीं हुई। एजेंट का नाम या RC नंबर दें, फिर MEA सूची देखें। | एजंटची तपासणी झाली नाही. एजंटचे नाव किंवा RC नंबर द्या, मग MEA यादी तपासा. |
| `rule.R3_NO_RC_NUMBER.title` | Agent RC number missing | एजेंट का RC नंबर नहीं है | एजंटचा RC नंबर नाही |
| `rule.R3_NO_RC_NUMBER.hit` | The offer does not show a recruiting agent RC number. Ask the agent for the RC number in writing before you pay. | ऑफ़र में भर्ती एजेंट का RC नंबर नहीं लिखा है। पैसे देने से पहले एजेंट से लिखित में RC नंबर माँगें। | ऑफरमध्ये भरती एजंटचा RC नंबर लिहिलेला नाही. पैसे देण्यापूर्वी एजंटकडून लेखी RC नंबर मागा. |
| `rule.R3_NO_RC_NUMBER.clear` | The offer shows an agent RC number. Check it on eMigrate before you pay. | ऑफ़र में एजेंट का RC नंबर लिखा है। पैसे देने से पहले eMigrate पर जाँचें। | ऑफरमध्ये एजंटचा RC नंबर लिहिलेला आहे. पैसे देण्यापूर्वी eMigrate वर तपासा. |
| `rule.R3_NO_RC_NUMBER.unknown` | The offer does not say if there is an agent. Ask who will recruit you and for their RC number. | ऑफ़र में नहीं लिखा कि कोई एजेंट है या नहीं। पूछें कि आपको कौन भर्ती कर रहा है और उनका RC नंबर क्या है। | ऑफरमध्ये एजंट आहे का ते लिहिलेले नाही. तुम्हाला कोण भरती करत आहे आणि त्यांचा RC नंबर काय आहे ते विचारा. |
| `rule.R4_FEE_OVER_CAP.title` | Fee is above MEA limit | फ़ीस MEA सीमा से ज़्यादा | फी MEA च्या मर्यादेपेक्षा जास्त आहे |
| `rule.R4_FEE_OVER_CAP.hit` | The fee asked is above the limit in MEA advice for this kind of job. Do not pay until the agent explains the fee in writing. | माँगी गई फ़ीस इस तरह की नौकरी के लिए MEA की सलाह में दी गई सीमा से ज़्यादा है। जब तक एजेंट फ़ीस लिखित में न समझाए, कुछ न दें। | मागितलेले शुल्क या प्रकारच्या नोकरीसाठी MEA च्या सल्ल्यातील मर्यादेपेक्षा जास्त आहे. एजंट शुल्क लेखी स्पष्ट करेपर्यंत काहीही देऊ नका. |
| `rule.R4_FEE_OVER_CAP.clear` | The fee asked is within the limit in MEA advice. | माँगी गई फ़ीस MEA की सलाह की सीमा के भीतर है। | मागितलेले शुल्क MEA च्या सल्ल्यातील मर्यादेत आहे. |
| `rule.R4_FEE_OVER_CAP.unknown` | The offer does not say how much you must pay. Ask for the full fee in writing. | ऑफ़र में नहीं लिखा कि कितना पैसा देना है। पूरी फ़ीस लिखित में माँगें। | किती पैसे द्यायचे ते ऑफरमध्ये लिहिलेले नाही. पूर्ण शुल्क लेखी मागा. |
| `rule.R5_NO_TRIPARTITE_CONTRACT.title` | No three-party contract mentioned | तीन पक्षों वाला अनुबंध नहीं | तीन पक्षांच्या कराराचा उल्लेख नाही |
| `rule.R5_NO_TRIPARTITE_CONTRACT.hit` | The offer does not show a contract signed by the employer, the agent and you. Ask for a copy of the three-party contract before you pay. | ऑफ़र में ऐसा अनुबंध नहीं दिखता जिस पर नियोक्ता, एजेंट और आप तीनों के हस्ताक्षर हों। पैसे देने से पहले तीन पक्षों वाले अनुबंध की कॉपी माँगें। | ऑफरमध्ये नियोक्ता, एजंट आणि तुम्ही तिघांनी सही केलेला करार दिसत नाही. पैसे देण्यापूर्वी तीन पक्षांच्या कराराची प्रत मागा. |
| `rule.R5_NO_TRIPARTITE_CONTRACT.clear` | The offer says the employer, the agent and you all sign one contract. | ऑफ़र में लिखा है कि नियोक्ता, एजेंट और आप तीनों एक ही अनुबंध पर हस्ताक्षर करेंगे। | ऑफरमध्ये लिहिले आहे की नियोक्ता, एजंट आणि तुम्ही तिघे एकाच करारावर सही कराल. |
| `rule.R5_NO_TRIPARTITE_CONTRACT.unknown` | The offer does not say who the contract is with. Ask who will sign it. | ऑफ़र में नहीं लिखा कि अनुबंध किसके साथ है। पूछें कि इस पर कौन हस्ताक्षर करेगा। | करार कोणाबरोबर आहे ते ऑफरमध्ये लिहिलेले नाही. तो कोण सही करेल ते विचारा. |
| `rule.R6_HIGH_RISK_CORRIDOR.title` | Route flagged as high risk | यह रास्ता ज़्यादा जोखिम वाला | हा मार्ग जास्त धोक्याचा मानला जातो |
| `rule.R6_HIGH_RISK_CORRIDOR.hit` | MEA advice flags this destination or transit country as high risk for workers. Do not pay or travel until you check the current advice. | MEA की सलाह के मुताबिक़ यह गंतव्य देश या बीच का देश कामगारों के लिए ज़्यादा जोखिम वाला है। मौजूदा सलाह जाँचने तक न पैसे दें, न जाएँ। | MEA च्या सल्ल्यानुसार हा गंतव्य देश किंवा मधला देश कामगारांसाठी जास्त धोक्याचा आहे. सध्याचा सल्ला तपासेपर्यंत पैसे देऊ नका आणि प्रवास करू नका. |
| `rule.R6_HIGH_RISK_CORRIDOR.clear` | The destination and transit countries are not on MEA's high-risk list in this check. | इस जाँच में गंतव्य और बीच के देश MEA की ज़्यादा जोखिम वाली सूची में नहीं हैं। | या तपासणीत गंतव्य आणि मधले देश MEA च्या जास्त धोक्याच्या यादीत नाहीत. |
| `rule.R6_HIGH_RISK_CORRIDOR.unknown` | The offer does not name the destination country. Ask which country you will work in. | ऑफ़र में गंतव्य देश का नाम नहीं है। पूछें कि आप किस देश में काम करेंगे। | ऑफरमध्ये गंतव्य देशाचे नाव नाही. तुम्ही कोणत्या देशात काम कराल ते विचारा. |
| `rule.R7_INFORMAL_CHANNEL_ONLY.title` | Offer only through chat apps | ऑफ़र सिर्फ़ चैट ऐप से | ऑफर फक्त चॅट अॅपवरून |
| `rule.R7_INFORMAL_CHANNEL_ONLY.hit` | The offer lists only chat apps or a phone number. Ask for an office address, an email and a website you can check. | ऑफ़र में सिर्फ़ चैट ऐप या फ़ोन नंबर लिखा है। दफ़्तर का पता, ईमेल और ऐसी वेबसाइट माँगें जिसे आप जाँच सकें। | ऑफरमध्ये फक्त चॅट अॅप किंवा फोन नंबर दिला आहे. कार्यालयाचा पत्ता, ईमेल आणि तपासता येईल अशी वेबसाइट मागा. |
| `rule.R7_INFORMAL_CHANNEL_ONLY.clear` | The offer lists an office address, an email or a website, not just chat. | ऑफ़र में दफ़्तर का पता, ईमेल या वेबसाइट भी लिखी है, सिर्फ़ चैट नहीं। | ऑफरमध्ये कार्यालयाचा पत्ता, ईमेल किंवा वेबसाइट लिहिली आहे, फक्त चॅट नाही. |
| `rule.R7_INFORMAL_CHANNEL_ONLY.unknown` | The offer does not say how to reach the agent. Ask for an office address and an email. | ऑफ़र में नहीं लिखा कि एजेंट से कैसे संपर्क करें। दफ़्तर का पता और ईमेल माँगें। | एजंटशी संपर्क कसा करायचा ते ऑफरमध्ये लिहिलेले नाही. कार्यालयाचा पत्ता आणि ईमेल मागा. |
| `rule.R8_NO_RECEIPT.title` | No receipt promised | रसीद का वादा नहीं है | पावतीचे आश्वासन नाही |
| `rule.R8_NO_RECEIPT.hit` | A fee is asked, but no receipt is promised. Ask for a written receipt for every payment before you pay. | फ़ीस माँगी गई है, पर रसीद देने का वादा नहीं है। पैसे देने से पहले हर भुगतान के बदले लिखित रसीद माँगें। | शुल्क मागितले आहे, पण पावती देण्याचे आश्वासन नाही. पैसे देण्यापूर्वी प्रत्येक रकमेच्या बदल्यात लेखी पावती मागा. |
| `rule.R8_NO_RECEIPT.clear` | The offer promises a receipt for any fee paid. | ऑफ़र में दी गई फ़ीस की रसीद देने का वादा है। | ऑफरमध्ये दिलेल्या शुल्काची पावती देण्याचे आश्वासन आहे. |
| `rule.R8_NO_RECEIPT.unknown` | The offer does not say if a receipt will be given. Ask before you pay. | ऑफ़र में नहीं लिखा कि रसीद मिलेगी या नहीं। पैसे देने से पहले पूछें। | पावती मिळेल की नाही ते ऑफरमध्ये लिहिलेले नाही. पैसे देण्यापूर्वी विचारा. |
| `rule.R9_PBBY_MISSING.title` | PBBY insurance not mentioned | PBBY बीमा का ज़िक्र नहीं | PBBY विम्याचा उल्लेख नाही |
| `rule.R9_PBBY_MISSING.hit` | PBBY insurance (Pravasi Bharatiya Bima Yojana) is not mentioned. Ask whether it applies to your job. | PBBY बीमा (प्रवासी भारतीय बीमा योजना) का ज़िक्र नहीं है। पूछें कि क्या यह आपकी नौकरी पर लागू होता है। | PBBY विमा (प्रवासी भारतीय विमा योजना) चा उल्लेख नाही. तो तुमच्या नोकरीला लागू होतो का ते विचारा. |
| `rule.R9_PBBY_MISSING.clear` | The offer mentions PBBY insurance. | ऑफ़र में PBBY बीमा का ज़िक्र है। | ऑफरमध्ये PBBY विम्याचा उल्लेख आहे. |
| `rule.R9_PBBY_MISSING.unknown` | The offer does not say whether PBBY insurance applies. | ऑफ़र में नहीं लिखा कि PBBY बीमा लागू होता है या नहीं। | PBBY विमा लागू होतो की नाही ते ऑफरमध्ये लिहिलेले नाही. |
| `rule.H1_SALARY_ANOMALY.title` | Salary looks unusually high | वेतन असामान्य रूप से ऊँचा | पगार असामान्यपणे जास्त वाटतो |
| `rule.H1_SALARY_ANOMALY.hit` | This is a warning sign, not a legal rule. The salary looks much higher than usual for this job, so ask the employer to explain it. | यह एक चेतावनी का संकेत है, कानूनी नियम नहीं। इस काम के लिए वेतन आम तौर से कहीं ज़्यादा लगता है, इसलिए नियोक्ता से इसकी वजह पूछें। | हा इशाऱ्याचा संकेत आहे, कायदेशीर नियम नाही. या कामासाठी पगार नेहमीपेक्षा खूप जास्त वाटतो, म्हणून नियोक्त्याला त्याचे कारण विचारा. |
| `rule.H1_SALARY_ANOMALY.clear` | The salary is in the usual range for this job. | इस काम के लिए वेतन आम तौर की सीमा में है। | या कामासाठी पगार नेहमीच्या मर्यादेत आहे. |
| `rule.H1_SALARY_ANOMALY.unknown` | The offer does not give a salary. Ask for the monthly salary in writing. | ऑफ़र में वेतन नहीं लिखा है। मासिक वेतन लिखित में माँगें। | ऑफरमध्ये पगार लिहिलेला नाही. मासिक पगार लेखी मागा. |
| `rule.H2_PASSPORT_HANDOVER.title` | Agent asks to hold your passport | एजेंट आपका पासपोर्ट रखना चाहता है | एजंटला तुमचा पासपोर्ट ठेवायचा आहे |
| `rule.H2_PASSPORT_HANDOVER.hit` | This is a warning sign, not a legal rule. Do not give your passport to an agent until you have a signed contract and have checked the agent. | यह एक चेतावनी का संकेत है, कानूनी नियम नहीं। जब तक हस्ताक्षर वाला अनुबंध न हो और एजेंट की जाँच न हो, अपना पासपोर्ट एजेंट को न दें। | हा इशाऱ्याचा संकेत आहे, कायदेशीर नियम नाही. सही केलेला करार मिळेपर्यंत आणि एजंटची तपासणी होईपर्यंत तुमचा पासपोर्ट एजंटकडे देऊ नका. |
| `rule.H2_PASSPORT_HANDOVER.clear` | The offer does not ask for your passport. | ऑफ़र में आपका पासपोर्ट नहीं माँगा गया है। | ऑफरमध्ये तुमचा पासपोर्ट मागितलेला नाही. |
| `rule.H2_PASSPORT_HANDOVER.unknown` | The offer does not say whether your passport will be kept. | ऑफ़र में नहीं लिखा कि आपका पासपोर्ट रखा जाएगा या नहीं। | तुमचा पासपोर्ट ठेवला जाईल की नाही ते ऑफरमध्ये लिहिलेले नाही. |
| `rule.H3_PRESSURE.title` | Pressure to decide quickly | जल्दी फ़ैसला करने का दबाव | लगेच निर्णय घेण्याचा दबाव |
| `rule.H3_PRESSURE.hit` | Warning sign, not a legal rule: the offer pushes you to decide fast. Take time to check before you pay. | चेतावनी का संकेत, कानूनी नियम नहीं: ऑफ़र आपको जल्दी फ़ैसला करने को कहता है। पैसे देने से पहले समय लेकर जाँच करें। | इशाऱ्याचा संकेत, कायदेशीर नियम नाही: ऑफर तुम्हाला लगेच निर्णय घ्यायला लावतो. पैसे देण्यापूर्वी वेळ घेऊन तपासा. |
| `rule.H3_PRESSURE.clear` | The offer does not push you to decide quickly. | ऑफ़र आपको जल्दी फ़ैसला करने पर मजबूर नहीं करता। | ऑफर तुम्हाला लगेच निर्णय घ्यायला भाग पाडत नाही. |
| `rule.H3_PRESSURE.unknown` | The offer does not say how long you have to decide. | ऑफ़र में नहीं लिखा कि फ़ैसला करने के लिए कितना समय है। | निर्णय घ्यायला किती वेळ आहे ते ऑफरमध्ये लिहिलेले नाही. |
| `next.STOP` | Do not pay or travel yet. Check each point with the Protector of Emigrants first. | अभी पैसे न दें और न जाएँ। हर बात की जाँच पहले प्रवासी संरक्षक से करवाएँ। | आत्ता पैसे देऊ नका आणि प्रवास करू नका. प्रत्येक मुद्द्याची तपासणी आधी प्रवासी संरक्षकाकडून करून घ्या. |
| `next.VERIFY_FIRST` | Get written answers to each point. Then check the agent on eMigrate before you pay. | हर बात का लिखित जवाब लें। फिर पैसे देने से पहले eMigrate पर एजेंट की जाँच करें। | प्रत्येक मुद्द्याची लेखी उत्तरे घ्या. मग पैसे देण्यापूर्वी eMigrate वर एजंटची तपासणी करा. |
| `next.NO_RED_FLAGS_FOUND` | Confirm with the Protector of Emigrants before paying anything. | कोई भी पैसा देने से पहले प्रवासी संरक्षक से पुष्टि कर लें। | कोणतेही पैसे देण्यापूर्वी प्रवासी संरक्षकाकडून खात्री करून घ्या. |
| `safety.title` | Check-in plan | चेक-इन योजना | चेक-इन योजना |
| `safety.intro` | Choose up to two people at home. If you miss a check-in, they get a simulated alert with the report packet. | घर पर ज़्यादा से ज़्यादा दो लोग चुनें। चेक-इन छूटने पर उन्हें रिपोर्ट पैकेट के साथ एक सिमुलेटेड (डेमो) अलर्ट मिलेगा। | घरी जास्तीत जास्त दोन व्यक्ती निवडा. चेक-इन चुकले तर त्यांना अहवाल पॅकेटसह सिम्युलेटेड (डेमो) अलर्ट मिळेल. |
| `safety.traveller_alias` | Your alias (not your real name) | आपका उपनाम (असली नाम नहीं) | तुमचे टोपणनाव (खरे नाव नाही) |
| `safety.contact_alias` | Contact alias | संपर्क का उपनाम | संपर्काचे टोपणनाव |
| `safety.contact_channel` | How to reach them | उन तक कैसे पहुँचें | त्यांच्याशी संपर्क कसा साधायचा |
| `safety.add_contact` | Add contact (up to 2) | संपर्क जोड़ें (ज़्यादा से ज़्यादा 2) | संपर्क जोडा (जास्तीत जास्त 2) |
| `safety.itinerary` | Travel plan | यात्रा का विवरण | प्रवासाचा तपशील |
| `safety.itinerary_placeholder` | Dates, city, the address where you will stay, and the agent's office. | तारीखें, शहर, जहाँ रहेंगे उसका पता, और एजेंट का दफ़्तर। | तारखा, शहर, राहण्याचा पत्ता आणि एजंटचे कार्यालय. |
| `safety.interval_hours` | Check-in every (hours) | हर कितने घंटे पर चेक-इन (घंटे) | किती तासांनी चेक-इन (तास) |
| `safety.save` | Save plan | योजना सेव करें | योजना जतन करा |
| `safety.checkin` | I am OK, check in now | मैं ठीक हूँ, अभी चेक-इन करें | मी ठीक आहे, आत्ता चेक-इन करा |
| `safety.checkin_note` | Note (optional) | नोट (ज़रूरी नहीं) | नोंद (ऐच्छिक) |
| `safety.status.ok` | On schedule | समय पर | वेळेवर |
| `safety.status.due` | Check-in due | चेक-इन बाकी है | चेक-इन बाकी आहे |
| `safety.status.missed` | Check-in missed | चेक-इन छूट गया | चेक-इन चुकले |
| `safety.next_due` | Next check-in by {time}. | अगला चेक-इन {time} तक। | पुढील चेक-इन {time} पर्यंत. |
| `safety.last_checkin` | Last check-in at {time}. | पिछला चेक-इन {time} पर। | शेवटचा चेक-इन {time} वाजता. |
| `safety.demo_advance` | Demo: move the clock forward 12 hours | डेमो: घड़ी 12 घंटे आगे करें | डेमो: घड्याळ 12 तास पुढे न्या |
| `safety.simulated_note` | Simulated. No real message is sent to anyone. | सिमुलेटेड। किसी को असली संदेश नहीं भेजा जाता। | सिम्युलेटेड. कोणालाही खरा संदेश पाठवला जात नाही. |
| `family.title` | Family alerts | परिवार के अलर्ट | कुटुंबासाठी अलर्ट |
| `family.alert_title` | Missed check-in alert | चेक-इन छूटने का अलर्ट | चेक-इन चुकल्याची सूचना |
| `family.alert_body` | Simulated alert: {alias} missed a check-in. Open the report packet to see the offer details and what to do next. | सिमुलेटेड अलर्ट: {alias} का चेक-इन छूट गया है। ऑफ़र की पूरी जानकारी और आगे क्या करना है, यह रिपोर्ट पैकेट में देखें। | सिम्युलेटेड सूचना: {alias} चा चेक-इन चुकला आहे. ऑफरची संपूर्ण माहिती आणि पुढे काय करायचे ते अहवाल पॅकेटमध्ये पहा. |
| `family.open_packet` | Open report packet | रिपोर्ट पैकेट खोलें | अहवाल पॅकेट उघडा |
| `family.no_alerts` | No alerts yet. | अभी कोई अलर्ट नहीं। | अजून कोणतीही सूचना नाही. |
| `family.simulated_badge` | Simulated (demo) | सिमुलेटेड (डेमो) | सिम्युलेटेड (डेमो) |
| `map.title` | Report map | रिपोर्ट का नक्शा | अहवाल नकाशा |
| `map.login_required` | Sign in to see the map. | नक्शा देखने के लिए साइन इन करें। | नकाशा पाहण्यासाठी साइन इन करा. |
| `map.email` | Email | ईमेल | ईमेल |
| `map.password` | Password | पासवर्ड | पासवर्ड |
| `map.sign_in` | Sign in | साइन इन करें | साइन इन करा |
| `map.sign_out` | Sign out | साइन आउट करें | साइन आउट करा |
| `map.synthetic_badge` | Synthetic data only | केवल काल्पनिक डेटा | फक्त काल्पनिक डेटा |
| `map.repeated_agents` | Agents seen in several reports | कई रिपोर्टों में दिखे एजेंट | अनेक अहवालांत दिसलेले एजंट |
| `map.repeated_templates` | Offer wording seen more than once | एक जैसे ऑफ़र के शब्द एक से ज़्यादा बार | सारखी ऑफर भाषा एकापेक्षा जास्त वेळा |
| `map.districts` | Districts | ज़िले | जिल्हे |
| `map.reports` | Reports | रिपोर्ट | अहवाल |
| `limits.title` | What Saavdhan can and cannot do | Saavdhan क्या कर सकता है और क्या नहीं | Saavdhan काय करू शकते आणि काय करू शकत नाही |
| `limits.what_it_does` | It checks only what the offer says, against public MEA guidance. All demo data is synthetic. | यह सिर्फ़ वही जाँचता है जो ऑफ़र में लिखा है, MEA की सार्वजनिक सलाह से मिलाकर। सारा डेमो डेटा काल्पनिक है। | ते फक्त ऑफरमध्ये जे लिहिले आहे ते, MEA च्या सार्वजनिक मार्गदर्शनाशी जुळवून तपासते. सर्व डेमो डेटा काल्पनिक आहे. |
| `limits.what_it_does_not` | It can be wrong. It is not legal advice. | यह गलत भी हो सकता है। यह कानूनी सलाह नहीं है। | ते चुकीचे असू शकते. ते कायदेशीर सल्ला नाही. |
| `limits.not_legal_advice` | For legal questions, ask the Protector of Emigrants or a lawyer. | कानूनी सवालों के लिए प्रवासी संरक्षक या किसी वकील से पूछें। | कायदेशीर प्रश्नांसाठी प्रवासी संरक्षक किंवा वकिलांना विचारा. |
| `limits.no_auto_report` | Saavdhan never reports anyone automatically. You decide who to tell. | Saavdhan किसी की भी रिपोर्ट अपने-आप नहीं करता। किसे बताना है, यह आप तय करते हैं। | Saavdhan कोणाचीही आपोआप तक्रार करत नाही. कोणाला सांगायचे ते तुम्ही ठरवता. |
| `limits.sources_title` | Sources | स्रोत | स्रोत |
| `limits.helplines_title` | Helplines and official sites | हेल्पलाइन और आधिकारिक वेबसाइट | हेल्पलाइन आणि अधिकृत वेबसाइट |
| `limits.verify_contacts` | Verify helpline contacts on official sites before use. | इस्तेमाल से पहले हेल्पलाइन नंबर आधिकारिक वेबसाइटों पर जाँच लें। | वापरण्यापूर्वी हेल्पलाइन संपर्क अधिकृत वेबसाइटवर तपासा. |
| `error.generic` | Something went wrong. Please try again. | कुछ गड़बड़ हुई। फिर से कोशिश करें। | काहीतरी चुकले. पुन्हा प्रयत्न करा. |
| `error.network` | No internet connection. Check your network and try again. | इंटरनेट नहीं है। नेटवर्क जाँचकर फिर से कोशिश करें। | इंटरनेट नाही. नेटवर्क तपासून पुन्हा प्रयत्न करा. |
| `common.loading` | Loading... | लोड हो रहा है... | लोड होत आहे... |
| `common.back` | Back | वापस | मागे |
| `common.close` | Close | बंद करें | बंद करा |
