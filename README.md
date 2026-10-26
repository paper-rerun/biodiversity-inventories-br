# Biodiversity inventories in Brazil

Versão em português: [README.pt-BR.md](README.pt-BR.md)

1,152 species occurrences from 105 sampling events, taken from the species tables of 8 open-access Embrapa publications printed between 1982 and 2014: fish of the Taquari River floodplain and birds of Nhumirim ranch in the Pantanal (MS), bats in forest remnants of Fênix in the Atlantic Forest (PR), saturniid moths in Cerrado fragments (RO and GO), amphibians and reptiles of Ouricuri and trees and shrubs of two fragments near Petrolina in the Caatinga (PE), mammals and game birds of a forest fragment in Acre and the trees, palms and understory of 5 ha of the Tapajós National Forest in the Amazon (AC and PA). Each row is one taxon at one event exactly as printed, in Darwin Core terms, with the page and table it came from.

These lists were printed as Embrapa leaflets and journal articles, and their records are not in GBIF. Each document was checked against GBIF before it was transcribed, and none of the 8 had its records there. This dataset makes them searchable and joinable with other occurrence data.

Part of [Paper Rerun](https://paper-rerun.github.io), in its Open Tables line. The work was done by AI agents on a home computer and reviewed by a human before publication.

## What is in it

| | |
|---|---|
| Publications | 8 (6 Embrapa leaflets in Infoteca-e and 2 journal articles in Alice, Embrapa's open repositories), 1982 to 2014 |
| Events | 105 (8 studies, 26 sites, 15 points, 12 habitat units, 9 plots, 4 strata and 31 field days), in Mato Grosso do Sul, Paraná, Rondônia, Goiás, Pernambuco, Acre and Pará |
| Occurrences | 1,152 (1,109 present and 43 absent as printed; 1,057 HumanObservation and 95 PreservedSpecimen), 529 distinct names as printed |

| Document | Group | Biome, state | Field work, as printed | Events | Occurrences | GBIF check |
|---|---|---|---|---:|---:|---|
| freydargas2014 | fish | Pantanal, MS | March to June 2013 | 21 | 138 | no ray-finned fish in the Taquari box in 2013 |
| nunes2009 | birds | Pantanal, MS | not printed (list of 2008) | 5 | 189 | 7 birds at Nhumirim up to 2008, from iNaturalist and eBird, none by the authors |
| bianconi2004 | bats | Atlantic Forest, PR | July 2002 to June 2003 | 8 | 56 | no bats in the Fênix box in 2002-2003 |
| camargo2009 | saturniid moths | Cerrado, RO and GO | 1999 (RO) and 2001 (GO), July to December | 13 | 95 | no Saturniidae in the Catalão box; 4 in the Vilhena box, from iNaturalist and from 1995 |
| miranda1982 | amphibians and reptiles, with birds and mammals in an annex | Caatinga, PE | December to March 1981 | 13 | 161 | 13 records from Ouricuri in 1979-1983, all from USP, of other species and collectors |
| calixto2014 | trees and shrubs | Caatinga, PE | not printed | 3 | 106 | near Petrolina only iNaturalist, SISBio and herbarium records by other people |
| silva2009 | mammals and game birds | Amazon, AC | 31 days between 3 May and 16 June 2006 | 32 | 231 | 1 mammal in the box in 2006, by another author |
| sandel2000 | trees, palms and understory | Amazon, PA | not printed | 10 | 176 | the IAN herbarium is in GBIF but holds nothing by Sandel; nearby records are SISBio, 2010-2022 |

Files:
- `data/event.csv`: one row per sampling event. Events nest through `parentEventID`, from the study down to sites, points, plots, habitat units, strata or field days. A field the child event does not print is taken from the nearest parent that does, and `inherited` says from which; coordinates, effort and sample size are never passed down.
- `data/occurrence.csv`: one row per occurrence, with `doc_id`, `page` and `table_or_figure`. Its `eventID` points to the event row it belongs to.
- `data/sources.csv`: the 8 publications, with authors, record link and licence notice.
- `qa/decisions.csv`: every disagreement between the two independent transcriptions and how it was settled against the PDF (1,283 decisions, with page).
- `qa/name_match.csv`: the 529 distinct names, as printed, matched against the GBIF backbone: 403 exact, 44 fuzzy, 82 only above species and 0 with no match. It is a check, not data; the dataset does not change with it.
- `method/`: the schema, the comparison script, the merge script and the name-match script.

### Columns

Join the two data files on `eventID`. The event file uses the Darwin Core terms `eventID`, `parentEventID`, `eventType`, `verbatimLocality`, `municipality`, `stateProvince`, `verbatimCoordinates`, `verbatimEventDate`, `habitat`, `samplingProtocol`, `samplingEffort` and `recordedBy`. The occurrence file uses `occurrenceID`, `eventID`, `basisOfRecord`, `scientificName`, `identificationQualifier`, `family`, `order`, `vernacularName`, `occurrenceStatus`, `individualCount`, `organismQuantity` and `organismQuantityType`. Columns that Darwin Core has no term for keep our names (`value_as_printed`, `printed_code`, `code_meaning`, `record_origin`, `source_inconsistency` and others) and are described in `method/schema.json`.

Names, dates and coordinates are kept exactly as printed. `scientificName` carries the authorship, the qualifier and any misspelling of the source; GBIF interprets it. Dates are only in `verbatimEventDate` ("entre março e junho de 2013"): there is no ISO `eventDate` yet. Coordinates are only in `verbatimCoordinates`, in degrees and minutes as printed: `decimalLatitude` and `decimalLongitude` are empty, and so is `geodeticDatum`, since no document prints one. `individualCount` and `organismQuantity` hold the printed number with a decimal point; `value_as_printed` keeps the cell as it is. `code_meaning` gives the legend of each printed code in short form.

## How it was made

1. **Collection.** An agent harvested Embrapa's open repositories through OAI-PMH, read the record page and the PDF of 40 candidates and took 8, recording each one it did not take, with the reason. Only documents whose records are not in GBIF were taken: each candidate went through a dataset search by title, an occurrence search for 3 species of its own table in a box around the site (and in the printed years, where there are any) and a search for each author's surname in the same box, with every hit read by hand. This left out 8 candidates whose records, or records of the same team and collection, are already in GBIF. The ICMBio repository returned nothing and INPA's OAI endpoint was down, so the pilot is Embrapa only.
2. **Two independent transcriptions.** Two agents per publication transcribed the events (place, date, coordinates, habitat, protocol, effort, collectors), an inventory of the tables and figures, and every species cell into a fixed schema, without seeing each other's work, copying names, dates and numbers exactly as printed.
3. **Comparison and adjudication.** A script paired the two transcriptions event by event and record by record and listed every disagreement and every entry present in only one of them. Each one was settled by checking the PDF, with the page as evidence.
4. **Name check.** The 529 distinct names were sent as printed to the GBIF species match, with the kingdom of each document. Nothing in the dataset was changed by it.

## How accurate it is

- **Names and numbers:** no name was misread in either transcription. Of the 1,151 paired records, both wrote the same name, letter by letter, in 1,150; the last one is an authorship the print leaves ambiguous (*Clarisia racemosa*, "Ruíz" or "Rulz", sandel2000 p16), kept as "Ruíz", as p18 prints it. One digit was misread in one transcription (miranda1982 Fig. 13, "0,18" read as "0,16") and corrected. The GBIF check confirms it from the other side: the 44 fuzzy matches are spellings of the source, checked against the text layer or the page, not misreadings.
- **Whole records:** one transcription alone was fully correct on 98.5% of records, the other on 77.8%, counting the records each left out (1 and 0). Almost all of the second one's errors come from two rules, each missed across a whole document: the rank word kept with the taxon name ("Família Anostomidae", "ORDEM CHARACIFORMES") in freydargas2014, 276 fields in 138 records, which the examples in our own schema invited; and a column header cut short in miranda1982 Fig. 13, 100 records. Without the two it is 95.7%. Events were harder: 77.1% and 80.0% of them fully right, in the same order. All 1,283 disagreements were settled against the PDF, so the dataset does not depend on either transcription alone.
- **Known limits:**
  - No ISO dates and no decimal coordinates yet. 681 occurrences have a printed date, always a period; 3 documents print no sampling date at all (calixto2014, nunes2009 and sandel2000, 471 occurrences). 557 occurrences have printed coordinates; 176 of them (sandel2000) are the range of the whole forest, not a point.
  - 30 names are abbreviated or incomplete in print (76 occurrences). Table 2 of calixto2014 abbreviates the genus ("A. pyrifolium") and the full name is only in its Table 1 (27 names, 54 occurrences); 3 more are not species names at all: an authorship alone, a dash and "Tinamídeo" (22 occurrences). They stay as printed, and GBIF cannot match them to a species. 87 of the exact and fuzzy matches fall on synonyms, as expected in lists from 1982 to 2014.
  - The 95 preserved specimens (camargo2009, deposited in the CPAC collection) have no institution code or catalogue number in print.
  - 42 records of nunes2009 mix the authors' field observations with cited literature: `record_origin` is `mixed` in 41 and `cited_source` in 1, and the source of each is in `printed_code` and `code_meaning`.
  - nunes2009 is a cut: only pages 11 to 13 of its species list are used, out of a list that runs to page 24 (about 320 species).
  - miranda1982 is a scan without a usable text layer. It was read from the rendered page, and the checks for copied text and for a rights notice could not run on it.
  - One document, silva2009, holds 231 occurrences, 20% of the dataset.

This is a pilot of 8 documents, run to settle the schema. A larger round, of 20 documents, is planned. The dataset is not published in GBIF for now.

## Licence and citation

- The dataset (the CSV files, schema and scripts) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Please cite the original publications listed in `data/sources.csv` as well as this dataset. Each row also carries its source in `bibliographicCitation`.
- The publications are not redistributed. Embrapa's repositories show a CC BY-NC-ND 4.0 notice on every record page, not an item licence; the 2 journal articles (bianconi2004 in Revista Brasileira de Zoologia and calixto2014 in Pesquisa Florestal Brasileira) keep their own terms; 4 Embrapa leaflets (freydargas2014, nunes2009, camargo2009 and silva2009) print "Todos os direitos reservados" (all rights reserved) and sandel2000 prints "© Embrapa". miranda1982 is an image scan and could not be searched for a notice. Only occurrences, which are facts, and short citations are used here.

Errors or missing records: please [open an issue](https://github.com/paper-rerun/biodiversity-inventories-br/issues).

## How this dataset was made

This dataset was built by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No value was estimated or typed by hand: each one was transcribed from the source PDF twice, independently, and every disagreement was checked against the page. The method and scripts are in `method/`. How the wider project works: https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md

Contact: Filipe Tessaro, via issues on this repository.
