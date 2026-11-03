"""Assemble the reference library for the manuscript.

For every DOI in REFERENCES the script

  1. pulls the canonical record from Crossref, so that the bibliography cannot
     contain an invented citation - a DOI that does not resolve is reported and
     excluded;
  2. looks for a legally free full text through interfaces that are meant for
     programmatic access - Unpaywall, the Europe PMC REST service, and the
     ``citation_pdf_url`` metadata tag that publishers expose for indexers - and
     downloads the PDF when one is offered;
  3. writes a one-page citation card as a PDF when no open copy is offered, so
     that the folder holds one file per reference either way;
  4. writes references.csv, references.bib and a numbered Vancouver list from
     the Crossref records.

The script identifies itself honestly in every request and does not retry
against servers that decline automated access; those references are represented
by their citation card, and the DOI link reaches the publisher's copy.

Run:  python fetch_references.py            (add --no-download for metadata only)
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace",
                              line_buffering=True)

HERE = Path(__file__).resolve().parent

# Crossref and Unpaywall ask callers to identify themselves with a contact
# address, which buys access to their faster "polite" pools. Set CROSSREF_EMAIL
# to your own address; the fallback keeps the script working without publishing
# anyone's personal address in this repository.
CONTACT = os.environ.get("CROSSREF_EMAIL", "anonymous@example.org")
UA = {
    "User-Agent": f"khp-unmet-need-lta-reference-fetcher/1.0 (mailto:{CONTACT})",
    "Accept": "application/pdf,application/xml,text/html;q=0.9,*/*;q=0.8",
}

# DOI -> short slug used for the file name, in citation order
REFERENCES: list[tuple[str, str]] = [
    ("10.2190/MCG0-UH8D-0AG8-VFNU", "01_CarrWolfe1976_unmet_need_indicators"),
    ("10.2307/2137284", "02_Andersen1995_behavioral_model"),
    ("10.1258/135581902760082517", "03_Gulliford2002_what_is_access"),
    ("10.1186/1475-9276-12-18", "04_Levesque2013_patient_centred_access"),
    ("10.1016/j.socscimed.2009.10.027", "05_Allin2010_subjective_unmet_need"),
    ("10.1787/3c8385d0-en", "06_OECD2019_health_for_everyone"),
    ("10.1787/507433b0-en", "07_OECD2022_health_at_a_glance_europe"),
    ("10.1787/7a7afb35-en", "08_OECD2023_health_at_a_glance"),
    ("10.1596/40348", "09_WHO_WorldBank2023_uhc_monitoring"),
    ("10.1093/heapol/czn037", "10_Kwon2009_thirty_years_nhi_korea"),
    ("10.1016/j.healthpol.2010.08.008", "11_KimYang2011_catastrophic_expenditure"),
    ("10.1016/j.healthpol.2016.04.005", "12_Ko2016_unmet_need_health_status"),
    ("10.1186/s12913-018-3369-2", "13_Hwang2018_reasons_for_unmet_need"),
    ("10.3389/fpubh.2022.828318", "14_Chung2022_financial_nonfinancial_barriers"),
    ("10.1186/s12903-017-0370-9", "15_Kim2017_inequality_unmet_dental"),
    ("10.3390/healthcare8020124", "16_Sohn2020_unmet_dental_income"),
    ("10.1186/s12939-024-02206-3", "17_Ji2024_coverage_expansion_spending"),
    ("10.1016/j.socscimed.2024.116574", "18_Eun2024_coverage_expansion_mortality"),
    ("10.3390/healthcare14030302", "19_Kim2026_catastrophic_coverage_noncovered"),
    ("10.1007/s10433-021-00631-9", "20_Smolic2021_access_covid_europe"),
    ("10.1002/9780470567333", "21_CollinsLanza2010_latent_transition_analysis"),
    ("10.1037/0012-1649.44.2.446", "22_LanzaCollins2008_lta_procedure"),
    ("10.1080/10705510701575396", "23_Nylund2007_number_of_classes"),
    ("10.1037/tps0000176", "24_NylundGibsonChoi2018_ten_questions_lca"),
    ("10.1093/pan/mpq025", "25_Vermunt2010_three_step"),
    ("10.1093/pan/mpu003", "26_Bakk2014_standard_errors_three_step"),
    ("10.1007/s11336-017-9592-7", "27_BakkKuha2018_two_step"),
    ("10.1111/j.2517-6161.1977.tb01600.x", "28_Dempster1977_em_algorithm"),
    ("10.1111/j.1467-9469.2007.00585.x", "29_VaradhanRoland2008_squarem"),
]


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def crossref(doi: str) -> dict | None:
    try:
        raw = _get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
        return json.loads(raw)["message"]
    except Exception as exc:                       # noqa: BLE001
        print(f"  ! Crossref lookup failed for {doi}: {exc}")
        return None


def _meta_pdf_url(url: str) -> str | None:
    """Read the citation_pdf_url tag that publishers publish for indexers."""
    try:
        html = _get(url).decode("utf-8", "replace")
    except Exception:                              # noqa: BLE001
        return None
    for pat in (r'name=["\']citation_pdf_url["\'][^>]*content=["\']([^"\']+)',
                r'content=["\']([^"\']+)["\'][^>]*name=["\']citation_pdf_url'):
        m = re.search(pat, html, flags=re.I)
        if m:
            return m.group(1)
    return None


def _open_access_record(doi: str) -> dict | None:
    """Europe PMC record for the DOI, which states open-access status and PMCID."""
    try:
        q = urllib.parse.urlencode({"query": f'DOI:"{doi}"', "format": "json",
                                    "resultType": "core", "pageSize": 1})
        res = json.loads(_get("https://www.ebi.ac.uk/europepmc/webservices/rest/"
                              f"search?{q}"))
        hits = res.get("resultList", {}).get("result", [])
    except Exception:                              # noqa: BLE001
        return None
    for h in hits:
        if h.get("isOpenAccess") == "Y" and h.get("pmcid"):
            return h
    return None


def _pmc_oa_pdf_url(pmcid: str) -> str | None:
    """The PMC Open Access Service, which NCBI provides for programmatic use."""
    try:
        xml = _get("https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id="
                   + urllib.parse.quote(pmcid)).decode("utf-8", "replace")
    except Exception:                              # noqa: BLE001
        return None
    m = re.search(r'<link[^>]+format="pdf"[^>]+href="([^"]+)"', xml)
    if not m:
        m = re.search(r'<link[^>]+href="([^"]+)"[^>]+format="pdf"', xml)
    if not m:
        return None
    return m.group(1).replace("ftp://ftp.ncbi.nlm.nih.gov/",
                              "https://ftp.ncbi.nlm.nih.gov/")


def render_xml_to_pdf(pmcid: str, rec: dict, path: Path) -> str | None:
    """Typeset the Europe PMC open-access JATS full text as a readable PDF.

    Used only for articles Europe PMC reports as open access, when the
    publisher's own PDF is not served to an identified client.  The licence
    statement carried in the XML is reproduced on the first page.
    """
    try:
        xml = _get("https://www.ebi.ac.uk/europepmc/webservices/rest/"
                   f"{pmcid}/fullTextXML", timeout=90).decode("utf-8", "replace")
    except Exception as exc:                       # noqa: BLE001
        print(f"  . Europe PMC full text unavailable ({exc})")
        return None
    if "<body" not in xml:
        return None

    import xml.etree.ElementTree as ET
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    def text_of(el) -> str:
        return re.sub(r"\s+", " ", "".join(el.itertext())).strip()

    root = ET.fromstring(xml)
    styles = getSampleStyleSheet()
    body = ParagraphStyle("b", parent=styles["Normal"], fontSize=10, leading=14,
                          spaceAfter=5)
    small = ParagraphStyle("s", parent=styles["Normal"], fontSize=8, leading=11,
                           textColor="#555555")
    title = re.sub(r"<[^>]+>|\s+", " ", (rec.get("title") or ["?"])[0]).strip()
    flow = [Paragraph(f"<b>{title}</b>", styles["Heading2"]),
            Paragraph(fmt_authors(rec, limit=25), body),
            Paragraph(vancouver(rec), small), Spacer(1, 8)]

    lic = root.find(".//license")
    if lic is not None:
        flow += [Paragraph("Licence: " + text_of(lic), small), Spacer(1, 4)]
    flow += [Paragraph("Full text retrieved from the Europe PMC open-access "
                       "REST service and typeset for this reference library; "
                       "figures and tables are omitted. The publisher's version "
                       "of record is at the DOI above.", small), Spacer(1, 12)]

    abstract = root.find(".//abstract")
    if abstract is not None:
        flow += [Paragraph("Abstract", styles["Heading4"]),
                 Paragraph(text_of(abstract), body), Spacer(1, 6)]
    for sec in root.findall(".//body//sec"):
        head = sec.find("title")
        if head is not None and text_of(head):
            flow.append(Paragraph(text_of(head), styles["Heading4"]))
        for para in sec.findall("p"):
            t = text_of(para)
            if t:
                flow.append(Paragraph(t.replace("&", "&amp;"), body))
    if len(flow) < 8:
        return None
    SimpleDocTemplate(str(path), pagesize=A4, title=title[:120],
                      author=fmt_authors(rec)).build(flow)
    node = root.find(".//license")
    return ("open-access full text rendered from Europe PMC XML"
            + (f" ({text_of(node)[:60]}...)" if node is not None else ""))


def candidate_urls(doi: str) -> tuple[list[str], str | None]:
    """Free-to-read candidates, in order of how likely they are to be a PDF."""
    out: list[str] = []
    licence = None
    try:
        up = json.loads(_get(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}"
                             f"?email={CONTACT}"))
    except Exception as exc:                       # noqa: BLE001
        print(f"  ! Unpaywall lookup failed: {exc}")
        up = {}
    locs = [up.get("best_oa_location") or {}] + list(up.get("oa_locations") or [])
    licence = next((l.get("license") for l in locs if l.get("license")), None)
    for loc in locs:
        for key in ("url_for_pdf", "url"):
            u = loc.get(key)
            if u and u not in out:
                out.append(u)
    epmc = _open_access_record(doi)
    if epmc:
        pmc_pdf = _pmc_oa_pdf_url(epmc["pmcid"])
        if pmc_pdf:
            out.insert(0, pmc_pdf)
    if doi.startswith("10.3390/"):                 # MDPI serves /pdf for every item
        out.append(f"https://www.mdpi.com/{doi.split('/', 1)[1]}/pdf")
    if not up.get("is_oa") and not epmc:
        out = []
    return out, licence, (epmc or {}).get("pmcid")


def fmt_authors(rec: dict, limit: int = 6) -> str:
    au = rec.get("author") or []
    if not au:
        return rec.get("publisher") or "Anon"
    names = []
    for a in au[:limit]:
        initials = "".join(p[0] for p in a.get("given", "").split() if p)[:2]
        names.append(f"{a.get('family', '')} {initials}".strip())
    return ", ".join(names) + (", et al." if len(au) > limit else "")


def vancouver(rec: dict) -> str:
    year = (rec.get("issued", {}).get("date-parts") or [[None]])[0][0]
    title = re.sub(r"<[^>]+>|\s+", " ", (rec.get("title") or ["?"])[0]).strip().rstrip(".")
    journal = (rec.get("container-title") or [rec.get("publisher", "")])[0]
    bits = journal
    if year:
        bits += f" {year}"
    if rec.get("volume"):
        bits += f";{rec['volume']}"
    if rec.get("issue"):
        bits += f"({rec['issue']})"
    if rec.get("page"):
        bits += f":{rec['page']}"
    return f"{fmt_authors(rec)}. {title}. {bits}. doi:{rec.get('DOI')}"


def citation_card(rec: dict, path: Path, note: str) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    styles = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=11, leading=15)
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=9,
                           leading=12, textColor="#555555")
    title = re.sub(r"<[^>]+>|\s+", " ", (rec.get("title") or ["Reference"])[0]).strip()
    doc = SimpleDocTemplate(str(path), pagesize=A4, title=title[:120],
                            author=fmt_authors(rec))
    year = (rec.get("issued", {}).get("date-parts") or [[None]])[0][0]
    doc.build([
        Paragraph("Reference record", styles["Heading2"]),
        Spacer(1, 6),
        Paragraph(f"<b>{title}</b>", body),
        Spacer(1, 6),
        Paragraph(fmt_authors(rec, limit=20), body),
        Spacer(1, 4),
        Paragraph(f"{(rec.get('container-title') or [rec.get('publisher', '')])[0]}"
                  f"{f', {year}' if year else ''}", body),
        Spacer(1, 10),
        Paragraph(f"DOI: <link href='https://doi.org/{rec.get('DOI')}'>"
                  f"https://doi.org/{rec.get('DOI')}</link>", body),
        Spacer(1, 14),
        Paragraph("Full citation (Vancouver)", styles["Heading4"]),
        Paragraph(vancouver(rec), body),
        Spacer(1, 16),
        Paragraph(note, small),
    ])


CARD_NOTE = ("No open-access full text is offered for this reference, so the folder "
             "holds its verified citation record instead. Follow the DOI link above "
             "to the publisher's copy through an institutional subscription or a "
             "library service.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-download", action="store_true",
                    help="refresh metadata and citation cards only")
    args = ap.parse_args()

    rows, bib = [], []
    for doi, slug in REFERENCES:
        print(f"[{slug}]")
        rec = crossref(doi)
        if rec is None:
            rows.append({"slug": slug, "doi": doi, "status": "DOI DID NOT RESOLVE"})
            continue
        target = HERE / f"{slug}.pdf"
        status, used_url, licence = "citation card (no open full text)", "", None
        pmcid = None
        if not args.no_download:
            candidates, licence, pmcid = candidate_urls(doi)
            seen: set[str] = set()
            while candidates:
                url = candidates.pop(0)
                if url in seen:
                    continue
                seen.add(url)
                try:
                    data = _get(url, timeout=90)
                except Exception as exc:           # noqa: BLE001
                    print(f"  . declined: {url[:70]} ({exc})")
                    continue
                if data[:4] == b"%PDF":
                    target.write_bytes(data)
                    used_url = url
                    status = f"open-access PDF ({licence or 'licence not stated'})"
                    break
                alt = _meta_pdf_url(url)
                print(f"  . landing page: {url[:70]}"
                      f"{' -> citation_pdf_url found' if alt else ''}")
                if alt and alt not in seen:
                    candidates.insert(0, alt)
                time.sleep(0.5)
        if not status.startswith("open-access") and pmcid:
            rendered = render_xml_to_pdf(pmcid, rec, target)
            if rendered:
                status, used_url = rendered, (
                    "https://www.ebi.ac.uk/europepmc/webservices/rest/"
                    f"{pmcid}/fullTextXML")
        if not status.startswith("open-access"):
            citation_card(rec, target, CARD_NOTE)
        print(f"  -> {status}")

        year = (rec.get("issued", {}).get("date-parts") or [[None]])[0][0]
        rows.append({
            "slug": slug, "doi": doi, "status": status,
            "authors": fmt_authors(rec, limit=20),
            "title": re.sub(r"<[^>]+>|\s+", " ",
                            (rec.get("title") or ["?"])[0]).strip(),
            "container": (rec.get("container-title") or [rec.get("publisher", "")])[0],
            "year": year, "volume": rec.get("volume", ""), "issue": rec.get("issue", ""),
            "page": rec.get("page", ""), "type": rec.get("type", ""),
            "vancouver": vancouver(rec), "source_url": used_url,
            "license": licence or "",
        })
        key = slug.split("_", 1)[1].split("_")[0] + str(year or "")
        entry_type = "book" if rec.get("type") in ("book", "monograph") else "article"
        bib.append(
            f"@{entry_type}{{{key},\n"
            f"  author = {{{fmt_authors(rec, limit=20)}}},\n"
            f"  title = {{{rows[-1]['title']}}},\n"
            f"  journal = {{{(rec.get('container-title') or [''])[0]}}},\n"
            f"  publisher = {{{rec.get('publisher', '')}}},\n"
            f"  year = {{{year or ''}}},\n"
            f"  volume = {{{rec.get('volume', '')}}},\n"
            f"  number = {{{rec.get('issue', '')}}},\n"
            f"  pages = {{{rec.get('page', '')}}},\n"
            f"  doi = {{{rec.get('DOI')}}}\n}}\n")
        time.sleep(0.4)

    fields = ["slug", "doi", "status", "authors", "title", "container", "year",
              "volume", "issue", "page", "type", "vancouver", "source_url", "license"]
    with (HERE / "references.csv").open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields)
        wr.writeheader()
        for r in rows:
            wr.writerow({k: r.get(k, "") for k in fields})
    (HERE / "references.bib").write_text("\n".join(bib), encoding="utf-8")
    (HERE / "reference_list_vancouver.txt").write_text(
        "\n".join(f"[{i}] {r['vancouver']}" for i, r in enumerate(rows, start=1)
                  if r.get("vancouver")), encoding="utf-8")
    n_oa = sum(r["status"].startswith("open-access") for r in rows)
    print(f"\n{len(rows)} references processed; {n_oa} open-access full texts "
          f"downloaded, {len(rows) - n_oa} citation cards written.")


if __name__ == "__main__":
    main()
