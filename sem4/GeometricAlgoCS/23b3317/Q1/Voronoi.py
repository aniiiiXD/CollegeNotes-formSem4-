import random
import math
from DataType import Point, Event, Arc, Segment, PriorityQueue

class Voronoi:
    def __init__(self, points):
        # print("=== Initializing Voronoi Diagram ===")
        self.output = []
        self.arc = None
        self.original_points = points 
        self.points = PriorityQueue()
        self.event = PriorityQueue()
        self.x0 = self.x1 = -50.0
        self.y0 = self.y1 = 550.0
        # print(f"Processing {len(points)} input points")
        for pts in points:
            point = Point(pts[0], pts[1])
            self.points.push(point)
            if point.x < self.x0: self.x0 = point.x
            if point.y < self.y0: self.y0 = point.y
            if point.x > self.x1: self.x1 = point.x
            if point.y > self.y1: self.y1 = point.y
        dx = (self.x1 - self.x0 + 1) / 5.0
        dy = (self.y1 - self.y0 + 1) / 5.0
        self.x0 -= dx
        self.x1 += dx
        self.y0 -= dy
        # print(f"Boundary set: ({self.x0:.1f},{self.y0:.1f}) to ({self.x1:.1f},{self.y1:.1f})")

    def process(self):
        # print("\n=== Starting Fortune's Algorithm ===")
        while not self.points.empty():
            if not self.event.empty() and (self.event.top().x <= self.points.top().x):
                self.process_event()
            else:
                # print("Processing site event")
                self.process_point()
        while not self.event.empty():
            self.process_event()
        self.finish_edges()
        # print("Fortune's algorithm completed successfully!")

    def process_point(self):
        p = self.points.pop()
        self.arc_insert(p)

    def process_event(self):
        e = self.event.pop()
        if e.valid:
            s = Segment(e.p)
            self.output.append(s)
            a = e.a
            if a.pprev:
                a.pprev.pnext = a.pnext
                a.pprev.s1 = s
            if a.pnext:
                a.pnext.pprev = a.pprev
                a.pnext.s0 = s
            if a.s0: a.s0.finish(e.p)
            if a.s1: a.s1.finish(e.p)
            if a.pprev: self.check_circle_event(a.pprev, e.x)
            if a.pnext: self.check_circle_event(a.pnext, e.x)

    def arc_insert(self, p):
        # print("Inserting new arc for point ({p.x}, {p.y})")
        if not self.arc:
            self.arc = Arc(p)
            return
        i = self.arc
        while i:
            flag, z = self.intersect(p, i)
            if flag:
                flag, zz = self.intersect(p, i.pnext)
                if i.pnext and not flag:
                    i.pnext.pprev = Arc(i.p, i, i.pnext)
                    i.pnext = i.pnext.pprev
                else:
                    i.pnext = Arc(i.p, i)
                i.pnext.s1 = i.s1
                i.pnext.pprev = Arc(p, i, i.pnext)
                i.pnext = i.pnext.pprev
                i = i.pnext
                seg = Segment(z)
                self.output.append(seg)
                i.pprev.s1 = i.s0 = seg
                seg = Segment(z)
                self.output.append(seg)
                i.pnext.s0 = i.s1 = seg
                self.check_circle_event(i, p.x)
                self.check_circle_event(i.pprev, p.x)
                self.check_circle_event(i.pnext, p.x)
                return
            i = i.pnext
        i = self.arc
        while i.pnext:
            i = i.pnext
        i.pnext = Arc(p, i)
        x = self.x0
        y = (i.pnext.p.y + i.p.y) / 2.0
        start = Point(x, y)
        seg = Segment(start)
        i.s1 = i.pnext.s0 = seg
        self.output.append(seg)
        # print("Arc insertion completed")

    def check_circle_event(self, i, x0):
        if i.e and i.e.x != self.x0:
            i.e.valid = False
        i.e = None
        if not i.pprev or not i.pnext:
            return
        flag, x, o = self.circle(i.pprev.p, i.p, i.pnext.p)
        if flag and x > self.x0:
            i.e = Event(x, o, i)
            self.event.push(i.e)

    def circle(self, a, b, c):
        if ((b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)) > 0: return False, None, None
        A, B, C, D = b.x - a.x, b.y - a.y, c.x - a.x, c.y - a.y
        E, F = A*(a.x + b.x) + B*(a.y + b.y), C*(a.x + c.x) + D*(a.y + c.y)
        G = 2*(A*(c.y - b.y) - B*(c.x - b.x))
        if G == 0: return False, None, None
        ox, oy = (D*E - B*F) / G, (A*F - C*E) / G
        x = ox + math.sqrt((a.x-ox)**2 + (a.y-oy)**2)
        return True, x, Point(ox, oy)

    def finish_edges(self):
        l = self.x1 + (self.x1 - self.x0) + (self.y1 - self.y0)
        i = self.arc
        while i.pnext:
            if i.s1:
                p = self.intersection(i.p, i.pnext.p, l*2.0)
                i.s1.finish(p)
            i = i.pnext

    def get_output(self):
        print(f"\n=== Generated {len(self.output)} Voronoi edges ===")
        return [(o.start.x, o.start.y, o.end.x, o.end.y) for o in self.output]

    def find_cell(self, q):
        query_point = Point(q[0], q[1])
        result = min(self.original_points, key=lambda site: math.sqrt((site[0] - query_point.x)**2 + (site[1] - query_point.y)**2))
        print(f"Found nearest site: ({result[0]:.1f}, {result[1]:.1f})")
        return result

    def intersect(self, p, i):
        if not i: return False, None
        if i.p.x == p.x: return False, None
        
        a = 0.0
        b = 0.0
        
        if i.pprev:
            a = self.intersection(i.pprev.p, i.p, p.x).y
        if i.pnext:
            b = self.intersection(i.p, i.pnext.p, p.x).y
            
        if ((not i.pprev) or (a <= p.y)) and ((not i.pnext) or (p.y <= b)):
            py = p.y
            px = (i.p.x*i.p.x + (i.p.y-py)*(i.p.y-py) - p.x*p.x) / (2.0*i.p.x - 2.0*p.x)
            return True, Point(px, py)
        return False, None

    def intersection(self, p0, p1, l):
        # Handle different cases for parabola intersection
        p = p0
        if p0.x == p1.x:
            py = (p0.y + p1.y) / 2.0
        elif p1.x == l:
            py = p1.y
        elif p0.x == l:
            py = p0.y
            p = p1
        else:
            # Calculate intersection of two parabolas
            z0 = 2.0 * (p0.x - l)
            z1 = 2.0 * (p1.x - l)
            a = 1.0/z0 - 1.0/z1
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = (p0.y*p0.y + p0.x*p0.x - l*l) / z0 - (p1.y*p1.y + p1.x*p1.x - l*l) / z1
            py = (-b - math.sqrt(b*b - 4*a*c)) / (2*a)
        
        px = (p.x*p.x + (p.y-py)*(p.y-py) - l*l) / (2.0*p.x - 2.0*l)
        return Point(px, py)
