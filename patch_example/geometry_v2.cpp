#include <vector>
#include <utility>
#include <cstdlib>

int euclidean(int a, int b) {
    if (b == 0) {
        return a;
    }
    return euclidean(b, a % b);
}

std::vector<std::pair<int, int>> bresenham(int x0, int y0, int x1, int y1) {
    std::vector<std::pair<int, int>> points;
    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);
    int x = x0, y = y0;
    int sx = (x0 < x1) ? 1 : -1;
    int sy = (y0 < y1) ? 1 : -1;

    if (dx > dy) {
        int err = dx / 2;
        while (x != x1) {
            points.emplace_back(x, y);
            err -= dy;
            if (err < 0) {
                y += sy;
                err += dx;
            }
            x += sx;
        }
    } else {
        int err = dy / 2;
        while (y != y1) {
            points.emplace_back(x, y);
            err -= dx;
            if (err < 0) {
                x += sx;
                err += dy;
            }
            y += sy;
        }
    }

    points.emplace_back(x, y);
    return points;
}
