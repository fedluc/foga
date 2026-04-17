cmake_minimum_required(VERSION 3.18)
project(hello_bindings_tested LANGUAGES CXX)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

add_library(hello_core STATIC cpp/src/greeting.cpp)
target_compile_features(hello_core PUBLIC cxx_std_17)
target_include_directories(hello_core PUBLIC cpp/include)

pybind11_add_module(_core src/hello_bindings/bindings.cpp)
target_link_libraries(_core PRIVATE hello_core)

install(TARGETS _core DESTINATION hello_bindings)
