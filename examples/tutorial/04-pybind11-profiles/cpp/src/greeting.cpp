#include "hello_core/greeting.hpp"

namespace hello_core {

std::string greet(const std::string& name) {
  return "hello, " + name + "!";
}

}  // namespace hello_core
