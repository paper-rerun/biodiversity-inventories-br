# Build schema.json for the biodiversity pilot (Darwin Core occurrences, transcribed as printed)
# Usage: python -I method/build_schema.py   (writes schema.json next to the method folder)
import json, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "schema.json"


def text(description, nullable=True, **extra):
	field = {"description": description, "type": ["string", "null"] if nullable else "string"}
	field.update(extra)
	return field


def page(description="PDF page (from 1) where this is printed; null when the value is null."):
	return {"description": description, "type": ["integer", "null"], "minimum": 1}


def integer(description, nullable=False, minimum=0):
	return {"description": description, "type": ["integer", "null"] if nullable else "integer", "minimum": minimum}


def obj(required, properties, description=None):
	result = {"type": "object", "additionalProperties": False, "required": required, "properties": properties}
	if description:
		result = {"description": description, **result}
	return result


RULES = [
	"1 SCOPE. Inventory and transcribe every page of the document, except when sources.json gives extract_pages for it. Then only those pages go to tables[] and records[]; the rest is read only to fill events[] (methods, site descriptions, dates, effort).",
	"2 INVENTORY FIRST, EVERY ENTRY. Before writing any record, render every page in scope and list in tables[], in page order, every table, annex and figure of the document (photo, map, scheme, profile, curve, chart and dendrogram included, whether or not it names a taxon) and every text block that ties a taxon to an event of this study (rule TEXT RECORDS), with table_id, page, label, kind and the number of data cells. An entry with no taxon cell is still listed, with data_cells = 0. A table continued on the next page gets one entry per page, each with its own count and its own event_ids: only the events that have a cell on that page. At the end fill transcribed and skipped_cells: data_cells = transcribed + skipped_cells and transcribed = number of records with that table_id. A document is not finished until every entry closes. Rules FIGURES and TABLES THAT GIVE NO RECORDS only say which kind an entry takes and whether it gives records; what enters the inventory is this rule.",
	"3 Read names and numbers from the rendered page, not only from the text layer. The printed page is the source: text layers of typewritten scans and two-column journals drop letters, split words and misplace columns ('FamOia' for 'Família', a name broken over three lines). Render at 150 dpi; go up only for one unreadable character.",
	"4 EVENTS FIRST. One events[] entry per site or sampling event the document distinguishes: a study-wide event for the whole survey, then one per site, point, plot, transect, fragment, farm, habitat or stratum that has its own column, code or table, and one per campaign or date block when the tables split the data by campaign. Children point to their parent in parent_event_id. A record always points to the most specific event its cell belongs to. Fix the event structure before writing records.",
	"5 EVENT FIELDS ONCE, WITH PAGE. Fill each event field from wherever the document prints it (methods, site table, caption, footnote, figure legend, abstract) and put the page in field_pages. verbatimLocality, verbatimEventDate and samplingEffort keep only the stretch that is the locality, the date or the effort, at most 15 words: not the sentence around it, and not the municipality or state, which have their own fields. A field printed once for the whole survey goes on the study event and the children inherit it; a child only repeats it when its own value differs. Use null only when the document prints it nowhere. Never take a locality from the authors' affiliation, the publisher's address or the series name: Embrapa Pantanal, Corumbá is the publisher, not the site.",
	"6 COORDINATES AS PRINTED. verbatimCoordinates is the printed text exactly, with degree, minute and second signs, hemisphere letters ('O' or 'W') and separators as printed ('18°14'10\"S - 55°40'41\"O'). decimalLatitude and decimalLongitude are filled only when the document prints the coordinate in decimal degrees, and then they copy it. Never convert degrees-minutes-seconds, UTM or a map position to decimal, never add a missing sign or hemisphere, never fix a coordinate that falls outside the site: write the conflict in source_inconsistency. geodeticDatum and verbatimCoordinateSystem only when printed.",
	"7 DATES AS PRINTED. verbatimEventDate is the printed text ('entre março e junho de 2013', 'novembro de 1993 e janeiro de 1994', 'dezembro a março de 1981', '2004'). Never normalize it to ISO, never infer a year from the publication year, the received date or a citation. A date printed only as the publication or edition year is not an event date.",
	"8 TABLE AXES BEFORE RECORDS. For every entry that gives records, fill table_level_labels before any record: what the rows are (taxa, with or without heading rows for order, family or subfamily), what the columns are (events, attributes of the taxon, derived metrics, totals), how the presence of a taxon at an event is shown (number, mark, list of event codes, source codes) and how absence is shown. Then fill columns[]: one entry per printed column with its header as printed and its role (rule COLUMN ROLES).",
	"9 COLUMN ROLES, closed examples. taxon_name = the name column; family, order, vernacular, authorship = those printed columns; event_count = a column of one event that prints numbers per taxon (N, número de indivíduos, capturas, abundância of one point or plot); event_mark = a column of one event that prints presence or absence marks (X, -, +, 1/0); event_code_list = one column whose cell lists the codes of the events where the taxon occurs ('PB5; CSU', '1, 2, 3, 14'); event_source_codes = a column of one event whose cell lists source or record-type codes ('Ta Tb n t w l'); event_quantity_other = a column of one event that prints a quantity that is not a count (frequência %, density, cover) and is the only quantity printed for that taxon at that event; attribute = a per-taxon trait or remark printed in a column (hábito, guilda, horário de atividade, habitat type, status migratório, estratégia reprodutiva, forma de registro, usos); threat_status = a conservation status column; voucher = collector number or collection acronym; derived_metric = values the authors computed from counts (DR, DA, FR, FA, DoA, DoR, IVI, IVC, área basal, % relative abundance, constância, índices); total = sums across events or across taxa; event_taxon_list = a column of a table whose rows and columns are both parts of the sampling (day x hour, trap x night) and whose cells list the taxa seen, with a count in parentheses ('Saguinus labiatus (5)'). event_* columns carry event_id; derived_metric and total cells are counted as data cells and skipped.",
	"10 ONE RECORD PER PRINTED TAXON-BY-EVENT CELL OR LIST LINE. An event_count, event_mark or event_quantity_other cell that holds something gives one record. An event_code_list cell gives one record per code it lists, and an event_source_codes cell one record per source code it lists (rule WHO RECORDED IT); each code counts as one data cell. An event_taxon_list cell gives one record per taxon it lists, in printed order (position_in_cell), each counting as one data cell; event_id is the row's event and event_detail_as_printed holds only what the column header or the row header of that cell prints ('7h-8h'), never the label of the block above it ('Manhã / 7h-8h' is wrong). A species list with no event columns gives one record per taxon line, tied to the event the list describes (the study event when the caption or methods tie it to nothing narrower). A taxon printed in two tables gives a record in each, with the same event only when the tables are about the same event; say so in notes.",
	"11 BLANK IS NOT ABSENT. A blank cell is not a data cell and gives no record. occurrenceStatus = 'absent' only when the table prints a mark that its legend or the methods define as absence ('( - ) ausente'), or prints 0 in a count column; then the cell is a data cell and gives a record. A '-' without such a legend is not a data cell. occurrenceStatus = 'present' for every count above 0, every presence mark, every code listed and every list line.",
	"12 NAMES EXACTLY AS PRINTED. verbatimScientificName holds the name as printed in that cell or line, with authorship and year when printed with it, with its punctuation, spacing, typos and old spellings ('Bufo paracnemis (lutz, 1934)', 'Ceratophrys cranvelly', 'Hoplias gr. malabaricus (Bloch 1794)'). Never correct, complete, update or split a name, never add authorship, never resolve it against a taxonomic backbone or a list; that is a later step outside the transcription. A name broken over lines is joined with single spaces. ABBREVIATED GENUS: when the cell prints the genus abbreviated ('A. pyrifolium', 'C. férrea') and the same document prints the full name in another table or list, verbatimScientificName keeps the abbreviated name and name_in_full_as_printed copies the full name as printed there, with its page in name_in_full_page; otherwise both stay null. NO SPECIES NAME: when the name cell holds only authorship ('Isbrucker e Nijssen 1979'), only '-' or only a Portuguese group name ('Tinamídeo'), the record stays, verbatimScientificName copies the cell as printed, name_status = 'incomplete_in_print', and a group name also goes to vernacularName. name_status is null for every other record.",
	"13 QUALIFIERS AS PRINTED. identificationQualifier copies the qualifier printed in the name ('cf.', 'aff.', 'sp.', 'spp.', 'sp. aff.', 'gr.', 'sp. 1', 'sp. n.'), exactly as printed, and verbatimScientificName still keeps it. Morphospecies and undetermined rows ('Indeterminada 1', 'Euglossa sp.', 'Morfoespécie 3') are records like any other.",
	"14 HIGHER TAXA ONLY AS PRINTED. family and order are filled only when printed: in their own column, or in a heading row above the taxon. Write the name as printed without the rank word in front of it: the heading 'Família Anostomidae' gives family_as_printed = 'Anostomidae' and 'ORDEM CHARACIFORMES' gives order_as_printed = 'CHARACIFORMES' (case kept as printed); a heading with no rank word ('Tinamidae') is copied whole. family_source and order_source say 'column' or 'heading_row'. A heading row is not a data cell. Never infer a family or order from the genus. higher_group_as_printed holds any other printed heading the taxon sits under (subfamily, class, 'Anfíbios', 'Mamíferos').",
	"15 VERNACULAR NAME as printed in the line or column ('Jararaquinha', 'aracuã-do-pantanal', 'Aroeira'), never from another source.",
	"16 QUANTITY AS PRINTED. individualCount takes the printed integer when the column or methods say it counts individuals or specimens (N = número de indivíduos, exemplares, indivíduos capturados). Every other quantity goes to organismQuantity with organismQuantityType copied from the header or legend as printed ('número de capturas', 'Frequência %', 'NP por classe de tamanho III'); never translate it to a Darwin Core vocabulary. organismQuantityType and header_as_printed copy the whole header, every word down to its last line, never cut in the middle ('FREQUÊNCIA CORRIGIDA' alone is wrong when the header goes on). value_as_printed keeps the printed text. The only allowed changes in the numeric fields are decimal comma to point and dropping a thousands point. Never compute, sum, convert or derive a quantity. A value the authors print next to the count in parentheses ('43 (22,4)', a percentage or a standard error) is not a separate cell or record: value_as_printed keeps the whole cell, the count goes to its field, and the column notes say what the parenthesis is.",
	"17 CODES AND SYMBOLS. Every code, letter, symbol or mark in a cell ('X', '*', 'VA2', 'Ta', 'n', 'Re', 'Cp,Ba', 'v (f)') goes to printed_code exactly as printed in that cell. Its meaning is written once, not on the record: table_level_labels.symbols lists every symbol of the table with its meaning (at most 15 words), page and place, and the merge joins it to the records by the code. A code with no printed meaning is listed with meaning_as_printed = null, and in end_checklist.codes as undefined. A code that names an event (rule 10) also sets event_id.",
	"18 WHO RECORDED IT. record_origin says what the document prints about the source of that record: this_study (the authors' own field work, 'este estudo', 'dados de campo de'), cited_source (a reference or another author, 'Fonte: Ta (TUBELIS; TOMAS 1999)'), collection (a specimen in a named collection), not_stated. A cell that joins sources ('Ta Tb n t', field codes of this study next to codes of a cited work) gives one record per source code, each with that single code in printed_code and its own record_origin, so the records of this study can be published apart from the literature; each code counts as one data cell. cited_source_as_printed holds the printed code or reference. recording_method_as_printed holds the printed method of that record ('v (identificação visual)', 'captura em rede', 'armadilha luminosa'), else null; samplingProtocol of the event holds the method for the whole event. MATERIAL FATE: the study event fills material_fate_as_printed with what the document prints about the fate of the material (at most 15 words: 'identificados no campo, fotografados e soltos', 'depositado na coleção CPAC') with its page in field_pages, and material_fate with its class: deposited_in_collection (the records are specimens kept in a named collection), released_or_observed (seen, heard, caught and released, plot tally), vouchers_not_tied_to_records (some vouchers kept, but the document ties no table row to them, or they only checked the identification), not_stated. A child event fills them only when its material differs. Never write basisOfRecord: the merge converts material_fate.",
	"19 STATUS AS PRINTED. A conservation status printed for the taxon (column, symbol or footnote: 'VU', 'Vulnerável (MMA, 2014)', 'EN', 'nc') goes to threat_status_as_printed with the list or authority as printed in threat_status_source_as_printed. Migratory or residence status ('Re', 'Intra') is an attribute, not a threat status.",
	"20 ATTRIBUTES PER LINE. Per-taxon columns that are neither name nor occurrence (hábito, guilda, horário de atividade, habitat of the taxon, estratégia reprodutiva, usos, tamanho máximo) go to line_attributes on every record of that line, one item per column with column_id and the value as printed. Their cells are data cells only when the table has no event columns and they are the only content of the line; otherwise they are attributes and are not counted.",
	"21 DERIVED VALUES ARE NOT OCCURRENCES. Relative abundance, density, frequency and dominance computed by the authors (DR, DA, FA, FR, DoA, DoR, IVI, IVC, área basal, % of total, constância de ocorrência), totals across events, totals per family, richness, diversity and similarity indices, rarefaction and estimator values are counted as data cells and skipped, never recorded, with the reason in skipped_reason. A per-event frequency or percentage is recorded only when it is the only quantity the document prints for that taxon at that event (rule COLUMN ROLES, event_quantity_other).",
	"22 TOTAL ROWS AND SUMMARY TABLES. A 'Total' row or column is counted and skipped. A table that prints only counts per family, order or habitat, or richness per site, is kind = summary: inventoried, cells counted, all skipped.",
	"23 TEXT RECORDS. A taxon tied to an event of this study only in the body text ('Eulaema mocsary foi capturada apenas na capoeira') is a mandatory record when no table or annex prints it for that event: table_or_figure = 'text', one tables[] entry with label 'text' per page, the quote in notes. A taxon named in the text without an event of this study, in a discussion or a comparison with other surveys, is not a record. A text mention that repeats a table cell is not recorded again.",
	"24 FIGURES. Every figure is in the inventory (rule INVENTORY FIRST, EVERY ENTRY). It gives records only when it prints taxon names with a value or mark per event (kind = figure_labeled). Photos, maps, schemes, profiles, rarefaction curves, dendrograms and bar charts without printed values take kind = figure_unlabeled and data_cells = 0; a photo caption that names a taxon gives no record.",
	"25 TABLES THAT GIVE NO RECORDS. Every table is in the inventory (rule INVENTORY FIRST, EVERY ENTRY). Site tables (coordinates, habitat, effort), soil, weather, method and key tables take kind = event_context, context, or legend and data_cells = 0; their content goes to events[] or table_level_labels. Tables from other studies printed for comparison (lists of other surveys, similarity with other areas) are kind = comparison, cells counted and skipped.",
	"26 CONTRADICTIONS. When the document contradicts itself (text against table, a name spelled two ways, a coordinate that does not fall in the named municipality, a total that does not match its rows, a date in the abstract against the methods, a species in the text missing from the list), record what the table prints and fill source_inconsistency with both versions and pages. Put it on the record when it is about that cell, on the event when it is about the site, on table_level_labels when it is about the table. A name spelled one way in a table and another way in another table, figure or page goes on every record of that name, in every table where it appears, each with both spellings and pages: check every name of a figure against the list before closing.",
	"27 ILLEGIBLE CELLS STAY IN. A cell or line that holds something but cannot be read with confidence is a record with value_kind = 'illegible', the best reading in value_as_printed or verbatimScientificName, and the doubt in notes. It counts as transcribed.",
	"28 page is the PDF page number counted from 1 (first page of the file = 1), not the number printed on the page. table_or_figure is the label as printed ('Tabela 2', 'Anexo I', 'Continuação do Anexo I', 'text').",
	"29 notes, source_inconsistency, meaning_as_printed and every other free-text field quote at most 15 words of the document. NO GLOSS IN PRINTED FIELDS: a field that copies the print (the _as_printed fields, the verbatim* fields, samplingEffort, samplingProtocol, habitat, organismQuantityType, vernacularName) holds only printed text. Our context, a page reference or a comment ('(por ponto por campanha, p7)') goes to notes, never inside it.",
	"30 TWO INDEPENDENT TRANSCRIPTIONS. Each document is transcribed twice, by A and B, each without seeing the other. A script diffs A and B record by record (key: table_id, row_index, position_in_cell, event_id, printed_code) and field by field, and an adjudicator decides every difference against the rendered page. Write transcriber = 'A' or 'B'.",
	"31 END-OF-TRANSCRIPTION CHECKLIST. Before closing, fill end_checklist. events: one entry per event and per field in its enum, filled, inherited (from the parent, page of the parent) or not_printed. tables: one entry per entry that gives records, with the symbols found in the cells against the symbols listed with meaning, the heading rows carried to family or order, the event columns with event_id, and the derived or total cells skipped. rows: per table, the taxon lines printed against the distinct row_index values in records, and rows_match. codes: every printed code with its meaning or 'undefined'. totals: the sums over tables[] and the record count, with every_table_closes true only when each entry closes.",
]

EVENT_FIELDS = ["verbatimLocality", "municipality", "stateProvince", "country", "verbatimCoordinates", "decimalLatitude", "decimalLongitude", "geodeticDatum", "verbatimElevation", "verbatimEventDate", "habitat", "samplingProtocol", "samplingEffort", "sampleSize", "material_fate_as_printed"]

event = obj(
	["event_id", "parent_event_id", "event_level", "event_label_as_printed", "verbatimLocality", "municipality", "stateProvince", "country", "verbatimCoordinates", "verbatimCoordinateSystem", "decimalLatitude", "decimalLongitude", "geodeticDatum", "verbatimElevation", "verbatimEventDate", "habitat", "samplingProtocol", "samplingEffort", "sampleSize_as_printed", "recordedBy_as_printed", "material_fate", "material_fate_as_printed", "field_pages", "source_inconsistency", "notes"],
	{
		"event_id": text("Short id unique inside the document: 'e1' for the study-wide event, then 'e2', 'e3' ... in the order the document presents the sites.", nullable=False, pattern="^e[0-9]+$"),
		"parent_event_id": text("event_id of the event this one sits in (a point in its station, a plot in its site, a campaign in its site, every site in the study event). null only for the study-wide event.", pattern="^e[0-9]+$"),
		"event_level": text("study = the whole survey; site = a named area, farm, fragment, reserve or locality; point = a sampling point, station or trap position inside a site; plot = a parcel or plot; transect; campaign = a sampling period or expedition; site_campaign = one site in one campaign; habitat = a habitat class used as a column; stratum = a vertical stratum, bait or trap type used as a column.", nullable=False, enum=["study", "site", "point", "plot", "transect", "campaign", "site_campaign", "habitat", "stratum"]),
		"event_label_as_printed": text("The label or code the document uses for this event, exactly as printed ('A', 'Ponto 1', 'VA1', 'FG', 'Invernada Rotacional', 'Nhumirim', 'Área I', 'EUG H1'). null for the study event when it has no label."),
		"verbatimLocality": text("Only the stretch that is the locality, as printed, with its hierarchy as printed, at most 15 words ('invernada Rotacional, fazenda Eldorado, Paiaguás'); municipality and state go to their own fields, not here. Never from the affiliation or the publisher."),
		"municipality": text("Municipality as printed ('Corumbá', 'Fênix', 'Ouricuri'), only when the document names it as the place of this event."),
		"stateProvince": text("State as printed ('MS', 'Mato Grosso do Sul', 'PE')."),
		"country": text("Country as printed; null when the document does not print it for the site."),
		"verbatimCoordinates": text("Coordinates exactly as printed, signs and hemisphere letters included (rule COORDINATES AS PRINTED)."),
		"verbatimCoordinateSystem": text("As printed or as the printed format shows it ('graus, minutos e segundos', 'UTM 22S'); null when no coordinates are printed."),
		"decimalLatitude": {"description": "Only when printed in decimal degrees; a copy of the printed number with point as decimal separator. Never converted.", "type": ["number", "null"], "minimum": -90, "maximum": 90},
		"decimalLongitude": {"description": "Only when printed in decimal degrees; a copy of the printed number. Never converted.", "type": ["number", "null"], "minimum": -180, "maximum": 180},
		"geodeticDatum": text("Datum as printed ('SAD69', 'WGS 84'); null when not printed."),
		"verbatimElevation": text("Elevation as printed ('100–800 m', '175 m acima do nível do mar')."),
		"verbatimEventDate": text("Only the stretch that is the date or period, as printed, at most 15 words (rule DATES AS PRINTED)."),
		"habitat": text("Habitat or vegetation of this event as printed ('Vazante', 'Lagoa permanente', 'campo cerrado', 'mata alta sem babaçu', 'pastagem')."),
		"samplingProtocol": text("Sampling method as printed, in the document's words, at most 15 words quoted ('redes de arrasto e tarrafas', 'método de quadrantes centrados', 'armadilhas luminosas com lâmpadas mistas de 250 watts')."),
		"samplingEffort": text("Only the stretch that is the effort, as printed for this event, at most 15 words ('5 arrastos', '10 lances', '20 armadilhas por 48 horas', '12 noites'); no gloss of ours (rule 29)."),
		"sampleSize_as_printed": text("Area or size of the sample as printed ('1 ha', '10 unidades amostrais de 8 m x 40 m', '25 pontos')."),
		"recordedBy_as_printed": text("Collectors or observers of this event as printed, when the document names them for the field work; never the author list by default."),
		"material_fate": text("Rule WHO RECORDED IT, MATERIAL FATE: the class of what the document prints about the material. Filled on the study event; on a child only when it differs, else null (the merge takes the parent's).", enum=["deposited_in_collection", "released_or_observed", "vouchers_not_tied_to_records", "not_stated", None]),
		"material_fate_as_printed": text("What the document prints about the fate of the material, at most 15 words ('identificados no campo, fotografados e soltos', 'depositado na coleção CPAC'), page in field_pages; null when not printed or when the parent's applies."),
		"field_pages": {"description": "Page of each filled field: {field name: page}. Every non-null field among " + ", ".join(EVENT_FIELDS) + " and verbatimCoordinateSystem has its page here; inherited fields are not repeated.", "type": "object", "additionalProperties": {"type": "integer", "minimum": 1}},
		"source_inconsistency": text("Both versions and pages when the document contradicts itself about this event (rule CONTRADICTIONS)."),
		"notes": text("Anything else about the event, at most 15 words quoted."),
	},
	"One site or sampling event as the document distinguishes it (rules EVENTS FIRST, EVENT FIELDS ONCE, WITH PAGE).",
)

symbol = obj(
	["symbol", "meaning_as_printed", "page", "place"],
	{
		"symbol": text("The code, letter, mark or abbreviation as printed ('X', '-', '*', 'VA1', 'Ta', 'Cp', 'Re', 'v').", nullable=False),
		"meaning_as_printed": text("Its meaning as printed, at most 15 words; null when the document defines it nowhere."),
		"page": page(),
		"place": text("Where it is defined.", enum=["caption", "header", "footnote", "legend", "methods", "text", "other_table", None]),
	},
)

column = obj(
	["column_id", "header_as_printed", "role", "event_id", "organismQuantityType_as_printed", "notes"],
	{
		"column_id": text("Short id unique inside the table: 'c1', 'c2' ... from left to right.", nullable=False, pattern="^c[0-9]+$"),
		"header_as_printed": text("The whole column header exactly as printed, every line of it, never cut, with spanning headers joined by ' / ' ('Estação / A / 1', 'Fazendas/Fontes / Ipanema').", nullable=False),
		"role": text("Rule COLUMN ROLES.", nullable=False, enum=["taxon_name", "family", "order", "vernacular", "authorship", "event_count", "event_mark", "event_code_list", "event_source_codes", "event_quantity_other", "event_taxon_list", "attribute", "threat_status", "voucher", "derived_metric", "total", "other"]),
		"event_id": text("For event_count, event_mark, event_source_codes and event_quantity_other: the event of this column. null otherwise, and null for event_taxon_list, whose event is the row's.", pattern="^e[0-9]+$"),
		"organismQuantityType_as_printed": text("For event_count and event_quantity_other: what the numbers are, copied whole and never cut from the header, caption, legend or methods ('N = número de indivíduos', 'número de capturas', 'Frequência %'). null otherwise."),
		"notes": text("Where the meaning came from when not in the header (page), at most 15 words quoted."),
	},
)

table_level_labels = obj(
	["row_identity", "column_axis", "presence_shown_as", "absence_shown_as", "symbols", "quantity_meaning", "heading_levels", "threat_list_as_printed", "footnotes", "source_inconsistency"],
	{
		"row_identity": text("What the rows are, in a few words ('espécies de peixes com cabeçalhos de ordem e família', 'famílias botânicas').", nullable=False),
		"column_axis": text("What the columns are.", nullable=False, enum=["events", "attributes_only", "events_and_attributes", "single_event_list", "events_by_events", "mixed"]),
		"presence_shown_as": text("How the table shows that a taxon occurred at an event.", nullable=False, enum=["count", "mark", "event_code_list", "source_codes", "quantity_other", "list_line", "taxa_in_cells", "mixed"]),
		"absence_shown_as": text("The printed absence mark and where its meaning is defined ('( - ) ausente, caption p4'), '0 in count columns', or null when the table shows no absence (blank cells)."),
		"symbols": {"description": "Every code, letter or mark used in the cells, once, with its meaning (rule CODES AND SYMBOLS). This is the only place a meaning is written: the merge joins it to each record by printed_code.", "type": "array", "items": symbol},
		"quantity_meaning": text("What the numbers in the cells are, as printed, with page and place ('N= número de indivíduos, caption p12')."),
		"heading_levels": {"description": "Printed heading rows that group the taxa, top-down ('ORDEM', 'Família', 'subfamília', 'Anfíbios').", "type": "array", "items": {"type": "string"}},
		"threat_list_as_printed": text("The threatened-species list the table refers to, as printed ('MMA, 2014'), else null."),
		"footnotes": {"description": "Every footnote or note under the table, as printed (at most 15 words each), with what it was used for.", "type": "array", "items": obj(["marker", "text", "used_for"], {"marker": text("Footnote marker as printed ('1', '*', 'a/'), or null."), "text": text("At most 15 words quoted.", nullable=False), "used_for": text("Field or column that took it, or 'nothing'.", nullable=False)})},
		"source_inconsistency": text("Contradictions about the table as a whole (rule CONTRADICTIONS)."),
	},
)

table = obj(
	["table_id", "page", "label", "kind", "caption_summary", "event_ids", "data_cells", "transcribed", "skipped_cells", "skipped_reason", "table_level_labels", "columns"],
	{
		"table_id": text("Short id unique inside the document: 'k1', 'k2' ... in page order; one per page for a continued table.", nullable=False, pattern="^k[0-9]+$"),
		"page": integer("PDF page (from 1) of this entry.", minimum=1),
		"label": text("Label as printed ('Tabela 2', 'TABELA 1', 'Anexo I', 'Continuação do Anexo I', 'Figura 3'), or 'text' for taxa named in the body text of that page.", nullable=False),
		"kind": text("occurrence_matrix = taxa x events with counts, marks or codes; species_list = taxa of one event, one per line, with or without attributes; plot_table = phytosociological or plot table of one event with counts and derived metrics; event_context = sites, coordinates, dates, effort; summary = counts or richness per family, site or habitat, all skipped; comparison = other studies, all skipped; legend = keys and abbreviations only; figure_labeled; figure_unlabeled; text; context = soil, weather, methods.", nullable=False, enum=["occurrence_matrix", "species_list", "plot_table", "event_context", "summary", "comparison", "legend", "figure_labeled", "figure_unlabeled", "text", "context"]),
		"caption_summary": text("The caption in our own words or quoted, at most 15 words quoted."),
		"event_ids": {"description": "Events whose records are in this entry. For a table continued over several pages, only the events with a cell on this entry's page. A record's event_id is always one of these.", "type": "array", "items": {"type": "string", "pattern": "^e[0-9]+$"}},
		"data_cells": integer("Cells that hold an occurrence, a quantity, a mark, a code, a derived value or a total, counted before transcription. Each code inside an event_code_list or event_source_codes cell counts as 1. A list line counts as 1. Excludes headers, heading rows, name, family, vernacular and authorship cells, attribute cells of a table with event columns, and blank cells. A '-' counts only when the legend defines it as absence. 0 for event_context, legend, context and figure_unlabeled."),
		"transcribed": integer("Records written from this entry. Must equal the number of records with this table_id."),
		"skipped_cells": integer("data_cells - transcribed."),
		"skipped_reason": text("Which cells were skipped and why (derived metric, total, comparison, outside extract_pages), when skipped_cells > 0."),
		"table_level_labels": {"oneOf": [table_level_labels, {"type": "null"}], "description": "Filled for every entry that gives records; null otherwise."},
		"columns": {"description": "One entry per printed column of an entry that gives records (rule COLUMN ROLES). Empty otherwise.", "type": "array", "items": column},
	},
)

line_attribute = obj(["column_id", "value_as_printed"], {"column_id": text("Column of the attribute.", nullable=False, pattern="^c[0-9]+$"), "value_as_printed": text("The cell as printed.", nullable=False)})

record = obj(
	["record_id", "event_id", "table_id", "column_id", "row_index", "position_in_cell", "event_detail_as_printed", "page", "table_or_figure", "value_kind", "verbatimScientificName", "identificationQualifier", "name_in_full_as_printed", "name_in_full_page", "name_status", "family_as_printed", "family_source", "order_as_printed", "order_source", "higher_group_as_printed", "vernacularName", "occurrenceStatus", "individualCount", "organismQuantity", "organismQuantityType", "value_as_printed", "printed_code", "record_origin", "cited_source_as_printed", "recording_method_as_printed", "voucher_as_printed", "threat_status_as_printed", "threat_status_source_as_printed", "line_attributes", "source_inconsistency", "notes"],
	{
		"record_id": text("'r1', 'r2' ... in reading order: table by table, row by row, left to right.", nullable=False, pattern="^r[0-9]+$"),
		"event_id": text("The most specific event of this cell or line (rules EVENTS FIRST, ONE RECORD PER PRINTED TAXON-BY-EVENT CELL OR LIST LINE).", nullable=False, pattern="^e[0-9]+$"),
		"table_id": text("tables[] entry of this record.", nullable=False, pattern="^k[0-9]+$"),
		"column_id": text("Column of the cell; null for a list line of a table whose only occurrence is the line itself.", pattern="^c[0-9]+$"),
		"row_index": integer("Taxon line number inside this table entry, counted from 1 over taxon lines only, or over event lines when the rows are events (heading rows and total rows are not counted). The key that ties A and B together.", minimum=1),
		"position_in_cell": integer("Order of the taxon inside an event_taxon_list cell, from 1; 1 for every other record.", minimum=1),
		"event_detail_as_printed": text("For event_taxon_list records: only what the column header or row header of the cell prints ('7h-8h', 'Tarde'), without the label of the block above it; else null."),
		"page": integer("PDF page (from 1) of the cell.", minimum=1),
		"table_or_figure": text("Label as printed, or 'text'.", nullable=False),
		"value_kind": text("count = a number of individuals or captures; quantity = another number; mark = a presence or absence mark; code = an event, source or record code; list_line = a line of a species list with no cell value; illegible.", nullable=False, enum=["count", "quantity", "mark", "code", "list_line", "illegible"]),
		"verbatimScientificName": text("Rule NAMES EXACTLY AS PRINTED.", nullable=False),
		"identificationQualifier": text("Rule QUALIFIERS AS PRINTED; null when none is printed."),
		"name_in_full_as_printed": text("Rule NAMES EXACTLY AS PRINTED, ABBREVIATED GENUS: the full name as the same document prints it elsewhere ('Aspidosperma pyrifolium Mart.'); null when the cell is not abbreviated or the document prints the full name nowhere."),
		"name_in_full_page": page("PDF page (from 1) where name_in_full_as_printed is printed; null when it is null."),
		"name_status": text("Rule NAMES EXACTLY AS PRINTED, NO SPECIES NAME: 'incomplete_in_print' when the name cell holds only authorship, only '-' or only a Portuguese group name; null otherwise.", enum=["incomplete_in_print", None]),
		"family_as_printed": text("Rule HIGHER TAXA ONLY AS PRINTED."),
		"family_source": text("Where the family came from.", enum=["column", "heading_row", None]),
		"order_as_printed": text("Rule HIGHER TAXA ONLY AS PRINTED."),
		"order_source": text("Where the order came from.", enum=["column", "heading_row", None]),
		"higher_group_as_printed": text("Any other printed heading above the taxon (subfamily, class, 'Répteis'), joined with ' / ' top-down."),
		"vernacularName": text("Rule VERNACULAR NAME; also the Portuguese group name of a name cell with no species name ('Tinamídeo')."),
		"occurrenceStatus": text("Rule BLANK IS NOT ABSENT.", nullable=False, enum=["present", "absent"]),
		"individualCount": integer("Rule QUANTITY AS PRINTED: only for counts of individuals or specimens.", nullable=True),
		"organismQuantity": {"description": "Rule QUANTITY AS PRINTED: any other printed quantity, decimal comma turned to point.", "type": ["number", "null"]},
		"organismQuantityType": text("What organismQuantity is, as printed (from the column's organismQuantityType_as_printed)."),
		"value_as_printed": text("The cell text exactly as printed, for count, quantity, mark and illegible records; null for code and list_line records."),
		"printed_code": text("Rule CODES AND SYMBOLS: the code or symbol in the cell, or the event code for an event_code_list record, or the one source code of this record (rule WHO RECORDED IT). Its meaning lives in table_level_labels.symbols."),
		"record_origin": text("Rule WHO RECORDED IT. A cell that joins sources gives one record per source, so there is no 'mixed'.", nullable=False, enum=["this_study", "cited_source", "collection", "not_stated"]),
		"cited_source_as_printed": text("The printed source code or reference for this record, else null."),
		"recording_method_as_printed": text("The printed method of this record, else null."),
		"voucher_as_printed": text("Collector number, collection acronym or catalogue number as printed ('RCM 4311', 'AMNH, MZUSP')."),
		"threat_status_as_printed": text("Rule STATUS AS PRINTED."),
		"threat_status_source_as_printed": text("The list or authority as printed ('MMA, 2014')."),
		"line_attributes": {"description": "Rule ATTRIBUTES PER LINE.", "type": "array", "items": line_attribute},
		"source_inconsistency": text("Rule CONTRADICTIONS, when about this cell or line."),
		"notes": text("At most 15 words quoted; the quote for text records."),
	},
	"One printed taxon-by-event cell, one event code inside a code-list cell, or one line of a species list.",
)

end_checklist = obj(
	["events", "tables", "rows", "codes", "totals"],
	{
		"events": {"description": "One entry per event and per field in the enum.", "type": "array", "items": obj(["event_id", "field", "status", "page"], {"event_id": text("Event.", nullable=False, pattern="^e[0-9]+$"), "field": text("Field.", nullable=False, enum=EVENT_FIELDS), "status": text("filled, inherited from the parent, or printed nowhere.", nullable=False, enum=["filled", "inherited", "not_printed"]), "page": page("Page where it is printed (of the parent when inherited); null when not_printed.")})},
		"tables": {"description": "One entry per table entry that gives records.", "type": "array", "items": obj(
			["table_id", "symbols_in_cells", "symbols_with_meaning", "heading_rows_carried", "event_columns", "event_columns_with_event_id", "derived_or_total_cells_skipped", "attribute_columns_in_line_attributes"],
			{
				"table_id": text("Table entry.", nullable=False, pattern="^k[0-9]+$"),
				"symbols_in_cells": {"description": "Distinct codes and marks found in the cells.", "type": "array", "items": {"type": "string"}},
				"symbols_with_meaning": {"description": "Those of them with a printed meaning in table_level_labels.symbols.", "type": "array", "items": {"type": "string"}},
				"heading_rows_carried": {"description": "true when every record under a family or order heading row carries it with family_source or order_source = 'heading_row'; null when the table has no heading rows.", "type": ["boolean", "null"]},
				"event_columns": integer("Columns with an event_* role."),
				"event_columns_with_event_id": integer("Of those, the ones with event_id filled. Must be equal."),
				"derived_or_total_cells_skipped": integer("Cells skipped as derived metric, total or comparison."),
				"attribute_columns_in_line_attributes": {"description": "true when every attribute column appears in line_attributes of its records; null when the table has none.", "type": ["boolean", "null"]},
			},
		)},
		"rows": {"description": "One entry per table entry that gives records.", "type": "array", "items": obj(
			["table_id", "taxon_lines_printed", "distinct_row_index_in_records", "lines_without_records", "rows_match"],
			{
				"table_id": text("Table entry.", nullable=False, pattern="^k[0-9]+$"),
				"taxon_lines_printed": integer("Taxon lines printed in this entry, excluding heading and total rows."),
				"distinct_row_index_in_records": integer("Distinct row_index values among the records of this entry."),
				"lines_without_records": {"description": "row_index of taxon lines that gave no record (every cell blank, derived or total), with the reason.", "type": "array", "items": {"type": "string"}},
				"rows_match": {"description": "true only when taxon_lines_printed = distinct_row_index_in_records + number of lines_without_records.", "type": "boolean"},
			},
		)},
		"codes": {"description": "Every distinct printed code in the document, with its meaning or 'undefined'.", "type": "array", "items": obj(["symbol", "table_ids", "meaning_as_printed"], {"symbol": text("Code as printed.", nullable=False), "table_ids": {"type": "array", "items": {"type": "string", "pattern": "^k[0-9]+$"}}, "meaning_as_printed": text("Meaning, or 'undefined'.", nullable=False)})},
		"totals": obj(
			["tables", "data_cells", "transcribed", "skipped_cells", "records", "events", "every_table_closes"],
			{
				"tables": integer("Number of tables[] entries."),
				"data_cells": integer("Sum of tables[].data_cells."),
				"transcribed": integer("Sum of tables[].transcribed. Must equal records."),
				"skipped_cells": integer("Sum of tables[].skipped_cells."),
				"records": integer("Length of records[]."),
				"events": integer("Length of events[]."),
				"every_table_closes": {"description": "true only when every tables[] entry has data_cells = transcribed + skipped_cells and transcribed equal to its records.", "type": "boolean"},
			},
		),
	},
)

schema = {
	"$schema": "https://json-schema.org/draft/2020-12/schema",
	"$id": "biodiversidade-piloto/schema.json",
	"title": "Brazilian fauna and flora inventories in Portuguese-language technical literature, one Darwin Core occurrence per printed taxon-by-event cell or list line",
	"version": "2.0",
	"description": "Fixed output format for every blind transcriber of the biodiversity pilot. Each document gives one JSON object {doc_id, transcriber, schema_version, events, tables, records, end_checklist}. events holds each site or sampling event once, with its printed locality, coordinates, dates, habitat, method and effort and the page of each; a child event inherits what its parent prints. tables is the inventory of every table, annex and figure of the document (0 cells when it names no taxon) and every text block with a record, with its cell count closed, its axes, its symbols and their printed meanings, and one columns[] entry per printed column with its role. Every record points to its event_id, table_id and column_id. Field names follow Darwin Core where a term exists (verbatimLocality, verbatimCoordinates, verbatimEventDate, habitat, samplingProtocol, samplingEffort, verbatimScientificName, identificationQualifier, vernacularName, occurrenceStatus, individualCount, organismQuantity, organismQuantityType); fields ending in _as_printed hold printed text for which the Darwin Core term will be filled in a later step. The transcription copies what is printed and never computes, converts, infers or resolves names. Carried over from the agricultural rounds (batata/schema.json v8, rules 2, 3, 17, 18, 35, 41, 46, 48, 49): inventory first with a closed cell count per table, read from the rendered page, copy exactly as printed, never compute or infer, illegible cells stay in, contradictions recorded with both versions, page from the PDF, short quotes only, end-of-transcription checklist, two independent transcriptions with diff and adjudication. Source PDFs and record pages are in sources.json. Changed in 2.0, after the 8-document pilot (RODADA.md, 'O que mudar no schema'): rank word out of family and order (rule 14), whole headers (16), one inventory rule (2, 24, 25), name_in_full_as_printed and name_status (12), name variants on every record (26), short verbatim fields (5) and code meanings only in symbols (17), fixed event_detail_as_printed (10), no gloss in printed fields (29), event_ids per page (2), material_fate on the event and one record per source code (18).",
	"rules": RULES,
	"type": "object",
	"additionalProperties": False,
	"required": ["doc_id", "transcriber", "schema_version", "events", "tables", "records", "end_checklist"],
	"properties": {
		"doc_id": text("id of the document in sources.json.", nullable=False),
		"transcriber": text("Rule TWO INDEPENDENT TRANSCRIPTIONS.", nullable=False, enum=["A", "B", "adjudicated"]),
		"schema_version": text("Version of this schema used.", nullable=False),
		"events": {"description": "One entry per site or sampling event, the study-wide event first.", "type": "array", "minItems": 1, "items": {"$ref": "#/$defs/event"}},
		"tables": {"description": "Inventory of every table, annex and figure of the document, and every text block with a record, in page order (rule INVENTORY FIRST, EVERY ENTRY).", "type": "array", "items": {"$ref": "#/$defs/table"}},
		"records": {"type": "array", "items": {"$ref": "#/$defs/record"}},
		"end_checklist": {"$ref": "#/$defs/end_checklist"},
	},
	"$defs": {"event": event, "table": table, "column": column, "symbol": symbol, "table_level_labels": table_level_labels, "record": record, "end_checklist": end_checklist},
}

OUT.write_text(json.dumps(schema, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("wrote", OUT, "rules", len(RULES))
