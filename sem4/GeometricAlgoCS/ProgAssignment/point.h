// Point.h
struct Point {
    double x, y;
    
    Point(double _x = 0.0, double _y = 0.0) : x(_x), y(_y) {}
};

// Event.h
struct Arc;

struct Event {
    double x;
    Point* p;
    Arc* a;
    bool valid;
    
    Event(double _x, Point* _p, Arc* _a) : x(_x), p(_p), a(_a), valid(true) {}
    
    // For priority queue comparison
    bool operator<(const Event& other) const {
        return x > other.x; // Reversed for min-heap priority queue
    }
};

// Segment.h
struct Segment {
    Point start;
    Point* end;
    bool done;
    
    Segment(Point* p) : start(*p), end(nullptr), done(false) {}
    
    void finish(Point* p) {
        if (done) return;
        end = p;
        done = true;
    }
};

// Arc.h
struct Arc {
    Point* p;
    Arc* pprev;
    Arc* pnext;
    Event* e;
    Segment* s0;
    Segment* s1;
    
    Arc(Point* _p, Arc* a = nullptr, Arc* b = nullptr) 
        : p(_p), pprev(a), pnext(b), e(nullptr), s0(nullptr), s1(nullptr) {}
};
