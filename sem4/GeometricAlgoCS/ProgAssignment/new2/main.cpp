#include "voronoi.hh"
#include <iostream>

int main() {
    Voronoi::FortuneAlgorithm voronoi;

    // Example points for the diagram
    voronoi.add_point({100, 200});
    voronoi.add_point({300, 400});
    voronoi.add_point({200, 100});
    voronoi.add_point({400, 300});
    voronoi.add_point({250, 250});

    // Compute the Voronoi diagram
    voronoi.compute();

    // Print the output segments
    voronoi.print_output();

    return 0;
}
