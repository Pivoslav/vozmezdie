#!/usr/bin/env python3
"""
Run experiment for first document only: use agent judgements as LLM output,
load ground truth from HTML, compare, generate report.
Usage: python run_experiment_first_doc.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


# Agent judgements for doc 1127 from reading the Russian original (data/russian_originals/1127.txt).
# No ground truth consulted. entry_rus is filled so content_rus matching can align to GT.
# Format: section, entry_eng, entry_rus, content_category, framing, context.
AGENT_JUDGEMENTS_1127 = [
    {"section": 1, "entry_eng": "CENTRAL COMMITTEE OF THE COMMUNIST PARTY OF UKRAINE", "entry_rus": "ЦЕНТРАЛЬНЫЙ КОМИТЕТ КОММУНИСТИЧЕСКОЙ ПАРТИИ У К Р А И Н Ы", "content_category": "Actors", "framing": "Institutional / Bureaucratic Lingo", "context": "Header of the information note."},
    {"section": 2, "entry_eng": "9,582 foreigners from capitalist and developing countries", "entry_rus": "На территории Украинской ССР находятся 9582 иностранца из капиталистических и развивающихся стран", "content_category": "Information", "framing": "Generic / Neutral Language", "context": "Statistics on the territory of the Ukrainian SSR."},
    {"section": 3, "entry_eng": "U.S. Embassy in Moscow M. Spengler", "entry_rus": "сотрудник посольства США в Москве М.Спэнглер", "content_category": "Actors", "framing": "Generic / Neutral Language", "context": "Introductory visit in Kyiv."},
    {"section": 4, "entry_eng": "Ukrainian Society for Cultural Relations with Foreign Countries", "entry_rus": "Украинское общество культурных связей с зарубежными странами", "content_category": "Actors", "framing": "Generic / Neutral Language", "context": "Delegation members from Canada and Japan arrived there."},
    {"section": 5, "entry_eng": "On Measures to Discredit Ukrainian Bourgeois Nationalists Abroad", "entry_rus": "О мерах по компрометации украинских буржуазных националистов за рубежом", "content_category": "Context and Concepts", "framing": "Ideological Framing (Discrediting)", "context": "Section title on KGB disinformation campaign."},
    {"section": 6, "entry_eng": "KGB efforts documenting the criminal activities", "entry_rus": "проведенной органами КГБ документации преступной деятельности", "content_category": "Actions", "framing": "Institutional / Bureaucratic Lingo", "context": "Reports No. 364/sv and 366/sv."},
    {"section": 7, "entry_eng": "war criminals", "entry_rus": "военных преступников", "content_category": "Status and Condition", "framing": "Ideological Framing (Discrediting)", "context": "Individuals in the U.S. who had participated in atrocities."},
    {"section": 8, "entry_eng": "So That We Do Not Forget", "entry_rus": "Чтобы мы не забыли", "content_category": "Documents", "framing": "Ideological Phrasing (Normalizing)", "context": "Book revised for Canadian readers, published in Toronto."},
    {"section": 9, "entry_eng": "Ukrainian bourgeois nationalists who had settled in Canada", "entry_rus": "осевших в Канаде украинских буржуазных националистов", "content_category": "Actors", "framing": "Ideological Framing (Discrediting)", "context": "Target of discredit campaign."},
    {"section": 10, "entry_eng": "D. Hanusiak held a press conference", "entry_rus": "Д.Ганусяк провел пресс-конференцию", "content_category": "Events", "framing": "Action-Focused Language", "context": "To popularize the book with progressive press and Canadian television."},
    {"section": 11, "entry_eng": "progressive Ukrainian, Jewish, and other émigré press", "entry_rus": "прогрессивной украинской, еврейской и другой эмигрантской печати", "content_category": "Actors", "framing": "Ideological Phrasing (Normalizing)", "context": "Audience of the press conference."},
    {"section": 12, "entry_eng": "Soviet propaganda", "entry_rus": "советской пропагандой", "content_category": "Information", "framing": "Ideological Framing (Discrediting)", "context": "A. Bandera's characterization of the book."},
    {"section": 13, "entry_eng": "OUN in crimes, committed by the Hitlerites", "entry_rus": "соучастие ОУН в преступлениях гитлеровцев", "content_category": "Context and Concepts", "framing": "Ideological Framing (Discrediting)", "context": "Facts cited in the book exposing complicity."},
    {"section": 14, "entry_eng": "Berdychiv District Communications Node", "entry_rus": "начальник Бердичевского районного узла связи Пустовик Н.Н.", "content_category": "Places", "framing": "Generic / Neutral Language", "context": "Handed over a sheet to KGB."},
    {"section": 15, "entry_eng": "city KGB office", "entry_rus": "горотдел КГБ", "content_category": "Actors", "framing": "Institutional / Bureaucratic Lingo", "context": "Measures to identify the person who committed the act."},
    {"section": 16, "entry_eng": "insulting remarks directed at one of the CPSU Central Committee leaders", "entry_rus": "оскорбительные выпады в отношении одного из руководителей ЦК КПСС", "content_category": "Actions", "framing": "Ideological Framing (Discrediting)", "context": "Handwritten text on the sheet."},
    {"section": 17, "entry_eng": "Chumka substation", "entry_rus": "подстанции Чумка", "content_category": "Places", "framing": "Generic / Neutral Language", "context": "Short circuit on high-voltage power line."},
    {"section": 18, "entry_eng": "Deputy Head of the Odesa District Substation K. K. Usachov", "entry_rus": "заместителя начальника Одесской районной электроподстанции Усачева К.С.", "content_category": "Actors", "framing": "Institutional / Bureaucratic Lingo", "context": "Violated switching procedure; accident investigation."},
    {"section": 19, "entry_eng": "military unit 12472", "entry_rus": "войсковой части 12472", "content_category": "Places", "framing": "Generic / Neutral Language", "context": "Stationed in village of Davydkivtsi, Khmelnytskyi district."},
    {"section": 20, "entry_eng": "Private V. N. Karimov", "entry_rus": "рядовой Каримов В.Н.", "content_category": "Actors", "framing": "Generic / Neutral Language", "context": "Left post with rifle and ammunition; desertion."},
    {"section": 21, "entry_eng": "Desertion with Weapons", "entry_rus": "Дезертирство с оружием", "content_category": "Events", "framing": "Action-Focused Language", "context": "Section heading, Khmelnytskyi Oblast."},
    {"section": 22, "entry_eng": "KGB under the USSR Council of Ministers", "entry_rus": "КГБ при СМ СССР", "content_category": "Actors", "framing": "Institutional / Bureaucratic Lingo", "context": "Informed of desertion and of personnel incident."},
    {"section": 23, "entry_eng": "Senior Lieutenant Vitalii Yemelyanovich Kobyzyev", "entry_rus": "оперуполномоченный Киевского райотдела КГБ старший лейтенант Кобызев Виталий Емельянович", "content_category": "Actors", "framing": "Generic / Neutral Language", "context": "Operative officer of Kyiv District KGB Office."},
    {"section": 24, "entry_eng": "died by suicide through hanging", "entry_rus": "покончивший жизнь самоубийством путем повешения", "content_category": "Events", "framing": "Generic / Neutral Language", "context": "Personnel incident, Kharkiv."},
    {"section": 25, "entry_eng": "V. FEDORCHUK", "entry_rus": "В.ФЕДОРЧУК", "content_category": "Actors", "framing": "Institutional / Bureaucratic Lingo", "context": "Chairman of the State Security Committee under the Council of Ministers of the Ukrainian SSR."},
]


def main() -> int:
    config_path = ROOT / "config" / "pipeline_config.example.json"
    if not config_path.exists():
        print("Config not found:", config_path)
        return 1
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    from run import load_taxonomy
    taxonomy = load_taxonomy(config)

    from ingest import run as ingest_run
    documents = ingest_run(config, ROOT)
    if not documents:
        print("No documents from ingest.")
        return 1
    first_doc = documents[0]
    doc_id = first_doc.get("document_id", "")
    if not doc_id:
        print("First document has no document_id.")
        return 1

    # Restrict to first document only for this experiment
    documents = [first_doc]
    document_ids = [doc_id]

    llm_by_doc = {doc_id: AGENT_JUDGEMENTS_1127}
    from ground_truth import run as gt_run
    gt_by_doc = gt_run(config, document_ids)

    from compare import run as compare_run
    comparison_by_doc = compare_run(llm_by_doc, gt_by_doc, config)

    out_config = config.get("output", {})
    out_dir = ROOT / out_config.get("dir", "data/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / out_config.get("intermediate_json", "comparison_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"documents": documents, "comparison_by_doc": comparison_by_doc}, f, indent=2, ensure_ascii=False)
    print("Saved:", json_path)

    from report import run as report_run
    out_path = report_run(comparison_by_doc, documents, taxonomy, config)
    print("Report:", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
