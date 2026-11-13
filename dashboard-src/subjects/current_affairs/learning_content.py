"""Editorial learning layer, checked against PDF file-page numbers (not printed pages).

All event claims retain the supplied issue's time context. These are study selections,
not a claim that eight bullets exhaust a chapter. Memory aids are explicitly editorial.
"""

LEARNING = {
    1: {
        "intro": "A one-liner becomes easier to remember when you attach its category, place and date. Start with these anchor facts, then use the source Q&A bank to build your own three-column revision sheet.",
        "route": ["Match the category before the answer", "Keep amounts with their scheme", "Keep sports results with the event and year"],
        "aid": "Build a three-column sheet: trigger | answer | date/category. Cover the answer column and recall it. This is a learning aid, not an exam-frequency ranking.",
        "points": [
            ("Three air-quality categories", "Swachh Vayu Survekshan 2026: above 10 lakh population - Lucknow; 3-10 lakh - Rourkela; below 3 lakh - Kalinganagar. Keep each winner with its population band.", [5]),
            ("A train needs two endpoints", "The issue places the hydrogen fuel-cell train on the Jind-Sonipat section in Haryana. Water is the stated by-product of electricity generation in the fuel cell.", [5]),
            ("A named wetland", "Jai Prakash Narayan Bird Sanctuary is also called Surha Tal and is in Ballia, Uttar Pradesh. The one-liner calls it India's 100th Ramsar site in June 2026; the map gives another date, flagged below.", [5, 145]),
            ("Cotton mission outlay", "The Mission for Cotton Productivity has a stated total outlay of ₹5,659.22 crore. Keep the programme's name and amount together.", [5, 6]),
            ("Two Census mascots", "Census 2027 mascots: Pragati is the female enumerator and Vikas is the male enumerator. Retain both names and their roles.", [6]),
            ("Welfare outlay", "The one-liner gives ₹53,428 crore for Pradhan Mantri Samajik Sahayata Yojana. The detailed article links this to the renamed National Social Assistance Programme for FY 2026-27 to FY 2030-31.", [10, 93]),
            ("Distance, event, placing", "Neeraj Chopra's Lausanne Diamond League 2026 result is reported as second place with 88.05 metres on 21 August 2026. Retain the metres unit with the event and placing.", [17]),
            ("Venue pair", "The issue places the 23rd Commonwealth Games in Glasgow, Scotland, from 23 July to 2 August 2026, and lists Ahmedabad, Gujarat, as the 2030 host.", [17])
        ],
        "comparison": {"title": "Same award survey, different population bands", "headers": ["Population category", "Winner in the issue", "Recall cue"], "rows": [["Above 10 lakh", "Lucknow", "Largest band"], ["3-10 lakh", "Rourkela", "Middle band"], ["Below 3 lakh", "Kalinganagar", "Smallest band"]], "pages": [5]},
        "recall": [
            ("Why is 'Lucknow won Swachh Vayu' an incomplete revision note?", "It omits the population category. The issue names Lucknow only for cities above 10 lakh; Rourkela and Kalinganagar win the other two bands.", [5]),
            ("Reconstruct the hydrogen-train fact in three parts.", "Jind-Sonipat | Haryana | water as the fuel-cell electricity-generation by-product. Linking route, state and science prevents a place-only answer.", [5]),
            ("Match the cotton mission to its stated outlay.", "Mission for Cotton Productivity - ₹5,659.22 crore. Modified UDAN and the welfare programme have different outlays; the scheme name is part of the answer.", [5, 6]),
            ("Distinguish Pragati from Vikas.", "Both are Census 2027 mascots: Pragati represents a female enumerator and Vikas a male enumerator.", [6]),
            ("Give Neeraj Chopra's Lausanne result with its unit and context.", "88.05 metres: Neeraj Chopra's reported second-place javelin throw at the Lausanne Diamond League on 21 August 2026. A bare number is harder to check and remember.", [17])
        ],
        "practice": [
            ("In the supplied issue, which city wins the Swachh Vayu category below 3 lakh population?", ["Lucknow", "Rourkela", "Kalinganagar", "Jabalpur"], 2, "Kalinganagar belongs to the below-3-lakh band. Lucknow wins above 10 lakh and Rourkela wins 3-10 lakh; the category is the decisive detail.", 5),
            ("Which Census 2027 mascot-role pair is reported correctly?", ["Pragati - female enumerator", "Pragati - male enumerator", "Vikas - female enumerator", "Vikas - farmer identity mascot"], 0, "Pragati represents the female enumerator; Vikas represents the male enumerator. The source pairs two names with two roles.", 6),
            ("What is the Mission for Cotton Productivity outlay in the issue?", ["₹28,840 crore", "₹53,428 crore", "₹2,584.60 crore", "₹5,659.22 crore"], 3, "The mission's stated outlay is ₹5,659.22 crore. ₹28,840 crore is associated with Modified UDAN; ₹53,428 crore is the welfare-programme figure.", 6),
            ("What distance accompanies Neeraj Chopra's reported Lausanne 2026 second place?", ["88.05 metres", "88.05 kilometres", "85.08 metres", "90.58 metres"], 0, "The result is 88.05 metres. Metres measure the javelin throw; keep the reported second place and Lausanne 2026 context with the distance.", 17)
        ],
        "checks": [
            {"pages": [6], "text": "The ₹2,584.60 crore answer follows a question saying only 'this scheme', after an unrelated euthanasia item. The answer is preserved in the source evidence, but is not assigned to a scheme in the guide or tested."},
            {"pages": [5, 145], "text": "The one-liner dates Surha Tal's 100th-site news to June 2026, while the map prints 19 January 2025. Keep both source dates visible; no current Ramsar-date verification is claimed."}
        ]
    },
    2: {
        "intro": "Read national news as a chain: institution → decision → intended effect → number or date. Separate the historical launch of a scheme from a later expansion, and a legal right from its safeguards.",
        "route": ["Schemes: ministry and purpose", "Institutions: legal basis and dates", "Infrastructure: route and status"],
        "aid": "For each scheme write WHO does WHAT for WHOM. Add the outlay last. This editorial prompt helps reconstruct a fact instead of memorising an isolated amount.",
        "points": [
            ("UDAN's purpose", "RCS-UDAN means Regional Connectivity Scheme - Ude Desh ka Aam Nagrik. The source dates its launch to 21 October 2016 and describes affordable connectivity to unserved and underserved regions.", [18]),
            ("SEMICON's value chain", "SEMICON India 2026 ran at Yashobhoomi, New Delhi, on 17-19 September under Silicon to Systems: Building the Ecosystem. Semicon 2.0 has six pillars spanning design, materials, fabrication, packaging, R&D and talent.", [28]),
            ("Ken to Betwa", "The Ken-Betwa Link Project transfers surplus Ken basin water towards the water-deficit Betwa basin in Bundelkhand, across Madhya Pradesh and Uttar Pradesh. Both rivers are Yamuna tributaries; Phase I includes Daudhan Dam.", [38]),
            ("Modified UDAN", "The issue gives an outlay of ₹28,840 crore for FY 2026-27 to FY 2035-36, with 100 airports and 200 modern helipads envisaged. Its approval and launch dates are separate milestones.", [18, 47]),
            ("RTI's two dates", "The RTI Act received assent on 15 June 2005 and became fully operational on 12 October 2005. Its full-implementation anniversary in the issue is 12 October 2026.", [19]),
            ("Census: two different tasks", "Census 2027 has Houselisting and Housing Census followed by Population Enumeration. The Office of the Registrar General and Census Commissioner, India, under the Ministry of Home Affairs, conducts it; digital collection still includes house-to-house visits.", [49, 50]),
            ("Market access for SHGs", "SARAS Melas under DAY-NRLM connect rural women entrepreneurs with buyers. The Vijayawada edition at Punnami Ghat is dated 13-31 October 2026; the issue traces the first National SARAS Mela to Delhi in 1999.", [19]),
            ("Access with safeguards", "The issue's internet-rights article distinguishes access under Article 21 read with Article 19(1)(a) from permissible protection against harmful content; it lists child modes, parental supervision and private-by-default accounts.", [18])
        ],
        "comparison": {"title": "Do not confuse a scheme's timeline", "headers": ["Milestone", "Source date/detail", "What to remember"], "rows": [["UDAN launch", "21 October 2016", "Scheme begins"], ["First UDAN flight", "Shimla-Delhi, April 2017", "Operational milestone"], ["Modified UDAN", "₹28,840 crore; FY 2026-27 to 2035-36", "Later expansion"]], "pages": [18, 47]},
        "recall": [
            ("Explain UDAN in one sentence without using its outlay.", "It is the regional-connectivity scheme for affordable and viable air services to unserved and underserved regions. Purpose comes before the expansion figures.", [18]),
            ("Reconstruct the Ken-Betwa link as a direction and two States.", "Surplus Ken basin water moves towards the water-deficit Betwa basin in Bundelkhand, across Madhya Pradesh and Uttar Pradesh. Both rivers are tributaries of the Yamuna.", [38]),
            ("Which two RTI dates should a timeline keep?", "15 June 2005 for assent and 12 October 2005 for full operation. The 21-year anniversary is measured from full operation.", [19]),
            ("What does Silicon to Systems ask you to remember beyond a chip factory?", "The source's Semicon 2.0 ecosystem includes design, machines and materials, fabrication, advanced packaging, R&D and talent development. A complete value chain has several linked capabilities.", [28]),
            ("Distinguish the Census's two phases and its collection method.", "Houselisting and Housing Census records homes, amenities and assets; Population Enumeration records people and their characteristics. Digital collection and optional self-enumeration do not remove house-to-house visits.", [49, 50])
        ],
        "practice": [
            ("Which pair correctly separates UDAN's launch and first flight?", ["2017 launch; 2016 first flight", "2016 launch; Shimla-Delhi flight in April 2017", "2016 launch; Jind-Sonipat flight in 2017", "2026 launch; Shimla-Delhi flight in 2026"], 1, "The source launches the scheme on 21 October 2016 and dates its first Shimla-Delhi flight to April 2017. Launch and first operation are different events.", 18),
            ("From which RTI milestone does the issue count 21 years in October 2026?", ["Assent on 15 June 2005", "Raj Narain judgment in 1975", "Full operation on 12 October 2005", "Freedom of Information Act, 2002"], 2, "The anniversary is of full implementation on 12 October 2005. Assent was earlier, on 15 June 2005.", 19),
            ("Which direction and river system fit the Ken-Betwa project?", ["Ken to Betwa; both Yamuna tributaries", "Betwa to Ken; both Godavari tributaries", "Ken to Ganga; both Narmada tributaries", "Betwa to Mahanadi; both coastal rivers"], 0, "The project seeks to transfer surplus Ken basin water towards the water-deficit Betwa basin. Both rivers are Yamuna tributaries, serving Bundelkhand in MP and UP.", 38),
            ("Which Census statement correctly separates the two phases?", ["Population Enumeration records only housing assets", "Houselisting replaces Population Enumeration", "Houselisting and Population Enumeration are the same task", "Houselisting records homes and amenities; Population Enumeration records people's characteristics"], 3, "Houselisting records housing conditions, amenities and assets; Population Enumeration records demography, literacy, migration and other population characteristics. The two phases serve different purposes.", 49)
        ],
        "checks": [{"pages": [18, 47], "text": "The issue discusses a Modified UDAN launch on 4 July 2026 and Cabinet approval on 25 March 2026. These are kept as distinct milestones; the date is not silently replaced by one undifferentiated 'launch' date."}]
    },
    3: {
        "intro": "International affairs is a matching exercise with a reason behind each match. Learn the organisation's members and purpose, then attach a summit's host, theme and outcome. Keep an index's edition year separate from the year it is released.",
        "route": ["Bilateral: partner and agreement", "Multilateral: members, host, outcome", "Reports: publisher, edition, rank"],
        "aid": "Use 'M-H-O' for a summit: Members, Host, Outcome. For an index, use 'P-Y-R': Publisher, Year, Rank. These are editorial memory prompts.",
        "points": [
            ("EFTA's four members", "EFTA comprises Iceland, Liechtenstein, Norway and Switzerland. The source states that Switzerland is outside the European Economic Area.", [53]),
            ("TEPA dates and scale", "India-EFTA TEPA was signed on 10 March 2024 and entered into force on 1 October 2025. Its stated aims are US$100 billion in investment and one million direct Indian jobs over 15 years.", [53]),
            ("The Swiss visit's 3Ts", "Guy Parmelin's 5-7 October 2026 visit is organised around Trade, Technology and Talent. The source lists migration, young-professional exchange, transport technology, research and innovation arrangements.", [53]),
            ("Mobility is not unlimited exchange", "The young-professionals agreement provides for 300 professionals annually from each side, expandable to 500. The migration MoU separately mentions multiple-entry visas valid up to five years.", [53]),
            ("BRICS host and theme", "The issue places the 18th BRICS Summit at Bharat Mandapam, New Delhi, on 12-13 September 2026. Its theme is Building for Resilience, Innovation, Cooperation and Sustainability.", [75]),
            ("Membership versus participation", "The summit account distinguishes 11 full BRICS members from 10 partner countries. It also counts 32 delegations, including regional and international organisations.", [75]),
            ("Payment cooperation", "The BRICS article reports work on local-currency transactions and payment-system interoperability. It explicitly says no common BRICS currency was announced.", [75]),
            ("A complete index entry", "The issue's summary lists Human Development Report 2025 - UNDP - India 130 of 193; Global Innovation Index 2025 - WIPO - India 38th. Edition labels must stay attached to the ranks.", [86])
        ],
        "comparison": {"title": "Organisations and agreements are different things", "headers": ["Term", "What it is in this chapter", "Anchor fact"], "rows": [["EFTA", "Four-country trade association", "Iceland, Liechtenstein, Norway, Switzerland"], ["India-EFTA TEPA", "Trade and economic partnership agreement", "In force 1 October 2025"], ["BRICS", "Multilateral grouping", "Full members and partner countries are distinct"]], "pages": [53, 75]},
        "recall": [
            ("Name all four EFTA members, then identify the EEA exception stated here.", "Iceland, Liechtenstein, Norway and Switzerland. The source identifies Switzerland as not belonging to the EEA; EFTA membership does not automatically mean EEA membership.", [53]),
            ("Explain why 2024 and 2025 both matter for TEPA.", "10 March 2024 is the signing date; 1 October 2025 is entry into force. Signing and legal operation are separate milestones.", [53]),
            ("Reconstruct the TEPA target with a time period.", "US$100 billion in investment and one million direct jobs in India over 15 years. Dropping the 15-year period changes the scale of the claim.", [53]),
            ("Does the summit article announce a common BRICS currency?", "No. It discusses local currencies and interoperability among payment/messaging systems, while explicitly saying no common currency was announced.", [75]),
            ("What three fields should you remember for an index?", "Publisher, edition year and rank (plus denominator where given). Here HDR 2025 is UNDP, 130/193; GII 2025 is WIPO, 38th.", [86])
        ],
        "practice": [
            ("Which country belongs to EFTA in the source's four-member list?", ["Germany", "France", "Norway", "Italy"], 2, "Norway is listed with Iceland, Liechtenstein and Switzerland. Do not substitute a nearby European country for a member.", 53),
            ("What does 1 October 2025 mark in the TEPA timeline?", ["EFTA's establishment", "TEPA's entry into force", "TEPA's signing", "The 18th BRICS Summit"], 1, "The agreement was signed on 10 March 2024 and entered into force on 1 October 2025. EFTA itself was established in 1960.", 53),
            ("Which BRICS statement preserves the supplied summit account?", ["A common BRICS currency was launched", "Partner countries are all full members", "Only 11 delegations attended", "Payment interoperability continued; no common currency was announced"], 3, "The source explicitly distinguishes payment/local-currency cooperation from a common currency and full members from partners.", 75),
            ("Which report-publisher pair is correct in the PDF summary?", ["Human Development Report - UNDP", "Human Development Report - WIPO", "Global Innovation Index - UNDP", "Global Gender Gap Report - UNCTAD"], 0, "The summary pairs HDR with UNDP and GII with WIPO. Publisher is a separate field from India's rank and the report's edition year.", 86)
        ],
        "checks": [{"pages": [86], "text": "The international rankings table has visibly overlapping rows and awkward publisher/date entries. Its text is retained as source evidence; the guide uses only clearly readable HDR/GII rows and does not certify every rank or publisher as current."}]
    },
    4: {
        "intro": "Economic numbers need labels. Before learning a percentage, ask: GDP or GSDP, real or nominal, which financial year, and provisional estimate or budget estimate? Approval of a transaction is also different from its completion.",
        "route": ["Banking and monetary institutions", "GDP, base year and estimate status", "Budget and Centre-State transfers"],
        "aid": "Write every economic figure as measure + period + unit + status. '4.3%' becomes 'Centre fiscal deficit, FY 2026-27 BE, % of GDP'. This is an editorial learning aid.",
        "points": [
            ("IDBI: approved, not completed", "The issue reports CCEA approval on 14 October 2026 for a 60.72% IDBI stake sale to 10955230 Canada Inc., a Fairfax group company, for about ₹52,878.08 crore; completion remains subject to further regulatory conditions.", [87]),
            ("The stake adds up", "Government of India: 30.48% to be sold; LIC: 30.24%. Together these form the approved 60.72% stake. The source describes remaining stakes as approximately 15% and 19%.", [87]),
            ("Real versus nominal GDP", "The provisional FY 2025-26 table lists real GDP ₹323.12 lakh crore with 7.7% growth and nominal GDP ₹346.36 lakh crore with 8.9% growth. They use different price bases.", [91]),
            ("A base-year revision", "The new GDP series is described as using 2022-23 instead of 2011-12. The same page later shows revised FY 2025-26 growth of 7.8%; keep this separate from the earlier provisional 7.7%.", [91]),
            ("Union Budget snapshot", "For FY 2026-27 BE, the issue gives a fiscal deficit of 4.3% of GDP, versus 4.4% in FY 2025-26 RE. It gives public capital expenditure of ₹12.2 lakh crore.", [113, 116]),
            ("Capital and revenue expenditure", "The source describes capital expenditure as creating assets or reducing liabilities; revenue expenditure includes salaries, subsidies and interest. FY 2026-27 growth over RE is given as 11.5% and 6.6% respectively.", [116]),
            ("Finance Commission basics", "The 16th Finance Commission is linked to Article 280, chaired by Dr Arvind Panagariya, and covers FY 2026-27 to FY 2030-31. The source retains a 41% States' vertical share of the divisible tax pool.", [93]),
            ("Vertical share versus State weights", "The issue's horizontal weights are income distance 42.5%, population 2011 17.5%, and 10% each for demographic performance, area, forest and contribution to GDP. These weights add to 100%; they are not the 41% vertical share.", [93])
        ],
        "comparison": {"title": "Four labels that change an economic number", "headers": ["Pair", "First meaning", "Second meaning"], "rows": [["Real / nominal", "Constant prices", "Current prices"], ["BE / RE", "Budget Estimate", "Revised Estimate"], ["Vertical / horizontal devolution", "Centre-States share of the pool", "Distribution across States"], ["Approval / completion", "Transaction authorised", "Regulatory conditions still matter"]], "pages": [87, 91, 93, 113]},
        "recall": [
            ("Reconstruct the IDBI stake from the two sellers.", "30.48% from the Government plus 30.24% from LIC equals 60.72%. The issue reports approval, not unconditional completion.", [87]),
            ("Why should the 7.7% and 7.8% GDP figures not be merged?", "The page labels the first as the provisional annual estimate and later shows a revised figure under a new-series discussion. Preserve each label instead of choosing one silently.", [91]),
            ("Compare real and nominal GDP using the page's own terms.", "Real GDP uses constant prices; nominal GDP uses current prices. Therefore the two rupee totals and growth rates are not interchangeable.", [91]),
            ("Explain 41% versus 100% in the Finance Commission notes.", "41% is the States' vertical share of the divisible pool. The horizontal criteria weights describe distribution across States and sum to 100%.", [93]),
            ("What makes a fiscal-deficit answer precise?", "Specify the government, financial year, estimate status and denominator: the issue's Centre FY 2026-27 BE is 4.3% of GDP, versus FY 2025-26 RE at 4.4%.", [113])
        ],
        "practice": [
            ("Which combination equals the source's approved 60.72% IDBI stake sale?", ["45.48% + 49.24%", "30.48% + 30.24%", "15% + 19%", "41% + 17.5%"], 1, "The stakes being sold are 30.48% from Government and 30.24% from LIC. Their earlier holdings and approximate residual holdings describe different stages.", 87),
            ("The new GDP series described in the issue uses which base year?", ["2004-05", "2011-12", "2022-23", "2026-27"], 2, "The issue identifies 2022-23 as the new base, replacing 2011-12. A base year is different from the year whose growth is estimated.", 91),
            ("Which figure is the States' vertical tax-devolution share in the 16th FC article?", ["41%", "42.5%", "17.5%", "100%"], 0, "41% is the vertical share. 42.5% and 17.5% are separate horizontal criteria weights, while all horizontal weights sum to 100%.", 93),
            ("Which statement correctly labels the issue's Union fiscal-deficit figure?", ["4.3% of State GSDP, FY 2025-26 RE", "4.4% of GDP, FY 2026-27 BE", "4.3 lakh crore, FY 2026-27", "4.3% of GDP, Centre, FY 2026-27 BE"], 3, "The source gives 4.3% of GDP for the Centre's FY 2026-27 Budget Estimate and 4.4% for FY 2025-26 Revised Estimate. Keep the unit and status.", 113)
        ],
        "checks": [{"pages": [91], "text": "The same page carries 7.7% provisional FY 2025-26 real GDP growth and 7.8% in a revised-estimates table under the new GDP series. Both are retained with their labels; no latest official estimate is asserted."}]
    },
    5: {
        "intro": "Make each technology story answer four questions: who built it, what it does, how it works, and what stage it reached. A flyby is different from a landing, and reactor criticality is different from commercial operation.",
        "route": ["Space missions: target and payload", "AI: data, compute and use", "Energy and defence: capability and stage"],
        "aid": "Use a mission passport: agency | target | payload | milestone. Draw separate boxes for demonstration, launch, criticality and full operation so the verbs do not blur together.",
        "points": [
            ("MMX target", "JAXA's MMX mission studies Phobos and Deimos and seeks to return at least 10 grams from Phobos. The issue reports an October 2026 launch, expected arrival in 2027 and sample delivery in 2031.", [121]),
            ("MMX instruments", "TENGOO provides imaging; OROCHI takes multi-wavelength images; LIDAR measures distance. MEGANE uses gamma rays and neutrons for elemental composition, while MIRS is an infrared spectrometer.", [121]),
            ("An international rover", "IDEFIX is the MMX rover jointly developed by CNES (France) and DLR (Germany). It assesses the surface before the spacecraft lands.", [121]),
            ("GAGAN's function", "GAGAN means GPS Aided GEO Augmented Navigation. ISRO and the Airports Authority of India developed the system to improve GPS accuracy and supply integrity information for navigation.", [121]),
            ("Compute near the data", "Pathfinder's orbital-data-centre model processes data on a satellite rather than sending all raw data to Earth. The source assigns satellite construction and hyperspectral imaging to Pixxel and the AI backbone to Sarvam.", [123]),
            ("Artemis II's purpose", "The article describes Artemis II as a crewed lunar flyby, not a Moon landing. It tests Orion's life support, communications, navigation, manual operation and re-entry protection.", [123]),
            ("Criticality is a milestone", "The issue reports first criticality of the 500 MWe PFBR at Kalpakkam, Tamil Nadu, on 6 April 2026. BHAVINI built it; criticality means the start of a sustained nuclear chain reaction.", [129]),
            ("Three AI Summit Sutras", "The India-AI Impact Summit 2026 at Bharat Mandapam, New Delhi, is guided by People, Planet and Progress. The source dates it to 16-21 February 2026 and separately lists seven thematic Chakras.", [129])
        ],
        "comparison": {"title": "Different missions, different success conditions", "headers": ["Mission/system", "Purpose", "Distinction to retain"], "rows": [["MMX", "Study Martian moons and return Phobos material", "Sample return, not crewed exploration"], ["Artemis II", "Crewed lunar flyby and system testing", "Flyby, not landing"], ["PFBR", "Fast-breeder nuclear-energy programme", "First criticality, not full commercial operation"], ["GAGAN", "Augment GPS navigation", "Navigation system, not a sample-return mission"]], "pages": [121, 123, 129]},
        "recall": [
            ("Give MMX's agency, two targets and sample target.", "JAXA; Phobos and Deimos; at least 10 grams returned from Phobos. The sampling moon must not be confused with the two moons being studied.", [121]),
            ("Distinguish LIDAR from MEGANE in this mission.", "LIDAR measures surface distance using laser pulses. MEGANE measures gamma rays and neutrons to infer elemental composition. They answer different scientific questions.", [121]),
            ("Explain an orbital data centre using the source's edge-computing analogy.", "Processing happens near the data's source on a satellite instead of sending all raw data to a distant Earth-based server. Pixxel supplies the satellite and imaging; Sarvam supplies the AI layer.", [123]),
            ("Why is 'Artemis II landed on the Moon' wrong for this article?", "The source describes a crewed lunar flyby to test systems and return safely. A mission toward and around the Moon is not a surface landing.", [123]),
            ("What can you infer from PFBR first criticality, and what should you not infer?", "A sustained chain reaction has begun. The article treats full operation as a later condition, so criticality alone does not establish commercial operation.", [129])
        ],
        "practice": [
            ("From which moon does the issue's MMX mission seek to return material?", ["Titan", "Europa", "Deimos only", "Phobos"], 3, "MMX studies Phobos and Deimos, but the stated sample-return target is Phobos, with at least 10 grams.", 121),
            ("Which GAGAN developer pair is given in the source?", ["ISRO and Airports Authority of India", "JAXA and BHAVINI", "CNES and DLR", "Pixxel and Sarvam"], 0, "ISRO and AAI developed GAGAN. CNES-DLR is the IDEFIX rover pair, and Pixxel-Sarvam is the orbital-computing collaboration.", 121),
            ("How does the source classify Artemis II?", ["Uncrewed Mars landing", "Crewed lunar flyby", "Crewed lunar surface landing", "Phobos sample-return flight"], 1, "The article explicitly calls it a crewed lunar flyby to test systems for travel beyond low Earth orbit and safe return, not a Moon landing.", 123),
            ("PFBR's first criticality most directly means what in the article?", ["All future reactors are commercially operational", "The reactor produces no chain reaction", "A sustained nuclear chain reaction has begun", "Its capacity is 500 megawatts thermal"], 2, "The page defines the criticality milestone as initiating a sustained chain reaction and gives capacity as 500 MWe (electrical). It does not equate that milestone with full commercial operation.", 129)
        ],
        "checks": []
    },
    6: {
        "intro": "Environmental reports are easiest to read by separating a measured value, a target and a projection. Always preserve the baseline year, the unit and exclusions. For wetlands, keep the place-state pair and treat the issue's changing tally as dated information.",
        "route": ["Climate: actuals, targets, baselines", "Wetlands: names and locations", "COP outcomes: mitigation, adaptation, finance"],
        "aid": "For a climate number ask 'relative to when?' and 'what is excluded?'. For a wetland, first recall the State, then the date. This is an editorial reading aid.",
        "points": [
            ("A small difference is not proof of a peak", "The issue's Emissions Gap Report article gives global emissions of 58.4 GtCO₂e in 2025 against a revised 58.5 in 2024, but says uncertainty prevents confirmation of a decline or peak.", [144]),
            ("Absolute and per-capita emissions", "The same article gives India 4.5 billion tonnes CO₂e in 2025 and 3.1 tonnes per person against a 6.4-tonne global average. Both Indian figures exclude land use, land-use change and forestry (LULUCF).", [144]),
            ("Reductions need a baseline", "The source's pathway requires global reductions of 18% by 2030, 45% by 2035 and 69% by 2040 against 2025 levels. These are pathway requirements, not claimed achieved reductions.", [144]),
            ("Dated Ramsar tally", "The issue reports Sauj Lake and Sukhna Wetland additions on 15 October 2026 and a total of 103 Indian Ramsar sites. This is the issue's snapshot, not a live total.", [144]),
            ("UP wetland pair", "The map places Sauj Lake in Mainpuri and Jai Prakash Narayan Bird Sanctuary (Surha Tal) in Uttar Pradesh. It lists 14 UP entries; its dates differ from the prose and are flagged.", [145]),
            ("Largest, smallest and first", "The map's fact box identifies Sundarbans, West Bengal, as India's largest Ramsar wetland; Vembannur Wetland Complex, Tamil Nadu, as smallest; Chilika and Keoladeo as the first Indian sites in 1981.", [145]),
            ("COP30 setting", "COP30 is placed in Belém, Brazil, on 10-22 November 2025. The article describes an implementation focus and a four-step action cycle: Coordinate, Measure, Showcase, Scale.", [156]),
            ("A target with two years", "The Belém 4x Pledge described in the article targets quadrupling sustainable-fuel use by 2035 relative to 2024, with progress tracked by the IEA. It is a pledge, not a completed result.", [156])
        ],
        "comparison": {"title": "Actual, target and projection", "headers": ["Kind of statement", "Example from the issue", "Reading rule"], "rows": [["Measured/estimated actual", "58.4 GtCO₂e in 2025", "Keep uncertainty and revised comparison"], ["Pathway requirement", "18% reduction by 2030 from 2025", "A requirement is not an achievement"], ["Pledge", "4x sustainable fuels by 2035 from 2024", "Keep both target year and baseline"], ["Dated inventory", "103 Ramsar sites, October 2026", "Do not call it today's count"]], "pages": [144, 156]},
        "recall": [
            ("Why does 58.4 versus 58.5 not establish an emissions peak?", "The source explicitly says uncertainty prevents confirmation of a decline or peak. A tiny difference between estimates is not enough to discard that caveat.", [144]),
            ("Explain how India's large total and lower per-capita figure can coexist.", "Total emissions and emissions per person measure different things. The source gives 4.5 billion tonnes overall and 3.1 tonnes per person, excluding LULUCF; do not compare those numbers without their units.", [144]),
            ("Reconstruct the three global reduction requirements with their baseline.", "18% by 2030, 45% by 2035 and 69% by 2040, all against 2025. They describe a pathway, not cuts already achieved.", [144]),
            ("Recover the COP30 action cycle in order.", "Coordinate → Measure → Showcase → Scale. The source presents this as its implementation activation cycle.", [156]),
            ("What are the target and baseline in the Belém 4x Pledge?", "Quadruple sustainable-fuel use by 2035 relative to 2024. IEA tracking is the monitoring detail, not the baseline year.", [156])
        ],
        "practice": [
            ("Which caveat accompanies the issue's 58.4 versus 58.5 GtCO₂e comparison?", ["A permanent emissions peak is proven", "Land use is the only emission source", "Uncertainty prevents confirming a decline or peak", "The figures are per-capita tonnes"], 2, "The article explicitly retains uncertainty. The values are global totals in gigatonnes CO₂-equivalent, not per-person values.", 144),
            ("Which map pair is printed for Sauj Lake?", ["Mainpuri - Uttar Pradesh", "Ballia - Bihar", "Chandigarh - Punjab", "Mainpuri - Tamil Nadu"], 0, "The map lists Sauj Lake (Mainpuri) under Uttar Pradesh. Surha Tal is the separate Ballia-related entry in the one-liners.", 145),
            ("Which sequence matches COP30's action cycle in the issue?", ["Scale, Coordinate, Measure, Showcase", "Measure, Scale, Coordinate, Showcase", "Showcase, Measure, Scale, Coordinate", "Coordinate, Measure, Showcase, Scale"], 3, "The article gives Coordinate → Measure → Showcase → Scale. The order moves from organising action to tracking, displaying and expanding it.", 156),
            ("What baseline belongs to the source's Belém 4x sustainable-fuels target for 2035?", ["2005", "2024", "2025", "2030"], 1, "The pledge seeks a fourfold increase by 2035 relative to 2024. Baseline and target year are essential parts of the statement.", 156)
        ],
        "checks": [{"pages": [144, 145], "text": "The prose says Sauj Lake and Sukhna were added on 15 October 2026, but the map labels Sauj 18 June 2026 and Sukhna 16 March 2026. The map also labels Surha Tal 19 January 2025 while p. 5 describes its 100th-site news in June 2026. These dates are preserved and not used as unqualified test keys."}]
    },
    7: {
        "intro": "Make a UP map in your head: event → district → purpose. Read the state budget separately from the economic survey: a budget proposes future spending, while the survey describes estimates and trends for earlier years.",
        "route": ["Districts and state initiatives", "Procurement: crop, MSP, dates", "Budget versus survey"],
        "aid": "Keep two notebooks lines for money: 'Budget = plan' and 'Survey = reported economy'. Always add the financial year and estimate status. This is an editorial learning aid.",
        "points": [
            ("Place-event pair", "The issue places the Wings Over Ganga air show at Namo Ghat, Varanasi, on 22, 24 and 25 October 2026, and the 50th India Carpet Expo at Bhadohi on 4 October 2026.", [157]),
            ("Two paddy grades", "UP's reported FY 2026-27 paddy procurement MSPs are ₹2,441 per quintal for common paddy and ₹2,461 for Grade A. The procurement target is 65 lakh metric tonnes.", [157]),
            ("Two procurement windows", "The source gives western UP's paddy window as 12 October 2026-15 February 2027 and eastern UP's as 1 November 2026-28 February 2027, with payment within 48 hours.", [157]),
            ("UP-AIM scope", "The reported UP Artificial Intelligence Mission has a proposed ₹2,000 crore outlay for FY 2026-27 to FY 2030-31, with ₹225 crore for FY 2026-27, district AI centres in all 75 districts and a target to train 5 lakh youth.", [157]),
            ("Budget balances", "For FY 2026-27, the budget discussion estimates a revenue surplus of ₹64,458 crore (1.6% of GSDP), a fiscal deficit of ₹1,18,481 crore (3%) and a primary deficit of ₹49,560 crore (1.2%).", [165]),
            ("Receipts and State GST", "The budget article estimates revenue receipts of ₹7,28,928 crore and own tax revenue of ₹3,34,491 crore. State GST is its largest own-tax source, budgeted at ₹1,49,956 crore.", [165]),
            ("Survey's sector mix", "The economic survey gives the FY 2024-25 primary-secondary-tertiary shares as 25.8%, 27.2% and 47.0%. These are broad sectors, not individual subsectors.", [166]),
            ("Income labels matter", "The survey gives FY 2024-25 net per-capita income as ₹1,09,844 and gross per-capita income as ₹1,26,304. Its March 2026 population estimate is 25.19 crore; this is an estimate, not a fresh Census count.", [168])
        ],
        "comparison": {"title": "Reading the state balances", "headers": ["Measure, FY 2026-27", "Issue's amount/ratio", "Meaning in the article"], "rows": [["Revenue surplus", "₹64,458 crore; 1.6% of GSDP", "Revenue receipts exceed revenue expenditure"], ["Fiscal deficit", "₹1,18,481 crore; 3% of GSDP", "Overall financing gap"], ["Primary deficit", "₹49,560 crore; 1.2% of GSDP", "Gap before interest payments"]], "pages": [165]},
        "recall": [
            ("Reconstruct the two UP paddy MSPs with the unit.", "Common ₹2,441/quintal; Grade A ₹2,461/quintal, for the reported 2026-27 procurement policy. Grade A is ₹20 higher; the unit is per quintal, not per tonne.", [157]),
            ("How do the western and eastern procurement windows differ?", "West starts 12 October 2026 and ends 15 February 2027; east starts 1 November 2026 and ends 28 February 2027. Retain the region with each date pair.", [157]),
            ("Why can a state have a revenue surplus and a fiscal deficit?", "The revenue account can be in surplus while the broader budget still requires financing, including for capital spending. The issue itself reports a revenue surplus and a 3%-of-GSDP fiscal deficit together.", [165]),
            ("Which is the largest broad sector in the survey's 2024-25 mix?", "The tertiary sector at 47.0%, against 27.2% secondary and 25.8% primary. Broad-sector shares should not be substituted for a manufacturing-only share.", [166]),
            ("Which qualifications belong to the population and income figures?", "Population 25.19 crore is a March 2026 estimate. ₹1,09,844 is net per-capita income for FY 2024-25; ₹1,26,304 is the gross figure.", [168])
        ],
        "practice": [
            ("Which UP paddy MSP pair is printed for the 2026-27 policy?", ["Common ₹2,461; Grade A ₹2,441", "Common ₹2,441; Grade A ₹2,461", "Common ₹2,410; Grade A ₹2,900", "Common ₹4,023; Grade A ₹4,073"], 1, "The paddy pair is ₹2,441 and ₹2,461 per quintal. The other figures on the page concern maize/bajra and jowar, so crop labels matter.", 157),
            ("Which venue-event pair appears in the UP chapter?", ["Namo Ghat - India Carpet Expo", "Bhadohi - Wings Over Ganga", "Namo Ghat, Varanasi - Wings Over Ganga", "Bodh Gaya - India Carpet Expo"], 2, "Wings Over Ganga is the Varanasi air show at Namo Ghat. Bhadohi is the separate India Carpet Expo location.", 157),
            ("What is the source's UP fiscal-deficit target for FY 2026-27?", ["1.6% of GDP", "4.3% of GSDP", "1.2% of GDP", "3% of GSDP"], 3, "The State fiscal deficit is 3% of GSDP. 1.6% is the revenue-surplus ratio and 1.2% the primary-deficit ratio; 4.3% is the Union figure in another chapter.", 165),
            ("Which figure is net per-capita income in the UP survey for FY 2024-25?", ["₹1,09,844", "₹1,26,304", "₹76,490", "₹69,321"], 0, "₹1,09,844 is net per-capita income; ₹1,26,304 is gross. ₹76,490 and ₹69,321 belong to Bihar's per-capita GSDP and NSDP figures.", 168)
        ],
        "checks": [{"pages": [164, 165], "text": "The UP budget table's row labels and prose do not align cleanly: ₹1,77,744.12 crore appears next to 'Interest Payments' in the table, while prose describes about ₹1,77,744 crore as capital outlay. The evidence is retained; do not memorise that table row as an unqualified interest-payment figure."}]
    },
    8: {
        "intro": "Bihar remains in the supplied book even for a UPPSC reader. Use it for State-to-State comparisons, but keep proposed investments, July draft incentives and actual budget figures in separate boxes.",
        "route": ["Digital infrastructure: existing and proposed", "Budget: size and financing", "Survey: growth and district economy"],
        "aid": "Place each policy number under 'operational', 'proposed' or 'draft'. An investment letter of intent is not installed capacity. This is an editorial learning aid.",
        "points": [
            ("Data centre versus AI factory", "The issue reports a ₹400 crore CtrlS data centre at Patliputra, Patna, with initial IT load of 12 MW, inaugurated on 13 October 2026. A separate LoI concerns a proposed ₹10,000 crore, 150 MW AI factory in Bodh Gaya.", [169]),
            ("A dashboard's scope", "The Sankalp Dashboard, launched alongside the Samanvay Portal on 13 October 2026, is described as bringing work of all 48 Bihar departments onto one platform.", [169]),
            ("MSME draft qualifier", "The chapter's MSME targets and detailed subsidies are explicitly from the July 2026 draft: formalise 1 crore MSMEs, generate over 1 crore jobs and train 1 lakh MSMEs annually. Do not silently call all draft incentives final.", [169]),
            ("Budget size has boundaries", "The FY 2026-27 budget discussion gives ₹3,47,589.76 crore including debt repayment, versus about ₹3,24,925 crore excluding it. The separate Appropriation Bill gross figure is ₹3,53,045.15 crore.", [174]),
            ("Fiscal balance", "The issue's Bihar FY 2026-27 target is a ₹1,143.19 crore revenue surplus and ₹39,111.80 crore fiscal deficit, or 2.99% of GSDP. Projected current-price GSDP is ₹13.09 lakh crore.", [174]),
            ("Saat Nischay-3 period", "The development roadmap is for 2025-2030. The agriculture roadmap discussed separately is the Fourth Agriculture Roadmap, 2023-2028.", [175]),
            ("Same year, two growth rates", "For FY 2024-25 quick estimates, the Bihar survey reports 8.6% constant-price GSDP growth and 13.1% current-price growth; the constant-price series uses base year 2011-12.", [176]),
            ("Per-capita and district comparisons", "FY 2024-25 per-capita GSDP at current prices is ₹76,490, while per-capita NSDP is ₹69,321. The survey names Patna, Begusarai and Munger as the top three GDDP districts in that order.", [174, 175, 176])
        ],
        "comparison": {"title": "Three distinctions in the Bihar chapter", "headers": ["Pair", "First item", "Second item"], "rows": [["Existing / proposed digital capacity", "Patna data centre: 12 MW initial IT load", "Bodh Gaya AI factory LoI: 150 MW proposed"], ["Budget including / excluding repayment", "₹3,47,589.76 crore", "About ₹3,24,925 crore"], ["Current / constant-price growth, FY 2024-25 QE", "13.1%", "8.6%, base 2011-12"]], "pages": [169, 174, 176]},
        "recall": [
            ("Why must the two CtrlS capacities be kept separate?", "12 MW is the Patna data centre's initial IT load. 150 MW is the proposed Bodh Gaya AI factory under an LoI. Different projects and stages cannot be merged.", [169]),
            ("What qualification belongs to the MSME incentive list?", "The source explicitly says those details come from the July 2026 draft. A policy launch paragraph does not make every draft detail an enacted rule.", [169]),
            ("Explain the three budget totals without choosing one as the only correct number.", "₹3,47,589.76 crore includes debt repayment; about ₹3,24,925 crore excludes it; ₹3,53,045.15 crore is gross appropriation. They use different coverage.", [174]),
            ("Separate the periods of Saat Nischay-3 and the agriculture roadmap.", "Saat Nischay-3 covers 2025-2030; the Fourth Agriculture Roadmap covers 2023-2028. Similar roadmap language does not mean the same dates.", [175]),
            ("Why are Bihar's 8.6% and 13.1% not conflicting here?", "They refer to constant-price and current-price GSDP growth respectively for FY 2024-25 quick estimates. The price basis changes the measure.", [176])
        ],
        "practice": [
            ("Which statement preserves the source's Bihar digital-infrastructure stages?", ["Both projects are operational at 150 MW", "The Patna centre is only a letter of intent", "Bodh Gaya's 12 MW factory is completed", "Patna has 12 MW initial IT load; Bodh Gaya's 150 MW AI factory is proposed under an LoI"], 3, "The article separates an inaugurated Patna data centre from a proposed Bodh Gaya project. Keep location, capacity and stage together.", 169),
            ("How are the detailed Bihar MSME targets/incentives qualified on p. 169?", ["July 2026 draft", "Final Census results", "Union Budget actual expenditure", "A verified UPPSC answer key"], 0, "The note explicitly says the details are from the July 2026 draft. The guide retains that qualifier instead of presenting every incentive as final.", 169),
            ("What period belongs to Saat Nischay-3 in the source?", ["2023-2028", "2025-2030", "2026-2031", "2011-2012"], 1, "Saat Nischay-3 covers 2025-2030. The 2023-2028 period belongs to the separate Fourth Agriculture Roadmap.", 175),
            ("Which growth pair is reported for Bihar FY 2024-25 quick estimates?", ["8.6% current; 13.1% constant", "7.7% constant; 8.9% current", "8.6% constant; 13.1% current", "13.1% constant; 13.1% current"], 2, "The Bihar survey gives 8.6% at constant 2011-12 prices and 13.1% at current prices. The estimate status and price basis must accompany the figures.", 176)
        ],
        "checks": [{"pages": [169, 174], "text": "MSME incentive details retain the source's 'July 2026 draft' label. Bihar budget totals retain their including/excluding debt-repayment and gross-appropriation definitions; they are not treated as interchangeable totals."}]
    },
    9: {
        "intro": "Short news is best learned in pairs: person-post, book-author, exercise-partner and day-theme. Keep only one kind of pair on each flashcard so neighbouring table rows do not get mixed.",
        "route": ["People, places and appointments", "Awards, books and creators", "Exercises, dates and themes"],
        "aid": "Turn each pair around: read the book and recall the author, then read the author and recall the book. Reverse recall reveals weak matches. This is a learning aid, not an extra source claim.",
        "points": [
            ("PMO's author", "PMO: Prime Minister's Office Through the Years is attributed to Himanshu Roy. Match the full title to the author.", [220]),
            ("An autobiography pair", "Triumph of the Indian Republic: My Life, My Struggles is Ram Nath Kovind's autobiography; the page also lists the Hindi title Bharatiya Ganatantra Ki Vijaygatha, Mera Jeevan, Mera Sangharsh.", [220]),
            ("A judicial succession", "The issue dates Surya Kant's oath as the 53rd Chief Justice of India to 24 November 2025, succeeding B.R. Gavai. It lists 9 February 2027 as his due retirement date; these are the issue's dated office entries.", [182]),
            ("Compassion and murals", "Karuna: The Power of Compassion is attributed to Kailash Satyarthi; Tides of Time: Bharat's History through Murals in Parliament to Sudha Murty.", [220]),
            ("Audit and biography", "When Audit Matters: CAG Interventions That Made a Difference is edited by Vinod Rai; The Library Man of India: The Story of P.N. Panicker is by P.P. Sathyan.", [220]),
            ("A named appointment", "The issue reports Sudhakar Dalela as India's next Ambassador to Nepal on 16 October 2026. This is a dated appointment item rather than a claim about today's incumbent.", [178]),
            ("An award and a field", "The issue names Toby Kiers for the Tyler Prize for Environmental Achievement in January 2026, for research on underground fungal networks. It separately lists Graça Machel for the Indira Gandhi Prize for Peace, Disarmament and Development 2025.", [203]),
            ("Naval exercise partners", "The exercise table pairs SIMBEX with Singapore-India at Visakhapatnam, VARUNA with India-France at Toulon, and SLINEX with India-Sri Lanka at Visakhapatnam. Keep the exercise, partners and location together.", [213])
        ],
        "comparison": {"title": "The role is part of the book-author match", "headers": ["Book", "Name in the source", "Role/form"], "rows": [["PMO: Prime Minister's Office Through the Years", "Himanshu Roy", "Author"], ["When Audit Matters", "Vinod Rai", "Editor"], ["Triumph of the Indian Republic", "Ram Nath Kovind", "Autobiography"], ["Belonging: A Journey of Love", "Sonia Gandhi", "Memoir"]], "pages": [220]},
        "recall": [
            ("Who wrote PMO, and who edited When Audit Matters?", "Himanshu Roy is listed as author of PMO: Prime Minister's Office Through the Years; Vinod Rai as editor of When Audit Matters. The role is part of the match.", [220]),
            ("Match SIMBEX, VARUNA and SLINEX to India's partners.", "SIMBEX - Singapore; VARUNA - France; SLINEX - Sri Lanka. The source places SIMBEX and SLINEX at Visakhapatnam, and VARUNA at Toulon in France.", [213]),
            ("Which pair separates Kovind's autobiography and Sonia Gandhi's memoir?", "Kovind: Triumph of the Indian Republic: My Life, My Struggles. Sonia Gandhi: Belonging: A Journey of Love. The subtitles belong to different books.", [220]),
            ("Distinguish the Tyler Prize and Indira Gandhi Prize entries.", "Toby Kiers - Tyler Prize for Environmental Achievement, research on underground fungal networks; Graça Machel - Indira Gandhi Prize for Peace, Disarmament and Development 2025. Keep the award's year with its name.", [203]),
            ("How should an appointment flashcard be qualified?", "Attach post, person and source date. Here it is Sudhakar Dalela, next Ambassador to Nepal, 16 October 2026; this does not independently verify the current office-holder.", [178])
        ],
        "practice": [
            ("Who is credited with PMO: Prime Minister's Office Through the Years?", ["Vinod Rai", "Himanshu Roy", "Vijay Goel", "P.P. Sathyan"], 1, "Himanshu Roy is credited as PMO's author. Vinod Rai is the editor of When Audit Matters and P.P. Sathyan wrote The Library Man of India.", 220),
            ("Which naval exercise-partner pair matches the source table?", ["VARUNA - Singapore", "SIMBEX - France", "SLINEX - Sri Lanka", "SLINEX - Australia"], 2, "SLINEX pairs India with Sri Lanka. VARUNA pairs India with France and SIMBEX with Singapore; similar naval settings do not make the partners interchangeable.", 213),
            ("Which contribution is associated with Toby Kiers in the issue?", ["A CAG audit compilation", "Naval search-and-rescue drills", "An autobiography of a former President", "Research on underground fungal networks"], 3, "The Tyler Prize entry recognises Toby Kiers for research on underground fungal networks. The award's environmental field helps distinguish it from books and exercises.", 203),
            ("Which dated judicial succession is reported in the issue?", ["Surya Kant succeeded B.R. Gavai as 53rd CJI", "B.R. Gavai succeeded Surya Kant as 53rd CJI", "Vinod Rai became 53rd CJI", "Himanshu Roy became 53rd CJI"], 0, "The appointment list records Surya Kant's oath as the 53rd Chief Justice on 24 November 2025 after B.R. Gavai. Keep the ordinal, succession and date together.", 182)
        ],
        "checks": [{"pages": [213], "text": "Some rows in the exercise table overlap in the PDF. The guide uses the clearly legible SIMBEX, VARUNA and SLINEX rows; consult the original page before learning other row-to-location matches."}]
    },
    10: {
        "intro": "Start every sports note with the competition, edition and category. Men's and women's tournaments, T20 and ODI formats, and winners versus individual awards are different rows. Use the issue's result tables as dated source claims.",
        "route": ["Competition, edition and host", "Champion and runner-up", "Individual awards and future hosts"],
        "aid": "Use a four-cell scorecard: event | host/date | champion | individual award. Test one cell at a time, then reconstruct the whole row. This is an editorial memory aid.",
        "points": [
            ("Men's T20 World Cup", "The issue's 10th ICC Men's T20 World Cup is co-hosted by India and Sri Lanka from 7 February to 8 March 2026, with 20 teams and 55 matches; it reports India as champion and Sanju Samson as Player of the Tournament.", [222]),
            ("Women's T20 World Cup", "The source places the 10th ICC Women's T20 World Cup in England and Wales, 12 June-5 July 2026, expanded to 12 teams and 33 matches; it reports Australia champion and Beth Mooney Player of the Tournament.", [221]),
            ("A different women's World Cup", "The 2025 ICC Women's Cricket World Cup article reports India champion and South Africa runner-up, with the final at DY Patil Stadium, Navi Mumbai. Do not merge this with the 2026 T20 event.", [222]),
            ("Two Indian youth/tournament results", "The source reports India as U-19 World Cup 2026 champion (record sixth title), with Vaibhav Suryavanshi Player of the Series; WPL 2026 champion is Royal Challengers Bengaluru, runner-up Delhi Capitals.", [222]),
            ("Asian Games identity", "The 20th Asian Games are placed at Aichi-Nagoya, Japan, 19 September-4 October 2026. The mascot is Honohon and slogan Imagine One Asia; the issue reports India fourth with 85 medals, including 21 gold.", [237]),
            ("Commonwealth identity", "The issue's Glasgow 2026 Commonwealth Games use the unicorn mascot Finnie and a compact 10-sport model. It reports India fourth with 39 medals: 13 gold, 17 silver and nine bronze.", [237, 238]),
            ("Expanded FIFA format", "The 2026 men's FIFA World Cup is described as co-hosted by Canada, Mexico and the USA, with 48 teams and 104 matches across 16 host cities. Mascots are Maple (Canada), Zayu (Mexico) and Clutch (USA).", [238]),
            ("Future host pairs", "The issue lists the 2028 Olympics at Los Angeles, the 2032 Olympics at Brisbane, the 2030 Asian Games at Doha and the 2034 Asian Games at Riyadh. These remain the issue's future-host entries.", [239])
        ],
        "comparison": {"title": "Keep the cricket tournaments apart", "headers": ["Competition in the issue", "Host", "Reported champion / main individual award"], "rows": [["Men's T20 World Cup 2026", "India and Sri Lanka", "India / Sanju Samson"], ["Women's T20 World Cup 2026", "England and Wales", "Australia / Beth Mooney"], ["Women's Cricket World Cup 2025", "India", "India / separate 2025 event"], ["Men's U-19 World Cup 2026", "Zimbabwe and Namibia", "India / Vaibhav Suryavanshi"]], "pages": [221, 222]},
        "recall": [
            ("Reconstruct the men's T20 event without borrowing a women's-event detail.", "India and Sri Lanka; 7 February-8 March 2026; 20 teams and 55 matches; reported champion India; Player of the Tournament Sanju Samson.", [222]),
            ("Why do India and Australia both appear as women's World Cup champions in these pages?", "They are different competitions and years: India is the source's 2025 Women's Cricket World Cup champion, while Australia is its 2026 Women's T20 World Cup champion.", [221, 222]),
            ("Distinguish Honohon from Finnie.", "Honohon is the Aichi-Nagoya Asian Games mascot; Finnie is the Glasgow Commonwealth Games unicorn. Attach the event and host to each name.", [237]),
            ("Recover the three FIFA host-mascot pairs.", "Canada - Maple; Mexico - Zayu; USA - Clutch. The source also gives 48 teams and 104 matches, a separate format fact.", [238]),
            ("Pair the next two Olympic host cities listed in the issue with their years.", "Los Angeles - 2028; Brisbane - 2032. Keep these future-host listings separate from Asian Games hosts Doha 2030 and Riyadh 2034.", [239])
        ],
        "practice": [
            ("Which host pair belongs to the issue's 2026 ICC Men's T20 World Cup?", ["England and Wales", "Zimbabwe and Namibia", "Canada and Mexico", "India and Sri Lanka"], 3, "India and Sri Lanka host the men's T20 event. England-Wales is the women's T20 event and Zimbabwe-Namibia the men's U-19 event.", 222),
            ("Which mascot-event pair is printed correctly?", ["Finnie - Glasgow Commonwealth Games", "Finnie - Aichi-Nagoya Asian Games", "Honohon - FIFA World Cup", "Clutch - Asian Games"], 0, "Finnie is the Commonwealth Games unicorn; Honohon belongs to Aichi-Nagoya. Clutch is the USA FIFA mascot.", 237),
            ("Which team/match expansion describes the 2026 men's FIFA World Cup in the issue?", ["32 teams; 64 matches", "48 teams; 104 matches", "20 teams; 55 matches", "12 teams; 33 matches"], 1, "The issue gives 48 teams and 104 matches for FIFA 2026. The other figures describe earlier FIFA format or different cricket tournaments.", 238),
            ("Which future Olympic host pair appears in the source?", ["Doha 2028; Riyadh 2032", "Brisbane 2028; Los Angeles 2032", "Los Angeles 2028; Brisbane 2032", "Ahmedabad 2028; Doha 2032"], 2, "The future-events list pairs Los Angeles with the 2028 Olympics and Brisbane with 2032. Doha and Riyadh are Asian Games hosts in separate years.", 239)
        ],
        "checks": [{"pages": [239], "text": "The Messi item reports an international-retirement announcement on 31 August 2026 and a last match in October 2026. Both source statements are retained; the guide does not turn them into a single independently verified retirement date."}]
    }
}
