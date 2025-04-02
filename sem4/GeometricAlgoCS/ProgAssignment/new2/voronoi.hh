#pragma once

#include <vector>
#include <queue>
#include <memory>
#include <cmath>
#include <iostream>

namespace Voronoi {

struct Point {
    double x;
    double y;
    
    Point(double x = 0.0, double y = 0.0) : x(x), y(y) {}
    
    bool operator==(const Point& other) const {
        return x == other.x && y == other.y;
    }
    
    bool operator!=(const Point& other) const {
        return !(*this == other);
    }
};

struct Segment {
    Point start;
    Point end;
    bool done;
    
    Segment(const Point& p) : start(p), end(), done(false) {}
    
    void finish(const Point& p) {
        if (!done) {
            end = p;
            done = true;
        }
    }
};

class Arc;
class Event;

using ArcPtr = std::shared_ptr<Arc>;
using EventPtr = std::shared_ptr<Event>;
using SegmentPtr = std::shared_ptr<Segment>;

class Arc {
public:
    Point p;
    ArcPtr prev;
    ArcPtr next;
    EventPtr event;
    SegmentPtr left_segment;
    SegmentPtr right_segment;
    
    Arc(const Point& pp, ArcPtr a = nullptr, ArcPtr b = nullptr)
        : p(pp), prev(a), next(b), event(nullptr), left_segment(nullptr), right_segment(nullptr) {}
};

class Event {
public:
    double x;
    Point p;
    ArcPtr arc;
    bool valid;
    
    Event(double xx, const Point& pp, ArcPtr aa)
        : x(xx), p(pp), arc(aa), valid(true) {}
};

class FortuneAlgorithm {
public:
    FortuneAlgorithm() = default;
    
    void add_point(const Point& p);
    void compute();
    std::vector<SegmentPtr> get_segments() const;
    int locate_cell(const Point& q) const;
    void print_output() const;
    
private:
    ArcPtr root = nullptr;
    std::priority_queue<Point, std::vector<Point>, std::greater<>> points;
    std::priority_queue<EventPtr, std::vector<EventPtr>, std::greater<>> events;
    std::vector<SegmentPtr> output_segments;
    
    double x_min = 0.0, x_max = 0.0, y_min = 0.0, y_max = 0.0;
    
    void process_point();
    void process_event();
    void front_insert(const Point& p);
    
    bool check_circle_event(ArcPtr i, double x0);
    bool circle(const Point& a, const Point& b, const Point& c, double* x, Point* o) const;
    
    bool intersect(const Point& p, ArcPtr i, Point* result = nullptr) const;
    Point intersection(const Point& p0, const Point& p1, double l) const;
    
    void finish_edges();
    
    struct EventComparator {
        bool operator()(const EventPtr& a, const EventPtr& b) const {
            return a->x > b->x;
        }
    };
};

} // namespace Voronoi