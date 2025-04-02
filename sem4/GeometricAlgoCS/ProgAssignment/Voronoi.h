// Voronoi.h
class Voronoi {
    private:
        std::vector<Segment*> output;
        Arc* arc;
        std::priority_queue<Event> events;
        std::vector<Point> points;
        
        // Bounding box coordinates
        double x0, x1, y0, y1;
        
        // Algorithm helper methods
        void process_point();
        void process_event();
        void arc_insert(Point* p);
        void check_circle_event(Arc* i, double x0);
        bool circle(Point* a, Point* b, Point* c, double& x, Point* o);
        bool intersect(Point* p, Arc* i, Point*& result);
        Point* intersection(Point* p0, Point* p1, double l);
        void finish_edges();
    
    public:
        Voronoi(const std::vector<Point>& input_points);
        ~Voronoi();
        
        void process();
        std::vector<std::array<double, 4>> get_output() const;
        
        // Query function to find which cell a point belongs to
        int locate_cell(const Point& query) const;
    };
    