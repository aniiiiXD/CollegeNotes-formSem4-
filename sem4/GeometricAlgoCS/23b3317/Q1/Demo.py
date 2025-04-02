import tkinter as tk
from tkinter import messagebox
from Voronoi import Voronoi


class MainWindow:
    RADIUS=3
    LOCK_FLAG=False    
    
    def __init__(self,master):
        print("Starting Voronoi diagram generator...")
        self.master=master
        self.master.title("Voronoi")        
        self.vp=None
        self.points=[]
        #print("initializing window components")
        self.frmMain=tk.Frame(self.master,relief=tk.RAISED,borderwidth=1)
        self.frmMain.pack(fill=tk.BOTH,expand=1)
        self.w=tk.Canvas(self.frmMain,width=500,height=500)
        self.w.config(background='white')
        self.w.bind('<Double-1>',self.onDoubleClick)
        self.w.bind('<Button-3>',self.onRightClick)
        self.w.pack()       
        #print("adding buttons")
        self.frmButton=tk.Frame(self.master)
        self.frmButton.pack()        
        self.btnCalculate=tk.Button(self.frmButton,text='Calculate',width=25,command=self.onClickCalculate)
        self.btnCalculate.pack(side=tk.LEFT)        
        self.btnClear=tk.Button(self.frmButton,text='Clear',width=25,command=self.onClickClear)
        self.btnClear.pack(side=tk.LEFT)
        
        
        
        
    def onClickCalculate(self):
        print("Calculating Voronoi diagram...")
        
        if not self.LOCK_FLAG:
            self.LOCK_FLAG=True        
            pObj=self.w.find_all()
            #print(f"Found {len(pObj)} points")
            self.points=[]
            
            for p in pObj:
                coord=self.w.coords(p)
                #print(f"Point coordinates: {coord}")
                self.points.append((coord[0]+self.RADIUS,coord[1]+self.RADIUS))
            print(f"Total points to process: {len(self.points)}")
            self.vp=Voronoi(self.points)
            #print("Processing points...")
            self.vp.process()
            lines=self.vp.get_output()
            print(f"Generated {len(lines)} Voronoi edges")
            self.drawLinesOnCanvas(lines)            
            #print("Diagram complete!")

    
    def onClickClear(self):
        print("Clearing canvas...")
        self.LOCK_FLAG=False
        self.vp=None
        self.points=[]
        self.w.delete(tk.ALL)
        #print("Canvas cleared!")

    
    def onDoubleClick(self,event):
        if not self.LOCK_FLAG:
            #print(f"Adding point at ({event.x}, {event.y})")
            self.w.create_oval(event.x-self.RADIUS,event.y-self.RADIUS,event.x+self.RADIUS,event.y+self.RADIUS,fill="black")

    
    def onRightClick(self,event):
        if self.LOCK_FLAG and self.vp:
            #print(f"Query point: ({event.x}, {event.y})")
            query_point=(event.x,event.y)
            closest_site=self.vp.find_cell(query_point)            
            print(f"Found closest site: {closest_site}")
            self.w.create_oval(event.x-self.RADIUS,event.y-self.RADIUS,event.x+self.RADIUS,event.y+self.RADIUS,fill="red",outline="red")            
            self.w.create_oval(closest_site[0]-2*self.RADIUS,closest_site[1]-2*self.RADIUS,closest_site[0]+2*self.RADIUS,closest_site[1]+2*self.RADIUS,outline="red",width=2)            
            self.w.create_line(event.x,event.y,closest_site[0],closest_site[1],fill="red",dash=(4,4))            
            
            distance=((event.x-closest_site[0])**2+(event.y-closest_site[1])**2)**0.5
            #print(f"Distance to closest site: {distance:.2f}")
            messagebox.showinfo("Query Result",f"Point ({event.x}, {event.y}) belongs to the Voronoi cell of site ({closest_site[0]:.1f}, {closest_site[1]:.1f})\nDistance: {distance:.2f}")


    def drawLinesOnCanvas(self,lines):
        #print("Drawing Voronoi edges...")
        for l in lines:
            #print(f"Drawing line: {l}")
            self.w.create_line(l[0],l[1],l[2],l[3],fill='blue')
        
        

def main():
    print("=== Voronoi Diagram Generator ===")
    root=tk.Tk()
    app=MainWindow(root)
    root.mainloop()
    
    
if __name__=='__main__':main()