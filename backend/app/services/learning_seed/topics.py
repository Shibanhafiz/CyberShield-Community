"""Seed data: 10 learning topics for the Learning Center.

All example messages use fictional placeholders. Keep entries short —
the frontend renders them as cards, not articles.
"""

TOPICS: list[dict] = [
    {
        "slug": "how-scams-work",
        "title": "How Scams Work: An Introduction",
        "category": "Fundamentals",
        "description": "The basic tricks almost every scam relies on, in plain language.",
        "content": {
            "what_it_is": "Most scams are not hacking. They are persuasion: a stranger creates urgency or fear, pretends to be someone trustworthy, and asks you to act before you can think or verify.",
            "warning_signs": [
                "Pressure to act immediately",
                "Threats (account blocked, arrest, disconnection)",
                "Requests for OTPs, passwords, PINs or money",
                "Instructions to keep the matter secret",
                "Contact moved to a private chat, app or video call",
            ],
            "example": "You get a call: 'Your bank account will be frozen in 2 hours. Tell me the OTP you just received to stop it.' The caller sounds official and does not let you hang up.",
            "attacker_goal": "To make you hand over money or secret codes before you verify who they really are.",
            "should_do": [
                "Pause. Scammers need you in a hurry; slowing down defeats them.",
                "Verify through an official channel you open yourself (official app, website, helpline).",
                "Talk to a family member before acting.",
            ],
            "never_do": [
                "Never share OTPs, PINs, passwords or card numbers with anyone.",
                "Never transfer money to 'prove innocence' or 'pay a fee' to strangers.",
                "Never stay on a video call with an unknown 'officer'.",
            ],
        },
    },
    {
        "slug": "phishing",
        "title": "Phishing Messages & Fake Links",
        "category": "Phishing",
        "description": "Fake SMS, WhatsApp and email messages that steal logins and money.",
        "content": {
            "what_it_is": "Phishing messages pretend to come from a bank, delivery company, government office or social app. They contain a link to a fake website that looks real and steals whatever you type.",
            "warning_signs": [
                "Unexpected link asking you to log in, verify or pay",
                "Sender name looks right but the actual link looks odd",
                "Spelling mistakes or strange domain endings",
                "Threats like 'account will be blocked today'",
            ],
            "example": "SMS: 'Dear customer, your KYC is pending. Update now or services stop: http://kyc-verify-example.tk' (fictional link). The real bank never sends such links.",
            "attacker_goal": "To get you to open the link and type your login, card or personal details.",
            "should_do": [
                "Do not open the link. Open the official app or website yourself.",
                "Check the sender: compare the real official number or address.",
                "Report the message in CyberShield so the community can track it.",
            ],
            "never_do": [
                "Never log in through a link received by SMS, WhatsApp or email.",
                "Never forward the link to friends 'to check' — they might open it.",
            ],
        },
    },
    {
        "slug": "otp-banking-scams",
        "title": "OTP & Banking Scams",
        "category": "OTP & Banking",
        "description": "Why no genuine caller ever needs your OTP.",
        "content": {
            "what_it_is": "An OTP proves it is YOU. Scammers trigger a real OTP to your phone (by starting a transaction) and then call pretending to be bank staff, asking you to read it out to 'stop fraud' or 'get a refund'.",
            "warning_signs": [
                "Anyone asking for your OTP — by call, SMS or chat",
                "'Refund' or 'cashback' that needs your OTP or a collect request",
                "Claims your account shows fraud and you must act now",
                "Caller knows your name or partial details (these leak easily)",
            ],
            "example": "Call: 'Sir, Rs 49,999 was wrongly debited. I am sending an OTP to reverse it — please read it out.' The OTP actually authorises a payment FROM your account.",
            "attacker_goal": "To get the OTP that completes a transaction from your account.",
            "should_do": [
                "Cut the call. Call your bank's official helpline yourself.",
                "Read every OTP SMS fully — it says what the code is for.",
                "If you shared an OTP, block your card/UPI and call the bank at once.",
            ],
            "never_do": [
                "Never read out or forward an OTP to anyone — not bank staff, not police, not family asking over a new number.",
                "Never approve a UPI 'collect request' from strangers, even for 'refunds'.",
            ],
        },
    },
    {
        "slug": "job-scams",
        "title": "Job & Work-From-Home Scams",
        "category": "Job Scams",
        "description": "Fake offers that charge you before you earn anything.",
        "content": {
            "what_it_is": "Fake recruiters offer easy high-paying work (typing, rating videos, reviews) and ask for a registration, training or verification fee first. The job never exists — or pays only until you deposit more.",
            "warning_signs": [
                "Joining, registration or kit fee before any work",
                "Salary far above market for simple tasks, no interview",
                "Contact only on WhatsApp or Telegram, no company email",
                "Pressure: 'offer closes today, pay now'",
            ],
            "example": "'Congratulations! Selected for data-entry work, Rs 30,000/week from home. Pay Rs 2,000 security deposit to start.' Real employers never charge candidates.",
            "attacker_goal": "To collect advance fees (and sometimes ID documents) from many job seekers.",
            "should_do": [
                "Verify the company on its official website and careers page.",
                "Ask for a written offer on company letterhead with a verifiable contact.",
                "Search the company name plus the word 'fraud' before paying anything.",
            ],
            "never_do": [
                "Never pay to get a job — no genuine employer charges candidates.",
                "Never send ID copies plus fees to unknown recruiters.",
            ],
        },
    },
    {
        "slug": "investment-scams",
        "title": "Investment & Trading Scams",
        "category": "Investment Scams",
        "description": "Guaranteed returns that guarantee only your loss.",
        "content": {
            "what_it_is": "Fraudsters promise huge assured profits from stocks, crypto, forex or 'AI trading bots'. Early small withdrawals are allowed to build trust; then they demand bigger deposits and disappear.",
            "warning_signs": [
                "Guaranteed or risk-free high returns ('double in 30 days')",
                "Pressure to invest today, 'limited slots'",
                "Unregistered 'advisors' on Telegram/WhatsApp groups",
                "Fake profit dashboards showing your money 'growing'",
            ],
            "example": "'Our AI bot earns 10% daily on crypto. Deposit Rs 25,000 and watch it grow risk-free.' The dashboard is fake; withdrawals stop once you deposit more.",
            "attacker_goal": "To get you to deposit larger and larger sums you can never withdraw.",
            "should_do": [
                "Remember: high returns always mean high risk. Guarantees are a red flag.",
                "Deal only with SEBI-registered intermediaries; verify registration.",
                "Discuss any investment with a trusted person first.",
            ],
            "never_do": [
                "Never invest through links or groups strangers send you.",
                "Never pay 'release fees' or 'taxes' to withdraw your own money.",
            ],
        },
    },
    {
        "slug": "delivery-scams",
        "title": "Delivery & Courier Scams",
        "category": "Delivery Scams",
        "description": "Fake parcel holds that demand small release fees.",
        "content": {
            "what_it_is": "You get an SMS that a parcel is stuck and needs a small fee (Rs 25–200) via a link. The link steals card details or installs malware. Sometimes a 'prize parcel' needs delivery charges.",
            "warning_signs": [
                "Parcel you never ordered, or fee you never agreed to",
                "Tiny urgent fee with a link, odd domain",
                "Tracking link sent by SMS instead of the official app",
            ],
            "example": "'India Post: package held. Pay Rs 25 redelivery fee here: [link].' You were expecting nothing — and the post office does not work this way.",
            "attacker_goal": "To steal your card details or install malware through the payment link.",
            "should_do": [
                "Track parcels only in the courier's official app or website.",
                "If expecting nothing, ignore and delete the message.",
            ],
            "never_do": [
                "Never pay delivery fees through SMS links.",
                "Never enter card details on pages opened from message links.",
            ],
        },
    },
    {
        "slug": "digital-arrest",
        "title": "Digital-Arrest & Police-Threat Scams",
        "category": "Digital Arrest",
        "description": "Fake officers on video calls demanding money.",
        "content": {
            "what_it_is": "Callers posing as police, CBI, customs or judges accuse you of a crime (drugs parcel, money laundering) and keep you on a video call — a so-called 'digital arrest' — until you transfer money to 'prove innocence'.",
            "warning_signs": [
                "Video-call 'interrogation' by supposed officers",
                "Orders not to disconnect or tell anyone",
                "Demands to transfer money to 'verify funds' or pay bail online",
                "Case numbers and uniforms shown on camera (easily faked)",
            ],
            "example": "'CBI officer speaking. A parcel in your name has illegal items. Stay on video call and transfer Rs 2,00,000 as security deposit.' Real agencies never work like this.",
            "attacker_goal": "To frighten you into transferring money while isolated on a call.",
            "should_do": [
                "Hang up immediately. Real police never demand money on video calls.",
                "Call the national cyber helpline 1930 or visit your local police station.",
                "Tell a family member what happened.",
            ],
            "never_do": [
                "Never stay on a video call with unknown 'officers'.",
                "Never transfer money to 'prove innocence' or avoid arrest.",
                "Never keep it secret because the caller ordered secrecy.",
            ],
        },
    },
    {
        "slug": "fake-support",
        "title": "Fake Customer-Support Scams",
        "category": "Fake Support",
        "description": "Fraud helplines and agents who 'fix' problems by robbing you.",
        "content": {
            "what_it_is": "Fake support numbers appear in search results. When you call, the 'agent' asks you to install a remote-access app, share your screen, or pay a fee — then empties your account or locks your device.",
            "warning_signs": [
                "Support number found via random search results or ads",
                "Agent asks for remote access (TeamViewer, QuickSupport, screen share)",
                "Payment to a personal UPI ID for 'service charges'",
                "Calls about problems you never reported",
            ],
            "example": "'Amazon support: a Rs 54,999 order was placed on your account. Share your screen so we can cancel it.' The order never existed; screen access lets them steal OTPs.",
            "attacker_goal": "To see your screen (OTPs, banking) or get direct payments.",
            "should_do": [
                "Use support contacts from the official app or website only.",
                "If a company calls you, hang up and call back on the official number.",
            ],
            "never_do": [
                "Never install remote-access apps at a stranger's request.",
                "Never share your screen with unknown 'agents'.",
            ],
        },
    },
    {
        "slug": "malicious-apps",
        "title": "Malicious Apps & APKs",
        "category": "Malicious Apps",
        "description": "Dangerous apps that spy on your SMS and steal OTPs.",
        "content": {
            "what_it_is": "Scammers send apps outside the Play Store ('update KYC app', 'electricity bill app', 'trading app'). Once installed, these apps read your SMS (including OTPs), contacts and banking apps.",
            "warning_signs": [
                "APK file sent over WhatsApp or a download link",
                "App asks for SMS, accessibility or notification permissions",
                "App name mimics a bank or government service",
                "'Support agent' guiding the installation step by step",
            ],
            "example": "'Electricity department: download this Quick Bill app to avoid disconnection tonight.' The app reads all incoming OTP SMS and forwards them to criminals.",
            "attacker_goal": "To silently read OTPs and banking messages from your phone.",
            "should_do": [
                "Install apps only from the Google Play Store (or App Store).",
                "Check app permissions; deny SMS/accessibility access you do not understand.",
                "If installed, uninstall, change passwords and inform your bank.",
            ],
            "never_do": [
                "Never install APKs sent by strangers or support callers.",
                "Never grant SMS or accessibility permissions to unknown apps.",
            ],
        },
    },
    {
        "slug": "social-engineering",
        "title": "Social-Engineering Tactics",
        "category": "Social Engineering",
        "description": "The psychological tricks behind every scam above.",
        "content": {
            "what_it_is": "Social engineering means manipulating people instead of computers. Four levers appear again and again: urgency (act now), authority (bank, police, support), secrecy (tell no one), and greed or fear (prize, prize loss, arrest).",
            "warning_signs": [
                "Urgency: countdowns, 'today only', '2 hours left'",
                "Authority: uniforms, badges, official-sounding titles",
                "Secrecy: 'do not tell family or police'",
                "Too good to be true: prizes, guaranteed returns, dream jobs",
            ],
            "example": "A 'customs officer' says a gift parcel needs Rs 15,000 duty today, and warns you not to tell anyone. Urgency + authority + secrecy = all three levers at once.",
            "attacker_goal": "To stop you from thinking clearly or asking for help.",
            "should_do": [
                "Name the trick: 'They are rushing me. They forbid me from asking help.'",
                "Break secrecy first — tell someone you trust.",
                "Verify independently, never through contacts the stranger provides.",
            ],
            "never_do": [
                "Never obey 'keep this secret' from an unknown caller.",
                "Never decide under a countdown — hang up and think.",
            ],
        },
    },
]
