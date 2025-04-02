import tkinter as tk
from VoronoiGenerator import VoronoiGenerator

class VoronoiApp:
    """GUI application for Voronoi diagram visualization"""
    
    # Constants for visualization
    POINT_SIZE = 4
    
    def __init__(self, master):
        """Initialize the application"""
        self.master = master
        self.master.title("Voronoi Diagram Generator")
        
        # Track whether the diagram is locked after computation
        self.is_locked = False
        
        # Create main frame
        self.main_frame = tk.Frame(self.master, relief=tk.SUNKEN, borderwidth=2)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas for drawing
        self.canvas = tk.Canvas(self.main_frame, width=600, height=600, bg="white")
        self.canvas.bind("<Double-1>", self.handle_double_click)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create button frame
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create buttons
        self.generate_button = tk.Button(
            self.button_frame, 
            text="Generate Diagram", 
            width=20, 
            command=self.generate_diagram
        )
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(
            self.button_frame,
            text="Reset Canvas",
            width=20,
            command=self.reset_canvas
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.query_button = tk.Button(
            self.button_frame,
            text="Query Mode",
            width=20,
            command=self.toggle_query_mode
        )
        self.query_button.pack(side=tk.LEFT, padx=5)
        
        # State variables
        self.query_mode = False
        self.voronoi_generator = None
        self.sites = []
    
    def handle_double_click(self, event):
        """Handle double-click events on the canvas"""
        if self.is_locked:
            if self.query_mode:
                self.query_point(event.x, event.y)
            return
            
        # Add a new site point
        self.canvas.create_oval(
            event.x - self.POINT_SIZE,
            event.y - self.POINT_SIZE,
            event.x + self.POINT_SIZE,
            event.y + self.POINT_SIZE,
            fill="black"
        )
        
        # Store the site coordinates
        self.sites.append((event.x, event.y))
    
    def generate_diagram(self):
        """Generate and display the Voronoi diagram"""
        if not self.sites or self.is_locked:
            return
            
        self.is_locked = True
        
        # Create Voronoi generator and process the diagram
        self.voronoi_generator = VoronoiGenerator(self.sites)
        self.voronoi_generator.generate()
        
        # Draw the resulting edges
        edges = self.voronoi_generator.get_edges()
        for edge in edges:
            x1, y1, x2, y2 = edge
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1.5)
    
    def query_point(self, x, y):
        """Find the Voronoi cell containing the query point"""
        if not self.voronoi_generator:
            return
            
        # First, clear any previous query markers
        self.canvas.delete("query")
        
        # Display query point
        self.canvas.create_oval(
            x - self.POINT_SIZE, 
            y - self.POINT_SIZE,
            x + self.POINT_SIZE,
            y + self.POINT_SIZE,
            fill="red",
            tags="query"
        )
        
        # Find the Voronoi cell containing the query point
        nearest_site = self.voronoi_generator.find_cell((x, y))
        
        if nearest_site:
            # Highlight the nearest site and draw a line to it
            self.canvas.create_oval(
                nearest_site.x - self.POINT_SIZE*1.5,
                nearest_site.y - self.POINT_SIZE*1.5,
                nearest_site.x + self.POINT_SIZE*1.5,
                nearest_site.y + self.POINT_SIZE*1.5,
                outline="red",
                width=2,
                tags="query"
            )
            
            self.canvas.create_line(
                x, y, 
                nearest_site.x, nearest_site.y,
                fill="red",
                dash=(4, 2),
                tags="query"
            )
    
    def reset_canvas(self):
        """Clear the canvas and reset the application state"""
        self.canvas.delete(tk.ALL)
        self.sites = []
        self.voronoi_generator = None
        self.is_locked = False
        self.query_mode = False
        self.query_button.config(text="Query Mode")
    
    def toggle_query_mode(self):
        """Toggle between site placement and query modes"""
        if not self.is_locked:
            # Cannot enter query mode if diagram hasn't been generated
            return
            
        self.query_mode = not self.query_mode
        
        if self.query_mode:
            self.query_button.config(text="Exit Query Mode")
            self.canvas.delete("query")  # Clear any existing queries
        else:
            self.query_button.config(text="Query Mode")
            self.canvas.delete("query")

def main():
    """Entry point for the application"""
    root = tk.Tk()
    app = VoronoiApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()