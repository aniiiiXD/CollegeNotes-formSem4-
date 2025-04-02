import math
from GeometryTypes import Vertex, CircleEvent, BeachSection, VoronoiEdge, EventQueue

class VoronoiGenerator:
    """Implements Fortune's algorithm for generating Voronoi diagrams"""
    
    def __init__(self, points_list):
        """Initialize with list of point coordinates [(x1, y1), (x2, y2), ...]"""
        self.edges = []  # List of line segments forming the diagram
        self.beach_line = None  # Root of the beach line tree
        
        # Priority queues for events
        self.site_events = EventQueue()
        self.circle_events = EventQueue()
        
        # Set initial bounding box (expanded as needed)
        self.bounds = {
            'min_x': float('inf'),
            'max_x': float('-inf'),
            'min_y': float('inf'),
            'max_y': float('-inf')
        }
        
        # Convert input points to Vertex objects and add to site events queue
        for x, y in points_list:
            site = Vertex(x, y)
            self.site_events.push(site)
            
            # Update bounding box
            self.bounds['min_x'] = min(self.bounds['min_x'], x)
            self.bounds['max_x'] = max(self.bounds['max_x'], x)
            self.bounds['min_y'] = min(self.bounds['min_y'], y)
            self.bounds['max_y'] = max(self.bounds['max_y'], y)
        
        # Add margins to bounding box
        width = self.bounds['max_x'] - self.bounds['min_x']
        height = self.bounds['max_y'] - self.bounds['min_y']
        padding_x = width / 5
        padding_y = height / 5
        
        self.bounds['min_x'] -= padding_x
        self.bounds['max_x'] += padding_x
        self.bounds['min_y'] -= padding_y
        self.bounds['max_y'] += padding_y
    
    def generate(self):
        """Process all events to generate the Voronoi diagram"""
        # Process all site events and circle events in order
        while not self.site_events.is_empty():
            if (not self.circle_events.is_empty() and 
                (hasattr(self.circle_events.peek(), 'x_pos') and 
                 self.circle_events.peek().x_pos <= self.site_events.peek().x)):
                self._handle_circle_event()
            else:
                self._handle_site_event()
        
        # Process any remaining circle events
        while not self.circle_events.is_empty():
            self._handle_circle_event()
            
        # Finish any incomplete edges
        self._complete_edges()
        
    def find_cell(self, query_point):
        """Find the Voronoi cell containing the query point"""
        # For a query point q, find the site whose Voronoi cell contains q
        query = Vertex(query_point[0], query_point[1])
        nearest_site = None
        min_distance = float('inf')
        
        # Brute force approach: find the nearest site to the query point
        current = self.beach_line
        while current:
            dist = query.distance_to(current.site)
            if dist < min_distance:
                min_distance = dist
                nearest_site = current.site
                
            current = current.next_section
            
        return nearest_site
    
    def _handle_site_event(self):
        """Process a site event: add new beach section"""
        new_site = self.site_events.pop()
        self._insert_beach_section(new_site)
    
    def _handle_circle_event(self):
        """Process a circle event: create a vertex and update beach line"""
        circle_event = self.circle_events.pop()
        
        if not circle_event.is_valid:
            return
            
        # Create a vertex at the circle center
        vertex = circle_event.center
        arc = circle_event.beach_arc
        
        # Create a new edge
        new_edge = VoronoiEdge(vertex)
        self.edges.append(new_edge)
        
        # Update beach line structure
        left_arc = arc.prev_section
        right_arc = arc.next_section
        
        if left_arc:
            left_arc.next_section = right_arc
            left_arc.right_edge = new_edge
            
        if right_arc:
            right_arc.prev_section = left_arc
            right_arc.left_edge = new_edge
            
        # Complete edges connected to the disappearing arc
        if arc.left_edge:
            arc.left_edge.complete_edge(vertex)
            
        if arc.right_edge:
            arc.right_edge.complete_edge(vertex)
            
        # Check for new circle events around the updated beach sections
        if left_arc:
            self._check_circle_event(left_arc, vertex.x)  # Using vertex.x instead of new_site.x
            
        if right_arc:
            self._check_circle_event(right_arc, vertex.x)  # Using vertex.x instead of new_site.x
    
    def _insert_beach_section(self, site):
        """Insert a new arc into the beach line for a site event"""
        if self.beach_line is None:
            # First site - create the first beach section
            self.beach_line = BeachSection(site)
            return
            
        # Find the arc above the new site
        arc = self._find_arc_above(site)
        
        if arc.circle_event:
            # Invalidate any circle event involving this arc
            arc.circle_event.is_valid = False
            arc.circle_event = None
            
        # Split the existing arc
        split_point = self._calculate_breakpoint(arc.site, site, site.x)
        
        # Create new edges
        left_edge = VoronoiEdge(split_point)
        right_edge = VoronoiEdge(split_point)
        self.edges.append(left_edge)
        self.edges.append(right_edge)
        
        # Create and link new beach sections
        left_arc = BeachSection(arc.site, arc.prev_section, None)
        middle_arc = BeachSection(site, left_arc, None)
        right_arc = BeachSection(arc.site, middle_arc, arc.next_section)
        
        # Update links
        left_arc.next_section = middle_arc
        middle_arc.next_section = right_arc
        
        if arc.prev_section:
            arc.prev_section.next_section = left_arc
        else:
            self.beach_line = left_arc
            
        if arc.next_section:
            arc.next_section.prev_section = right_arc
            
        # Assign edges
        left_arc.right_edge = left_edge
        middle_arc.left_edge = left_edge
        middle_arc.right_edge = right_edge
        right_arc.left_edge = right_edge
        
        # Check for new circle events
        self._check_circle_event(left_arc, site.x)
        self._check_circle_event(right_arc, site.x)
    
    def _find_arc_above(self, site):
        """Find the arc in the beach line above the given site"""
        current = self.beach_line
        while current:
            is_above, _ = self._is_point_above_arc(site, current)
            if is_above:
                return current
            current = current.next_section
            
        # If no arc found, return the last arc
        return self.beach_line
    
    def _is_point_above_arc(self, point, arc):
        """Check if a point is above an arc in the beach line"""
        if arc.next_section is None:
            return True, None
            
        # Calculate breakpoints
        left_break = self._calculate_breakpoint(arc.site, arc.next_section.site, point.x)
        
        if point.y < left_break.y:
            return True, left_break
        else:
            return False, left_break
    
    def _calculate_breakpoint(self, p1, p2, directrix):
        """Calculate the breakpoint between two sites at a given directrix position"""
        # Handle special cases
        if p1.x == p2.x:
            y = (p1.y + p2.y) / 2
            return Vertex((p1.x**2 + (p1.y-y)**2 - directrix**2) / (2*p1.x - 2*directrix), y)
            
        if p1.x == directrix:
            return Vertex(p1.x, p1.y)
            
        if p2.x == directrix:
            return Vertex(p2.x, p2.y)
            
        # General case - quadratic formula
        z1 = 2 * (p1.x - directrix)
        z2 = 2 * (p2.x - directrix)
        
        a = 1/z1 - 1/z2
        b = -2*(p1.y/z1 - p2.y/z2)
        c = (p1.y**2 + p1.x**2 - directrix**2)/z1 - (p2.y**2 + p2.x**2 - directrix**2)/z2
        
        y = (-b - math.sqrt(b**2 - 4*a*c)) / (2*a)
        
        # Calculate corresponding x
        p = p1  # Use p1 as reference point
        x = (p.x**2 + (p.y-y)**2 - directrix**2) / (2*p.x - 2*directrix)
        
        return Vertex(x, y)
    
    def _check_circle_event(self, arc, x_pos):
        """Check for a potential circle event involving the given arc"""
        # Remove any existing circle event
        if arc.circle_event and arc.circle_event.is_valid:
            arc.circle_event.is_valid = False
        arc.circle_event = None
        
        if not arc.prev_section or not arc.next_section:
            return
            
        # Check if the arcs form a valid circle event
        is_valid, x, center = self._compute_circle(
            arc.prev_section.site, 
            arc.site, 
            arc.next_section.site
        )
        
        if is_valid and x > x_pos:
            # Create and schedule the circle event
            circle_event = CircleEvent(x, center, arc)
            arc.circle_event = circle_event
            self.circle_events.push(circle_event)
    
    def _compute_circle(self, a, b, c):
        """Compute circle passing through three points"""
        # Check if these points form a counterclockwise turn
        if ((b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)) > 0:
            return False, None, None
            
        # Compute circumcenter using matrix method
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = A*(a.x + b.x) + B*(a.y + b.y)
        F = C*(a.x + c.x) + D*(a.y + c.y)
        G = 2*(A*(c.y - b.y) - B*(c.x - b.x))
        
        if G == 0:  # Points are collinear
            return False, None, None
        
        # Center of the circle
        center_x = (D*E - B*F) / G
        center_y = (A*F - C*E) / G
        center = Vertex(center_x, center_y)
        
        # Radius
        radius = math.sqrt((a.x - center_x)**2 + (a.y - center_y)**2)
        
        # Right end of the circle on the x-axis
        x = center_x + radius
        
        return True, x, center
    
    def _complete_edges(self):
        """Complete all unfinished edges of the diagram"""
        # Use a point far outside the bounding box to complete the edges
        far_point_x = self.bounds['max_x'] + 2*(self.bounds['max_x'] - self.bounds['min_x'])
        
        current = self.beach_line
        while current and current.next_section:
            if current.right_edge and not current.right_edge.is_complete:
                # Calculate the end point at infinity
                end_point = self._calculate_breakpoint(
                    current.site,
                    current.next_section.site,
                    far_point_x
                )
                current.right_edge.complete_edge(end_point)
                
            current = current.next_section
    
    def get_edges(self):
        """Return edges as list of line segments [(x1,y1,x2,y2), ...]"""
        result = []
        for edge in self.edges:
            if edge.is_complete:
                result.append((
                    edge.start_point.x, 
                    edge.start_point.y, 
                    edge.end_point.x, 
                    edge.end_point.y
                ))
        return result