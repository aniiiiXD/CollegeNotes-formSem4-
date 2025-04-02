import math
import heapq
import random
import tkinter as tk
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set

class EventType(Enum):
    SITE = 0
    CIRCLE = 1

@dataclass
class Point:
    x: float
    y: float
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9
    
    def __hash__(self):
        return hash((round(self.x, 9), round(self.y, 9)))
    
    def distance_to(self, other):
        """Calculate Euclidean distance to another point"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class Event:
    point: Point
    type: EventType
    arc: Optional['Arc'] = None
    valid: bool = True
    
    def __lt__(self, other):
        # For priority queue ordering
        return self.point.x < other.point.x

class Segment:
    def __init__(self, start: Point):
        self.start = start
        self.end = None
        self.done = False
        # Store the two sites that define this edge
        self.site1 = None
        self.site2 = None
    
    def finish(self, end: Point):
        if not self.done:
            self.end = end
            self.done = True
    
    def get_line_segment(self) -> Tuple[float, float, float, float]:
        if self.done:
            return self.start.x, self.start.y, self.end.x, self.end.y
        return None

class Arc:
    def __init__(self, site: Point, prev: Optional['Arc'] = None, next: Optional['Arc'] = None):
        self.site = site
        self.prev = prev
        self.next = next
        self.event = None  # Circle event
        self.left_edge = None  # Segment connecting to left neighbor
        self.right_edge = None  # Segment connecting to right neighbor

class VoronoiCell:
    def __init__(self, site: Point):
        self.site = site
        self.vertices = []  # Ordered list of vertices defining the cell
        self.edges = []     # List of edges forming the boundary
    
    def add_vertex(self, vertex: Point):
        self.vertices.append(vertex)
    
    def add_edge(self, edge: Segment):
        self.edges.append(edge)
    
    def contains_point(self, point: Point) -> bool:
        """Check if a point is inside this Voronoi cell"""
        # The basic principle: a point is in this cell if this site
        # is the closest site to the query point
        return True  # This will be implemented by the nearest site check in FortuneVoronoi

class FortuneVoronoi:
    def __init__(self, points: List[Tuple[float, float]]):
        self.site_points = [Point(x, y) for x, y in points]
        self.output_edges = []
        self.beach_line = None  # Root of the beach line binary tree
        self.cells = {}  # Maps site points to VoronoiCell objects
        
        # Initialize cell for each site
        for site in self.site_points:
            self.cells[site] = VoronoiCell(site)
        
        # Compute bounding box with margin
        self._compute_bounding_box()
        
        # Event queue (priority queue)
        self.events = []
        
        # Populate initial site events
        for site in self.site_points:
            heapq.heappush(self.events, Event(site, EventType.SITE))
    
    def _compute_bounding_box(self):
        """Compute bounding box with margins for the diagram"""
        if not self.site_points:
            self.x_min, self.y_min = -50.0, -50.0
            self.x_max, self.y_max = 550.0, 550.0
            return
            
        self.x_min = min(point.x for point in self.site_points)
        self.y_min = min(point.y for point in self.site_points)
        self.x_max = max(point.x for point in self.site_points)
        self.y_max = max(point.y for point in self.site_points)
        
        # Add margins (20% of the range)
        dx = (self.x_max - self.x_min) * 0.2
        dy = (self.y_max - self.y_min) * 0.2
        self.x_min -= dx
        self.y_min -= dy
        self.x_max += dx
        self.y_max += dy
    
    def process(self):
        """Process all events to construct the Voronoi diagram"""
        while self.events:
            event = heapq.heappop(self.events)
            
            # Skip invalid circle events
            if not event.valid:
                continue
                
            # Current sweep line position
            sweep_x = event.point.x
            
            if event.type == EventType.SITE:
                self._handle_site_event(event)
            else:
                self._handle_circle_event(event)
        
        # Finish edges that haven't been completed
        self._complete_edges()
        
        # Construct Voronoi cells from edges
        self._construct_cells()
        
        return self.get_edges()
    
    def _handle_site_event(self, event: Event):
        """Handle a site event: a new point to be added to the diagram"""
        site = event.point
        
        # First point case - just create the beach line
        if self.beach_line is None:
            self.beach_line = Arc(site)
            return
        
        # Find the arc above the new site
        arc_above = self._find_arc_above(site)
        if arc_above is None:
            # Should never happen if sites are distinct
            return
            
        # Check if there was a circle event planned for this arc
        if arc_above.event:
            arc_above.event.valid = False
            arc_above.event = None
        
        # Split the arc
        self._split_arc(arc_above, site)
        
        # Check for new circle events
        self._check_circle_events(site.x)
    
    def _handle_circle_event(self, event: Event):
        """Handle a circle event: arcs converging and creating a Voronoi vertex"""
        if not event.valid:
            return
            
        # Center of the circle (Voronoi vertex)
        center = event.point
        
        # Arc that will disappear
        arc = event.arc
        
        # Get the arcs to the left and right
        left_arc = arc.prev
        right_arc = arc.next
        
        # Create a new edge at the vertex
        new_edge = Segment(center)
        self.output_edges.append(new_edge)
        
        # Set the sites that define this edge
        new_edge.site1 = left_arc.site
        new_edge.site2 = right_arc.site
        
        # Connect this vertex to edges
        if arc.left_edge:
            arc.left_edge.finish(center)
            # Update cells with this vertex
            if arc.left_edge.site1 and arc.left_edge.site2:
                self.cells[arc.left_edge.site1].add_vertex(center)
                self.cells[arc.left_edge.site2].add_vertex(center)
        
        if arc.right_edge:
            arc.right_edge.finish(center)
            # Update cells with this vertex
            if arc.right_edge.site1 and arc.right_edge.site2:
                self.cells[arc.right_edge.site1].add_vertex(center)
                self.cells[arc.right_edge.site2].add_vertex(center)
            
        # Remove the disappearing arc
        if left_arc:
            left_arc.next = right_arc
            # Connect left and right arcs with the new edge
            left_arc.right_edge = new_edge
        
        if right_arc:
            right_arc.prev = left_arc
            right_arc.left_edge = new_edge
            
        # Check for new circle events
        self._check_circle_events(center.x)
    
    def _find_arc_above(self, site: Point) -> Optional[Arc]:
        """Find the arc directly above a new site in the beach line"""
        if not self.beach_line:
            return None
            
        # Start at the leftmost arc
        current = self.beach_line
        while current.prev:
            current = current.prev
            
        # Traverse the beach line to find the arc above the site
        while current:
            # Calculate the breakpoint between current arc and its right neighbor
            if current.next:
                breakpoint = self._compute_breakpoint(current.site, current.next.site, site.x)
                if site.y <= breakpoint:
                    return current
            else:
                # Rightmost arc always contains the point (no right breakpoint)
                return current
                
            current = current.next
        
        return None
    
    def _compute_breakpoint(self, p1: Point, p2: Point, directrix: float) -> float:
        """Compute y-coordinate of the breakpoint of two parabolas at given directrix (x) position"""
        # Handle special cases
        if abs(p1.y - p2.y) < 1e-9:
            return (p1.y + p2.y) / 2
            
        if abs(p1.x - p2.x) < 1e-9:
            return p1.y
            
        # Calculate intersection of two parabolas
        # Each parabola is defined by the distance to its focus (site) and the directrix
        a1 = 1.0 / (2.0 * (p1.y - directrix))
        b1 = -2.0 * p1.x * a1
        c1 = a1 * p1.x * p1.x + (p1.y * p1.y - directrix * directrix) / (2.0 * (p1.y - directrix))
        
        a2 = 1.0 / (2.0 * (p2.y - directrix))
        b2 = -2.0 * p2.x * a2
        c2 = a2 * p2.x * p2.x + (p2.y * p2.y - directrix * directrix) / (2.0 * (p2.y - directrix))
        
        # Solve for the intersection
        if abs(a1 - a2) < 1e-9:
            # Parabolas have same curvature, solve linear equation
            x = (c2 - c1) / (b1 - b2)
        else:
            # Quadratic formula
            A = a1 - a2
            B = b1 - b2
            C = c1 - c2
            discriminant = B * B - 4 * A * C
            
            if discriminant < 0:
                # No intersection (shouldn't happen)
                return (p1.y + p2.y) / 2
                
            x = (-B - math.sqrt(discriminant)) / (2 * A)
            
        # Calculate y using the equation of the first parabola
        y = a1 * x * x + b1 * x + c1
        return y
    
    def _split_arc(self, arc: Arc, site: Point):
        """Split an arc and insert the new site"""
        # Create new arcs
        left_arc = Arc(arc.site)
        middle_arc = Arc(site)
        right_arc = Arc(arc.site)
        
        # Set up connections
        if arc.prev:
            arc.prev.next = left_arc
            left_arc.prev = arc.prev
        else:
            # Update beach line root if needed
            self.beach_line = left_arc
            
        left_arc.next = middle_arc
        middle_arc.prev = left_arc
        middle_arc.next = right_arc
        right_arc.prev = middle_arc
        right_arc.next = arc.next
        
        if arc.next:
            arc.next.prev = right_arc
        
        # Create edges
        breakpoint = self._compute_intersection_point(left_arc.site, middle_arc.site, site.x)
        left_edge = Segment(breakpoint)
        left_edge.site1 = left_arc.site
        left_edge.site2 = middle_arc.site
        self.output_edges.append(left_edge)
        
        breakpoint = self._compute_intersection_point(middle_arc.site, right_arc.site, site.x)
        right_edge = Segment(breakpoint)
        right_edge.site1 = middle_arc.site
        right_edge.site2 = right_arc.site
        self.output_edges.append(right_edge)
        
        # Set edge references
        left_arc.right_edge = left_edge
        middle_arc.left_edge = left_edge
        middle_arc.right_edge = right_edge
        right_arc.left_edge = right_edge
        
        # Transfer existing edge references
        if arc.left_edge:
            left_arc.left_edge = arc.left_edge
        if arc.right_edge:
            right_arc.right_edge = arc.right_edge
    
    def _compute_intersection_point(self, p1: Point, p2: Point, directrix: float) -> Point:
        """Compute the intersection point of two arcs at the given directrix position"""
        y = self._compute_breakpoint(p1, p2, directrix)
        
        # Calculate x by using the parabola equation
        h = p1.x
        k = p1.y
        p = directrix
        
        if abs(k - p) < 1e-9:
            # Handle edge case where focus is on directrix
            x = h
        else:
            # Calculate x using the parabola equation
            x = (y - k) * (y - k) / (2 * (k - p)) + h
            
        return Point(x, y)
    
    def _check_circle_events(self, sweep_x: float):
        """Check for new circle events in the beach line"""
        # Start at the leftmost arc
        arc = self.beach_line
        while arc and arc.prev:
            arc = arc.prev
            
        # Process each arc
        while arc:
            self._check_circle_event_for_arc(arc, sweep_x)
            arc = arc.next
    
    def _check_circle_event_for_arc(self, arc: Arc, sweep_x: float):
        """Check if a circle event should be created for an arc"""
        # We need three consecutive arcs to form a circle event
        if not arc or not arc.prev or not arc.next:
            return
            
        # Get the three consecutive sites
        a = arc.prev.site
        b = arc.site
        c = arc.next.site
        
        # Check if the three points make a circle
        success, center, radius = self._compute_circle(a, b, c)
        if not success:
            return
            
        # Event point is the rightmost point of the circle (center.x + radius)
        event_x = center.x + radius
        
        # Only add the event if it's still ahead of the sweep line
        if event_x > sweep_x:
            # Create a new circle event
            event_point = Point(event_x, center.y)
            circle_event = Event(event_point, EventType.CIRCLE, arc=arc)
            
            # Schedule the event
            heapq.heappush(self.events, circle_event)
            
            # Set the reference to the event in the arc
            arc.event = circle_event
    
    def _compute_circle(self, a: Point, b: Point, c: Point) -> Tuple[bool, Optional[Point], float]:
        """Compute the center and radius of the circle through three points"""
        # Check if the points form a counterclockwise turn
        # If it's clockwise, a circle event will occur
        dx1 = b.x - a.x
        dy1 = b.y - a.y
        dx2 = c.x - b.x
        dy2 = c.y - b.y
        
        # Cross product to check orientation
        cross = dx1 * dy2 - dy1 * dx2
        
        # We're only interested in clockwise turns (negative cross product)
        if cross >= 0:
            return False, None, 0
            
        # Compute the circumcenter using the perpendicular bisector method
        D = 2 * (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y))
        
        if abs(D) < 1e-9:
            # Points are collinear or nearly so
            return False, None, 0
            
        ux = ((a.x*a.x + a.y*a.y) * (b.y - c.y) + 
              (b.x*b.x + b.y*b.y) * (c.y - a.y) + 
              (c.x*c.x + c.y*c.y) * (a.y - b.y)) / D
              
        uy = ((a.x*a.x + a.y*a.y) * (c.x - b.x) + 
              (b.x*b.x + b.y*b.y) * (a.x - c.x) + 
              (c.x*c.x + c.y*c.y) * (b.x - a.x)) / D
              
        center = Point(ux, uy)
        radius = math.sqrt((center.x - a.x)**2 + (center.y - a.y)**2)
        
        return True, center, radius
    
    def _complete_edges(self):
        """Complete any unfinished edges by extending them to the bounding box"""
        # Extend unfinished edges to the bounding box
        for edge in self.output_edges:
            if not edge.done:
                # If we have a start point but no end point, extend to bounding box
                if edge.start:
                    # For simplicity, extend to a point far outside the bounding box
                    far_point = self._compute_edge_end(edge)
                    edge.finish(far_point)
                    
                    # Update cells with this vertex
                    if edge.site1 and edge.site2:
                        self.cells[edge.site1].add_vertex(far_point)
                        self.cells[edge.site2].add_vertex(far_point)
    
    def _compute_edge_end(self, edge: Segment) -> Point:
        """Compute an end point for an unfinished edge by intersecting with the bounding box"""
        # Find the direction of the perpendicular bisector
        if edge.site1 and edge.site2:
            # Direction perpendicular to the line connecting the two sites
            dx = edge.site2.y - edge.site1.y  # Perpendicular direction
            dy = edge.site1.x - edge.site2.x
            
            # Normalize
            length = math.sqrt(dx*dx + dy*dy)
            if length < 1e-9:
                # Default direction if sites are too close
                return Point(self.x_max + 100, edge.start.y)
                
            dx /= length
            dy /= length
            
            # Scale to ensure it reaches the bounding box
            scale = 2 * max(self.x_max - self.x_min, self.y_max - self.y_min)
            
            # Try both directions from the start point
            end1 = Point(edge.start.x + dx * scale, edge.start.y + dy * scale)
            end2 = Point(edge.start.x - dx * scale, edge.start.y - dy * scale)
            
            # Choose the end point that's further from the midpoint of the two sites
            midpoint = Point((edge.site1.x + edge.site2.x) / 2, (edge.site1.y + edge.site2.y) / 2)
            
            # Check which direction is going away from the midpoint
            dist1 = (end1.x - midpoint.x) * dx + (end1.y - midpoint.y) * dy
            dist2 = (end2.x - midpoint.x) * dx + (end2.y - midpoint.y) * dy
            
            if dist1 > dist2:
                return end1
            else:
                return end2
        
        # Fallback if we don't have site information
        return Point(self.x_max + 100, edge.start.y)
    
    def _construct_cells(self):
        """Construct Voronoi cells from the computed edges"""
        # Add edges to the appropriate cells
        for edge in self.output_edges:
            if edge.site1 and edge.site2 and edge.done:
                self.cells[edge.site1].add_edge(edge)
                self.cells[edge.site2].add_edge(edge)
    
    def get_edges(self) -> List[Tuple[float, float, float, float]]:
        """Get the list of edges as line segments"""
        result = []
        for edge in self.output_edges:
            if edge.done:
                result.append((edge.start.x, edge.start.y, edge.end.x, edge.end.y))
        return result
    
    def find_nearest_site(self, query_point: Point) -> Point:
        """Find the site whose Voronoi cell contains the query point"""
        nearest_site = None
        min_distance = float('inf')
        
        # For a point to be in a Voronoi cell, its generator (site) must be 
        # the closest site to the query point
        for site in self.site_points:
            distance = query_point.distance_to(site)
            if distance < min_distance:
                min_distance = distance
                nearest_site = site
                
        return nearest_site
    
    def query_point(self, x: float, y: float) -> Point:
        """Find which Voronoi cell contains the query point"""
        query = Point(x, y)
        return self.find_nearest_site(query)


# Demo app using Tkinter
class VoronoiApp:
    def __init__(self, root, width=600, height=600):
        self.root = root
        self.root.title("Voronoi Diagram with Query")
        self.width = width
        self.height = height
        self.POINT_RADIUS = 3
        self.LOCKED = False
        self.points = []
        self.voronoi = None
        self.query_marker = None
        
        # Main frame
        self.frame = tk.Frame(root, relief=tk.RAISED, borderwidth=1)
        self.frame.pack(fill=tk.BOTH, expand=1)
        
        # Canvas
        self.canvas = tk.Canvas(self.frame, width=width, height=height, bg='white')
        self.canvas.bind('<Double-1>', self.on_double_click)
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.pack()
        
        # Instructions label
        self.instructions = tk.Label(
            root, 
            text="Double-click to add points. Click to query a location after calculating."
        )
        self.instructions.pack()
        
        # Status label
        self.status = tk.Label(root, text="")
        self.status.pack()
        
        # Buttons
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack()
        
        self.calc_btn = tk.Button(self.btn_frame, text='Calculate Voronoi Diagram', width=25, command=self.calculate)
        self.calc_btn.pack(side=tk.LEFT)
        
        self.clear_btn = tk.Button(self.btn_frame, text='Clear', width=25, command=self.clear)
        self.clear_btn.pack(side=tk.LEFT)
        
        # Random points button
        self.random_btn = tk.Button(self.btn_frame, text='Generate Random Points', width=25, command=self.generate_random)
        self.random_btn.pack(side=tk.LEFT)
    
    def on_double_click(self, event):
        if not self.LOCKED:
            self.canvas.create_oval(
                event.x - self.POINT_RADIUS, 
                event.y - self.POINT_RADIUS, 
                event.x + self.POINT_RADIUS, 
                event.y + self.POINT_RADIUS, 
                fill="black"
            )
            self.points.append((event.x, event.y))
            self.status.config(text=f"Added point at ({event.x}, {event.y}). Total points: {len(self.points)}")
    
    def on_click(self, event):
        if self.LOCKED and self.voronoi:
            # Query which cell contains this point
            nearest_site = self.voronoi.query_point(event.x, event.y)
            
            # Clear previous query marker
            if self.query_marker:
                self.canvas.delete(self.query_marker)
            
            # Draw a cross at the query point
            self.query_marker = self.canvas.create_line(
                event.x - 5, event.y - 5, event.x + 5, event.y + 5, 
                fill="red", width=2
            )
            self.canvas.create_line(
                event.x - 5, event.y + 5, event.x + 5, event.y - 5, 
                fill="red", width=2
            )
            
            # Highlight the Voronoi cell
            self.highlight_cell(nearest_site)
            
            self.status.config(text=f"Query point ({event.x}, {event.y}) belongs to cell of site ({nearest_site.x:.1f}, {nearest_site.y:.1f})")
    
    def highlight_cell(self, site):
        # Redraw all Voronoi edges
        self.redraw_voronoi()
        
        # Highlight the specific site
        self.canvas.create_oval(
            site.x - self.POINT_RADIUS - 3, 
            site.y - self.POINT_RADIUS - 3, 
            site.x + self.POINT_RADIUS + 3, 
            site.y + self.POINT_RADIUS + 3, 
            outline="red", width=2
        )
        
        # Highlight edges belonging to this site's cell
        if site in self.voronoi.cells:
            for edge in self.voronoi.cells[site].edges:
                if edge.done:
                    self.canvas.create_line(
                        edge.start.x, edge.start.y, edge.end.x, edge.end.y, 
                        fill="red", width=2
                    )
    
    def calculate(self):
        if not self.LOCKED and self.points and len(self.points) >= 3:
            self.LOCKED = True
            
            # Calculate Voronoi diagram
            self.voronoi = FortuneVoronoi(self.points)
            edges = self.voronoi.process()
            
            # Draw the edges
            for edge in edges:
                self.canvas.create_line(edge[0], edge[1], edge[2], edge[3], fill='blue')
            
            self.status.config(text="Voronoi diagram calculated. Click anywhere to query.")
        elif len(self.points) < 3:
            self.status.config(text="Please add at least 3 points for a meaningful Voronoi diagram.")
    
    def redraw_voronoi(self):
        # Clear all but the site points
        self.canvas.delete("all")
        
        # Redraw site points
        for x, y in self.points:
            self.canvas.create_oval(
                x - self.POINT_RADIUS, 
                y - self.POINT_RADIUS, 
                x + self.POINT_RADIUS, 
                y + self.POINT_RADIUS, 
                fill="black"
            )
        
        # Redraw Voronoi edges
        if self.voronoi:
            edges = self.voronoi.get_edges()
            for edge in edges:
                self.canvas.create_line(edge[0], edge[1], edge[2], edge[3], fill='blue')
    
    def clear(self):
        self.LOCKED = False
        self.canvas.delete(tk.ALL)
        self.points = []
        self.voronoi = None
        self.query_marker = None
        self.status.config(text="Cleared. Double-click to add points.")
    
    def generate_random(self):
        if not self.LOCKED:
            self.clear()
            num_points = 20
            margin = 50
            
            for _ in range(num_points):
                x = random.randint(margin, self.width - margin)
                y = random.randint(margin, self.height - margin)
                self.canvas.create_oval(
                    x - self.POINT_RADIUS, 
                    y - self.POINT_RADIUS, 
                    x + self.POINT_RADIUS, 
                    y + self.POINT_RADIUS, 
                    fill="black"
                )
                self.points.append((x, y))
            
            self.status.config(text=f"Generated {num_points} random points.")


# Main function
def main():
    import tkinter as tk
    root = tk.Tk()
    app = VoronoiApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()