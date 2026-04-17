cmake_minimum_required(VERSION 3.18)
project(hello_cpp_basic LANGUAGES CXX)

add_library(hello_core STATIC src/greeting.cpp)
target_compile_features(hello_core PUBLIC cxx_std_17)
target_include_directories(hello_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

add_executable(hello_cli app/main.cpp)
target_link_libraries(hello_cli PRIVATE hello_core)
