# Inventários de biodiversidade no Brasil

English version: [README.md](README.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23680348.svg)](https://doi.org/10.5281/zenodo.23680348)

1.152 ocorrências de espécies em 105 eventos de amostragem, tiradas das tabelas de espécies de 8 publicações de acesso aberto da Embrapa impressas entre 1982 e 2014: peixes da planície de inundação do rio Taquari e aves da fazenda Nhumirim no Pantanal (MS), morcegos em remanescentes florestais de Fênix na Mata Atlântica (PR), mariposas Saturniidae em fragmentos de Cerrado (RO e GO), anfíbios e répteis de Ouricuri e árvores e arbustos de dois fragmentos perto de Petrolina na Caatinga (PE), mamíferos e aves de caça de um fragmento florestal no Acre e as árvores, palmeiras e sub-bosque de 5 ha da Floresta Nacional do Tapajós na Amazônia (AC e PA). Cada linha é um táxon num evento exatamente como foi impresso, em termos Darwin Core, com a página e a tabela de onde saiu.

Essas listas foram impressas como folhetos da Embrapa e artigos de periódico, e os registros delas não estão no GBIF. Cada documento foi conferido no GBIF antes de ser transcrito, e nenhum dos 8 tinha os seus registros lá. Este dataset torna essas listas pesquisáveis e combináveis com outros dados de ocorrência.

Faz parte do [Paper Rerun](https://paper-rerun.github.io), na linha Open Tables. O trabalho foi feito por agentes de IA num computador doméstico e revisado por uma pessoa antes da publicação.

## O que tem

| | |
|---|---|
| Publicações | 8 (6 folhetos da Embrapa no Infoteca-e e 2 artigos de periódico no Alice, os repositórios abertos da Embrapa), 1982 a 2014 |
| Eventos | 105 (8 estudos, 26 sítios, 15 pontos, 12 unidades ecológicas, 9 parcelas, 4 estratos e 31 dias de campo), em Mato Grosso do Sul, Paraná, Rondônia, Goiás, Pernambuco, Acre e Pará |
| Ocorrências | 1.152 (1.109 presenças e 43 ausências impressas; 1.057 HumanObservation e 95 PreservedSpecimen), 529 nomes distintos como impressos |

| Documento | Grupo | Bioma, UF | Campo, como impresso | Eventos | Ocorrências | Conferência no GBIF |
|---|---|---|---|---:|---:|---|
| freydargas2014 | peixes | Pantanal, MS | março a junho de 2013 | 21 | 138 | nenhum peixe ósseo na caixa do Taquari em 2013 |
| nunes2009 | aves | Pantanal, MS | não impresso (lista de 2008) | 5 | 189 | 7 aves em Nhumirim até 2008, do iNaturalist e do eBird, nenhuma dos autores |
| bianconi2004 | morcegos | Mata Atlântica, PR | julho de 2002 a junho de 2003 | 8 | 56 | nenhum morcego na caixa de Fênix em 2002-2003 |
| camargo2009 | mariposas Saturniidae | Cerrado, RO e GO | 1999 (RO) e 2001 (GO), de julho a dezembro | 13 | 95 | nenhum Saturniidae na caixa de Catalão; 4 na de Vilhena, do iNaturalist e de 1995 |
| miranda1982 | anfíbios e répteis, com aves e mamíferos num anexo | Caatinga, PE | dezembro a março de 1981 | 13 | 161 | 13 registros de Ouricuri em 1979-1983, todos da USP, de outras espécies e coletores |
| calixto2014 | árvores e arbustos | Caatinga, PE | não impresso | 3 | 106 | perto de Petrolina, só registros do iNaturalist, do SISBio e de herbário, de outras pessoas |
| silva2009 | mamíferos e aves de caça | Amazônia, AC | 31 dias entre 3 de maio e 16 de junho de 2006 | 32 | 231 | 1 mamífero na caixa em 2006, de outro autor |
| sandel2000 | árvores, palmeiras e sub-bosque | Amazônia, PA | não impresso | 10 | 176 | o herbário IAN está no GBIF, mas não tem nada do Sandel; o que há perto é do SISBio, de 2010 a 2022 |

Arquivos:
- `data/event.csv`: uma linha por evento de amostragem. Os eventos se encaixam por `parentEventID`, do estudo para baixo: sítio, ponto, parcela, unidade ecológica, estrato ou dia de campo. Um campo que o evento filho não imprime vem do evento acima mais próximo que imprime, e `inherited` diz de qual; coordenada, esforço e tamanho de amostra nunca descem.
- `data/occurrence.csv`: uma linha por ocorrência, com `doc_id`, `page` e `table_or_figure`. O `eventID` aponta para a linha do evento a que ela pertence.
- `data/sources.csv`: as 8 publicações, com autores, link do registro e aviso de licença.
- `qa/decisions.csv`: cada divergência entre as duas transcrições independentes e como ela foi resolvida conferindo o PDF (1.283 decisões, com a página).
- `qa/name_match.csv`: os 529 nomes distintos, como impressos, conferidos no backbone do GBIF: 403 exatos, 44 aproximados, 82 só acima da espécie e 0 sem resultado. É conferência, não dado; o dataset não muda com ela.
- `method/`: o schema, o script de comparação, o script de junção e o script de conferência de nomes.

### Colunas

Junte os dois arquivos de dados por `eventID`. O arquivo de eventos usa os termos Darwin Core `eventID`, `parentEventID`, `eventType`, `verbatimLocality`, `municipality`, `stateProvince`, `verbatimCoordinates`, `verbatimEventDate`, `habitat`, `samplingProtocol`, `samplingEffort` e `recordedBy`. O de ocorrências usa `occurrenceID`, `eventID`, `basisOfRecord`, `scientificName`, `identificationQualifier`, `family`, `order`, `vernacularName`, `occurrenceStatus`, `individualCount`, `organismQuantity` e `organismQuantityType`. As colunas que não têm termo no Darwin Core ficam com nomes nossos (`value_as_printed`, `printed_code`, `code_meaning`, `record_origin`, `source_inconsistency` e outras) e estão descritas em `method/schema.json`.

Nomes, datas e coordenadas ficam exatamente como impressos. `scientificName` traz a autoria, o qualificador e qualquer erro de grafia da fonte; o GBIF interpreta. A data está só em `verbatimEventDate` ("entre março e junho de 2013"): ainda não há `eventDate` em ISO. A coordenada está só em `verbatimCoordinates`, em graus e minutos como impressa: `decimalLatitude` e `decimalLongitude` estão vazias, e `geodeticDatum` também, porque nenhum documento imprime datum. `individualCount` e `organismQuantity` trazem o número impresso com ponto decimal; `value_as_printed` guarda a célula como ela é. `code_meaning` dá a legenda de cada código impresso em forma curta.

### Principais colunas

O arquivo está em UTF-8, com vírgula separando as colunas. Em todo registro, `doc_id` liga a linha a `data/sources.csv`, e `page` e `table_or_figure` dizem de onde ela saiu (página do PDF contada a partir de 1, e o rótulo da tabela como impresso, "Anexo I", "Tabela 2", "Fig. 13").

- `eventID` e `parentEventID`: o evento e o evento acima dele, no formato `doc_id#e1`. O estudo inteiro não tem pai; o dia de campo de silva2009, por exemplo, aponta para o estudo.
- `eventType`: o nível do evento, entre `study` (estudo), `site` (sítio), `point` (ponto), `plot` (parcela), `habitat` (unidade ecológica), `stratum` (estrato) e `campaign` (dia ou campanha de campo).
- `verbatimLocality`, `municipality` e `stateProvince`: o local como impresso. A UF vem como a fonte escreve, sigla ou nome por extenso ("PE", "Paraná").
- `verbatimCoordinates`: a coordenada como impressa ("23º55’S-51º57’W"), ainda sem conversão para decimal.
- `verbatimEventDate`: a data ou o período como impresso ("entre julho de 2002 e junho de 2003", "Dia 12"). Vazia em calixto2014, nunes2009 e sandel2000, que não imprimem data.
- `inherited`: os campos que o evento recebeu do evento acima, e de qual ("habitat:e1").
- `scientificName`: o nome exatamente como impresso, com autoria e grafia da fonte ("Myotis aff. riparius Handley, 1960", "A. pyrifolium").
- `identificationQualifier`: o qualificador impresso junto do nome ("sp.", "aff.", "cf.", "gr."). Vazio na maioria dos registros.
- `occurrenceStatus`: `present` ou `absent`. Ausência só entra onde a legenda ou um 0 impresso diz que é ausência (43 registros).
- `individualCount` e `organismQuantity`: a contagem de indivíduos, ou outra quantidade com a unidade em `organismQuantityType` (a frequência corrigida de miranda1982, os grupos observados por 10 km de silva2009). Número pronto para cálculo, com ponto decimal; a célula como impressa está em `value_as_printed`.
- `basisOfRecord`: `HumanObservation` (observação, captura e soltura, parcela) ou `PreservedSpecimen` (as 95 mariposas de camargo2009, depositadas na coleção CPAC), conforme o que cada documento diz sobre o material.
- `record_origin`: `this_study` quando o registro é do próprio estudo, `mixed` quando junta observação dos autores e literatura citada, `cited_source` quando vem só da literatura. Os 42 que não são `this_study` são de nunes2009, e a fonte de cada um está em `printed_code` e `code_meaning`.

## Como foi feito

1. **Coleta.** Um agente percorreu os repositórios abertos da Embrapa pelo OAI-PMH, leu a página do registro e o PDF de 40 candidatos e ficou com 8, registrando cada um que não entrou, com o motivo. Só entrou documento cujos registros não estão no GBIF: cada candidato passou por uma busca de dataset pelo título, uma busca de ocorrência de 3 espécies da própria tabela numa caixa em volta do local (e nos anos impressos, quando há) e uma busca do sobrenome de cada autor na mesma caixa, com cada acerto olhado à mão. Isso tirou 8 candidatos cujos registros, ou registros da mesma equipe e coleção, já estão no GBIF. O repositório do ICMBio respondeu vazio e o OAI do INPA estava fora do ar, então o piloto é só Embrapa.
2. **Duas transcrições independentes.** Dois agentes por publicação transcreveram os eventos (local, data, coordenada, habitat, protocolo, esforço, coletores), um inventário das tabelas e figuras e cada célula de espécie num schema fixo, sem ver o trabalho um do outro, copiando nomes, datas e números exatamente como impressos.
3. **Comparação e arbitragem.** Um script pareou as duas transcrições evento por evento e registro por registro e listou cada divergência e cada item presente em só uma delas. Cada caso foi resolvido conferindo o PDF, com a página como evidência.
4. **Conferência de nomes.** Os 529 nomes distintos foram mandados como impressos para o match de espécies do GBIF, com o reino de cada documento. Nada no dataset mudou com isso.

## Qual a precisão

- **Nomes e números:** nenhum nome foi lido errado em nenhuma das duas transcrições. Dos 1.151 registros pareados, as duas escreveram o mesmo nome, letra por letra, em 1.150; o que sobra é uma autoria que a impressão deixa ambígua (*Clarisia racemosa*, "Ruíz" ou "Rulz", sandel2000 p16), mantida como "Ruíz", como a p18 imprime. Um algarismo foi lido errado numa transcrição (miranda1982 Fig. 13, "0,18" lido como "0,16") e corrigido. A conferência no GBIF confirma isso pelo outro lado: os 44 nomes aproximados são grafia da fonte, conferida na camada de texto ou na página, e não erro de leitura.
- **Registros inteiros:** sozinha, uma transcrição estava totalmente correta em 98,5% dos registros, e a outra em 77,8%, contando os registros que cada uma deixou de fora (1 e 0). Quase todos os erros da segunda vêm de duas regras, cada uma perdida num documento inteiro: a palavra de posto guardada junto do nome do táxon ("Família Anostomidae", "ORDEM CHARACIFORMES") em freydargas2014, 276 campos em 138 registros, o que os exemplos do nosso próprio schema convidavam a fazer; e um cabeçalho de coluna cortado em miranda1982 Fig. 13, 100 registros. Sem as duas, ela fica em 95,7%. Os eventos foram mais difíceis: 77,1% e 80,0% deles totalmente certos, na mesma ordem. As 1.283 decisões foram resolvidas conferindo o PDF, então o dataset não depende de nenhuma das duas transcrições sozinha.
- **Limites conhecidos:**
  - Ainda não há data ISO nem coordenada decimal. 681 ocorrências têm data impressa, sempre um período; 3 documentos não imprimem data de amostragem nenhuma (calixto2014, nunes2009 e sandel2000, 471 ocorrências). 557 ocorrências têm coordenada impressa; 176 delas (sandel2000) são a faixa da floresta inteira, não um ponto.
  - 30 nomes estão abreviados ou incompletos na impressão (76 ocorrências). A Tabela 2 de calixto2014 abrevia o gênero ("A. pyrifolium"), e o nome inteiro só está na Tabela 1 (27 nomes, 54 ocorrências); outros 3 não são nome de espécie: uma autoria sozinha, um traço e "Tinamídeo" (22 ocorrências). Eles ficam como impressos, e o GBIF não consegue casá-los com uma espécie. 87 dos nomes exatos e aproximados caem em sinônimo, o esperado em listas de 1982 a 2014.
  - Os 95 espécimes preservados (camargo2009, depositados na coleção CPAC) não têm código de instituição nem número de catálogo impresso.
  - 42 registros de nunes2009 juntam observação de campo dos autores e literatura citada: `record_origin` é `mixed` em 41 e `cited_source` em 1, e a fonte de cada um está em `printed_code` e `code_meaning`.
  - nunes2009 é um recorte: só as páginas 11 a 13 da lista de espécies foram usadas, de uma lista que vai até a página 24 (umas 320 espécies).
  - miranda1982 é um documento escaneado sem camada de texto útil. Foi lido a partir da imagem da página, e nele não rodam a busca de texto copiado nem a de aviso de direitos.
  - Um documento, silva2009, tem 231 ocorrências, 20% do dataset.

Este é um piloto de 8 documentos, feito para acertar o schema. Uma rodada maior, de 20 documentos, está planejada. Por enquanto o dataset não está publicado no GBIF.

## Licença e citação

- O dataset (os arquivos CSV, o schema e os scripts) é publicado sob a licença [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Por favor, cite as publicações originais listadas em `data/sources.csv` e também este dataset. Cada linha também traz a sua fonte em `bibliographicCitation`.
- As publicações não são redistribuídas. Os repositórios da Embrapa exibem um aviso CC BY-NC-ND 4.0 na página de todo registro, e não uma licença do item; os 2 artigos de periódico (bianconi2004 na Revista Brasileira de Zoologia e calixto2014 na Pesquisa Florestal Brasileira) mantêm os próprios termos; 4 folhetos da Embrapa (freydargas2014, nunes2009, camargo2009 e silva2009) trazem "Todos os direitos reservados", e sandel2000 traz "© Embrapa". miranda1982 é uma imagem escaneada, e não foi possível procurar nele um aviso. Aqui são usadas só as ocorrências, que são fatos, e citações curtas.

Erros ou registros que faltam: por favor, [abra uma issue](https://github.com/paper-rerun/biodiversity-inventories-br/issues).

## Como este dataset foi feito

Este dataset foi montado por agentes de IA (Claude, da Anthropic) num computador doméstico e revisado por uma pessoa antes da publicação. Nenhum valor foi estimado ou digitado à mão: cada um foi transcrito do PDF original duas vezes, de forma independente, e cada divergência foi conferida na página. O método e os scripts estão em `method/`. Como funciona o projeto como um todo (em inglês): https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md

Contato: Filipe Tessaro, pelas issues deste repositório.
