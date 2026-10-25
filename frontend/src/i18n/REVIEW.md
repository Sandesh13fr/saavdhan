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

- **R4 fee cap**: `rule.R4_FEE_OVER_CAP.hit` and `.clear` take `{cap}` in all three languages. The copy still says "as reported from MEA advice" and prints "Rs 30,000 + 18% GST" in text. `backend/rules.py` says that figure must be verified before release, so `{cap}` must be filled from one verified constant.
- **R6 corridor**: the copy does not say MEA publishes a "high-risk list". It describes a pattern seen in reported fake-job cases and says MEA has warned about such offers. Confirm that MEA warning exists before release.
- **Agent list not checked**: `verdict.ra_not_checked` is an app key, not in `docs/CONTRACTS.md`. It is listed in `EXTRA_KEYS` in `check_i18n.py`.
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
| `verdict.ra_not_checked` | Agent list not checked yet. | एजेंट सूची की जाँच अभी नहीं हुई है। | एजंट यादीची तपासणी अजून झालेली नाही. |
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
| `rule.R2_RA_NOT_LISTED.clear` | This agent appears on MEA's active recruiting agent list dated {date}. Still confirm on eMigrate. | यह एजेंट MEA की सक्रिय भर्ती एजेंट सूची में दिखता है, जो {date} की है। फिर भी eMigrate पर पुष्टि करें। | हा एजंट MEA च्या सक्रिय भरती एजंट यादीत दिसतो, जी {date} रोजीची आहे. तरीही eMigrate वर खात्री करा. |
| `rule.R2_RA_NOT_LISTED.unknown` | Saavdhan could not check this agent against MEA's list. | Saavdhan इस एजेंट की जाँच MEA की सूची से नहीं कर सका। | Saavdhan या एजंटची MEA यादीशी तपासणी करू शकला नाही. |
| `rule.R3_NO_RC_NUMBER.title` | Agent RC number missing | एजेंट का RC नंबर नहीं है | एजंटचा RC नंबर नाही |
| `rule.R3_NO_RC_NUMBER.hit` | The offer does not show a recruiting agent RC number. Ask the agent for the RC number in writing before you pay. | ऑफ़र में भर्ती एजेंट का RC नंबर नहीं लिखा है। पैसे देने से पहले एजेंट से लिखित में RC नंबर माँगें। | ऑफरमध्ये भरती एजंटचा RC नंबर लिहिलेला नाही. पैसे देण्यापूर्वी एजंटकडून लेखी RC नंबर मागा. |
| `rule.R3_NO_RC_NUMBER.clear` | The offer shows an agent RC number. Check it on eMigrate before you pay. | ऑफ़र में एजेंट का RC नंबर लिखा है। पैसे देने से पहले eMigrate पर जाँचें। | ऑफरमध्ये एजंटचा RC नंबर लिहिलेला आहे. पैसे देण्यापूर्वी eMigrate वर तपासा. |
| `rule.R3_NO_RC_NUMBER.unknown` | The offer does not say if there is an agent. Ask who will recruit you and for their RC number. | ऑफ़र में नहीं लिखा कि कोई एजेंट है या नहीं। पूछें कि आपको कौन भर्ती कर रहा है और उनका RC नंबर क्या है। | ऑफरमध्ये एजंट आहे का ते लिहिलेले नाही. तुम्हाला कोण भरती करत आहे आणि त्यांचा RC नंबर काय आहे ते विचारा. |
| `rule.R4_FEE_OVER_CAP.title` | Fee is above MEA limit | फ़ीस MEA सीमा से ज़्यादा | फी MEA च्या मर्यादेपेक्षा जास्त आहे |
| `rule.R4_FEE_OVER_CAP.hit` | The fee is above Rs {cap} (Rs 30,000 + 18% GST, as reported from MEA advice). Ask the agent to explain the fee in writing before you pay. | फ़ीस रुपये {cap} से ज़्यादा है (MEA की सलाह के अनुसार रुपये 30,000 + 18% GST)। पैसे देने से पहले एजेंट से फ़ीस लिखित में समझाने को कहें। | शुल्क रुपये {cap} पेक्षा जास्त आहे (MEA च्या सल्ल्यानुसार रुपये 30,000 + 18% GST). पैसे देण्यापूर्वी एजंटला शुल्क लेखी स्पष्ट करायला सांगा. |
| `rule.R4_FEE_OVER_CAP.clear` | The fee is within Rs {cap} (Rs 30,000 + 18% GST, as reported from MEA advice). | फ़ीस रुपये {cap} की सीमा के भीतर है (MEA की सलाह के अनुसार रुपये 30,000 + 18% GST)। | शुल्क रुपये {cap} च्या मर्यादेत आहे (MEA च्या सल्ल्यानुसार रुपये 30,000 + 18% GST). |
| `rule.R4_FEE_OVER_CAP.unknown` | The offer does not say how much you must pay. Ask for the full fee in writing. | ऑफ़र में नहीं लिखा कि कितना पैसा देना है। पूरी फ़ीस लिखित में माँगें। | किती पैसे द्यायचे ते ऑफरमध्ये लिहिलेले नाही. पूर्ण शुल्क लेखी मागा. |
| `rule.R5_NO_TRIPARTITE_CONTRACT.title` | No three-party contract mentioned | तीन पक्षों वाला अनुबंध नहीं | तीन पक्षांच्या कराराचा उल्लेख नाही |
| `rule.R5_NO_TRIPARTITE_CONTRACT.hit` | The offer does not show a contract signed by the employer, the agent and you. Ask for a copy of the three-party contract before you pay. | ऑफ़र में ऐसा अनुबंध नहीं दिखता जिस पर नियोक्ता, एजेंट और आप तीनों के हस्ताक्षर हों। पैसे देने से पहले तीन पक्षों वाले अनुबंध की कॉपी माँगें। | ऑफरमध्ये नियोक्ता, एजंट आणि तुम्ही तिघांनी सही केलेला करार दिसत नाही. पैसे देण्यापूर्वी तीन पक्षांच्या कराराची प्रत मागा. |
| `rule.R5_NO_TRIPARTITE_CONTRACT.clear` | The offer says the employer, the agent and you all sign one contract. | ऑफ़र में लिखा है कि नियोक्ता, एजेंट और आप तीनों एक ही अनुबंध पर हस्ताक्षर करेंगे। | ऑफरमध्ये लिहिले आहे की नियोक्ता, एजंट आणि तुम्ही तिघे एकाच करारावर सही कराल. |
| `rule.R5_NO_TRIPARTITE_CONTRACT.unknown` | The offer does not say who the contract is with. Ask who will sign it. | ऑफ़र में नहीं लिखा कि अनुबंध किसके साथ है। पूछें कि इस पर कौन हस्ताक्षर करेगा। | करार कोणाबरोबर आहे ते ऑफरमध्ये लिहिलेले नाही. तो कोण सही करेल ते विचारा. |
| `rule.R6_HIGH_RISK_CORRIDOR.title` | Route seen in fake-job cases | बनावट नौकरी के मामलों वाला रास्ता | बनावट नोकरीच्या प्रकरणांशी जुळणारा मार्ग |
| `rule.R6_HIGH_RISK_CORRIDOR.hit` | This job and route match a pattern seen in reported fake-job cases (Thailand, Myanmar, Cambodia, Laos; data-entry/IT/support roles). MEA has warned about such offers. | यह नौकरी और रास्ता उन रिपोर्ट की गई बनावट नौकरी के मामलों जैसा है जो थाईलैंड, म्यांमार, कंबोडिया और लाओस से जुड़े हैं (डेटा एंट्री, IT या सपोर्ट के काम)। MEA ने ऐसे ऑफ़र के बारे में चेतावनी दी है। | ही नोकरी आणि मार्ग नोंदवलेल्या बनावट नोकरी प्रकरणांशी जुळतो, जी थायलंड, म्यानमार, कंबोडिया आणि लाओसशी संबंधित आहेत (डेटा एंट्री, IT किंवा सपोर्ट भूमिका). MEA ने अशा ऑफरबद्दल इशारा दिला आहे. |
| `rule.R6_HIGH_RISK_CORRIDOR.clear` | The route and job do not match the corridor pattern Saavdhan checks. | रास्ता और नौकरी उस पैटर्न से नहीं मिलते जिसकी Saavdhan जाँच करता है। | मार्ग आणि नोकरी Saavdhan तपासत असलेल्या पॅटर्नशी जुळत नाहीत. |
| `rule.R6_HIGH_RISK_CORRIDOR.unknown` | The offer does not give the job role or the route. Add the role and every country you will pass through. | ऑफ़र में काम का प्रकार या रास्ता नहीं लिखा है। काम का प्रकार और वे सभी देश जोड़ें जहाँ से आप गुजरेंगे। | ऑफरमध्ये नोकरीचा प्रकार किंवा मार्ग लिहिलेला नाही. नोकरीचा प्रकार आणि तुम्ही ज्या सर्व देशांमधून जाल ते देश जोडा. |
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


## UI rebuild keys (mock screens), all Hindi and Marathi NEED NATIVE REVIEW

Added for the rebuilt screens. They use app-only prefixes (`ui.`, `nav2.`, `home.`, `submit.`, `review.`, `result.`, `evidence.`, `plan.`, `checkin.`, `family2.`, `help.`, `login.`, `pmap.`, `pdetail.`, `fact.`, `value.`, `steps.`, `illo.`, `demo.`). None uses a prefix that `backend/templates` mirrors, so no backend change is needed. Every key is listed in `EXTRA_KEYS` in `check_i18n.py`.

Notes for reviewers:
- `home.hindi_line` is the board's Hindi line and stays Hindi in every language.
- `result.word.*` are the giant verdict words. Hindi uses रुकें / पहले जाँचें and Marathi uses थांबा / आधी तपासा. Check that they read naturally as a one-word headline.
- `help.cyber.what` avoids "fraud" (forbidden word): "Cyber crime and lost money".
- Brand and product names (WhatsApp, UPI, MEA, MADAD, eMigrate, PBBY, RC) stay in Latin script.

| Key | English source | Hindi (needs native review) | Marathi (needs native review) |
|---|---|---|---|
| `ui.demo` | Demo | डेमो | डेमो |
| `ui.demo_data` | Demo data | डेमो डेटा | डेमो डेटा |
| `ui.footer` | Hack for Social Cause, independent concept. Demo data is synthetic and labelled. | Hack for Social Cause, स्वतंत्र कॉन्सेप्ट। डेमो डेटा काल्पनिक है और उस पर लेबल लगा है। | Hack for Social Cause, स्वतंत्र संकल्पना. डेमो डेटा काल्पनिक आहे आणि त्यावर लेबल आहे. |
| `ui.home_label` | Saavdhan home | Saavdhan होम | Saavdhan मुख्यपृष्ठ |
| `ui.institution_link` | Institution access | संस्था लॉगिन | संस्था लॉगिन |
| `ui.language` | Language | भाषा | भाषा |
| `ui.main_nav` | Main | मुख्य | मुख्य |
| `ui.main_nav_mobile` | Main menu | मुख्य मेनू | मुख्य मेनू |
| `ui.new_tab` | opens in a new tab | नए टैब में खुलेगा | नवीन टॅबमध्ये उघडेल |
| `ui.yes` | Yes | हाँ | हो |
| `ui.no` | No | नहीं | नाही |
| `ui.skip` | Skip to content | सीधे सामग्री पर जाएँ | थेट मजकुराकडे जा |
| `nav2.check` | Check | जाँच | तपासणी |
| `nav2.checkins` | Check-ins | चेक-इन | चेक-इन |
| `nav2.help` | Help | मदद | मदत |
| `demo.bangkok_hint` | Chat with several warning signs | कई चेतावनी संकेतों वाली चैट | अनेक धोक्याच्या खुणा असलेली चॅट |
| `demo.dubai_hint` | Offer with a few gaps | कुछ अधूरी बातों वाला ऑफ़र | काही अपूर्ण गोष्टी असलेली ऑफर |
| `home.title` | Before you pay. Before you fly. | पैसे देने से पहले। उड़ान से पहले। | पैसे देण्याआधी. विमान पकडण्याआधी. |
| `home.sub` | Check overseas job offers. Keep family close. | विदेश की नौकरी के ऑफ़र जाँचें। परिवार को साथ रखें। | परदेशातील नोकरीच्या ऑफर तपासा. कुटुंबाला सोबत ठेवा. |
| `home.hindi_line` | विदेश की नौकरी? पहले जाँच। | विदेश की नौकरी? पहले जाँच। | विदेश की नौकरी? पहले जाँच। |
| `home.cta` | Check my offer | मेरा ऑफ़र जाँचें | माझी ऑफर तपासा |
| `home.steps_label` | How it works | यह कैसे काम करता है | हे कसे काम करते |
| `home.step_add` | Add offer | ऑफ़र जोड़ें | ऑफर जोडा |
| `home.step_evidence` | See evidence | सबूत देखें | पुरावा पहा |
| `home.step_checkins` | Plan check-ins | चेक-इन तय करें | चेक-इन ठरवा |
| `illo.job_offer` | Job Offer | नौकरी ऑफ़र | नोकरी ऑफर |
| `illo.visa_type` | VISA TYPE | वीज़ा प्रकार | व्हिसा प्रकार |
| `illo.tourist_visa` | Tourist visa | टूरिस्ट वीज़ा | टुरिस्ट व्हिसा |
| `steps.label` | Progress | प्रगति | प्रगती |
| `steps.add` | Add | जोड़ें | जोडा |
| `steps.review` | Review | देखें | तपासा |
| `steps.result` | Result | नतीजा | निकाल |
| `steps.done` | done | पूरा | पूर्ण |
| `submit.title` | Let's check your offer. | चलिए, आपका ऑफ़र जाँचें। | चला, तुमची ऑफर तपासू. |
| `submit.sub` | Paste a chat or upload a document. | चैट चिपकाएँ या दस्तावेज़ अपलोड करें। | चॅट पेस्ट करा किंवा कागदपत्र अपलोड करा. |
| `submit.tabs_label` | How to add the offer | ऑफ़र कैसे जोड़ें | ऑफर कशी जोडायची |
| `submit.tab_paste` | Paste chat | चैट चिपकाएँ | चॅट पेस्ट करा |
| `submit.tab_upload` | Upload file | फ़ाइल अपलोड करें | फाइल अपलोड करा |
| `submit.paste_placeholder` | Paste the offer here... | ऑफ़र यहाँ चिपकाएँ... | ऑफर इथे पेस्ट करा... |
| `submit.paste_hint` | You can paste text and attach files. Both are checked together. | आप टेक्स्ट चिपका सकते हैं और फ़ाइलें भी जोड़ सकते हैं। दोनों की जाँच साथ होती है। | तुम्ही मजकूर पेस्ट करू शकता आणि फाइलीही जोडू शकता. दोन्हींची तपासणी एकत्र होते. |
| `submit.drop_title` | Choose files or drop them here | फ़ाइलें चुनें या यहाँ छोड़ें | फाइली निवडा किंवा इथे टाका |
| `submit.drop_types` | PDF, JPG, PNG or TXT, up to 10 files | PDF, JPG, PNG या TXT, ज़्यादा से ज़्यादा 10 फ़ाइलें | PDF, JPG, PNG किंवा TXT, जास्तीत जास्त 10 फाइली |
| `submit.files_label` | Attached files | जोड़ी गई फ़ाइलें | जोडलेल्या फाइली |
| `submit.remove_file` | Remove {name} | {name} हटाएँ | {name} काढा |
| `submit.has_text` | Text added | टेक्स्ट जोड़ा गया | मजकूर जोडला |
| `submit.try_demo` | Try demo | डेमो आज़माएँ | डेमो वापरून पहा |
| `submit.cta` | Review details | जानकारी देखें | माहिती तपासा |
| `review.title` | Does this look right? | क्या यह सही लगता है? | हे बरोबर वाटते का? |
| `review.sub` | Tap a detail to see where it came from. | कोई जानकारी दबाएँ और देखें कि वह कहाँ से आई। | माहितीवर टॅप करा आणि ती कुठून आली ते पहा. |
| `review.flagged` | Flagged | चिह्नित | खूण केलेले |
| `review.source_quote` | Source quote | मूल उद्धरण | मूळ उतारा |
| `review.no_quote` | The offer does not say this. Ask for it in writing. | ऑफ़र में यह नहीं लिखा है। इसे लिखित में माँगें। | ऑफरमध्ये हे लिहिलेले नाही. ते लेखी मागा. |
| `review.more` | More details from the offer ({count}) | ऑफ़र की और जानकारी ({count}) | ऑफरमधील आणखी माहिती ({count}) |
| `review.cta` | See result | नतीजा देखें | निकाल पहा |
| `review.edit` | Edit details | जानकारी बदलें | माहिती बदला |
| `review.not_analyzed` | This offer has not been checked yet. | यह ऑफ़र अभी जाँचा नहीं गया है। | ही ऑफर अजून तपासलेली नाही. |
| `fact.agent` | Agent | एजेंट | एजंट |
| `fact.country` | Country | देश | देश |
| `fact.visa` | Visa | वीज़ा | व्हिसा |
| `fact.salary` | Salary | वेतन | पगार |
| `fact.fee` | Fee | फ़ीस | फी |
| `fact.contract` | Contract | अनुबंध | करार |
| `fact.role` | Job | नौकरी | नोकरी |
| `fact.employer` | Employer | नियोक्ता | नियोक्ता |
| `fact.rc` | Agent RC number | एजेंट RC नंबर | एजंट RC नंबर |
| `fact.payment` | Payment mode | भुगतान का तरीका | पैसे देण्याची पद्धत |
| `fact.channel` | Contact channel | संपर्क का तरीका | संपर्काची पद्धत |
| `fact.transit` | Transit countries | बीच के देश | मधले देश |
| `fact.receipt` | Receipt promised | रसीद का वादा | पावतीचे आश्वासन |
| `fact.pbby` | PBBY insurance | PBBY बीमा | PBBY विमा |
| `fact.passport` | Passport handover | पासपोर्ट सौंपना | पासपोर्ट देणे |
| `value.visa.employment` | Employment | रोज़गार | रोजगार |
| `value.visa.work` | Work | काम | काम |
| `value.visa.tourist` | Tourist | टूरिस्ट | टुरिस्ट |
| `value.visa.visit` | Visit | विज़िट | व्हिजिट |
| `value.visa.unknown` | Unclear | साफ़ नहीं | स्पष्ट नाही |
| `result.word.STOP` | STOP | रुकें | थांबा |
| `result.word.VERIFY` | VERIFY | पहले | आधी |
| `result.word.FIRST` | FIRST | जाँचें | तपासा |
| `result.word.NO_RED_FLAGS_FOUND` | No red flags found. | कोई चेतावनी संकेत नहीं मिला। | धोक्याची खूण आढळली नाही. |
| `result.sub.STOP` | Pause payment and travel. Verify the offer first. | भुगतान और यात्रा रोकें। पहले ऑफ़र की जाँच करें। | पैसे देणे आणि प्रवास थांबवा. आधी ऑफर तपासा. |
| `result.sub.VERIFY_FIRST` | A few details need confirmation. | कुछ बातों की पुष्टि ज़रूरी है। | काही गोष्टींची खात्री करणे गरजेचे आहे. |
| `result.sub.NO_RED_FLAGS_FOUND` | Confirm with the Protector of Emigrants before paying. | पैसे देने से पहले Protector of Emigrants (प्रवासी संरक्षक) से पुष्टि करें। | पैसे देण्याआधी Protector of Emigrants (प्रवासी संरक्षक) यांच्याकडून खात्री करा. |
| `result.tag.STOP` | STOP | रुकें | थांबा |
| `result.tag.VERIFY_FIRST` | VERIFY FIRST | पहले जाँचें | आधी तपासा |
| `result.tag.NO_RED_FLAGS_FOUND` | NO RED FLAGS FOUND | कोई चेतावनी संकेत नहीं | धोक्याची खूण नाही |
| `result.points_heading` | Points from this check | इस जाँच के बिंदु | या तपासणीतील मुद्दे |
| `result.passed` | Checks that passed ({count}) | जिन जाँचों में कुछ नहीं मिला ({count}) | ज्या तपासण्यांत काही आढळले नाही ({count}) |
| `result.severity` | Severity | गंभीरता | गांभीर्य |
| `result.not_clearance` | This is a check, not a clearance. Still verify independently. | यह एक जाँच है, मंज़ूरी नहीं। फिर भी खुद अलग से जाँच करें। | ही एक तपासणी आहे, मंजुरी नाही. तरीही स्वतः वेगळी तपासणी करा. |
| `result.cta_evidence` | See the evidence | सबूत देखें | पुरावा पहा |
| `result.cta_report` | View report | रिपोर्ट देखें | अहवाल पहा |
| `result.get_help` | Get reporting help | शिकायत में मदद लें | तक्रारीसाठी मदत घ्या |
| `result.plan_checkins` | Plan check-ins | चेक-इन तय करें | चेक-इन ठरवा |
| `result.foot_confirm` | Confirm with the Protector of Emigrants before paying. | पैसे देने से पहले Protector of Emigrants से पुष्टि करें। | पैसे देण्याआधी Protector of Emigrants यांच्याकडून खात्री करा. |
| `result.foot_quotes` | Show source quotes + list date | मूल उद्धरण और सूची की तारीख़ देखें | मूळ उतारे आणि यादीची तारीख पहा |
| `evidence.title` | See why it was flagged. | देखें, इसे क्यों चिह्नित किया गया। | याला खूण का केली ते पहा. |
| `evidence.offer_text` | Offer text | ऑफ़र का टेक्स्ट | ऑफरचा मजकूर |
| `evidence.quoted_line` | Quoted line | उद्धृत पंक्ति | उद्धृत ओळ |
| `evidence.counter` | Flag {n} of {total} | {total} में से {n}वाँ बिंदु | {total} पैकी {n} वा मुद्दा |
| `evidence.prev` | Previous flag | पिछला बिंदु | मागचा मुद्दा |
| `evidence.next` | Next flag | अगला बिंदु | पुढचा मुद्दा |
| `evidence.no_quote` | No quote: this point is about something the offer does not say. | कोई उद्धरण नहीं: यह बिंदु उस बात के बारे में है जो ऑफ़र में नहीं लिखी। | उतारा नाही: हा मुद्दा ऑफरमध्ये न लिहिलेल्या गोष्टीबद्दल आहे. |
| `evidence.rule_reference` | Rule reference | नियम का स्रोत | नियमाचा स्रोत |
| `evidence.heuristic_note` | Warning sign, not a rule. No official rule is linked. | चेतावनी संकेत, नियम नहीं। कोई सरकारी नियम जुड़ा नहीं है। | धोक्याची खूण, नियम नाही. कोणताही सरकारी नियम जोडलेला नाही. |
| `evidence.ask_next` | What to ask next | आगे क्या पूछें | पुढे काय विचारायचे |
| `evidence.none` | Nothing was flagged in this check. | इस जाँच में कुछ भी चिह्नित नहीं हुआ। | या तपासणीत कशावरही खूण झाली नाही. |
| `evidence.download` | Download report | रिपोर्ट डाउनलोड करें | अहवाल डाउनलोड करा |
| `evidence.back` | Back to result | नतीजे पर वापस | निकालाकडे परत |
| `plan.demo_only` | Demo alerts only | सिर्फ़ डेमो अलर्ट | फक्त डेमो अलर्ट |
| `plan.title` | Keep family close. | परिवार को साथ रखें। | कुटुंबाला सोबत ठेवा. |
| `plan.sub` | Add up to two trusted contacts and a check-in time. | दो भरोसेमंद संपर्क और चेक-इन का समय जोड़ें। | दोन विश्वासू संपर्क आणि चेक-इनची वेळ जोडा. |
| `plan.you` | You | आप | तुम्ही |
| `plan.contact_n` | Contact {n} | संपर्क {n} | संपर्क {n} |
| `plan.optional` | optional | वैकल्पिक | ऐच्छिक |
| `plan.name_placeholder` | Name or alias | नाम या उपनाम | नाव किंवा टोपणनाव |
| `plan.channel_placeholder` | How to reach them | उनसे संपर्क कैसे करें | संपर्क कसा करायचा |
| `plan.half_contact` | Fill in both the name and how to reach each contact, or leave both empty. | हर संपर्क का नाम और संपर्क का तरीका दोनों भरें, या दोनों खाली छोड़ें। | प्रत्येक संपर्काचे नाव आणि संपर्काची पद्धत दोन्ही भरा, किंवा दोन्ही रिकामे ठेवा. |
| `plan.permission` | I have their permission. | मेरे पास उनकी अनुमति है। | माझ्याकडे त्यांची परवानगी आहे. |
| `plan.cta` | Create check-in plan | चेक-इन योजना बनाएँ | चेक-इन योजना तयार करा |
| `plan.interval_label` | Check-in time | चेक-इन का समय | चेक-इनची वेळ |
| `plan.ring_label` | Check in every {hours} hours | हर {hours} घंटे में चेक-इन | दर {hours} तासांनी चेक-इन |
| `plan.hours_short` | {hours}h | {hours} घं | {hours} ता |
| `plan.every` | Check in every | चेक-इन हर | चेक-इन दर |
| `plan.hours_option` | {hours} hours | {hours} घंटे | {hours} तास |
| `plan.trip` | Add trip details | यात्रा की जानकारी जोड़ें | प्रवासाची माहिती जोडा |
| `plan.need_title` | Check an offer first. | पहले एक ऑफ़र जाँचें। | आधी एक ऑफर तपासा. |
| `plan.need_body` | Check-ins are linked to a checked offer. Check one, then make a plan. | चेक-इन एक जाँचे गए ऑफ़र से जुड़े होते हैं। पहले जाँच करें, फिर योजना बनाएँ। | चेक-इन तपासलेल्या ऑफरशी जोडलेले असतात. आधी तपासा, मग योजना करा. |
| `checkin.title_ok` | Time to check in. | चेक-इन का समय। | चेक-इनची वेळ. |
| `checkin.title_due` | Check in now. | अभी चेक-इन करें। | आता चेक-इन करा. |
| `checkin.title_missed` | Check-in missed. | चेक-इन छूट गया। | चेक-इन चुकले. |
| `checkin.simulated` | Simulated | सिमुलेटेड | सिम्युलेटेड |
| `checkin.missed_note` | Your contacts got a simulated alert. | आपके संपर्कों को सिमुलेटेड अलर्ट गया। | तुमच्या संपर्कांना सिम्युलेटेड अलर्ट गेला. |
| `checkin.see_family` | See the family view | परिवार का दृश्य देखें | कुटुंबाचे दृश्य पहा |
| `checkin.today` | Today | आज | आज |
| `checkin.tomorrow` | Tomorrow | कल | उद्या |
| `checkin.yesterday` | Yesterday | बीता कल | काल |
| `checkin.contacts` | {count} family contacts | {count} परिवार संपर्क | {count} कुटुंबीय संपर्क |
| `checkin.cta` | I'm okay | मैं ठीक हूँ | मी ठीक आहे |
| `checkin.done` | Checked in. Your next check-in time has moved. | चेक-इन हो गया। अगले चेक-इन का समय आगे बढ़ गया। | चेक-इन झाले. पुढच्या चेक-इनची वेळ पुढे गेली. |
| `checkin.trip` | Trip details | यात्रा की जानकारी | प्रवासाची माहिती |
| `checkin.change_time` | Change time | समय बदलें | वेळ बदला |
| `checkin.get_help` | Get help | मदद लें | मदत घ्या |
| `checkin.no_trip` | No trip details added. | यात्रा की कोई जानकारी नहीं जोड़ी गई। | प्रवासाची माहिती जोडलेली नाही. |
| `checkin.contacts_list` | Contacts: {names} | संपर्क: {names} | संपर्क: {names} |
| `checkin.timeline` | Check-in timeline | चेक-इन समयरेखा | चेक-इन कालरेषा |
| `checkin.previous` | Previous check-in | पिछला चेक-इन | मागचे चेक-इन |
| `checkin.next` | Next check-in | अगला चेक-इन | पुढचे चेक-इन |
| `checkin.no_plan_title` | No check-in plan yet. | अभी कोई चेक-इन योजना नहीं। | अजून चेक-इन योजना नाही. |
| `checkin.no_plan_body` | Add up to two contacts and choose how often you will check in. | दो संपर्क जोड़ें और चुनें कि कितनी बार चेक-इन करेंगे। | दोन संपर्क जोडा आणि किती वेळा चेक-इन कराल ते निवडा. |
| `family2.simulated` | Simulated alert | सिमुलेटेड अलर्ट | सिम्युलेटेड अलर्ट |
| `family2.phone_view` | Family phone view | परिवार के फ़ोन का दृश्य | कुटुंबाच्या फोनचे दृश्य |
| `family2.title` | Check-in missed. | चेक-इन छूट गया। | चेक-इन चुकले. |
| `family2.title_none` | No alerts yet. | अभी कोई अलर्ट नहीं। | अजून अलर्ट नाही. |
| `family2.sub` | Try contacting them first. | पहले उनसे संपर्क करने की कोशिश करें। | आधी त्यांच्याशी संपर्क करून पहा. |
| `family2.sub_none` | If a check-in is missed, a simulated alert shows here. | चेक-इन छूटने पर यहाँ सिमुलेटेड अलर्ट दिखेगा। | चेक-इन चुकल्यास इथे सिम्युलेटेड अलर्ट दिसेल. |
| `family2.cta_report` | View trip & report | यात्रा और रिपोर्ट देखें | प्रवास आणि अहवाल पहा |
| `family2.back_checkin` | Back to check-in | चेक-इन पर वापस | चेक-इनकडे परत |
| `family2.reporting` | Reporting options | शिकायत के विकल्प | तक्रारीचे पर्याय |
| `family2.to` | To {alias} via {channel} | {alias} को, {channel} से | {alias} यांना, {channel} द्वारे |
| `help.demo_directory` | Demo directory | डेमो सूची | डेमो यादी |
| `help.title` | Find the right help. | सही मदद पाएँ। | योग्य मदत शोधा. |
| `help.verify` | Verify on the official site before use | इस्तेमाल से पहले सरकारी साइट पर जाँचें | वापरण्याआधी सरकारी साइटवर तपासा |
| `help.mea.name` | MEA | MEA | MEA |
| `help.mea.what` | Agent complaints helpline | एजेंट शिकायत हेल्पलाइन | एजंट तक्रार हेल्पलाइन |
| `help.madad.name` | MADAD | MADAD | MADAD |
| `help.madad.what` | Consular help | कांसुलर मदद | कॉन्सुलर मदत |
| `help.embassy.name` | Embassy | दूतावास | दूतावास |
| `help.embassy.what` | Indian mission overseas | विदेश में भारतीय मिशन | परदेशातील भारतीय मिशन |
| `help.cyber.name` | 1930 | 1930 | 1930 |
| `help.cyber.what` | Cyber crime and lost money | साइबर अपराध, ऑनलाइन पैसे का नुकसान | सायबर गुन्हा, ऑनलाइन पैशांचे नुकसान |
| `help.police.name` | Police | पुलिस | पोलीस |
| `help.police.what` | Report a crime locally | स्थानीय पुलिस में शिकायत | स्थानिक पोलिसांकडे तक्रार |
| `help.emigrate.name` | eMigrate | eMigrate | eMigrate |
| `help.emigrate.what` | Check an agent's RC number | एजेंट का RC नंबर जाँचें | एजंटचा RC नंबर तपासा |
| `help.report_zip` | Get report ZIP | रिपोर्ट ZIP पाएँ | अहवाल ZIP मिळवा |
| `help.zip_note` | The ZIP has the offer, quotes and rule results. Nothing is sent anywhere. | ZIP में ऑफ़र, उद्धरण और नियमों के नतीजे हैं। कुछ भी कहीं नहीं भेजा जाता। | ZIP मध्ये ऑफर, उतारे आणि नियमांचे निकाल आहेत. काहीही कुठेही पाठवले जात नाही. |
| `help.zip_none` | Check an offer to make a report ZIP. | रिपोर्ट ZIP के लिए पहले ऑफ़र जाँचें। | अहवाल ZIP साठी आधी ऑफर तपासा. |
| `help.limit_legal` | Not legal advice | कानूनी सलाह नहीं | कायदेशीर सल्ला नाही |
| `help.limit_report` | No automatic reporting | अपने-आप कोई शिकायत नहीं | आपोआप तक्रार नाही |
| `help.limit_demo` | Demo data is synthetic | डेमो डेटा काल्पनिक है | डेमो डेटा काल्पनिक आहे |
| `help.limit_wrong` | It can be wrong | यह गलत हो सकता है | हे चुकू शकते |
| `login.hero` | See patterns. Respect privacy. | पैटर्न देखें। निजता का सम्मान करें। | पॅटर्न पहा. गोपनीयतेचा आदर करा. |
| `login.restricted` | Restricted access | सीमित पहुँच | मर्यादित प्रवेश |
| `login.title` | Institutional access | संस्थागत लॉगिन | संस्थात्मक लॉगिन |
| `login.show_password` | Show password | पासवर्ड दिखाएँ | पासवर्ड दाखवा |
| `login.cta` | Enter demo | डेमो में जाएँ | डेमोमध्ये जा |
| `pmap.title` | Patterns, at a glance. | पैटर्न, एक नज़र में। | पॅटर्न, एका नजरेत. |
| `pmap.synthetic` | Synthetic data | काल्पनिक डेटा | काल्पनिक डेटा |
| `pmap.filter_label` | Highlight a district | ज़िला चुनें | जिल्हा निवडा |
| `pmap.all_districts` | All districts | सभी ज़िले | सर्व जिल्हे |
| `pmap.illustrative` | Illustrative map | उदाहरण नक्शा | उदाहरण नकाशा |
| `pmap.demo` | Demo | डेमो | डेमो |
| `pmap.repeated_hashes` | Repeated hashes | दोहराए गए हैश | पुन्हा आलेले हॅश |
| `pmap.chips_label` | Highlighted districts | चुने गए ज़िले | निवडलेले जिल्हे |
| `pmap.explore` | Explore patterns | पैटर्न देखें | पॅटर्न पहा |
| `pmap.hash_note` | Hashes link reports; repetition alone does not establish wrongdoing. | हैश रिपोर्टों को जोड़ते हैं; सिर्फ़ दोहराव से गलत काम साबित नहीं होता। | हॅश अहवाल जोडतात; फक्त पुनरावृत्तीने चुकीचे काम सिद्ध होत नाही. |
| `pmap.row` | {count} reports, {n} districts | {count} रिपोर्ट, {n} ज़िले | {count} अहवाल, {n} जिल्हे |
| `pdetail.title_agent` | One contact. {n} districts. | एक संपर्क। {n} ज़िले। | एक संपर्क. {n} जिल्हे. |
| `pdetail.title_template` | One template. {n} districts. | एक जैसा ऑफ़र। {n} ज़िले। | एकसारखी ऑफर. {n} जिल्हे. |
| `pdetail.hash` | Hash | हैश | हॅश |
| `pdetail.copy` | Copy full hash | पूरा हैश कॉपी करें | पूर्ण हॅश कॉपी करा |
| `pdetail.copied` | Copied | कॉपी हुआ | कॉपी झाले |
| `pdetail.graph_label` | Hash {hash} linked to {districts} | हैश {hash}, जुड़े ज़िले: {districts} | हॅश {hash}, जोडलेले जिल्हे: {districts} |
| `pdetail.side_label` | Pattern details | पैटर्न की जानकारी | पॅटर्नची माहिती |
| `pdetail.reports` | {count} demo reports | {count} डेमो रिपोर्ट | {count} डेमो अहवाल |
| `pdetail.reports_body` | {count} synthetic reports share this hash across {n} districts. | {n} ज़िलों की {count} काल्पनिक रिपोर्टों में यही हैश है। | {n} जिल्ह्यांतील {count} काल्पनिक अहवालांत हाच हॅश आहे. |
| `pdetail.districts` | {n} districts | {n} ज़िले | {n} जिल्हे |
| `pdetail.district_total` | {count} reports in district | ज़िले में {count} रिपोर्ट | जिल्ह्यात {count} अहवाल |
| `pdetail.full_hash` | Full hash | पूरा हैश | पूर्ण हॅश |
| `pdetail.hash_explain` | A one-way hash. It links reports without showing the phone number or text. | एकतरफ़ा हैश। यह फ़ोन नंबर या टेक्स्ट दिखाए बिना रिपोर्टों को जोड़ता है। | एकतर्फी हॅश. फोन नंबर किंवा मजकूर न दाखवता तो अहवाल जोडतो. |
| `pdetail.not_found` | This pattern is not in the current data. | यह पैटर्न मौजूदा डेटा में नहीं है। | हा पॅटर्न सध्याच्या डेटामध्ये नाही. |
| `pdetail.back` | Back to map | नक्शे पर वापस | नकाशाकडे परत |
| `value.token.upi` | UPI | UPI | UPI |
| `value.token.cash` | Cash | नकद | रोख |
| `value.token.bank_transfer` | Bank transfer | बैंक ट्रांसफ़र | बँक ट्रान्सफर |
| `value.token.card` | Card | कार्ड | कार्ड |
| `value.token.crypto` | Crypto | क्रिप्टो | क्रिप्टो |
| `value.token.other` | Other | अन्य | इतर |
| `value.token.whatsapp` | WhatsApp | WhatsApp | WhatsApp |
| `value.token.telegram` | Telegram | Telegram | Telegram |
| `value.token.instagram` | Instagram | Instagram | Instagram |
| `value.token.facebook` | Facebook | Facebook | Facebook |
| `value.token.email` | Email | ईमेल | ईमेल |
| `value.token.website` | Website | वेबसाइट | वेबसाइट |
| `value.token.phone` | Phone | फ़ोन | फोन |
| `value.token.office_address` | Office address | दफ़्तर का पता | कार्यालयाचा पत्ता |
| `value.token.employer` | Employer | नियोक्ता | नियोक्ता |
| `value.token.agent` | Agent | एजेंट | एजंट |
| `value.token.worker` | Worker | कामगार | कामगार |
| `error.unavailable` | This feature is not available on the server yet. | यह सुविधा अभी सर्वर पर उपलब्ध नहीं है। | ही सुविधा अजून सर्व्हरवर उपलब्ध नाही. |
