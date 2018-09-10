import wx
import os
import numpy as np
from scipy import special, optimize
import matplotlib.pyplot as plt
from wxmplot import ImagePanel

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200,100))        
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        filemenu= wx.Menu()

         # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")            
        filemenu.AppendSeparator()
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program") 
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit") 
     
        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)     
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)

        # operational buttons
        self.sizerHbar = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = []
        bb = wx.Button(self, -1, "Draw Bessel")
        bb.Bind(wx.EVT_BUTTON, self.DisplayBessel)
        self.buttons.append(bb)        
        self.sizerHbar.Add(self.buttons[0], 1, wx.EXPAND)
        
        # image import
        self.MaxImageSize = 460
        self.Image = wx.StaticBitmap(self, bitmap=wx.Bitmap(self.MaxImageSize, self.MaxImageSize))
        self.ImageFile = 'plot.png'

        # calculate bessel
        self.CalculateBessel(3, self.ImageFile)

        # calculate intensity
        self.CalculateIntensity('intensity.png')
        # calculate contour
        self.CalculateContour('contour.png')       

        # Use some sizers to see layout options
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(bb, 0, wx.CENTER | wx.ALL,10)

        # adding stretchable space before and after centers the image.
        box.Add((1,1),1)
        box.Add(self.Image, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        box.Add((1,1),1)
        box.Add(self.sizerHbar, 0, wx.EXPAND)

        # calculate gradient
        self.panel = ImagePanel(self, dpi=96)
        self.CalculateGradient('gradient.png', self.panel)
        
        #Layout sizers       
        box.Add(self.panel,0,wx.EXPAND)
        self.SetSizerAndFit(box)        

        self.Show()

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)

    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "A small text editor", "About Sample Editor", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.
    
    def OnOpen(self,e):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.png", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            self.ImageFile = os.path.join(self.dirname, self.filename)
            f.close()
            self.DisplayBessel()
        dlg.Destroy()

    def DisplayBessel(self, event=None):
        #load Image
        Img = wx.Image(self.ImageFile, wx.BITMAP_TYPE_PNG)
        # scale the image, preserving the aspect ratio
        W = Img.GetWidth()
        H = Img.GetHeight()
        if W > H:
            NewW = self.MaxImageSize
            NewH = self.MaxImageSize * H / W
        else:
            NewH = self.MaxImageSize
            NewW = self.MaxImageSize * W / H
        Img = Img.Scale(NewW,NewH)
 
        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        self.Image.SetBitmap(wx.Bitmap(Img))
        self.Refresh()

    def CalculateBessel(self, order, output):
        # Compute maximum
        f = lambda x: -special.jv(order, x)
        sol = optimize.minimize(f, 1.0)

        # Plot
        x = np.linspace(0, 10, 5000)
        plt.plot(x, special.jv(order, x), '-', sol.x, -sol.fun, 'o')

        # Produce output
        plt.savefig(output, dpi=96)

    def CalculateIntensity(self, output):
        y, x = np.mgrid[-5:5:101j, -4:6:101j]
        dat = np.sin(x*x/3.0 + y*y)/(1 + (x+y)*(x+y))

        x0 = x[0,:]
        y0 = y[:,0]
        plt.plot(y, x, dat)

         # Produce output
        plt.savefig(output, dpi=96)

    def CalculateContour(self, output):
        y, x = np.mgrid[-5:5:101j, -4:6:101j]
        dat = np.sin(x*x/3.0 + y*y)/(1 + (x+y)*(x+y))

        x0 = x[0,:]
        y0 = y[:,0]

        plt.plot( x, y, dat)

         # Produce output
        plt.savefig(output, dpi=96)
   
    def CalculateGradient(self, output, panel):
        def gauss2d(x, y, x0, y0, sx, sy):
            return np.outer( np.exp( -(((y-y0)/float(sy))**2)/2), np.exp( -(((x-x0)/float(sx))**2)/2) )
        
        ny = 350
        nx = 350
        x = np.arange(nx)
        y = np.arange(ny)
        ox =  x / 100.0
        oy = -1 + y / 200.0
        red  = 0.02 * np.random.random(size=nx*ny).reshape(ny, nx)
        red =  red + (6.0*gauss2d(x, y, 90,   76,  5,  6) +
                    3.0*gauss2d(x, y, 165, 190,  70,  33) +
                    2.0*gauss2d(x, y, 180, 100,  12,  6))
        green  = 0.3 * np.random.random(size=nx*ny).reshape(ny, nx)
        green = green  + (5.0*gauss2d(x, y, 173,  98,  4,  9) +
                        3.2*gauss2d(x, y, 270, 230, 78, 63))

        blue = 0.1 * np.random.random(size=nx*ny).reshape(ny, nx)
        blue = blue + (2.9*gauss2d(x, y, 240, 265,  78,  23) +
                    3.5*gauss2d(x, y, 185,  95,  22, 11) +
                    7.0*gauss2d(x, y, 220,  310,  40,  133))

        dat = np.array([red, green, blue]).swapaxes(2, 0)

        plt.plot(  y, x, blue)
        panel.display(dat, x=ox, y=oy,
                  subtitles={'red':'Red Image', 'green': 'Green Blob', 'blue': 'other'})

         # Produce output
        plt.savefig(output, dpi=96)

app = wx.App(False)
frame = MainWindow(None, "Sample Display")
app.MainLoop()
