# Biodiversity inventories in Brazil

Versão em português: [README.pt-BR.md](README.pt-BR.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23680348.svg)](https://doi.org/10.5281/zenodo.23680348)

2,850 species occurrences from 322 sampling events, taken from the species tables of 28 open-access Brazilian publications printed between 1982 and 2020: fish, birds, mammals, bats, frogs and reptiles, dung beetles, butterflies, moths, bees, trees and mangrove plants, from the Amazon, Cerrado, Caatinga, Pantanal, Atlantic Forest, Pampa and the coast, in 13 states. Each row is one taxon at one event exactly as printed, in Darwin Core terms, with the page and table it came from.

These lists were printed as Embrapa leaflets, journal articles and master's dissertations, and their records are not in GBIF. Each document was checked against GBIF before it was transcribed, and none of the 28 had its records there. This dataset makes them searchable and joinable with other occurrence data.

Part of [Paper Rerun](https://paper-rerun.github.io), in its Open Tables line. The work was done by AI agents on a home computer and reviewed by a human before publication.

## Versions

- **v2.0.0** (November 2026): 28 documents. Adds a round of 20 documents to the 8 of the pilot, all merged with schema 2.0. The new schema adds an ISO `eventDate` derived from the printed date, takes `basisOfRecord` from what each document prints about the fate of the material, and marks names left incomplete in print in `name_status`.
- **v1.0.0** (October 2026): pilot of 8 Embrapa publications, 1,152 occurrences.

## What is in it

| | |
|---|---|
| Publications | 28: 23 from Embrapa's open repositories (Alice and Infoteca-e) and 5 master's dissertations from the UFU, UFV and UFMG repositories; 1982 to 2020 |
| Events | 322 (28 studies, 56 sites, 21 site campaigns, 90 campaigns, 82 points, 23 plots, 16 habitat units and 6 strata), in AC, AM, GO, MA, MG, MS, PA, PB, PE, PI, PR, RO and RS |
| Occurrences | 2,850 (2,713 present and 137 absent as printed; 2,436 HumanObservation and 414 PreservedSpecimen), 1,256 distinct names as printed |

| Document | Group | Biome, state | Year | Events | Occurrences |
|---|---|---|---:|---:|---:|
| freydargas2014 | fish | Pantanal, MS | 2014 | 21 | 138 |
| nunes2009 (birds) | birds | Pantanal, MS | 2009 | 5 | 189 |
| bianconi2004 | bats | Atlantic Forest, PR | 2004 | 8 | 56 |
| camargo2009 | saturniid moths | Cerrado, RO and GO | 2009 | 13 | 95 |
| miranda1982 | amphibians and reptiles | Caatinga, PE | 1982 | 13 | 161 |
| calixto2014 | trees and shrubs | Caatinga, PE | 2014 | 3 | 106 |
| silva2009 | mammals and game birds | Amazon, AC | 2009 | 32 | 231 |
| sandel2000 | trees, palms and understory | Amazon, PA | 2000 | 10 | 176 |
| mai2010 | fish caught in coastal weirs | coast, PI | 2010 | 1 | 118 |
| queiroga2018 | fish of a vereda | Cerrado, MG | 2018 | 14 | 36 |
| winckler2011 | fish in rice fields | Pampa, RS | 2011 | 7 | 12 |
| mauricio2018 | birds | Pampa, RS | 2018 | 4 | 193 |
| carvalho2013 | waterbirds | Cerrado, MG | 2013 | 58 | 192 |
| silva2009b | mammals and birds | Amazon, AM | 2009 | 32 | 254 |
| dias2006 | mammals | Atlantic Forest, PR | 2006 | 3 | 50 |
| nunes2009 (mammals) | mammals | Atlantic Forest, MG | 2009 | 29 | 86 |
| silveira2010 | bats | Pantanal, MS | 2010 | 3 | 36 |
| gordo2003 | frogs | Pantanal, MS | 2003 | 1 | 19 |
| carosini2013 | leaf-litter frogs | Atlantic Forest, MG | 2013 | 17 | 84 |
| santos2019 | dung beetles | Amazon, AC | 2019 | 1 | 15 |
| rodrigues2010 | dung beetles | Pantanal, MS | 2010 | 5 | 35 |
| pereira2011 | butterflies | Cerrado, MG | 2011 | 1 | 27 |
| viana2020 | hawkmoths and saturniid moths | Cerrado, MG | 2020 | 16 | 130 |
| lopes2010 | bees and the plants they visit | Cerrado-Caatinga, PI | 2010 | 15 | 172 |
| vieira2002 | trees | Amazon, RO | 2002 | 1 | 70 |
| tourinho1998 | mangrove and associated plants | Amazon coast, PA | 1998 | 7 | 87 |
| pereira2012 | woody plants | Caatinga, PB | 2012 | 1 | 63 |
| rego2008 | stingless bees and their nest trees | Cerrado, MA | 2008 | 1 | 19 |

The two nunes2009 are different documents, told apart by `doc_id` (`nunes2009-aves-nhumirim-pantanal-ms` and `nunes2009-mamiferos-serra-do-brigadeiro-mg`).

Files:
- `data/event.csv`: one row per sampling event. Events nest through `parentEventID`, from the study down to sites, campaigns, points, plots, habitat units or strata. A field the child event does not print is taken from the nearest parent that does, and `inherited` says from which; coordinates, effort and sample size are never passed down.
- `data/occurrence.csv`: one row per occurrence, with `doc_id`, `page` and `table_or_figure`. Its `eventID` points to the event row it belongs to.
- `data/sources.csv`: the 28 publications, with authors, record link, licence notice and the GBIF check that was run before transcription.
- `qa/decisions.csv`: every disagreement between the two independent transcriptions and how it was settled against the PDF (3,199 decisions, with page).
- `qa/name_match.csv`: the distinct names, as printed, matched against the GBIF backbone: 1,258 name and kingdom pairs, 926 exact, 110 fuzzy, 222 only above species (150 of them printed with "sp.", "aff.", "cf." or "gr.") and 0 with no match. It is a check, not data; the dataset does not change with it.
- `method/`: the schema (`schema.json`, built by `build_schema.py`), the comparison, merge and name-match scripts, and the checks of the schema and of the adjudicated files.

### Columns

Join the two data files on `eventID`. The event file uses the Darwin Core terms `eventID`, `parentEventID`, `eventType`, `verbatimLocality`, `municipality`, `stateProvince`, `verbatimCoordinates`, `verbatimEventDate`, `eventDate`, `habitat`, `samplingProtocol`, `samplingEffort` and `recordedBy`. The occurrence file uses `occurrenceID`, `eventID`, `basisOfRecord`, `eventDate`, `scientificName`, `identificationQualifier`, `family`, `order`, `vernacularName`, `occurrenceStatus`, `individualCount`, `organismQuantity` and `organismQuantityType`. Columns that Darwin Core has no term for keep our names (`value_as_printed`, `printed_code`, `code_meaning`, `record_origin`, `name_status`, `material_fate`, `source_inconsistency` and others) and are described in `method/schema.json`.

Names and coordinates are kept exactly as printed. `scientificName` carries the authorship, the qualifier and any misspelling of the source; GBIF interprets it. `stateProvince` is also as printed, so it is "MG" in some documents and "Minas Gerais" in others. `verbatimEventDate` keeps the printed date. `eventDate` is an ISO date or interval derived from it, filled in 1,087 occurrences, and `eventDate_derivation` says how. An ambiguous printed date leaves `eventDate` empty. Coordinates are only in `verbatimCoordinates`: `decimalLatitude` and `decimalLongitude` are empty.

`basisOfRecord` comes from `material_fate`, what the document prints about the material. Only `deposited_in_collection` becomes PreservedSpecimen; `released_or_observed`, `vouchers_not_tied_to_records` and `not_stated` become HumanObservation. `basisOfRecord_source` says which event it came from.

## How it was made

1. **Collection.** Agents harvested Embrapa's open repositories through OAI-PMH and searched the DSpace repositories of three universities (UFU, UFV and UFMG), read the record page and the PDF of each candidate and recorded each one not taken, with the reason. Only documents whose records are not in GBIF were taken: each candidate went through a dataset search by title, an occurrence search for 3 species of its own table in a box around the site (and in the printed years, where there are any) and a search for each author's surname in the same box, with every hit read by hand. The result of that check for each document is in `data/sources.csv`. The pilot read 40 candidates and took 8; the round read 49 and took 20. The ICMBio and INPA repositories could not be reached in either.
2. **Two independent transcriptions.** Two agents per publication transcribed the events (place, date, coordinates, habitat, protocol, effort, collectors, fate of the material), an inventory of the tables and figures, and every species cell into a fixed schema, without seeing each other's work, copying names, dates and numbers exactly as printed.
3. **Comparison and adjudication.** A script paired the two transcriptions event by event and record by record and listed every disagreement and every entry present in only one of them. Each one was settled by checking the PDF, with the page as evidence. In the round, each document also got a separate pass that checked the place, date and method of each table on its own, to catch context errors that both transcriptions make together.
4. **Name check.** The distinct names were sent as printed to the GBIF species match, with the kingdom of each table. Morphospecies ("Ataenius sp.1") are sent as the genus alone, since a fuzzy match would otherwise pick a real species by its letters. Nothing in the dataset was changed by it.

## How accurate it is

- **Names and numbers:** across the 2,839 paired records, no letter of a name was misread in either transcription. One digit was misread once, in the pilot (miranda1982 Fig. 13, "0,18" read as "0,16"), and corrected. The fuzzy matches against GBIF are spellings of the source (*Anisostremus* for *Anisotremus*, *Goupia glaba*), which both transcriptions read the same way.
- **Whole records:** counting the records each one left out, one transcription alone was fully correct on 81.2% of the round's records and the other on 92.0% (98.5% and 77.8% in the pilot). Almost all errors come from one rule missed across a whole document, such as a cut column header, a code legend copied into the record or a derived metric taken for a count. Without those, both are near 94% in the round. All 3,199 disagreements were settled against the PDF, so the dataset does not depend on either transcription alone.
- **Context errors:** in the round, 12 cases in 9 documents had both transcriptions agree on the wrong event, method or habitat for a block of records (459 occurrences). The context pass caught them and 11 were fixed. The one left: the 12 trees of the lopes2010 site descriptions inherit the bee sampling protocol of their study event, because the schema cannot block that inheritance yet.
- **Known limits:**
  - No decimal coordinates yet. 2,108 occurrences have printed coordinates in their event or a parent event; in sandel2000 they are the range of the whole forest, not a point.
  - `eventDate` is empty in 1,763 occurrences. Some documents print no date at all (calixto2014, nunes2009 birds, sandel2000), and 670 occurrences of the round have a date in a form the merge does not read yet ("2015-2016", "2018 / Outubro", "início em ... término em").
  - 14 occurrences have `name_status` `incomplete_in_print`: the line prints no species name, or the name is illegible, so `scientificName` is empty or partial. The abbreviated genera of calixto2014 Table 2 and carvalho2013 are kept as printed.
  - 41 records of nunes2009 (birds) mix the authors' field observations with cited literature: `record_origin` is `mixed`, and the source of each is in `printed_code` and `code_meaning`. From the round on, a cell that joins sources gives one record per source.
  - nunes2009 (birds) is a cut: only pages 11 to 13 of its species list are used.
  - miranda1982 is a scan without a usable text layer. It was read from the rendered page, and the checks for copied text and for a rights notice could not run on it.

The dataset is not published in GBIF for now.

## Licence and citation

- The dataset (the CSV files, schema and scripts) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Please cite the original publications listed in `data/sources.csv` as well as this dataset. Each row also carries its source in `bibliographicCitation` and the licence notice of that source in `license`.
- The publications are not redistributed. Embrapa's repositories show a CC BY-NC-ND 4.0 notice on every record page, not an item licence, and several Embrapa leaflets print "Todos os direitos reservados" (all rights reserved). Journal articles keep their own terms. The 5 dissertations carry only "Acesso Aberto" (open access), with no Creative Commons licence. Only occurrences, which are facts, and short citations are used here.

Errors or missing records: please [open an issue](https://github.com/paper-rerun/biodiversity-inventories-br/issues).

## How this dataset was made

This dataset was built by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No value was estimated or typed by hand: each one was transcribed from the source PDF twice, independently, and every disagreement was checked against the page. The method and scripts are in `method/`. How the wider project works: https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md

Contact: Filipe Tessaro, via issues on this repository.
