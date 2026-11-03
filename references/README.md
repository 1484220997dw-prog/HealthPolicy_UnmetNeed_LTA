# references/

One PDF per reference, named by its position in the manuscript's citation order, plus
machine-readable metadata.

| File | What it is |
|---|---|
| `NN_Author1234_slug.pdf` | the reference itself, one per citation |
| `references.csv` | Crossref metadata for every reference, and how each PDF was obtained |
| `references.bib` | the same records as BibTeX |
| `reference_list_vancouver.txt` | the numbered list, ready to paste into the manuscript |
| `fetch_references.py` | the script that built all of the above |

## How the PDFs were obtained

`fetch_references.py` takes a list of DOIs and, for each one:

1. fetches the canonical record from **Crossref**, so the bibliography cannot contain an
   invented citation — a DOI that does not resolve is reported and excluded;
2. asks **Unpaywall** and the **Europe PMC** and **PMC Open Access** services whether a
   legally free full text exists, and downloads it if so;
3. writes a one-page **citation record** as a PDF when no open copy is offered.

Of the 29 references, **10 are open-access full texts** and **19 are citation records**
for articles behind a paywall. Seven of the ten open-access items are typeset from the
Europe PMC open-access XML, with the licence statement reproduced on the first page,
because the publishers do not serve their own PDF to an identified automated client; the
version of record is at the DOI printed on each file.

The script identifies itself honestly in every request and does not retry against
servers that decline automated access. Reach the paywalled items through the DOI link on
their citation record, using an institutional subscription or a library service, and
replace the citation record with the publisher's PDF if you want the full set locally.

## Refreshing

```bash
python fetch_references.py
```

```bash
python fetch_references.py --no-download
```

The second form refreshes the metadata and the citation records without downloading
anything.
