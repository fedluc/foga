#include <iostream>

#include "hello_core/greeting.hpp"

int main() {
  if (hello_core::greet("foga") != "hello, foga!") {
    std::cerr << "unexpected greeting" << std::endl;
    return 1;
  }
  return 0;
}
