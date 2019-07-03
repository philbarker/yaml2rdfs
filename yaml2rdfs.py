#!/usr/bin/env python3
import sys, yaml
from argparse import ArgumentParser
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS


class Schema:
    def __init__(self, infile_name: str):
        with open(infile_name, "r") as infile:
            try:
                self.yaml = yaml.safe_load(infile)
                print("INFO: yaml loaded from %s" % infile_name)
            except IOError as exc:
                msg = "FATAL ERROR: could not load yaml from " + infile_name
                print(msg)
                print(exc)
            except yaml.YAMLError as exc:
                msg = "FATAL ERROR: could not parse yaml from " + infile_name
                print(msg)
                print(exc)
            self.make_graph()

    def make_graph(self):
        SDO = Namespace("http://schema.org/")
        OER = Namespace("http://oerschema.org/")
        self.g = Graph()
        self.g.bind("sdo", "http://schema.org/")
        self.g.bind("oer", "http://oerschema.org/")
        for aClass, defn in self.yaml["classes"].items():
            if aClass != "":
                self.g.add((OER[aClass], RDF.type, RDFS.Class))
                if "label" in defn.keys():
                    self.g.add((OER[aClass], RDFS.label, Literal(defn["label"])))
                if "comment" in defn.keys():
                    self.g.add((OER[aClass], RDFS.comment, Literal(defn["comment"])))
                if "subClassOf" in defn.keys():
                    for parentClass in defn["subClassOf"]:
                        if parentClass[:5] == "http:":
                            self.g.add(
                                (OER[aClass], RDFS.subClassOf, URIRef(parentClass))
                            )
                        elif parentClass == "rdfs:datatype":
                            self.g.add((OER[aClass], RDFS.subClassOf, RDFS.Datatype))
                        elif (len(parentClass) > 5) and (parentClass[5] == "rdfs:"):
                            self.g.add(
                                (OER[aClass], RDFS.subClassOf, RDFS[parentClass])
                            )
                        else:
                            self.g.add((OER[aClass], RDFS.subClassOf, OER[parentClass]))
            else:
                pass  # honestly don't know why get blank keys
        for aProperty, defn in self.yaml["properties"].items():
            if aProperty != "":
                self.g.add((OER[aProperty], RDF.type, RDF.Property))
                self.g.add((OER[aProperty], RDF.type, OER.Property))
                if "label" in defn.keys():
                    self.g.add((OER[aProperty], RDFS.label, Literal(defn["label"])))
                if ("comment" in defn.keys()) and (defn["comment"] != ""):
                    self.g.add((OER[aProperty], RDFS.comment, Literal(defn["comment"])))
                if "range" in defn.keys():
                    for aRange in defn["range"]:
                        self.g.add((OER[aProperty], SDO["rangeIncludes"], OER[aRange]))
                if "domain" in defn.keys():
                    for aDomain in defn["range"]:
                        self.g.add(
                            (OER[aProperty], SDO["domainIncludes"], OER[aDomain])
                        )
            else:
                pass  # honestly don't know why get blank keys
        print("INFO: yaml converted to RDFS graph")

    def print_graph(self):
        print(self.g.serialize(format="turtle").decode("utf-8"))

    def save_graph(self, outfile_name: str):
        try:
            with open(outfile_name, "w") as outfile:
                outfile.write(self.g.serialize(format="turtle").decode("utf-8"))
        except IOError as exc:
            msg = "ERROR: could not open %s to save RDFS" % outfile_name
            print(msg)
            print(exc)
            return
        print("INFO: RDFS saved as turtle to %s" % outfile_name)


def parse_arguments():
    parser = ArgumentParser(
        prog="yaml2rdfs.py",
        description="convert yaml description of oerschema.org classes and properties into RDFS in turtle.",
    )
    parser.add_argument(
        "-if",
        "--infile",
        type=str,
        default="schema.yml",
        metavar="<file path>",
        help="input file, the YAML description of oerschema.org",
    )
    parser.add_argument(
        "-of",
        "--outfile",
        type=str,
        default="schema.ttl",
        metavar="<file path>",
        help="output file, the RDFS description of oerschema.org in turtle",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    schema = Schema(args.infile)
    schema.save_graph(args.outfile)
