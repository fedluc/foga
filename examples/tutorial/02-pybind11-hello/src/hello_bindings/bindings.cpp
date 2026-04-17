#include <pybind11/pybind11.h>

#include "hello_core/greeting.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_core, module) {
  module.doc() = "Minimal hello-world bindings";
  module.def("greet", &hello_core::greet, py::arg("name"));
}
