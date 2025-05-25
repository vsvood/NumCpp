// Example: NdArray usage with std::ranges
#include <iostream>
#include <ranges>
#include "NumCpp/NdArray.hpp"

int main() {
    // Create a 1D NdArray
    nc::NdArray<int> arr = {1, 2, 3, 4, 5};
    std::cout << "Original NdArray: ";
    for (auto v : arr) std::cout << v << ' ';
    std::cout << '\n';

    // Use std::ranges::for_each to increment each element
    std::ranges::for_each(arr, [](int& v) { v += 10; });
    std::cout << "After std::ranges::for_each (+10): ";
    for (auto v : arr) std::cout << v << ' ';
    std::cout << '\n';

    // Use std::ranges::transform_view to create a view of squares
    auto squares = arr | std::views::transform([](int v) { return v * v; });
    std::cout << "Squares (transform_view): ";
    for (auto v : squares) std::cout << v << ' ';
    std::cout << '\n';

    // Use std::ranges::reverse_view
    auto reversed = arr | std::views::reverse;
    std::cout << "Reversed: ";
    for (auto v : reversed) std::cout << v << ' ';
    std::cout << '\n';

    // Check if NdArray satisfies std::ranges::range
    constexpr bool is_range = std::ranges::range<nc::NdArray<int>>;
    std::cout << "NdArray<int> is std::ranges::range: " << std::boolalpha << is_range << '\n';

    return 0;
} 