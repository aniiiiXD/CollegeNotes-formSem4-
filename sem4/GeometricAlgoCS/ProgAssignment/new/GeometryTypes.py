import itertools
import heapq
import math

class Vertex:
    """Represents a 2D point with x and y coordinates"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def distance_to(self, other):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        
    def __repr__(self):
        return f"Vertex({self.x}, {self.y})"

class CircleEvent:
    """Represents a circle event in Fortune's algorithm"""
    def __init__(self, x_pos, center, beach_arc):
        self.x_pos = x_pos
        self.center = center
        self.beach_arc = beach_arc
        self.is_valid = True

class BeachSection:
    """Represents a section of the beach line"""
    def __init__(self, site, prev_section=None, next_section=None):
        self.site = site
        self.prev_section = prev_section
        self.next_section = next_section
        self.circle_event = None
        self.left_edge = None
        self.right_edge = None

class VoronoiEdge:
    """Represents an edge in the Voronoi diagram"""
    def __init__(self, start_point):
        self.start_point = start_point
        self.end_point = None
        self.is_complete = False
        
    def complete_edge(self, end_point):
        """Mark an edge as complete with the given endpoint"""
        if self.is_complete:
            return
        self.end_point = end_point
        self.is_complete = True
        
    def __repr__(self):
        return f"Edge: {self.start_point} -> {self.end_point or 'incomplete'}"

class EventQueue:
    """Priority queue for site and circle events, prioritized by x-coordinate"""
    def __init__(self):
        self._queue = []
        self._entry_map = {}
        self._counter = itertools.count()
    
    def push(self, item):
        """Add a new item to the priority queue"""
        # Avoid duplicates
        if item in self._entry_map:
            return
            
        # Use x-coordinate as primary key (min-heap)
        count = next(self._counter)
        if hasattr(item, 'x_pos'):
            priority = item.x_pos  # For circle events
        else:
            priority = item.x      # For site events
            
        entry = [priority, count, item]
        self._entry_map[item] = entry
        heapq.heappush(self._queue, entry)
    
    def invalidate(self, item):
        """Mark an entry as removed"""
        entry = self._entry_map.pop(item)
        entry[-1] = 'REMOVED'
    
    def pop(self):
        """Remove and return the lowest priority item"""
        while self._queue:
            priority, count, item = heapq.heappop(self._queue)
            if item != 'REMOVED':
                del self._entry_map[item]
                return item
        raise KeyError('pop from empty priority queue')
    
    def peek(self):
        """View the lowest priority item without removing it"""
        while self._queue:
            priority, count, item = heapq.heappop(self._queue)
            if item != 'REMOVED':
                del self._entry_map[item]
                # Re-add the item
                self.push(item)
                return item
        raise KeyError('peek from empty priority queue')
    
    def is_empty(self):
        """Check if the queue is empty"""
        return len(self._entry_map) == 0