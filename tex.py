
class TexFile:

    def __init__(self, file_name):
        self.file = open(file_name, "w")

    def write_table_column(self, *args):
        for i in range(len(args) - 1):
            self.file.write("{} & ".format(args[i]))
        self.file.write(" {} \\\\\n".format(args[-1]))

    def write_table(self, table_content, ref = None, caption = None):
        # write table header
        self.file.write("\\begin{table}\n")
        self.file.write("\\centering\n")
        if caption is not None:
            self.file.write("\\caption{{}}\n".format(caption))
        if ref is not None:
            self.file.write("\\label{{}}\n".format(ref))

        #write tabular header and
        self.file.write("\\begin{tabular}{|")
        for i in range(len(table_content.keys())):
            self.file.write("c|")
        self.file.write("}\n")
        self.file.write("\\hline\n")
        self.write_table_column(*table_content.keys())
        self.file.write("\\hline\n")

        #write table body
        try:
            row = list()
            keys = list(table_content.keys())
            for i in range(len(table_content[keys[0]])):
                row.clear()
                for k in keys:
                    row.append(table_content[k][i])
                self.write_table_column(*row)
        except IndexError:
            raise InvalidArgument("table_content shall contain only lists of same length")

        #close everything
        self.file.write("\\hline")
        self.file.write("\\end{tabular}")
        self.file.write("\\end{table}")
