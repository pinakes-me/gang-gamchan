"""강감찬자료실 LOD 파일럿: CSV → Turtle 변환.

사용법: python scripts/csv_to_ttl.py
입력:  data/books.csv, vocab/concepts.csv
출력:  output/concepts.ttl, output/books.ttl
"""
import csv
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS, OWL, XSD

BASE = Path(__file__).resolve().parent.parent
SCHEMA = Namespace("https://schema.org/")
GGO = Namespace("https://pinakes-me.github.io/gang-gamchan/ontology#")
GGC = Namespace("https://pinakes-me.github.io/gang-gamchan/vocab#")
GGR = Namespace("https://pinakes-me.github.io/gang-gamchan/resource/")

HOLDINGS = {
    "관악중앙도서관": GGO["lib-gwanak-central"],
    "용꿈꾸는작은도서관": GGO["lib-yongkkum"],
    "책사랑작은도서관": GGO["lib-chaeksarang"],
    "뜰안에작은도서관": GGO["lib-tteuran"],
    "성현동작은도서관": GGO["lib-seonghyeon"],
    "글빛정보도서관": GGO["lib-geulbit"],
    "보물섬작은도서관": GGO["lib-bomulseom"],
    "낙성대공원도서관": GGO["lib-nakseongdae-park"],
    "조원도서관": GGO["lib-jowon"],
    "은천동작은도서관": GGO["lib-eunchen"],
    "우리작은도서관": GGO["lib-woori"],
    "다사랑작은도서관": GGO["lib-dasarang"],
    "꿈나무영유아도서관": GGO["lib-kkumnamu"],
    "굴렁쇠작은도서관": GGO["lib-gulleongsoe"],
    "글사랑작은도서관": GGO["lib-geulsarang"],
    "어울작은도서관": GGO["lib-eoul"],
    "울타리작은도서관": GGO["lib-ultari"],
    "새싹작은도서관": GGO["lib-saessak"],
}


def bind(g):
    g.bind("schema", SCHEMA)
    g.bind("ggo", GGO)
    g.bind("ggc", GGC)
    g.bind("ggr", GGR)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("owl", OWL)


def build_concepts():
    g = Graph()
    bind(g)
    scheme = GGC["scheme"]
    g.add((scheme, RDF.type, SKOS.ConceptScheme))
    g.add((scheme, SKOS.prefLabel, Literal("강감찬자료실 주제어휘 초안", lang="ko")))
    with open(BASE / "vocab/concepts.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            c = GGC[row["concept_id"]]
            g.add((c, RDF.type, SKOS.Concept))
            g.add((c, SKOS.inScheme, scheme))
            g.add((c, SKOS.prefLabel, Literal(row["pref_label_ko"], lang="ko")))
            if row["pref_label_en"]:
                g.add((c, SKOS.prefLabel, Literal(row["pref_label_en"], lang="en")))
            if row["broader"]:
                g.add((c, SKOS.broader, GGC[row["broader"]]))
            else:
                g.add((scheme, SKOS.hasTopConcept, c))
            if row["wikidata"]:
                g.add((c, OWL.sameAs, URIRef(row["wikidata"])))
            if row["scope_note"]:
                g.add((c, SKOS.scopeNote, Literal(row["scope_note"], lang="ko")))
    return g


def build_books():
    g = Graph()
    bind(g)
    with open(BASE / "data/books.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            b = GGR[f"book/{row['id']}"]
            g.add((b, RDF.type, SCHEMA.Book))
            g.add((b, DCTERMS.title, Literal(row["title"], lang="ko")))
            g.add((b, SCHEMA.author, Literal(row["creator"])))
            g.add((b, SCHEMA.publisher, Literal(row["publisher"])))
            g.add((b, SCHEMA.datePublished, Literal(row["year"], datatype=XSD.gYear)))
            g.add((b, GGO.sourceList, GGO["list-books"]))
            if row["series_note"]:
                g.add((b, SCHEMA.isPartOf, Literal(row["series_note"])))
            if row["volume_note"]:
                g.add((b, SCHEMA.volumeNumber, Literal(row["volume_note"])))
            for h in filter(None, row["holdings"].split(";")):
                lib = HOLDINGS.get(h.strip())
                if lib:
                    g.add((b, GGO.heldBy, lib))
            for s in filter(None, row["subjects"].split(";")):
                g.add((b, DCTERMS.subject, GGC[s.strip()]))
            if row.get("isbn"):
                g.add((b, SCHEMA.isbn, Literal(row["isbn"])))
            if row["review_flag"] == "Y":
                g.add((b, RDFS.comment, Literal(f"검수 필요: {row['note']}", lang="ko")))
    return g


if __name__ == "__main__":
    out = BASE / "output"
    out.mkdir(exist_ok=True)
    build_concepts().serialize(out / "concepts.ttl", format="turtle")
    g = build_books()
    g.serialize(out / "books.ttl", format="turtle")
    print(f"books.ttl: {len(g)} triples")
