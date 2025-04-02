#include "voronoi.hh"
#include <algorithm>
#include <memory>
#include <cmath>

namespace Voronoi {

void FortuneAlgorithm::add_point(const Point& p) {
    points.push(p);
    
    // Update bounding box
    if (points.size() == 1) {
        x_min = x_max = p.x;
        y_min = y_max = p.y;
    } else {
        x_min = std::min(x_min, p.x);
        y_min = std::min(y_min, p.y);
        x_max = std::max(x_max, p.x);
        y_max = std::max(y_max, p.y);
    }
}

void FortuneAlgorithm::compute() {
    // Add margins to the bounding box
    const double dx = (x_max - x_min + 1) / 5.0;
    const double dy = (y_max - y_min + 1) / 5.0;
    x_min -= dx; x_max += dx;
    y_min -= dy; y_max += dy;
    
    // Process the queues
    while (!points.empty()) {
        if (!events.empty() && events.top()->x <= points.top().x) {
            process_event();
        } else {
            process_point();
        }
    }
    
    // Process remaining circle events
    while (!events.empty()) {
        process_event();
    }
    
    finish_edges();
}

std::vector<SegmentPtr> FortuneAlgorithm::get_segments() const {
    return output_segments;
}

int FortuneAlgorithm::locate_cell(const Point& q) const {
    // Find the closest point in the diagram to q
    int closest_index = -1;
    double min_distance = std::numeric_limits<double>::max();
    
    // This is a naive O(n) implementation - for better performance, 
    // you'd want to use a spatial index or walk the diagram structure
    
    // First, collect all the sites
    std::vector<Point> sites;
    for (ArcPtr arc = root; arc != nullptr; arc = arc->next) {
        sites.push_back(arc->p);
    }
    
    // Find the closest site
    for (size_t i = 0; i < sites.size(); ++i) {
        double dist = std::hypot(q.x - sites[i].x, q.y - sites[i].y);
        if (dist < min_distance) {
            min_distance = dist;
            closest_index = static_cast<int>(i);
        }
    }
    
    return closest_index;
}

void FortuneAlgorithm::print_output() const {
    // Bounding box coordinates
    std::cout << x_min << " " << x_max << " " << y_min << " " << y_max << "\n";
    
    // Output each segment
    for (const auto& seg : output_segments) {
        if (seg->done) {
            std::cout << seg->start.x << " " << seg->start.y << " "
                      << seg->end.x << " " << seg->end.y << "\n";
        }
    }
}

void FortuneAlgorithm::process_point() {
    Point p = points.top();
    points.pop();
    front_insert(p);
}

void FortuneAlgorithm::process_event() {
    EventPtr e = events.top();
    events.pop();
    
    if (e->valid) {
        // Create a new segment
        auto s = std::make_shared<Segment>(e->p);
        output_segments.push_back(s);
        
        // Remove the associated arc
        ArcPtr a = e->arc;
        if (a->prev) {
            a->prev->next = a->next;
            a->prev->right_segment = s;
        }
        if (a->next) {
            a->next->prev = a->prev;
            a->next->left_segment = s;
        }
        
        // Finish the edges
        if (a->left_segment) a->left_segment->finish(e->p);
        if (a->right_segment) a->right_segment->finish(e->p);
        
        // Recheck circle events
        if (a->prev) check_circle_event(a->prev, e->x);
        if (a->next) check_circle_event(a->next, e->x);
    }
}

void FortuneAlgorithm::front_insert(const Point& p) {
    if (!root) {
        root = std::make_shared<Arc>(p);
        return;
    }
    
    // Find the current arc(s) at height p.y
    for (ArcPtr i = root; i != nullptr; i = i->next) {
        Point z, zz;
        if (intersect(p, i, &z)) {
            // New parabola intersects arc i
            if (i->next && !intersect(p, i->next, &zz)) {
                i->next->prev = std::make_shared<Arc>(i->p, i, i->next);
                i->next = i->next->prev;
            } else {
                i->next = std::make_shared<Arc>(i->p, i);
            }
            i->next->right_segment = i->right_segment;
            
            // Add p between i and i->next
            i->next->prev = std::make_shared<Arc>(p, i, i->next);
            i->next = i->next->prev;
            
            i = i->next; // Now i points to the new arc
            
            // Add new segments
            i->prev->right_segment = i->left_segment = std::make_shared<Segment>(z);
            output_segments.push_back(i->left_segment);
            
            i->next->left_segment = i->right_segment = std::make_shared<Segment>(z);
            output_segments.push_back(i->right_segment);
            
            // Check for new circle events
            check_circle_event(i, p.x);
            check_circle_event(i->prev, p.x);
            check_circle_event(i->next, p.x);
            
            return;
        }
    }
    
    // Special case: if p never intersects an arc, append to the list
    ArcPtr i;
    for (i = root; i->next != nullptr; i = i->next) {}
    
    i->next = std::make_shared<Arc>(p, i);
    // Insert segment between p and i
    Point start;
    start.x = x_min;
    start.y = (i->next->p.y + i->p.y) / 2;
    i->right_segment = i->next->left_segment = std::make_shared<Segment>(start);
    output_segments.push_back(i->right_segment);
}

bool FortuneAlgorithm::check_circle_event(ArcPtr i, double x0) {
    // Invalidate any old event
    if (i->event && i->event->x != x0) {
        i->event->valid = false;
    }
    i->event = nullptr;
    
    if (!i->prev || !i->next) {
        return false;
    }
    
    double x;
    Point o;
    
    if (circle(i->prev->p, i->p, i->next->p, &x, &o) && x > x0) {
        i->event = std::make_shared<Event>(x, o, i);
        events.push(i->event);
        return true;
    }
    
    return false;
}

bool FortuneAlgorithm::circle(const Point& a, const Point& b, const Point& c, double* x, Point* o) const {
    // Check that bc is a "right turn" from ab
    if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y) > 0) {
        return false;
    }
    
    // Algorithm from O'Rourke 2ed p. 189
    const double A = b.x - a.x;
    const double B = b.y - a.y;
    const double C = c.x - a.x;
    const double D = c.y - a.y;
    const double E = A * (a.x + b.x) + B * (a.y + b.y);
    const double F = C * (a.x + c.x) + D * (a.y + c.y);
    const double G = 2 * (A * (c.y - b.y) - B * (c.x - b.x));
    
    if (G == 0) return false; // Points are colinear
    
    // Point o is the center of the circle
    o->x = (D * E - B * F) / G;
    o->y = (A * F - C * E) / G;
    
    // o.x plus radius equals max x coordinate
    *x = o->x + std::hypot(a.x - o->x, a.y - o->y);
    return true;
}

bool FortuneAlgorithm::intersect(const Point& p, ArcPtr i, Point* res) const {
    if (i->p.x == p.x) return false;
    
    double a = 0.0, b = 0.0;
    if (i->prev) // Get intersection of i->prev, i
        a = intersection(i->prev->p, i->p, p.x).y;
    if (i->next) // Get intersection of i->next, i
        b = intersection(i->p, i->next->p, p.x).y;
    
    if ((!i->prev || a <= p.y) && (!i->next || p.y <= b)) {
        if (res) {
            res->y = p.y;
            // Plug back into parabola equation
            res->x = (i->p.x * i->p.x + (i->p.y - res->y) * (i->p.y - res->y) - p.x * p.x)
                   / (2 * i->p.x - 2 * p.x);
        }
        return true;
    }
    return false;
}

Point FortuneAlgorithm::intersection(const Point& p0, const Point& p1, double l) const {
    Point res;
    Point p = p0;
    
    if (p0.x == p1.x) {
        res.y = (p0.y + p1.y) / 2;
    } else if (p1.x == l) {
        res.y = p1.y;
    } else if (p0.x == l) {
        res.y = p0.y;
        p = p1;
    } else {
        // Use quadratic formula
        const double z0 = 2 * (p0.x - l);
        const double z1 = 2 * (p1.x - l);
        
        const double a = 1/z0 - 1/z1;
        const double b = -2 * (p0.y/z0 - p1.y/z1);
        const double c = (p0.y*p0.y + p0.x*p0.x - l*l)/z0
                       - (p1.y*p1.y + p1.x*p1.x - l*l)/z1;
        
        res.y = (-b - std::sqrt(b*b - 4*a*c)) / (2*a);
    }
    // Plug back into one of the parabola equations
    res.x = (p.x*p.x + (p.y-res.y)*(p.y-res.y) - l*l)/(2*p.x-2*l);
    return res;
}

void FortuneAlgorithm::finish_edges() {
    // Advance the sweep line so no parabolas can cross the bounding box
    const double l = x_max + (x_max - x_min) + (y_max - y_min);
    
    // Extend each remaining segment
    for (ArcPtr i = root; i->next != nullptr; i = i->next) {
        if (i->right_segment) {
            i->right_segment->finish(intersection(i->p, i->next->p, l * 2));
        }
    }
}

} // namespace Voronoi