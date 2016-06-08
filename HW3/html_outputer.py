
class HtmlOutputer(object):
    def __init__(self):
        self.data = []

    def collect_data(self, data):
        if data is None:
            return
        self.data.append(data)

    def output_html(self):
        data_set = set()
        data_set_1 = set()
        count = 0
        fout = open('output.html', 'w')

        fout.write("<html>")
        fout.write("<body>")
        fout.write("<table>")
        fout.write("<tr>")
        fout.write("<td> Number </td>")
        fout.write("<td> Email </td>")
        fout.write("</tr>")

        for item in self.data:
            data_set = set(item)

            for item in data_set:
                data_set_1.add(item)

        for email in data_set_1:
            count = count+1
            fout.write("<tr>")
            fout.write("<td> %d </td>"% count)
            fout.write("<td> %s </td>"% email)
            fout.write("</tr>")

        fout.write("</table>")
        fout.write("</body>")
        fout.write("</html>")