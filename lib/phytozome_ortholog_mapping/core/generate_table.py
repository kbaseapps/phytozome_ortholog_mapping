from urllib.request import urlopen
import time
import json
import sys
import os
import re

class GenerateTable:

    def log(self,message, prefix_newline=False):
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
        print(('\n' if prefix_newline else '') + time_str + ': ' + message)

    def __init__(self):
        pass

    def generate_table(self, table_dict):

        html_lines=list()
        html_lines.append('<table class="table table-bordered table-striped">')

        header_list = ["Feature","Ortholog","InParanoid Score"]

        html_lines.append('<thead>')
        internal_header_line = "</td><td>".join(header_list)
        html_lines.append('<tr><td>'+internal_header_line+'</td></tr>')
        html_lines.append('</thead>')

        html_lines.append("<tbody>")
        for feature in sorted(table_dict.keys()):
            for ortholog in sorted(table_dict[feature].keys()):
                html_lines.append("<tr>")
                internal_row_line = "</td><td>".join([feature,
                                                      ortholog,
                                                      table_dict[feature][ortholog]])
                html_lines.append("<td>"+internal_row_line+"</td>")
                html_lines.append("</tr>")
        html_lines.append("</tbody>")
        html_lines.append("</table>")

        return "\n".join(html_lines)

def main():

    table = GenerateTable()

    with open("annotation_output.json") as fh:
        annotation_output = json.load(fh)

    ##########################################################
    # Generate role table
    table_html_string = "" #table.generate_table(annotation_output)

    with open(os.path.join('../../../data','app_report_templates',
                           'report_table_template.html')) as report_template_file:
        report_template_string = report_template_file.read()

    # Insert html table
    table_report_string = report_template_string.replace('*TABLES*', table_html_string)

    table_html_file="role_table_output.html"
    with open(os.path.join('../../../data','app_report_templates',
                           table_html_file),'w') as table_file:
        table_file.write(table_report_string)

    table.log(message="Role table written to file: "+table_html_file)

if(__name__ == "__main__"):
    main()
