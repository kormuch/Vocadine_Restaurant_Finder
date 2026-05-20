# training_data.py
# VocaDine — spaCy NER Training Data
# Restaurant voice assistant for English-speaking tourists in Germany
# 600 annotated sentences across 5 entity labels

from typing import List, Tuple, Dict, Any

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_example(text: str, entity_spans: List[Tuple[str, str]]) -> Tuple[str, Dict]:
    """
    Convert (text, [(entity_text, label), ...]) into spaCy training format.
    Uses text.lower().find() for robust character-position detection.
    Skips entities not found and prints a warning.
    Skips overlapping entities.
    """
    entities = []
    used_ranges = []

    for entity_text, label in entity_spans:
        start = text.lower().find(entity_text.lower())
        if start == -1:
            print(f"WARNING: '{entity_text}' not found in: {text!r}")
            continue

        end = start + len(entity_text)

        # Overlap detection
        overlapping = False
        for (us, ue) in used_ranges:
            if start < ue and end > us:
                print(f"WARNING: '{entity_text}' overlaps with existing entity in: {text!r}")
                overlapping = True
                break

        if not overlapping:
            entities.append((start, end, label))
            used_ranges.append((start, end))

    return (text, {"entities": entities})


# ---------------------------------------------------------------------------
# RAW data — 600 tuples: (text, [(entity_text, label), ...])
# ---------------------------------------------------------------------------
# Distribution:
#   LOCATION only:          60
#   CUISINE only:           80
#   DIET only:              50
#   BUDGET only:            50
#   GROUP_SIZE only:        50
#   LOCATION + CUISINE:     60
#   CUISINE + DIET:         40
#   CUISINE + BUDGET:       40
#   GROUP_SIZE + CUISINE:   30
#   GROUP_SIZE + LOCATION:  20
#   3+ slots combined:      80
#   Adversarial/edge:       40
#   TOTAL:                 600

RAW: List[Tuple[str, List[Tuple[str, str]]]] = [

    # ------------------------------------------------------------------
    # LOCATION only — 60 sentences
    # ------------------------------------------------------------------
    ("Are there any restaurants near the centre of Berlin?", [("Berlin", "LOCATION")]),
    ("We are staying in Munich for the weekend.", [("Munich", "LOCATION")]),
    ("Can you suggest somewhere to eat in Hamburg?", [("Hamburg", "LOCATION")]),
    ("I need a restaurant in Frankfurt tonight.", [("Frankfurt", "LOCATION")]),
    ("What's good to eat in Cologne?", [("Cologne", "LOCATION")]),
    ("We just arrived in Stuttgart and we're hungry.", [("Stuttgart", "LOCATION")]),
    ("Show me options in Dresden please.", [("Dresden", "LOCATION")]),
    ("Is there anything decent in Leipzig?", [("Leipzig", "LOCATION")]),
    ("Looking for a place to dine in Nuremberg.", [("Nuremberg", "LOCATION")]),
    ("Any recommendations for Düsseldorf?", [("Düsseldorf", "LOCATION")]),
    ("We're spending the night in Hannover.", [("Hannover", "LOCATION")]),
    ("What are the dining options in Bremen?", [("Bremen", "LOCATION")]),
    ("I'll be in Bonn tomorrow evening.", [("Bonn", "LOCATION")]),
    ("Can you find me something in Heidelberg?", [("Heidelberg", "LOCATION")]),
    ("We're visiting Freiburg this weekend.", [("Freiburg", "LOCATION")]),
    ("Any nice spots in Augsburg?", [("Augsburg", "LOCATION")]),
    ("We need a table somewhere in Dortmund.", [("Dortmund", "LOCATION")]),
    ("Any restaurants in Mannheim you'd recommend?", [("Mannheim", "LOCATION")]),
    ("I'm passing through Karlsruhe tonight.", [("Karlsruhe", "LOCATION")]),
    ("What can I find in Münster?", [("Münster", "LOCATION")]),
    ("We're based in Wiesbaden for a few days.", [("Wiesbaden", "LOCATION")]),
    ("Any good places in Regensburg?", [("Regensburg", "LOCATION")]),
    ("We'll be visiting Haigerloch this weekend.", [("Haigerloch", "LOCATION")]),
    ("Can you help me find something in Tübingen?", [("Tübingen", "LOCATION")]),
    ("I'm looking for a restaurant in Lübeck.", [("Lübeck", "LOCATION")]),
    ("What should I eat while in Kiel?", [("Kiel", "LOCATION")]),
    ("We are travelling through Erfurt.", [("Erfurt", "LOCATION")]),
    ("Any ideas for dining in Rostock?", [("Rostock", "LOCATION")]),
    ("I need something in Saarbrücken.", [("Saarbrücken", "LOCATION")]),
    ("We're stopping in Magdeburg for dinner.", [("Magdeburg", "LOCATION")]),
    ("Heading to Berlin tomorrow, where should we eat?", [("Berlin", "LOCATION")]),
    ("What's popular in Munich for dinner?", [("Munich", "LOCATION")]),
    ("Is there anything open late in Hamburg?", [("Hamburg", "LOCATION")]),
    ("We only have a few hours in Frankfurt.", [("Frankfurt", "LOCATION")]),
    ("I heard Cologne has great food, any tips?", [("Cologne", "LOCATION")]),
    ("We just checked into our hotel in Stuttgart.", [("Stuttgart", "LOCATION")]),
    ("Not sure what's around in Dresden.", [("Dresden", "LOCATION")]),
    ("Any hidden gems in Leipzig?", [("Leipzig", "LOCATION")]),
    ("Spending the afternoon in Nuremberg, any lunch spots?", [("Nuremberg", "LOCATION")]),
    ("I'm a tourist in Düsseldorf, help me find food.", [("Düsseldorf", "LOCATION")]),
    ("We're in Hannover until Sunday.", [("Hannover", "LOCATION")]),
    ("What do locals eat in Bremen?", [("Bremen", "LOCATION")]),
    ("We're doing a day trip to Bonn.", [("Bonn", "LOCATION")]),
    ("Can you point me to something in Heidelberg?", [("Heidelberg", "LOCATION")]),
    ("We're in Freiburg for a conference.", [("Freiburg", "LOCATION")]),
    ("Just arrived in Augsburg, very hungry.", [("Augsburg", "LOCATION")]),
    ("Any late-night dining in Dortmund?", [("Dortmund", "LOCATION")]),
    ("We love Mannheim, what's the food scene like?", [("Mannheim", "LOCATION")]),
    ("Staying near the station in Karlsruhe.", [("Karlsruhe", "LOCATION")]),
    ("We're wandering around Münster today.", [("Münster", "LOCATION")]),
    ("What's on in Wiesbaden tonight?", [("Wiesbaden", "LOCATION")]),
    ("I've never been to Regensburg before.", [("Regensburg", "LOCATION")]),
    ("We'd love to find something nice in Haigerloch.", [("Haigerloch", "LOCATION")]),
    ("Visiting Tübingen for the first time.", [("Tübingen", "LOCATION")]),
    ("Is Lübeck worth visiting for food?", [("Lübeck", "LOCATION")]),
    ("We're exploring Kiel by the waterfront.", [("Kiel", "LOCATION")]),
    ("Short layover in Erfurt, need a quick bite.", [("Erfurt", "LOCATION")]),
    ("First time in Rostock, no idea where to go.", [("Rostock", "LOCATION")]),
    ("We're passing through Saarbrücken.", [("Saarbrücken", "LOCATION")]),
    ("Need dinner ideas for Magdeburg.", [("Magdeburg", "LOCATION")]),

    # ------------------------------------------------------------------
    # CUISINE only — 80 sentences
    # ------------------------------------------------------------------
    ("I'm really in the mood for Italian tonight.", [("Italian", "CUISINE")]),
    ("Can we find some Greek food around here?", [("Greek", "CUISINE")]),
    ("I'd love some Japanese cuisine for dinner.", [("Japanese", "CUISINE")]),
    ("Let's try Chinese food this evening.", [("Chinese", "CUISINE")]),
    ("I fancy some Indian food right now.", [("Indian", "CUISINE")]),
    ("Mexican sounds perfect, does anywhere do that?", [("Mexican", "CUISINE")]),
    ("I've been craving Thai all day.", [("Thai", "CUISINE")]),
    ("How about Vietnamese? I love pho.", [("Vietnamese", "CUISINE")]),
    ("I could really go for some Turkish food.", [("Turkish", "CUISINE")]),
    ("French cuisine would be a lovely treat.", [("French", "CUISINE")]),
    ("Something traditional German would be great.", [("German", "CUISINE")]),
    ("I'm in the mood for Spanish food.", [("Spanish", "CUISINE")]),
    ("Mediterranean is always a good idea.", [("Mediterranean", "CUISINE")]),
    ("Have you heard of Korean BBQ? I want that.", [("Korean", "CUISINE")]),
    ("A good burger place, please.", [("Burger", "CUISINE")]),
    ("I want Lebanese food tonight.", [("Lebanese", "CUISINE")]),
    ("Moroccan cuisine is on my mind.", [("Moroccan", "CUISINE")]),
    ("Let's try Ethiopian for something different.", [("Ethiopian", "CUISINE")]),
    ("I've always wanted to try Peruvian food.", [("Peruvian", "CUISINE")]),
    ("Brazilian churrascaria would be amazing.", [("Brazilian", "CUISINE")]),
    ("Middle Eastern food is what I'm after.", [("Middle Eastern", "CUISINE")]),
    ("I fancy some sushi tonight.", [("Sushi", "CUISINE")]),
    ("Pizza is always a safe bet.", [("Pizza", "CUISINE")]),
    ("I want a proper pasta dinner.", [("Pasta", "CUISINE")]),
    ("Seafood is what I feel like eating.", [("Seafood", "CUISINE")]),
    ("Tapas would be fun, is there a place?", [("Tapas", "CUISINE")]),
    ("Any Asian restaurants around?", [("Asian", "CUISINE")]),
    ("I'm craving Italian food badly.", [("Italian", "CUISINE")]),
    ("Could we do Greek tonight? I love gyros.", [("Greek", "CUISINE")]),
    ("Japanese ramen sounds incredible right now.", [("Japanese", "CUISINE")]),
    ("We should try some dim sum, so Chinese it is.", [("Chinese", "CUISINE")]),
    ("A good curry place, Indian preferably.", [("Indian", "CUISINE")]),
    ("Tacos and nachos — Mexican for sure.", [("Mexican", "CUISINE")]),
    ("Thai green curry is what I'm dreaming of.", [("Thai", "CUISINE")]),
    ("I'd really enjoy Vietnamese spring rolls.", [("Vietnamese", "CUISINE")]),
    ("Turkish doner is always satisfying.", [("Turkish", "CUISINE")]),
    ("French bistro vibes tonight.", [("French", "CUISINE")]),
    ("I want something authentically German.", [("German", "CUISINE")]),
    ("Spanish tapas and wine, please.", [("Spanish", "CUISINE")]),
    ("Mediterranean meze sounds delightful.", [("Mediterranean", "CUISINE")]),
    ("Korean fried chicken is trending everywhere.", [("Korean", "CUISINE")]),
    ("I'm after a gourmet burger place.", [("Burger", "CUISINE")]),
    ("Lebanese mezze would be perfect.", [("Lebanese", "CUISINE")]),
    ("I've been reading about Moroccan tagine, I want that.", [("Moroccan", "CUISINE")]),
    ("Ethiopian injera is so unique, let's try it.", [("Ethiopian", "CUISINE")]),
    ("Peruvian ceviche is amazing, any places?", [("Peruvian", "CUISINE")]),
    ("Brazilian rodizio is a must-do experience.", [("Brazilian", "CUISINE")]),
    ("I'd like some falafel — Middle Eastern please.", [("Middle Eastern", "CUISINE")]),
    ("A sushi restaurant would make me very happy.", [("Sushi", "CUISINE")]),
    ("Deep dish or Neapolitan, any pizza place.", [("Pizza", "CUISINE")]),
    ("Pasta carbonara is my go-to comfort food.", [("Pasta", "CUISINE")]),
    ("I'm a big fan of fresh seafood dishes.", [("Seafood", "CUISINE")]),
    ("Tapas style sharing is great for groups.", [("Tapas", "CUISINE")]),
    ("Any good pan-Asian restaurants nearby?", [("Asian", "CUISINE")]),
    ("I'm thinking Italian, maybe a trattoria.", [("Italian", "CUISINE")]),
    ("Greek meze and ouzo, that's the plan.", [("Greek", "CUISINE")]),
    ("I want sashimi and miso soup — proper Japanese.", [("Japanese", "CUISINE")]),
    ("Peking duck sounds fantastic right now.", [("Chinese", "CUISINE")]),
    ("A proper korma or tikka masala, Indian definitely.", [("Indian", "CUISINE")]),
    ("Burritos and guacamole, Mexican all the way.", [("Mexican", "CUISINE")]),
    ("Pad thai is my absolute favourite dish.", [("Thai", "CUISINE")]),
    ("Banh mi and fresh rolls, Vietnamese please.", [("Vietnamese", "CUISINE")]),
    ("I want a kebab — proper Turkish one.", [("Turkish", "CUISINE")]),
    ("Coq au vin would be wonderful, French cuisine.", [("French", "CUISINE")]),
    ("Schnitzel and sauerkraut — very German.", [("German", "CUISINE")]),
    ("Paella is calling my name, Spanish food.", [("Spanish", "CUISINE")]),
    ("Hummus and grilled halloumi, Mediterranean.", [("Mediterranean", "CUISINE")]),
    ("Bibimbap is one of my favourites, Korean food.", [("Korean", "CUISINE")]),
    ("A proper smash burger with fries sounds great.", [("Burger", "CUISINE")]),
    ("Kibbeh and fattoush, that's Lebanese for me.", [("Lebanese", "CUISINE")]),
    ("I want to try a Moroccan couscous tonight.", [("Moroccan", "CUISINE")]),
    ("Berbere-spiced stew, Ethiopian please.", [("Ethiopian", "CUISINE")]),
    ("Lomo saltado is what I'm after — Peruvian.", [("Peruvian", "CUISINE")]),
    ("I could eat churrasco all day, Brazilian food.", [("Brazilian", "CUISINE")]),
    ("Shawarma or hummus — Middle Eastern is what I want.", [("Middle Eastern", "CUISINE")]),
    ("Sushi rolls and edamame, perfect dinner.", [("Sushi", "CUISINE")]),
    ("A wood-fired pizza would be ideal.", [("Pizza", "CUISINE")]),
    ("Fresh pasta with truffle sauce sounds divine.", [("Pasta", "CUISINE")]),
    ("Grilled fish and oysters — seafood restaurant.", [("Seafood", "CUISINE")]),
    ("Small plates to share, a tapas bar.", [("Tapas", "CUISINE")]),

    # ------------------------------------------------------------------
    # DIET only — 50 sentences
    # ------------------------------------------------------------------
    ("I'm vegan so I need plant-based options.", [("vegan", "DIET")]),
    ("Do you have vegetarian restaurants nearby?", [("vegetarian", "DIET")]),
    ("I need somewhere that does gluten-free food.", [("gluten-free", "DIET")]),
    ("Only halal please, that's important for me.", [("halal", "DIET")]),
    ("I require kosher food strictly.", [("kosher", "DIET")]),
    ("I'm lactose-free, so no dairy for me.", [("lactose-free", "DIET")]),
    ("Are there any pescatarian-friendly places?", [("pescatarian", "DIET")]),
    ("I can't have dairy at all.", [("dairy-free", "DIET")]),
    ("I have a nut allergy, I need nut-free food.", [("nut-free", "DIET")]),
    ("We're a vegan couple, any suggestions?", [("vegan", "DIET")]),
    ("My partner is vegetarian so that's a must.", [("vegetarian", "DIET")]),
    ("Gluten intolerance means I need special options.", [("gluten-free", "DIET")]),
    ("Our whole group eats halal.", [("halal", "DIET")]),
    ("Keeping kosher is non-negotiable for me.", [("kosher", "DIET")]),
    ("I'm lactose intolerant, anything lactose-free?", [("lactose-free", "DIET")]),
    ("I eat fish but no meat — pescatarian.", [("pescatarian", "DIET")]),
    ("Dairy causes me problems, I need dairy-free.", [("dairy-free", "DIET")]),
    ("Severe nut allergy, absolutely nut-free please.", [("nut-free", "DIET")]),
    ("I follow a strictly vegan diet.", [("vegan", "DIET")]),
    ("Vegetarian only — I don't eat any meat.", [("vegetarian", "DIET")]),
    ("Please make sure it's gluten-free certified.", [("gluten-free", "DIET")]),
    ("Halal certification is required for us.", [("halal", "DIET")]),
    ("I keep a kosher diet.", [("kosher", "DIET")]),
    ("No lactose please, I'm lactose intolerant.", [("lactose-free", "DIET")]),
    ("I eat seafood but nothing else — pescatarian diet.", [("pescatarian", "DIET")]),
    ("Completely dairy-free, even butter is a problem.", [("dairy-free", "DIET")]),
    ("Nuts are dangerous for me, must be nut-free.", [("nut-free", "DIET")]),
    ("Being vegan, I need a fully plant-based menu.", [("vegan", "DIET")]),
    ("Vegetarian food only, no fish either.", [("vegetarian", "DIET")]),
    ("Celiac disease means strictly gluten-free.", [("gluten-free", "DIET")]),
    ("We only eat halal meat.", [("halal", "DIET")]),
    ("I observe kosher dietary laws.", [("kosher", "DIET")]),
    ("Lactose-free options are a necessity for me.", [("lactose-free", "DIET")]),
    ("Fish yes, meat no — I'm pescatarian.", [("pescatarian", "DIET")]),
    ("I need a completely dairy-free meal.", [("dairy-free", "DIET")]),
    ("Please confirm the kitchen is nut-free.", [("nut-free", "DIET")]),
    ("I've been vegan for five years, need proper options.", [("vegan", "DIET")]),
    ("Is there a vegetarian restaurant close by?", [("vegetarian", "DIET")]),
    ("My doctor said gluten-free is essential.", [("gluten-free", "DIET")]),
    ("Halal is a must for religious reasons.", [("halal", "DIET")]),
    ("I follow kosher rules very strictly.", [("kosher", "DIET")]),
    ("No dairy whatsoever, I'm lactose-free.", [("lactose-free", "DIET")]),
    ("I'm a pescatarian so fish dishes are fine.", [("pescatarian", "DIET")]),
    ("Dairy products make me ill, dairy-free please.", [("dairy-free", "DIET")]),
    ("Nut-free kitchen is a must for my child.", [("nut-free", "DIET")]),
    ("As a vegan I look for places with tofu and legumes.", [("vegan", "DIET")]),
    ("Strictly vegetarian, no meat stock either.", [("vegetarian", "DIET")]),
    ("Cross-contamination matters, must be gluten-free.", [("gluten-free", "DIET")]),
    ("The entire family needs halal options.", [("halal", "DIET")]),
    ("I'd prefer something dairy-free if possible.", [("dairy-free", "DIET")]),

    # ------------------------------------------------------------------
    # BUDGET only — 50 sentences
    # ------------------------------------------------------------------
    ("We're on a tight budget, something cheap.", [("cheap", "BUDGET")]),
    ("Looking for something affordable tonight.", [("affordable", "BUDGET")]),
    ("Something budget-friendly would be ideal.", [("budget-friendly", "BUDGET")]),
    ("I don't want to spend much, somewhere inexpensive.", [("inexpensive", "BUDGET")]),
    ("Moderate pricing is fine for us.", [("moderate", "BUDGET")]),
    ("Mid-range restaurants are what we prefer.", [("mid-range", "BUDGET")]),
    ("Something with reasonable prices please.", [("reasonable", "BUDGET")]),
    ("We're OK with expensive if the food is worth it.", [("expensive", "BUDGET")]),
    ("I'd like fine dining for a special occasion.", [("fine dining", "BUDGET")]),
    ("Upscale is fine, we want to treat ourselves.", [("upscale", "BUDGET")]),
    ("A luxury restaurant for our anniversary.", [("luxury", "BUDGET")]),
    ("Somewhere fancy for a special night.", [("fancy", "BUDGET")]),
    ("We don't mind paying a bit, somewhere pricey.", [("pricey", "BUDGET")]),
    ("Keep it cheap, we're backpackers.", [("cheap", "BUDGET")]),
    ("We're travelling on a budget, affordable options only.", [("affordable", "BUDGET")]),
    ("Budget-friendly is the keyword for us.", [("budget-friendly", "BUDGET")]),
    ("Something inexpensive — we spent a lot on accommodation.", [("inexpensive", "BUDGET")]),
    ("Moderate prices work perfectly for us.", [("moderate", "BUDGET")]),
    ("Mid-range is our sweet spot.", [("mid-range", "BUDGET")]),
    ("Reasonable pricing, nothing too extravagant.", [("reasonable", "BUDGET")]),
    ("Happy to go expensive for a memorable meal.", [("expensive", "BUDGET")]),
    ("We want fine dining quality tonight.", [("fine dining", "BUDGET")]),
    ("Upscale restaurant, we're celebrating.", [("upscale", "BUDGET")]),
    ("A luxury experience would be perfect tonight.", [("luxury", "BUDGET")]),
    ("Somewhere fancy that won't disappoint.", [("fancy", "BUDGET")]),
    ("I know it's pricey but worth it.", [("pricey", "BUDGET")]),
    ("Cheap eats are what I'm after.", [("cheap", "BUDGET")]),
    ("Nothing too expensive, somewhere affordable.", [("affordable", "BUDGET")]),
    ("We're watching our spending, budget-friendly please.", [("budget-friendly", "BUDGET")]),
    ("Inexpensive but decent quality.", [("inexpensive", "BUDGET")]),
    ("Not too pricey — moderate is fine.", [("moderate", "BUDGET")]),
    ("Mid-range works, not looking for anything flashy.", [("mid-range", "BUDGET")]),
    ("Reasonable prices and good food.", [("reasonable", "BUDGET")]),
    ("An expensive restaurant to really splurge.", [("expensive", "BUDGET")]),
    ("Fine dining would be a dream tonight.", [("fine dining", "BUDGET")]),
    ("We want upscale, we're treating the family.", [("upscale", "BUDGET")]),
    ("A luxury dinner is what we have in mind.", [("luxury", "BUDGET")]),
    ("Fancy atmosphere and excellent food.", [("fancy", "BUDGET")]),
    ("Pricey is OK, quality matters more than cost.", [("pricey", "BUDGET")]),
    ("We need the cheapest option available.", [("cheap", "BUDGET")]),
    ("Affordable means we can eat well without stress.", [("affordable", "BUDGET")]),
    ("Budget-friendly restaurants are perfect for students.", [("budget-friendly", "BUDGET")]),
    ("Something inexpensive for a quick lunch.", [("inexpensive", "BUDGET")]),
    ("Moderate budget, nothing extreme.", [("moderate", "BUDGET")]),
    ("Mid-range, so around fifteen to twenty euros per person.", [("mid-range", "BUDGET")]),
    ("Reasonable cost, we have kids with us.", [("reasonable", "BUDGET")]),
    ("Worth spending more on, somewhere expensive.", [("expensive", "BUDGET")]),
    ("Fine dining for our last night in Germany.", [("fine dining", "BUDGET")]),
    ("Upscale setting for a business dinner.", [("upscale", "BUDGET")]),
    ("A luxury meal to end the trip perfectly.", [("luxury", "BUDGET")]),

    # ------------------------------------------------------------------
    # GROUP_SIZE only — 50 sentences
    # ------------------------------------------------------------------
    ("Table for two, please.", [("two", "GROUP_SIZE")]),
    ("There are four of us total.", [("four", "GROUP_SIZE")]),
    ("Just me tonight, dining solo.", [("solo", "GROUP_SIZE")]),
    ("A table for three would be great.", [("three", "GROUP_SIZE")]),
    ("It's just me dining alone.", [("alone", "GROUP_SIZE")]),
    ("We're a group of six.", [("six", "GROUP_SIZE")]),
    ("Party of five looking for a table.", [("five", "GROUP_SIZE")]),
    ("I'm with seven friends.", [("seven", "GROUP_SIZE")]),
    ("Eight of us are coming for dinner.", [("eight", "GROUP_SIZE")]),
    ("There will be ten people at our table.", [("ten", "GROUP_SIZE")]),
    ("We're a party of twelve.", [("twelve", "GROUP_SIZE")]),
    ("Just me and my partner.", [("me and my partner", "GROUP_SIZE")]),
    ("Me and my friend want a table.", [("me and my friend", "GROUP_SIZE")]),
    ("It's me and my wife for dinner.", [("me and my wife", "GROUP_SIZE")]),
    ("Me and two friends, so three in total.", [("me and two friends", "GROUP_SIZE")]),
    ("Just a couple looking for somewhere to eat.", [("a couple", "GROUP_SIZE")]),
    ("We're a pair, just the two of us.", [("the two of us", "GROUP_SIZE")]),
    ("Three of us will be dining.", [("three of us", "GROUP_SIZE")]),
    ("Four of us are ready for dinner.", [("four of us", "GROUP_SIZE")]),
    ("Five of us, all hungry.", [("five of us", "GROUP_SIZE")]),
    ("A family of four needs a table.", [("family", "GROUP_SIZE")]),
    ("We're a large group, about ten people.", [("large group", "GROUP_SIZE")]),
    ("A small group of three friends.", [("small group", "GROUP_SIZE")]),
    ("Party of two looking for something cosy.", [("party of two", "GROUP_SIZE")]),
    ("Party of four for dinner tonight.", [("party of four", "GROUP_SIZE")]),
    ("Reservation for 2 please.", [("2", "GROUP_SIZE")]),
    ("We need a table for 4.", [("4", "GROUP_SIZE")]),
    ("Booking for 6 people.", [("6", "GROUP_SIZE")]),
    ("We are 8 people, can you accommodate us?", [("8", "GROUP_SIZE")]),
    ("A table for 3 tonight.", [("3", "GROUP_SIZE")]),
    ("There are 5 of us.", [("5", "GROUP_SIZE")]),
    ("7 people need a reservation.", [("7", "GROUP_SIZE")]),
    ("Dinner for 10 please.", [("10", "GROUP_SIZE")]),
    ("Just me, a solo diner.", [("just me", "GROUP_SIZE")]),
    ("The two of us want a quiet corner.", [("the two of us", "GROUP_SIZE")]),
    ("The three of us are celebrating tonight.", [("the three of us", "GROUP_SIZE")]),
    ("We are a pair, two guests.", [("pair", "GROUP_SIZE")]),
    ("I'm flying solo this evening.", [("solo", "GROUP_SIZE")]),
    ("Table for one, please.", [("one", "GROUP_SIZE")]),
    ("Two guests for this evening.", [("two", "GROUP_SIZE")]),
    ("We'll need seating for five.", [("five", "GROUP_SIZE")]),
    ("Six hungry travellers need a table.", [("six", "GROUP_SIZE")]),
    ("How about a table for eight?", [("eight", "GROUP_SIZE")]),
    ("Can you seat twelve of us?", [("twelve", "GROUP_SIZE")]),
    ("Just me and my wife, two people.", [("two", "GROUP_SIZE")]),
    ("We are a group of 7.", [("7", "GROUP_SIZE")]),
    ("Our party has 10 members.", [("10", "GROUP_SIZE")]),
    ("I'll be eating alone tonight.", [("alone", "GROUP_SIZE")]),
    ("We are a family group.", [("family", "GROUP_SIZE")]),
    ("We're a large group tonight, need a big table.", [("large group", "GROUP_SIZE")]),

    # ------------------------------------------------------------------
    # LOCATION + CUISINE — 60 sentences
    # ------------------------------------------------------------------
    ("Looking for Italian food in Munich.", [("Italian", "CUISINE"), ("Munich", "LOCATION")]),
    ("Any Greek restaurants in Berlin?", [("Greek", "CUISINE"), ("Berlin", "LOCATION")]),
    ("I'd like Japanese in Hamburg tonight.", [("Japanese", "CUISINE"), ("Hamburg", "LOCATION")]),
    ("Chinese food in Frankfurt — any ideas?", [("Chinese", "CUISINE"), ("Frankfurt", "LOCATION")]),
    ("Good Indian places in Cologne?", [("Indian", "CUISINE"), ("Cologne", "LOCATION")]),
    ("Mexican in Stuttgart sounds fun.", [("Mexican", "CUISINE"), ("Stuttgart", "LOCATION")]),
    ("Is there a Thai restaurant in Dresden?", [("Thai", "CUISINE"), ("Dresden", "LOCATION")]),
    ("Vietnamese food in Leipzig — where?", [("Vietnamese", "CUISINE"), ("Leipzig", "LOCATION")]),
    ("I want Turkish food in Nuremberg.", [("Turkish", "CUISINE"), ("Nuremberg", "LOCATION")]),
    ("French cuisine in Düsseldorf, recommendations?", [("French", "CUISINE"), ("Düsseldorf", "LOCATION")]),
    ("Traditional German food in Hannover.", [("German", "CUISINE"), ("Hannover", "LOCATION")]),
    ("Spanish tapas in Bremen.", [("Spanish", "CUISINE"), ("Bremen", "LOCATION")]),
    ("Mediterranean in Bonn — any good spots?", [("Mediterranean", "CUISINE"), ("Bonn", "LOCATION")]),
    ("Korean BBQ in Heidelberg?", [("Korean", "CUISINE"), ("Heidelberg", "LOCATION")]),
    ("Burger places in Freiburg.", [("Burger", "CUISINE"), ("Freiburg", "LOCATION")]),
    ("Lebanese food in Augsburg.", [("Lebanese", "CUISINE"), ("Augsburg", "LOCATION")]),
    ("Moroccan in Dortmund, is that possible?", [("Moroccan", "CUISINE"), ("Dortmund", "LOCATION")]),
    ("Ethiopian restaurant in Mannheim?", [("Ethiopian", "CUISINE"), ("Mannheim", "LOCATION")]),
    ("Peruvian food in Karlsruhe.", [("Peruvian", "CUISINE"), ("Karlsruhe", "LOCATION")]),
    ("Brazilian churrasco in Münster.", [("Brazilian", "CUISINE"), ("Münster", "LOCATION")]),
    ("Middle Eastern in Wiesbaden?", [("Middle Eastern", "CUISINE"), ("Wiesbaden", "LOCATION")]),
    ("Sushi in Regensburg tonight.", [("Sushi", "CUISINE"), ("Regensburg", "LOCATION")]),
    ("Pizza in Haigerloch — any places?", [("Pizza", "CUISINE"), ("Haigerloch", "LOCATION")]),
    ("Pasta restaurant in Tübingen.", [("Pasta", "CUISINE"), ("Tübingen", "LOCATION")]),
    ("Seafood in Lübeck sounds amazing.", [("Seafood", "CUISINE"), ("Lübeck", "LOCATION")]),
    ("Tapas bar in Kiel?", [("Tapas", "CUISINE"), ("Kiel", "LOCATION")]),
    ("Asian food in Erfurt.", [("Asian", "CUISINE"), ("Erfurt", "LOCATION")]),
    ("I'm looking for Italian in Rostock.", [("Italian", "CUISINE"), ("Rostock", "LOCATION")]),
    ("Greek in Saarbrücken, any tips?", [("Greek", "CUISINE"), ("Saarbrücken", "LOCATION")]),
    ("Japanese in Magdeburg, is there any?", [("Japanese", "CUISINE"), ("Magdeburg", "LOCATION")]),
    ("Where can I get Italian food in Berlin?", [("Italian", "CUISINE"), ("Berlin", "LOCATION")]),
    ("I want sushi somewhere in Munich.", [("Sushi", "CUISINE"), ("Munich", "LOCATION")]),
    ("Any pizza places in Hamburg?", [("Pizza", "CUISINE"), ("Hamburg", "LOCATION")]),
    ("Can you find Greek food in Frankfurt?", [("Greek", "CUISINE"), ("Frankfurt", "LOCATION")]),
    ("I'd kill for Thai food here in Cologne.", [("Thai", "CUISINE"), ("Cologne", "LOCATION")]),
    ("Vietnamese noodles in Stuttgart — where?", [("Vietnamese", "CUISINE"), ("Stuttgart", "LOCATION")]),
    ("Find me a burger joint in Dresden.", [("Burger", "CUISINE"), ("Dresden", "LOCATION")]),
    ("Indian curry house in Leipzig?", [("Indian", "CUISINE"), ("Leipzig", "LOCATION")]),
    ("Mexican street food in Nuremberg.", [("Mexican", "CUISINE"), ("Nuremberg", "LOCATION")]),
    ("Turkish kebab in Düsseldorf.", [("Turkish", "CUISINE"), ("Düsseldorf", "LOCATION")]),
    ("I want French in Hannover tonight.", [("French", "CUISINE"), ("Hannover", "LOCATION")]),
    ("German comfort food in Bremen.", [("German", "CUISINE"), ("Bremen", "LOCATION")]),
    ("Mediterranean mezze in Bonn.", [("Mediterranean", "CUISINE"), ("Bonn", "LOCATION")]),
    ("Korean in Heidelberg for dinner.", [("Korean", "CUISINE"), ("Heidelberg", "LOCATION")]),
    ("Lebanese in Freiburg, any good ones?", [("Lebanese", "CUISINE"), ("Freiburg", "LOCATION")]),
    ("Moroccan restaurant in Augsburg.", [("Moroccan", "CUISINE"), ("Augsburg", "LOCATION")]),
    ("Ethiopian in Dortmund — worth trying?", [("Ethiopian", "CUISINE"), ("Dortmund", "LOCATION")]),
    ("Peruvian in Mannheim?", [("Peruvian", "CUISINE"), ("Mannheim", "LOCATION")]),
    ("Brazilian in Karlsruhe tonight.", [("Brazilian", "CUISINE"), ("Karlsruhe", "LOCATION")]),
    ("Middle Eastern food in Münster.", [("Middle Eastern", "CUISINE"), ("Münster", "LOCATION")]),
    ("Seafood restaurant in Wiesbaden.", [("Seafood", "CUISINE"), ("Wiesbaden", "LOCATION")]),
    ("Spanish food in Regensburg.", [("Spanish", "CUISINE"), ("Regensburg", "LOCATION")]),
    ("I want pasta in Tübingen.", [("Pasta", "CUISINE"), ("Tübingen", "LOCATION")]),
    ("Any Asian options in Lübeck?", [("Asian", "CUISINE"), ("Lübeck", "LOCATION")]),
    ("Tapas in Kiel for tonight.", [("Tapas", "CUISINE"), ("Kiel", "LOCATION")]),
    ("Sushi restaurant in Erfurt.", [("Sushi", "CUISINE"), ("Erfurt", "LOCATION")]),
    ("Italian near the old town in Rostock.", [("Italian", "CUISINE"), ("Rostock", "LOCATION")]),
    ("Pizza place in Saarbrücken?", [("Pizza", "CUISINE"), ("Saarbrücken", "LOCATION")]),
    ("Japanese cuisine in Magdeburg.", [("Japanese", "CUISINE"), ("Magdeburg", "LOCATION")]),
    ("Good Greek food in Haigerloch?", [("Greek", "CUISINE"), ("Haigerloch", "LOCATION")]),

    # ------------------------------------------------------------------
    # CUISINE + DIET — 40 sentences
    # ------------------------------------------------------------------
    ("I want vegan Italian food.", [("vegan", "DIET"), ("Italian", "CUISINE")]),
    ("Vegetarian Japanese, is that possible?", [("Vegetarian", "DIET"), ("Japanese", "CUISINE")]),
    ("Gluten-free pizza, do you know anywhere?", [("Gluten-free", "DIET"), ("pizza", "CUISINE")]),
    ("Halal Turkish restaurant please.", [("Halal", "DIET"), ("Turkish", "CUISINE")]),
    ("Kosher French cuisine — exists?", [("Kosher", "DIET"), ("French", "CUISINE")]),
    ("Lactose-free pasta options anywhere?", [("Lactose-free", "DIET"), ("pasta", "CUISINE")]),
    ("Pescatarian-friendly Mediterranean restaurant.", [("Pescatarian", "DIET"), ("Mediterranean", "CUISINE")]),
    ("Dairy-free Indian food, I love curry.", [("Dairy-free", "DIET"), ("Indian", "CUISINE")]),
    ("Nut-free Thai restaurant.", [("Nut-free", "DIET"), ("Thai", "CUISINE")]),
    ("Vegan Korean BBQ options?", [("vegan", "DIET"), ("Korean", "CUISINE")]),
    ("Vegetarian Greek mezze.", [("vegetarian", "DIET"), ("Greek", "CUISINE")]),
    ("Gluten-free sushi options nearby?", [("gluten-free", "DIET"), ("sushi", "CUISINE")]),
    ("Halal Chinese food please.", [("halal", "DIET"), ("Chinese", "CUISINE")]),
    ("Kosher Israeli food — similar to Middle Eastern.", [("kosher", "DIET"), ("Middle Eastern", "CUISINE")]),
    ("Lactose-free Vietnamese dishes.", [("lactose-free", "DIET"), ("Vietnamese", "CUISINE")]),
    ("Pescatarian-friendly seafood restaurant of course.", [("pescatarian", "DIET"), ("Seafood", "CUISINE")]),
    ("Dairy-free Mexican food — hold the cheese.", [("dairy-free", "DIET"), ("Mexican", "CUISINE")]),
    ("Nut-free Chinese restaurant please.", [("nut-free", "DIET"), ("Chinese", "CUISINE")]),
    ("Vegan pizza with plant-based toppings.", [("vegan", "DIET"), ("pizza", "CUISINE")]),
    ("Vegetarian Indian curry.", [("vegetarian", "DIET"), ("Indian", "CUISINE")]),
    ("Gluten-free burger options.", [("gluten-free", "DIET"), ("Burger", "CUISINE")]),
    ("Halal Indian restaurant please.", [("halal", "DIET"), ("Indian", "CUISINE")]),
    ("Kosher Mediterranean place.", [("kosher", "DIET"), ("Mediterranean", "CUISINE")]),
    ("Lactose-free French cuisine.", [("lactose-free", "DIET"), ("French", "CUISINE")]),
    ("Pescatarian-friendly Japanese restaurant.", [("pescatarian", "DIET"), ("Japanese", "CUISINE")]),
    ("Dairy-free pasta dish, no cream sauces.", [("dairy-free", "DIET"), ("pasta", "CUISINE")]),
    ("Nut-free Lebanese mezze.", [("nut-free", "DIET"), ("Lebanese", "CUISINE")]),
    ("Vegan sushi, is there such a thing?", [("vegan", "DIET"), ("sushi", "CUISINE")]),
    ("Vegetarian Ethiopian food.", [("vegetarian", "DIET"), ("Ethiopian", "CUISINE")]),
    ("Gluten-free Korean options?", [("gluten-free", "DIET"), ("Korean", "CUISINE")]),
    ("Halal Moroccan restaurant.", [("halal", "DIET"), ("Moroccan", "CUISINE")]),
    ("Kosher food — maybe some good deli.", [("kosher", "DIET"), ("German", "CUISINE")]),
    ("Lactose-free Thai food.", [("lactose-free", "DIET"), ("Thai", "CUISINE")]),
    ("Pescatarian Spanish food — tapas with seafood.", [("pescatarian", "DIET"), ("Spanish", "CUISINE")]),
    ("Dairy-free sushi.", [("dairy-free", "DIET"), ("sushi", "CUISINE")]),
    ("Nut-free Italian food.", [("nut-free", "DIET"), ("Italian", "CUISINE")]),
    ("Vegan Mexican, hold all the animal products.", [("vegan", "DIET"), ("Mexican", "CUISINE")]),
    ("Vegetarian tapas bar.", [("vegetarian", "DIET"), ("Tapas", "CUISINE")]),
    ("Gluten-free Mediterranean options.", [("gluten-free", "DIET"), ("Mediterranean", "CUISINE")]),
    ("Halal Turkish kebab restaurant.", [("halal", "DIET"), ("Turkish", "CUISINE")]),

    # ------------------------------------------------------------------
    # CUISINE + BUDGET — 40 sentences
    # ------------------------------------------------------------------
    ("Italian food that's affordable.", [("Italian", "CUISINE"), ("affordable", "BUDGET")]),
    ("Cheap Japanese restaurants around?", [("Japanese", "CUISINE"), ("cheap", "BUDGET")]),
    ("Budget-friendly Indian place.", [("Indian", "CUISINE"), ("budget-friendly", "BUDGET")]),
    ("Inexpensive Greek food, any ideas?", [("Greek", "CUISINE"), ("inexpensive", "BUDGET")]),
    ("Moderate-priced Thai restaurant.", [("Thai", "CUISINE"), ("moderate", "BUDGET")]),
    ("Mid-range Chinese restaurant.", [("Chinese", "CUISINE"), ("mid-range", "BUDGET")]),
    ("Reasonable Mexican food.", [("Mexican", "CUISINE"), ("reasonable", "BUDGET")]),
    ("Expensive French cuisine for a splurge.", [("French", "CUISINE"), ("expensive", "BUDGET")]),
    ("Fine dining Italian restaurant.", [("Italian", "CUISINE"), ("fine dining", "BUDGET")]),
    ("Upscale Japanese sushi bar.", [("Sushi", "CUISINE"), ("upscale", "BUDGET")]),
    ("Luxury Mediterranean dinner.", [("Mediterranean", "CUISINE"), ("luxury", "BUDGET")]),
    ("Fancy Spanish restaurant tonight.", [("Spanish", "CUISINE"), ("fancy", "BUDGET")]),
    ("Pricey but worth it — Korean BBQ.", [("Korean", "CUISINE"), ("pricey", "BUDGET")]),
    ("Affordable pizza places around.", [("pizza", "CUISINE"), ("affordable", "BUDGET")]),
    ("Cheap Vietnamese noodle soup.", [("Vietnamese", "CUISINE"), ("cheap", "BUDGET")]),
    ("Budget-friendly burger place.", [("Burger", "CUISINE"), ("budget-friendly", "BUDGET")]),
    ("Inexpensive Turkish kebab.", [("Turkish", "CUISINE"), ("inexpensive", "BUDGET")]),
    ("Moderate Indian buffet pricing.", [("Indian", "CUISINE"), ("moderate", "BUDGET")]),
    ("Mid-range seafood restaurant.", [("Seafood", "CUISINE"), ("mid-range", "BUDGET")]),
    ("Reasonable pasta dinner.", [("Pasta", "CUISINE"), ("reasonable", "BUDGET")]),
    ("Expensive sushi omakase experience.", [("Sushi", "CUISINE"), ("expensive", "BUDGET")]),
    ("Fine dining French bistro.", [("French", "CUISINE"), ("fine dining", "BUDGET")]),
    ("Upscale Italian ristorante.", [("Italian", "CUISINE"), ("upscale", "BUDGET")]),
    ("Luxury German tasting menu.", [("German", "CUISINE"), ("luxury", "BUDGET")]),
    ("Fancy tapas bar.", [("Tapas", "CUISINE"), ("fancy", "BUDGET")]),
    ("Pricey but elegant Lebanese restaurant.", [("Lebanese", "CUISINE"), ("pricey", "BUDGET")]),
    ("Affordable Asian street food.", [("Asian", "CUISINE"), ("affordable", "BUDGET")]),
    ("Cheap Moroccan place.", [("Moroccan", "CUISINE"), ("cheap", "BUDGET")]),
    ("Budget-friendly Ethiopian restaurant.", [("Ethiopian", "CUISINE"), ("budget-friendly", "BUDGET")]),
    ("Inexpensive Mexican tacos.", [("Mexican", "CUISINE"), ("inexpensive", "BUDGET")]),
    ("Moderate Brazilian rodizio.", [("Brazilian", "CUISINE"), ("moderate", "BUDGET")]),
    ("Mid-range Greek taverna.", [("Greek", "CUISINE"), ("mid-range", "BUDGET")]),
    ("Reasonable Korean food.", [("Korean", "CUISINE"), ("reasonable", "BUDGET")]),
    ("Expensive but amazing sushi.", [("Sushi", "CUISINE"), ("expensive", "BUDGET")]),
    ("Fine dining Chinese restaurant.", [("Chinese", "CUISINE"), ("fine dining", "BUDGET")]),
    ("Upscale seafood restaurant.", [("Seafood", "CUISINE"), ("upscale", "BUDGET")]),
    ("Luxury Middle Eastern feast.", [("Middle Eastern", "CUISINE"), ("luxury", "BUDGET")]),
    ("Fancy Peruvian restaurant.", [("Peruvian", "CUISINE"), ("fancy", "BUDGET")]),
    ("Pricey Italian fine dining.", [("Italian", "CUISINE"), ("pricey", "BUDGET")]),
    ("Affordable Thai food for students.", [("Thai", "CUISINE"), ("affordable", "BUDGET")]),

    # ------------------------------------------------------------------
    # GROUP_SIZE + CUISINE — 30 sentences
    # ------------------------------------------------------------------
    ("Table for two at an Italian place.", [("two", "GROUP_SIZE"), ("Italian", "CUISINE")]),
    ("Four of us want sushi.", [("four of us", "GROUP_SIZE"), ("sushi", "CUISINE")]),
    ("Party of five for Thai tonight.", [("five", "GROUP_SIZE"), ("Thai", "CUISINE")]),
    ("Just me, looking for a Greek spot.", [("just me", "GROUP_SIZE"), ("Greek", "CUISINE")]),
    ("Six of us for a Korean BBQ.", [("six", "GROUP_SIZE"), ("Korean", "CUISINE")]),
    ("Three of us want Indian food.", [("three of us", "GROUP_SIZE"), ("Indian", "CUISINE")]),
    ("A couple looking for Mediterranean.", [("a couple", "GROUP_SIZE"), ("Mediterranean", "CUISINE")]),
    ("Eight people for a Chinese banquet.", [("eight", "GROUP_SIZE"), ("Chinese", "CUISINE")]),
    ("Me and my friend want Mexican.", [("me and my friend", "GROUP_SIZE"), ("Mexican", "CUISINE")]),
    ("Large group for Brazilian rodizio.", [("large group", "GROUP_SIZE"), ("Brazilian", "CUISINE")]),
    ("Table for 3 at a Japanese place.", [("3", "GROUP_SIZE"), ("Japanese", "CUISINE")]),
    ("The two of us want French cuisine.", [("the two of us", "GROUP_SIZE"), ("French", "CUISINE")]),
    ("Party of four for Lebanese food.", [("party of four", "GROUP_SIZE"), ("Lebanese", "CUISINE")]),
    ("Seven of us for a Turkish dinner.", [("seven", "GROUP_SIZE"), ("Turkish", "CUISINE")]),
    ("Solo diner wanting sushi.", [("solo", "GROUP_SIZE"), ("sushi", "CUISINE")]),
    ("Family of four looking for pizza.", [("family", "GROUP_SIZE"), ("pizza", "CUISINE")]),
    ("Ten people need a Vietnamese restaurant.", [("ten", "GROUP_SIZE"), ("Vietnamese", "CUISINE")]),
    ("Me and my partner want tapas.", [("me and my partner", "GROUP_SIZE"), ("tapas", "CUISINE")]),
    ("Small group for Spanish food.", [("small group", "GROUP_SIZE"), ("Spanish", "CUISINE")]),
    ("Two guests want burger and fries.", [("two", "GROUP_SIZE"), ("Burger", "CUISINE")]),
    ("Four people for a seafood restaurant.", [("four", "GROUP_SIZE"), ("Seafood", "CUISINE")]),
    ("Just me eating pasta alone.", [("just me", "GROUP_SIZE"), ("pasta", "CUISINE")]),
    ("The three of us want Ethiopian.", [("the three of us", "GROUP_SIZE"), ("Ethiopian", "CUISINE")]),
    ("A pair for Middle Eastern food.", [("pair", "GROUP_SIZE"), ("Middle Eastern", "CUISINE")]),
    ("Five people for a Moroccan dinner.", [("five", "GROUP_SIZE"), ("Moroccan", "CUISINE")]),
    ("Me and two friends want Korean.", [("me and two friends", "GROUP_SIZE"), ("Korean", "CUISINE")]),
    ("Booking for 6 at an Asian restaurant.", [("6", "GROUP_SIZE"), ("Asian", "CUISINE")]),
    ("Table for 8 — we want Peruvian.", [("8", "GROUP_SIZE"), ("Peruvian", "CUISINE")]),
    ("Twelve of us for a big German feast.", [("twelve", "GROUP_SIZE"), ("German", "CUISINE")]),
    ("Me and my wife want something French.", [("me and my wife", "GROUP_SIZE"), ("French", "CUISINE")]),

    # ------------------------------------------------------------------
    # GROUP_SIZE + LOCATION — 20 sentences
    # ------------------------------------------------------------------
    ("Table for two in Berlin.", [("two", "GROUP_SIZE"), ("Berlin", "LOCATION")]),
    ("Three of us visiting Hamburg.", [("three of us", "GROUP_SIZE"), ("Hamburg", "LOCATION")]),
    ("Party of four in Munich.", [("party of four", "GROUP_SIZE"), ("Munich", "LOCATION")]),
    ("Six people need a restaurant in Frankfurt.", [("six", "GROUP_SIZE"), ("Frankfurt", "LOCATION")]),
    ("Just me in Cologne tonight.", [("just me", "GROUP_SIZE"), ("Cologne", "LOCATION")]),
    ("Me and my partner in Stuttgart.", [("me and my partner", "GROUP_SIZE"), ("Stuttgart", "LOCATION")]),
    ("Large group in Dresden.", [("large group", "GROUP_SIZE"), ("Dresden", "LOCATION")]),
    ("Family dining in Leipzig.", [("family", "GROUP_SIZE"), ("Leipzig", "LOCATION")]),
    ("The two of us in Nuremberg.", [("the two of us", "GROUP_SIZE"), ("Nuremberg", "LOCATION")]),
    ("Eight people in Düsseldorf.", [("eight", "GROUP_SIZE"), ("Düsseldorf", "LOCATION")]),
    ("Solo traveller in Hannover.", [("solo", "GROUP_SIZE"), ("Hannover", "LOCATION")]),
    ("Me and my wife in Bremen.", [("me and my wife", "GROUP_SIZE"), ("Bremen", "LOCATION")]),
    ("Five of us in Heidelberg.", [("five of us", "GROUP_SIZE"), ("Heidelberg", "LOCATION")]),
    ("Small group in Freiburg.", [("small group", "GROUP_SIZE"), ("Freiburg", "LOCATION")]),
    ("Table for 4 in Augsburg.", [("4", "GROUP_SIZE"), ("Augsburg", "LOCATION")]),
    ("Ten travellers in Dortmund.", [("ten", "GROUP_SIZE"), ("Dortmund", "LOCATION")]),
    ("A couple dining in Mannheim.", [("a couple", "GROUP_SIZE"), ("Mannheim", "LOCATION")]),
    ("Seven friends in Karlsruhe.", [("seven", "GROUP_SIZE"), ("Karlsruhe", "LOCATION")]),
    ("The three of us in Tübingen.", [("the three of us", "GROUP_SIZE"), ("Tübingen", "LOCATION")]),
    ("Me and two friends in Lübeck.", [("me and two friends", "GROUP_SIZE"), ("Lübeck", "LOCATION")]),

    # ------------------------------------------------------------------
    # 3+ SLOTS COMBINED — 80 sentences
    # ------------------------------------------------------------------
    ("Italian restaurant in Berlin for two people.", [("Italian", "CUISINE"), ("Berlin", "LOCATION"), ("two", "GROUP_SIZE")]),
    ("Vegan sushi in Munich for three of us.", [("vegan", "DIET"), ("sushi", "CUISINE"), ("Munich", "LOCATION"), ("three of us", "GROUP_SIZE")]),
    ("Affordable Greek food in Hamburg for four.", [("affordable", "BUDGET"), ("Greek", "CUISINE"), ("Hamburg", "LOCATION"), ("four", "GROUP_SIZE")]),
    ("Cheap vegan Mexican in Frankfurt.", [("cheap", "BUDGET"), ("vegan", "DIET"), ("Mexican", "CUISINE"), ("Frankfurt", "LOCATION")]),
    ("Japanese for two in Cologne, mid-range budget.", [("Japanese", "CUISINE"), ("two", "GROUP_SIZE"), ("Cologne", "LOCATION"), ("mid-range", "BUDGET")]),
    ("Halal Turkish in Stuttgart for a party of five.", [("halal", "DIET"), ("Turkish", "CUISINE"), ("Stuttgart", "LOCATION"), ("five", "GROUP_SIZE")]),
    ("Vegetarian Indian in Dresden, budget-friendly.", [("vegetarian", "DIET"), ("Indian", "CUISINE"), ("Dresden", "LOCATION"), ("budget-friendly", "BUDGET")]),
    ("Korean BBQ in Leipzig for six people.", [("Korean", "CUISINE"), ("Leipzig", "LOCATION"), ("six", "GROUP_SIZE")]),
    ("Fine dining French in Nuremberg for just the two of us.", [("fine dining", "BUDGET"), ("French", "CUISINE"), ("Nuremberg", "LOCATION"), ("the two of us", "GROUP_SIZE")]),
    ("Gluten-free Italian in Düsseldorf for three.", [("gluten-free", "DIET"), ("Italian", "CUISINE"), ("Düsseldorf", "LOCATION"), ("three", "GROUP_SIZE")]),
    ("Upscale sushi in Hannover for me and my partner.", [("upscale", "BUDGET"), ("sushi", "CUISINE"), ("Hannover", "LOCATION"), ("me and my partner", "GROUP_SIZE")]),
    ("Vegan pizza in Bremen, affordable please.", [("vegan", "DIET"), ("pizza", "CUISINE"), ("Bremen", "LOCATION"), ("affordable", "BUDGET")]),
    ("Halal Indian in Bonn for five of us.", [("halal", "DIET"), ("Indian", "CUISINE"), ("Bonn", "LOCATION"), ("five of us", "GROUP_SIZE")]),
    ("Cheap Chinese in Heidelberg for two.", [("cheap", "BUDGET"), ("Chinese", "CUISINE"), ("Heidelberg", "LOCATION"), ("two", "GROUP_SIZE")]),
    ("Vegetarian Mediterranean in Freiburg for a family.", [("vegetarian", "DIET"), ("Mediterranean", "CUISINE"), ("Freiburg", "LOCATION"), ("family", "GROUP_SIZE")]),
    ("Luxury Italian in Augsburg for me and my wife.", [("luxury", "BUDGET"), ("Italian", "CUISINE"), ("Augsburg", "LOCATION"), ("me and my wife", "GROUP_SIZE")]),
    ("Thai food in Dortmund for six, nothing too pricey.", [("Thai", "CUISINE"), ("Dortmund", "LOCATION"), ("six", "GROUP_SIZE"), ("pricey", "BUDGET")]),
    ("Gluten-free sushi in Mannheim for just me.", [("gluten-free", "DIET"), ("sushi", "CUISINE"), ("Mannheim", "LOCATION"), ("just me", "GROUP_SIZE")]),
    ("Affordable Vietnamese in Karlsruhe for three of us.", [("affordable", "BUDGET"), ("Vietnamese", "CUISINE"), ("Karlsruhe", "LOCATION"), ("three of us", "GROUP_SIZE")]),
    ("Lebanese food in Münster for four, halal please.", [("Lebanese", "CUISINE"), ("Münster", "LOCATION"), ("four", "GROUP_SIZE"), ("halal", "DIET")]),
    ("Fancy Spanish tapas in Wiesbaden for eight.", [("fancy", "BUDGET"), ("Spanish", "CUISINE"), ("Wiesbaden", "LOCATION"), ("eight", "GROUP_SIZE")]),
    ("Vegan Ethiopian in Regensburg for two of us.", [("vegan", "DIET"), ("Ethiopian", "CUISINE"), ("Regensburg", "LOCATION"), ("two", "GROUP_SIZE")]),
    ("Inexpensive Turkish in Haigerloch for a small group.", [("inexpensive", "BUDGET"), ("Turkish", "CUISINE"), ("Haigerloch", "LOCATION"), ("small group", "GROUP_SIZE")]),
    ("Pescatarian seafood in Tübingen for me and my friend.", [("pescatarian", "DIET"), ("Seafood", "CUISINE"), ("Tübingen", "LOCATION"), ("me and my friend", "GROUP_SIZE")]),
    ("Fine dining German in Lübeck for just the two of us.", [("fine dining", "BUDGET"), ("German", "CUISINE"), ("Lübeck", "LOCATION"), ("the two of us", "GROUP_SIZE")]),
    ("Dairy-free Korean in Kiel for three.", [("dairy-free", "DIET"), ("Korean", "CUISINE"), ("Kiel", "LOCATION"), ("three", "GROUP_SIZE")]),
    ("Moderate Moroccan in Erfurt for a party of four.", [("moderate", "BUDGET"), ("Moroccan", "CUISINE"), ("Erfurt", "LOCATION"), ("party of four", "GROUP_SIZE")]),
    ("Vegetarian pizza in Rostock, cheap if possible.", [("vegetarian", "DIET"), ("pizza", "CUISINE"), ("Rostock", "LOCATION"), ("cheap", "BUDGET")]),
    ("Upscale Greek in Saarbrücken for two.", [("upscale", "BUDGET"), ("Greek", "CUISINE"), ("Saarbrücken", "LOCATION"), ("two", "GROUP_SIZE")]),
    ("Halal Moroccan in Magdeburg for six.", [("halal", "DIET"), ("Moroccan", "CUISINE"), ("Magdeburg", "LOCATION"), ("six", "GROUP_SIZE")]),
    ("Affordable Japanese for me and my wife in Berlin.", [("affordable", "BUDGET"), ("Japanese", "CUISINE"), ("me and my wife", "GROUP_SIZE"), ("Berlin", "LOCATION")]),
    ("Gluten-free pasta in Munich for four people.", [("gluten-free", "DIET"), ("pasta", "CUISINE"), ("Munich", "LOCATION"), ("four", "GROUP_SIZE")]),
    ("Budget-friendly Indian buffet in Hamburg for the three of us.", [("budget-friendly", "BUDGET"), ("Indian", "CUISINE"), ("Hamburg", "LOCATION"), ("the three of us", "GROUP_SIZE")]),
    ("Vegan Thai in Frankfurt, reasonable prices.", [("vegan", "DIET"), ("Thai", "CUISINE"), ("Frankfurt", "LOCATION"), ("reasonable", "BUDGET")]),
    ("Kosher food in Cologne for two guests.", [("kosher", "DIET"), ("Cologne", "LOCATION"), ("two", "GROUP_SIZE")]),
    ("Luxury seafood in Stuttgart for a large group.", [("luxury", "BUDGET"), ("Seafood", "CUISINE"), ("Stuttgart", "LOCATION"), ("large group", "GROUP_SIZE")]),
    ("Vegetarian Chinese in Dresden for five of us.", [("vegetarian", "DIET"), ("Chinese", "CUISINE"), ("Dresden", "LOCATION"), ("five of us", "GROUP_SIZE")]),
    ("Inexpensive Mexican in Leipzig for me and two friends.", [("inexpensive", "BUDGET"), ("Mexican", "CUISINE"), ("Leipzig", "LOCATION"), ("me and two friends", "GROUP_SIZE")]),
    ("Halal Indian buffet in Nuremberg for a family.", [("halal", "DIET"), ("Indian", "CUISINE"), ("Nuremberg", "LOCATION"), ("family", "GROUP_SIZE")]),
    ("Fine dining Italian in Düsseldorf for me and my partner.", [("fine dining", "BUDGET"), ("Italian", "CUISINE"), ("Düsseldorf", "LOCATION"), ("me and my partner", "GROUP_SIZE")]),
    ("Gluten-free Greek in Hannover for three of us.", [("gluten-free", "DIET"), ("Greek", "CUISINE"), ("Hannover", "LOCATION"), ("three of us", "GROUP_SIZE")]),
    ("Affordable Vietnamese in Bremen for a couple.", [("affordable", "BUDGET"), ("Vietnamese", "CUISINE"), ("Bremen", "LOCATION"), ("a couple", "GROUP_SIZE")]),
    ("Vegan Korean in Bonn for four.", [("vegan", "DIET"), ("Korean", "CUISINE"), ("Bonn", "LOCATION"), ("four", "GROUP_SIZE")]),
    ("Mid-range Turkish in Heidelberg for seven people.", [("mid-range", "BUDGET"), ("Turkish", "CUISINE"), ("Heidelberg", "LOCATION"), ("seven", "GROUP_SIZE")]),
    ("Pescatarian Mediterranean in Freiburg for two.", [("pescatarian", "DIET"), ("Mediterranean", "CUISINE"), ("Freiburg", "LOCATION"), ("two", "GROUP_SIZE")]),
    ("Fancy sushi in Augsburg for just me.", [("fancy", "BUDGET"), ("sushi", "CUISINE"), ("Augsburg", "LOCATION"), ("just me", "GROUP_SIZE")]),
    ("Dairy-free Italian in Dortmund for the two of us.", [("dairy-free", "DIET"), ("Italian", "CUISINE"), ("Dortmund", "LOCATION"), ("the two of us", "GROUP_SIZE")]),
    ("Cheap Thai for eight people in Mannheim.", [("cheap", "BUDGET"), ("Thai", "CUISINE"), ("eight", "GROUP_SIZE"), ("Mannheim", "LOCATION")]),
    ("Halal Lebanese in Karlsruhe for five of us.", [("halal", "DIET"), ("Lebanese", "CUISINE"), ("Karlsruhe", "LOCATION"), ("five of us", "GROUP_SIZE")]),
    ("Moderate seafood in Münster for me and my friend.", [("moderate", "BUDGET"), ("Seafood", "CUISINE"), ("Münster", "LOCATION"), ("me and my friend", "GROUP_SIZE")]),
    ("Gluten-free pizza in Wiesbaden for a party of two.", [("gluten-free", "DIET"), ("pizza", "CUISINE"), ("Wiesbaden", "LOCATION"), ("party of two", "GROUP_SIZE")]),
    ("Vegetarian sushi in Regensburg for three.", [("vegetarian", "DIET"), ("sushi", "CUISINE"), ("Regensburg", "LOCATION"), ("three", "GROUP_SIZE")]),
    ("Upscale French in Haigerloch for me and my wife.", [("upscale", "BUDGET"), ("French", "CUISINE"), ("Haigerloch", "LOCATION"), ("me and my wife", "GROUP_SIZE")]),
    ("Affordable Indian in Tübingen for a large group.", [("affordable", "BUDGET"), ("Indian", "CUISINE"), ("Tübingen", "LOCATION"), ("large group", "GROUP_SIZE")]),
    ("Vegan German food in Lübeck for two people.", [("vegan", "DIET"), ("German", "CUISINE"), ("Lübeck", "LOCATION"), ("two", "GROUP_SIZE")]),
    ("Inexpensive tapas in Kiel for the three of us.", [("inexpensive", "BUDGET"), ("tapas", "CUISINE"), ("Kiel", "LOCATION"), ("the three of us", "GROUP_SIZE")]),
    ("Dairy-free pasta in Erfurt for solo dining.", [("dairy-free", "DIET"), ("pasta", "CUISINE"), ("Erfurt", "LOCATION"), ("solo", "GROUP_SIZE")]),
    ("Fine dining Greek in Rostock for a pair.", [("fine dining", "BUDGET"), ("Greek", "CUISINE"), ("Rostock", "LOCATION"), ("pair", "GROUP_SIZE")]),
    ("Halal Chinese in Saarbrücken for six people.", [("halal", "DIET"), ("Chinese", "CUISINE"), ("Saarbrücken", "LOCATION"), ("six", "GROUP_SIZE")]),
    ("Cheap sushi in Magdeburg for me and my partner.", [("cheap", "BUDGET"), ("sushi", "CUISINE"), ("Magdeburg", "LOCATION"), ("me and my partner", "GROUP_SIZE")]),
    ("Vegetarian tapas in Berlin, budget-friendly, for four.", [("vegetarian", "DIET"), ("tapas", "CUISINE"), ("Berlin", "LOCATION"), ("budget-friendly", "BUDGET"), ("four", "GROUP_SIZE")]),
    ("Luxury Japanese omakase in Munich for two.", [("luxury", "BUDGET"), ("Japanese", "CUISINE"), ("Munich", "LOCATION"), ("two", "GROUP_SIZE")]),
    ("Gluten-free Korean in Hamburg for a family.", [("gluten-free", "DIET"), ("Korean", "CUISINE"), ("Hamburg", "LOCATION"), ("family", "GROUP_SIZE")]),
    ("Affordable Lebanese in Frankfurt for three.", [("affordable", "BUDGET"), ("Lebanese", "CUISINE"), ("Frankfurt", "LOCATION"), ("three", "GROUP_SIZE")]),
    ("Pescatarian sushi in Cologne for me and my wife.", [("pescatarian", "DIET"), ("sushi", "CUISINE"), ("Cologne", "LOCATION"), ("me and my wife", "GROUP_SIZE")]),
    ("Vegan Mexican in Stuttgart for five of us, cheap.", [("vegan", "DIET"), ("Mexican", "CUISINE"), ("Stuttgart", "LOCATION"), ("five of us", "GROUP_SIZE"), ("cheap", "BUDGET")]),
    ("Mid-range Indian in Dresden for a small group.", [("mid-range", "BUDGET"), ("Indian", "CUISINE"), ("Dresden", "LOCATION"), ("small group", "GROUP_SIZE")]),
    ("Nut-free Italian in Leipzig for eight people.", [("nut-free", "DIET"), ("Italian", "CUISINE"), ("Leipzig", "LOCATION"), ("eight", "GROUP_SIZE")]),
    ("Fancy seafood in Nuremberg for a couple.", [("fancy", "BUDGET"), ("Seafood", "CUISINE"), ("Nuremberg", "LOCATION"), ("a couple", "GROUP_SIZE")]),
    ("Halal Turkish in Düsseldorf for ten people.", [("halal", "DIET"), ("Turkish", "CUISINE"), ("Düsseldorf", "LOCATION"), ("ten", "GROUP_SIZE")]),
    ("Inexpensive Vietnamese in Hannover for me and two friends.", [("inexpensive", "BUDGET"), ("Vietnamese", "CUISINE"), ("Hannover", "LOCATION"), ("me and two friends", "GROUP_SIZE")]),
    ("Lactose-free French in Bremen for solo.", [("lactose-free", "DIET"), ("French", "CUISINE"), ("Bremen", "LOCATION"), ("solo", "GROUP_SIZE")]),
    ("Reasonable Thai in Bonn for a party of five.", [("reasonable", "BUDGET"), ("Thai", "CUISINE"), ("Bonn", "LOCATION"), ("party of five", "GROUP_SIZE")]),
    ("Vegan pizza in Heidelberg for just me.", [("vegan", "DIET"), ("pizza", "CUISINE"), ("Heidelberg", "LOCATION"), ("just me", "GROUP_SIZE")]),
    ("Upscale Greek in Freiburg for four people.", [("upscale", "BUDGET"), ("Greek", "CUISINE"), ("Freiburg", "LOCATION"), ("four", "GROUP_SIZE")]),
    ("Dairy-free Korean in Augsburg for two.", [("dairy-free", "DIET"), ("Korean", "CUISINE"), ("Augsburg", "LOCATION"), ("two", "GROUP_SIZE")]),
    ("Budget-friendly Chinese in Dortmund for seven.", [("budget-friendly", "BUDGET"), ("Chinese", "CUISINE"), ("Dortmund", "LOCATION"), ("seven", "GROUP_SIZE")]),
    ("Kosher Mediterranean in Mannheim for the two of us.", [("kosher", "DIET"), ("Mediterranean", "CUISINE"), ("Mannheim", "LOCATION"), ("the two of us", "GROUP_SIZE")]),
    ("Cheap Ethiopian in Karlsruhe for a group of five.", [("cheap", "BUDGET"), ("Ethiopian", "CUISINE"), ("Karlsruhe", "LOCATION"), ("five", "GROUP_SIZE")]),

    # ------------------------------------------------------------------
    # ADVERSARIAL / EDGE CASES — 40 sentences
    # ------------------------------------------------------------------
    # Negations — do NOT label the negated entity
    ("I don't want Italian tonight.", []),
    ("Please no Chinese food, I had it yesterday.", []),
    ("Anything but Thai, I'm not in the mood.", []),
    ("Not Indian, my stomach can't handle spicy right now.", []),
    ("I specifically don't want expensive places.", []),
    ("We're not looking for fancy dining.", []),
    ("Avoid vegan restaurants please, I eat meat.", []),
    ("Don't show me fast food or burger joints.", []),

    # Corrections
    ("Actually, make that four people, not three.", [("four", "GROUP_SIZE")]),
    ("Wait, we're going to Munich, not Hamburg.", [("Munich", "LOCATION")]),
    ("Actually I changed my mind, Greek not Italian.", [("Greek", "CUISINE")]),
    ("Correction: we need a table for six, not four.", [("six", "GROUP_SIZE")]),
    ("On second thought, let's do something affordable.", [("affordable", "BUDGET")]),
    ("Sorry, I meant vegetarian, not vegan.", [("vegetarian", "DIET")]),

    # Indirect / synonym phrasings
    ("Something not too pricey, maybe mid-range.", [("mid-range", "BUDGET")]),
    ("I fancy sushi tonight.", [("sushi", "CUISINE")]),
    ("Looking for plant-based options.", [("vegan", "DIET")]),
    ("We eat no meat whatsoever.", [("vegetarian", "DIET")]),
    ("A table for myself and nobody else.", [("just me", "GROUP_SIZE")]),
    ("Something that won't break the bank.", [("affordable", "BUDGET")]),
    ("An upmarket spot for a celebration.", [("upscale", "BUDGET")]),
    ("I'm after a proper sit-down meal in the capital.", [("Berlin", "LOCATION")]),
    ("We want to splash out on a memorable dinner.", [("fine dining", "BUDGET")]),
    ("We're counting pennies — the cheaper the better.", [("cheap", "BUDGET")]),

    # Ambiguous phrasings
    ("We're two adults and a toddler.", [("two", "GROUP_SIZE")]),
    ("The kids are gluten-free but I'm not fussy.", [("gluten-free", "DIET")]),
    ("We prefer light dishes — something Mediterranean style.", [("Mediterranean", "CUISINE")]),
    ("Somewhere with good veggie options in the south of Germany.", [("vegetarian", "DIET")]),
    ("We're in the Black Forest area, near Freiburg.", [("Freiburg", "LOCATION")]),
    ("I enjoy raw fish — maybe a sushi place?", [("sushi", "CUISINE")]),

    # Mixed with negation + valid entity
    ("No Indian please, but we do want something in Berlin.", [("Berlin", "LOCATION")]),
    ("I don't want cheap food, I want fine dining.", [("fine dining", "BUDGET")]),
    ("Not vegan — I eat meat — but we need halal.", [("halal", "DIET")]),
    ("We don't want Thai, we want Japanese in Munich.", [("Japanese", "CUISINE"), ("Munich", "LOCATION")]),
    ("Forget the Italian idea, let's do Greek for six.", [("Greek", "CUISINE"), ("six", "GROUP_SIZE")]),
    ("Not looking for fine dining, just something moderate in Hamburg.", [("moderate", "BUDGET"), ("Hamburg", "LOCATION")]),

    # Unexpected phrasing / colloquial
    ("Give me something nice to eat in Frankfurt, not too fancy.", [("Frankfurt", "LOCATION")]),
    ("We're a squad of eight ready to eat Korean.", [("eight", "GROUP_SIZE"), ("Korean", "CUISINE")]),
    ("Solo trip, just myself, something decent.", [("solo", "GROUP_SIZE")]),
    ("Me and the missus want a romantic dinner — French cuisine.", [("me and my partner", "GROUP_SIZE"), ("French", "CUISINE")]),
    ("A spot that does good noodles — maybe Vietnamese or ramen.", [("Vietnamese", "CUISINE")]),
]

# ---------------------------------------------------------------------------
# Validate count
# ---------------------------------------------------------------------------
assert len(RAW) == 600, f"Expected 600 examples, got {len(RAW)}"


# ---------------------------------------------------------------------------
# Conversion to spaCy format
# ---------------------------------------------------------------------------

def get_training_data():
    """Convert RAW list to spaCy NER training format."""
    return [make_example(text, entities) for text, entities in RAW]


# ---------------------------------------------------------------------------
# Train / Val / Test split
# ---------------------------------------------------------------------------

def split_data(seed: int = 42):
    """
    Split training data into train (420), val (90), test (90).
    Uses a fixed seed for reproducibility.
    """
    import random
    data = get_training_data()
    rng = random.Random(seed)
    rng.shuffle(data)

    train = data[:420]
    val   = data[420:510]
    test  = data[510:600]

    assert len(train) == 420
    assert len(val)   == 90
    assert len(test)  == 90

    return train, val, test


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from collections import Counter

    data = get_training_data()

    label_counts: Counter = Counter()
    for _text, ann in data:
        seen = set()
        for (_start, _end, label) in ann["entities"]:
            if label not in seen:
                label_counts[label] += 1
                seen.add(label)

    train, val, test = split_data()

    print("=" * 50)
    print("VocaDine — spaCy NER Training Data Summary")
    print("=" * 50)
    print(f"Total examples : {len(data)}")
    print(f"Train          : {len(train)}")
    print(f"Val            : {len(val)}")
    print(f"Test           : {len(test)}")
    print()
    print("Label distribution (sentences containing label):")
    for label in ["LOCATION", "CUISINE", "DIET", "BUDGET", "GROUP_SIZE"]:
        print(f"  {label:<12} : {label_counts.get(label, 0)}")
    print("=" * 50)
