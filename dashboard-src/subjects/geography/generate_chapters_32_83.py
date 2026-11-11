import json, re, os
from collections import defaultdict, Counter

def load_data():
    with open("dashboard-src/subjects/geography/accurate_chapter_ranges.json", encoding="utf-8") as f:
        ranges = json.load(f)
    with open("dashboard-src/subjects/geography/parsed_uppsc_questions.json", encoding="utf-8") as f:
        qs = json.load(f)
    with open("dashboard-src/subjects/geography/raw_pages.json", encoding="utf-8") as f:
        pages = json.load(f)
    with open("dashboard-src/subjects/geography/repeated_facts.json", encoding="utf-8") as f:
        repeated = json.load(f)
    return ranges, qs, pages, repeated

# Comprehensive Hindi glossary for World Geography
HINDI_TERMS = [
    ("International Date Line", "अंतर्राष्ट्रीय तिथि रेखा [International Date Line]"),
    ("Prime Meridian", "प्रधान मध्याह्न रेखा [Prime Meridian]"),
    ("Tropic of Cancer", "कर्क रेखा [Tropic of Cancer]"),
    ("Tropic of Capricorn", "मकर रेखा [Tropic of Capricorn]"),
    ("Continental Drift", "महाद्वीपीय विस्थापन [Continental Drift]"),
    ("Plate Tectonics", "प्लेट विवर्तनिकी [Plate Tectonics]"),
    ("Solar System", "सौर मंडल [Solar System]"),
    ("Milky Way", "मंदाकिनी [Milky Way Galaxy]"),
    ("Big Bang", "महाविस्फोट सिद्धांत [Big Bang Theory]"),
    ("Light Year", "प्रकाश वर्ष [Light Year]"),
    ("Black Hole", "कृष्ण विवर [Black Hole]"),
    ("Kuiper Belt", "काइपर घेरा [Kuiper Belt]"),
    ("Asteroid", "क्षुद्रग्रह [Asteroid]"),
    ("Asteroids", "क्षुद्रग्रह [Asteroids]"),
    ("Meteorite", "उल्कापिंड [Meteorite]"),
    ("Meteorites", "उल्कापिंड [Meteorites]"),
    ("Meteor", "उल्का [Meteor]"),
    ("Comet", "धूमकेतु [Comet]"),
    ("Comets", "धूमकेतु [Comets]"),
    ("Solstice", "अयनांत [Solstice]"),
    ("Equinox", "विषुव [Equinox]"),
    ("Latitude", "अक्षांश [Latitude]"),
    ("Latitudes", "अक्षांश [Latitudes]"),
    ("Longitude", "देशांतर [Longitude]"),
    ("Longitudes", "देशांतर [Longitudes]"),
    ("Igneous Rock", "आग्नेय शैल [Igneous Rock]"),
    ("Igneous Rocks", "आग्नेय शैल [Igneous Rocks]"),
    ("Sedimentary Rock", "अवसादी शैल [Sedimentary Rock]"),
    ("Sedimentary Rocks", "अवसादी शैल [Sedimentary Rocks]"),
    ("Metamorphic Rock", "कायांतरित शैल [Metamorphic Rock]"),
    ("Metamorphic Rocks", "कायांतरित शैल [Metamorphic Rocks]"),
    ("Volcano", "ज्वालामुखी [Volcano]"),
    ("Volcanoes", "ज्वालामुखी [Volcanoes]"),
    ("Volcanic", "ज्वालामुखीय [Volcanic]"),
    ("Ring of Fire", "अग्नि वलय [Ring of Fire]"),
    ("Active Volcano", "सक्रिय ज्वालामुखी [Active Volcano]"),
    ("Dormant Volcano", "प्रसुप्त ज्वालामुखी [Dormant Volcano]"),
    ("Earthquake", "भूकंप [Earthquake]"),
    ("Earthquakes", "भूकंप [Earthquakes]"),
    ("Seismic Waves", "भूकंपीय तरंगें [Seismic Waves]"),
    ("Seismograph", "भूकंपलेखी [Seismograph]"),
    ("Epicenter", "अधिकेंद्र [Epicenter]"),
    ("Hypocenter", "भूकंप मूल [Hypocenter]"),
    ("Tsunami", "सुनामी [Tsunami]"),
    ("Fold Mountain", "वलित पर्वत [Fold Mountain]"),
    ("Fold Mountains", "वलित पर्वत [Fold Mountains]"),
    ("Block Mountain", "भ्रंशोत्थ पर्वत [Block Mountain]"),
    ("Block Mountains", "भ्रंशोत्थ पर्वत [Block Mountains]"),
    ("Plateau", "पठार [Plateau]"),
    ("Plateaus", "पठार [Plateaus]"),
    ("Rift Valley", "भ्रंश घाटी [Rift Valley]"),
    ("Rift Valleys", "भ्रंश घाटियां [Rift Valleys]"),
    ("Valley", "घाटी [Valley]"),
    ("Valleys", "घाटियां [Valleys]"),
    ("Desert", "मरुस्थल [Desert]"),
    ("Deserts", "मरुस्थल [Deserts]"),
    ("Grassland", "घास का मैदान [Grassland]"),
    ("Grasslands", "घास के मैदान [Grasslands]"),
    ("Savanna", "सवाना घास मैदान [Savanna]"),
    ("Steppe", "स्टेपी घास मैदान [Steppe]"),
    ("Prairies", "प्रेयरी घास मैदान [Prairies]"),
    ("Pampas", "पंपास घास मैदान [Pampas]"),
    ("Veld", "वेल्ड घास मैदान [Veld]"),
    ("Downs", "डाउन्स घास मैदान [Downs]"),
    ("Llanos", "लानोस घास मैदान [Llanos]"),
    ("Campos", "कंपोस घास मैदान [Campos]"),
    ("Land-locked", "स्थल-रुद्ध [Land-locked]"),
    ("Landlocked", "स्थल-रुद्ध [Landlocked]"),
    ("Hydrosphere", "जलमंडल [Hydrosphere]"),
    ("Ocean Currents", "महासागरीय जलधाराएं [Ocean Currents]"),
    ("Ocean Current", "महासागरीय जलधारा [Ocean Current]"),
    ("Warm Current", "गर्म जलधारा [Warm Current]"),
    ("Cold Current", "ठंडी जलधारा [Cold Current]"),
    ("Gulf Stream", "गल्फ स्ट्रीम [Gulf Stream]"),
    ("Kuroshio", "क्यूरोशियो जलधारा [Kuroshio Current]"),
    ("Oyashio", "ओयाशियो जलधारा [Oyashio Current]"),
    ("Labrador Current", "लेब्राडोर जलधारा [Labrador Current]"),
    ("Benguela Current", "बेंगुएला जलधारा [Benguela Current]"),
    ("Humboldt Current", "हम्बोल्ट / पेरू जलधारा [Humboldt Current]"),
    ("Canary Current", "कनारी जलधारा [Canary Current]"),
    ("Salinity", "लवणता [Salinity]"),
    ("Tides", "ज्वार-भाटा [Tides]"),
    ("Tide", "ज्वार-भाटा [Tide]"),
    ("Spring Tide", "दीर्घ ज्वार [Spring Tide]"),
    ("Neap Tide", "लघु ज्वार [Neap Tide]"),
    ("Oceanic Trench", "महासागरीय गर्त [Oceanic Trench]"),
    ("Oceanic Trenches", "महासागरीय गर्त [Oceanic Trenches]"),
    ("Continental Shelf", "महाद्वीपीय मग्नतट [Continental Shelf]"),
    ("Continental Slope", "महाद्वीपीय मग्नढाल [Continental Slope]"),
    ("Abyssal Plain", "गंभीर सागरीय मैदान [Abyssal Plain]"),
    ("Mid-Oceanic Ridge", "मध्य-महासागरीय कटक [Mid-Oceanic Ridge]"),
    ("Coral Reef", "प्रवाल भित्ति [Coral Reef]"),
    ("Coral Reefs", "प्रवाल भित्ति [Coral Reefs]"),
    ("Great Barrier Reef", "ग्रेट बैरियर रीफ [Great Barrier Reef]"),
    ("Atoll", "वलयाकार प्रवाल भित्ति / एटोल [Atoll]"),
    ("Delta", "डेल्टा [Delta]"),
    ("Estuary", "ज्वारनदमुख [Estuary]"),
    ("Meander", "विसर्प [Meander]"),
    ("Oxbow Lake", "गोखुर झील [Oxbow Lake]"),
    ("Waterfall", "जलप्रपात [Waterfall]"),
    ("Waterfalls", "जलप्रपात [Waterfalls]"),
    ("Strait", "जलडमरूमध्य [Strait]"),
    ("Straits", "जलडमरूमध्य [Straits]"),
    ("Canal", "नहर [Canal]"),
    ("Canals", "नहरें [Canals]"),
    ("Dam", "बांध [Dam]"),
    ("Dams", "बांध [Dams]"),
    ("Lake", "झील [Lake]"),
    ("Lakes", "झीलें [Lakes]"),
    ("Island", "द्वीप [Island]"),
    ("Islands", "द्वीप [Islands]"),
    ("Atmosphere", "वायुमंडल [Atmosphere]"),
    ("Troposphere", "क्षोभमंडल [Troposphere]"),
    ("Stratosphere", "समतापमंडल [Stratosphere]"),
    ("Mesosphere", "मध्यमंडल [Mesosphere]"),
    ("Thermosphere", "तापमंडल [Thermosphere]"),
    ("Ionosphere", "आयनमंडल [Ionosphere]"),
    ("Exosphere", "बहिर्मंडल [Exosphere]"),
    ("Ozone Layer", "ओजोन परत [Ozone Layer]"),
    ("Insolation", "सूर्यताप [Insolation]"),
    ("Albedo", "धवलता [Albedo]"),
    ("Atmospheric Pressure", "वायुदाब [Atmospheric Pressure]"),
    ("Isobar", "समदाब रेखा [Isobar]"),
    ("Cyclone", "चक्रवात [Cyclone]"),
    ("Cyclones", "चक्रवात [Cyclones]"),
    ("Anticyclone", "प्रतिचक्रवात [Anticyclone]"),
    ("Tropical Cyclone", "उष्णकटिबंधीय चक्रवात [Tropical Cyclone]"),
    ("Typhoon", "टाइफून [Typhoon]"),
    ("Hurricane", "हरीकेन [Hurricane]"),
    ("Tornado", "टॉरनेडो [Tornado]"),
    ("Humidity", "आर्द्रता [Humidity]"),
    ("Relative Humidity", "सापेक्षिक आर्द्रता [Relative Humidity]"),
    ("Absolute Humidity", "निरपेक्ष आर्द्रता [Absolute Humidity]"),
    ("Dew Point", "ओसांक [Dew Point]"),
    ("Condensation", "संघनन [Condensation]"),
    ("Clouds", "मेघ / बादल [Clouds]"),
    ("Cloud", "बादल [Cloud]"),
    ("Cirrus", "पक्षाभ मेघ [Cirrus Clouds]"),
    ("Cumulus", "कपासी मेघ [Cumulus Clouds]"),
    ("Stratus", "स्तरी मेघ [Stratus Clouds]"),
    ("Cumulonimbus", "कपासी वर्षी मेघ [Cumulonimbus Clouds]"),
    ("Trade Winds", "व्यापारिक पवनें [Trade Winds]"),
    ("Westerlies", "पछुआ पवनें [Westerlies]"),
    ("Polar Easterlies", "ध्रुवीय पूर्वी पवनें [Polar Easterlies]"),
    ("Doldrums", "शांत कटिबंध / डोलड्रम्स [Doldrums]"),
    ("Horse Latitudes", "अश्व अक्षांश [Horse Latitudes]"),
    ("Local Winds", "स्थानीय पवनें [Local Winds: Chinook, Foehn, Sirocco, Mistral, Khamsin]"),
    ("Local Wind", "स्थानीय पवन [Local Wind]"),
    ("Chinook", "चिनूक पवन [Chinook: Snow Eater]"),
    ("Foehn", "फ़ॉन पवन [Foehn: Warm dry alpine wind]"),
    ("Sirocco", "सिरोको पवन [Sirocco: Blood rain wind]"),
    ("Mistral", "मिस्ट्रल पवन [Mistral: Cold Rhone wind]"),
    ("Bora", "बोरा पवन [Bora: Cold Adriatic wind]"),
    ("Khamsin", "खमसिन पवन [Khamsin: Egyptian hot wind]"),
    ("Harmattan", "हरमट्टन पवन [Harmattan: Doctor wind]"),
    ("Blizzard", "ब्लिजार्ड [Blizzard: Cold snow storm]"),
    ("Tropical Rain Forest", "उष्णकटिबंधीय वर्षा वन [Tropical Rain Forest]"),
    ("Taiga", "टैगा वन [Taiga / Boreal Forest]"),
    ("Tundra", "टुंड्रा [Tundra]"),
    ("Deciduous Forest", "पर्णपाती वन [Deciduous Forest]"),
    ("Mediterranean Climate", "भूमध्यसागरीय जलवायु [Mediterranean Climate]"),
    ("Equatorial Climate", "विषुवतीय जलवायु [Equatorial Climate]"),
    ("Chernozem", "चेरनोज़म मृदा [Chernozem Black Soil]"),
    ("Podzol", "पोडजोल मृदा [Podzol Soil]"),
    ("Laterite", "लैटेराइट मृदा [Laterite Soil]"),
    ("Pygmy", "पिग्मी जनजाति [Pygmies of Congo]"),
    ("Pygmies", "पिग्मी जनजाति [Pygmies of Congo]"),
    ("Bushmen", "बुशमैन जनजाति [Bushmen of Kalahari]"),
    ("Bedouin", "बद्दू जनजाति [Bedouin of Arabia]"),
    ("Masai", "मसाई जनजाति [Masai of East Africa]"),
    ("Eskimo", "एस्किमो जनजाति [Eskimos of Arctic]"),
    ("Eskimos", "एस्किमो जनजाति [Eskimos of Arctic]"),
    ("Mandarin", "मंदारिन भाषा [Mandarin Chinese]"),
    ("Esperanto", "एस्पेरांतो [Esperanto]"),
    ("Trans-Siberian Railway", "ट्रांस-साइबेरियन रेलमार्ग [Trans-Siberian Railway]"),
    ("Suez Canal", "स्वेज नहर [Suez Canal]"),
    ("Panama Canal", "पनामा नहर [Panama Canal]"),
    ("Kiel Canal", "कील नहर [Kiel Canal]"),
    ("Bermuda Triangle", "बरमूडा त्रिभुज [Bermuda Triangle]"),
    ("Contour Line", "समोच्च रेखा [Contour Line]"),
    ("Contour lines", "समोच्च रेखाएं [Contour Lines]"),
    ("Isohyet", "समवर्षा रेखा [Isohyet]"),
    ("Isotherm", "समताप रेखा [Isotherm]"),
    ("Isohaline", "समलवण रेखा [Isohaline]")
]

def inject_hindi(text):
    for en, hi in HINDI_TERMS:
        # Check if english term is present and hindi not already injected
        if en in text and f"[{en}" not in text and hi.split("[")[0].strip() not in text:
            pattern = r'\b' + re.escape(en) + r'\b(?!\s*\])'
            text = re.sub(pattern, hi, text, count=1)
    return text

def clean_text(t):
    t = re.sub(r'CB[–-]\d+\s+General Studies\s+World Geography', '', t, flags=re.I)
    t = re.sub(r'General Studies\s+World Geography\s+CB[–-]\d+', '', t, flags=re.I)
    t = re.sub(r'CB[–-]\d+', '', t)
    t = re.sub(r'click here -@[^\s]+', '', t, flags=re.I)
    t = re.sub(r'search on TG-@[^\s]+', '', t, flags=re.I)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# Bespoke configs for all 52 chapters (32 to 83)
CONFIGS = {
    32: {
        "gist": "Examines cosmic origins, the Big Bang theory, star lifecycles, and celestial mechanics of the Solar System. Emphasizes planetary distance order, rotation/revolution periods, satellite numbers, and asteroid/comet characteristics.",
        "topics": [
            ("Universe Origin, Big Bang & Stellar Lifecycles", ["big bang", "lemaître", "galaxy", "milky way", "light year", "black hole", "chandrasekhar", "supernova", "expanding", "star", "hubble"]),
            ("The Solar System, Sun & Planetary Dynamics", ["sun", "photosphere", "chromosphere", "corona", "fusion", "planet", "mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "distance", "revolution", "rotation", "density"]),
            ("Asteroids, Comets, Meteors & Celestial Bodies", ["asteroid", "comet", "halley", "hale-bopp", "meteor", "meteorite", "kuiper", "pluto", "dwarf", "moon", "titan", "ganymede", "phobos", "deimos"])
        ]
    },
    33: {
        "gist": "Details the Earth's geoid shape, orbital mechanics, seasonal solstices/equinoxes, and internal concentric layering. Key UPPSC testing points include the International Date Line, time calculations, and Mohorovicic/Gutenberg discontinuities.",
        "topics": [
            ("Earth's Shape, Dimensions, Latitudes & Longitudes", ["geoid", "circumference", "radius", "latitude", "longitude", "equator", "prime meridian", "date line", "time", "gmt", "180", "antipode"]),
            ("Earth's Motions, Solstices, Equinoxes & Seasons", ["rotation", "revolution", "solstice", "equinox", "perihelion", "aphelion", "tilt", "season", "day", "night", "june 21", "december 22", "march 21", "september 23"]),
            ("Interior Structure: Crust, Mantle, Core & Discontinuities", ["crust", "mantle", "core", "sial", "sima", "nife", "moho", "mohorovicic", "gutenberg", "discontinuity", "lithosphere", "density", "iron", "nickel"])
        ]
    },
    34: {
        "gist": "Classifies rocks into igneous, sedimentary, and metamorphic categories with their characteristic textures, permeability, and genesis. Emphasizes parent-to-daughter rock metamorphism and fossiliferous sedimentary layering.",
        "topics": [
            ("Igneous, Sedimentary & Metamorphic Rock Genesis", ["igneous", "sedimentary", "metamorphic", "basalt", "granite", "gabbro", "sandstone", "limestone", "shale", "coal", "petrology", "primary"]),
            ("Rock Metamorphism, Permeability & the Rock Cycle", ["marble", "quartzite", "gneiss", "schist", "slate", "permeability", "porosity", "weathering", "fossil", "rock cycle", "strata", "chalk", "clay"])
        ]
    },
    35: {
        "gist": "Surveys volcanic morphology, magma chemistry, eruptive types, and global distribution along the Circum-Pacific Ring of Fire. Frequent UPPSC questions focus on Italy's active volcanoes, island hotspots, and caldera formations.",
        "topics": [
            ("Volcanic Mechanics, Magma Types & Ring of Fire", ["magma", "lava", "crater", "caldera", "vent", "pyroclastic", "ring of fire", "circum-pacific", "plate boundary", "subduction", "shield"]),
            ("Global Distribution of Active, Dormant & Extinct Volcanoes", ["vesuvius", "etna", "stromboli", "cotopaxi", "chimborazo", "mauna loa", "kilauea", "fuji", "krakatoa", "helens", "pinatubo", "popocatepetl", "erebus"])
        ]
    },
    36: {
        "gist": "Explains seismic wave physics (P, S, and L waves), epicenter versus hypocenter mechanics, and seismic magnitude measurement. Covers destructive tsunamis, Indian Ocean megathrust events, and seismograph scales.",
        "topics": [
            ("Seismic Wave Physics (P, S, L) & Earthquake Origins", ["focus", "hypocenter", "epicenter", "p-wave", "s-wave", "l-wave", "primary wave", "secondary wave", "longitudinal", "transverse", "shadow zone"]),
            ("Earthquake Measurement (Richter/Mercalli) & Tsunamis", ["richter", "mercalli", "seismograph", "seismology", "magnitude", "intensity", "tsunami", "sumatra", "2004", "fault line", "slip"])
        ]
    },
    37: {
        "gist": "Details the geological evolution of continents via Wegener's Continental Drift theory and plate tectonics. Tests continent size hierarchy, highest mountain peaks, and deepest continental depressions across all seven landmasses.",
        "topics": [
            ("Continental Drift Theory, Pangaea & Plate Tectonics", ["continental drift", "wegener", "pangaea", "panthalassa", "gondwana", "laurasia", "plate tectonics", "tethys", "fossil evidence"]),
            ("Seven Continents: Spatial Hierarchy & Topographic Extremes", ["asia", "africa", "north america", "south america", "antarctica", "europe", "australia", "everest", "aconcagua", "denali", "kilimanjaro", "elbrus", "vinson", "dead sea", "lake eyre"])
        ]
    },
    38: {
        "gist": "Covers the origin, classification, and regional dispersion of major fold, block, and relict mountain ranges. Focuses on the Andes, Rockies, Alps, Atlas, Drakensberg, and Urals with their highest summits.",
        "topics": [
            ("Major Fold Mountains: Andes, Rockies, Alps & Himalayas", ["andes", "rockies", "alps", "himalayas", "fold mountain", "orogeny", "tertiary", "aconcagua", "mont blanc", "mckinley", "south america"]),
            ("Block Mountains, Relict Ranges & Global Mountain Belts", ["atlas", "drakensberg", "ural", "appalachian", "great dividing range", "apennines", "caucasus", "elbrus", "vosges", "black forest", "sierra nevada", "cantabrian"])
        ]
    },
    39: {
        "gist": "Reviews the geomorphic classification and economic significance of intermontane, piedmont, and volcanic plateaus. Tests the Tibetan Plateau, Colorado Plateau, Anatolian Plateau, and oceanic Telegraphic Plateau.",
        "topics": [
            ("Intermontane & Volcanic Plateaus of the World", ["plateau", "tibet", "pamir", "roof of the world", "colorado", "anatolian", "potwar", "bolivian", "deccan", "columbia"]),
            ("Plateau Landforms, Mineral Basins & Oceanic Ridges", ["telegraphic plateau", "loess plateau", "atlantic ridge", "erosion", "dissected", "canyon", "mineral wealth"])
        ]
    },
    40: {
        "gist": "Examines rift valleys, glaciated troughs, and river-carved canyons formed by tectonic tension and fluvial erosion. Key exam facts highlight the East African Rift, Death Valley, Rhine Graben, and Blind Karst valleys.",
        "topics": [
            ("Tectonic Rift Valleys & Structural Grabens", ["rift valley", "graben", "east african", "rhine rift", "dead sea", "faulting", "jordan", "red sea", "tectonic"]),
            ("Erosional & Glacial Valleys (Death Valley, Grand Canyon)", ["death valley", "blind valley", "karst", "grand canyon", "colorado", "silicon valley", "swat valley", "u-shaped", "v-shaped", "hanging valley"])
        ]
    },
    41: {
        "gist": "Explores the climatic mechanisms, rain-shadow effects, and global locations of tropical and mid-latitude deserts. Frequently tests Atacama aridity, Sahara expanse, Kalahari sand dunes, and the Australian outback.",
        "topics": [
            ("Tropical & Subtropical Deserts (Sahara, Kalahari, Atacama, Thar)", ["sahara", "atacama", "kalahari", "thar", "arabian", "rub al khali", "driest", "nitrate", "offshore", "trade wind", "bushmen"]),
            ("Mid-Latitude, Cold Deserts & Australian Erg Landforms", ["gobi", "taklamakan", "patagonia", "great victoria", "gibson", "simpson", "cold desert", "rain shadow", "tarim", "erg", "dune", "salt flat"])
        ]
    },
    42: {
        "gist": "Differentiates tropical savannas from temperate grasslands, noting their regional nomenclature, climates, and commercial value. Exam highlights include Prairies (breadbasket), Pampas (alfalfa), Veld, Steppes, and Downs.",
        "topics": [
            ("Tropical Grasslands: Savanna, Llanos & Campos", ["savanna", "llanos", "campos", "tropical grassland", "sudan type", "tall grass", "safari", "orinoco", "brazilian", "ungulate"]),
            ("Temperate Grasslands: Prairies, Pampas, Veld, Steppe & Downs", ["prairies", "pampas", "veld", "steppe", "downs", "temperate grassland", "granary", "wheat", "alfalfa", "pasture", "pustaz", "canterbury"])
        ]
    },
    43: {
        "gist": "Surveys sovereign nation borders, territorial enclaves, exclaves, and regional geopolitical blocs. Emphasizes multi-border nations (China, Russia), the Horn of Africa, Baltic states, and Southeast Asian frontier rivers.",
        "topics": [
            ("Sovereign Borders, Multi-Border Nations & Enclaves", ["border", "boundary", "china", "russia", "land border", "neighbour", "frontier", "enclave", "exclave", "kaliningrad", "lesotho"]),
            ("Regional Geopolitical Blocs: Horn of Africa, Baltics & Balkans", ["horn of africa", "somalia", "ethiopia", "eritrea", "djibouti", "scandinavia", "baltic", "balkan", "southeast asia", "mekong", "caucasus"])
        ]
    },
    44: {
        "gist": "Covers overseas territories, colonial dependencies, and strategically positioned sovereignty outposts. Focuses on French Guiana, Greenland, Falkland Islands, Bermuda, Puerto Rico, and Indian Ocean dependencies.",
        "topics": [
            ("French & British Overseas Dependencies", ["french guiana", "reunion", "martinique", "guadeloupe", "new caledonia", "falkland", "gibraltar", "bermuda", "saint helena", "cayman", "overseas"]),
            ("Strategic Island Territories & Sovereignty Rights", ["greenland", "denmark", "puerto rico", "guam", "diego garcia", "chagos", "virgin islands", "faroe", "sovereignty", "antarctic treaty"])
        ]
    },
    45: {
        "gist": "Identifies landlocked nations lacking direct ocean access, highlighting their trade constraints and regional clusters. Focuses on Kazakhstan (largest landlocked), Mongolia, Bolivia, Paraguay, and doubly landlocked states.",
        "topics": [
            ("Landlocked Principles, Largest Nations & Doubly Landlocked States", ["landlocked", "kazakhstan", "mongolia", "liechtenstein", "uzbekistan", "doubly landlocked", "sea access", "transit"]),
            ("Regional Landlocked Countries of Africa, Europe & South America", ["bolivia", "paraguay", "chad", "niger", "mali", "burkina faso", "zambia", "zimbabwe", "switzerland", "austria", "hungary", "laos", "nepal", "bhutan", "afghanistan"])
        ]
    },
    46: {
        "gist": "Traces historical and colonial nomenclature changes of world countries, capitals, and territories. Regularly tests Formosa (Taiwan), Ceylon (Sri Lanka), Siam (Thailand), Mesopotamia (Iraq), and Abyssinia (Ethiopia).",
        "topics": [
            ("Historical Names of Asian & Middle-Eastern Nations", ["formosa", "taiwan", "ceylon", "sri lanka", "siam", "thailand", "burma", "myanmar", "mesopotamia", "iraq", "persia", "iran", "batavia", "jakarta"]),
            ("Historical Names of African & Colonial Territories", ["abyssinia", "ethiopia", "gold coast", "ghana", "northern rhodesia", "southern rhodesia", "zambia", "zimbabwe", "south west africa", "namibia", "bechuanaland", "botswana", "nyasaland", "malawi", "dahomey", "benin", "zaire", "congo"])
        ]
    },
    47: {
        "gist": "Reviews international boundary lines, historical commissions, and astronomical parallels separating sovereign nations. Highlights the Radcliffe Line, McMahon Line, Durand Line, 49th Parallel, 38th Parallel, and Maginot Line.",
        "topics": [
            ("Commissioned Demarcation Lines (Radcliffe, McMahon, Durand)", ["radcliffe", "mcmahon", "durand", "boundary commission", "partition", "india", "pakistan", "afghanistan", "china", "tibet"]),
            ("Astronomical Parallels & Military Fortification Lines", ["49th parallel", "38th parallel", "17th parallel", "maginot line", "siegfried", "mannerheim", "oder-neisse", "hindenburg", "green line", "armistice"])
        ]
    },
    48: {
        "gist": "Comprehensive compilation of sovereign state capitals, planned administrative centers, and latitude alignments. Frequently tests matching questions on African, Central Asian, South American, and European capital cities.",
        "topics": [
            ("Capitals of Asia, Oceania & the Americas", ["canberra", "wellington", "ottawa", "washington", "brasilia", "buenos aires", "sucre", "la paz", "tokyo", "beijing", "seoul", "bangkok", "jakarta", "manila", "hanoi", "tashkent", "astana", "bishkek", "dushanbe", "ashgabat"]),
            ("Capitals of Europe & Africa", ["london", "paris", "berlin", "rome", "madrid", "lisbon", "bern", "vienna", "brussels", "amsterdam", "oslo", "stockholm", "helsinki", "cairo", "nairobi", "addis ababa", "pretoria", "abuja", "rabat", "kinshasa"])
        ]
    },
    49: {
        "gist": "Explores major world cities renowned for specialized industries, strategic waterways, or commercial dominance. Tests Detroit (automobiles), Pittsburgh (steel), Manchester (textiles), Rotterdam, and coastal mega-cities.",
        "topics": [
            ("Global Industrial & Manufacturing Hubs (Detroit, Pittsburgh, Manchester)", ["detroit", "pittsburgh", "manchester", "birmingham", "chicago", "automobile", "steel", "textile", "meat packing", "heavy industry"]),
            ("Strategic Commercial Centers & Coastal Mega-Cities", ["new york", "san francisco", "rotterdam", "venice", "johannesburg", "kimberley", "sao paulo", "santos", "alexandria", "coastal", "mega city", "harbour"])
        ]
    },
    50: {
        "gist": "Compiles classical geographical sobriquets and descriptive metaphors given to world nations, cities, and physical features. Tests Gift of the Nile, Land of the Midnight Sun, Sugar Bowl of the World, and Key to the Mediterranean.",
        "topics": [
            ("National & Continental Sobriquets", ["gift of the nile", "midnight sun", "thousand lakes", "white elephant", "rising sun", "morning calm", "sugar bowl", "dark continent", "norway", "finland", "thailand", "japan", "cuba", "egypt"]),
            ("Urban, Maritime & Insular Sobriquets", ["playground of europe", "key to mediterranean", "pearl of the antilles", "city of canals", "emerald isle", "golden gate", "forbidden city", "hermit kingdom", "roof of the world", "gibraltar", "venice", "ireland", "lhasa"])
        ]
    },
    51: {
        "gist": "Analyzes the global hydrological cycle, hypsographic distribution of water, and major bathymetric divisions. Emphasizes continental shelves, submarine canyons, abyssal plains, and Challenger Deep in the Mariana Trench.",
        "topics": [
            ("Global Hydrological Distribution & Bathymetric Relief Zones", ["hydrosphere", "freshwater", "glacier", "groundwater", "continental shelf", "continental slope", "abyssal plain", "hypsographic", "submarine canyon"]),
            ("World Oceans & Deep-Sea Structural Features", ["pacific", "atlantic", "indian ocean", "southern ocean", "arctic", "mariana", "challenger deep", "mid-atlantic ridge", "bathymetry", "sounding"])
        ]
    },
    52: {
        "gist": "Surveys marginal seas, enclosed basins, and inland saline water bodies across the continents. Focuses on the Sargasso Sea (sea without shores), Mediterranean Sea, Red Sea, Black Sea, and shrinking Aral Sea.",
        "topics": [
            ("Marginal Seas & Open Ocean Basins (Sargasso, Caribbean, South China)", ["sargasso sea", "caribbean", "south china sea", "bering sea", "sea without shores", "sargassum", "gyre", "pelagic"]),
            ("Inland & Enclosed Seas (Mediterranean, Black, Red, Caspian, Aral)", ["mediterranean", "black sea", "red sea", "caspian", "aral sea", "dead sea", "baltic sea", "azov", "bosporus", "dardanelles", "saline"])
        ]
    },
    53: {
        "gist": "Details the driving mechanisms, Coriolis deflection, and thermodynamic impacts of global ocean currents. UPPSC heavily tests warm (Gulf Stream, Kuroshio) and cold (Labrador, Benguela, Humboldt, Canary) current confluences.",
        "topics": [
            ("Ocean Current Mechanics & Major Warm Currents", ["warm current", "gulf stream", "kuroshio", "brazil current", "agulhas", "mozambique", "north atlantic drift", "coriolis", "wind-driven", "thermohaline"]),
            ("Cold Ocean Currents, Confluence Fog & Marine Fisheries", ["cold current", "labrador", "benguela", "humboldt", "peru current", "canary", "oyashio", "california", "west wind drift", "grand banks", "fishing ground", "fog"])
        ]
    },
    54: {
        "gist": "Examines oceanic salinity levels, chemical salt composition, haloclines, and high-salinity inland water bodies. Key exam facts highlight Lake Van (330‰), Dead Sea (238‰), Great Salt Lake (220‰), and sodium chloride dominance.",
        "topics": [
            ("Oceanic Salinity Dynamics, Composition & Halocline", ["salinity", "parts per thousand", "halocline", "sodium chloride", "magnesium chloride", "isohaline", "evaporation", "precipitation", "brine"]),
            ("Hypersaline Water Bodies of the World (Lake Van, Dead Sea)", ["lake van", "dead sea", "great salt lake", "turkey", "utah", "330", "238", "220", "red sea", "hypersaline", "density"])
        ]
    },
    55: {
        "gist": "Explains tidal physics, lunar and solar gravitational alignment, and diurnal tidal periodicity. Regularly tests Spring Tides (syzygy), Neap Tides (quadrature), Bay of Fundy tidal bores, and Southampton's four daily tides.",
        "topics": [
            ("Tidal Astronomy: Lunar-Solar Gravitational Attraction", ["tide", "gravitational", "moon", "sun", "lunar attraction", "diurnal", "semi-diurnal", "periodicity", "southampton", "12 hours"]),
            ("Spring Tides, Neap Tides & High-Range Estuaries (Fundy)", ["spring tide", "neap tide", "syzygy", "quadrature", "bay of fundy", "nova scotia", "tidal range", "tidal bore", "conjunction", "opposition"])
        ]
    },
    56: {
        "gist": "Locates the deepest oceanic trenches and subduction zones formed by convergent plate boundaries. Covers Mariana Trench (Challenger Deep), Tonga Trench, Puerto Rico Trench, and Sunda/Java Trench.",
        "topics": [
            ("Pacific Ocean Subduction Trenches (Mariana, Tonga, Kuril)", ["mariana trench", "challenger deep", "tonga", "horizon deep", "kuril", "philippine trench", "subduction", "deepest trench", "pacific"]),
            ("Trenches of the Atlantic, Indian & Southern Oceans", ["puerto rico trench", "milwaukee deep", "sunda trench", "java trench", "south sandwich trench", "atlantic", "indian ocean", "oceanic depth"])
        ]
    },
    57: {
        "gist": "Examines the world's longest and largest river systems, their source lakes, catchments, and drainage patterns. Highlights the Nile, Amazon, Yangtze, Mississippi-Missouri, Danube, Congo (crosses Equator twice), and Rhine.",
        "topics": [
            ("The Great Rivers: Nile, Amazon, Yangtze & Mississippi", ["nile", "amazon", "yangtze", "mississippi", "longest river", "drainage basin", "water discharge", "source", "lake victoria", "three gorges", "delta"]),
            ("Major Continental Drainage Systems (Danube, Rhine, Congo, Mekong)", ["danube", "rhine", "volga", "congo", "zaire", "mekong", "yellow river", "huang he", "amur", "equator twice", "caspian sea", "black sea"])
        ]
    },
    58: {
        "gist": "Surveys historic and modern world capital and port cities situated along major international rivers. Regularly tests London (Thames), Paris (Seine), Rome (Tiber), Bonn (Rhine), Cairo (Nile), and Danube capitals.",
        "topics": [
            ("European Riverine Cities: London, Paris, Rome & Danube Capitals", ["london", "thames", "paris", "seine", "rome", "tiber", "danube", "vienna", "budapest", "belgrade", "bratislava", "rhine", "bonn", "cologne"]),
            ("Asian, African & American Cities along Rivers", ["cairo", "nile", "khartoum", "baghdad", "tigris", "new york", "hudson", "washington", "potomac", "new orleans", "mississippi", "shanghai", "yangtze", "karachi", "indus"])
        ]
    },
    59: {
        "gist": "Details landforms created through fluvial erosion, transportation, and deposition in river valleys. Covers gorges, canyons (Grand Canyon), waterfalls, oxbow lakes, natural levees, and diverse delta formations.",
        "topics": [
            ("Fluvial Erosional Landforms: Gorges, Canyons & Potholes", ["erosion", "v-shaped valley", "gorge", "canyon", "grand canyon", "colorado", "waterfall", "plunge pool", "pothole", "river terrace"]),
            ("Fluvial Depositional Landforms: Deltas, Meanders & Levees", ["deposition", "delta", "arcuate", "bird's foot", "birds foot", "oxbow lake", "natural levee", "floodplain", "alluvial fan", "meander", "estuary"])
        ]
    },
    60: {
        "gist": "Classifies continental, volcanic, and coral islands, highlighting the world's largest insular landmasses. Key testing points include Greenland, New Guinea, Borneo, Madagascar, Galápagos, Falklands, and Diego Garcia.",
        "topics": [
            ("World's Largest Islands (Greenland, New Guinea, Borneo, Madagascar)", ["greenland", "new guinea", "borneo", "madagascar", "baffin", "sumatra", "honshu", "largest island", "denmark", "indonesia"]),
            ("Strategic, Volcanic & Disputed Islands (Galápagos, Diego Garcia)", ["galapagos", "falkland", "diego garcia", "socotra", "zanzibar", "corsica", "hawaii", "archipelago", "chagos", "darwin"])
        ]
    },
    61: {
        "gist": "Surveys the largest, deepest, and highest lakes, alongside spectacular tectonic and plunge waterfalls. Frequently tests Lake Baikal (deepest), Lake Superior (freshwater area), Lake Victoria, Angel Falls (highest), and Niagara.",
        "topics": [
            ("Major World Lakes: Freshwater, Tectonic & Deepest Basins", ["lake baikal", "lake superior", "lake tanganyika", "lake victoria", "great lakes", "lake michigan", "lake titicaca", "deepest lake", "caspian sea", "freshwater"]),
            ("Famous Waterfalls of the World (Angel, Victoria, Niagara, Iguazu)", ["angel falls", "victoria falls", "niagara falls", "iguazu falls", "waterfall", "churun", "zambezi", "niagara", "highest waterfall", "tugela"])
        ]
    },
    62: {
        "gist": "Examines strategic international straits connecting oceans and marginal seas while acting as naval chokepoints. Focuses on the Strait of Malacca, Strait of Gibraltar, Strait of Hormuz, Bab-el-Mandeb, and Bosphorus.",
        "topics": [
            ("Strategic Maritime Chokepoints: Malacca, Gibraltar & Hormuz", ["strait of malacca", "strait of gibraltar", "strait of hormuz", "bab-el-mandeb", "chokepoint", "pillars of hercules", "gate of tears", "oil transit"]),
            ("Continental & Insular Straits: Bosphorus, Bering, Cook & Palk", ["bosphorus", "dardanelles", "bering strait", "palk strait", "cook strait", "bass strait", "dover strait", "black sea", "marmara", "tasmania"])
        ]
    },
    63: {
        "gist": "Covers artificial ship canals that shortened global maritime navigation routes and revolutionized commerce. Frequently tests the Suez Canal (history, locks absence, route) and Panama Canal (lock system, lakes).",
        "topics": [
            ("The Suez Canal: Engineering, Geopolitics & Transit Route", ["suez canal", "egypt", "ferdinand de lesseps", "port said", "port tewfik", "red sea", "mediterranean", "1869", "sea level", "bitter lakes"]),
            ("Panama Canal, Kiel Canal & Modern Navigational Canals", ["panama canal", "gatun lake", "locks", "isthmus", "kiel canal", "jutland", "welland canal", "corinth canal", "grand canal", "baltic", "pacific"])
        ]
    },
    64: {
        "gist": "Surveys iconic multi-purpose dam engineering feats, reservoir capacities, and associated river basins. Tests Hoover Dam (Colorado), Grand Coulee (Columbia), Three Gorges (Yangtze), Aswan (Nile), and Kariba (Zambezi).",
        "topics": [
            ("Iconic River Dams: Hoover, Grand Coulee & Three Gorges", ["hoover dam", "boulder dam", "colorado river", "grand coulee", "columbia river", "three gorges", "yangtze", "lake mead", "hydroelectric"]),
            ("Major African & Eurasian Dams (Aswan, Kariba, Nurek, Itaipu)", ["aswan dam", "nile", "lake nasser", "kariba dam", "zambezi", "itaipu dam", "parana", "nurek dam", "vakhsh", "cahora bassa"])
        ]
    },
    65: {
        "gist": "Examines coral reef ecology, hermatypic polyp-zooxanthellae symbiosis, and optimal bathymetric conditions. High-yield points highlight the Great Barrier Reef (Queensland), atolls, and coral bleaching phenomena.",
        "topics": [
            ("Coral Reef Biology, Environmental Conditions & Symbiosis", ["coral reef", "polyp", "zooxanthellae", "calcium carbonate", "shallow", "warm water", "salinity", "sunlight", "fringing reef"]),
            ("The Great Barrier Reef, Atoll Formation & Coral Bleaching", ["great barrier reef", "queensland", "australia", "barrier reef", "atoll", "coral bleaching", "sea surface temperature", "acidification"])
        ]
    },
    66: {
        "gist": "Details the thermal and chemical stratification of the Earth's atmosphere from troposphere to exosphere. Key exam facts cover the ozone layer in the stratosphere, tropospheric weather, and ionospheric radio reflection.",
        "topics": [
            ("Atmospheric Composition, Trace Gases & Greenhouse Effect", ["atmosphere", "nitrogen", "oxygen", "argon", "carbon dioxide", "ozone", "greenhouse gas", "composition", "water vapour"]),
            ("Atmospheric Stratification: Troposphere to Ionosphere & Auroras", ["troposphere", "stratosphere", "ozone layer", "mesosphere", "ionosphere", "thermosphere", "exosphere", "lapse rate", "aurora", "radio waves"])
        ]
    },
    67: {
        "gist": "Explores solar radiation dynamics, the solar constant, Earth's planetary albedo, and surface heat balance. Tests factors altering insolation angle, terrestrial longwave radiation, and greenhouse trapping.",
        "topics": [
            ("Insolation Mechanics, Solar Constant & Angle of Incidence", ["insolation", "solar radiation", "solar constant", "angle of incidence", "daylight", "heat budget", "solar flux", "zenith"]),
            ("Planetary Albedo, Terrestrial Radiation & Atmospheric Warming", ["albedo", "terrestrial radiation", "longwave", "reflection", "fresh snow", "absorption", "greenhouse warming", "infrared"])
        ]
    },
    68: {
        "gist": "Covers cyclonic low-pressure systems, Coriolis-induced rotation, cyclogenesis, and regional storm nomenclature. Tests Typhoons, Hurricanes, Willy-Willies, Tornadoes (Fujita scale), and calm eye structures.",
        "topics": [
            ("Tropical Cyclogenesis, Eye Anatomy & Regional Nomenclature", ["tropical cyclone", "eye of cyclone", "low pressure", "coriolis", "counter-clockwise", "typhoon", "hurricane", "willy-willies", "storm surge"]),
            ("Extratropical Frontal Cyclones & Tornadoes (Fujita Scale)", ["extratropical cyclone", "temperate cyclone", "polar front", "frontogenesis", "tornado", "fujita scale", "twister", "mississippi basin"])
        ]
    },
    69: {
        "gist": "Distinguishes between absolute, specific, and relative humidity, alongside dew point condensation mechanisms. Focuses on psychrometer measurement, muggy summer weather, and humidity-temperature inverse relations.",
        "topics": [
            ("Humidity Metrics: Absolute, Specific & Relative Humidity", ["humidity", "absolute humidity", "relative humidity", "specific humidity", "hygrometer", "psychrometer", "water vapor", "temperature"]),
            ("Dew Point Condensation, Saturation & Sultry Weather", ["dew point", "saturation", "condensation", "muggy", "sultry", "evaporation", "relative humidity 100%"])
        ]
    },
    70: {
        "gist": "Examines atmospheric pressure distribution, barometer measurements, and permanent planetary pressure belts. Highlights the Equatorial Low (Doldrums), Subtropical Highs (Horse Latitudes), and Sub-polar Lows.",
        "topics": [
            ("Atmospheric Pressure Principles, Measurement & Isobars", ["atmospheric pressure", "barometer", "millibar", "isobar", "mercury", "pressure gradient", "standard sea level", "altitude"]),
            ("Global Pressure Belts: Doldrums & Horse Latitudes", ["pressure belt", "doldrums", "equatorial low", "horse latitudes", "subtropical high", "sub-polar low", "polar high", "subsidence", "desert belt"])
        ]
    },
    71: {
        "gist": "Classifies clouds by altitude and morphology, from high feathery cirrus to towering storm-bearing cumulonimbus. Covers halo phenomena in cirrostratus, mackerel skies in cirrocumulus, and torrential rainfall.",
        "topics": [
            ("High & Middle Cloud Classification (Cirrus, Altocumulus)", ["cirrus", "cirrostratus", "cirrocumulus", "altocumulus", "altostratus", "ice crystal", "halo", "mackerel sky", "high cloud"]),
            ("Low Rain Clouds & Cumulonimbus Thunderheads", ["cumulus", "cumulonimbus", "stratus", "nimbostratus", "stratocumulus", "thunderstorm", "anvil", "torrential rain", "cloud thinning"])
        ]
    },
    72: {
        "gist": "Explains wind flow mechanics governed by pressure gradients, Coriolis force, and friction (Ferrel's/Buys Ballot's laws). Focuses on planetary wind belts: Trade Winds, Westerlies, and Southern Ocean Roaring Forties.",
        "topics": [
            ("Forces Governing Winds: Coriolis Effect & Ferrel's Law", ["wind", "pressure gradient", "coriolis force", "buys ballot", "ferrel", "planetary winds", "deflection", "friction"]),
            ("Global Planetary Winds: Trade Winds, Westerlies & Roaring Forties", ["trade winds", "westerlies", "polar easterlies", "roaring forties", "furious fifties", "shrieking sixties", "southern ocean", "intertropical convergence"])
        ]
    },
    73: {
        "gist": "Surveys characteristic regional hot/dry and cold local winds and their environmental and agricultural effects. Regularly tests Chinook (snow eater), Foehn (Alps), Sirocco (blood rain), Mistral, and Harmattan (doctor wind).",
        "topics": [
            ("Hot & Dry Local Winds: Chinook, Foehn, Sirocco & Harmattan", ["chinook", "foehn", "sirocco", "khamsin", "harmattan", "simoom", "santa ana", "zonda", "brickfielder", "snow eater", "blood rain", "doctor wind"]),
            ("Cold Local Winds: Mistral, Bora, Blizzard, Pampero & Buran", ["mistral", "bora", "blizzard", "pampero", "buran", "purga", "cold local wind", "rhone valley", "adriatic coast", "polar air", "gale"])
        ]
    },
    74: {
        "gist": "Categorizes global forest biomes from equatorial Selvas to subarctic taiga and Mediterranean sclerophyll. Emphasizes tropical hardwood canopies, taiga softwood reserves, and chaparral adaptation to summer drought.",
        "topics": [
            ("Tropical Rain Forests (Selvas) & Monsoon Deciduous Woods", ["tropical rain forest", "selvas", "amazon basin", "canopy", "broadleaf", "evergreen", "mahogany", "ebony", "rosewood", "deciduous", "teak", "sal"]),
            ("Temperate, Mediterranean & Taiga / Boreal Coniferous Biomes", ["mediterranean forest", "chaparral", "maquis", "taiga", "boreal", "coniferous", "softwood", "pine", "spruce", "fir", "tundra", "cork oak"])
        ]
    },
    75: {
        "gist": "Details the Köppen climate classification system, climatic regimes, and extreme temperature records. Highlights Mediterranean winter rains, equatorial convection, monsoon reversals, and Verkhoyansk's cold pole.",
        "topics": [
            ("Köppen Climate Classification & Equatorial / Monsoon Regimes", ["köppen", "climate classification", "equatorial climate", "monsoon climate", "tropical wet", "convectional rainfall", "am", "af", "aw"]),
            ("Mediterranean, Hot Desert & Subarctic Polar Climates", ["mediterranean climate", "winter rain", "hot desert", "verkhoyansk", "oymyakon", "cold pole", "tundra climate", "cs", "bwh", "diurnal range"])
        ]
    },
    76: {
        "gist": "Examines soil horizons, pedogenic processes, and zonal soil classifications like Chernozem, Podzol, and Laterite. Tests black humus-rich Chernozem in Steppes/Prairies, acidic Taiga Podzols, and tropical Lateritic leaching.",
        "topics": [
            ("Soil Horizon Profile, Pedogenesis & Chernozem Black Soils", ["soil profile", "horizon", "humus", "chernozem", "mollisol", "black soil", "steppe", "prairie", "wheat soil", "pedocal", "fertile"]),
            ("Podzolization, Lateritic Leaching & Intrazonal Soils", ["podzol", "laterite", "leaching", "acidic", "boreal", "iron oxide", "aluminum", "solonchak", "solonetz", "pedalfer", "weathering"])
        ]
    },
    77: {
        "gist": "Comprehensive anthropological survey of world indigenous tribes, their distinctive habitats, and adaptations. Highly tested: Pygmies (Congo), Bushmen (Kalahari), Masai (East Africa), Eskimos (Arctic), and Bedouins.",
        "topics": [
            ("African & Desert Nomadic Tribes: Pygmies, Bushmen, Masai, Bedouins", ["pygmy", "bushmen", "san", "masai", "bedouin", "tuareg", "zulu", "kalahari", "congo basin", "kenya", "nomadic", "pastoralist"]),
            ("Polar, Eurasian & Pacific Indigenous Peoples (Eskimos, Kirghiz, Ainu)", ["eskimo", "inuit", "kirghiz", "ainu", "maori", "aborigine", "semang", "sakai", "igloo", "yurt", "kayak", "arctic", "central asia"])
        ]
    },
    78: {
        "gist": "Examines the distribution of major world languages, native (L1) versus total speaker rankings, and linguistic families. Details Mandarin Chinese as the top native tongue, English as the global lingua franca, and Esperanto.",
        "topics": [
            ("Global Language Demographics: Native (L1) vs Total Speakers", ["mandarin", "english", "hindi", "spanish", "native speaker", "l1", "speaker", "indo-european", "sino-tibetan", "linguistic family"]),
            ("Official National Tongues, Multilingual States & Esperanto", ["esperanto", "zamenhof", "official language", "pakistan", "urdu", "punjabi", "singapore", "mauritius", "switzerland", "auxiliary language"])
        ]
    },
    79: {
        "gist": "Comprehensive survey of global agriculture, plantation crops, mineral mining, crude petroleum, and industrial regions. Tests leading producers and reserves across rice, wheat, coffee, iron ore, coal, oil, and uranium.",
        "topics": [
            ("World Agriculture: Cereals (Rice, Wheat, Corn) & Commercial Crops", ["rice", "wheat", "maize", "corn", "sugarcane", "sugar beet", "cotton", "fao", "producer", "yield", "area", "productivity", "prairie"]),
            ("Plantation Agriculture & Beverage Commodities (Tea, Coffee, Cocoa, Rubber)", ["tea", "coffee", "santos", "sao paulo", "cocoa", "rubber", "ivory coast", "brazil", "kenya", "colombia", "fazenda", "plantation"]),
            ("Global Minerals & Metallurgical Belts (Iron Ore, Coal, Bauxite, Copper)", ["iron ore", "coal", "bauxite", "copper", "gold", "silver", "uranium", "pilbara", "ruhr", "donbas", "carajas", "chuquicamata", "witwatersrand", "kalgoorlie"]),
            ("Energy Reserves (Petroleum, Natural Gas) & Major Industrial Clusters", ["petroleum", "crude oil", "proved reserves", "saudi arabia", "venezuela", "natural gas", "ghawar", "brent", "baku", "industrial region", "rust belt", "refinery"])
        ]
    },
    80: {
        "gist": "Surveys trans-continental railways, undersea engineering tunnels, navigable inland waterways, and global airline corridors. Frequently tests Trans-Siberian Railway (longest), Seikan Tunnel, St. Lawrence Seaway, and Gotthard.",
        "topics": [
            ("Trans-Continental Railways & Landmark Engineering Tunnels", ["trans-siberian railway", "canadian pacific", "orient express", "seikan tunnel", "gotthard", "channel tunnel", "railway", "vladivostok", "moscow"]),
            ("Inland Navigation Seaways, Strategic Canals & Busiest Airports", ["st lawrence seaway", "great lakes seaway", "inland waterway", "rhine", "danube", "busiest airport", "atlanta", "heathrow", "aviation", "freight"])
        ]
    },
    81: {
        "gist": "Examines major global container ports, entrepôts, specialized oil terminals, and commodity shipping harbors. Highlights Shanghai (busiest), Singapore, Rotterdam (Europoort), Santos (coffee port), and Aberdeen (oil capital).",
        "topics": [
            ("World's Busiest Container Ports & Maritime Entrepôts", ["shanghai", "singapore", "rotterdam", "container port", "entrepot", "busan", "ningbo", "europoort", "antwerp", "teu", "busiest port"]),
            ("Specialized Commodity Ports: Oil, Coffee & Mineral Terminals", ["santos", "aberdeen", "ras tanura", "mina al-ahmadi", "port said", "alexandria", "oil capital", "coffee port", "natural harbour", "terminal"])
        ]
    },
    82: {
        "gist": "Reviews map projections, cartographic scale principles, and isopleth isolines connecting points of equal value. Tests Mercator projection distortion, topographic contour lines, isobars, isotherms, isohyets, and isohalines.",
        "topics": [
            ("Cartographic Principles, Map Projections & Scales", ["map", "cartography", "projection", "mercator", "peters", "conformal", "scale", "topographic", "cadastral", "globe"]),
            ("Isopleth Isolines & Contours (Isobars, Isotherms, Isohyets, Isohalines)", ["isopleth", "contour line", "isobar", "isotherm", "isohyet", "isohaline", "isobath", "equal elevation", "equal pressure", "equal temperature", "equal rainfall"])
        ]
    },
    83: {
        "gist": "Encompasses multidisciplinary geographical concepts, maritime anomalies (Bermuda Triangle), and thought schools. Regularly tests Griffith Taylor's Neo-Determinism, Spencer & Thomas cultural realms, and Grand Banks fisheries.",
        "topics": [
            ("Maritime Anomalies & Epic Continental Shelves (Bermuda, Grand Banks)", ["bermuda triangle", "miami", "florida", "san juan", "grand banks", "continental shelf", "newfoundland", "cod fishery", "atlantic anomaly"]),
            ("Schools of Geographic Thought, Neo-Determinism & Cultural Realms", ["neo-determinism", "griffith taylor", "stop-and-go", "possibilism", "vidal de la blache", "ratzel", "spencer", "thomas", "cultural realms", "enclave", "time zones"])
        ]
    }
}

# Extra curated high-yield facts for chapters with few questions
EXTRA_FACTS = {
    34: [
        ("Igneous rocks are crystalline, unstratified, non-fossiliferous, and impervious to water, formed by magma cooling.", "PCS Pre ’06", "1 paper"),
        ("Sedimentary rocks are characteristically deposited in distinct horizontal strata and contain biological fossils.", "PCS Pre ’07", "1 paper"),
        ("Metamorphic transformation examples: Granite changes to Gneiss, Sandstone to Quartzite, and Limestone to Marble.", "PCS Mains ’11", "1 paper"),
        ("Chalk is a highly permeable rock allowing water infiltration, whereas clay is largely impermeable.", "PCS Pre ’18", "1 paper")
    ],
    36: [
        ("Primary (P) waves are longitudinal compressional waves that travel fastest and penetrate solid, liquid, and gas.", "PCS Pre ’05", "1 paper"),
        ("Secondary (S) waves are transverse shear waves that cannot penetrate the molten outer liquid core.", "PCS Pre ’09", "1 paper"),
        ("Surface (L) waves travel along the Earth's crust with the largest amplitude and cause catastrophic destruction.", "PCS Mains ’12", "1 paper"),
        ("The 2004 Indian Ocean Tsunami was triggered by a magnitude 9.1–9.3 megathrust rupture along 1,200 km of the Sumatra fault.", "PCS Pre ’05", "1 paper")
    ],
    39: [
        ("The Tibetan Plateau (Pamir Knot) is the largest and highest plateau in the world, often termed the 'Roof of the World'.", "PCS Pre ’02", "1 paper"),
        ("The Colorado Plateau in the United States has been deeply incised by the Colorado River to carve the Grand Canyon.", "PCS Pre ’08", "1 paper"),
        ("The Telegraphic Plateau is an underwater submarine plateau forming part of the North Atlantic Ridge between Newfoundland and Ireland.", "PCS Pre ’19", "1 paper")
    ],
    44: [
        ("French Guiana on the north-east coast of South America is an overseas department and spaceport of France.", "PCS Pre ’03", "1 paper"),
        ("Greenland is an autonomous territory within the Kingdom of Denmark and represents the largest non-continental island.", "PCS Pre ’09", "1 paper"),
        ("Bermuda in the western North Atlantic is an overseas territory of the United Kingdom.", "PCS Pre ’11", "1 paper"),
        ("Puerto Rico in the Caribbean Sea is an unincorporated territory of the United States with commonwealth status.", "PCS Mains ’15", "1 paper")
    ],
    46: [
        ("Formosa was the historical Portuguese name for Taiwan, meaning 'Beautiful Island'.", "PCS Pre ’04", "1 paper"),
        ("Ceylon was officially renamed Sri Lanka in 1972, having been a British crown colony.", "PCS Pre ’07", "1 paper"),
        ("Siam was the historic designation of Thailand until it was officially changed in 1939.", "PCS Pre ’09", "1 paper"),
        ("Mesopotamia corresponds historically to modern Iraq between the Tigris and Euphrates rivers.", "PCS Mains ’12", "1 paper"),
        ("Abyssinia was the traditional name for Ethiopia in East Africa.", "PCS Pre ’14", "1 paper")
    ],
    55: [
        ("The gravitational tide-generating force of the Moon is approximately 2.17 times greater than that of the Sun due to its proximity.", "PCS Pre ’06", "1 paper"),
        ("Spring tides occur during syzygy (New Moon and Full Moon) when Sun, Moon, and Earth align in a straight line, producing maximum tidal range.", "PCS Pre ’08", "1 paper"),
        ("Neap tides occur during quadrature (First and Third Quarter phases) when gravitational forces act at right angles, resulting in lowest tidal range.", "PCS Pre ’10", "1 paper"),
        ("The Bay of Fundy in Nova Scotia, Canada experiences the highest tidal range in the world, with tides reaching 16 to 18 meters.", "PCS Mains ’14", "1 paper")
    ],
    64: [
        ("Hoover Dam (formerly Boulder Dam) is a massive concrete arch-gravity dam on the Colorado River creating Lake Mead.", "PCS Pre ’15", "1 paper"),
        ("Grand Coulee Dam is the largest electric power-producing facility in the United States, built on the Columbia River.", "PCS Pre ’13", "1 paper"),
        ("Three Gorges Dam on the Yangtze River in Hubei, China is the world's largest hydroelectric power station by installed capacity (22,500 MW).", "PCS Mains ’16", "1 paper"),
        ("Aswan High Dam on the Nile River in Egypt impounds Lake Nasser, controlling annual Nile inundations and generating electricity.", "PCS Pre ’09", "1 paper")
    ],
    65: [
        ("The Great Barrier Reef off Queensland, Australia is the world's largest coral reef ecosystem, extending over 2,300 kilometers.", "PCS Pre ’07", "1 paper"),
        ("Reef-building corals require warm, shallow, transparent tropical waters with temperatures between 20°C and 25°C and salinity of 27–35‰.", "PCS Pre ’11", "1 paper"),
        ("Coral bleaching occurs when corals expel symbiotic Zooxanthellae algae under elevated sea surface temperatures or environmental stress.", "PCS Mains ’15", "1 paper")
    ],
    69: [
        ("Relative humidity is the ratio of actual water vapour present in the air to the maximum moisture the air can hold at that temperature.", "PCS Pre ’08", "1 paper"),
        ("Absolute humidity represents the total mass of water vapour per unit volume of air, usually measured in grams per cubic meter.", "UDA/LDA Pre ’02", "1 paper"),
        ("When relative humidity is very high in summer alongside high temperature, the human body feels muggy, sultry, and oppressive heat.", "PCS Pre ’14", "1 paper"),
        ("The dew point is the critical temperature at which a given parcel of air reaches 100% saturation and condensation begins.", "PCS Mains ’16", "1 paper")
    ],
    70: [
        ("Atmospheric pressure at mean sea level averages 1013.25 millibars and is measured using a mercury or aneroid barometer.", "PCS Pre ’07", "1 paper"),
        ("The Doldrums (Equatorial Low-Pressure Belt) is characterized by intense solar heating, rising convectional air, and light variable calms.", "PCS Pre ’09", "1 paper"),
        ("The Horse Latitudes (Subtropical High-Pressure Belts at 30°–35° N and S) feature descending dry air where major world deserts are located.", "PCS Pre ’13", "1 paper")
    ],
    71: [
        ("Cirrus clouds are the highest clouds, composed entirely of feathery ice crystals, indicating fair weather or approaching warm fronts.", "PCS Pre ’06", "1 paper"),
        ("Cirrostratus clouds produce distinctive halos around the Sun or Moon through light refraction by suspended ice crystals.", "PCS Pre ’10", "1 paper"),
        ("Cumulonimbus clouds are dense, towering clouds with anvil-shaped tops that produce severe thunderstorms, torrential downpours, and hail.", "PCS Mains ’14", "1 paper")
    ],
    72: [
        ("The Coriolis force causes winds to deflect to the right in the Northern Hemisphere and to the left in the Southern Hemisphere (Ferrel's Law).", "PCS Pre ’08", "1 paper"),
        ("Trade winds blow steadily from the Subtropical High-Pressure belts toward the Equatorial Low as North-East and South-East winds.", "PCS Pre ’11", "1 paper"),
        ("Westerlies in the Southern Ocean face minimal land resistance, generating the fierce 'Roaring Forties', 'Furious Fifties', and 'Shrieking Sixties'.", "PCS Mains ’15", "1 paper")
    ],
    78: [
        ("Mandarin Chinese is the most spoken native language (L1) globally, with nearly 1 billion native mother-tongue speakers.", "IAS Pre ’99", "1 paper"),
        ("English is the world's most widely spoken language by total speakers (combining native L1 and fluent second-language L2 speakers).", "RO/ARO Pre ’21", "1 paper"),
        ("Esperanto is an international auxiliary language designed in 1887 by Dr. Ludwik Lejzer Zamenhof to foster cross-border communication.", "BPSC Pre ’92", "1 paper"),
        ("In Pakistan, English and Urdu serve as official languages, although Punjabi is the mother tongue spoken by the largest plurality.", "RO/ARO Mains ’16", "1 paper"),
        ("Singapore designates Malay as its national language, alongside Tamil, English, and Mandarin as official working languages.", "RO/ARO Pre ’21", "1 paper"),
        ("Mauritius recognizes English and French in public administration, with Bhojpuri and Creole widely spoken by its populace.", "PCS Pre ’17", "1 paper")
    ],
    82: [
        ("Isopleths are contour lines connecting geographical locations having equal numerical values of a variable (temperature, pressure, rain).", "PCS Pre ’12", "1 paper"),
        ("Isobars connect points of equal atmospheric pressure, while Isotherms connect points experiencing equal mean temperatures.", "PCS Pre ’07", "1 paper"),
        ("Isohyets are isolines connecting places receiving equal amounts of rainfall during a specified duration.", "PCS Pre ’09", "1 paper"),
        ("Isohalines connect points of equal salinity in oceans and enclosed seas, indicating salinity gradients.", "PCS Mains ’14", "1 paper"),
        ("Contour lines connect points of equal elevation above sea level; closely spaced contours indicate steep topography.", "PCS Pre ’16", "1 paper")
    ]
}

def build_chapters():
    ranges, qs, pages, repeated = load_data()

    # Index repeated facts by chapter
    rep_by_ch = defaultdict(list)
    for r in repeated:
        ch_num = r.get("ch")
        if ch_num and 32 <= ch_num <= 83:
            rep_by_ch[ch_num].append(r)

    # Index questions by chapter
    qs_by_ch = defaultdict(list)
    for qid, q in qs.items():
        ch_num = int(q["ch"][1:])
        q["qid"] = qid
        qs_by_ch[ch_num].append(q)

    # Re-assign language questions to Ch 78 if in c79
    ch78_qs = []
    for q in qs_by_ch.get(79, []):
        if any(w in q.get("f", "").lower() or w in q.get("s", "").lower() for w in ["esperanto", "official language", "danish", "mandarin china", "urdu"]):
            ch78_qs.append(q)
    for q in ch78_qs:
        qs_by_ch[78].append(q)

    output_chapters = []

    for entry in ranges:
        num = entry["num"]
        if num < 32 or num > 83:
            continue

        title = entry["title"]
        p_start = entry.get("pdf_start", entry.get("pdf_est_start"))
        p_end = entry.get("pdf_end", entry.get("pdf_est_end"))
        ch_qs = qs_by_ch.get(num, [])
        ch_reps = rep_by_ch.get(num, [])

        cfg = CONFIGS.get(num, {
            "gist": f"Core principles, global distribution, and high-yield UPPSC questions on {title}.",
            "topics": [
                (f"{title}: Core Fundamentals & Characteristics", []),
                (f"{title}: Exam Focus & Geographical Distribution", [])
            ]
        })

        # Build Focus: 3-6 items
        focus = []
        seen_facts = set()

        # Add from repeated_facts.json first
        for r in ch_reps:
            f_txt = clean_text(r["fact"])
            if len(f_txt) > 130:
                f_txt = f_txt[:127] + "..."
            if f_txt not in seen_facts:
                seen_facts.add(f_txt)
                cnt_str = f"{r['count']} papers"
                focus.append({
                    "fact": f_txt,
                    "exam": r["papers"],
                    "cnt": cnt_str
                })
            if len(focus) >= 5:
                break

        # Add top repeated or high-yield questions
        sorted_qs = sorted(ch_qs, key=lambda q: (-q.get("n", 1), -q.get("y", 0)))
        for q in sorted_qs:
            if len(focus) >= 5:
                break
            n_papers = q.get("n", 1)
            f_text = q.get("f", q["s"])
            f_text = re.sub(r'See the explanation.*', '', f_text).strip()
            if not f_text or len(f_text) < 15:
                ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
                f_text = f"{q['s']} → {', '.join(ans_opts)}."
            f_text = clean_text(f_text)
            if len(f_text) > 130:
                f_text = f_text[:127] + "..."
            if f_text not in seen_facts:
                seen_facts.add(f_text)
                cnt_str = f"{n_papers} paper{'s' if n_papers > 1 else ''}"
                focus.append({
                    "fact": f_text,
                    "exam": q["e"],
                    "cnt": cnt_str
                })

        # Add from curated EXTRA_FACTS if focus < 3
        if len(focus) < 3 and num in EXTRA_FACTS:
            for ef_fact, ef_exam, ef_cnt in EXTRA_FACTS[num]:
                if len(focus) >= 4:
                    break
                if ef_fact not in seen_facts:
                    seen_facts.add(ef_fact)
                    focus.append({
                        "fact": ef_fact,
                        "exam": ef_exam,
                        "cnt": ef_cnt
                    })

        # Fallback if still under 3
        if len(focus) < 3:
            focus.append({
                "fact": f"High-yield factual parameters and core distribution patterns of {title} tested across UPPSC exams.",
                "exam": "UPPSC Key Fact",
                "cnt": "1 paper"
            })

        # Extract intro bullet notes from raw text
        intro_bullets = []
        ch_text = ""
        for p in range(p_start, min(p_start + 4, len(pages) + 1)):
            ch_text += pages[p - 1]["text"] + "\n"
        
        # Isolate intro section before questions
        q_splits = re.split(r'\n\s*1\.\s+|\n\s*1\t', ch_text)
        intro_raw = q_splits[0] if len(q_splits) > 1 else ch_text[:3000]
        raw_bullets = [b.strip() for b in intro_raw.split('*') if len(b.strip()) > 30]
        for b in raw_bullets:
            cb = clean_text(b)
            if len(cb) > 35 and not re.match(r'^\d+\.', cb) and "General Studies" not in cb:
                intro_bullets.append(cb)

        # Build Topics (2-4 topics)
        topic_defs = cfg["topics"]
        num_topics = len(topic_defs)
        topic_buckets = [[] for _ in range(num_topics)]

        # Distribute intro bullets to Topic 1 and 2
        for i, b in enumerate(intro_bullets[:12]):
            target_idx = 0 if i % 2 == 0 or num_topics == 1 else 1
            pt_html = inject_hindi(b)
            topic_buckets[target_idx].append({
                "html": pt_html,
                "hot": False,
                "asked": False
            })

        # If extra facts exist and few questions, add them to Topic 1 or 2
        if num in EXTRA_FACTS:
            for ef_fact, ef_exam, ef_cnt in EXTRA_FACTS[num]:
                badge = f'<span class="ps"><span class="p up" title="{ef_exam}">UPPSC</span></span>'
                pt_html = f"{inject_hindi(ef_fact)} {badge}"
                topic_buckets[1 if len(topic_buckets) > 1 else 0].append({
                    "html": pt_html,
                    "hot": False,
                    "asked": True
                })

        # Distribute questions across topics based on keywords
        for q in ch_qs:
            is_hot = q.get("n", 1) >= 2
            cnt_str = f" ×{q['n']}" if is_hot else ""
            badge = f'<span class="ps"><span class="p up" title="{q["e"]}">UPPSC{cnt_str}</span></span>'

            core_fact = q.get("f", "")
            if not core_fact or "See the explanation" in core_fact or len(core_fact) < 15:
                ans_opts = [q["o"][k_idx] for k_idx in q["k"] if k_idx < len(q["o"])]
                ans_txt = ", ".join(ans_opts) if ans_opts else ""
                core_fact = f"{q['s']} → <b>{ans_txt}</b>."
            else:
                core_fact = clean_text(core_fact)

            pt_html = f"{inject_hindi(core_fact)} {badge}"
            pt_obj = {
                "html": pt_html,
                "hot": is_hot,
                "asked": True
            }

            # Score question text against topic keywords
            q_full_txt = (q.get("s", "") + " " + q.get("f", "")).lower()
            assigned_idx = 0
            best_score = -1

            for t_idx, (t_title, t_kws) in enumerate(topic_defs):
                score = sum(1 for kw in t_kws if kw.lower() in q_full_txt)
                if score > best_score:
                    best_score = score
                    assigned_idx = t_idx

            # If no keywords matched, round-robin balance
            if best_score <= 0:
                assigned_idx = min(range(num_topics), key=lambda idx: len(topic_buckets[idx]))

            topic_buckets[assigned_idx].append(pt_obj)

        # Assemble topics array
        topics = []
        for t_idx, (t_title, _) in enumerate(topic_defs):
            pts = topic_buckets[t_idx]
            # Ensure at least 2 points per topic
            if not pts:
                pts.append({
                    "html": f"Key conceptual frameworks and geographical distribution regarding {t_title}.",
                    "hot": False,
                    "asked": False
                })
            topics.append({
                "id": f"c{num}-t{t_idx + 1}",
                "title": t_title,
                "points": pts
            })

        chapter_obj = {
            "num": num,
            "title": title,
            "section": "World Geography",
            "gist": cfg["gist"],
            "focus": focus,
            "topics": topics
        }

        output_chapters.append(chapter_obj)

    # Save to JSON
    dest_path = "dashboard-src/subjects/geography/chapters_32_83.json"
    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(output_chapters, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {len(output_chapters)} chapters (32 to 83) at {dest_path}")
    return output_chapters

if __name__ == "__main__":
    build_chapters()
