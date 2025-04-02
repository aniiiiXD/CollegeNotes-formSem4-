import heapq
import itertools

class Point:
   x = 0.0
   y = 0.0
   
   def __init__(self, x, y):
       print(f"Creating point at ({x}, {y})")
       self.x = x
       self.y = y

class Event:
    x = 0.0
    p = None
    a = None
    valid = True
    
    def __init__(self, x, p, a):
        #print(f"Creating event at x={x}")
        self.x = x
        self.p = p
        self.a = a
        self.valid = True

class Arc:
    p = None
    pprev = None
    pnext = None
    e = None
    s0 = None
    s1 = None
    
    def __init__(self, p, a=None, b=None):
        #print(f"Creating arc for point ({p.x}, {p.y})")
        self.p = p
        self.pprev = a
        self.pnext = b
        self.e = None
        self.s0 = None
        self.s1 = None

class Segment:
    start = None
    end = None
    done = False
    
    def __init__(self, p):
        #print(f"Starting new segment at ({p.x}, {p.y})")
        self.start = p
        self.end = None
        self.done = False

    def finish(self, p):
        if self.done: return
        #print(f"Finishing segment at ({p.x}, {p.y})")
        self.end = p
        self.done = True        

class PriorityQueue:
    def __init__(self):
        print("Initializing priority queue")
        self.pq = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def push(self, item):
        #print(f"Pushing item with priority {item.x}")
        if item in self.entry_finder: return
        count = next(self.counter)

        entry = [item.x, count, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)

    def remove_entry(self, item):
        #print("Removing entry from queue")
        entry = self.entry_finder.pop(item)
        entry[-1] = 'Removed'

    def pop(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item is not 'Removed':
                #print(f"Popped item with priority {priority}")
                del self.entry_finder[item]
                return item
        print("Warning: Attempted pop from empty queue")
        raise KeyError('pop from an empty priority queue')

    def top(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item is not 'Removed':
                del self.entry_finder[item]
                self.push(item)
                #print(f"Peeked item with priority {priority}")
                return item
        print("Warning: Attempted top from empty queue")
        raise KeyError('top from an empty priority queue')

    def empty(self):
        return not self.pq

