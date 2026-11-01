# Inventários de biodiversidade no Brasil

English version: [README.md](README.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23680348.svg)](https://doi.org/10.5281/zenodo.23680348)

2.850 ocorrências de espécies em 322 eventos de amostragem, tiradas das tabelas de espécies de 28 publicações brasileiras de acesso aberto impressas entre 1982 e 2020: peixes, aves, mamíferos, morcegos, anfíbios e répteis, besouros coprófagos, borboletas, mariposas, abelhas, árvores e plantas de manguezal, da Amazônia, do Cerrado, da Caatinga, do Pantanal, da Mata Atlântica, do Pampa e do litoral, em 13 estados. Cada linha é um táxon num evento exatamente como foi impresso, em termos Darwin Core, com a página e a tabela de onde saiu.

Essas listas foram impressas como folhetos da Embrapa, artigos de periódico e dissertações de mestrado, e os registros delas não estão no GBIF. Cada documento foi conferido no GBIF antes de ser transcrito, e nenhum dos 28 tinha os seus registros lá. Este dataset torna essas listas pesquisáveis e combináveis com outros dados de ocorrência.

Faz parte do [Paper Rerun](https://paper-rerun.github.io), na linha Open Tables. O trabalho foi feito por agentes de IA num computador doméstico e revisado por uma pessoa antes da publicação.

## Versões

- **v2.0.0** (novembro de 2026): 28 documentos. Junta uma rodada de 20 documentos aos 8 do piloto, todos fundidos com o schema 2.0. O schema novo traz `eventDate` em ISO derivado da data impressa, tira o `basisOfRecord` do que cada documento imprime sobre o destino do material e marca em `name_status` os nomes que a impressão deixa incompletos.
- **v1.0.0** (outubro de 2026): piloto de 8 publicações da Embrapa, 1.152 ocorrências.

## O que tem

| | |
|---|---|
| Publicações | 28: 23 dos repositórios abertos da Embrapa (Alice e Infoteca-e) e 5 dissertações de mestrado dos repositórios da UFU, da UFV e da UFMG; 1982 a 2020 |
| Eventos | 322 (28 estudos, 56 sítios, 21 sítio-campanhas, 90 campanhas, 82 pontos, 23 parcelas, 16 unidades ecológicas e 6 estratos), em AC, AM, GO, MA, MG, MS, PA, PB, PE, PI, PR, RO e RS |
| Ocorrências | 2.850 (2.713 presenças e 137 ausências impressas; 2.436 HumanObservation e 414 PreservedSpecimen), 1.256 nomes distintos como impressos |

| Documento | Grupo | Bioma, UF | Ano | Eventos | Ocorrências |
|---|---|---|---:|---:|---:|
| freydargas2014 | peixes | Pantanal, MS | 2014 | 21 | 138 |
| nunes2009 (aves) | aves | Pantanal, MS | 2009 | 5 | 189 |
| bianconi2004 | morcegos | Mata Atlântica, PR | 2004 | 8 | 56 |
| camargo2009 | mariposas Saturniidae | Cerrado, RO e GO | 2009 | 13 | 95 |
| miranda1982 | anfíbios e répteis | Caatinga, PE | 1982 | 13 | 161 |
| calixto2014 | árvores e arbustos | Caatinga, PE | 2014 | 3 | 106 |
| silva2009 | mamíferos e aves de caça | Amazônia, AC | 2009 | 32 | 231 |
| sandel2000 | árvores, palmeiras e sub-bosque | Amazônia, PA | 2000 | 10 | 176 |
| mai2010 | peixes de currais de pesca | litoral, PI | 2010 | 1 | 118 |
| queiroga2018 | peixes de vereda | Cerrado, MG | 2018 | 14 | 36 |
| winckler2011 | peixes em lavoura de arroz | Pampa, RS | 2011 | 7 | 12 |
| mauricio2018 | aves | Pampa, RS | 2018 | 4 | 193 |
| carvalho2013 | aves aquáticas | Cerrado, MG | 2013 | 58 | 192 |
| silva2009b | mamíferos e aves | Amazônia, AM | 2009 | 32 | 254 |
| dias2006 | mamíferos | Mata Atlântica, PR | 2006 | 3 | 50 |
| nunes2009 (mamíferos) | mamíferos | Mata Atlântica, MG | 2009 | 29 | 86 |
| silveira2010 | morcegos | Pantanal, MS | 2010 | 3 | 36 |
| gordo2003 | anuros | Pantanal, MS | 2003 | 1 | 19 |
| carosini2013 | anuros de serrapilheira | Mata Atlântica, MG | 2013 | 17 | 84 |
| santos2019 | besouros coprófagos | Amazônia, AC | 2019 | 1 | 15 |
| rodrigues2010 | besouros coprófagos | Pantanal, MS | 2010 | 5 | 35 |
| pereira2011 | borboletas | Cerrado, MG | 2011 | 1 | 27 |
| viana2020 | esfingídeos e saturnídeos | Cerrado, MG | 2020 | 16 | 130 |
| lopes2010 | abelhas e plantas visitadas | Cerrado-Caatinga, PI | 2010 | 15 | 172 |
| vieira2002 | árvores | Amazônia, RO | 2002 | 1 | 70 |
| tourinho1998 | manguezal e plantas associadas | litoral amazônico, PA | 1998 | 7 | 87 |
| pereira2012 | plantas lenhosas | Caatinga, PB | 2012 | 1 | 63 |
| rego2008 | abelhas sem ferrão e árvores de ninho | Cerrado, MA | 2008 | 1 | 19 |

Os dois nunes2009 são documentos diferentes, separados pelo `doc_id` (`nunes2009-aves-nhumirim-pantanal-ms` e `nunes2009-mamiferos-serra-do-brigadeiro-mg`).

Arquivos:
- `data/event.csv`: uma linha por evento de amostragem. Os eventos se encaixam por `parentEventID`, do estudo para baixo: sítio, campanha, ponto, parcela, unidade ecológica ou estrato. Um campo que o evento filho não imprime vem do evento acima mais próximo que imprime, e `inherited` diz de qual; coordenada, esforço e tamanho de amostra nunca descem.
- `data/occurrence.csv`: uma linha por ocorrência, com `doc_id`, `page` e `table_or_figure`. O `eventID` aponta para a linha do evento a que ela pertence.
- `data/sources.csv`: as 28 publicações, com autores, link do registro, aviso de licença e a conferência no GBIF feita antes da transcrição.
- `qa/decisions.csv`: cada divergência entre as duas transcrições independentes e como ela foi resolvida conferindo o PDF (3.199 decisões, com a página).
- `qa/name_match.csv`: os nomes distintos, como impressos, conferidos no backbone do GBIF: 1.258 pares de nome e reino, 926 exatos, 110 aproximados, 222 só acima da espécie (150 deles impressos com "sp.", "aff.", "cf." ou "gr.") e 0 sem resultado. É conferência, não dado; o dataset não muda com ela.
- `method/`: o schema (`schema.json`, gerado por `build_schema.py`), os scripts de comparação, junção e conferência de nomes, e as checagens do schema e dos arquivos arbitrados.

### Colunas

Junte os dois arquivos de dados por `eventID`. O arquivo de eventos usa os termos Darwin Core `eventID`, `parentEventID`, `eventType`, `verbatimLocality`, `municipality`, `stateProvince`, `verbatimCoordinates`, `verbatimEventDate`, `eventDate`, `habitat`, `samplingProtocol`, `samplingEffort` e `recordedBy`. O de ocorrências usa `occurrenceID`, `eventID`, `basisOfRecord`, `eventDate`, `scientificName`, `identificationQualifier`, `family`, `order`, `vernacularName`, `occurrenceStatus`, `individualCount`, `organismQuantity` e `organismQuantityType`. As colunas que não têm termo no Darwin Core ficam com nomes nossos (`value_as_printed`, `printed_code`, `code_meaning`, `record_origin`, `name_status`, `material_fate`, `source_inconsistency` e outras) e estão descritas em `method/schema.json`.

Nomes e coordenadas ficam exatamente como impressos. `scientificName` traz a autoria, o qualificador e qualquer erro de grafia da fonte; o GBIF interpreta. `stateProvince` também vem como impresso, então é "MG" em alguns documentos e "Minas Gerais" em outros. `verbatimEventDate` guarda a data impressa. `eventDate` é a data ou o intervalo em ISO tirado dela, preenchido em 1.087 ocorrências, e `eventDate_derivation` diz como. Data impressa ambígua deixa `eventDate` vazio. A coordenada está só em `verbatimCoordinates`: `decimalLatitude` e `decimalLongitude` estão vazias.

`basisOfRecord` vem de `material_fate`, o que o documento imprime sobre o material. Só `deposited_in_collection` vira PreservedSpecimen; `released_or_observed`, `vouchers_not_tied_to_records` e `not_stated` viram HumanObservation. `basisOfRecord_source` diz de qual evento veio.

## Como foi feito

1. **Coleta.** Os agentes percorreram os repositórios abertos da Embrapa pelo OAI-PMH e buscaram nos repositórios DSpace de três universidades (UFU, UFV e UFMG), leram a página do registro e o PDF de cada candidato e registraram cada um que não entrou, com o motivo. Só entrou documento cujos registros não estão no GBIF: cada candidato passou por uma busca de dataset pelo título, uma busca de ocorrência de 3 espécies da própria tabela numa caixa em volta do local (e nos anos impressos, quando há) e uma busca do sobrenome de cada autor na mesma caixa, com cada acerto olhado à mão. O resultado dessa conferência para cada documento está em `data/sources.csv`. O piloto leu 40 candidatos e ficou com 8; a rodada leu 49 e ficou com 20. Os repositórios do ICMBio e do INPA não responderam em nenhuma das duas.
2. **Duas transcrições independentes.** Dois agentes por publicação transcreveram os eventos (local, data, coordenada, habitat, protocolo, esforço, coletores, destino do material), um inventário das tabelas e figuras e cada célula de espécie num schema fixo, sem ver o trabalho um do outro, copiando nomes, datas e números exatamente como impressos.
3. **Comparação e arbitragem.** Um script pareou as duas transcrições evento por evento e registro por registro e listou cada divergência e cada item presente em só uma delas. Cada caso foi resolvido conferindo o PDF, com a página como evidência. Na rodada, cada documento ainda passou por uma conferência à parte do local, da data e do método de cada tabela, para pegar o erro de contexto que as duas transcrições cometem juntas.
4. **Conferência de nomes.** Os nomes distintos foram mandados como impressos para o match de espécies do GBIF, com o reino de cada tabela. Morfoespécie ("Ataenius sp.1") vai só com o gênero, porque o match aproximado escolheria uma espécie real pela semelhança das letras. Nada no dataset mudou com isso.

## Qual a precisão

- **Nomes e números:** nos 2.839 registros pareados, nenhuma letra de nome foi lida errado em nenhuma das duas transcrições. Um algarismo foi lido errado uma vez, no piloto (miranda1982 Fig. 13, "0,18" lido como "0,16"), e corrigido. Os nomes aproximados no GBIF são grafia da fonte (*Anisostremus* por *Anisotremus*, *Goupia glaba*), lida igual pelas duas transcrições.
- **Registros inteiros:** contando os registros que cada uma deixou de fora, uma transcrição sozinha acertou por inteiro 81,2% dos registros da rodada, e a outra 92,0% (98,5% e 77,8% no piloto). Quase todo erro vem de uma regra perdida num documento inteiro, como um cabeçalho de coluna cortado, a legenda de um código copiada no registro ou uma métrica derivada tomada por contagem. Sem esses casos, as duas ficam perto de 94% na rodada. As 3.199 divergências foram resolvidas conferindo o PDF, então o dataset não depende de nenhuma das duas transcrições sozinha.
- **Erros de contexto:** na rodada, em 12 casos em 9 documentos as duas transcrições concordaram no evento, no método ou no habitat errado de um bloco de registros (459 ocorrências). A conferência de contexto pegou os 12, e 11 foram corrigidos. O que sobra: as 12 árvores das descrições de sítio de lopes2010 herdam o protocolo de coleta de abelhas do evento do estudo, porque o schema ainda não deixa bloquear essa herança.
- **Limites conhecidos:**
  - Ainda não há coordenada decimal. 2.108 ocorrências têm coordenada impressa no próprio evento ou num evento acima; em sandel2000 ela é a faixa da floresta inteira, não um ponto.
  - `eventDate` está vazio em 1.763 ocorrências. Alguns documentos não imprimem data nenhuma (calixto2014, nunes2009 aves, sandel2000), e 670 ocorrências da rodada têm data num formato que a junção ainda não lê ("2015-2016", "2018 / Outubro", "início em ... término em").
  - 14 ocorrências têm `name_status` `incomplete_in_print`: a linha não imprime nome de espécie, ou o nome está ilegível, então `scientificName` fica vazio ou parcial. Os gêneros abreviados da Tabela 2 de calixto2014 e de carvalho2013 ficam como impressos.
  - 41 registros de nunes2009 (aves) juntam observação de campo dos autores e literatura citada: `record_origin` é `mixed`, e a fonte de cada um está em `printed_code` e `code_meaning`. Da rodada em diante, uma célula que junta fontes vira um registro por fonte.
  - nunes2009 (aves) é um recorte: só as páginas 11 a 13 da lista de espécies foram usadas.
  - miranda1982 é um documento escaneado sem camada de texto útil. Foi lido a partir da imagem da página, e nele não rodam a busca de texto copiado nem a de aviso de direitos.

Por enquanto o dataset não está publicado no GBIF.

## Licença e citação

- O dataset (os arquivos CSV, o schema e os scripts) é publicado sob a licença [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Por favor, cite as publicações originais listadas em `data/sources.csv` e também este dataset. Cada linha também traz a sua fonte em `bibliographicCitation` e o aviso de licença dessa fonte em `license`.
- As publicações não são redistribuídas. Os repositórios da Embrapa exibem um aviso CC BY-NC-ND 4.0 na página de todo registro, e não uma licença do item, e vários folhetos da Embrapa trazem "Todos os direitos reservados". Artigos de periódico mantêm os próprios termos. As 5 dissertações trazem só "Acesso Aberto", sem licença Creative Commons. Aqui são usadas só as ocorrências, que são fatos, e citações curtas.

Erros ou registros que faltam: por favor, [abra uma issue](https://github.com/paper-rerun/biodiversity-inventories-br/issues).

## Como este dataset foi feito

Este dataset foi montado por agentes de IA (Claude, da Anthropic) num computador doméstico e revisado por uma pessoa antes da publicação. Nenhum valor foi estimado ou digitado à mão: cada um foi transcrito do PDF original duas vezes, de forma independente, e cada divergência foi conferida na página. O método e os scripts estão em `method/`. Como funciona o projeto como um todo (em inglês): https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md

Contato: Filipe Tessaro, pelas issues deste repositório.
