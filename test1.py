import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
clr.AddReference("Microsoft.Web.WebView2.WinForms")

from System.Windows.Forms import Application, Form
from Microsoft.Web.WebView2.WinForms import WebView2
from System import Uri
from System.Drawing import Size

class MyUI(Form):
    def __init__(self):
        self.Text = "NiceGUI-like UI"
        self.Size = Size(800, 600)
        self.web = WebView2()
        self.web.Size = self.ClientSize
        self.Controls.Add(self.web)
        html = """
        <html>
        <body style='font-family:sans-serif;text-align:center;margin-top:100px;'>
          <h1>Hello from IronPython 3!</h1>
          <button onclick="alert('Clicked!')">Click Me</button>
        </body>
        </html>
        """
        self.web.Source = Uri("data:text/html," + Uri.EscapeDataString(html))

Application.Run(MyUI())