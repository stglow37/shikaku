#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <iomanip>
#include <queue>
#include <cmath>

using namespace std;
using namespace std::chrono;

// --- Data Structures ---

struct Rectangle {
    int r, c, h, w, area;
};

// --- Solver Class ---

class RectangleSolver {
private:
    int n;
    int board_area;
    vector<vector<int>> grid;
    vector<Rectangle> best_solution;
    int best_count;
    vector<bool> used_areas;
    
    // Statistics
    long long nodes_explored;
    long long pruned_branches;
    double runtime_sec;

    // Returns {row, col} of the top-leftmost empty cell. {-1, -1} if full.
    pair<int, int> first_empty() const {
        for (int r = 0; r < n; ++r) {
            for (int c = 0; c < n; ++c) {
                if (grid[r][c] == 0) return {r, c};
            }
        }
        return {-1, -1};
    }

    // Pruning 2: Theoretical maximum additional rectangles
    int upper_bound(int remaining_area) const {
        int max_additional = 0;
        int area_left = remaining_area;
        int current_val = 1;
        
        while (area_left > 0) {
            if (!used_areas[current_val]) {
                if (area_left >= current_val) {
                    area_left -= current_val;
                    max_additional++;
                } else {
                    break;
                }
            }
            current_val++;
        }
        return max_additional;
    }

    // Pruning 3: Ensure all empty components can at least fit the smallest available area
    bool component_analysis() const {
        int smallest_avail = 1;
        while (smallest_avail <= board_area && used_areas[smallest_avail]) {
            smallest_avail++;
        }
        
        vector<vector<bool>> visited(n, vector<bool>(n, false));
        int dr[] = {-1, 1, 0, 0};
        int dc[] = {0, 0, -1, 1};

        for (int r = 0; r < n; ++r) {
            for (int c = 0; c < n; ++c) {
                if (grid[r][c] == 0 && !visited[r][c]) {
                    int comp_size = 0;
                    queue<pair<int, int>> q;
                    q.push({r, c});
                    visited[r][c] = true;
                    
                    while (!q.empty()) {
                        auto [curr_r, curr_c] = q.front();
                        q.pop();
                        comp_size++;
                        
                        for (int i = 0; i < 4; ++i) {
                            int nr = curr_r + dr[i];
                            int nc = curr_c + dc[i];
                            if (nr >= 0 && nr < n && nc >= 0 && nc < n) {
                                if (grid[nr][nc] == 0 && !visited[nr][nc]) {
                                    visited[nr][nc] = true;
                                    q.push({nr, nc});
                                }
                            }
                        }
                    }
                    if (comp_size < smallest_avail) return false;
                }
            }
        }
        return true;
    }

    void place(const Rectangle& rect, int id) {
        for (int i = 0; i < rect.h; ++i) {
            for (int j = 0; j < rect.w; ++j) {
                grid[rect.r + i][rect.c + j] = id;
            }
        }
        used_areas[rect.area] = true;
    }

    void remove(const Rectangle& rect) {
        for (int i = 0; i < rect.h; ++i) {
            for (int j = 0; j < rect.w; ++j) {
                grid[rect.r + i][rect.c + j] = 0;
            }
        }
        used_areas[rect.area] = false;
    }

    void search(vector<Rectangle>& current_rects) {
        nodes_explored++;
        
        auto [r, c] = first_empty();
        
        // Base case: Board is full
        if (r == -1) {
            if (current_rects.size() > best_count) {
                best_count = current_rects.size();
                best_solution = current_rects;
            }
            return;
        }

        int current_count = current_rects.size();
        int remaining_cells = board_area;
        for (const auto& rect : current_rects) remaining_cells -= rect.area;

        // Pruning 1 & 2: Logical and Theoretical bounds
        if (current_count + upper_bound(remaining_cells) <= best_count) {
            pruned_branches++;
            return;
        }

        // Pruning 3: Component Analysis
        if (!component_analysis()) {
            pruned_branches++;
            return;
        }

        // Generate valid rectangles at (r, c)
        vector<Rectangle> valid_rects;
        int max_h = n - r;
        int max_w = n - c;
        
        for (int h = 1; h <= max_h; ++h) {
            for (int w = 1; w <= max_w; ++w) {
                int area = h * w;
                if (used_areas[area]) continue;
                
                // Check collision
                bool collision = false;
                for (int i = 0; i < h; ++i) {
                    for (int j = 0; j < w; ++j) {
                        if (grid[r + i][c + j] != 0) {
                            collision = true;
                            break;
                        }
                    }
                    if (collision) break;
                }
                
                if (!collision) {
                    valid_rects.push_back({r, c, h, w, area});
                }
            }
        }

        // Sort heuristic: Largest area first, then closer to square shape
        sort(valid_rects.begin(), valid_rects.end(), [](const Rectangle& a, const Rectangle& b) {
            if (a.area != b.area) return a.area > b.area;
            return abs(a.h - a.w) < abs(b.h - b.w);
        });

        // Branching
        for (const auto& rect : valid_rects) {
            place(rect, current_count + 1);
            current_rects.push_back(rect);
            
            search(current_rects);
            
            current_rects.pop_back();
            remove(rect);
        }
    }

public:
    RectangleSolver(int size) : n(size), board_area(size * size), best_count(0), 
                                nodes_explored(0), pruned_branches(0), runtime_sec(0.0) {
        grid.assign(n, vector<int>(n, 0));
        used_areas.assign(board_area + 1, false);
    }

    void solve() {
        auto start = high_resolution_clock::now();
        
        vector<Rectangle> current_rects;
        search(current_rects);
        
        auto end = high_resolution_clock::now();
        runtime_sec = duration_cast<duration<double>>(end - start).count();
    }

    // Displays the construction only if requested
    void show_construction(bool show = true) {
        cout << "\n--- Results for N = " << n << " ---\n";
        cout << "Max Rectangles : " << best_count << "\n";
        cout << "Runtime        : " << fixed << setprecision(4) << runtime_sec << " seconds\n";
        cout << "Nodes Explored : " << nodes_explored << "\n";
        cout << "Branches Pruned: " << pruned_branches << "\n";

        if (!show) return; // Skip construction if show is false

        cout << "\nOptimal Grid Construction (Rectangle IDs):\n";
        vector<vector<int>> final_grid(n, vector<int>(n, 0));
        int id = 1;
        for (const auto& rect : best_solution) {
            for (int i = 0; i < rect.h; ++i) {
                for (int j = 0; j < rect.w; ++j) {
                    final_grid[rect.r + i][rect.c + j] = id;
                }
            }
            id++;
        }

        for (int r = 0; r < n; ++r) {
            for (int c = 0; c < n; ++c) {
                cout << setw(3) << final_grid[r][c] << " ";
            }
            cout << "\n";
        }
        
        cout << "\nRectangle Details:\n";
        for (size_t i = 0; i < best_solution.size(); ++i) {
            const auto& rect = best_solution[i];
            cout << "ID " << setw(2) << i+1 
                 << " -> Area: " << setw(2) << rect.area 
                 << " | Size: " << rect.h << "x" << rect.w 
                 << " | Pos: (" << rect.r << "," << rect.c << ")\n";
        }
    }
};

// --- Main Execution ---

int main() {
    int n = 9; // Change N here
    
    RectangleSolver solver(n);
    solver.solve();
    
    // Toggle the boolean to true/false to show/hide the grid construction
    bool want_construction = true; 
    solver.show_construction(want_construction);

    return 0;
}

