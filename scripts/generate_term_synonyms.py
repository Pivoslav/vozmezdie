#!/usr/bin/env python3
"""
Generate term_synonyms.json from terms_for_synonyms.json.

For each term, produces 1-5 synonyms in English and Russian, matching
formal/bureaucratic/Cold War archival register.
Uses: (1) curated mappings, (2) NLTK WordNet for English, (3) wiki-synonyms for Russian.
Empty arrays for proper nouns, titles, and unclear cases.

Usage: python scripts/generate_term_synonyms.py
Output: config/term_synonyms.json

Requires: pip install nltk wiki-synonyms
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Light stopwords for extracting content words from phrases (English)
_EN_STOP = frozenset(
    "a an the of in on at to for with by and or but is are was were be been being "
    "have has had do does did will would could should may might must shall can "
    "that this these those it its".split()
)

# Curated synonym mappings: (entry_eng, entry_rus) -> (synonyms_eng, synonyms_rus)
# Formal, bureaucratic, Cold War archival register
SYNONYM_MAP: dict[tuple[str, str], tuple[list[str], list[str]]] = {
    # Institutional / bureaucratic
    ("authorized personnel", "уполномоченный персонал"): (
        ["cleared staff", "accredited personnel", "authorized staff", "cleared personnel"],
        ["уполномоченные сотрудники", "аккредитованный персонал", "служебный персонал", "допущенный персонал"],
    ),
    ("counterintelligence measures", "контрразведывательные меры"): (
        ["counterespionage measures", "security measures", "intelligence countermeasures", "counterintelligence operations"],
        ["меры контрразведки", "контрразведывательные операции", "меры по борьбе с разведкой"],
    ),
    ("counter-propaganda materials", "контрпропагандистских материалов"): (
        ["counterpropaganda materials", "anti-propaganda materials", "ideological counter-materials"],
        ["материалы контрпропаганды", "антипропагандистские материалы"],
    ),
    ("ideological subversion", "идеологической диверсии"): (
        ["ideological diversion", "political subversion", "psychological warfare", "ideological sabotage"],
        ["идеологическая диверсия", "политическая диверсия", "психологическая война"],
    ),
    ("anti-social elements", "антиобщественных элементов"): (
        ["antisocial elements", "hostile elements", "anti-state elements", "deviant elements"],
        ["антиобщественные элементы", "враждебные элементы", "антигосударственные элементы"],
    ),
    ("accomplices", "пособников"): (
        ["collaborators", "accessories", "accomplices to crime", "abettors"],
        ["пособники", "соучастники", "сообщники"],
    ),
    ("fascist accomplices", "фашистских пособников"): (
        ["Nazi collaborators", "fascist collaborators", "collaborationists", "accessories to fascism"],
        ["фашистские пособники", "нацистские пособники", "коллаборационисты"],
    ),
    ("Nazi accomplices", "нацистских пособников"): (
        ["Nazi collaborators", "fascist accomplices", "collaborationists", "accessories to Nazism"],
        ["нацистские пособники", "фашистские пособники", "коллаборационисты"],
    ),
    ("recovered", "изъяты"): (
        ["seized", "confiscated", "impounded", "retrieved"],
        ["изъяты", "конфискованы", "изъятые"],
    ),
    ("confiscated", "конфискованы"): (
        ["seized", "impounded", "requisitioned", "recovered"],
        ["конфискованы", "изъяты", "реквизированы"],
    ),
    ("measures taken", "принятых мер"): (
        ["measures implemented", "measures carried out", "actions taken", "steps taken"],
        ["принятых мер", "осуществленных мер", "проведенных мероприятий"],
    ),
    ("measures carried out", "осуществленных мероприятий"): (
        ["measures implemented", "measures taken", "operations conducted", "actions performed"],
        ["осуществленных мероприятий", "проведенных мер", "выполненных мероприятий"],
    ),
    ("Assistant to the Military Attaché", "помощник военного атташе"): (
        ["Deputy Military Attaché", "Assistant Military Attaché", "Military Attaché Deputy"],
        ["помощник военного атташе", "заместитель военного атташе"],
    ),
    ("Assistant Military Attaché", "помощник военного атташе"): (
        ["Deputy Military Attaché", "Military Attaché Assistant"],
        ["помощник военного атташе", "заместитель военного атташе"],
    ),
    ("Assistant Cultural Attaché", "атташе по вопросам культуры"): (
        ["Deputy Cultural Attaché", "Cultural Attaché Assistant"],
        ["помощник атташе по культуре", "заместитель культурного атташе"],
    ),
    ("assistant", "помощник"): (
        ["deputy", "aide", "adjutant", "auxiliary"],
        ["помощник", "заместитель", "помощник-адъютант"],
    ),
    ("authorities", "власти"): (
        ["officials", "government bodies", "administrative bodies", "competent organs"],
        ["власти", "органы власти", "руководящие органы"],
    ),
    ("police authorities", "органы милиции"): (
        ["law enforcement", "police organs", "militia authorities", "internal affairs bodies"],
        ["органы милиции", "правоохранительные органы", "органы внутренних дел"],
    ),
    ("health authorities", "органов здравоохранения"): (
        ["health agencies", "public health bodies", "health administration"],
        ["органы здравоохранения", "ведомства здравоохранения"],
    ),
    ("assistance was rendered", "оказана помощь"): (
        ["assistance was provided", "aid was given", "support was extended"],
        ["оказана помощь", "предоставлена помощь", "была оказана помощь"],
    ),
    ("border violator", "нарушителя границы"): (
        ["border violator", "illegal border crosser", "unauthorized entrant"],
        ["нарушитель границы", "незаконный пересекатель границы"],
    ),
    ("detained", "задержанного"): (
        ["apprehended", "arrested", "taken into custody"],
        ["задержанного", "арестованного", "взятого под стражу"],
    ),
    ("detained border violator", "задержанного им нарушителя границы"): (
        ["apprehended border violator", "detained illegal crosser"],
        ["задержанного нарушителя границы", "арестованного незаконного пересекателя"],
    ),
    ("demonstration", "демонстрация"): (
        ["rally", "protest", "public gathering", "showing"],
        ["демонстрация", "митинг", "массовое мероприятие"],
    ),
    ("a demonstration", "демонстрация"): (
        ["a rally", "a public showing", "a display"],
        ["демонстрация", "показ", "митинг"],
    ),
    ("leaflet", "листовку"): (
        ["leaflet", "handbill", "flyer", "propaganda leaflet"],
        ["листовка", "воззвание", "пропагандистская листовка"],
    ),
    ("a leaflet", "листовку"): (
        ["a handbill", "a flyer", "a leaflet"],
        ["листовка", "воззвание"],
    ),
    ("handwritten leaflet", "исполненная от руки листовка"): (
        ["handwritten handbill", "manuscript leaflet", "hand-drawn flyer"],
        ["рукописная листовка", "листовка handwritten"],
    ),
    ("member of the Komsomol", "член ВЛКСМ"): (
        ["Komsomol member", "Young Communist League member", "Komsomol cadre"],
        ["член ВЛКСМ", "комсомолец", "член комсомола"],
    ),
    ("long-term character", "долговременный характер"): (
        ["lasting nature", "permanent character", "enduring nature", "sustained character"],
        ["долговременный характер", "длительный характер", "постоянный характер"],
    ),
    ("unfit for use", "непригодны"): (
        ["unsuitable for use", "unserviceable", "inoperable", "condemned"],
        ["непригодны", "непригодны к эксплуатации", "неисправны"],
    ),
    ("in the near future", "в ближайшее время"): (
        ["in the immediate future", "shortly", "soon", "in due course"],
        ["в ближайшее время", "в скором времени", "в ближайший срок"],
    ),
    ("this year", "с.г."): (
        ["current year", "present year", "year in question"],
        ["текущего года", "настоящего года", "с.г."],
    ),
    ("of this year", "с.г."): (
        ["of the current year", "of the present year"],
        ["текущего года", "с.г."],
    ),
    ("As a result", "В результате"): (
        ["Consequently", "Accordingly", "Thus", "Therefore"],
        ["В результате", "Следовательно", "Соответственно"],
    ),
    ("As a result of", "В результате осуществления"): (
        ["Following", "Pursuant to", "As a consequence of"],
        ["В результате", "Вследствие", "По итогам"],
    ),
    ("As a result of measures carried out", "В результате осуществленных мероприятий"): (
        ["Following measures implemented", "As a result of actions taken"],
        ["В результате проведенных мероприятий", "Вследствие принятых мер"],
    ),
    ("as a result of the accident", "вследствие аварии"): (
        ["due to the accident", "following the accident", "as a consequence of the accident"],
        ["вследствие аварии", "в результате аварии", "из-за аварии"],
    ),
    ("as a separate edition", "отдельным изданием"): (
        ["as a separate publication", "in separate print", "as a standalone edition"],
        ["отдельным изданием", "отдельной публикацией"],
    ),
    ("counter-propaganda", "контрпропаганда"): (
        ["counterpropaganda", "anti-propaganda", "counter-information"],
        ["контрпропаганда", "антипропаганда"],
    ),
    ("ideological centers", "идеологических центров"): (
        ["ideological hubs", "propaganda centers", "ideological bases"],
        ["идеологических центров", "идеологических центров влияния"],
    ),
    ("ideological subversion", "идеологической диверсии"): (
        ["ideological sabotage", "political subversion", "psychological warfare"],
        ["идеологическая диверсия", "политическая диверсия"],
    ),
    ("hostile actions", "враждебные действия"): (
        ["hostile activities", "adversarial actions", "enemy actions", "subversive actions"],
        ["враждебные действия", "враждебная деятельность", "подрывные действия"],
    ),
    ("anti-social activities", "антиобщественной деятельности"): (
        ["antisocial activities", "hostile activities", "anti-state activities"],
        ["антиобщественная деятельность", "враждебная деятельность"],
    ),
    ("expelled from the USSR", "выдворенная из СССР"): (
        ["deported from the USSR", "removed from the USSR", "expulsed from the USSR"],
        ["выдворенная из СССР", "депортированная из СССР", "высланная из СССР"],
    ),
    ("departed for", "убыли в"): (
        ["departed to", "left for", "proceeded to", "traveled to"],
        ["убыли в", "отправились в", "выехали в"],
    ),
    ("gathering", "сборище"): (
        ["assembly", "meeting", "convocation", "rally"],
        ["сборище", "собрание", "митинг"],
    ),
    ("provocative campaigns", "провокационные кампании"): (
        ["provocation campaigns", "subversive campaigns", "destabilization campaigns"],
        ["провокационные кампании", "подрывные кампании"],
    ),
    ("Hitlerite occupiers", "гитлеровскими оккупантами"): (
        ["Nazi occupiers", "German fascist occupiers", "Hitlerite invaders"],
        ["гитлеровские оккупанты", "нацистские оккупанты", "гитлеровские захватчики"],
    ),
    ("foreign OUN", "зарубежные ОУН"): (
        ["overseas OUN", "OUN abroad", "OUN in exile"],
        ["зарубежная ОУН", "ОУН за рубежом"],
    ),
    ("orders and instructions", "приказов и указаний"): (
        ["directives and orders", "instructions and commands", "directives"],
        ["приказы и указания", "директивы и распоряжения"],
    ),
    ("hostile actions of foreigners", "враждебные действия иностранцев"): (
        ["adversarial actions by foreigners", "subversive activities of foreigners"],
        ["враждебные действия иностранцев", "подрывная деятельность иностранцев"],
    ),
    ("psychological warfare", "психологическая война"): (
        ["ideological warfare", "information warfare", "psychological operations"],
        ["психологическая война", "идеологическая война", "информационная война"],
    ),
    ("exposing", "разоблачающие"): (
        ["unmasking", "revealing", "discrediting", "denouncing"],
        ["разоблачающие", "раскрывающие", "дискредитирующие"],
    ),
    ("discrediting", "дискредитацию"): (
        ["discrediting", "undermining", "defaming", "compromising"],
        ["дискредитация", "подрыв репутации", "компрометация"],
    ),
    ("rapprochement", "сближению"): (
        ["rapprochement", "reconciliation", "normalization of relations", "drawing closer"],
        ["сближение", "нормализация отношений", "примирение"],
    ),
    ("postgraduates", "аспиранты"): (
        ["postgraduate students", "graduate students", "doctoral candidates"],
        ["аспиранты", "аспиранты-исследователи"],
    ),
    ("interns", "стажёры"): (
        ["trainees", "interns", "probationers"],
        ["стажеры", "практиканты"],
    ),
    ("border patrol", "пограничным нарядом"): (
        ["border guard", "frontier patrol", "border detachment"],
        ["пограничным нарядом", "пограничной заставой", "пограничниками"],
    ),
    ("discovered", "обнаружены"): (
        ["discovered", "found", "detected", "located"],
        ["обнаружены", "найдены", "выявлены"],
    ),
    ("intelligence services", "спецслужбами"): (
        ["intelligence agencies", "secret services", "special services"],
        ["спецслужбами", "разведывательными службами", "органами разведки"],
    ),
    ("collision occurred", "произошло столкновение"): (
        ["collision occurred", "accident occurred", "impact took place"],
        ["произошло столкновение", "произошел инцидент", "имело место столкновение"],
    ),
    ("organized", "организована"): (
        ["arranged", "coordinated", "conducted", "staged"],
        ["организована", "проведена", "осуществлена"],
    ),
    ("violator", "нарушителя"): (
        ["violator", "transgressor", "offender"],
        ["нарушителя", "правонарушителя"],
    ),
    ("material resources", "материальные ресурсы"): (
        ["material assets", "physical resources", "tangible resources"],
        ["материальные ресурсы", "вещественные ресурсы"],
    ),
    ("mass media", "средства массовой информации"): (
        ["mass media", "media", "press and broadcast", "news media"],
        ["СМИ", "средства массовой информации", "масс-медиа"],
    ),
    ("consumer goods", "промышленными товарами"): (
        ["consumer products", "manufactured goods", "commodities"],
        ["потребительские товары", "промышленные товары"],
    ),
    ("carried out", "осуществили"): (
        ["implemented", "conducted", "performed", "executed"],
        ["осуществили", "провели", "выполнили"],
    ),
    ("citizens", "граждан"): (
        ["citizens", "nationals", "inhabitants", "residents"],
        ["граждане", "граждан", "население"],
    ),
    ("cinema", "кино"): (
        ["cinema", "film", "motion pictures", "movies"],
        ["кино", "кинематограф", "кинопрокат"],
    ),
    ("centers of ideological subversion", "центров идеологической диверсии"): (
        ["centers of ideological sabotage", "ideological subversion centers", "propaganda centers"],
        ["центров идеологической диверсии", "центров идеологической диверсии"],
    ),
    ("ceased unlawful activities", "прекратил противоправную деятельность"): (
        ["ceased illegal activities", "discontinued unlawful conduct", "stopped illicit activities"],
        ["прекратил противоправную деятельность", "прекратил противозаконную деятельность"],
    ),
    ("committed crimes", "совершивших преступления"): (
        ["who committed offenses", "perpetrators", "criminal offenders"],
        ["совершивших преступления", "преступников", "правонарушителей"],
    ),
    ("in accordance with", "В соответствии с"): (
        ["pursuant to", "in compliance with", "in conformity with"],
        ["В соответствии с", "Согласно", "Во исполнение"],
    ),
    ("in a correctional labor colony", "в исправительно-трудовой колонии"): (
        ["in a corrective labor colony", "in a labor camp", "in penal colony"],
        ["в исправительно-трудовой колонии", "в ИТК", "в колонии"],
    ),
    ("in an intoxicated state", "в нетрезвом состоянии"): (
        ["while intoxicated", "under the influence", "in a state of inebriation"],
        ["в нетрезвом состоянии", "в состоянии алкогольного опьянения"],
    ),
    ("in connection with", "в связи с"): (
        ["in connection with", "with regard to", "concerning", "pursuant to"],
        ["в связи с", "в отношении", "по поводу"],
    ),
    ("in coordination with", "по согласованию с"): (
        ["in coordination with", "in concert with", "with the approval of"],
        ["по согласованию с", "во взаимодействии с"],
    ),
    ("special measures", "специальных мероприятий"): (
        ["special measures", "targeted measures", "operational measures", "special operations"],
        ["специальные мероприятия", "оперативные мероприятия", "целевые меры"],
    ),
    ("state security", "госбезопасности"): (
        ["state security", "state security organs", "internal security"],
        ["госбезопасность", "органы госбезопасности", "государственная безопасность"],
    ),
    ("Committee for State Security", "Комитетом госбезопасности"): (
        ["State Security Committee", "KGB", "Committee for State Security of the republic"],
        ["Комитет госбезопасности", "КГБ", "органы КГБ"],
    ),
    ("KGB", "КГБ"): (
        ["State Security Committee", "Committee for State Security", "security services"],
        ["КГБ", "Комитет госбезопасности", "органы госбезопасности"],
    ),
    ("anti-Soviet", "антисоветской"): (
        ["anti-Soviet", "hostile to the Soviet Union", "anti-communist"],
        ["антисоветская", "враждебная СССР", "антикоммунистическая"],
    ),
    ("reactionary circles", "реакционные круги"): (
        ["reactionary circles", "reactionary forces", "conservative circles"],
        ["реакционные круги", "реакционные силы", "консервативные круги"],
    ),
    ("perestroika", "перестройки"): (
        ["perestroika", "restructuring", "reform policy"],
        ["перестройка", "реструктуризация", "политика реформ"],
    ),
    ("Abroad", "за рубежом"): (
        ["overseas", "abroad", "in foreign countries", "externally"],
        ["за рубежом", "за границей", "в зарубежных странах"],
    ),
    ("abroad", "за рубежом"): (
        ["overseas", "abroad", "in foreign countries"],
        ["за рубежом", "за границей", "вне страны"],
    ),
    ("[about this] in the near future", "в ближайшее время"): (
        ["in the immediate future", "shortly", "soon"],
        ["в ближайшее время", "в скором времени"],
    ),
    ("[Also present are] the Assistant Military Attaché", "помощник военного атташе"): (
        ["Deputy Military Attaché", "Assistant Military Attaché"],
        ["помощник военного атташе", "заместитель военного атташе"],
    ),
    ("[they were] recovered", "изъяты"): (
        ["seized", "confiscated", "impounded", "retrieved"],
        ["изъяты", "конфискованы"],
    ),
    ("[but are] unfit for use", "к эксплуатации непригодны"): (
        ["unsuitable for use", "unserviceable", "inoperable"],
        ["непригодны к эксплуатации", "неисправны"],
    ),
    ("a detained border violator", "задержанного им нарушителя границы"): (
        ["apprehended border violator", "detained illegal crosser"],
        ["задержанного нарушителя границы", "арестованного незаконного пересекателя"],
    ),
    ("a leaflet", "листовку"): (
        ["a handbill", "a flyer", "a leaflet"],
        ["листовка", "воззвание"],
    ),
    ("a long-term character", "долговременный характер"): (
        ["lasting nature", "permanent character", "enduring nature"],
        ["долговременный характер", "длительный характер"],
    ),
    ("a member of the Komsomol", "член ВЛКСМ"): (
        ["Komsomol member", "Young Communist League member"],
        ["член ВЛКСМ", "комсомолец", "член комсомола"],
    ),
    ("According to operational data", "По оперативным данным"): (
        ["According to operational intelligence", "Per operational information"],
        ["По оперативным данным", "По оперативной информации"],
    ),
    ("According to operational data received", "По полученным оперативным данным"): (
        ["Per received operational intelligence", "According to operational reports"],
        ["По полученным оперативным данным", "По оперативным сводкам"],
    ),
    ("According to operational data obtained", "По полученным оперативным данным"): (
        ["Per obtained operational intelligence", "According to operational reports"],
        ["По полученным оперативным данным", "По оперативным данным"],
    ),
    ("according to preliminary data", "по предварительным данным"): (
        ["per preliminary data", "according to initial reports"],
        ["по предварительным данным", "по первичным данным"],
    ),
    ("a collision occurred", "произошло столкновение"): (
        ["a collision occurred", "an accident occurred", "an impact took place"],
        ["произошло столкновение", "произошел инцидент"],
    ),
    ("a collision occurred", "произошло их столкновение"): (
        ["a collision occurred", "their collision occurred"],
        ["произошло столкновение", "произошел их столкновение"],
    ),
    ("a border patrol discovered", "пограничным нарядом были обнаружены"): (
        ["discovered by border guards", "found by frontier patrol"],
        ["обнаружены пограничным нарядом", "выявлены пограничниками"],
    ),
    ("a gathering organized [...] took place", "состоялось организованное [...] сборище"): (
        ["an organized gathering took place", "a staged assembly occurred"],
        ["состоялось организованное сборище", "произошло организованное собрание"],
    ),
}

# Patterns that indicate proper noun, title, or unclear -> use []
PROPER_NOUN_PATTERNS = [
    r'^["\u00ab\u201c].*["\u00bb\u201d]$',  # Quoted text (document titles)
    r'^\(?\d+[,\s\d]*\)?$',  # Pure numbers
    r'^\d+[\s,]*\d+.*(чел\.|persons?|foreigners?|students?)$',  # Stats with numbers
    r'^[A-Z][a-z]+ [A-Z][a-z]+$',  # Likely proper name
    r'^[A-Z]\.[A-Z]\.',  # Initials
    r'\[\.\.\.\].*\[\.\.\.\]',  # Fragments with ...
]
PROPER_NOUN_RE = re.compile('|'.join(f'({p})' for p in PROPER_NOUN_PATTERNS))

# Lazy-loaded WordNet and wiki-synonyms (avoid import/time cost if not used)
_wordnet = None
_wiki_synonyms = None


def _get_wordnet():
    global _wordnet
    if _wordnet is None:
        try:
            import nltk
            for resource in ("wordnet", "omw-1.4"):
                nltk.download(resource, quiet=True)
            from nltk.corpus import wordnet as wn
            _wordnet = wn
        except Exception:
            _wordnet = False
    return _wordnet


def _get_wiki_synonyms():
    global _wiki_synonyms
    if _wiki_synonyms is None:
        try:
            from wiki_synonyms import DataWorker
            _wiki_synonyms = DataWorker()
        except Exception:
            _wiki_synonyms = False
    return _wiki_synonyms


def _english_synonyms_api(text: str, max_out: int = 5) -> list[str]:
    """Get English synonyms via NLTK WordNet. Handles single words and phrases."""
    wn = _get_wordnet()
    if wn is False:
        return []
    text = (text or "").strip()
    if not text or len(text) > 80:
        return []
    words = re.findall(r"[a-zA-Z]+", text.lower())
    seen = set()
    out = []
    for w in words:
        if w in _EN_STOP or len(w) < 3:
            continue
        for synset in wn.synsets(w):
            for lemma in synset.lemma_names():
                cand = lemma.replace("_", " ").lower()
                if cand != w and cand not in seen:
                    seen.add(cand)
                    out.append(cand)
                    if len(out) >= max_out:
                        return out
    return out[:max_out]


def _get_rusynonyms_graph():
    """Lazy-load rusynonyms SynonymsGraph."""
    if not hasattr(_get_rusynonyms_graph, "_sg"):
        try:
            from ru_synonyms import SynonymsGraph
            _get_rusynonyms_graph._sg = SynonymsGraph()
        except Exception:
            _get_rusynonyms_graph._sg = False
    return _get_rusynonyms_graph._sg


def _russian_synonyms_api(text: str, max_out: int = 5) -> list[str]:
    """Get Russian synonyms: wiki-synonyms first, then rusynonyms per word."""
    text = (text or "").strip()
    if not text or len(text) > 100:
        return []
    out = []
    seen = {text.lower()}
    dw = _get_wiki_synonyms()
    if dw is not False:
        try:
            elements = dw.get_elements_by_synonym(text)
            if elements:
                for el in (elements if isinstance(elements, (list, tuple)) else list(elements)):
                    s = (el if isinstance(el, str) else str(el)).strip()
                    if s and s.lower() not in seen:
                        seen.add(s.lower())
                        out.append(s)
                        if len(out) >= max_out:
                            return out[:max_out]
        except Exception:
            pass
    sg = _get_rusynonyms_graph()
    if sg is not False:
        for w in re.findall(r"[\u0400-\u04ff]+", text):
            if len(w) < 2:
                continue
            try:
                if sg.is_in_dictionary(w):
                    for syn in sg.get_list(w):
                        s = (syn if isinstance(syn, str) else str(syn)).strip()
                        if s and s.lower() not in seen:
                            seen.add(s.lower())
                            out.append(s)
                            if len(out) >= max_out:
                                return out[:max_out]
            except Exception:
                pass
    return out[:max_out]


def _is_proper_or_unclear(eng: str, rus: str) -> bool:
    """Return True if term should get empty synonym arrays."""
    e = (eng or "").strip()
    r = (rus or "").strip()
    if not e and not r:
        return True
    s = e or r
    # Document titles in quotes
    if s.startswith('"') or s.startswith('\u201c') or s.startswith('\u00ab'):
        return True
    # Mostly numbers
    if re.match(r'^[\d\s,\.\(\)]+$', s):
        return True
    # Very long sentence fragments (often incomplete)
    if len(s) > 120:
        return True
    # Bracketed fragments that are clearly incomplete
    if s.startswith('[') and ']' in s[:30] and len(s) < 50:
        return True
    # Single word that is a number
    if s.isdigit():
        return True
    return False


def get_synonyms(entry_eng: str, entry_rus: str) -> tuple[list[str], list[str]]:
    """Return (synonyms_eng, synonyms_rus) for the term."""
    eng = (entry_eng or "").strip()
    rus = (entry_rus or "").strip()
    if _is_proper_or_unclear(eng, rus):
        return ([], [])

    key = (eng, rus)
    if key in SYNONYM_MAP:
        return SYNONYM_MAP[key]
    key_lower = (eng.lower(), rus.lower())
    for (e, r), val in SYNONYM_MAP.items():
        if e.lower() == key_lower[0] and r.lower() == key_lower[1]:
            return val

    syn_eng = _english_synonyms_api(eng, max_out=5)
    syn_rus = _russian_synonyms_api(rus, max_out=5)
    return (syn_eng, syn_rus)


def main() -> int:
    terms_path = ROOT / "data" / "output" / "terms_for_synonyms.json"
    out_path = ROOT / "config" / "term_synonyms.json"

    if not terms_path.exists():
        print(f"Not found: {terms_path}")
        print("Run: python scripts/export_terms_for_synonyms.py")
        return 1

    with open(terms_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    terms = data.get("terms", [])
    term_synonyms = []
    with_synonyms = 0

    for t in terms:
        entry_eng = t.get("entry_eng", "")
        entry_rus = t.get("entry_rus", "")
        syn_eng, syn_rus = get_synonyms(entry_eng, entry_rus)
        if syn_eng or syn_rus:
            with_synonyms += 1
        term_synonyms.append({
            "entry_eng": entry_eng,
            "entry_rus": entry_rus,
            "synonyms_eng": syn_eng[:5],
            "synonyms_rus": syn_rus[:5],
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"term_synonyms": term_synonyms}, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(term_synonyms)} entries to {out_path}")
    print(f"Terms with synonyms: {with_synonyms}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
