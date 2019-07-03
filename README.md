Convert a description of a schema in yaml (the way oerschema.org does it) into rdfs in turtle.

optional arguments:
  -h, --help            show this help message and exit
  -if <file path>, --infile <file path>
                        input file, the YAML description of oerschema.org
  -of <file path>, --outfile <file path>
                        output file, the RDFS description of oerschema.org in
                        turtle

If no arguments are supplied defaults to schema.yaml and schema.ttl for input and output file names.
